import configparser  # importing config file reader

import mysql.connector  # importing mysql connector
from fastapi import FastAPI, HTTPException, Depends  # importing fastapi modules
from fastapi.security import OAuth2PasswordBearer  # importing fastapi oath2 module
from pydantic import BaseModel  # importing pydantic for backwards compatibility

config = configparser.ConfigParser()  # initialize config parser
config.read('config.ini')  # reading config.ini file
host = config["mysql"]["host"]  # setting host
port = config["mysql"]["port"]  # setting port
user = config["mysql"]["username"]  # setting username
password = config["mysql"]["password"]  # setting password
database = config["mysql"]["database"]  # setting database

# creating MysqlConnection
mydb = mysql.connector.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

"""
Creating database table : Task
"""
mycursor = mydb.cursor(dictionary=True)  # creating mysql cursor
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS tasks (title VARCHAR(255) PRIMARY KEY, description VARCHAR(255), status VARCHAR(20))")  # sql query to create table
mycursor.close()  # closing the cursor

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # Creating authentication dependency on OAuth2

todo = FastAPI(
    dependencies=[Depends(oauth2_scheme)])  # Creating FastApi app for tasks and adding dependencies for authentication


class Task(BaseModel):
    """
    Task model

    title: name of the task
    description: description of the task
    status: status of the task ["not started", "ongoing", "completed"]
    """
    title: str
    description: str
    status: str


@todo.get("/", tags=["Home"])
async def root():
    """
    Root endpoint
     Tagging under : Home

     :return : list of tasks and their status
    """
    mycursor = mydb.cursor(dictionary=True)  # sql query to retrieve data from mysql database
    mycursor.execute("SELECT title, status FROM tasks")  # sql query to retrieve data from mysql database
    tasks = mycursor.fetchall()  # get list of tasks
    mycursor.close()  # close the cursor
    return tasks  # return list of tasks


@todo.get("/todo", tags=["To-Dos"])
async def get_todos():
    """
    Get Todo endpoint
     Show tasks in detailed form
     Tagging under : To-Dos

     :returns : list of tasks
    """
    mycursor = mydb.cursor(dictionary=True)  # create mysql cursor
    mycursor.execute("SELECT title, description, status FROM tasks")  # sql query to retrieve data from mysql database
    tasks = mycursor.fetchall()  # get list of tasks
    mycursor.close()  # close the cursor
    return tasks  # return list of tasks


@todo.post("/todo", tags=["To-Dos"])
async def create_todo(task: Task) -> dict:
    """
        Create Todo endpoint
         Creates a new Task
         Input a Task object and saves it to mysql
         Tagging under : To-Dos

         :param task: Task object
         :return: Dictionary object of the created task data

        """

    mycursor = mydb.cursor(dictionary=True)  # create mysql cursor

    """
    Inititalize the variable from Task object
    """
    title = task.title  # name of the task
    description = task.description  # description of the task
    status = task.status  # status of the task

    """
    Checks for the compatible input of task status
    """
    status_opt = ["not started", "ongoing", "completed"]
    if not status in status_opt:
        raise HTTPException(status_code=404,
                            detail="Status input incompatible")  # Raise error if task status is not supported

    """
    inserting the task to the database
    """
    try:
        sql = "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)"  # sql query to insert
        val = (title, description, status)  # values for sql query
        mycursor.execute(sql, val)  # executing sql query
        mydb.commit()  # committing the change to mysql
        mycursor.close()  # close the cursor
    except:
        raise HTTPException(status_code=404, detail="task name already exist")  # raise an error for existing tasks name

    return {"title": title, "description": description, "status": status}


def validate_title(title):
    """
    Function to check if the title is valid at the time of accessing the specific task through localhost/todo/<title>
    api call

    :param title: title of the task
    :return: True if the title is valid else False
    """
    mycursor = mydb.cursor(dictionary=True)  # creating mysql cursor
    sql = "SELECT *FROM tasks where title = %s"  # sql query to retrieve data from mysql database
    val = (title,)  # value for the query
    mycursor.execute(sql, val)  # executing the query
    task = mycursor.fetchone()  # fetching any data available from mysql database
    mycursor.close()  # close the cursor
    if task is None:  # checking for availability of data
        return False  # returning False if no data available
    return True  # returning True if data available


@todo.get("/todo/{title}", tags=["Task"])
async def get_task(title) -> dict:
    """
    Get Task endpoint
     Show details of a specific task
     Tagging under : Task

     :param title: title of the task
     :return: dictionary object of the task details for the title task

    """

    mycursor = mydb.cursor(dictionary=True)  # creating mysql cursor
    sql = "SELECT *FROM tasks where title = %s"  # sql query to retrieve data from mysql database
    val = (title,)  # value for the query
    mycursor.execute(sql, val)  # executing the query
    task = mycursor.fetchone()  # fetching any data available from mysql database
    mycursor.close()  # close the cursor

    if task is None:
        raise HTTPException(status_code=404, detail="task name does not exist")  # if task not available raise error

    return task  # return task details


@todo.put("/todo/{title}", tags=["Task"])
async def update_task(title, task: Task) -> dict:
    """Updates a task
        Input a Task object and saves it to mysql after the update process
        Tagging under : Task
        :param title: title of the task which details have to change
        :param task: Task object with new details
        :return: Dictionary object of the updated task data

        Will have to provide all the three attributes of the task object whenever the task
        have to be updated, either one on more attributes have to be changed, keep the old values remaining attributes
    """

    if not validate_title(title):  # validate title
        raise HTTPException(status_code=404, detail="task name does not exist")  # Raise error if title does not exist

    """
    Initilalize the required attributes
    """
    mycursor = mydb.cursor(dictionary=True)  # create mysql cursor
    new_title = task.title  # new title for the task
    description = task.description  # new description for the task
    status = task.status  # new status for the

    """
    Checks for the compatible input of task status
    """
    status_opt = ["not started", "ongoing", "completed"]
    if not status in status_opt:
        raise HTTPException(status_code=404,
                            detail="Status input incompatible")  # Raise an error if input for status is not supported

    """
    updating the values to mysql 
    """
    try:
        sql = "UPDATE tasks SET title = %s, description = %s, status = %s WHERE title = %s"  # query for update
        val = (new_title, description, status, title)  # values for the query
        mycursor.execute(sql, val)  # execute the query
        mydb.commit()  # commit the changes to the query

    except Exception:
        raise HTTPException(status_code=404,
                            detail="task name already exist")  # Raise error if title name is changed to something exists already in the database

    return {"title": task.title, "description": task.description,
            "status": task.status}  # Return the updated values of the task


@todo.delete("/todo/{title}", tags=["Task"])
async def delete_task(title):
    """
    Delete Task endpoint
     Deletes a specific task
     Tagging under : Task

     :param: title: title of the task
     :return: Status of the task
    """
    if not validate_title(title):  # validate title
        raise HTTPException(status_code=404, detail="task name does not exist")  # Raise error if title name not valid
    mycursor = mydb.cursor(dictionary=True)  # create mysql cursor
    sql = "DELETE FROM tasks WHERE title = %s"  # sql query for deletion of task
    val = (title,)  # value for the query
    mycursor.execute(sql, val)  # execute the query
    mydb.commit()  # commit the changes to database
    return {"Done": "Deleted Successfully"}  # return status
