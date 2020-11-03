import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  # setup CORS
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


 # ENDPOINTS

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response


  @app.route('/categories', methods=['GET'])
  def get_all_categories():
    categories = Category.query.all()
    formatted_categories = {category.id: category.type for category in categories}

    return jsonify({
      'success': True,
      'categories': formatted_categories,
      'total_categories': len(categories),
      'current_category': None
    })

  @app.route('/questions', methods=['GET'])
  def get_all_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = Question.query.all()
    categories = Category.query.all()

    if page > (len(questions) / QUESTIONS_PER_PAGE):
      abort(404)

    if questions is None:
      abort(404)

    formatted_questions = [question.format() for question in questions]
    formatted_categories = {category.id: category.type for category in categories}

    return jsonify({
      'success': True,
      'questions': formatted_questions[start:end],
      'total_questions': len(questions),
      'categories': formatted_categories,
      'current_category': None
    })


  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    
    question = Question.query.filter(Question.id == question_id).one_or_none()

    if question is None:
      abort(404)

    Question.delete(question)

    return jsonify({
      'success': True,
      'question_id': question_id
    })


  @app.route('/questions', methods=['POST'])
  def create_question():

    body = request.get_json()

    new_question = body.get('question')
    new_answer = body.get('answer')
    new_category = body.get('category')
    new_difficulty = body.get('difficulty')

    if new_question == None:
      abort(400)

    try:
      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)

      question.insert()

      selection = Question.query.order_by('id').all()
          
      return jsonify({
              'success': True,
              'total_questions': len(selection)
          })

    except:
      abort(422)


  @app.route('/questions/search', methods=['POST'])
  def search_question():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10
    body = request.get_json()
    search_term = body.get('searchTerm')

    try:
      searched_questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    
      if searched_questions is None:
        abort(404)

      formatted_questions = [question.format() for question in searched_questions]
 
      return jsonify({
        'success': True,
        'questions': formatted_questions[start:end],
        'total_questions': len(searched_questions),
      })

    except:
      abort(422)


  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_question_category(category_id):

    if category_id > 6:
      abort(404)

    try:
      searched_questions = Question.query.filter(Question.category == category_id).all()
    
      if category_id is None:
        abort(404)

      formatted_questions = [question.format() for question in searched_questions]
 
      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'total_questions': len(searched_questions),
      })

    except:
      abort(422)


  @app.route('/quizzes', methods=['POST'])
  def play_quiz():

    try:
      header = request.get_json()
      previous_questions = header.get('previous_questions')
      quiz_category = header.get('quiz_category')

      if quiz_category['id'] == 0:
        questions = Question.query.all()

      else:
        questions = Question.query.filter(quiz_category['id'] == Question.category).all()

      print(len(questions))

      selected_questions = []

      for question in questions:
        if question.id not in previous_questions:
          selected_questions.append(question)

      print(len(selected_questions))

      if len(selected_questions) < 1:
        return jsonify({
          'success': True,
          'question': None
        })

      else:
        question = random.choice(selected_questions)
        return jsonify({
          'success': True,
          'question': question.format(),
        })

    except:
      abort(422)


  @app.errorhandler(400)
  def invalid_data(error):
    return jsonify({
      'success': False, 
      'error': 400,
      'message': "Invalid Data"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False, 
      'error': 404,
      'message': "Not Found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False, 
      'error': 422,
      'message': "Unprocessable Entity"
    }), 422

  return app

    