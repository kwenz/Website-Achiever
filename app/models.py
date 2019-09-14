from app import db
from hashlib import md5
from datetime import datetime
import math 
from sqlalchemy.sql.expression import func


#to avoid circular import

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




achies=db.Table('achieved',
    db.Column('user_id',db.Integer,db.ForeignKey('user.id')),
    db.Column('achievement_id',db.Integer,db.ForeignKey('achievement.id')))

todos=db.Table('todo',
    db.Column('user_id',db.Integer,db.ForeignKey('user.id')),
    db.Column('achievement_id',db.Integer,db.ForeignKey('achievement.id')))

helped=db.Table('helped',
    db.Column('website_id',db.Integer,db.ForeignKey('website.id')),
    db.Column('achievement_id',db.Integer,db.ForeignKey('achievement.id')))

followers=db.Table('followers',
    db.Column('who_follows_id',db.Integer,db.ForeignKey('user.id')),
    db.Column('who_is_followed_id',db.Integer,db.ForeignKey('user.id')))

described=db.Table('described',
    db.Column('story_id',db.Integer,db.ForeignKey('story.id')),
    db.Column('achievement_id',db.Integer,db.ForeignKey('achievement.id')))

required=db.Table('required',db.Column('required_id',db.Integer,db.ForeignKey('achievement.id')),db.Column('allowed_id',db.Integer,db.ForeignKey('achievement.id')))



class Category(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),index=True)
    added=db.Column(db.DateTime)
    adder=db.Column(db.String(25))

    subcategories=db.relationship('Subcategory',backref='category',lazy='dynamic')

    def in_achieved(self,user):
        for ach in user.achieved:
            if self.id==ach.group.subcategory.category.id:
                return True
        else:
            return False

    def in_todo(self,user):
        for ach in user.todo:
            if self.id==ach.group.subcategory.category.id:
                return True
        else:
            return False


class Subcategory(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),index=True)
    added=db.Column(db.DateTime)
    adder=db.Column(db.String(25))
    category_id=db.Column(db.Integer,db.ForeignKey('category.id'))

    groups=db.relationship('Group',backref='subcategory',lazy='dynamic')

    def in_achieved(self,user):
        for ach in user.achieved:
            if self.id==ach.group.subcategory.id:
                return True
        else:
            return False

    def in_todo(self,user):
        for ach in user.todo:
            if self.id==ach.group.subcategory.id:
                return True
        else:
            return False


class Group(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),index=True)
    added=db.Column(db.DateTime)
    adder=db.Column(db.String(25))
    subcategory_id=db.Column(db.Integer,db.ForeignKey('subcategory.id'))

    achievements=db.relationship('Achievement',backref='group',lazy='dynamic')

    def in_achieved(self,user):
        for ach in user.achieved:
            if self.id==ach.group.id:
                return True
        else:
            return False

    def in_todo(self,user):
        for ach in user.todo:
            if self.id==ach.group.id:
                return True
        else:
            return False


class Achievement(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    altname=db.Column(db.String(20))
    level=db.Column(db.Integer)
    description=db.Column(db.Text)
    requirements=db.Column(db.Text)
    imgurl=db.Column(db.String(200))
    points=db.Column(db.Integer)
    title=db.Column(db.String(100))
    group_id=db.Column(db.Integer,db.ForeignKey('group.id'))

    added=db.Column(db.DateTime)
    adder=db.Column(db.String(25))

    comments=db.relationship('Post',backref='achievement',lazy='dynamic')
    promotions=db.relationship('Promoted',backref='achievement',lazy="dynamic",cascade="all,delete-orphan")
    companies=db.relationship('Interested',backref='achievement',lazy="dynamic",cascade="all,delete-orphan")

    allowed=db.relationship('Achievement',secondary=required,
        primaryjoin=(required.c.required_id==id),
        secondaryjoin=(required.c.allowed_id==id),
        backref=db.backref('required',lazy='dynamic'),lazy='dynamic')

    def promotions_attached(self,owner_id=None):
        if owner_id:
            return Promotion.query.join("achievements","achievement").filter(Promoted.achievement_id==self.id).filter(Company.owner_id==owner_id).all()
        else:
            return Promotion.query.join("achievements","achievement").filter(Promoted.achievement_id==self.id).all()

    def random_promotions_attached(self,n):
        return Promotion.query.join("achievements","achievement").filter(Promoted.achievement_id==self.id).order_by(func.random()).limit(n)

    def promotions_count(self,owner_id=None):
        if owner_id:
            return Promotion.query.join("achievements","achievement").filter(Promoted.achievement_id==self.id).join("company").filter(Company.owner_id==owner_id).count()
        else:
            return Promotion.query.join("achievements","achievement").filter(Promoted.achievement_id==self.id).count()

    def companies_attached(self,owner_id=None):
        if owner_id:
            return Company.query.join("achievements","achievement").filter(Interested.achievement_id==self.id).filter(Company.owner_id==owner_id).all()
        else:
            return Company.query.join("achievements","achievement").filter(Interested.achievement_id==self.id).all()

    def companies_attached_count(self,owner_id=None):
        if owner_id:
            return Company.query.join("achievements","achievement").filter(Interested.achievement_id==self.id).filter(Company.owner_id==owner_id).count()
        else:
            return Company.query.join("achievements","achievement").filter(Interested.achievement_id==self.id).count()


    def is_sponsored(self,comp):
        intr=Interested.query.filter_by(achievement_id=self.id,company_id=comp.id).first()
        if intr is not None:
            return intr.sponsored
        else:
            return False

    def is_sponsored_user(self,user):
        for comp in user.companies:
            if self.is_sponsored(comp):
                return True
        else:
            return False

    def __repr__(self):
        return 'Category: %s, Subcategory: %s, Name: %s,level: %s, points: %d \n'%(self.group.subcategory.category.name,self.group.subcategory.name,self.group.name,self.level,self.points)


    def already_allowing(self,ach):
        return self.allowed.filter(required.c.allowed_id==ach.id).count()>0

    def allow(self,ach):
        if not self.already_allowing(ach):
            self.allowed.append(ach)
            return self

    def stop_allowing(self,ach):
        if self.already_allowing(ach):
            self.allowed.remove(ach)
            return self


    def all_required(self,user):
        for ach in self.required:
            if ach not in user.achieved:
                return False
                break
        else:
            return True

    def any_allowed(self,user):
        for ach in self.allowed:
            if ach in user.achieved:
                return True
                break
        else:
            return False

    def required_tree(self,unavi):
        if self.required.count()>0:
            for ach in self.required:
                unavi.append(ach)
                if ach.required.count()>0:
                    unavi+=ach.required_tree(unavi)
            return unavi
        else:
            return []






class Company(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),index=True)
    email=db.Column(db.String(64),index=True,unique=True)
    address=db.Column(db.String(128),index=True)
    city=db.Column(db.String(32),index=True)
    zipcode=db.Column(db.String(15))
    tel=db.Column(db.String(15))
    url=db.Column(db.String(64))
    short_desc=db.Column(db.String(144))
    description=db.Column(db.Text)
    lat=db.Column(db.Float)
    lon=db.Column(db.Float)
    imgurl=db.Column(db.String(200))
    added=db.Column(db.DateTime)
    rating=db.Column(db.Float)
    hits=db.Column(db.Integer)
    links_avi=db.Column(db.Integer)
    sponsored_avi=db.Column(db.Integer)
    promos_avi=db.Column(db.Integer)
    owner_id=db.Column(db.Integer,db.ForeignKey('owner.id'))

    reviews=db.relationship('Review',backref='company',lazy='dynamic')

    promotions=db.relationship('Promotion',backref='company',lazy='dynamic',cascade='all, delete-orphan')

    achievements=db.relationship("Interested",backref="company",lazy="dynamic",cascade="all, delete-orphan")

    def already_ofinterest(self,ach):
        return Interested.query.filter_by(achievement_id=ach.id,company_id=self.id).count()>0


    def of_interest(self):
        return Achievement.query.join("companies","company").filter(Interested.company_id==self.id).all()

    def of_interest_count(self):
        return Achievement.query.join("companies","company").filter(Interested.company_id==self.id).count()



    def not_interested(self,ach):
        if self.already_ofinterest(ach):
            intd=Interested.query.filter_by(company_id=self.id,achievement_id=ach.id).first()
            if intd.sponsored:
                self.sponsored_avi+=1
            self.achievements.remove(intd)
            self.links_avi+=1
            return self


    def get_interested(self,ach):
        if not self.already_ofinterest(ach):
            if self.links_avi:
                self.achievements.append(Interested(achievement=ach,sponsored=False))
                self.links_avi-=1
                return self

    def in_proximity(self,user_lat,user_lon,max_distance):

        return spherical_distance(self.lat,self.lon,user_lat,user_lon)<=max_distance
     

class Promoted(db.Model):
    achievement_id=db.Column(db.Integer,db.ForeignKey('achievement.id'),primary_key=True)
    promotion_id=db.Column(db.Integer,db.ForeignKey('promotion.id'),primary_key=True)
    clicks=db.Column(db.Integer)


class Interested(db.Model):
    achievement_id=db.Column(db.Integer,db.ForeignKey('achievement.id'),primary_key=True)
    company_id=db.Column(db.Integer,db.ForeignKey('company.id'),primary_key=True)
    sponsored=db.Column(db.Boolean)



class Promotion(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    url=db.Column(db.String(64))
    imgurl=db.Column(db.String(200))
    company_id=db.Column(db.Integer,db.ForeignKey('company.id'))
    added=db.Column(db.DateTime)
    links_avi=db.Column(db.Integer)
    company_clicks=db.Column(db.Integer)

    achievements=db.relationship("Promoted",backref="promotion",lazy="dynamic",cascade="all, delete-orphan")

    def promoted_achievements(self):
        return Achievement.query.join("promotions","promotion").filter(Promoted.promotion_id==self.id).all()

    def promoted_count(self):
        return Achievement.query.join("promotions","promotion").filter(Promoted.promotion_id==self.id).count()

    def is_promoted(self,ach):
        return Promoted.query.filter_by(achievement_id=ach.id,promotion_id=self.id).count()>0

    def promote(self,ach):
        if not self.is_promoted(ach):
            if self.links_avi:
                self.achievements.append(Promoted(achievement=ach,clicks=0))
                self.links_avi-=1
                return self

    def stop_promoting(self,ach):
        if self.is_promoted(ach):
            prmtd=Promoted.query.filter_by(promotion_id=self.id,achievement_id=ach.id).first()
            self.achievements.remove(prmtd)
            self.links_avi+=1
            return self

    def clicks_number(self,ach):
        return Promoted.query.filter_by(promotion_id=self.id,achievement_id=ach.id).first().clicks

    def total_clicks(self):
        return sum([row.clicks for row in Promoted.query.filter_by(promotion_id=self.id).all() if row.clicks is not None])


class Website(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    url=db.Column(db.String(64))
    imgurl=db.Column(db.String(200))
    name=db.Column(db.String(64))

    helped=db.relationship('Achievement',secondary=helped,
        primaryjoin=(helped.c.website_id==id),
        secondaryjoin=(helped.c.achievement_id==Achievement.id),
        backref=db.backref('websites',lazy='dynamic'),
        lazy='dynamic')


    def is_helped(self,ach):
        return self.helped.filter(helped.c.achievement_id==ach.id).count()>0

    def help(self,ach):
        if not self.is_helped(ach):
            self.helped.append(ach)
            return self

    def stop_helping(self,ach):
        if self.is_helped(ach):
            self.helped.remove(ach)
            return self




class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.String(1000))
    timestamp=db.Column(db.DateTime)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    achievement_id=db.Column(db.Integer,db.ForeignKey('achievement.id'))

    def __repr__(self):
        return '<Post %r>' %(self.body)




class Story(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    added=db.Column(db.DateTime)
    last_edited=db.Column(db.DateTime)
    title=db.Column(db.String(100))
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))

    described=db.relationship('Achievement',secondary=described,
        primaryjoin=(described.c.story_id==id),
        secondaryjoin=(described.c.achievement_id==Achievement.id),
        backref=db.backref('stories',lazy='dynamic'),
        lazy='dynamic')


    def is_described(self,ach):
        return self.described.filter(described.c.achievement_id==ach.id).count()>0

    def describe(self,ach):
        if not self.is_described(ach):
            self.described.append(ach)
            return self

    def stop_describing(self,ach):
        if self.is_described(ach):
            self.described.remove(ach)
            return self




class Review(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    rating=db.Column(db.Integer)
    timestamp=db.Column(db.DateTime)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    company_id=db.Column(db.Integer,db.ForeignKey('company.id'))

    def __repr__(self):
        return '<Review %r>' %(self.body)



class Base(db.Model):

    __tablename__ = "base"
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),index=True,unique=True)
    password=db.Column(db.String(128))
    role=db.Column(db.String(10))
    last_seen=db.Column(db.DateTime)

    __mapper_args__={'polymorphic_identity':'base','polymorphic_on':role}

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    
    
class Admin(Base):
    __tablename__='admin'
    id=db.Column(db.Integer,db.ForeignKey('base.id'),primary_key=True)
    __mapper_args__={'polymorphic_identity':'admin'}


class Owner(Base):
    __tablename__='owner'
    id=db.Column(db.Integer,db.ForeignKey('base.id'),primary_key=True)
    email=db.Column(db.String(120),index=True,unique=True)
    upload_dir=db.Column(db.String(120))
    comp_upload_dir=db.Column(db.String(120))
    prom_upload_dir=db.Column(db.String(120))
    imgurl=db.Column(db.String(120))
    nickname=db.Column(db.String(64))
    about_me=db.Column(db.String(140))
    account_type=db.Column(db.String(10)) #basic, premium, ultimate
    special_companies_avi=db.Column(db.Integer)
    normal_companies_avi=db.Column(db.Integer)
    __mapper_args__={'polymorphic_identity':'owner'}


    companies=db.relationship('Company',backref='owner',lazy='dynamic')


    def promotions_available(self):
        avi=0
        for comp in self.companies:
            avi+=comp.promos_avi
        return avi

    def owned_promotions(self):
        return Promotion.query.join("company","owner").filter(Company.owner_id==self.id).all()

    def promotions_count(self):
        return Promotion.query.join("company","owner").filter(Company.owner_id==self.id).count()

    def promoted_achs(self):
        return Achievement.query.join((Promoted,Achievement.promotions)).join((Promotion,Promoted.promotion)).join((Company,Promotion.company)).filter(Company.owner_id==self.id).all()

    def promoted_achs_count(self):
        achs=Achievement.query.join((Promoted,Achievement.promotions)).join((Promotion,Promoted.promotion)).join((Company,Promotion.company)).filter(Company.owner_id==self.id).all()
        k=0
        for ach in achs: k+=1
        return k

    def interested_achs(self):
        return Achievement.query.join((Interested,Achievement.companies)).join((Company,Interested.company)).filter(Company.owner_id==self.id).all()

    def interested_achs_count(self):
        achs=Achievement.query.join((Interested,Achievement.companies)).join((Company,Interested.company)).filter(Company.owner_id==self.id).all()
        k=0
        for ach in achs: k+=1
        return k


class User(Base):
    __tablename__ = "user"
    id=db.Column(db.Integer,db.ForeignKey('base.id'),primary_key=True)
    nickname=db.Column(db.String(64))
    email=db.Column(db.String(120),index=True,unique=True)
    total=db.Column(db.Integer)
    max_score=db.Column(db.Integer)
    max_desired=db.Column(db.Integer)
    upload_dir=db.Column(db.String(120))
    imgurl=db.Column(db.String(100))
    about_me=db.Column(db.String(140))

    lat=db.Column(db.Float)
    lon=db.Column(db.Float)
    title=db.Column(db.String(100))


    __mapper_args__={'polymorphic_identity':'user'}

    posts=db.relationship('Post',backref='user',lazy='dynamic')

    stories=db.relationship('Story',backref='user',lazy='dynamic',cascade='all')

    reviews=db.relationship('Review',backref='user',lazy='dynamic')

    achieved=db.relationship('Achievement',secondary=achies,
        primaryjoin=(achies.c.user_id==id),
        secondaryjoin=(achies.c.achievement_id==Achievement.id),
        backref=db.backref('users_achieved',lazy='dynamic'),
        lazy='dynamic')

    todo=db.relationship('Achievement',secondary=todos,
        primaryjoin=(todos.c.user_id==id),
        secondaryjoin=(todos.c.achievement_id==Achievement.id),
        backref=db.backref('users_todo',lazy='dynamic'),
        lazy='dynamic')

    followed=db.relationship('User',secondary=followers,
        primaryjoin=(followers.c.who_follows_id==id),
        secondaryjoin=(followers.c.who_is_followed_id==id),
        backref=db.backref('followers',lazy='dynamic'),lazy='dynamic')

    def __repr__(self):
        return "<User %r>"%(self.username)

    def already_achieved(self,ach):
        return self.achieved.filter(achies.c.achievement_id==ach.id).count()>0

    def already_on_list(self,ach):
        return self.todo.filter(todos.c.achievement_id==ach.id).count()>0

    def remove_ach(self,ach):
        if self.already_achieved(ach):
            self.achieved.remove(ach)
            self.max_desired-=ach.points
            self.total-=ach.points
            return self
        elif self.already_on_list(ach):
            self.max_desired-=ach.points
            self.todo.remove(ach)
            return self


    def add_ach(self,ach):
        if self.already_on_list(ach):
            self.todo.remove(ach)
        else:
            self.max_desired+=ach.points

        if not self.already_achieved(ach):
            self.total+=ach.points
            self.achieved.append(ach)
            return self

    def add_to_list(self,ach):
        if self.already_achieved(ach):
            self.achieved.remove(ach)
            self.total-=ach.points
        else:
            self.max_desired+=ach.points

        if not self.already_on_list(ach):
            self.todo.append(ach)              
            return self

    def already_following(self,user):
        return self.followed.filter(followers.c.who_is_followed_id==user.id).count()>0

    def follow(self,user):
        if not self.already_following(user):
            self.followed.append(user)
            return self

    def unfollow(self,user):
        if self.already_following(user):
            self.followed.remove(user)
            return self

    def followed_posts(self,k):
        return Post.query.join(followers, (followers.c.who_is_followed_id==Post.user_id)).filter(followers.c.who_follows_id==self.id).order_by(Post.timestamp.desc()).limit(k)

    def followed_stories(self,k):
        return Story.query.join(followers, (followers.c.who_is_followed_id==Story.user_id)).filter(followers.c.who_follows_id==self.id).order_by(Story.added.desc()).limit(k)

    def followed_reviews(self,k):
        return Review.query.join(followers, (followers.c.who_is_followed_id==Review.user_id)).filter(followers.c.who_follows_id==self.id).order_by(Review.timestamp.desc()).limit(k)


    @staticmethod
    def make_unique_nickname(username):
        
        if User.query.filter_by(username=username).first() is None:
            return username

        version=2

        while True:
            new_username=username+str(version)
            if User.query.filter_by(username=new_nickname).first() is None:
                break
            version+=1

        return new_username






