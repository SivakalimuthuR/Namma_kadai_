from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from models import db, Company, Item, Purchase, Sale
from forms import ItemForm, PurchaseForm, SaleForm

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


@app.route('/item/add', methods=['GET', 'POST'])
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(name=form.name.data, price=form.price.data, qty=form.qty.data)
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('home'))
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

@app.route('/sale/add', methods=['GET', 'POST'])
def add_sale():
    form = SaleForm()
    if form.validate_on_submit():
        item = Item.query.get(form.item_id.data)
        company = Company.query.first()
        amount = form.qty.data * form.rate.data
        if item.qty < form.qty.data:
            flash('Insufficient stock for sale!', 'danger')
        else:
            sale = Sale(item_id=form.item_id.data, qty=form.qty.data, rate=form.rate.data, amount=amount)
            item.qty -= form.qty.data
            company.cash_balance += amount
            db.session.add(sale)
            db.session.commit()
            flash('Sale added successfully!', 'success')
            return redirect(url_for('home'))
    return render_template('add_sale.html', form=form)


@app.route('/reports')
def view_reports():
    company = Company.query.first()
    items = Item.query.all()
    return render_template('view_reports.html', cash_balance=company.cash_balance, items=items)


if __name__ == '__main__':
    app.run(debug=True)
