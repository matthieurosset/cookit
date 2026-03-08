import json

from ..db import query, execute, get_db


def list_all():
    lists = query('SELECT * FROM shopping_list ORDER BY created_at DESC')
    result = []
    for lst in lists:
        total = query(
            'SELECT COUNT(*) as c FROM shopping_item WHERE list_id = ?',
            [lst['id']], one=True
        )['c']
        checked = query(
            'SELECT COUNT(*) as c FROM shopping_item WHERE list_id = ? AND checked = 1',
            [lst['id']], one=True
        )['c']
        result.append({**dict(lst), 'total': total, 'checked': checked})
    return result


def get(list_id):
    return query('SELECT * FROM shopping_list WHERE id = ?', [list_id], one=True)


def create(name):
    return execute(
        'INSERT INTO shopping_list (name) VALUES (?)', [name.strip()]
    ).lastrowid


def delete(list_id):
    execute('DELETE FROM shopping_list WHERE id = ?', [list_id])


def get_items(list_id):
    return query(
        '''SELECT si.*, r.title as recipe_title
           FROM shopping_item si
           LEFT JOIN recipe r ON si.recipe_id = r.id
           WHERE si.list_id = ?
           ORDER BY si.checked, si.recipe_id NULLS FIRST, si.id''',
        [list_id]
    )


def add_item(list_id, name, quantity=None, unit=None, recipe_id=None):
    return execute(
        '''INSERT INTO shopping_item (list_id, name, quantity, unit, recipe_id)
           VALUES (?, ?, ?, ?, ?)''',
        [list_id, name.strip(), quantity, unit, recipe_id]
    ).lastrowid


def add_recipe_items(list_id, recipe_id, portions=None):
    from .recipe import get as get_recipe
    recipe = get_recipe(recipe_id)
    if not recipe:
        return

    ingredients = json.loads(recipe['ingredients'])
    ratio = portions / recipe['portions'] if portions else 1

    for ing in ingredients:
        qty = ing.get('quantity', '')
        if qty and ratio != 1:
            try:
                qty = str(round(float(str(qty).replace(',', '.')) * ratio, 2))
                if qty.endswith('.0'):
                    qty = qty[:-2]
            except (ValueError, TypeError):
                pass
        add_item(list_id, ing.get('name', ''), qty, ing.get('unit', ''), recipe_id)


def toggle_item(item_id):
    item = query('SELECT * FROM shopping_item WHERE id = ?', [item_id], one=True)
    if item:
        new_val = 0 if item['checked'] else 1
        execute('UPDATE shopping_item SET checked = ? WHERE id = ?', [new_val, item_id])
        return new_val
    return None


def delete_item(item_id):
    execute('DELETE FROM shopping_item WHERE id = ?', [item_id])


def clear_checked(list_id):
    execute(
        'DELETE FROM shopping_item WHERE list_id = ? AND checked = 1',
        [list_id]
    )
