from flask import Flask,request,make_response, flash
from db import db
import ssl

from celery import Celery
from model import User
from flask_mail import Mail,Message


app = Flask(__name__)





app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] =  465
app.config['MAIL_USERNAME'] = 'leenasaindane80@gmail.com'
app.config['MAIL_PASSWORD'] = 'ggnjlonkojqxmzsq'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER']='leenasaindane80@gmail.com'
mail=Mail(app)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
celery = Celery(app.name, broker='redis://localhost:6379/0')
db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()


with app.app_context():
   db.create_all()

from user import users
app.register_blueprint(users)


from post import posts
app.register_blueprint(posts)

from comment import comments
app.register_blueprint(comments)


@celery.task
def send_async_email(email_data):
    msg = Message(email_data['subject'],
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email_data['to']])
    msg.body = email_data['body']
    with app.app_context():
        mail.send(msg)


@app.route('/email', methods=['GET', 'POST'])
def index():
    # user = User.query.filter_by(email = email).first()
    # print(user)
    print(ssl.OPENSSL_VERSION)
    # email = request.form['email']
    email = request.json.get('email')
    print(email,'----')
    
    email_data = {
        'subject': 'Hello Lina,!',
        'to': email,
        'body': 'Hey ,Lina how are you! sending mail from blog application,'
    }
 
    send_async_email.delay(email_data)
    flash('Sending email to {0}'.format(email))

    return make_response('Successfully email.', 201)
 



if __name__ =="__main__":
 
    app.run(debug=True)     