import re
from itertools import groupby
from operator import attrgetter
import pandas as pd
from flask import flash, redirect, url_for, request, make_response, current_app, render_template
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
from flask_login import login_required, current_user

import os
from app import db
from app.blueprints.main import bp
from app.models import Patent
from config import DB_TO_EXCEL, DB_TO_EXCEL_RE, DB_COLUMNS

from app.util.helpers import allowed_file, redirect_url


def paginate(items, per_page):
    page = request.args.get('page', 1, type=int)
    items = items.paginate(page, per_page, False)

    kwargs = request.values.copy()
    if "page" in kwargs:
        del kwargs["page"]

    next_url = url_for(request.endpoint, **kwargs, page=items.next_num) if items.has_next else None
    prev_url = url_for(request.endpoint, **kwargs, page=items.prev_num) if items.has_prev else None
    return items, next_url, prev_url


@bp.route('/', methods=["GET"])
@login_required
def index():
    patents = Patent.query_by_current_user()

    filters = {}
    for field in DB_COLUMNS:
        if values := request.args.getlist(field):
            searches = []
            for value in values:
                searches += value.split("|")
            filters[field] = searches

            condition = or_()
            for search in searches:
                if search.lower() == 'none':
                    condition = or_(condition, getattr(Patent, field).__eq__(None))
                else:
                    condition = or_(condition, getattr(Patent, field).like(f'%{search}%'))
            patents = patents.filter(condition)
        elif field == 'relevant':
            patents = patents.filter(Patent.is_not_marked)

    if (search := request.args.get('search')) and search != '':
        condition = or_(getattr(Patent, field).like(f'%{search}%') for field in DB_COLUMNS)
        patents = patents.filter(condition)

    patents, next_url, prev_url = paginate(patents, per_page=50)

    return render_template('main/index.html', patents=patents.items, pages=patents.pages, num_patents=patents.total,
                           next_url=next_url, prev_url=prev_url, search=search, filters=filters)


@bp.route('/cleansing', methods=["GET"])
@login_required
def cleansing():
    combos = db.session.query(Patent.family, Patent.pv_assignee, Patent.original_assignee, Patent.inpadoc_assignee,
                              Patent.final_assignee, Patent.type). \
        filter(Patent.user_id == current_user.id, Patent.is_marked_relevant). \
        group_by(Patent.pv_assignee, Patent.original_assignee, Patent.inpadoc_assignee). \
        order_by(Patent.family)

    combos, next_url, prev_url = paginate(combos, per_page=50)

    families_combos = {k: list(g) for k, g in groupby(combos.items, attrgetter('family'))}

    return render_template("main/cleansing.html", families_combos=families_combos,
                           pages=combos.pages, next_url=next_url, prev_url=prev_url)


@bp.route('/cleansing/auto', methods=["GET"])
@login_required
def cleansing_auto():
    patents = Patent.query_by_current_user().filter(Patent.is_marked_relevant)

    for p in patents:
        if p.final_assignee is None:
            for assignee in (p.pv_assignee, p.inpadoc_assignee, p.original_assignee):
                if assignee and assignee.lower() != "unknown":
                    p.final_assignee = assignee
                    break
        if p.final_assignee is not None and p.type is None:
            bef, aft = r"(^|\s)", r"(\s|,|$)"  # To match as a word rather than possibly part of an unrelated word
            if re.search(rf"{bef}(Company|Corporation|((Limited|Ltd|L\.?L\.?C|Inc|Corp|S\.?A)\.?)){aft}",
                         p.final_assignee, re.IGNORECASE):
                p.type = "Company"
            elif re.search(rf"{bef}University|College{aft}", p.final_assignee, re.IGNORECASE):
                p.type = "University"
            elif re.search(rf"{bef}Agency|National|Bureau|Federal|Ministry{aft}", p.final_assignee, re.IGNORECASE):
                p.type = "Federal Agency"
        db.session.merge(p)
    db.session.commit()

    return redirect(redirect_url())


@bp.route('/cleansing/clear', methods=["GET"])
@login_required
def cleansing_clear():
    patents = Patent.query_by_current_user().filter(Patent.is_marked_relevant)

    for p in patents:
        p.final_assignee = None
        p.type = None
        db.session.merge(p)
    db.session.commit()

    return redirect(redirect_url())


@bp.route('/cleansing', methods=["POST"])
@login_required
def cleansing_post():
    families = request.form.getlist('family[]')
    final_assignees = request.form.getlist('final_assignee[]')
    types = request.form.getlist('type[]')

    # Process only the families with any non-empty input fields
    form_data = {families[i]: (final_assignees[i], types[i]) for i in range(len(families))
                 if final_assignees[i] or types[i]}

    # Select combinations of pv_assignee, original_assignee, and inpadoc_assignee from patents that
    # are in the family and marked relevant (as shown in the /cleansing page), as long as the
    # combination is not none, none, none
    combos = db.session.query(Patent.family, Patent.pv_assignee,
                              Patent.original_assignee, Patent.inpadoc_assignee).filter(
        Patent.user_id == current_user.id,
        Patent.is_marked_relevant,
        Patent.family.in_(form_data.keys()),
        ~and_(Patent.pv_assignee == None, Patent.original_assignee == None, Patent.inpadoc_assignee == None)
    ).group_by(
        Patent.pv_assignee, Patent.original_assignee, Patent.inpadoc_assignee
    ).all()

    # Map all combinations to their correct family
    combo_to_family = {tuple(combo): family for (family, *combo) in combos}

    # Match patents in the family as well as patents with the same pv_assignee, original_assignee,
    # and inpadoc_assignee combo as any patent in the family
    matches_any_combo = or_(
        and_(Patent.pv_assignee == x, Patent.original_assignee == y, Patent.inpadoc_assignee == z)
        for _, x, y, z in combos
    )
    patents = Patent.query_by_current_user().filter(
        or_(Patent.family.in_(form_data.keys()), matches_any_combo)
    )

    for p in patents:
        if (family := p.family) not in form_data:
            family = combo_to_family[(p.pv_assignee, p.original_assignee, p.inpadoc_assignee)]
        final_assignee, type_ = form_data[family]
        p.final_assignee = final_assignee if final_assignee else None
        p.type = type_ if type_ else None
        db.session.merge(p)
    db.session.commit()

    return redirect(redirect_url())


@bp.route('/exports', methods=["GET", "POST"])
@login_required
def exports():
    if request.method == "POST":
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

            return merge_and_export(path)
    return render_template("main/exports.html")


def merge_and_export(path):
    # Import dataframe, actually a CSV
    excel_df = pd.read_csv(path)

    # Build translation table for column headers
    translate = {}
    for db_col in ["doc_nbr", "relevant", "final_assignee", "type"]:
        excel_col = DB_TO_EXCEL[db_col]
        if excel_col in excel_df.columns:
            translate[db_col] = excel_col
        else:
            regex = DB_TO_EXCEL_RE[db_col]
            for col in excel_df.columns:
                if regex.fullmatch(col):
                    translate[db_col] = col
                    break

        # Add column if not found
        if db_col not in translate:
            excel_df[excel_col] = ""
            translate[db_col] = excel_col

    # Export db to dataframe and translate columns
    patents = Patent.query_by_current_user().all()
    data = [p.serialize() for p in patents]
    df2 = pd.DataFrame(data)
    df2 = df2[translate.keys()]
    df2 = df2.rename(columns=translate)

    # Update using index
    excel_df = excel_df.set_index(translate["doc_nbr"])
    df2 = df2.set_index(translate["doc_nbr"])
    excel_df.update(df2)

    # Make response
    resp = make_response(excel_df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp


@bp.route('/export', methods=["GET"])
@login_required
def export():
    patents = Patent.query_by_current_user()
    if 'relevant' in request.args:
        patents = patents.filter(Patent.is_marked_relevant)
    columns = request.args.getlist("columns")
    data = [p.serialize_excel(columns) for p in patents.all()]
    df = pd.DataFrame(data)
    resp = make_response(df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

