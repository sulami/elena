from flask import Flask

from elena.util import Debug

app = Flask("elena")

@app.route("/")
def index():
    Debug("Called index")
    return "Hello there!"

if __name__ == "__main__":
    app.run()

