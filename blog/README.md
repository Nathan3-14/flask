# Blog
## Dev Tools
To use any, run `python3` and once inside the shell, run `import app as a`
### Update / Create Database
To update or create the database, run `a.create_all()`
### Delete User
To delete a user, run `delete_user(<id: int> <delete_all: bool>)`, where delete all is preset to False, but if you want to remove all users, set it to True
### Add Admin
To add an admin, run `add_admin(<username: str>, <password: str>)`
