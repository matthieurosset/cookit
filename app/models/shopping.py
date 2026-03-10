import json

from ..db import query, execute


def get_or_create_list():
    """Get the single shopping list, creating it if needed."""
    lst = query('SELECT * FROM shopping_list LIMIT 1', one=True)
    if not lst:
        execute("INSERT INTO shopping_list (name) VALUES ('courses')")
        lst = query('SELECT * FROM shopping_list LIMIT 1', one=True)
    return lst


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


def update_quantity(item_id, delta):
    """Increment or decrement the quantity of an item."""
    item = query('SELECT * FROM shopping_item WHERE id = ?', [item_id], one=True)
    if not item:
        return None
    current = item['quantity'] or ''
    try:
        val = float(str(current).replace(',', '.')) if current else 0
        val = val + delta
        if val < 0:
            val = 0
        # Format nicely: integer if whole number
        if val == int(val):
            new_qty = str(int(val))
        else:
            new_qty = str(round(val, 2))
        execute('UPDATE shopping_item SET quantity = ? WHERE id = ?', [new_qty, item_id])
        return new_qty
    except (ValueError, TypeError):
        return current


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


def clear_all(list_id):
    execute('DELETE FROM shopping_item WHERE list_id = ?', [list_id])


def get_suggestions(q):
    """Return item suggestions matching query, sorted by frequency."""
    rows = query(
        '''SELECT name,
                  quantity,
                  unit,
                  COUNT(*) as freq
           FROM shopping_item
           WHERE LOWER(name) LIKE ?
           GROUP BY LOWER(name)
           ORDER BY freq DESC
           LIMIT 8''',
        ['%' + q.lower() + '%']
    )
    seen = set()
    results = []
    for r in rows:
        key = r['name'].lower()
        if key not in seen:
            seen.add(key)
            results.append({
                'name': r['name'],
                'quantity': r['quantity'] or '',
                'unit': r['unit'] or '',
            })
    return results


def get_frequent_items(limit=10):
    """Return the most frequently added items."""
    rows = query(
        '''SELECT name,
                  quantity,
                  unit,
                  COUNT(*) as freq
           FROM shopping_item
           GROUP BY LOWER(name)
           ORDER BY freq DESC
           LIMIT ?''',
        [limit]
    )
    return [{'name': r['name'], 'quantity': r['quantity'] or '',
             'unit': r['unit'] or ''} for r in rows]
