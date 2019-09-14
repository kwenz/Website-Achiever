from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, PasswordField, TextField, validators, SelectField, FormField, FieldList, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange
from .models import User
from flask.ext.pagedown.fields import PageDownField
from datetime import datetime
from wtforms.fields.html5 import DateTimeLocalField, DateField, IntegerRangeField, URLField, TelField



class LoginForm(Form):
    username=StringField('username',validators=[DataRequired()])
    password=PasswordField('password',validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class EditForm(Form):
    nickname=StringField('nickname',validators=[DataRequired()])
    about_me=TextAreaField('about_me',validators=[Length(min=0,max=140)])
    title=SelectField('title')

class EditOwnerForm(Form):
    nickname=StringField('nickname',validators=[DataRequired()])
    about_me=TextAreaField('about_me',validators=[Length(min=0,max=140)])



class AccountCreationForm(Form):
    username=TextField('Username',validators=[DataRequired()])
    password=PasswordField('New Password', [validators.Required(),validators.Length(min=6,max=30,message="Password has to have at least 6 characters."),validators.EqualTo('confirm',message="Passwords must match")])
    confirm=PasswordField('Repeat Password')
    email=TextField('Email Address',[validators.Required(),validators.Email()])


class CategoryForm(Form):
    category=StringField('category',[validators.Required(),validators.Length(min=1,max=20)])


class SubcategoryForm(Form):
    subcategory=StringField('subcategory',[validators.Required(),validators.Length(min=1,max=20)])


class GroupForm(Form):
     group=StringField('group',[validators.Required(),validators.Length(min=1,max=20)])



class AchievementForm(Form):
    level=BooleanField('level')
    altname=StringField('altname',[validators.Optional(),validators.Length(min=1,max=20)])
    description=TextAreaField('description',[validators.Required(),validators.Length(min=1,max=1000,message="Description cannot be longer than 1000 characters.")])
    requirements=TextAreaField('requirements',[validators.Required(),validators.Length(min=1,max=1000,message="Requirements cannot be longer than 1000 characters.")])
    points=DecimalField('points',[validators.Required(),validators.NumberRange(min=0,max=1000000)])
    title=StringField('title',[validators.Optional(),validators.Length(min=1,max=100)])


class CompanyForm(Form):
    company_name=StringField('company_name',[validators.Required(),validators.Length(min=1,max=64)])
    email=StringField('email',[validators.Required(),validators.Email(),validators.Length(min=1,max=64)])
    address=StringField('address',[validators.Required(),validators.Length(min=1,max=128)])
    city=StringField('city',[validators.Required(),validators.Length(min=1,max=32)])
    zipcode=StringField('zipcode',[validators.Required(),validators.Length(min=1,max=15)])
    tel=TelField('tel',[validators.Required()])
    url=URLField('url',[validators.Required()])
    short_desc=TextAreaField('short_desc',[validators.Required(),validators.Length(min=1,max=144,message="Description cannot be longer than 144 characters.")])
    description=TextAreaField('description',[validators.Required(),validators.Length(min=1,max=1000,message="Description cannot be longer than 1000 characters.")])
    



class AddWebsiteForm(Form):
    website_name=StringField('website_name',[validators.Required(),validators.Length(min=1,max=64)])
    url=URLField('url',validators=[DataRequired()])



class AddPromotionForm(Form):
    company=SelectField('company',[validators.Required()],coerce=int)
    url=URLField('url',validators=[DataRequired()])



class PostForm(Form):
    post=TextAreaField('post',[validators.Required(),validators.Length(min=1,max=1000,message="Post cannot be longer than 1000 characters.")])


class ReviewForm(Form):
    review=TextAreaField('review',[validators.Required()])
    rating=SelectField('rating',choices=[(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)],coerce=int)


class StoryForm(Form):
    title=StringField('title',[validators.Required(),validators.Length(min=1,max=100,message="Title cannot be longer than 100 characters.")])
    story=PageDownField('story',validators=[DataRequired()])
    



class CompanySearchForm(Form):
    company_name=StringField('company_name',[validators.Length(min=0,max=40),validators.Optional()])
    city=StringField('city',[validators.Length(min=0,max=20),validators.Optional()])
    rating_low=DecimalField('rating_low',[validators.NumberRange(min=0,max=10),validators.Optional()])
    rating_high=DecimalField('rating_high',[validators.NumberRange(min=0,max=10),validators.Optional()])
    distance=DecimalField('distance',[validators.NumberRange(min=0,max=100),validators.Optional()])


class UserSearchForm(Form):
    nickname=StringField('nickname',[validators.Length(min=0,max=40),validators.Optional()])
    achieved_low=DecimalField('achieved_low',[validators.NumberRange(min=0),validators.Optional()])
    achieved_high=DecimalField('achieved_high',[validators.NumberRange(min=0),validators.Optional()])
    points_low=DecimalField('points_low',[validators.NumberRange(min=0),validators.Optional()])
    points_high=DecimalField('points_high',[validators.NumberRange(min=0),validators.Optional()])
    followers_low=DecimalField('followers_low',[validators.NumberRange(min=0),validators.Optional()])
    followers_high=DecimalField('followers_high',[validators.NumberRange(min=0),validators.Optional()])


class StorySearchForm(Form):
    title=StringField('title',[validators.Length(min=0,max=100),validators.Optional()])
    date_min=DateField('date_min',[validators.Optional()])
    date_max=DateField('date_max',[validators.Optional()])



class AchievementSearchForm(Form):
    keyword=StringField('keyword',[validators.Length(min=0,max=50),validators.Optional()])
