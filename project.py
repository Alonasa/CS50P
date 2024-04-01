import os
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms.fields.simple import EmailField, PasswordField, SubmitField
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
    deadline = Column(DateTime, nullable=False)
    finished = Column(DateTime, default=None, nullable=False)
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


class RegisterForm(BaseForm):
    submit = SubmitField("Register", render_kw={"class": "btn-warning btn-sm mt-3"})


class LoginForm(BaseForm):
    submit = SubmitField("Login", render_kw={"class": "btn-warning btn-sm mt-3"})


@app.route('/')
def main():
    return render_template("base.html")


def add_user():
    pass


@app.route('/authorize', methods=["POST", "GET"])
def authorize():
    form = LoginForm()
    if request.method == "POST":
        new_user = User(password=form.password.data.strip(), email=form.email.data.strip())

        db.session.add(new_user)
        db.session.commit()

    return render_template("base-form.html", form=form)


def create_task():
    pass


def update_task():
    pass


def delete_task():
    pass


def show_statistic():
    pass


if __name__ == "__main__":
    app.run(port=4000, debug=True)
