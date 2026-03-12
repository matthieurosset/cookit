import json
import os

from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, send_from_directory, current_app)

from ..models import recipe as recipe_model
from ..models import tag as tag_model
from ..services import images
from ..services.scaling import scale_ingredients

bp = Blueprint('recipes', __name__)


@bp.route('/recettes')
def index():
    search = request.args.get('q', '').strip()
    tag_id = request.args.get('tag', type=int)

    recipes = recipe_model.list_all(search=search, tag_id=tag_id)
    tags = tag_model.list_all()
    recipe_tags = recipe_model.get_all_tags()

    # For HTMX requests, return only the cards partial
    if request.headers.get('HX-Request'):
        return render_template('recipes/partials/cards.html', recipes=recipes, recipe_tags=recipe_tags)

    return render_template('recipes/list.html', recipes=recipes, tags=tags,
                           recipe_tags=recipe_tags, search=search, active_tag=tag_id)


@bp.route('/recettes/nouvelle', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        data = _parse_form(request)
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            data['image_path'] = images.save_image(image_file)
        elif request.form.get('prefill_image'):
            data['image_path'] = request.form['prefill_image']

        recipe_id = recipe_model.create(data)

        tag_ids = request.form.getlist('tags')
        if tag_ids:
            recipe_model.set_tags(recipe_id, tag_ids)

        flash('Recette ajoutée !', 'success')
        return redirect(url_for('recipes.detail', recipe_id=recipe_id))

    tags = tag_model.list_all()
    return render_template('recipes/form.html', recipe=None, tags=tags, recipe_tags=[])


@bp.route('/recettes/<int:recipe_id>')
def detail(recipe_id):
    recipe = recipe_model.get(recipe_id)
    if not recipe:
        flash('Recette introuvable.', 'error')
        return redirect(url_for('recipes.index'))

    recipe_tags = recipe_model.get_tags(recipe_id)
    ingredients = json.loads(recipe['ingredients'])
    steps = json.loads(recipe['steps'])

    return render_template('recipes/detail.html', recipe=recipe,
                           ingredients=ingredients, steps=steps,
                           tags=recipe_tags, portions=recipe['portions'])


@bp.route('/recettes/<int:recipe_id>/modifier', methods=['GET', 'POST'])
def edit(recipe_id):
    recipe = recipe_model.get(recipe_id)
    if not recipe:
        flash('Recette introuvable.', 'error')
        return redirect(url_for('recipes.index'))

    if request.method == 'POST':
        data = _parse_form(request)
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            images.delete_image(recipe['image_path'])
            data['image_path'] = images.save_image(image_file)
        else:
            data['image_path'] = None  # COALESCE in SQL keeps existing

        recipe_model.update(recipe_id, data)

        tag_ids = request.form.getlist('tags')
        recipe_model.set_tags(recipe_id, tag_ids)

        flash('Recette mise à jour !', 'success')
        return redirect(url_for('recipes.detail', recipe_id=recipe_id))

    tags = tag_model.list_all()
    recipe_tags = [t['id'] for t in recipe_model.get_tags(recipe_id)]
    edit_data = {
        'ingredients': json.loads(recipe['ingredients']),
        'steps': json.loads(recipe['steps']),
    }
    return render_template('recipes/form.html', recipe=recipe, tags=tags,
                           recipe_tags=recipe_tags, edit_data=edit_data)


@bp.route('/recettes/<int:recipe_id>/supprimer', methods=['POST'])
def delete(recipe_id):
    recipe = recipe_model.get(recipe_id)
    if recipe:
        images.delete_image(recipe['image_path'])
        recipe_model.delete(recipe_id)
        flash('Recette supprimée.', 'success')
    return redirect(url_for('recipes.index'))



@bp.route('/recettes/<int:recipe_id>/ingredients')
def scaled_ingredients(recipe_id):
    recipe = recipe_model.get(recipe_id)
    if not recipe:
        return '', 404

    portions = request.args.get('portions', recipe['portions'], type=int)
    portions = max(1, min(99, portions))
    ingredients = json.loads(recipe['ingredients'])
    scaled = scale_ingredients(ingredients, recipe['portions'], portions)

    return render_template('recipes/partials/ingredients.html',
                           ingredients=scaled, portions=portions,
                           recipe_id=recipe_id)


@bp.route('/recettes/hasard')
def random_recipe():
    recipe = recipe_model.random()
    if recipe:
        return redirect(url_for('recipes.detail', recipe_id=recipe['id']))
    flash('Aucune recette pour le moment.', 'info')
    return redirect(url_for('recipes.index'))


@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


def _parse_form(req):
    """Parse recipe form data into a dict."""
    ingredients = []
    names = req.form.getlist('ing_name')
    qtys = req.form.getlist('ing_qty')
    units = req.form.getlist('ing_unit')
    for name, qty, unit in zip(names, qtys, units):
        if name.strip():
            ingredients.append({
                'name': name.strip(),
                'quantity': qty.strip(),
                'unit': unit.strip(),
            })

    steps = []
    for step in req.form.getlist('step'):
        if step.strip():
            steps.append(step.strip())

    prep_time = req.form.get('prep_time', type=int)
    cook_time = req.form.get('cook_time', type=int)

    return {
        'title': req.form.get('title', '').strip(),
        'ingredients': ingredients,
        'steps': steps,
        'portions': req.form.get('portions', 4, type=int),
        'prep_time': prep_time if prep_time and prep_time > 0 else None,
        'cook_time': cook_time if cook_time and cook_time > 0 else None,
        'source_url': req.form.get('source_url', '').strip() or None,
    }
