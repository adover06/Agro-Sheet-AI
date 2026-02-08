"""
Schedule data structures and utilities
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json


@dataclass
class TimeBlock:
    """Represents a 30-minute time block in the schedule"""
    start_time: str  # HH:MM format
    end_time: str    # HH:MM format
    task_name: Optional[str] = None
    task_id: Optional[str] = None
    category: str = "empty"  # projects, school, personal, breaks, fixed_events
    color: Optional[str] = None
    is_flexible: bool = True
    duration_blocks: int = 1  # How many 30-min blocks this task occupies


@dataclass
class DailySchedule:
    """Represents a full day's schedule"""
    day_name: str  # Monday, Tuesday, etc.
    date: Optional[str] = None  # YYYY-MM-DD
    blocks: List[TimeBlock] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "day": self.day_name,
            "date": self.date,
            "blocks": [
                {
                    "time": f"{b.start_time}-{b.end_time}",
                    "task": b.task_name,
                    "category": b.category,
                    "color": b.color,
                    "duration_blocks": b.duration_blocks
                }
                for b in self.blocks
            ]
        }


@dataclass
class WeeklySchedule:
    """Represents a full week's schedule"""
    week_start_date: Optional[str] = None
    schedules: Dict[str, DailySchedule] = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "week_start_date": self.week_start_date,
            "days": {day: schedule.to_dict() for day, schedule in self.schedules.items()}
        }


@dataclass
class Task:
    """Represents a task from Google Tasks"""
    id: str
    title: str
    description: Optional[str] = None
    importance: str = "normal"  # high, normal, low
    due_date: Optional[str] = None
    estimated_duration: Optional[int] = None  # minutes
    has_time_constraint: bool = False
    constraint_start_time: Optional[str] = None  # HH:MM
    constraint_end_time: Optional[str] = None    # HH:MM
    category: str = "school"  # projects, school, personal
    is_starred: bool = True


def create_empty_schedule() -> WeeklySchedule:
    """Create an empty weekly schedule with all time blocks"""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedule = WeeklySchedule()
    
    for day in days:
        daily = DailySchedule(day_name=day)
        
        # Create 30-minute blocks from 9 AM to 12 AM (midnight)
        current_hour = 9
        current_minute = 0
        
        while current_hour < 24:
            start_time = f"{current_hour:02d}:{current_minute:02d}"
            current_minute += 30
            
            if current_minute >= 60:
                current_minute = 0
                current_hour += 1
            
            end_time = f"{current_hour:02d}:{current_minute:02d}"
            
            block = TimeBlock(
                start_time=start_time,
                end_time=end_time,
                task_name=None,
                category="empty"
            )
            daily.blocks.append(block)
        
        schedule.schedules[day] = daily
    
    return schedule


def save_schedule_to_json(schedule: WeeklySchedule, filepath: str):
    """Save weekly schedule to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(schedule.to_dict(), f, indent=2)


def load_schedule_from_json(filepath: str) -> WeeklySchedule:
    """Load weekly schedule from JSON file"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    schedule = WeeklySchedule(week_start_date=data.get("week_start_date"))
    
    for day_name, day_data in data.get("days", {}).items():
        daily = DailySchedule(day_name=day_name, date=day_data.get("date"))
        
        for block_data in day_data.get("blocks", []):
            time_range = block_data.get("time", "").split("-")
            block = TimeBlock(
                start_time=time_range[0] if len(time_range) > 0 else "00:00",
                end_time=time_range[1] if len(time_range) > 1 else "00:30",
                task_name=block_data.get("task"),
                category=block_data.get("category", "empty"),
                color=block_data.get("color")
            )
            daily.blocks.append(block)
        
        schedule.schedules[day_name] = daily
    
    return schedule
