from flask import Flask, request, render_template, redirect, session
import requests
import secrets
import DBcm
import bcrypt
from concurrent.futures import ThreadPoolExecutor

salt = bcrypt.gensalt()
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

config = {
    "host": "localhost",
    "database": "macro_meals_db",
    "user": "root",
    "password": "macro_meals_password",
}


@app.route("/")
def index():
    return render_template("index.html", title="Welcome")


@app.route("/register")
def register():
    return render_template("register.html", title="Welcome")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")
    return render_template("dashboard.html", heading="Welcome, " + session["username"])


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    errors = ""
    if request.method == "POST":
        username = request.form.get("username")
        email= request.form.get("email")
        Userpassword = request.form.get("password")
        print(Userpassword)
        with DBcm.UseDatabase(config) as db:
            SQL = """select * from users where Email = %s"""
            db.execute(SQL, (email,))
            res = db.fetchall()
            Userpassword = Userpassword.encode("utf-8")
            hashedDB = res[0][3].encode("utf-8")
            passres = bcrypt.checkpw(Userpassword, hashedDB)
            if res and passres:
                session["username"] = username
                return redirect("/dashboard")
            else:
                errors = "Username/Password are incorrect"
    return render_template("login.html", title="Welcome", errors=errors)

@app.route("/addrecipe", methods=["GET", "POST"])
def addrecipe():
    errors = []
    pass

def check_email_exists(email):
    with DBcm.UseDatabase(config) as d:
        SQL = """select * from users where Email = %s"""
        d.execute(SQL, (email,))
        rows = d.fetchall()
    if len(rows) > 0:
        return True
    else:
        return False

@app.route("/processform", methods=["GET", "POST"])
def processform():
    errors  = []
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    repeatpassword = request.form.get("repeatpassword")
    password = password.encode("utf-8")
    repeatpassword = repeatpassword.encode("utf-8")
    hashed_password = bcrypt.hashpw(password, salt)
    hashed_repeat_password = bcrypt.hashpw(repeatpassword, salt)
    if password!=repeatpassword:
        errors.append("Passwords do not match")
    if check_email_exists(email) == True:
        errors.append("Email already registered")
    else:
        with DBcm.UseDatabase(config) as db:
            SQL = """
                insert into users
                (Username, Email, Password)
                values
                (%s, %s, %s)
            """

            db.execute(SQL, (username, email, hashed_password))
        return redirect("/login")
    return render_template("register.html", title="Welcome", errors = errors )


@app.route("/recipe")
def edamam():
    return render_template(
        "edamam.html",
        title="Macro Meals",
        heading="Enter the following for a Personalised Recipe",
    )


@app.route("/recipe", methods=["GET", "POST"])
def process():
    app_id = "41124d1e"
    app_key = "da107657cdc9a798f1921db69fe67581"
    meal_type = request.form.getlist("mealcheck")
    meal_type = ",".join(meal_type)
    ingredients = request.form["ingredients"]
    health = request.form.getlist("dietcheck")
    health = ",".join(health)
    selectedIng = request.form.getlist("check")
    selectedIng = ",".join(selectedIng)
    if ingredients == "":
        ingredients = selectedIng
    else:
        ingredients = selectedIng + "," + ingredients
    if health == "" and meal_type == "":
        result = requests.get(
            f"https://api.edamam.com/search?q={ingredients}&app_id={app_id}&app_key={app_key}"
        )
    elif not meal_type:
        result = requests.get(
            f"https://api.edamam.com/search?q={ingredients}&health={health}&app_id={app_id}&app_key={app_key}"
        )
    elif health == "" or " ":
        result = requests.get(
            f"https://api.edamam.com/search?q={ingredients}&mealType={meal_type}&app_id={app_id}&app_key={app_key}"
        )
    else:
        result = requests.get(
            f"https://api.edamam.com/search?q={ingredients}&health={health}&mealType={meal_type}&app_id={app_id}&app_key={app_key}"
        )
    data = result.json()
    res = data["hits"]

    with ThreadPoolExecutor() as executor:
        status_codes = list(executor.map(check_status, [row['recipe']['url'] for row in res]))
        res = [row for i, row in enumerate(res) if status_codes[i] == 200]
    return render_template(
        "results.html", title="Suggested Recipes ", heading="Your Recipes", data=res
    )

def check_status(url):
    return requests.get(url).status_code


if __name__ == "__main__":  # pragma no cover
    app.run(debug=True)
