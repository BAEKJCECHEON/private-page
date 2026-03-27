from flask import Flask, request, redirect, session, render_template
import sqlite3
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret-key"

# 업로드 폴더
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# DB 초기화
def init_db():
    conn = sqlite3.connect("app.db")
    c = conn.cursor()

    # 게시판
    c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT,
        created_at TEXT
    )
    ''')

    # todo
    c.execute('''
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        done INTEGER
    )
    ''')

    # 기념일
    c.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        date TEXT,
        memo TEXT
    )
    ''')

    # 📸 앨범
    c.execute('''
    CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        caption TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()


# D-day
def get_dday():
    start_date = datetime(2024, 1, 17)
    today = datetime.now()
    return (today - start_date).days + 1


# 로그인
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.form.get("password") == "134679":
            session["auth"] = True
            return redirect("/home")
        else:
            return render_template("index.html", error=True)
    return render_template("index.html")

# 홈
@app.route("/home")
def home():
    if not session.get("auth"):
        return redirect("/")

    conn = sqlite3.connect("app.db")
    c = conn.cursor()

    posts = c.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    todos = c.execute("SELECT * FROM todos").fetchall()
    events = c.execute("SELECT * FROM events ORDER BY date").fetchall()
    photos = c.execute("SELECT * FROM photos ORDER BY id DESC").fetchall()

    conn.close()

    return render_template("home.html",
                           posts=posts,
                           todos=todos,
                           events=events,
                           photos=photos,
                           dday=get_dday())


# 게시판
@app.route("/post", methods=["POST"])
def post():
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    c.execute("INSERT INTO posts (content, created_at) VALUES (?, ?)",
              (request.form["content"], datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()
    return redirect("/home")


@app.route("/delete_post/<int:id>")
def delete_post(id):
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/home")


# todo
@app.route("/add_todo", methods=["POST"])
def add_todo():
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    c.execute("INSERT INTO todos (text, done) VALUES (?, 0)",
              (request.form["text"],))
    conn.commit()
    conn.close()
    return redirect("/home")


@app.route("/toggle_todo/<int:id>")
def toggle_todo(id):
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    c.execute("UPDATE todos SET done = NOT done WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/home")


# 기념일
@app.route("/add_event", methods=["POST"])
def add_event():
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    c.execute("INSERT INTO events (title, date, memo) VALUES (?, ?, ?)",
              (request.form["title"], request.form["date"], request.form["memo"]))
    conn.commit()
    conn.close()
    return redirect("/home")


@app.route("/delete_event/<int:id>")
def delete_event(id):
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/home")


# 📸 앨범
@app.route("/upload_photo", methods=["POST"])
def upload_photo():
    file = request.files["photo"]
    caption = request.form["caption"]

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        conn = sqlite3.connect("app.db")
        c = conn.cursor()
        c.execute("INSERT INTO photos (filename, caption) VALUES (?, ?)",
                  (filename, caption))
        conn.commit()
        conn.close()

    return redirect("/home")


@app.route("/delete_photo/<int:id>")
def delete_photo(id):
    conn = sqlite3.connect("app.db")
    c = conn.cursor()

    photo = c.execute("SELECT filename FROM photos WHERE id=?", (id,)).fetchone()

    if photo:
        try:
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], photo[0]))
        except:
            pass

    c.execute("DELETE FROM photos WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/home")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)