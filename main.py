from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'all_blogposts', 'index',]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html',title="All Users", users=users)

@app.route('/singleuser')
def single_user():
    owner_id = request.args.get('id')
    user_blogs = Blog.query.filter_by(owner_id=owner_id).all()
    blogs = Blog.query.all()
    return render_template('singleuser.html', user_blogs=user_blogs)

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()

        if not user:
           return '<h1>User does not exist, please <a href="/signup">signup</a> for an account</h1>'
            
        if user.password != password:
            flash('incorrect password')
            

        if user and user.password == password:
            session['username'] = username
            flash("Welcome, {username}")
            return redirect('/newpost')
        

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        username_error = ''
        password_error = ''
        verify_error = ''
   
        existing_user = User.query.filter_by(username=username).first()

        #validating username
        if len(username) == 0:
            username_error = "username required"
            username = ''

        #validating password            
        if len(password) == 0:
            password_error = "password required"
            password = ''

        if len(verify) == 0:
            verify_error = "must verify password"
  
        if verify != password and not password_error:
            verify_error = "passwords do not match" 
            verify = ''

        if existing_user:
            flash('user already exists, please login')

        if not username_error and not password_error and not verify_error and not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return render_template('newpost.html',username=username)

        else:
            return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error,
            username=username, password=password, verify=verify,)

    return render_template('signup.html')

        

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/blog')
def all_blogposts():
    blogs = Blog.query.all()
    
    return render_template('blog.html',title="My Blog!", blogs=blogs)

@app.route('/blogpost')
def single_blogpost():
    blogpost_id = request.args.get('id')
    blogpost = Blog.query.filter_by(id=blogpost_id).first()
    user = User.query.filter_by(id=blogpost.owner_id).first()
    return render_template('blogpost.html', blogpost=blogpost, user=user)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
   
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        
        if len(title) == 0 or len(body)==0:
            return render_template('newpost.html')

        else:
            new_post = Blog(title,body,owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blogpost?id={}'.format(new_post.id))
        
    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()