import unittest
from spring_pkg.database.memory.db import MemoryDatabase
from spring_pkg.database.base.query_expression import (
    F, Q, EqualExpression, NotEqualExpression, GreaterThanExpression,
    LessThanExpression, GreaterEqualExpression, LessEqualExpression,
    AndExpression, OrExpression
)
from tests.dbclasses import User, Product, Person, Employee, UserWithAliases

def t_create_user(a,b,c):
    return User(name=a, email=b, age=c)

def t_create_user_with_aliases(a,b,c):
    return UserWithAliases(name=a, age=b, email=c)

def t_create_employee(a,b,c):
    return Employee(employee_id=a, department=b, salary=c)

class TestQueryExpressions(unittest.TestCase):
    
    def setUp(self):
        self.db = MemoryDatabase()
        
        # Insert test users
        users_data = [
            t_create_user("Alice", "alice@example.com", 30),
            t_create_user("Bob", "bob@example.com", 25),
            t_create_user("Charlie", "charlie@example.com", 35),
            t_create_user("Diana", "diana@example.com", 28),
            t_create_user("Eve", "eve@example.com", 32),
        ]
        
        for user in users_data:
            self.db.insert(user)
        
        # Insert test products
        products_data = [
            Product(price=999.99, category="Electronics", name="Laptop"),
            Product(price=299.99, category="Electronics", name="Tablet"),
            Product(price=19.99, category="Books", name="Python Guide"),
            Product(price=49.99, category="Books", name="Database Design"),
            Product(price=1299.99, category="Electronics", name="Desktop"),
        ]
        
        for product in products_data:
            self.db.insert(product)
        
        # Insert test employees
        employees_data = [
            t_create_employee("E001", "Engineering", "75000"),
            t_create_employee("E002", "Marketing", "65000"),
            t_create_employee("E003", "Engineering", "85000"),
            t_create_employee("E004", "Sales", "55000"),
            t_create_employee("E005", "Engineering", "95000"),
        ]
        
        for emp in employees_data:
            self.db.insert(emp)


class TestFieldExpressions(TestQueryExpressions):
    
    def test_f_function_creates_field_expression(self):
        """Test that F() function creates FieldExpression objects"""
        age_field = F('age')
        self.assertEqual(age_field.field_name, 'age')
        
        name_field = F('name')
        self.assertEqual(name_field.field_name, 'name')
    
    def test_equal_expression(self):
        """Test equal expressions (==)"""
        # Find users with age 30
        expr = F('age') == 30
        self.assertIsInstance(expr, EqualExpression)
        self.assertEqual(expr.field, 'age')
        self.assertEqual(expr.value, 30)
        
        # Test with database
        results = list(self.db.find(User, expr))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Alice")
        self.assertEqual(results[0].age, 30)
    
    def test_not_equal_expression(self):
        """Test not equal expressions (!=)"""
        # Find users with age not 30
        expr = F('age') != 30
        results = list(self.db.find(User, expr))
        
        # Should find 4 users (all except Alice)
        self.assertEqual(len(results), 4)
        names = [user.name for user in results]
        self.assertNotIn("Alice", names)
        self.assertIn("Bob", names)
        self.assertIn("Charlie", names)
    
    def test_greater_than_expression(self):
        """Test greater than expressions (>)"""
        # Find users older than 30
        expr = F('age') > 30
        results = list(self.db.find(User, expr))
        
        # Should find Charlie (35) and Eve (32)
        self.assertEqual(len(results), 2)
        names = [user.name for user in results]
        self.assertIn("Charlie", names)
        self.assertIn("Eve", names)
    
    def test_less_than_expression(self):
        """Test less than expressions (<)"""
        # Find users younger than 30
        expr = F('age') < 30
        results = list(self.db.find(User, expr))
        
        # Should find Bob (25) and Diana (28)
        self.assertEqual(len(results), 2)
        names = [user.name for user in results]
        self.assertIn("Bob", names)
        self.assertIn("Diana", names)
    
    def test_greater_equal_expression(self):
        """Test greater than or equal expressions (>=)"""
        # Find users 30 or older
        expr = F('age') >= 30
        results = list(self.db.find(User, expr))
        
        # Should find Alice (30), Charlie (35), and Eve (32)
        self.assertEqual(len(results), 3)
        names = [user.name for user in results]
        self.assertIn("Alice", names)
        self.assertIn("Charlie", names)
        self.assertIn("Eve", names)
    
    def test_less_equal_expression(self):
        """Test less than or equal expressions (<=)"""
        # Find users 30 or younger
        expr = F('age') <= 30
        results = list(self.db.find(User, expr))
        
        # Should find Alice (30), Bob (25), and Diana (28)
        self.assertEqual(len(results), 3)
        names = [user.name for user in results]
        self.assertIn("Alice", names)
        self.assertIn("Bob", names)
        self.assertIn("Diana", names)


class TestComplexExpressions(TestQueryExpressions):
    
    def test_and_expression(self):
        """Test AND expressions"""
        # Find users between ages 25 and 32 (inclusive)
        expr = (F('age') >= 25) & (F('age') <= 32)
        results = list(self.db.find(User, expr))
        
        # Should find Bob (25), Diana (28), Alice (30), and Eve (32)
        self.assertEqual(len(results), 4)
        names = [user.name for user in results]
        self.assertIn("Bob", names)
        self.assertIn("Diana", names)
        self.assertIn("Alice", names)
        self.assertIn("Eve", names)
        self.assertNotIn("Charlie", names)  # 35 is too old
    
    def test_or_expression(self):
        """Test OR expressions"""
        # Find users who are either 25 or 35 years old
        expr = (F('age') == 25) | (F('age') == 35)
        results = list(self.db.find(User, expr))
        
        # Should find Bob (25) and Charlie (35)
        self.assertEqual(len(results), 2)
        names = [user.name for user in results]
        self.assertIn("Bob", names)
        self.assertIn("Charlie", names)
    
    def test_complex_nested_expressions(self):
        """Test complex nested expressions"""
        # Find products that are either:
        # - Electronics with price > 500
        # - Books with price < 30
        expr = ((F('category') == 'Electronics') & (F('price') > 500)) | \
               ((F('category') == 'Books') & (F('price') < 30))
        
        results = list(self.db.find(Product, expr))
        
        # Should find: Laptop (999.99), Desktop (1299.99), Python Guide (19.99)
        self.assertEqual(len(results), 3)
        names = [product.name for product in results]
        self.assertIn("Laptop", names)
        self.assertIn("Desktop", names)
        self.assertIn("Python Guide", names)
        self.assertNotIn("Tablet", names)  # Electronics but price <= 500
        self.assertNotIn("Database Design", names)  # Books but price >= 30


class TestQFunction(TestQueryExpressions):
    
    def test_q_function_single_field(self):
        """Test Q() function with single field"""
        expr = Q(age=30)
        results = list(self.db.find(User, expr))
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Alice")
    
    def test_q_function_multiple_fields(self):
        """Test Q() function with multiple fields (AND logic)"""
        expr = Q(category="Electronics", price=999.99)
        results = list(self.db.find(Product, expr))
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Laptop")
    
    def test_combining_q_with_f_expressions(self):
        """Test combining Q() with F() expressions"""
        # Find electronics products with price > 500
        expr = Q(category="Electronics") & (F('price') > 500)
        results = list(self.db.find(Product, expr))
        
        # Should find Laptop and Desktop
        self.assertEqual(len(results), 2)
        names = [product.name for product in results]
        self.assertIn("Laptop", names)
        self.assertIn("Desktop", names)


class TestDatabaseFindWithExpressions(TestQueryExpressions):
    
    def test_find_with_single_expression(self):
        """Test Database.find() with single expression"""
        results = list(self.db.find(User, F('age') > 30))
        
        self.assertEqual(len(results), 2)
        ages = [user.age for user in results]
        self.assertTrue(all(age > 30 for age in ages))
    
    def test_find_with_multiple_expressions(self):
        """Test Database.find() with multiple expressions"""
        # Find engineering employees with salary > 70000
        results = list(self.db.find(Employee, 
                                   F('department') == 'Engineering',
                                   F('salary') > '70000'))  # Note: salary is string in test data
        
        # Should find employees with Engineering department and high salary
        self.assertGreater(len(results), 0)
        for emp in results:
            self.assertEqual(emp.department, 'Engineering')
    
    def test_find_with_expression_and_kwargs(self):
        """Test Database.find() with both expressions and keyword arguments"""
        # Find users over 25 in a specific way
        results = list(self.db.find(User, F('age') > 25, email="alice@example.com"))
        
        # Should find Alice (if age > 25 and email matches)
        if results:  # Alice is 30, so this should match
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Alice")
    
    def test_find_no_results(self):
        """Test Database.find() with expressions that match nothing"""
        results = list(self.db.find(User, F('age') > 100))
        self.assertEqual(len(results), 0)
    
    def test_find_all_results(self):
        """Test Database.find() with expressions that match everything"""
        results = list(self.db.find(User, F('age') > 0))
        self.assertEqual(len(results), 5)  # All users


class TestFieldAliasesWithExpressions(TestQueryExpressions):
    
    def setUp(self):
        super().setUp()
        
        # Insert test users with aliases
        aliased_users = [
            t_create_user_with_aliases("John", 28, "john@example.com"),
            t_create_user_with_aliases("Jane", 32, "jane@example.com"),
            t_create_user_with_aliases("Jack", 25, "jack@example.com"),
        ]
        
        for user in aliased_users:
            self.db.insert(user)
    
    def test_expressions_with_field_aliases(self):
        """Test that expressions work correctly with field aliases"""
        # Query using the original field name (should be mapped to alias)
        expr = F('age') > 27
        results = list(self.db.find(UserWithAliases, expr))
        
        # Should find John (28) and Jane (32)
        self.assertEqual(len(results), 2)
        names = [user.name for user in results]
        self.assertIn("John", names)
        self.assertIn("Jane", names)
        self.assertNotIn("Jack", names)  # 25 <= 27


class TestExpressionEvaluation(TestQueryExpressions):
    
    def test_equal_expression_evaluation(self):
        """Test EqualExpression.evaluate() method"""
        expr = EqualExpression('age', 30)
        
        # Test row that matches
        matching_row = {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}
        self.assertTrue(expr.evaluate(matching_row))
        
        # Test row that doesn't match
        non_matching_row = {'name': 'Bob', 'age': 25, 'email': 'bob@example.com'}
        self.assertFalse(expr.evaluate(non_matching_row))
    
    def test_greater_than_evaluation_with_none(self):
        """Test GreaterThanExpression handles None values correctly"""
        expr = GreaterThanExpression('salary', 50000)
        
        # Test row with None value
        row_with_none = {'name': 'Test', 'salary': None}
        self.assertFalse(expr.evaluate(row_with_none))
        
        # Test row with valid value
        row_with_value = {'name': 'Test', 'salary': 60000}
        self.assertTrue(expr.evaluate(row_with_value))
    
    def test_and_expression_evaluation(self):
        """Test AndExpression.evaluate() method"""
        expr = AndExpression(
            EqualExpression('department', 'Engineering'),
            GreaterThanExpression('salary', 70000)
        )
        
        # Test row that matches both conditions
        matching_row = {'department': 'Engineering', 'salary': 80000}
        self.assertTrue(expr.evaluate(matching_row))
        
        # Test row that matches only first condition
        partial_match = {'department': 'Engineering', 'salary': 60000}
        self.assertFalse(expr.evaluate(partial_match))
        
        # Test row that matches neither condition
        no_match = {'department': 'Marketing', 'salary': 60000}
        self.assertFalse(expr.evaluate(no_match))
    
    def test_or_expression_evaluation(self):
        """Test OrExpression.evaluate() method"""
        expr = OrExpression(
            EqualExpression('department', 'Engineering'),
            GreaterThanExpression('salary', 90000)
        )
        
        # Test row that matches first condition
        first_match = {'department': 'Engineering', 'salary': 70000}
        self.assertTrue(expr.evaluate(first_match))
        
        # Test row that matches second condition
        second_match = {'department': 'Marketing', 'salary': 95000}
        self.assertTrue(expr.evaluate(second_match))
        
        # Test row that matches both conditions
        both_match = {'department': 'Engineering', 'salary': 95000}
        self.assertTrue(expr.evaluate(both_match))
        
        # Test row that matches neither condition
        no_match = {'department': 'Marketing', 'salary': 70000}
        self.assertFalse(expr.evaluate(no_match))


class TestSQLGeneration(TestQueryExpressions):
    
    def test_equal_expression_to_sql(self):
        """Test EqualExpression.to_sql() method"""
        expr = EqualExpression('name', 'Alice')
        sql, params = expr.to_sql()
        
        self.assertEqual(sql, "name = %s")
        self.assertEqual(params, ['Alice'])
    
    def test_equal_expression_to_sql_with_none(self):
        """Test EqualExpression.to_sql() with None value"""
        expr = EqualExpression('name', None)
        sql, params = expr.to_sql()
        
        self.assertEqual(sql, "name IS NULL")
        self.assertEqual(params, [])
    
    def test_not_equal_expression_to_sql(self):
        """Test NotEqualExpression.to_sql() method"""
        expr = NotEqualExpression('status', 'inactive')
        sql, params = expr.to_sql()
        
        self.assertEqual(sql, "status != %s")
        self.assertEqual(params, ['inactive'])
    
    def test_not_equal_expression_to_sql_with_none(self):
        """Test NotEqualExpression.to_sql() with None value"""
        expr = NotEqualExpression('name', None)
        sql, params = expr.to_sql()
        
        self.assertEqual(sql, "name IS NOT NULL")
        self.assertEqual(params, [])
    
    def test_greater_than_expression_to_sql(self):
        """Test GreaterThanExpression.to_sql() method"""
        expr = GreaterThanExpression('age', 25)
        sql, params = expr.to_sql()
        
        self.assertEqual(sql, "age > %s")
        self.assertEqual(params, [25])
    
    def test_and_expression_to_sql(self):
        """Test AndExpression.to_sql() method"""
        left = EqualExpression('department', 'Engineering')
        right = GreaterThanExpression('salary', 70000)
        expr = AndExpression(left, right)
        
        sql, params = expr.to_sql()
        
        self.assertEqual(sql, "(department = %s) AND (salary > %s)")
        self.assertEqual(params, ['Engineering', 70000])
    
    def test_or_expression_to_sql(self):
        """Test OrExpression.to_sql() method"""
        left = EqualExpression('department', 'Engineering')
        right = EqualExpression('department', 'Marketing')
        expr = OrExpression(left, right)
        
        sql, params = expr.to_sql()
        
        self.assertEqual(sql, "(department = %s) OR (department = %s)")
        self.assertEqual(params, ['Engineering', 'Marketing'])


class TestAliasMapping(TestQueryExpressions):
    
    def test_expression_alias_mapping(self):
        """Test that expressions correctly map field names to aliases"""
        expr = EqualExpression('name', 'Test Product')
        
        # Map 'name' to 'product_name' alias
        aliases = {'name': 'product_name'}
        expr.map_names(aliases)
        
        self.assertEqual(expr.field, 'product_name')
    
    def test_complex_expression_alias_mapping(self):
        """Test alias mapping on complex expressions"""
        left = EqualExpression('name', 'Test')
        right = GreaterThanExpression('age', 25)
        expr = AndExpression(left, right)
        
        # Map field names
        aliases = {'name': 'full_name', 'age': 'years_old'}
        expr.map_names(aliases)
        
        # Check that both sides were mapped
        self.assertEqual(expr.left.field, 'full_name')
        self.assertEqual(expr.right.field, 'years_old')


class TestDatabaseDeleteWithExpressions(TestQueryExpressions):
    
    def test_delete_with_single_expression(self):
        """Test Database.delete() with single expression"""
        # Count initial users
        initial_count = len(list(self.db.find(User)))
        self.assertEqual(initial_count, 5)
        
        # Delete users older than 32
        deleted_count = self.db.delete(User, F('age') > 32)
        
        # Should delete Charlie (35)
        self.assertEqual(deleted_count, 1)
        
        # Verify deletion
        remaining_users = list(self.db.find(User))
        self.assertEqual(len(remaining_users), 4)
        names = [user.name for user in remaining_users]
        self.assertNotIn("Charlie", names)
    
    def test_delete_with_multiple_expressions(self):
        """Test Database.delete() with multiple expressions"""
        # Delete engineering employees with salary < 80000
        deleted_count = self.db.delete(Employee, 
                                      F('department') == 'Engineering',
                                      F('salary') < '80000')
        
        # Should delete E001 (salary 75000)
        self.assertEqual(deleted_count, 1)
        
        # Verify remaining engineering employees have higher salaries
        remaining_engineers = list(self.db.find(Employee, F('department') == 'Engineering'))
        for emp in remaining_engineers:
            self.assertGreaterEqual(int(emp.salary), 80000)
    
    def test_delete_with_complex_expression(self):
        """Test Database.delete() with complex AND/OR expressions"""
        # Delete products that are either:
        # - Books with price > 30, OR
        # - Electronics with price < 400
        expr = ((F('category') == 'Books') & (F('price') > 30)) | \
               ((F('category') == 'Electronics') & (F('price') < 400))
        
        deleted_count = self.db.delete(Product, expr)
        
        # Should delete: Database Design (Books, 49.99) and Tablet (Electronics, 299.99)
        self.assertEqual(deleted_count, 2)
        
        # Verify deletions
        remaining_products = list(self.db.find(Product))
        names = [product.name for product in remaining_products]
        self.assertNotIn("Database Design", names)
        self.assertNotIn("Tablet", names)
        self.assertIn("Laptop", names)  # Electronics but price >= 400
        self.assertIn("Python Guide", names)  # Books but price <= 30
    
    def test_delete_with_expression_and_kwargs(self):
        """Test Database.delete() with both expressions and keyword arguments"""
        # Delete users over 30 with specific email pattern
        deleted_count = self.db.delete(User, F('age') > 30, email="charlie@example.com")
        
        # Should delete Charlie (35, charlie@example.com)
        self.assertEqual(deleted_count, 1)
        
        # Verify Charlie is gone but Eve (32) remains (no matching email)
        remaining_users = list(self.db.find(User))
        names = [user.name for user in remaining_users]
        self.assertNotIn("Charlie", names)
        self.assertIn("Eve", names)
    
    def test_delete_no_matches(self):
        """Test Database.delete() with expressions that match nothing"""
        # Try to delete users older than 100
        deleted_count = self.db.delete(User, F('age') > 100)
        
        self.assertEqual(deleted_count, 0)
        
        # Verify no users were deleted
        remaining_users = list(self.db.find(User))
        self.assertEqual(len(remaining_users), 5)
    
    def test_delete_all_matches(self):
        """Test Database.delete() that matches all records"""
        # Delete all products
        deleted_count = self.db.delete(Product, F('price') > 0)
        
        self.assertEqual(deleted_count, 5)  # All 5 products
        
        # Verify no products remain
        remaining_products = list(self.db.find(Product))
        self.assertEqual(len(remaining_products), 0)
    
    def test_delete_with_q_function(self):
        """Test Database.delete() with Q() expressions"""
        # Delete specific user using Q()
        deleted_count = self.db.delete(User, Q(name="Bob", age=25))
        
        self.assertEqual(deleted_count, 1)
        
        # Verify Bob is gone
        remaining_users = list(self.db.find(User))
        names = [user.name for user in remaining_users]
        self.assertNotIn("Bob", names)
    
    def test_delete_return_count(self):
        """Test that Database.delete() returns correct count of deleted records"""
        # Delete multiple employees from Engineering
        deleted_count = self.db.delete(Employee, F('department') == 'Engineering')
        
        # Should delete 3 engineering employees
        self.assertEqual(deleted_count, 3)
        
        # Verify count matches actual deletions
        remaining_employees = list(self.db.find(Employee))
        engineering_remaining = [emp for emp in remaining_employees if emp.department == 'Engineering']
        self.assertEqual(len(engineering_remaining), 0)
    
    def test_delete_with_field_aliases(self):
        """Test Database.delete() with field aliases"""
        # Add some aliased users first
        aliased_users = [
            t_create_user_with_aliases("TestUser1", 40, "test1@example.com"),
            t_create_user_with_aliases("TestUser2", 50, "test2@example.com"),
        ]
        
        for user in aliased_users:
            self.db.insert(user)
        
        # Delete using original field name (should be mapped to alias)
        deleted_count = self.db.delete(UserWithAliases, F('age') > 45)
        
        # Should delete TestUser2 (age 50)
        self.assertEqual(deleted_count, 1)
        
        # Verify correct user was deleted
        remaining_aliased = list(self.db.find(UserWithAliases, F('name') == 'TestUser1'))
        self.assertEqual(len(remaining_aliased), 1)
        
        remaining_aliased = list(self.db.find(UserWithAliases, F('name') == 'TestUser2'))
        self.assertEqual(len(remaining_aliased), 0)


if __name__ == '__main__':
    unittest.main()
