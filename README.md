# Flask API Backend for UI display on Schema of Fractionalised Real World Assets

A minimal, modular, and extensible Flask + SQLAlchemy backend.

## 📁 Project Structure

```
provision_it_v2/
├── app/
│   ├── __init__.py            # App factory with Blueprint auto-discovery
│   ├── models.py              # SQLAlchemy models matching schema.sql
│   ├── database.py            # Database configuration and connection
│   ├── decorators.py          # Authentication and validation decorators
│   ├── controllers/           # MVC Controllers
│   ├── services/              # MVC Services (business logic)
│   ├── views/                 # MVC Views (response formatting)
│   └── routes/                # URL routing
├── frontend/                  # Htmls for web display and css for template
│   ├── Icons/                 # Icons stored
├── test/
│   ├── confest.py             # Pytest configuration and fixtures for the Provision-it test suite
│   ├── test_database/         # Separate testing database 
│   ├── test_utils/            # Utiles to auto set up schema and mock data
│   └── tests/                 # Actual tests
│         ├── E2E              # Playwright auto end-to-end tests
│         ├── infrastructure   # Tests on testing db
│         ├── integration      # Integration tests
│         ├── Jest             # Jest testing embeded JavaScript functions in htmls
│         └── unit             # Unit tests of backend
├── .github/
│   ├── pylint.yml             # Pylint format test
│   └── python-app.yml         # Running auto tests when pushed based on run_tests.py
├── config.py                  # Configuration management
├── .flaskenv                  # Flask env
├── .coveragerc                # Coverage report env
├── schema_postgres.sql        # Database schema with tables, functions, triggers
├── import_postgres.sql        # Database insert data
├── fix_sequences.sql          # Fix sequence synchronization issues after database import
├── init_db_postgres.py        # Database initialization
├── run.py                     # Application entry point
├── run_tests.py               # Application tests
├── requirements.txt           # Dependencies
├── .env                       # Environment configuration template
├── setup_env.sh               # Automated setup script for Unix/Linux/macOS
├── setup_env.bat              # Automated setup script for Windows
└── README.md                  # This file
```

# 🚀 Quick Start

If PostgreSQL is not installed on  device go to [Skip to PostgreSQL download](#additional-postgresql-download) first.

## Creating environment

### Option 1: Automated Setup (Recommended)

#### For Unix/Linux/macOS:
```bash
# Clone or copy the provision_it_v2 directory
cd provision_it_v2

# Run the automated setup script
./setup_env.sh
```

#### For Windows:
```powershell
# Clone or copy the provision_it_v2 directory
cd provision_it_v2

# create env and database
setup_env.bat

# if vitural environment not auto active run follwoing:

# Method 1 (CMD/Batch): 
venv\Scripts\activate.bat

#Method 2 (PowerShell): 
.\venv\Scripts\Activate.ps1
```

The setup scripts will automatically:
- ✅ Check Python version (3.8+ required)
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ **Create .env file with database configuration** (interactive prompts)
- ✅ Generate secure secret key automatically
- ✅ Interactive database configuration prompts

## 🔧 Interactive .env Configuration

When you run the setup scripts, they will prompt you for database configuration:

```
[INFO] Configuring database settings...
Database host [localhost]: 
Database port [5432]: 
Database name [provision_it_v2]: 
Database user [postgres]: 
Database password: 
[SUCCESS] .env file created with database configuration
[INFO] Database URL: postgresql://postgres:***@localhost:5432/provision_it_v2
```

### Option 2: Manual Setup

#### 1. Setup Environment

```bash
# Clone or copy the provision_it_v2 directory
cd provision_it_v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Database

```bash
# Create/Edit .env file with your database settings
# DATABASE_URL=postgresql://username:password@localhost:5432/api_backbone

# OR use the automated setup scripts which create .env interactively
```

## Initialize/Drop Database

### Mac/Linux
```bash
# 1. Create database
createdb your_database_name

# 2. Run initialization
python init_db_postgres.py

# 3. Delete database
dropdb your_database_name

# 3.1 kill all database connection of database
psql -U your_username -d postgres

-- Kill all connections to your_database
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'provision_it_v2'
  AND pid <> pg_backend_pid();
```

###  Windows:
### Add PostgreSQL bin to PATH (permanent fix for convinence)
**Steps:**
1. Press Win + R, type ``sysdm.cpl``, hit Enter. → Opens System Properties.
2. Go to Advanced tab → click Environment Variables.
3. Under User variables, find Path.
    - If it exists → select it, click Edit.
    - If not → click New.
4.Add this line (adjust version number if needed):
```makefile
C:\Program Files\PostgreSQL\17\bin
```
5. Click OK → close all dialogs.
6. Restart PowerShell / terminal.
7. Test it works:
```powershell
psql --version
createdb --help
```
If it shows version, the Python script will work without changes. 
[Back to start](#creating-environment)
```powershell
# 1. Create database
createdb -U your_username your_database_name

# 2. Run initialization
python init_db_postgres.py

# 3. Delete database
dropdb -U your_username your_database_name

# 3.1 kill all database connection of database
psql -U your_username -d postgres

-- Kill all connections to your_database
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'provision_it_v2'
  AND pid <> pg_backend_pid();
```

## Additional postgreSQL download:

#### For Unix/Linux/macOS:
```bash
brew update
brew install postgresql@17

# Then link it (so psql works globally):
brew link postgresql@17 --force

# You can start PostgreSQL 17 manually or enable background service:
brew services start postgresql@17
# Data directory (default): /usr/local/var/postgresql@17
```
[Back to start](#creating-environment)

#### For Windows:
```powershell
Invoke-WebRequest -Uri "https://get.enterprisedb.com/postgresql/postgresql-17.0-1-windows-x64.exe" -OutFile "$env:USERPROFILE\Downloads\postgresql-17-installer.exe"
Start-Process -FilePath "$env:USERPROFILE\Downloads\postgresql-17-installer.exe" -Wait

# Then follow the GUI installer steps (set password, port 5432, etc.).

# Finally verify:
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -V
```
Then [add global path to the system](#windows).

# Run the Application

```bash
# Development server
python run.py

# Or using Flask CLI
flask run
```

## 🔍 Health Checks

The application includes several health check endpoints:

- `GET /health` - Basic health status
- `GET /health/db` - Database connectivity check
- `GET /health/detailed` - Comprehensive system status

## 🧪 Testing

### By Category

```bash
# Unit tests
python run_tests.py --unit

# Integration tests
python run_tests.py --integration

# E2E tests
python run_tests.py --e2e --auto-flask

# Infrastructure tests
python run_tests.py --infrastructure

# Default: Unit + Integration
python run_tests.py

# With coverage
python run_tests.py --coverage

# With more details
python run_tests.py --verbose
```


## 🔧 Adding New Features

### Adding New API Routes

1. Create a new Python file in `app/routes/` (e.g., `users.py`)
2. Define a Blueprint named `bp`:

```python
from flask import Blueprint, jsonify
from app.models import User

bp = Blueprint('users', __name__)

@bp.route('/users')
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@bp.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())
```

3. The Blueprint will be automatically discovered and registered!

### Adding New Models

The models in `app/models.py` already match the schema structure. To add new models:

1. Add the table to `schema_postgres.sql`
2. Add the corresponding SQLAlchemy model to `app/models.py`
3. Update the `init_db` process if needed

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Debug mode | `true` |
| `FLASK_HOST` | Server host | `127.0.0.1` |
| `FLASK_PORT` | Server port | `5001` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://localhost/database_name` |

### Configuration Classes

- `DevelopmentConfig` - Development settings
- `ProductionConfig` - Production settings  
- `TestingConfig` - Testing settings

## 🤝 Collaborative Development

### For New Team Members

1. **Clone the repository**
2. **Run `setup_env.sh/setup_env.bat` to create `.env`** and configure your database
3. **If step 2 not working: create and install dependencies manually**: `pip install -r requirements.txt`
4. **Initialize database**: `python init_db_postgres.py`
5. **Run tests**: `python run_tests.py`
6. **Start development**: `python run.py`

### Adding Features

- **New APIs**: Drop a `.py` file in `app/routes/` with a Blueprint named `bp`
- **New Models**: Add to `app/models.py` and update `schema_postgres.sql`
- **New Tests**: Add to `tests/` directory
- **No core file changes needed** for new API routes!

## 🐛 Troubleshooting

### Database Connection Issues

1. **Check PostgreSQL is running**: `pg_ctl status`
2. **Verify connection string**: Check `DATABASE_URL` in `.env`
3. **Test connection**: `psql $DATABASE_URL`
4. **Check firewall**: Ensure port 5432 is accessible

### Schema Initialization Issues

1. **Check schema.sql exists**: `ls -la schema_postgres.sql`
2. **Verify SQL syntax**: Test with `psql -f schema_postgres.sql`
3. **Check permissions**: Ensure database user has CREATE privileges
4. **Review logs**: Check Flask application logs for SQL errors

### Import Errors

1. **Activate virtual environment**: `source venv/bin/activate`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Check Python path**: Ensure you're in the project root

### Blueprint Not Registered

1. **Check file name**: Must end with `.py`
2. **Check Blueprint name**: Must be named `bp`
3. **Check syntax**: No import errors in the file
4. **Restart server**: Blueprints are loaded at startup

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Add tests for new functionality
5. Submit a pull request

---

**Happy coding! 🚀**