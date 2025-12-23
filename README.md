# Meal Maker

An application that suggests recipes based on ingredients you have on hand.

## Features

- Ingredient-based recipe suggestions
- Basic recipe database with 50-100 recipes
- Filtering by meal type and dietary preferences
- Detailed recipe pages with ingredients and instructions
- Shopping list generator for missing ingredients

## Tech Stack

- **Frontend**: React (Next.js) with Tailwind CSS
- **Backend**: FastAPI (Python) with PostgreSQL
- **Optional API Integration**: Spoonacular or Edamam

## Setup and Installation

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- PostgreSQL

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

### Or Docker
```bash
# Create and deploy the project
docker compose up --build
```

```
### Database Migration

```bash
cd backend

alembic revision -m "Changes made"

alembic upgrade head
```

## Project Structure
- `/frontend` - Next.js application
- `/backend` - FastAPI application