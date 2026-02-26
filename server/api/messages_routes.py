import json
import queue

from flask import Blueprint, Response, jsonify, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.dashboard_services import get_user_slack_messages
from services.sse_hub import register as sse_register, unregister as sse_unregister

messages_bp = Blueprint('messages_bp', __name__)

# How often to send a keepalive comment so proxies don't close the stream (seconds)
SSE_KEEPALIVE_INTERVAL = 25


@messages_bp.route('/get-messages', methods=['GET'])
@jwt_required()
def get_messages_data():
    user_id = get_jwt_identity()
    messages = get_user_slack_messages(user_id)
    return jsonify(messages), 200


@messages_bp.route('/stream', methods=['GET'])
@jwt_required(locations=['query_string'])
def messages_stream():
    """Server-Sent Events stream for the current user. New Slack messages are pushed here."""
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    def generate():
        q = sse_register(user_id)
        try:
            while True:
                try:
                    event_type, data = q.get(timeout=SSE_KEEPALIVE_INTERVAL)
                    yield f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"
        finally:
            sse_unregister(user_id, q)

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        },
    )
