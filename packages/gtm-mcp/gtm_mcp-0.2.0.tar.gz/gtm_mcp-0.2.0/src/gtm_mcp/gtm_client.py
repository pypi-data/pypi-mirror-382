import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from google.auth.credentials import TokenState
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SERVICE_NAME = 'tagmanager'
VERSION = 'v2'
TOKEN_FILE = Path.home() / '.gtm-mcp' / 'token.json'
SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.delete.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
    "https://www.googleapis.com/auth/tagmanager.manage.accounts",
    "https://www.googleapis.com/auth/tagmanager.manage.users",
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/tagmanager.readonly"
]

def get_client_config() -> Dict[str, Any]:
    """
    Get OAuth client configuration from environment variables.

    Users must set these environment variables:
    - GTM_CLIENT_ID: Your Google OAuth Client ID
    - GTM_CLIENT_SECRET: Your Google OAuth Client Secret
    - GTM_PROJECT_ID: Your Google Cloud Project ID

    See setup guide for instructions on creating these credentials.
    """
    client_id = os.getenv("GTM_CLIENT_ID")
    client_secret = os.getenv("GTM_CLIENT_SECRET")
    project_id = os.getenv("GTM_PROJECT_ID")

    if not client_id or not client_secret:
        raise ValueError(
            "Missing required OAuth credentials!\n\n"
            "Please set the following environment variables:\n"
            "  - GTM_CLIENT_ID\n"
            "  - GTM_CLIENT_SECRET\n"
            "  - GTM_PROJECT_ID (optional)\n\n"
            "See the setup guide for instructions:\n"
            "https://github.com/paolbtl/gtm-mcp/blob/main/SETUP.md"
        )

    return {
        "installed": {
            "client_id": client_id,
            "project_id": project_id or "gtm-mcp",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"]
        }
    }

class GTMClient:
    def __init__(self):
        self.service = None
        self.credentials = None
        self._authenticate()
    def _authenticate(self):
        credentials = None

        # Load existing token if available
        if TOKEN_FILE.exists():
            try:
                credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            except Exception as e:
                print(f"Warning: Could not load token file: {e}")
                credentials = None

        # Refresh expired credentials or run OAuth flow
        if credentials and credentials.token_state != TokenState.FRESH and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
                TOKEN_FILE.write_text(credentials.to_json())
            except Exception as e:
                print(f"Warning: Could not refresh token: {e}")
                credentials = None

        # Run OAuth flow if no valid credentials
        if not credentials or not credentials.valid:
            client_config = get_client_config()
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            credentials = flow.run_local_server(port=0)
            
        # Save credentials for future use
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(credentials.to_json())

        self.credentials = credentials
        self.service = build(SERVICE_NAME, VERSION, credentials=self.credentials)
    def list_accounts(self) -> List[Dict[str, Any]]:
        "List all Google Tag Manager accounts"
        try:
            response = self.service.accounts().list().execute()
            return response.get("account",[])
        except HttpError as e:
            raise Exception(f"Failed to list accounts: {e}")
    def list_containers(self, account_id: str) -> List[Dict[str, Any]]:
        try:
            parent = f"accounts/{account_id}"
            response = self.service.accounts().containers().list(parent=parent).execute()
            return response.get('container', [])
        except HttpError as e:
            raise Exception(f"Failed to list containers: {e}")
    def get_container(self, container_path: str) -> Dict[str, Any]:
        """Get container details."""
        try:
            return self.service.accounts().containers().get(path=container_path).execute()
        except HttpError as e:
            raise Exception(f"Failed to get container: {e}")
    
    def list_workspaces(self, container_path: str) -> List[Dict[str, Any]]:
        """List all workspaces in a container."""
        try:
            response = self.service.accounts().containers().workspaces().list(
                parent=container_path
            ).execute()
            return response.get('workspace', [])
        except HttpError as e:
            raise Exception(f"Failed to list workspaces: {e}")
    
    def list_tags(self, workspace_path: str) -> List[Dict[str, Any]]:
        """List all tags in a workspace."""
        try:
            response = self.service.accounts().containers().workspaces().tags().list(
                parent=workspace_path
            ).execute()
            return response.get('tag', [])
        except HttpError as e:
            raise Exception(f"Failed to list tags: {e}")
    
    def get_tag(self, tag_path: str) -> Dict[str, Any]:
        """Get a specific tag's details."""
        try:
            return self.service.accounts().containers().workspaces().tags().get(
                path=tag_path
            ).execute()
        except HttpError as e:
            raise Exception(f"Failed to get tag: {e}")

    def create_tag(self, workspace_path: str, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tag in a workspace."""
        try:
            return self.service.accounts().containers().workspaces().tags().create(
                parent=workspace_path,
                body=tag_data
            ).execute()
        except HttpError as e:
            raise Exception(f"Failed to create tag: {e}")
    
    def update_tag(self, tag_path: str, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing tag."""
        try:
            return self.service.accounts().containers().workspaces().tags().update(
                path=tag_path,
                body=tag_data
            ).execute()
        except HttpError as e:
            raise Exception(f"Failed to update tag: {e}")
    
    def list_triggers(self, workspace_path: str) -> List[Dict[str, Any]]:
        """List all triggers in a workspace."""
        try:
            response = self.service.accounts().containers().workspaces().triggers().list(
                parent=workspace_path
            ).execute()
            return response.get('trigger', [])
        except HttpError as e:
            raise Exception(f"Failed to list triggers: {e}")
    
    def create_trigger(self, workspace_path: str, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new trigger in a workspace."""
        try:
            return self.service.accounts().containers().workspaces().triggers().create(
                parent=workspace_path,
                body=trigger_data
            ).execute()
        except HttpError as e:
            raise Exception(f"Failed to create trigger: {e}")
    
    def list_variables(self, workspace_path: str) -> List[Dict[str, Any]]:
        """List all variables in a workspace."""
        try:
            response = self.service.accounts().containers().workspaces().variables().list(
                parent=workspace_path
            ).execute()
            return response.get('variable', [])
        except HttpError as e:
            raise Exception(f"Failed to list variables: {e}")

    def get_variable(self, variable_path: str) -> Dict[str, Any]:
        """Get a specific variable's details."""
        try:
            return self.service.accounts().containers().workspaces().variables().get(
                path=variable_path
            ).execute()
        except HttpError as e:
            raise Exception(f"Failed to get variable: {e}")

    def create_variable(self, workspace_path: str, variable_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new variable in a workspace."""
        try:
            return self.service.accounts().containers().workspaces().variables().create(
                parent=workspace_path,
                body=variable_data
            ).execute()
        except HttpError as e:
            raise Exception(f"Failed to create variable: {e}")

    def update_variable(self, variable_path: str, variable_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing variable."""
        try:
            return self.service.accounts().containers().workspaces().variables().update(
                path=variable_path,
                body=variable_data
            ).execute()
        except HttpError as e:
            raise Exception(f"Failed to update variable: {e}")

    def create_version(self, workspace_path: str, name: str, notes: str = "") -> Dict[str, Any]:
        """Create a new container version."""
        try:
            version_data = {
                "name": name,
                "notes": notes
            }
            return self.service.accounts().containers().workspaces().create_version(
                path=workspace_path,
                body=version_data
            ).execute()
        except HttpError as e:
            raise Exception(f"Failed to create version: {e}")
    
    def publish_version(self, version_path: str) -> Dict[str, Any]:
        """Publish a container version."""
        try:
            return self.service.accounts().containers().versions().publish(
                path=version_path
            ).execute()
        except HttpError as e:
            raise Exception(f"Failed to publish version: {e}")