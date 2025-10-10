from spring_pkg.database import DatabaseEntity, dbfield, dbtable

# Test entity classes
@dbtable(schema="test_schema", table="users")
class User(DatabaseEntity):
    name: str
    email: str
    age: int


@dbtable(schema="test_schema", table="products")
class Product(DatabaseEntity):
    price: float
    category: str
    name = dbfield(alias="product_name") 


@dbtable(schema="test_schema", table="people")
class Person(DatabaseEntity):
    name: str
    age: int    


@dbtable(schema="test_schema", table="employees")  
class Employee(DatabaseEntity):
    employee_id: str
    department: str
    salary: str
    

@dbtable(schema="aliased_schema", table="users")
class UserWithAliases(DatabaseEntity):
    email: str
    # Add field aliases
    name = dbfield(alias="full_name")
    age = dbfield(alias="years_old")
    
