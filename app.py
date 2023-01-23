from flask import Flask, request, render_template
import requests
import DBcm
app = Flask(__name__)

config = {
    "host": "localhost",
    "database": "macro_meals_db",
    "user":"root",
    "password": "macro_meals_password"
}

@app.route("/")
def index():
    return render_template("index.html", title="Welcome", heading="")

@app.route("/login")
def login():
    return render_template("login.html", title="Welcome", heading="")

@app.route("/processform", methods=['GET', 'POST'])
def processform():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    with DBcm.UseDatabase(config) as db:
        SQL = """
            insert into users
            (Username, Email, Password)
            values
            (%s, %s, %s)
        """
        db.execute(SQL, (username, email,password))
    return render_template("index.html", title="Thanks For Your Information")

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
