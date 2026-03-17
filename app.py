from flask import Flask, render_template, request
from buildings import locations

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "student" and password == "Student@123":
            return render_template("dashboard.html")
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    result = None

    if request.method == 'POST':
        location = request.form['location']
        result = locations.get(location)

    return render_template("dashboard.html", result=result)


@app.route('/map')
def map():
    return render_template("map.html")


if __name__ == "__main__":
    app.run(debug=True)
