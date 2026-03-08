import os
import uuid

from PIL import Image
from flask import current_app


def save_image(file_storage):
    """Save uploaded image, create thumbnail. Returns relative path."""
    if not file_storage or not file_storage.filename:
        return None

    ext = os.path.splitext(file_storage.filename)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp'):
        return None

    filename = f'{uuid.uuid4().hex}.jpg'
    upload_dir = current_app.config['UPLOAD_FOLDER']
    thumb_dir = os.path.join(upload_dir, 'thumbs')
    os.makedirs(thumb_dir, exist_ok=True)

    full_path = os.path.join(upload_dir, filename)
    thumb_path = os.path.join(thumb_dir, filename)

    img = Image.open(file_storage.stream)
    img = img.convert('RGB')

    # Main image: max 1200px wide
    if img.width > 1200:
        ratio = 1200 / img.width
        img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
    img.save(full_path, 'JPEG', quality=85)

    # Thumbnail: 400px wide
    ratio = 400 / img.width
    thumb = img.resize((400, int(img.height * ratio)), Image.LANCZOS)
    thumb.save(thumb_path, 'JPEG', quality=80)

    return filename


def delete_image(filename):
    """Delete image and its thumbnail."""
    if not filename:
        return

    upload_dir = current_app.config['UPLOAD_FOLDER']
    for path in [
        os.path.join(upload_dir, filename),
        os.path.join(upload_dir, 'thumbs', filename),
    ]:
        if os.path.exists(path):
            os.remove(path)
