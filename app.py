from flask import Flask, request, render_template
import  requests

app = Flask(__name__)

# app_id = '0620fd4d'
# app_key = 'cb6954f29368c1f234ebc4d102ea0a20	'
# ingredient = 'banana'
# meal_type='breakfast'
# result = requests.get(f'https://api.edamam.com/search?q={ingredient}&mealType={meal_type}&app_id={app_id}&app_key={app_key}')
# data = result.json()
# res=data['hits']
# for i in res:
#     #print(res[0]['recipe']['label'])
#     print (i['recipe']['label'])
#     print('')
#     for i in res:
#         print (i['recipe']['ingredientLines'])
#         print('')


@app.route("/")
def index():
    return render_template("index.html", title="Welcome", heading="API Test")

@app.route("/" ,methods=['GET', 'POST'])
def process():
    app_id = '0620fd4d'
    app_key = 'cb6954f29368c1f234ebc4d102ea0a20	'
    meal_type=request.form["mealtype"]
    ingredients = request.form["ingredients"]
    num=request.form["numIng"]
    result = requests.get(f'https://api.edamam.com/search?q={ingredients}&mealType={meal_type}&ingr={num}&app_id={app_id}&app_key={app_key}')
    data = result.json()
    res=data['hits']
    return render_template("ingredients.html", title="Suggested Recipes ", heading="Your Recipes :)", data=res)

if __name__ == "__main__":  # pragma no cover
    app.run(debug=True)
