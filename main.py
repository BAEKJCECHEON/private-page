from flask import Flask, request, redirect, session, render_template
import psycopg2
from datetime import datetime
import calendar

app = Flask(__name__)
app.secret_key = "secret-key"

DATABASE_URL = "postgresql://mydb_qftc_user:UpdqTVT3YO30EAAk6n7oqNpkDCFxTMLK@dpg-d731j5fkijhs73d8gq4g-a/mydb_qftc"

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id SERIAL PRIMARY KEY,
        content TEXT,
        user TEXT,
        created_at TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS schedules (
        id SERIAL PRIMARY KEY,
        date TEXT,
        content TEXT,
        user TEXT
    )
    ''')

    conn.commit()
    conn.close()

def get_dday():
    start = datetime(2026, 1, 17)
    return (datetime.now() - start).days + 1

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pw = request.form.get("password")

        if pw == "134679":
            session["auth"] = True
            session["user"] = "수연"
            return redirect("/home")
        elif pw == "root":
            session["auth"] = True
            session["user"] = "재천"
            return redirect("/home")
        else:
            return render_template("index.html", error=True)

    return render_template("index.html")

@app.route("/home")
def home():
    if not session.get("auth"):
        return redirect("/")

    conn = get_conn()
    c = conn.cursor()

    # 글
    c.execute("SELECT * FROM posts ORDER BY id DESC")
    posts = c.fetchall()

    # 일정
    c.execute("SELECT * FROM schedules")
    schedules = c.fetchall()

    conn.close()

    today = datetime.now()
    year = today.year
    month = today.month
    cal = calendar.monthcalendar(year, month)

    return render_template("home.html",
                           posts=posts,
                           schedules=schedules,
                           calendar=cal,
                           year=year,
                           month=month,
                           user=session.get("user"),
                           dday=get_dday())

@app.route("/post", methods=["POST"])
def post():
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        "INSERT INTO posts (content, user, created_at) VALUES (%s, %s, %s)",
        (request.form["content"],
         session["user"],
         datetime.now().strftime("%Y-%m-%d"))
    )

    conn.commit()
    conn.close()
    return redirect("/home")

@app.route("/add_schedule", methods=["POST"])
def add_schedule():
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        "INSERT INTO schedules (date, content, user) VALUES (%s, %s, %s)",
        (request.form["date"],
         request.form["content"],
         session["user"])
    )

    conn.commit()
    conn.close()
    return redirect("/home")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)