from flask import Blueprint, jsonify

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return jsonify({"message": "Welcome to Flask API amiin ku soo dhawaaw flask guuleeso"})

@bp.route('/health')
def health_check():
    return jsonify({"status": "healthy"}) 