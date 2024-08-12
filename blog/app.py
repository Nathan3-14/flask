from typing import Any, List, Tuple
from flask import Flask, make_response, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
try:
    from s__encr import encr, decr
except ModuleNotFoundError:
    print("Please download encr file to use")
    quit()


def get_form_property(property: str, template_path: str) -> Tuple[bool, str]: #? (is_template, value)
    value = request.form[property]
    if value == "":
        return (True, render_template(template_path, needed_fields=[property]))
    return (False, value)


def set_cookie(cookie_name: str, value: Any, redirect_location: str="/"):
    response = make_response(redirect(redirect_location))
    response.set_cookie(cookie_name, value)
   
    return response


def get_cookie(cookie_name: str):
   value = request.cookies.get(cookie_name)
   return value


def render_template_full(notifications: List[str], *args, **kwargs) -> str:
    notification_string = ""
    for notification in notifications:
        notification_string += f"{notification}"
    
    current_user = get_current_user()
    if current_user == None:
        return render_template(*args, **kwargs, notifications=notification_string, no_user=True)

    return render_template(*args, **kwargs, notifications=notification_string, current_user=current_user.display_name)


def get_current_user() -> "User | None":
    current_user = User.query.filter_by(uuid=get_cookie("current_user")).first()
    return current_user


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(24))
    display_name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.Integer, nullable=False)
    permission_level = db.Column(db.Integer, default=0, nullable=False)

    def set_uuid(self):
        self.uuid = f"{self.display_name}{self.id}"

    def __repr__(self) -> str:
        return f"User {self.id} ({self.display_name})"



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(250), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self) -> str:
        return f"Comment {self.id}"

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
    return render_template_full([], "home.html", top_posts=top_posts)

@app.route("/users/login/", methods=["POST", "GET"])
def user_login():
    if request.method == "POST":
        try:
            uuid = get_form_property("uuid", "login-user.html")
            if uuid[0]: return uuid[1]
            uuid = uuid[1]
            password = get_form_property("password", "login-user.html")
            if password[0]: return password[1]
            password = password[1]

            current_user = User.query.filter_by(uuid=uuid).first()
            if current_user == None:
                return render_template_full([], "login-user.html", needed_fields=["uuid", "password"], failed=True)
            return set_cookie("current_user", current_user.uuid)
        except Exception as e:
            print(e)
            return "<div><style>color: red</style><h1>An error occurred while creating your user</h1></div>"
    else:
        return render_template_full([], "login-user.html", needed_fields=[])

@app.route("/users/create/", methods=["POST", "GET"])
def user_create():
    if request.method == "POST":
        try:
            user_name = request.form["username"]
            if user_name == "":
                return render_template_full([], "create-user.html", needed_fields=["username"])
            user_password = request.form["password"]
            if user_password == "":
                return render_template_full([], "create-user.html", needed_fields=["password"])
            
            new_user = User(display_name=user_name, password=encr(user_password)) # #type:ignore
            db.session.add(new_user)
            db.session.commit()
            new_user.set_uuid()
            db.session.commit()

            return set_cookie("current_user", new_user.uuid)
        except Exception as e:
            print(e)
            return "<div><style>color: red</style><h1>An error occurred while creating your user</h1></div>"
        
    else:
        return render_template_full([], "create-user.html", needed_fields=[])

@app.route("/posts/create/", methods=["POST", "GET"])
def post_create():
    if request.method == "POST":
        try:
            post_title = request.form["title"]
            if post_title == "":
                return render_template_full([], "create-post.html", needed_fields=["title"])
            
            post_body = request.form["body"]
            new_post = Post(title=post_title, body=post_body) # type:ignore
            db.session.add(new_post)
            db.session.commit()
        except Exception as e:
            print(e)
            return "<div><style>color: red</style><h1>An error occurred while creating your post</h1></div>"
        return redirect("/")
    else:
        return render_template_full([], "create-post.html", needed_fields=[])

@app.route("/posts/<int:id>/")
def view_post(id: int):
    post = session.get(id)
    return render_template("post.html", post=post)

@app.route("/admin/")
def admin():
    if get_current_user().permission_level != 2:
        return redirect("/")


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
    return render_template_full([], "admin.html", posts=posts, page_count=pages, per_page=per_page)

@app.route("/admin/delete/<int:id>/")
def admin_delete_post(id: int):
    try:
        db.session.delete(Post.query.get(id))
        db.session.commit()
    except Exception as e:
        print(e)
        return "<div><style>color: red</style><h1>An error occurred while deleting the post</h1></div>"
    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True)

#* Import app to create db *#
if __name__ == "app":
    def delete_user(id: int, all: bool=False):
        with app.app_context():
            if all:
                for user in User.query.order_by("id").all():
                    db.session.delete(user)
            else:
                db.session.delete(User.query.get(id))
            db.session.commit()
    
    def create_all():
        with app.app_context():
            db.create_all()
    
    def add_admin(uname: str, pword: str):
        with app.app_context():
            new_user = User(display_name=uname, password=encr(pword), permission_level=2)
            db.session.add(new_user)
            db.session.commit()
            new_user.set_uuid()
            db.session.commit()
