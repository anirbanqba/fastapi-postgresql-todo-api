from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
class Todo(BaseModel):
    title: str
    description: str
    completed: bool
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()
todos = [
    {
        "id": 1,
        "title": "Learn Python",
        "completed": False
    },
    {
        "id": 2,
        "title": "Learn GIT",
        "completed": False
    },
    {
        "id": 3,
        "title": "Learn docker",
        "completed": False
    }
]
@app.get("/todos")
def get_todos():
    cursor.execute("SELECT * FROM todos;")
    rows = cursor.fetchall()

    todos_list = []

    for row in rows:
        todo = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "completed": row[3]
        }

        todos_list.append(todo)

    return todos_list

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    cursor.execute(
        "SELECT * FROM todos WHERE id = %s;",
        (todo_id,)
    )

    row = cursor.fetchone()

    if row:
        return {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "completed": row[3]
        }

    raise HTTPException(status_code=404, detail="Todo not found")
@app.post("/todos")
def create_todo(todo: Todo):
    cursor.execute(
        "INSERT INTO todos (title, description, completed) VALUES (%s, %s, %s) RETURNING id;",
        (todo.title, todo.description, todo.completed)
    )

    new_id = cursor.fetchone()[0]
    conn.commit()

    return {
    "id": new_id,
    "title": todo.title,
    "description": todo.description,
    "completed": todo.completed
}

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: Todo):
    cursor.execute(
        """
        UPDATE todos
        SET title = %s,
            description = %s,
            completed = %s
        WHERE id = %s
        RETURNING id, title, description, completed;
        """,
        (
    updated_todo.title,
    updated_todo.description,
    updated_todo.completed,
    todo_id
        )
    )

    row = cursor.fetchone()
    conn.commit()

    if row:
        return {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "completed": row[3]
        }

    raise HTTPException(status_code=404, detail="Todo not found")
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    cursor.execute(
        "DELETE FROM todos WHERE id = %s RETURNING id;",
        (todo_id,)
    )

    deleted_row = cursor.fetchone()
    conn.commit()

    if deleted_row:
        return {"message": "Todo deleted successfully"}

    raise HTTPException(status_code=404, detail="Todo not found")
