import sqlite3
import os
from datetime import datetime

# conn = sqlite3.connect(
#     "smart-study-buddy/database/studybuddy.db",
#     check_same_thread=False
# )

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "studybuddy.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)

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

# Quiz schedules for spaced repetition
cursor.execute('''
CREATE TABLE IF NOT EXISTS quiz_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    scheduled_date DATE NOT NULL,
    completed BOOLEAN DEFAULT 0,
    completed_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
''')

# Index for faster queries
cursor.execute('''
CREATE INDEX IF NOT EXISTS idx_quiz_schedules_user_date 
ON quiz_schedules(user_id, scheduled_date, completed)
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

# ============ QUIZ SCHEDULE FUNCTIONS ============

def save_study_schedule(user_id, topic, scheduled_dates):
    """
    Save spaced repetition schedule to database
    
    Args:
        user_id: User ID
        topic: Topic to review
        scheduled_dates: List of dates to review (e.g., ["2024-07-01", "2024-07-03"])
    """
    for scheduled_date in scheduled_dates:
        cursor.execute("""
            INSERT INTO quiz_schedules (user_id, topic, scheduled_date)
            VALUES (?, ?, ?)
        """, (user_id, topic, scheduled_date))
    
    conn.commit()


def get_upcoming_schedule(user_id, days_ahead=30):
    """
    Get upcoming scheduled reviews for user
    
    Returns list of dicts:
    [
        {"id": 1, "topic": "Photosynthesis", "date": "2024-07-01", "completed": False},
    ]
    """
    from datetime import timedelta
    today = datetime.now().date()
    future_date = today + timedelta(days=days_ahead)
    
    cursor.execute("""
        SELECT id, topic, scheduled_date, completed
        FROM quiz_schedules
        WHERE user_id = ?
          AND scheduled_date >= ?
          AND scheduled_date <= ?
          AND completed = 0
        ORDER BY scheduled_date ASC
    """, (user_id, str(today), str(future_date)))
    
    rows = cursor.fetchall()
    return [
        {
            "id": row[0],
            "topic": row[1],
            "date": row[2],
            "completed": bool(row[3])
        }
        for row in rows
    ]


def get_overdue_schedule(user_id):
    """Get reviews that should have been completed by now"""
    today = datetime.now().date()
    
    cursor.execute("""
        SELECT id, topic, scheduled_date
        FROM quiz_schedules
        WHERE user_id = ?
          AND scheduled_date < ?
          AND completed = 0
        ORDER BY scheduled_date ASC
    """, (user_id, str(today)))
    
    rows = cursor.fetchall()
    result = []
    for row in rows:
        sched_date = datetime.strptime(row[2], "%Y-%m-%d").date()
        overdue_days = (today - sched_date).days
        result.append({
            "id": row[0],
            "topic": row[1],
            "overdue_days": overdue_days
        })
    return result


def mark_schedule_completed(schedule_id):
    """Mark a schedule item as completed"""
    today = datetime.now().date()
    
    cursor.execute("""
        UPDATE quiz_schedules
        SET completed = 1, completed_date = ?
        WHERE id = ?
    """, (str(today), schedule_id))
    
    conn.commit()