from flask import Flask   # Import the Flask class from the flask module

# Create an instance of Flask called app which will be the central object
app = Flask(__name__)

print('hello world')

@app.route('/')
def index():
    return 'hello'