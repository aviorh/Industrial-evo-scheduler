import connexion

app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api('api.yaml')


if __name__ == '__main__':
    app.run(debug=True, port=9997)
