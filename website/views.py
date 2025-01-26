from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    get_flashed_messages,
    redirect,
    url_for,
    session,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from flask_security import roles_required
from . import db
from .models import (
    User,
    Product,
    Order,
    Machine,
    Category,
    Machine_Product,
    Customer_Cart,
    Order_Cart_Product,
)
from sqlalchemy import and_


views = Blueprint("views", __name__)


@views.route("/")
@login_required
def home():
    user = current_user

    if current_user.role == "employee":
        
        unapproved_orders = Order.query.filter_by(status="pending").count()
        return render_template("admin/home.html", user=current_user, unapproved_orders=unapproved_orders)
    else:
        categories = Category.query.all()
        return render_template("home.html", categories=categories)


@views.route("/admin")
@login_required
def admin_home():
    return render_template("admin/home.html", user=current_user)


@views.route("/admin/users", methods=["GET"])
@login_required
def users():
    users = User.query.all()
    return render_template("/admin/users.html", users=users)


@views.route("/admin/users/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        role = request.form.get("role")

        user = User.query.filter_by(email=email).first()

        if user:
            flash("This email already exists", category="error")
        elif len(email) < 4:
            flash("Email must contain at least 4 characters", category="error")
        elif len(first_name) < 2:
            flash("First Name must contain at least 2 characters", category="error")
        elif password1 != password2:
            flash("Passwords do not match!", category="error")
        elif len(password1) < 7:
            flash("Password must contain at least 7 characters", category="error")
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                password=generate_password_hash(password1, method="pbkdf2:sha256"),
                role=role,
            )
            db.session.add(new_user)
            db.session.commit()

            flash("Account created successfully", category="success")

            return redirect(url_for("views.users"))

    return render_template("admin/add_user.html")


@views.route("/admin/users/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        role = request.form.get("role")

        user = User.query.filter_by(id=user_id).first()

        if len(email) < 4:
            flash("Email must contain at least 4 characters", category="error")
        elif len(first_name) < 2:
            flash("First Name must contain at least 2 characters", category="error")
        else:
            user.email = email
            user.first_name = first_name
            user.role = role
            db.session.commit()

            flash("Account edited successfully", category="success")

            return redirect(url_for("views.users"))

    user = User.query.filter_by(id=user_id).first()
    return render_template("admin/edit_user.html", user=user)


@views.route("/admin/users/delete_user/<int:user_id>", methods=["POST"])
def DELETE_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("views.users"))


@views.route("admin/products")
def products():
    all_products = Product.query.all()
    for product in all_products:
        product.low_stock=product.stock_quantity<5
    return render_template("admin/products.html", products=all_products)


@views.route("/admin/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        
        new_stock = request.form.get("stock_quantity")
        product.stock_quantity = new_stock
        db.session.commit()
        return redirect(url_for("views.products"))

    return render_template("admin/edit_product.html", product=product)


@views.route("/admin/products/delete_product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("views.products"))


@views.route("/admin/products/increase_stock/<int:product_id>/<int:increase_by>", methods=["POST"])
def increase_stock(product_id, increase_by):
    print(product_id)
    product = Product.query.get_or_404(product_id)
    product.stock_quantity += increase_by
    db.session.commit()
    return jsonify({"message": "Success!"}), 200

@views.route("/admin/products/reduce_stock/<int:product_id>/<int:decrease_by>", methods=["POST"])
def reduce_stock(product_id, decrease_by):
    print(product_id)
    product = Product.query.get_or_404(product_id)
    product.stock_quantity -= decrease_by
    if product.stock_quantity < 0:
        return jsonify({"message": "Stock can't be less than 0"}), 400
    db.session.commit()
    return jsonify({"message": "Success!"}), 200


@views.route("/admin/orders")
def orders():
    all_orders = Order.query.all()
    return render_template("admin/orders.html", orders=all_orders)


@views.route("/customer/machines/<int:category_id>", methods=["GET"])
@login_required
def get_machines(category_id):
    machines = Machine.query.filter_by(category_id=category_id).all()
    return render_template("/customer/machines.html", machines=machines)


@views.route("/customer/products/<int:machine_id>", methods=["GET"])
@login_required
def get_customer_products(machine_id):
    products = (
        Product.query.join(Machine_Product)
        .filter(Machine_Product.machine_id == machine_id)
        .all()
    )
    return render_template("/customer/products.html", products=products)


@views.route("/addtocart/<int:customer_id>/<int:product_id>", methods=["POST"])
def add_to_cart(customer_id, product_id):
    print(f"{customer_id, product_id}")
    cart_item = (
        Customer_Cart.query.join(Product)
        .join(User)
        .join(
            Order_Cart_Product,
            Customer_Cart.id == Order_Cart_Product.cart_product_id,
            isouter=True,
        )
        .filter(Product.id == product_id, User.id == customer_id, Order_Cart_Product.order_id.is_(None))
        .first()
    )

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Customer_Cart(
            customer_id=customer_id, product_id=product_id, quantity=1
        )
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"message": "Success!"}), 200


@views.route("/customer/cart/<int:user_id>", methods=["GET"])
def get_cart(user_id):
    cart_items = (
        db.session.query(Customer_Cart, Product)
        .join(Product, Customer_Cart.product_id == Product.id)
        .join(
            Order_Cart_Product,
            Customer_Cart.id == Order_Cart_Product.cart_product_id,
            isouter=True,
        )
        .filter(
            and_(
                Order_Cart_Product.order_id.is_(None),
                Customer_Cart.customer_id == user_id,
            )
        )
        .all()
    )
    print(cart_items)

    total_price = 0
    cart_products = []
    for cart in cart_items:
        price = cart.Product.price * cart.Customer_Cart.quantity
        total_price += price
        cart_products.append(
            {
                "id": cart.Product.id,
                "cartid": cart.Customer_Cart.id,
                "name": cart.Product.product_name,
                "quantity": cart.Customer_Cart.quantity,
                "price": price,
            }
        )

    customer_cart = {"total_price": total_price, "cart_products": cart_products}

    return render_template("/customer/cart.html", customer_cart=customer_cart)


@views.route("/customer/cart/<int:user_id>", methods=["POST"])
def submit_order(user_id):
    order_items = (
        db.session.query(Customer_Cart, Product)
        .join(Product, Customer_Cart.product_id == Product.id)
        .join(
            Order_Cart_Product,
            Customer_Cart.id == Order_Cart_Product.cart_product_id,
            isouter=True,
        )
        .filter(
            and_(
                Order_Cart_Product.order_id.is_(None),
                Customer_Cart.customer_id == user_id,
            )
        )
        .all()
    )
    order = Order(status="pending", customer_id=user_id)
    db.session.add(order)
    db.session.commit()
    for order_item in order_items:
        order_cart_product = Order_Cart_Product(
            order_id=order.id, cart_product_id=order_item.Customer_Cart.id
        )
        db.session.add(order_cart_product)

    db.session.commit()
    flash("Order submitted successfully!", "success")
    return redirect(url_for("views.home"))


@views.route("/admin/orders/<int:order_id>", methods=["GET"])
def edit_order(order_id):
    order = (
        db.session.query(Order.id, Order.status, User.first_name)
        .join(User, User.id == Order.customer_id)
        .filter(Order.id == order_id)
        .first()
    )

    order_items = (
        db.session.query(Order, Order_Cart_Product, Customer_Cart, User, Product)
        .join(Order_Cart_Product, Order.id == Order_Cart_Product.order_id)
        .join(Customer_Cart, Order_Cart_Product.cart_product_id == Customer_Cart.id)
        .join(User, Customer_Cart.customer_id == User.id)
        .join(Product, Customer_Cart.product_id == Product.id)
        .filter(Order.id == order_id)
        .all()
    )

    customer_order = {}
    customer_order["order_id"] = order.id
    customer_order["customer_name"] = order.first_name
    customer_order["status"] = order.status

    total_price = 0

    products = []
    for order, order_cart_product, customer_cart, user, product in order_items:
        print(customer_cart)
        price = product.price * customer_cart.quantity
        total_price += price
        products.append(
            {
                "name": product.product_name,
                "quantity": customer_cart.quantity,
                "price": price,
            }
        )

    customer_order["total_price"] = total_price
    customer_order["products"] = products
    print(customer_order)
    return render_template("/admin/edit_order.html", customer_order=customer_order)


@views.route("/admin/orders/<int:order_id>", methods=["POST"])
def approve_order(order_id):
    order = db.session.query(Order).filter(Order.id == order_id).first()
    order.status = "approved"
    db.session.commit()
    return redirect(url_for("views.orders"))
