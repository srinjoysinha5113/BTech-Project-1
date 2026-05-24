# MySQL Setup Instructions

## Prerequisites

1. Install MySQL Server on your system
2. Start MySQL service
3. Create a database for the project

## Database Setup

### Option 1: Using MySQL Command Line

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE post_quantum_db;

# Create user (optional, for production)
CREATE USER 'pqc_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON post_quantum_db.* TO 'pqc_user'@'localhost';
FLUSH PRIVILEGES;
```

### Option 2: Using MySQL Workbench

1. Open MySQL Workbench
2. Connect to your MySQL server
3. Execute: `CREATE DATABASE post_quantum_db;`

## Update Configuration

Update the `.env` file with your MySQL credentials. 

**Note:** If your password contains special characters like `@`, you must URL-encode them (e.g., `@` becomes `%40`).

```env
DATABASE_URL=mysql+pymysql://root:YOUR_ENCODED_PASSWORD@localhost:3306/post_quantum_db
```

## Run Migrations

Once MySQL is set up and configured, run the migrations from the `backend` directory:

```bash
# Ensure you are in the backend directory
cd backend

# Run migrations
venv\Scripts\python.exe -m alembic upgrade head
```

## Troubleshooting: Special Characters in Password

If you encounter a `ValueError: invalid interpolation syntax` when running migrations, ensure that the `%` characters in your URL-encoded password are escaped as `%%` in the `alembic/env.py` file. The project is already configured to handle this automatically:

```python
# In alembic/env.py
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))
```

## Verify Connection

Start the backend server and test the health endpoint:

```bash
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then visit: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

The database status should show `"connected"`.
