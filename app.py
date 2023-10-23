from flask import Flask, render_template, request, redirect, session, flash
from models import connect_db, db, User, My_Recipes
from forms import UserForm, RecipesForm
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///recipe_finder_2"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'hungtran'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
with app.app_context():
    db.create_all()



########## ROUTES #########


@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/my_recipes', methods=['GET', 'POST'])
def show_recipes():
    if 'user_id' not in session:
        flash('Please Log In First!')
        return redirect('/login')
    
    form = RecipesForm()
    all_recipes = My_Recipes.query.all()
    if form.validate_on_submit():
        text = form.text.data
        recipe_name = form.recipe_name.data
        new_recipe = My_Recipes(text=text, recipe_name=recipe_name, user_id=session['user_id'])
        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe Created')
        return redirect('/my_recipes')
    
    if request.method == 'POST':
        recipe_id = request.form.get('id')
        action = request.form.get('action')

        if action == 'remove_favorite':
            recipe = My_Recipes.query.get_or_404(recipe_id)
            if recipe.user_id == session['user_id']:
                recipe.is_favorite = False
                db.session.commit()
                flash('Removed from favorites!')
            else:
                flash('You Dont Have The Permission To Do That.')

        elif action == 'add_favorite':
            recipe = My_Recipes.query.get_or_404(recipe_id)
            if recipe.user_id == session['user_id']:
                recipe.is_favorite = True
                db.session.commit()
                flash('Added to favorites!')
            else:
                flash('You Dont Have The Permission To Do That.')

    return render_template('my_recipes.html', form=form, recipes=all_recipes)


@app.route('/my_recipes/<int:id>/toggle_favorite', methods=['POST'])
def toggle_favorite(id):
    if 'user_id' not in session:
        flash('Please Log In First!')
        return redirect('/login')

    recipe = My_Recipes.query.get_or_404(id)

    if recipe.user_id == session['user_id']:
        recipe.is_favorite = not recipe.is_favorite
        db.session.commit()
        flash('Recipe updated!')
    else:
        flash('You Dont Have The Permission To Do That.')

    return redirect('/my_recipes')


# @app.route('/bookmark/<recipe_uri>', methods=['POST'])
# def bookmark(recipe_uri):
#     if 'user_id' not in session:
#         flash('Please Log In First!')
#         return redirect(url_for('login'))

#     user_id = session['user_id']

#     # Check if the recipe is not already bookmarked
#     if not Bookmark.query.filter_by(recipe_uri=recipe_uri, user_id=user_id).first():
#         bookmark = Bookmark(recipe_uri=recipe_uri, user_id=user_id)
#         db.session.add(bookmark)
#         db.session.commit()

#     flash('Recipe bookmarked!')
#     return redirect(url_for('index'))


@app.route('/my_recipes/<int:id>', methods=['POST'])
def delete_recipe(id):
    '''Delete Recipe'''
    recipe = My_Recipes.query.get_or_404(id)
    if recipe.user_id == session['user_id']:
        db.session.delete(recipe)
        db.session.commit()
        flash('Recipe Deleted!')
        return redirect('/my_recipes')
    flash('You Dont Have The Permission To Do That.')
    return redirect('/my_recipes')


@app.route('/search', methods=['POST'])
def search():
    search_value = request.form.get('searchInput')

    if not search_value:
        return render_template('index.html', error='Please enter a search value')

    api_url = f'https://api.edamam.com/search?q={search_value}&app_id=8be19060&app_key=229ab3365ee8d660b03ce476d4920033&from=0&to=10'

    try:
        response = requests.get(api_url)
        data = response.json()
        recipes = data.get('hits', [])

        for recipe in recipes:
            recipe['calories'] = recipe['recipe'].get('calories', 0)

        return render_template('index.html', recipes=recipes)
    except Exception as e:
        return render_template('index.html', error=f'Error fetching recipes: {str(e)}')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User.register(username, password)
        
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        flash('Welcome! Successfully Created your Account!')
        return redirect('/my_recipes')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome Back, {user.username}!')
            session['user_id'] = user.id
            return redirect('/my_recipes')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash('See You Soon!')
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)