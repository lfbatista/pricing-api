import json
from flask import Flask, jsonify, request
from order_total import CACHE, OrderTotal, pricing

app = Flask(__name__)
CACHE.init_app(app)
orders_total = dict()


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
        if cur not in orders_total:
            order_total = OrderTotal(payload, cur).total_order_summary()
            orders_total[cur] = order_total
            return order_total
        return orders_total[cur]
    except Exception as e:
        print('Exception:', str(e))
        return 'Error processing data'


if __name__ == '__main__':
    app.run()
