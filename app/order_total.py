import json

from flask_caching import Cache
import requests

CACHE = Cache(config={'CACHE_TYPE': 'simple'})
API_KEY = 'f5ce88e88cfe3383ed89'
API_URL = 'https://free.currconv.com/api/v7/'


class OrderTotal:
    def __init__(self, order, cur):
        self.order = order
        self.cur = cur
        self.items = self.order_items()

    def order_items(self):
        """
        computes the item price and vat for a given pricing, order, and exchange rate.
        :returns list of items dictionaries
        """
        items = []
        products = {product['product_id']: product for product in pricing['prices']}

        for item in self.order['order']['items']:
            product = products.get(item['product_id'])

            vat = 0
            if product['vat_band'] == 'standard':
                vat = pricing['vat_bands']['standard'] * product['price']
            items.append(
                {
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'price': self.convert_price(product['price']),
                    'vat': self.convert_price(vat),
                }
            )

        return items

    def convert_price(self, price):
        """
        converts price value to is given currency passed in exchange_rate
        :param price: value to convert
        :returns converted price, rounded
        """
        return round(price * exchange_rate(to=self.cur), 2)

    def items_price(self):
        """
        :returns list of prices
        """
        return (item['quantity'] * item['price'] for item in self.items)

    def items_vat(self):
        """
        :returns list of vats
        """
        return (item['quantity'] * item['vat'] for item in self.items)

    def total_order_price(self):
        """
        :returns rounded sum of items_price and items_vat
        """
        return round(sum(self.items_price()) + sum(self.items_vat()), 2)

    def total_order_summary(self):
        """
        :returns order_total dictionary
        """

        order_total = {
            'order_total': {
                'order_id': self.order['order']['id'],
                'currency': self.cur,
                'items': self.items,
                'total': self.total_order_price(),
                'total_vat': sum(self.items_vat())
            }
        }

        return order_total


def cache(func):
    """Cache function value if passed arguments changed"""
    def wrapper_func(*args, **kwargs):
        current_args = CACHE.get('args')
        current_kwargs = CACHE.get('kwargs')
        current_func = CACHE.get('func')

        if current_args != args or current_kwargs != kwargs:
            CACHE.set('args', args)
            CACHE.get('args')

            CACHE.set('kwargs', kwargs)
            CACHE.get('kwargs')

            CACHE.set('func', func(*args, **kwargs))
            return CACHE.get('func')
        return current_func

    return wrapper_func


@cache
def exchange_rate(fr='GBP', to='EUR'):
    """
    :argument fr: currency code to exchange from
    :argument to: currency code to exchange to
    :returns current exchange rate from currencyconverterapi.com
    """

    curs = f'{fr}_{to}'
    request = f'{API_URL}convert?q={curs}&compact=ultra&apiKey={API_KEY}'
    response = requests.get(request)
    content = json.loads(response.content)

    if response.status_code == 200:
        return content[curs]

    print(content)
    return 1


with open('pricing.json') as f:
    pricing = json.load(f)
