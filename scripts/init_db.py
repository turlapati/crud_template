#!/usr/bin/env python3
"""
Initialize the database by creating all tables.
This script is designed to be robust and can be run safely even if models
have been imported elsewhere in the application.
"""
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from sqlalchemy import create_engine, inspect, Engine

def setup_project_path() -> Path:
    """Add the project root to the Python path and return it."""
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root

def import_from_path(module_name: str, file_path: Path) -> ModuleType:
    """
    Dynamically import a module from a file path, avoiding re-execution if already imported.
    
    Args:
        module_name: The name to give to the imported module.
        file_path: Path to the module file.
        
    Returns:
        The imported module.
    """
    if module_name in sys.modules:
        return sys.modules[module_name]
        
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if not spec or not spec.loader:
        raise ImportError(f"Could not import module from {file_path}")
        
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def load_all_models() -> None:
    """
    Dynamically import all Python files from the 'app/models' directory
    to ensure SQLAlchemy's declarative base registers them.
    """
    project_root = setup_project_path()
    models_dir = project_root / 'app' / 'models'
    
    print("Loading all models...")
    for model_file in models_dir.glob('*.py'):
        if model_file.name != '__init__.py':
            module_name = f'app.models.{model_file.stem}'
            try:
                import_from_path(module_name, model_file)
                print(f"  ✓ Loaded model: {module_name}")
            except Exception as e:
                # This logic is now safer due to the check in import_from_path
                print(f"  ⚠ Failed to load model {module_name}: {e}")

def verify_tables_exist(engine: Engine) -> bool:
    """
    Verify that all required database tables exist by comparing SQLAlchemy's
    metadata with the actual database schema.
    
    Args:
        engine: SQLAlchemy engine to inspect.
        
    Returns:
        bool: True if all tables exist, False otherwise.
    """
    try:
        from app.db.base import Base  # Import Base here
        
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        required_tables = set(Base.metadata.tables.keys())
        
        if not required_tables:
            print("⚠ No models found in SQLAlchemy metadata. Cannot verify tables.")
            return False
            
        missing_tables = required_tables - existing_tables
        if missing_tables:
            print(f"❌ Missing tables in the database: {', '.join(missing_tables)}")
            return False
        
        print(f"✓ All required tables exist: {', '.join(required_tables)}")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False

def init_db() -> None:
    """
    Initialize the database. This function loads all models, then creates
    all tables defined in the SQLAlchemy metadata.
    """
    # Ensure project path is set up
    setup_project_path()
    
    # This is the crucial step: load all models so Base.metadata is populated
    load_all_models()
    
    # Now that models are loaded, we can import what we need
    from app.core.config import settings
    from app.db.base import Base
    
    print("\nInitializing database...")
    try:
        engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
        
        print("Creating database tables...")
        # create_all() is idempotent and won't re-create existing tables.
        Base.metadata.create_all(bind=engine)
        print("✓ `create_all` command finished.")
        
        # Verify tables were created
        if not verify_tables_exist(engine):
            print("\n⚠ Database initialization failed: Not all tables were created.")
            sys.exit(1)
        
        print("\n✅ Database initialized successfully!")
            
    except Exception as e:
        print(f"❌ An unexpected error occurred during database initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
