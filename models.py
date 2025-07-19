from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import json
import os
import logging

class User(UserMixin):
    def __init__(self, user_id, email, password_hash=None, name="", theme="dark", email_notifications=False, sms_notifications=False, push_notifications=True):
        self.id = user_id
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.theme = theme
        self.email_notifications = email_notifications
        self.sms_notifications = sms_notifications
        self.push_notifications = push_notifications
        self.created_at = datetime.now().isoformat()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'password_hash': self.password_hash,
            'name': self.name,
            'theme': self.theme,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'push_notifications': self.push_notifications,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(
            user_id=data['id'],
            email=data['email'],
            password_hash=data['password_hash'],
            name=data.get('name', ''),
            theme=data.get('theme', 'dark'),
            email_notifications=data.get('email_notifications', False),
            sms_notifications=data.get('sms_notifications', False),
            push_notifications=data.get('push_notifications', True)
        )
        user.created_at = data.get('created_at', datetime.now().isoformat())
        return user

class UserManager:
    def __init__(self, data_file='data/users.json'):
        self.data_file = data_file
        self.ensure_data_directory()
        self.users = self.load_users()

    def ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

    def load_users(self):
        """Load users from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    users_data = json.load(f)
                    return {user_id: User.from_dict(data) for user_id, data in users_data.items()}
            return {}
        except Exception as e:
            logging.error(f"Error loading users: {e}")
            return {}

    def save_users(self):
        """Save users to JSON file"""
        try:
            users_data = {user_id: user.to_dict() for user_id, user in self.users.items()}
            with open(self.data_file, 'w') as f:
                json.dump(users_data, f, indent=2, default=str)
            return True
        except Exception as e:
            logging.error(f"Error saving users: {e}")
            return False

    def create_user(self, email, password, name=""):
        """Create a new user"""
        # Generate unique user ID
        user_id = str(len(self.users) + 1)
        while user_id in self.users:
            user_id = str(int(user_id) + 1)

        user = User(user_id, email, name=name)
        user.set_password(password)
        self.users[user_id] = user
        
        if self.save_users():
            return user
        return None

    def get_user(self, user_id):
        """Get user by ID"""
        return self.users.get(user_id)

    def get_user_by_email(self, email):
        """Get user by email"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def update_user(self, user_id, **kwargs):
        """Update user information"""
        user = self.users.get(user_id)
        if not user:
            return False

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        return self.save_users()

    def authenticate_user(self, email, password):
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if user and user.check_password(password):
            return user
        return None

# Global user manager instance
user_manager = UserManager()