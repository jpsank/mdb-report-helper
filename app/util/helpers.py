from flask import session, render_template, request, url_for, flash, redirect
from functools import wraps


def allowed_file(filename, extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions


def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


def admin_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if not is_admin():
            flash('You must log in to access this page.')
            return redirect(url_for('admin.login'))
        return fn(*args, **kwargs)
    return decorated_view


def is_admin():
    return 'is_admin' in session


def login_admin():
    session['is_admin'] = ''


def logout_admin():
    session.pop('is_admin')


def render_template_w_admin(*args, **kwargs):
    return render_template(*args, **kwargs, is_admin=is_admin())


def is_valid_name(text):
    """ Checks if name is valid (only ASCII printable characters, no slashes) """
    return all(32 <= ord(ch) <= 126 and ch != '/' for ch in text)


def nl2br(text):
    return text.replace('\n', '<br>')

