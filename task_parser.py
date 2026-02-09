"""
Task parsing and time-aware utilities
"""
import re
from typing import Optional, Tuple
from schedule_models import Task


def parse_time_from_text(text: str) -> Optional[Tuple[str, str]]:
    """
    Extract time range from text like '9-10am' or '09:00-10:00'
    Returns: (start_time, end_time) in HH:MM format or None
    """
    # Pattern for times like "9-10am", "9:30-10:30am", "09:00-10:00"
    patterns = [
        r'(\d{1,2}):?(\d{2})?\s*-\s*(\d{1,2}):?(\d{2})?\s*(am|pm)?',  # 9:00-10:00 or 9-10
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start_hour = int(match.group(1))
            start_minute = int(match.group(2)) if match.group(2) else 0
            end_hour = int(match.group(3))
            end_minute = int(match.group(4)) if match.group(4) else 0
            am_pm = match.group(5)
            
            # Handle AM/PM conversion
            if am_pm and am_pm.lower() == 'pm' and start_hour < 12:
                start_hour += 12
                end_hour += 12
            
            start_time = f"{start_hour:02d}:{start_minute:02d}"
            end_time = f"{end_hour:02d}:{end_minute:02d}"
            
            return (start_time, end_time)
    
    return None


def estimate_duration_from_title(title: str) -> int:
    """
    Estimate task duration in minutes based on title keywords
    Returns: estimated duration in minutes
    """
    title_lower = title.lower()
    
    # Quick tasks (15-30 minutes)
    quick_keywords = ['quick', 'short', 'brief', 'email', 'message', 'call']
    if any(kw in title_lower for kw in quick_keywords):
        return 30
    
    # Medium tasks (30-60 minutes)
    medium_keywords = ['review', 'read', 'prepare', 'plan', 'organize', 'clean']
    if any(kw in title_lower for kw in medium_keywords):
        return 60
    
    # Project-related (1-2 hours)
    project_keywords = ['project', 'code', 'develop', 'design', 'build', 'write']
    if any(kw in title_lower for kw in project_keywords):
        return 90
    
    # Study/school (1-2 hours)
    school_keywords = ['study', 'homework', 'assignment', 'class', 'exam', 'research']
    if any(kw in title_lower for kw in school_keywords):
        return 90
    
    # Default: 45 minutes
    return 45


def round_to_nearest_30_min(time_str: str, round_up: bool = False) -> str:
    """
    Round time to nearest 30-minute block
    E.g., 9:15 -> 9:00, 9:25 -> 9:30
    """
    hours, minutes = map(int, time_str.split(':'))
    
    if round_up:
        if minutes > 0:
            hours += 1
            minutes = 0
        if minutes != 0:
            minutes = 30
    else:
        if minutes > 0 and minutes <= 30:
            minutes = 0
        elif minutes > 30:
            minutes = 30
    
    return f"{hours:02d}:{minutes:02d}"


def categorize_task(title: str, description: str = "") -> str:
    """
    Categorize task as projects, school, or personal
    """
    text = (title + " " + description).lower()
    
    project_keywords = ['project', 'code', 'develop', 'build', 'design', 'app', 'feature']
    school_keywords = ['class', 'homework', 'assignment', 'exam', 'study', 'course', 'lecture']
    personal_keywords = ['personal', 'prayer', 'cooking', 'exercise', 'health', 'family']
    
    if any(kw in text for kw in project_keywords):
        return 'projects'
    elif any(kw in text for kw in school_keywords):
        return 'school'
    elif any(kw in text for kw in personal_keywords):
        return 'personal'
    
    # Default: school if not specified
    return 'school'


def extract_duration_from_text(text: str) -> Optional[int]:
    """
    Extract duration from text like '1 hour', '2.5 hours', '30 mins'
    Returns: duration in minutes or None
    """
    # Pattern for "N hours" or "N.N hours"
    hour_pattern = r'(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)\b'
    hour_match = re.search(hour_pattern, text, re.IGNORECASE)
    if hour_match:
        hours = float(hour_match.group(1))
        return int(hours * 60)
        
    # Pattern for "N minutes"
    min_pattern = r'(\d+)\s*(?:minute|min|minutes|mins)\b'
    min_match = re.search(min_pattern, text, re.IGNORECASE)
    if min_match:
        minutes = int(min_match.group(1))
        return minutes
        
    return None


def parse_task_from_todo(todo_item: dict) -> Task:
    """
    Parse a task from Google Tasks API response
    """
    # Handle Google Tasks format
    title = todo_item.get('title', 'Untitled')
    
    # Google Tasks uses 'notes' field for description
    description = todo_item.get('notes', '')
    if description is None:
        description = ""
    
    # Check for time constraints in title or description
    full_text = title + " " + description
    time_constraint = parse_time_from_text(full_text)
    
    # Estimate duration:
    # 1. Check for time constraint range (e.g. 9-10am)
    # 2. Check for explicit duration string (e.g. 1 hour)
    # 3. Estimate based on keywords
    estimated_duration = None
    if time_constraint:
        start_h, start_m = map(int, time_constraint[0].split(':'))
        end_h, end_m = map(int, time_constraint[1].split(':'))
        # Calculate diff in minutes, handling day wrap if needed (though parser doesn't assume wrap here)
        diff_mins = (end_h * 60 + end_m) - (start_h * 60 + start_m)
        if diff_mins > 0:
            estimated_duration = diff_mins
    
    if not estimated_duration:
        # Check for explicit duration in text
        explicit_duration = extract_duration_from_text(full_text)
        if explicit_duration:
            estimated_duration = explicit_duration
        else:
            estimated_duration = estimate_duration_from_title(title)
    
    category = categorize_task(title, description)
    
    # Google Tasks doesn't have importance, check description for hints
    importance = 'normal'  # Default medium importance
    if 'important' in full_text.lower() or 'urgent' in full_text.lower():
        importance = 'high'
    elif 'low priority' in full_text.lower():
        importance = 'low'
    
    # Parse due date from Google Tasks format (YYYY-MM-DD)
    due_date = todo_item.get('due', None)
    
    return Task(
        id=todo_item.get('id', ''),
        title=title,
        description=description,
        importance=importance,
        estimated_duration=estimated_duration,
        has_time_constraint=time_constraint is not None,
        constraint_start_time=time_constraint[0] if time_constraint else None,
        constraint_end_time=time_constraint[1] if time_constraint else None,
        category=category,
        is_starred=True,
        due_date=due_date
    )
