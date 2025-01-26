from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
import pytz




class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)  
    password = db.Column(db.String(50), nullable=False)  
    first_name = db.Column(db.String(20), nullable=False)  
    role = db.Column(db.String(10), nullable=False, default='customer')  



class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String, nullable=False) 
    product_name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

  
class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship('Order_Cart_Product', backref='order', lazy=True)
    status = db.Column(db.String, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Athens')))


class Order_Cart_Product(db.Model):
    __tablename__ = 'orders_cart_products'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    cart_product_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)



class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)


class Machine(db.Model):
    __tablename__ = 'machines'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category_id=db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)


class  Machine_Product(db.Model):
       __tablename__ = 'machines_products'
       
       id = db.Column(db.Integer, primary_key=True)
       product_id=db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
       machine_id=db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=False)
       
       
class  Customer_Cart(db.Model):
       __tablename__ = 'carts'
       
       id = db.Column(db.Integer, primary_key=True)
       product_id=db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
       customer_id=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
       quantity=db.Column(db.Integer,nullable=False)


       