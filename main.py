from flask import Flask, request, redirect, session, render_template

app = Flask(__name__)
app.secret_key = "secret-key"

# 🔹 index (로그인 역할)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.form.get("password") == "134679":
            session["auth"] = True
            return redirect("/home")
        else:
            return render_template("index.html", error=True)

    return render_template("index.html")


# 🔹 보호된 페이지
@app.route("/home")
def home():
    if session.get("auth"):
        return render_template("home.html")
    else:
        return redirect("/")


# 🔹 로그아웃
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)