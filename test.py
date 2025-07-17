import unittest

class SweetShop:
    def __init__(self):
        # The project requires each sweet to have:
        # ID, name, category, price, and quantity.
        # A dictionary is a good way to store the sweets, using the ID as the key.
        self.sweets = {}

    def add_sweet(self, sweet_id, name, category, price, quantity):
        """Adds a new sweet to the shop."""
        # To be implemented
        pass

    def delete_sweet(self, sweet_id):
        """Deletes a sweet from the shop."""
        # To be implemented
        pass

    def get_all_sweets(self):
        """Returns a list of all sweets."""
        # To be implemented
        pass

    def search_by_name(self, name):
        """Searches for sweets by name."""
        # To be implemented
        pass

    def search_by_category(self, category):
        """Searches for sweets by category."""
        # To be implemented
        pass

    def search_by_price_range(self, min_price, max_price):
        """Searches for sweets within a price range."""
        # To be implemented
        pass
    
    def sort_by(self, key):
        """Sorts sweets by a given key (name, price, quantity)."""
        # To be implemented
        pass

    def purchase_sweet(self, sweet_id, quantity_to_buy):
        """Handles the purchase of a sweet, decreasing its stock."""
        # To be implemented
        pass

    def restock_sweet(self, sweet_id, quantity_to_add):
        """Restocks a sweet, increasing its stock."""
        # To be implemented
        pass

class TestSweetShop(unittest.TestCase):
    """
    Test suite for the Sweet Shop Management System.
    This follows the requirements specified in the project document.
    """

    def setUp(self):
        """
        Set up a new SweetShop instance before each test.
        This ensures that tests are isolated from each other.
        """
        self.shop = SweetShop()
        # Pre-populate the shop with some sample data for testing
        self.shop.add_sweet(1001, "Kaju Katli", "Nut-Based", 50, 20)
        self.shop.add_sweet(1002, "Gajar Halwa", "Vegetable-Based", 30, 15)
        self.shop.add_sweet(1003, "Gulab Jamun", "Milk-Based", 10, 50)
        self.shop.add_sweet(1004, "Chocolate Bar", "Chocolate", 20, 100)

    # 1. Core Operations Tests
    def test_add_sweet(self):
        """Test that a new sweet can be successfully added."""
        initial_count = len(self.shop.get_all_sweets())
        self.shop.add_sweet(1005, "Jalebi", "Milk-Based", 25, 30)
        new_count = len(self.shop.get_all_sweets())
        self.assertEqual(new_count, initial_count + 1)
        # Verify the added sweet's details
        added_sweet = self.shop.sweets.get(1005)
        self.assertIsNotNone(added_sweet)
        self.assertEqual(added_sweet['name'], "Jalebi")

    def test_add_sweet_with_duplicate_id(self):
        """Test that adding a sweet with a duplicate ID fails."""
        # This should ideally raise a specific error or return False
        with self.assertRaises(ValueError, msg="Should raise ValueError for duplicate ID"):
            self.shop.add_sweet(1001, "Duplicate Sweet", "Test", 1, 1)

    def test_delete_sweet(self):
        """Test that a sweet can be successfully removed."""
        initial_count = len(self.shop.get_all_sweets())
        result = self.shop.delete_sweet(1001)
        new_count = len(self.shop.get_all_sweets())
        self.assertTrue(result, "delete_sweet should return True on success")
        self.assertEqual(new_count, initial_count - 1)
        self.assertIsNone(self.shop.sweets.get(1001))

    def test_delete_non_existent_sweet(self):
        """Test that attempting to delete a sweet that does not exist fails gracefully."""
        result = self.shop.delete_sweet(9999)
        self.assertFalse(result, "delete_sweet should return False for non-existent ID")

    def test_view_all_sweets(self):
        """Test that all available sweets can be viewed."""
        sweets = self.shop.get_all_sweets()
        self.assertEqual(len(sweets), 4)

    # 2. Search & Sort Features Tests
    def test_search_by_name(self):
        """Test searching for sweets by name."""
        results = self.shop.search_by_name("Kaju Katli")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Kaju Katli")

    def test_search_by_category(self):
        """Test searching for sweets by category."""
        results = self.shop.search_by_category("Milk-Based")
        self.assertEqual(len(results), 1) # Should be Gulab Jamun
        self.assertEqual(results[0]['name'], "Gulab Jamun")

    def test_search_by_price_range(self):
        """Test searching for sweets within a given price range."""
        results = self.shop.search_by_price_range(25, 55)
        self.assertEqual(len(results), 2)
        names = {sweet['name'] for sweet in results}
        self.assertIn("Kaju Katli", names)
        self.assertIn("Gajar Halwa", names)

    def test_search_no_results(self):
        """Test that a search with no matches returns an empty list."""
        results = self.shop.search_by_name("Non-existent Sweet")
        self.assertEqual(len(results), 0)

    def test_sort_by_name(self):
        """Test sorting sweets by name in ascending order."""
        sorted_sweets = self.shop.sort_by('name')
        names = [sweet['name'] for sweet in sorted_sweets]
        self.assertEqual(names, ["Chocolate Bar", "Gajar Halwa", "Gulab Jamun", "Kaju Katli"])

    def test_sort_by_price(self):
        """Test sorting sweets by price in ascending order."""
        sorted_sweets = self.shop.sort_by('price')
        prices = [sweet['price'] for sweet in sorted_sweets]
        self.assertEqual(prices, [10, 20, 30, 50])

    def test_sort_by_quantity(self):
        """Test sorting sweets by quantity in ascending order."""
        sorted_sweets = self.shop.sort_by('quantity')
        quantities = [sweet['quantity'] for sweet in sorted_sweets]
        self.assertEqual(quantities, [15, 20, 50, 100])

    # 3. Inventory Management Tests
    def test_purchase_sweet_sufficient_stock(self):
        """Test purchasing a sweet when there is enough stock."""
        initial_quantity = self.shop.sweets[1003]['quantity'] # Gulab Jamun
        purchase_quantity = 10
        self.shop.purchase_sweet(1003, purchase_quantity)
        new_quantity = self.shop.sweets[1003]['quantity']
        self.assertEqual(new_quantity, initial_quantity - purchase_quantity)

    def test_purchase_sweet_insufficient_stock(self):
        """Test that purchasing a sweet raises an error if stock is insufficient."""
        purchase_quantity = 100 # Only 15 in stock for Gajar Halwa
        with self.assertRaises(ValueError, msg="Should raise ValueError for insufficient stock"):
            self.shop.purchase_sweet(1002, purchase_quantity)

    def test_purchase_non_existent_sweet(self):
        """Test that purchasing a non-existent sweet raises an error."""
        with self.assertRaises(KeyError, msg="Should raise KeyError for non-existent sweet ID"):
            self.shop.purchase_sweet(9999, 5)

    def test_restock_sweet(self):
        """Test that restocking a sweet correctly increases its quantity."""
        initial_quantity = self.shop.sweets[1001]['quantity'] # Kaju Katli
        restock_quantity = 50
        self.shop.restock_sweet(1001, restock_quantity)
        new_quantity = self.shop.sweets[1001]['quantity']
        self.assertEqual(new_quantity, initial_quantity + restock_quantity)

    def test_restock_non_existent_sweet(self):
        """Test that restocking a non-existent sweet raises an error."""
        with self.assertRaises(KeyError, msg="Should raise KeyError for non-existent sweet ID"):
            self.shop.restock_sweet(9999, 20)

if __name__ == '__main__':
    """
    This allows the test suite to be run directly from the command line.
    """
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
