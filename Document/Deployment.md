# 🚀 Provision-it Deployment Guide

A comprehensive guide to get the Provision-it application running on any system.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

### Required Software
- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 12+** - See installation instructions below
- **Git** - For cloning the repository

### System Requirements
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Disk Space**: At least 1GB free space
- **Network**: Internet connection for package installation

## 🔧 PostgreSQL Installation

### macOS (using Homebrew)
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql@17

# Start PostgreSQL service
brew services start postgresql@17

# Verify installation
psql --version
```

### Windows
1. Download PostgreSQL installer from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run the installer and follow the setup wizard
3. Remember the password you set for the `postgres` user
4. Add PostgreSQL to your PATH:
   - Press `Win + R`, type `sysdm.cpl`, hit Enter
   - Go to Advanced tab → Environment Variables
   - Under User variables, find or create `Path`
   - Add: `C:\Program Files\PostgreSQL\17\bin`
   - Restart your terminal/PowerShell

### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

## 🚀 Quick Start (Recommended)

### Step 1: Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd Provision-it_forked

# Run automated setup (choose your platform)
```

#### For macOS/Linux:
```bash
chmod +x setup_env.sh
./setup_env.sh
```

#### For Windows:
```cmd
setup_env.bat
```

The setup script will:
- ✅ Check Python version (3.8+ required)
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create `.env` file with database configuration
- ✅ Generate secure secret key
- ✅ Test database connectivity

### Step 2: Database Setup

The setup script creates your `.env` file, but you still need to create the database:

```bash
# Create the database (replace 'your_username' with your PostgreSQL username)
createdb -U your_username provision_it

# Initialize the database schema and data
python init_db_postgres.py
```

### Step 3: Start the Application

```bash
# Activate virtual environment (if not already active)
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# if using PowerShell
.\venv\Scripts\Activate.ps1

# Start the application
python run.py

# Or using Flask CLI
flask run
```

## 🛠️ Manual Setup (Alternative)

If the automated setup doesn't work, follow these manual steps:

### Step 1: Environment Setup

```bash
# Navigate to project directory
cd Provision-it_forked

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Database Configuration

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env  # macOS/Linux
# or
type nul > .env  # Windows
```

Add the following content to `.env`:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
FLASK_HOST=127.0.0.1
FLASK_PORT=5001

# Security (generate a secure key)
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/provision_it

# For testing (optional)
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/provision_it_test
```

**Replace the following values:**
- `username`: Your PostgreSQL username
- `password`: Your PostgreSQL password
- `your-secret-key-here`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`

### Step 3: Database Creation and Initialization

```bash
# Create database
createdb -U your_username provision_it

# Initialize schema and data
python init_db_postgres.py
```

### Step 4: Start Application

```bash
python run.py

# Or using Flask CLI
flask run
```

## 🗄️ Database Management

### Initialize Database

```bash
# Create database
createdb -U your_username provision_it

# Initialize schema and data
python init_db_postgres.py
```

### Drop Database

#### macOS/Linux
```bash
# Delete database
dropdb -U your_username provision_it

# Kill all database connections (if needed)
psql -U your_username -d postgres

-- Kill all connections to your database
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'provision_it'
  AND pid <> pg_backend_pid();
```

#### Windows
```bash
# Delete database
dropdb -U your_username provision_it

# Kill all database connections (if needed)
psql -U your_username -d postgres

-- Kill all connections to your database
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'provision_it'
  AND pid <> pg_backend_pid();
```

## 🧪 Testing

Run tests to verify everything is working:

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --unit              # Unit tests only
python run_tests.py --integration       # Integration tests only
python run_tests.py --e2e --auto-flask  # End-to-end tests
python run_tests.py --coverage          # With coverage report
python run_tests.py --verbose           # With more details
```

## 🔍 Health Checks

The application provides several health check endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Basic application health |
| `GET /health/db` | Database connectivity check |
| `GET /health/detailed` | Comprehensive system status |

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. PostgreSQL Connection Issues

**Problem**: `psql: error: connection to server failed`

**Solutions**:
```bash
# Check if PostgreSQL is running
# macOS:
brew services list | grep postgresql

# Linux:
sudo systemctl status postgresql

# Windows: Check Services (services.msc) for PostgreSQL

# Start PostgreSQL if not running
# macOS:
brew services start postgresql@17

# Linux:
sudo systemctl start postgresql

# Test connection
psql -U your_username -d postgres
```

#### 2. Python Version Issues

**Problem**: `Python 3.8+ is required`

**Solutions**:
```bash
# Check Python version
python --version

# Install Python 3.8+ if needed
# macOS:
brew install python@3.11

# Linux:
sudo apt install python3.11

# Windows: Download from python.org
```

#### 3. Virtual Environment Issues

**Problem**: `ModuleNotFoundError` or import errors

**Solutions**:
```bash
# Ensure virtual environment is activated
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 4. Database Permission Issues

**Problem**: `permission denied for database`

**Solutions**:
```bash
# Grant permissions to your user
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE provision_it TO your_username;"

# Or create a new user with proper permissions
psql -U postgres -c "CREATE USER your_username WITH PASSWORD 'your_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE provision_it TO your_username;"
```

#### 5. Port Already in Use

**Problem**: `Address already in use`

**Solutions**:
```bash
# Find process using port 5001
# macOS/Linux:
lsof -i :5001

# Windows:
netstat -ano | findstr :5001

# Kill the process or change port in .env file
FLASK_PORT=5002
```

#### 7. Validation Script Issues

**Problem**: `python validate_setup.py` fails

**Solutions**:
```bash
# Make sure you're in the project directory
cd Provision-it_forked

# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Run validation
python validate_setup.py
```

**Common validation failures**:
- **Python version**: Install Python 3.8+
- **Virtual environment**: Run `python -m venv venv` and activate it
- **Dependencies**: Run `pip install -r requirements.txt`
- **PostgreSQL**: Install PostgreSQL and add to PATH
- **Database**: Create database with `createdb -U your_username provision_it`

### Getting Help

If you're still having issues:

1. **Check the logs**: Look at the terminal output for specific error messages
2. **Verify prerequisites**: Ensure Python 3.8+ and PostgreSQL are properly installed
3. **Test database connection**: Use `psql` to verify you can connect to PostgreSQL
4. **Check file permissions**: Ensure you have read/write access to the project directory
5. **Review .env file**: Verify all database connection details are correct

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Debug mode | `true` |
| `FLASK_HOST` | Server host | `127.0.0.1` |
| `FLASK_PORT` | Server port | `5001` |
| `SECRET_KEY` | Flask secret key | Generated automatically |
| `DATABASE_URL` | PostgreSQL connection string | Configured during setup |

### Configuration Classes

- `DevelopmentConfig` - Development settings (default)
- `ProductionConfig` - Production settings
- `TestingConfig` - Testing settings

## 🚀 Production Deployment

### Security Considerations

1. **Change default secret key**:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Use environment variables** for sensitive data
3. **Enable HTTPS** in production
4. **Set up proper database permissions**
5. **Configure firewall** to restrict database access

### Performance Optimization

1. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5001 run:app
   ```

2. **Configure PostgreSQL** for production workloads
3. **Set up monitoring** and logging
4. **Use a reverse proxy** (nginx) for static files

## 🤝 Development Workflow

### For New Team Members

1. **Clone the repository**
2. **Run setup script**: `./setup_env.sh` or `setup_env.bat`
3. **Create database**: `createdb -U your_username provision_it`
4. **Initialize database**: `python init_db_postgres.py`
5. **Run tests**: `python run_tests.py`
6. **Start development**: `python run.py`

### Adding New Features

- **New APIs**: Create a `.py` file in `app/routes/` with a Blueprint named `bp`
- **New Models**: Add to `app/models.py` and update `schema_postgres.sql`
- **New Tests**: Add to `tests/` directory
- **No core file changes needed** for new API routes!

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

**Need help?** Check the troubleshooting section above or review the application logs for specific error messages.