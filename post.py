from functools import wraps
from flask import jsonify,request
from flask import Blueprint
from db import db
from model import Post
from flask import current_app as app


posts=Blueprint('posts',__name__)

@posts.route('/post_list', methods=['GET'])
def get_post():
    post = Post.query.all()
    print(post)
    output = []
    app.logger.info('Showing list of User Post')
    for i in post:
        post_data = {}
        post_data['id'] = i.id
        post_data['title'] = i.title
        post_data['description'] = i.description
        post_data['user_id'] = i.user_id
        post_data['date_posted ']=i.date_posted 
        output.append(post_data)

    return jsonify({'Posts': output})





@posts.route("/add_post", methods=['POST'])
def add_post():
    post = request.json
    try:
        post = Post(title=post['title'], description=post['description'],user_id=post['user_id'] )
        db.session.add(post)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": e})

    return jsonify({'message': "post is created!"})
        # post = Post(title=post['title'], description=post['description'],user_id=post['user_id'] )
        # db.session.add(post)
        # db.session.commit()
        # app.logger.info('Add Post data of User in Database')
        # if not post:
        #     return {
        #         "message": "The post has been created by user",
        #         "data": None,
        #         "error": "Conflict"
        #     }, 400

        # return jsonify({
        #     "message": "successfully created a new post",
        #     "data": post
        # }), 201

    
   

@posts.route("/get_post/<int:user_id>/", methods=["GET"])
def get_posts(user_id):
    try:
        posts = Post.query.get(user_id)
        response={}
        response['id']=posts.id
        response['title']=posts.title
        response['description']=posts.description
        response['user_id']=posts.user_id
        print(posts)
        app.logger.info('Showing all list of Post by User')
        return jsonify({
            "message": "successfully retrieved all posts",
            "data": response
        })
    except Exception as e:
        app.logger.warning('failed to retrieve all post')
        return jsonify({
            "message": "failed to retrieve all post",
            "error": str(e),
            "data": None
        }), 500


@posts.route("/update_post/<int:id>/", methods=['PUT'])
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
        app.logger.info('Update data to Post Table ')
        return jsonify({'message': "post is updated!"})
    else:
        app.logger.info('Post of User is not Found ')
        return jsonify({'message': "post not found!"})

   

@posts.route("/post_delete/<int:id>/", methods=["DELETE"])
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    if post:
        print(post)
        db.session.delete(post)
        db.session.commit()
        app.logger.info('Adding data to Post Table ')
        return jsonify({
                "message": "successfully deleted a post",
            }), 200
    app.logger.warning(' Not Found')
    return jsonify({
        "message": "post not found",
    }), 404
