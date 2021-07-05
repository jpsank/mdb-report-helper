from flask import session, render_template, request, url_for


def allowed_file(filename, extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions


def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


def is_admin():
    return 'is_admin' in session


def login_admin():
    session['is_admin'] = ''


def logout_admin():
    session.pop('is_admin')


def render_template_w_admin(*args, **kwargs):
    return render_template(*args, **kwargs, is_admin=is_admin())
