import sqlite3
from datetime import datetime

conn = sqlite3.connect(
    "database/studybuddy.db",
    check_same_thread=False
)

cursor = conn.cursor()

# Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# User preferences
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    learning_style TEXT DEFAULT 'visual',
    daily_study_goal INTEGER DEFAULT 60,
    notification_enabled BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Progress tracking
cursor.execute('''
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic TEXT,
    score INTEGER,
    weak_area TEXT,
    learning_level TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Study groups
cursor.execute('''
CREATE TABLE IF NOT EXISTS study_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users (id)
)
''')

# Group members
cursor.execute('''
CREATE TABLE IF NOT EXISTS group_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES study_groups (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Shared notes
cursor.execute('''
CREATE TABLE IF NOT EXISTS shared_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    title TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES study_groups (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Platform integrations
cursor.execute('''
CREATE TABLE IF NOT EXISTS platform_integrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform_name TEXT,
    api_token TEXT,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

conn.commit()





# ============ USER FUNCTIONS ============

def create_user(username, email, password_hash):
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash)
    )
    conn.commit()
    return cursor.lastrowid

def get_user_by_username(username):
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone()

def get_user_by_email(email):
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cursor.fetchone()

# ============ PREFERENCES FUNCTIONS ============

def set_user_preference(user_id, learning_style, daily_goal, notification):
    cursor.execute(
        "SELECT id FROM user_preferences WHERE user_id = ?",
        (user_id,)
    )
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            """UPDATE user_preferences
               SET learning_style = ?, daily_study_goal = ?, notification_enabled = ?
               WHERE user_id = ?""",
            (learning_style, daily_goal, notification, user_id)
        )
    else:
        cursor.execute(
            """INSERT INTO user_preferences 
               (user_id, learning_style, daily_study_goal, notification_enabled)
               VALUES (?, ?, ?, ?)""",
            (user_id, learning_style, daily_goal, notification)
        )
    conn.commit()

def get_user_preference(user_id):
    cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

# ============ PROGRESS FUNCTIONS ============

def save_progress(user_id, topic, score, weak_area, learning_level):
    cursor.execute(
        """INSERT INTO progress
           (user_id, topic, score, weak_area, learning_level)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, topic, score, weak_area, learning_level)
    )
    conn.commit()

def fetch_progress(user_id):
    cursor.execute("SELECT * FROM progress WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    return cursor.fetchall()

def get_user_stats(user_id):
    cursor.execute(
        """SELECT topic, AVG(score) as avg_score, COUNT(*) as attempts 
           FROM progress WHERE user_id = ? 
           GROUP BY topic""",
        (user_id,)
    )
    return cursor.fetchall()

# ============ STUDY GROUP FUNCTIONS ============

def create_study_group(group_name, created_by, description):
    cursor.execute(
        """INSERT INTO study_groups (group_name, created_by, description)
           VALUES (?, ?, ?)""",
        (group_name, created_by, description)
    )
    conn.commit()
    return cursor.lastrowid

def add_member_to_group(group_id, user_id):
    cursor.execute(
        "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)",
        (group_id, user_id)
    )
    conn.commit()

def get_user_groups(user_id):
    cursor.execute(
        """SELECT * FROM study_groups WHERE id IN 
           (SELECT group_id FROM group_members WHERE user_id = ?)""",
        (user_id,)
    )
    return cursor.fetchall()

def get_group_members(group_id):
    cursor.execute(
        """SELECT u.id, u.username FROM users u 
           WHERE u.id IN (SELECT user_id FROM group_members WHERE group_id = ?)""",
        (group_id,)
    )
    return cursor.fetchall()

# ============ SHARED NOTES FUNCTIONS ============

def save_shared_note(group_id, user_id, title, content):
    cursor.execute(
        """INSERT INTO shared_notes (group_id, user_id, title, content)
           VALUES (?, ?, ?, ?)""",
        (group_id, user_id, title, content)
    )
    conn.commit()

def get_group_notes(group_id):
    cursor.execute(
        "SELECT * FROM shared_notes WHERE group_id = ? ORDER BY created_at DESC",
        (group_id,)
    )
    return cursor.fetchall()

# ============ PLATFORM INTEGRATION FUNCTIONS ============

def add_platform_integration(user_id, platform_name, api_token):
    cursor.execute(
        """INSERT INTO platform_integrations (user_id, platform_name, api_token)
           VALUES (?, ?, ?)""",
        (user_id, platform_name, api_token)
    )
    conn.commit()

def get_user_integrations(user_id):
    cursor.execute(
        "SELECT * FROM platform_integrations WHERE user_id = ?",
        (user_id,)
    )
    return cursor.fetchall()