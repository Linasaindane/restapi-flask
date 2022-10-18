import re
from functools import wraps
from flask import Flask,jsonify,request,Blueprint,make_response
import jwt
from  werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from db import db
from flask import current_app as app
from model import User
from apscheduler.schedulers.background import BackgroundScheduler


users=Blueprint('users',__name__)

sched = BackgroundScheduler(daemon = True)
sched.start()


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



@users.route('/user', methods =['GET'])
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        output.append({
            'id':user.id,
            'username' : user.username,
            'email' : user.email,
            'password':user.password
        })
    app.logger.info('Showing list of User')
    print('User is login on :-----',output)
    return jsonify({'users': output})


@sched.scheduled_job(trigger = 'cron', minute = '*')
def print_login_user():
    # get_all_users()
    # users = User.query.get(id=1)
 
    print('Working on Blog application by User')



@users.route('/signup', methods =['POST'])
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
        app.logger.info('Add user in Database')
        return make_response('Successfully registered.', 201)
    else:
        app.logger.error('Already exists !')
        return make_response('User already exists. Please Log in.', 202)
  

@users.route('/login', methods =['POST'])
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

    # email_data = {
    #     'subject': 'Hello from the other side!',
    #     'to': email,
    #     'body': 'Hey Paul, sending you this email from my Flask app, lmk if it works'
    # }

    # send_async_email.delay(email_data)
    # flash('Sending email to {0}'.format(email))    
  
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
  
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
    )        

    
  
# @users.route('/getuser', methods = ['GET'])
# def get_user():   
#     user= User.query.all()
#     result = {}
#     j=0
   
#     for i in user:
#         result[j] = i.username
#         j = j+1
    
#     print(result)
#     app.logger.info(' Showing all list of user')
#     return result

  





@users.route("/user_delete/<int:id>/", methods=["DELETE"])
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if user:
        print(user)
        db.session.delete(user)
        db.session.commit()
        app.logger.info('Delete User from Database')
        return jsonify({
                "message": "successfully deleted a user",
            }), 200
    return jsonify({
        "message": "user not found",
    }), 404
