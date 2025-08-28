from celery import Celery

app = Celery("tasks", broker="redis://localhost", backend="redis://localhost")


@app.task
def add(message: str):
    print(f"Your message is - {message}")
    return message


@app.task
def create_browser():
    return "."
