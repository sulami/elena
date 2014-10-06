from flask import Flask

app = Flask("elena")

@app.route("/")
def index():
    return "Hello there!"

if __name__ == "__main__":
    app.run()

