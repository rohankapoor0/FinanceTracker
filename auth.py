from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import UserModel, db
from flask_login import login_user, logout_user, login_required

# Authentication module
auth = Blueprint('auth', __name__)

class AuthService:
    """Service for handling authentication operations."""
    @staticmethod
    def login_user(username, password):
        user = UserModel.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return True
        return False

    @staticmethod
    def register_user(username, email, password):
        if UserModel.query.filter_by(username=username).first():
            return False
        new_user = UserModel(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return True

    @staticmethod
    def logout_user():
        logout_user()
