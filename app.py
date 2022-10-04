import os 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from flask_swagger_ui import get_swaggerui_blueprint
import jwt

import re
from flask_bcrypt import Bcrypt
from flask import Flask,jsonify,request,make_response
from flask_marshmallow import Marshmallow
from functools import wraps
# import uuid # for public id
from  werkzeug.security import generate_password_hash, check_password_hash
# imports for PyJWT authentication


app = Flask(__name__)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app) 
db.create_all()



migrate = Migrate(app, db)



class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True)
    email = db.Column(db.String(40), index = True, nullable=True)
    password = db.Column(db.String(128))
     
    def __repr__(self):
        return f"User('{self.username}'"

 
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)   
    title = db.Column(db.String(100), nullable=False) 
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Post('{self.title}'"
 
   

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
    user = db.relationship('User', backref='comment')
    post = db.relationship('Post', backref='comment')
 
    def __repr__(self):
        return f"Comment('{self.id}'"


SWAGGER_URL = '/swagger/'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "restapi_app"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)





def validate(data, regex):
    """Custom Validator"""
    return True if re.match(regex, data) else False

def validate_password(password: str):
    """Password Validator"""
    reg = r"\b^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$\b"
    return validate(password, reg)

def validate_user(**args):
    """User Validator"""
    if  not args.get('username') or not args.get('email') or not args.get('password'):
        return {
            'email': 'Email is required',
            'password': 'Password is required',
            'username': 'Name is required'
        }
    if not isinstance(args.get('username'), str) or \
        not isinstance(args.get('email'), str) or not isinstance(args.get('password'), str):
        return {
            'email': 'Email must be a string',
            'password': 'Password must be a string',
            'username': 'Name must be a string'
        }
    
    if not validate_password(args.get('password')):
        return {
            'password': 'Password is invalid, Should be atleast 8 characters with \
                upper and lower case letters, numbers and special characters'
        }
    if not 2 <= len(args['name'].split(' ')) <= 30:
        return {
            'name': 'Name must be between 2 and 30 words'
        }
    return True



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
       
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['id']).first()
            print(current_user,"hiiiiiiii")
        except:
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated



@app.route('/user', methods =['GET'])
# @token_required
def get_all_users():
    
    users = User.query.all()
    print()
    
    output = []
    for user in users:
        # appending the user data json
        # to the response list
        output.append({
            'id':user.id,
            'username' : user.username,
            'email' : user.email,
            'password':user.password
        })
  
    return jsonify({'users': output})



@app.route('/signup', methods =['POST'])
def signup():
    data = request.json
    username= data.get('username')
    email =data.get('email')
    password = data.get('password')
  
    # checking for existing user
    user = User.query.filter_by(email = email).first()
    if not user:
        # database ORM object
        user = User(
          
            username = username,
            email = email,
            password = generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
  
        return make_response('Successfully registered.', 201)
    else:
        return make_response('User already exists. Please Log in.', 202)
  

@app.route('/login', methods =['POST'])
def login():
    
    auth = request.json
  
    if not auth or not auth.get('email') or not auth.get('password'):
             return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
        )
  
    user = User.query\
        .filter_by(email = auth.get('email'))\
        .first()
  
    if not user:
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
        )
  
    if check_password_hash(user.password, auth.get('password')):
        token = jwt.encode({
            'id': user.id,
            'exp' : datetime.utcnow() + timedelta(minutes = 30)
        }, app.config['SECRET_KEY'])
  
        return make_response(jsonify({'token' : token}), 201)
    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
    )        

    
  
@app.route('/getuser', methods = ['GET'])
def get_user():   
    user= User.query.all()
    result = {}
    j=0
   
    for i in user:
        result[j] = i.username
        j = j+1
    
    print(result)
    return result

  





@app.route("/user_delete/<int:id>/", methods=["DELETE"])
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if user:
        print(user)
        db.session.delete(user)
        db.session.commit()
        return jsonify({
                "message": "successfully deleted a user",
            }), 200
    return jsonify({
        "message": "user not found",
    }), 404


@app.route('/post_list', methods=['GET'])
def get_post():
    post = Post.query.all()
    print(post)
    output = []

    for i in post:
        post_data = {}
        post_data['id'] = i.id
        post_data['title'] = i.title
        post_data['description'] = i.description
        post_data['user_id'] = i.user_id
        post_data['date_posted ']=i.date_posted 
        output.append(post_data)

    return jsonify({'Posts': output})





@app.route("/add_post", methods=['POST'])
def add_post():
    try:
        post = request.json

        if not post:
            return {
                "message": "Invalid data,",
                "data": None,
                "error": "Bad Request"
            }, 400
        post = Post(title=post['title'], description=post['description'],user_id=post['user_id'] )
        db.session.add(post)
        db.session.commit()
        if not post:
            return {
                "message": "The post has been created by user",
                "data": None,
                "error": "Conflict"
            }, 400

        return jsonify({
            "message": "successfully created a new post",
            "data": post
        }), 201

    except Exception as e:
        return jsonify({
            "message": "failed to create a new post",
            "error": str(e),
            "data": None
        }), 500
   

@app.route("/get_post/<int:user_id>/", methods=["GET"])
def get_posts(user_id):
    try:
        posts = Post.query.get(user_id)
        response={}
        response['id']=posts.id
        response['title']=posts.title
        response['description']=posts.description
        response['user_id']=posts.user_id
        print(posts)
        return jsonify({
            "message": "successfully retrieved all posts",
            "data": response
        })
    except Exception as e:
        return jsonify({
            "message": "failed to retrieve all post",
            "error": str(e),
            "data": None
        }), 500


@app.route("/update_post/<int:id>/", methods=['PUT'])
def update_post(id):
    data = request.json
    print(data)
    post = Post.query.filter_by(id=id).first()
    # post= Post.query.all()
    # for p in post:
        # print(p,'this is p ')
    # print("This is post data >>>>>>>>>>>>>>>",post)
    if post:
        post.title = data.get("title")
        post.description = data.get("description")
        db.session.commit()
        return jsonify({'message': "post is updated!"})
    else:
        return jsonify({'message': "post not found!"})

   

@app.route("/post_delete/<int:id>/", methods=["DELETE"])
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    if post:
        print(post)
        db.session.delete(post)
        db.session.commit()
        return jsonify({
                "message": "successfully deleted a post",
                "data": None
            }), 200
    return jsonify({
        "message": "post not found",
    }), 404

   

@app.route('/get_comment', methods=['GET'])
def get_comment():
    comment = Comment.query.filter_by(id=1).first()
    print(comment.content, "comment")
    return jsonify({
        "message": "successfully get a comments",
        "data": comment
    }), 200


@app.route('/add_comment', methods=['POST'])
def add_comment():
    data = request.json

    # print("data==========",type(data),data, data['content'], data['post'], data['user_id'], data['user'])
    try:

        comment= Comment(content=data['content'],post_id=data['post'],user_id=data['user_id'])
        # print(comment)
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": e})

    return jsonify({'message': "post is created!"})
   

@app.route("/update_comment/<int:id>/", methods=['PUT'])

def update_comment(id):
    data = request.json
    print(data)
    comment = Comment.query.filter_by(id=id).first()
    print('-----')
    if comment :
        comment.content = data.get("content")
        db.session.commit()
        return jsonify({'message': "comment is updated!"})
    else:
        return jsonify({'message': "comment is not found!"})

@app.route("/comment_delete/<int:id>/", methods=["DELETE"])
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    if comment:
        print(comment)
        db.session.delete(comment)
        db.session.commit()
        return jsonify({
                "message": "successfully deleted a comment",
                "data": id
            }), 200
    return jsonify({
        "message": "comment not found",
    }), 404



if __name__ =="__main__":
 db.create_all()   
 app.run(debug=True) 

