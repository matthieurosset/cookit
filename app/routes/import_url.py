import json
import os
import uuid

import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

from ..services.scraper import fetch_recipe

bp = Blueprint('import_url', __name__)


@bp.route('/recettes/importer', methods=['GET', 'POST'])
def import_recipe():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if not url:
            flash('URL requise.', 'error')
            return render_template('recipes/import.html')

        data = fetch_recipe(url)
        if not data:
            flash('Impossible d\'extraire la recette. Vous pouvez la saisir manuellement.', 'error')
            from ..models import tag as tag_model
            tags = tag_model.list_all()
            return render_template('recipes/form.html', recipe=None, tags=tags,
                                   recipe_tags=[], prefill={'source_url': url})

        # Try to download image
        image_path = None
        if data.get('image_url'):
            image_path = _download_image(data['image_url'])

        from ..models import tag as tag_model
        tags = tag_model.list_all()

        # Pre-fill the form
        prefill = {
            'title': data['title'],
            'description': data['description'],
            'ingredients': data['ingredients'],
            'steps': data['steps'],
            'portions': data['portions'],
            'prep_time': data['prep_time'],
            'cook_time': data['cook_time'],
            'source_url': url,
            'image_path': image_path,
        }

        return render_template('recipes/form.html', recipe=None, tags=tags,
                               recipe_tags=[], prefill=prefill)

    return render_template('recipes/import.html')


def _download_image(image_url):
    """Download image from URL and save it."""
    try:
        resp = requests.get(image_url, timeout=15, stream=True, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; Cookit/1.0)'
        })
        resp.raise_for_status()

        content_type = resp.headers.get('content-type', '')
        if 'image' not in content_type:
            return None

        from PIL import Image
        from io import BytesIO

        img = Image.open(BytesIO(resp.content))
        img = img.convert('RGB')

        filename = f'{uuid.uuid4().hex}.jpg'
        upload_dir = current_app.config['UPLOAD_FOLDER']
        thumb_dir = os.path.join(upload_dir, 'thumbs')
        os.makedirs(thumb_dir, exist_ok=True)

        # Main image
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        img.save(os.path.join(upload_dir, filename), 'JPEG', quality=85)

        # Thumbnail
        ratio = 400 / img.width
        thumb = img.resize((400, int(img.height * ratio)), Image.LANCZOS)
        thumb.save(os.path.join(thumb_dir, filename), 'JPEG', quality=80)

        return filename
    except Exception:
        return None
