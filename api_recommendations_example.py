#!/usr/bin/env python3
"""
API Integration example showing how to get alice_smith's personalized recommendations
"""

from fastapi.testclient import TestClient
from backend import api
import json

client = TestClient(api.app)


def get_alice_recommendations_via_api():
    """
    Demonstrates how to get personalized recommendations for alice_smith
    through the REST API
    """
    
    print("=" * 80)
    print("🎓 PERSONALIZED RECOMMENDATIONS VIA API")
    print("=" * 80)
    print()
    
    # Step 1: Login as alice_smith
    print("🔐 Step 1: Authenticating alice_smith...")
    login_response = client.post(
        "/auth/login",
        json={
            "username": "alice_smith",
            "password": "Alice123!"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.json()}")
        return
    
    login_data = login_response.json()
    token = login_data["access_token"]
    user_id = login_data["user_id"]
    
    print(f"✅ Logged in successfully!")
    print(f"   User ID: {user_id}")
    print(f"   Token: {token[:30]}...")
    print()
    
    # Step 2: Get dashboard
    print("📊 Step 2: Fetching dashboard metrics...")
    headers = {"Authorization": f"Bearer {token}"}
    dashboard_response = client.get("/dashboard", headers=headers)
    
    if dashboard_response.status_code == 200:
        dashboard = dashboard_response.json()
        print(f"✅ Dashboard retrieved!")
        print(f"   Total Tests: {dashboard['total_tests']}")
        print(f"   Average Score: {dashboard['average_score']}%")
        print(f"   Best Topic: {dashboard['best_topic']}")
        print(f"   Study Streak: {dashboard['study_streak']} days")
        print()
    else:
        print(f"❌ Dashboard retrieval failed: {dashboard_response.json()}")
        return
    
    # Step 3: Get preferences
    print("⚙️ Step 3: Fetching user preferences...")
    pref_response = client.get("/preferences", headers=headers)
    
    if pref_response.status_code == 200:
        prefs = pref_response.json()
        print(f"✅ Preferences retrieved!")
        print(f"   Learning Style: {prefs['learning_style']}")
        print(f"   Daily Goal: {prefs['daily_study_goal']} minutes")
        print()
    else:
        print(f"❌ Preferences retrieval failed: {pref_response.json()}")
        return
    
    # Step 4: Get personalized recommendations
    print("🎯 Step 4: Fetching personalized recommendations...")
    recs_response = client.get("/recommendations", headers=headers)
    
    if recs_response.status_code != 200:
        print(f"❌ Recommendations retrieval failed: {recs_response.json()}")
        return
    
    print(f"✅ Personalized recommendations retrieved!")
    print()
    
    recs = recs_response.json()["recommendations"]
    
    # Display recommendations
    print("=" * 80)
    print("📌 PERSONALIZED RECOMMENDATIONS FOR ALICE_SMITH")
    print("=" * 80)
    print()
    
    # Summary
    print("🎯 SUMMARY")
    for item in recs.get("summary", []):
        print(f"   {item}")
    print()
    
    # Performance Insights
    print("📊 PERFORMANCE INSIGHTS")
    for item in recs.get("performance_insights", []):
        print(f"   {item}")
    print()
    
    # Learning Style Tips
    print("💡 LEARNING STYLE RECOMMENDATIONS (VISUAL LEARNER)")
    for item in recs.get("learning_style_tips", []):
        print(f"   {item}")
    print()
    
    # Weak Area Focus
    if recs.get("weak_area_focus"):
        print("🎯 WEAK AREA FOCUS")
        for item in recs.get("weak_area_focus", []):
            print(f"   {item}")
        print()
    
    # Action Items
    print("✅ ACTION ITEMS")
    for item in recs.get("action_items", []):
        print(f"   {item}")
    print()
    
    # Motivational
    print("🌟 MOTIVATIONAL MESSAGE")
    for item in recs.get("motivational", []):
        print(f"   {item}")
    print()
    
    # Show raw JSON
    print("=" * 80)
    print("📤 RAW API RESPONSE (JSON)")
    print("=" * 80)
    print(json.dumps(recs, indent=2))
    print()


def show_api_usage():
    """Show the API usage pattern"""
    print()
    print("=" * 80)
    print("📚 API USAGE DOCUMENTATION")
    print("=" * 80)
    print()
    print("Endpoint: GET /recommendations")
    print()
    print("Authentication: Required (Bearer Token)")
    print()
    print("Request Example:")
    print("-" * 80)
    print("""
curl -X GET "http://localhost:8000/recommendations" \\
  -H "Authorization: Bearer <your_token>"
    """)
    print("-" * 80)
    print()
    print("Response Format:")
    print("-" * 80)
    print("""
{
  "recommendations": {
    "summary": [string],                    // Overall performance assessment
    "performance_insights": [string],       // Score analysis, streak, volume
    "learning_style_tips": [string],        // Customized learning tips
    "weak_area_focus": [string],            // Topics needing improvement
    "action_items": [string],               // Prioritized next steps
    "motivational": [string]                // Personalized encouragement
  }
}
    """)
    print("-" * 80)
    print()
    print("Features:")
    print("  ✨ Personalized by learning style (visual/auditory/kinesthetic)")
    print("  ✨ Performance-aware recommendations")
    print("  ✨ Topic-specific improvement suggestions")
    print("  ✨ Study streak and consistency tracking")
    print("  ✨ Motivational, growth-oriented messaging")
    print()


if __name__ == "__main__":
    get_alice_recommendations_via_api()
    show_api_usage()
