from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

class Task(BaseModel):
    title: str
    description: str

def get_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="fastapi"
    )

@app.post("/tasks/", response_model=Task)
async def create_task(task: Task):
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "INSERT INTO task (title, description) VALUES (%s, %s)"
    cursor.execute(query, (task.title, task.description))
    connection.commit()
    task.id = cursor.lastrowid
    cursor.close()
    connection.close()
    return task

@app.get("/tasks/", response_model=list[Task])
async def read_tasks():
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM task"
    cursor.execute(query)
    tasks = cursor.fetchall()
    cursor.close()
    connection.close()
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
async def read_task(task_id: int):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM task WHERE id = %s"
    cursor.execute(query, (task_id,))
    task = cursor.fetchone()
    cursor.close()
    connection.close()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task):
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "UPDATE task SET title = %s, description = %s WHERE id = %s"
    cursor.execute(query, (task.title, task.description, task_id))
    connection.commit()
    cursor.close()
    connection.close()
    return task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "DELETE FROM task WHERE id = %s"
    cursor.execute(query, (task_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "Task deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)