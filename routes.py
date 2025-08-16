from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Question, Interview, Answer
from forms import RegistrationForm, LoginForm, RoleSelectionForm, AnswerForm
from utils import calculate_feedback, get_performance_insights
from datetime import datetime
import random

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    form = RoleSelectionForm()
    recent_interviews = Interview.query.filter_by(
        user_id=current_user.id, 
        completed=True
    ).order_by(Interview.completed_at.desc()).limit(5).all()
    
    # Calculate user statistics
    total_interviews = Interview.query.filter_by(user_id=current_user.id, completed=True).count()
    avg_score = 0
    if total_interviews > 0:
        scores = [interview.total_score for interview in Interview.query.filter_by(user_id=current_user.id, completed=True).all()]
        avg_score = round(sum(scores) / len(scores), 2)
    
    return render_template('dashboard.html', 
                         form=form, 
                         recent_interviews=recent_interviews,
                         total_interviews=total_interviews,
                         avg_score=avg_score)

@app.route('/start_interview', methods=['POST'])
@login_required
def start_interview():
    form = RoleSelectionForm()
    if form.validate_on_submit():
        role = form.role.data
        
        # Get random questions for the selected role
        questions = Question.query.filter_by(role=role).all()
        if len(questions) < 5:
            flash(f'Not enough questions available for {role}. Please contact administrator.', 'error')
            return redirect(url_for('dashboard'))
        
        selected_questions = random.sample(questions, min(5, len(questions)))
        
        # Create new interview
        interview = Interview(user_id=current_user.id, role=role)
        db.session.add(interview)
        db.session.commit()
        
        # Store interview and questions in session
        session['current_interview_id'] = interview.id
        session['interview_questions'] = [q.id for q in selected_questions]
        session['current_question_index'] = 0
        
        return redirect(url_for('interview'))
    
    flash('Please select a valid role.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/interview', methods=['GET', 'POST'])
@login_required
def interview():
    # Check if there's an active interview
    if 'current_interview_id' not in session:
        flash('No active interview found. Please start a new interview.', 'error')
        return redirect(url_for('dashboard'))
    
    interview_id = session['current_interview_id']
    interview = Interview.query.get_or_404(interview_id)
    
    # Verify interview belongs to current user
    if interview.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard'))
    
    question_ids = session['interview_questions']
    current_index = session['current_question_index']
    
    # Check if interview is complete
    if current_index >= len(question_ids):
        return redirect(url_for('complete_interview'))
    
    current_question = Question.query.get(question_ids[current_index])
    form = AnswerForm()
    
    if request.method == 'POST':
        # Check if this is a skip action
        is_skip = request.form.get('skip_question') == 'true'
        
        if is_skip or form.validate_on_submit():
            # Use skip message if skipping, otherwise use user's answer
            user_answer = "Question skipped by user." if is_skip else form.answer.data
            
            # Save the answer
            answer = Answer(
                interview_id=interview_id,
                question_id=current_question.id,
                user_answer=user_answer
            )
            
            # Calculate feedback and score
            feedback_data = calculate_feedback(current_question, user_answer)
            answer.score = feedback_data['score']
            answer.feedback = feedback_data['feedback']
            
            db.session.add(answer)
            db.session.commit()
            
            # Move to next question
            session['current_question_index'] = current_index + 1
            
            # Check if this was the last question
            if session['current_question_index'] >= len(question_ids):
                return redirect(url_for('complete_interview'))
            
            message = 'Question skipped!' if is_skip else 'Answer submitted successfully!'
            flash(message, 'success')
            return redirect(url_for('interview'))
    
    progress_percentage = ((current_index + 1) / len(question_ids)) * 100
    
    return render_template('interview.html', 
                         question=current_question,
                         form=form,
                         question_number=current_index + 1,
                         total_questions=len(question_ids),
                         progress=progress_percentage,
                         interview=interview)

@app.route('/complete_interview')
@login_required
def complete_interview():
    if 'current_interview_id' not in session:
        flash('No active interview found.', 'error')
        return redirect(url_for('dashboard'))
    
    interview_id = session['current_interview_id']
    interview = Interview.query.get_or_404(interview_id)
    
    # Mark interview as completed
    interview.completed = True
    interview.completed_at = datetime.utcnow()
    interview.total_score = interview.calculate_total_score()
    
    db.session.commit()
    
    # Clear session data
    session.pop('current_interview_id', None)
    session.pop('interview_questions', None)
    session.pop('current_question_index', None)
    
    return redirect(url_for('results', interview_id=interview.id))

@app.route('/results/<int:interview_id>')
@login_required
def results(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Verify interview belongs to current user
    if interview.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard'))
    
    if not interview.completed:
        flash('Interview not completed yet.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get performance insights
    insights = get_performance_insights(interview)
    
    return render_template('results.html', 
                         interview=interview, 
                         insights=insights)

@app.route('/interview_history')
@login_required
def interview_history():
    interviews = Interview.query.filter_by(
        user_id=current_user.id, 
        completed=True
    ).order_by(Interview.completed_at.desc()).all()
    
    return render_template('interview_history.html', interviews=interviews)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
