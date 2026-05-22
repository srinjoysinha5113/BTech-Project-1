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

Update the `.env` file with your MySQL credentials:

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/post_quantum_db
```

## Run Migrations

Once MySQL is set up and configured, run the migrations:

```bash
cd backend
venv\Scripts\python.exe -m alembic upgrade head
```

## Verify Connection

Start the backend server and test the health endpoint:

```bash
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then visit: http://localhost:8000/api/v1/health

The database status should show "connected".
