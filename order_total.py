import json
from flask_caching import Cache
import requests

CACHE = Cache(config={'CACHE_TYPE': 'simple'})
API_KEY = 'f5ce88e88cfe3383ed89'
API_URL = 'https://free.currconv.com/api/v7/'


class OrderTotal(object):
    def __init__(self, order, cur):
        self.order = order
        self.cur = cur
        self.items = self.order_items()

    def order_items(self):
        """
        :returns list of dictionaries containing product_id, quantity, price, and vat
        """
        items = []
        for product in pricing['prices']:
            for item in self.order['order']['items']:
                if item['product_id'] == product['product_id']:
                    if product['vat_band'] == 'standard':
                        items.append({'product_id': item['product_id'],
                                      'quantity': item['quantity'],
                                      'price': round(product['price'] * exchange_rate(to=self.cur), 2),
                                      'vat': round(pricing['vat_bands']['standard']
                                                   * product['price'] * exchange_rate(to=self.cur), 2)})
                    else:
                        items.append({'product_id': item['product_id'],
                                      'quantity': item['quantity'],
                                      'price': round(product['price'] * exchange_rate(to=self.cur), 2),
                                      'vat': 0})
        # overkill
        # items = [{'product_id': item['product_id'],
        #            'quantity': item['quantity'],
        #            'price': round(product['price'] * exchange_rate(to=cur), 2),
        #            'vat': round(pricing['vat_bands']['standard'] * product['price'] * exchange_rate(to=cur), 2)}
        #           if product['vat_band'] == 'standard' else
        #           {'product_id': item['product_id'],
        #            'quantity': item['quantity'],
        #            'price': round(product['price'] * exchange_rate(to=cur), 2),
        #            'vat': 0}
        #           for item in order['order']['items'] for product in pricing['prices']
        #           if item['product_id'] == product['product_id']]

        return items

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


# def exchange_rate(fr='GBP', to='EUR'):
#     """
#     :argument fr: currency code to exchange from
#     :argument to: currency code to exchange to
#     :returns cached current exchange rate from currencyconverterapi.com
#     """
#
#     curs = f'{fr}_{to}'
#     request = API_URL + 'convert?q=' + curs + '&compact=ultra&apiKey=' + API_KEY
#     response = requests.get(request)
#     content = json.loads(response.content)
#
#     if response.status_code == 200:
#         return content[curs]
#
#     print(content)
#     return 1


def exchange_rate(fr='GBP', to='EUR'):
    """
    :argument fr: currency code to exchange from
    :argument to: currency code to exchange to
    :returns cached current exchange rate from currencyconverterapi.com
    """
    cur = CACHE.get('cur')
    current_rate = CACHE.get('rate')

    if cur != to:
        curs = f'{fr}_{to}'
        request = API_URL + 'convert?q=' + curs + '&compact=ultra&apiKey=' + API_KEY
        response = requests.get(request)
        content = json.loads(response.content)

        if response.status_code == 200:
            CACHE.set('cur', to)
            CACHE.get('cur')
            CACHE.set('rate', content[curs])
            return CACHE.get('rate')
        print(content)
        return 1
    return current_rate


with open('pricing.json') as f:
    pricing = json.load(f)