from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app
from data_manager import DataManager
from models import user_manager
from datetime import datetime, date
import random
import re

# Motivational prompts
DAILY_PROMPTS = [
    "What are three things you're grateful for today?",
    "How did you show kindness to yourself or others today?",
    "What's one small victory you achieved today?",
    "What emotion are you feeling right now, and that's okay?",
    "What's one thing that made you smile today?",
    "How can you be gentle with yourself today?",
    "What's one positive affirmation you need to hear right now?",
    "What activity brings you the most peace?",
    "Who in your life are you most grateful for?",
    "What's one thing you're looking forward to?",
    "How did you take care of your mental health today?",
    "What's one lesson you learned about yourself recently?",
    "What makes you feel most confident?",
    "How can you practice self-compassion today?",
    "What's one way you can connect with others today?"
]

# Motivational sayings for notifications
MOTIVATIONAL_SAYINGS = [
    "You are stronger than you think and more capable than you realize.",
    "Every small step forward is progress worth celebrating.",
    "Your mental health journey is unique and valid.",
    "It's okay to have difficult days - they don't define you.",
    "You deserve the same compassion you show others.",
    "Taking care of your mental health is a sign of strength, not weakness.",
    "You are worthy of love, peace, and happiness.",
    "Progress isn't always linear, and that's perfectly okay.",
    "Your feelings are valid, and you have the strength to work through them.",
    "You've overcome challenges before, and you can do it again.",
    "Self-care isn't selfish - it's necessary.",
    "You are not alone in your journey.",
    "Small acts of self-kindness can create big changes.",
    "Your story isn't over yet - there are beautiful chapters ahead.",
    "You have the power to create positive change in your life.",
    "Rest is productive too - honor what your mind and body need.",
    "You are enough, exactly as you are right now.",
    "Healing isn't a destination, it's a journey worth taking.",
    "Your courage to keep going inspires more than you know.",
    "Tomorrow is a new day with new possibilities."
]

def get_user_data_manager():
    """Get data manager for current user"""
    if current_user.is_authenticated:
        return DataManager(current_user.id)
    return DataManager()

@app.route('/')
def index():
    """Main dashboard"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # Get user-specific data manager
    data_manager = get_user_data_manager()
    
    # Get today's prompt
    today_index = datetime.now().timetuple().tm_yday % len(DAILY_PROMPTS)
    daily_prompt = DAILY_PROMPTS[today_index]
    
    # Get recent entries for dashboard
    recent_moods = data_manager.get_mood_entries(7)
    recent_sleep = data_manager.get_sleep_entries(7)
    recent_habits = data_manager.get_habit_entries(7)
    
    # Calculate quick stats
    stats = {
        'total_entries': len(data_manager.data['mood_entries']) + len(data_manager.data['sleep_entries']),
        'avg_mood_week': 0,
        'avg_sleep_week': 0,
        'habit_completion_week': 0
    }
    
    if recent_moods:
        stats['avg_mood_week'] = round(sum(entry['mood_score'] for entry in recent_moods) / len(recent_moods), 1)
    
    if recent_sleep:
        stats['avg_sleep_week'] = round(sum(entry['duration'] for entry in recent_sleep) / len(recent_sleep), 1)
    
    if recent_habits:
        completed_habits = sum(1 for entry in recent_habits if entry['completed'])
        stats['habit_completion_week'] = round((completed_habits / len(recent_habits)) * 100)
    
    # Get notification settings for the dashboard
    notification_settings = data_manager.get_notification_settings()
    
    return render_template('index.html', 
                         daily_prompt=daily_prompt,
                         stats=stats,
                         recent_moods=recent_moods[:3],
                         recent_sleep=recent_sleep[:3],
                         notification_settings=notification_settings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        # Basic validation
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('auth/login.html')
        
        # Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash('Please enter a valid email address.', 'error')
            return render_template('auth/login.html')
        
        # Authenticate user
        user = user_manager.authenticate_user(email, password)
        if user:
            login_user(user, remember=remember_me)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.name or user.email}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Basic validation
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('auth/signup.html')
        
        # Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash('Please enter a valid email address.', 'error')
            return render_template('auth/signup.html')
        
        # Password validation
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/signup.html')
        
        # Check if user already exists
        existing_user = user_manager.get_user_by_email(email)
        if existing_user:
            flash('An account with this email already exists.', 'error')
            return render_template('auth/signup.html')
        
        # Create new user
        user = user_manager.create_user(email, password, name)
        if user:
            login_user(user)
            flash(f'Welcome to MindTrack, {user.name or user.email}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Error creating account. Please try again.', 'error')
    
    return render_template('auth/signup.html')

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/forgot-password')
def forgot_password():
    """Forgot password page (placeholder for now)"""
    flash('Password reset functionality will be available soon. Please contact support if needed.', 'info')
    return redirect(url_for('login'))

@app.route('/mood', methods=['GET', 'POST'])
@login_required
def mood_tracking():
    """Mood tracking page"""
    data_manager = get_user_data_manager()
    if request.method == 'POST':
        mood_score = int(request.form.get('mood_score'))
        notes = request.form.get('notes', '')
        
        if data_manager.add_mood_entry(mood_score, notes):
            flash('Mood entry saved successfully!', 'success')
        else:
            flash('Error saving mood entry.', 'error')
        
        return redirect(url_for('mood_tracking'))
    
    mood_entries = data_manager.get_mood_entries(30)
    return render_template('mood_tracking.html', mood_entries=mood_entries)

@app.route('/sleep', methods=['GET', 'POST'])
@login_required
def sleep_tracking():
    """Sleep tracking page"""
    data_manager = get_user_data_manager()
    if request.method == 'POST':
        duration = float(request.form.get('duration'))
        quality = int(request.form.get('quality'))
        bedtime = request.form.get('bedtime', '')
        wake_time = request.form.get('wake_time', '')
        notes = request.form.get('notes', '')
        
        if data_manager.add_sleep_entry(duration, quality, bedtime, wake_time, notes):
            flash('Sleep entry saved successfully!', 'success')
        else:
            flash('Error saving sleep entry.', 'error')
        
        return redirect(url_for('sleep_tracking'))
    
    sleep_entries = data_manager.get_sleep_entries(30)
    return render_template('sleep_tracking.html', sleep_entries=sleep_entries)

@app.route('/habits', methods=['GET', 'POST'])
@login_required
def habits():
    """Habits tracking page"""
    data_manager = get_user_data_manager()
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_habit':
            name = request.form.get('name')
            description = request.form.get('description', '')
            
            if data_manager.add_habit(name, description):
                flash('Habit added successfully!', 'success')
            else:
                flash('Error adding habit.', 'error')
        
        elif action == 'log_habit':
            habit_id = int(request.form.get('habit_id'))
            completed = request.form.get('completed') == 'on'
            notes = request.form.get('notes', '')
            
            if data_manager.add_habit_entry(habit_id, completed, notes):
                flash('Habit entry saved successfully!', 'success')
            else:
                flash('Error saving habit entry.', 'error')
        
        return redirect(url_for('habits'))
    
    all_habits = data_manager.get_habits()
    habit_entries = data_manager.get_habit_entries(30)
    
    # Check if habits were completed today
    today_str = date.today().isoformat()
    today_entries = [entry for entry in habit_entries if entry['date'] == today_str]
    completed_today = {entry['habit_id']: entry['completed'] for entry in today_entries}
    
    return render_template('habits.html', 
                         habits=all_habits, 
                         habit_entries=habit_entries,
                         completed_today=completed_today)

@app.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    """Secure journaling page"""
    data_manager = get_user_data_manager()
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'set_password':
            password = request.form.get('password')
            if data_manager.set_journal_password(password):
                session['journal_authenticated'] = True
                flash('Journal password set successfully!', 'success')
            else:
                flash('Error setting password.', 'error')
        
        elif action == 'authenticate':
            password = request.form.get('password')
            if data_manager.verify_journal_password(password):
                session['journal_authenticated'] = True
                flash('Access granted!', 'success')
            else:
                flash('Incorrect password.', 'error')
        
        elif action == 'add_entry':
            if session.get('journal_authenticated'):
                title = request.form.get('title')
                content = request.form.get('content')
                
                if data_manager.add_journal_entry(title, content):
                    flash('Journal entry saved successfully!', 'success')
                else:
                    flash('Error saving journal entry.', 'error')
            else:
                flash('Please authenticate first.', 'error')
        
        elif action == 'logout':
            session.pop('journal_authenticated', None)
            flash('Logged out of journal.', 'info')
        
        return redirect(url_for('journal'))
    
    # Check if password is set
    has_password = data_manager.has_journal_password()
    is_authenticated = session.get('journal_authenticated', False)
    
    journal_entries = []
    if is_authenticated:
        journal_entries = data_manager.get_journal_entries(30)
    
    return render_template('journal.html', 
                         has_password=has_password,
                         is_authenticated=is_authenticated,
                         journal_entries=journal_entries)

@app.route('/insights')
@login_required
def insights():
    """Insights and data visualization page"""
    data_manager = get_user_data_manager()
    mood_entries = data_manager.get_mood_entries(30)
    sleep_entries = data_manager.get_sleep_entries(30)
    insights_list = data_manager.get_insights()
    
    return render_template('insights.html', 
                         mood_entries=mood_entries,
                         sleep_entries=sleep_entries,
                         insights=insights_list)

@app.route('/api/mood_data')
@login_required
def api_mood_data():
    """API endpoint for mood chart data"""
    data_manager = get_user_data_manager()
    entries = data_manager.get_mood_entries(30)
    entries.reverse()  # Chronological order for charts
    
    return jsonify({
        'dates': [entry['date'] for entry in entries],
        'scores': [entry['mood_score'] for entry in entries]
    })

@app.route('/api/sleep_data')
@login_required
def api_sleep_data():
    """API endpoint for sleep chart data"""
    data_manager = get_user_data_manager()
    entries = data_manager.get_sleep_entries(30)
    entries.reverse()  # Chronological order for charts
    
    return jsonify({
        'dates': [entry['date'] for entry in entries],
        'duration': [entry['duration'] for entry in entries],
        'quality': [entry['quality'] for entry in entries]
    })

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Enhanced settings page with user profile and preferences"""
    data_manager = get_user_data_manager()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Basic validation
            if not email:
                flash('Email is required.', 'error')
                return redirect(url_for('settings'))
            
            # Validate email format
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                flash('Please enter a valid email address.', 'error')
                return redirect(url_for('settings'))
            
            # Check if email is already taken by another user
            existing_user = user_manager.get_user_by_email(email)
            if existing_user and existing_user.id != current_user.id:
                flash('This email is already in use by another account.', 'error')
                return redirect(url_for('settings'))
            
            # Handle password change
            if new_password:
                if not current_password:
                    flash('Please enter your current password to change it.', 'error')
                    return redirect(url_for('settings'))
                
                if not current_user.check_password(current_password):
                    flash('Current password is incorrect.', 'error')
                    return redirect(url_for('settings'))
                
                if len(new_password) < 6:
                    flash('New password must be at least 6 characters long.', 'error')
                    return redirect(url_for('settings'))
                
                if new_password != confirm_password:
                    flash('New passwords do not match.', 'error')
                    return redirect(url_for('settings'))
                
                current_user.set_password(new_password)
            
            # Update profile
            if user_manager.update_user(current_user.id, name=name, email=email):
                current_user.name = name
                current_user.email = email
                flash('Profile updated successfully!', 'success')
            else:
                flash('Error updating profile.', 'error')
        
        elif action == 'update_theme':
            theme = request.form.get('theme', 'dark')
            if user_manager.update_user(current_user.id, theme=theme):
                current_user.theme = theme
                flash('Theme updated successfully!', 'success')
            else:
                flash('Error updating theme.', 'error')
        
        elif action == 'update_notifications':
            email_notifications = request.form.get('email_notifications') == 'on'
            sms_notifications = request.form.get('sms_notifications') == 'on'
            push_notifications = request.form.get('push_notifications') == 'on'
            
            # Update browser notification settings
            enabled = request.form.get('browser_notifications_enabled') == 'on'
            frequency = request.form.get('notification_frequency', 'daily')
            
            # Update user notification preferences
            user_success = user_manager.update_user(current_user.id, 
                                                  email_notifications=email_notifications,
                                                  sms_notifications=sms_notifications,
                                                  push_notifications=push_notifications)
            
            # Update browser notification settings
            browser_success = data_manager.update_notification_settings(enabled=enabled, frequency=frequency)
            
            if user_success and browser_success:
                current_user.email_notifications = email_notifications
                current_user.sms_notifications = sms_notifications
                current_user.push_notifications = push_notifications
                flash('Notification settings updated successfully!', 'success')
            else:
                flash('Error updating notification settings.', 'error')
        
        elif action == 'test_notification':
            # Test browser notification functionality
            if data_manager.update_notification_settings(last_notification=datetime.now().isoformat()):
                flash('Test notification sent! Check if you received it.', 'info')
            else:
                flash('Error sending test notification.', 'error')
        
        return redirect(url_for('settings'))
    
    # Get current notification settings
    notification_settings = data_manager.get_notification_settings()
    
    return render_template('enhanced_settings.html', 
                         user=current_user,
                         notification_settings=notification_settings)

@app.route('/api/motivational_saying')
@login_required
def api_motivational_saying():
    """API endpoint to get a random motivational saying"""
    saying = random.choice(MOTIVATIONAL_SAYINGS)
    return jsonify({'saying': saying})
