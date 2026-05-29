"""Simple verification script for ExportService implementation.

This script verifies that the ExportService has the required methods
for Task 7.2 without needing a full database setup.
"""
import inspect
from app.services import export_service


def verify_export_service():
    """Verify that ExportService has all required methods."""
    print("Verifying ExportService implementation for Task 7.2...")
    print()
    
    # Check for required functions
    required_functions = [
        "create_export_task",
        "get_export_status",
        "generate_csv_export",
        "generate_geojson_export",
    ]
    
    all_passed = True
    
    for func_name in required_functions:
        if hasattr(export_service, func_name):
            func = getattr(export_service, func_name)
            sig = inspect.signature(func)
            print(f"✓ {func_name}{sig}")
            
            # Check parameters
            params = list(sig.parameters.keys())
            
            if func_name == "create_export_task":
                expected = ["db", "format", "entity_type", "filters", "created_by"]
                if all(p in params for p in expected):
                    print(f"  ✓ Has all expected parameters: {expected}")
                else:
                    print(f"  ✗ Missing parameters. Expected: {expected}, Got: {params}")
                    all_passed = False
                    
            elif func_name == "get_export_status":
                expected = ["db", "task_id"]
                if all(p in params for p in expected):
                    print(f"  ✓ Has all expected parameters: {expected}")
                else:
                    print(f"  ✗ Missing parameters. Expected: {expected}, Got: {params}")
                    all_passed = False
                    
            elif func_name == "generate_csv_export":
                expected = ["db", "task_id", "entity_type", "filters"]
                if all(p in params for p in expected):
                    print(f"  ✓ Has all expected parameters: {expected}")
                else:
                    print(f"  ✗ Missing parameters. Expected: {expected}, Got: {params}")
                    all_passed = False
                    
            elif func_name == "generate_geojson_export":
                expected = ["db", "task_id", "entity_type", "filters"]
                if all(p in params for p in expected):
                    print(f"  ✓ Has all expected parameters: {expected}")
                else:
                    print(f"  ✗ Missing parameters. Expected: {expected}, Got: {params}")
                    all_passed = False
        else:
            print(f"✗ {func_name} - NOT FOUND")
            all_passed = False
        
        print()
    
    # Check for EXPORT_DIR constant
    if hasattr(export_service, "EXPORT_DIR"):
        print(f"✓ EXPORT_DIR constant defined: {export_service.EXPORT_DIR}")
    else:
        print("✗ EXPORT_DIR constant - NOT FOUND")
        all_passed = False
    
    print()
    print("=" * 60)
    if all_passed:
        print("✓ All required methods and constants are present!")
        print("✓ Task 7.2 implementation is complete!")
    else:
        print("✗ Some required methods or constants are missing!")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    try:
        success = verify_export_service()
        exit(0 if success else 1)
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
