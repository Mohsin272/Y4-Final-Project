from flask import Flask, request, render_template
import  requests

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", title="Welcome", heading="API Test")

@app.route("/edamam")
def edamam():
    return render_template("edamam.html", title="Edamam", heading="API Test")

@app.route("/spoonacular")
def spoonacular():
    return render_template("spoonacular.html", title="Edamam", heading="API Test")

@app.route("/spoonacular")
def spoonProcess():
    api_key='e989ba4eca774666be46dfb04dfd23f5'
    ingredients = request.form["ingredients"]
    results=requests.get(f'https://api.spoonacular.com/recipes/findByIngredients?apiKey={api_key}&ingredients={ingredients}&ranking=1#')
    res=results.json()
    return render_template("spoonacularResults.html", title="Spoonacular", heading="Your Spoonacular Recipes", data=res)

@app.route("/edamam" ,methods=['GET', 'POST'])
def process():
    app_id = '0620fd4d'
    app_key = 'cb6954f29368c1f234ebc4d102ea0a20	'
    meal_type=request.form["mealtype"]
    ingredients = request.form["ingredients"]
    health=request.form["dietdropdown"]
    if health =="" or " ":
         result = requests.get(f'https://api.edamam.com/search?q={ingredients}&mealType={meal_type}&app_id={app_id}&app_key={app_key}')
    else:
        result = requests.get(f'https://api.edamam.com/search?q={ingredients}&health={health}&mealType={meal_type}&app_id={app_id}&app_key={app_key}')
    data = result.json()
    res=data['hits']
    return render_template("ingredients.html", title="Suggested Recipes ", heading="Your Recipes :)", data=res)

if __name__ == "__main__":  # pragma no cover
    app.run(debug=True)
