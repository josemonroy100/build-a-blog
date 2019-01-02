from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:peru1968@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Welcome!")
            return redirect('/blog')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']


        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/blog')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')


@app.route("/blog", methods=['POST', 'GET'])
def blog():
    owner = User.query.filter_by(email=session['email']).first()
    blogs = Blog.query.filter_by(owner=owner).all()
    if request.args:
        blog_id = request.args.get('id')
        for blog in blogs:
            if int(blog_id) == blog.id:
                title = blog.title
                body = blog.body
                return render_template('post.html', title=title, body=body)
    else:
        return render_template("blog.html", heading="Life is a Blog!", blogs=blogs)



@app.route("/newpost", methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'GET':
        return render_template("newpost.html", heading="New Blog Entry")
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if not title and not body:
            flash("Please enter a title for your blog")
            flash("Please enter a body for your blog")
            return render_template("newpost.html", heading="New Blog Entry")
        elif not title:
            flash("Please enter a title for your blog")
            return render_template("newpost.html", heading="New Blog Entry", body=body)
        elif not body:
            flash("Please enter content for your blog")
            return render_template("newpost.html", heading="New Blog Entry", title=title)
        else:
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            return render_template('post.html', title=title, body=body)


@app.route('/logout')
def logout():
    del session['email']
    flash("See You Soon!")
    return redirect('/login')


if __name__ == '__main__':
    app.run()