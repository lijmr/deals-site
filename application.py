from flask import Flask, render_template, redirect, request, url_for, abort, jsonify
from jinja2 import Environment, PackageLoader, select_autoescape
from flask import Response
from werkzeug.utils import secure_filename

import requests
import os
import time
import random
import string
import datetime
import base64

from jinja2 import Template

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime
from sqlalchemy import event

app = Flask(__name__)


# SQLite Database creation
Base = declarative_base()
db_name = os.getenv("DEALS_SITE_DB","deals-site.db")
db_url = "sqlite:///" + db_name
engine = create_engine(db_url, echo=True, future=True)
Session = sessionmaker(bind=engine)


# Product object class
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    categories = Column(String)
    price = Column(Float)
    description = Column(String)
    image = Column(String)
    likes = Column(Integer)
    date = Column(DateTime)
    favorites = relationship("Favorite", cascade="all, delete-orphan")

    def __repr__(self):
        return "<Product(title='%s', url='%s', categories='%s', price='%f', description='%s', likes='%d', date='%s')>" % (
                self.title, self.url, self.categories, self.price, self.description, self.likes, self.date)

    # Ref: https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# User object class
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s')>" % (self.name, self.role)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Favorite object class
class Favorite(Base):
    __tablename__ = 'favorites'
    productId = Column(ForeignKey("products.id"), primary_key=True)
    userName = Column(ForeignKey("user.name"), primary_key=True)

    def __repr__(self):
        return "<Favorite(productId='%d', userName='%d')>" % (self.productId, self.userName)

    # Ref: https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


Base.metadata.create_all(engine)


# Product REST API calls
@app.route("/products")
def get_products():
    app.logger.info("Inside get_products")
    ret_obj = {}

    session = Session()
    products = session.query(Product)
    product_list = []
    for product in products:
        product_list.append(product.as_dict())

    ret_obj['products'] = product_list
    return ret_obj

@app.route("/products", methods=['POST'])
def add_product():
    app.logger.info("Inside add_product")

    title = request.form['titleInput']
    url = request.form['urlInput']
    categories = request.form['categorySelect']
    price = float(request.form['priceInput'])
    description = request.form['descriptionInput']

    # Convert file to String by encoding image file, then decoding it
    file = request.files['imageInput']
    if not file:
        return Response("No image uploaded\n", status=400)
    image = base64.b64encode(file.read()).decode('utf8')

    likes = 0
    date = datetime.datetime.now()

    product = Product(title=title,
                    url=url,
                    categories=categories,
                    price=price,
                    description=description,
                    image=image,
                    likes=likes,
                    date=date)

    session = Session()
    session.add(product)
    session.commit()

    return product.as_dict()


@app.route("/")
def index():
    app.logger.info("Inside index")
    return render_template('deals-site.html')


# Main method
if __name__ == '__main__':
    app.debug = True
    app.logger.info('Portal started...')
    app.run(host='0.0.0.0', port=5003) 