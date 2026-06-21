import os
from pathlib import Path
from util.auth import hash_password

TEST_DB_PATH = Path(__file__).resolve().parent / "test_db.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import FridgeItem, MealType, User, Recipe, Ingredient, ShoppingListItem, Diet

# Create test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    # First drop all tables
    Base.metadata.drop_all(bind=engine)
    # Then create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    
    # Authenticate the client
    response = client.post("/auth/tokens", json={"username": test_user.username, "password": "hashedpassword123"})

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    access_token = data.get("access_token")

    client.headers.update({"Authorization": f"Bearer {access_token}"})
    
    yield client
    
@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(
        username="testexample",
        hashed_password=hash_password("hashedpassword123"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_diet(db_session):
    diet = Diet(
        name="Vegetarian"
    )
    db_session.add(diet)
    db_session.commit()
    db_session.refresh(diet)
    return diet

@pytest.fixture(scope="function")
def test_meal_type(db_session):
    meal_type = MealType(
        name="Dinner"
    )
    db_session.add(meal_type)
    db_session.commit()
    db_session.refresh(meal_type)
    return meal_type

@pytest.fixture(scope="function")
def test_recipe(db_session, test_user, test_diet, test_meal_type, test_ingredient):
    recipe = Recipe(
        title="Test Recipe",
        description="Test Description",
        instructions="Test Instructions",
        cooking_time=30,
        servings=4,
        user_id=test_user.id,
    )
    db_session.add(recipe)
    db_session.commit()

    recipe.diets.append(test_diet)
    recipe.meal_types.append(test_meal_type)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe

@pytest.fixture(scope="function")
def test_ingredient(db_session):
    ingredient = Ingredient(
        name="Test Ingredient",
        category="Test Category",
    )
    db_session.add(ingredient)
    db_session.commit()
    db_session.refresh(ingredient)
    return ingredient

@pytest.fixture(scope="function")
def test_recipe_with_ingredient(db_session, test_recipe, test_ingredient):
    test_recipe.ingredients.append(test_ingredient)
    db_session.commit()
    db_session.refresh(test_recipe)
    return test_recipe

@pytest.fixture(scope="function")
def test_shopping_list_item(db_session, test_user):
    item = ShoppingListItem(
        name="Onion",
        quantity="2 units",
        completed=False,
        id=4,
        user_id=test_user.id,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item

@pytest.fixture(scope="function")
def test_fridge_item(db_session, test_user):
    item = FridgeItem(
        name="TestIngredient",
        user_id=test_user.id
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item