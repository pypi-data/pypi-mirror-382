import os

import sqlalchemy
from dotenv import load_dotenv

load_dotenv()

name = os.getenv("NAME")


def greet_world():
    return f"Hola mundo: {name=}"


def greet_juan():
    return "Hola mundo: juan"


def greet_nelson():
    return "Hola mundo: nelson"


def view_version_sqlalchemy():
    print(sqlalchemy.__version__)
