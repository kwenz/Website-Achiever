import os




WTF_CSRF_ENABLED=True
SECRET_KEY='you-will-never-guess'


POSTS_PER_PAGE=10
STORIES_PER_PAGE=3

MAX_DISTANCE=30

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


basedir=os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI="sqlite:///"+os.path.join(basedir,'app.db')
SQLALCHEMY_MIGRATE_REPO=os.path.join(basedir,'db_repository')

GOOGLE_API_KEY='AIzaSyA4PdZGnvUz0swhVbJLAItHg0XYChZOiIg'
GOOGLE_GEOCODE_URL='https://maps.googleapis.com/maps/api/geocode/json'

ADMIN_USERNAME='admin'
ADMIN_PASSWORD='admin'
