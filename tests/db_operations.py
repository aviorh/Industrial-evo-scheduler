from src.api.app import create_app
from src.database.models import *

app = create_app()

app.app.app_context().push()


def update_schema():
    db.create_all()


def delete_all_site_data():
    db.session.query(SiteData).delete()
    db.session.commit()


def delete_all_problems():
    db.session.query(Problem).delete()
    db.session.commit()


def delete_all_solutions():
    db.session.query(Solution).delete()
    db.session.commit()


def clear_db():
    delete_all_problems()
    delete_all_site_data()
    delete_all_solutions()
