from flask import Flask, render_template, request, redirect
import sqlite3
from buildings import locations

app = Flask(__name__)

def get_db():
    return sqlite3.connect("users.db")


@app.route('/', methods=['GET','POST'])
def login():

    error=None

    if request.method=='POST':

        username=request.form['username']
        password=request.form['password']

        conn=get_db()
        cursor=conn.cursor()

        cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
        )

        user=cursor.fetchone()
        conn.close()

        if user:
            return redirect("/dashboard")
        else:
            error="Invalid username or password"

    return render_template("login.html",error=error)


@app.route('/register',methods=['GET','POST'])
def register():

    error=None

    if request.method=='POST':

        username=request.form['username']
        password=request.form['password']

        conn=get_db()
        cursor=conn.cursor()

        try:
            cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username,password)
            )

            conn.commit()
            conn.close()

            return redirect("/")

        except:
            error="Username already exists"

    return render_template("register.html",error=error)


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


@app.route('/academic')
def academic():
    return render_template("academic.html")


@app.route('/food')
def food():
    return render_template("food.html")


@app.route('/gobble')
def gobble():
    return render_template("gobble.html")


@app.route('/hostels')
def hostels():
    return render_template("hostels.html")


@app.route('/girls_hostel')
def girls_hostel():
    return render_template("girls_hostel.html")


@app.route('/boys_hostel')
def boys_hostel():
    return render_template("boys_hostel.html")


@app.route('/map/<location>')
def map(location):

    description=locations.get(location,"Location information not available")

    return render_template("map.html",location=location,description=description)


if __name__=="__main__":
    app.run(debug=True)
