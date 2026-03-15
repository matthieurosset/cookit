from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash

from ..models import shopping as shopping_model
from ..models.shopping import STORES, STORE_LABELS
from ..models import recipe as recipe_model

bp = Blueprint('shopping', __name__)


@bp.route('/courses')
def index():
    lst = shopping_model.get_or_create_list()
    items = shopping_model.get_items(lst['id'])
    grouped = _group_items(items)
    return render_template('shopping/index.html', list=lst, all_items=items,
                           grouped_items=grouped)


@bp.route('/courses/ajouter', methods=['POST'])
def add_item():
    lst = shopping_model.get_or_create_list()
    name = request.form.get('name', '').strip()
    quantity = request.form.get('quantity', '').strip() or None
    unit = request.form.get('unit', '').strip() or None

    if name:
        shopping_model.add_item(lst['id'], name, quantity, unit)

    if request.headers.get('HX-Request'):
        return _render_items_partial(lst['id'])
    return redirect(url_for('shopping.index'))


@bp.route('/courses/ajouter-recette', methods=['POST'])
def add_recipe():
    lst = shopping_model.get_or_create_list()
    recipe_id = request.form.get('recipe_id', type=int)
    portions = request.form.get('portions', type=int)

    if recipe_id:
        shopping_model.add_recipe_items(lst['id'], recipe_id, portions)
        flash('Ingrédients ajoutés aux courses', 'success')

    referrer = request.referrer
    if referrer and '/recettes/' in referrer:
        return redirect(referrer)
    return redirect(url_for('shopping.index'))


@bp.route('/courses/item/<int:item_id>/toggle', methods=['PATCH'])
def toggle_item(item_id):
    from ..db import query
    item = query('SELECT * FROM shopping_item WHERE id = ?', [item_id], one=True)
    if not item:
        return '', 404
    shopping_model.toggle_item(item_id)
    if request.headers.get('HX-Request'):
        return _render_items_partial(item['list_id'])
    return '', 204


@bp.route('/courses/item/<int:item_id>/quantite', methods=['PATCH'])
def update_quantity(item_id):
    from ..db import query as db_query
    delta = request.form.get('delta', type=float, default=1)
    item = db_query('SELECT * FROM shopping_item WHERE id = ?', [item_id], one=True)
    if not item:
        return '', 404
    shopping_model.update_quantity(item_id, delta)
    if request.headers.get('HX-Request'):
        return _render_items_partial(item['list_id'])
    return '', 204


@bp.route('/courses/item/<int:item_id>/supprimer', methods=['DELETE'])
def delete_item(item_id):
    from ..db import query
    item = query('SELECT * FROM shopping_item WHERE id = ?', [item_id], one=True)
    list_id = item['list_id'] if item else None
    shopping_model.delete_item(item_id)
    if list_id and request.headers.get('HX-Request'):
        return _render_items_partial(list_id)
    return '', 204


@bp.route('/courses/item/<int:item_id>/magasin/<store>', methods=['PATCH'])
def set_store(item_id, store):
    from ..db import query
    if store not in ('migros', 'coop'):
        return '', 400
    item = query('SELECT * FROM shopping_item WHERE id = ?', [item_id], one=True)
    if not item:
        return '', 404
    shopping_model.set_store(item_id, store)
    if request.headers.get('HX-Request'):
        return _render_items_partial(item['list_id'])
    return '', 204


@bp.route('/courses/vider-coches', methods=['POST'])
def clear_checked():
    lst = shopping_model.get_or_create_list()
    shopping_model.clear_checked(lst['id'])
    if request.headers.get('HX-Request'):
        return _render_items_partial(lst['id'])
    return redirect(url_for('shopping.index'))


@bp.route('/courses/vider', methods=['POST'])
def clear_all():
    lst = shopping_model.get_or_create_list()
    shopping_model.clear_all(lst['id'])
    if request.headers.get('HX-Request'):
        return _render_items_partial(lst['id'])
    return redirect(url_for('shopping.index'))


@bp.route('/courses/suggestions')
def suggestions():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    results = shopping_model.get_suggestions(q)
    return jsonify(results)


def _group_items(items):
    """Group items by store, preserving store order."""
    groups = {}
    for store_key in STORES:
        groups[store_key] = []
    for item in items:
        key = item['store'] if item['store'] in STORES else None
        groups[key].append(item)
    return [{'key': k, 'label': STORE_LABELS[k], 'entries': groups[k]}
            for k in STORES if groups[k]]


def _render_items_partial(list_id):
    items = shopping_model.get_items(list_id)
    grouped = _group_items(items)
    return render_template('shopping/partials/items.html',
                           all_items=items, grouped_items=grouped)
