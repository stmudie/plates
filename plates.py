from flask import Flask, render_template

app = Flask(__name__, static_folder='static')


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/client')
def client():
    return render_template('client.html')

@app.route('/epics')
def epics():
    return render_template('epics.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
