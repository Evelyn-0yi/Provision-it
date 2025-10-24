#!/usr/bin/env python3
"""
Comprehensive test runner for the Provision-it project.
Handles unit tests, Api tests, and Flask app management.
"""

import sys
import subprocess
import argparse
import os
import time
import threading
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print('='*60)


def print_step(step, description):
    """Print a step indicator."""
    print(f"\n📋 Step {step}: {description}")


def run_command(cmd, description, capture_output=False):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=capture_output, text=True)
        print(f"✅ {description} completed successfully")
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        if capture_output and e.stderr:
            print(f"Error: {e.stderr}")
        return False, e.stderr if capture_output else ""


def check_environment():
    """Check if required environment is set up."""
    print_step(1, "Checking environment setup")
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("⚠️  Warning: .env file not found")
        print("   Make sure you have configured your database settings")
        print("   You can run: python setup_env.sh (Linux/Mac) or setup_env.bat (Windows)")
        return False
    
    # Check if DATABASE_URL is set
    if not os.environ.get('DATABASE_URL'):
        print("⚠️  Warning: DATABASE_URL not set in environment")
        print("   Please set DATABASE_URL in your .env file")
        return False
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not activated")
        print("   Please activate your virtual environment first:")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   venv\\Scripts\\activate    # Windows")
        return False
    
    # Check if required packages are installed
    try:
        import psycopg2
        print("✅ PostgreSQL driver (psycopg2) is available")
    except ImportError:
        print("❌ Error: psycopg2 not installed")
        print("   Please install dependencies: pip install -r requirements.txt")
        return False
    
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ Error: pytest not installed")
        print("   Please install dependencies: pip install -r requirements.txt")
        return False
    
    print("✅ Environment check completed")
    return True


def check_flask_app(port=5001):
    """Check if Flask app is running."""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Flask application is running on http://localhost:{port}")
            return True
    except Exception:
        pass
    return False


def start_flask_app(port=5001):
    """Start Flask app in background."""
    print(f"🔄 Starting Flask application on port {port}...")
    
    # Set up environment variables for Flask
    env = os.environ.copy()
    env['FLASK_PORT'] = str(port)
    env['FLASK_HOST'] = '127.0.0.1'
    env['FLASK_DEBUG'] = 'false'
    
    # FORCE use of test database for E2E tests
    if env.get('TEST_DATABASE_URL'):
        env['DATABASE_URL'] = env['TEST_DATABASE_URL']
        print(f"   Using test database: {env['TEST_DATABASE_URL'].split('@')[-1]}")
    else:
        print("   ⚠️  Warning: TEST_DATABASE_URL not set, using DATABASE_URL")
    
    # Create log file for Flask output
    log_file = open('flask_test.log', 'w')
    
    # Start Flask app in background
    flask_process = subprocess.Popen(
        [sys.executable, 'run.py'],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )
    
    # Wait for Flask app to start
    for i in range(30):  # Wait up to 30 seconds
        time.sleep(1)
        if check_flask_app(port):
            print(f"✅ Flask application started successfully on port {port}")
            return flask_process
        print(f"   Waiting for Flask app... ({i+1}/30)")
    
    # Flask failed to start - show the logs
    print("❌ Flask application failed to start")
    print("\n📋 Flask startup logs:")
    log_file.close()
    try:
        with open('flask_test.log', 'r') as f:
            logs = f.read()
            if logs:
                print(logs)
            else:
                print("   No logs available")
    except Exception as e:
        print(f"   Could not read logs: {e}")
    
    flask_process.terminate()
    flask_process.wait()
    return None


def stop_flask_app(flask_process):
    """Stop Flask app."""
    if flask_process:
        print("🔄 Stopping Flask application...")
        flask_process.terminate()
        flask_process.wait()
        print("✅ Flask application stopped")
        
        # Clean up log file
        try:
            if Path('flask_test.log').exists():
                Path('flask_test.log').unlink()
        except Exception:
            pass


def setup_playwright():
    """Set up Playwright if needed."""
    try:
        import playwright
        print("✅ Playwright is available")
        return True
    except ImportError:
        print("🔄 Installing Playwright...")
        success, _ = run_command([
            sys.executable, '-m', 'pip', 'install', 'playwright', 'pytest-playwright'
        ], "Installing Playwright packages")
        
        if not success:
            return False
        
        # Install browser
        success, _ = run_command([
            sys.executable, '-m', 'playwright', 'install', 'chromium'
        ], "Installing Chromium browser")
        
        return success


def setup_test_database():
    """Set up test database with fresh data."""
    print_step(2, "Setting up test database")
    
    try:
        # Always reset the test database to ensure clean state
        script_path = Path('test/test_database/manage_test_db.py')
        if script_path.exists():
            print("🔄 Resetting test database for clean test run...")
            success, _ = run_command([sys.executable, str(script_path), 'reset'], 
                                   "Reset test database", capture_output=True)
            if not success:
                print("❌ Test database reset failed")
                return False
            
            print("📝 Setting up fresh test database...")
            success, _ = run_command([sys.executable, str(script_path), 'full-setup'], 
                                   "Setup test database", capture_output=True)
            if success:
                print("✅ Test database setup completed")
                return True
            else:
                print("❌ Test database setup failed")
                return False
        else:
            print("❌ Test database management script not found")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up test database: {e}")
        return False


def run_e2e_tests(args):
    """Run E2E tests using Playwright."""
    print_step(3, "Running E2E Tests (Playwright Framework)")
    
    e2e_dir = Path('test/tests/E2E')
    
    # Check if E2E directory exists
    if not e2e_dir.exists():
        print("❌ E2E test directory not found")
        return False
    
    # Check if npm is installed
    try:
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm not found. Please install Node.js and npm")
        print("   Visit: https://nodejs.org/")
        return False
    
    # Change to E2E directory
    original_dir = os.getcwd()
    os.chdir(e2e_dir)
    
    try:
        # Install dependencies if package.json exists
        if Path('package.json').exists():
            print("🔄 Installing E2E test dependencies...")
            success, _ = run_command(['npm', 'install'], "Install npm packages", capture_output=True)
            if not success:
                print("❌ Failed to install npm packages")
                return False
            
            # Install Playwright browsers if needed
            print("🔄 Ensuring browsers are installed...")
            subprocess.run(['npx', 'playwright', 'install'], 
                         capture_output=True, check=False)
        
        # Determine which tests to run
        if args.verbose:
            cmd = ['npx', 'playwright', 'test', '--reporter=list']
        else:
            cmd = ['npx', 'playwright', 'test']
        
        # Add specific test file if specified
        if hasattr(args, 'test_file') and args.test_file:
            cmd.append(args.test_file)
        
        # Set up environment for Playwright
        # E2E tests need the HTML file server (port 8080) AND Flask API (port 5001)
        # Don't skip webServer for E2E tests
        e2e_env = os.environ.copy()
        # e2e_env['SKIP_WEBSERVER'] = '1'  # Don't set this - E2E needs HTML files!
        
        # E2E tests use port 8080 for HTML files (served by webServer in config)
        # Flask API runs on port 5001 (started by --auto-flask)
        
        # Run E2E tests
        print("🎭 Running E2E tests...")
        result = subprocess.run(cmd, capture_output=False, env=e2e_env)
        
        if result.returncode == 0:
            print("\n🎉 E2E tests completed successfully!")
            print("\n📊 View detailed report:")
            print("   npx playwright show-report")
            return True
        else:
            print("\n💥 E2E tests failed!")
            print("\n🔧 Debugging:")
            print("   - View report: npx playwright show-report")
            print("   - Run with UI: npx playwright test --ui")
            print("   - Debug mode: npx playwright test --debug")
            return False
    
    finally:
        os.chdir(original_dir)


def run_tests(args):
    """Run the actual tests."""
    print_step(3, "Running tests")
    
    # Base pytest command
    cmd = [sys.executable, '-m', 'pytest']
    
    # Add verbosity
    if args.verbose:
        cmd.append('-v')
    
    # Determine test scope
    if args.unit:
        cmd.extend(['test/tests/unit/', '--maxfail=1'])
        test_type = "Unit Tests"
    elif args.integration:
        cmd.extend(['test/tests/integration/', '--maxfail=1'])
        test_type = "Integration Tests"
    elif args.infrastructure:
        cmd.extend(['test/tests/infrastructure/', '--maxfail=1'])
        test_type = "Infrastructure Tests"
    else:
        # Run unit and integration tests by default (exclude E2E and infrastructure)
        cmd.extend(['test/tests/unit/', 'test/tests/integration/', '--maxfail=1'])
        test_type = "All Backend Tests (Unit + Integration)"
    
    # Add coverage if requested
    if args.coverage and not args.fast:
        cmd.extend([
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            '--cov-report=xml:coverage.xml',
            '--cov-fail-under=40'
        ])
    
    # Add other options
    if not args.show_warnings:
        cmd.append('--disable-warnings')
    cmd.append('--tb=short')
    
    # Run the tests
    success, output = run_command(cmd, f"Running {test_type}")
    
    if success:
        print(f"\n🎉 {test_type} completed successfully!")
        if args.coverage and not args.fast:
            print("\n📊 Coverage report generated:")
            print("   - HTML: htmlcov/index.html")
            print("   - XML:  coverage.xml")
    else:
        print(f"\n💥 {test_type} failed!")
        if output:
            print(f"Output: {output}")
    
    return success


def run_frontend_tests(args):
    """Run frontend unit tests using Jest."""
    print_step(3, "Running Frontend Unit Tests (Jest Framework)")
    
    frontend_test_dir = Path('test/tests/Jest')
    
    # Check if frontend test directory exists
    if not frontend_test_dir.exists():
        print("❌ Frontend unit test directory not found")
        return False
    
    # Check if npm is installed
    try:
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm not found. Please install Node.js and npm")
        print("   Visit: https://nodejs.org/")
        return False
    
    # Change to frontend test directory
    original_dir = os.getcwd()
    os.chdir(frontend_test_dir)
    
    try:
        # Install dependencies if package.json exists
        if Path('package.json').exists():
            print("🔄 Installing frontend test dependencies...")
            success, _ = run_command(['npm', 'install'], "Install npm packages", capture_output=True)
            if not success:
                print("❌ Failed to install npm packages")
                return False
        
        # Determine which tests to run
        cmd = ['npm', 'test']
        if args.coverage:
            cmd = ['npm', 'run', 'test:coverage']
        elif args.verbose:
            cmd = ['npm', 'run', 'test:verbose']
        
        # Run Jest tests
        print("🧪 Running frontend unit tests...")
        result = subprocess.run(cmd, capture_output=False)
        
        if result.returncode == 0:
            print("\n🎉 Frontend unit tests completed successfully!")
            if args.coverage:
                print("\n📊 View coverage report:")
                print("   Open test/tests/Jest/coverage/index.html in browser")
            return True
        else:
            print("\n💥 Frontend unit tests failed!")
            print("\n🔧 Debugging:")
            print("   - Run with verbose: npm run test:verbose")
            print("   - Run in watch mode: npm run test:watch")
            return False
    
    finally:
        os.chdir(original_dir)


def main():
    parser = argparse.ArgumentParser(description='Run tests for Provision-it project with automatic test database setup')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only (test/tests/unit/)')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only (test/tests/integration/)')
    parser.add_argument('--e2e', action='store_true', help='Run E2E tests (test/tests/E2E/)')
    parser.add_argument('--Jest', action='store_true', help='Run frontend unit tests (test/tests/Jest/)')
    parser.add_argument('--infrastructure', action='store_true', help='Run infrastructure tests (test/tests/infrastructure/)')
    parser.add_argument('--playwright', action='store_true', help='Alias for --e2e')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--fast', action='store_true', help='Run tests quickly (no coverage)')
    parser.add_argument('--skip-db-setup', action='store_true', help='Skip test database setup')
    parser.add_argument('--reset-db', action='store_true', help='Reset test database before running tests')
    parser.add_argument('--auto-flask', action='store_true', help='Automatically start/stop Flask app for E2E tests')
    parser.add_argument('--skip-flask-check', action='store_true', help='Skip Flask app availability check')
    parser.add_argument('--test-file', type=str, help='Specific E2E test file to run')
    parser.add_argument('--flask-port', type=int, default=5001, help='Port for Flask app (default: 5001)')
    parser.add_argument('--show-warnings', action='store_true', help='Show test warnings (hidden by default)')
    
    args = parser.parse_args()
    
    print_header("Provision-it Comprehensive Test Runner")
    print("This script handles Unit, Integration, and E2E tests with automatic setup.")
    
    # Check environment
    if not check_environment():
        print_header("Environment Setup Required! ⚠️")
        print("\n🔧 Please fix the environment issues above and try again.")
        print("\n💡 Quick setup:")
        print("   1. Activate virtual environment: source venv/bin/activate")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Run tests: python run_tests.py")
        sys.exit(1)
    
    flask_process = None
    try:
        # Handle frontend unit tests
        if args.Jest:
            print_header("Running Frontend Unit Tests (Jest)")
            print("JavaScript unit tests for embedded functions in HTML files")
            
            success = run_frontend_tests(args)
            
            if success:
                print_header("Frontend Unit Tests Completed Successfully! 🎉")
                print("\n💡 Next steps:")
                print("   - View coverage: open test/tests/Jest/coverage/index.html")
                print("   - Run in watch mode: cd test/tests/Jest && npm run test:watch")
            else:
                print_header("Frontend Unit Tests Failed! 💥")
                print("\n🔧 Troubleshooting:")
                print("   - Check npm installation: npm --version")
                print("   - Install dependencies: cd test/tests/Jest && npm install")
                print("   - Run with verbose: cd test/tests/Jest && npm run test:verbose")
                sys.exit(1)
        # Handle E2E tests separately
        elif args.e2e or args.playwright:
            print_header("Running E2E Tests (Playwright)")
            print("Browser-based end-to-end tests for frontend HTML pages")
            
            # Start Flask app if --auto-flask is specified
            if args.auto_flask:
                if not check_flask_app(args.flask_port):
                    flask_process = start_flask_app(args.flask_port)
                    if not flask_process:
                        print("❌ Failed to start Flask app. Exiting.")
                        sys.exit(1)
                else:
                    print(f"✅ Flask app already running on port {args.flask_port}")
            
            success = run_e2e_tests(args)
            
            if success:
                print_header("E2E Tests Completed Successfully! 🎉")
                print("\n💡 Next steps:")
                print("   - View detailed report: cd test/tests/E2E && npx playwright show-report")
                print("   - Run with UI: cd test/tests/E2E && npm run test:ui")
                print("   - Debug tests: cd test/tests/E2E && npm run test:debug")
            else:
                print_header("E2E Tests Failed! 💥")
                print("\n🔧 Troubleshooting:")
                print("   - Check if Flask app is running (use --auto-flask)")
                print("   - View report: cd test/tests/E2E && npx playwright show-report")
                print("   - Run with UI: cd test/tests/E2E && npm run test:ui")
                sys.exit(1)
        else:
            # Setup test database unless skipped (not needed for Playwright)
            if not args.skip_db_setup:
                if args.reset_db:
                    print_step(2, "Resetting test database")
                    try:
                        from test_database.setup import reset_test_database
                        success = reset_test_database()
                        if not success:
                            print("❌ Test database reset failed")
                            sys.exit(1)
                    except ImportError:
                        script_path = Path('test/test_database/manage_test_db.py')
                        if script_path.exists():
                            success, _ = run_command(['python', str(script_path), 'reset'], 
                                                   "Manual test database reset", capture_output=True)
                            if not success:
                                sys.exit(1)
                
                success = setup_test_database()
                if not success:
                    print("❌ Test database setup failed. Exiting.")
                    sys.exit(1)
            else:
                print_step(2, "Skipping test database setup (--skip-db-setup)")
            
            # Run tests
            success = run_tests(args)
            
            if success:
                print_header("Test Run Completed Successfully! 🎉")
                print("\n💡 Tips:")
                print("   - Use --unit to run only unit tests (44 tests)")
                print("   - Use --integration to run only integration tests (22 tests)")
                print("   - Use --e2e for E2E tests (13 tests)")
                print("   - Use --Jest for frontend unit tests")
                print("   - Use --infrastructure for database setup tests (19 tests)")
                print("   - Use --coverage to see test coverage")
                print("   - Use --verbose for detailed output")
            else:
                print_header("Test Run Failed! 💥")
                print("\n🔧 Troubleshooting:")
                print("   - Check test database setup: python test/test_database/manage_test_db.py info")
                print("   - Reset test database: python test/test_database/manage_test_db.py reset")
                print("   - Run tests with --verbose for more details")
                sys.exit(1)
    
    finally:
        # Clean up Flask app if we started it
        if flask_process:
            stop_flask_app(flask_process)


if __name__ == '__main__':
    main()