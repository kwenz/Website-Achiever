import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
from config import basedir
from sqlalchemy.orm import sessionmaker
from flaskext.markdown import Markdown
from flask.ext.principal import Principal,Permission,RoleNeed




# Session = sessionmaker()
# session=Session()



app=Flask(__name__)
app.config.from_object('config')

db=SQLAlchemy(app)

pagedown=PageDown()
pagedown.init_app(app)

mkd=Markdown(app)

lm=LoginManager()
lm.init_app(app)
lm.login_view='login'

principals=Principal(app)

admin_permission=Permission(RoleNeed('admin'))
owner_permission=Permission(RoleNeed('owner'))

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    file_handler=RotatingFileHandler('tmp/ach.log','a',1*1024*1024,10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('Achievement startup')


from app import views,models