from app import db, models
import datetime
import shutil
import os
from hashlib import md5

bas=models.Base.query.all()
o=models.Owner.query.all()
a=models.User.query.all()
b=models.Achievement.query.all()
c=models.Company.query.all()
d=models.Promotion.query.all()
e=models.Post.query.all()
f=models.Website.query.all()
g=models.Story.query.all()
h=models.Category.query.all()
j=models.Subcategory.query.all()
k=models.Group.query.all()






for u in b:
	if u.imgurl:
		try:
			os.remove(u.imgurl)
		except FileNotFoundError:
			pass
		
	db.session.delete(u)

for t in c:
	db.session.delete(t)

for u in d:
	db.session.delete(u)

for t in e:
	db.session.delete(t)

for u in f:
	if u.imgurl:
		try:
			os.remove(u.imgurl)
		except FileNotFoundError:
			pass
		
	db.session.delete(u)
	

for t in g:
	db.session.delete(t)

for t in k:
	db.session.delete(t)

for t in j:
	db.session.delete(t)

for t in h:
	db.session.delete(t)
	
for t in a:
	if t.upload_dir:
		try:
			shutil.rmtree(t.upload_dir)
		except FileNotFoundError:
			pass
	db.session.delete(t)
	

for z in o:
	if z.upload_dir:
		try:
			shutil.rmtree(z.upload_dir)
		except FileNotFoundError:
			pass
	db.session.delete(z)
	

for ba in bas:
	db.session.delete(ba)


db.session.commit()


#admin:

ad=models.Admin(username='admin',password=md5(('admin').encode('utf-8')).hexdigest(),role='admin')

db.session.add(ad)
db.session.commit()

# #users:

# u=models.User(username='Anon',email='jesus@maria.com',password='pwd',total=0, role='user', imgurl='images/av.jpg')

# #achievements
# a1=models.Achievement(category='Education',subcategory='Language',name='Spanish',level=1,points=10,imgurl='https://goo.gl/dqduFX',description="This achievement shows that you have basic understaning of Spanish language.",requirements="You should finish approximately 1 year of Spanish classes and be able to make a very basic conversation and read simple articles.")
# a2=models.Achievement(category='Education',subcategory='Language',name='Spanish',level=2,points=100,imgurl='https://goo.gl/dqduFX',description="This achievement shows that you are an intermediate Spanish languege user.",requirements="You should finish approximately 2 to 3 years of Spanish classes and be able to make simply express your thoughts and feelings.")
# a3=models.Achievement(category='Education',subcategory='Language',name='Spanish',level=3,points=1000,imgurl='https://goo.gl/dqduFX',description="This achievement shows that you an advanced Spanish languege user.",requirements="You should finish approximately 5 years of Spanish classes, feel comfortable when speaking Spanish and be able to read Spanish articles.")
# a4=models.Achievement(category='Education',subcategory='Language',name='Spanish',level=4,points=5000,imgurl='https://goo.gl/dqduFX',description="This achievement shows that you have mastered the Spanish languege.",requirements="Being a native speaker or being completely fluent in this language.")

# b1=models.Achievement(category='Education',subcategory='Language',name='German',level=1,points=10,imgurl="https://goo.gl/A1Byc3",description="This achievement shows that you have basic understaning of German language.",requirements="You should finish approximately 1 year of German classes and be able to make a very basic conversation and read simple articles.")
# b2=models.Achievement(category='Education',subcategory='Language',name='German',level=2,points=100,imgurl="https://goo.gl/A1Byc3",description="This achievement shows that you are an intermediate German languege user.",requirements="You should finish approximately 2 to 3 years of German classes and be able to make simply express your thoughts and feelings.")
# b3=models.Achievement(category='Education',subcategory='Language',name='German',level=3,points=1000,imgurl="https://goo.gl/A1Byc3",description="This achievement shows that you an advanced German languege user.",requirements="You should finish approximately 5 years of German classes, feel comfortable when speaking German and be able to read German articles.")
# b4=models.Achievement(category='Education',subcategory='Language',name='German',level=4,points=5000,imgurl="https://goo.gl/A1Byc3",description="This achievement shows that you have mastered the German languege.",requirements="Being a native speaker or being completely fluent in this language.", title="Fuhrer")

# c1=models.Achievement(category='Education',subcategory='University',name='Ivy League',level=None,points=1000,imgurl="https://goo.gl/iAE9kV",description="This achievement is a proof of degree acquired for an Ivy League institution.",requirements="Graduated from an Ivy League university.")

# d1=models.Achievement(category='Education',subcategory='Math skills',name='Arithmetics',level=None,points=10,imgurl="https://goo.gl/LkMjIs",description="You are proficient in basic mathematical calculations.",requirements="Elementary school mathematics.")
# d2=models.Achievement(category='Education',subcategory='Math skills',name='Basic algebra',level=None,points=100,imgurl="https://goo.gl/bDSU45",description="You have basic knowledge of algebra.", requirements="High school mathematics.")
# d3=models.Achievement(category='Education',subcategory='Math skills',name='Calculus',level=None,points=500,imgurl="https://goo.gl/sfnoyZ",description="You have mastered mathematical calculus.", requirements="A course in calculus.")

# e1=models.Achievement(category='Sport',subcategory='Dance',name='Salsa',level=1,points=10,imgurl="https://goo.gl/oOlX5I",description="Basic ability to dance Salsa.", requirements="An introductory course in Salsa dance.")
# e2=models.Achievement(category='Sport',subcategory='Dance',name='Salsa',level=2,points=100,imgurl="https://goo.gl/oOlX5I",description="Achievement showing that you are able not to humiliate yourself on a dancefloor.", requirements="An intermediate course in Salsa.")
# e3=models.Achievement(category='Sport',subcategory='Dance',name='Salsa',level=3,points=500,imgurl="https://goo.gl/oOlX5I",description="Salsa dancing feels as natural as walking.", requirements="An advanced course in Salsa dance.")
# e4=models.Achievement(category='Sport',subcategory='Dance',name='Salsa',level=4,points=2000,imgurl="https://goo.gl/oOlX5I",description="Achievement prooving your Salsa dance mastery.", requirements="Finish a full course in Salsa and be able to compete against professional dancers.")

# f1=models.Achievement(category='Sport',subcategory='Martial arts',name='Karate',level=1,points=10,imgurl="https://goo.gl/8q80OS",description="Basic Karate skills.", requirements="White or yellow belt.")
# f2=models.Achievement(category='Sport',subcategory='Martial arts',name='Karate',level=3,points=500,imgurl="https://goo.gl/8q80OS",description="Basic ability to fight and mastery of basic karate moves.", requirements="Brown belt.")
# f3=models.Achievement(category='Sport',subcategory='Martial arts',name='Karate',level=2,points=200,imgurl="https://goo.gl/8q80OS",description="Karate seems less like a mystery to you now.", requirements="At least green belt.")
# f4=models.Achievement(category='Sport',subcategory='Martial arts',name='Karate',level=4,points=2000,imgurl="https://goo.gl/8q80OS",description="Proof that you have sweat your ass off for so long, that you were finally given a black belt.", requirements="Black belt.",title="The Karate Master")
# f5=models.Achievement(category='Sport',subcategory='Martial arts',name='Karate',level=5,points=5000,imgurl="https://goo.gl/8q80OS",description="True mastery of the martial art.", requirements="3rd dan.",title="Killing Machine")



# #companies
# z1=models.Company(name="Language school 'Escobar'",email="esco@gmail.com",address="311 Broadway",city="New York",zipcode="NY 10007", tel="347-100-2210",url="http://www.esco-school.com",lat=0,lon=0,short_desc="Language school.",description="We are a renowned New York language school offering courses in all widely-used languages.",imgurl="./static/images/flag1.png",sponsored=True)
# z2=models.Company(name="Language school 'Wie heisst du'",email="wie@gmail.com",address="33 E23rd Street",city="New York",zipcode="NY 10012", tel="356-130-1834",url="http://www.wiewie.com",lat=0,lon=0,short_desc="German language school.",description="We are a New York based language school offering courses in German language.",imgurl="./static/images/german.png",sponsored=True)
# z3=models.Company(name="Language school 'Brooklyner'",email="brookllang@yahoo.com",address="15L Bedford Avenue",city="Brooklyn",zipcode="NY 11040", tel="756-333-1124",url="http://www.lang-brook.com",lat=0,lon=0,short_desc="Language school.",description="Our school offers courses in many languages, from Hebrew to Swahili. All of them taught by native speakers residing in New York City.",imgurl="./static/images/lang.png",sponsored=True)
# z4=models.Company(name="'Hello' Language School",email="herro@hotmail.com",address="233 Main Street",city="Queens",zipcode="NY 12057", tel="954-591-2357",url="http://www.herrohello.com",lat=0,lon=0,short_desc="Another language school.",description="Language school based in Queens offering courses in all major languages.",imgurl="./static/images/hello.png",sponsored=False)
# z5=models.Company(name="Harvard University",email="harvard@harvard.edu",address="86 Brattle Street", city="Cambridge", zipcode="MA 02138",tel="617-495-1000",url="http://www.harvard.edu/",lat=0,lon=0,short_desc="Ivy League University",description="One of the oldest and best schools in the U.S.",imgurl="./static/images/veritas.jpg",sponsored=True)
# z6=models.Company(name="Karate school 'Meikyo'",email="meikyoo@yahoo.com",address="14 W106th Street", city="New York", zipcode="NY 10024",tel="554-567-7863",url="http://www.meimei.com",lat=0,lon=0,short_desc="Karate School",description="Kyokushinkai Karate school operating on Upper West Side. Beginner and advanced classes offered",imgurl="./static/images/karate2.jpg",sponsored=True)
# z7=models.Company(name="Karate school 'Chi'",email="chi@gmail.com",address="433 Lexington Avenue", city="New York", zipcode="NY 10004",tel="972-123-7214",url="http://www.chi-school.com",lat=0,lon=0,short_desc="Karate School",description="An old karate school that trains only future champions!",imgurl="./static/images/karate1.png",sponsored=True)


# db.session.add(u)
# db.session.add(a1)
# db.session.add(a2)
# db.session.add(a3)
# db.session.add(a4)
# db.session.add(b1)
# db.session.add(b2)
# db.session.add(b3)
# db.session.add(b4)
# db.session.add(c1)
# db.session.add(d1)
# db.session.add(d2)
# db.session.add(d3)
# db.session.add(e1)
# db.session.add(e2)
# db.session.add(e3)
# db.session.add(e4)
# db.session.add(f3)
# db.session.add(f4)
# db.session.add(f1)
# db.session.add(f2)
# db.session.add(f5)
# db.session.add(z1)
# db.session.add(z2)
# db.session.add(z3)
# db.session.add(z4)
# db.session.add(z5)
# db.session.add(z6)
# db.session.add(z7)

# db.session.commit()




# #connections - user to achievements
# u1=u.add_ach(a1)
# u2=u.add_ach(a2)
# u3=u.add_to_list(a3)
# u4=u.add_ach(e1)
# u5=u.add_ach(d3)




# db.session.add(u1)
# db.session.add(u2)
# db.session.add(u3)
# db.session.add(u4)
# db.session.add(u5)
# db.session.commit()


# #connections - companies to achievements

# x1=z1.get_interested(a1)
# x2=z1.get_interested(a2)
# x3=z1.get_interested(a3)
# x4=z1.get_interested(a4)
# x5=z1.get_interested(b1)
# x6=z1.get_interested(b2)
# x7=z1.get_interested(b3)
# x8=z1.get_interested(b4)

# y1=z3.get_interested(a1)
# y2=z3.get_interested(a2)
# y3=z3.get_interested(a3)
# y4=z3.get_interested(a4)
# y5=z3.get_interested(b1)
# y6=z3.get_interested(b2)
# y7=z3.get_interested(b3)
# y8=z3.get_interested(b4)

# w1=z4.get_interested(a1)
# w2=z4.get_interested(a2)
# w3=z4.get_interested(a3)
# w4=z4.get_interested(a4)
# w5=z4.get_interested(b1)
# w6=z4.get_interested(b2)
# w7=z4.get_interested(b3)
# w8=z4.get_interested(b4)

# v1=z2.get_interested(b1)
# v2=z2.get_interested(b2)
# v3=z2.get_interested(b3)
# v4=z2.get_interested(b4)

# t1=z5.get_interested(c1)

# s1=z6.get_interested(f1)
# s2=z6.get_interested(f2)
# s3=z6.get_interested(f3)
# s4=z6.get_interested(f4)

# r1=z7.get_interested(f1)
# r2=z7.get_interested(f2)
# r3=z7.get_interested(f3)
# r4=z7.get_interested(f4)
# r5=z7.get_interested(f5)

# db.session.add(x1)
# db.session.add(x2)
# db.session.add(x3)
# db.session.add(x4)
# db.session.add(x5)
# db.session.add(x6)
# db.session.add(x7)
# db.session.add(x8)

# db.session.add(y1)
# db.session.add(y2)
# db.session.add(y3)
# db.session.add(y4)
# db.session.add(y5)
# db.session.add(y6)
# db.session.add(y7)
# db.session.add(y8)

# db.session.add(w1)
# db.session.add(w2)
# db.session.add(w3)
# db.session.add(w4)
# db.session.add(w5)
# db.session.add(w6)
# db.session.add(w7)
# db.session.add(w8)

# db.session.add(v1)
# db.session.add(v2)
# db.session.add(v3)
# db.session.add(v4)

# db.session.add(s1)
# db.session.add(s2)
# db.session.add(s3)
# db.session.add(s4)

# db.session.add(r1)
# db.session.add(r2)
# db.session.add(r3)
# db.session.add(r4)
# db.session.add(r5)

# db.session.add(t1)

# db.session.commit()


# #promotions
# p1=models.Promotion(url="http://www.esco-school.com/promo1",imgurl="./static/images/banner1.jpg",company=z1)
# p2=models.Promotion(url="http://www.esco-school.com/promo2",imgurl="./static/images/banner2.jpg",company=z1)
# p3=models.Promotion(url="http://www.wiewie.com/promo",imgurl="./static/images/banner3.jpg",company=z2)

# db.session.add(p1)
# db.session.add(p2)
# db.session.add(p3)

# db.session.commit()


# #connecitons - promotions to achievements


# o1=p1.promote(a1)
# o2=p1.promote(a2)
# o3=p1.promote(a3)
# o4=p1.promote(a4)
# o5=p1.promote(b1)
# o6=p1.promote(b2)
# o7=p1.promote(b3)
# o8=p1.promote(b4)

# l1=p2.promote(a1)
# l2=p2.promote(a2)
# l3=p2.promote(b1)
# l4=p2.promote(b2)

# k1=p3.promote(b1)

# db.session.add(k1)

# db.session.add(o1)
# db.session.add(o2)
# db.session.add(o3)
# db.session.add(o4)
# db.session.add(o5)
# db.session.add(o6)
# db.session.add(o7)
# db.session.add(o8)

# db.session.add(l1)
# db.session.add(l2)
# db.session.add(l3)
# db.session.add(l4)

# db.session.commit()


# #websites:
# web1=models.Website(url="http://www.tripadvisor.com",imgurl="./static/images/tripadv.jpg",name="Trip Advisor")
# web2=models.Website(url="http://jka.or.jp/en/",imgurl="./static/images/jka.jpg",name="Japanese Karate Association")
# web3=models.Website(url="http://www.itkf.org/",imgurl="./static/images/itkf.jpg",name="International Traditional Karate Federation")

# db.session.add(web1)
# db.session.add(web2)
# db.session.add(web3)

# db.session.commit()


# #connections - websites to achievements

# help1=web1.help(a4)
# help2=web1.help(b4)

# help3=web2.help(f1)
# help4=web2.help(f2)
# help5=web2.help(f3)
# help6=web2.help(f4)
# help7=web2.help(f5)

# help31=web3.help(f1)
# help41=web3.help(f2)
# help51=web3.help(f3)
# help61=web3.help(f4)
# help71=web3.help(f5)

# db.session.add(help1)
# db.session.add(help2)
# db.session.add(help3)
# db.session.add(help4)
# db.session.add(help5)
# db.session.add(help6)
# db.session.add(help7)
# db.session.add(help31)
# db.session.add(help41)
# db.session.add(help51)
# db.session.add(help61)
# db.session.add(help71)

# db.session.commit()