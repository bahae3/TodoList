from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound
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
    return User.query.get(user_id)


# Creating users table
class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    lists = db.relationship("TodoList", backref="user", lazy=True)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


# Creating To do List table
class TodoList(db.Model):
    __tablename__ = "list"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item = db.Column(db.String, nullable=False)

    def __init__(self, user_id, item):
        self.user_id = user_id
        self.item = item


with app.app_context():
    db.create_all()

date = datetime.now()


@app.route("/")
def home():
    return render_template("home.html", date=date.strftime("%A, %d %B"), year=date.year)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # if request.method == "POST":
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
    if form.validate_on_submit():
        # if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        # Changed this 👇
        existing_user = User.query.filter_by(email=email).first()
        # existing_user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one()
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
    # Fetching items for a specific user ID as a list
    items = [item[0].capitalize() for item in
             TodoList.query.filter_by(user_id=current_user.id).with_entities(TodoList.item).all()]
    length_items_list = len(items)

    form = TodoListForm()
    if form.validate_on_submit():
        user_typed_item = request.form["todo_list"].capitalize()
        new_todo = TodoList(user_id=current_user.id, item=user_typed_item)
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for("todo"))
    return render_template("todo.html", form=form, current_user=current_user, year=date.year, items=items,
                           len=length_items_list)


@app.route("/success")
@login_required
def success():
    items = [item[0].capitalize() for item in
             TodoList.query.filter_by(user_id=current_user.id).with_entities(TodoList.item).all()]
    return render_template("success.html", current_user=current_user, date=date.strftime("%A, %d %B"), year=date.year,
                           items=items)


@app.route("/update/<int:user_id_list>", methods=['GET', 'POST'])
def update(user_id_list):
    # list_to_delete = db.session.execute(db.select(TodoList).filter_by(user_id=user_id_list)).scalar_one()
    list_to_delete = TodoList.query.filter_by(user_id=user_id_list).first()
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for("todo"))


@app.route("/delete/<int:user_id_list>", methods=['GET', 'POST'])
def delete(user_id_list):
    TodoList.query.filter_by(user_id=user_id_list).delete()
    db.session.commit()
    return redirect(url_for("success"))



@app.route("/delete_item/<string:item_to_delete>", methods=['GET', 'POST'])
def delete_item(item_to_delete):
    try:
        item_to_be_deleted = TodoList.query.filter_by(item=item_to_delete).one()
        db.session.delete(item_to_be_deleted)
        db.session.commit()
    except NoResultFound:
        flash("Item not found or already deleted!', 'error")
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
