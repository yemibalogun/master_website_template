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
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, unique_filename)
    
    file.save(file_path)
    
    # Return URL (local for dev, S3 URL in production)
    return f"/{upload_folder}/{unique_filename}"