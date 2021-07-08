import re
import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

# Flask-SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Session
SESSION_TYPE = 'sqlalchemy'


UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')


# Translating column names from Excel

DB_COLUMNS = (
    'doc_nbr', 'family', 'pub_date', 'app_date', 'pub_country', 'pub_kind', 'pv_assignee', 'original_assignee',
    'inpadoc_assignee', 'inventor', 'cpc_subgroup', 'title', 'abstract', 'google_patents_link', 'final_assignee',
    'type', 'relevant', 'notes'
)
EXCEL_COLUMNS = (
    'Docnumber', 'Family', 'Pub Date', 'App Date', 'Pub Country', 'Pub Kind', 'PV Assignee', 'Original Assignee',
    'INPADOC Assignee', 'Inventor', 'CPC Sub Group', 'Title', 'Abstract', 'Google Patents Link', 'Final Assignee',
    'Type', 'Relevant? (yes/no)', 'Notes'
)

DB_TO_EXCEL = {k: v for k, v in zip(DB_COLUMNS, EXCEL_COLUMNS)}
DB_TO_EXCEL_RE = {
    'doc_nbr': re.compile(r"(Doc\.?|Document|Patent|Priority)\s?(Number|Nbr\.?|No\.?)", re.IGNORECASE),
    'final_assignee': re.compile("Final Assignee", re.IGNORECASE),
    'type': re.compile("Type", re.IGNORECASE),
    'relevant': re.compile(r"(Relevant)\??\s?(\(yes/no\))?", re.IGNORECASE)
}

EXCEL_TO_DB = {k: v for k, v in zip(EXCEL_COLUMNS, DB_COLUMNS)}
EXCEL_TO_DB.update({
    " Title": "title",
    "Assignee": "final_assignee",
})


