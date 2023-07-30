from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from forms import TodoListForm, SignupForm, LoginForm, ContactForm
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from datetime import datetime
import smtplib

# Creating the application
app = Flask(__name__)
app.config['SECRET_KEY'] = "bahae03"

# Connect to database
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Creating users table
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    lists = relationship("TodoList")


# Creating To do List table
class TodoList(db.Model):
    __tablename__ = "list"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_list1 = db.Column(db.String(255), nullable=False)
    user_list2 = db.Column(db.String(255), nullable=False)
    user_list3 = db.Column(db.String(255), nullable=False)
    user_list4 = db.Column(db.String(255), nullable=False)


db.create_all()

date = datetime.now()


@app.route("/")
def home():
    return render_template("home.html", date=date.strftime("%A, %d %B"), year=date.year)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.data.get('username'),
            email=form.data.get('email'),
            password=form.data.get('password')
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("signup.html", form=form, current_user=current_user, year=date.year)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.data.get("email")
        password = form.data.get("password")
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if existing_user.password == password:
                login_user(existing_user)
                return redirect(url_for("todo"))
            else:
                flash('Wrong password. Try again!')
                return redirect(url_for('login'))
        elif not existing_user:
            flash('Wrong email. Try again!')
            return redirect(url_for('login'))
    return render_template("login.html", form=form, current_user=current_user, year=date.year)


@app.route("/todo", methods=['GET', 'POST'])
@login_required
def todo():
    user_list_db = TodoList.query.filter_by(user_id=current_user.id).first()
    if user_list_db:
        return redirect(url_for("success"))
    form = TodoListForm()
    if form.validate_on_submit():
        user_list = form.data.get("todo_list")
        user_list_split = user_list.split(", ")
        all_the_list = []
        for i in user_list_split:
            all_the_list.append(i)
        new_list = TodoList(
            user_id=current_user.id,
            user_list1=all_the_list[0],
            user_list2=all_the_list[1],
            user_list3=all_the_list[2],
            user_list4=all_the_list[3],
        )
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for("success"))
    return render_template("todo.html", form=form, current_user=current_user, year=date.year)


@app.route("/success")
@login_required
def success():
    all_of_the_list = TodoList.query.filter_by(user_id=current_user.id).first()
    if not all_of_the_list:
        listed_todo_items = []
    else:
        listed_todo_items = [all_of_the_list.user_list1.capitalize(),
                             all_of_the_list.user_list2.capitalize(),
                             all_of_the_list.user_list3.capitalize(),
                             all_of_the_list.user_list4.capitalize()]
    return render_template("success.html", current_user=current_user, date=date.strftime("%A, %d %B"), year=date.year,
                           list=listed_todo_items)


@app.route("/update/<int:user_id_list>", methods=['GET', 'POST'])
def update(user_id_list):
    list_to_delete = TodoList.query.filter_by(user_id=user_id_list).first()
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for("todo"))


@app.route("/delete/<int:user_id_list>", methods=['GET', 'POST'])
def delete(user_id_list):
    list_to_delete = TodoList.query.filter_by(user_id=user_id_list).first()
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for("success"))


@app.route("/contact", methods=['POST', 'GET'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        the_message = form.data.get("message")
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(EMAIL, PASSWORD)
            connection.sendmail(
                from_addr=EMAIL,
                to_addrs=EMAIL_REC,
                msg=f"Subject:Message from {current_user.email}\n\n{the_message}"
            )
        return redirect(url_for("success"))
    return render_template("contact.html", form=form, year=date.year, current_user=current_user)


@app.route("/aboutUs")
def aboutus():
    return render_template("aboutus.html", current_user=current_user)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
