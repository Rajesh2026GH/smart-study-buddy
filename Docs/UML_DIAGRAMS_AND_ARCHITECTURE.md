# Smart Study Buddy - UML Diagrams & Visual Architecture

## 1. System Architecture Diagram

```mermaid
graph TB
    User["👤 User<br/>Streamlit Client"]
    
    subgraph Frontend["PRESENTATION LAYER"]
        UI["Streamlit UI<br/>Authentication<br/>Study Interface<br/>Dashboard<br/>Analytics"]
    end
    
    subgraph API["API LAYER - FastAPI"]
        Auth["🔐 Auth Module<br/>Login/Signup<br/>JWT Management"]
        Quiz["🎯 Quiz Module<br/>Generation<br/>Evaluation"]
        Analytics_API["📊 Analytics<br/>Dashboard<br/>Progress Tracking"]
        Collab["👥 Collaboration<br/>Groups<br/>Notes Sharing"]
    end
    
    subgraph Business["BUSINESS LOGIC LAYER"]
        Concepts["🔍 Concept<br/>Extractor"]
        QuizGen["📝 Quiz<br/>Generator"]
        Eval["✅ Evaluator"]
        Explain["💡 Explainer"]
        Adaptive["🧠 Adaptive<br/>Learning"]
        Schedule["📅 Scheduler"]
        Analytics_Logic["📈 Analytics"]
    end
    
    subgraph AI["AI LAYER"]
        OpenAI["🤖 OpenAI GPT<br/>API<br/>3.5 / 4"]
    end
    
    subgraph Data["DATA LAYER"]
        DB["🗄️ SQLite3<br/>Database<br/>studybuddy.db"]
        Tables["📋 Tables:<br/>users, progress<br/>study_groups<br/>preferences<br/>integrations"]
    end
    
    User -->|HTTP Requests| UI
    UI -->|API Calls| Auth
    UI -->|API Calls| Quiz
    UI -->|API Calls| Analytics_API
    UI -->|API Calls| Collab
    
    Auth --> Business
    Quiz --> Business
    Analytics_API --> Business
    Collab --> Business
    
    Business -->|Prompt Engineering| OpenAI
    
    Business -->|Query/Store| DB
    DB --> Tables
    
    style User fill:#e1f5ff
    style Frontend fill:#fff3e0
    style API fill:#f3e5f5
    style Business fill:#e8f5e9
    style AI fill:#fce4ec
    style Data fill:#ede7f6
```

## 2. Class Diagram - Core Modules

```mermaid
classDiagram
    class User {
        -int id
        -str username
        -str email
        -str password_hash
        -datetime created_at
        +login()
        +signup()
        +update_preferences()
    }
    
    class UserPreferences {
        -int user_id
        -str learning_style
        -int daily_study_goal
        -bool notification_enabled
        +set_style()
        +get_preferences()
    }
    
    class Progress {
        -int user_id
        -str topic
        -int score
        -str weak_area
        -str learning_level
        -datetime timestamp
        +save_progress()
        +get_history()
    }
    
    class QuizGenerator {
        -str text
        -str difficulty
        -str learning_style
        +generate_quiz()
        +generate_varied_quizzes()
        -format_questions()
    }
    
    class ConceptExtractor {
        -str text
        +extract_concepts()
        -parse_response()
    }
    
    class Evaluator {
        -str quiz
        -str user_answers
        +evaluate_answers()
        -calculate_score()
        -generate_feedback()
    }
    
    class AdaptiveLearning {
        -int score
        +get_learning_level()
        +get_recommendation()
        -adjust_difficulty()
    }
    
    class Scheduler {
        -list weak_topics
        +generate_personalized_schedule()
        -calculate_intervals()
    }
    
    class Analytics {
        -int user_id
        +get_user_dashboard()
        +get_progress_by_topic()
        +calculate_study_streak()
        -aggregate_metrics()
    }
    
    class StudyGroup {
        -int id
        -str group_name
        -int created_by
        +create_group()
        +add_member()
        +share_note()
    }
    
    class PlatformIntegration {
        -str platform_name
        -str api_token
        +connect_platform()
        +sync_progress()
        -get_platform_data()
    }
    
    User "1" -- "1" UserPreferences
    User "1" -- "*" Progress
    User "1" -- "*" StudyGroup
    User "1" -- "*" PlatformIntegration
    
    QuizGenerator --> ConceptExtractor
    QuizGenerator --> Evaluator
    Evaluator --> AdaptiveLearning
    AdaptiveLearning --> Scheduler
    Analytics --> Progress
    StudyGroup --> User
```

## 3. Database Entity-Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ USER_PREFERENCES : has
    USERS ||--o{ PROGRESS : generates
    USERS ||--o{ STUDY_GROUPS : creates
    USERS ||--o{ GROUP_MEMBERS : joins
    USERS ||--o{ SHARED_NOTES : contributes
    USERS ||--o{ PLATFORM_INTEGRATIONS : connects
    
    STUDY_GROUPS ||--o{ GROUP_MEMBERS : contains
    STUDY_GROUPS ||--o{ SHARED_NOTES : hosts
    
    USERS {
        int id PK
        string username UK
        string email UK
        string password_hash
        timestamp created_at
    }
    
    USER_PREFERENCES {
        int id PK
        int user_id FK
        string learning_style
        int daily_study_goal
        boolean notification_enabled
    }
    
    PROGRESS {
        int id PK
        int user_id FK
        string topic
        int score
        string weak_area
        string learning_level
        timestamp timestamp
    }
    
    STUDY_GROUPS {
        int id PK
        string group_name
        int created_by FK
        string description
        timestamp created_at
    }
    
    GROUP_MEMBERS {
        int id PK
        int group_id FK
        int user_id FK
        timestamp joined_at
    }
    
    SHARED_NOTES {
        int id PK
        int group_id FK
        int user_id FK
        string title
        string content
        timestamp created_at
    }
    
    PLATFORM_INTEGRATIONS {
        int id PK
        int user_id FK
        string platform_name
        string api_token
        timestamp connected_at
    }
```

## 4. Quiz Generation Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant API as FastAPI
    participant Auth as Authentication
    participant DB as Database
    participant OpenAI as OpenAI API
    
    User->>UI: 1. Click "Generate Quiz"
    UI->>API: 2. POST /generate-quiz<br/>(text, difficulty, style)
    
    API->>Auth: 3. Verify JWT Token
    Auth-->>API: 4. Token Valid ✓
    
    API->>DB: 5. Query User Preferences
    DB-->>API: 6. Return {learning_style: "visual"}
    
    API->>DB: 7. Query Progress History
    DB-->>API: 8. Return Recent Scores
    
    API->>API: 9. Determine Current Level<br/>(Beginner/Intermediate/Advanced)
    
    API->>OpenAI: 10. Send Prompt<br/>{text, style, difficulty}
    OpenAI-->>API: 11. Return Generated Quiz
    
    API->>DB: 12. Log Quiz Generation<br/>(timestamp, user_id)
    DB-->>API: 13. Confirmed ✓
    
    API-->>UI: 14. Return Quiz JSON
    UI-->>User: 15. Display Quiz Questions
    
    User->>UI: 16. Submit Answers
    UI->>API: 17. POST /evaluate-answers<br/>(quiz, answers)
    
    API->>OpenAI: 18. Request Evaluation<br/>(quiz, user_answers)
    OpenAI-->>API: 19. Return Score & Feedback
    
    API->>API: 20. Calculate Learning Level
    
    API->>DB: 21. Save Progress Record<br/>(score, level, topic, timestamp)
    DB-->>API: 22. Progress Saved ✓
    
    API->>DB: 23. Check if Weak Area<br/>(score < 60%)
    
    alt Score < 60%
        API->>API: 24a. Generate Schedule<br/>(1, 3, 7 day intervals)
        API->>DB: 25a. Save Schedule
    else Score >= 60%
        API->>API: 24b. Prepare Next Challenge
        API->>DB: 25b. Set Difficulty+1
    end
    
    API-->>UI: 26. Return Results<br/>(score, feedback, recommendation)
    UI-->>User: 27. Display Results & Recommendations
```

## 5. Learning Journey State Machine

```mermaid
stateDiagram-v2
    [*] --> Authentication
    
    Authentication --> Preferences : Setup Complete
    
    Preferences --> StudySelection : Preferences Set
    
    StudySelection --> ConceptIdentification : Upload/Paste Text
    
    ConceptIdentification --> QuizGeneration : Concepts Extracted
    
    QuizGeneration --> QuizAttempt : Quiz Generated
    
    QuizAttempt --> AnswerSubmission : Quiz Completed
    
    AnswerSubmission --> Evaluation : Answers Submitted
    
    Evaluation --> ScoreAnalysis : Evaluation Complete
    
    ScoreAnalysis --> LevelDetermination : Analyze Score
    
    LevelDetermination --> Beginner : Score < 60%
    LevelDetermination --> Intermediate : 60% ≤ Score < 85%
    LevelDetermination --> Advanced : Score ≥ 85%
    
    Beginner --> RecommendationBeginner : Recommend Revision
    Intermediate --> RecommendationIntermediate : Recommend Practice
    Advanced --> RecommendationAdvanced : Recommend Advanced
    
    RecommendationBeginner --> ScheduleCreation : Create Schedule
    RecommendationIntermediate --> ScheduleCreation : Create Schedule
    RecommendationAdvanced --> ScheduleCreation : Create Schedule
    
    ScheduleCreation --> Dashboard : Schedule Generated
    
    Dashboard --> Analytics : View Progress
    Dashboard --> Collaboration : Join Study Group
    Dashboard --> StudySelection : Continue Learning
    
    Analytics --> Dashboard : Back to Dashboard
    Collaboration --> Dashboard : Group Joined
    
    Dashboard --> [*] : Logout
    
    note right of Beginner
        Learning Level: BEGINNER
        Next Difficulty: Same or Easier
        Recommendation: Revise Fundamentals
    end note
    
    note right of Intermediate
        Learning Level: INTERMEDIATE
        Next Difficulty: Medium
        Recommendation: Practice Concepts
    end note
    
    note right of Advanced
        Learning Level: ADVANCED
        Next Difficulty: Hard
        Recommendation: Proceed to Advanced
    end note
```

## 6. Adaptive Difficulty Algorithm Flowchart

```mermaid
flowchart TD
    A["START: User Completes Quiz"] --> B["Calculate Quiz Score"]
    B --> C{"Score < 60%?"}
    
    C -->|YES| D["Level = BEGINNER"]
    C -->|NO| E{"Score < 85%?"}
    
    E -->|YES| F["Level = INTERMEDIATE"]
    E -->|NO| G["Level = ADVANCED"]
    
    D --> H["Recommendation:<br/>Revise Fundamentals"]
    F --> I["Recommendation:<br/>Practice Medium Difficulty"]
    G --> J["Recommendation:<br/>Proceed to Advanced"]
    
    H --> K["Save to Database:<br/>user_id, score, topic,<br/>learning_level"]
    I --> K
    J --> K
    
    K --> L{"Weak Area<br/>Detected?"}
    
    L -->|YES: Score < 60%| M["Generate Schedule:<br/>Day 1, 3, 7<br/>Spaced Repetition"]
    L -->|NO| N["Mark as Improving"]
    
    M --> O["Save Schedule"]
    N --> O
    
    O --> P["Determine Next Quiz Level"]
    
    P --> Q{"Current Level?"}
    
    Q -->|BEGINNER| R["Next Quiz:<br/>SAME DIFFICULTY"]
    Q -->|INTERMEDIATE| S["Next Quiz:<br/>MEDIUM DIFFICULTY"]
    Q -->|ADVANCED| T["Next Quiz:<br/>HARD DIFFICULTY"]
    
    R --> U["Update Database<br/>next_difficulty"]
    S --> U
    T --> U
    
    U --> V["Return to User:<br/>Score + Feedback +<br/>Recommendation"]
    
    V --> W["END: User Views Results"]
    
    style A fill:#e1f5ff
    style W fill:#c8e6c9
    style D fill:#ffccbc
    style F fill:#fff9c4
    style G fill:#d1c4e9
```

## 7. Three Learning Styles Comparison

```mermaid
graph TB
    Topic["📚 TOPIC:<br/>Photosynthesis"]
    
    subgraph Visual["👁️ VISUAL LEARNER"]
        V1["Display Diagrams"]
        V2["Show Flowcharts"]
        V3["Color-coded Sections"]
        V4["Visual Analogies"]
        V5["ASCII Diagrams"]
    end
    
    subgraph Auditory["🎵 AUDITORY LEARNER"]
        A1["Step-by-Step Narration"]
        A2["Conversational Tone"]
        A3["Key Phrases Repeated"]
        A4["Think-Aloud Commentary"]
        A5["Dialogue Format"]
    end
    
    subgraph Kinesthetic["🤲 KINESTHETIC LEARNER"]
        K1["Hands-On Activities"]
        K2["Real-World Scenarios"]
        K3["Practical Examples"]
        K4["Role-Playing Exercises"]
        K5["Interactive Simulations"]
    end
    
    Topic --> Visual
    Topic --> Auditory
    Topic --> Kinesthetic
    
    V1 --> Q1["Q: Look at diagram,<br/>what does X show?"]
    A1 --> Q2["Q: Explain process<br/>in your words"]
    K1 --> Q3["Q: How would you<br/>apply this?"]
    
    V2 --> Q1
    A2 --> Q2
    K2 --> Q3
    
    V3 --> R1["Quiz Style:<br/>VISUAL"]
    A3 --> R2["Quiz Style:<br/>AUDITORY"]
    K3 --> R3["Quiz Style:<br/>KINESTHETIC"]
    
    style Topic fill:#fff9c4
    style Visual fill:#e1f5ff
    style Auditory fill:#f3e5f5
    style Kinesthetic fill:#e8f5e9
```

## 8. Spaced Repetition Schedule

```mermaid
graph LR
    A["Day 0<br/>LEARN"] -->|Initial Learning| B["✓ Mastered<br/>70% Retention"]
    
    B -->|1 Day Later| C["Day 1<br/>REVIEW 1"]
    C -->|✓| D["✓ Consolidated<br/>80% Retention"]
    
    D -->|3 Days Later| E["Day 3<br/>REVIEW 2"]
    E -->|✓| F["✓ Strengthened<br/>85% Retention"]
    
    F -->|7 Days Later| G["Day 7<br/>REVIEW 3"]
    G -->|✓| H["✓ Mastered<br/>90% Retention"]
    
    H -->|Monitored| I["Long-term<br/>Memory"]
    
    style A fill:#ffccbc
    style B fill:#fff9c4
    style C fill:#fff9c4
    style D fill:#c8e6c9
    style E fill:#c8e6c9
    style F fill:#b3e5fc
    style G fill:#b3e5fc
    style H fill:#ce93d8
    style I fill:#ce93d8
    
    classDef retention fill:#d1c4e9,stroke:#5e35b1,stroke-width:2px
    class B,D,F,H,I retention
```

## 9. User Progress Analytics Flow

```mermaid
flowchart TD
    User["👤 User"] -->|Request Dashboard| API["Get Dashboard"]
    
    API -->|Query| DB1[("Fetch All<br/>Progress Records")]
    DB1 -->|Returns| Data["List of Quiz Attempts:<br/>{topic, score, date}"]
    
    Data -->|Calculate| M1["Total Tests<br/>Completed"]
    Data -->|Calculate| M2["Average Score"]
    Data -->|Calculate| M3["Best Topic"]
    Data -->|Calculate| M4["Worst Topic"]
    Data -->|Calculate| M5["Study Streak"]
    
    M1 --> Metrics["📊 Metrics Object:<br/>total_tests: 25<br/>avg_score: 78.5%<br/>best: Photosynthesis<br/>worst: Respiration<br/>streak: 5 days"]
    M2 --> Metrics
    M3 --> Metrics
    M4 --> Metrics
    M5 --> Metrics
    
    Metrics -->|Format| Response["JSON Response<br/>{<br/>  'total_tests': 25,<br/>  'average_score': 78.5,<br/>  'best_topic': '...',<br/>  'worst_topic': '...',<br/>  'study_streak': 5<br/>}"]
    
    Response -->|Render| Dashboard["📈 DASHBOARD<br/>┌─────────────────┐<br/>│ Total: 25 tests │<br/>│ Avg: 78.5%      │<br/>│ Streak: 🔥 5    │<br/>│ Best: Photo     │<br/>│ Worst: Resp.    │<br/>└─────────────────┘"]
    
    Dashboard -->|Display| UI["Show in Streamlit"]
    
    UI -->|Visualize| Charts["📊 Charts:<br/>• Progress Over Time<br/>• Topic Performance<br/>• Weekly Trends<br/>• Learning Curve"]
    
    Charts --> User
    
    style User fill:#e1f5ff
    style Metrics fill:#fff9c4
    style Dashboard fill:#c8e6c9
    style Charts fill:#f3e5f5
```

## 10. Multi-Platform Integration Architecture

```mermaid
graph TB
    User["👤 User<br/>Smart Study Buddy"]
    
    SSB["Smart Study<br/>Buddy Database<br/>Local Progress<br/>Preferences<br/>Scores"]
    
    API_Bridge["🔗 Platform<br/>Integration<br/>Module"]
    
    subgraph Platforms["External Learning Platforms"]
        P1["🎓 Coursera<br/>API v2"]
        P2["📚 Udemy<br/>API"]
        P3["🎯 Khan Academy<br/>API"]
        P4["📖 edX<br/>API"]
    end
    
    User <-->|Study| SSB
    User <-->|Connect| API_Bridge
    
    API_Bridge <-->|Sync Progress| P1
    API_Bridge <-->|Sync Progress| P2
    API_Bridge <-->|Sync Progress| P3
    API_Bridge <-->|Sync Progress| P4
    
    P1 <-->|Bidirectional<br/>Sync| SSB
    P2 <-->|Bidirectional<br/>Sync| SSB
    P3 <-->|Bidirectional<br/>Sync| SSB
    P4 <-->|Bidirectional<br/>Sync| SSB
    
    SSB -->|Unified View| Dashboard["🎯 Unified Dashboard<br/>Aggregate Progress<br/>Cross-Platform<br/>Recommendations"]
    
    Dashboard --> User
    
    style User fill:#e1f5ff
    style SSB fill:#fff9c4
    style API_Bridge fill:#f3e5f5
    style Platforms fill:#e8f5e9
    style Dashboard fill:#ffe0b2
```

## 11. Collaboration & Study Groups

```mermaid
graph TB
    subgraph Users["Study Group Members"]
        U1["👨 User A<br/>Creator"]
        U2["👩 User B<br/>Member"]
        U3["👨 User C<br/>Member"]
        U4["👩 User D<br/>Member"]
    end
    
    subgraph Group["Study Group:<br/>Biology 2024"]
        GInfo["📝 Group Info<br/>Name<br/>Description<br/>Created Date"]
        Notes["📋 Shared Notes:<br/>Photosynthesis<br/>Cell Structure<br/>DNA Replication"]
    end
    
    subgraph Features["Group Features"]
        F1["👁️ View Member<br/>Progress"]
        F2["💬 Discuss Topics"]
        F3["📊 Compare Scores"]
        F4["📅 Schedule<br/>Study Sessions"]
    end
    
    U1 -->|Creates| Group
    U2 -->|Joins| Group
    U3 -->|Joins| Group
    U4 -->|Joins| Group
    
    Group -->|Contains| GInfo
    Group -->|Contains| Notes
    Group -->|Enables| Features
    
    U1 -->|View| F1
    U2 -->|Contribute| Notes
    U3 -->|Share| F2
    U4 -->|Track| F3
    
    Notes -->|Shows in| F3
    
    style Users fill:#e1f5ff
    style Group fill:#fff9c4
    style Features fill:#c8e6c9
```

---

## Architecture Summary

### Layer Structure
1. **Presentation Layer** (Streamlit UI)
2. **API Layer** (FastAPI endpoints)
3. **Business Logic** (AI algorithms, adaptations)
4. **AI Layer** (OpenAI GPT integration)
5. **Data Layer** (SQLite database)

### Data Flow
- User interacts with Streamlit UI
- UI sends HTTP requests to FastAPI backend
- Backend applies business logic
- Calls OpenAI APIs for content generation
- Stores/retrieves data from SQLite
- Returns results to UI for visualization

### Key Algorithms
1. **Adaptive Learning**: Adjusts difficulty based on score
2. **Spaced Repetition**: Schedules reviews at optimal intervals
3. **Learning Style Customization**: Generates content matching preference
4. **Progress Analytics**: Calculates comprehensive metrics
5. **Recommendation Engine**: Suggests next steps based on performance

