#!/usr/bin/env python3
"""
Shared utilities for test database management.
Contains common functions to eliminate code duplication.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
from pathlib import Path


def setup_paths():
    """Set up Python paths for test database scripts."""
    project_root = Path(__file__).parent.parent.parent
    test_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(test_dir))


def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    
    # Get database configuration
    database_url = os.environ.get('DATABASE_URL')
    test_database_url = os.environ.get('TEST_DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    return database_url, test_database_url


def parse_database_url(database_url):
    """Parse database URL into components."""
    import re
    
    # Parse postgresql://user:password@host:port/database
    pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, database_url)
    
    if not match:
        raise ValueError(f"Invalid database URL format: {database_url}")
    
    user, password, host, port, database = match.groups()
    
    return {
        'user': user,
        'password': password,
        'host': host,
        'port': int(port),
        'database': database
    }


def get_server_connection_params(main_db_config):
    """Get server connection parameters for database operations."""
    return {
        'host': main_db_config['host'],
        'port': main_db_config['port'],
        'user': main_db_config['user'],
        'password': main_db_config['password'],
        'database': 'postgres'
    }


def get_test_connection_params(test_db_config):
    """Get test database connection parameters."""
    return {
        'host': test_db_config['host'],
        'port': test_db_config['port'],
        'user': test_db_config['user'],
        'password': test_db_config['password'],
        'database': test_db_config['database']
    }


def get_sample_users_data():
    """Get sample users data for seeding."""
    return [
        ('admin', 'admin@test.com', 'admin123', True),
        ('testuser1', 'user1@test.com', 'password123', False),
        ('testuser2', 'user2@test.com', 'password123', False),
        ('manager1', 'manager@test.com', 'manager123', True)
    ]


def seed_test_database(test_db_config):
    """Seed test database with sample data for testing."""
    try:
        conn = psycopg2.connect(**get_test_connection_params(test_db_config))
        cursor = conn.cursor()
        
        print("📝 Seeding test database with sample data...")
        
        # Insert sample users (without specifying user_id since it's GENERATED ALWAYS)
        users_data = get_sample_users_data()
        
        user_ids = []
        for username, email, password, is_manager in users_data:
            cursor.execute("""
                INSERT INTO "Users" (user_name, email, password, is_manager, created_at, is_deleted)
                VALUES (%s, %s, %s, %s, NOW(), FALSE)
                RETURNING user_id
            """, (username, email, password, is_manager))
            user_ids.append(cursor.fetchone()[0])
        
        # Insert sample assets (without specifying asset_id since it's GENERATED ALWAYS)
        assets_data = [
            ('Modern Art Painting', 'Contemporary art collection piece', 1000, 1, 100, 1000000.00),
            ('Technology Equity Fund A', 'Diversified tech sector investment fund', 500, 1, 50, 500000.00),
            ('Commercial Real Estate Trust', 'Prime location commercial property portfolio', 2000, 10, 200, 2000000.00),
            ('Crypto Token', 'Digital asset cryptocurrency holdings', 10000, 1, 1000, 100000.00),
            ('Vintage Sports Car', 'Classic collectible automobile', 100, 1, 10, 250000.00)
        ]
        
        asset_ids = []
        for name, description, total_unit, unit_min, unit_max, total_value in assets_data:
            cursor.execute("""
                INSERT INTO "Assets" (asset_name, asset_description, total_unit, unit_min, unit_max, total_value, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                RETURNING asset_id
            """, (name, description, total_unit, unit_min, unit_max, total_value))
            asset_ids.append(cursor.fetchone()[0])
        
        # Insert sample fractions (using actual user_ids and asset_ids from above)
        fractions_data = [
            # Modern Art Painting (Asset 0)
            (asset_ids[0], user_ids[0], None, 600, True, 1000.00),   # admin owns 600 units
            (asset_ids[0], user_ids[1], None, 400, True, 1000.00),   # testuser1 owns 400 units
            # Technology Equity Fund (Asset 1)
            (asset_ids[1], user_ids[0], None, 300, True, 1000.00),   # admin owns 300 units
            (asset_ids[1], user_ids[2], None, 200, True, 1000.00),   # testuser2 owns 200 units
            # Commercial Real Estate (Asset 2)
            (asset_ids[2], user_ids[1], None, 1000, True, 1000.00),  # testuser1 owns 1000 units
            (asset_ids[2], user_ids[3], None, 1000, True, 1000.00),  # manager1 owns 1000 units
            # Crypto Token (Asset 3)
            (asset_ids[3], user_ids[0], None, 5000, True, 10.00),    # admin owns 5000 units
            (asset_ids[3], user_ids[1], None, 5000, True, 10.00),    # testuser1 owns 5000 units
            # Vintage Sports Car (Asset 4)
            (asset_ids[4], user_ids[2], None, 50, True, 2500.00),    # testuser2 owns 50 units
            (asset_ids[4], user_ids[3], None, 50, True, 2500.00)     # manager1 owns 50 units
        ]
        
        for asset_id, owner_id, parent_id, units, is_active, value_per_unit in fractions_data:
            cursor.execute("""
                INSERT INTO "Fractions" (asset_id, owner_id, parent_fraction_id, units, is_active, created_at, value_perunit)
                VALUES (%s, %s, %s, %s, %s, NOW(), %s)
            """, (asset_id, owner_id, parent_id, units, is_active, value_per_unit))
        
        # Insert sample asset value history (using actual asset_ids)
        value_history_data = [
            # Modern Art Painting history
            (asset_ids[0], 1000000.00, 'manual_adjust', user_ids[0], 'Initial value'),
            (asset_ids[0], 1050000.00, 'manual_adjust', user_ids[0], 'Market appreciation'),
            # Technology Equity Fund history
            (asset_ids[1], 500000.00, 'manual_adjust', user_ids[0], 'Initial value'),
            (asset_ids[1], 520000.00, 'manual_adjust', user_ids[0], 'Tech sector growth'),
            # Commercial Real Estate history
            (asset_ids[2], 2000000.00, 'manual_adjust', user_ids[0], 'Initial value'),
            (asset_ids[2], 2050000.00, 'manual_adjust', user_ids[0], 'Property appreciation'),
            # Crypto Token history
            (asset_ids[3], 100000.00, 'manual_adjust', user_ids[0], 'Initial value'),
            (asset_ids[3], 110000.00, 'manual_adjust', user_ids[0], 'Market recovery'),
            # Vintage Sports Car history
            (asset_ids[4], 250000.00, 'manual_adjust', user_ids[0], 'Initial valuation')
        ]
        
        for asset_id, value, source, adjusted_by, reason in value_history_data:
            cursor.execute("""
                INSERT INTO "AssetValueHistory" (asset_id, value, recorded_at, source, adjusted_by, adjustment_reason)
                VALUES (%s, %s, NOW(), %s, %s, %s)
            """, (asset_id, value, source, adjusted_by, reason))
        
        conn.commit()
        print("✅ Test database seeded with sample data")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error seeding test database: {e}")
        sys.exit(1)


def clear_test_database_data(test_db_config):
    """Clear all data from test database tables."""
    try:
        conn = psycopg2.connect(
            host=test_db_config['host'],
            port=test_db_config['port'],
            user=test_db_config['user'],
            password=test_db_config['password'],
            database=test_db_config['database']
        )
        
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('TRUNCATE TABLE "AssetValueHistory" CASCADE')
        cursor.execute('TRUNCATE TABLE "Transactions" CASCADE')
        cursor.execute('TRUNCATE TABLE "Offers" CASCADE')
        cursor.execute('TRUNCATE TABLE "Fractions" CASCADE')
        cursor.execute('TRUNCATE TABLE "Assets" CASCADE')
        cursor.execute('TRUNCATE TABLE "Users" CASCADE')
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error clearing test database: {e}")
        sys.exit(1)