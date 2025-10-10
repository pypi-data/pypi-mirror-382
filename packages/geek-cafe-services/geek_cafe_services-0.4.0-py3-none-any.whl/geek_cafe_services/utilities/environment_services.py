"""
Geek Cafe SaaS Services Environment Services.

This module provides utilities for loading and accessing environment variables
used throughout the Geek Cafe SaaS Services application. It includes classes for
loading environment files and accessing specific environment variables in a
consistent manner.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dotenv import load_dotenv
from aws_lambda_powertools import Logger


logger = Logger(__name__)

DEBUGGING = os.getenv("DEBUGGING", "false").lower() == "true"


class EnvironmentServices:
    """Utility class for loading environment variables from files.
    
    This class provides methods to load environment variables from .env files,
    load event files for testing, and search for files in the project directory structure.
    """

    def load_environment(
        self,
        *,
        starting_path: Optional[str] = None,
        file_name: str = ".env.dev",
        override_vars: bool = True,
        raise_error_if_not_found: bool = True,
    ) -> None:
        """Load environment variables from a .env file.
        
        Searches for the specified environment file starting from the given path
        and loads the environment variables from it.
        
        Args:
            starting_path: Path to start searching from. If None, uses the current file's location.
            file_name: Name of the environment file to load (default: ".env.dev").
            override_vars: Whether to override existing environment variables (default: True).
            raise_error_if_not_found: Whether to raise an error if the file is not found (default: True).
            
        Raises:
            RuntimeError: If the environment file is not found and raise_error_if_not_found is True.
        """

        if not starting_path:
            starting_path = __file__

        environment_file: str | None = self.find_file(
            starting_path=starting_path,
            file_name=file_name,
            raise_error_if_not_found=raise_error_if_not_found,
        )

        if environment_file:
            load_dotenv(dotenv_path=environment_file, override=override_vars)

        if DEBUGGING:
            env_vars = os.environ
            logger.debug(f"Loaded environment file: {environment_file}")
            # print(env_vars)

    def load_event_file(self, full_path: str) -> Dict[str, Any]:
        """Load and parse a JSON event file.
        
        Loads a JSON event file and handles common event structures by extracting
        the actual event data from nested 'message' or 'event' fields if present.
        
        Args:
            full_path: The full path to the JSON event file.
            
        Returns:
            The parsed event data as a dictionary.
            
        Raises:
            RuntimeError: If the event file does not exist.
        """
        if not os.path.exists(full_path):
            raise RuntimeError(f"Failed to locate event file: {full_path}")

        event: Dict = {}
        with open(full_path, mode="r", encoding="utf-8") as json_file:
            event = json.load(json_file)

        if "message" in event:
            tmp = event.get("message")
            if isinstance(tmp, Dict):
                event = tmp

        if "event" in event:
            tmp = event.get("event")
            if isinstance(tmp, Dict):
                event = tmp

        return event

    def find_file(
        self, starting_path: str, file_name: str, raise_error_if_not_found: bool = True, max_parent_directories: int = 25
    ) -> Optional[str]:
        """Search for a file in the project directory structure.
        
        Searches for the specified file by traversing up the directory tree
        starting from the given path, up to a maximum number of parent directories.
        
        Args:
            starting_path: Path to start searching from.
            file_name: Name of the file to search for.
            raise_error_if_not_found: Whether to raise an error if the file is not found (default: True).
            max_parent_directories: Maximum number of parent directories to search (default: 25).
            
        Returns:
            The full path to the found file, or None if not found and raise_error_if_not_found is False.
            
        Raises:
            RuntimeError: If the file is not found and raise_error_if_not_found is True.
        """
        parents = max_parent_directories
        starting_path = starting_path or __file__

        paths: List[str] = []
        for parent in range(parents):
            # Check if we have enough parent directories available
            current_path = Path(starting_path)
            if parent >= len(current_path.parents):
                break
            
            path = current_path.parents[parent].absolute()
            print(f"searching: {path}")
            tmp = os.path.join(path, file_name)
            paths.append(tmp)
            if os.path.exists(tmp):
                return tmp

        if raise_error_if_not_found:
            searched_paths = "\n".join(paths)
            raise RuntimeError(
                f"Failed to locate environment file: {file_name} in: \n {searched_paths}"
            )

        return None


class EnvironmentVariables:
    """
    Centralized access to environment variables used throughout the application.
    
    This class provides static methods to access environment variables in a consistent manner,
    with proper typing and default values where appropriate. Using this class instead of direct
    os.getenv calls helps track and manage all environment variables in one place, making
    maintenance and documentation easier.
    """

    @staticmethod
    def get_aws_region() -> Optional[str]:
        """
        Get the AWS region from environment variables.
        
        Returns:
            The AWS region as a string, or None if not set.
        """
        value = os.getenv("AWS_REGION")
        return value

    @staticmethod
    def get_aws_profile() -> Optional[str]:
        """
        Get the AWS profile used for CLI/boto3 commands.
        
        This should only be set with temporary credentials and only for development purposes.
        
        Returns:
            The AWS profile name as a string, or None if not set.
        """
        value = os.getenv("AWS_PROFILE")
        return value

    @staticmethod
    def get_aws_account_id() -> Optional[str]:
        """
        Get the AWS account ID from environment variables.
        
        Returns:
            The AWS account ID as a string, or None if not set.
        """
        value = os.getenv("AWS_ACCOUNT_ID")
        return value

    @staticmethod
    def get_auth_target_validation_level() -> Optional[str]:
        """
        Get the authentication target validation level from environment variables.
        
        Validation levels:
            PASS_THROUGH: Allows the logged in user to be listed as the target
                if the target user isn't explicitly listed. This provides backward compatibility
                during conversion from short URLs to more detailed URL routes.
                
            STRICT: Requires a target user/tenant to be explicitly specified in the path.
                This will be required for all new endpoints. The endpoints have been created
                but some UI and tests have not been updated yet.
        
        Returns:
            The validation level as a string ("PASS_THROUGH" or "STRICT"), or None if not set.
        """
        value = os.getenv("AUTH_TARGET_VALIDATION_LEVEL")
        return value

    

    @staticmethod
    def get_logging_level(default: str = "INFO") -> str:
        """
        Get the logging level from environment variables.
        
        Args:
            default: Default logging level to use if not set in environment (default: "INFO").
            
        Returns:
            The logging level as a string.
        """
        value = os.getenv("LOG_LEVEL", default)
        return value

    @staticmethod
    def get_app_domain():
        """
        gets the app domain name from an environment var
        """
        value = os.getenv("APP_DOMAIN")
        return value

    @staticmethod
    def get_ses_user_name():
        """
        gets the ses user-name from an environment var
        """
        value = os.getenv("SES_USER_NAME")
        return value

    @staticmethod
    def get_ses_password():
        """
        gets the ses password from an environment var
        """
        value = os.getenv("SES_PASSWORD")
        return value

    @staticmethod
    def get_ses_endpoint():
        """
        gets the ses endpoint from an environment var
        """
        value = os.getenv("SES_END_POINT")
        return value

    @staticmethod
    def get_cognito_user_pool() -> str | None:
        """
        gets the cognito user pool from an environment var
        """
        value = os.getenv("COGNITO_USER_POOL")
        return value

    @staticmethod
    def get_dynamodb_table_name():
        """
        gets the dynamodb table name from an environment var
        """
        value = os.getenv("APPLICATION_TABLE_NAME")
        return value

    @staticmethod
    def get_dynamodb_raise_on_error_setting() -> bool:
        """
        gets the dynamodb table name from an environment var
        """
        value = str(os.getenv("RAISE_ON_DB_ERROR", "true")).lower() == "true"

        return value

    @staticmethod
    def get_tenant_user_file_bucket_name():
        """
        gets the tenant user file bucket name from an environment var
        """
        value = os.getenv("TENANT_USER_FILE_BUCKET")
        return value

    @staticmethod
    def get_tenant_user_upload_bucket_name():
        """
        gets the tenant user upload bucket name from an environment var
        """
        value = os.getenv("UPLOAD_BUCKET")
        return value

    @staticmethod
    def get_lambda_function_to_invoke() -> str | None:
        """
        gets the lambda function to invoke from an environment var
        this is used by sync to async lambda invocation, or by the queue
        """
        value = os.getenv("LAMBDA_FUNCTION_TO_INVOKE")
        return value

    @staticmethod
    def get_amazon_trace_id():
        """
        gets the amazon trace id from an environment var
        """
        value = os.getenv("_X_AMZN_TRACE_ID", "NA")
        return value

    @staticmethod
    def get_integration_tests_setting() -> bool:
        """
        determine if integration tests are run from an environment var
        """
        value = str(os.getenv("RUN_INTEGRATION_TESTS", "False")).lower() == "true"
        env = EnvironmentVariables.get_environment_setting()

        if env.lower().startswith("prod"):
            value = False

        return value

    @staticmethod
    def get_environment_setting() -> str:
        """
        gets the environment name from an environment var
        """
        value = os.getenv("ENVIRONMENT") or os.getenv("ENVIRONMENT_NAME")

        if not value:
            logger.warning(
                "ENVIRONMENT var is not set. A future version will throw an error."
            )
            return ""

        return value

    @staticmethod
    def is_development_environment() -> bool:
        """
        determine if the environment is development
        """
        env = EnvironmentVariables.get_environment_setting()
        return env.lower().startswith("dev")
