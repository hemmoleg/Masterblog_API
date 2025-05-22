from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog_API' # (3) You can change this if you like
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
    {"id": 3, "title": "Third post", "content": "This is the 3. post."},
    {"id": 4, "title": "Fourth post", "content": "This is the 4. post."},
    {"id": 5, "title": "Test post", "content": "This is the TEST post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort = request.args.get('sort')
    direction = request.args.get('direction')

    valid_fields = {'title', 'content'}
    valid_directions = {'asc', 'desc'}

    if sort or direction:
        if sort not in valid_fields:
            return jsonify({"error": f"Invalid sort field: '{sort}'. Must be 'title' or 'content'."}), 400
        if direction not in valid_directions:
            return jsonify({"error": f"Invalid direction: '{direction}'. Must be 'asc' or 'desc'."}), 400

        reverse = (direction == 'desc')
        sorted_posts = sorted(POSTS, key=lambda p: p[sort].lower(), reverse=reverse)
        return jsonify(sorted_posts)

    # Return unsorted if parameters are missing or invalid
    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json(silent=True)
    print(data)
    if data:
        title = data.get('title')
        content = data.get('content')
    else:
        title = request.form.get('title')
        content = request.form.get('content')

    if title is None:
        return jsonify({'error': 'title is None'}), 400

    if content is None:
        return jsonify({'error': 'content is None'}), 400

    post_id = POSTS[len(POSTS) - 1]['id']
    new_post = {
        'title': title,
        'content': content,
        'id': post_id + 1
    }
    POSTS.append(new_post)

    return new_post


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete(post_id):
    index_to_delete = next(
        (_idx for _idx, post in enumerate(POSTS) if post['id'] == post_id),
        -1
    )

    if index_to_delete == -1:
        return {'error': f'Post with id {post_id} not found'}, 404

    POSTS.pop(index_to_delete)

    return {'message': f'Post with id {post_id} has been deleted'}, 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update(post_id):
    data = request.get_json(silent=True)
    print(data)
    if data:
        title = data.get('title')
        content = data.get('content')
    else:
        title = request.form.get('title')
        content = request.form.get('content')

    if title is None:
        return jsonify({'error': 'title is None'}), 400

    if content is None:
        return jsonify({'error': 'content is None'}), 400

    for post in POSTS:
        if post["id"] == post_id:
            post["title"] = title
            post["content"] = content
            return post, 200

    return {'error': f'Np post with id {post_id} found'}, 400


@app.route('/api/posts/search', methods=['GET'])
def search():
    title = request.args.get('title')
    content = request.args.get('content')

    if not title and not content:
        return []

    results = [
        post for post in POSTS
        if(
            (title is None or title.lower() in post['title'].lower()) and
            (content is None or content.lower() in post['content'].lower())
        )
    ]

    return results, 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
