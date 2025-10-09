import re
import traceback
import typing as tp
import urllib
from datetime import timedelta

import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import requests
from google.auth import impersonated_credentials
from google.cloud import storage


def get_bucket_and_path(gcs_full_path: str) -> tp.Tuple[str, str]:
    """Splits a google cloud storage path into bucket_name and the rest
    of the path without the 'gs://' at the beginning

    Args:
        gcs_full_path (str): A valid Gcloud Storage path

    Raises:
        ValueError: If input path does not start with gs://

    Returns:
        tp.Tuple[str]: Bucket name and the rest of the path
    """
    m = re.match(r"(gs://)([^/]+)/(.*)", gcs_full_path)

    if m is None:
        raise ValueError("path is not valid, it needs to start with 'gs://'")

    bucket = m.group(2)
    file_path = m.group(3)
    return bucket, file_path


def gcs_to_http(url: str) -> str:
    """
    Parses a url to a http url.

    Args:
        url (str): The url to parse.

    Returns:
        str: The http url.
    """
    return url.replace("gs://", "https://storage.cloud.google.com/")


def gcs_to_storage_search(url: str) -> str:
    """
    Parses a url to a http url.

    Args:
        url (str): The url to parse.

    Returns:
        str: The http url.
    """
    # Remove the gs:// prefix
    url = url.replace("gs://", "")
    # get the bucket
    splitted = url.split("/")
    bucket = splitted[0]
    # get the path
    path = "/".join(splitted[1:])
    path_web = urllib.parse.quote(path)
    url = f"https://console.cloud.google.com/storage/browser/{bucket};tab=objects?prefix={path_web}&forceOnObjectsSortingFiltering=false"
    return url


def generate_download_signed_url_v4(
    gcs_path: str,
    storage_client: storage.Client,
    signing_credentials: google.oauth2.credentials.Credentials,
    expiration_mins: int = 30,
) -> str:
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    url = None
    try:
        bucket, file_path = get_bucket_and_path(gcs_path)
        bucket = storage_client.bucket(bucket)
        blob = bucket.blob(file_path)

        url = blob.generate_signed_url(
            version="v4",
            # This URL is valid for 15 minutes
            expiration=timedelta(minutes=expiration_mins),
            # Allow GET requests using this URL.
            method="GET",
            credentials=signing_credentials,
        )
    except Exception as e:
        print(f"Error getting signed URL: {e}")

    return url


def get_signing_credentials(
    target_principal: str,
) -> impersonated_credentials.Credentials:
    """
    Sign the credentials using the impersonated credentials of the target service account.

    The target service account is retrieved from the environment variable "TARGET_SERVICE_ACCOUNT".
    The scope for the impersonated credentials is set to "https://www.googleapis.com/auth/devstorage.read_only",
    which allows read-only access to Google Cloud Storage.

    Args:
        target_principal (str): The target service account to impersonate.

    Returns:
        impersonated_credentials.Credentials: The signed impersonated credentials.
    """
    # Get the default credentials and project
    credentials, _ = google.auth.default()

    # Create impersonated credentials with the target service account and scope
    signing_credentials = impersonated_credentials.Credentials(
        source_credentials=credentials,  # The source credentials
        target_principal=target_principal,  # The service account to impersonate
        target_scopes="https://www.googleapis.com/auth/devstorage.read_only",  # The scope for the impersonated credentials
        lifetime=10 * 60,  # The validity of the impersonated credentials in seconds
    )

    return signing_credentials


def get_google_auth_user() -> str:
    """!
    Get the user of the google auth
    @return: User of the google auth
    """
    try:
        credentials, _ = google.auth.default()
        # check if credentials has client_id attribute, if so it means we auth with a personal account
        personal_account = hasattr(credentials, "client_id")
        if personal_account:
            # For personal accounts, get email from Google's userinfo endpoint
            # Ensure we have a valid token
            if not credentials.valid:
                request = google.auth.transport.requests.Request()
                credentials.refresh(request)

            # Call Google's userinfo endpoint to get the user's email
            headers = {"Authorization": f"Bearer {credentials.token}"}
            response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                user_info = response.json()
                return user_info.get("email", credentials.client_id)
            return credentials.client_id  # This is NOT the email!
        else:
            return credentials.service_account_email
    except Exception as e:
        print(f"Error getting user info: {e}")
        traceback.print_exc()
        return "Unknown"
