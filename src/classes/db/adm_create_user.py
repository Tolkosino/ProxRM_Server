from classes.db.user import DB_User

user = DB_User()

username = input("Enter a username: ")
password = input("Enter a password: ")
permissions = input("Enter user permissions: ")

user.create_user(username, password, permissions)