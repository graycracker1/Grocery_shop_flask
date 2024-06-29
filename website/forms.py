from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, length, NumberRange, Email
from flask_wtf.file import FileField, FileRequired

#signup_form
class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), length(min=2)])
    password1 = PasswordField('Enter Your Password', validators=[DataRequired(), length(min=6)])
    password2 = PasswordField('Confirm Your Password', validators=[DataRequired(), length(min=6)])
    submit = SubmitField('Sign Up')

#login_form
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Enter Your Password', validators=[DataRequired()])
    submit = SubmitField('Log in')

#password_change_form
class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), length(min=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), length(min=6)])
    change_password = SubmitField('Change Password')

#edit_profile_form
class EditProfileForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), length(min=2)])
    address = StringField('Address', validators=[DataRequired(), length(max=256)])
    submit = SubmitField('Save Changes')


#shop_items_form
class ShopItemsForm(FlaskForm):
    product_name = StringField('Name of Product', validators=[DataRequired()])
    current_price = FloatField('Current Price', validators=[DataRequired()])
    previous_price = FloatField('Previous Price', validators=[DataRequired()])
    in_stock = IntegerField('In Stock', validators=[DataRequired(), NumberRange(min=0)])

    unit_of_measurement = SelectField('Unit of Measurement', choices=[('pieces', 'Pieces'), ('kilos', 'Kilos'), ('liters', 'Liters')])
    small_unit_of_measurement = StringField('Small Unit of Measurement', validators=[DataRequired()])

    product_picture = FileField('Product Picture', validators=[DataRequired()])
    flash_sale = BooleanField('Flash Sale')

    add_product = SubmitField('Add Product')
    update_product = SubmitField('Update')


#order_form
class OrderForm(FlaskForm):
    order_status = SelectField('Order Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'),
                                                        ('Out for delivery', 'Out for delivery'),
                                                        ('Delivered', 'Delivered'), ('Canceled', 'Canceled')])

    update = SubmitField('Update Status')


# contact_us_form

#customer
class CustomerContactForm(FlaskForm):
    #name = StringField('Name', validators=[DataRequired()])
    feedback = TextAreaField('Feedback', validators=[DataRequired(), length(max=1000)])

#farmer
class FarmerContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    product = StringField('Product', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(max=10000)])
    unit = SelectField('Unit of Measurement', choices=[('pieces', 'Pieces'), ('kilos', 'Kilos'), ('liters', 'Liters')])
    description = TextAreaField('Description', validators=[DataRequired(), length(max=500)])
