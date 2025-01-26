from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from os import path
from flask_login import LoginManager
from sqlalchemy import select


db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'AAAAAAA'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')


    from .models import User, Product, Order, Order_Cart_Product  

    create_database(app)  
    import_products(app, db)  
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print("Created Database!")
        

def import_products(app, db): 
    
    from .models import Product, User, Category, Machine, Machine_Product
    import pandas as pd
    from werkzeug.security import generate_password_hash, check_password_hash
    
    file_path = 'C:/Users/Tom/Desktop/diplwmatiki_db.xlsx'
    with app.app_context():
        data = pd.read_excel(file_path)
        
        categories_count = Category.query.count()
        
        
    
        if categories_count == 0:
            
            distinct_categories = data['Category'].unique()
            
            for c in distinct_categories:
                print(c)
                category= Category(
                    name = c
                )
                
                db.session.add(category)
                
            db.session.commit()

        
        machines_count = Machine.query.count()
        
        if machines_count == 0:
            
            machines = data[['Machine', 'Category']].drop_duplicates().values

            for m in machines:
                name = m[0]
                category = Category.query.filter_by(name=m[1]).first()
                if category:
                    category_id = category.id

                    machine = Machine(
                        name = name,
                        category_id = category_id
                    )
                    db.session.add(machine)
                    
            db.session.commit()

        
        
        
        products_count = Product.query.count()
    
        if products_count == 0:
           
            for index, row in data.iterrows():
                print(f"Processing row {index}: {row}")
                product = Product(
                    product_code=row['Product Code'],
                    product_name=row['Product Name'],
                    price=row['Price'],
                    stock_quantity=row['Stock Quantity'],
                )
                db.session.add(product)

            try:
                db.session.commit()
                print("Data imported successfully.")
            except Exception as e:
                print(f"Error importing data: {e}")
        else:
            print("Products already imported")
            
            machines_products = data[['Machine', 'Product Name']].values
            
            for m in machines_products:
                machine = Machine.query.filter_by(name=m[0]).first()
                machine_id = machine.id
                
                product = Product.query.filter_by(product_name=m[1]).first()
                product_id = product.id
                
                machine_product = Machine_Product(
                    machine_id = machine_id,
                    product_id = product_id
                )
                db.session.add(machine_product)
                
            db.session.commit()
            
        admin = User.query.filter(User.role=='employee').first()
        
        if not admin:
            new_user=User(email='tomchatz96@gmail.com', first_name='user.emp', password=generate_password_hash('123456789', method='pbkdf2:sha256'), role='employee')
            db.session.add(new_user)
            db.session.commit()
        else: 
            print("employee already imported")


        customer = User.query.filter(User.role=='customer').first()

        if not customer:
            new_user=User(email='tomchatz97@gmail.com', first_name='user.cust', password=generate_password_hash('123456789', method='pbkdf2:sha256'), role='customer')
            db.session.add(new_user)
            db.session.commit()
        else: 
            print("customer already imported")