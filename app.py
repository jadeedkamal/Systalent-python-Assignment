from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import Union
import re 

app = FastAPI()

class Task(BaseModel):
    title: str = None
    is_done : str = None
    user: str = None

class User(BaseModel):
    username: str = None
    password: str = None
    status: str = None

@app.get("/")
def root():
    con = sqlite3.connect("tasks.db")
    cur = con.cursor()

    try:
        cur.execute("CREATE TABLE tasks(title, status, user)")
        cur.execute("CREATE TABLE users(username, password, status)")   
        
        con.commit()
        cur.close()
    except:
        pass
    
    cur.close()
    return{"OBJECTIVE":"CREATE A TO-DO APPLICATION"}
    

# STORE A NEW TASK INTO DB
@app.post("/tasks/create/{taskname}", response_model=Task)
def create_item(taskname: str) -> Task:

    con = sqlite3.connect("tasks.db")
    cur = con.cursor()

    store = cur.execute("SELECT * FROM users WHERE status='True'").fetchall()
    if store!=[]:

        task = Task()
        task.title = taskname
        task.is_done = 'False'
        task.user = store[0][0]

        cur.execute(f"INSERT into tasks VALUES ('{task.title}','{task.is_done}', '{task.user}')")
        con.commit()
        cur.close()

        return task
    
    else:
        raise HTTPException(status_code=404, detail="Please Login First")

# VIEW ALL TASKS IN THE DB
@app.get("/tasks/all", response_model=list[Task])
def all_item() -> Task:
    con = sqlite3.connect("tasks.db")
    cur = con.cursor()

    store = cur.execute(f"SELECT * from tasks").fetchall()
    temp = []

    for i in store:
        task = Task()
        task.title = i[0]
        task.is_done = i[1]
        task.user = i[2]
        temp.append(task)

    return temp

# VIEW ALL TASK RELATED TO LOGGED IN USER
@app.get("/tasks/user", response_model=list[Task])
def get_item() -> Task:

    con = sqlite3.connect("tasks.db")
    cur = con.cursor()
    temp = cur.execute("SELECT * FROM users WHERE status='True'").fetchall()

    print(temp)
    if temp!=[]:
        user = temp[0][0]

    store = cur.execute(f"SELECT * from tasks WHERE user='{user}'").fetchall()
    print(store)
    temp = []

    for i in store:
        task = Task()
        task.title = i[0]
        task.is_done = i[1]
        task.user = user
        temp.append(task)

    return temp
    
# EDIT A SPECIFIC TASK IN DB 
@app.get("/tasks/edit/{task_id}", response_model=Task)
def edit_item(item_id: str) -> Task:

    con = sqlite3.connect("tasks.db")
    cur = con.cursor()
    temp = cur.execute("SELECT * FROM users WHERE status='True'").fetchall()
    if temp!=[]:
        user = temp[0][0]

    store = cur.execute(f"SELECT * from tasks WHERE title='{item_id}' AND user='{user}'").fetchall()
    
    print(store)
    if store != []:
        if store[0][1] == "False":
            cur.execute(f"UPDATE tasks SET status='True' WHERE title='{item_id}'")
        else:
            cur.execute(f"UPDATE tasks SET status='False' WHERE title='{item_id}'")

        con.commit()
        cur.close()
        task = Task()
            
        task.title = store[0][0]
        task.is_done = 'True'
        task.user=store[0][2]
        return task
    else:
        raise HTTPException(status_code=404, detail="task Not Found")

# DELETE A SPECIFIC TASK DB
@app.get("/tasks/delete/{task_id}", response_model=Task)
def delete_item(item_id: str) -> Task:

    con = sqlite3.connect("tasks.db")
    cur = con.cursor()
    temp = cur.execute("SELECT * FROM users WHERE status='True'").fetchall()
    if temp!=[]:
        user = temp[0][0]

    store = cur.execute(f"SELECT * from tasks WHERE title='{item_id}' AND user='{user}'").fetchall()
    
    if store != []:
        cur.execute(f"DELETE FROM tasks WHERE title='{item_id}'")
        con.commit()
        cur.close()
        task = Task()
            
        task.title = store[0][0]
        task.is_done = store[0][1]
        task.user = store[0][2]
        return task
    else:
        raise HTTPException(status_code=404, detail="task Not Found")

# CREATE A NEW USER
@app.get("/users/register/{u_name}", response_model=User)
def register_user(u_name: str, password: str) -> User:
    

    if re.match(r"[^@]+@[^@]+\.[^@]+", u_name):
        user = User()
        user.username = u_name
        user.password = password

        u_n = f"'{user.username}'"
        p_n = f"'{user.password}'"
        con = sqlite3.connect("tasks.db")
        cur = con.cursor()
        cur.execute(f"INSERT into users VALUES ({u_n},{p_n},'False')")
        con.commit()
        cur.close()
        return user

    else:
        raise HTTPException(status_code=422, detail="Invalid User Name")

@app.get("/users/all", response_model=list[User])
def all_users() -> User:
    con = sqlite3.connect("tasks.db")
    cur = con.cursor()
    store = cur.execute("SELECT * from users").fetchall()

    temp = []

    for i in store:
        user = User()
        user.username = i[0]
        user.password = i[1]
        user.status = i[2]

        temp.append(user)

    return temp

@app.get("/users/delete/{u_name}", response_model=User)
def delte_user(u_name:str) -> User:
    con = sqlite3.connect("tasks.db")
    cur = con.cursor()
    store = cur.execute(f"SELECT * from users WHERE username='{u_name}'").fetchall()
    

    if store != []:
        cur.execute(f"DELETE FROM users WHERE username='{u_name}'")
        con.commit()
        cur.close()
        user = User()
            
        user.username = store[0][0]
        user.password = store[0][1]
        user.status = store[0][2]

        return user
    else:
        raise HTTPException(status_code=404, detail="User Not Found")

@app.get("/users/login/{u_name}", response_model=User)
def login_user(u_name:str, password:str) -> User:
    con = sqlite3.connect("tasks.db")
    cur = con.cursor()
    store = cur.execute("SELECT * from users").fetchall()

    flag = 0

    for i in store:
        if u_name == i[0]:
            flag = 1

            if password!=i[1]:
                flag = 2

    if flag == 1:
        print("SUCCESS")
        cur.execute(f"UPDATE users SET status='True' WHERE username='{u_name}'")
        cur.execute(f"UPDATE users SET status='False' WHERE NOT username='{u_name}'")
        con.commit()
        cur.close()

        user = User()
        user.username = u_name
        user.password = password
        user.status = 'True'

        return user

    elif flag == 2:
        raise HTTPException(status_code=404, detail="Incorrect Password")
    if flag == 0:
        raise HTTPException(status_code=404, detail="User Not Found")
    

