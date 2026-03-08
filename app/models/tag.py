from ..db import query, execute


def list_all():
    return query('SELECT * FROM tag ORDER BY name')


def get(tag_id):
    return query('SELECT * FROM tag WHERE id = ?', [tag_id], one=True)


def create(name):
    return execute(
        'INSERT INTO tag (name) VALUES (?)',
        [name.strip()]
    ).lastrowid


def update(tag_id, name):
    execute(
        'UPDATE tag SET name = ? WHERE id = ?',
        [name.strip(), tag_id]
    )


def delete(tag_id):
    execute('DELETE FROM tag WHERE id = ?', [tag_id])


def get_recipe_count(tag_id):
    row = query(
        'SELECT COUNT(*) as c FROM recipe_tag WHERE tag_id = ?',
        [tag_id], one=True
    )
    return row['c'] if row else 0
