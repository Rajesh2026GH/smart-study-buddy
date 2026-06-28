import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from backend.pdf_reader import extract_text_from_pdf

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Smart Study Buddy",
    page_icon="🎓",
    layout="wide"
)

# ============ SESSION STATE INITIALIZATION ============
if "access_token" not in st.session_state:
    st.session_state.access_token = None
    st.session_state.user_id = None
    st.session_state.username = None

API_BASE_URL = "http://127.0.0.1:8000"

def get_headers():
    """Get authorization headers"""
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}

# ============ AUTHENTICATION SECTION ============
def show_auth_page():
    """Show login/signup page"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/auth/login",
                    json={"username": login_username, "password": login_password}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.access_token = data["access_token"]
                    st.session_state.user_id = data["user_id"]
                    st.session_state.username = data["username"]
                    st.success(f"Welcome back, {data['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Login failed: {str(e)}")
    
    with col2:
        st.subheader("Sign Up")
        signup_username = st.text_input("Username", key="signup_username")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        
        if st.button("Sign Up"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/auth/signup",
                    json={"username": signup_username, "email": signup_email, "password": signup_password}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.access_token = data["access_token"]
                    st.session_state.user_id = data["user_id"]
                    st.session_state.username = data["username"]
                    st.success(f"Account created! Welcome, {data['username']}!")
                    st.rerun()
                else:
                    st.error("Sign up failed")
            except Exception as e:
                st.error(f"Sign up failed: {str(e)}")

# ============ MAIN APPLICATION ============
def show_main_app():
    """Show main application after login"""
    
    # Header with user info
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("Smart Study Buddy 🎓")
    with col2:
        if st.button("Logout"):
            st.session_state.access_token = None
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
    
    st.write(f"Welcome, **{st.session_state.username}**!")
    
    # Create tabs for different features
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📚 Study",
        "📊 Dashboard",
        "👥 Groups",
        "⚙️ Preferences",
        "🔗 Platforms",
        "📈 Analytics",
        "💡 Recommendations"
    ])
    
    # ============ STUDY TAB ============
    with tab1:
        st.header("📚 Study Materials")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Upload Study Material")
            uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
            pdf_text = ""
            
            if uploaded_file:
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("PDF Uploaded Successfully")
                pdf_text = extract_text_from_pdf(uploaded_file.name)
                st.write(f"Extracted: {len(pdf_text)} characters")
        
        with col2:
            st.subheader("Or Enter Text")
            pdf_text = st.text_area("Paste learning material here", height=200)
        
        if pdf_text:
            # Concept Extraction
            st.subheader("🔍 Extract Key Concepts")
            if st.button("Extract Concepts"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/extract-concepts",
                        json={"text": pdf_text[:3000]},
                        headers=get_headers()
                    )
                    if response.status_code == 200:
                        st.success("Concepts extracted:")
                        st.write(response.json()["concepts"])
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            # Quiz Generation
            st.subheader("🎯 Generate Quiz")
            
            # Get recommended difficulty
            recommended = "medium"
            last_score = None
            level = ""
            try:
                rec_response = requests.get(
                    f"{API_BASE_URL}/recommended-difficulty",
                    headers=get_headers()
                )
                if rec_response.status_code == 200:
                    rec_data = rec_response.json()
                    recommended = rec_data.get("difficulty", "medium")
                    last_score = rec_data.get("last_score")
                    level = rec_data.get("level", "")
            except:
                pass
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Show recommended difficulty with visual emphasis
                if last_score is not None:
                    st.markdown(f"**Last Score:** {last_score}/100 | **Level:** {level}")
                
                # Pre-select recommended difficulty
                difficulty_options = ["easy", "medium", "hard"]
                default_index = difficulty_options.index(recommended) if recommended in difficulty_options else 1
                
                difficulty = st.select_slider(
                    "Difficulty",
                    difficulty_options,
                    value=recommended,  # ← Pre-selected
                    help=f"Recommended based on your recent performance"
                )
            
            with col2:
                learning_style = st.selectbox("Learning Style", ["visual", "auditory", "kinesthetic"])
            
            if st.button("Generate Quiz"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/generate-quiz",
                        json={
                            "text": pdf_text[:3000],
                            "difficulty": difficulty,
                            "learning_style": learning_style
                        },
                        headers=get_headers()
                    )
                    if response.status_code == 200:
                        quiz_data = response.json()["quiz"]
                        st.session_state["quiz"] = quiz_data
                        st.success("Quiz generated!")
                        st.write(quiz_data)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            # Topic Explainer
            st.subheader("💡 Explain a Topic")
            topic = st.text_input("Enter topic to explain")
            explain_style = st.selectbox("Explanation Style", ["visual", "auditory", "kinesthetic"])
            multiple_styles = st.checkbox("Show all learning styles")
            
            if st.button("Get Explanation"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/explain",
                        json={
                            "topic": topic,
                            "learning_style": explain_style,
                            "multiple_styles": multiple_styles
                        },
                        headers=get_headers()
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if "explanations" in data:
                            for style, explanation in data["explanations"].items():
                                st.write(f"**{style.upper()}:**")
                                st.write(explanation)
                        else:
                            st.write(data["explanation"])
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            # Answer Evaluation
            if "quiz" in st.session_state:
                st.subheader("✅ Quiz Evaluation")
                user_answers = st.text_area("Enter Your Answers")
                topic = st.text_input("Topic")
                
                if st.button("Evaluate Answers"):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/evaluate",
                            json={
                                "user_id": st.session_state.user_id,
                                "topic": topic,
                                "quiz": st.session_state["quiz"],
                                "user_answers": user_answers,
                                "score": 0,  # Placeholder - auto-calculated by backend
                                "weak_area": ""  # Placeholder - auto-extracted by backend
                            },
                            headers=get_headers()
                        )
                        if response.status_code == 200:
                            data = response.json()
                            
                            if "error" in data:
                                st.error(f"Evaluation Error: {data['error']}")
                            else:
                                st.success("Evaluation Complete!")
                                
                                # Display auto-extracted score prominently
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Your Score", f"{data['score']}/100")
                                with col2:
                                    st.metric("Correct Answers", data['correct_answers'])
                                with col3:
                                    st.metric("Incorrect Answers", data['incorrect_answers'])
                                
                                # Display progress bar
                                st.progress(data['score'] / 100)
                                
                                # Display feedback
                                st.subheader("📝 Feedback")
                                st.write(data["evaluation"])
                                
                                # Display weak areas (auto-extracted)
                                if data.get('weak_areas'):
                                    st.warning(f"**Areas to Improve:** {', '.join(data['weak_areas'])}")
                                
                                # Display question-by-question feedback
                                if data.get('question_feedback'):
                                    st.subheader("📋 Question Breakdown")
                                    for qf in data['question_feedback']:
                                        if qf['correct']:
                                            st.success(f"✓ Q{qf['question_num']}: {qf['explanation']}")
                                        else:
                                            st.error(f"✗ Q{qf['question_num']}: {qf['explanation']}")
                                
                                # Display level and recommendation
                                st.info(f"**Learning Level:** {data['learning_level']}")
                                st.info(f"**Recommendation:** {data['recommendation']}")
                                
                                # Display schedule
                                st.subheader("📅 Spaced Repetition Schedule")
                                for item in data["schedule"]:
                                    st.write(f"- **{item.get('topic', 'Review')}** → {item.get('revision_date', 'TBD')}")
                                
                                st.session_state["last_evaluation"] = data
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # ============ DASHBOARD TAB ============
    with tab2:
        st.header("📊 Your Dashboard")
        try:
            response = requests.get(
                f"{API_BASE_URL}/dashboard",
                headers=get_headers()
            )
            if response.status_code == 200:
                dashboard = response.json()
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Tests", dashboard["total_tests"])
                col2.metric("Average Score", f"{dashboard['average_score']}%")
                col3.metric("Study Streak", f"{dashboard['study_streak']} days")
                col4.metric("Best Topic", dashboard["best_topic"] or "N/A")
                
                st.subheader("📅 Upcoming Reviews")
                try:
                    schedule_response = requests.get(
                        f"{API_BASE_URL}/schedule/upcoming",
                        headers=get_headers()
                    )
                    if schedule_response.status_code == 200:
                        schedule_data = schedule_response.json()
                        
                        if schedule_data["overdue"]:
                            st.warning(f"⚠️ You have {len(schedule_data['overdue'])} overdue reviews!")
                            for item in schedule_data["overdue"]:
                                col1, col2, col3 = st.columns([2, 1, 1])
                                with col1:
                                    st.write(f"📌 {item['topic']}")
                                with col2:
                                    st.write(f"⏰ {item['overdue_days']} days overdue")
                                with col3:
                                    if st.button("Start", key=f"overdue_{item['id']}"):
                                        st.session_state["review_topic"] = item['topic']
                                        st.write(f"Starting review of {item['topic']}...")
                        
                        if schedule_data["upcoming"]:
                            st.info(f"✅ You have {len(schedule_data['upcoming'])} upcoming reviews")
                            for item in schedule_data["upcoming"]:
                                col1, col2, col3 = st.columns([2, 1, 1])
                                with col1:
                                    st.write(f"📌 {item['topic']}")
                                with col2:
                                    st.write(f"📅 {item['date']}")
                                with col3:
                                    if st.button("Review", key=f"upcoming_{item['id']}"):
                                        st.session_state["review_topic"] = item['topic']
                        else:
                            st.success("No upcoming reviews scheduled!")
                            
                except Exception as e:
                    st.error(f"Error loading schedule: {str(e)}")
                
                st.subheader("Recent Activity")
                if dashboard["recent_activity"]:
                    recent_df = pd.DataFrame(dashboard["recent_activity"])
                    st.dataframe(recent_df)
        except Exception as e:
            st.error(f"Error loading dashboard: {str(e)}")
    
    # ============ STUDY GROUPS TAB ============
    with tab3:
        st.header("👥 Study Groups")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Create New Group")
            group_name = st.text_input("Group Name")
            group_desc = st.text_area("Description")
            
            if st.button("Create Group"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/groups/create",
                        json={"group_name": group_name, "description": group_desc},
                        headers=get_headers()
                    )
                    if response.status_code == 200:
                        st.success(response.json()["message"])
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            st.subheader("Your Groups")
            try:
                response = requests.get(
                    f"{API_BASE_URL}/groups",
                    headers=get_headers()
                )
                if response.status_code == 200:
                    groups = response.json()["groups"]
                    for group in groups:
                        st.write(f"📌 **{group[1]}**")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.subheader("Share Notes with Group")
        selected_group = st.number_input("Group ID", min_value=1)
        note_title = st.text_input("Note Title")
        note_content = st.text_area("Note Content")
        
        if st.button("Share Note"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/groups/{selected_group}/notes",
                    json={"title": note_title, "content": note_content},
                    headers=get_headers()
                )
                if response.status_code == 200:
                    st.success("Note shared successfully!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # ============ PREFERENCES TAB ============
    with tab4:
        st.header("⚙️ Learning Preferences")
        
        learning_style = st.selectbox("Preferred Learning Style", ["visual", "auditory", "kinesthetic"])
        daily_goal = st.slider("Daily Study Goal (minutes)", 15, 300, 60)
        notifications = st.checkbox("Enable Notifications", True)
        
        if st.button("Save Preferences"):
            try:
                response = requests.put(
                    f"{API_BASE_URL}/preferences",
                    json={
                        "learning_style": learning_style,
                        "daily_study_goal": daily_goal,
                        "notification_enabled": notifications
                    },
                    headers=get_headers()
                )
                if response.status_code == 200:
                    st.success("Preferences updated!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # ============ PLATFORMS TAB ============
    with tab5:
        st.header("🔗 Platform Integrations")
        
        st.write("Connect with popular learning platforms:")
        platform = st.selectbox("Select Platform", ["coursera", "khan_academy", "udemy", "edx"])
        api_token = st.text_input("API Token", type="password")
        
        if st.button("Connect Platform"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/platforms/connect",
                    json={"platform_name": platform, "api_token": api_token},
                    headers=get_headers()
                )
                if response.status_code == 200:
                    st.success(response.json()["message"])
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.subheader("Connected Platforms")
        try:
            response = requests.get(
                f"{API_BASE_URL}/platforms",
                headers=get_headers()
            )
            if response.status_code == 200:
                platforms = response.json()["connected_platforms"]
                if platforms:
                    for p in platforms:
                        st.write(f"✅ {p[2]}")
                else:
                    st.info("No platforms connected yet")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # ============ ANALYTICS TAB ============
    with tab6:
        st.header("📈 Advanced Analytics")
        
        try:
            # Topic breakdown
            response = requests.get(
                f"{API_BASE_URL}/stats/by-topic",
                headers=get_headers()
            )
            if response.status_code == 200:
                topics = response.json()["topic_stats"]
                if topics:
                    st.subheader("Performance by Topic")
                    topic_data = pd.DataFrame(topics).T
                    st.bar_chart(topic_data["average_score"])
            
            # Weekly progress
            response = requests.get(
                f"{API_BASE_URL}/weekly-progress",
                headers=get_headers()
            )
            if response.status_code == 200:
                weekly = response.json()["weekly_progress"]
                if weekly:
                    st.subheader("Weekly Progress Trend")
                    st.line_chart(weekly)
        except Exception as e:
            st.error(f"Error loading analytics: {str(e)}")
    
    # ============ RECOMMENDATIONS TAB ============
    with tab7:
        st.header("💡 Personalized Recommendations")
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/recommendations",
                headers=get_headers()
            )
            if response.status_code == 200:
                recommendations = response.json()["recommendations"]
                if recommendations:
                    # Summary Section
                    if recommendations.get("summary"):
                        with st.container():
                            st.subheader("📌 Summary")
                            for item in recommendations["summary"]:
                                st.info(item)
                    
                    # Performance Insights Section
                    if recommendations.get("performance_insights"):
                        st.subheader("📊 Performance Insights")
                        for item in recommendations["performance_insights"]:
                            st.write(f"• {item}")
                    
                    # Learning Style Tips Section
                    if recommendations.get("learning_style_tips"):
                        st.subheader("💡 Learning Style Tips")
                        for item in recommendations["learning_style_tips"]:
                            st.write(item)
                    
                    # Weak Area Focus Section
                    if recommendations.get("weak_area_focus"):
                        st.subheader("🎯 Weak Area Focus")
                        for item in recommendations["weak_area_focus"]:
                            st.warning(item)
                    
                    # Action Items Section
                    if recommendations.get("action_items"):
                        st.subheader("✅ Action Items")
                        for item in recommendations["action_items"]:
                            st.write(f"→ {item}")
                    
                    # Motivational Section
                    if recommendations.get("motivational"):
                        st.subheader("🌟 Motivational Message")
                        for item in recommendations["motivational"]:
                            st.success(item)
                else:
                    st.success("Keep up the great work! You're on track!")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ============ MAIN ============
if __name__ == "__main__":
    if st.session_state.access_token is None:
        show_auth_page()
    else:
        show_main_app()
