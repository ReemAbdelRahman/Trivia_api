import os
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization, true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  #the following function will be called for questions and categories when pagination is needed  
  def paginate_collection(request, collection):
    page = request.args.get('page', 1, type = int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_collection = []
    for c in collection:
      formatted_collection.append(c.format())

    curr_collection  = formatted_collection[start:end]
    
    return curr_collection         
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    
    current_categories = paginate_collection(request,categories)
    

    if len(current_categories) == 0:
      abort(404 , {'message': 'There are no available categories'})

    return jsonify({
      'categories': current_categories,
      'total_categories': len(categories),
      'success': True
    })


  @app.route('/categories/<int:category_id>')
  def get_category(category_id):
    try:
      category = Category.query.get(category_id)
      if category is None:
        #https://stackoverflow.com/questions/21294889/how-to-get-access-to-error-message-from-abort-command-when-using-custom-error-ha
        abort(404 , {'message': 'There is no category with the specified id'})


      return jsonify({
      'category' : category.format(),
      'success': True
      })

    except Exception as e:
      print(e)
      abort(404 , {'message': 'There is no category with the specified id'})




  @app.route('/categories/<int:category_id>', methods = ['PATCH'])
  def update_category(category_id):
    #https://stackoverflow.com/questions/54472696/failed-to-decode-json-object-expecting-value-line-1-column-1-char-0-p
    body = request.json
    #https://stackoverflow.com/questions/6386308/http-requests-and-json-parsing-in-python
    #resp = request.get(url=url, params=params)
    #data = resp.json() # Check the JSON Response Content documentation below
    print("hello")
    print(body)
    try:
      category = Category.query.get(category_id)
      if category is None:
        abort(404, {'message': 'There is no category with the specified id'})

      if 'type' in body:
        category.type = body.get('type')  

      category.update()

      return jsonify({
        'success': True,
        'id': category.id
      })
    except Exception as e:
      print(e)
      abort(400, {'message': 'The specified category could not be updated'})  


  @app.route('/categories/<int:category_id>', methods = ['DELETE'])
  def delete_category(category_id):
    try:
      category = Category.query.get(category_id)
      if category is None:
        abort(404, {'message': 'There is no category with the specified id'})


      category.delete()

      current_categories = paginate_collection(request, Category.query.order_by(Category.id).all())


      return jsonify({
        'success': True,
        'deleted':category_id,
        'categories': current_categories,
        'total_categories': len(Category.query.all()) 
        })

    except Exception as e:
      print(e)
      abort(422, {'message': 'The specified category could not be deleted'})

       
  

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    
    current_questions = paginate_collection(request,questions)
    

    if len(current_questions) == 0:
      abort(404, {'message': 'There is no question with the specified id'})

    return jsonify({
      'questions': current_questions,
      'total_questions': len(questions),
      'success': True
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods = ['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      if question is None:
        abort(404, {'message': 'There is no question with the specified id'})


      question.delete()

      current_questions = paginate_collection(request, Question.query.order_by(Question.id).all())


      return jsonify({
        'success': True,
        'deleted':question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all()) 
        })

    except Exception as e:
      print(e)
      flash(e)
      abort(422, {'message': 'The specified question could not be deleted'})  

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods = ['POST'])
  def create_question():
    body = request.json

    new_question   = body.get('question', None)
    new_answer     = body.get('answer', None)
    new_category   = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      question = Question(question = new_question,
                          answer   = new_answer,
                          category = new_category,
                          difficulty =  new_difficulty)
      question.insert()

      current_questions = paginate_collection(request,Question.query.order_by(Question.id).all())                    
      return jsonify({
        'success': True,
        'create' : question.id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
        })

    except Exception as e:
      abort(405, {'message': 'The new question could not be posted'})    
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.json
    if 'search_term' in body:
      search_term   = body.get('search_term', None) 
    
    try:
      questions = Question.query.filter(Question.question.like('%' + search_term + '%')).all()
      current_questions = paginate_collection(request,questions.order_by(Question.id))
      return jsonify({
            'success': True,
            'related_questions': current_questions,
            'total_questions': len(Question.query.all())
            })
    
    except Exception as e:
      abort(404, {'message': 'No questions with the searched criteria were found'})           

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions_cat():
    body = request.json
    if 'category' in body:
      category = body.get('category', None)
    try:
      questions = Question.query.filter_by(category = category).all()
      current_questions = paginate_collection(request,questions.order_by(Question.id))
      return jsonify({
            'success': True,
            'related_questions': current_questions,
            'total_questions': len(Question.query.all())
            })
    
    except Exception as e:
      abort(404, {'message': 'No questions with the specified category were found'})   


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  #https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
  # status code messages
  #https://stackoverflow.com/questions/21294889/how-to-get-access-to-error-message-from-abort-command-when-using-custom-error-ha 
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success" : False,
      "error": 404,
      "message": "Not Found: " + error.description['message']
    }), 404


  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success" : False,
      "error": 400,
      "message": "Bad request: " + error.description['message']
    }), 400

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success" : False,
      "error": 422,
      "message": "Unprocessable Entity: " + error.description['message'] 
    }), 422

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success" : False,
      "error": 405,
      "message": "Method Not Allowed" + error.description['message']
    }), 405          
  
  return app

    