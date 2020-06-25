import json
import unittest

from app import app, items_vat

MOCK_ITEMS = [{'price': 599, 'product_id': 1, 'quantity': 1, 'vat': 119.8},
              {'price': 250, 'product_id': 2, 'quantity': 5, 'vat': 0},
              {'price': 250, 'product_id': 3, 'quantity': 1, 'vat': 0}]

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

MOCK_RESULT = {
    'order_total': {
        'currency': 'GBP',
        'items': [
            {
                'price': 599,
                'product_id': 1,
                'quantity': 1,
                'vat': 119.8
            },
            {
                'price': 250,
                'product_id': 2,
                'quantity': 5,
                'vat': 0
            },
            {
                'price': 250,
                'product_id': 3,
                'quantity': 1,
                'vat': 0
            }
        ],
        'order_id': 12345,
        'total': 2218.8,
        'total_vat': 119.8
    }
}


class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.items_vat = items_vat
        self.items_vat = items_vat

    def test_pricing(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_orders(self):
        result = self.app.post('/orders', data=json.dumps(MOCK_ORDER))
        self.assertEqual(json.loads(result.data), MOCK_RESULT)

    def test_items_vat(self):
        items = [item for item in self.items_vat(MOCK_ITEMS)]
        self.assertEqual(items, [119.8, 0, 0])


if __name__ == '__main__':
    unittest.main()
