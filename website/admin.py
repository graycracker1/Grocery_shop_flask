from flask import Blueprint, render_template, flash, send_from_directory, redirect, request
from flask_login import login_required, current_user
from .forms import ShopItemsForm, OrderForm
from werkzeug.utils import secure_filename
from .models import Product, Order, Customer, CustomerContact, FarmerContact
from . import db



from . import admin


admin = Blueprint('admin', __name__)


@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)


@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id == 1:
        form = ShopItemsForm()

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data

            unit_of_measurement = form.unit_of_measurement.data  # Get unit of measurement from form
            small_unit_of_measurement = form.small_unit_of_measurement.data  # small Get unit of measurement from form

            flash_sale = form.flash_sale.data

            file = form.product_picture.data

            file_name = secure_filename(file.filename)

            file_path = f'./media/{file_name}'

            file.save(file_path)

            new_shop_item = Product()
            new_shop_item.product_name = product_name
            new_shop_item.current_price = current_price
            new_shop_item.previous_price = previous_price
            new_shop_item.in_stock = in_stock

            new_shop_item.unit_of_measurement = unit_of_measurement  # Set unit of measurement
            new_shop_item.small_unit_of_measurement = small_unit_of_measurement # small

            new_shop_item.flash_sale = flash_sale
            new_shop_item.product_picture = file_path

            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'{product_name} added Successfully')
                print('Product Added')
                return render_template('add_shop_items.html', form=form)
            except Exception as e:
                print(e)
                flash('Product Not Added!!')

        return render_template('add_shop_items.html', form=form)

    return render_template('404.html')

@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template('404.html')


# @admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
# @login_required
# def update_item(item_id):
#     if current_user.id == 1:
#         form = ShopItemsForm()

#         item_to_update = Product.query.get(item_id)

#         # Pre-fill the form fields with existing values
#         form.product_name.data = item_to_update.product_name
#         form.previous_price.data = item_to_update.previous_price
#         form.current_price.data = item_to_update.current_price
#         form.in_stock.data = item_to_update.in_stock

#         form.unit_of_measurement.data = item_to_update.unit_of_measurement #unit
#         form.small_unit_of_measurement.data = item_to_update.small_unit_of_measurement #small

#         form.flash_sale.data = item_to_update.flash_sale

#         if form.validate_on_submit():
#             # Retrieve updated values from the form
#             product_name = form.product_name.data
#             current_price = form.current_price.data
#             previous_price = form.previous_price.data
#             in_stock = form.in_stock.data

#             unit_of_measurement =form.unit_of_measurement.data #unit
#             small_unit_of_measurement =form.small_unit_of_measurement.data #small

#             flash_sale = form.flash_sale.data

#             file = form.product_picture.data

#             file_name = secure_filename(file.filename)

#             file_path = f'./media/{file_name}'

#             file.save(file_path)

#             # Update the item in the database
#             item_to_update.product_name = product_name
#             item_to_update.current_price = current_price
#             item_to_update.previous_price = previous_price
#             item_to_update.in_stock = in_stock

#             item_to_update.unit_of_measurement = unit_of_measurement #unit
#             item_to_update.small_unit_of_measurement = small_unit_of_measurement #small

#             item_to_update.flash_sale = flash_sale

#             try:
#                 db.session.commit()
#                 flash('Item updated successfully.')
#                 return redirect('/shop-items')
#             except Exception as e:
#                 db.session.rollback()
#                 flash('Failed to update item.')
#                 print(e)

#         return render_template('update_item.html', form=form)
#     return render_template('404.html')



@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id == 1:
        form = ShopItemsForm()
        item_to_update = Product.query.get(item_id)
        
        if request.method == 'POST':
            if form.validate_on_submit():
                item_to_update.product_name = form.product_name.data
                item_to_update.current_price = form.current_price.data
                item_to_update.previous_price = form.previous_price.data
                item_to_update.in_stock = form.in_stock.data
                item_to_update.unit_of_measurement = form.unit_of_measurement.data
                item_to_update.small_unit_of_measurement = form.small_unit_of_measurement.data
                item_to_update.flash_sale = form.flash_sale.data

                file = form.product_picture.data
                if file:
                    file_name = secure_filename(file.filename)
                    file_path = f'./media/{file_name}'
                    file.save(file_path)
                    item_to_update.product_picture = file_path
                
                try:
                    db.session.commit()
                    flash('Item updated successfully.')
                    return redirect('/shop-items')
                except Exception as e:
                    db.session.rollback()
                    flash('Failed to update item.')
                    print(e)
        
        # Pre-fill the form fields with existing values
        form.product_name.data = item_to_update.product_name
        form.previous_price.data = item_to_update.previous_price
        form.current_price.data = item_to_update.current_price
        form.in_stock.data = item_to_update.in_stock
        form.unit_of_measurement.data = item_to_update.unit_of_measurement
        form.small_unit_of_measurement.data = item_to_update.small_unit_of_measurement
        form.flash_sale.data = item_to_update.flash_sale

        return render_template('update_item.html', form=form)
    else:
        return render_template('404.html')


#delete_item
@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.id == 1:
        try:
            item_to_delete = Product.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            flash('One Item deleted')
            return redirect('/shop-items')
        except Exception as e:
            print('Item not deleted', e)
            flash('Item not deleted!!')
        return redirect('/shop-items')

    return render_template('404.html')


#view_orders
@admin.route('/view-orders')
@login_required
def order_view():
    if current_user.id == 1:
        orders = Order.query.all()
        return render_template('view_orders.html', orders=orders)
    return render_template('404.html')


#update_order
@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    if current_user.id == 1:
        form = OrderForm()

        order = Order.query.get(order_id)

        if form.validate_on_submit():
            status = form.order_status.data
            order.status = status

            try:
                db.session.commit()
                flash(f'Order {order_id} Updated successfully')
                return redirect('/view-orders')
            except Exception as e:
                print(e)
                flash(f'Order {order_id} not updated')
                return redirect('/view-orders')

        return render_template('order_update.html', form=form)

    return render_template('404.html')


#customer
@admin.route('/customers')
@login_required
def display_customers():
    if current_user.id == 1:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')


#admin_page
@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id == 1:
        return render_template('admin.html')
    return render_template('404.html')


#contact us

#customer
@admin.route('/feedback-entry', methods=['GET', 'POST'])
@login_required
def feedback_entry():
    if current_user.id == 1:
        items = CustomerContact.query.order_by(CustomerContact.id).all()
        return render_template('feedback_entry.html', items=items)
    return render_template('404.html')

#farmer
@admin.route('/contact-us-entry', methods=['GET', 'POST'])
@login_required
def contact_us_entry():
    if current_user.id == 1:
        items = FarmerContact.query.order_by(FarmerContact.id).all()
        return render_template('contact_us_entry.html', items=items)
    return render_template('404.html')


# @admin.route('/contact-us-entry')
# def contact_us_entry():
#     items = CustomerContact.query.all()
#     return render_template('contact_us_entry.html', items=items)
