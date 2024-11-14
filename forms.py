from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from models import Item

class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    price = FloatField('Price per Unit', validators=[DataRequired(), NumberRange(min=0)])
    qty = IntegerField('Quantity', default=0)
    submit = SubmitField('Save')

class PurchaseForm(FlaskForm):
    item_id = IntegerField('Item ID', validators=[DataRequired()])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    rate = FloatField('Rate per Unit', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Purchase')

class SaleForm(FlaskForm):
    # Populate dropdown with item names and store item ID in the choice tuple
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    rate = DecimalField('Rate', validators=[DataRequired()])
    submit = SubmitField('Add Sale')

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        # Fetch items from database for the dropdown choices
        self.item_id.choices = [(item.id, item.name) for item in Item.query.all()]
