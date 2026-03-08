from flask import Flask, request, render_template, redirect, render_template_string
import sqlite3
import os
import subprocess

app = Flask(__name__)

DATABASE = "users.db"


# -------------------------
# DATABASE SETUP
# -------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("INSERT INTO users (username,password) VALUES ('admin','admin123')")
    cursor.execute("INSERT INTO users (username,password) VALUES ('user','password')")

    conn.commit()
    conn.close()


init_db()


# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# SQL INJECTION VULNERABILITY
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            # Intentionally vulnerable query
            query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
            result = cursor.execute(query).fetchone()

            if result:
                return "Login successful"
            else:
                return "Invalid credentials"

        except Exception as e:
            return str(e)  # exposes SQL errors

    return render_template("login.html")


# -------------------------
# XSS VULNERABILITY
# -------------------------
@app.route("/search")
def search():

    query = request.args.get("q")

    if query:
        return f"Search results for: {query}"

    return render_template("search.html")


# -------------------------
# COMMAND INJECTION
# -------------------------
@app.route("/ping")
def ping():

    host = request.args.get("host")

    if host:
        command = f"ping -c 1 {host}"
        output = subprocess.getoutput(command)

        return f"<pre>{output}</pre>"

    return """
    <form>
        Host: <input name='host'>
        <input type='submit'>
    </form>
    """


# -------------------------
# SSTI VULNERABILITY
# -------------------------
@app.route("/ssti")
def ssti():
    name = request.args.get("name")

    if name:
        template = "Hello " + name
        return render_template_string(template)

    return """
    <form>
        Name: <input name='name'>
        <input type='submit'>
    </form>
    """


# -------------------------
# DIRECTORY TRAVERSAL
# -------------------------
@app.route("/read")
def read_file():

    filename = request.args.get("file")

    if filename:
        try:
            with open(filename, "r") as f:
                return f"<pre>{f.read()}</pre>"
        except:
            return "File not found"

    return """
    <form>
        File path: <input name='file'>
        <input type='submit'>
    </form>
    """


# -------------------------
# OPEN REDIRECT
# -------------------------
@app.route("/redirect")
def open_redirect():

    url = request.args.get("url")

    if url:
        return redirect(url)

    return """
    <form>
        URL: <input name='url'>
        <input type='submit'>
    </form>
    """


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


