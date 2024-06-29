from flask import Blueprint, render_template, flash, redirect, request, jsonify
from .models import Product, Cart, Order, db, CustomerContact, FarmerContact, Wishlist
from flask_login import login_required, current_user
from . import db
from intasend import APIService
from .forms import CustomerContactForm, FarmerContactForm

views = Blueprint('views', __name__)

API_PUBLISHABLE_KEY = 'ISPubKey_test_d1bec40f-d242-476e-b7f1-1d488daa4f23'

API_TOKEN = 'ISSecretKey_test_e05e5a41-62b5-4860-bf49-31cfeb084ac6'

#home
@views.route('/')
def home():

    items_true = Product.query.filter_by(flash_sale=True)
    items_false = Product.query.filter_by(flash_sale=False)

    return render_template('home.html', items_true=items_true, items_false=items_false, 
                           cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [], 
                           wishlist=Wishlist.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


#add_to_wishlist
@views.route('/add-to-wishlist/<int:item_id>')
@login_required
def add_to_wishlist(item_id):
    item_to_add = Product.query.get(item_id)
    if not item_to_add:
        flash('Product not found.')
        return redirect(request.referrer)

    if Wishlist.query.filter_by(product_link=item_id, customer_link=current_user.id).first():
        flash('Product already in your wishlist.')
        return redirect(request.referrer)

    new_wishlist_item = Wishlist()
    new_wishlist_item.product_link = item_to_add.id
    new_wishlist_item.customer_link = current_user.id

    try:
        db.session.add(new_wishlist_item)
        db.session.commit()
        flash('Product added to wishlist.')
    except Exception as e:
        print('Error adding product to wishlist:', e)
        flash('Failed to add product to wishlist.')

    return redirect(request.referrer)


#wishlist
@views.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = Wishlist.query.filter_by(customer_link=current_user.id).all()
    return render_template('wishlist.html', wishlist=wishlist_items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


#remove_from_wishlist
@views.route('/remove-from-wishlist', methods=['POST'])
@login_required
def remove_from_wishlist():
    item_id = request.form.get('item_id')
    wishlist_item = Wishlist.query.get(item_id)
    if not wishlist_item:
        flash('Wishlist item not found.')
        return redirect(request.referrer)

    try:
        db.session.delete(wishlist_item)
        db.session.commit()
        flash('Product removed from wishlist.')
    except Exception as e:
        print('Error removing product from wishlist:', e)
        flash('Failed to remove product from wishlist.')

    return redirect(request.referrer)


#add_to_cart
@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    
    if item_to_add.in_stock <= 0:
        flash('This item is currently out of stock.')
        return redirect(request.referrer)

    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    
    # Check if the item already exists in the cart
    if item_exists:
        try:
            item_exists.quantity += 1
            db.session.commit()
            flash(f'Quantity of {item_exists.product.product_name} has been updated')
            return redirect(request.referrer)
        except Exception as e:
            print('Quantity not Updated', e)
            flash(f'Quantity of {item_exists.product.product_name} not updated')
            return redirect(request.referrer)

    # If the item is not already in the cart, add it
    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.customer_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.product_name} added to cart')
    except Exception as e:
        print('Item not added to cart', e)
        flash(f'{new_cart_item.product.product_name} has not been added to cart')

    return redirect(request.referrer)


#cart
@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.current_price * item.quantity

    return render_template('cart.html', cart=cart, amount=amount, total=amount+200, wishlist=Wishlist.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


#plus_cart
@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity += 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


#minus_cart
@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            db.session.commit()
        else:
            # If quantity is 1, remove the item from the cart
            db.session.delete(cart_item)
            db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity if cart_item.quantity > 0 else 0,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


#remove_from_cart
@views.route('/remove-from-cart', methods=['POST'])
@login_required
def remove_from_cart():
    cart_id = request.form.get('cart_id')
    cart_item = Cart.query.get(cart_id)

    if not cart_item:
        flash('Cart item not found.', 'error')
        return redirect(request.referrer)

    try:
        product_name = cart_item.product.product_name
        db.session.delete(cart_item)
        db.session.commit()
        flash(f'{product_name} removed from cart.', 'success')
    except Exception as e:
        print('Error removing product from cart:', e)
        flash('Failed to remove product from cart.', 'error')

    return redirect(request.referrer)


#place_order
@views.route('/place-order')
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()
    if customer_cart:
        try:
            total = 0
            total_quantity = 0
            
            # Calculate total amount and quantity in the cart
            for item in customer_cart:
                total += item.product.current_price * item.quantity
                total_quantity += item.quantity

            # # Check if total quantity exceeds available stock for any product in the cart
            # for item in customer_cart:
            #     if item.quantity > item.product.in_stock:
            #         flash(f"The quantity of {item.product.product_name} exceeds the available stock.")
            #         return redirect('/cart')  # Redirect back to cart if any item exceeds stock
                
            
            # Check if total quantity exceeds available stock for any product in the cart
            items_exceeding_stock = [item for item in customer_cart if item.quantity > item.product.in_stock]
            if items_exceeding_stock:
                # Determine the appropriate flash message based on the number of items exceeding stock
                if len(items_exceeding_stock) == 1:
                    flash(f"The quantity of {items_exceeding_stock[0].product.product_name} exceeds the available stock.")
                else:
                    flash(f"The quantities of {', '.join([item.product.product_name for item in items_exceeding_stock])} exceed the available stock.")
                return redirect('/cart')  # Redirect back to cart if any item exceeds stock


            # Proceed with placing the order
            service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
            create_order_response = service.collect.mpesa_stk_push(phone_number='254-5530808', email=current_user.email,
                                                                   amount=total + 200, narrative='Purchase of goods')

            for item in customer_cart:
                new_order = Order()
                new_order.quantity = item.quantity
                new_order.price = item.product.current_price
                new_order.status = create_order_response['invoice']['state'].capitalize()
                new_order.payment_id = create_order_response['id']

                new_order.product_link = item.product_link
                new_order.customer_link = item.customer_link

                db.session.add(new_order)

                product = Product.query.get(item.product_link)

                product.in_stock -= item.quantity

                db.session.delete(item)

                db.session.commit()

            flash('Order Placed Successfully')

            return redirect('/orders')
        except Exception as e:
            print(e)
            flash('Order not placed')
            return redirect('/')
    else:
        flash('Your cart is Empty')
        return redirect('/')


#orders
@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [], wishlist=Wishlist.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


#search

# @views.route('/search', methods=['GET', 'POST'])
# def search():
#     if request.method == 'POST':
#         search_query = request.form.get('search')
#         items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
#         return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
#                            if current_user.is_authenticated else [], wishlist=Wishlist.query.filter_by(customer_link=current_user.id).all()
#                            if current_user.is_authenticated else [])

#     return render_template('search.html')





@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                            if current_user.is_authenticated else [], wishlist=Wishlist.query.filter_by(customer_link=current_user.id).all()
                            if current_user.is_authenticated else [])

    sort_by = request.args.get('sort')
    if sort_by == 'price_low_high':
        items = Product.query.order_by(Product.current_price.asc()).all()
    elif sort_by == 'price_high_low':
        items = Product.query.order_by(Product.current_price.desc()).all()
    elif sort_by == 'name':
        items = Product.query.order_by(Product.product_name).all()
    elif sort_by == 'availability':
        items = Product.query.order_by(Product.in_stock.desc()).all()
    else:
        items = Product.query.all()

    return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                            if current_user.is_authenticated else [], wishlist=Wishlist.query.filter_by(customer_link=current_user.id).all()
                            if current_user.is_authenticated else [])



#contact us

#customer
@views.route('/feedback')
@login_required
def feedback():
    customer_form = CustomerContactForm()
    return render_template('feedback.html', customer_form=customer_form, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [], wishlist=Wishlist.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

@views.route('/contact/customer', methods=['POST'])
@login_required
def customer_contact():
    form = CustomerContactForm(request.form)
    if form.validate():
        contact = CustomerContact(
            name=current_user.username,
            email=current_user.email, 
            feedback=form.feedback.data,
            customer_id=current_user.id 
        )
        db.session.add(contact)
        db.session.commit()
        flash('Your message has been sent successfully!')
        return redirect('/')
    else:
        flash('Please fill in all the required fields.')
        return redirect('/feedback')


#farmer
@views.route('/contact-us')
def contact_us():
    farmer_form = FarmerContactForm()
    return render_template('contact_us.html', farmer_form=farmer_form, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [], wishlist=Wishlist.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

@views.route('/contact/farmer', methods=['POST'])
def farmer_contact():
    form = FarmerContactForm(request.form)
    if form.validate():
        contact = FarmerContact(
            name=form.name.data,
            email=form.email.data,
            product=form.product.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            description=form.description.data
        )
        db.session.add(contact)
        db.session.commit()
        flash('Your message has been sent successfully!')
        return redirect('/')
    else:
        flash('Please fill in all the required fields.')
        return redirect('/contact-us')


#about_us
@views.route('/about-us')
def about_us():
    return render_template('about_us.html', cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [], wishlist=Wishlist.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])
