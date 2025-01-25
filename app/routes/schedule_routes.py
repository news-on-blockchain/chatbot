from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError, validate
from config.settings import Config
from app.services.vector_service import VectorService
from app.services.schedule_service import ScheduleService
from werkzeug.exceptions import BadRequest

bp = Blueprint('schedule', __name__)

# Input validation schemas
class StudentSchema(Schema):
    semester = fields.Integer(
        required=True, 
        validate=validate.Range(min=1, max=10),
        error_messages={
            'required': 'Semester is required.',
            'validator_failed': 'Semester must be between 1 and 10.'
        }
    )
    branch = fields.String(
        required=True, 
        validate=validate.Length(min=2, max=50),
        error_messages={
            'required': 'Branch is required.',
            'length': 'Branch must be between 2 and 50 characters.'
        }
    )
    group = fields.String(
        required=True, 
        validate=validate.Length(min=1, max=10),
        error_messages={
            'required': 'Group is required.',
            'length': 'Group must be between 1 and 10 characters.'
        }
    )
    institute_id = fields.Integer(
        required=False, 
        validate=validate.Range(min=1),
        error_messages={
            'validator_failed': 'Invalid institute ID.'
        }
    )

class QuerySchema(Schema):
    query = fields.String(
        required=True, 
        validate=validate.Length(min=1, max=500),
        error_messages={
            'required': 'Query text is required.',
            'length': 'Query must be between 1 and 500 characters.'
        }
    )
    student = fields.Nested(StudentSchema, required=True)

# Initialize services
vector_service = VectorService(Config)
schedule_service = ScheduleService(vector_service)

@bp.route('/train', methods=['POST'])
def train_vector_store():
    """
    Endpoint to train/update vector store
    
    Returns:
        JSON response with training status
    """
    try:
        result = vector_service.train_vector_store()
        return jsonify({
            "status": "success", 
            "message": result
        }), 200
    except Exception as e:
        # Log the full error for debugging
        bp.logger.error(f"Training error: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Vector store training failed",
            "tokens": 500,
            "details": str(e)
        }), 500

@bp.route('/query', methods=['POST'])
def schedule_query():
    """
    Process schedule query with comprehensive error handling
    
    Returns:
        JSON response with query results or error details
    """
    try:
        # Parse and validate incoming JSON
        query_schema = QuerySchema()
        try:
            data = query_schema.load(request.get_json())
        except ValidationError as validation_err:
            # Return detailed validation errors
            return jsonify({
                "status": "error", 
                "message": "Input validation failed",
                "tokens": 500,
                "details": validation_err.messages
            }), 400
        
        # Extract validated data
        query = data['query']
        student_data = data['student']
        
        # Additional custom validations if needed
        if not query.strip():
            return jsonify({
                "status": "error", 
                "message": "Query cannot be empty or whitespace"
            }), 400
        
        # Perform query
        response = schedule_service.process_query(query, student_data)
        
        # Handle empty or meaningless responses
        if not response or response.strip() in ['', 'None', 'N/A']:
            return jsonify({
                "status": "warning", 
                "message": "No relevant information found",
                "tokens": 500,
                "details": "The query did not match any schedules or information"
            }), 404
        
        return jsonify({
            "status": "success", 
            "response": response
        }), 200
    
    except BadRequest as bad_req:
        # Handle bad request errors
        bp.logger.warning(f"Bad request: {str(bad_req)}")
        return jsonify({
            "status": "error", 
            "message": "Invalid request format",
            "tokens": 500,
            "details": str(bad_req)
        }), 400
    
    except ValueError as val_err:
        # Handle value-related errors
        bp.logger.error(f"Value error: {str(val_err)}")
        return jsonify({
            "status": "error", 
            "message": "Invalid input value",
            "tokens": 500,
            "details": str(val_err)
        }), 400
    
    except Exception as e:
        # Catch-all for unexpected errors
        bp.logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error", 
            "message": "An unexpected error occurred",
            "tokens": 500,
            "details": "Please contact support if this persists"
        }), 500

# Add custom error handlers
@bp.errorhandler(400)
def bad_request(error):
    """Custom error handler for bad requests"""
    return jsonify({
        "status": "error", 
        "message": "Bad Request",
        "tokens": 500,
        "details": str(error)
    }), 400

@bp.errorhandler(404)
def not_found(error):
    """Custom error handler for not found errors"""
    return jsonify({
        "status": "error", 
        "message": "Resource Not Found",
        "tokens": 500,
        "details": str(error)
    }), 404

@bp.errorhandler(500)
def internal_error(error):
    """Custom error handler for internal server errors"""
    return jsonify({
        "status": "error", 
        "message": "Internal Server Error",
        "tokens": 500,
        "details": "An unexpected error occurred on the server"
    }), 500