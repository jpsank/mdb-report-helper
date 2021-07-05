import pandas as pd

from app.models import Patent
from app import db


TRANSLATE = {
    'Docnumber': 'doc_nbr',
    'Family': 'family',
    'Pub Date': 'pub_date',
    'App Date': 'app_date',
    'Pub Country': 'pub_country',
    'Pub Kind': 'pub_kind',
    'Assignee': 'pv_assignee',
    'PV Assignee': 'pv_assignee',
    'Original Assignee': 'original_assignee',
    'INPADOC Assignee': 'inpadoc_assignee',
    'Inventor': 'inventor',

    # CPC info redundant
    'CPC Section': None,
    'CPC Main Class': None,
    'CPC Sub Class': None,
    'CPC Main Group': None,
    'CPC Sub Group': 'cpc_subgroup',

    ' Title': 'title',
    'Title': 'title',
    'Abstract': 'abstract',
    'Google Patents Link': 'google_patents_link',
    'Relevant? (yes/no)': 'relevant',
    'Notes': 'notes',

    # Delete unused data
    'Unnamed: 22': None,
    'First pub year': None,
    '#': None,
    'count': None,
}

# DATA_PATH = os.path.join(current_dir, '..', 'data/Yale University.xlsx - Raw data.csv')


def populate(data_path):
    patent_df = pd.read_csv(data_path)
    patent_df = patent_df.rename(columns=TRANSLATE)
    patent_df = patent_df.drop(columns=[None])

    # print(patent_df.columns)
    # print(patent_df)

    for (index, series) in patent_df.iterrows():
        patent = Patent(**series)
        db.session.merge(patent)

    db.session.commit()
