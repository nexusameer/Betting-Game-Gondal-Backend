# Betting Game Gondal Backend

This repository contains the backend Django application for a betting game. It provides the API endpoints and logic for managing users, games, bets, and results.

## Table of Contents

* [Prerequisites](#prerequisites)
* [Setup and Installation](#setup-and-installation)
* [API Endpoints](#api-endpoints)
* [Project Structure](#project-structure)
* [Running Tests](#running-tests)
* [Deployment](#deployment)
* [Contributing](#contributing)
* [License](#license)

## Prerequisites


Before you begin, ensure you have the following installed:

* **Python 3.x:** Django requires Python.
* **pip:** Python's package installer.
* **Virtualenv (recommended):** To create isolated Python environments.
* **PostgreSQL (or another supported database):** For storing application data.

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/nexusameer/Betting-Game-Gondal-Backend.git](https://github.com/nexusameer/Betting-Game-Gondal-Backend.git)
    cd Betting-Game-Gondal-Backend
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate      # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the database:**

    * Create a PostgreSQL database (or configure your database of choice).
    * Rename `gondal_backend/settings.example.py` to `gondal_backend/settings.py`.
    * Edit `gondal_backend/settings.py` and update the `DATABASES` settings with your database credentials. Example for PostgreSQL:

        ```python
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'your_database_name',
                'USER': 'your_database_user',
                'PASSWORD': 'your_database_password',
                'HOST': 'localhost',  # Or your database host
                'PORT': '5432',       # Or your database port
            }
        }
        ```

5.  **Run migrations:**

    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser (for admin access):**

    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

    The server will be accessible at `http://127.0.0.1:8000/`.

## API Endpoints

This Django application provides the following API endpoints:

* **User Management:**
    * `POST /api/users/`: Create a new user.
    * `GET /api/users/{id}/`: Retrieve a user.
    * `PUT /api/users/{id}/`: Update a user.
    * `DELETE /api/users/{id}/`: Delete a user.
* **Game Management:**
    * `POST /api/games/`: Create a new game.
    * `GET /api/games/`: Retrieve all games.
    * `GET /api/games/{id}/`: Retrieve a game.
    * `PUT /api/games/{id}/`: Update a game.
    * `DELETE /api/games/{id}/`: Delete a game.
* **Bet Management:**
    * `POST /api/bets/`: Create a new bet.
    * `GET /api/bets/`: Retrieve all bets.
    * `GET /api/bets/{id}/`: Retrieve a bet.
    * `PUT /api/bets/{id}/`: Update a bet.
    * `DELETE /api/bets/{id}/`: Delete a bet.
* **Result Management:**
    * `POST /api/results/`: Create a new result.
    * `GET /api/results/`: Retrieve all results.
    * `GET /api/results/{id}/`: Retrieve a result.
    * `PUT /api/results/{id}/`: Update a result.
    * `DELETE /api/results/{id}/`: Delete a result.
* **Authentication:**
    * Authentication is handled using Django Rest Framework's authentication mechanisms. Check the code for the specific implementation.

## Project Structure

