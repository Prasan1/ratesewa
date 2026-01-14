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
        # R2 requires specific config to work with boto3
        from botocore.config import Config as BotoConfig

        boto_config = BotoConfig(
            signature_version='s3v4',
            s3={
                'addressing_style': 'path'
            }
        )

        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name='auto',  # R2 uses 'auto' for region
            config=boto_config
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

            print(f"[R2] Attempting upload to bucket '{self.bucket_name}', object '{object_name}'")

            # Upload file
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_name,
                ExtraArgs=extra_args
            )

            print(f"[R2] ✓ Upload successful: {object_name}")
            return object_name

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            print(f"[R2] ✗ ClientError uploading file: {error_code} - {error_msg}")
            print(f"[R2] Full error: {e}")
            return None
        except Exception as e:
            print(f"[R2] ✗ Unexpected error uploading file: {type(e).__name__}: {e}")
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
        print("[R2] Credentials not configured, falling back to local storage")
        return None

    print(f"[R2] Initializing with bucket: {bucket_name}, endpoint: {endpoint_url}")

    # Initialize R2 client
    try:
        r2 = R2Storage(access_key_id, secret_access_key, endpoint_url, bucket_name)
    except Exception as e:
        print(f"[R2] Failed to initialize R2Storage: {type(e).__name__}: {e}")
        return None

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


def save_profile_photo(file_obj, doctor_id, filename):
    """
    Save profile photo to R2

    Args:
        file_obj: File object (can be BytesIO from PIL or file from request.files)
        doctor_id: Doctor ID
        filename: Filename to use

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
        print("[R2] Credentials not configured for photo upload, falling back to local storage")
        return None

    print(f"[R2] Initializing for photo upload: {filename}")

    # Initialize R2 client
    try:
        r2 = R2Storage(access_key_id, secret_access_key, endpoint_url, bucket_name)
    except Exception as e:
        print(f"[R2] Failed to initialize R2Storage for photo: {type(e).__name__}: {e}")
        return None

    # Create R2 object path: photos/{doctor_id}/{filename}
    object_name = f"photos/{doctor_id}/{filename}"

    # Reset file pointer to beginning
    try:
        file_obj.seek(0)
    except Exception:
        pass  # File might not support seek

    # Upload to R2
    result = r2.upload_file(file_obj, object_name, 'image/jpeg')

    if result:
        return object_name
    return None


def delete_profile_photo(object_name):
    """
    Delete profile photo from R2

    Args:
        object_name: R2 object path

    Returns:
        bool: True if successful, False otherwise
    """
    # Get R2 credentials from environment
    access_key_id = os.getenv('R2_ACCESS_KEY_ID', '').strip()
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY', '').strip()
    endpoint_url = os.getenv('R2_ENDPOINT_URL', '').strip()
    bucket_name = os.getenv('R2_BUCKET_NAME', 'ranksewa-documents').strip()

    # Check if R2 is configured
    if not all([access_key_id, secret_access_key, endpoint_url]):
        return False

    # Initialize R2 client
    try:
        r2 = R2Storage(access_key_id, secret_access_key, endpoint_url, bucket_name)
        return r2.delete_file(object_name)
    except Exception as e:
        print(f"[R2] Error deleting photo: {e}")
        return False


def save_clinic_logo(file_obj, clinic_id, filename):
    """
    Save clinic logo to R2

    Args:
        file_obj: File object (can be BytesIO from PIL or file from request.files)
        clinic_id: Clinic ID
        filename: Filename to use

    Returns:
        str: R2 object path if successful, None otherwise
    """
    # Get R2 credentials from environment
    access_key_id = os.getenv('R2_ACCESS_KEY_ID', '').strip()
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY', '').strip()
    endpoint_url = os.getenv('R2_ENDPOINT_URL', '').strip()
    bucket_name = os.getenv('R2_BUCKET_NAME', 'ranksewa-documents').strip()

    # Check if R2 is configured
    if not all([access_key_id, secret_access_key, endpoint_url]):
        print("[R2] Credentials not configured for clinic logo upload, falling back to local storage")
        return None

    print(f"[R2] Initializing for clinic logo upload: {filename}")

    # Initialize R2 client
    try:
        r2 = R2Storage(access_key_id, secret_access_key, endpoint_url, bucket_name)
    except Exception as e:
        print(f"[R2] Failed to initialize R2Storage for clinic logo: {type(e).__name__}: {e}")
        return None

    # Create R2 object path: clinic_logos/{clinic_id}/{filename}
    object_name = f"clinic_logos/{clinic_id}/{filename}"

    # Reset file pointer to beginning
    try:
        file_obj.seek(0)
    except Exception:
        pass

    # Upload to R2
    result = r2.upload_file(file_obj, object_name, 'image/jpeg')

    if result:
        return object_name
    return None


def delete_clinic_logo(object_name):
    """
    Delete clinic logo from R2

    Args:
        object_name: R2 object path

    Returns:
        bool: True if successful, False otherwise
    """
    # Get R2 credentials from environment
    access_key_id = os.getenv('R2_ACCESS_KEY_ID', '').strip()
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY', '').strip()
    endpoint_url = os.getenv('R2_ENDPOINT_URL', '').strip()
    bucket_name = os.getenv('R2_BUCKET_NAME', 'ranksewa-documents').strip()

    # Check if R2 is configured
    if not all([access_key_id, secret_access_key, endpoint_url]):
        return False

    # Initialize R2 client
    try:
        r2 = R2Storage(access_key_id, secret_access_key, endpoint_url, bucket_name)
        return r2.delete_file(object_name)
    except Exception as e:
        print(f"[R2] Error deleting clinic logo: {e}")
        return False


def get_clinic_logo(object_name):
    """
    Get clinic logo from R2

    Args:
        object_name: R2 object path

    Returns:
        bytes: File content if successful, None otherwise
    """
    # Get R2 credentials from environment
    access_key_id = os.getenv('R2_ACCESS_KEY_ID', '').strip()
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY', '').strip()
    endpoint_url = os.getenv('R2_ENDPOINT_URL', '').strip()
    bucket_name = os.getenv('R2_BUCKET_NAME', 'ranksewa-documents').strip()

    # Check if R2 is configured
    if not all([access_key_id, secret_access_key, endpoint_url]):
        return None

    # Initialize R2 client
    try:
        r2 = R2Storage(access_key_id, secret_access_key, endpoint_url, bucket_name)
        return r2.get_file_object(object_name)
    except Exception as e:
        print(f"[R2] Error getting clinic logo: {e}")
        return None
