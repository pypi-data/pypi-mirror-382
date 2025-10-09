"""
AWS Session Manager and Credential Provider.

This module provides centralized AWS credential management and session handling
with support for multiple authentication methods.
"""

import logging
import os
from typing import Optional, Tuple
import boto3
from botocore.config import Config
from botocore.exceptions import (
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
    ProfileNotFound,
)

logger = logging.getLogger(__name__)

# Default boto3 configuration for all AWS clients
DEFAULT_BOTO_CONFIG = Config(
    max_pool_connections=50,
    retries={"max_attempts": 3, "mode": "adaptive"},
    connect_timeout=10,
    read_timeout=60,
)


class AWSCredentialProvider:
    """
    Provides AWS credentials using a priority-based resolution chain.

    Credential Resolution Order:
    1. CLI arguments (highest priority)
    2. Configuration file (blazetest.toml)
    3. Environment variables
    4. AWS Profile (~/.aws/credentials)
    5. IAM Role (if role_arn specified)
    6. Default AWS credential chain (instance profile, ECS task role, etc.)
    """

    def __init__(
        self,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        session_token: Optional[str] = None,
        role_arn: Optional[str] = None,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.session_token = session_token
        self.role_arn = role_arn
        self.profile = profile
        self.region = region
        self._credentials = None
        self._credential_source = None

    def get_credentials(
        self,
    ) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
        """
        Get AWS credentials using the resolution chain.

        Returns:
            Tuple of (access_key_id, secret_access_key, session_token, source)
        """
        if self._credentials:
            return self._credentials

        # 1. Try explicit access keys (CLI args or config file)
        if self.access_key_id and self.secret_access_key:
            logger.info("Using AWS credentials from explicit access keys")
            self._credentials = (
                self.access_key_id,
                self.secret_access_key,
                self.session_token,
                "explicit_keys",
            )
            return self._credentials

        # 2. Try IAM role assumption
        if self.role_arn:
            try:
                logger.info(f"Attempting to assume IAM role: {self.role_arn}")
                creds = self._assume_role(self.role_arn)
                self._credentials = creds
                return self._credentials
            except Exception as e:
                logger.warning(f"Failed to assume role {self.role_arn}: {e}")

        # 3. Try AWS profile
        if self.profile:
            try:
                logger.info(f"Using AWS profile: {self.profile}")
                creds = self._get_profile_credentials(self.profile)
                self._credentials = creds
                return self._credentials
            except ProfileNotFound:
                logger.warning(f"AWS profile not found: {self.profile}")
            except Exception as e:
                logger.warning(f"Failed to use profile {self.profile}: {e}")

        # 4. Try environment variables
        env_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        env_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        env_session_token = os.environ.get("AWS_SESSION_TOKEN")

        if env_access_key and env_secret_key:
            logger.info("Using AWS credentials from environment variables")
            self._credentials = (
                env_access_key,
                env_secret_key,
                env_session_token,
                "environment",
            )
            return self._credentials

        # 5. Fall back to default AWS credential chain
        try:
            logger.info("Using default AWS credential chain")
            session = boto3.Session(region_name=self.region)
            credentials = session.get_credentials()
            if credentials:
                frozen = credentials.get_frozen_credentials()
                self._credentials = (
                    frozen.access_key,
                    frozen.secret_key,
                    frozen.token,
                    "default_chain",
                )
                return self._credentials
        except Exception as e:
            logger.error(f"Failed to get credentials from default chain: {e}")

        # No credentials found
        raise NoCredentialsError(
            "Unable to locate AWS credentials. Please configure credentials using:\n"
            "1. CLI: blazetest run -ak ACCESS_KEY -as SECRET_KEY\n"
            "2. Config: [cloud.aws.credentials] in blazetest.toml\n"
            "3. Environment: export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=...\n"
            "4. AWS Profile: aws configure --profile blazetest\n"
            "5. IAM Role: Specify role_arn in config or run on EC2/ECS"
        )

    def _assume_role(
        self, role_arn: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
        """Assume an IAM role and return temporary credentials."""
        sts_client = boto3.client("sts", region_name=self.region)
        response = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName="blazetest-session"
        )

        credentials = response["Credentials"]
        return (
            credentials["AccessKeyId"],
            credentials["SecretAccessKey"],
            credentials["SessionToken"],
            f"assumed_role:{role_arn}",
        )

    def _get_profile_credentials(
        self, profile: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
        """Get credentials from AWS profile."""
        session = boto3.Session(profile_name=profile, region_name=self.region)
        credentials = session.get_credentials()
        if credentials:
            frozen = credentials.get_frozen_credentials()
            return (
                frozen.access_key,
                frozen.secret_key,
                frozen.token,
                f"profile:{profile}",
            )
        raise NoCredentialsError(f"No credentials found in profile: {profile}")


class AWSSessionManager:
    """
    Singleton session manager for AWS boto3 clients.
    Provides centralized session and client creation with proper configuration.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._session = None
        self._clients = {}
        self._credential_provider = None
        self._initialized = True

    def configure(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        session_token: Optional[str] = None,
        role_arn: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        """
        Configure the session manager with credentials.

        Args:
            region: AWS region
            access_key_id: AWS access key ID (optional)
            secret_access_key: AWS secret access key (optional)
            session_token: AWS session token (optional)
            role_arn: IAM role ARN to assume (optional)
            profile: AWS profile name (optional)
        """
        self._credential_provider = AWSCredentialProvider(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            session_token=session_token,
            role_arn=role_arn,
            profile=profile,
            region=region,
        )

        # Get credentials using the provider
        access_key, secret_key, token, source = (
            self._credential_provider.get_credentials()
        )

        logger.info(f"AWS credentials resolved from: {source}")

        # Create session with resolved credentials
        self._session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=token,
            region_name=region,
        )

        # Clear cached clients when credentials change
        self._clients = {}

    def get_client(self, service_name: str, **kwargs):
        """
        Get a boto3 client for the specified service.

        Args:
            service_name: AWS service name (e.g., 's3', 'lambda', 'ecr')
            **kwargs: Additional arguments to pass to boto3.client()

        Returns:
            boto3 client instance
        """
        if not self._session:
            raise RuntimeError(
                "AWSSessionManager not configured. Call configure() first."
            )

        # Use default boto config if not provided
        if "config" not in kwargs:
            kwargs["config"] = DEFAULT_BOTO_CONFIG

        # Create client key for caching
        client_key = f"{service_name}_{str(sorted(kwargs.items()))}"

        # Return cached client if available
        if client_key in self._clients:
            return self._clients[client_key]

        # Create new client
        client = self._session.client(service_name, **kwargs)
        self._clients[client_key] = client

        return client

    def get_resource(self, service_name: str, **kwargs):
        """
        Get a boto3 resource for the specified service.

        Args:
            service_name: AWS service name (e.g., 's3')
            **kwargs: Additional arguments to pass to boto3.resource()

        Returns:
            boto3 resource instance
        """
        if not self._session:
            raise RuntimeError(
                "AWSSessionManager not configured. Call configure() first."
            )

        return self._session.resource(service_name, **kwargs)

    def reset(self):
        """Reset the session manager (useful for testing)."""
        self._session = None
        self._clients = {}
        self._credential_provider = None
