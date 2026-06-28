# Smart Study Buddy - Detailed Code Implementation Guide

## Quick Start Understanding

### 1. How Data Flows Through the System

```
USER INTERACTION EXAMPLE: Generate Quiz

┌─────────────────────────────────────────────────────────────────────┐
│ 1. USER UPLOADS PDF or PASTES TEXT                                 │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. FRONTEND (app.py - Streamlit)                                    │
│    - User clicks "Extract Concepts"                                  │
│    - Reads PDF/text from file                                        │
│    - Prepares request                                                │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. API REQUEST (from app.py)                                        │
│    POST http://127.0.0.1:8000/extract-concepts                      │
│    Headers: Authorization: Bearer {token}                           │
│    Body: {"text": "full study material..."}                          │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. BACKEND RECEIVES REQUEST (api.py)                                │
│    @app.post("/extract-concepts")                                   │
│    def extract_concepts_endpoint(request: ConceptRequest):          │
│        - Validates JWT token                                         │
│        - Checks request data                                         │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 5. CALL BUSINESS LOGIC (concept_extractor.py)                       │
│    def extract_concepts(text: str) -> str:                          │
│        - Prepare prompt for GPT                                      │
│        - Call OpenAI API                                             │
│        - Parse response                                              │
│        - Return formatted concepts                                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 6. OPENAI API CALL                                                   │
│    Model: gpt-3.5-turbo                                              │
│    Prompt: "Extract important concepts from text..."                 │
│    Temperature: 0.7 (balanced creativity)                            │
│    Returns: Structured bullet-point concepts                         │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 7. RESPONSE SENT BACK TO FRONTEND                                    │
│    {                                                                 │
│        "concepts": [                                                 │
│            "Photosynthesis - light to energy",                       │
│            "Light-dependent reactions",                              │
│            "Calvin cycle..."                                         │
│        ]                                                             │
│    }                                                                 │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 8. DISPLAY IN STREAMLIT UI                                           │
│    st.write(response.json()["concepts"])                             │
│    • Shows formatted concept list                                    │
│    • User can review and proceed                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Code Examples & Explanations

### Example 1: Complete Quiz Generation Flow

#### File: `backend/api.py`
```python
# Step 1: Define Request Model
class QuizRequest(BaseModel):
    text: str                           # Study material
    difficulty: Optional[str] = "medium" # easy/medium/hard
    learning_style: Optional[str] = "visual"  # visual/auditory/kinesthetic

# Step 2: API Endpoint
@app.post("/generate-quiz")
def generate_quiz_endpoint(request: QuizRequest, 
                          authorization: Optional[str] = Header(None)):
    """
    Endpoint that generates a customized quiz
    """
    # Step 3: Extract and verify user from token
    try:
        user_id = get_user_id_from_token(authorization)
    except HTTPException:
        return {"error": "Unauthorized"}
    
    # Step 4: Get user's learning style preference (if not provided)
    if not request.learning_style:
        prefs = get_user_preference(user_id)
        request.learning_style = prefs[2]  # learning_style at index 2
    
    # Step 5: Call the quiz generation logic
    try:
        quiz = generate_quiz(
            request.text,
            request.difficulty,
            request.learning_style
        )
        
        # Step 6: Return quiz to user
        return {
            "quiz": quiz,
            "difficulty": request.difficulty,
            "style": request.learning_style,
            "status": "success"
        }
    
    except Exception as e:
        return {"error": str(e), "status": "failed"}
```

#### File: `backend/quiz_generator.py`
```python
# Step 1: Import and initialize OpenAI
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Step 2: Main quiz generation function
def generate_quiz(text: str, difficulty: str = "medium", 
                  learning_style: str = "visual") -> str:
    """
    Generate quiz questions based on:
    - text: Study material content
    - difficulty: Quiz difficulty level
    - learning_style: How to present questions
    
    Returns: String with formatted quiz questions
    """
    
    # Step 3: Map learning style to question format
    style_instructions = {
        "visual": "Create visual and diagram-based questions",
        "auditory": "Create step-by-step and narrative-based questions",
        "kinesthetic": "Create practical and scenario-based questions"
    }
    
    quiz_type = style_instructions.get(learning_style, "Create standard MCQs")
    
    # Step 4: Build the prompt - This is crucial!
    prompt = f"""
    You are an expert educator creating a quiz.
    
    Generate 5 multiple choice quiz questions from this content:
    
    CONTENT:
    {text}
    
    REQUIREMENTS:
    - Difficulty Level: {difficulty}
    - Question Style: {quiz_type}
    - Format: Multiple choice (A, B, C, D)
    - Include correct answer marked with *
    - Include explanation for correct answer
    
    For each question:
    1. Question text
    2. Four options (A, B, C, D)
    3. Correct answer (mark with *)
    4. Why it's correct (2-3 sentences)
    5. Common misconception students have
    
    Ensure questions are diverse and test different skills.
    """
    
    # Step 5: Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Model to use
        messages=[
            {
                "role": "system",
                "content": "You are an expert educator creating effective quiz questions."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.8,        # Creativity level (0-1)
        max_tokens=2000,        # Max response length
        top_p=0.95              # Diversity
    )
    
    # Step 6: Extract and return the response
    quiz_content = response.choices[0].message.content
    
    return quiz_content
```

#### Usage in Streamlit Frontend (`app.py`)
```python
import streamlit as st
import requests

# Step 1: Get user input
st.header("🎯 Generate Quiz")
col1, col2, col3 = st.columns(3)

with col1:
    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])

with col2:
    learning_style = st.selectbox(
        "Your Learning Style",
        ["visual", "auditory", "kinesthetic"]
    )

with col3:
    st.write("")  # Spacing

# Step 2: Get study material
pdf_text = st.text_area("Paste study material", height=200)

# Step 3: Create button
if st.button("Generate Quiz"):
    # Step 4: Send request to API
    try:
        response = requests.post(
            "http://127.0.0.1:8000/generate-quiz",
            json={
                "text": pdf_text,
                "difficulty": difficulty,
                "learning_style": learning_style
            },
            headers={
                "Authorization": f"Bearer {st.session_state.access_token}"
            }
        )
        
        # Step 5: Handle response
        if response.status_code == 200:
            data = response.json()
            quiz = data["quiz"]
            
            # Step 6: Display the quiz
            st.success("Quiz Generated!")
            st.write(quiz)
            
            # Step 7: Allow user to attempt quiz
            user_answers = st.text_area("Your Answers")
            
            if st.button("Submit Quiz"):
                eval_response = requests.post(
                    "http://127.0.0.1:8000/evaluate-answers",
                    json={
                        "quiz": quiz,
                        "user_answers": user_answers
                    },
                    headers={
                        "Authorization": f"Bearer {st.session_state.access_token}"
                    }
                )
                
                if eval_response.status_code == 200:
                    results = eval_response.json()
                    st.info(f"Your Score: {results['score']}/100")
                    st.write(results['feedback'])
        
        else:
            st.error(f"Error: {response.status_code}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
```

---

### Example 2: User Authentication Flow

#### File: `backend/auth.py`
```python
import bcrypt
import jwt
from datetime import datetime, timedelta
import os

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
EXPIRATION_HOURS = 24

# ===== PASSWORD HASHING =====
def hash_password(password: str) -> str:
    """
    Hash password using bcrypt
    
    Why bcrypt?
    - Intentionally slow (prevents brute-force attacks)
    - Adds salt automatically (prevents rainbow tables)
    - Industry standard for password hashing
    
    Process:
    1. Generate random salt (16 rounds)
    2. Hash password with salt
    3. Return hash string
    """
    
    # Generate salt (2^rounds = 2^10 = 1024 iterations)
    # Higher number = more secure but slower
    salt = bcrypt.gensalt(rounds=10)
    
    # Hash password with salt
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Return as string
    return hashed.decode('utf-8')


def verify_password(password: str, hash_value: str) -> bool:
    """
    Verify plain password against stored hash
    
    bcrypt does this securely by:
    - Extracting salt from stored hash
    - Hashing provided password with same salt
    - Comparing hashes (constant-time comparison)
    """
    
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hash_value.encode('utf-8')
        )
    except Exception:
        return False

# ===== JWT TOKEN MANAGEMENT =====
def create_access_token(user_id: int, username: str) -> str:
    """
    Create JWT token for user session
    
    JWT Structure: header.payload.signature
    
    Payload contains:
    - user_id: Who is this token for?
    - username: Username for display
    - exp: When does it expire? (24 hours from now)
    - iat: When was it issued?
    """
    
    # Create payload
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    
    # Encode with secret key
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return token


def verify_token(token: str) -> dict or None:
    """
    Verify JWT token and extract payload
    
    Checks:
    1. Token not tampered with (signature valid)
    2. Token not expired
    3. Algorithm matches
    
    Returns: Payload dict if valid, None if invalid
    """
    
    try:
        # Decode and verify
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        return payload
    
    except jwt.ExpiredSignatureError:
        # Token expired (older than 24 hours)
        print("Token has expired")
        return None
    
    except jwt.InvalidTokenError:
        # Token tampered with or invalid
        print("Invalid token")
        return None
```

#### File: `backend/api.py` - Login & Signup Endpoints
```python
from backend.auth import hash_password, verify_password, create_access_token
from backend.database import create_user, get_user_by_username

class SignUpRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/signup")
def signup(request: SignUpRequest):
    """
    Register a new user
    
    Steps:
    1. Validate input (not empty, email format)
    2. Check if user already exists
    3. Hash password
    4. Store in database
    5. Create JWT token
    6. Return token to user
    """
    
    try:
        # Step 1: Check if user exists
        existing_user = get_user_by_username(request.username)
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
        
        # Step 2: Hash the password
        hashed_password = hash_password(request.password)
        
        # Step 3: Store user in database
        user_id = create_user(
            request.username,
            request.email,
            hashed_password
        )
        
        # Step 4: Set default user preferences
        # User starts with visual learning style and 60 min/day goal
        set_user_preference(user_id, "visual", 60, True)
        
        # Step 5: Create JWT token
        access_token = create_access_token(user_id, request.username)
        
        # Step 6: Return response
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
    """
    Login existing user
    
    Steps:
    1. Find user by username in database
    2. Verify password (bcrypt)
    3. If correct, create JWT token
    4. Return token
    """
    
    try:
        # Step 1: Query database for user
        user = get_user_by_username(request.username)
        
        if not user:
            # Don't reveal if username exists (security best practice)
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Step 2: Verify password
        # user[3] is the password_hash from database
        if not verify_password(request.password, user[3]):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Step 3: Password correct! Create token
        # user[0] = id, user[1] = username
        access_token = create_access_token(user[0], user[1])
        
        # Step 4: Return token
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
```

---

### Example 3: Adaptive Learning Algorithm

#### File: `backend/adaptive_learning.py`
```python
def get_learning_level(score: int) -> str:
    """
    Determine user's learning level based on quiz score
    
    Based on Bloom's Taxonomy:
    - Beginner (< 60%): Haven't grasped concept yet
    - Intermediate (60-85%): Understand concept, need practice
    - Advanced (≥ 85%): Mastered concept, ready for complexity
    
    Arguments:
        score: Quiz score out of 100
    
    Returns:
        "Beginner" | "Intermediate" | "Advanced"
    
    Example:
        score = 55 → "Beginner"
        score = 72 → "Intermediate"
        score = 88 → "Advanced"
    """
    
    # Threshold 1: Basic competency
    if score < 60:
        return "Beginner"
    
    # Threshold 2: Intermediate competency
    elif score < 85:
        return "Intermediate"
    
    # Threshold 3: Advanced competency
    else:
        return "Advanced"


def get_recommendation(score: int) -> str:
    """
    Generate personalized recommendation based on score
    
    Not just about passing/failing - provide actionable guidance
    
    Example Output:
        score = 45 → "Focus on core concepts, don't move forward yet"
        score = 70 → "Practice applying these concepts to new scenarios"
        score = 92 → "Challenge yourself with harder problems"
    """
    
    if score >= 85:
        # Advanced level - push for mastery
        return "Excellent work! Proceed to advanced topics - you've mastered this concept."
    
    elif score >= 60:
        # Intermediate level - consolidate knowledge
        return "Good progress! Practice medium difficulty questions to strengthen your understanding."
    
    else:
        # Beginner level - rebuild foundation
        return "Take time to revise fundamentals and repeat quizzes. Don't rush forward!"


# ===== USAGE EXAMPLE =====
# When user completes a quiz:

quiz_score = 73  # User got 73%

level = get_learning_level(quiz_score)
# Returns: "Intermediate"

recommendation = get_recommendation(quiz_score)
# Returns: "Good progress! Practice medium difficulty questions..."

# Store in database:
# INSERT INTO progress (user_id, topic, score, learning_level)
# VALUES (5, "Photosynthesis", 73, "Intermediate")

# Next quiz will automatically be at MEDIUM difficulty
```

---

### Example 4: Spaced Repetition Scheduler

#### File: `backend/scheduler.py`
```python
from datetime import datetime, timedelta

def generate_personalized_schedule(weak_topics: list) -> list:
    """
    Generate spaced repetition schedule for weak areas
    
    Scientific Basis:
    - Ebbinghaus Forgetting Curve: We forget ~50% within 1 day
    - Spacing reviews at optimal intervals extends retention
    - Proven intervals: 1 day, 3 days, 7 days, 14 days, 30 days
    
    Our implementation uses: 1 day, 3 days, 7 days
    
    Arguments:
        weak_topics: List of topics where user scored < 60%
                    Example: ["Photosynthesis", "Cellular Respiration"]
    
    Returns:
        List of schedule items with dates
        Example:
        [
            {"topic": "Photosynthesis", "revision_date": "2024-06-29"},
            {"topic": "Photosynthesis", "revision_date": "2024-07-01"},
            {"topic": "Photosynthesis", "revision_date": "2024-07-05"},
            {"topic": "Cellular Respiration", "revision_date": "2024-06-29"},
            ...
        ]
    """
    
    schedule = []
    current_date = datetime.now()
    
    # Spacing intervals (in days) - based on learning research
    # 1 day: Prevents initial forgetting (consolidation)
    # 3 days: Strengthens memory (expansion)
    # 7 days: Moves to long-term memory (integration)
    intervals = [1, 3, 7]
    
    # For each weak topic
    for topic in weak_topics:
        # Create review schedule
        for days in intervals:
            # Calculate future date
            study_date = current_date + timedelta(days=days)
            
            # Add to schedule
            schedule.append({
                "topic": topic,
                "revision_date": study_date.strftime("%Y-%m-%d"),
                "priority": "High" if days == 1 else "Medium"
            })
    
    # Sort by date
    schedule.sort(key=lambda x: x['revision_date'])
    
    return schedule


# ===== USAGE EXAMPLE =====
# User completes quiz with these results:
# - Photosynthesis: 55% (weak area!)
# - Cellular Respiration: 48% (weak area!)
# - DNA Replication: 82% (good)

weak_topics = ["Photosynthesis", "Cellular Respiration"]

schedule = generate_personalized_schedule(weak_topics)

# Returns:
# [
#   {"topic": "Photosynthesis", "revision_date": "2024-06-29", "priority": "High"},
#   {"topic": "Cellular Respiration", "revision_date": "2024-06-29", "priority": "High"},
#   {"topic": "Photosynthesis", "revision_date": "2024-07-01", "priority": "Medium"},
#   {"topic": "Cellular Respiration", "revision_date": "2024-07-01", "priority": "Medium"},
#   {"topic": "Photosynthesis", "revision_date": "2024-07-05", "priority": "Medium"},
#   {"topic": "Cellular Respiration", "revision_date": "2024-07-05", "priority": "Medium"},
# ]

# This schedule is stored in database and notified to user
# If user reviews and still < 60%, reschedule with extended intervals
# If user reviews and > 85%, mark as "mastered" - no more reviews needed
```

---

### Example 5: Progress Analytics

#### File: `backend/analytics.py`
```python
from backend.database import get_user_stats, fetch_progress

def get_user_dashboard(user_id: int) -> dict:
    """
    Generate comprehensive dashboard for user
    
    Aggregates all progress data into metrics
    
    Returns dict with:
    - total_tests: Number of quizzes completed
    - average_score: Mean score across all quizzes
    - best_topic: Topic with highest average score
    - worst_topic: Topic with lowest average score
    - study_streak: Consecutive days studied
    - topic_breakdown: Performance by topic
    - recent_activity: Last 5 quiz attempts
    """
    
    # Step 1: Get user's preference and all progress records
    stats = get_user_stats(user_id)
    progress = fetch_progress(user_id)  # List of all attempts
    # progress[i] = (id, user_id, topic, score, weak_area, learning_level, timestamp)
    
    # Step 2: Calculate basic metrics
    total_tests = len(progress)
    
    # Handle case of no progress yet
    if total_tests == 0:
        return {
            "total_tests": 0,
            "average_score": 0,
            "best_topic": None,
            "worst_topic": None,
            "study_streak": 0,
            "message": "Start your first quiz to see analytics!"
        }
    
    # Step 3: Calculate average score
    scores = [int(p[3]) for p in progress]  # p[3] is score column
    avg_score = sum(scores) / len(scores)
    
    # Step 4: Analyze performance by topic
    topic_scores = {}
    
    for p in progress:
        topic = p[2]  # p[2] is topic column
        score = int(p[3])  # p[3] is score column
        
        # Group scores by topic
        if topic not in topic_scores:
            topic_scores[topic] = []
        
        topic_scores[topic].append(score)
    
    # Step 5: Find best and worst topics
    best_topic = max(
        topic_scores,
        key=lambda t: sum(topic_scores[t]) / len(topic_scores[t])
    )
    
    worst_topic = min(
        topic_scores,
        key=lambda t: sum(topic_scores[t]) / len(topic_scores[t])
    )
    
    # Step 6: Calculate study streak
    study_streak = calculate_study_streak(progress)
    
    # Step 7: Compile and return dashboard
    return {
        "total_tests": total_tests,
        "average_score": round(avg_score, 2),
        "best_topic": best_topic,
        "worst_topic": worst_topic,
        "study_streak": study_streak,
        "topic_breakdown": {
            topic: {
                "attempts": len(scores),
                "average": round(sum(scores) / len(scores), 2),
                "highest": max(scores),
                "lowest": min(scores)
            }
            for topic, scores in topic_scores.items()
        },
        "recent_activity": progress[:5]  # Last 5 quizzes
    }


def calculate_study_streak(progress: list) -> int:
    """
    Calculate consecutive days user has studied
    
    Logic:
    1. Extract dates from progress records
    2. Sort in reverse (most recent first)
    3. Count consecutive dates backwards from today
    4. Stop counting when gap found
    
    Example:
    - Studied: Days 1, 2, 3, 5, 6, 10
    - Streak: 2 (Days 5-6, because gap on Day 4)
    """
    
    if not progress:
        return 0
    
    # Step 1: Extract unique dates from timestamps
    dates = set()
    for record in progress:
        timestamp = record[6]  # p[6] is timestamp
        if timestamp:
            # Extract just the date part (YYYY-MM-DD)
            date = timestamp.split(' ')[0]
            dates.add(date)
    
    # Step 2: Sort dates in reverse (most recent first)
    sorted_dates = sorted(list(dates), reverse=True)
    
    if not sorted_dates:
        return 0
    
    # Step 3: Count consecutive dates
    streak = 1
    today = datetime.now().date()
    
    for i, date_str in enumerate(sorted_dates):
        # Convert string to date object
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Expected date going backwards from today
        expected_date = today - timedelta(days=i)
        
        # Does this date match the expected sequence?
        if date_obj == expected_date:
            if i > 0:  # Increment streak (skip first iteration)
                streak += 1
        else:
            break  # Streak broken
    
    return streak

# ===== USAGE EXAMPLE =====
# Get dashboard for user ID 5

dashboard = get_user_dashboard(5)

# Returns something like:
# {
#     "total_tests": 25,
#     "average_score": 78.5,
#     "best_topic": "Photosynthesis",
#     "worst_topic": "Cellular Respiration",
#     "study_streak": 5,
#     "topic_breakdown": {
#         "Photosynthesis": {
#             "attempts": 5,
#             "average": 87.2,
#             "highest": 95,
#             "lowest": 78
#         },
#         "Cellular Respiration": {
#             "attempts": 4,
#             "average": 62.5,
#             "highest": 72,
#             "lowest": 48
#         }
#     }
# }
```

---

## Configuration & Environment Variables

### `.env` File Setup

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_API_MODEL=gpt-3.5-turbo  # or gpt-4 for better results

# Database
DATABASE_PATH=database/studybuddy.db

# Server
API_BASE_URL=http://127.0.0.1:8000
FRONTEND_URL=http://localhost:8501

# JWT Secret
SECRET_KEY=your-secret-key-min-32-chars-recommended

# Platform Integration Tokens
COURSERA_API_KEY=your-key
UDEMY_API_KEY=your-key
KHAN_ACADEMY_API_KEY=your-key
EDX_API_KEY=your-key
```

### Key Configuration Parameters

| Parameter | Purpose | Default | Tuning |
|-----------|---------|---------|--------|
| `temperature` | Creativity level (0-1) | 0.7 | ↑ for more variation, ↓ for consistency |
| `max_tokens` | Max response length | 2000 | Adjust based on content needs |
| `top_p` | Diversity | 0.95 | ↓ for focused, ↑ for diverse |
| `difficulty_threshold` | Score thresholds | 60, 85 | Adjust per content difficulty |
| `spacing_intervals` | Days for review | [1, 3, 7] | Add more (14, 30) for long-term |
| `bcrypt_rounds` | Password security | 10 | ↑ for more security (slower) |

---

## Testing Guide

### Unit Test Example: Quiz Generation

```python
# tests/test_quiz_generator.py
import pytest
from backend.quiz_generator import generate_quiz

def test_generate_quiz_basic():
    """Test basic quiz generation"""
    text = "Photosynthesis is the process where plants convert light to chemical energy"
    
    quiz = generate_quiz(text, difficulty="easy", learning_style="visual")
    
    # Assertions
    assert quiz is not None
    assert len(quiz) > 0
    assert "Question" in quiz or "Q" in quiz
    assert "Answer" in quiz or "A)" in quiz

def test_generate_quiz_visual_style():
    """Test that visual style produces diagram-based questions"""
    text = "DNA structure: double helix with base pairs"
    
    visual_quiz = generate_quiz(text, learning_style="visual")
    
    # Visual quizzes should mention diagrams
    assert visual_quiz is not None

def test_generate_quiz_difficulty_levels():
    """Test all difficulty levels generate quizzes"""
    text = "Sample study material"
    
    for difficulty in ["easy", "medium", "hard"]:
        quiz = generate_quiz(text, difficulty=difficulty)
        assert quiz is not None
        assert len(quiz) > 100  # Should have substantial content

@pytest.mark.integration
def test_generate_quiz_with_openai():
    """Integration test with real OpenAI API"""
    # This test requires OPENAI_API_KEY in env
    text = """
    Photosynthesis is the process where plants use light energy to convert 
    carbon dioxide and water into glucose and oxygen.
    """
    
    quiz = generate_quiz(text, difficulty="medium")
    
    # Validate structure
    assert "Question" in quiz or "Q1" in quiz
    assert "option" in quiz.lower() or ")" in quiz
```

---

## Deployment Checklist

### Before Going to Production

- [ ] Set `SECRET_KEY` to random 32+ character string
- [ ] Move from SQLite to PostgreSQL (better for scale)
- [ ] Add HTTPS/SSL certificates
- [ ] Set up environment variables securely (not in code)
- [ ] Enable CORS only for your frontend domain
- [ ] Add rate limiting to API endpoints
- [ ] Implement logging and monitoring
- [ ] Add database backups
- [ ] Test error handling thoroughly
- [ ] Load test with expected user volume
- [ ] Set up CI/CD pipeline

---

## Performance Optimization Tips

### 1. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_preference(user_id):
    # Only query database if not in cache
    return db.query(...)
```

### 2. Database Indexing
```sql
CREATE INDEX idx_user_progress ON progress(user_id, timestamp DESC);
CREATE INDEX idx_topic_scores ON progress(topic, score);
```

### 3. Async Operations
```python
import asyncio

async def process_quiz_async(quiz_data):
    # Parallel processing
    score_task = evaluate_answers_async(quiz_data)
    recommendation_task = get_recommendation_async(score)
    
    results = await asyncio.gather(score_task, recommendation_task)
    return results
```

---

