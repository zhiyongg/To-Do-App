from flask import Flask, render_template, url_for, redirect, session
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with,abort


app = Flask(__name__)

# Database using SQLite
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

# Define User table
class userModel(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<User {self.id}>"

#-------------------------Login-------------------------------------
oauth = OAuth(app)
app.config['SECRET_KEY'] = "your-super-secret-key"

# Replace with your actual App ID and App Secret
app.config['GOOGLE_CLIENT_ID'] = "Your Google OAuth Client ID"
app.config['GOOGLE_CLIENT_SECRET'] = "Your Google OAuth Client Secret"

app.config['GITHUB_CLIENT_ID'] = 'Your Github OAuth Client ID'
app.config['GITHUB_CLIENT_SECRET'] = 'Your Github OAuth Client Secret'

app.config['FACEBOOK_CLIENT_ID'] = 'Your Facebook OAuth Client ID'
app.config['FACEBOOK_CLIENT_SECRET'] = 'Your Facebook OAuth Client Secret'

# Register Google, GitHub, and Facebook as OAuth
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    # Add this line for OpenID Connect discovery
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
    )

github = oauth.register(
    name='github',
    client_id=app.config['GITHUB_CLIENT_ID'],
    client_secret=app.config['GITHUB_CLIENT_SECRET'],
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# Facebook registrations
facebook = oauth.register(
    name='facebook',
    client_id=app.config['FACEBOOK_CLIENT_ID'],
    client_secret=app.config['FACEBOOK_CLIENT_SECRET'],
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    api_base_url='https://graph.facebook.com/',
    client_kwargs={'scope': 'email public_profile'},
)

# Default route
@app.route('/')
def index():
  return render_template('index.html')

# To-do Page after login
@app.route('/todo')
def todo():
    return render_template('todo.html')

# Google login route
@app.route('/login/google')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


# Google authorize route
@app.route('/login/google/authorize')
def google_authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    userinfo = token.get('userinfo')

    if userinfo:
        user_id = userinfo.get('sub')  # <-- Google's unique user id
        session['user_id'] = user_id
        print(f"\n[Google] User ID: {user_id}")
        return redirect(url_for('todo'))
    else:
        resp = google.get('userinfo').json()
        return "Google login fallback."


# Github login route
@app.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)


# Github authorize route
@app.route('/login/github/authorize')
def github_authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    resp = github.get('user').json()
    user_id = resp.get('id')  # <-- GitHub's unique user id
    session['user_id'] = user_id
    print(f"\n[GitHub] User ID: {user_id}")
    # return f"Hello, {resp.get('login')}! Your GitHub User ID is {user_id}."
    return redirect(url_for('todo'))

# Facebook login route
@app.route('/login/facebook')
def facebook_login():
    facebook = oauth.create_client('facebook')
    redirect_uri = url_for('facebook_authorize', _external=True)
    return facebook.authorize_redirect(redirect_uri)


# Facebook authorize route
@app.route('/login/facebook/authorize')
def facebook_authorize():
    facebook = oauth.create_client('facebook')
    token = facebook.authorize_access_token()
    resp = facebook.get('me?fields=id,name,email,picture').json()
    user_id = resp.get('id')  # <-- Facebook's unique user id
    session['user_id'] = user_id  # <-- FIXED
    print(f"\n[Facebook] User ID: {user_id}")
    user_name = resp.get('name', 'Facebook User')
    return f"Hello, {user_name}! Your Facebook User ID is {user_id}."



#------------------To do App--------------------------------------


# Define item table for user task
class itemModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    userID = db.Column(db.String(200), db.ForeignKey('user_model.id'), nullable=False)

    def __repr__(self):
        return f"Item(id={self.id}, title={self.title}, completed={self.completed}, userID = {self.userID})"

# Define the expected inputs
item_args = reqparse.RequestParser()
item_args.add_argument('title', type=str, required=True, help="Title cannot be blank")
item_args.add_argument('completed', type=bool, required=False, help="Status must be true or false")
item_args.add_argument('userID', type=int, required=True, help="User ID is required")

# The format of the output in JSON
itemFields = {
    'id':fields.Integer,
    'title':fields.String,
    'completed':fields.Boolean,
    'userID':fields.Integer,
}

class Items(Resource):
    #List all the task
    @marshal_with(itemFields)
    def get(self):
        if 'user_id' not in session:
            abort(401, message="You must login first")
        # Only get items for the logged-in user
        items = itemModel.query.filter_by(userID=session['user_id']).all()
        return items

    # Add new task
    @marshal_with(itemFields)
    def post(self):
        if 'user_id' not in session:
            abort(401, message="You must login first")
        args = item_args.parse_args()
        if not args["title"].strip():
            abort(400, message="Title cannot be blank or empty string")

        # Auto-fill userID from session
        item = itemModel(
            title=args["title"],
            completed=args.get("completed", False),
            userID=session["user_id"]  # Auto set
        )
        db.session.add(item)
        db.session.commit()
        return item, 201

class Item(Resource):

    # Get the specific task
    @marshal_with(itemFields)
    def get(self, id):
        if 'user_id' not in session:
            abort(401, message="You must login first")
        item = itemModel.query.filter_by(id=id, userID=session['user_id']).first()
        if not item:
            abort(404, "Item not found")
        return item

    # Update the task status
    @marshal_with(itemFields)
    def patch(self, id):
        if 'user_id' not in session:
            abort(401, message="You must login first")
        args = item_args.parse_args()
        item = itemModel.query.filter_by(id=id, userID=session['user_id']).first()
        if not item:
            abort(404, "Item not found")
        item.title = args["title"]
        if args.get('completed') is not None:
            item.completed = args['completed']
        db.session.commit()
        return item

    # Delete the task
    @marshal_with(itemFields)
    def delete(self, id):
        if 'user_id' not in session:
            abort(401, message="You must login first")
        item = itemModel.query.filter_by(id=id, userID=session['user_id']).first()
        if not item:
            abort(404, "Item not found")
        db.session.delete(item)
        db.session.commit()
        return item, 200

# API end point
api.add_resource(Items,'/api/items/')
api.add_resource(Item,'/api/items/<int:id>')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
