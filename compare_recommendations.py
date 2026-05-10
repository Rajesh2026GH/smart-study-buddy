#!/usr/bin/env python3
"""
Comparison script showing personalized recommendations for multiple seeded users
"""

from backend.database import get_user_by_username, get_user_preference
from backend.analytics import get_user_dashboard, get_learning_recommendations
import json


def display_user_recommendations(username):
    """Display personalized recommendations for a user"""
    
    # Get user
    user = get_user_by_username(username)
    if not user:
        print(f"❌ {username} not found.")
        return None
    
    user_id = user[0]
    
    # Get preferences
    pref = get_user_preference(user_id)
    learning_style = pref[2] if pref else "visual"
    daily_goal = pref[3] if pref else 60
    
    # Get dashboard
    dashboard = get_user_dashboard(user_id)
    
    # Get recommendations
    recommendations = get_learning_recommendations(user_id)
    
    return {
        "user_id": user_id,
        "username": username,
        "learning_style": learning_style,
        "daily_goal": daily_goal,
        "dashboard": dashboard,
        "recommendations": recommendations
    }


def main():
    """Display and compare recommendations for seeded users"""
    
    print("=" * 80)
    print("🎓 SMART STUDY BUDDY - PERSONALIZED RECOMMENDATIONS COMPARISON")
    print("=" * 80)
    print()
    
    users_to_compare = ["alice_smith", "bob_johnson"]
    user_data = []
    
    for username in users_to_compare:
        data = display_user_recommendations(username)
        if data:
            user_data.append(data)
    
    if not user_data:
        print("❌ No seeded users found. Please run seed_data.py first.")
        return
    
    # Display detailed comparison
    for i, data in enumerate(user_data, 1):
        print(f"\n{'=' * 80}")
        print(f"USER {i}: {data['username'].upper()}")
        print(f"{'=' * 80}\n")
        
        print(f"👤 Profile & Preferences")
        print(f"   Learning Style: {data['learning_style'].upper()}")
        print(f"   Daily Goal: {data['daily_goal']} minutes")
        print()
        
        print(f"📊 Performance Dashboard")
        dashboard = data['dashboard']
        print(f"   Total Quizzes: {dashboard['total_tests']}")
        print(f"   Average Score: {dashboard['average_score']}%")
        print(f"   Best Topic: {dashboard['best_topic'] or 'N/A'}")
        print(f"   Weakest Topic: {dashboard['worst_topic'] or 'N/A'}")
        print(f"   Study Streak: {dashboard['study_streak']} day(s)")
        print()
        
        recs = data['recommendations']
        
        print(f"🎯 Key Recommendations")
        if recs['summary']:
            print(f"   • {recs['summary'][0]}")
        if recs['performance_insights']:
            print(f"   • {recs['performance_insights'][0]}")
        if recs['weak_area_focus']:
            print(f"   • {recs['weak_area_focus'][0]}")
        print()
        
        print(f"💡 Learning Style Tips")
        if recs['learning_style_tips']:
            for tip in recs['learning_style_tips'][:2]:  # Show first 2 tips
                print(f"   {tip}")
        print()
        
        print(f"✅ Action Items")
        if recs['action_items']:
            for action in recs['action_items'][:3]:  # Show first 3 actions
                print(f"   {action}")
    
    print(f"\n{'=' * 80}")
    print("📊 COMPARISON SUMMARY")
    print(f"{'=' * 80}\n")
    
    # Create comparison table
    print(f"{'Metric':<30} {'alice_smith':<25} {'bob_johnson':<25}")
    print("-" * 80)
    
    for i, data in enumerate(user_data):
        if i == 0:
            print(f"{'Learning Style':<30} {data['learning_style']:<25} {user_data[1]['learning_style']:<25}")
            print(f"{'Daily Goal':<30} {str(data['daily_goal']) + ' min':<25} {str(user_data[1]['daily_goal']) + ' min':<25}")
            print(f"{'Total Quizzes':<30} {str(data['dashboard']['total_tests']):<25} {str(user_data[1]['dashboard']['total_tests']):<25}")
            print(f"{'Average Score':<30} {str(data['dashboard']['average_score']) + '%':<25} {str(user_data[1]['dashboard']['average_score']) + '%':<25}")
            print(f"{'Best Topic':<30} {str(data['dashboard']['best_topic']):<25} {str(user_data[1]['dashboard']['best_topic']):<25}")
            print(f"{'Study Streak':<30} {str(data['dashboard']['study_streak']) + ' day(s)':<25} {str(user_data[1]['dashboard']['study_streak']) + ' day(s)':<25}")
    
    print()
    print("✨ Each user receives recommendations tailored to their:")
    print("   ✓ Learning style (visual, auditory, kinesthetic)")
    print("   ✓ Current performance level")
    print("   ✓ Weak areas and topics needing focus")
    print("   ✓ Study habits and streak patterns")
    print("   ✓ Daily study goals")
    print()


if __name__ == "__main__":
    main()
