import json

from flask import Flask, jsonify, request
from flask_caching import Cache
import requests

cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__)
cache.init_app(app)

API_KEY = 'f5ce88e88cfe3383ed89'
API_URL = 'https://free.currconv.com/api/v7/'


@app.route('/')
@app.route('/prices')
def prices():
    return jsonify(pricing)


@app.route('/orders', methods=('POST', 'PUT'))
def orders():
    """
    :parameter cur: currency code
    :returns json object from total_order_summary
    """
    try:
        cur = request.args.get('cur', default='GBP').upper()
        payload = json.loads(request.get_data().decode('utf-8'))
        return jsonify(total_order_summary(payload, cur))
    except Exception as e:
        print('Exception:', str(e))
        return 'Error processing data'


def order_items(order, cur):
    """
    :argument order: order dictionary
    :argument cur: currency code
    :returns list of dictionaries containing product_id, quantity, price, and vat
    """
    items = []
    for product in pricing['prices']:
        for item in order['order']['items']:
            if item['product_id'] == product['product_id']:
                if product['vat_band'] == 'standard':
                    items.append({'product_id': item['product_id'],
                                  'quantity': item['quantity'],
                                  'price': round(product['price'] * exchange_rate(to=cur), 2),
                                  'vat': round(pricing['vat_bands']['standard']
                                               * product['price'] * exchange_rate(to=cur), 2)})
                else:
                    items.append({'product_id': item['product_id'],
                                  'quantity': item['quantity'],
                                  'price': round(product['price'] * exchange_rate(to=cur), 2),
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


def items_price(items):
    """
    :argument items: items dictionary
    :returns list of prices
    """
    return (item['quantity'] * item['price'] for item in items)


def items_vat(items):
    """
    :argument items: items dictionary
    :returns list of vats
    """
    return (item['quantity'] * item['vat'] for item in items)


def total_order_price(order, cur):
    """
    :argument order: order dictionary
    :argument cur: currency code
    :returns rounded sum of items_price and items_vat
    """
    return round(sum(items_price(order_items(order, cur))) + sum(items_vat(order_items(order, cur))), 2)


def total_order_summary(order, cur):
    """
    :argument order: order dictionary
    :argument cur: currency code
    :returns order_total dictionary
    """

    order_total = {
        'order_total': {
            'order_id': order['order']['id'],
            'currency': cur,
            'items': order_items(order, cur),
            'total': total_order_price(order, cur),
            'total_vat': sum(items_vat(order_items(order, cur)))
        }
    }

    return order_total


def exchange_rate(fr='GBP', to='EUR'):
    """
    :argument fr: currency code to exchange from
    :argument to: currency code to exchange to
    :returns cached current exchange rate from currencyconverterapi.com
    """
    cur = cache.get('cur')
    current_rate = cache.get('rate')

    if cur != to:
        curs = f'{fr}_{to}'
        request = API_URL + 'convert?q=' + curs + '&compact=ultra&apiKey=' + API_KEY
        response = requests.get(request)
        content = json.loads(response.content)

        if response.status_code == 200:
            cache.set('cur', to)
            cache.get('cur')
            cache.set('rate', content[curs])
            return cache.get('rate')

        print(content)
        return 1

    return current_rate


with open('pricing.json') as f:
    pricing = json.load(f)

if __name__ == '__main__':
    app.run()
