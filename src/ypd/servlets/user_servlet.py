from flask import flash, redirect, render_template, request, url_for
from flask_classy import FlaskView, route
from flask_login import login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from ypd.form.user_form import LoginForm, RegistrationForm
from ypd.model.user import User

"""A class that represents User creation routes"""
class UserView(FlaskView):
    # Routes work
    @route('/login/', methods=['POST', 'GET'])
    def login(self):
        form = LoginForm()
        if request.method == 'POST' and form.validate_on_submit:
            try:
                user = User.log_in(username=form.username.data, password=form.password.data)
                login_user(user, remember=form.remember.data)
                return redirect(url_for('IndexView:get'))
            except ValueError as e:
                flash(str(e))

        return render_template('login.html', form=form)

    @login_required
    def logout(self):
        logout_user()
        return redirect(url_for('UserView:login'))

    # Routes work
    @route('/signup/', methods=['POST', 'GET'])
    def signup(self):
        form = RegistrationForm()
        if request.method == 'POST' and form.validate_on_submit:
            try:
                user = User.sign_up(form.username.data, form.password.data, form.username.data)
                login_user(user, remember=True)
                return redirect(url_for('IndexView:get'))
            except IntegrityError:
                flash(f'"{form.username.data}" already has an account')
            except ValueError:
                flash(f'You must select an account type')

        return render_template('signup.html', form=form)
