from datetime import datetime, timedelta



def generate_personalized_schedule(weak_topics):

    schedule = []

    current_date = datetime.now()

    for topic in weak_topics:

        # spaced repetition intervals
        intervals = [1, 3, 7]

        for days in intervals:

            study_date = current_date + timedelta(days=days)

            schedule.append({
                "topic": topic,
                "revision_date": study_date.strftime("%Y-%m-%d")
            })

    return schedule