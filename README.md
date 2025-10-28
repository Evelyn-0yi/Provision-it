<h1 align="center">
  <img src="frontend/Icons/pvit90.png" width="150px"/><br/>
  Fractionalized Real-World Assets Database Schema
</h1>

This project implements a proof-of-concept schema and system for **fractionalised ownership of real-world assets**.
It supports asset creation, fraction trading, valuation tracking, and historical ledger views.

## Problem Statement

We think creating a database schema for fractionalised ownership of real world assets will solve the problem of tracking, trading, and reporting asset fractions at scale.

**We'll know we've succeeded if:**
- Users can create assets, divide them into fractions, and trade them reliably
- The system maintains a clear ledger of ownership history and asset values (whole and fractional) at any point in time
- Queries remain performant even as the number of assets and trades grows large

## Project Scope

### Must Have
- Database schema for assets, fractions, holdings, users, and transactions
- Ability to trade fractions between owners with real-time updates
- Ownership ledger to view history and snapshots
- Asset valuation reporting (whole + fractional)
- Platform manager role for approving assets and setting fraction counts

### Nice to Have
- Support for multiple asset categories (property, collectibles, etc.)
- Query optimization and performance reports
- Performance/stress testing framework
- Basic UI with light/dark mode
- API layer with OpenAPI routes
- User authentication & activity tracking

### Not in Scope
- Real-time price feeds and external market integration
- Guest user roles
- Advanced trading features (bidding/auctions)
- Blockchain/tokenisation implementation

<hr/>

## Dependencies
Before cloning and attempting to run this code, you will need:
- Python 3.8+
- PostgreSQL 12+
- Git (Optional, repo can also be downloaded as .zip)
- Virtual Environment (venv)

<br/>

## Getting Started

This project provides a complete database schema and API implementation for fractionalized real-world asset management, developed for Provision-it.

1. Clone this repo to your device.
2. Run the automated setup script:
   - **macOS/Linux**: `./setup_env.sh`
   - **Windows**: `setup_env.bat`
3. Create a PostgreSQL database and configure your `.env` file with database settings
4. Initialize the database schema and data: `python init_db_postgres.py`
5. Start the application: `python run.py` or `flask run`
6. Access the application at `http://localhost:5001`

<br/>

## Deployment

You can deploy this application to any hosting platform of your choice. For production deployment:

1. Configure production environment variables in `.env`
2. Set up PostgreSQL database on your hosting platform
3. Install dependencies: `pip install -r requirements.txt`
4. Initialize database: `python init_db_postgres.py`
5. Use a production WSGI server like Gunicorn: `gunicorn -w 4 -b 0.0.0.0:5001 run:app`

For detailed deployment instructions, see [SetUp.md](Document/SetUp.md).

<br/>

## Features

<details>
  <summary>User Management</summary>
  
  * User registration and authentication
  * Profile management
  * Session handling and security
  * User portfolio tracking
</details>

<details>
  <summary>Admin Panel</summary>
  
  * Adding new assets
  * Modifying existed assets value
  * Assets metadata and last updated value
</details>

<details>
  <summary>Asset Management</summary>
  
  * Real-world asset registration and tracking
  * Asset value history and monitoring
  * Asset metadata
  * Fractional ownership structure
</details>

<details>
  <summary>Trading System</summary>
  
  * Buy and sell asset fractions
  * Offer creation and management
  * Transaction processing and history
</details>

<details>
  <summary>Portfolio Management</summary>
  
  * User portfolio tracking
  * Fraction ownership management
  * Transaction history
  * Value calculations and reporting
</details>

<br/>

## Tech Stack

- **Database Schema**: PostgreSQL with comprehensive fractionalized asset management
- Backend Framework: Flask
- Database: PostgreSQL
- ORM: SQLAlchemy
- Authentication: Flask-based
- Testing: Pytest, Playwright (E2E), Jest (Frontend)
- CI: GitHub Actions

<br/>

## Project Structure

### Backend Architecture

```
app/
├── controllers/         # MVC Controllers
├── services/            # MVC Services (business logic)
├── views/               # MVC Views (response formatting)
├── routes/              # URL routing with Blueprint auto-discovery
├── models.py            # SQLAlchemy models
├── database.py          # Database configuration
└── decorators.py        # Authentication and validation decorators
```

### Frontend

```
frontend/
├── *.html              # HTML templates for web interface
├── common.css          # Styling and layout
└── Icons/              # Application icons and assets
```

### Database Schema Files

```
├── schema_postgres.sql      # Main database schema with tables, functions, triggers
├── import_postgres.sql      # Initial data import for testing
├── fix_sequences.sql        # Fix sequence synchronization issues
└── init_db_postgres.py      # Database initialization script
```

### Core Application Files

```
├── run.py                  # Application entry point
├── run_tests.py            # Comprehensive test runner
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
└── .env                    # Environment configuration
```

### Setup Scripts

```
├── setup_env.sh            # Automated setup script for Unix/Linux/macOS
└── setup_env.bat           # Automated setup script for Windows
```

### Testing

```
test/
├── tests/             # Comprehensive test suite
│   ├── E2E/           # End-to-end tests with Playwright
│   ├── integration/   # Integration tests
│   ├── Jest/          # Frontend JavaScript tests
│   └── unit/          # Unit tests
└── test_database/     # Testing database utilities
```

<br/>

## API Documentation

The application provides RESTful APIs for all major functionality:

- **Authentication**: User registration, login, profile management
- **Assets**: Asset CRUD operations, value tracking
- **Fractions**: Fractional ownership management
- **Trading**: Buy/sell operations, offer management
- **Portfolio**: User portfolio tracking and management
- **Transactions**: Transaction history and processing

For detailed API documentation, see [API_DOCUMENTATION.md](Document/API_DOCUMENTATION.md).

<br/>

## Database Schema

The core of this project is a comprehensive PostgreSQL database schema designed specifically for fractionalized real-world asset management. The schema includes the following main entities:

- **Users**: User accounts and profiles for asset owners and traders
- **Assets**: Real-world assets available for fractionalization (properties, collectibles, etc.)
- **Fractions**: Fractional ownership units representing portions of assets
- **Transactions**: Complete buy/sell transaction records with ownership transfers
- **Offers**: Trading offers and bids for asset fractions
- **AssetValueHistory**: Historical asset value tracking for both whole and fractional valuations
- **Portfolios**: User portfolio tracking and management

This schema enables reliable tracking of ownership history, real-time trading capabilities, and comprehensive reporting at scale.

For detailed schema information, see `schema_postgres.sql` and [ER_diagram.png](Document/ER_diagram.png).

<br/>

## Testing

Run the comprehensive test suite:

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

<br/>

## Health Checks

The application includes several health check endpoints:

- `GET /health` - Basic application health
- `GET /health/db` - Database connectivity check
- `GET /health/detailed` - Comprehensive system status

<br/>

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Debug mode | `true` |
| `FLASK_HOST` | Server host | `127.0.0.1` |
| `FLASK_PORT` | Server port | `5001` |
| `SECRET_KEY` | Flask secret key | Generated automatically |
| `DATABASE_URL` | PostgreSQL connection string | Configured during setup |

<br/>

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Add tests for new functionality
5. Submit a pull request

<br/>

## License

This project is open source and available under the [MIT License](./LICENSE).

© 2025 Group 12 – Provision IT (COMP30022, University of Melbourne)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

<br/>

## Links

- [SetUp Guide](Document/SetUp.md)
- [API Documentation](Document/API_DOCUMENTATION.md)
- [Source Code](https://github.com/Evelyn-0yi/Provision-it)

**Client**: Provision-it  
**Project**: Fractionalized Real-World Assets Database Schema

---

**Happy coding! 🚀**
