from backend.database import get_user_stats, fetch_progress, get_user_preference
from datetime import datetime, timedelta


def get_user_dashboard(user_id):
    """Get comprehensive dashboard data for user"""
    
    stats = get_user_stats(user_id)
    progress = fetch_progress(user_id)
    
    # Calculate metrics
    total_tests = len(progress)
    
    if total_tests == 0:
        avg_score = 0
        best_topic = None
        worst_topic = None
    else:
        scores = [int(p[3]) for p in progress]  # score is index 3
        avg_score = sum(scores) / len(scores)
        
        # Find best and worst topics
        topic_scores = {}
        for p in progress:
            topic = p[2]
            score = int(p[3])
            if topic not in topic_scores:
                topic_scores[topic] = []
            topic_scores[topic].append(score)
        
        best_topic = max(topic_scores, key=lambda t: sum(topic_scores[t]) / len(topic_scores[t]))
        worst_topic = min(topic_scores, key=lambda t: sum(topic_scores[t]) / len(topic_scores[t]))
    
    # Calculate streak
    study_streak = calculate_study_streak(progress)
    
    return {
        "total_tests": total_tests,
        "average_score": round(avg_score, 2),
        "best_topic": best_topic,
        "worst_topic": worst_topic,
        "study_streak": study_streak,
        "topic_breakdown": stats,
        "recent_activity": progress[:5]  # Last 5 activities
    }


def calculate_study_streak(progress):
    """Calculate consecutive days studied"""
    if not progress:
        return 0
    
    dates = set()
    for p in progress:
        # Extract date from timestamp
        timestamp = p[6]  # timestamp is index 6
        if timestamp:
            date = timestamp.split(' ')[0]
            dates.add(date)
    
    # Sort dates
    sorted_dates = sorted(list(dates), reverse=True)
    
    if not sorted_dates:
        return 0
    
    streak = 1
    today = datetime.now().date()
    
    for i, date_str in enumerate(sorted_dates):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        expected_date = today - timedelta(days=i)
        
        if date_obj == expected_date:
            if i > 0:
                streak += 1
        else:
            break
    
    return streak


def get_progress_by_topic(user_id):
    """Get progress breakdown by topic"""
    stats = get_user_stats(user_id)
    
    topics = {}
    for stat in stats:
        topic = stat[0]
        avg_score = stat[1]
        attempts = stat[2]
        
        topics[topic] = {
            "average_score": round(avg_score, 2),
            "total_attempts": attempts,
            "progress_percentage": round((avg_score / 100) * 100, 1)
        }
    
    return topics


def get_learning_recommendations(user_id):
    """Get personalized recommendations based on dashboard performance and preferences"""
    dashboard = get_user_dashboard(user_id)
    progress = fetch_progress(user_id)
    
    # Get user preferences
    pref = get_user_preference(user_id)
    learning_style = pref[2] if pref else "visual"  # learning_style is at index 2
    daily_goal = pref[3] if pref else 60  # daily_study_goal is at index 3
    
    recommendations = {
        "summary": [],
        "performance_insights": [],
        "learning_style_tips": [],
        "weak_area_focus": [],
        "motivational": [],
        "action_items": []
    }
    
    # ===== PERFORMANCE ANALYSIS =====
    avg_score = dashboard["average_score"]
    total_tests = dashboard["total_tests"]
    best_topic = dashboard["best_topic"]
    worst_topic = dashboard["worst_topic"]
    streak = dashboard["study_streak"]
    
    # Performance level assessment
    if avg_score >= 90:
        performance_level = "Outstanding"
        recommendations["summary"].append("🌟 You're performing excellently! Keep maintaining this high standard.")
    elif avg_score >= 80:
        performance_level = "Strong"
        recommendations["summary"].append("👍 You're doing well! You're making solid progress across your studies.")
    elif avg_score >= 70:
        performance_level = "Good"
        recommendations["summary"].append("✅ You're on track! With some focused effort, you can improve further.")
    elif avg_score >= 60:
        performance_level = "Developing"
        recommendations["summary"].append("⚠️ You're making progress, but there's room for improvement.")
    else:
        performance_level = "Needs Attention"
        recommendations["summary"].append("🔴 Your scores suggest you need more focused practice and review.")
    
    # ===== PERFORMANCE INSIGHTS =====
    if avg_score >= 80:
        recommendations["performance_insights"].append(f"Average Score: {avg_score}% - Excellent performance! You're mastering the material.")
    elif avg_score >= 60:
        recommendations["performance_insights"].append(f"Average Score: {avg_score}% - Solid progress. Consider deeper review of fundamentals.")
    else:
        recommendations["performance_insights"].append(f"Average Score: {avg_score}% - Consider slowing down and reviewing core concepts.")
    
    # Best topic insight
    if best_topic:
        best_score = max(
            [s for t, s in [(p[2], int(p[3])) for p in progress] if t == best_topic],
            default=0
        )
        recommendations["performance_insights"].append(f"📈 Strongest Area: {best_topic} ({best_score}%) - You've mastered this topic well!")
    
    # Test volume insight
    if total_tests < 5:
        recommendations["performance_insights"].append(f"📝 You've taken {total_tests} quiz(zes). Taking more assessments helps identify knowledge gaps.")
    elif total_tests < 10:
        recommendations["performance_insights"].append(f"✍️ Good progress: {total_tests} quizzes taken. Continue building your assessment history.")
    else:
        recommendations["performance_insights"].append(f"💪 Impressive effort: {total_tests} quizzes completed! Consistent practice is paying off.")
    
    # Study streak insight
    if streak > 7:
        recommendations["performance_insights"].append(f"🔥 Amazing streak: {streak} days! Your dedication is exceptional.")
    elif streak > 3:
        recommendations["performance_insights"].append(f"🌱 Good streak: {streak} days. Keep up the consistent daily practice!")
    elif streak > 0:
        recommendations["performance_insights"].append(f"📅 Streak: {streak} day(s). Try to extend this into a lasting habit.")
    else:
        recommendations["performance_insights"].append("⏸️ No active streak yet. Start studying today to begin a daily habit!")
    
    # ===== WEAK AREA ANALYSIS & FOCUS =====
    if worst_topic:
        worst_score = min(
            [s for t, s in [(p[2], int(p[3])) for p in progress] if t == worst_topic],
            default=0
        )
        weak_area_diff = best_score - worst_score if best_topic else avg_score - worst_score
        
        recommendations["weak_area_focus"].append(f"🎯 Priority Focus: {worst_topic} ({worst_score}%)")
        recommendations["weak_area_focus"].append(f"   → Focus on this topic to improve your overall performance.")
        recommendations["weak_area_focus"].append(f"   → Score gap between best and worst: {abs(weak_area_diff):.0f}%")
        
        # Get specific weak areas from progress
        weak_areas = [
            p[4] for p in progress if p[2] == worst_topic and p[4] != "None"
        ]
        if weak_areas:
            recommendations["weak_area_focus"].append(f"   → Specific challenges: {', '.join(set(weak_areas))}")
    
    # ===== LEARNING STYLE-SPECIFIC RECOMMENDATIONS =====
    style_tips = {
        "visual": [
            "💡 Visual Learner Tips:",
            "   • Use diagrams and charts when studying concepts",
            "   • Create mind maps to organize information hierarchically",
            "   • Watch video explanations to visualize complex topics",
            "   • Use color-coded notes to highlight key points"
        ],
        "auditory": [
            "💡 Auditory Learner Tips:",
            "   • Discuss topics out loud with peers or study groups",
            "   • Listen to explanatory videos and podcasts",
            "   • Record your understanding and play it back",
            "   • Participate in group discussions and Q&A sessions"
        ],
        "kinesthetic": [
            "💡 Kinesthetic Learner Tips:",
            "   • Practice hands-on problem-solving and coding",
            "   • Work through examples step-by-step",
            "   • Use physical manipulatives and interactive tools",
            "   • Take frequent breaks to apply concepts in practice"
        ]
    }
    
    if learning_style in style_tips:
        recommendations["learning_style_tips"] = style_tips[learning_style]
    
    # ===== DAILY GOAL ALIGNMENT =====
    if daily_goal >= 120:
        recommendations["action_items"].append(f"⏱️ Daily Goal: {daily_goal} min - You've set an ambitious goal! Break it into focused study sessions.")
    elif daily_goal >= 60:
        recommendations["action_items"].append(f"⏱️ Daily Goal: {daily_goal} min - A realistic target for consistent progress.")
    else:
        recommendations["action_items"].append(f"⏱️ Daily Goal: {daily_goal} min - Consider increasing to at least 60 min for better retention.")
    
    # ===== ACTION ITEMS =====
    recommendations["action_items"].append("✓ Next Steps:")
    
    if worst_topic and worst_score < 75:
        recommendations["action_items"].append(f"  1. Schedule a focused review session on {worst_topic}")
    
    if total_tests < 5:
        recommendations["action_items"].append(f"  {2 if worst_topic and worst_score < 75 else 1}. Take 2-3 more quizzes to get a comprehensive performance picture")
    
    if streak == 0:
        step_num = 3 if worst_topic and worst_score < 75 and total_tests < 5 else (2 if worst_topic and worst_score < 75 or total_tests < 5 else 1)
        recommendations["action_items"].append(f"  {step_num}. Study today to start building your streak!")
    else:
        step_num = 3 if worst_topic and worst_score < 75 and total_tests < 5 else (2 if worst_topic and worst_score < 75 or total_tests < 5 else 1)
        recommendations["action_items"].append(f"  {step_num}. Continue your {streak}-day streak by studying today")
    
    # ===== MOTIVATIONAL MESSAGE =====
    if avg_score >= 85:
        recommendations["motivational"].append("🎉 You're a top performer! Your consistent effort is clearly paying off.")
    elif streak > 5:
        recommendations["motivational"].append("🚀 Your dedication to daily studying is admirable and will lead to mastery!")
    elif best_topic and best_score >= 90:
        recommendations["motivational"].append(f"🌟 You've proven you can excel at {best_topic}. Apply that same approach to other areas!")
    elif avg_score >= 70:
        recommendations["motivational"].append("📚 You're on a good learning trajectory. Keep pushing yourself!")
    else:
        recommendations["motivational"].append("💪 Learning takes time. Focus on understanding one concept at a time, and improvement will follow.")
    
    return recommendations


def get_weekly_progress(user_id, weeks=4):
    """Get progress data for the last N weeks"""
    progress = fetch_progress(user_id)
    
    weekly_data = {}
    for p in progress:
        # Extract timestamp
        timestamp = p[6]
        if timestamp:
            date_obj = datetime.strptime(timestamp.split()[0], "%Y-%m-%d")
            week_key = date_obj.strftime("%Y-W%U")
            
            if week_key not in weekly_data:
                weekly_data[week_key] = []
            
            weekly_data[week_key].append(int(p[3]))  # score
    
    # Calculate weekly averages
    weekly_averages = {
        week: round(sum(scores) / len(scores), 2)
        for week, scores in weekly_data.items()
    }
    
    return weekly_averages
