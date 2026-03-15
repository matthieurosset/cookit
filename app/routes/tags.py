from flask import Blueprint, render_template, request, redirect, url_for, flash

from ..models import tag as tag_model

bp = Blueprint('tags', __name__)


@bp.route('/tags')
def index():
    tags = tag_model.list_all_with_counts()
    return render_template('tags/manage.html', tags=tags)


@bp.route('/tags/nouveau', methods=['POST'])
def create():
    name = request.form.get('name', '').strip()
    if name:
        tag_model.create(name)
        flash('Tag créé !', 'success')
    if request.headers.get('HX-Request'):
        tags = tag_model.list_all_with_counts()
        return render_template('tags/partials/tag_list.html', tags=tags)
    return redirect(url_for('tags.index'))


@bp.route('/tags/<int:tag_id>/supprimer', methods=['POST'])
def delete(tag_id):
    tag_model.delete(tag_id)
    flash('Tag supprimé.', 'success')
    if request.headers.get('HX-Request'):
        tags = tag_model.list_all_with_counts()
        return render_template('tags/partials/tag_list.html', tags=tags)
    return redirect(url_for('tags.index'))
