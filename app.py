from importlib.metadata import EntryPoint
from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from models import db, Company, Item, Purchase, Sale
from forms import ItemForm, PurchaseForm, SaleForm
from sqlalchemy.exc import IntegrityError
from flask import jsonify
# from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Initialize data when the app starts
with app.app_context():
    db.create_all()
    if not Company.query.first():
        # Create initial company record
        db.session.add(Company(name="Namma Kadai", cash_balance=1000))
        db.session.commit()

@app.route('/')
def home():
    company = Company.query.first()
    items = Item.query.all()
    balance = company.cash_balance if company else 0
    return render_template('home.html', balance=balance, items=items)

# *********************************************************************************************************

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    form = ItemForm()
    items = Item.query.all()  # Display all items
    balance = Company.query.first().cash_balance if Company.query.first() else 0

    if form.validate_on_submit():
        if not Item.query.filter_by(name=form.name.data).first():  # Add only if item doesn't exist
            db.session.add(Item(name=form.name.data, price=form.price.data, qty=form.qty.data))
            db.session.commit()
            flash('Item added successfully!', 'success')
        else:
            flash('Item already exists.', 'danger')
        return redirect(url_for('add_item'))

    return render_template('add_item.html', form=form, items=items, balance=balance)

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item deleted successfully'})
    return jsonify({'success': False, 'message': 'Item not found'})

@app.route('/edit_item/<int:item_id>', methods=['POST'])
def edit_item(item_id):
    item = Item.query.get(item_id)
    if item:
        data = request.json
        new_name = data.get('name', item.name)

        if not Item.query.filter(Item.name == new_name, Item.id != item.id).first():  # Avoid duplicate names
            item.name = new_name
            item.price = data.get('price', item.price)
            item.qty = data.get('qty', item.qty)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Item updated successfully'})
        return jsonify({'success': False, 'message': 'Item with this name already exists.'})
    return jsonify({'success': False, 'message': 'Item not found'})

# *********************************************************************************************************
@app.route('/purchase/add', methods=['GET', 'POST'])
def add_purchase():
    form = PurchaseForm()
    
    # Fetch available items from the database for dropdown
    items = Item.query.all()
    form.item_id.choices = [(item.id, item.name) for item in items]
    company = Company.query.first()
    balance = company.cash_balance if company else 0

    if form.validate_on_submit():
        item_ids = request.form.getlist('item_id')  # Use getlist without brackets
        quantities = request.form.getlist('qty')
        rates = request.form.getlist('rate')

        items_to_purchase = []
        total_amount = 0
        company = Company.query.first()

        for i in range(len(item_ids)):
            item = Item.query.get(item_ids[i])
            qty = int(quantities[i])  # Convert to integer
            rate = float(rates[i])     # Convert to float
            amount = qty * rate

            if company.cash_balance < amount:
                flash('Insufficient balance for purchase!', 'danger')
                return redirect(url_for('add_purchase'))

            purchase = Purchase(item_id=item_ids[i], qty=qty, rate=rate, amount=amount)
            items_to_purchase.append(purchase)
            item.qty += qty
            total_amount += amount

        company.cash_balance -= total_amount
        db.session.add_all(items_to_purchase)
        db.session.commit()

        flash('Purchase added successfully!', 'success')
        return render_template('add_purchase.html', form=form, items=items, balance=balance)

    return render_template('add_purchase.html', form=form, items=items, balance=balance)
# *********************************************************************************************************
@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    items = {item.id: (item.name, item.qty) for item in Item.query.all()}
    company = Company.query.first()
    balance = company.cash_balance if company else 0

    if request.method == 'POST':
        sales = request.form.to_dict(flat=False)
        total_sale_amount = 0
        sales_to_add = []

        try:
            # Calculate the number of sales entries based on `item_id` keys
            sale_count = sum(1 for key in sales if 'item_id' in key)

            for i in range(sale_count):
                item_ids = map(int, sales[f'sales[{i}][item_id]'])
                qty = int(sales[f'sales[{i}][qty]'][0])
                rate = float(sales[f'sales[{i}][rate]'][0])

                for item_id in item_ids:
                    item = Item.query.get(item_id)
                    if item and item.qty >= qty:
                        amount = qty * rate
                        sales_to_add.append(Sale(item_id=item_id, qty=qty, rate=rate, amount=amount))
                        item.qty -= qty
                        total_sale_amount += amount
                    else:
                        flash(f"Not enough stock for item {item_id}.", 'danger')
                        return redirect(url_for('add_sale'))

            if sales_to_add:
                company.cash_balance += total_sale_amount
                db.session.add_all(sales_to_add)
                db.session.commit()
                flash('Sales successfully added!', 'success')
            else:
                flash('No valid sales processed.', 'danger')

        except Exception as e:
            db.session.rollback()
            flash("An error occurred while processing the sale.", 'danger')

        return redirect(url_for('add_sale'))

    return render_template('add_sale.html', items=items, balance=balance)
# *********************************************************************************************************

@app.route('/view_reports')
def view_reports():
    purchase_page = request.args.get('purchase_page', default=1, type=int)
    sale_page = request.args.get('sale_page', default=1, type=int)
    company = Company.query.first()
    balance = company.cash_balance if company else 0

    purchases = Purchase.query.order_by(Purchase.timestamp.desc()).paginate(page=purchase_page, per_page=5)
    sales = Sale.query.order_by(Sale.timestamp.desc()).paginate(page=sale_page, per_page=5)

    return render_template('view_reports.html',purchases=purchases,sales=sales,balance=balance)

if __name__ == '__main__':
    app.run(debug=True)
