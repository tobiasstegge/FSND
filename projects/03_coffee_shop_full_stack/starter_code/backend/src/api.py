import os
from os import error, times
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()

    drinks_short = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinks_short
    })

'''
implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()

    drinks_long = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinks_long
    })

'''
implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):

    body = request.get_json()
    new_title = body.get('title')
    new_recipe = body.get('recipe')

    new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))

    new_drink.insert()
    print('Inserted new drink')

    return jsonify({
        'success': True,
        'drinks': new_drink.long()
    })

'''
implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH', 'OPTIONS'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):

    drink = Drink.query.filter(Drink.id==id).one_or_none()

    if drink is None:
        abort(404)

    body = request.get_json()
    new_title = body.get('title')
    new_recipe = body.get('recipe')

    drink.title = new_title 
    drink.recipe = json.dumps(new_recipe)
    drink.update()

    print('Updated drink')

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })

'''
implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):

    drink = Drink.query.filter(Drink.id==id).one_or_none()

    if drink is None:
        abort(404)

    drink.delete()

    print('Deleted drink')

    return jsonify({
        'success': True,
        'delete': id
    })



## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
Example error handling for ressource not found 
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404


'''
    error handler for AuthError
'''

@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify({
        "success": False,
        "error": e.status_code,
        "message": str(e.error) + " (authentification fails)"
                    }), 401

