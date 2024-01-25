# import the function that will return an instance of a connection
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re	# the regex module
# create a regular expression object that we'll use later
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    DB = "login_and_registration_schema"
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email_address = data['email_address']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    # Now we use class methods to query our database
    # READ all
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        # make sure to call the connectToMySQL function with the schema you are targeting.
        results = connectToMySQL(cls.DB).query_db(query)
        # protection
        if not results:
            return []
        # Create an empty list to append our instances of users
        users = []
        # Iterate over the db results and create instances of users with cls.
        for user in results:
            users.append( cls(user) )
        return users

    # READ - read a row/record in the data base by id
    @classmethod
    def get_one(cls, data):
        query = """SELECT * FROM users WHERE id = %(user_id)s;"""
        result = connectToMySQL(cls.DB).query_db(query, data)

        one_user = cls(result[0])
        return one_user

    # READ - read a row/record in the data base by email
    @classmethod
    def get_one_by_email(cls, data):
        query = """SELECT * FROM users WHERE email_address = %(email)s;"""
        result = connectToMySQL(cls.DB).query_db(query, data)

        if not result:
            return None

        return User(result[0])


    # READ - read a row/record in the data base by id
    # @classmethod
    # def get_one(cls, id):
    #     query = """SELECT * FROM users WHERE id = %(id)s;"""
    #     result = connectToMySQL(cls.DB).query_db(query, {"id" : id})
    #     # protection

    #     one_user = cls(result[0])
    #     return one_user

    # CREATE
    @classmethod
    def add(cls, data):
        query = """
            INSERT INTO users (first_name,last_name,email_address,password)
    	    VALUES (%(fname)s,%(lname)s,%(email)s,%(pwd)s);
        """
        user_id = connectToMySQL(cls.DB).query_db(query, data)
        return user_id
    
    # VALIDATE
    @staticmethod
    def validate_user(user):
        is_valid = True
        if len(user['fname']) < 3:
            flash("First Name must be at least 3 characters")
            is_valid = False
        if len(user['lname']) < 3:
            flash("Last Name must be at least 3 characters")
            is_valid = False

        if len(user['email']) < 3:
            flash("Email must be at least 3 characters", 'register')
            is_valid = False

        # test whether a field matches the pattern
        if not EMAIL_REGEX.match(user['email']):
            flash("Invalid email address!", 'register')
            is_valid = False

        # checks if email already in the database
        if (re.fullmatch(EMAIL_REGEX, user['email'])):
            this_user = {
                'email' : user['email']
            }
            results = User.check_database(this_user)
            if len(results) != 0:
                flash("Email already in use, try a different email", 'register')
                is_valid = False

        if len(user['pwd']) < 3:
            flash("Password must be at least 3 characters", 'register')
            is_valid = False

        # passwords to have a least 1 digit
        if (re.search('[0-9]', user['pwd']) == None ):
            flash("Password requires at least one digit", 'register')
            is_valid = False

        # passwords to have a least 1 uppercase letter
        if (re.search('[A-Z]', user['pwd']) == None ):
            flash("Password requires at least one uppercase letter", 'register')
            is_valid = False

        if user['pwd'] != user['pwd_confirm']:
            flash("Passwords does not match")
            is_valid = False

        return is_valid
    
    # VALIDATE
    @staticmethod
    def validate_login(user):
        is_valid = True

        # checks email
        if len(user['email']) < 3:
            flash("Email must be at least 3 characters", 'login')
            is_valid = False
        # test whether a field matches the pattern
        if not EMAIL_REGEX.match(user['email']):
            flash("Invalid email address!", 'login')
            is_valid = False

        # checks password
        if len(user['pwd']) < 3:
            flash("Password must be at least 3 characters", 'login')
            is_valid = False

        return is_valid
    
    # VALIDATE
    # checks database for emails in use
    @classmethod
    def check_database(cls, data):
        query = """SELECT * FROM users WHERE email_address = %(email)s;"""
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results
