from fastapi import status


def test_get_recipe_by_id(client, test_recipe):
    response = client.get(f"/recipes/{test_recipe.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_recipe.id
    assert data["title"] == test_recipe.title
    assert "instructions" in data
    assert "recipe_ingredients" in data


def test_get_recipes(client, test_recipe):
    response = client.get("/recipes/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(recipe["id"] == test_recipe.id for recipe in data)


def test_get_recipes_with_meal_type(client, test_recipe):
    params = {"meal_type": test_recipe.meal_types[0]}
    response = client.get("/recipes/", params=params)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(recipe["id"] == test_recipe.id for recipe in data)
    # Check that all returned recipes have a meal type with the same id as test_recipe's meal type
    # NOTE Cannot check by object since it is just json when returned?
    for recipe in data:
        meal_type_ids = [mt["id"] for mt in recipe["meal_types"]]
        assert test_recipe.meal_types[0].id in meal_type_ids


def test_add_user_favourite_recipe(authenticated_client, test_recipe):
    item_data = {"recipe_id": test_recipe.id}

    response = authenticated_client.post(f"/users/favourites/", params=item_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"] is not None
    assert data["recipe_id"] == test_recipe.id


def test_get_user_favourite_recipes(authenticated_client, test_recipe):
    # First, add the recipe to the user's favourites
    item_data = {"recipe_id": test_recipe.id}

    response = authenticated_client.post(f"/users/favourites/", params=item_data)

    # Check if the recipe was added to favourites
    assert response.status_code == status.HTTP_200_OK

    # Now, retrieve the user's favourite recipes
    response = authenticated_client.get("/users/favourites/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(recipe["id"] == test_recipe.id for recipe in data)


def test_remove_user_favourite_recipe(authenticated_client, test_recipe):
    # First, add the recipe to the user's favourites
    item_data = {"recipe_id": test_recipe.id}

    response = authenticated_client.post(f"/users/favourites/", params=item_data)

    # Check if the recipe was added to favourites
    assert response.status_code == status.HTTP_200_OK

    # Now, remove the recipe from favourites
    response = authenticated_client.delete(f"/users/favourites/{test_recipe.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data is True


# TODO: Fix this test
# def test_get_recipe_suggestions(client, test_ingredient):
#     params = {"ingredients": test_ingredient.name, "count": 3}
#     response = client.get("/recipes/suggestions/", params=params)

#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     assert isinstance(data, list)
#     assert len(data) > 0
