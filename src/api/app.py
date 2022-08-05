import connexion
from src.database.database import db


def create_app():
    connexion_app = connexion.FlaskApp(__name__, specification_dir='./')
    connexion_app.add_api('api.yaml', arguments={'title': 'Evolutionary Manufacturing Scheduler API'}, pythonic_params=True)

    app = connexion_app.app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/avior/Desktop/GIT/industrial-evo-scheduler/iplanner_new1.db'
    db.init_app(app)

    return connexion_app


if __name__ == '__main__':
    app = create_app()
    app.app.app_context().push()
    app.run(debug=True, port=9997)
