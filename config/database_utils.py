"""
Database utilities and helper functions
"""
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from .database import engine, Base
from .settings import settings
import logging

logger = logging.getLogger(__name__)

def get_database_info() -> dict:
    """
    Get detailed database information

    Returns:
        Dict with database details
    """
    try:
        with engine.connect() as connection:
            # Get database type and version
            result = connection.execute(text("SELECT version()"))
            version_info = result.fetchone()[0] if result else "Unknown"

            return {
                "url": settings.database.url,
                "driver": engine.dialect.name,
                "version": version_info,
                "pool_size": settings.database.pool_size,
                "max_overflow": settings.database.max_overflow,
                "pool_recycle": settings.database.pool_recycle,
                "echo": settings.database.echo,
                "status": "connected"
            }
    except Exception as e:
        return {
            "url": settings.database.url,
            "driver": engine.dialect.name if engine else "Unknown",
            "error": str(e),
            "status": "disconnected"
        }

def check_tables_exist() -> dict:
    """
    Check if required tables exist in database

    Returns:
        Dict with table status
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names(schema="admin")

        required_tables = ["user"]  # Add more tables as needed
        table_status = {}

        for table in required_tables:
            table_status[table] = table in existing_tables

        return {
            "schema": "admin",
            "required_tables": required_tables,
            "existing_tables": existing_tables,
            "table_status": table_status,
            "all_tables_exist": all(table_status.values())
        }
    except Exception as e:
        return {
            "error": str(e),
            "all_tables_exist": False
        }

def create_schema_if_not_exists():
    """
    Create admin schema if it doesn't exist
    """
    try:
        with engine.connect() as connection:
            # Check if schema exists
            result = connection.execute(
                text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'admin'")
            )

            if not result.fetchone():
                # Create schema
                connection.execute(text("CREATE SCHEMA admin"))
                connection.commit()
                logger.info("Created admin schema")
            else:
                logger.info("Admin schema already exists")

    except SQLAlchemyError as e:
        logger.error(f"Failed to create admin schema: {e}")
        raise

def reset_database():
    """
    Drop and recreate all tables (USE WITH CAUTION!)
    """
    try:
        logger.warning("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)

        logger.info("Creating all tables...")
        Base.metadata.create_all(bind=engine)

        logger.info("Database reset completed")
        return True

    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return False

def get_connection_pool_status() -> dict:
    """
    Get connection pool status

    Returns:
        Dict with pool information
    """
    try:
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
    except Exception as e:
        return {"error": str(e)}

def diagnose_database_issues() -> dict:
    """
    Comprehensive database diagnosis

    Returns:
        Dict with diagnosis results
    """
    diagnosis = {
        "timestamp": str(__import__("datetime").datetime.now()),
        "settings": {
            "url": settings.database.url,
            "pool_size": settings.database.pool_size,
            "echo": settings.database.echo
        }
    }

    # Test basic connection
    try:
        from .database import test_db_connection
        diagnosis["connection_test"] = {"status": test_db_connection()}
    except Exception as e:
        diagnosis["connection_test"] ={"status": False}
        diagnosis["connection_error"] = str(e)

    # Get database info
    diagnosis["database_info"] = get_database_info()

    # Check tables
    diagnosis["table_check"] = check_tables_exist()

    # Pool status
    diagnosis["pool_status"] = get_connection_pool_status()

    return diagnosis