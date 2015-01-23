from flask import Flask, render_template

app = Flask(__name__, static_folder='static')


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/client')
def client():
    return render_template('client.html')

if __name__ == '__main__':
    app.run(debug=True)
