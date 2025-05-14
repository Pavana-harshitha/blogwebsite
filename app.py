from flask import Flask,render_template,jsonify,redirect,url_for
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,LoginManager,logout_user,current_user,login_required
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import PasswordField,StringField,SubmitField,TextAreaField
from wtforms.validators import ValidationError,Length,InputRequired,DataRequired
from datetime import datetime
from flask_mail import Mail,Message
from random import randint

app=Flask(__name__)
mail=Mail(app)

app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"]=465
app.config["MAIL_USERNAME"]='studentmart32@gmail.com'
app.config['MAIL_PASSWORD']='zdze nziw jeex jlvf'                   
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail=Mail(app)
otp=randint(000000,999999)


app=Flask(__name__)
basedir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SECRET_KEY']='thisissecretkey'

bcrypt=Bcrypt(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,unique=True,nullable=False)
    email=db.Column(db.String,unique=True,nullable=False)
    image_url=db.Column(db.String,nullable=False,default="default.jpg")
    password=db.Column(db.String,nullable=False)
    posts=db.relationship('Post',backref='author',lazy=True)

class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String,nullable=False)
    date_posted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    content=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

class RegistrationForm(FlaskForm):
    username=StringField(validators=[InputRequired()],render_kw={"placeholder":"Username"})
    email=StringField(validators=[InputRequired()],render_kw={"placeholder":"EmailID"})
    
    submit=SubmitField('Send OTP')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')
        

class LoginForm(FlaskForm):
    username=StringField(validators=[InputRequired()],render_kw={"placeholder":"Username"})
    password=PasswordField(validators=[InputRequired(),Length(min=8, max=20)],render_kw={"placeholder":"Password"})
    submit=SubmitField('Login')


class PostForm(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])
    content=TextAreaField('Content',validators=[DataRequired()])
    post=SubmitField('Post')


@app.route('/db_create', methods=['GET'])
def db_create():
    db.create_all()
    return jsonify(message="Database created")


@app.route('/db_destroy', methods=['GET'])
def db_destroy():
    db.drop_all()
    return jsonify(message="Database dropped")


@app.route('/')
@app.route('/home')
def home():
    post=Post.query.all()
    return render_template('home.html',posts=post)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/post1',methods=['GET','POST'])
@login_required
def post1():
    post1=PostForm()
    if post1.validate_on_submit():
         post=Post(title=post1.title.data,content=post1.content.data,author=current_user)
         db.session.add(post)
         db.session.commit()
         return redirect(url_for('home'))
    return render_template('post.html',post1=post1)



@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
    return render_template('login.html',forms=form)


@app.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data)
        new_user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
   

    return render_template('register.html',forms=form)



@app.route('/account')
@login_required
def account():
    image=url_for('static',filename='images/'+current_user.image_url)
    return render_template("account.html",image=image)



@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True,port=5006)
