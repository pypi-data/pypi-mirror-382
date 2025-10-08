import json
import logging
import uuid
from typing import Optional, Union

import boto3
from botocore.config import Config

from blazetest.core.project_config.model import AWSConfig

logger = logging.getLogger(__name__)


class S3Manager:
    s3_bucket_name: Optional[str] = None

    def __init__(
        self,
        aws_config: AWSConfig,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        self.aws_config = aws_config

        # Configure boto3 for better performance with connection pooling
        boto_config = Config(
            max_pool_connections=50,  # Support up to 50 concurrent connections
            retries={
                "max_attempts": 3,
                "mode": "adaptive",
            },  # Adaptive retry for transient errors
        )

        self.s3_client = boto3.client(
            "s3",
            region_name=aws_config.region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=boto_config,
        )
        self.s3_resource = boto3.resource(
            "s3",
            region_name=aws_config.region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def get_json_object(self, key: str) -> Optional[Union[dict, list]]:
        try:
            response = self.s3_client.get_object(Bucket=self.s3_bucket_name, Key=key)
            file_content = response["Body"].read().decode("utf-8")
            results = json.loads(file_content)
        except Exception as e:
            logger.debug("File not found or error in reading file from S3 bucket.")
            logger.debug(str(e))
            return None
        return results

    def put_object(self, key: str, body: str) -> bool:
        try:
            self.s3_client.put_object(Bucket=self.s3_bucket_name, Key=key, Body=body)
        except Exception as e:
            logger.debug("An error occurred while trying to upload file to S3.")
            logger.debug(str(e))
            return False
        return True

    # TODO: add tags while creating s3 bucket
    def find_or_create_s3_bucket(self, tags: dict) -> str:  # noqa
        s3_bucket_name = self.find_s3_bucket()

        if s3_bucket_name:
            logger.info(f"Using already existing S3 bucket: {s3_bucket_name}")
        else:
            location = {"LocationConstraint": self.aws_config.region}
            s3_bucket_name = (
                f"{self.aws_config.s3_bucket_prefix}-{str(uuid.uuid4())[:8]}"
            )
            self.s3_client.create_bucket(
                Bucket=s3_bucket_name,
                CreateBucketConfiguration=location,
            )
            logger.info(f"Created new S3 bucket: {s3_bucket_name}")

        self.s3_bucket_name = s3_bucket_name
        return self.s3_bucket_name

    def find_s3_bucket(self):
        self.s3_bucket_name = self._find_bucket_by_prefix(
            prefix=self.aws_config.s3_bucket_prefix
        )
        return self.s3_bucket_name

    def _find_bucket_by_prefix(self, prefix: str) -> Optional[str]:
        """Find an S3 bucket by its name prefix.

        :param prefix: The prefix to match against bucket names.
        :return: List of bucket names that match the prefix.
        """
        bucket_list = []

        for bucket in self.s3_resource.buckets.all():
            if bucket.name.startswith(prefix):
                bucket_list.append(bucket.name)

        if bucket_list:
            return bucket_list[0]
        else:
            return None
