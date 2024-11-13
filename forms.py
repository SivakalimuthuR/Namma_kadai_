from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

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
    item_id = IntegerField('Item ID', validators=[DataRequired()])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    rate = FloatField('Rate per Unit', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Sale')
