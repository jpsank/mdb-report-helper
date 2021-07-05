from app import db


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

    relevant = db.Column(db.String, nullable=True)  # relevant, irrelevant, None

    def is_relevant(self):
        if self.relevant is None:
            return -1
        return 1 if self.relevant.lower() == 'yes' else 0 if self.relevant.lower() == 'no' else -1

    def serialize(self):
        # return {'Docnumber': self.doc_nbr,
        #         'Family': self.family,
        #         'Pub Date': self.pub_date,
        #         'App Date': self.app_date,
        #         'Pub Country': self.pub_country,
        #         'Pub Kind': self.pub_kind,
        #         'PV Assignee': self.pv_assignee,
        #         'Original Assignee': self.original_assignee,
        #         'INPADOC Assignee': self.inpadoc_assignee,
        #         'Inventor': self.inventor,
        #         'CPC Sub Group': self.cpc_subgroup,
        #         ' Title': self.title,
        #         'Abstract': self.abstract,
        #         'Google Patents Link': self.google_patents_link,
        #         'Notes': self.notes,
        #         'Relevant? (yes/no)': self.relevant}
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
                'relevant': self.relevant}

