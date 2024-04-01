import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

app = Flask(__name__)


class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE")
db = SQLAlchemy(model_class=Base)
db.init(app)


class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    password = Column(String(250), nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    tasks = relationship("Task")


class Task(db.Model):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    deadline = Column(DateTime, nullable=False)
    finished = Column(DateTime, default=None, nullable=False)
    is_done = Column(Boolean, nullable=False)
    author = relationship("User", back_populates="tasks")


def main():
    pass


def add_user():
    pass


def authorize():
    pass


def create_task():
    pass


def update_task():
    pass


def delete_task():
    pass


def show_statistic():
    pass


if __name__ == "__main__":
    main()
