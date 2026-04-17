## ⚙️ Backend Installation & Setup (Django)

### 1. Prerequisites
Make sure you have **Python** (3.8 or higher) and **pip** installed on your system.
You will also need **PostgreSQL** installed locally.

### 2. Set Up a Virtual Environment
It is highly recommended to run the project inside a virtual environment to keep dependencies isolated.

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
For security reasons, the `.env` file containing secrets is **not** pushed to GitHub.
When another developer clones this repository, they must create their own `.env` file by duplicating the provided `.env.example` file.

```bash
# On Windows, you can just manually copy .env.example and rename it to .env
# Or in PowerShell:
copy .env.example .env
```
Open your newly created `.env` file and paste in your database connection string, as well as the secret keys provided by your manager:
```env
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<database_name>
```

### 5. Database Setup (PostgreSQL)
Ensure your PostgreSQL server is running. Create a new database for the project (e.g. `milk_delivery_db`).
If you use `psql`:
```bash
psql -U postgres
CREATE DATABASE milk_delivery_db;
```
*(Make sure the username, password, and database name match what is set in your `DATABASE_URL` inside `.env`)*

### 6. Apply Migrations
Set up your database tables by running:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Admin)
Create an admin account to access the Django admin panel:
```bash
python manage.py createsuperuser
```
Follow the prompts to set your email, username, and password.

### 8. Run Application (Local Setup)
```bash
python manage.py runserver
```
The application will be running at `http://127.0.0.1:8000/`. You can access the admin panel at `http://127.0.0.1:8000/admin/`.
