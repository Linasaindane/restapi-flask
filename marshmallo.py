from flask import current_app as app
from flask_marshmallow import Marshmallow


ma = Marshmallow(app)


class UserSchema(ma.Schema):
    class Meta:
        
        fields = ("username", "email", "password")



class PostSchema(ma.Schema):
    class Meta:
        fields = ("title", "description", "user_id"," date_posted ")
  

class CommentSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("content", "created_at", "user_id","post_id")
  

