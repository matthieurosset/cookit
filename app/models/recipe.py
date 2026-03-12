import json

from ..db import query, execute, get_db


def list_all(search=None, tag_id=None):
    sql = 'SELECT DISTINCT r.* FROM recipe r'
    conditions = []
    args = []

    if tag_id:
        sql += ' JOIN recipe_tag rt ON r.id = rt.recipe_id'
        conditions.append('rt.tag_id = ?')
        args.append(tag_id)

    if search:
        conditions.append('r.title LIKE ? COLLATE NOCASE')
        args.append(f'%{search}%')

    if conditions:
        sql += ' WHERE ' + ' AND '.join(conditions)

    sql += ' ORDER BY r.title COLLATE NOCASE'
    return query(sql, args)


def get(recipe_id):
    return query('SELECT * FROM recipe WHERE id = ?', [recipe_id], one=True)


def create(data):
    return execute(
        '''INSERT INTO recipe (title, ingredients, steps, portions,
           prep_time, cook_time, image_path, source_url)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        [data['title'],
         json.dumps(data['ingredients'], ensure_ascii=False),
         json.dumps(data['steps'], ensure_ascii=False),
         data.get('portions', 4),
         data.get('prep_time'), data.get('cook_time'),
         data.get('image_path'), data.get('source_url')]
    ).lastrowid


def update(recipe_id, data):
    execute(
        '''UPDATE recipe SET title=?, ingredients=?, steps=?,
           portions=?, prep_time=?, cook_time=?, image_path=COALESCE(?, image_path),
           source_url=?, updated_at=CURRENT_TIMESTAMP
           WHERE id=?''',
        [data['title'],
         json.dumps(data['ingredients'], ensure_ascii=False),
         json.dumps(data['steps'], ensure_ascii=False),
         data.get('portions', 4),
         data.get('prep_time'), data.get('cook_time'),
         data.get('image_path'), data.get('source_url'),
         recipe_id]
    )


def delete(recipe_id):
    execute('DELETE FROM recipe WHERE id = ?', [recipe_id])



def random():
    return query('SELECT * FROM recipe ORDER BY RANDOM() LIMIT 1', one=True)


def get_all_tags():
    """Return a dict mapping recipe_id -> list of tags."""
    rows = query(
        '''SELECT rt.recipe_id, t.id, t.name FROM tag t
           JOIN recipe_tag rt ON t.id = rt.tag_id
           ORDER BY t.name'''
    )
    result = {}
    for row in rows:
        result.setdefault(row['recipe_id'], []).append(row)
    return result


def get_tags(recipe_id):
    return query(
        '''SELECT t.* FROM tag t
           JOIN recipe_tag rt ON t.id = rt.tag_id
           WHERE rt.recipe_id = ?
           ORDER BY t.name''',
        [recipe_id]
    )


def set_tags(recipe_id, tag_ids):
    db = get_db()
    db.execute('DELETE FROM recipe_tag WHERE recipe_id = ?', [recipe_id])
    for tag_id in tag_ids:
        db.execute('INSERT INTO recipe_tag (recipe_id, tag_id) VALUES (?, ?)',
                   [recipe_id, int(tag_id)])
    db.commit()


def count():
    row = query('SELECT COUNT(*) as c FROM recipe', one=True)
    return row['c'] if row else 0
