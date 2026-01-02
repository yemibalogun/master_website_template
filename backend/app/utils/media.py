import os
import uuid 
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if not allowed_file(file.filename):
        raise ValueError("File type not allowed")
    
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, unique_filename)
    
    file.save(file_path)
    
    # Return URL (local for dev, S3 URL in production)
    return f"/{upload_folder}/{unique_filename}"


def delete_file(file_url):
    """
    Deletes a file given its URL or path.
    Converts URL to local path if necessary.
    """
    if not file_url:
        return False

    # Remove leading slash if present
    file_path = file_url.lstrip('/')

    # Convert relative URL to absolute path
    if not os.path.isabs(file_path):
        file_path = os.path.join(current_app.root_path, file_path)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    return False