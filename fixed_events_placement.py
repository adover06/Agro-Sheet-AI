"""
Fixed events scheduling logic
"""
from typing import List, Dict, Tuple
from config_loader import FixedEvent, get_events_for_day
from schedule_models import DailySchedule, WeeklySchedule, TimeBlock


def place_fixed_events(schedule: WeeklySchedule, fixed_events: List[FixedEvent]) -> Tuple[WeeklySchedule, List[Tuple[str, int]]]:
    """
    Place fixed events in the schedule
    Returns: (updated_schedule, list_of_flexible_events)
    
    Flexible events are returned separately for intelligent placement by the agent
    """
    flexible_events = []
    
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for day_name in days_of_week:
        daily_schedule = schedule.schedules[day_name]
        day_events = get_events_for_day(fixed_events, day_name)
        
        for event in day_events:
            if event.flexible:
                # Collect flexible events for later placement
                if event.duration:
                    flexible_events.append((event.name, event.duration))
            else:
                # Place fixed-time events immediately
                _place_fixed_time_event(daily_schedule, event)
    
    return schedule, flexible_events


def _place_fixed_time_event(daily_schedule: DailySchedule, event: FixedEvent):
    """
    Place a fixed-time event in a daily schedule
    """
    if not event.start_time or not event.end_time:
        return
    
    start_h, start_m = map(int, event.start_time.split(':'))
    end_h, end_m = map(int, event.end_time.split(':'))
    
    for block in daily_schedule.blocks:
        block_start_h, block_start_m = map(int, block.start_time.split(':'))
        block_end_h, block_end_m = map(int, block.end_time.split(':'))
        
        block_start_minutes = block_start_h * 60 + block_start_m
        block_end_minutes = block_end_h * 60 + block_end_m
        event_start_minutes = start_h * 60 + start_m
        event_end_minutes = end_h * 60 + end_m
        
        # Check if block overlaps with event
        if block_start_minutes >= event_start_minutes and block_end_minutes <= event_end_minutes:
            block.task_name = event.name
            block.category = event.category
            block.is_flexible = False
            block.color = None  # Will be set by color scheme
