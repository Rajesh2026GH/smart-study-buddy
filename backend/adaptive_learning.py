def get_learning_level(score):

    if score >= 85:
        return "Advanced"

    elif score >= 60:
        return "Intermediate"

    else:
        return "Beginner"



def get_recommendation(score):

    if score >= 85:
        return "Proceed to advanced topics"

    elif score >= 60:
        return "Practice medium difficulty questions"

    else:
        return "Revise fundamentals and repeat quizzes"


def get_recommended_difficulty(score):
    """
    Map learning level to recommended quiz difficulty
    
    Returns: "easy", "medium", or "hard"
    """
    level = get_learning_level(score)
    
    difficulty_map = {
        "Beginner": "easy",
        "Intermediate": "medium",
        "Advanced": "hard"
    }
    
    return difficulty_map.get(level, "medium")