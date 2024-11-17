from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, FloatField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
from models import Item

class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField('Price per Unit', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save')

class PurchaseForm(FlaskForm):
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    rate = FloatField('Rate per Unit', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Purchase')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_id.choices = [(item.id, item.name) for item in Item.query.all()]

class SaleForm(FlaskForm):
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    rate = DecimalField('Rate', validators=[DataRequired()])
    submit = SubmitField('Add Sale')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_id.choices = [(item.id, item.name) for item in Item.query.all()]
