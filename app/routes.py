from flask import request, render_template
from . import app, db
from .models import Golfer, Course, Teetime, Golfer_comment
from .auth import basic_auth, token_auth

# define route
@app.route('/')
def index():
    return render_template('index.html')

# golfer endpoints

# create new golfer
@app.route('/golfers', methods=['POST'])
def create_golfer():
    if not request.is_json:
        return {'error': 'You content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json

    # Validate that the data has all of the required fields
    required_fields = ['first_name', 'last_name', 'email', 'username', 'password', 'golfer_age', 'city', 'district', 'country']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    #pull the individual data from the body
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')  #or pw_hash???
    golfer_age = data.get('golfer_age')
    city = data.get('city')
    district = data.get('district')
    country = data.get('country')

    #check to see if any current users already have the username and/or email
    check_golfers = db.session.execute(db.select(Golfer).where( (Golfer.username == username) | (Golfer.email == email) )).scalars().all()
    if check_golfers:
        return {'error': "A golfer with that username and/or email already exists"}, 400
    
    #create a new instance of user with the data rom the request
    new_golfer = Golfer(first_name=first_name, last_name=last_name,  username=username, email=email, password=password, golfer_age=golfer_age, city=city, district=district, country=country)

    return new_golfer.to_dict(), 201


# get token
@app.route('/token')
@basic_auth.login_required
def get_token():
    golfer = basic_auth.current_user()
    return golfer.get_token()

#get golfer
@app.route('/golfers/me')
@token_auth.login_required
def get_me():
    golfer = token_auth.current_user()
    return golfer.to_dict()

# update golfer
@app.route('/golfers/me', methods=['PUT'])
@token_auth.login_required
def update_me():
    golfer = token_auth.current_user()
    data = request.json
    golfer.update(**data)
    return golfer.to_dict()

# delete golfer
@app.route('/golfers/me', methods=['DELETE'])
@token_auth.login_required
def delete_me():
    golfer = token_auth.current_user()
    golfer.delete()
    return {'success': 'Golfer has been successfully deleted'}, 200


# golfer login
@app.route('/login', methods=['GET'])
@basic_auth.login_required
def login():
    golfer = basic_auth.current_user()
    return golfer.get_token()



# teetime enpoints
@app.route('/teetimes')
def get_teetimes():
    select_stmt = db.select(Teetime)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where(Teetime.course_name.ilike(f"%{search}%"))
    # Get the teetimes from the database
    teetimes = db.session.execute(select_stmt).scalars().all()
    return [t.to_dict() for t in teetimes]  #list comprehension calling to_dict and looping thru all teetimes to get them


#get a single teetime by ID
@app.route('/teetimes/<int:teetime_id>')
def get_teetime(teetime_id):
    # Get the teetime from the database by ID
    teetime = db.session.get(Teetime, teetime_id)
    if teetime:
        return teetime.to_dict()
    else:
        return {'error': f"Tee Time with an ID of {teetime_id} does not exist"}, 404
    
#Create a Teetime
@app.route('/teetimes', methods=['POST']) # same url but depending on if you are making a get request or in this case a get request it will vary in what it returns
@token_auth.login_required
def create_teetime():
    #check if the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    #get the data from the request body
    data = request.json
    #validate the incoming data
    required_fields = ['course_name', 'price', 'teetime_date', 'teetime_time', 'space_remaining']
    missing_fields = []
    # For each of the required fields
    for field in required_fields:
        # If the field is not in the request body dictionary
        if field not in data:
            # Add that field to the list of missing fields
            missing_fields.append(field)
    # If there are any missing fields, return 400 status code with the missing fields listed
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Get data values
    course_name = data.get('course_name')
    price = data.get('price')
    teetime_date = data.get('teetime_date')
    teetime_time = data.get('teetime_time')
    space_remaining = data.get('space_remaining')

    current_golfer = token_auth.current_user()

    # Create a new Teetime instance with data (and get the id from the token authenticated user)
    new_teetime = Teetime(course_name=course_name, price=price, teetime_date=teetime_date, teetime_time=teetime_time, space_remaining=space_remaining, golfer_id=current_golfer.golfer_id)
    # last part of above line from .id to .golfer_id ================================================================================================================================

    # Return the newly created teetime dictionary with a 201 Created Status Code
    return new_teetime.to_dict(), 201

#update teetime endpoint
@app.route('/teetimes/<int:teetime_id>', methods=['PUT'])
@token_auth.login_required
def edit_teetime(teetime_id):
    # Check to see that they have a JSON body
    if not request.is_json:
        return {'error': 'You content-type must be application/json'}, 400
    # Let's the find teetime in the db
    teetime = db.session.get(Teetime, teetime_id)
    if teetime is None:
        return {'error': f"Tee Time with ID #{teetime_id} does not exist"}, 404
    # Get the current user based on the token
    current_golfer = token_auth.current_user()
    # Check if the current user is the author of the teetime
    if current_golfer is not teetime.golfer:
        return {'error': "This is not your Tee Time. You do not have permission to edit"}, 403
    
    # Get the data from the request
    data = request.json
    # Pass that data into the teetime's update method
    teetime.update(**data)
    return teetime.to_dict()

@app.route('/teetimes/<int:teetime_id>', methods=['DELETE'])
@token_auth.login_required
def delete_teetime(teetime_id):
    # based on the teetime_id parameter check to see Teetime exists
    teetime = db.session.get(Teetime, teetime_id)

    if teetime is None:
        return {'error': f'Teetime with {teetime_id} does not exist. Please try again'}, 404
    
    #Make sure user trying to delete teetime is the user whom created it
    current_golfer = token_auth.current_user()
    if teetime.golfer is not current_golfer:
        return {'error': 'You do not have permission to delete this Tee Time'}, 403
    
    #delete the teetime
    teetime.delete()
    return {'success': f"Your Tee Time at {teetime.course_name} was successfully deleted"}, 200





# Create a golfer_comment
@app.route('/teetimes/<int:teetime_id>/golfer_comments', methods=['POST'])
@token_auth.login_required
def create_golfer_comment(teetime_id):
    
    #make sure the request has a body
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    #grab the correct teetime
    teetime = db.session.get(Teetime, teetime_id)
    if teetime is None:
        return {'error': f"Teetime with ID {teetime_id} does not exist"}, 404
    
    data = request.json
    
    required_fields = ['body']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
            
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be present in the request body"}, 400
    
    body = data.get('body')
    current_golfer = token_auth.current_user()
    new_golfer_comment = Golfer_comment(body=body, golfer_id=current_golfer.id, teetime_id=teetime.id)
    return new_golfer_comment.to_dict(), 201

# Delete a golfer_comment
@app.route('/teetimes/<int:teetime_id>/golfer_comments/<int:golfer_comment_id>', methods=['DELETE'])
@token_auth.login_required
def delete_comment(teetime_id, golfer_comment_id):
    
    #grab our teetime by id 
    teetime = db.session.get(Teetime, teetime_id)
    
    if teetime is None:
        return {'error': f"Teetime with ID {teetime_id} does not exist"}, 404
    
    golfer_comment = db.session.get(Golfer_comment, golfer_comment_id)
    
    if golfer_comment is None:
        return {'error': f"Comment {golfer_comment_id} does not exist"}, 404
    
    if golfer_comment.teetime_id != teetime.id:
        return {'error' : f"Comment #{golfer_comment_id} is not associated with teetime #{teetime_id}"}, 403
    
    current_golfer = token_auth.current_user()
    
    if golfer_comment.golfer != current_golfer:
        return {'error': 'You do not have permission to delete this comment'}, 403
    
    golfer_comment.delete()
    return {'success': "Comment has been successfully deleted"}, 200 
