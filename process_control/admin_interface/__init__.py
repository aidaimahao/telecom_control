from flask import Blueprint
from flask_restplus import Api


admin_interface = Blueprint('admin_interface', __name__, template_folder='../../templates')
# api = Api(admin_interface)
import process_control.admin_interface.views
