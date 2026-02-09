"""
Fixed events configuration loader
"""
import yaml
from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class FixedEvent:
    """Represents a fixed or flexible daily event"""
    name: str
    days: List[str]  # Monday-Sunday or "Daily"
    start_time: Optional[str] = None  # HH:MM
    end_time: Optional[str] = None    # HH:MM
    duration: Optional[int] = None    # minutes (for flexible events)
    flexible: bool = False
    is_free: bool = False  # free time vs. committed time
    category: str = "personal"
    preferred_start: Optional[str] = None  # HH:MM - preferred earliest time
    preferred_end: Optional[str] = None    # HH:MM - preferred latest time


def load_fixed_events_config(filepath: str) -> List[FixedEvent]:
    """
    Load fixed events from YAML configuration file
    """
    events = []
    
    try:
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
        
        if not config or 'fixed_events' not in config:
            return events
        
        for event_data in config['fixed_events']:
            event = FixedEvent(
                name=event_data.get('name', ''),
                days=event_data.get('days', []),
                start_time=event_data.get('start_time'),
                end_time=event_data.get('end_time'),
                duration=event_data.get('duration'),
                flexible=event_data.get('flexible', False),
                is_free=event_data.get('is_free', False),
                category=event_data.get('category', 'personal'),
                preferred_start=event_data.get('preferred_start'),
                preferred_end=event_data.get('preferred_end')
            )
            events.append(event)
    
    except FileNotFoundError:
        print(f"Warning: Fixed events config file not found at {filepath}")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config: {e}")
    
    return events


def get_events_for_day(events: List[FixedEvent], day_name: str) -> List[FixedEvent]:
    """
    Get all fixed events that apply to a specific day
    """
    matching_events = []
    
    for event in events:
        if 'Daily' in event.days or day_name in event.days:
            matching_events.append(event)
    
    return matching_events
