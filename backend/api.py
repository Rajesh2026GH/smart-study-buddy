from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from backend.quiz_generator import generate_quiz, generate_varied_quizzes
from backend.explainer import explain_topic, explain_with_multiple_styles
from backend.concept_extractor import extract_concepts
from backend.evaluator import evaluate_answers
from backend.database import (
    save_progress, fetch_progress, create_user, get_user_by_username,
    get_user_preference, set_user_preference, get_user_stats,
    create_study_group, add_member_to_group, get_user_groups, get_group_notes
)
from backend.adaptive_learning import get_learning_level, get_recommendation
from backend.scheduler import generate_personalized_schedule
from backend.auth import hash_password, verify_password, create_access_token, verify_token
from backend.collaboration import create_new_group, invite_member, get_my_groups, share_note, get_group_info
from backend.platform_integration import PlatformIntegration
from backend.analytics import get_user_dashboard, get_progress_by_topic, get_learning_recommendations, get_weekly_progress

app = FastAPI()

# ============ REQUEST MODELS ============

class QuizRequest(BaseModel):
    text: str
    difficulty: Optional[str] = "medium"
    learning_style: Optional[str] = "visual"

class ExplainRequest(BaseModel):
    topic: str
    learning_style: Optional[str] = "visual"
    multiple_styles: Optional[bool] = False

class ConceptRequest(BaseModel):
    text: str

class EvaluationRequest(BaseModel):
    user_id: int
    topic: str
    quiz: str
    user_answers: str
    score: int
    weak_area: str

class SignUpRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class PreferencesRequest(BaseModel):
    learning_style: str
    daily_study_goal: int
    notification_enabled: bool

class StudyGroupRequest(BaseModel):
    group_name: str
    description: Optional[str] = ""

class InviteRequest(BaseModel):
    user_id: int

class SharedNoteRequest(BaseModel):
    title: str
    content: str

class PlatformRequest(BaseModel):
    platform_name: str
    api_token: str

# ============ HELPER FUNCTIONS ============

def get_user_id_from_token(authorization: Optional[str] = Header(None)):
    """Extract user_id from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        token = authorization.split(" ")[1]
        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload["user_id"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============ BASIC ENDPOINTS ============

@app.get("/")
def home():
    return {"message": "Smart Study Buddy Backend Running"}

# ============ AUTHENTICATION ENDPOINTS ============

@app.post("/auth/signup")
def signup(request: SignUpRequest):
    """Register a new user"""
    try:
        existing_user = get_user_by_username(request.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        hashed_password = hash_password(request.password)
        user_id = create_user(request.username, request.email, hashed_password)
        
        # Set default preferences
        set_user_preference(user_id, "visual", 60, True)
        
        access_token = create_access_token(user_id, request.username)
        
        return {
            "user_id": user_id,
            "username": request.username,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login")
def login(request: LoginRequest):
    """Login user and return access token"""
    try:
        user = get_user_by_username(request.username)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(request.password, user[3]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(user[0], user[1])
        
        return {
            "user_id": user[0],
            "username": user[1],
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ USER PREFERENCES ENDPOINTS ============

@app.get("/preferences")
def get_preferences(user_id: int = Depends(get_user_id_from_token)):
    """Get user preferences"""
    prefs = get_user_preference(user_id)
    if not prefs:
        return {"error": "Preferences not found"}
    
    return {
        "learning_style": prefs[2],
        "daily_study_goal": prefs[3],
        "notification_enabled": prefs[4]
    }

@app.put("/preferences")
def update_preferences(request: PreferencesRequest, user_id: int = Depends(get_user_id_from_token)):
    """Update user preferences"""
    set_user_preference(user_id, request.learning_style, request.daily_study_goal, request.notification_enabled)
    return {"message": "Preferences updated successfully"}

# ============ LEARNING ENDPOINTS ============

@app.post("/generate-quiz")
def quiz_api(request: QuizRequest, user_id: int = Depends(get_user_id_from_token)):
    """Generate quiz with learning style support"""
    quiz = generate_quiz(request.text, request.difficulty, request.learning_style)
    return {"quiz": quiz}

@app.post("/generate-varied-quizzes")
def varied_quizzes_api(request: QuizRequest, user_id: int = Depends(get_user_id_from_token)):
    """Generate quizzes in all difficulty levels and styles"""
    quizzes = generate_varied_quizzes(request.text)
    return {"quizzes": quizzes}

@app.post("/explain")
def explain_api(request: ExplainRequest, user_id: int = Depends(get_user_id_from_token)):
    """Explain topic with learning style support"""
    if request.multiple_styles:
        explanations = explain_with_multiple_styles(request.topic)
        return {"explanations": explanations}
    else:
        explanation = explain_topic(request.topic, request.learning_style)
        return {"explanation": explanation}

@app.post("/extract-concepts")
def concept_api(request: ConceptRequest, user_id: int = Depends(get_user_id_from_token)):
    """Extract key concepts from text"""
    concepts = extract_concepts(request.text)
    return {"concepts": concepts}

@app.post("/evaluate")
def evaluate_api(request: EvaluationRequest, user_id: int = Depends(get_user_id_from_token)):
    """Evaluate quiz answers and save progress"""
    result = evaluate_answers(request.quiz, request.user_answers)
    level = get_learning_level(request.score)
    recommendation = get_recommendation(request.score)
    
    save_progress(request.user_id, request.topic, request.score, request.weak_area, level)
    
    schedule = generate_personalized_schedule([request.weak_area])
    
    return {
        "evaluation": result,
        "learning_level": level,
        "recommendation": recommendation,
        "schedule": schedule
    }

# ============ PROGRESS & ANALYTICS ENDPOINTS ============

@app.get("/progress")
def progress_api(user_id: int = Depends(get_user_id_from_token)):
    """Get user progress"""
    progress = fetch_progress(user_id)
    return {"progress": progress}

@app.get("/dashboard")
def dashboard_api(user_id: int = Depends(get_user_id_from_token)):
    """Get user dashboard with comprehensive analytics"""
    dashboard = get_user_dashboard(user_id)
    return dashboard

@app.get("/stats/by-topic")
def stats_by_topic(user_id: int = Depends(get_user_id_from_token)):
    """Get progress breakdown by topic"""
    topics = get_progress_by_topic(user_id)
    return {"topic_stats": topics}

@app.get("/recommendations")
def recommendations_api(user_id: int = Depends(get_user_id_from_token)):
    """Get personalized learning recommendations"""
    recommendations = get_learning_recommendations(user_id)
    return {"recommendations": recommendations}

@app.get("/weekly-progress")
def weekly_progress_api(weeks: int = 4, user_id: int = Depends(get_user_id_from_token)):
    """Get weekly progress data"""
    data = get_weekly_progress(user_id, weeks)
    return {"weekly_progress": data}

# ============ STUDY GROUP ENDPOINTS ============

@app.post("/groups/create")
def create_group_api(request: StudyGroupRequest, user_id: int = Depends(get_user_id_from_token)):
    """Create a new study group"""
    group_id = create_new_group(request.group_name, user_id, request.description)
    return {"group_id": group_id, "message": "Study group created successfully"}

@app.get("/groups")
def get_groups_api(user_id: int = Depends(get_user_id_from_token)):
    """Get all user's study groups"""
    groups = get_my_groups(user_id)
    return {"groups": groups}

@app.post("/groups/{group_id}/invite")
def invite_to_group(group_id: int, request: InviteRequest, user_id: int = Depends(get_user_id_from_token)):
    """Invite user to study group"""
    invite_member(group_id, request.user_id)
    return {"message": "User invited successfully"}

@app.get("/groups/{group_id}/info")
def group_info_api(group_id: int, user_id: int = Depends(get_user_id_from_token)):
    """Get study group information"""
    info = get_group_info(group_id)
    return info

@app.post("/groups/{group_id}/notes")
def share_note_api(group_id: int, request: SharedNoteRequest, user_id: int = Depends(get_user_id_from_token)):
    """Share a note with study group"""
    share_note(group_id, user_id, request.title, request.content)
    return {"message": "Note shared successfully"}

@app.get("/groups/{group_id}/notes")
def get_group_notes_api(group_id: int, user_id: int = Depends(get_user_id_from_token)):
    """Get shared notes from study group"""
    notes = get_group_notes(group_id)
    return {"notes": notes}

# ============ PLATFORM INTEGRATION ENDPOINTS ============

@app.post("/platforms/connect")
def connect_platform(request: PlatformRequest, user_id: int = Depends(get_user_id_from_token)):
    """Connect to external learning platform"""
    integration = PlatformIntegration(user_id)
    message = integration.connect_platform(request.platform_name, request.api_token)
    return {"message": message}

@app.get("/platforms")
def get_platforms(user_id: int = Depends(get_user_id_from_token)):
    """Get all connected platforms"""
    integration = PlatformIntegration(user_id)
    platforms = integration.get_all_integrations()
    return {"connected_platforms": platforms}

@app.get("/platforms/{platform_name}/courses")
def get_platform_courses(platform_name: str, user_id: int = Depends(get_user_id_from_token)):
    """Get courses from connected platform"""
    integration = PlatformIntegration(user_id)
    courses = integration.get_platform_courses(platform_name)
    return {"platform": platform_name, "courses": courses}
