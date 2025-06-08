from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from pydantic import ValidationError

from aitravel_app.services.user_service import UserService, UserAlreadyExistsError
from aitravel_app.schemas.user_schemas import UserCreateSchema

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('map.index'))
    if request.method == 'POST':
        try:
            form_data = request.form
            if not form_data.get('username') or not form_data.get('password'):
                flash("Username and password are required.", 'danger')
                return render_template('register.html'), 400

            user_data = UserCreateSchema(username=form_data.get('username'), password=form_data.get('password'))
            UserService.create_user(user_data)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except ValidationError as e:
            errors = e.errors()
            for error in errors:
                flash(f"Validation Error for {error['loc'][0]}: {error['msg']}", 'danger')
        except UserAlreadyExistsError as e:
            flash(str(e), 'danger')
        except Exception as e:
            current_app.logger.error(f"Registration error: {e}", exc_info=True)
            flash('An unexpected error occurred during registration.', 'danger')
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('map.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('login.html'), 400

        user = UserService.check_user_credentials(username, password)
        if user:
            login_user(user, remember=request.form.get('remember') == 'on')
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('map.index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
