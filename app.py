import uuid

import yaml
from flask import Flask, flash, request, render_template, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'life is pointless'

# setting up PRODUCTS list of dictionaries corresponding to each product
with open('products.yml') as _f:
    PRODUCTS = yaml.load(_f)

# setting up DENOMINATIONS list of dictionaries corresponding to each denomination
with open('denominations.yml') as _f:
    DENOMINATIONS = yaml.load(_f)


ORDER_DB = 'orders.yml'


def record_order(product_id, amount_paid, item_price):

    # generates order's id
    order_id = str(uuid.uuid4()).split('-', 1)[0]
    orders = {
        order_id: {
            'product_id': product_id,
            'time': str(datetime.now()).split(".")[0],
            'amount_paid': amount_paid,
            'item_price': item_price
        }
    }
    with open(ORDER_DB, 'a') as f:
        f.write(yaml.dump(orders, default_flow_style=False))
    return order_id

# the route() decorator is used to bind a function to a URL
@app.route('/', methods=['POST', 'GET'])
def index():
    context = {}
    if request.method == 'POST':
        # TODO
        if request.form['product']:
        
            product_id = int(request.form['product'])
            amount_paid = int(request.form['paid'])
            item_price = PRODUCTS[product_id]['price']

            context['product_id'] = product_id

            if amount_paid > item_price:
                order_id = record_order(product_id, amount_paid, item_price)
                flash('Order Placed Successfully', 'success')
                # return render_template('confirmation.jinja', order_id=order_id, amount_paid=amount_paid, item_price=item_price, title='Order Confirmation')
                return redirect('/confirmation/' + str(order_id))
            else:
                flash('Amount Paid is Insufficient', 'danger')

        else:
            flash('Please Choose a Product', 'danger')

    return render_template('index.jinja', products=PRODUCTS, title='Order Form', **context)

# adds a variable part to the URL
@app.route('/confirmation/<order_id>')
def confirmation(order_id):
    with open(ORDER_DB) as f:
        orders = yaml.load(f) or {}

    order = orders.get(order_id)
    if order is None:
        # TODO what do we do here?
        flash('The order with order id = {} doesn\'t exist'.format(order_id), 'danger')
    # TODO other stuff has to be calculated here.
    else:
        amount_paid = orders[order_id]['amount_paid']
        item_price = orders[order_id]['item_price']
        date = orders[order_id]['time']
        change_due = (amount_paid - item_price) * 100

        change_denoms = u""

        for denom in DENOMINATIONS:
            num_of_denom = int(change_due / denom['value'])
            if num_of_denom > 0:
                change_denoms += u"{} of {}, ".format(num_of_denom, denom['name'])
                change_due -= num_of_denom * denom['value'] 

        return render_template('confirmation.jinja', order_id=order_id, date=date, amount_paid=amount_paid, item_price=item_price, 
            change_denoms=change_denoms[:-2], change_due=amount_paid-item_price ,title='Order Confirmation')
    return render_template('confirmation.jinja', title='Order Confirmation')


@app.route('/orders/')
def orders():
    with open(ORDER_DB) as f:
        orders = yaml.load(f) or {}
    
    # creates a set of dates
    date_list = []
    for order in orders.values():
        if order['time'].split()[0] not in date_list:
            date_list.append(order['time'].split()[0])

    date_list.sort()


    orders_by_date = {}

    for date in date_list:
        orders_by_date[date] = []
        for order in orders:
            if orders[order]['time'].split()[0] == date:
                orders_by_date[date].append(
                    {
                        'order_id': order,
                        'product_id': orders[order]['product_id']
                    }
                )

    return render_template('orders_by_date.jinja', title='Orders', date_list=date_list, orders_by_date=orders_by_date)



if __name__ == '__main__':
    # enable debug support so that the server will reload itself on code changes
    app.run(debug=True, use_reloader=True)
