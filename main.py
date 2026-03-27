from flask import Flask, request, redirect, session, render_template
import psycopg2
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret-key"

# 🔥 너 DB URL
DATABASE_URL = "postgresql://mydb_qftc_user:UpdqTVT3YO30EAAk6n7oqNpkDCFxTMLK@dpg-d731j5fkijhs73d8gq4g-a/mydb_qftc"


# DB 연결 함수
def get_conn():
    return psycopg2.connect(DATABASE_URL)


# DB 초기화
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
    CREATE TABLE IF NOT EXISTS photos (
        id SERIAL PRIMARY KEY,
        filename TEXT,
        caption TEXT,
        user TEXT,
        created_at TEXT
    )
    ''')

    conn.commit()
    conn.close()


# D-DAY 계산
def get_dday():
    start = datetime(2026, 1, 17)
    today = datetime.now()
    return (today - start).days + 1


# 로그인
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


# 홈
@app.route("/home")
def home():
    if not session.get("auth"):
        return redirect("/")

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM posts ORDER BY id DESC")
    posts = c.fetchall()

    c.execute("SELECT * FROM photos ORDER BY id DESC")
    photos = c.fetchall()

    conn.close()

    return render_template("home.html",
                           posts=posts,
                           photos=photos,
                           user=session.get("user"),
                           dday=get_dday())


# 글 작성
@app.route("/post", methods=["POST"])
def post():
    if not session.get("auth"):
        return redirect("/")

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


# 사진 업로드
@app.route("/upload_photo", methods=["POST"])
def upload_photo():
    if not session.get("auth"):
        return redirect("/")

    file = request.files["photo"]
    caption = request.form.get("caption")

    if file:
        filename = file.filename
        file.save("static/uploads/" + filename)

        conn = get_conn()
        c = conn.cursor()

        c.execute(
            "INSERT INTO photos (filename, caption, user, created_at) VALUES (%s, %s, %s, %s)",
            (filename,
             caption,
             session["user"],
             datetime.now().strftime("%Y-%m-%d"))
        )

        conn.commit()
        conn.close()

    return redirect("/home")


# 로그아웃
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# 실행
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)