from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

db = SQLAlchemy(app)
api = Api(app)


#################################

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    todos = db.relationship('Todo', backref='owner', lazy=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def json(self):
        todos = [todo.json() for todo in self.todos]
        return {'id': self.id, 'name': self.name, 'email': self.email, 'todos': todos}


class Todo(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, title, description, user_id):
        self.title = title
        self.description = description
        self.user_id = user_id

    def json(self):
        return {'id': self.id, 'title': self.title, 'description': self.description}


#################################


class AddUser(Resource):

    def post(self, name, email):
        user = User(name, email)
        db.session.add(user)
        db.session.commit()

        return {'note': 'added user'}


class SingleUser(Resource):

    def get(self, name):
        user = User.query.filter_by(name=name).first()

        if user:
            return user.json()
        else:
            return {'user': None}, 404


class AllUsers(Resource):

    def get(self):
        users = User.query.all()
        return [user.json() for user in users]


class AddTodo(Resource):

    def post(self, title, description, user_id):
        todo = Todo(title, description, user_id)
        db.session.add(todo)
        db.session.commit()

        return {'note': 'added task'}


class AllTodos(Resource):

    def get(self, user_id):
        todos = Todo.query.filter_by(user_id=user_id).all()
        return [todo.json() for todo in todos]


api.add_resource(AddUser, '/users/add/<string:name>/<string:email>')
api.add_resource(SingleUser, '/users/<string:name>')
api.add_resource(AllUsers, '/users')
api.add_resource(AddTodo, '/todos/add/<string:title>/<string:description>/<int:user_id>')
api.add_resource(AllTodos, '/todos/<int:user_id>')

if __name__ == '__main__':
    app.run()
