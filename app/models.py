import secrets
from . import db 
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash



class Golfer(db.Model):
    golfer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False) #pw_hash ?!?!
    golfer_age = db.Column(db.Integer, nullable=False)
    handicap = db.Column(db.Float, nullable=True)
    right_handed = db.Column(db.Boolean, nullable=True)
    alcohol = db.Column(db.Boolean, nullable=True)
    legal_drugs = db.Column(db.Boolean, nullable=True)
    smoker = db.Column(db.Boolean, nullable=True)
    gambler = db.Column(db.Boolean, nullable=True)
    tees = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=False)
    district = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=True)
    music = db.Column(db.Boolean, nullable=True)
    token = db.Column(db.String, nullable=True)
    tokenExp = db.Column(db.DateTime(timezone=True), nullable=True)
    teetimes = db.relationship('Teetime', back_populates="golfer")
    golfer_comments = db.relationship("Golfer_comment", back_populates="golfer")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password(kwargs.get('password', '')) #find the password in args

    def __repr__(self):
        return f"<Golfer {self.golfer_id}|{self.username}>"
    
    def set_password(self, plaintext_password):
        self.password = generate_password_hash(plaintext_password)
        self.save()
    
    def save(self): #to add to the database automatically like done in the terminal
        db.session.add(self)
        db.session.commit()

    def check_password(self, plaintext_password):
        return check_password_hash(self.password, plaintext_password)
    
    #turn the User into a dict type
    def to_dict(self):
        return {
            "golfer_id": self.golfer_id,
            # changed above to golfer ID ================================================================================================================================
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "email": self.email,
            "handicap": self.handicap,
            "golfer_age": self.golfer_age,
            "phone":self.phone,
            "city": self.city,
            "district": self.district,
            "country": self.country,
            "right_handed": self.right_handed,
            "alcohol": self.alcohol,
            "legal_drugs": self.legal_drugs,
            "smoker": self.smoker,
            "gambler": self.gambler,
            "music": self.music,
            "tees": self.tees
        }
    
    def update(self, **kwargs):
        allowed_fields = {'first_name', 'last_name', 'city', 'district', 'country', 'email', 'phone', 'handicap', 'golfer_age', 'right_handed', 'alcohol', 'legal_drugs', 'smoker', 'gambler', 'tees', 'music'}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.save()
    
    def get_token(self):
        now = datetime.now(timezone.utc)
        if self.token and self.tokenExp > now + timedelta(minutes=1):
            return {"token": self.token, "tokenExp": self.tokenExp}
        self.token = secrets.token_hex(16)
        self.tokenExp = now + timedelta(hours=1)
        self.save()
        return {"token": self.token, "tokenExp": self.tokenExp}
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    

class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    district = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    weekday_price = db.Column(db.Integer, nullable=True)
    weekend_price = db.Column(db.Integer, nullable=True)
    strict_dress = db.Column(db.Boolean, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    slope = db.Column(db.Float, nullable=True)
    course_length = db.Column(db.Integer, nullable=True)
    par = db.Column(db.Integer, nullable=False)
    designer = db.Column(db.String, nullable=True)
    teetimes = db.relationship("Teetime", back_populates="course")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Course {self.course_id}|{self.course_name}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "course_id": self.course_id,
            # changed to course_id ================================================================================================================================
            "course_name": self.course_name,
            "address": self.address,
            "city": self.city,
            "district": self.district,
            "country": self.country,
            "weekday_price": self.weekday_price,
            "weekend_price": self.weekend_price,
            "strict_dress":self.strict_dress,
            "rating": self.rating,
            "slope":self.slope,
            "couse_length": self.course_length,
            "par": self.par,
            "designer": self.designer
        }
    
    def update(self, **kwargs):
        allowed_fields = {"course_name", "weekday_price", "weekend_price", "strict_dress", "rating", "slope", "course_length", "par"}
        for key, value in kwargs.items():
            if key in allowed_fields:  
                setattr(self, key, value) 
        self.save() 

    def delete(self):
        db.session.delete(self) 
        db.session.commit()



class Teetime(db.Model):
    teetime_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    teetime_date = db.Column(db.String, nullable=False)
    teetime_time = db.Column(db.String, nullable=False)
    space_remaining = db.Column(db.Integer, nullable=False)
    golfer_id = db.Column(db.Integer, db.ForeignKey('golfer.golfer_id'), nullable=False)
    # made nullable true below ================================================================================================================================
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=True)
    golfer = db.relationship("Golfer", back_populates='teetimes')
    golfer_comments = db.relationship("Golfer_comment", back_populates='teetime')
    course = db.relationship("Course", back_populates="teetimes")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Teetime {self.teetime_id}|{self.course_name}|{self.price}|{self.teetime_date}|{self.teetime_time}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "teetime_id": self.teetime_id,
            # changed to teetime_ID above ================================================================================================================================
            'course_name': self.course_name,
            "course_details": self.course.to_dict(),
            "price": self.price,
            "teetime_date": self.teetime_date,
            "teetime_time": self.teetime_time,
            "space_remaining": self.space_remaining,
            # "course_id":self.course_id,
            # added course ID above ================================================================================================================================
            "golfer": self.golfer.to_dict(),
            "golfer_comments": [golfer_comment.to_dict() for golfer_comment in self.golfer_comments]
        }



    def update(self, **kwargs):
        allowed_fields = {"price", "teetime_date", "teetime_time", "space_remaining"}

        for key, value in kwargs.items():
            if key in allowed_fields:  
                setattr(self, key, value) 
        self.save()

    def delete(self):
        db.session.delete(self) # deleting THIS object from the database
        db.session.commit() # commiting our changes




class Golfer_comment(db.Model):
    golfer_comment_id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    golfer_id = db.Column(db.Integer, db.ForeignKey('golfer.golfer_id'), nullable=False)
    teetime_id = db.Column(db.Integer, db.ForeignKey('teetime.teetime_id'), nullable=False)
    teetime = db.relationship('Teetime', back_populates="golfer_comments")
    golfer = db.relationship('Golfer', back_populates='golfer_comments')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Comment {self.golfer_comment_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.golfer_comment_id,
            'body': self.body,
            'teetime_id': self.teetime_id,
            'golfer': self.golfer.to_dict()
        }


    

	
