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
        pass
    else:
        return render_template("create-post.html")


if __name__ == "__main__":
    app.run(debug=True)

#* Import app to create db *#
if __name__ == "app":
    with app.app_context():
        db.create_all()
