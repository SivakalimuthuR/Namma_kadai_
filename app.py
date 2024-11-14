from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from models import db, Company, Item, Purchase, Sale
from forms import ItemForm, PurchaseForm, SaleForm
from sqlalchemy.exc import IntegrityError
from flask import jsonify

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

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
    return render_template('home.html', cash_balance=company.cash_balance, items=items)


@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        new_item = Item(name=form.name.data, price=form.price.data, qty=form.qty.data)
        
        try:
            db.session.add(new_item)
            db.session.commit()
            flash('Item added successfully!', 'success')
            return redirect(url_for('add_item'))  # Redirect back to the add_item page
        except IntegrityError:
            db.session.rollback()  # Roll back any partial transactions
            flash('Item already exists. Please add a different item.', 'danger')
            return redirect(url_for('add_item'))  # Redirect back to add_item with flash

    return render_template('add_item.html', form=form)



@app.route('/purchase/add', methods=['GET', 'POST'])
def add_purchase():
    form = PurchaseForm()
    if form.validate_on_submit():
        item = Item.query.get(form.item_id.data)
        company = Company.query.first()
        amount = form.qty.data * form.rate.data
        if company.cash_balance < amount:
            flash('Insufficient balance for purchase!', 'danger')
        else:
            purchase = Purchase(item_id=form.item_id.data, qty=form.qty.data, rate=form.rate.data, amount=amount)
            item.qty += form.qty.data
            company.cash_balance -= amount
            db.session.add(purchase)
            db.session.commit()
            flash('Purchase added successfully!', 'success')
            return redirect(url_for('home'))
    return render_template('add_purchase.html', form=form)

@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    form = SaleForm()
    items = {item.id: item.qty for item in Item.query.all()}  # item quantities for JavaScript
    
    if form.validate_on_submit():
        item_id = form.item_id.data
        qty = form.qty.data
        rate = form.rate.data
        amount = qty * rate

        sale = Sale(item_id=item_id, qty=qty, rate=rate, amount=amount)
        
        item = Item.query.get(item_id)
        if item and item.qty >= qty:  # Ensure enough stock
            item.qty -= qty
            db.session.add(sale)
            db.session.commit()
            flash('Sale added successfully!', 'success')
            return redirect(url_for('add_sale'))
        else:
            flash('Not enough quantity in stock for this sale.', 'danger')

    return render_template('add_sale.html', form=form, items=items)


@app.route('/reports')
def view_reports():
    company = Company.query.first()
    items = Item.query.all()
    return render_template('view_reports.html', cash_balance=company.cash_balance, items=items)


if __name__ == '__main__':
    app.run(debug=True)
