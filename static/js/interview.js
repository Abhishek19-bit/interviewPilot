// Interview Timer and Auto-submit functionality
let timeLeft = 30; // 30 seconds per question
let timerInterval;
let submitted = false;

// Initialize timer when page loads
document.addEventListener('DOMContentLoaded', function() {
    startTimer();
    
    // Auto-focus on answer textarea
    const answerTextarea = document.getElementById('answerTextarea');
    if (answerTextarea) {
        answerTextarea.focus();
    }
    
    // Prevent form submission if already submitted
    const form = document.getElementById('answerForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (submitted) {
                e.preventDefault();
                return false;
            }
            submitted = true;
            
            // Disable submit button to prevent double submission
            const submitBtn = document.getElementById('submitBtn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
            }
        });
    }
    
    // Auto-resize textarea
    if (answerTextarea) {
        answerTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
});

function startTimer() {
    const timerElement = document.getElementById('timer');
    if (!timerElement) return;
    
    timerInterval = setInterval(function() {
        timeLeft--;
        
        // Update timer display
        timerElement.textContent = timeLeft + 's';
        
        // Change timer color based on time left
        timerElement.classList.remove('warning', 'danger');
        if (timeLeft <= 10) {
            timerElement.classList.add('danger');
            // Add pulse effect for urgency
            timerElement.style.animation = 'pulse 1s infinite';
        } else if (timeLeft <= 20) {
            timerElement.classList.add('warning');
        }
        
        // Auto-submit when time runs out
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            autoSubmitAnswer();
        }
    }, 1000);
}

function autoSubmitAnswer() {
    if (submitted) return;
    
    // Show time's up modal
    const modal = new bootstrap.Modal(document.getElementById('timeUpModal'));
    modal.show();
    
    // Auto-submit after 3 seconds if user doesn't click continue
    setTimeout(function() {
        modal.hide();
        submitAnswer();
    }, 3000);
}

function submitAnswer() {
    if (submitted) return;
    
    const form = document.getElementById('answerForm');
    const answerTextarea = document.getElementById('answerTextarea');
    
    // If answer is empty, add a default message
    if (!answerTextarea.value.trim()) {
        answerTextarea.value = "Time ran out - no answer provided.";
    }
    
    // Submit the form
    if (form) {
        submitted = true;
        form.submit();
    }
}

function skipQuestion() {
    if (submitted) return;
    
    const answerTextarea = document.getElementById('answerTextarea');
    if (answerTextarea) {
        answerTextarea.value = "Question skipped by user.";
    }
    
    submitAnswer();
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        submitAnswer();
    }
    
    // Escape to skip question
    if (e.key === 'Escape') {
        e.preventDefault();
        if (confirm('Are you sure you want to skip this question?')) {
            skipQuestion();
        }
    }
});

// Save answer to localStorage periodically (in case of browser crash)
setInterval(function() {
    const answerTextarea = document.getElementById('answerTextarea');
    if (answerTextarea && answerTextarea.value.trim()) {
        localStorage.setItem('interview_current_answer', answerTextarea.value);
    }
}, 5000);

// Restore answer from localStorage if available
document.addEventListener('DOMContentLoaded', function() {
    const answerTextarea = document.getElementById('answerTextarea');
    const savedAnswer = localStorage.getItem('interview_current_answer');
    
    if (answerTextarea && savedAnswer && !answerTextarea.value.trim()) {
        answerTextarea.value = savedAnswer;
        answerTextarea.dispatchEvent(new Event('input')); // Trigger auto-resize
    }
});

// Clear saved answer when form is submitted
document.getElementById('answerForm')?.addEventListener('submit', function() {
    localStorage.removeItem('interview_current_answer');
});

// Progress indicator animation
function updateProgress() {
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        const currentWidth = parseFloat(progressBar.style.width);
        progressBar.style.transition = 'width 0.5s ease';
    }
}

// Smooth scrolling for mobile devices
function scrollToQuestion() {
    const questionCard = document.querySelector('.question-card');
    if (questionCard && window.innerWidth <= 768) {
        questionCard.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
}

// Initialize smooth scrolling on mobile
document.addEventListener('DOMContentLoaded', function() {
    if (window.innerWidth <= 768) {
        setTimeout(scrollToQuestion, 500);
    }
});

// Warn user before leaving the page
window.addEventListener('beforeunload', function(e) {
    if (!submitted && document.getElementById('answerTextarea')?.value.trim()) {
        e.preventDefault();
        e.returnValue = 'You have an unsaved answer. Are you sure you want to leave?';
        return e.returnValue;
    }
});

// Add visual feedback for typing
document.getElementById('answerTextarea')?.addEventListener('input', function() {
    const charCount = this.value.length;
    const wordCount = this.value.trim().split(/\s+/).filter(word => word.length > 0).length;
    
    // You could add a character/word counter here if desired
    // For now, just add a subtle visual indicator that user is typing
    this.style.borderColor = charCount > 0 ? '#667eea' : '';
});
