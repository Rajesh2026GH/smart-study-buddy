# Smart Study Buddy 🎓 - Complete Feature Guide

A comprehensive AI-powered learning platform that adapts to your learning style and helps you master any subject.

## ✨ Features Implemented

### 1. **Core Learning Features** ✅
- 📚 **PDF Text Extraction**: Upload study materials and automatically extract text
- 🔍 **Concept Extraction**: AI identifies key concepts from study materials
- 🎯 **Adaptive Quiz Generation**: Creates quizzes at multiple difficulty levels
- 💡 **Intelligent Topic Explanations**: Explains concepts in detail with examples
- ✅ **Answer Evaluation**: Grades quizzes and provides feedback
- 📊 **Progress Tracking**: Monitors learning progress over time

### 2. **Learning Styles Support** ✅
Three distinct learning styles supported:
- **Visual**: Diagrams, flowcharts, visual descriptions
- **Auditory**: Step-by-step verbal explanations, conversational tone
- **Kinesthetic**: Hands-on activities, practical examples, real-world applications

Each feature (quizzes, explanations) can be customized for your preferred learning style.

### 3. **User Management & Authentication** ✅
- 🔐 User registration and secure login
- 🔒 JWT token-based authentication
- 🔑 Password hashing with bcrypt
- 👤 User profiles with preferences
- ⚙️ Customizable learning settings

### 4. **Personalized Learning Preferences** ✅
- 🎨 Select preferred learning style (visual/auditory/kinesthetic)
- ⏰ Set daily study goals (15-300 minutes)
- 🔔 Toggle notification preferences
- 📊 Automatic recommendations based on performance

### 5. **Progress & Analytics Dashboard** ✅
- 📈 Comprehensive dashboard with key metrics:
  - Total tests completed
  - Average score across all topics
  - Study streak counter
  - Best and worst topics
- 📊 Topic-by-topic performance breakdown
- 📉 Weekly progress trends
- 🎯 Performance visualization charts

### 6. **Study Group Collaboration** ✅
- 👥 Create and manage study groups
- 👫 Invite members to join groups
- 📝 Share notes with group members
- 👁️ View group member progress
- 💬 Collaborative learning environment

### 7. **Platform Integration** ✅
- 🔗 Connect with external learning platforms:
  - Coursera
  - Khan Academy
  - Udemy
  - edX
- 📚 Import course content from platforms
- 🔄 Sync learning progress across platforms
- 🌐 Seamless multi-platform learning

### 8. **Spaced Repetition Scheduling** ✅
- 📅 Automatic schedule generation based on weak areas
- ⏱️ Intelligent spacing intervals (1, 3, 7 days)
- 🎓 Optimized for long-term retention
- 📋 Personalized study plans

### 9. **Adaptive Learning Algorithms** ✅
- 🧠 Adjusts difficulty based on performance:
  - Beginner: Score < 60%
  - Intermediate: Score 60-85%
  - Advanced: Score > 85%
- 🎯 Smart recommendations based on performance
- 📊 Continuous difficulty adjustment

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Database**: SQLite3
- **AI/LLM**: OpenAI GPT-3.5/GPT-4
- **Authentication**: JWT + bcrypt
- **Visualization**: Plotly, Pandas
- **PDF Processing**: PyPDF2

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Dependencies listed in requirements.txt

## 🚀 Installation & Setup

### 1. Clone and Setup Environment
```bash
cd smart-study-buddy
python -m venv venv
source venv/Scripts/activate  # Windows
# or: source venv/bin/activate  # macOS/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy example to .env and update with your API key
cp .env.example .env

# Edit .env and add:
# OPENAI_API_KEY=your_key_here
# OPENAI_API_MODEL=gpt-3.5-turbo
# SECRET_KEY=your_secret_key
```

### 4. Initialize Database
```bash
mkdir -p database
python -c "from backend.database import *; print('Database initialized')"
```

### 5. Start Services

**Terminal 1 - Backend API:**
```bash
python -m uvicorn backend.api:app --reload
# Server runs on http://127.0.0.1:8000
```

**Terminal 2 - Frontend:**
```bash
streamlit run app.py
# App opens on http://localhost:8501
```

## 📖 How to Use

### 1. **Authentication**
- Sign up for a new account or login
- Set your learning preferences
- Start learning!

### 2. **Study Phase**
- Upload PDF or paste learning material
- Click "Extract Concepts" to identify key topics
- Select difficulty and learning style
- Click "Generate Quiz" for practice questions

### 3. **Explanation**
- Enter any topic you want to understand better
- Choose your preferred learning style
- Get customized explanations with examples
- Request explanations in all three learning styles if needed

### 4. **Quiz & Evaluation**
- Complete the quiz
- Submit your answers
- Get instant evaluation and feedback
- See your learning level and recommendations
- View personalized study schedule

### 5. **Track Progress**
- Visit the Dashboard tab to see all your metrics
- Check Analytics tab for advanced statistics
- View weekly trends and performance
- Get personalized recommendations

### 6. **Collaborate**
- Create or join study groups
- Share notes with group members
- See how group members are performing
- Learn together!

### 7. **Integrate Platforms**
- Connect your Coursera, Khan Academy, or other platform accounts
- Import courses and materials
- Sync progress across platforms

## 📊 API Endpoints

### Authentication
- `POST /auth/signup` - Create new account
- `POST /auth/login` - Login and get token

### Learning
- `POST /generate-quiz` - Generate quiz (with learning style)
- `POST /generate-varied-quizzes` - All difficulty levels & styles
- `POST /explain` - Explain topic (with learning style)
- `POST /extract-concepts` - Extract key concepts
- `POST /evaluate` - Evaluate answers and save progress

### User Settings
- `GET /preferences` - Get user preferences
- `PUT /preferences` - Update preferences

### Analytics & Progress
- `GET /dashboard` - Get dashboard data
- `GET /progress` - Get user progress
- `GET /stats/by-topic` - Topic breakdown
- `GET /recommendations` - Get recommendations
- `GET /weekly-progress` - Weekly trends

### Study Groups
- `POST /groups/create` - Create new group
- `GET /groups` - Get user's groups
- `POST /groups/{group_id}/invite` - Invite member
- `GET /groups/{group_id}/info` - Get group info
- `POST /groups/{group_id}/notes` - Share note
- `GET /groups/{group_id}/notes` - Get shared notes

### Platform Integration
- `POST /platforms/connect` - Connect external platform
- `GET /platforms` - Get connected platforms
- `GET /platforms/{platform_name}/courses` - Get courses

## 🎨 UI Features

- **7 Main Tabs**:
  1. 📚 Study Materials - Upload, extract, quiz, explain
  2. 📊 Dashboard - View key metrics
  3. 👥 Study Groups - Collaborate with others
  4. ⚙️ Preferences - Customize settings
  5. 🔗 Platforms - Manage integrations
  6. 📈 Analytics - Advanced statistics
  7. 💡 Recommendations - Personalized suggestions

- **Authentication UI** - Clean login/signup interface
- **Responsive Design** - Works on desktop and tablet
- **Data Visualization** - Charts and graphs for progress tracking
- **Session Management** - Secure user sessions with JWT

## 📈 Advanced Features

### Spaced Repetition
- Automatically schedules review sessions
- Uses evidence-based intervals (1, 3, 7 days)
- Focuses on weak areas
- Maximizes retention

### Adaptive Difficulty
- Adjusts quiz difficulty based on performance
- Provides easier material for struggling students
- Challenges advanced learners
- Continuously adapts to progress

### Learning Style Customization
- All content adapts to learning style
- Multiple explanation options
- Style-specific quiz questions
- Save preference for consistent experience

### Collaborative Learning
- Study groups for peer support
- Shared note-taking
- Group performance tracking
- Social learning motivation

## 🔒 Security Features

- Secure password hashing (bcrypt)
- JWT-based authentication
- Session management
- Secure API endpoints
- Environment variable configuration

## 📝 Database Schema

**Users** - Store user accounts
**User Preferences** - Learning style, goals, notifications
**Progress** - Test results and performance data
**Study Groups** - Collaboration spaces
**Group Members** - Group membership tracking
**Shared Notes** - Collaborative notes
**Platform Integrations** - External platform connections

## 🎓 Best Practices

1. **Start with assessments** - Take baseline quizzes to identify weak areas
2. **Follow your learning style** - Choose the style that works best for you
3. **Use spaced repetition** - Don't skip the scheduled review sessions
4. **Join groups** - Collaborative learning improves retention
5. **Review analytics** - Check dashboard regularly for insights
6. **Set realistic goals** - Adjust daily study time based on your schedule
7. **Be consistent** - Study regularly to build streaks and momentum

## 🐛 Troubleshooting

**API Connection Error**
- Make sure backend is running: `python -m uvicorn backend.api:app --reload`
- Check that port 8000 is available

**Authentication Issues**
- Verify .env file has SECRET_KEY set
- Check database is initialized
- Try signing up again

**OpenAI Errors**
- Verify OPENAI_API_KEY is set in .env
- Check API key is valid and has credits
- Verify OPENAI_API_MODEL is correctly specified

**Database Errors**
- Delete studybuddy.db and restart to reinitialize
- Check database directory exists: `mkdir -p database`

## 🚀 Future Enhancements

- Mobile app version
- Real-time collaboration features
- Video content analysis
- Speech-to-text for auditory learners
- Advanced NLP for deeper content analysis
- Gamification features
- Teacher dashboard
- Student performance reports

## 📞 Support

For issues or feature requests, please check:
1. .env configuration
2. API server status
3. Database connectivity
4. OpenAI API access

## 📄 License

This project is open source and available for educational purposes.

---

**Happy Learning! 🎓📚**
