from flask_wtf import FlaskForm
from wtforms import DecimalField, FormField, IntegerField, FloatField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
from wtforms import FieldList
from wtforms import Form
from models import Item

class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField('Price per Unit', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save')


class PurchaseForm(FlaskForm):
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])  # This will be the dropdown for items
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])  # Quantity input
    rate = FloatField('Rate per Unit', validators=[DataRequired(), NumberRange(min=0)])  # Rate input
    submit = SubmitField('Add Purchase')


class SaleForm(FlaskForm):
    # Populate dropdown with item names and store item ID in the choice tuple
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    rate = DecimalField('Rate', validators=[DataRequired()])
    submit = SubmitField('Add Sale')



    def __init__(self, *args, **kwargs):
        super(PurchaseForm, self).__init__(*args, **kwargs)
        # This populates the dropdown with all items (id and name)
        self.item_id.choices = [(item.id, item.name) for item in Item.query.all()]