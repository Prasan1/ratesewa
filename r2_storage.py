"""
Cloudflare R2 Storage Utility
Handles file uploads and downloads to/from Cloudflare R2
"""
import os
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename

class R2Storage:
    """Cloudflare R2 Storage Manager"""

    def __init__(self, access_key_id, secret_access_key, endpoint_url, bucket_name):
        """
        Initialize R2 client

        Args:
            access_key_id: R2 Access Key ID
            secret_access_key: R2 Secret Access Key
            endpoint_url: R2 Endpoint URL
            bucket_name: R2 Bucket Name
        """
        self.bucket_name = bucket_name

        # Initialize S3-compatible client for R2
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name='auto'  # R2 uses 'auto' for region
        )

    def upload_file(self, file_obj, object_name, content_type=None):
        """
        Upload a file to R2

        Args:
            file_obj: File object to upload (from request.files)
            object_name: S3 object name (path in bucket)
            content_type: MIME type of file (optional)

        Returns:
            str: Object name if successful, None otherwise
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            # Upload file
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_name,
                ExtraArgs=extra_args
            )

            print(f"File uploaded successfully to R2: {object_name}")
            return object_name

        except ClientError as e:
            print(f"Error uploading file to R2: {e}")
            return None

    def upload_file_from_path(self, file_path, object_name, content_type=None):
        """
        Upload a file from local path to R2

        Args:
            file_path: Local file path
            object_name: S3 object name (path in bucket)
            content_type: MIME type of file (optional)

        Returns:
            str: Object name if successful, None otherwise
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            # Upload file
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                object_name,
                ExtraArgs=extra_args
            )

            print(f"File uploaded successfully to R2: {object_name}")
            return object_name

        except ClientError as e:
            print(f"Error uploading file to R2: {e}")
            return None

    def download_file(self, object_name, download_path):
        """
        Download a file from R2 to local path

        Args:
            object_name: S3 object name (path in bucket)
            download_path: Local path to save file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.s3_client.download_file(
                self.bucket_name,
                object_name,
                download_path
            )
            print(f"File downloaded successfully from R2: {object_name}")
            return True

        except ClientError as e:
            print(f"Error downloading file from R2: {e}")
            return False

    def get_file_object(self, object_name):
        """
        Get file object from R2 (for streaming)

        Args:
            object_name: S3 object name (path in bucket)

        Returns:
            bytes: File content if successful, None otherwise
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
            return response['Body'].read()

        except ClientError as e:
            print(f"Error getting file from R2: {e}")
            return None

    def delete_file(self, object_name):
        """
        Delete a file from R2

        Args:
            object_name: S3 object name (path in bucket)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
            print(f"File deleted successfully from R2: {object_name}")
            return True

        except ClientError as e:
            print(f"Error deleting file from R2: {e}")
            return False

    def file_exists(self, object_name):
        """
        Check if file exists in R2

        Args:
            object_name: S3 object name (path in bucket)

        Returns:
            bool: True if exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
            return True
        except ClientError:
            return False


def save_verification_document(file, doctor_id, doc_type):
    """
    Save verification document to R2

    Args:
        file: File object from request.files
        doctor_id: Doctor ID or temp ID
        doc_type: Type of document (medical_degree, govt_id, practice_license)

    Returns:
        str: R2 object path if successful, None otherwise
    """
    # Get R2 credentials from environment (strip whitespace/newlines)
    access_key_id = os.getenv('R2_ACCESS_KEY_ID', '').strip()
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY', '').strip()
    endpoint_url = os.getenv('R2_ENDPOINT_URL', '').strip()
    bucket_name = os.getenv('R2_BUCKET_NAME', 'ranksewa-documents').strip()

    # Check if R2 is configured (all values must be non-empty after stripping)
    if not all([access_key_id, secret_access_key, endpoint_url]):
        print("R2 credentials not configured, falling back to local storage")
        return None

    # Initialize R2 client
    r2 = R2Storage(access_key_id, secret_access_key, endpoint_url, bucket_name)

    # Generate secure filename
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1]

    # Create R2 object path: verification/{doctor_id}/{doc_type}{ext}
    object_name = f"verification/{doctor_id}/{doc_type}{file_ext}"

    # Determine content type
    content_type = file.content_type or 'application/octet-stream'

    # Reset file pointer to beginning
    file.seek(0)

    # Upload to R2
    result = r2.upload_file(file, object_name, content_type)

    if result:
        return object_name
    return None


def get_verification_document(object_name):
    """
    Get verification document from R2

    Args:
        object_name: R2 object path

    Returns:
        bytes: File content if successful, None otherwise
    """
    # Get R2 credentials from environment (strip whitespace/newlines)
    access_key_id = os.getenv('R2_ACCESS_KEY_ID', '').strip()
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY', '').strip()
    endpoint_url = os.getenv('R2_ENDPOINT_URL', '').strip()
    bucket_name = os.getenv('R2_BUCKET_NAME', 'ranksewa-documents').strip()

    # Check if R2 is configured
    if not all([access_key_id, secret_access_key, endpoint_url]):
        return None

    # Initialize R2 client
    r2 = R2Storage(access_key_id, secret_access_key, endpoint_url, bucket_name)

    # Get file from R2
    return r2.get_file_object(object_name)


def delete_verification_document(object_name):
    """
    Delete verification document from R2

    Args:
        object_name: R2 object path

    Returns:
        bool: True if successful, False otherwise
    """
    # Get R2 credentials from environment (strip whitespace/newlines)
    access_key_id = os.getenv('R2_ACCESS_KEY_ID', '').strip()
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY', '').strip()
    endpoint_url = os.getenv('R2_ENDPOINT_URL', '').strip()
    bucket_name = os.getenv('R2_BUCKET_NAME', 'ranksewa-documents').strip()

    # Check if R2 is configured
    if not all([access_key_id, secret_access_key, endpoint_url]):
        return False

    # Initialize R2 client
    r2 = R2Storage(access_key_id, secret_access_key, endpoint_url, bucket_name)

    # Delete file from R2
    return r2.delete_file(object_name)
