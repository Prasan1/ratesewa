"""
File upload utilities for doctor verification documents
Handles secure file upload, validation, and storage
"""
import os
import uuid
import hashlib
from werkzeug.utils import secure_filename
from PIL import Image


# Allowed file extensions for different document types
ALLOWED_EXTENSIONS = {
    'image': {'jpg', 'jpeg', 'png'},
    'document': {'pdf'},
    'all': {'jpg', 'jpeg', 'png', 'pdf'}
}

# Maximum file size in MB
MAX_FILE_SIZE_MB = 10


def allowed_file(filename, file_type='all'):
    """
    Check if file extension is allowed

    Args:
        filename: Name of the file
        file_type: Type of file ('image', 'document', 'all')

    Returns:
        Boolean indicating if file is allowed
    """
    if not filename or '.' not in filename:
        return False

    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS.get(file_type, ALLOWED_EXTENSIONS['all'])


def validate_file_size(file, max_mb=MAX_FILE_SIZE_MB):
    """
    Validate file size doesn't exceed maximum

    Args:
        file: FileStorage object
        max_mb: Maximum size in megabytes

    Returns:
        Boolean indicating if file size is valid
    """
    # Seek to end to get size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset to beginning

    max_bytes = max_mb * 1024 * 1024
    return file_size <= max_bytes


def get_file_size_mb(file):
    """
    Get file size in megabytes

    Args:
        file: FileStorage object

    Returns:
        Float representing file size in MB
    """
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset to beginning

    return file_size / (1024 * 1024)


def generate_unique_filename(original_filename):
    """
    Generate a unique filename while preserving extension

    Args:
        original_filename: Original file name

    Returns:
        Unique filename string
    """
    # Get extension
    extension = ''
    if '.' in original_filename:
        extension = '.' + original_filename.rsplit('.', 1)[1].lower()

    # Generate unique name using UUID
    unique_name = str(uuid.uuid4())

    return secure_filename(unique_name + extension)


def save_verification_document(file, upload_folder, doctor_id, doc_type):
    """
    Save a verification document to the filesystem

    Args:
        file: FileStorage object from request.files
        upload_folder: Base upload folder path
        doctor_id: ID of the doctor
        doc_type: Type of document ('medical_degree', 'govt_id', 'practice_license')

    Returns:
        Relative path to saved file, or None if save failed
    """
    if not file or file.filename == '':
        return None

    # Validate file type
    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS['all'])}")

    # Validate file size
    if not validate_file_size(file):
        raise ValueError(f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB")

    # Create doctor-specific directory
    doctor_folder = os.path.join(upload_folder, 'verification', str(doctor_id))
    os.makedirs(doctor_folder, exist_ok=True)

    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename)

    # Save file
    filepath = os.path.join(doctor_folder, unique_filename)
    file.save(filepath)

    # Return relative path (from upload_folder)
    relative_path = os.path.join('verification', str(doctor_id), unique_filename)

    # Validate if it's an image (optional quality check)
    if allowed_file(file.filename, 'image'):
        try:
            # Try to open and verify it's a valid image
            img = Image.open(filepath)
            img.verify()
        except Exception as e:
            # If image is invalid, delete it and raise error
            if os.path.exists(filepath):
                os.remove(filepath)
            raise ValueError(f"Invalid image file: {str(e)}")

    return relative_path


def delete_verification_document(upload_folder, relative_path):
    """
    Delete a verification document from filesystem

    Args:
        upload_folder: Base upload folder path
        relative_path: Relative path to the file

    Returns:
        Boolean indicating if deletion was successful
    """
    if not relative_path:
        return False

    full_path = os.path.join(upload_folder, relative_path)

    try:
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {full_path}: {e}")
        return False


def get_file_hash(filepath):
    """
    Calculate MD5 hash of a file (for duplicate detection)

    Args:
        filepath: Full path to the file

    Returns:
        MD5 hash string
    """
    hash_md5 = hashlib.md5()

    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error hashing file {filepath}: {e}")
        return None


def validate_image_dimensions(file, min_width=200, min_height=200, max_width=5000, max_height=5000):
    """
    Validate image dimensions

    Args:
        file: FileStorage object
        min_width, min_height: Minimum dimensions
        max_width, max_height: Maximum dimensions

    Returns:
        Tuple (is_valid: bool, message: str)
    """
    try:
        img = Image.open(file)
        width, height = img.size
        file.seek(0)  # Reset file pointer

        if width < min_width or height < min_height:
            return False, f"Image too small. Minimum: {min_width}x{min_height}px"

        if width > max_width or height > max_height:
            return False, f"Image too large. Maximum: {max_width}x{max_height}px"

        return True, "Valid"

    except Exception as e:
        file.seek(0)  # Reset file pointer
        return False, f"Invalid image: {str(e)}"


def get_upload_path(upload_folder, doctor_id, filename):
    """
    Get full path for uploaded file

    Args:
        upload_folder: Base upload folder
        doctor_id: Doctor ID
        filename: Filename

    Returns:
        Full file path
    """
    return os.path.join(upload_folder, 'verification', str(doctor_id), filename)
