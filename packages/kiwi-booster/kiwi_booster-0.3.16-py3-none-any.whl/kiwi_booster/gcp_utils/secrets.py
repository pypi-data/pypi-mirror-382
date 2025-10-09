"""
sadas
"""
import google.auth
import google.auth.transport.requests
import google_crc32c
from google.auth import impersonated_credentials
from google.cloud import secretmanager


def access_secret_version(secret_id: str, version_id: str, project_id: str) -> str:
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Verify payload checksum.
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    success = True
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        print("Data corruption detected.")
        success = False

    if not success:
        raise ValueError("Secret not found")

    return response.payload.data.decode("UTF-8")


def get_token(url: str, target_principal: str) -> str:
    """
    Get a token to authenticate the user for the API calls using impersonation.

    Args:
        url (str): URL of the API
        target_principal (str): Email of the user to impersonate

    Returns:
        token (str): Token to authenticate the user
    """
    target_scopes = ["https://www.googleapis.com/auth/cloud-platform"]

    personal_creds, _ = google.auth.default()

    target_credentials = impersonated_credentials.Credentials(
        source_credentials=personal_creds,
        target_principal=target_principal,
        target_scopes=target_scopes,
        lifetime=3600,
    )

    token_credentials = impersonated_credentials.IDTokenCredentials(
        target_credentials, target_audience=url
    )
    request = google.auth.transport.requests.Request()
    token_credentials.refresh(request)

    return token_credentials.token
