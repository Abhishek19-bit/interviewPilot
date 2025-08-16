from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=4, max=20, message='Username must be between 4 and 20 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RoleSelectionForm(FlaskForm):
    role = SelectField('Select Role', choices=[
        ('python_developer', 'Python Developer'),
        ('data_engineer', 'Data Engineer'),
        ('web_developer', 'Web Developer'),
        ('data_scientist', 'Data Scientist'),
        ('devops_engineer', 'DevOps Engineer'),
        ('software_engineer', 'Software Engineer')
    ], validators=[DataRequired()])
    submit = SubmitField('Start Interview')

class AnswerForm(FlaskForm):
    answer = TextAreaField('Your Answer', validators=[
        DataRequired(), 
        Length(min=10, message='Answer must be at least 10 characters')
    ], render_kw={"rows": 8, "placeholder": "Type your answer here..."})
    submit = SubmitField('Submit Answer')
