from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, hashlib, json, os
from buildings import locations, building_polygons, building_floors
from functools import wraps
from flask_dance.contrib.google import make_google_blueprint, google

app = Flask(__name__)
app.secret_key = "guideu-secret-change-this"

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

google_bp = make_google_blueprint(
    client_id     = "904493667673-oulj1hgm7n4td7uce4upn4hu0cqn1cst.apps.googleusercontent.com",
    client_secret = "dummy_123",
    scope         = ["openid",
                     "https://www.googleapis.com/auth/userinfo.email",
                     "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_to   = "google_login_callback"
)
app.register_blueprint(google_bp, url_prefix="/login")

FLOOR_NAMES = ['Ground Floor', '1st Floor', '2nd Floor', '3rd Floor', '4th Floor']

def get_db():
    return sqlite3.connect("users.db")

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect("users.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT UNIQUE NOT NULL,
            password  TEXT,
            email     TEXT UNIQUE,
            google_id TEXT UNIQUE,
            avatar    TEXT
        )
    """)
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def welcome():
    return render_template("welcome.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = hash_pw(request.form['password'])
        conn     = get_db()
        user     = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()
        if user:
            session["user"]   = username
            session["avatar"] = user[5] or ""
            return redirect("/dashboard")
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = hash_pw(request.form['password'])
        conn     = get_db()
        try:
            conn.execute(
                "INSERT INTO users(username, password) VALUES(?,?)",
                (username, password)
            )
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            error = "Username already exists"
    return render_template("register.html", error=error)

@app.route('/google-login-callback')
def google_login_callback():
    if not google.authorized:
        return redirect(url_for("google.login"))
    try:
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            return redirect("/login")
        info      = resp.json()
        google_id = info["id"]
        email     = info.get("email", "")
        name      = info.get("name", email.split("@")[0])
        avatar    = info.get("picture", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE google_id=? OR email=?",
            (google_id, email)
        ).fetchone()

        if user:
            conn.execute(
                "UPDATE users SET google_id=?, avatar=? WHERE id=?",
                (google_id, avatar, user[0])
            )
            conn.commit()
            session["user"]   = user[1]
            session["avatar"] = avatar
        else:
            username = name.replace(" ", "_").lower()
            base = username; i = 1
            while conn.execute(
                "SELECT id FROM users WHERE username=?", (username,)
            ).fetchone():
                username = f"{base}_{i}"; i += 1

            conn.execute(
                "INSERT INTO users(username, email, google_id, avatar) VALUES(?,?,?,?)",
                (username, email, google_id, avatar)
            )
            conn.commit()
            session["user"]   = username
            session["avatar"] = avatar

        conn.close()
        return redirect("/dashboard")
    except Exception as e:
        print("Google OAuth error:", e)
        return redirect("/login")

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html",
        user   = session["user"],
        avatar = session.get("avatar", "")
    )

@app.route('/academic')
@login_required
def academic():
    return render_template("academic.html")

@app.route('/food')
@login_required
def food():
    return render_template("food.html")

@app.route('/hostels')
@login_required
def hostels():
    return render_template("hostels.html")

@app.route('/girls_hostel')
@login_required
def girls_hostel():
    return render_template("girls_hostel.html")

@app.route('/boys_hostel')
@login_required
def boys_hostel():
    return render_template("boys_hostel.html")

@app.route('/gobble')
@login_required
def gobble():
    return render_template("gobble.html")

@app.route('/health')
@login_required
def health():
    return render_template("health.html")

@app.route('/tour')
@login_required
def tour():
    return render_template("tour.html")

@app.route('/campus')
@login_required
def campus():
    return render_template("campus_map.html",
        polygons  = json.dumps(building_polygons),
        floors    = json.dumps(building_floors),
        locations = json.dumps(locations)
    )

@app.route('/navigate/<location>')
@login_required
def navigate(location):
    loc = locations.get(location)
    if loc:
        return render_template("Navigate.html",
            location    = location,
            description = loc["desc"],
            lat         = loc["lat"],
            lng         = loc["lng"]
        )
    return redirect("/campus")

@app.route('/floorplan/<building>/<int:floor>')
@login_required
def floorplan(building, floor):
    total = building_floors.get(building, 1)
    if floor >= total:
        floor = 0

    has_image    = False
    img_filename = None
    for ext in ['jpeg', 'jpg', 'png']:
        test_name = f"{building.replace(' ', '_')}_{floor}.{ext}"
        test_path = os.path.join(app.static_folder, "floorplans", test_name)
        if os.path.exists(test_path):
            has_image    = True
            img_filename = test_name
            break

    return render_template("Floorplan.html",
        building     = building,
        floor        = floor,
        total_floors = total,
        floor_names  = FLOOR_NAMES,
        has_image    = has_image
    )

@app.route('/privacy')
def privacy():
    return render_template("privacy.html")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)