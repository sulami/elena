from flask import Flask, request

from elena.database import Database
from elena.models import BooleanStatus, NumberStatus

from config import DefaultConfig

app = Flask("elena")
app.config.from_object('config.DefaultConfig')

def init_db():
    app.db = Database(app.config['DB_URI'])

@app.teardown_appcontext
def shutdown_session(exception=None):
    app.db.db_session.remove()

@app.route("/")
def index():
    return "Are you still there?"

@app.route("/new/", methods=['POST'])
def new_status():
    name = request.form['name']
    type = request.form['type']
    if type == "bool":
        status = BooleanStatus(name, True)
        app.db.db_session.add(status)
        app.db.db_session.commit()
    return "Success!"

@app.route("/get/<string:name>/")
def query_status(name):
    try:
        return str(BooleanStatus.query.filter(BooleanStatus.name == name)
                   .first().get_status())
    except AttributeError:
        return "ERROR: This status does not exist", 404

if __name__ == "__main__":
    app.run()

