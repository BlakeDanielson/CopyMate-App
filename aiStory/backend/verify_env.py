#!/usr/bin/env python
"""
Verification script to test the backend environment setup.

This script checks if all required dependencies are installed and can be imported,
tests database connectivity (if database URL is provided), and verifies that
environment variables are properly loaded.

Run this script after setting up your environment to ensure everything is working:
    poetry run python verify_env.py
"""
import importlib
import sys
from typing import Dict, List, Tuple

# ANSI color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_status(message: str, success: bool = True) -> None:
    """Print a status message with appropriate formatting."""
    if success:
        print(f"{GREEN}✓ {message}{RESET}")
    else:
        print(f"{RED}✗ {message}{RESET}")


def check_imports(packages: List[str]) -> Tuple[List[str], List[str]]:
    """Check if packages can be imported.
    
    Args:
        packages: List of package names to check
        
    Returns:
        Tuple of (imported packages, failed packages)
    """
    successful = []
    failed = []
    
    for package in packages:
        try:
            importlib.import_module(package)
            successful.append(package)
        except ImportError as e:
            failed.append(f"{package} ({str(e)})")
            
    return successful, failed


def check_database_connection() -> bool:
    """Test database connection using SQLAlchemy.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine
        import asyncio
        
        from backend.config import settings
        
        if not settings.database_url:
            print(f"{YELLOW}⚠ Database URL not configured. Skipping connection test.{RESET}")
            return False
            
        async def test_connection():
            """Test async database connection."""
            engine = create_async_engine(settings.database_url)
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar() == 1
                
        return asyncio.run(test_connection())
    except Exception as e:
        print(f"{RED}Error testing database connection: {e}{RESET}")
        return False


def check_environment_variables() -> Dict[str, bool]:
    """Check if key environment variables are loaded.
    
    Returns:
        Dictionary of variable names and whether they are set
    """
    try:
        from backend.config import settings
        
        # List of important environment variables to check
        key_vars = [
            "debug",
            "database_url",
            "secret_key",
            "access_token_expire_minutes",
            "refresh_token_expire_days",
            "auth_rate_limit_requests_per_minute",
        ]
        
        results = {}
        for var in key_vars:
            value = getattr(settings, var, None)
            exists = value is not None
            results[var] = exists
            
            # Add extra validation for secret key
            if var == "secret_key" and exists:
                key_length = len(value)
                if key_length < 32:
                    print(f"{YELLOW}⚠ Secret key is too short ({key_length} chars). It should be at least 32 characters.{RESET}")
                    print(f"{YELLOW}  Generate a secure key with: openssl rand -hex 32{RESET}")
                    results[var] = False
            
        return results
    except Exception as e:
        print(f"{RED}Error checking environment variables: {e}{RESET}")
        return {}


def main() -> int:
    """Run all verification checks and display results.
    
    Returns:
        Exit code (0 for success, 1 for errors)
    """
    print(f"{BOLD}Verifying AI Story Creator Backend Environment{RESET}\n")
    
    # Packages to check
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "pydantic_settings",
        "pytest",
        "alembic",
        "asyncpg",
        "aiosqlite",
        "python_jose",
        "passlib",
        "python_multipart",
        "email_validator",
        "tenacity",
        "python_slugify",
        "rich",
        "slowapi",
    ]
    
    # Verify imports
    print(f"{BOLD}Checking dependencies:{RESET}")
    successful, failed = check_imports(required_packages)
    
    for pkg in successful:
        print_status(f"Import {pkg}")
        
    for pkg in failed:
        print_status(f"Import {pkg}", False)
    
    # Check environment
    print(f"\n{BOLD}Checking environment:{RESET}")
    try:
        from backend.config import settings
        print_status(f"Configuration loaded")
        print(f"  App name: {settings.app_name}")
        print(f"  Debug mode: {settings.debug}")
    except Exception as e:
        print_status(f"Configuration loading failed: {e}", False)
    
    # Check environment variables
    env_vars = check_environment_variables()
    for var, exists in env_vars.items():
        if exists:
            print_status(f"Environment variable: {var}")
        else:
            print_status(f"Environment variable: {var} not set", False)
    
    # Check database connection
    print(f"\n{BOLD}Checking database connection:{RESET}")
    db_ok = check_database_connection()
    if db_ok:
        print_status("Database connection successful")
    else:
        print_status("Database connection failed", False)
    
    # Summary
    print(f"\n{BOLD}Verification Summary:{RESET}")
    all_success = (len(failed) == 0)
    
    if all_success and db_ok:
        print(f"{GREEN}All checks passed successfully!{RESET}")
        return 0
    elif all_success:
        print(f"{YELLOW}All package imports successful, but some checks failed. See above for details.{RESET}")
        return 1
    else:
        print(f"{RED}Some checks failed. See above for details.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())