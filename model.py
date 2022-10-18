from datetime import datetime
from db import db
from flask import current_app as app
# from flask_marshmallow import Marshmallow






class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True)
    email = db.Column(db.String(40), index = True, nullable=True)
    password = db.Column(db.String(128))
     
    def __repr__(self):
        return f"User('{self.username}'"


# class UserSchema(ma.Schema):
#     class Meta:
#         # Fields to expose
#         fields = ("username", "email", "password")


 
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)   
    title = db.Column(db.String(100), nullable=False) 
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Post('{self.title}'"
 
# class PostSchema(ma.Schema):
#     class Meta:
#         # Fields to expose
#         fields = ("title", "description", "user_id"," date_posted ")
  

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

# class CommentSchema(ma.Schema):
#     class Meta:
#         # Fields to expose
#         fields = ("content", "created_at", "user_id","post_id")
  

SWAGGER_URL = '/swagger/'
API_URL = '/static/swagger.json'
# SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
#     SWAGGER_URL,
#     API_URL,
#     config={
#         'app_name': "restapi_app"
#     }
# )
# app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)



