import connexion
from src.database.database import db
import os
from flask_cors import CORS


def create_app():
    connexion_app = connexion.FlaskApp(__name__, specification_dir='./')
    connexion_app.add_api('api.yaml', arguments={'title': 'Evolutionary Manufacturing Scheduler API'}, pythonic_params=True)
    CORS(connexion_app.app)
    connexion_app.app.config['CORS_HEADERS'] = 'Content-Type'

    app = connexion_app.app
    current_dir_path = os.path.dirname(__file__)
    current_db_path = f"{current_dir_path}/../../iplanner_new5.db".replace("C:", "")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{current_db_path}'
    db.init_app(app)

    return connexion_app


if __name__ == '__main__':
    app = create_app()
    app.app.app_context().push()
    app.run(debug=True, port=9997)
