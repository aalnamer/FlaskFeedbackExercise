from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db, User, Feedback
from forms import UserForm, UserLoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app_ctx = app.app_context()
app_ctx.push()
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)



@app.route("/")
def register_redirect():
    return redirect ("/register")

@app.route("/register" , methods=['GET', 'POST'])
def register_page():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username,password,email,first_name,last_name)
        
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
        session['username'] = new_user.username
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f'users/{new_user.username}')
        
    return render_template('register.html', form=form)
    
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form= UserLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password =  form.password.data
        
        user= User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!")
            session['username']= user.username
        else:
            form.username.errors = ['Invalid Username/password.']
    
    return render_template("login.html", form=form)



@app.route('/secret', methods=['GET', 'POST'])
def show_secret():
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    else:
        return render_template("secret.html")



@app.route('/users/<username>', methods=['GET', 'POST'])
def show_user(username):
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    user = User.query.filter(User.username == username).first()
    if user.username == session['username']:
        return render_template("userinfo.html", user=user)
    flash("You don't have permission to do that!")
    return redirect("/register")



@app.route('/users/<username>/delete', methods=['GET', 'POST'])
def delete_user(username):
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    user = User.query.filter(User.username == username).first()
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    
    return redirect ("/login")



@app.route('/users/<username>/feedback/new', methods=['GET', 'POST'])
def new_feedback(username):
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    form = FeedbackForm()
    
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        
        new_feedback = Feedback(title = title, content = content, username=username)
        
        db.session.add(new_feedback)
        db.session.commit()
        
        return redirect(f"/users/{new_feedback.username}")
    else:
        return render_template("feedbackform.html", form= form)

        

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title= form.title.data
        feedback.content= form.content.data
        db.session.commit()
        return redirect(f"/users/{feedback.username}")
    
    return render_template("/feedback_editform.html", form = form, feedback=feedback)
    
    
@app.route("/feedback/<int:feedback_id>/delete", methods=["GET", "POST"])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f"/users/{feedback.username}")




@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/')



# @app.route('/users/<username>')
# def show_all_user_info():
#     retur