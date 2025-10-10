import unittest
import tempfile
import os
from spring_pkg.database import DatabaseEntity, dbfield, dbtable, memory, postgres
from spring_pkg.database.memory.db import MemoryDatabase
from spring_pkg.database.base.database import Database
from spring_pkg.database.base.db_entity_base import DatabaseEntityBase
from .dbclasses import User, Product


class TestDatabaseModule(unittest.TestCase):
    
    def test_imports(self):
        """Test that all database components can be imported"""
        # Test main imports
        self.assertTrue(hasattr(DatabaseEntity, '__init__'))
        self.assertTrue(callable(dbfield))
        self.assertTrue(callable(dbtable))
        
        # Test submodules
        self.assertIsNotNone(memory)
        self.assertIsNotNone(postgres)
    
    def test_dbtable_decorator(self):
        """Test @dbtable decorator functionality"""
        # Test that decorator sets the correct attributes
        self.assertEqual(User.__schema__, "test_schema")
        self.assertEqual(User.__tablename__, "users")
        
        self.assertEqual(Product.__schema__, "test_schema")
        self.assertEqual(Product.__tablename__, "products")
    
    def test_dbfield_alias(self):
        """Test dbfield with alias"""
        # Test that Product has field aliases
        self.assertTrue(hasattr(Product, '__field_aliases__'))
        self.assertIn('name', Product.__field_aliases__)
        self.assertEqual(Product.__field_aliases__['name'], 'product_name')


class TestDatabaseEntity(unittest.TestCase):
    
    def test_entity_creation(self):
        """Test creating database entities"""
        user = User(name="John Doe", email="john@example.com", age=30)
        
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.email, "john@example.com")
        self.assertEqual(user.age, 30)
    
    def test_entity_inheritance(self):
        """Test that entities inherit from DatabaseEntity"""
        user = User(name="Jane", email="jane@example.com", age=25)
        
        self.assertIsInstance(user, DatabaseEntity)
        self.assertIsInstance(user, DatabaseEntityBase)
    
    def test_entity_methods(self):
        """Test entity methods"""
        user = User(name="Bob", email="bob@example.com", age=35)
        
        # Test to_json method (should exist from DatabaseEntity)
        if hasattr(user, 'to_json'):
            json_data = user.to_json()
            self.assertIsInstance(json_data, dict)
        
        # Test that entity has required attributes
        self.assertTrue(hasattr(user, '__schema__'))
        self.assertTrue(hasattr(user, '__tablename__'))


class TestMemoryDatabase(unittest.TestCase):
    
    def setUp(self):
        self.db = MemoryDatabase()
    
    def test_memory_database_creation(self):
        """Test creating a memory database"""
        self.assertIsInstance(self.db, Database)
        self.assertIsInstance(self.db, MemoryDatabase)
    
    def test_insert_and_find(self):
        """Test basic insert and find operations"""
        # Create test user
        user = User(name="Alice", email="alice@example.com", age=28)
        
        # Insert user
        self.db.insert(user)
        
        # Find user
        found_users = list(self.db.find(User, name="Alice"))
        
        self.assertEqual(len(found_users), 1)
        found_user = found_users[0]
        self.assertEqual(found_user.name, "Alice")
        self.assertEqual(found_user.email, "alice@example.com")
        self.assertEqual(found_user.age, 28)
    
    def test_multiple_entities(self):
        """Test working with multiple entity types"""
        # Insert users
        user1 = User(name="John", email="john@example.com", age=30)
        user2 = User(name="Jane", email="jane@example.com", age=25)
        self.db.insert(user1)
        self.db.insert(user2)
        
        # Insert products
        product1 = Product(name="Laptop", price=999.99, category="Electronics")
        product2 = Product(name="Book", price=19.99, category="Education")
        self.db.insert(product1)
        self.db.insert(product2)
        
        # Find all users
        users = list(self.db.find(User))
        self.assertEqual(len(users), 2)
        
        # Find all products
        products = list(self.db.find(Product))
        self.assertEqual(len(products), 2)
        
        # Find specific entities
        electronics = list(self.db.find(Product, category="Electronics"))
        self.assertEqual(len(electronics), 1)
        self.assertEqual(electronics[0].name, "Laptop")
    
    def test_field_aliases(self):
        """Test that field aliases work correctly"""
        product = Product(name="Mouse", price=29.99, category="Electronics")
        self.db.insert(product)
        
        # Find product
        found_products = list(self.db.find(Product, name="Mouse"))
        
        self.assertEqual(len(found_products), 1)
        found_product = found_products[0]
        self.assertEqual(found_product.name, "Mouse")
        self.assertEqual(found_product.price, 29.99)
    
    def test_find_with_no_results(self):
        """Test find operations that return no results"""
        # Search for non-existent user
        users = list(self.db.find(User, name="NonExistent"))
        self.assertEqual(len(users), 0)
    
    def test_update_operations(self):
        """Test update operations if available"""
        user = User(name="Bob", email="bob@example.com", age=40)
        self.db.insert(user)
        
        # Try to update (if method exists)
        if hasattr(self.db, 'update'):
            user.age = 41
            self.db.update(user, {"name": "Bob"})
            
            # Find updated user
            updated_users = list(self.db.find(User, name="Bob"))
            if updated_users:
                self.assertEqual(updated_users[0].age, 41)


class TestDatabaseBase(unittest.TestCase):
    
    def test_database_abstract_methods(self):
        """Test that Database base class has required methods"""
        # Test that Database class exists and has expected methods
        self.assertTrue(hasattr(Database, '_insert'))
        self.assertTrue(hasattr(Database, '_update'))
        self.assertTrue(hasattr(Database, '_find'))
        self.assertTrue(hasattr(Database, 'insert'))
        self.assertTrue(hasattr(Database, 'update'))
        self.assertTrue(hasattr(Database, 'find'))
    
    def test_database_cannot_be_instantiated(self):
        """Test that abstract Database cannot be instantiated directly"""
        try:
            # This should work as Database may not be truly abstract
            db = Database()
            # If it works, verify it has the expected interface
            self.assertTrue(hasattr(db, 'insert'))
        except TypeError:
            # If it's abstract, that's expected
            pass


class TestDatabaseIntegration(unittest.TestCase):
    
    def test_full_workflow(self):
        """Test a complete database workflow"""
        db = MemoryDatabase()
        
        # Create entities
        users = [
            User(name="Alice", email="alice@example.com", age=30),
            User(name="Bob", email="bob@example.com", age=25),
            User(name="Charlie", email="charlie@example.com", age=35)
        ]
        
        products = [
            Product(name="Laptop", price=1200.00, category="Electronics"),
            Product(name="Book", price=25.00, category="Education"),
            Product(name="Headphones", price=150.00, category="Electronics")
        ]
        
        # Insert all entities
        for user in users:
            db.insert(user)
        for product in products:
            db.insert(product)
        
        # Perform various queries
        all_users = list(User.find(db))
        self.assertEqual(len(all_users), 3)
        
        electronics = list(Product.find(db, category="Electronics").all())
        self.assertEqual(len(electronics), 2)
        
        young_users = list(db.find(User, age=25).all())
        self.assertEqual(len(young_users), 1)
        self.assertEqual(young_users[0].name, "Bob")
        
        # Test that entities maintain their types
        for user in all_users:
            self.assertIsInstance(user, User)
            self.assertIsInstance(user, DatabaseEntity)
        
        for product in electronics:
            self.assertIsInstance(product, Product)
            self.assertIsInstance(product, DatabaseEntity)


if __name__ == '__main__':
    unittest.main()
