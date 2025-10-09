import json
import logging
import uuid
from typing import Optional, Union

from blazetest.core.project_config.model import AWSConfig
from blazetest.core.cloud.aws.session import AWSSessionManager
from blazetest.core.cloud.aws.error_handler import handle_aws_errors

logger = logging.getLogger(__name__)


class S3Manager:
    s3_bucket_name: Optional[str] = None

    def __init__(
        self,
        aws_config: AWSConfig,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
    ):
        self.aws_config = aws_config

        # Configure AWS Session Manager
        session_mgr = AWSSessionManager()
        session_mgr.configure(
            region=aws_config.region,
            access_key_id=aws_access_key_id or aws_config.credentials.access_key_id,
            secret_access_key=aws_secret_access_key
            or aws_config.credentials.secret_access_key,
            session_token=aws_session_token or aws_config.credentials.session_token,
            role_arn=aws_config.credentials.role_arn,
            profile=aws_config.credentials.profile,
        )

        # Get S3 client and resource from session manager
        # Session manager handles connection pooling, retries, and caching
        self.s3_client = session_mgr.get_client("s3")
        self.s3_resource = session_mgr.get_resource("s3")

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
    @handle_aws_errors
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
