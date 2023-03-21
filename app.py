from flask import Flask, request, render_template, redirect, session
import requests
import secrets
import DBcm
import bcrypt
from concurrent.futures import ThreadPoolExecutor
from appconfig import config
import re

salt = bcrypt.gensalt()
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


@app.route("/")
def index():
    return render_template("index.html", title="Welcome")


@app.route("/register")
def register():
    return render_template("register.html", title="Welcome")


@app.route("/deleteRecipe", methods=["GET", "POST"])
def deleteRecipe():
    email = session.get("email", None)
    url = request.form.get("Link")
    if email is not None:
        with DBcm.UseDatabase(config) as db:
            SQL = """delete from saved_recipes where Email = %s and Link = %s"""
            data = (email, url)
            db.execute(SQL, data)
        return redirect("/recipe")
    else:
        return redirect("/login")


@app.route("/savedRecipes")
def savedRecipes():
    email = session.get("email", None)
    if email is not None:
        with DBcm.UseDatabase(config) as db:
            SQL = """select * from saved_recipes where Email = %s"""
            db.execute(SQL, (email,))
            res = db.fetchall()
        return render_template(
            "savedRecipes.html",
            title="Saved Recipe",
            res=res,
            heading="Your Saved Recipes",
        )
    else:
        return redirect("/login")


@app.route("/dashboard")
def dashboard():
    # if "username" not in session:
    #     return redirect("/login")
    return render_template(
        "edamam.html",
        title=session["username"] + "'s Dashboard",
        name=session["username"],
        #heading="Welcome, " + session["username"],
    )


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect("/recipe")
    errors = ""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        Userpassword = request.form.get("password")
        with DBcm.UseDatabase(config) as db:
            SQL = """select * from users where Email = %s"""
            db.execute(SQL, (email,))
            res = db.fetchall()
            if res:
                Userpassword = Userpassword.encode("utf-8")
                hashedDB = res[0][3].encode("utf-8")
                passres = bcrypt.checkpw(Userpassword, hashedDB)
                if res and passres:
                    session["username"] = username
                    session["email"] = email
                    return redirect("/recipe")
                else:
                    errors = "Username/Password are incorrect"
            else:
                errors = "User does not exist"
    return render_template("login.html", title="Welcome", errors=errors)


@app.route("/addrecipe", methods=["GET", "POST"])
def addrecipe():
    errors = []
    Ingredients = request.form.get("Ingredients").strip("[]")
    Calories = request.form.get("Calories")
    Servings = request.form.get("Servings")
    Carbs_name = request.form.get("Carbs name")
    Carbs_value = request.form.get("Carbs value")
    Carbs_unit = request.form.get("Carbs unit")
    Fat_name = request.form.get("Fat name")
    Fat_value = request.form.get("Fat value")
    Fat_unit = request.form.get("Fat unit")
    Protein_name = request.form.get("Protein name")
    Protein_value = request.form.get("Protein value")
    Protein_unit = request.form.get("Protein unit")
    Sugars_name = request.form.get("Sugars name")
    Sugars_value = request.form.get("Sugars value")
    Sugars_unit = request.form.get("Sugars unit")
    Fiber_name = request.form.get("Fiber name")
    Fiber_value = request.form.get("Fiber value")
    Fiber_unit = request.form.get("Fiber unit")
    Link = request.form.get("Link")
    Label = request.form.get("Label")
    Image = request.form.get("Image")
    Username = session.get("username", None)
    Email = session.get("email", None)
    Carbon = request.form.get("carbon")

    if Username and Email is not None:
        with DBcm.UseDatabase(config) as db:
            SQL = """
                    insert into saved_recipes
                    (Username, Email, Ingredients, Calories, Servings,
                    Carbs_name, Carbs_value, Carbs_unit, 
                    Fat_name, Fat_value, Fat_unit,
                    Protein_name, Protein_value, Protein_unit,
                    Sugars_name, Sugars_value, Sugars_unit,
                    Fiber_name, Fiber_value, Fiber_unit,
                    Link, Label, Image, Carbon
                    )
                    values
                    (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                    )
                """
            db.execute(
                SQL,
                (
                    Username,
                    Email,
                    Ingredients,
                    Calories,
                    Servings,
                    Carbs_name,
                    Carbs_value,
                    Carbs_unit,
                    Fat_name,
                    Fat_value,
                    Fat_unit,
                    Protein_name,
                    Protein_value,
                    Protein_unit,
                    Sugars_name,
                    Sugars_value,
                    Sugars_unit,
                    Fiber_name,
                    Fiber_value,
                    Fiber_unit,
                    Link,
                    Label,
                    Image,
                    Carbon,
                ),
            )
        return redirect("/recipe")
    else:
        return redirect("/login")


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
    errors = []
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    repeatpassword = request.form.get("repeatpassword")
    password = password.encode("utf-8")
    repeatpassword = repeatpassword.encode("utf-8")
    hashed_password = bcrypt.hashpw(password, salt)
    hashed_password_r = bcrypt.hashpw(repeatpassword, salt)
    if hashed_password != hashed_password_r:
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
    return render_template("register.html", title="Welcome", errors=errors)


@app.route("/recipe")
def edamam():
    return render_template(
        "edamam.html",
        title="Macro Meals",
        #heading="Enter the following for a Personalised Recipe",
    )


@app.route("/recipe", methods=["GET", "POST"])
def process():
    app_id = "9e0266d1"
    app_key = "573469b41542adce2933662450986489"
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

    ingredients_list = []
    res_list = []
    # Sample list of ingredients
    for row in res:
        for ing in row["recipe"]["ingredientLines"]:
            ingredients_list.append(ing)
        value = get_carbon_value(ingredients_list, items)
        res_list.append(value)

    with ThreadPoolExecutor() as executor:
        status_codes = list(
            executor.map(check_status, [row["recipe"]["url"] for row in res])
        )
        res = [row for i, row in enumerate(res) if status_codes[i] == 200]
    return render_template(
        "results.html",
        title="Suggested Recipes ",
        #heading="Your Recipes",
        data=res,
        cfv=res_list,
    )


def get_carbon_value(ingredients_list, high_carbon_ingredients):
    # Define a regular expression pattern to extract ingredient names
    ingredient_pattern = re.compile(r"^\d*\s*(?:\d+\/\d+\s*)?(?:cup|tsp|tbsp)?\s*(.*)")

    # Extract ingredient names from the list
    ingredient_names = []
    for ingredient in ingredients_list:
        match = ingredient_pattern.match(ingredient)
        if match:
            ingredient_names.append(match.group(1).lower())  # Convert to lowercase

    # Count the number of matching ingredients
    matches = sum(
        1
        for ingredient in ingredient_names
        if any(match.lower() in ingredient for match in high_carbon_ingredients)
    )

    # Return a color code based on the total number of matching ingredients
    if matches >= 2:
        return "RED"
    else:
        return "GREEN"


def check_status(url):
    try:
        response = requests.get(url).status_code
        return response
    except:
        return 0


items = [
    "Avocado",
    "Barley",
    "Beef",
    "Cheese",
    "Chicken",
    "Chocolate",
    "Coffee",
    "Corn",
    "Dark Chocolate",
    "Lamb",
    "Leeks",
    "Maize",
    "Mutton",
    "Palm Oil",
    "Pork",
    "Potatoes",
    "Poultry Meat",
    "Rapeseed Oil",
    "Salmon",
    "Shrimp",
    "Soy milk",
    "Soybean Oil",
    "Soybeans",
    "Sunflower Oil",
    "Tofu",
    "Tuna",
    "Wine",
]

if __name__ == "__main__":  # pragma no cover
    app.run(debug=True)
