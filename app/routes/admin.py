import pandas as pd
from flask import flash, redirect, url_for, request, \
    send_from_directory, current_app
from werkzeug.utils import secure_filename

import os
from app import app, db
from app.models import Patent
from app.populate import populate
from app.forms import AdminPassForm

from .util import is_admin, login_admin, logout_admin, render_template_w_admin, redirect_url, allowed_file,\
    admin_required


@app.route('/vote/<relevant>/<pid>', methods=["GET"])
@admin_required
def vote(relevant, pid):
    patent1 = Patent.query.get(pid)
    if patent1 is None:
        flash('Patent not found.')
        return redirect(url_for('index'))

    patents = Patent.query.filter(Patent.family == patent1.family)

    if relevant == "undecided":
        relevant = None
    elif relevant != "yes" and relevant != "no":
        flash(f'Invalid choice "{relevant}" for relevance. Must be "yes", "no", or "undecided"')
        return redirect(redirect_url())

    for patent in patents:
        patent.relevant = relevant
        db.session.merge(patent)

    db.session.commit()

    return redirect(redirect_url())


@app.route('/admin', methods=["GET", "POST"])
@admin_required
def admin():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(redirect_url())

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(redirect_url())
        if file and allowed_file(file.filename, {'csv'}):
            filename = secure_filename(file.filename)
            path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            populate(path)
            return redirect(redirect_url())
    return render_template_w_admin("admin.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin():
        return redirect(redirect_url())
    form = AdminPassForm()
    if form.validate_on_submit():
        if form.password.data == current_app.config['ADMIN_PASS']:
            login_admin()
            return redirect(url_for('admin'))
        else:
            flash('Invalid password')
            return redirect(url_for('login'))
    return render_template_w_admin('login.html', form=form)


@app.route('/logout')
@admin_required
def logout():
    logout_admin()
    return redirect(redirect_url())


@app.route('/uploads/<name>', methods=["GET"])
@admin_required
def download_file(name):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], name)


@app.route('/reset_db', methods=["GET"])
@admin_required
def reset_db():
    db.drop_all()
    db.create_all()
    return redirect(redirect_url())



