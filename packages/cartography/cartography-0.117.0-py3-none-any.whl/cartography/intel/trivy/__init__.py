import json
import logging
from typing import Any

import boto3
from neo4j import Session

from cartography.client.aws import list_accounts
from cartography.client.aws.ecr import get_ecr_images
from cartography.config import Config
from cartography.intel.trivy.scanner import cleanup
from cartography.intel.trivy.scanner import get_json_files_in_dir
from cartography.intel.trivy.scanner import get_json_files_in_s3
from cartography.intel.trivy.scanner import sync_single_image_from_file
from cartography.intel.trivy.scanner import sync_single_image_from_s3
from cartography.stats import get_stats_client
from cartography.util import timeit

logger = logging.getLogger(__name__)
stat_handler = get_stats_client("trivy.scanner")


@timeit
def get_scan_targets(
    neo4j_session: Session,
    account_ids: list[str] | None = None,
) -> set[str]:
    """
    Return list of ECR images from all accounts in the graph.
    """
    if not account_ids:
        aws_accounts = list_accounts(neo4j_session)
    else:
        aws_accounts = account_ids

    ecr_images: set[str] = set()
    for account_id in aws_accounts:
        for _, _, image_uri, _, _ in get_ecr_images(neo4j_session, account_id):
            ecr_images.add(image_uri)

    return ecr_images


def _get_intersection(
    image_uris: set[str], json_files: set[str], trivy_s3_prefix: str
) -> list[tuple[str, str]]:
    """
    Get the intersection of ECR images in the graph and S3 scan results.

    Args:
        image_uris: Set of ECR images in the graph
        json_files: Set of S3 object keys for JSON files
        trivy_s3_prefix: S3 prefix path containing scan results

    Returns:
        List of tuples (image_uri, s3_object_key)
    """
    intersection = []
    prefix_len = len(trivy_s3_prefix)
    for s3_object_key in json_files:
        # Sample key "123456789012.dkr.ecr.us-west-2.amazonaws.com/other-repo:v1.0.json"
        # Sample key "folder/derp/123456789012.dkr.ecr.us-west-2.amazonaws.com/other-repo:v1.0.json"
        # Remove the prefix and the .json suffix
        image_uri = s3_object_key[prefix_len:-5]

        if image_uri in image_uris:
            intersection.append((image_uri, s3_object_key))

    return intersection


@timeit
def sync_trivy_aws_ecr_from_s3(
    neo4j_session: Session,
    trivy_s3_bucket: str,
    trivy_s3_prefix: str,
    update_tag: int,
    common_job_parameters: dict[str, Any],
    boto3_session: boto3.Session,
) -> None:
    """
    Sync Trivy scan results from S3 for AWS ECR images.

    Args:
        neo4j_session: Neo4j session for database operations
        trivy_s3_bucket: S3 bucket containing scan results
        trivy_s3_prefix: S3 prefix path containing scan results
        update_tag: Update tag for tracking
        common_job_parameters: Common job parameters for cleanup
        boto3_session: boto3 session for S3 operations
    """
    logger.info(
        f"Using Trivy scan results from s3://{trivy_s3_bucket}/{trivy_s3_prefix}"
    )

    image_uris: set[str] = get_scan_targets(neo4j_session)
    json_files: set[str] = get_json_files_in_s3(
        trivy_s3_bucket, trivy_s3_prefix, boto3_session
    )
    intersection: list[tuple[str, str]] = _get_intersection(
        image_uris, json_files, trivy_s3_prefix
    )

    if len(intersection) == 0:
        logger.error(
            f"Trivy sync was configured, but there are no ECR images with S3 json scan results in bucket "
            f"'{trivy_s3_bucket}' with prefix '{trivy_s3_prefix}'. "
            "Skipping Trivy sync to avoid potential data loss. "
            "Please check the S3 bucket and prefix configuration. We expect the json files in s3 to be named "
            f"`<image_uri>.json` and to be in the same bucket and prefix as the scan results. If the prefix is "
            "a folder, it MUST end with a trailing slash '/'. "
        )
        logger.error(f"JSON files in S3: {json_files}")
        raise ValueError("No ECR images with S3 json scan results found.")

    logger.info(f"Processing {len(intersection)} ECR images with S3 scan results")
    for image_uri, s3_object_key in intersection:
        sync_single_image_from_s3(
            neo4j_session,
            image_uri,
            update_tag,
            trivy_s3_bucket,
            s3_object_key,
            boto3_session,
        )

    cleanup(neo4j_session, common_job_parameters)


@timeit
def sync_trivy_aws_ecr_from_dir(
    neo4j_session: Session,
    results_dir: str,
    update_tag: int,
    common_job_parameters: dict[str, Any],
) -> None:
    """Sync Trivy scan results from local files for AWS ECR images."""
    logger.info(f"Using Trivy scan results from {results_dir}")

    image_uris: set[str] = get_scan_targets(neo4j_session)
    json_files: set[str] = get_json_files_in_dir(results_dir)

    if not json_files:
        logger.error(
            f"Trivy sync was configured, but no json files were found in {results_dir}."
        )
        raise ValueError("No Trivy json results found on disk")

    logger.info(f"Processing {len(json_files)} local Trivy result files")

    for file_path in json_files:
        # First, check if the image exists in the graph before syncing
        try:
            # Peek at the artifact name without processing the file
            with open(file_path, encoding="utf-8") as f:
                trivy_data = json.load(f)
                artifact_name = trivy_data.get("ArtifactName")

            if artifact_name and artifact_name not in image_uris:
                logger.debug(
                    f"Skipping results for {artifact_name} since the image is not present in the graph"
                )
                continue

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to read artifact name from {file_path}: {e}")
            continue

        # Now sync the file since we know the image exists in the graph
        sync_single_image_from_file(
            neo4j_session,
            file_path,
            update_tag,
        )

    cleanup(neo4j_session, common_job_parameters)


@timeit
def start_trivy_ingestion(neo4j_session: Session, config: Config) -> None:
    """Start Trivy scan ingestion from S3 or local files.

    Args:
        neo4j_session: Neo4j session for database operations
        config: Configuration object containing S3 or directory paths
    """
    if not config.trivy_s3_bucket and not config.trivy_results_dir:
        logger.info("Trivy configuration not provided. Skipping Trivy ingestion.")
        return

    if config.trivy_results_dir:
        common_job_parameters = {
            "UPDATE_TAG": config.update_tag,
        }
        sync_trivy_aws_ecr_from_dir(
            neo4j_session,
            config.trivy_results_dir,
            config.update_tag,
            common_job_parameters,
        )
        return

    if config.trivy_s3_prefix is None:
        config.trivy_s3_prefix = ""

    common_job_parameters = {
        "UPDATE_TAG": config.update_tag,
    }

    boto3_session = boto3.Session()

    sync_trivy_aws_ecr_from_s3(
        neo4j_session,
        config.trivy_s3_bucket,
        config.trivy_s3_prefix,
        config.update_tag,
        common_job_parameters,
        boto3_session,
    )

    # Support other Trivy resource types here e.g. if Google Cloud has images.
