from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app
from data_manager import data_manager
from datetime import datetime, date
import random

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

@app.route('/')
def index():
    """Main dashboard"""
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
    
    return render_template('index.html', 
                         daily_prompt=daily_prompt,
                         stats=stats,
                         recent_moods=recent_moods[:3],
                         recent_sleep=recent_sleep[:3])

@app.route('/mood', methods=['GET', 'POST'])
def mood_tracking():
    """Mood tracking page"""
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
def sleep_tracking():
    """Sleep tracking page"""
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
def habits():
    """Habits tracking page"""
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
def journal():
    """Secure journaling page"""
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
def insights():
    """Insights and data visualization page"""
    mood_entries = data_manager.get_mood_entries(30)
    sleep_entries = data_manager.get_sleep_entries(30)
    insights_list = data_manager.get_insights()
    
    return render_template('insights.html', 
                         mood_entries=mood_entries,
                         sleep_entries=sleep_entries,
                         insights=insights_list)

@app.route('/api/mood_data')
def api_mood_data():
    """API endpoint for mood chart data"""
    entries = data_manager.get_mood_entries(30)
    entries.reverse()  # Chronological order for charts
    
    return jsonify({
        'dates': [entry['date'] for entry in entries],
        'scores': [entry['mood_score'] for entry in entries]
    })

@app.route('/api/sleep_data')
def api_sleep_data():
    """API endpoint for sleep chart data"""
    entries = data_manager.get_sleep_entries(30)
    entries.reverse()  # Chronological order for charts
    
    return jsonify({
        'dates': [entry['date'] for entry in entries],
        'duration': [entry['duration'] for entry in entries],
        'quality': [entry['quality'] for entry in entries]
    })
