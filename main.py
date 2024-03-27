from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
import mysql.connector
from starlette.responses import HTMLResponse

app = FastAPI()

class Task(BaseModel):
    title: str
    description: str

def get_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="fastApi"
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

@app.get("/create_task", response_class=HTMLResponse)
async def create_task_form():
    form_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Create Task</title>
    </head>
    <body>
        <h1>Create Task</h1>
        <form action="/tasks/" method="post">
            <label for="title">Title:</label><br>
            <input type="text" id="title" name="title" required><br>
            <label for="description">Description:</label><br>
            <textarea id="description" name="description"></textarea><br>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=form_html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
