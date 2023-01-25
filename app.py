from flask import Flask, request, render_template, redirect
import requests
import secrets
import DBcm
import bcrypt
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

config = {
    "host": "localhost",
    "database": "macro_meals_db",
    "user":"root",
    "password": "macro_meals_password"
}

@app.route("/")
def index():
    return render_template("index.html", title="Welcome", heading="")

@app.route("/register")
def register():
    return render_template("register.html", title="Welcome", heading="")
@app.route("/login")
def login():
    return render_template("login.html", title="Welcome", heading="")

@app.route("/processform", methods=['GET', 'POST'])
def processform():
    errors=[]
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    repeatpassword = request.form.get("repeatpassword")
    password = password.encode('utf-8')
    repeatpassword = repeatpassword.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)
    hashed_repeat_password =  bcrypt.hashpw(repeatpassword, salt)
    if bcrypt.checkpw(hashed_password, hashed_repeat_password):
        errors="Passwords do not match"
    else:
        with DBcm.UseDatabase(config) as db:
            SQL = """
                insert into users
                (Username, Email, Password)
                values
                (%s, %s, %s)
            """

            db.execute(SQL, (username, email,hashed_password))
        return redirect("/recipe")
    return render_template("register.html", title="Welcome",errors=errors)

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
    return render_template(
        "results.html", title="Suggested Recipes ", heading="Your Recipes", data=res
    )


if __name__ == "__main__":  # pragma no cover
    app.run(debug=True)
