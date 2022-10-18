
from flask import jsonify,request,Blueprint
from model import Comment
from db import db
from flask import current_app as app

comments=Blueprint('comments',__name__)


@comments.route('/get_comment', methods=['GET'])
def get_comment():
    comment = Comment.query.all()
    output = []
    app.logger.info('Showing list of User Post')
    for i in comment:
        comment_data = {}
        comment_data['id'] = i.id
        comment_data['content'] = i.content
        comment_data['created_at'] = i.created_at
        comment_data['user_id'] = i.user_id
        comment_data['post_id ']=i.post_id 
        output.append(comment_data)
        app.logger.info('Showing list of Comment by user')
 
    return jsonify({'Comment': output})
   

@comments.route('/add_comment', methods=['POST'])
def add_comment():
    data = request.json
    try:
        comment= Comment(content=data['content'],post_id=data['post_id'],user_id=data['user_id'])
        # print(comment)
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": e})

    return jsonify({'message': "post is created!"})
   

@comments.route("/update_comment/<int:id>/", methods=['PUT'])
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

@comments.route("/comment_delete/<int:id>/", methods=["DELETE"])
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    if comment:
        print(comment)   
        db.session.delete(comment)
        db.session.commit()
        app.logger.error('Delete the Comment by User ')
      
        return jsonify({
                "message": "successfully deleted a comment",
                "data": id
            }), 200
    return jsonify({
        "message": "comment not found",
    }), 404
