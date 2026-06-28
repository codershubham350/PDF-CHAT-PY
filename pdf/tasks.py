import os
import shlex
import sys
from invoke import task


@task
def dev(ctx):
    ctx.run(
        "flask --app app.web run --debug --port 8000",
        pty=os.name != "nt",
        env={"APP_ENV": "development"},
    )


# @task
# def devworker(ctx):
#     ctx.run(
#         "watchmedo auto-restart --directory=./app --pattern=*.py --recursive -- celery -A app.celery.worker worker --concurrency=1 --loglevel=INFO --pool=solo",
#         pty=os.name != "nt",
#         env={"APP_ENV": "development"},
#     )

# @task
# def devworker(ctx):
#     ctx.run(
#         r'watchmedo auto-restart --directory=./app --pattern=*.py --recursive -- "C:\Users\DELL\.virtualenvs\pdf-KEI2IIix\Scripts\python.exe" -m celery -A app.celery.worker worker --concurrency=1 --loglevel=INFO --pool=solo',
#         pty=os.name != "nt",
#         env={"APP_ENV": "development"},
#     )

@task
def devworker(ctx):
    python = f'"{sys.executable}"'

    cmd = (
        f"{python} "
        "-m celery "
        "-A app.celery.worker "
        "worker "
        "--concurrency=1 "
        "--loglevel=INFO "
        "--pool=solo"
    )

    # print("Python:", sys.executable)

    ctx.run(
        f"watchmedo auto-restart --directory=./app --pattern=*.py --recursive -- {cmd}",
        pty=os.name != "nt",
        env={"APP_ENV": "development"},
    )