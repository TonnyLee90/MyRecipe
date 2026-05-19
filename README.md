# MyRecipe

A community recipe-sharing web app built with Flask. Users can post their own recipes, browse and save recipes from others, and explore dishes from the [TheMealDB](https://www.themealdb.com/) API.

---

## Features

- **User authentication** — sign up, log in, and log out with hashed passwords
- **Post recipes** — share recipes with a title, description, ingredients, and instructions
- **My Recipes** — view and delete your own posted recipes
- **Save / Unsave** — bookmark community recipes to your personal favorites list
- **Search** — search local recipes or query TheMealDB's database
- **Explore** — browse random meals fetched from TheMealDB
- **External recipe detail** — view full ingredient lists and instructions for TheMealDB meals

---

## Technology

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask 3.x |
| Database | PostgreSQL (via [Neon](https://neon.tech)) |
| ORM | Flask-SQLAlchemy + Flask-Migrate (Alembic) |
| Auth | Flask-Login, Werkzeug password hashing |
| Forms & CSRF | Flask-WTF, WTForms |
| External API | [TheMealDB](https://www.themealdb.com/api.php) |
| Frontend | Jinja2 templates, plain CSS |

---

## Getting Started

### Prerequisites

- Python 3.10+
- A PostgreSQL database (local or hosted, e.g. [Neon](https://neon.tech))

### 1. Clone the repository

```bash
git clone https://github.com/TonnyLee90/MyRecipe.git
cd MyRecipe
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root

```env
DATABASE_URL=postgresql+psycopg2://user:password@host/dbname?sslmode=require
SECRET_KEY=your-random-secret-key
```

Generate a strong secret key with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Apply database migrations

```bash
flask db upgrade
```

### 6. Run the development server

```bash
python run.py
```

The app will be available at `http://127.0.0.1:5000`.

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Flask session signing key — keep this secret and random |

---


## Routes

| Method | URL | Auth required | Description |
|---|---|---|---|
| GET | `/` | No | Home feed |
| GET | `/explore` | No | Random meals from TheMealDB |
| GET | `/search` | No | Search local or TheMealDB |
| GET | `/external/<meal_id>` | No | TheMealDB recipe detail |
| GET/POST | `/post_recipe` | Yes | Create a new recipe |
| GET | `/recipe/<id>` | No | Local recipe detail |
| POST | `/recipe/<id>/delete` | Yes | Delete your recipe |
| POST | `/save/<id>` | Yes | Save a recipe |
| POST | `/unsave/<id>` | Yes | Unsave a recipe |
| GET | `/favorites` | Yes | Your saved recipes |
| GET | `/my_recipes` | Yes | Your posted recipes |
| GET/POST | `/login` | No | Log in |
| GET/POST | `/signup` | No | Create account |
| GET | `/logout` | Yes | Log out |
