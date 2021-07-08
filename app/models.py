from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, or_, and_, not_, select


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

    def serialize(self):
        return {'doc_nbr': self.doc_nbr,
                'family': self.family,
                'pub_date': self.pub_date,
                'app_date': self.app_date,
                'pub_country': self.pub_country,
                'pub_kind': self.pub_kind,
                'pv_assignee': self.pv_assignee,
                'original_assignee': self.original_assignee,
                'inpadoc_assignee': self.inpadoc_assignee,
                'inventor': self.inventor,
                'cpc_subgroup': self.cpc_subgroup,
                'title': self.title,
                'abstract': self.abstract,
                'google_patents_link': self.google_patents_link,
                'notes': self.notes,
                'final_assignee': self.final_assignee,
                'type': self.type,
                'relevant': self.relevant}

    def serialize_formal(self):
        return {'Docnumber': self.doc_nbr,
                'Family': self.family,
                'Pub Date': self.pub_date,
                'App Date': self.app_date,
                'Pub Country': self.pub_country,
                'Pub Kind': self.pub_kind,
                'PV Assignee': self.pv_assignee,
                'Original Assignee': self.original_assignee,
                'INPADOC Assignee': self.inpadoc_assignee,
                'Inventor': self.inventor,
                'CPC Sub Group': self.cpc_subgroup,
                'Title': self.title,
                'Abstract': self.abstract,
                'Google Patents Link': self.google_patents_link,
                'Notes': self.notes,
                'Final Assignee': self.final_assignee,
                'Type': self.type,
                'Relevant? (yes/no)': self.relevant}

