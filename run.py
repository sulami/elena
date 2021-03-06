from datetime import timedelta

from flask import Flask, request

from elena.database import Database
from elena.models import Status
from elena.util import str_to_bool

from config import DefaultConfig

app = Flask("elena")
app.config.from_object('config.DefaultConfig')

def init_db():
    app.db = Database(app.config['DB_URI'])

@app.teardown_appcontext
def shutdown_session(exception=None):
    app.db.session.remove()

@app.route("/")
def index():
    status = Status.query.all()
    r = ''
    for s in status:
        r += s.__repr__() + "\n"
    return r

@app.route("/set/<string:name>/", methods=['POST'])
def set_status(name):
    value = request.form['value']
    status = Status.query.get(name)
    if status:
        status.set(value)
    else:
        status = Status(name, value)
    app.db.session.add(status)
    app.db.session.commit()
    return "Success!", 201

@app.route("/get/<string:name>/")
def get_status(name):
    status = Status.query.get(name)
    if status:
        if status.pull:
            status.pull_update()
            app.db.session.add(status)
            app.db.session.commit()
        return status.get(), 200
    return "ERROR: This status does not exist", 404

@app.route("/his/<string:name>/")
def get_history(name):
    status = Status.query.get(name)
    if status:
        if status.pull:
            status.pull_update()
            app.db.session.add(status)
            app.db.session.commit()
        return status.get_history(), 200
    return "ERROR: This status does not exist", 404

@app.route("/del/<string:name>/")
def del_status(name):
    status = Status.query.get(name)
    if status:
        app.db.session.delete(status)
        app.db.session.commit()
        return "Success!", 204
    return "ERROR: This status does not exist", 404

@app.route("/atr/<string:name>/", methods=['POST'])
def set_attr(name):
    status = Status.query.get(name)
    valid = False
    if not status:
        return "ERROR: This status does not exist", 404
    if 'history' in request.form:
        valid = True
        status.history = str_to_bool(request.form['history'])
        for d in status.data_points.offset(1):
            app.db.session.delete(d)
    if 'pull' in request.form:
        valid = True
        if str_to_bool(request.form['pull']):
            if 'pull_url' in request.form:
                status.pull_url = request.form['pull_url']
            elif not status.pull_url:
                return "ERROR: No URL to pull from given or present", 400
            if 'pull_time' in request.form:
                status.pull_time = timedelta(0, int(request.form['pull_time']))
            elif not status.pull_time:
                return "ERROR: No pull interval given or present", 400
            status.pull = True
        else:
            status.pull = False
    else:
        if 'pull_url' in request.form:
            valid = True
            status.pull_url = request.form['pull_url']
        if 'pull_time' in request.form:
            valid = True
            status.pull_time = timedelta(seconds=int(request.form['pull_time']))
    if not valid:
        return "ERROR: No valid attribute given", 400
    app.db.session.add(status)
    app.db.session.commit()
    return "Success!", 200

@app.route("/status/")
def statusreport():
    # TODO elaborate status report
    return "Number of Stati:" + str(len(Status.query.all())), 200

if __name__ == "__main__":
    init_db()
    app.run()

