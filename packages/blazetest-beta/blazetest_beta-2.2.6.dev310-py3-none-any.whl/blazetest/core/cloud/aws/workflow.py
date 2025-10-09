import json
import logging
import time
from typing import Dict, Optional

from botocore.exceptions import WaiterError

from blazetest.core.utils.exceptions import AWSLambdaFunctionNotCreated
from blazetest.core.cloud.aws.session import AWSSessionManager
from blazetest.core.cloud.aws.error_handler import handle_aws_errors

logger = logging.getLogger(__name__)


class AWSWorkflow:
    """
    The AWSWorkflow class is used to deploy an AWS Lambda function using boto3.

    Attributes:
        s3_bucket_name (str): The name of the S3 bucket to use.
        resource_prefix (str): The prefix for resource names.
        tags (dict): Tags to pass to the lambda
        env_vars (Dict[str, str]): Environment variables for the Lambda function.

    Methods:
        deploy(): Deploys the Lambda function.
        create_lambda_function(): Creates the Lambda function.
        create_iam_role(): Creates the IAM role for the Lambda function.
        create_iam_policy(): Creates the IAM policy for the Lambda function.
        attach_policy_to_role(): Attaches the IAM policy to the IAM role.
    """

    def __init__(
        self,
        aws_region: str,
        resource_prefix: str,
        s3_bucket_name: str,
        tags: dict,
        env_vars: Dict[str, str],
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        role_arn: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        self.aws_region = aws_region
        self.resource_prefix = resource_prefix
        self.s3_bucket_name = s3_bucket_name
        self.tags = tags or {}
        self.env_vars = env_vars

        # Configure AWS Session Manager
        session_mgr = AWSSessionManager()
        session_mgr.configure(
            region=aws_region,
            access_key_id=aws_access_key_id,
            secret_access_key=aws_secret_access_key,
            session_token=aws_session_token,
            role_arn=role_arn,
            profile=profile,
        )

        # Get AWS clients from session manager
        self.iam_client = session_mgr.get_client("iam")
        self.lambda_client = session_mgr.get_client("lambda")
        self.sts_client = session_mgr.get_client("sts")

    @handle_aws_errors
    def deploy(
        self,
        loki_user: str,
        loki_host: str,
        loki_api_key: str,
        image_uri: str,
        memory_size: int,
        function_timeout: int,
    ) -> str:
        """
        Deploys Lambda function and returns the version-qualified function name.

        Returns:
            str: Qualified function name (e.g., "function-name:123") for safe concurrent execution
        """
        role_arn, role_created = self.get_or_create_iam_role()
        policy_arn, policy_created = self.get_or_create_iam_policy()

        if role_created or policy_created:
            self.attach_policy_to_role(role_arn, policy_arn)
            logger.info("Waiting for IAM role/policy propagation...")
            time.sleep(10)

        qualified_function_name = self.create_or_update_lambda_function(
            role_arn,
            loki_user,
            loki_host,
            loki_api_key,
            image_uri,
            memory_size,
            function_timeout,
        )

        return qualified_function_name

    @handle_aws_errors
    def get_or_create_iam_role(self) -> tuple[str, bool]:
        # AWS IAM role names have a 64 character limit, reserve 5 chars for "-role"
        role_name = f"{self.resource_prefix[:59]}-role"
        try:
            response = self.iam_client.get_role(RoleName=role_name)
            logger.info(f"IAM role {role_name} already exists.")
            return response["Role"]["Arn"], False
        except self.iam_client.exceptions.NoSuchEntityException:
            logger.info(f"Creating IAM role {role_name}...")
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
            )
            return response["Role"]["Arn"], True

    @handle_aws_errors
    def get_or_create_iam_policy(self) -> tuple[str, bool]:
        # AWS IAM policy names have a 128 character limit, reserve 7 chars for "-policy"
        policy_name = f"{self.resource_prefix[:121]}-policy"
        try:
            response = self.iam_client.get_policy(
                PolicyArn=f"arn:aws:iam::{self.sts_client.get_caller_identity()['Account']}:policy/{policy_name}"
            )
            logger.info(f"IAM policy {policy_name} already exists.")
            return response["Policy"]["Arn"], False
        except self.iam_client.exceptions.NoSuchEntityException:
            logger.info(f"Creating IAM policy {policy_name}...")
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["s3:PutObject"],
                        "Resource": f"arn:aws:s3:::{self.s3_bucket_name}/*",
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                            "logs:PutRetentionPolicy",
                            "logs:DescribeLogStreams",
                        ],
                        "Resource": ["arn:aws:logs:*:*:*"],
                    },
                ],
            }
            response = self.iam_client.create_policy(
                PolicyName=policy_name, PolicyDocument=json.dumps(policy_document)
            )
            return response["Policy"]["Arn"], True

    def attach_policy_to_role(self, role_arn: str, policy_arn: str):
        logger.info(f"Attaching IAM policy to IAM role {self.resource_prefix}...")
        role_name = role_arn.split("/")[-1]
        try:
            self.iam_client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            logger.info(f"Policy {policy_arn} is already attached to role {role_name}")

    @handle_aws_errors
    def create_or_update_lambda_function(
        self,
        role_arn: str,
        loki_user: str,
        loki_host: str,
        loki_api_key: str,
        image_uri: str,
        memory_size: int,
        function_timeout: int,
    ) -> str:
        """
        Creates or updates Lambda function and returns the version-specific ARN.

        Returns:
            str: Version-specific function ARN (e.g., function_name:123) for safe concurrent execution
        """
        # Use consistent function name without UUID for reuse
        # AWS Lambda function names have a 64 character limit, reserve 7 chars for "-runner"
        function_name = f"{self.resource_prefix[:57]}-runner"
        session_uuid = self.tags.get("blazetest:uuid", "unknown")

        environment_variables = {
            "S3_BUCKET": self.s3_bucket_name,
            "LOKI_USER": loki_user,
            "LOKI_HOST": loki_host,
            "LOKI_API_KEY": loki_api_key,
            **self.env_vars,
        }

        environment_variables = {
            k: v for k, v in environment_variables.items() if v is not None
        }

        # Check if function already exists
        function_exists = False
        try:
            self.lambda_client.get_function(FunctionName=function_name)
            function_exists = True
            logger.info(f"Lambda function {function_name} already exists. Updating...")

            # Update function code with new image
            code_update_response = self.lambda_client.update_function_code(
                FunctionName=function_name,
                ImageUri=image_uri,
                Publish=False,  # Don't publish yet, we'll do it after config update
            )

            # Wait for code update to complete before updating configuration
            waiter = self.lambda_client.get_waiter("function_updated")
            waiter.wait(
                FunctionName=function_name, WaiterConfig={"Delay": 1, "MaxAttempts": 60}
            )

            # Update function configuration
            self.lambda_client.update_function_configuration(
                FunctionName=function_name,
                Role=role_arn,
                MemorySize=memory_size,
                Timeout=function_timeout,
                Environment={"Variables": environment_variables},
            )

            logger.info(f"Updated Lambda function {function_name} with new image")

        except self.lambda_client.exceptions.ResourceNotFoundException:
            # Function doesn't exist, create it
            logger.info(f"Creating Lambda function {function_name}...")
            self.lambda_client.create_function(
                FunctionName=function_name,
                Role=role_arn,
                PackageType="Image",
                Code={"ImageUri": image_uri},
                Description="Lambda function for execution of PyTest tests in parallel",
                MemorySize=memory_size,
                Timeout=function_timeout,
                Environment={"Variables": environment_variables},
                Tags=self.tags,
            )

        # Wait for function to be ready (active or updated)
        logger.info(f"Waiting for function {function_name} to be ready...")

        try:
            if function_exists:
                waiter = self.lambda_client.get_waiter("function_updated")
                waiter.wait(
                    FunctionName=function_name,
                    WaiterConfig={"Delay": 1, "MaxAttempts": 60},
                )
            else:
                waiter = self.lambda_client.get_waiter("function_active")
                waiter.wait(
                    FunctionName=function_name,
                    WaiterConfig={"Delay": 1, "MaxAttempts": 60},
                )
            logger.info(f"Function {function_name} is now ready.")
        except WaiterError as e:
            logger.warning(
                f"Function {function_name} waiter timed out, but continuing: {str(e)}"
            )

        # Publish a new version for this deployment
        # This creates an immutable snapshot that won't be affected by future updates
        logger.info(f"Publishing new version for session {session_uuid}...")
        version_response = self.lambda_client.publish_version(
            FunctionName=function_name,
            Description=f"BlazeTest session {session_uuid}",
        )

        version_number = version_response["Version"]
        version_arn = version_response["FunctionArn"]

        logger.info(f"Published version {version_number} for session {session_uuid}")
        logger.info(f"Version ARN: {version_arn}")

        # Return the qualified ARN (function:version) for safe concurrent execution
        # Each test run will use its own immutable version
        return f"{function_name}:{version_number}"
