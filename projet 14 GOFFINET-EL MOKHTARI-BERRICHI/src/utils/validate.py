import json
from jsonschema import validate, ValidationError
from pathlib import Path
import sys

# Add src directory to Python path
SRC_PATH = Path(__file__).parent.parent
sys.path.append(str(SRC_PATH))

def load_schema(schema_name: str) -> dict:
    """Load a JSON schema from the schemas directory"""
    schema_path = Path(__file__).parent.parent / "schemas" / f"{schema_name}.schema.json"
    with open(schema_path, "r") as f:
        return json.load(f)

from jsonschema import validate, ValidationError
from src.utils.validate import load_schema

def validate_data(data: dict, schema_name: str) -> bool:
    """Validate data against the specified schema"""
    try:
        schema = load_schema(schema_name)
        validate(instance=data, schema=schema)
        return True

    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return False

    except FileNotFoundError as e:
        print(f"Schema not found: {e}")
        return False

    except Exception as e:
        print(f"Unexpected error during validation: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate JSON data against a schema")
    parser.add_argument("schema", help="Name of the schema to validate against")
    parser.add_argument("file", help="Path to JSON file to validate")
    
    args = parser.parse_args()
    
    try:
        with open(args.file, "r") as f:
            data = json.load(f)
            
        if validate_data(data, args.schema):
            print("Validation passed successfully")
            sys.exit(0)
        else:
            print("Validation failed")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)