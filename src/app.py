from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def hello():
    tmpl = render_template('index.html')
    return tmpl

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
