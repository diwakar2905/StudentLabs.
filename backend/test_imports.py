#!/usr/bin/env python3
"""Test all module imports"""

def test_import(module_name, import_statement):
    try:
        exec(import_statement)
        print(f"✓ {module_name} imported")
        return True
    except Exception as e:
        print(f"✗ {module_name} error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing imports...\n")
    
    test_import("database",        "from database import init_db, get_db")
    test_import("models",          "from models import *")
    test_import("auth",            "from routes import auth")
    test_import("research",        "from routes import research")
    test_import("generate",        "from routes import generate")
    test_import("export",          "from routes import export")
    test_import("projects",        "from routes import projects")
    test_import("main",            "import main")
    
    print("\nAll imports tested!")
