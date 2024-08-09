from typing import Any, List
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(500))
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self) -> str:
        return f"Post {self.id}"

@app.route("/")
def index():
    top_posts = Post.query.order_by(Post.date_created).all()[:5]
    return render_template("home.html", top_posts=top_posts)

@app.route("/posts/create/", methods=["POST", "GET"])
def post_create():
    if request.method == "POST":
        try:
            post_title = request.form["title"]
            post_body = request.form["body"]
            new_post = Post(title=post_title, body=post_body) # type:ignore
            db.session.add(new_post)
            db.session.commit()
        except:
            return "<div><style>color: red</style><h1>An error occurred while creating your post</h1></div>"
        return redirect("/")
    else:
        return render_template("create-post.html")

@app.route("/posts/<int:id>")
def view_post(id: int):
    post = Post.query.get(id)
    return render_template("post.html", post=post)

@app.route("/admin/")
def admin():
    page = request.args.get("page")
    per_page = request.args.get("perpage")
    if page == None or not page.isdigit():
        page = 0
    else:
        page = int(page)
    if per_page == None or not per_page.isdigit():
        per_page = 10
    else:
        per_page = int(per_page)
    posts = Post.query.order_by(Post.date_created).all()
    pages = len(posts) // per_page + 1
    posts = posts[
        page*per_page:
        (page*per_page)+per_page
    ]
    return render_template("admin.html", posts=posts, page_count=pages, per_page=per_page)

@app.route("/admin/delete/<int:id>")
def admin_post(id: int):
    try:
        db.session.delete(Post.query.get(id))
        db.session.commit()
    except:
        return "<div><style>color: red</style><h1>An error occurred while deleting the post</h1></div>"
    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True)

#* Import app to create db *#
if __name__ == "app":
    def app_context(func):                                                                                            
        def inner(args: List[Any]):
            with app.app_context():
                func(*args)
        return inner  
       
    @app_context
    def remove_post(post_id: int):
        db.session.delete(Post.query.get(post_id))
        db.session.commit()
    
    @app_context
    def create_all():
        db.create_all()
