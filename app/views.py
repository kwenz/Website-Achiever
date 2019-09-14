from flask import render_template, flash, redirect, session, url_for, g, request, jsonify,current_app
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.principal import Principal, Identity, AnonymousIdentity,identity_changed
from app import app, db, lm, pagedown, mkd, principals, admin_permission, owner_permission
from flask.ext.principal import identity_loaded, RoleNeed, UserNeed
from .models import User,Promoted, Achievement, Company, Post, Review, Promotion, Story, Base, Website, Owner, Group, Category, Subcategory, Interested
from datetime import datetime
from sqlalchemy.sql.expression import func
from .forms import AddWebsiteForm, EditForm, AccountCreationForm, LoginForm, PostForm, ReviewForm, StoryForm, CompanySearchForm,UserSearchForm, StorySearchForm, AchievementSearchForm, AchievementForm, CompanyForm, AddPromotionForm, CategoryForm, SubcategoryForm, GroupForm, EditOwnerForm
from .decorators import async
from operator import itemgetter
from hashlib import md5
from config import POSTS_PER_PAGE, STORIES_PER_PAGE,basedir,ALLOWED_EXTENSIONS, GOOGLE_API_KEY,GOOGLE_GEOCODE_URL, MAX_DISTANCE, ADMIN_USERNAME,ADMIN_PASSWORD
import os
import re
import math
import requests, json
from werkzeug import secure_filename







#HELPERS




def spherical_distance(lat_a,lon_a,lat_b,lon_b):

    lat_a=float(lat_a)
    lon_a=float(lon_a)
    lat_b=float(lat_b)
    lon_b=float(lon_b)

    del_lat=math.radians(abs(lat_a-lat_b))
    del_lon=math.radians(abs(lon_a-lon_b))
    lat_a=math.radians(lat_a)
    lat_b=math.radians(lat_b)
    Earth_radius=6371

    del_ang=2*math.asin(math.sqrt((math.sin(del_lat/2))**2+math.cos(lat_a)*math.cos(lat_b)*(math.sin(del_lon/2))**2))

    distance=Earth_radius*del_ang

    return distance


@app.before_request
def before_request():
    g.user=current_user
    if g.user.is_authenticated():
        g.user.last_seen=datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()



@lm.user_loader
def load_user(id):
    return Base.query.get(int(id))



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



@identity_loaded.connect_via(app)
def on_identity_loaded(sender,identity):

    identity.user=current_user

    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    if hasattr(current_user, 'role'):
        identity.provides.add(RoleNeed(current_user.role))



# RENDERS

@app.route('/',methods=['GET'])
@app.route('/index',methods=['GET'])
def index():

    return render_template('index.html')


@app.route('/index_comp',methods=['GET'])
def index_comp():

    return render_template('index_comp.html')



@app.route('/create_account',methods=['GET','POST'])
def create_account():

    form=AccountCreationForm()

    if request.method=='POST' and form.validate_on_submit():

        user=User.query.filter_by(username=form.username.data.lower()).first()

        if user==None:

            pwd=md5(form.password.data.encode('utf-8')).hexdigest()

            user_dir=os.path.join(basedir,'app/static/images/users/'+form.username.data.lower())

            os.makedirs(user_dir)

            nickname=User.make_unique_nickname(form.username.data)

            max_s=0

            for ach in Achievement.query.all():
                max_s+=ach.points

            new_user=User(username=form.username.data.lower(),nickname=nickname,password=pwd,email=form.email.data,title="None",total=0,max_score=max_s,max_desired=0,upload_dir=user_dir,lat=0,lon=0,role='user')

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user,remember=False)

            identity_changed.send(current_app._get_current_object(),identity=Identity(new_user.id))

            return redirect(url_for('list'))

        else:
            flash("Such username already exists.")

            return redirect(url_for('create_account'))

        

    return render_template('create_account.html',form=form)


@app.route('/create_owner_account',methods=['GET','POST'])
def create_owner_account():

    account_type=request.args.get('account')

    if account_type=='b':
        act='basic'
        avi=1
    elif account_type=='p':
        act='premium'
        avi=3
    elif account_type=='u':
        act='ultimate'
        avi=10
    else:
        return redirect(url_for('index'))

    form=AccountCreationForm()

    if request.method=='POST' and form.validate_on_submit():

        owner=Owner.query.filter_by(username=form.username.data.lower()).first()

        if owner==None:

            pwd=md5(form.password.data.encode('utf-8')).hexdigest()

            owner_dir=os.path.join(basedir,'app/static/images/owners/'+form.username.data.lower())

            os.makedirs(owner_dir)

            prom_dir=os.path.join(owner_dir,'promotions')
            comp_dir=os.path.join(owner_dir,'companies')

            os.makedirs(prom_dir)
            os.makedirs(comp_dir)

            new_owner=Owner(username=form.username.data.lower(),password=pwd,email=form.email.data,upload_dir=owner_dir,comp_upload_dir=comp_dir,prom_upload_dir=prom_dir,role='owner',account_type=act,special_companies_avi=avi,normal_companies_avi=0)

            db.session.add(new_owner)
            db.session.commit()

            login_user(new_owner,remember=False)

            identity_changed.send(current_app._get_current_object(),identity=Identity(new_owner.id))

            return redirect(url_for('owner',id=new_owner.id))

        else:
            flash("Such username already exists.")

            return redirect(url_for('create_owner_account'))

        

    return render_template('create_owner_account.html',form=form)



@app.route('/login',methods=['GET','POST'])
def login():
    
    if g.user is not None and g.user.is_authenticated() and g.user.role=='user':
        return redirect(url_for('user',username=g.user.username))

    form=LoginForm()


    if request.method=='POST' and form.validate_on_submit():

        pwd=md5(form.password.data.encode('utf-8')).hexdigest()


        if form.username.data.lower()==ADMIN_USERNAME and form.password.data==ADMIN_PASSWORD:

            admin=Base.query.filter_by(username=form.username.data.lower(),password=pwd).first()

            login_user(admin,remember=form.remember_me.data)

            identity_changed.send(current_app._get_current_object(),identity=Identity(admin.id))

            return redirect(url_for('user_list'))

        else:

            user=User.query.filter_by(username=form.username.data.lower(),password=pwd).first()

            owner=Owner.query.filter_by(username=form.username.data.lower(),password=pwd).first()

            if user is None and owner is None:
                flash('Invalid login. Please try again.')
                return redirect(url_for('login'))

            if owner is None:
                login_user(user,remember=form.remember_me.data)

                identity_changed.send(current_app._get_current_object(),identity=Identity(user.id))
                
                max_s=0
                for ach in Achievement.query.all():
                    max_s+=ach.points
                user.max_score=max_s
                db.session.add(user)
                db.session.commit()

                return redirect(request.args.get('next') or url_for('feed'))
            else:
                login_user(owner,remember=form.remember_me.data)

                identity_changed.send(current_app._get_current_object(),identity=Identity(owner.id))

                return redirect(request.args.get('next') or url_for('owner',id=owner.id))

    return render_template('login.html',form=form)



@login_required
@app.route('/todos',methods=['GET','POST'])
def todos():
    
    user=User.query.filter_by(id=g.user.id).first()

    if user==None:
        flash('User %s not found.'% username)
        return redirect(url_for('index'))


    categories=[category for category in Category.query.order_by('name').all() if category.in_todo(user)]


    max_score=float(user.max_score)
    points_tot=float(user.total)

    progress_pr=points_tot/max_score*100
    progress_pr="{:.2f}".format(progress_pr)

    max_score=str(int(max_score))
    points_tot=str(int(points_tot))
    
    return render_template('todos.html',progress=points_tot,total=max_score,progress_pr=progress_pr,categories=categories)



@login_required
@app.route('/list',methods=['GET','POST'])
def list():
    
    user=User.query.filter_by(id=g.user.id).first()

    if user==None:
        flash('User %s not found.'% username)
        return redirect(url_for('index'))



    categories=Category.query.order_by('name').all()

    max_score=float(user.max_score)
    points_tot=float(user.total)

    progress_pr=points_tot/max_score*100

    progress_pr="{:.2f}".format(progress_pr)

    max_score=str(int(max_score))
    points_tot=str(int(points_tot))
    
    return render_template('ach_list.html',categories=categories,progress=points_tot,total=max_score,progress_pr=progress_pr)
   


@login_required
@app.route('/achieved',methods=['GET','POST'])
def achieved():
    
    user=User.query.filter_by(id=g.user.id).first()

    if user==None:
        flash('User %s not found.'% username)
        return redirect(url_for('index'))


    categories=[category for category in Category.query.order_by('name').all() if category.in_achieved(user)]
    

    max_score=float(user.max_score)
    points_tot=float(user.total)

    progress_pr=points_tot/max_score*100
    progress_pr="{:.2f}".format(progress_pr)

    max_score=str(int(max_score))
    points_tot=str(int(points_tot))
    
    return render_template('achieved.html',progress=points_tot,total=max_score,progress_pr=progress_pr,k=0,categories=categories)



@login_required
@app.route('/ach_info',methods=['GET','POST'])
@app.route('/ach_info/<int:page>',methods=['GET','POST'])
def ach_info(page=1):

    form=PostForm()

    id=request.args.get('id')

    achievement=Achievement.query.filter_by(id=id).first()

    posts=achievement.comments.order_by(Post.timestamp.desc()).paginate(page,POSTS_PER_PAGE,False)


    if request.method=='POST' and form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), user=g.user,achievement=achievement)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('ach_info',id=id,page=1))


    return render_template('ach_info.html',achievement=achievement,posts=posts, form=form,k=0,Story=Story)



@login_required
@app.route('/ach_info_todo',methods=['GET'])
def ach_info_todo():


    id=request.args.get('id')

    achievement=Achievement.query.filter_by(id=id).first()

    companies=[]

    for company in achievement.companies_attached():
        if g.user.role=="user":
            if spherical_distance(g.user.lat,g.user.lon,company.lat,company.lon)<=MAX_DISTANCE:

                companies.append(company)
        else:
            companies.append(company)

    return render_template('ach_info_todo.html',achievement=achievement,companies=companies)



@login_required
@app.route('/comp_info',methods=['GET','POST'])
@app.route('/comp_info/<int:page>',methods=['GET','POST'])
def comp_info(page=1):



    form=ReviewForm()

    comp_id=request.args.get('id')
    
    company=Company.query.filter_by(id=comp_id).first()

    if request.method=="GET" and current_user.role=='user':
        if company.hits==None:
            company.hits=0

        company.hits+=1
        db.session.add(company)
        db.session.commit()

    reviews=company.reviews.order_by(Review.timestamp.desc()).paginate(page,POSTS_PER_PAGE,False)


    if request.method=='POST' and form.validate_on_submit():

        if company.rating:
            N=company.reviews.count()
            y=form.rating.data
            company.rating=company.rating*(N/(N+1))+y/(N+1)
        else:
            company.rating=form.rating.data

        review = Review(body=form.review.data, rating=form.rating.data, timestamp=datetime.utcnow(), user=g.user, company=company)
        
        db.session.add(review)
        db.session.add(company)
        db.session.commit()




        return redirect(url_for('comp_info',id=comp_id,page=1))



    return render_template('comp_info.html',company=company,key=GOOGLE_API_KEY,k=0,form=form,reviews=reviews)



@login_required
@app.route('/user/<username>',methods=['GET'])
def user(username):

    user=User.query.filter_by(username=username).first()


    rand_bucket_lst=user.todo.order_by(func.random()).limit(3)
    rand_achieved=user.achieved.order_by(func.random()).limit(3)


    max_score=float(user.max_score)
    points_tot=float(user.total)
    max_desired=float(user.max_desired)

    progress_pr=points_tot/max_score*100
    progress_pr="{:.2f}".format(progress_pr)

    if max_desired:
        progress_desired=points_tot/max_desired*100
        progress_desired="{:.2f}".format(progress_desired)
    else:
        progress_desired=0.00


    return render_template('user.html',user=user,progr=progress_pr,progr_des=progress_desired,Story=Story,Review=Review,rand_bucket_lst=rand_bucket_lst,rand_achieved=rand_achieved)



@login_required
@app.route('/edit',methods=['GET','POST'])
def edit():

    user=User.query.filter_by(username=g.user.username).first()

    form=EditForm()

    form.title.choices=[(ach.title,ach.title) for ach in user.achieved.order_by('title') if ach.title!=None]
    form.title.choices.insert(0,('None','No title'))

    if form.validate_on_submit() and request.method=='POST':

        if request.files['file']:
            file=request.files['file']

            if file and allowed_file(file.filename):
                filename=secure_filename(file.filename)
                file.save(os.path.join(user.upload_dir,filename))
                user.imgurl="images/users/"+user.username+'/'+filename
            else:
                flash('You have provided an incorrect file type.')
                return redirect(url_for('edit'))

        if user.about_me!=form.about_me.data:
            user.about_me=form.about_me.data

        if user.title!=form.title.data:
            user.title=form.title.data

        if user.nickname!=form.nickname.data:
            user.nickname=form.nickname.data


        db.session.add(user)
        db.session.commit()

        

        return redirect(url_for('user',username=user.username))
    else:

        form.about_me.data=user.about_me
        form.title.data=user.title
        form.nickname.data=user.nickname

    return render_template('edit.html',form=form)



@login_required
@app.route('/story',methods=['GET'])
def story():

    story_id=request.args.get('story_id')

    story=Story.query.filter_by(id=story_id).first()

    return render_template('story.html',story=story,Story=Story)



@login_required
@app.route('/edit_story',methods=['GET','POST'])
def edit_story():


    user=User.query.filter_by(username=g.user.username).first()

    story_id=request.args.get('story_id')
    ach_id=request.args.get('ach_id')

    if story_id:
        story=Story.query.filter_by(id=story_id).first()
    else:
        story=False

    if ach_id:
        ach=Achievement.query.filter_by(id=ach_id).first()
    else:
        ach=False

    form=StoryForm()
    

    if request.method=='POST' and form.validate_on_submit():

        if not story:
            story=Story(body=form.story.data,added=datetime.utcnow(),last_edited=datetime.utcnow(),title=form.title.data,user=g.user)

            if ach:
                story=story.describe(ach)

            
        else:
            if story.title!=form.title.data and story.body!=form.story.data:
                story.last_edited=datetime.utcnow()
            if story.body!=form.story.data:
                story.body=form.story.data
            if story.title!=form.title.data:
                story.title=form.title.data

        db.session.add(story)
        db.session.commit()

        return redirect(url_for('append_achs_story',id=story.id))

    else:
        if story:
            form.title.data=story.title
            form.story.data=story.body

    return render_template('edit_story.html',form=form)
       
    
@app.route('/append_achs_story/<int:id>',methods=['GET'])
@login_required
def append_achs_story(id):

    story=Story.query.filter_by(id=id).first()

    achs=g.user.achieved

    return render_template('append_achs_story.html',achs=achs,story=story)


@login_required
@app.route('/stories',methods=['GET'])
@app.route('/stories/<int:page>',methods=['GET'])
def stories(page=1):

    user_id=request.args.get('user_id')

    user=User.query.filter_by(id=user_id).first()

    stories=user.stories.order_by(Story.last_edited.desc()).paginate(page,STORIES_PER_PAGE,False)

    return render_template('stories.html',stories=stories,user=user,page=1)



@login_required
@app.route('/companies',methods=['GET'])
@app.route('/companies/<int:page>',methods=['GET'])
def companies(page=1):

    companies=Company.query.order_by(Company.rating.desc()).paginate(page,POSTS_PER_PAGE*2,False)


    return render_template('companies.html', companies=companies)



@login_required
@app.route('/feed',methods=['GET'])
def feed():

    posts=g.user.followed_posts(10)
    reviews=g.user.followed_reviews(10)
    stories=g.user.followed_stories(10)


    session['last_refresh']=datetime.utcnow()


    feed=[]

    if posts.count()>0:
        for post in posts:
            feed.append(post)

    if reviews.count()>0:
        for review in reviews:
            feed.append(review)

    if posts.count()>0:
        for story in stories:
            feed.append(story)

    
    feed=sorted(feed,key=lambda x:x.timestamp,reverse=True)

    feed=feed[:15]

    return render_template('feed.html',feed=feed,posts=posts,reviews=reviews,stories=stories)



@login_required
@app.route('/followers/<username>',methods=['GET'])
def followers(username):

    user=User.query.filter_by(username=username).first()

    return render_template('followers.html',user=user)



@login_required
@app.route('/followed',methods=['GET'])
def followed():

    return render_template('followed.html')



@login_required
@app.route('/search',methods=['GET'])
def search():

    comp_form=CompanySearchForm()
    user_form=UserSearchForm()
    story_form=StorySearchForm()
    ach_form=AchievementSearchForm()

    return render_template('search.html',comp_form=comp_form,user_form=user_form,story_form=story_form,ach_form=ach_form)



@app.route('/query_company',methods=['POST'])
def query_company():

    comp_form=CompanySearchForm(request.form)

    if comp_form.validate_on_submit():

        companies=Company.query.all()

        if comp_form.company_name.data:

            name_to_match=r"\w*"+comp_form.company_name.data.lower()+r"\w*"
 
            companies[:]=[company for company in companies if re.search(name_to_match,company.name.lower())]

        if comp_form.city.data:

            city_to_match="\w*"+comp_form.city.data.lower()+"\w*"

            companies[:]=[company for company in companies if re.search(city_to_match,company.city.lower())]

        if comp_form.rating_low.data:

            companies[:]=[company for company in companies if company.rating and float(company.rating)>=comp_form.rating_low.data]



        if comp_form.rating_high.data:

            companies[:]=[company for company in companies if company.rating and float(company.rating)<=comp_form.rating_high.data]
        

        if comp_form.distance.data:

            companies[:]=[company for company in companies if company.in_proximity(g.user.lat,g.user.lon,comp_form.distance.data)]


        return render_template('results.html',companies=companies,type='C')
    else:
        return redirect(url_for('search'))


@app.route('/query_story',methods=['POST'])
def query_story():

    story_form=StorySearchForm()

    if story_form.validate_on_submit():

        stories=Story.query.order_by(Story.last_edited.desc()).all()

        if story_form.title.data:

            title_to_match=r"\w*"+story_form.title.data.lower()+r"\w*"
 
            stories[:]=[story for story in stories if re.search(title_to_match,story.title.lower())]

        if story_form.date_min.data:

            stories[:]=[story for story in stories if story.last_edited.date()>=story_form.date_min.data]

        if story_form.date_max.data:

            stories[:]=[story for story in stories if story.last_edited.date()<=story_form.date_max.data]
        

        return render_template('results.html',stories=stories,type='S')
    else:
        return redirect(url_for('search'))



@app.route('/query_ach',methods=['POST'])
def query_ach():

    ach_form=AchievementSearchForm()

    if ach_form.validate_on_submit():

        achievements=Achievement.query.all()

        if ach_form.keyword.data:

            keyword_to_match=r"\w*"+ach_form.keyword.data.lower()+r"\w*"
 
            achievements[:]=[ach for ach in achievements if re.search(keyword_to_match,ach.group.subcategory.category.name.lower()) or re.search(keyword_to_match,ach.group.subcategory.name.lower()) or re.search(keyword_to_match,ach.group.name.lower())]

        

        return render_template('results.html',achievements=achievements,type='A')
    else:
        return redirect(url_for('search'))



@app.route('/query_user',methods=['POST'])
def query_user():

    user_form=UserSearchForm(request.form)

    if user_form.validate_on_submit():

        users=User.query.all()

        if user_form.nickname.data:

            name_to_match=r"\w*"+user_form.nickname.data.lower()+r"\w*"
 
            users[:]=[user for user in users if user.nickname and re.search(name_to_match,user.nickname.lower())]


        if user_form.achieved_low.data:

            users[:]=[user for user in users if user.achieved.count()>=user_form.achieved_low.data]


        if user_form.achieved_high.data:

            users[:]=[user for user in users if user.achieved.count()>=user_form.achieved_high.data]


        if user_form.points_low.data:

            users[:]=[user for user in users if user.total>=user_form.points_low.data]


        if user_form.points_high.data:

            users[:]=[user for user in users if user.total>=user_form.points_high.data]


        if user_form.followers_low.data:

            users[:]=[user for user in users if user.followers.count()>=user_form.followers_low.data]


        if user_form.followers_high.data:

            users[:]=[user for user in users if user.followers.count()>=user_form.followers_high.data]


        return render_template('results.html',users=users,type='U')
    else:
        return redirect(url_for('search'))



#Owner pages:

@app.route('/achs_for_owners',methods=['GET'])
@login_required
@owner_permission.require(http_exception=403)
def achs_for_owners():

    achs=Achievement.query.all()
    

    return render_template('achs_for_owners.html',achs=achs)


@app.route('/owner/<int:id>',methods=['GET'])
@login_required
@owner_permission.require(http_exception=403)
def owner(id):

    owner=Owner.query.filter_by(id=id).first()

    achs_count=owner.promoted_achs_count()+owner.interested_achs_count()

    for ach in owner.promoted_achs():
        if ach in owner.interested_achs():
            achs_count-=1

    if owner.promotions_count()>0:
        promos=[(promo,promo.company_clicks+promo.total_clicks()) for promo in owner.owned_promotions()]

        sorted_promos=[promo[0] for promo in sorted(promos,key=lambda tup: tup[1],reverse=True)]

     
        sorted_promos=sorted_promos[:min(3,owner.promotions_count())]

        return render_template('owner.html',owner=owner,sorted_promos=sorted_promos,achs_count=achs_count)
    else:

        return render_template('owner.html',owner=owner,achs_count=achs_count)

@login_required
@app.route('/owner_edit',methods=['GET','POST'])
@owner_permission.require(http_exception=403)
def owner_edit():

    owner=Owner.query.filter_by(username=g.user.username).first()

    form=EditOwnerForm()

    if form.validate_on_submit() and request.method=='POST':

        if request.files['file']:
            file=request.files['file']

            if file and allowed_file(file.filename):
                filename=secure_filename(file.filename)
                file.save(os.path.join(owner.upload_dir,filename))
                owner.imgurl="images/owners/"+owner.username+'/'+filename
            else:
                flash('You have provided an incorrect file type.')
                return redirect(url_for('owner_edit'))

        if owner.about_me!=form.about_me.data:
            owner.about_me=form.about_me.data

        if owner.nickname!=form.nickname.data:
            owner.nickname=form.nickname.data


        db.session.add(owner)
        db.session.commit()

        return redirect(url_for('owner',id=owner.id))
    else:

        form.about_me.data=owner.about_me
        form.nickname.data=owner.nickname

    return render_template('owner_edit.html',form=form)


@app.route('/new_company',methods=['POST','GET'])
@login_required
@owner_permission.require(http_exception=403)
def new_company():


    form=CompanyForm()

    if g.user.special_companies_avi+g.user.normal_companies_avi==0:
        return redirect(url_for('owner',id=g.user.id))

    if form.validate_on_submit():

        if request.files['file']:

            file=request.files['file']

            if file and allowed_file(file.filename):

                filename=secure_filename(file.filename)
                save_path=os.path.join(g.user.comp_upload_dir,filename)
                file.save(save_path)
                path=os.path.join(os.path.join('images/owners/',g.user.username)+'/companies/',filename)


                parameters={'address':form.address.data+','+form.city.data+','+form.zipcode.data,'key':GOOGLE_API_KEY}

                r=requests.get(GOOGLE_GEOCODE_URL,params=parameters)

                data=json.loads(r.text)

                lat=data['results'][0]['geometry']['location']['lat']
                lon=data['results'][0]['geometry']['location']['lng']


                if g.user.special_companies_avi:
                    
                    if g.user.account_type=='basic':
                        avi=10
                        spd=1
                        pr=3
                    elif g.user.account_type=='premium':
                        avi=15
                        spd=1
                        pr=4
                    elif g.user.account_type=='basic':
                        avi=20
                        spd=2
                        pr=5
                    g.user.special_companies_avi-=1

                else:
                    avi=5
                    spd=1
                    pr=1
                    g.user.normal_companies_avi-=1

                company=Company(name=form.company_name.data,email=form.email.data,address=form.address.data,city=form.city.data,zipcode=form.zipcode.data,tel=form.tel.data,imgurl=path,url=form.url.data,short_desc=form.short_desc.data,description=form.description.data,lat=lat,lon=lon,owner=g.user,hits=0,added=datetime.utcnow(),links_avi=avi,sponsored_avi=spd,promos_avi=pr)


                db.session.add(company)
                db.session.commit()


                return redirect(url_for('append_achs_comp',id=company.id))
            else:

                flash('You have provided an incorrect file type.')
                return redirect(url_for('new_company'))
                
        else:
            flash("You didn't provide any picture")
            return redirect(url_for('new_company'))

    return render_template('new_company.html',form=form)




@app.route('/edit_company/<int:id>',methods=['POST','GET'])
@login_required
@owner_permission.require(http_exception=403)
def edit_company(id):

    form=CompanyForm()

    comp=Company.query.filter_by(id=id).first()


    if form.validate_on_submit() and request.method=='POST':

        if request.files['file']:

            file=request.files['file']

            if file and allowed_file(file.filename):

                filename=secure_filename(file.filename)
                save_path=os.path.join(g.user.comp_upload_dir,filename)
                file.save(save_path)
                path=os.path.join(os.path.join('images/owners/',g.user.username)+'/companies/',filename)

                comp.imgurl=path
            else:

                flash('You have provided an incorrect file type.')
                return redirect(url_for('edit_company',id=id))

        if comp.address!=form.address.data or comp.city!=form.city.data or comp.zipcode!=form.zipcode.data:
                
            parameters={'address':form.address.data+','+form.city.data+','+form.zipcode.data,'key':GOOGLE_API_KEY}

            r=requests.get(GOOGLE_GEOCODE_URL,params=parameters)

            data=json.loads(r.text)

            lat=data['results'][0]['geometry']['location']['lat']
            lon=data['results'][0]['geometry']['location']['lng']

            comp.lat=lat
            comp.lon=lon

        if comp.name!=form.company_name.data:
            comp.name=form.company_name.data

        if comp.email!=form.email.data:
            comp.email=form.email.data

        if comp.address!=form.address.data:
            comp.address=form.address.data

        if comp.city!=form.city.data:
            comp.city=form.city.data

        if comp.zipcode!=form.zipcode.data:
            comp.zipcode=form.zipcode.data

        if comp.tel!=form.tel.data:
            comp.tel=form.tel.data

        if comp.url!=form.url.data:
            comp.url=form.url.data

        if comp.description!=form.description.data:
            comp.description=form.description.data   

        if comp.short_desc!=form.short_desc.data:
            comp.short_desc=form.short_desc.data

        db.session.add(comp)
        db.session.commit()


        return redirect(url_for('comp_info',id=id))

    else:

        form.company_name.data=comp.name
        form.email.data=comp.email
        form.address.data=comp.address
        form.city.data=comp.city
        form.zipcode.data=comp.zipcode
        form.tel.data=comp.tel
        form.url.data=comp.url
        form.description.data=comp.description
        form.short_desc.data=comp.short_desc


    return render_template('edit_company.html',form=form,comp=comp)



@app.route('/append_achs_comp/<int:id>',methods=['GET'])
@login_required
@owner_permission.require(http_exception=403)
def append_achs_comp(id):

    company=Company.query.filter_by(id=id).first()

    achs=Achievement.query.all()

    return render_template('append_achs_comp.html',achs=achs,company=company)



@app.route('/owned_companies',methods=['GET'])
@login_required
@owner_permission.require(http_exception=403)
def owned_companies():

    # for company in g.user.companies:
    #     if not company.added:
    #         company.added=datetime.utcnow()

    #         db.session.add(company)
    #         db.session.commit()

    return render_template('owned_companies.html')


@app.route('/owned_promotions',methods=['GET'])
@login_required
@owner_permission.require(http_exception=403)
def owned_promotions():

    return render_template('owned_promotions.html')



@app.route('/new_promotion',methods=['POST','GET'])
@login_required
@owner_permission.require(http_exception=403)
def new_promotion():

    tot_proms=0
    for company in g.user.companies:
        tot_proms+=company.promos_avi

    if tot_proms==0:
        return redirect(url_for('owner',id=g.user.id))


    form=AddPromotionForm()

    form.company.choices=[(company.id,company.name) for company in g.user.companies.order_by('name') if company.promos_avi]



    if form.validate_on_submit():

        if request.files['file']:

            file=request.files['file']

            if file and allowed_file(file.filename):

                filename=secure_filename(file.filename)
                save_path=os.path.join(g.user.prom_upload_dir,filename)
                file.save(save_path)
                path=os.path.join(os.path.join('images/owners/',g.user.username)+'/promotions/',filename)

                if g.user.account_type=='basic':
                    avi=3
                elif g.user.account_type=='premium':
                    avi=4
                elif g.user.account_type=='ultimate':
                    avi=5
                    
                company=Company.query.filter_by(id=form.company.data).first()

                company.promos_avi-=1

                promo=Promotion(imgurl=path,url=form.url.data,company=company,added=datetime.utcnow(),company_clicks=0,links_avi=avi)

                db.session.add(promo)
                db.session.add(company)
                db.session.commit()

                return redirect(url_for('append_achs_prom',id=promo.id))

            else:

                flash('You have provided an incorrect file type.')
                return redirect(url_for('new_promotion'))
                
        else:
            flash("You didn't provide any picture")
            return redirect(url_for('new_promotion'))
            

    return render_template('new_promotion.html',form=form)



@app.route('/append_achs_prom/<int:id>',methods=['GET'])
@login_required
@owner_permission.require(http_exception=403)
def append_achs_prom(id):

    promotion=Promotion.query.filter_by(id=id).first()

    achs=Achievement.query.all()

    return render_template('append_achs_prom.html',achs=achs,promotion=promotion)


@app.route('/shop',methods=['GET','POST'])
@login_required
@owner_permission.require(http_exception=403)
def shop():

    if request.method=='POST':

        g.user.normal_companies_avi+=int(request.form['add_comp'])


        for company in g.user.companies:

            company.promos_avi+=int(request.form['c_prom'+str(company.id)])
            company.links_avi+=int(request.form['c_link'+str(company.id)])
            company.sponsored_avi+=int(request.form['c_spon'+str(company.id)])

            db.session.add(company)

        for promotion in g.user.owned_promotions():

            promotion.links_avi+=int(request.form['pr_link'+str(promotion.id)])
            db.session.add(promotion)

        db.session.add(g.user)
        db.session.commit()

        return redirect(url_for('owner',id=g.user.id))


    return render_template('shop.html')



#Admin only pages:

@app.route('/user_list')
@login_required
@admin_permission.require(http_exception=403)
def user_list():

    users=User.query.all()

    return render_template('user_list.html',users=users)


@app.route('/company_list')
@login_required
@admin_permission.require(http_exception=403)
def company_list():

    companies=Company.query.all()

    return render_template('company_list.html',companies=companies)



@app.route('/promo_list')
@login_required
@admin_permission.require(http_exception=403)
def promo_list():

    promos=Promotion.query.all()

    return render_template('promo_list.html',promos=promos)


@app.route('/website_list')
@login_required
@admin_permission.require(http_exception=403)
def website_list():

    webs=Website.query.all()

    return render_template('website_list.html',webs=webs)



@app.route('/achievement_list')
@login_required
@admin_permission.require(http_exception=403)
def achievement_list():

    achs=Achievement.query.all()

    return render_template('achievement_list.html',achs=achs)



@app.route('/new_website',methods=['POST','GET'])
@login_required
@admin_permission.require(http_exception=403)
def new_website():


    form=AddWebsiteForm()


    if form.validate_on_submit():

        if request.files['file']:

            file=request.files['file']

            if file and allowed_file(file.filename):

                filename=secure_filename(file.filename)
                save_path=os.path.join(basedir,'app/static/images/websites/')
                file.save(os.path.join(save_path,filename))
                path=os.path.join('images/websites/',filename)

                web=Website(imgurl=path,url=form.url.data,name=form.website_name.data)

                db.session.add(web)
                db.session.commit()

                return redirect(url_for('append_achs_web',id=web.id))
            else:

                flash('You have provided an incorrect file type.')
                return redirect(url_for('new_website'))
                
        else:
            flash("You didn't provide any picture")
            return redirect(url_for('new_website'))

    return render_template('new_website.html',form=form)



@app.route('/append_achs_web/<int:id>',methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def append_achs_web(id):

    web=Website.query.filter_by(id=id).first()

    achs=Achievement.query.all()

    return render_template('append_achs_web.html',achs=achs,web=web)


@app.route('/append_achs_req/<int:id>',methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def append_achs_req(id):

    ach=Achievement.query.filter_by(id=id).first()

    helper=[]
    unavi=set(ach.required_tree(helper))

    achievements=Achievement.query.all()

    return render_template('append_achs_req.html',achievements=achievements,ach=ach,unavi=unavi)



@app.route('/categories')
@login_required
@admin_permission.require(http_exception=403)
def categories():
    
    cats=Category.query.all()

    return render_template('categories.html',cats=cats)


@app.route('/subcategories',methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def subcategories():

    cat_id=request.args.get('cat_id')


    cat=Category.query.filter_by(id=cat_id).first()

    subs=cat.subcategories.all()

    return render_template('subcategories.html',cat=cat,subs=subs)



@app.route('/groups',methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def groups():

    sub_id=request.args.get('sub_id')

    sub=Subcategory.query.filter_by(id=sub_id).first()
    cat=sub.category

    grps=sub.groups.all()

    return render_template('groups.html',cat=cat,sub=sub,grps=grps)


@app.route('/achievs',methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def achievs():

    grp_id=request.args.get('grp_id')

    grp=Group.query.filter_by(id=grp_id).first()
    sub=grp.subcategory
    cat=sub.category

    achs=grp.achievements.all()

    return render_template('achievs.html',cat=cat,sub=sub,grp=grp,achs=achs)


@app.route('/edit_category',methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403)
def edit_category():


    cat_id=request.args.get('cat_id')

    if cat_id==None:
        cat=Category(name='')
    else:
        cat=Category.query.filter_by(id=cat_id).first()

    form=CategoryForm()

    if form.validate_on_submit() and request.method=='POST':

        if cat.name!=form.category.data:
            cat.name=form.category.data

        cat.adder=g.user.username
        cat.added=datetime.utcnow()

        db.session.add(cat)
        db.session.commit()


        return redirect(url_for('categories'))
    else:

        form.category.data=cat.name

    return render_template('edit_category.html',form=form)


@app.route('/edit_subcategory',methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403)
def edit_subcategory():

    cat_id=request.args.get('cat_id')
    sub_id=request.args.get('sub_id')

    cat=Category.query.filter_by(id=cat_id).first()
    
    if sub_id==None:
        sub=Subcategory(name='')
        sub.category=cat
    else:
        sub=Subcategory.query.filter_by(id=sub_id).first()

    form=SubcategoryForm()

    if form.validate_on_submit() and request.method=='POST':

        if sub.name!=form.subcategory.data:
            sub.name=form.subcategory.data

        sub.adder=g.user.username
        sub.added=datetime.utcnow()

        db.session.add(sub)
        db.session.commit()


        return redirect(url_for('subcategories',cat_id=cat_id))
    else:

        form.subcategory.data=sub.name

    return render_template('edit_subcategory.html',form=form)



@app.route('/edit_group',methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403)
def edit_group():

    grp_id=request.args.get('grp_id')
    sub_id=request.args.get('sub_id')
    
    sub=Subcategory.query.filter_by(id=sub_id).first()

    if grp_id==None:
        grp=Group(name='')
        grp.subcategory=sub
    else:
        grp=Group.query.filter_by(id=grp_id).first()

    form=GroupForm()

    if form.validate_on_submit() and request.method=='POST':

        if grp.name!=form.group.data:
            grp.name=form.group.data

        grp.adder=g.user.username
        grp.added=datetime.utcnow()

        db.session.add(grp)
        db.session.commit()


        return redirect(url_for('groups',sub_id=sub_id))
    else:

        form.group.data=grp.name

    return render_template('edit_group.html',form=form)


@app.route('/edit_achievement',methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403)
def edit_achievement():

    ach_id=request.args.get('ach_id')
    grp_id=request.args.get('grp_id')
    
    grp=Group.query.filter_by(id=grp_id).first()

    if grp.achievements.count()==0:
        multi=True
    elif grp.achievements.count()==1:
        if ach_id==None:
            multi=False
        else:
            multi=True
    else:
        multi=False


    if ach_id==None:

        ach=Achievement()
        ach.group=grp

    else:
        ach=Achievement.query.filter_by(id=ach_id).first()



    form=AchievementForm()

    if form.validate_on_submit():

        if request.files['file']:

            file=request.files['file']

            if file and allowed_file(file.filename):

                filename=secure_filename(file.filename)
                save_path=os.path.join(basedir,'app/static/images/achievements/')
                file.save(os.path.join(save_path,filename))
                path=os.path.join('images/achievements/',filename)
                
                ach.imgurl=path
            else:
                flash("You provided incorrect file format.")
                return redirect(url_for('edit_achievement',ach_id=ach.id,grp_id=grp.id))
        else:
            if not ach.imgurl:
                flash("You didn't provide an image.")
                return redirect(url_for('edit_achievement',ach_id=ach.id,grp_id=grp.id))
            
        if ach.altname!=form.altname.data:
            ach.altname=form.altname.data

        if ach.description!=form.description.data:
            ach.description=form.description.data

        if ach.requirements!=form.requirements.data:
            ach.requirements=form.requirements.data

        if ach.points!=int(form.points.data):
            ach.points=int(form.points.data)

        if form.title.data and ach.title!=form.title.data:
            ach.title=form.title.data


        if multi:
            if form.level.data and ach.level==None:
                ach.level=1
            elif ach.level==1 and form.level.data==False:
                ach.level=None
        else:
            ach.level=grp.achievements.count()
            

        ach.adder=g.user.username
        ach.added=datetime.utcnow()


        db.session.add(ach)
        db.session.commit()

        return redirect(url_for('achievs',grp_id=grp_id))


    else:

        form.altname.data=ach.altname
        if ach.level==1:
            form.level.data=True
        if ach.points:
            form.points.data=int(ach.points)
        else:
            form.points.data=0
        form.title.data=ach.title
        form.description.data=ach.description
        form.requirements.data=ach.requirements
        # form.process()


    return render_template('edit_achievement.html',form=form,multi=multi,imgurl=ach.imgurl)




#ERROR HANDLERS:


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(405)
def wrong_method(e):

    return redirect(request.referrer), 405







# FUNCTIONS:


@app.route('/logout')
@login_required
def logout():

    logout_user()

    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    
    identity_changed.send(current_app._get_current_object(),identity=AnonymousIdentity())

    return redirect(url_for('index'))





@app.route('/help_ach',methods=['POST'])
def help_ach():

    ach_id=request.form['ach_id']
    web_id=request.form['web_id']

    achievement=Achievement.query.filter_by(id=ach_id).first()
    web=Website.query.filter_by(id=web_id).first()

    w=web.help(achievement)

    if w is not None:
        db.session.add(w)
        db.session.commit()

    return jsonify({})


@app.route('/stop_helping',methods=['POST'])
def stop_help_ach():

    ach_id=request.form['ach_id']
    web_id=request.form['web_id']

    achievement=Achievement.query.filter_by(id=ach_id).first()
    web=Website.query.filter_by(id=web_id).first()

    w=web.stop_helping(achievement)

    if w is not None:
        db.session.add(w)
        db.session.commit()

    return jsonify({})



@app.route('/allow_ach',methods=['POST'])
def allow_ach():

    ach_id=request.form['ach_id']
    req_id=request.form['req_id']

    achievement=Achievement.query.filter_by(id=ach_id).first()
    req=Achievement.query.filter_by(id=req_id).first()

    a=req.allow(achievement)

    if a is not None:
        db.session.add(a)
        db.session.commit()

    return jsonify({})


@app.route('/stop_allowing_ach',methods=['POST'])
def stop_allowing_ach():

    ach_id=request.form['ach_id']
    req_id=request.form['req_id']

    achievement=Achievement.query.filter_by(id=ach_id).first()
    req=Achievement.query.filter_by(id=req_id).first()

    a=req.stop_allowing(achievement)

    if a is not None:
        db.session.add(a)
        db.session.commit()

    return jsonify({})



@app.route('/desc_ach',methods=['POST'])
def desc_ach():

    ach_id=request.form['ach_id']
    story_id=request.form['story_id']

    achievement=Achievement.query.filter_by(id=ach_id).first()
    story=Story.query.filter_by(id=story_id).first()

    unlock=False


    s=story.describe(achievement)

    if s is not None:
        db.session.add(s)
        db.session.commit()

    if story.described.count()>0:
        unlock=True

    return jsonify({'unlock':unlock})


@app.route('/stop_desc_ach',methods=['POST'])
def stop_desc_ach():

    ach_id=request.form['ach_id']
    story_id=request.form['story_id']

    achievement=Achievement.query.filter_by(id=ach_id).first()
    story=Story.query.filter_by(id=story_id).first()

    s=story.stop_describing(achievement)

    if s is not None:
        db.session.add(s)
        db.session.commit()

    lock=False

    if story.described.count()==0:
        lock=True

    return jsonify({'lock':lock})



@app.route('/promote_ach',methods=['POST'])
def promote_ach():

    ach_id=request.form['ach_id']
    promo_id=request.form['promo_id']

    achievement=Achievement.query.filter_by(id=ach_id).first()
    promo=Promotion.query.filter_by(id=promo_id).first()

    p=promo.promote(achievement)

    if p is not None:
        db.session.add(p)
        db.session.commit()

        return jsonify({'res':1,'avi':promo.links_avi})
    else:
        return jsonify({'res':0})



@app.route('/stop_promote_ach',methods=['POST'])
def stop_promote_ach():

    ach_id=request.form['ach_id']
    promo_id=request.form['promo_id']

    achievement=Achievement.query.filter_by(id=ach_id).first()
    promo=Promotion.query.filter_by(id=promo_id).first()

    p=promo.stop_promoting(achievement)

    if p is not None:
        db.session.add(p)
        db.session.commit()
    
    

    return jsonify({'avi':promo.links_avi})



@app.route('/get_inter',methods=['POST'])
def get_inter():

    ach_id=request.form['ach_id']
    company_id=request.form['company_id']

    achievement=Achievement.query.filter_by(id=ach_id).first()
    company=Company.query.filter_by(id=company_id).first()

    c=company.get_interested(achievement)

    if c is not None:
        db.session.add(c)
        db.session.commit()

        return jsonify({'res':1,'avi':company.links_avi})
    else:
        return jsonify({'res':0})


@app.route('/not_inter',methods=['POST'])
def not_inter():

    ach_id=request.form['ach_id']
    company_id=request.form['company_id']

    achievement=Achievement.query.filter_by(id=ach_id).first()
    company=Company.query.filter_by(id=company_id).first()

    c=company.not_interested(achievement)

    if c is not None:
        db.session.add(c)
        db.session.commit()

    return jsonify({'avi':company.links_avi,'spon':company.sponsored_avi})


@app.route('/sponsor',methods=['POST'])
def sponsor():

    company_id=request.form['company_id']
    ach_id=request.form['ach_id']


    intd=Interested.query.filter_by(company_id=company_id,achievement_id=ach_id).first()

    if intd is None:
        return jsonify({'res':0,'err':1})

    comp=Company.query.filter_by(id=company_id).first()

    if comp.sponsored_avi:
        intd.sponsored=True
        comp.sponsored_avi-=1

        db.session.add(intd)
        db.session.add(comp)
        db.session.commit()

        return jsonify({'res':1,'avi':comp.sponsored_avi})

    else:
        return jsonify({'res':0,'err':0})


@app.route('/not_sponsor',methods=['POST'])
def not_sponsor():

    company_id=request.form['company_id']
    ach_id=request.form['ach_id']


    intd=Interested.query.filter_by(company_id=company_id,achievement_id=ach_id).first()
    if intd is None:
        return jsonify({'res':0})

    comp=Company.query.filter_by(id=company_id).first()

    intd.sponsored=False
    comp.sponsored_avi+=1

    db.session.add(intd)
    db.session.add(comp)
    db.session.commit()

    return jsonify({'res':1,'avi':comp.sponsored_avi})





@app.route('/remove_web',methods=['POST'])
def remove_web():

    web_id=request.form['web_id']
    web=Website.query.filter_by(id=web_id).first()

    path=os.path.join(basedir,'app/static/'+web.imgurl)
    
    os.remove(path)

    db.session.delete(web)
    db.session.commit()

    return jsonify({})



@app.route('/del_comp',methods=['POST'])
def del_comp():

    company_id=request.form['company_id']
    comp=Company.query.filter_by(id=company_id).first()

    if comp.imgurl:
        try:
            path=os.path.join(basedir,'app/static/'+comp.imgurl)   
            os.remove(path)
        except FileNotFoundError:
            pass

    for promo in comp.promotions:
        
        if promo.imgurl:
            try:
                pr_path=os.path.join(basedir,'app/static/'+promo.imgurl)
                os.remove(pr_path)
            except FileNotFoundError:
                pass

        db.session.delete(promo)


    db.session.delete(comp)
    db.session.commit()

    return jsonify({})


@app.route('/remove_company',methods=['GET'])
def remove_company():

    company_id=request.args.get('company_id')
    comp=Company.query.filter_by(id=company_id).first()

    if comp.imgurl:
        try:
            path=os.path.join(basedir,'app/static/'+comp.imgurl)   
            os.remove(path)
        except FileNotFoundError:
            pass

    for promo in comp.promotions:
        
        if promo.imgurl:
            try:
                pr_path=os.path.join(basedir,'app/static/'+promo.imgurl)
                os.remove(pr_path)
            except FileNotFoundError:
                pass

        db.session.delete(promo)


    db.session.delete(comp)
    db.session.commit()

    return redirect(url_for('owned_companies'))


@app.route('/del_promo',methods=['POST'])
def del_promo():

    promo_id=request.form['promo_id']
    prom=Promotion.query.filter_by(id=promo_id).first()
    prom.company.promos_avi+=1

    if prom.imgurl:
        try:
            path=os.path.join(basedir,'app/static/'+prom.imgurl)
            os.remove(path)
        except FileNotFoundError:
            pass
   

    db.session.delete(prom)
    db.session.commit()

    return jsonify({})





@app.route('/delete_achie',methods=['POST'])
def delete_achie():

    ach_id=request.form['ach_id']
    ach=Achievement.query.filter_by(id=ach_id).first()

    users=User.query.all()
    companies=Company.query.all()
    promotions=Promotion.query.all()
    websites=Website.query.all()
    us=[]
    co=[]
    pr=[]
    we=[]

    for user in users:
        u.append(user.remove_ach(ach))

    for company in companies:
        c.append(company.not_interested(ach))

    for promo in promotions:
        p.append(promo.stop_promoting(ach))

    for web in websites:
        w.append(web.stop_helping(ach))

    

    for u in us:
        if u is not None:
            db.session.add(u)
    for c in co:
        if c is not None:
            db.session.add(c)
    for p in pr:
        if p is not None:
            db.session.add(p)
    for w in we:
        if w is not None:
            db.session.add(w)


    path=os.path.join(basedir,'app/static/'+ach.imgurl)
    
    os.remove(path)

    db.session.delete(ach)
    db.session.commit()

    return jsonify({})



@app.route('/delete_category',methods=['POST'])
def delete_category():

    cat_id=request.form['cat_id']
    cat=Category.query.filter_by(id=cat_id).first()

    db.session.delete(cat)
    db.session.commit()

    return jsonify({})


@app.route('/delete_subcategory',methods=['POST'])
def delete_subcategory():

    sub_id=request.form['sub_id']
    sub=Subcategory.query.filter_by(id=sub_id).first()

    db.session.delete(sub)
    db.session.commit()

    return jsonify({})


@app.route('/delete_group',methods=['POST'])
def delete_group():

    grp_id=request.form['grp_id']
    grp=Group.query.filter_by(id=grp_id).first()

    db.session.delete(grp)
    db.session.commit()

    return jsonify({})




@app.route('/add_achievement',methods=['POST'])
def add_achievement():

    ida=request.form['id']


    achiev=Achievement.query.filter_by(id=ida).first()

    if achiev not in g.user.todo and achiev.required.count()>0:
        lock=[ach.id for ach in achiev.required]
    else:
        lock=0

    if achiev is not None:
        new_ach=g.user.add_ach(achiev)
        if new_ach is not None:
            db.session.add(new_ach)
            db.session.add(g.user)
            db.session.commit()
    

    progr=float(g.user.total)/float(g.user.max_score)*100
    progr_des=float(g.user.total)/float(g.user.max_desired)*100
    progr_str="{:.1f}".format(progr)
    progr_des_str="{:.1f}".format(progr_des)
    total=str(g.user.total)


    if achiev.allowed.count()>0:
        unlock=[ach.id for ach in achiev.allowed if ach.all_required(g.user)]
        if len(unlock)==0:
            unlock=0
    else:
        unlock=0

    

    return jsonify({'pr':progr,'pr_des':progr_des,'pr_str':progr_str,'pr_des_str':progr_des_str,'ach_count':g.user.achieved.count(),'tot':total,'des':g.user.max_desired,'unlock':unlock,'lock':lock})



@app.route('/remove_achievement',methods=['POST'])
def remove_achievement():

    ida=request.form['id']

    achiev=Achievement.query.filter_by(id=ida).first()

    if achiev in g.user.achieved and achiev.allowed.count()>0:
        lock=[ach.id for ach in achiev.allowed if ach.all_required(g.user)]
        if len(lock)==0:
            lock=0
    else:
        lock=0

    if achiev is not None:
        new_ach=g.user.remove_ach(achiev)
        if new_ach is not None:
            db.session.add(g.user)
            db.session.add(new_ach)
            db.session.commit()


    progr=float(g.user.total)/float(g.user.max_score)*100
    progr_des=float(g.user.total)/float(g.user.max_desired)*100
    progr_str="{:.1f}".format(progr)
    progr_des_str="{:.1f}".format(progr_des)
    total=str(g.user.total)

    if achiev.required.count()>0:
        unlock=[ach.id for ach in achiev.required if not ach.any_allowed(g.user)]
        if len(unlock)==0:
            unlock=0
    else:
        unlock=0

    return jsonify({'pr':progr,'pr_des':progr_des,'pr_str':progr_str,'pr_des_str':progr_des_str,'ach_count':g.user.achieved.count(),'tot':total,'des':g.user.max_desired,'unlock':unlock,'lock':lock})




@app.route('/add_todo',methods=['POST'])
def add_todo():

    ida=request.form['id']

    achiev=Achievement.query.filter_by(id=ida).first()

    if achiev in g.user.achieved:
        avd=1
        if achiev.allowed.count()>0:
            lock=[ach.id for ach in achiev.allowed if ach.all_required(g.user)]
            if len(lock)==0:
                lock=0
        else:
            lock=0
    else:
        avd=0
        if achiev.required.count()>0:
            lock=[ach.id for ach in achiev.required]
            if len(lock)==0:
                lock=0
        else:
            lock=0



    if achiev is not None:
        new_ach=g.user.add_to_list(achiev)
        if new_ach is not None:
            db.session.add(g.user)
            db.session.add(new_ach)
            db.session.commit()
    
    progr=float(g.user.total)/float(g.user.max_score)*100
    progr_des=float(g.user.total)/float(g.user.max_desired)*100
    progr_str="{:.1f}".format(progr)
    progr_des_str="{:.1f}".format(progr_des)
    total=str(g.user.total)

    return jsonify({'pr':progr,'pr_des':progr_des,'pr_str':progr_str,'pr_des_str':progr_des_str,'ach_count':g.user.achieved.count(),'tot':total,'des':g.user.max_desired,'lock':lock,'avd':avd})





@app.route('/add_location',methods=['POST'])
def add_location():

    latitude=request.form['lat']
    longitude=request.form['lon']

    g.user.lat=latitude
    g.user.lon=longitude

    db.session.add(g.user)
    db.session.commit()


    return jsonify({})



@app.route('/geocode',methods=['POST'])
def geocode():

    ad=request.form['address']
    zipcode=request.form['zipcode']
    city=request.form['city']
    name=request.form['name']
    email=request.form['email']

    company=Company.query.filter_by(name=name,email=email).first()

    parameters={'address':ad+','+city+','+zipcode,'key':GOOGLE_API_KEY}

    r=requests.get(GOOGLE_GEOCODE_URL,params=parameters)

    data=json.loads(r.text)

    company.lat=data['results'][0]['geometry']['location']['lat']
    company.lon=data['results'][0]['geometry']['location']['lng']

    db.session.add(company)
    db.session.commit()


    return jsonify({'lat':company.lat,'lon':company.lon})



@app.route('/dist_to_comp',methods=['POST'])
def dist_to_comp():
    u_lat=request.form['u_lat']
    u_lon=request.form['u_lon']
    c_lat=request.form['c_lat']
    c_lon=request.form['c_lon']

    dist=spherical_distance(u_lat,u_lon,c_lat,c_lon)

    return jsonify({'dist':dist})





@app.route('/delete_rev',methods=['GET'])
def delete_rev():

    rev_id=request.args.get('rev_id')

    review=Review.query.filter_by(id=rev_id).first()

    company=review.company

    if company.reviews.count()>1:
        N=company.reviews.count()
        company.rating=company.rating*N/(N-1)-review.rating/(N-1)
    else:
        company.rating=0

    db.session.add(company)
    db.session.delete(review)
    db.session.commit()

    return redirect(url_for('comp_info',id=company.id,page=1))




@app.route('/delete_post',methods=['GET'])
def delete_post():

    post_id=request.args.get('post_id')

    post=Post.query.filter_by(id=post_id).first()

    achievement=post.achievement
    
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('ach_info',id=achievement.id,page=1))




@app.route('/delete_story',methods=['GET'])
def delete_story():

    story_id=request.args.get('story_id')

    story=Story.query.filter_by(id=story_id).first()

    
    db.session.delete(story)
    db.session.commit()


    return redirect(url_for('stories',user_id=g.user.id))






@app.route('/follow',methods=['POST'])
def follow():

    user_id=request.form['user_id']

    user=User.query.filter_by(id=user_id).first()

    u=g.user.follow(user)

    if u is None:
        flash("Cannot follow "+user.nickname+'.')
        return redirect(url_for('user',username=user.username))

    db.session.add(u)
    db.session.commit()


    return jsonify({})



@app.route('/unfollow',methods=['POST'])
def unfollow():

    user_id=request.form['user_id']

    user=User.query.filter_by(id=user_id).first()

    u=g.user.unfollow(user)

    db.session.add(u)
    db.session.commit()


    return jsonify({})






@app.route('/refresh_feed',methods=['POST','GET'])
def refresh_feed():

    posts=g.user.followed_posts(10)
    reviews=g.user.followed_reviews(10)
    stories=g.user.followed_stories(10)

    
    refreshed_feed=[]

    for post in posts:
        if post.timestamp>session['last_refresh']:
            refreshed_feed.append(post)

    for review in reviews:
        if review.timestamp>session['last_refresh']:
            refreshed_feed.append(review)

    for story in stories:
        if story.timestamp>session['last_refresh']:
            refreshed_feed.append(story)

    session['last_refresh']=datetime.utcnow()

    if len(refreshed_feed)>0:
        refreshed_feed=sorted(refreshed_feed,key=lambda x:x.timestamp)

        feed_dict={}

        for n in range(0,len(refreshed_feed)):
            if refreshed_feed[n] in posts:
                r=render_template('post_feed.html',post=refreshed_feed[n])
                feed_dict[n]=['post',r]
            elif refreshed_feed[n] in reviews:
                r=render_template('review_feed.html',review=refreshed_feed[n])
                feed_dict[n]=['review',r]
            else:
                r=render_template('story_feed.html',story=refreshed_feed[n])
                feed_dict[n]=['story',r]


        return jsonify(feed_dict)
    else:
        return jsonify({})


@app.route('/add_click',methods=["POST"])
def add_click():

    pr_id=request.form['pr_id']
    ach_id=request.form['ach_id']

    if ach_id!='C':
        promo=Promoted.query.filter_by(promotion_id=pr_id,achievement_id=ach_id).first()

        if promo.clicks==None:
            promo.clicks=0
        promo.clicks=promo.clicks+1

        
    else:

        promo=Promotion.query.filter_by(id=pr_id).first()
        
        if promo.company_clicks==None:
            promo.company_clicks=0

        promo.company_clicks+=1

    db.session.add(promo)
    db.session.commit()

    return jsonify({})












