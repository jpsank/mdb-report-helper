import pandas as pd

from app.models import Patent
from app import db
from config import EXCEL_TO_DB, DB_COLUMNS


def populate(data_path):
    patents_df = pd.read_csv(data_path)
    patents_df = patents_df.rename(columns=EXCEL_TO_DB)
    patents_df = patents_df.drop(columns=[c for c in patents_df.columns if c not in DB_COLUMNS])

    # print(patents_df.columns)
    # print(patents_df)

    for (index, series) in patents_df.iterrows():
        patent = Patent(**series)
        db.session.merge(patent)

    db.session.commit()
