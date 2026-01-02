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


def save_profile_photo(file, upload_folder, doctor_id, max_size_mb=5):
    """
    Save and optimize a doctor's profile photo

    Args:
        file: FileStorage object from request.files
        upload_folder: Base upload folder path
        doctor_id: ID of the doctor
        max_size_mb: Maximum file size in MB (default 5MB)

    Returns:
        Relative path to saved photo, or None if save failed
    """
    if not file or file.filename == '':
        return None

    # Validate file type - only images allowed
    if not allowed_file(file.filename, 'image'):
        raise ValueError(f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS['image'])}")

    # Validate file size
    if not validate_file_size(file, max_mb=max_size_mb):
        raise ValueError(f"File too large. Maximum size: {max_size_mb}MB")

    # Validate image dimensions
    is_valid, message = validate_image_dimensions(file, min_width=100, min_height=100)
    if not is_valid:
        raise ValueError(message)

    # Create photos directory
    photos_folder = os.path.join(upload_folder, 'photos')
    os.makedirs(photos_folder, exist_ok=True)

    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename)

    # Save and optimize image
    filepath = os.path.join(photos_folder, unique_filename)

    try:
        # Open and process image
        img = Image.open(file)

        # Convert RGBA to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Resize if image is too large (max 800x800 for profile photos)
        max_dimension = 800
        if img.width > max_dimension or img.height > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        # Save optimized image to BytesIO first (for R2 upload)
        from io import BytesIO
        img_bytes = BytesIO()
        img.save(img_bytes, 'JPEG', quality=85, optimize=True)

        # Try to upload to R2 first
        import r2_storage
        r2_path = None
        try:
            r2_path = r2_storage.save_profile_photo(img_bytes, doctor_id, unique_filename)
        except Exception as e:
            print(f"[R2] Photo upload failed, falling back to local storage: {e}")

        # If R2 upload succeeded, return R2 path
        if r2_path:
            print(f"[R2] Photo uploaded successfully to R2: {r2_path}")
            return r2_path

        # Fallback: Save to local storage
        try:
            img_bytes.seek(0)
        except Exception:
            pass

        with open(filepath, 'wb') as f:
            f.write(img_bytes.getvalue())

        # Return relative path for local storage
        relative_path = os.path.join('photos', unique_filename)
        print(f"[Local] Photo saved to local storage: {relative_path}")
        return relative_path

    except Exception as e:
        # If save fails, clean up and raise error
        if os.path.exists(filepath):
            os.remove(filepath)
        raise ValueError(f"Error processing image: {str(e)}")


def delete_profile_photo(upload_folder, relative_path):
    """
    Delete a profile photo from R2 or local filesystem

    Args:
        upload_folder: Base upload folder path
        relative_path: Relative path to the photo (R2 or local)

    Returns:
        Boolean indicating if deletion was successful
    """
    if not relative_path:
        return False

    # Check if this is an R2 path (format: photos/{doctor_id}/{filename})
    # R2 paths have doctor ID in them, local paths are just photos/{filename}
    import r2_storage

    if relative_path.count('/') > 1:  # R2 path has multiple slashes
        # Try to delete from R2
        try:
            result = r2_storage.delete_profile_photo(relative_path)
            if result:
                print(f"[R2] Photo deleted from R2: {relative_path}")
                return True
        except Exception as e:
            print(f"[R2] Error deleting from R2, trying local: {e}")

    # Try local storage (fallback or for old photos)
    full_path = os.path.join(upload_folder, relative_path)

    try:
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"[Local] Photo deleted from local storage: {relative_path}")
            return True
        return False
    except Exception as e:
        print(f"Error deleting photo {full_path}: {e}")
        return False
