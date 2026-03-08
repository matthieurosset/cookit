import json

from flask import Blueprint, render_template, request, redirect, url_for, flash

from ..models import shopping as shopping_model
from ..models import recipe as recipe_model

bp = Blueprint('shopping', __name__)


@bp.route('/courses')
def index():
    lists = shopping_model.list_all()
    return render_template('shopping/lists.html', lists=lists)


@bp.route('/courses/nouvelle', methods=['POST'])
def create():
    name = request.form.get('name', '').strip()
    if name:
        list_id = shopping_model.create(name)
        return redirect(url_for('shopping.detail', list_id=list_id))
    flash('Nom requis.', 'error')
    return redirect(url_for('shopping.index'))


@bp.route('/courses/<int:list_id>')
def detail(list_id):
    lst = shopping_model.get(list_id)
    if not lst:
        flash('Liste introuvable.', 'error')
        return redirect(url_for('shopping.index'))

    items = shopping_model.get_items(list_id)
    recipes = recipe_model.list_all()

    # Group items by recipe
    grouped = {}
    free_items = []
    for item in items:
        if item['recipe_id']:
            key = item['recipe_id']
            if key not in grouped:
                grouped[key] = {'title': item['recipe_title'] or 'Recette supprimee', 'entries': []}
            grouped[key]['entries'].append(item)
        else:
            free_items.append(item)

    return render_template('shopping/detail.html', list=lst, items=items,
                           grouped=grouped, free_items=free_items, recipes=recipes)


@bp.route('/courses/<int:list_id>/ajouter', methods=['POST'])
def add_item(list_id):
    name = request.form.get('name', '').strip()
    quantity = request.form.get('quantity', '').strip() or None
    unit = request.form.get('unit', '').strip() or None

    if name:
        shopping_model.add_item(list_id, name, quantity, unit)

    if request.headers.get('HX-Request'):
        return _render_items_partial(list_id)
    return redirect(url_for('shopping.detail', list_id=list_id))


@bp.route('/courses/<int:list_id>/ajouter-recette', methods=['POST'])
def add_recipe(list_id):
    recipe_id = request.form.get('recipe_id', type=int)
    portions = request.form.get('portions', type=int)

    if recipe_id:
        shopping_model.add_recipe_items(list_id, recipe_id, portions)

    if request.headers.get('HX-Request'):
        return _render_items_partial(list_id)
    return redirect(url_for('shopping.detail', list_id=list_id))


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


@bp.route('/courses/<int:list_id>/vider-coches', methods=['POST'])
def clear_checked(list_id):
    shopping_model.clear_checked(list_id)
    if request.headers.get('HX-Request'):
        return _render_items_partial(list_id)
    return redirect(url_for('shopping.detail', list_id=list_id))


@bp.route('/courses/<int:list_id>/supprimer', methods=['POST'])
def delete_list(list_id):
    shopping_model.delete(list_id)
    flash('Liste supprimee.', 'success')
    return redirect(url_for('shopping.index'))


def _render_items_partial(list_id):
    items = shopping_model.get_items(list_id)
    grouped = {}
    free_items = []
    for item in items:
        if item['recipe_id']:
            key = item['recipe_id']
            if key not in grouped:
                grouped[key] = {'title': item['recipe_title'] or 'Recette supprimee', 'entries': []}
            grouped[key]['entries'].append(item)
        else:
            free_items.append(item)
    return render_template('shopping/partials/items.html',
                           list_id=list_id, grouped=grouped, free_items=free_items)
