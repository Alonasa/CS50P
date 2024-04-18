import datetime
import os
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms.fields.datetime import DateTimeField
from wtforms.fields.simple import EmailField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
csrf = CSRFProtect(app)
Bootstrap(app)
app.config['SECRET_KEY'] = os.environ.get("SEC_KEY")


class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    password = Column(String(250), nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    tasks = relationship("Task")

    def __init__(self, email, password, tasks=None):
        self.email = email
        self.password = password
        self.tasks = tasks or []

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Task(db.Model):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    title = Column(String(250), nullable=False)
    deadline = Column(DateTime, default=None)
    finished = Column(DateTime, default=None)
    is_done = Column(Boolean, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="tasks")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


class BaseForm(FlaskForm):
    email = EmailField("Your Email", validators=[DataRequired()], render_kw={"placeholder": "e-mail"})
    password = PasswordField("Your Password", validators=[DataRequired(), Length(min=8)],
                             render_kw={"placeholder": "password at least 8 chars"})


def yellow_submit(title):
    return SubmitField(title, render_kw={"class": "btn-warning btn-sm mt-3"})


class RegisterForm(BaseForm):
    submit = yellow_submit("Register")


class LoginForm(BaseForm):
    submit = yellow_submit("Login")


class AddTaskForm(FlaskForm):
    title = StringField("Task Title", validators=[DataRequired()],
                        render_kw={"placeholder": "Task title, min length 2"})
    deadline = DateTimeField("Deadline Date", format="%Y-%m-%d", validators=[DataRequired()],
                             render_kw={"placeholder": "YYYY-MM-DD"})
    submit = yellow_submit("Add task")


@app.route('/')
def main():
    return render_template("base.html")


def add_user(password, email):
    new_user = User(password=password, email=email)
    db.session.add(new_user)
    db.session.commit()
    db.session.close()


@app.route("/authorize", methods=["GET", "POST"])
def authorize():
    form = RegisterForm()
    form_email = form.email.data
    form_password = form.password.data

    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(email=form_email.strip()).first()

        if user:
            flash("You are already have an account.... Redirecting to login.....".title())
            return redirect(url_for("login"))
        add_user(form_password.strip(), form_email.strip())
        flash("New user added to the system".title())

    return render_template("login.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    password = request.form.get("password")
    email = request.form.get("email")

    if request.method == "POST" and form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user and user.password == password:
            session['user_id'] = user.id  # Storing user_id in session
            flash('Authorized in the system'.title())
            form = AddTaskForm()
            if 'user_id' not in session:
                flash("You are not logged in.")
                return redirect(url_for("login"))

            if request.method == "POST" and form.validate_on_submit():
                new_task = Task(
                    date=datetime.datetime.now().date(),
                    title=form.title.data,
                    deadline=form.deadline.data,
                    is_done=False,
                    author_id=session['user_id']
                )
                db.session.add(new_task)
                db.session.commit()
                flash("New Task Added")
            return render_template("show-tasks.html", tasks=get_tasks(), form=form)
        else:
            flash('Some of the fields is wrong'.title())

    return render_template("login.html", form=form)


@app.route("/add-task", methods=["POST", "GET"])
def create_task():
    form = AddTaskForm()
    if 'user_id' not in session:
        flash("You are not logged in.")
        return redirect(url_for("login"))

    if request.method == "POST" and form.validate_on_submit():
        new_task = Task(
            date=datetime.datetime.now().date(),
            title=form.title.data,
            deadline=form.deadline.data,
            is_done=False,
            author_id=session['user_id']
        )
        db.session.add(new_task)
        db.session.commit()
        flash("New Task Added")
        return render_template("show-tasks.html", tasks=get_tasks())

    return render_template("tasks.html", form=form)


def update_task():
    pass


def delete_task():
    pass


def show_statistic():
    pass


def get_tasks():
    user_id = session.get('user_id')
    tasks = Task.query.filter_by(author_id=user_id).all()
    return tasks


@app.route("/tasks")
def show_tasks():
    tasks = get_tasks()
    render_template("show-tasks.html", tasks=tasks)


if __name__ == "__main__":
    app.run(port=4000, debug=True)
