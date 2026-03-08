from flask import Flask, request, render_template, redirect
import sqlite3
import os

app = Flask(__name__)

DB = "users.db"

def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("CREATE TABLE users (username TEXT, password TEXT)")
        c.execute("INSERT INTO users VALUES ('admin','admin123')")
        c.execute("INSERT INTO users VALUES ('test','test123')")
        conn.commit()
        conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")


# -------------------------------
# SQL Injection Vulnerability
# -------------------------------

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        # INTENTIONALLY VULNERABLE
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"

        result = c.execute(query).fetchone()

        if result:
            return f"Welcome {username}"
        else:
            return "Invalid login"

    return render_template("login.html")


# -------------------------------
# XSS Vulnerability
# -------------------------------

@app.route("/search")
def search():

    q = request.args.get("q","")

    return f"<h2>Results for {q}</h2>"


# -------------------------------
# Command Injection
# -------------------------------

@app.route("/ping")
def ping():

    ip = request.args.get("ip")

    result = os.popen(f"ping -c 1 {ip}").read()

    return f"<pre>{result}</pre>"


# -------------------------------
# SSTI Vulnerability
# -------------------------------

@app.route("/hello")
def hello():

    name = request.args.get("name","guest")

    template = f"""
    <h1>Hello {name}</h1>
    """

    return render_template_string(template)


# -------------------------------
# File Inclusion
# -------------------------------

@app.route("/file")
def file():

    filename = request.args.get("name")

    try:
        with open(filename) as f:
            return f.read()
    except:
        return "File not found"


# -------------------------------
# Open Redirect
# -------------------------------

@app.route("/redirect")
def redir():

    url = request.args.get("url")

    return redirect(url)


# -------------------------------
# Debug Info Leak
# -------------------------------

@app.route("/debug")
def debug():

    return str(os.environ)


if __name__ == "__main__":
    app.run(debug=True)
