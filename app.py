from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class Task(BaseModel):
    title: str = None
    is_done : bool = False

@app.get("/")
def root():
    con = sqlite3.connect("tasks.db")
    cur = con.cursor()

    try:   
        cur.execute("CREATE TABLE tasks(title, status)")
    except:
        pass
    
    cur.close()
    return{"OBJECTIVE":"CREATE A TO-DO APPLICATION"}
    

# STORE A NEW TASK INTO DB
@app.post("/items", response_model=Task)
def create_item(task: Task):

    con = sqlite3.connect("tasks.db")
    cur = con.cursor()

    task_name = f"'{task.title}'"
    task_status = f"'{task.is_done}'"

    cur.execute(f"INSERT into tasks VALUES ({task_name},{task_status})")
    con.commit()
    cur.close()

    return task

# VIEW ALL TASKS IN THE DB
@app.get("/itemsall", response_model=list[Task])
def all_item() -> Task:
    con = sqlite3.connect("tasks.db")
    cur = con.cursor()
    store = cur.execute("SELECT * from tasks").fetchall()
    temp = []

    for i in store:
        task = Task()
        task.title = i[0]
        task.is_done = i[1]
        temp.append(task)

    return temp

# VIEW SPECIFIC TASK IN DB USING TASKID
@app.get("/items/{task_id}", response_model=Task)
def get_item(item_id: int) -> Task:

    con = sqlite3.connect("tasks.db")
    cur = con.cursor()

    store = cur.execute("SELECT * from tasks").fetchall()
    cur.close()

    if item_id < len(store):
        task = Task()
        
        task.title = store[0][0]
        task.is_done = store[0][1]
        return task

    else:
        raise HTTPException(status_code=404, detail="task Not Found")
