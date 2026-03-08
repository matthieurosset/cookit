from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from ..models import shopping as shopping_model
from ..models import recipe as recipe_model

bp = Blueprint('shopping', __name__)


@bp.route('/courses')
def index():
    lst = shopping_model.get_or_create_list()
    items = shopping_model.get_items(lst['id'])
    recipes = recipe_model.list_all()

    grouped = {}
    free_items = []
    for item in items:
        if item['recipe_id']:
            key = item['recipe_id']
            if key not in grouped:
                grouped[key] = {'title': item['recipe_title'] or 'Recette supprimée', 'entries': []}
            grouped[key]['entries'].append(item)
        else:
            free_items.append(item)

    frequent = shopping_model.get_frequent_items(10)
    return render_template('shopping/index.html', list=lst, items=items,
                           grouped=grouped, free_items=free_items,
                           recipes=recipes, frequent=frequent)


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

    if request.headers.get('HX-Request'):
        return _render_items_partial(lst['id'])
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


@bp.route('/courses/item/<int:item_id>/supprimer', methods=['DELETE'])
def delete_item(item_id):
    from ..db import query
    item = query('SELECT * FROM shopping_item WHERE id = ?', [item_id], one=True)
    list_id = item['list_id'] if item else None
    shopping_model.delete_item(item_id)
    if list_id and request.headers.get('HX-Request'):
        return _render_items_partial(list_id)
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


def _render_items_partial(list_id):
    items = shopping_model.get_items(list_id)
    grouped = {}
    free_items = []
    for item in items:
        if item['recipe_id']:
            key = item['recipe_id']
            if key not in grouped:
                grouped[key] = {'title': item['recipe_title'] or 'Recette supprimée', 'entries': []}
            grouped[key]['entries'].append(item)
        else:
            free_items.append(item)
    return render_template('shopping/partials/items.html',
                           grouped=grouped, free_items=free_items)
