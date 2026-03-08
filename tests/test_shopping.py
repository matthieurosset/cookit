def test_shopping_index(client):
    resp = client.get('/courses')
    assert resp.status_code == 200
    assert b'Listes de courses' in resp.data


def test_create_list(client):
    resp = client.post('/courses/nouvelle', data={'name': 'Semaine 12'},
                       follow_redirects=True)
    assert resp.status_code == 200
    assert b'Semaine 12' in resp.data


def test_add_item(client):
    client.post('/courses/nouvelle', data={'name': 'Test'})
    resp = client.post('/courses/1/ajouter', data={
        'name': 'Tomates',
        'quantity': '500',
        'unit': 'g',
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_toggle_item(client):
    client.post('/courses/nouvelle', data={'name': 'Test'})
    client.post('/courses/1/ajouter', data={'name': 'Lait'})
    resp = client.patch('/courses/item/1/toggle')
    assert resp.status_code in (200, 204)


def test_delete_list(client):
    client.post('/courses/nouvelle', data={'name': 'A supprimer'})
    resp = client.post('/courses/1/supprimer', follow_redirects=True)
    assert resp.status_code == 200


def test_add_recipe_to_list(client):
    # Create a recipe first
    client.post('/recettes/nouvelle', data={
        'title': 'Pates carbo',
        'portions': '4',
        'ing_name': ['pates', 'lardons'],
        'ing_qty': ['500', '200'],
        'ing_unit': ['g', 'g'],
        'step': ['Cuire'],
    })
    # Create a shopping list
    client.post('/courses/nouvelle', data={'name': 'Courses'})
    # Add recipe items
    resp = client.post('/courses/1/ajouter-recette', data={
        'recipe_id': '1',
        'portions': '4',
    }, follow_redirects=True)
    assert resp.status_code == 200
