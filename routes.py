from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app
from data_manager import DataManager
from models import user_manager
from datetime import datetime, date
import random
import re

# Daily reflection prompts - Changes every day
DAILY_REFLECTION_PROMPTS = [
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
    "What's one way you can connect with others today?",
    "What challenge helped you grow stronger recently?",
    "How do you want to feel at the end of today?",
    "What's one thing you appreciate about your body today?",
    "What boundary do you need to set for your well-being?",
    "How can you honor your needs today?",
    "What would you tell a friend going through what you're experiencing?",
    "What's one thing you've overcome that you're proud of?",
    "How can you create more joy in your daily routine?",
    "What aspect of your life deserves more attention?",
    "What's one way you can practice patience with yourself today?",
    "How has your perspective changed recently?",
    "What's something you're curious to explore about yourself?",
    "How can you make today feel meaningful?",
    "What's one thing you've learned to let go of?",
    "How do you want to nurture yourself today?",
    "What strength do you possess that others might not see?"
]

# Daily Mental Health Tips - Changes every day
DAILY_MENTAL_HEALTH_TIPS = [
    {
        "title": "Practice Deep Breathing",
        "tip": "Take 5 minutes to practice deep breathing. Breathe in for 4 counts, hold for 4, exhale for 6. This activates your parasympathetic nervous system and reduces stress.",
        "category": "Breathing & Relaxation"
    },
    {
        "title": "Express Gratitude",
        "tip": "Write down 3 things you're grateful for today. Gratitude practice rewires your brain to notice positive aspects of life and improves overall mood.",
        "category": "Mindfulness & Gratitude"
    },
    {
        "title": "Move Your Body",
        "tip": "Even 10 minutes of physical activity can boost your mood. Try a short walk, stretching, or dancing to your favorite song.",
        "category": "Physical Wellness"
    },
    {
        "title": "Connect with Nature",
        "tip": "Spend time outdoors, even if it's just looking out a window at trees or sky. Nature exposure reduces cortisol levels and improves mental clarity.",
        "category": "Nature & Environment"
    },
    {
        "title": "Practice Self-Compassion",
        "tip": "Talk to yourself as you would to a good friend. Replace self-criticism with understanding and kindness toward yourself.",
        "category": "Self-Care & Compassion"
    },
    {
        "title": "Limit News Consumption",
        "tip": "Set boundaries around news and social media. Choose specific times to check updates rather than constantly scrolling throughout the day.",
        "category": "Digital Wellness"
    },
    {
        "title": "Focus on the Present",
        "tip": "Practice the 5-4-3-2-1 grounding technique: notice 5 things you see, 4 you can touch, 3 you hear, 2 you smell, and 1 you taste.",
        "category": "Mindfulness & Grounding"
    },
    {
        "title": "Prioritize Quality Sleep",
        "tip": "Create a relaxing bedtime routine. Avoid screens 1 hour before bed and keep your bedroom cool, dark, and quiet for better rest.",
        "category": "Sleep & Rest"
    },
    {
        "title": "Reach Out to Someone",
        "tip": "Connect with a friend, family member, or loved one today. Social connections are vital for mental health and emotional well-being.",
        "category": "Social Connection"
    },
    {
        "title": "Try Creative Expression",
        "tip": "Engage in any form of creativity - drawing, writing, singing, cooking. Creative activities reduce stress and provide emotional outlets.",
        "category": "Creativity & Expression"
    },
    {
        "title": "Set Small, Achievable Goals",
        "tip": "Choose one small task you can complete today. Accomplishing small goals builds confidence and creates positive momentum.",
        "category": "Goal Setting & Achievement"
    },
    {
        "title": "Practice Mindful Eating",
        "tip": "Eat one meal today without distractions. Pay attention to flavors, textures, and how food makes you feel physically and emotionally.",
        "category": "Nutrition & Mindfulness"
    },
    {
        "title": "Declutter Your Space",
        "tip": "Organize one small area of your living space. A tidy environment can reduce mental clutter and create a sense of accomplishment.",
        "category": "Environment & Organization"
    },
    {
        "title": "Learn Something New",
        "tip": "Spend 15 minutes learning about something that interests you. Learning new things stimulates brain growth and boosts self-esteem.",
        "category": "Learning & Growth"
    },
    {
        "title": "Practice Saying No",
        "tip": "It's okay to decline requests that overwhelm you. Setting healthy boundaries protects your energy and mental health.",
        "category": "Boundaries & Self-Care"
    },
    {
        "title": "Use Positive Affirmations",
        "tip": "Choose a positive statement about yourself and repeat it throughout the day. 'I am capable,' 'I am worthy,' or 'I am growing stronger.'",
        "category": "Self-Talk & Affirmations"
    },
    {
        "title": "Take Breaks During Work",
        "tip": "Every hour, take a 5-minute break from work or screens. Step away, stretch, or simply rest your eyes to prevent mental fatigue.",
        "category": "Work-Life Balance"
    },
    {
        "title": "Listen to Calming Music",
        "tip": "Create a playlist of songs that make you feel peaceful or happy. Music has powerful effects on mood and can reduce anxiety.",
        "category": "Music & Sound"
    },
    {
        "title": "Practice Forgiveness",
        "tip": "Consider forgiving someone (including yourself) for a past mistake. Letting go of resentment frees up mental energy for positive growth.",
        "category": "Emotional Healing"
    },
    {
        "title": "Hydrate Mindfully",
        "tip": "Drink water throughout the day and notice how it makes you feel. Dehydration can affect mood, energy, and cognitive function.",
        "category": "Physical Wellness"
    },
    {
        "title": "Practice Random Acts of Kindness",
        "tip": "Do something kind for someone else today, even something small. Helping others boosts your own mood and creates positive connections.",
        "category": "Kindness & Service"
    },
    {
        "title": "Embrace Imperfection",
        "tip": "Remember that mistakes are part of learning and growth. Perfectionism can create unnecessary stress and anxiety.",
        "category": "Self-Acceptance"
    },
    {
        "title": "Create a Calming Environment",
        "tip": "Add something soothing to your space today - a plant, soft lighting, or pleasant scent. Your environment affects your mood.",
        "category": "Environment & Ambiance"
    },
    {
        "title": "Practice Body Awareness",
        "tip": "Do a quick body scan. Notice areas of tension and consciously relax them. Physical awareness helps process emotions.",
        "category": "Body & Mind Connection"
    },
    {
        "title": "Limit Multitasking",
        "tip": "Focus on one task at a time today. Single-tasking reduces stress and improves the quality of your work and attention.",
        "category": "Focus & Productivity"
    },
    {
        "title": "Celebrate Small Wins",
        "tip": "Acknowledge something you accomplished today, no matter how small. Celebrating progress builds resilience and motivation.",
        "category": "Self-Recognition"
    },
    {
        "title": "Try Progressive Muscle Relaxation",
        "tip": "Tense and then relax each muscle group in your body, starting from your toes and working up. This releases physical tension.",
        "category": "Relaxation Techniques"
    },
    {
        "title": "Write Your Thoughts",
        "tip": "Spend 10 minutes writing about your thoughts or feelings. Journaling helps process emotions and gain clarity.",
        "category": "Writing & Reflection"
    },
    {
        "title": "Practice Acceptance",
        "tip": "Identify one thing you can't control and practice accepting it. Focus your energy on what you can influence instead.",
        "category": "Acceptance & Control"
    },
    {
        "title": "Use Your Senses",
        "tip": "Engage one of your senses intentionally - smell a flower, feel a soft texture, or listen to birds singing. Sensory experiences ground you in the present.",
        "category": "Sensory Awareness"
    },
    {
        "title": "Plan Something to Look Forward To",
        "tip": "Schedule something enjoyable for this week or next - a movie, meal with a friend, or hobby time. Anticipation boosts mood.",
        "category": "Future Planning & Joy"
    }
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

def get_daily_mental_health_tip():
    """Get today's mental health tip based on current date"""
    today = datetime.now()
    # Create a seed based on year and day of year to ensure same tip per day
    day_seed = today.year * 1000 + today.timetuple().tm_yday
    random.seed(day_seed)
    
    # Select today's tip
    tip_index = random.randint(0, len(DAILY_MENTAL_HEALTH_TIPS) - 1)
    daily_tip = DAILY_MENTAL_HEALTH_TIPS[tip_index]
    
    # Reset random seed
    random.seed()
    
    return daily_tip

def get_daily_reflection_prompt():
    """Get today's reflection prompt based on current date"""
    today = datetime.now()
    # Create a different seed for prompts to ensure variety from tips
    prompt_seed = (today.year * 1000 + today.timetuple().tm_yday) * 2 + 1
    random.seed(prompt_seed)
    
    # Select today's prompt
    prompt_index = random.randint(0, len(DAILY_REFLECTION_PROMPTS) - 1)
    daily_prompt = DAILY_REFLECTION_PROMPTS[prompt_index]
    
    # Reset random seed
    random.seed()
    
    return daily_prompt

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
    
    # Get today's dynamic prompt and mental health tip
    daily_prompt = get_daily_reflection_prompt()
    daily_mental_health_tip = get_daily_mental_health_tip()
    
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
                         daily_mental_health_tip=daily_mental_health_tip,
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

@app.route('/api/daily_mental_health_tip')
@login_required
def api_daily_mental_health_tip():
    """API endpoint to get today's mental health tip"""
    daily_tip = get_daily_mental_health_tip()
    return jsonify(daily_tip)
