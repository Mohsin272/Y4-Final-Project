# Author - Mohsin Tahir
# Date - 17/04/23
from flask import Flask, request, render_template, redirect, session
import requests
import secrets
import DBcm
import bcrypt
from appconfig import config
import re
import openai
import secret

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
    username = session.get("username", None)
    url = request.form.get("Link")
    if username is not None:
        with DBcm.UseDatabase(config) as db:
            SQL = """delete from saved_recipes where Username = %s and Link = %s"""
            data = (username, url)
            db.execute(SQL, data)
        return redirect("/savedRecipes")
    else:
        return redirect("/login")


@app.route("/savedRecipes")
def savedRecipes():
    username = session.get("username", None)
    if username is not None:
        with DBcm.UseDatabase(config) as db:
            SQL = """select * from saved_recipes where Username = %s"""
            db.execute(SQL, (username,))
            res = db.fetchall()
        return render_template("savedRecipes.html", title="Saved Recipe", res=res,)
    else:
        return redirect("/login")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")


@app.route("/passreset", methods=["GET", "POST"])
def changepw():
    return render_template("changepw.html", title="Change Password")


@app.route("/processreset", methods=["GET", "POST"])
def processreset():
    errors = []
    email = request.form.get("email")
    password = request.form.get("password")
    repeatpassword = request.form.get("repeatpassword")
    password = password.encode("utf-8")
    repeatpassword = repeatpassword.encode("utf-8")
    hashed_password = bcrypt.hashpw(password, salt)
    hashed_password_r = bcrypt.hashpw(repeatpassword, salt)
    if hashed_password != hashed_password_r:
        errors.append("Passwords do not match")
    else:
        with DBcm.UseDatabase(config) as db:
            SQL = """
                UPDATE users
                SET Password = %s
                WHERE Email = %s
            """
            db.execute(SQL, (hashed_password, email))
        return redirect("/login")
    return render_template("changepw.html", title="Change Password", errors=errors)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect("/recipe")
    errors = ""
    if request.method == "POST":
        username = request.form.get("username")
        Userpassword = request.form.get("password")
        with DBcm.UseDatabase(config) as db:
            SQL = """select * from users where Username = %s"""
            db.execute(SQL, (username,))
            res = db.fetchall()
            if res:
                Userpassword = Userpassword.encode("utf-8")
                hashedDB = res[0][3].encode("utf-8")
                passres = bcrypt.checkpw(Userpassword, hashedDB)
                if res and passres:
                    session["username"] = username
                    session["email"] = res[0][2]
                    return redirect("/recipe")
                else:
                    errors = "Username/Password are incorrect"
            else:
                errors = "Username/Password are incorrect"
    return render_template("login.html", title="Welcome", errors=errors)


@app.route("/gpt", methods=["POST", "GET"])
def gpt():
    openai.api_key = secret.open_ai_api_key
    ing = request.form.get("Ingredients").strip("[]")
    message = "print this list of ingredients with carbon footprint friendly alternatives. Only print a list no explanation please."
    separator = "\n"
    ingredient_list = ing.split(", ")
    joined_ingredients = separator.join(ingredient_list)
    message_with_ingredients = message + "\n\n" + joined_ingredients
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message_with_ingredients},],
    )
    result = ""
    for choice in response.choices:
        result = choice.message.content
    output = re.split(r"(?<=\D)\s*-\s+", result)
    output = [s.strip() for s in output if s.strip()]
    return render_template("gpt.html", title="GPT Results", output=output)


@app.route("/addrecipe", methods=["GET", "POST"])
def addrecipe():
    Ingredients = request.form.get("Ingredients").strip("[]")
    Calories = request.form.get("Calories")
    Servings = request.form.get("Servings")
    Carbs_value = request.form.get("Carbs value")
    Fat_value = request.form.get("Fat value")
    Protein_value = request.form.get("Protein value")
    Sugars_value = request.form.get("Sugars value")
    Fiber_value = request.form.get("Fiber value")
    Link = request.form.get("Link")
    Label = request.form.get("Label")
    Username = session.get("username", None)
    Email = session.get("email", None)
    Carbon = request.form.get("carbon")
    Cost = request.form.get("cost")

    if Username and Email is not None:
        with DBcm.UseDatabase(config) as db:
            SQL = """SELECT * FROM saved_recipes WHERE Email = %s AND Link = %s"""
            db.execute(SQL, (Email, Link))
            existing_recipe = db.fetchone()

        if existing_recipe:
            return redirect("/savedRecipes")
        with DBcm.UseDatabase(config) as db:
            SQL = """
                    insert into saved_recipes
                    (Username, Email, Ingredients, Calories, Servings,
                    Carbs_value,
                    Fat_value,
                    Protein_value,
                    Sugars_value,
                    Fiber_value,
                    Link, Label, Carbon, Cost
                    )
                    values
                    (%s, %s, %s, %s, %s,
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
                    Carbs_value,
                    Fat_value,
                    Protein_value,
                    Sugars_value,
                    Fiber_value,
                    Link,
                    Label,
                    Carbon,
                    Cost,
                ),
            )
        return redirect("/savedRecipes")
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
    return render_template("edamam.html", title="Macro Meals",)


def sort_by_criteria(res, criteria):
    if criteria == "caloriesLH":
        return sorted(res, key=lambda r: int(r["recipe"]["calories"]) / int(r["recipe"]["yield"]))
    elif criteria == "caloriesHL":
        return sorted(res, key=lambda r: int(r["recipe"]["calories"]) / int(r["recipe"]["yield"]), reverse=True)
    elif criteria == "servingLH":
        return sorted(res, key=lambda r: r["recipe"]["yield"])
    elif criteria == "servingHL":
        return sorted(res, key=lambda r: r["recipe"]["yield"], reverse=True)
    elif criteria == "carbsLH":
        return sorted(
            res, key=lambda r: int(r["recipe"]["totalNutrients"]["CHOCDF.net"]["quantity"]) / int(r["recipe"]["yield"])
        )
    elif criteria == "carbsHL":
        return sorted(
            res,
            key=lambda r: int(r["recipe"]["totalNutrients"]["CHOCDF.net"]["quantity"]) / int(r["recipe"]["yield"]),
            reverse=True,
        )
    elif criteria == "fatLH":
        return sorted(
            res, key=lambda r: int(r["recipe"]["totalNutrients"]["FAT"]["quantity"]) / int(r["recipe"]["yield"])
        )
    elif criteria == "fatHL":
        return sorted(
            res,
            key=lambda r: int(r["recipe"]["totalNutrients"]["FAT"]["quantity"]) / int(r["recipe"]["yield"]),
            reverse=True,
        )
    elif criteria == "proteinLH":
        return sorted(
            res, key=lambda r:int(r["recipe"]["totalNutrients"]["PROCNT"]["quantity"]) / int(r["recipe"]["yield"])
        )
    elif criteria == "proteinHL":
        return sorted(
            res,
            key=lambda r: int(r["recipe"]["totalNutrients"]["PROCNT"]["quantity"]) / int(r["recipe"]["yield"]),
            reverse=True,
        )
    elif criteria == "sugarLH":
        return sorted(
            res, key=lambda r: int(r["recipe"]["totalNutrients"]["SUGAR"]["quantity"]) / int(r["recipe"]["yield"])
        )
    elif criteria == "sugarHL":
        return sorted(
            res,
            key=lambda r: int(r["recipe"]["totalNutrients"]["SUGAR"]["quantity"]) / int(r["recipe"]["yield"]),
            reverse=True,
        )
    elif criteria == "fiberLH":
        return sorted(
            res, key=lambda r: int(r["recipe"]["totalNutrients"]["FIBTG"]["quantity"]) / int(r["recipe"]["yield"])
        )
    elif criteria == "fiberHL":
        return sorted(
            res,
            key=lambda r: int(r["recipe"]["totalNutrients"]["FIBTG"]["quantity"]) / int(r["recipe"]["yield"]),
            reverse=True,
        )


def process_ingredients(res, items):
    ingredients_list = []
    res_list = []
    for row in res:
        for ing in row["recipe"]["ingredientLines"]:
            ingredients_list.append(ing)
        value = get_carbon_value(ingredients_list, items)
        res_list.append(value)
    return res_list


@app.route("/sort_results", methods=["POST", "GET"])
def sort_results():
    app_id = secret.edamam_app_id
    app_key = secret.edamam_api_key
    meal_type = request.form.get("meal")
    ingredients = request.form.get("ing")
    health = request.form.get("health")
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
    criteria = request.form["criteria"]
    res = sort_by_criteria(res, criteria)

    res_list = []
    res_list = process_ingredients(res, items, items_carbon_values)
    cost_list = process_costs(res, expensive, expensive_cost)

    return render_template(
        "results.html",
        title="Suggested Recipes ",
        data=res,
        cfv=res_list,
        meal=meal_type,
        ing=ingredients,
        health=health,
        cost=cost_list,
    )


@app.route("/recipe", methods=["GET", "POST"])
def process():
    app_id = secret.edamam_app_id
    app_key = secret.edamam_api_key
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
    res_list = []
    res_list = process_ingredients(res, items, items_carbon_values)
    cost_list = process_costs(res, expensive, expensive_cost)

    accessible_recipes = []
    for row in res:
        url = row["recipe"]["url"]
        status_code = check_status(url)
        if status_code != 404:
            accessible_recipes.append(row)

    res = accessible_recipes
    return render_template(
        "results.html",
        title="Suggested Recipes ",
        data=res,
        cfv=res_list,
        meal=meal_type,
        ing=ingredients,
        health=health,
        cost=cost_list,
    )


def extract_quantity(ingredient):
    quantity_match = re.search(r"(\d+([.,]\d+)?)", ingredient)
    if quantity_match:
        return float(quantity_match.group(1))
    else:
        return 1


def get_carbon_value(ingredients_list, items, items_carbon_values, serving_size):
    total_carbon_value = 0
    for ing in ingredients_list:
        for item, carbon_value in zip(items, items_carbon_values):
            if item.lower() in ing.lower():
                quantity = extract_quantity(ing)
                total_carbon_value += carbon_value * quantity
                break
    if serving_size >= 4:
        total_carbon_value /= serving_size
    if total_carbon_value >= 30:
        return "RED"
    else:
        return "GREEN"


def process_ingredients(res, items, items_carbon_values):
    res_list = []
    for row in res:
        ingredients_list = []
        for ing in row["recipe"]["ingredientLines"]:
            ingredients_list.append(ing)
        serving_size = row["recipe"]["yield"]
        value = get_carbon_value(
            ingredients_list, items, items_carbon_values, serving_size
        )
        res_list.append(value)
    return res_list


def get_cost_value(ingredients_list, expensive, expensive_cost, serving_size):
    total_cost_value = 0
    for ing in ingredients_list:
        for item, price in zip(expensive, expensive_cost):
            if item.lower() in ing.lower():
                quantity = extract_quantity(ing)
                total_cost_value += price * quantity
                break

    if serving_size >= 4:
        total_cost_value /= serving_size

    if total_cost_value >= 50:
        return "High Cost"
    elif total_cost_value >= 25:
        return "Average Cost"
    else:
        return "Low Cost"


def process_costs(res, expensive, expensive_cost):
    res_list = []
    for row in res:
        ingredients_list = []
        for ing in row["recipe"]["ingredientLines"]:
            ingredients_list.append(ing)
        serving_size = row["recipe"]["yield"]
        value = get_cost_value(
            ingredients_list, expensive, expensive_cost, serving_size
        )
        res_list.append(value)
    return res_list


def check_status(url):
    try:
        response = requests.head(url)
        return response.status_code
    except requests.RequestException:
        return None


items = [
    "Avocado",
    "Beef",
    "Cheese",
    "Chicken",
    "Chocolate",
    "Coffee",
    "Corn",
    "Lamb",
    "Mutton",
    "Palm Oil",
    "Pork",
    "Rapeseed Oil",
    "Shrimp",
    "Soy milk",
    "Soybean Oil",
    "Soybeans",
    "Sunflower Oil",
    "Tofu",
    "Steak",
    "Prawn",
]
# Carbon values an items taken from https://ourworldindata.org/food-choice-vs-eating-local
items_carbon_values = [
    2,  # Avocado
    60,  # Beef
    21,  # Cheese
    6,  # Chicken
    19,  # Chocolate
    17,  # Coffee
    1,  # Corn
    24,  # Lamb
    24,  # Mutton
    8,  # Palm Oil
    7,  # Pork
    4,  # Rapeseed Oil
    12,  # Shrimp
    3,  # Soy milk
    6.2,  # Soybean Oil
    1,  # Soybeans
    3.5,  # Sunflower Oil
    2,  # Tofu
    60,  # Steak
    12,  # Prawn
]
# Cost items taken from https://www.bbc.co.uk/programmes/articles/1LX0tn2vrN5Ls7RXcfb47rz/eight-of-the-world-s-most-expensive-foods
expensive = ["Wagyu", "Lobster", "Truffle", "Manuka Honey", "Saffron", "Caviar"]
expensive_cost = [
    300,  # Wagyu (per kg)
    50,  # Lobster (per kg)
    4000,  # Truffle (per kg)
    62,  # Manuka Honey (per kg)
    3990,  # Saffron (per kg)
    2100,  # Caviar (per kg)
]

if __name__ == "__main__":  # pragma no cover
    app.run(debug=True)
