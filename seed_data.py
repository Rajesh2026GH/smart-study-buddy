#!/usr/bin/env python3
"""
Sample Data Seeding Script for Smart Study Buddy
Creates sample users for testing and demonstration purposes
"""

from backend.database import (
    create_user, set_user_preference, save_progress,
    create_study_group, add_member_to_group
)
from backend.auth import hash_password


def seed_sample_users():
    """Create sample users with test data"""
    
    print("🌱 Creating sample users...")
    
    # Sample users with credentials
    sample_users = [
        {
            "username": "alice_smith",
            "email": "alice@studybuddy.com",
            "password": "Alice123!",
            "learning_style": "visual",
            "daily_goal": 90
        },
        {
            "username": "bob_johnson",
            "email": "bob@studybuddy.com",
            "password": "Bob456!",
            "learning_style": "auditory",
            "daily_goal": 60
        },
        {
            "username": "charlie_davis",
            "email": "charlie@studybuddy.com",
            "password": "Charlie789!",
            "learning_style": "kinesthetic",
            "daily_goal": 120
        },
        {
            "username": "diana_wilson",
            "email": "diana@studybuddy.com",
            "password": "Diana321!",
            "learning_style": "visual",
            "daily_goal": 75
        },
        {
            "username": "evan_martinez",
            "email": "evan@studybuddy.com",
            "password": "Evan654!",
            "learning_style": "auditory",
            "daily_goal": 45
        }
    ]
    
    user_ids = []
    
    for user_data in sample_users:
        try:
            # Create user
            hashed_pwd = hash_password(user_data["password"])
            user_id = create_user(
                user_data["username"],
                user_data["email"],
                hashed_pwd
            )
            user_ids.append(user_id)
            
            # Set preferences
            set_user_preference(
                user_id,
                user_data["learning_style"],
                user_data["daily_goal"],
                True
            )
            
            print(f"✅ Created user: {user_data['username']} (ID: {user_id})")
            print(f"   📧 Email: {user_data['email']}")
            print(f"   🎨 Learning Style: {user_data['learning_style']}")
            print(f"   ⏰ Daily Goal: {user_data['daily_goal']} minutes")
            print()
            
        except Exception as e:
            print(f"❌ Error creating user {user_data['username']}: {str(e)}")
    
    return user_ids


def seed_sample_progress(user_ids):
    """Create sample progress data for demonstration"""
    
    print("\n📊 Creating sample progress data...")
    
    sample_progress = [
        {"user_id": user_ids[0], "topic": "Python Basics", "score": 85, "weak_area": "Recursion", "level": "Intermediate"},
        {"user_id": user_ids[0], "topic": "Data Structures", "score": 92, "weak_area": "None", "level": "Advanced"},
        {"user_id": user_ids[0], "topic": "Algorithms", "score": 78, "weak_area": "Sorting", "level": "Intermediate"},
        
        {"user_id": user_ids[1], "topic": "Web Development", "score": 88, "weak_area": "CSS", "level": "Advanced"},
        {"user_id": user_ids[1], "topic": "JavaScript", "score": 75, "weak_area": "Async/Await", "level": "Intermediate"},
        {"user_id": user_ids[1], "topic": "React", "score": 82, "weak_area": "Hooks", "level": "Intermediate"},
        
        {"user_id": user_ids[2], "topic": "Machine Learning", "score": 91, "weak_area": "None", "level": "Advanced"},
        {"user_id": user_ids[2], "topic": "Deep Learning", "score": 87, "weak_area": "CNN Architecture", "level": "Advanced"},
        {"user_id": user_ids[2], "topic": "Statistics", "score": 79, "weak_area": "Probability", "level": "Intermediate"},
        
        {"user_id": user_ids[3], "topic": "Mathematics", "score": 90, "weak_area": "None", "level": "Advanced"},
        {"user_id": user_ids[3], "topic": "Calculus", "score": 84, "weak_area": "Integration", "level": "Intermediate"},
        
        {"user_id": user_ids[4], "topic": "Physics", "score": 76, "weak_area": "Quantum Mechanics", "level": "Intermediate"},
        {"user_id": user_ids[4], "topic": "Thermodynamics", "score": 72, "weak_area": "Entropy", "level": "Beginner"},
    ]
    
    for progress in sample_progress:
        try:
            save_progress(
                progress["user_id"],
                progress["topic"],
                progress["score"],
                progress["weak_area"],
                progress["level"]
            )
            print(f"✅ Added: {progress['topic']} (Score: {progress['score']}%) for User ID {progress['user_id']}")
        except Exception as e:
            print(f"❌ Error adding progress: {str(e)}")


def seed_study_groups(user_ids):
    """Create sample study groups for collaboration"""
    
    print("\n👥 Creating sample study groups...")
    
    sample_groups = [
        {
            "name": "Python Masters",
            "creator": user_ids[0],
            "description": "Advanced Python programming and data structures",
            "members": [user_ids[0], user_ids[1], user_ids[2]]
        },
        {
            "name": "Web Dev Crew",
            "creator": user_ids[1],
            "description": "Frontend and backend web development",
            "members": [user_ids[1], user_ids[0]]
        },
        {
            "name": "ML Study Group",
            "creator": user_ids[2],
            "description": "Machine Learning and AI fundamentals",
            "members": [user_ids[2], user_ids[3], user_ids[4]]
        },
        {
            "name": "STEM Scholars",
            "creator": user_ids[3],
            "description": "Science, Technology, Engineering, and Mathematics",
            "members": [user_ids[3], user_ids[4]]
        }
    ]
    
    for group in sample_groups:
        try:
            group_id = create_study_group(
                group["name"],
                group["creator"],
                group["description"]
            )
            
            # Add members to group
            for member_id in group["members"]:
                if member_id != group["creator"]:  # Creator already added
                    add_member_to_group(group_id, member_id)
            
            print(f"✅ Created group: {group['name']} (ID: {group_id})")
            print(f"   📝 Description: {group['description']}")
            print(f"   👥 Members: {len(group['members'])}")
            print()
            
        except Exception as e:
            print(f"❌ Error creating group {group['name']}: {str(e)}")


def main():
    """Main seeding function"""
    
    print("=" * 60)
    print("🌱 Smart Study Buddy - Sample Data Seeding")
    print("=" * 60)
    print()
    
    try:
        # Create sample users
        user_ids = seed_sample_users()
        
        if user_ids:
            # Create sample progress data
            seed_sample_progress(user_ids)
            
            # Create sample study groups
            seed_study_groups(user_ids)
            
            print("\n" + "=" * 60)
            print("✅ Sample data seeding completed successfully!")
            print("=" * 60)
            print()
            print("📝 Sample User Credentials for Testing:")
            print("-" * 60)
            
            sample_users = [
                ("alice_smith", "Alice123!"),
                ("bob_johnson", "Bob456!"),
                ("charlie_davis", "Charlie789!"),
                ("diana_wilson", "Diana321!"),
                ("evan_martinez", "Evan654!")
            ]
            
            for username, password in sample_users:
                print(f"  Username: {username}")
                print(f"  Password: {password}")
                print()
            
            print("-" * 60)
            print("🚀 You can now login with any of these accounts!")
            print("=" * 60)
        else:
            print("❌ Failed to create sample users")
    
    except Exception as e:
        print(f"❌ Seeding failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
