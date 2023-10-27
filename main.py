from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
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
    return db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one()


# Creating users table
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    lists = relationship("TodoList")


# Creating To do List table
class TodoList(db.Model):
    __tablename__ = "list"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_list1: Mapped[str] = mapped_column(String, nullable=False)
    user_list2: Mapped[str] = mapped_column(String, nullable=False)
    user_list3: Mapped[str] = mapped_column(String, nullable=False)
    user_list4: Mapped[str] = mapped_column(String, nullable=False)


with app.app_context():
    db.create_all()

date = datetime.now()


@app.route("/")
def home():
    return render_template("home.html", date=date.strftime("%A, %d %B"), year=date.year)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    # if form.validate_on_submit():
    if request.method == "POST":
        new_user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=request.form['password']
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("signup.html", form=form, current_user=current_user, year=date.year)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # if form.validate_on_submit():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        # Changed this 👇
        # existing_user = User.query.filter_by(email=email).first()
        existing_user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one()
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
    # user_list_db = TodoList.query.filter_by(user_id=current_user.id).first()
    user_list_db = db.session.execute(db.select(TodoList).filter_by(user_id=current_user)).scalar_one()
    if user_list_db:
        return redirect(url_for("success"))
    form = TodoListForm()
    # if form.validate_on_submit():
    if request.method == "POST":
        user_list = request.form["todo_list"]
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
    all_of_the_list = db.session.execute(db.select(TodoList).filter_by(user_id=current_user)).scalar_one()
    # all_of_the_list = TodoList.query.filter_by(user_id=current_user.id).first()
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
    list_to_delete = db.session.execute(db.select(TodoList).filter_by(user_id=user_id_list)).scalar_one()
    # list_to_delete = TodoList.query.filter_by(user_id=user_id_list).first()
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for("todo"))


@app.route("/delete/<int:user_id_list>", methods=['GET', 'POST'])
def delete(user_id_list):
    list_to_delete = db.session.execute(db.select(TodoList).filter_by(user_id=user_id_list)).scalar_one()
    # list_to_delete = TodoList.query.filter_by(user_id=user_id_list).first()
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
            connection.login("bahaeassaoui23@gmail.com", "ufyd prcu mgwk ezka")
            connection.sendmail(
                from_addr="bahaeassaoui23@gmail.com",
                to_addrs="bahaeassaoui23@gmail.com",
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
