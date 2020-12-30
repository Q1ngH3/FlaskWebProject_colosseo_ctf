from flask import Blueprint
home_page = Blueprint('home_page',__name__)
from . import views