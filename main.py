import uvicorn  # import uvicorn for server creating server for FastApi framework
from fastapi import FastAPI  # importing FastAPI module

from myauth import auth as auth_  # importing auth app from auth  module
from todo_app import todo  # importing myapi app from todo_app file module

main_app = FastAPI()  # creating main app for our TO-DO-app
main_app.include_router(auth_.router)  # Importing auth app router to main app
main_app.include_router(todo.router)  # Importing myapi app router to main app

# craeting main function
if __name__ == "__main__":
    uvicorn.run("main:main_app", reload=True)  # creating server for execution
