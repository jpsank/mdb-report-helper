from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, or_, and_

from config import DB_COLUMNS, DB_TO_EXCEL


class Patent(db.Model):
    __tablename__ = 'patents'

    id = db.Column(db.Integer, primary_key=True)

    doc_nbr = db.Column(db.String)
    family = db.Column(db.String, nullable=True)
    pub_date = db.Column(db.String, nullable=True)
    app_date = db.Column(db.String, nullable=True)
    pub_country = db.Column(db.String, nullable=True)
    pub_kind = db.Column(db.String, nullable=True)
    pv_assignee = db.Column(db.String, nullable=True)
    original_assignee = db.Column(db.String, nullable=True)
    inpadoc_assignee = db.Column(db.String, nullable=True)
    inventor = db.Column(db.String, nullable=True)
    cpc_section = db.Column(db.String, nullable=True)
    cpc_main_class = db.Column(db.String, nullable=True)
    cpc_sub_class = db.Column(db.String, nullable=True)
    cpc_main_group = db.Column(db.String, nullable=True)
    cpc_subgroup = db.Column(db.String, nullable=True)
    title = db.Column(db.String)
    abstract = db.Column(db.String)
    google_patents_link = db.Column(db.String)

    # General notes field if available
    notes = db.Column(db.String, nullable=True)

    final_assignee = db.Column(db.String, nullable=True)
    type = db.Column(db.String, nullable=True)  # University, Company, Federal Agency, Independent Inventor
    relevant = db.Column(db.String, nullable=True)  # Yes, no, None

    @hybrid_property
    def is_marked_relevant(self):
        if self.relevant is None:
            return False
        return self.relevant.lower() == "yes"

    @is_marked_relevant.expression
    def is_marked_relevant(self):
        return and_(
            ~Patent.relevant.is_(None),
            func.lower(Patent.relevant) == "yes"
        )

    @hybrid_property
    def is_marked_irrelevant(self):
        if self.relevant is None:
            return False
        return self.relevant.lower() == "no"

    @is_marked_irrelevant.expression
    def is_marked_irrelevant(self):
        return and_(
            ~Patent.relevant.is_(None),
            func.lower(Patent.relevant) == "no"
        )

    @hybrid_property
    def is_not_marked(self):
        if self.relevant is None:
            return True
        return self.relevant.lower() not in ("yes", "no")

    @is_not_marked.expression
    def is_not_marked(self):
        return or_(
            Patent.relevant.is_(None),
            ~func.lower(Patent.relevant).in_(("yes", "no"))
        )

    def relevant_status(self):
        """ Return 1 if relevant, 0 if not relevant, and -1 if unknown """
        if self.relevant is None:
            return -1
        return 1 if self.relevant.lower() == "yes" else 0 if self.relevant.lower() == "no" else -1

    def serialize(self, columns=()):
        if columns:
            return {col: getattr(self, col) for col in columns if col in DB_COLUMNS}
        return {col: getattr(self, col) for col in DB_COLUMNS}

    def serialize_excel(self, columns=()):
        if columns:
            return {DB_TO_EXCEL[col]: getattr(self, col) for col in columns if col in DB_COLUMNS}
        return {excel_col: getattr(self, db_col) for db_col, excel_col in DB_TO_EXCEL.items()}
