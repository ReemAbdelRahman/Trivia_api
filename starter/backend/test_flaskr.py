import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql+psycopg2://{}:{}@{}/{}".format('postgres', 'password','localhost:5432', self.database_name)
        #self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #Test 1
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))

    #Test 2
    def test_404_not_found_categories_page(self):
        res = self.client().get('/categories?page=5000', json = {'type': "History"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not Found: There are no available categories") 

    #Test 3
    #This test should fail because it's expecting a status code of 404    
    def test_failing_404_not_found_categories_page(self):
        res = self.client().get('/categories?page=5000', json = {'type': "History"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not Found: There are no available categories")  

    #Test 4
    def test_update_category_type(self):
        res = self.client().patch('/categories/2', json = {'type': "History"})
        data =json.loads(res.data)
        category_id = 2
        category = Category.query.get(category_id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(category.format()['type'], "History")
    #Test 5
    def test_400_for_failed_category_update(self):
        res = self.client().patch('/categories/2')
        data =json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Bad request: The specified category could not be updated")

    #Test 6
    # def test_delete_question(self):
    #     no_questions = len(Question.query.all())
    #     res = self.client().delete('questions/10')
    #     data = json.loads(res.data)

    #     question_id = 10
    #     question = Question.query.get(question_id)

    #     # assertion: the number of questions has decreased by one    
    #     self.assertEqual(len(Question.query.all()), no_questions-1)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertEqual(data['deleted'], 2)
    #     self.assertEqual(question, None)

    #Test 7
    def test_404_if_delete_question_that_does_not_exist(self):
        res = self.client().delete('/questions/500')
        print(f"hello: {res}")
        data =json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Unprocessable Entity: The specified question could not be deleted")


    def test_create_question(self):
        new_question = Question (
                        question = "Testing creation of questions",
                        answer = "Let's see",
                        category = "Entertainment",
                        difficulty = 1 )

        no_questions = len(Question.query.all())  

        res = self.client().post('/questions', json = new_question.format())
        data =json.loads(res.data)    

        #assertion: the number of questions has been incremented by one    
        self.assertEqual(len(Question.query.all()), no_questions+1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])


    def test_405_if_question_creation_endpoint_is_not_allowed(self):
        new_question = Question (
                        question = "Testing creation of questions",
                        answer = "Let's see",
                        category = "Entertainment",
                        difficulty = 1 )


        res = self.client().post('/questions/1000', json = new_question.format())
        data =json.loads(res.data)    

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Method Not Allowed: The method is not allowed for the requested URL")

    def test_search_for_questions(self):
        res = self.client().post('/questions', json = {"search_term":"Which"})
        data =json.loads(res.data)    

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['related_questions']))


    def test_404_for_search_for_questions(self):
        res = self.client().post('/questions', json = {"search_term":"Reem"})
        data =json.loads(res.data)    

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not Found: No questions with the searched criteria were found")    


    



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()