"""
Example usage of the to_dict method with the @dbtable decorator.
"""

from spring_pkg.database.base.dbtable import dbtable
from spring_pkg.database.base.dbfield import dbfield

@dbtable(schema="test_schema", table="records")
class Record:
    id: int = dbfield(alias="record_id")
    text: str = dbfield(alias="text_content")
    status: str = dbfield(default="active")
    count: int = dbfield(default=0)

# Example usage:
if __name__ == "__main__":
    # Create an instance
    record = Record(id=1, text="Hello World", status="published", count=42)
    
    # Convert specific fields to dictionary using field references
    # This would work if we had proper field descriptors
    result1 = record.to_dict(["id", "text"])
    print("Using field names:", result1)
    # Expected output: {"record_id": 1, "text_content": "Hello World"}
    
    # Convert all fields
    result2 = record.to_dict(["id", "text", "status", "count"])
    print("All fields:", result2)
    # Expected output: {"record_id": 1, "text_content": "Hello World", "status": "published", "count": 42}
    
    # Demonstrating the class structure
    print(f"Schema: {record.__schema__}")
    print(f"Table: {record.__tablename__}")
    print(f"Field aliases: {record.__field_aliases__}")
