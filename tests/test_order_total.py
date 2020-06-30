import unittest
import sys
sys.path.append('app')

from app import OrderTotal

MOCK_ORDER = {
    'order': {
        'id': 12345,
        'customer': {},
        'items': [
            {
                'product_id': 1,
                'quantity': 1
            },
            {
                'product_id': 2,
                'quantity': 5
            },
            {
                'product_id': 3,
                'quantity': 1
            }
        ]
    }
}


class TestOrderTotal(unittest.TestCase):
    def setUp(self):
        self.items_vat = OrderTotal(MOCK_ORDER, 'GBP').items_vat

    def test_items_vat(self):
        items = [item for item in self.items_vat()]
        self.assertEqual(items, [119.8, 0, 0])


if __name__ == '__main__':
    unittest.main()
