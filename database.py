


# app = Flask(__name__)
# ma = Marshmallow(app)
# bcrypt = Bcrypt(app)

# app.config['SECRET_KEY'] = 'thisissecret'
# app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///app.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db=SQLAlchemy(app) 
# db.create_all()



# migrate = Migrate(app, db)




# class User(db.Model):
#     __tablename__ = 'user'
#     id = db.Column(db.Integer, primary_key = True)
#     username = db.Column(db.String(32), index = True)
#     email = db.Column(db.String(40), index = True, nullable=True)
#     password = db.Column(db.String(128))
     
#     def __repr__(self):
#         return f"User('{self.username}'"

 
# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)   
#     title = db.Column(db.String(100), nullable=False) 
#     description = db.Column(db.Text, nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

#     def __repr__(self):
#         return f"Post('{self.title}'"
 
   

# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(200), nullable=False)
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
#     post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
#     user = db.relationship('User', backref='comment')
#     post = db.relationship('Post', backref='comment')
 
#     def __repr__(self):
#         return f"Comment('{self.id}'"