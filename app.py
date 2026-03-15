from flask import Flask, render_template, request, redirect, url_for
from buildings import buildings

app = Flask(__name__)

username = "student"
password = "Campus@123"

@app.route("/", methods=["GET","POST"])
def login():

    error = None

    if request.method == "POST":

        user = request.form.get("username")
        pwd = request.form.get("password")

        if user == username and pwd == password:
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/dashboard", methods=["GET","POST"])
def dashboard():

    result = None

    if request.method == "POST":

        location = request.form.get("location")

        if location in buildings:
            result = buildings[location]

    return render_template("dashboard.html", result=result)


@app.route("/map")
def map_view():
    return render_template("map.html")


if __name__ == "__main__":
    app.run(debug=True)