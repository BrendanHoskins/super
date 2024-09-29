from flask import Blueprint

slack_bp = Blueprint('slack', __name__)

from . import slack_oauth_routes
from . import slack_usage_routes
from . import slack_events_routes