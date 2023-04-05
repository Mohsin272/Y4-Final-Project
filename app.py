from flask import Flask, request, render_template, redirect, session, jsonify
import requests
import secrets
import DBcm
import bcrypt
from concurrent.futures import ThreadPoolExecutor
from appconfig import config
import re
import openai

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
            # heading="Your Saved Recipes",
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
        # heading="Welcome, " + session["username"],
    )


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
        # email = request.form.get("email")
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
                    # session["email"] = email
                    return redirect("/recipe")
                else:
                    errors = "Username/Password are incorrect"
            else:
                errors = "User does not exist"
    return render_template("login.html", title="Welcome", errors=errors)

@app.route("/gpt", methods=["POST", "GET"])
def gpt():
    openai.api_key = "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"
    ing = request.form.get("Ingredients").strip("[]")
    message = "print this list of ingredients with carbon footprint friendly alternatives. Only print a list no explanation please."

    separator = "\n"

    ingredient_list = ing.split(", ")

    # Join the ingredients list using the separator
    joined_ingredients = separator.join(ingredient_list)

    # Concatenate the message string and the joined ingredients list
    message_with_ingredients = message + "\n\n" + joined_ingredients

    # Print the result
    #print(message_with_ingredients)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "user", "content": message_with_ingredients},
            ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content
    return render_template("gpt.html", title="GPT Results",result=result)

@app.route("/addrecipe", methods=["GET", "POST"])
def addrecipe():
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
                    Link, Label, Carbon
                    )
                    values
                    (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s
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
                    Carbon,
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
        return sorted(res, key=lambda r: r["recipe"]["calories"])
    elif criteria == "caloriesHL":
        return sorted(res, key=lambda r: r["recipe"]["calories"], reverse=True)
    elif criteria == "servingLH":
        return sorted(res, key=lambda r: r["recipe"]["yield"])
    elif criteria == "servingHL":
        return sorted(res, key=lambda r: r["recipe"]["yield"], reverse=True)
    elif criteria == "carbsLH":
        return sorted(
            res, key=lambda r: r["recipe"]["totalNutrients"]["CHOCDF.net"]["quantity"]
        )
    elif criteria == "carbsHL":
        return sorted(
            res,
            key=lambda r: r["recipe"]["totalNutrients"]["CHOCDF.net"]["quantity"],
            reverse=True,
        )
    elif criteria == "fatLH":
        return sorted(
            res, key=lambda r: r["recipe"]["totalNutrients"]["FAT"]["quantity"]
        )
    elif criteria == "fatHL":
        return sorted(
            res,
            key=lambda r: r["recipe"]["totalNutrients"]["FAT"]["quantity"],
            reverse=True,
        )
    elif criteria == "proteinLH":
        return sorted(
            res, key=lambda r: r["recipe"]["totalNutrients"]["PROCNT"]["quantity"]
        )
    elif criteria == "proteinHL":
        return sorted(
            res,
            key=lambda r: r["recipe"]["totalNutrients"]["PROCNT"]["quantity"],
            reverse=True,
        )
    elif criteria == "sugarLH":
        return sorted(
            res, key=lambda r: r["recipe"]["totalNutrients"]["SUGAR"]["quantity"]
        )
    elif criteria == "sugarHL":
        return sorted(
            res,
            key=lambda r: r["recipe"]["totalNutrients"]["SUGAR"]["quantity"],
            reverse=True,
        )
    elif criteria == "fiberLH":
        return sorted(
            res, key=lambda r: r["recipe"]["totalNutrients"]["FIBTG"]["quantity"]
        )
    elif criteria == "fiberHL":
        return sorted(
            res,
            key=lambda r: r["recipe"]["totalNutrients"]["FIBTG"]["quantity"],
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
    app_id = "9e0266d1"
    app_key = "573469b41542adce2933662450986489"
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

    # Sort the results based on the given criteria
    res = sort_by_criteria(res, criteria)

    # Process the ingredients and get the carbon values
    res_list = process_ingredients(res, items)

    # Return the sorted results in the same template as before
    return render_template(
        "results.html",
        title="Suggested Recipes ",
        data=res,
        cfv=res_list,
        meal=meal_type,
        ing=ingredients,
        health=health,
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
    # res = sorted(res, key=lambda r: r['recipe']['calories'])

    ingredients_list = []
    res_list = []
    # Sample list of ingredients
    for row in res:
        for ing in row["recipe"]["ingredientLines"]:
            ingredients_list.append(ing)
        value = get_carbon_value(ingredients_list, items)
        res_list.append(value)

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
        # heading="Your Recipes",
        data=res,
        cfv=res_list,
        meal=meal_type,
        ing=ingredients,
        health=health,
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


# def check_status(url):
#     try:
#         response = requests.get(url).status_code
#         return response
#     except:
#         return 0


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
]

if __name__ == "__main__":  # pragma no cover
    app.run(debug=True)
