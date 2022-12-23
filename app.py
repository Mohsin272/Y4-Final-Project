from flask import Flask, request, render_template
import requests

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", title="Welcome", heading="")


@app.route("/recipe")
def edamam():
    return render_template(
        "edamam.html",
        title="Macro Meals",
        heading="Enter the following for a Personalised Recipe",
    )


def convert_to_metric(value, unit):
    # This function converts the given value and unit to the equivalent
    # value in metric units. It returns a string with the value and unit
    # in the format "value unit".

    # Convert ounces to grams
    if unit == "oz":
        value = value * 28.3495
        unit = "g"

    # Convert pounds to grams
    elif unit == "lb":
        value = value * 453.592
        unit = "g"

    # Convert fluid ounces to milliliters
    elif unit == "fl oz":
        value = value * 29.5735
        unit = "ml"

    # Convert cups to milliliters
    elif unit == "cup":
        value = value * 236.588
        unit = "ml"

    # Convert pints to milliliters
    elif unit == "pt":
        value = value * 473.176
        unit = "ml"

    # Convert quarts to milliliters
    elif unit == "qt":
        value = value * 946.353
        unit = "ml"

    # Convert gallons to milliliters
    elif unit == "gal":
        value = value * 3785.41
        unit = "ml"

    # Return the converted value and unit
    return f"{value} {unit}"


@app.route("/recipe", methods=["GET", "POST"])
def process():
    app_id = "0620fd4d"
    app_key = "cb6954f29368c1f234ebc4d102ea0a20	"
    meal_type = request.form["mealtype"]
    ingredients = request.form["ingredients"]
    health = request.form["dietdropdown"]
    if health == "" or " ":
        result = requests.get(
            f"https://api.edamam.com/search?q={ingredients}&mealType={meal_type}&app_id={app_id}&app_key={app_key}"
        )
    elif meal_type == "" or " ":
        result = requests.get(
            f"https://api.edamam.com/search?q={ingredients}&health={health}&app_id={app_id}&app_key={app_key}"
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
