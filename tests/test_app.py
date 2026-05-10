import os
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend import api


client = TestClient(api.app)


def fake_generate_quiz(text, difficulty="medium", learning_style="visual"):
    return (
        "1. What is the study goal?\n"
        "A. Practice\nB. Sleep\nC. Forget\nD. None\n"
        "Answer: A\n"
        "Explanation: Practice helps learning."
    )


def fake_explain_topic(topic, learning_style="visual"):
    return f"{learning_style.title()} explanation for {topic}."


def fake_explain_with_multiple_styles(topic):
    return {
        "visual": f"Visual explanation for {topic}.",
        "auditory": f"Auditory explanation for {topic}.",
        "kinesthetic": f"Kinesthetic explanation for {topic}."
    }


def fake_extract_concepts(text):
    return "- concept one\n- concept two"


def fake_evaluate_answers(quiz, user_answers):
    return {
        "score": 95,
        "correct_answers": "A, B, C, D",
        "weak_areas": "None",
        "improvement_suggestions": "Keep practicing."
    }


def get_sample_content_from_path():
    target_dir = Path(r"D:\AI\GenAI\Code\Files")
    if not target_dir.exists() or not target_dir.is_dir():
        pytest.skip("Sample file directory not available")

    for ext in ["*.txt", "*.md", "*.py", "*.json", "*.csv"]:
        for path in target_dir.glob(ext):
            try:
                return path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

    pytest.skip(r"No readable sample text file found in D:\AI\GenAI\Code\Files")


def test_full_learning_flow(monkeypatch):
    # Patch LLM-dependent functions to avoid external API calls
    monkeypatch.setattr(api, "generate_quiz", fake_generate_quiz)
    monkeypatch.setattr(api, "explain_topic", fake_explain_topic)
    monkeypatch.setattr(api, "explain_with_multiple_styles", fake_explain_with_multiple_styles)
    monkeypatch.setattr(api, "extract_concepts", fake_extract_concepts)
    monkeypatch.setattr(api, "evaluate_answers", fake_evaluate_answers)

    username = f"test_{uuid.uuid4().hex[:8]}"
    password = "TestPass123!"
    email = f"{username}@example.com"

    # Sign up a new user
    signup_response = client.post(
        "/auth/signup",
        json={"username": username, "email": email, "password": password},
    )
    assert signup_response.status_code == 200
    signup_data = signup_response.json()
    assert signup_data["username"] == username
    assert "access_token" in signup_data
    token = signup_data["access_token"]
    user_id = signup_data["user_id"]

    headers = {"Authorization": f"Bearer {token}"}

    # Login with the same user
    login_response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["username"] == username

    # Get default preferences
    pref_response = client.get("/preferences", headers=headers)
    assert pref_response.status_code == 200
    assert pref_response.json()["learning_style"] == "visual"

    # Update preferences
    update_response = client.put(
        "/preferences",
        json={"learning_style": "auditory", "daily_study_goal": 80, "notification_enabled": False},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["message"] == "Preferences updated successfully"

    # Verify updated preferences
    pref_response = client.get("/preferences", headers=headers)
    assert pref_response.status_code == 200
    pref_data = pref_response.json()
    assert pref_data["learning_style"] == "auditory"
    assert pref_data["daily_study_goal"] == 80
    assert pref_data["notification_enabled"] in (0, False)

    # Extract concepts from study material
    concept_response = client.post(
        "/extract-concepts",
        json={"text": "Chapter 1: AI fundamentals."},
        headers=headers,
    )
    assert concept_response.status_code == 200
    assert "concept one" in concept_response.json()["concepts"]

    # Generate a custom quiz
    quiz_response = client.post(
        "/generate-quiz",
        json={"text": "AI overview", "difficulty": "easy", "learning_style": "visual"},
        headers=headers,
    )
    assert quiz_response.status_code == 200
    assert "What is the study goal" in quiz_response.json()["quiz"]

    # Generate multi-style explanations
    explain_response = client.post(
        "/explain",
        json={"topic": "Reinforcement Learning", "multiple_styles": True},
        headers=headers,
    )
    assert explain_response.status_code == 200
    explanation_data = explain_response.json()["explanations"]
    assert explanation_data["visual"].startswith("Visual explanation")
    assert explanation_data["auditory"].startswith("Auditory explanation")
    assert explanation_data["kinesthetic"].startswith("Kinesthetic explanation")

    # Evaluate answers and save progress
    evaluate_response = client.post(
        "/evaluate",
        json={
            "user_id": user_id,
            "topic": "AI basics",
            "quiz": quiz_response.json()["quiz"],
            "user_answers": "A, B, C, D",
            "score": 95,
            "weak_area": "None",
        },
        headers=headers,
    )
    assert evaluate_response.status_code == 200
    eval_data = evaluate_response.json()
    assert eval_data["learning_level"] == "Advanced"
    assert eval_data["recommendation"] == "Proceed to advanced topics"
    assert isinstance(eval_data["schedule"], list)

    # Fetch progress for the user
    progress_response = client.get("/progress", headers=headers)
    assert progress_response.status_code == 200
    assert len(progress_response.json()["progress"]) >= 1

    # Get dashboard data
    dashboard_response = client.get("/dashboard", headers=headers)
    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()
    assert "total_tests" in dashboard
    assert "study_streak" in dashboard

    # Create and list study groups
    group_response = client.post(
        "/groups/create",
        json={"group_name": "Test Study Group", "description": "Group for study sessions"},
        headers=headers,
    )
    assert group_response.status_code == 200
    assert group_response.json()["message"] == "Study group created successfully"

    groups_response = client.get("/groups", headers=headers)
    assert groups_response.status_code == 200
    assert any("Test Study Group" in str(group) for group in groups_response.json()["groups"])

    # Connect a learning platform
    platform_response = client.post(
        "/platforms/connect",
        json={"platform_name": "coursera", "api_token": "fake-token"},
        headers=headers,
    )
    assert platform_response.status_code == 200
    assert "Connected to coursera" in platform_response.json()["message"]

    integrations_response = client.get("/platforms", headers=headers)
    assert integrations_response.status_code == 200
    assert any("coursera" in str(item) for item in integrations_response.json()["connected_platforms"])


def test_seeded_users_dashboard_and_personalized_schedule(monkeypatch):
    # Use seeded users from the database
    seeded_users = [
        {"username": "alice_smith", "password": "Alice123!"},
        {"username": "bob_johnson", "password": "Bob456!"},
    ]

    monkeypatch.setattr(api, "generate_quiz", fake_generate_quiz)
    monkeypatch.setattr(api, "explain_topic", fake_explain_topic)
    monkeypatch.setattr(api, "explain_with_multiple_styles", fake_explain_with_multiple_styles)
    monkeypatch.setattr(api, "extract_concepts", fake_extract_concepts)
    monkeypatch.setattr(api, "evaluate_answers", fake_evaluate_answers)

    sample_text = None
    try:
        sample_text = get_sample_content_from_path()
    except pytest.skip.Exception:
        sample_text = "Sample textbook content for test case."

    for user in seeded_users:
        login_response = client.post(
            "/auth/login",
            json={"username": user["username"], "password": user["password"]},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        user_id = login_response.json()["user_id"]
        headers = {"Authorization": f"Bearer {token}"}

        dashboard_response = client.get("/dashboard", headers=headers)
        assert dashboard_response.status_code == 200
        dashboard_data = dashboard_response.json()
        assert "total_tests" in dashboard_data
        assert "study_streak" in dashboard_data

        recommendations_response = client.get("/recommendations", headers=headers)
        assert recommendations_response.status_code == 200
        recs = recommendations_response.json()["recommendations"]
        assert isinstance(recs, dict)
        assert "summary" in recs
        assert "performance_insights" in recs
        assert "learning_style_tips" in recs
        assert "weak_area_focus" in recs
        assert "action_items" in recs

        concept_response = client.post(
            "/extract-concepts",
            json={"text": sample_text[:1500]},
            headers=headers,
        )
        assert concept_response.status_code == 200
        assert "concept one" in concept_response.json()["concepts"]

        quiz_response = client.post(
            "/generate-quiz",
            json={"text": sample_text[:1500], "difficulty": "medium", "learning_style": "visual"},
            headers=headers,
        )
        assert quiz_response.status_code == 200
        assert "What is the study goal" in quiz_response.json()["quiz"]

        evaluate_response = client.post(
            "/evaluate",
            json={
                "user_id": user_id,
                "topic": "Textbook Review",
                "quiz": quiz_response.json()["quiz"],
                "user_answers": "A, B, C, D",
                "score": 82,
                "weak_area": "Review Topic",
            },
            headers=headers,
        )
        assert evaluate_response.status_code == 200
        schedule_data = evaluate_response.json()["schedule"]
        assert isinstance(schedule_data, list)
        assert len(schedule_data) > 0
        assert all("revision_date" in item for item in schedule_data)

        progress_response = client.get("/progress", headers=headers)
        assert progress_response.status_code == 200
        assert isinstance(progress_response.json()["progress"], list)
        assert len(progress_response.json()["progress"]) >= 1

        # Optional: verify the personalized schedule is roughly based on the weak area
        assert any("Review Topic" in str(item) for item in schedule_data)


def test_existing_user_flow(monkeypatch):
    # Use a seeded existing user if available, otherwise create it
    username = "alice_smith"
    password = "Alice123!"
    email = "alice@studybuddy.com"

    # Patch LLM-dependent functions for the flow
    monkeypatch.setattr(api, "generate_quiz", fake_generate_quiz)
    monkeypatch.setattr(api, "explain_topic", fake_explain_topic)
    monkeypatch.setattr(api, "explain_with_multiple_styles", fake_explain_with_multiple_styles)
    monkeypatch.setattr(api, "extract_concepts", fake_extract_concepts)
    monkeypatch.setattr(api, "evaluate_answers", fake_evaluate_answers)

    login_response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )

    if login_response.status_code == 401:
        signup_response = client.post(
            "/auth/signup",
            json={"username": username, "email": email, "password": password},
        )
        assert signup_response.status_code == 200
        login_response = client.post(
            "/auth/login",
            json={"username": username, "password": password},
        )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Confirm the existing user can fetch preferences and dashboard data
    pref_response = client.get("/preferences", headers=headers)
    assert pref_response.status_code == 200

    dashboard_response = client.get("/dashboard", headers=headers)
    assert dashboard_response.status_code == 200
    assert "study_streak" in dashboard_response.json()

    # Confirm the user can perform a new concept extraction and quiz generation
    concept_response = client.post(
        "/extract-concepts",
        json={"text": "Sample text for existing user."},
        headers=headers,
    )
    assert concept_response.status_code == 200
    assert "concept one" in concept_response.json()["concepts"]

    quiz_response = client.post(
        "/generate-quiz",
        json={"text": "Existing user content", "difficulty": "medium", "learning_style": "kinesthetic"},
        headers=headers,
    )
    assert quiz_response.status_code == 200
    assert "What is the study goal" in quiz_response.json()["quiz"]
