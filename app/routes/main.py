import re

import pandas as pd
from flask import flash, redirect, url_for, request, make_response, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import or_

import os
from app import app, db
from app.models import Patent

from .util import render_template_w_admin, allowed_file, redirect_url


def paginate(items, per_page):
    page = request.args.get('page', 1, type=int)
    items = items.paginate(page, per_page, False)

    kwargs = request.values.copy()
    if "page" in kwargs:
        del kwargs["page"]

    next_url = url_for(request.endpoint, **kwargs, page=items.next_num) if items.has_next else None
    prev_url = url_for(request.endpoint, **kwargs, page=items.prev_num) if items.has_prev else None
    return items, next_url, prev_url


@app.route('/', methods=["GET"])
def index():
    patents = db.session.query(Patent)

    fields = ['doc_nbr', 'family', 'pub_date', 'app_date', 'pub_country', 'pub_kind', 'pv_assignee',
              'original_assignee', 'inpadoc_assignee', 'inventor', 'cpc_subgroup', 'title', 'abstract',
              'google_patents_link', 'relevant', 'notes']
    filters = {}
    for field in fields:
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
            patents = patents.filter(Patent.relevant.__eq__(None))

    if (search := request.args.get('search')) and search != '':
        condition = or_(getattr(Patent, field).like(f'%{search}%') for field in fields)
        patents = patents.filter(condition)

    patents, next_url, prev_url = paginate(patents, per_page=50)

    return render_template_w_admin('index.html', patents=patents.items, next_url=next_url, prev_url=prev_url,
                                   num_patents=patents.total, search=search, filters=filters)


@app.route('/exports', methods=["GET", "POST"])
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
    return render_template_w_admin("exports.html")


def merge_and_export(path):
    df = pd.read_csv(path)

    patents = Patent.query.all()
    data = [p.serialize() for p in patents]
    df2 = pd.DataFrame(data)

    doc_nbr_h = "Docnumber"
    relevant_h = "Relevant? (yes/no)"

    def find_column(regex):
        for col in df.columns:
            if regex.fullmatch(col):
                return col
        return None

    if doc_nbr_h not in df.columns:
        pattern = re.compile(r"(doc|document|patent|priority)\s?(number|nbr|no)", re.IGNORECASE)
        doc_nbr_h = find_column(pattern)

    if relevant_h not in df.columns:
        pattern = re.compile(r"(relevant)\??\s?(\(yes/no\))?", re.IGNORECASE)
        relevant_h = find_column(pattern)

    if doc_nbr_h is None or relevant_h is None:
        flash("Invalid format of uploaded file")
        return redirect(redirect_url())

    df2 = df2[["doc_nbr", "relevant"]]
    df2 = df2.rename(columns={"doc_nbr": doc_nbr_h, "relevant": relevant_h})

    df = df.set_index(doc_nbr_h)
    df2 = df2.set_index(doc_nbr_h)

    df.update(df2)
    resp = make_response(df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp


@app.route('/export', methods=["GET"])
def export():
    patents = Patent.query.all()
    data = [p.serialize() for p in patents]
    df = pd.DataFrame(data)
    resp = make_response(df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

