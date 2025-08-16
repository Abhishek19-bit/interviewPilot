from app import db
from models import Question
import re

def calculate_feedback(question, user_answer):
    """Calculate feedback and score based on keyword matching and answer quality."""
    if not user_answer or not user_answer.strip():
        return {
            'score': 0,
            'feedback': 'No answer provided. ❌'
        }
    
    keywords = question.get_keywords_list()
    user_answer_lower = user_answer.lower()
    
    # Count matched keywords
    matched_keywords = []
    for keyword in keywords:
        if keyword in user_answer_lower:
            matched_keywords.append(keyword)
    
    # Calculate keyword score
    keyword_score = (len(matched_keywords) / len(keywords)) * 100 if keywords else 0
    
    # Consider answer length (bonus points for detailed answers)
    word_count = len(user_answer.split())
    length_bonus = min(10, word_count / 10)  # Up to 10 bonus points
    
    # Final score
    final_score = min(100, keyword_score + length_bonus)
    
    # Generate feedback
    missing_keywords = [kw for kw in keywords if kw not in matched_keywords]
    
    if final_score >= 70:
        feedback = "Strong answer! ✅ You covered the key concepts well."
        if matched_keywords:
            feedback += f" Keywords covered: {', '.join(matched_keywords)}."
    elif final_score >= 40:
        feedback = f"Decent answer, but could be improved. "
        if missing_keywords:
            feedback += f"Consider mentioning: {', '.join(missing_keywords[:3])}."
    else:
        feedback = "Weak answer. ❌ This concept needs more attention. "
        if missing_keywords:
            feedback += f"Important topics to study: {', '.join(missing_keywords[:5])}."
    
    return {
        'score': round(final_score, 2),
        'feedback': feedback
    }

def get_performance_insights(interview):
    """Generate performance insights for an interview."""
    answers = interview.answers
    if not answers:
        return {}
    
    total_score = interview.total_score
    high_scores = [a for a in answers if a.score >= 70]
    low_scores = [a for a in answers if a.score < 40]
    
    # Determine performance level
    if total_score >= 80:
        performance_level = "Excellent"
        performance_color = "success"
    elif total_score >= 60:
        performance_level = "Good"
        performance_color = "info"
    elif total_score >= 40:
        performance_level = "Fair"
        performance_color = "warning"
    else:
        performance_level = "Needs Improvement"
        performance_color = "danger"
    
    # Generate strengths and weaknesses
    strengths = []
    weaknesses = []
    
    if high_scores:
        strengths.append(f"Strong performance on {len(high_scores)} out of {len(answers)} questions")
    if total_score >= 60:
        strengths.append("Good overall understanding of concepts")
    
    if low_scores:
        weaknesses.append(f"Struggled with {len(low_scores)} questions")
    if total_score < 60:
        weaknesses.append("Need to strengthen fundamental concepts")
    
    # Suggested resources based on role
    resources = get_suggested_resources(interview.role)
    
    return {
        'performance_level': performance_level,
        'performance_color': performance_color,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'suggested_resources': resources,
        'high_performing_questions': len(high_scores),
        'low_performing_questions': len(low_scores)
    }

def get_suggested_resources(role):
    """Get suggested learning resources based on role."""
    resources = {
        'python_developer': [
            {'name': 'Python.org Official Tutorial', 'url': 'https://docs.python.org/3/tutorial/'},
            {'name': 'Real Python', 'url': 'https://realpython.com/'},
            {'name': 'Python Tricks by Dan Bader', 'url': 'https://realpython.com/products/python-tricks-book/'},
            {'name': 'GeeksforGeeks Python', 'url': 'https://www.geeksforgeeks.org/python-programming-language/'}
        ],
        'data_engineer': [
            {'name': 'Apache Airflow Documentation', 'url': 'https://airflow.apache.org/docs/'},
            {'name': 'Kafka Documentation', 'url': 'https://kafka.apache.org/documentation/'},
            {'name': 'AWS Data Engineering', 'url': 'https://aws.amazon.com/big-data/'},
            {'name': 'DataCamp Data Engineering Track', 'url': 'https://www.datacamp.com/tracks/data-engineer-with-python'}
        ],
        'web_developer': [
            {'name': 'MDN Web Docs', 'url': 'https://developer.mozilla.org/'},
            {'name': 'W3Schools', 'url': 'https://www.w3schools.com/'},
            {'name': 'freeCodeCamp', 'url': 'https://www.freecodecamp.org/'},
            {'name': 'JavaScript.info', 'url': 'https://javascript.info/'}
        ],
        'data_scientist': [
            {'name': 'Kaggle Learn', 'url': 'https://www.kaggle.com/learn'},
            {'name': 'Coursera Data Science', 'url': 'https://www.coursera.org/browse/data-science'},
            {'name': 'Towards Data Science', 'url': 'https://towardsdatascience.com/'},
            {'name': 'Scikit-learn Documentation', 'url': 'https://scikit-learn.org/stable/'}
        ],
        'devops_engineer': [
            {'name': 'Docker Documentation', 'url': 'https://docs.docker.com/'},
            {'name': 'Kubernetes Documentation', 'url': 'https://kubernetes.io/docs/'},
            {'name': 'AWS DevOps', 'url': 'https://aws.amazon.com/devops/'},
            {'name': 'Terraform Documentation', 'url': 'https://www.terraform.io/docs/'}
        ],
        'software_engineer': [
            {'name': 'LeetCode', 'url': 'https://leetcode.com/'},
            {'name': 'System Design Primer', 'url': 'https://github.com/donnemartin/system-design-primer'},
            {'name': 'Clean Code by Robert Martin', 'url': 'https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882'},
            {'name': 'GeeksforGeeks', 'url': 'https://www.geeksforgeeks.org/'}
        ]
    }
    
    return resources.get(role, [
        {'name': 'GeeksforGeeks', 'url': 'https://www.geeksforgeeks.org/'},
        {'name': 'Stack Overflow', 'url': 'https://stackoverflow.com/'},
        {'name': 'GitHub', 'url': 'https://github.com/'},
        {'name': 'Medium Tech Articles', 'url': 'https://medium.com/topic/technology'}
    ])

def seed_questions():
    """Seed the database with initial questions if it's empty."""
    if Question.query.count() > 0:
        return  # Questions already exist
    
    sample_questions = [
        # Python Developer Questions
        {
            'role': 'python_developer',
            'question_text': 'Explain the difference between a list and a tuple in Python. When would you use each?',
            'model_answer': 'Lists are mutable, ordered collections that can be modified after creation. Tuples are immutable, ordered collections that cannot be changed. Use lists when you need to modify the collection, and tuples for data that should remain constant.',
            'keywords': 'mutable, immutable, ordered, list, tuple, modify, constant, collection'
        },
        {
            'role': 'python_developer',
            'question_text': 'What is a decorator in Python and how do you create one?',
            'model_answer': 'A decorator is a function that takes another function as an argument and extends its behavior without modifying it. Created using @decorator_name syntax or by wrapping functions.',
            'keywords': 'decorator, function, wrapper, @, syntax, behavior, extends, modify'
        },
        {
            'role': 'python_developer',
            'question_text': 'Explain the concept of list comprehension with an example.',
            'model_answer': 'List comprehension provides a concise way to create lists. Example: [x**2 for x in range(10) if x%2==0] creates a list of squares of even numbers.',
            'keywords': 'list comprehension, concise, create, example, square, even, range, condition'
        },
        {
            'role': 'python_developer',
            'question_text': 'What is the Global Interpreter Lock (GIL) in Python?',
            'model_answer': 'GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python code simultaneously. It can be a bottleneck for CPU-bound multi-threaded programs.',
            'keywords': 'GIL, mutex, thread, simultaneous, bottleneck, CPU-bound, multi-threaded, protection'
        },
        {
            'role': 'python_developer',
            'question_text': 'How do you handle exceptions in Python? Provide an example.',
            'model_answer': 'Use try-except blocks to handle exceptions. Example: try: risky_operation() except ValueError: handle_error() finally: cleanup()',
            'keywords': 'exception, try, except, finally, error, handle, block, ValueError'
        },
        
        # Data Engineer Questions
        {
            'role': 'data_engineer',
            'question_text': 'What is ETL and how does it differ from ELT?',
            'model_answer': 'ETL (Extract, Transform, Load) processes data before loading into destination. ELT (Extract, Load, Transform) loads raw data first, then transforms it in the destination system.',
            'keywords': 'ETL, ELT, extract, transform, load, destination, raw data, process'
        },
        {
            'role': 'data_engineer',
            'question_text': 'Explain the concept of data partitioning and its benefits.',
            'model_answer': 'Data partitioning divides large datasets into smaller, manageable pieces based on criteria like date or region. Benefits include improved query performance, parallel processing, and easier maintenance.',
            'keywords': 'partitioning, dataset, manageable, criteria, date, region, performance, parallel, maintenance'
        },
        {
            'role': 'data_engineer',
            'question_text': 'What is Apache Kafka and what are its main use cases?',
            'model_answer': 'Apache Kafka is a distributed streaming platform for building real-time data pipelines. Main use cases include event streaming, log aggregation, real-time analytics, and microservices communication.',
            'keywords': 'Kafka, distributed, streaming, real-time, pipeline, event, log aggregation, analytics, microservices'
        },
        {
            'role': 'data_engineer',
            'question_text': 'Describe the CAP theorem and its implications for distributed systems.',
            'model_answer': 'CAP theorem states that distributed systems can only guarantee two of three properties: Consistency, Availability, and Partition tolerance. This affects database design and system architecture decisions.',
            'keywords': 'CAP theorem, consistency, availability, partition tolerance, distributed, database, architecture'
        },
        {
            'role': 'data_engineer',
            'question_text': 'What is data lineage and why is it important?',
            'model_answer': 'Data lineage tracks the flow and transformation of data from source to destination. It\'s important for debugging, compliance, impact analysis, and understanding data dependencies.',
            'keywords': 'data lineage, flow, transformation, source, destination, debugging, compliance, impact analysis, dependencies'
        },
        
        # Web Developer Questions
        {
            'role': 'web_developer',
            'question_text': 'Explain the difference between var, let, and const in JavaScript.',
            'model_answer': 'var is function-scoped and can be redeclared. let is block-scoped and can be reassigned but not redeclared. const is block-scoped and cannot be reassigned or redeclared.',
            'keywords': 'var, let, const, function-scoped, block-scoped, redeclared, reassigned, JavaScript'
        },
        {
            'role': 'web_developer',
            'question_text': 'What is the DOM and how do you manipulate it?',
            'model_answer': 'DOM (Document Object Model) is a programming interface for HTML documents. Manipulate it using methods like getElementById, querySelector, createElement, appendChild, and addEventListener.',
            'keywords': 'DOM, Document Object Model, HTML, getElementById, querySelector, createElement, appendChild, addEventListener'
        },
        {
            'role': 'web_developer',
            'question_text': 'Explain the concept of responsive web design.',
            'model_answer': 'Responsive web design creates websites that adapt to different screen sizes and devices using flexible layouts, images, and CSS media queries.',
            'keywords': 'responsive, web design, screen sizes, devices, flexible, layouts, CSS, media queries'
        },
        {
            'role': 'web_developer',
            'question_text': 'What is CORS and why is it important?',
            'model_answer': 'CORS (Cross-Origin Resource Sharing) is a security mechanism that allows or restricts web pages to access resources from other domains. Important for API security and preventing malicious attacks.',
            'keywords': 'CORS, Cross-Origin Resource Sharing, security, domains, API, malicious, attacks, resources'
        },
        {
            'role': 'web_developer',
            'question_text': 'Describe the difference between HTTP and HTTPS.',
            'model_answer': 'HTTP transmits data in plain text, while HTTPS encrypts data using SSL/TLS protocols. HTTPS provides security, data integrity, and authentication.',
            'keywords': 'HTTP, HTTPS, plain text, encrypt, SSL, TLS, security, integrity, authentication'
        }
    ]
    
    for q_data in sample_questions:
        question = Question(**q_data)
        db.session.add(question)
    
    db.session.commit()
    print("Sample questions added to database!")
