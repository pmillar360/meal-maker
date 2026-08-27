from fastapi import status
from app import models


def _create_recipe_with_ingredients(
    db_session,
    test_user,
    ingredient_names: list[str],
    meal_type=None,
    title: str = "Availability Test Recipe",
):
    recipe = models.Recipe(
        title=title,
        description="A recipe for availability endpoint tests",
        instructions="Mix and cook",
        cooking_time=15,
        servings=2,
        user_id=test_user.id,
    )
    db_session.add(recipe)
    db_session.flush()

    for ingredient_name in ingredient_names:
        ingredient = (
            db_session.query(models.Ingredient)
            .filter(models.Ingredient.name == ingredient_name)
            .first()
        )
        if ingredient is None:
            ingredient = models.Ingredient(name=ingredient_name, category="Produce")
            db_session.add(ingredient)
            db_session.flush()

        recipe_ingredient = models.RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            quantity="1",
            unit="unit",
        )
        db_session.add(recipe_ingredient)

    if meal_type:
        recipe.meal_types.append(meal_type)

    db_session.commit()
    db_session.refresh(recipe)
    return recipe


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


def test_get_recipes_with_fridge_availability(authenticated_client, db_session, test_user, test_meal_type):
    recipe = _create_recipe_with_ingredients(db_session, test_user, ["Onion", "Garlic"], meal_type=test_meal_type)

    authenticated_client.post("/fridge/", json={"name": "onion", "quantity": "1"})
    response = authenticated_client.get("/recipes/with-fridge-availability/", params={"meal_types": test_meal_type.name})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    recipe_availability = next(item for item in data if item["recipe"]["id"] == recipe.id)
    assert recipe_availability["total_ingredients"] == 2
    assert recipe_availability["available_ingredients"] == 1
    assert recipe_availability["missing_ingredients"] == 1
    assert recipe_availability["missing_ingredient_names"] == ["Garlic"]


def test_get_recipes_filters_by_search_query(client, db_session, test_user):
    matching_recipe = _create_recipe_with_ingredients(
        db_session,
        test_user,
        ["Chicken", "Rice"],
        title="Spicy Chicken Bowl",
    )
    _create_recipe_with_ingredients(
        db_session,
        test_user,
        ["Tomato", "Basil"],
        title="Tomato Pasta",
    )

    response = client.get("/recipes/", params={"search": "chicken"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert [recipe["id"] for recipe in data] == [matching_recipe.id]
    assert data[0]["title"] == "Spicy Chicken Bowl"


def test_get_recipes_with_fridge_availability_filters_by_selected_ingredients(
    authenticated_client,
    db_session,
    test_user,
):
    matching_recipe = _create_recipe_with_ingredients(
        db_session,
        test_user,
        ["Onion", "Garlic"],
        title="Savory Onion Skillet",
    )
    _create_recipe_with_ingredients(
        db_session,
        test_user,
        ["Tomato", "Basil"],
        title="Tomato Basil Soup",
    )

    authenticated_client.post("/fridge/", json={"name": "onion", "quantity": "1"})
    response = authenticated_client.get(
        "/recipes/with-fridge-availability/",
        params={"ingredients": "onion"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert [item["recipe"]["id"] for item in data] == [matching_recipe.id]
    assert data[0]["available_ingredients"] == 1
    assert data[0]["missing_ingredients"] == 1


def test_get_recipes_with_fridge_availability_combines_search_and_ingredient_filters(
    authenticated_client,
    db_session,
    test_user,
):
    matching_recipe = _create_recipe_with_ingredients(
        db_session,
        test_user,
        ["Onion", "Garlic"],
        title="Onion Chicken Bake",
    )
    _create_recipe_with_ingredients(
        db_session,
        test_user,
        ["Onion", "Pepper"],
        title="Onion Veggie Bake",
    )

    response = authenticated_client.get(
        "/recipes/with-fridge-availability/",
        params={"ingredients": "onion", "search": "chicken"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert [item["recipe"]["id"] for item in data] == [matching_recipe.id]
    assert data[0]["recipe"]["title"] == "Onion Chicken Bake"


def test_get_recipe_availability(authenticated_client, db_session, test_user):
    recipe = _create_recipe_with_ingredients(db_session, test_user, ["Tomato", "Basil"]) 

    authenticated_client.post("/fridge/", json={"name": "tomato", "quantity": "1"})
    response = authenticated_client.get(f"/recipes/{recipe.id}/availability/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["recipe"]["id"] == recipe.id
    assert data["total_ingredients"] == 2
    assert data["available_ingredients"] == 1
    assert data["missing_ingredients"] == 1
    assert data["missing_ingredient_names"] == ["Basil"]
    assert len(data["ingredient_statuses"]) == 2
    tomato_status = next(item for item in data["ingredient_statuses"] if item["ingredient"]["name"] == "Tomato")
    basil_status = next(item for item in data["ingredient_statuses"] if item["ingredient"]["name"] == "Basil")
    assert tomato_status["has_in_fridge"] is True
    assert tomato_status["missing"] is False
    assert basil_status["has_in_fridge"] is False
    assert basil_status["missing"] is True


def test_add_user_favourite_recipe(authenticated_client, test_recipe):
    response = authenticated_client.put(f"/users/me/favourites/{test_recipe.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"] is not None
    assert data["recipe_id"] == test_recipe.id


def test_get_user_favourite_recipes(authenticated_client, test_recipe):
    # First, add the recipe to the user's favourites
    response = authenticated_client.put(f"/users/me/favourites/{test_recipe.id}")

    # Check if the recipe was added to favourites
    assert response.status_code == status.HTTP_200_OK

    # Now, retrieve the user's favourite recipes
    response = authenticated_client.get("/users/me/favourites/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(recipe["id"] == test_recipe.id for recipe in data)


def test_remove_user_favourite_recipe(authenticated_client, test_recipe):
    # First, add the recipe to the user's favourites
    response = authenticated_client.put(f"/users/me/favourites/{test_recipe.id}")

    # Check if the recipe was added to favourites
    assert response.status_code == status.HTTP_200_OK

    # Now, remove the recipe from favourites
    response = authenticated_client.delete(f"/users/me/favourites/{test_recipe.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


# TODO: Fix this test
# def test_get_recipe_suggestions(client, test_ingredient):
#     params = {"ingredients": test_ingredient.name, "count": 3}
#     response = client.get("/recipes/suggestions/", params=params)

#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     assert isinstance(data, list)
#     assert len(data) > 0
