import connexion

app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api('api.yaml')
app.run(port=9999)


def trigger_sched():
    return 'success'


if __name__ == '__main__':
    app.run(debug=True)
