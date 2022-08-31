#!/usr/bin/python3
from flask import Flask

# Initialize the app
app = Flask(__name__, instance_relative_config=True)

# Load the views
from . import views

