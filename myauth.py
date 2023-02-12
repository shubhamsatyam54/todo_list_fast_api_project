import configparser  # importing config file reader
import datetime  # importing datetime manupulating time

import bcrypt as bcrypt  # import bcrypt for hashing passworda
import jwt  # importing JTW authentication
import mysql.connector  # importing mysql.connector
from fastapi import FastAPI, HTTPException, Depends  # import FastAPI modules
from fastapi.security import OAuth2PasswordRequestForm  # import FastAPI authentications modules
from pydantic import BaseModel  # importing pydantic for backwards compatibility

config = configparser.ConfigParser()  # initialize config parser
config.read('config.ini')  # reading config.ini file
host = config["mysql"]["host"]  # setting host
port = config["mysql"]["port"]  # setting port
user = config["mysql"]["username"]  # setting username
password = config["mysql"]["password"]  # setting password
database = config["mysql"]["database"]  # setting database
SECRET_KEY = config["JWT_Auth"]["SECRET_KEY"]  # setting secret key for tokening purposes
ALGORITHM = config["JWT_Auth"]["ALGORITHM"]  # setting algo for tokening purposes

# creating MysqlConnection
mydb = mysql.connector.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

"""
Connecting to m server for creating of Table of task
"""
mycursor = mydb.cursor(dictionary=True)  # creating mysql cursor
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS users (username VARCHAR(255) UNIQUE,password VARCHAR(255))")  # sql query to create table
mycursor.close()  # closing the cursor

auth = FastAPI()  # Creating FastApi app for user authentication


class User(BaseModel):
    """
    Model for user authentication

    username: username to authenticate
    password: password to authenticate
    """
    username: str
    password: str


def create_token(data):
    """
    Function to create token for user authentication

    :param: data: username of  the current user
    :return: token for user authentication
    """

    # craeting payload for token creation
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),  # time expiration of token
        "iat": datetime.datetime.utcnow(),  # time of creation of
        "sub": data  # date of user
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)  # create token

    return token  # return token


@auth.post("/signup", tags=["user"])
async def create_user(user: User):
    """
    Function to register a new user
    Tagging under : User

    :param user: User object to create a user in database
    :return: the status of creation

    """
    mycursor = mydb.cursor(dictionary=True)  # create mysql cursor

    """
    creating the new user and saving it to the mysql database
    """
    try:
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())  # hashing the password
        sql = "INSERT INTO users (username, password) VALUES (%s, %s)"  # sql query to insert the new user to the mysql database
        val = (user.username, hashed_password)  # values for the sql query
        mycursor.execute(sql, val)  # executing the sql query
        mydb.commit()  # comminting the change to mysql database
        mycursor.close()  # close the cursor
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail="Username already exists")  # Raise an error if username already exists

    return {"message": f"User : {user.username} created successfully"}  # return the status for successful creation


@auth.post("/login", tags=["user"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Function to login a user
    Tagging under : User

    :param form_data: user object to login using the oath2 form
    :return: token a generated JWT token for the user

    """
    mycursor = mydb.cursor(dictionary=True)  # create mysql cursor

    sql = "SELECT  username, password FROM users WHERE username = %s"  # query to retrive data from databse for the user tried login
    val = (form_data.username,)  # value for the query
    mycursor.execute(sql, val)  # executing query
    result = mycursor.fetchone()  # fetching available data from databse
    mycursor.close()  # close the cursor
    if not result:
        raise HTTPException(status_code=400,
                            detail="Incorrect username")  # raise an error if user not present in the databse
    user_username, user_password = result['username'], result[
        'password']  # else capture the username password it got from the database
    if not bcrypt.checkpw(form_data.password.encode('utf-8'), user_password.encode(
            'utf-8')):  # compares the password entered and the password in the databse with hashing them
        raise HTTPException(status_code=400, detail="Incorrect password")  # raise an error if the password is incorrect

    token = create_token(form_data.username)  # creates token if username and password matches the database
    return {"access_token": token, "token_type": "bearer"}  # return token for succesfull login
