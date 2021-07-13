import pandas as pd
from flask import flash, redirect, url_for, request, \
    send_from_directory, current_app, render_template
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

import os
from app import db
from app.blueprints.admin import bp
from app.blueprints.admin.forms import AdminPassForm
from app.models import Patent
from config import EXCEL_TO_DB, DB_COLUMNS

from app.util.helpers import is_admin, login_admin, logout_admin, redirect_url, allowed_file


@bp.route('/vote/<relevant>/<pid>', methods=["GET"])
@login_required
def vote(relevant, pid):
    patent1 = Patent.query.get(pid)
    if patent1 is None:
        flash('Patent not found.')
        return redirect(url_for('main.index'))

    patents = Patent.query_by_current_user().filter(Patent.family == patent1.family)

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


def populate(data_path):
    patents_df = pd.read_csv(data_path)
    patents_df = patents_df.rename(columns=EXCEL_TO_DB)
    patents_df = patents_df.drop(columns=[c for c in patents_df.columns if c not in DB_COLUMNS])

    # print(patents_df.columns)
    # print(patents_df)

    for (index, series) in patents_df.iterrows():
        patent = Patent(**series)
        patent.user_id = current_user.id
        db.session.merge(patent)

    db.session.commit()


@bp.route('/', methods=["GET", "POST"])
@login_required
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
    return render_template("admin/admin.html", is_admin=is_admin())


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin():
        return redirect(redirect_url())
    form = AdminPassForm()
    if form.validate_on_submit():
        if form.password.data == current_app.config['ADMIN_PASS']:
            login_admin()
            return redirect(url_for('admin.admin'))
        else:
            flash('Invalid password')
            return redirect(url_for('admin.login'))
    return render_template('admin/login.html', form=form)


@bp.route('/logout')
def logout():
    if is_admin():
        logout_admin()
    return redirect(redirect_url())


# @bp.route('/uploads/<name>', methods=["GET"])
# def download_file(name):
#     return send_from_directory(current_app.config["UPLOAD_FOLDER"], name)


@bp.route('/clear_data', methods=["GET"])
@login_required
def clear_data():
    Patent.query_by_current_user().delete()
    db.session.commit()
    return redirect(redirect_url())



