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
from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime, LargeBinary, ARRAY
from sqlalchemy import event

app = Flask(__name__)


# SQLite Database creation
Base = declarative_base()
db_name = os.getenv("DEALS_SITE_DB","deals-site.db")
db_url = "sqlite:///" + db_name
engine = create_engine(db_url, echo=True, future=True)
Session = sessionmaker(bind=engine)


# Deal object class
class Deal(Base):
    __tablename__ = 'deals'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    categories = Column(String)
    price = Column(Float)
    store = Column(String)
    description = Column(String)
    image = Column(LargeBinary)
    img_name = Column(String)
    img_mimetype = Column(String)
    likes = Column(Integer)
    date = Column(DateTime)
    favorites = relationship("Favorite", cascade="all, delete-orphan")

    def __repr__(self):
        return "<Deal(title='%s', url='%s', categories='%s', price='%f', description='%s', likes='%d', date='%s')>" % (
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
    dealId = Column(ForeignKey("deals.id"), primary_key=True)
    userName = Column(ForeignKey("user.name"), primary_key=True)

    def __repr__(self):
        return "<Favorite(dealId='%d', userName='%d')>" % (self.dealId, self.userName)

    # Ref: https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


Base.metadata.create_all(engine)


# Deal REST API calls
@app.route("/deals")
def get_deals():
    app.logger.info("Inside get_deals")
    ret_obj = {}

    session = Session()
    deals = session.query(Deal)
    deal_list = []
    for deal in deals:
        deal_dict = {"title": deal.title,
                        "url": deal.url,
                        "categories": deal.categories,
                        "price": deal.price,
                        "store": deal.store,
                        "description": deal.description,
                        "image": deal.img_name,
                        "likes": deal.likes,
                        "date": deal.date}
        deal_list.append(deal_dict)

    ret_obj['deals'] = deal_list
    return ret_obj

@app.route("/add_deal", methods=['POST'])
def add_deal():
    app.logger.info("Inside add_deal")

    title = request.form['titleInput']
    url = request.form['urlInput']
    categories = ','.join(request.form.getlist('categorySelect'))
    price = float(request.form['priceInput'])
    store = request.form['storeInput']
    description = request.form['descriptionInput']

    # Convert file to String by encoding image file, then decoding it
    file = request.files['imageInput']
    if not file:
        return Response("No image uploaded\n", status=400)
    image = file.read()
    img_name = secure_filename(file.filename)
    img_mimetype = file.mimetype

    likes = 0
    date = datetime.datetime.now()

    deal = Deal(title=title,
                    url=url,
                    categories=categories,
                    price=price,
                    store=store,
                    description=description,
                    image=image,
                    img_name=img_name,
                    img_mimetype=img_mimetype,
                    likes=likes,
                    date=date)

    session = Session()
    session.add(deal)
    session.commit()

    # Render webpage with new content
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(BASE_DIR, "templates/deals-site.html")

    fp = open(template_path,"r")
    contents = fp.read()
    t = Template(contents)

    deals_list = []
    deals = session.query(Deal)
    for deal in deals:
        deal = {"title": deal.title,
                    "url": deal.url,
                    "categories": deal.categories,
                    "price": "${:0.2f}".format(deal.price),
                    "store": deal.store,
                    "description": deal.description,
                    "image": base64.b64encode(deal.image).decode("ascii"),
                    "img_mimetype": deal.img_mimetype,
                    "likes": deal.likes,
                    "date": deal.date.strftime("%x")}
        deals_list.append(deal)
    
    main_page = t.render(deals_list=deals_list)

    return Response(main_page, status=200)


@app.route("/")
def index():
    app.logger.info("Inside index")

    # Render webpage content
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(BASE_DIR, "templates/deals-site.html")

    fp = open(template_path,"r")
    contents = fp.read()
    t = Template(contents)

    deals_list = []
    session = Session()
    deals = session.query(Deal)
    for deal in deals:
        deal = {"title": deal.title,
                    "url": deal.url,
                    "categories": deal.categories,
                    "price": "${:0.2f}".format(deal.price),
                    "store": deal.store,
                    "description": deal.description,
                    "image": base64.b64encode(deal.image).decode("ascii"),
                    "img_mimetype": deal.img_mimetype,
                    "likes": deal.likes,
                    "date": deal.date.strftime("%x")}
        deals_list.append(deal)
    
    main_page = t.render(deals_list=deals_list)

    return Response(main_page, status=200)


# Main method
if __name__ == '__main__':
    app.debug = True
    app.logger.info('Portal started...')
    app.run(host='0.0.0.0', port=5003) 