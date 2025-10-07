import swagger_client
from swagger_client.models.stack import Stack
from swagger_client.models.abstract_cluster import AbstractCluster
import os
import configparser
from pydantic import BaseModel, Field, create_model
from typing import Any


class ClientUtils:
    cp_url = None
    username = None
    token = None
    _current_project: Stack = None  # Use a private variable for the current project
    _current_environment: AbstractCluster = None

    @staticmethod
    def set_client_config(url: str, user: str, tok: str):
        ClientUtils.cp_url = url
        ClientUtils.username = user
        ClientUtils.token = tok

    @staticmethod
    def get_client():
        if ClientUtils.cp_url is None or ClientUtils.username is None or ClientUtils.token is None:
            raise ValueError("Client configuration not set. Call set_client_config first.")

        configuration = swagger_client.Configuration()
        configuration.username = ClientUtils.username
        configuration.password = ClientUtils.token
        configuration.host = ClientUtils.cp_url
        return swagger_client.ApiClient(configuration)

    @staticmethod
    def initialize():
        """
        Initialize configuration from environment variables or a credentials file.
        Ensures the control plane URL has https:// prefix and no trailing slash.

        Returns:
            tuple: containing cp_url, username, token, and profile.

        Raises:
            ValueError: If profile is not specified or if required credentials are missing.
        """
        profile = os.getenv("FACETS_PROFILE", "")
        cp_url = os.getenv("CONTROL_PLANE_URL", "")
        username = os.getenv("FACETS_USERNAME", "")
        token = os.getenv("FACETS_TOKEN", "")

        if profile and not (cp_url and username and token):
            # Assume credentials exist in ~/.facets/credentials
            config = configparser.ConfigParser()
            config.read(os.path.expanduser("~/.facets/credentials"))

            if config.has_section(profile):
                cp_url = config.get(profile, "control_plane_url", fallback=cp_url)
                username = config.get(profile, "username", fallback=username)
                token = config.get(profile, "token", fallback=token)
            else:
                raise ValueError(f"Profile '{profile}' not found in credentials file.")

        if not (cp_url and username and token):
            raise ValueError("Control plane URL, username, and token are required.")

        # Ensure cp_url has https:// prefix
        if cp_url and not (cp_url.startswith("http://") or cp_url.startswith("https://")):
            cp_url = f"https://{cp_url}"

        # Remove trailing slash if present
        if cp_url and cp_url.endswith("/"):
            cp_url = cp_url.rstrip("/")

        ClientUtils.set_client_config(cp_url, username, token)
        return cp_url, username, token, profile

    @staticmethod
    def set_current_project(project: Stack):
        """
        Set the current project in the utils configuration.

        Args:
            project (Stack): The complete project object to set as current.
        """
        ClientUtils._current_project = project

    @staticmethod
    def set_current_cluster(environment: AbstractCluster):
        """
        Set the current environment in the utils configuration.

        Args:
            environment (AbstractCluster): The complete environment object to set as current.
        """
        ClientUtils._current_environment = environment

    @staticmethod
    def get_current_project() -> Stack:
        """
        Get the current project object.

        Returns:
            Stack: The current project object.
        """
        return ClientUtils._current_project

    @staticmethod
    def get_current_cluster() -> AbstractCluster:
        """
        Get the current environment object.

        Returns:
            AbstractCluster: The current environment object.
        """
        return ClientUtils._current_environment

    @staticmethod
    def is_current_cluster_and_project_set() -> bool:
        """
        This will return true if the current environment is set and current project is set. 

        Returns:
            bool: True if the current environment is set and current project is set.
        """
        return ClientUtils._current_environment is not None and ClientUtils._current_project is not None
    
    @staticmethod
    def pydantic_instance_to_swagger_instance(pydantic_instance, swagger_class):
        swagger_kwargs = {}
        alias_map = swagger_class.attribute_map
        reverse_alias_map = {v: k for k, v in alias_map.items()}

        for field_name, value in pydantic_instance.dict(by_alias=True, exclude_unset=True).items():
            # Map alias (JSON key) back to swagger attribute name
            swagger_field = reverse_alias_map.get(field_name, field_name)

            # Fix for internal naming like _global
            if swagger_field.startswith("_") or swagger_field in swagger_class.swagger_types:
                swagger_kwargs[swagger_field] = value
            else:
                # Handle renamed fields like global_ → _global
                if swagger_field + "_" in swagger_class.swagger_types:
                    swagger_kwargs[swagger_field + "_"] = value
                else:
                    swagger_kwargs[swagger_field] = value

        return swagger_class(**swagger_kwargs)

    @staticmethod
    def refresh_current_project_and_cache():
        """
        Refresh the current project data from the server and update the cache.
        """
        curr_project = ClientUtils.get_current_project()
        if not curr_project:
            raise ValueError("No current project is set.")

        api_instance = swagger_client.UiStackControllerApi(ClientUtils.get_client())
        refreshed_project = api_instance.get_stack(curr_project.name)
        ClientUtils.set_current_project(refreshed_project)

    @staticmethod
    def extract_error_message(e):
        """
        Extract a user-friendly error message from an exception, especially HTTP errors.
        Checks for 'message', 'error', or 'detail' fields in the response body.
        """
        error_message = None
        if hasattr(e, 'body'):
            try:
                import json
                body = json.loads(e.body)
                error_message = (
                    body.get('message') or
                    body.get('error') or
                    body.get('detail') or
                    str(body)
                )
            except Exception:
                error_message = str(e)
        else:
            error_message = str(e)
        return error_message

    @staticmethod
    def resolve_project(project_name: str = None) -> Stack:
        """
        Resolve project from parameter or current context.

        Args:
            project_name: Optional project name to fetch. If None or empty, uses current project context.

        Returns:
            Stack: The resolved project object.

        Raises:
            ValueError: If project_name is provided but project doesn't exist, or if no current project is set.
        """
        # Normalize: treat empty strings as None
        project_name = project_name.strip() if project_name else None

        if project_name:
            # Fetch project by name from API
            api_instance = swagger_client.UiStackControllerApi(ClientUtils.get_client())
            try:
                project = api_instance.get_stack(project_name)
                return project
            except Exception as e:
                error_message = ClientUtils.extract_error_message(e)
                raise ValueError(f"Failed to fetch project '{project_name}': {error_message}")
        else:
            # Use current project context
            project = ClientUtils.get_current_project()
            if not project:
                raise ValueError("No current project is set. Please set a project using use_project() or provide project_name parameter.")
            return project

    @staticmethod
    def resolve_environment(env_name: str = None, project: Stack = None) -> AbstractCluster:
        """
        Resolve environment from parameter or current context.

        Args:
            env_name: Optional environment name to fetch. If None or empty, uses current environment context.
            project: Optional project object to search for environment. Required if env_name is provided.

        Returns:
            AbstractCluster: The resolved environment object.

        Raises:
            ValueError: If env_name is provided but environment doesn't exist, or if no current environment is set.
        """
        # Normalize: treat empty strings as None
        env_name = env_name.strip() if env_name else None

        if env_name:
            # Fetch environment by name
            if not project:
                raise ValueError("Project is required when resolving environment by env_name.")

            api_instance = swagger_client.UiStackControllerApi(ClientUtils.get_client())
            try:
                environments = api_instance.get_clusters(project.name)
                # Find environment by name
                found_environment = None
                for env in environments:
                    if env.name == env_name:
                        found_environment = env
                        break

                if not found_environment:
                    raise ValueError(f"Environment '{env_name}' not found in project '{project.name}'.")

                return found_environment
            except Exception as e:
                error_message = ClientUtils.extract_error_message(e)
                raise ValueError(f"Failed to fetch environment '{env_name}': {error_message}")
        else:
            # Use current environment context
            environment = ClientUtils.get_current_cluster()
            if not environment:
                raise ValueError("No current environment is set. Please set an environment using use_environment() or provide env_name parameter.")
            return environment
