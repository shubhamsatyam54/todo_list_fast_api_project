# todo_list_fast_api_project

- It is a Python Project based on FastApi framework created for keeping track of to-do-list.
- It keeps the track of to-do-list.
- Uses Mysql for database.
- Requirement file is also available for required packages.
- Files are commented for proper understanding of the code

## Usage:

- Open *config.ini* and declare the required variables then save the file:
    - mysql
        - `host` : mysql hostname
        - `port` : mysql port
        - `username` : mysql username
        - `password` : mysql password
        - `database` : mysql database
    - JWT_Auth
        - `SECRET_KEY` :Secret key for JWT authentication token
        - `ALGORITHM` : Algorithm for generating JWT authentication token

- Open *main.py* run the main function
- Another method: Run this command in terminal
    - `uvicorn main:main_app --host 0.0.0.0 --port 80`
- Access the api at *localhost:port*

### Schema Details

- *auth* app
    - | Name        |    Type     |                           Description                            | 
          |:-----------:|:----------------------------------------------------------------:|:------------|
      | title       |   string    |                        Title of the task                         |
      | description |   string    |                  Description detail of the task                  |
      | status      |   string    | Status of the task {``not started``, ``ongoing``, ``completed``} |
- *todo* app
    - | Name      |  Type   | Description          | 
          |:-------:|:--------:|:------------|
      | username  | string  | Username of the user |
      | passsword | string  | Password of the user |

### API Support for `auth` app used for authentication

| Url                   | Method | Description                                        |
|:----------------------|:------:|:---------------------------------------------------|
| localhost:port/signup |  POST  | Allow to create new user id  and password          |
| localhost:port/login  |  POST  | Allow to login using existing user id and password |

### API Support for `todo` app used for CRUD operations of tasks

| Url                         | Method | Description                                |
|:----------------------------|:------:|:-------------------------------------------|
| localhost:port/             |  GET   | Return the list of task and their status   |
| localhost:port/todo         |  GET   | Return the full details  of all the tasks  |
| localhost:port/todo         |  POST  | Allows to create a new Task                |
| localhost:port/todo{title}  |  GET   | Return all details to specific task title  |
| localhost:port/todo/{title} |  PUT   | Allows to update the specific task details |
| localhost:port/todo/{title} | DELETE | Allows to delete any specific task         |

### Extra Info:

- *auth.py* contains `auth` app used for authentication
- *todo_app.py* contains `todo` app used for CRUD operations of tasks

  