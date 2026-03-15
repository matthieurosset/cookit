import json

from ..db import query, execute

STORES = [None, 'migros', 'coop']
STORE_LABELS = {None: 'Sans distinction', 'migros': 'Migros', 'coop': 'Coop'}


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
           ORDER BY CASE WHEN si.store IS NULL THEN 0 WHEN si.store = 'migros' THEN 1 WHEN si.store = 'coop' THEN 2 END,
                    si.checked, si.name COLLATE NOCASE''',
        [list_id]
    )


def add_item(list_id, name, quantity=None, unit=None, recipe_id=None):
    row_id = execute(
        '''INSERT INTO shopping_item (list_id, name, quantity, unit, recipe_id)
           VALUES (?, ?, ?, ?, ?)''',
        [list_id, name.strip(), quantity, unit, recipe_id]
    ).lastrowid
    if recipe_id is None:
        _audit_item(name.strip(), quantity, unit)
    return row_id


def _audit_item(name, quantity=None, unit=None):
    execute(
        '''INSERT INTO shopping_item_audit (name, quantity, unit, count)
           VALUES (?, ?, ?, 1)
           ON CONFLICT(name) DO UPDATE SET
               quantity = excluded.quantity,
               unit = excluded.unit,
               count = count + 1''',
        [name, quantity, unit]
    )


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


def set_store(item_id, store):
    """Set store for an item. If already set to this store, clear it."""
    item = query('SELECT * FROM shopping_item WHERE id = ?', [item_id], one=True)
    if not item:
        return None
    new_store = None if item['store'] == store else store
    execute('UPDATE shopping_item SET store = ? WHERE id = ?', [new_store, item_id])
    return new_store


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
        '''SELECT name, quantity, unit, count
           FROM shopping_item_audit
           WHERE LOWER(name) LIKE ?
           ORDER BY count DESC
           LIMIT 8''',
        ['%' + q.lower() + '%']
    )
    return [{'name': r['name'], 'quantity': r['quantity'] or '',
             'unit': r['unit'] or ''} for r in rows]


def get_frequent_items(limit=10):
    """Return the most frequently added items, sorted alphabetically."""
    rows = query(
        '''SELECT name, quantity, unit, count FROM (
               SELECT name, quantity, unit, count
               FROM shopping_item_audit
               ORDER BY count DESC
               LIMIT ?
           ) ORDER BY name COLLATE NOCASE''',
        [limit]
    )
    return [{'name': r['name'], 'quantity': r['quantity'] or '',
             'unit': r['unit'] or ''} for r in rows]
