# Meal Maker

Meal Maker is a full-stack web app that suggests recipes based on the ingredients a user already has on hand. The MVP focuses on quick meal discovery, simple filtering, recipe details, and a shopping list for missing items.

## MVP Scope

The current product plan includes the following core features:

- Users enter ingredients they already have on hand
- The app returns ingredient-based recipe suggestions
- A basic recipe database with roughly 50 to 100 starter recipes
- Filtering by meal type such as breakfast, lunch, dinner, and snacks
- Filtering by dietary needs such as vegetarian, vegan, and high-protein
- Support for user diet preferences and optional filtering by a specific ingredient to include
- Detailed recipe pages with ingredients, cooking instructions, cooking time, and servings
- A shopping list generator for ingredients users do not have yet

## Tech Stack

- Frontend: Next.js, React, and Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Alembic, and PostgreSQL
- Local development fallback: SQLite can be used when a database URL is not configured
- Optional recipe integrations: Spoonacular or Edamam
- Optional rapid auth and storage alternative: Firebase

## Project Structure

- /frontend — Next.js application, route pages, reusable components, context, and API services
- /backend — FastAPI API, CRUD logic, ORM models, utilities, migrations, and tests

Implementation flow is organized as route handlers in the backend app layer, data operations in the CRUD layer, and shared support logic in utilities.

## Setup and Installation

### Prerequisites

- Node.js 14+
- Python 3.8+
- PostgreSQL for full local parity, or SQLite for lightweight development

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Setup

```bash
docker compose up --build
```

### Database Migrations

```bash
cd backend
alembic revision -m "describe change"
alembic upgrade head
```

## Testing and Verification

Use the following checks before considering MVP work complete:

### Backend tests

```bash
cd backend
pytest
```

You can also run the backend tests from the repository root:

```bash
python -m pytest backend
```

### Frontend validation

There is currently no dedicated frontend test suite configured, so the recommended validation step is a production build:

```bash
cd frontend
npm run build
```

Optional lint step:

```bash
cd frontend
npm run lint
```

### Manual MVP check

After the services are running, verify that you can:

1. Add or manage ingredients
2. View recipe suggestions based on available ingredients
3. Filter recipes by meal type and diet
4. Open a recipe detail page
5. Add missing ingredients to the shopping list

## MVP Completion Checklist

Use this checklist to finish and verify the MVP:

1. Verify ingredient-based recipe suggestion endpoints and frontend queries work correctly.
2. Confirm the database is seeded with initial recipe and ingredient data, including running the seed script when needed.
3. Validate meal type, dietary, and ingredient filters end to end.
4. Ensure the recipe detail page returns and displays ingredients, instructions, cooking time, and servings.
5. Confirm shopping list create, update, and delete flows work from the UI through the API.
6. Keep backend and frontend API contracts in sync as endpoints evolve.
7. Optionally integrate Spoonacular or Edamam for more dynamic recipe content.
8. Test the application end to end and prepare deployment once MVP behavior is stable.

This README is now the single maintained source of truth for project scope, setup, validation, and near-term priorities.

## Notes

- Backend tests live under the backend tests folder.
- Frontend auth and API behavior are centralized in the frontend services and context layers.
- For local development, review environment configuration before deployment-related changes.
