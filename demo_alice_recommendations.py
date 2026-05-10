#!/usr/bin/env python3
"""
Demo script showing alice_smith's personalized recommendations
based on her dashboard performance
"""

from backend.database import get_user_by_username, get_user_preference
from backend.analytics import get_user_dashboard, get_learning_recommendations, get_progress_by_topic
import json


def demo_alice_recommendations():
    """Display alice_smith's comprehensive personalized recommendations"""
    
    print("=" * 70)
    print("🎓 SMART STUDY BUDDY - PERSONALIZED RECOMMENDATIONS")
    print("=" * 70)
    print()
    
    # Get alice_smith's user ID
    alice = get_user_by_username("alice_smith")
    if not alice:
        print("❌ alice_smith not found. Please run seed_data.py first.")
        return
    
    user_id = alice[0]
    username = alice[1]
    email = alice[2]
    
    print(f"👤 User Profile")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print()
    
    # Get user preferences
    pref = get_user_preference(user_id)
    if pref:
        learning_style = pref[2]
        daily_goal = pref[3]
        notifications = "Enabled" if pref[4] else "Disabled"
        print(f"⚙️ Learning Preferences")
        print(f"   Learning Style: {learning_style}")
        print(f"   Daily Study Goal: {daily_goal} minutes")
        print(f"   Notifications: {notifications}")
        print()
    
    # Get dashboard metrics
    dashboard = get_user_dashboard(user_id)
    print(f"📊 Dashboard Metrics")
    print(f"   Total Quizzes Taken: {dashboard['total_tests']}")
    print(f"   Average Score: {dashboard['average_score']}%")
    print(f"   Best Topic: {dashboard['best_topic']}")
    print(f"   Weakest Topic: {dashboard['worst_topic']}")
    print(f"   Study Streak: {dashboard['study_streak']} day(s)")
    print()
    
    # Get topic breakdown
    topic_stats = get_progress_by_topic(user_id)
    print(f"📈 Performance by Topic")
    for topic, stats in topic_stats.items():
        print(f"   • {topic}")
        print(f"      Average Score: {stats['average_score']}%")
        print(f"      Attempts: {stats['total_attempts']}")
    print()
    
    # Get personalized recommendations
    recommendations = get_learning_recommendations(user_id)
    
    print("=" * 70)
    print("🎯 PERSONALIZED RECOMMENDATIONS FOR ALICE")
    print("=" * 70)
    print()
    
    # Summary
    if recommendations["summary"]:
        print("📌 SUMMARY")
        for item in recommendations["summary"]:
            print(f"   {item}")
        print()
    
    # Performance Insights
    if recommendations["performance_insights"]:
        print("📊 PERFORMANCE INSIGHTS")
        for item in recommendations["performance_insights"]:
            print(f"   {item}")
        print()
    
    # Weak Area Focus
    if recommendations["weak_area_focus"]:
        print("🎯 WEAK AREA FOCUS")
        for item in recommendations["weak_area_focus"]:
            print(f"   {item}")
        print()
    
    # Learning Style Tips
    if recommendations["learning_style_tips"]:
        print("💡 LEARNING STYLE RECOMMENDATIONS")
        for item in recommendations["learning_style_tips"]:
            print(f"   {item}")
        print()
    
    # Action Items
    if recommendations["action_items"]:
        print("✅ ACTION ITEMS")
        for item in recommendations["action_items"]:
            print(f"   {item}")
        print()
    
    # Motivational Message
    if recommendations["motivational"]:
        print("🌟 MOTIVATIONAL MESSAGE")
        for item in recommendations["motivational"]:
            print(f"   {item}")
        print()
    
    print("=" * 70)
    print("💾 Recommendation Data (JSON)")
    print("=" * 70)
    print(json.dumps(recommendations, indent=2))
    print()


if __name__ == "__main__":
    demo_alice_recommendations()
