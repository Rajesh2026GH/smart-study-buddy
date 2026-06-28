"""
Create test users with different proficiency levels for testing
- Beginner: Low scores, just started
- Intermediate: Medium scores, making progress
- Advanced: High scores, mastering content
"""

import sqlite3
from datetime import datetime, timedelta
from backend.auth import hash_password

conn = sqlite3.connect("database/studybuddy.db", check_same_thread=False)
cursor = conn.cursor()

# Test user credentials
TEST_USERS = {
    "beginner_user": {
        "username": "alice_smith",
        "email": "alice@studybuddy.com",
        "password": "Alice123!",
        "learning_style": "visual",
        "daily_goal": 30,
        "scores": [42, 38, 45, 40, 48],  # Low scores (< 50)
        "topics": ["Algebra", "Geometry", "Fractions", "Decimals", "Percentages"]
    },
    "intermediate_user": {
        "username": "bob_johnson",
        "email": "bob@studybuddy.com",
        "password": "Bob456!",
        "learning_style": "auditory",
        "daily_goal": 60,
        "scores": [65, 72, 68, 70, 75],  # Medium scores (60-80)
        "topics": ["Calculus", "Statistics", "Trigonometry", "Algebra II", "Linear Equations"]
    },
    "advanced_user": {
        "username": "charlie_davis",
        "email": "charlie@studybuddy.com",
        "password": "Charlie789!",
        "learning_style": "kinesthetic",
        "daily_goal": 120,
        "scores": [88, 92, 85, 90, 95],  # High scores (> 85)
        "topics": ["Differential Equations", "Matrix Theory", "Complex Analysis", "Abstract Algebra", "Topology"]
    }
}

def create_test_users():
    """Create test users with their progress data"""
    
    print("🔄 Creating test users...")
    
    for username, user_data in TEST_USERS.items():
        try:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (user_data["username"],))
            if cursor.fetchone():
                print(f"⏭️  User {username} already exists, skipping...")
                continue
            
            # Create user
            password_hash = hash_password(user_data["password"])
            # cursor.execute(
            #     """INSERT INTO users (username, email, password_hash)
            #        VALUES (?, ?, ?)""",
            #     (username, user_data["username"], password_hash)
            # )
            cursor.execute(
                """INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)""",
                (user_data["username"], user_data["email"], password_hash)
            )
            user_id = cursor.lastrowid
            conn.commit()
            print(f"✅ Created user: {username} (ID: {user_id})")
            
            # Set user preferences
            cursor.execute(
                """INSERT INTO user_preferences (user_id, learning_style, daily_study_goal)
                   VALUES (?, ?, ?)""",
                (user_id, user_data["learning_style"], user_data["daily_goal"])
            )
            conn.commit()
            print(f"   ✓ Set preferences: {user_data['learning_style']} style, {user_data['daily_goal']} min/day")
            
            # Create progress records
            for i, (score, topic) in enumerate(zip(user_data["scores"], user_data["topics"])):
                # Calculate timestamp (spread over the last 5 days)
                days_ago = 4 - i
                timestamp = datetime.now() - timedelta(days=days_ago)
                
                # Determine learning level
                if score >= 85:
                    level = "Advanced"
                elif score >= 60:
                    level = "Intermediate"
                else:
                    level = "Beginner"
                
                # Determine weak area based on score
                if score < 60:
                    weak_area = f"Concept understanding in {topic}"
                elif score < 75:
                    weak_area = f"Problem-solving in {topic}"
                else:
                    weak_area = None
                
                cursor.execute(
                    """INSERT INTO progress (user_id, topic, score, weak_area, learning_level, timestamp)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, topic, score, weak_area or "None", level, timestamp.strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
                print(f"   ✓ Added: {topic} - Score: {score} - Level: {level}")
            
            # Create some schedules for upcoming reviews
            print(f"   ✓ Creating spaced repetition schedules...")
            for i, topic in enumerate(user_data["topics"][:3]):  # Schedule first 3 topics
                days_out = [1, 3, 7]
                for days in days_out:
                    scheduled_date = (datetime.now() + timedelta(days=days)).date()
                    cursor.execute(
                        """INSERT INTO quiz_schedules (user_id, topic, scheduled_date)
                           VALUES (?, ?, ?)""",
                        (user_id, topic, str(scheduled_date))
                    )
                    conn.commit()
            
            print(f"✨ {username} setup complete!\n")
            
        except Exception as e:
            print(f"❌ Error creating {username}: {str(e)}\n")
            conn.rollback()

def print_test_credentials():
    """Print test user credentials for login"""
    print("\n" + "="*70)
    print("🧪 TEST USER CREDENTIALS")
    print("="*70)
    
    for user_key, user_data in TEST_USERS.items():
        level = "Beginner" if "beginner" in user_key else "Intermediate" if "intermediate" in user_key else "Advanced"
        print(f"\n📊 {level.upper()} USER")
        print(f"   Username: {user_key}")
        print(f"   Email:    {user_data['email']}")
        print(f"   Password: {user_data['password']}")
        print(f"   Learning Style: {user_data['learning_style']}")
        print(f"   Daily Goal: {user_data['daily_goal']} minutes")
        print(f"   Recent Scores: {user_data['scores']}")
        print(f"   Topics: {', '.join(user_data['topics'][:3])}...")
    
    print("\n" + "="*70)
    print("🎯 WHAT TO TEST:")
    print("="*70)
    print("""
1. LOGIN TESTS:
   - Try logging in with each user
   - Verify dashboard shows correct metrics
   
2. DASHBOARD TESTS:
   - Check Total Tests count
   - Verify Average Score is calculated correctly
   - Confirm Best/Worst Topics are shown
   - Check Study Streak calculation
   
3. UPCOMING REVIEWS:
   - Verify schedule shows upcoming reviews
   - Check that spaced repetition dates are visible
   - Test if overdue reviews appear (create some by backdating)
   
4. ADAPTIVE DIFFICULTY:
   - For Beginner: Should recommend "easy"
   - For Intermediate: Should recommend "medium"
   - For Advanced: Should recommend "hard"
   
5. QUIZ GENERATION:
   - Generate a quiz with recommended difficulty
   - Verify difficulty is pre-selected
   - Submit answers and verify:
     • Score is auto-extracted
     • Weak areas are identified
     • Schedule is created
     • Learning level is calculated
   
6. RECOMMENDATIONS:
   - Check that recommendations match performance level
   - Verify personalized tips
    """)
    print("="*70 + "\n")

if __name__ == "__main__":
    print("🚀 Starting test user setup...\n")
    create_test_users()
    print_test_credentials()
    print("✅ Test data setup complete!")
    print("   You can now login with the credentials above")
