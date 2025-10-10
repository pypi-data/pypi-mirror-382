import unittest
from spring_pkg.database.memory.db import MemoryDatabase
from spring_pkg.database.base.dbtable import dbtable, dbfield
from .dbclasses import Person, Employee, UserWithAliases


class TestFindIterInstances(unittest.TestCase):
    
    def setUp(self):
        self.db = MemoryDatabase()
        
        # Insert test data for Person
        self.db.insert(Person(name="Alice", age=30))
        self.db.insert(Person(name="Bob", age=25))
        self.db.insert(Person(name="Charlie", age=30))
        self.db.insert(Person(name="Diana", age=35))
        
        # Insert test data for Employee
        self.db.insert(Employee(employee_id="E001", department="Engineering", salary=75000.0))
        self.db.insert(Employee(employee_id="E002", department="Marketing", salary=65000.0))
        self.db.insert(Employee(employee_id="E003", department="Engineering", salary=80000.0))
        
        # Insert test data for UserWithAliases
        self.db.insert(UserWithAliases(name="John", age=28, email="john@example.com"))
        self.db.insert(UserWithAliases(name="Jane", age=32, email="jane@example.com"))
    
    def test_find_iter_returns_iterator(self):
        """Test that find returns an iterator"""
        result = self.db.find(Person, age=30)
        
        iterator = iter(result)

        # Check it's an iterator
        self.assertTrue(hasattr(iterator, '__iter__'))
        self.assertTrue(hasattr(iterator, '__next__'))
    
    def test_find_iter_returns_instances(self):
        """Test that find returns class instances, not dictionaries"""
        people = list(self.db.find(Person, age=30))
        
        # Should find Alice and Charlie (both age 30)
        self.assertEqual(len(people), 2)
        
        # Check that results are Person instances
        for person in people:
            self.assertIsInstance(person, Person)
            self.assertEqual(person.age, 30)
            self.assertIn(person.name, ["Alice", "Charlie"])
    
    def test_find_iter_with_different_criteria(self):
        """Test find with different filtering criteria"""
        # Find employees in Engineering
        engineers = list(self.db.find(Employee, department="Engineering"))
        self.assertEqual(len(engineers), 2)
        
        for engineer in engineers:
            self.assertIsInstance(engineer, Employee)
            self.assertEqual(engineer.department, "Engineering")
            self.assertIn(engineer.employee_id, ["E001", "E003"])
    
    def test_find_iter_with_aliases(self):
        """Test find with field aliases"""
        # Find users by age (stored as 'years_old' in database)
        users = list(self.db.find(UserWithAliases, years_old=28))
        
        self.assertEqual(len(users), 1)
        user = users[0]
        self.assertIsInstance(user, UserWithAliases)
        # Should have the correct field names, not aliases
        self.assertEqual(user.name, "John")
        self.assertEqual(user.age, 28)
        self.assertEqual(user.email, "john@example.com")
    
    def test_find_iter_no_matches(self):
        """Test find when no rows match criteria"""
        result = list(self.db.find(Person, age=999))
        self.assertEqual(len(result), 0)
    
    def test_find_nonexistent_table(self):
        """Test find with nonexistent table"""
        result = list(self.db.find(Person, name="Test"))
        self.assertEqual(len(result), 0)
    
    def test_find_memory_efficiency(self):
        """Test that find is memory efficient (doesn't load all at once)"""
        # Get iterator but don't consume it
        query_result = self.db.find(Person)

        iterator = iter(query_result)
        
        # Iterator should exist but not have consumed memory for all results yet
        self.assertTrue(hasattr(iterator, '__iter__'))
        
        # Consume one item at a time
        first_person = next(iterator)
        self.assertIsInstance(first_person, Person)
        
        # Can still get more items
        second_person = next(iterator)
        self.assertIsInstance(second_person, Person)
    
    def test_find_iter_vs_find_consistency(self):
        """Test that find and find return equivalent results"""
        criteria = {"age": 30}
        
        # Get results from both methods
        find_results = self.db.find(Person, **criteria).all()
        find_iter_results = list(self.db.find(Person, **criteria))
        
        # Should have same number of results
        self.assertEqual(len(find_results), len(find_iter_results))
        
        # Sort by name for comparison
        find_results.sort(key=lambda p: p.name)
        find_iter_results.sort(key=lambda p: p.name)
        
        # Should have equivalent data
        for find_person, iter_person in zip(find_results, find_iter_results):
            self.assertEqual(find_person.name, iter_person.name)
            self.assertEqual(find_person.age, iter_person.age)
            self.assertIsInstance(find_person, Person)
            self.assertIsInstance(iter_person, Person)


if __name__ == '__main__':
    unittest.main()
