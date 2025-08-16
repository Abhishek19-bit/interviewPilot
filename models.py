from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    interviews = db.relationship('Interview', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    model_answer = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, nullable=False)  # Comma-separated keywords
    difficulty_level = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_keywords_list(self):
        return [keyword.strip().lower() for keyword in self.keywords.split(',') if keyword.strip()]
    
    def __repr__(self):
        return f'<Question {self.id}: {self.role}>'

class Interview(db.Model):
    __tablename__ = 'interviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    total_score = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    answers = db.relationship('Answer', backref='interview', lazy=True, cascade='all, delete-orphan')
    
    def calculate_total_score(self):
        if not self.answers:
            return 0.0
        total = sum(answer.score for answer in self.answers)
        return round(total / len(self.answers), 2)
    
    def __repr__(self):
        return f'<Interview {self.id}: {self.role}>'

class Answer(db.Model):
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_answer = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, default=0.0)
    feedback = db.Column(db.Text)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('Question', backref='answers', lazy=True)
    
    def __repr__(self):
        return f'<Answer {self.id}: Score {self.score}>'
