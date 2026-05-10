from backend.database import (
    create_study_group, add_member_to_group, get_user_groups,
    get_group_members, save_shared_note, get_group_notes
)


def create_new_group(group_name, created_by, description=""):
    """Create a new study group"""
    group_id = create_study_group(group_name, created_by, description)
    # Add creator as first member
    add_member_to_group(group_id, created_by)
    return group_id


def invite_member(group_id, user_id):
    """Add a member to study group"""
    add_member_to_group(group_id, user_id)
    return True


def get_my_groups(user_id):
    """Get all groups user is member of"""
    return get_user_groups(user_id)


def get_group_info(group_id):
    """Get group members and recent notes"""
    members = get_group_members(group_id)
    notes = get_group_notes(group_id)
    return {
        "members": members,
        "recent_notes": notes[:10]  # Last 10 notes
    }


def share_note(group_id, user_id, title, content):
    """Share a note with study group"""
    save_shared_note(group_id, user_id, title, content)
    return True


def get_collaborative_progress(group_id):
    """Get combined progress stats of all group members"""
    members = get_group_members(group_id)
    progress_data = {
        "total_members": len(members),
        "group_performance": {}
    }
    return progress_data
