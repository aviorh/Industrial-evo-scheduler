import connexion
from flask_cors import CORS

app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api('api.yaml', arguments={'title': 'Evolutionary Manufacturing Scheduler API'}, pythonic_params=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == '__main__':
    app.run(debug=True, port=9997)
