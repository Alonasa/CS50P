import pytest
from unittest.mock import MagicMock
from project import authorize, User
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.app_context():
        db = SQLAlchemy(app)
        db.create_all()

        yield app

        db.drop_all()


def test_authorize(app, mocker):
    mocker.patch('your_module.RegisterForm', MagicMock())
    mocker.patch('your_module.request', MagicMock(form=MagicMock(get=lambda x: 'test@example.com')))
    mocker.patch('your_module.flash', MagicMock())
    mocker.patch('your_module.redirect', MagicMock())
    mocker.patch('your_module.url_for', MagicMock())

    with app.test_request_context(method='POST'):
        authorize()

        # Perform assertions based on the expected behavior of the authorize() function
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None