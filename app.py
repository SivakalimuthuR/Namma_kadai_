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
# csrf = CSRFProtect(app)

def initialize_data():
    with app.app_context():
        db.create_all()
        if not Company.query.first():
            # Create initial company record
            company = Company(name="Namma Kadai", cash_balance=1000)
            db.session.add(company)
            db.session.commit()

initialize_data()

# Define your routes here
@app.route('/')
def home():
    company = Company.query.first()
    items = Item.query.all()
    balance = company.cash_balance if company else 0  # balance already defined here
    return render_template('home.html', balance=balance, items=items)  # Only pass 'balance'

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    form = ItemForm()
    items = Item.query.all()  # Get all items to display in the table
    company = Company.query.first()
    balance = company.cash_balance if company else 0


    if form.validate_on_submit():
        # Check if item already exists
        if Item.query.filter_by(name=form.name.data).first():
            flash('Item already exists.', 'danger')
        else:
            new_item = Item(name=form.name.data, price=form.price.data, qty=form.qty.data)
            db.session.add(new_item)
            db.session.commit()
            flash('Item added successfully!', 'success')
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

        # Check if the new name already exists in another item
        existing_item = Item.query.filter_by(name=new_name).first()
        if existing_item and existing_item.id != item.id:
            return jsonify({'success': False, 'message': 'Item with this name already exists.'})

        # Update item fields
        item.name = new_name
        item.price = data.get('price', item.price)
        item.qty = data.get('qty', item.qty)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item updated successfully'})
    return jsonify({'success': False, 'message': 'Item not found'})

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


@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    items = {item.id: (item.name, item.qty) for item in Item.query.all()}  # Get items from DB
    company = Company.query.first()  # Get the company balance
    balance = company.cash_balance if company else 0

    if request.method == 'POST':
        try:
            # Retrieve the form data
            sales = request.form.to_dict(flat=False)
            print("Sales data:", sales)  # Debugging

            total_sale_amount = 0
            sales_to_add = []  # To store sale objects

            # The number of sales entries to process (based on how many item_ids exist)
            sale_count = sum(1 for key in sales.keys() if 'item_id' in key)
            print(f"Sale Count: {sale_count}")

            # Loop through each sale entry
            for i in range(sale_count):
                print(f"Processing Sale {i}...")
                
                item_ids = sales[f'sales[{i}][item_id]']  # This will contain multiple item IDs for a single sale
                qty = int(sales[f'sales[{i}][qty]'][0])  # Quantity
                rate = float(sales[f'sales[{i}][rate]'][0])  # Rate
                
                # Check each item in the current sale entry
                for item_id in item_ids:
                    item_id = int(item_id)  # Convert item_id to int
                    item = Item.query.get(item_id)  # Get the item from DB
                    
                    if item and item.qty >= qty:
                        # Process sale if stock is sufficient
                        amount = qty * rate
                        sale = Sale(item_id=item_id, qty=qty, rate=rate, amount=amount)
                        sales_to_add.append(sale)
                        item.qty -= qty  # Deduct the quantity from stock
                        total_sale_amount += amount  # Add to total sale amount
                    else:
                        flash(f"Not enough stock for item {item_id}.", 'danger')
                        return redirect(url_for('add_sale'))

            # If there are valid sales, commit to database
            if sales_to_add:
                company.cash_balance += total_sale_amount  # Update balance
                db.session.add_all(sales_to_add)
                db.session.commit()  # Commit sales transaction
                flash('Sales successfully added!', 'success')
            else:
                flash('Sale processing failed.', 'danger')

        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            print("Error processing sale:", e)
            flash("An error occurred while processing the sale.", 'danger')

        return redirect(url_for('add_sale'))

    return render_template('add_sale.html', items=items, balance=balance)



@app.route('/view_reports')
def view_reports():
    purchase_page = request.args.get('purchase_page', default=1, type=int)
    sale_page = request.args.get('sale_page', default=1, type=int)
    company = Company.query.first()
    balance = company.cash_balance if company else 0

    # Get paginated data in descending order
    purchases = Purchase.query.order_by(Purchase.timestamp.desc()).paginate(page=purchase_page, per_page=5)
    sales = Sale.query.order_by(Sale.timestamp.desc()).paginate(page=sale_page, per_page=5)

    return render_template(
        'view_reports.html',
        purchases=purchases,
        sales=sales,
        purchase_page=purchase_page,
        sale_page=sale_page,
        balance=balance
    )

if __name__ == '__main__':
    app.run(debug=True)
