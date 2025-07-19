import json
import os
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import logging

class DataManager:
    def __init__(self, data_file='data/user_data.json'):
        self.data_file = data_file
        self.ensure_data_directory()
        self.data = self.load_data()
    
    def ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def load_data(self):
        """Load data from JSON file or create new structure"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    # Ensure all required keys exist
                    default_structure = {
                        'mood_entries': [],
                        'sleep_entries': [],
                        'habits': [],
                        'habit_entries': [],
                        'journal_entries': [],
                        'journal_password_hash': None,
                        'settings': {
                            'created_date': datetime.now().isoformat()
                        }
                    }
                    for key in default_structure:
                        if key not in data:
                            data[key] = default_structure[key]
                    return data
            else:
                return {
                    'mood_entries': [],
                    'sleep_entries': [],
                    'habits': [],
                    'habit_entries': [],
                    'journal_entries': [],
                    'journal_password_hash': None,
                    'settings': {
                        'created_date': datetime.now().isoformat()
                    }
                }
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            return {
                'mood_entries': [],
                'sleep_entries': [],
                'habits': [],
                'habit_entries': [],
                'journal_entries': [],
                'journal_password_hash': None,
                'settings': {
                    'created_date': datetime.now().isoformat()
                }
            }
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
            return True
        except Exception as e:
            logging.error(f"Error saving data: {e}")
            return False
    
    def add_mood_entry(self, mood_score, notes=""):
        """Add a mood entry"""
        entry = {
            'id': len(self.data['mood_entries']) + 1,
            'date': date.today().isoformat(),
            'mood_score': mood_score,
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        }
        self.data['mood_entries'].append(entry)
        return self.save_data()
    
    def add_sleep_entry(self, duration, quality, bedtime="", wake_time="", notes=""):
        """Add a sleep entry"""
        entry = {
            'id': len(self.data['sleep_entries']) + 1,
            'date': date.today().isoformat(),
            'duration': duration,
            'quality': quality,
            'bedtime': bedtime,
            'wake_time': wake_time,
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        }
        self.data['sleep_entries'].append(entry)
        return self.save_data()
    
    def add_habit(self, name, description=""):
        """Add a new habit to track"""
        habit = {
            'id': len(self.data['habits']) + 1,
            'name': name,
            'description': description,
            'created_date': date.today().isoformat()
        }
        self.data['habits'].append(habit)
        return self.save_data()
    
    def add_habit_entry(self, habit_id, completed=True, notes=""):
        """Add a habit tracking entry"""
        entry = {
            'id': len(self.data['habit_entries']) + 1,
            'habit_id': habit_id,
            'date': date.today().isoformat(),
            'completed': completed,
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        }
        self.data['habit_entries'].append(entry)
        return self.save_data()
    
    def set_journal_password(self, password):
        """Set or update journal password"""
        self.data['journal_password_hash'] = generate_password_hash(password)
        return self.save_data()
    
    def verify_journal_password(self, password):
        """Verify journal password"""
        if not self.data['journal_password_hash']:
            return False
        return check_password_hash(self.data['journal_password_hash'], password)
    
    def add_journal_entry(self, title, content):
        """Add a journal entry"""
        entry = {
            'id': len(self.data['journal_entries']) + 1,
            'date': date.today().isoformat(),
            'title': title,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.data['journal_entries'].append(entry)
        return self.save_data()
    
    def get_mood_entries(self, days=30):
        """Get recent mood entries"""
        return sorted(self.data['mood_entries'], key=lambda x: x['date'], reverse=True)[:days]
    
    def get_sleep_entries(self, days=30):
        """Get recent sleep entries"""
        return sorted(self.data['sleep_entries'], key=lambda x: x['date'], reverse=True)[:days]
    
    def get_habits(self):
        """Get all habits"""
        return self.data['habits']
    
    def get_habit_entries(self, days=30):
        """Get recent habit entries"""
        return sorted(self.data['habit_entries'], key=lambda x: x['date'], reverse=True)[:days*len(self.data['habits'])]
    
    def get_journal_entries(self, days=30):
        """Get recent journal entries"""
        return sorted(self.data['journal_entries'], key=lambda x: x['date'], reverse=True)[:days]
    
    def has_journal_password(self):
        """Check if journal password is set"""
        return self.data['journal_password_hash'] is not None
    
    def get_insights(self):
        """Generate insights based on tracked data"""
        insights = []
        
        # Mood insights
        recent_moods = self.get_mood_entries(7)
        if recent_moods:
            avg_mood = sum(entry['mood_score'] for entry in recent_moods) / len(recent_moods)
            if avg_mood >= 8:
                insights.append("🌟 Your mood has been consistently high this week! Keep up the great work!")
            elif avg_mood >= 6:
                insights.append("😊 Your mood has been fairly positive this week. Consider what's been working well.")
            elif avg_mood >= 4:
                insights.append("🤔 Your mood has been moderate this week. Try incorporating more activities you enjoy.")
            else:
                insights.append("💙 Your mood has been challenging this week. Remember to be kind to yourself and consider reaching out for support.")
        
        # Sleep insights
        recent_sleep = self.get_sleep_entries(7)
        if recent_sleep:
            avg_duration = sum(entry['duration'] for entry in recent_sleep) / len(recent_sleep)
            if avg_duration >= 7:
                insights.append("💤 Great job maintaining healthy sleep habits!")
            else:
                insights.append("😴 Consider prioritizing more sleep - aim for 7-9 hours per night.")
        
        # Habit insights
        recent_habits = self.get_habit_entries(7)
        if recent_habits:
            completion_rate = sum(1 for entry in recent_habits if entry['completed']) / len(recent_habits)
            if completion_rate >= 0.8:
                insights.append("🎯 Excellent habit consistency! You're building strong routines.")
            elif completion_rate >= 0.5:
                insights.append("📈 Good progress on your habits. Small steps lead to big changes!")
            else:
                insights.append("🌱 Remember, building habits takes time. Focus on progress, not perfection.")
        
        return insights

# Global data manager instance
data_manager = DataManager()
