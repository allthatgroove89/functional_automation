"""
Objective Notifier Module
Handles emailing user with unsupported objectives
"""

from notifications import notify_unsupported


def notify_unsupported_objectives(unsupported_objectives):
    """
    Email user with the list of unsupported objectives that he requested
    
    Args:
        unsupported_objectives: List of unsupported objectives
    
    Returns:
        bool: True if notification sent successfully, False otherwise
    """
    if not unsupported_objectives:
        print("[OK] No unsupported objectives to notify about")
        return True
    
    print(f"Notifying user about {len(unsupported_objectives)} unsupported objectives...")
    
    # Extract objective details for notification
    unsupported_details = []
    for objective in unsupported_objectives:
        details = {
            'id': objective.get('id', 'Unknown'),
            'name': objective.get('name', 'Unknown'),
            'app': objective.get('app', 'Unknown'),
            'reason': 'Not supported in current system'
        }
        unsupported_details.append(details)
    
    # Send notification
    try:
        notify_unsupported(unsupported_details)
        print("[OK] Notification sent successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send notification: {str(e)}")
        return False


def create_unsupported_summary(unsupported_objectives):
    """
    Create a summary of unsupported objectives for notification
    
    Args:
        unsupported_objectives: List of unsupported objectives
    
    Returns:
        str: Formatted summary string
    """
    if not unsupported_objectives:
        return "No unsupported objectives found."
    
    summary = f"Found {len(unsupported_objectives)} unsupported objectives:\n\n"
    
    for i, objective in enumerate(unsupported_objectives, 1):
        summary += f"{i}. {objective.get('name', 'Unknown')} (ID: {objective.get('id', 'Unknown')})\n"
        summary += f"   App: {objective.get('app', 'Unknown')}\n"
        summary += f"   Reason: Not supported in current system\n\n"
    
    return summary
