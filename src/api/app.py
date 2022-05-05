import connexion


app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api('api.yaml', arguments={'title': 'Evolutionary Manufacturing Scheduler API'}, pythonic_params=True)


if __name__ == '__main__':
    app.run(debug=True, port=9997)
