"""
Demo mode to test scheduling without authentication
"""
import json
from schedule_models import Task, create_empty_schedule, save_schedule_to_json
from task_parser import parse_time_from_text, categorize_task
from config_loader import load_fixed_events_config
from fixed_events_placement import place_fixed_events
from scheduling_agent import SchedulingAgent
from datetime import datetime, timedelta


def demo_schedule():
    """
    Create a demo schedule with sample tasks and fixed events
    Useful for testing without authentication
    """
    
    print("🎯 Demo: Creating sample schedule...")
    
    # Sample tasks
    sample_tasks = [
        Task(
            id="1",
            title="Work on AI project 2-4pm",
            description="Build the scheduling agent",
            estimated_duration=120,
            constraint_start_time="14:00",
            constraint_end_time="16:00",
            has_time_constraint=True,
            category="projects",
            importance="high"
        ),
        Task(
            id="2",
            title="React homework",
            description="Complete assignment 5",
            estimated_duration=90,
            category="school",
            importance="normal"
        ),
        Task(
            id="3",
            title="Code review for team",
            description="Review pull requests",
            estimated_duration=45,
            category="projects",
            importance="high"
        ),
        Task(
            id="4",
            title="Calculus study session",
            description="Study chapters 5-7",
            estimated_duration=120,
            category="school",
            importance="normal"
        ),
        Task(
            id="5",
            title="Personal project 7pm-9pm",
            description="Work on side project",
            constraint_start_time="19:00",
            constraint_end_time="21:00",
            has_time_constraint=True,
            estimated_duration=120,
            category="projects",
            importance="high"
        ),
        Task(
            id="6",
            title="Quick email check",
            description="Respond to messages",
            estimated_duration=15,
            category="personal",
            importance="low"
        ),
    ]
    
    # Create empty schedule
    schedule = create_empty_schedule()
    
    # Set week start date
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    schedule.week_start_date = week_start.strftime("%Y-%m-%d")
    
    # Load and place fixed events
    fixed_events_config = load_fixed_events_config('config/fixed_events.yaml')
    schedule, flexible_events = place_fixed_events(schedule, fixed_events_config)
    
    print(f"✓ Placed fixed events")
    print(f"✓ Flexible events to place: {[e[0] for e in flexible_events]}")
    
    # Run scheduling agent
    agent = SchedulingAgent(schedule)
    success = agent.schedule_tasks(sample_tasks, flexible_events)
    
    if success:
        print("✓ Tasks scheduled successfully")
    
    # Save to JSON
    save_schedule_to_json(schedule, 'schedule_demo.json')
    print("✓ Saved demo schedule to schedule_demo.json")
    
    # Print summary
    print("\n📅 Demo Schedule Summary:")
    print("=" * 80)
    
    with open('schedule_demo.json', 'r') as f:
        schedule_data = json.load(f)
    
    for day_name, day_data in schedule_data.get('days', {}).items():
        print(f"\n{day_name.upper()}")
        print("-" * 80)
        
        task_count = 0
        for block in day_data.get('blocks', []):
            task = block.get('task')
            if task:
                time_range = block.get('time', '')
                category = block.get('category', '')
                print(f"  {time_range} | {task} [{category}]")
                task_count += 1
        
        if task_count == 0:
            print("  (No tasks scheduled)")
    
    print("\n✅ Demo complete!")
    print("\nTo use your real tasks, run: python main.py sync")
    print("To view the saved schedule, run: python main.py view-schedule")


if __name__ == '__main__':
    demo_schedule()
