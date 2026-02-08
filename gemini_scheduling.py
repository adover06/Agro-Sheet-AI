"""
Gemini Pro AI agent for intelligent task scheduling
"""
import os
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from schedule_models import Task, TimeBlock, DailySchedule, WeeklySchedule
from task_parser import round_to_nearest_30_min
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()


class GeminiSchedulingAgent:
    """
    Intelligent scheduling agent using Google's Gemini Pro
    Preferences: Night owl (prefers later times), Project > School bias
    """
    
    def __init__(self, week_schedule: WeeklySchedule):
        self.schedule = week_schedule
        self.max_continuous_minutes = 120  # 2 hours before splitting
        self.block_duration_minutes = 30
        
        # Initialize Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def schedule_tasks(self, tasks: List[Task], flexible_events: List[Tuple[str, int]]) -> bool:
        """
        Main scheduling method using Gemini AI
        Args:
            tasks: List of tasks to schedule
            flexible_events: List of (event_name, duration_minutes) for flexible placement
        Returns:
            bool: Whether scheduling was successful
        """
        try:
            # First, place flexible daily events intelligently
            self._place_flexible_events(flexible_events)
            
            # Use Gemini to get intelligent task ordering
            task_order = self._get_optimal_task_order(tasks)
            
            # Schedule tasks in the order suggested by Gemini
            for task in task_order:
                self._schedule_task(task)
            
            return True
        
        except Exception as e:
            print(f"Error during scheduling: {e}")
            return False
    
    def _get_optimal_task_order(self, tasks: List[Task]) -> List[Task]:
        """
        Use Gemini to determine optimal task ordering
        Considers priority, time sensitivity, task dependencies, etc.
        """
        try:
            # Format tasks for Gemini
            tasks_summary = self._format_tasks_for_gemini(tasks)
            
            prompt = f"""You are an expert schedule optimizer. Given the following tasks, determine the optimal order to schedule them considering:
1. Task importance and priority
2. Deadlines and time sensitivity
3. Task categories (projects > school > personal)
4. Estimated duration
5. Best time of day for focus (prefer afternoon/evening for important work)

Tasks to schedule:
{tasks_summary}

Return ONLY a JSON array with task titles in the optimal scheduling order, like:
["Task 1", "Task 2", "Task 3"]

Focus on:
- High priority/important tasks first
- Project work in afternoon/evening
- Personal tasks scattered throughout
- Quick tasks during low-energy periods
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse the response - it should be a JSON array
            if response_text.startswith('['):
                # Extract JSON from response
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                json_str = response_text[json_start:json_end]
                ordered_titles = json.loads(json_str)
                
                # Reorder tasks based on Gemini's suggestion
                task_map = {task.title: task for task in tasks}
                ordered_tasks = []
                
                for title in ordered_titles:
                    if title in task_map:
                        ordered_tasks.append(task_map[title])
                
                # Add any tasks that weren't in the response
                for task in tasks:
                    if task not in ordered_tasks:
                        ordered_tasks.append(task)
                
                return ordered_tasks
            
            # Fallback to default priority sorting if JSON parsing fails
            return sorted(tasks, key=lambda t: self._task_priority(t), reverse=True)
        
        except Exception as e:
            print(f"Error getting optimal task order from Gemini: {e}")
            # Fallback to default priority sorting
            return sorted(tasks, key=lambda t: self._task_priority(t), reverse=True)
    
    def _format_tasks_for_gemini(self, tasks: List[Task]) -> str:
        """Format tasks as a readable string for Gemini"""
        formatted = []
        for i, task in enumerate(tasks, 1):
            duration = task.estimated_duration or 60
            priority = "High" if task.importance >= 3 else "Medium" if task.importance >= 2 else "Low"
            formatted.append(
                f"{i}. {task.title} (Category: {task.category}, Priority: {priority}, "
                f"Duration: {duration}min, Due: {task.due_date or 'No deadline'})"
            )
        return "\n".join(formatted)
    
    def _task_priority(self, task: Task) -> float:
        """
        Calculate task priority score (higher = more important)
        Factors:
        - Importance level
        - Category (projects > school > personal)
        - Time sensitivity (closer deadline = higher priority)
        """
        score = 0.0
        
        # Importance (importance is a string: 'high', 'normal', 'low')
        importance_weight = {
            'high': 3.0,
            'normal': 2.0,
            'low': 1.0
        }
        score += importance_weight.get(str(task.importance).lower(), 2.0)
        
        # Category preference: Projects > School > Personal
        category_weights = {
            "projects": 3.0,
            "school": 2.0,
            "personal": 1.0,
            "other": 0.5
        }
        score += category_weights.get(task.category.lower(), 0.5)
        
        # Time sensitivity
        if task.due_date:
            try:
                due = datetime.strptime(task.due_date, "%Y-%m-%d")
                days_until = (due - datetime.now()).days
                if days_until == 0:
                    score += 10  # Due today
                elif days_until == 1:
                    score += 8   # Due tomorrow
                elif days_until <= 3:
                    score += 5   # Due soon
                elif days_until <= 7:
                    score += 2   # Due this week
            except:
                pass
        
        return score
    
    def _place_flexible_events(self, flexible_events: List[Tuple[str, int]]):
        """Place flexible daily events (meals, breaks, etc.) intelligently"""
        for event_name, duration_minutes in flexible_events:
            # Distribute throughout the week
            for day_name in self.schedule.schedules:
                day_schedule = self.schedule.schedules[day_name]
                
                # Try to find a gap and place the event
                placed = self._find_and_place_event(day_schedule, event_name, duration_minutes)
                if placed:
                    break
    
    def _find_and_place_event(self, day_schedule: DailySchedule, event_name: str, 
                              duration_minutes: int) -> bool:
        """Try to place an event in a day's schedule"""
        blocks_needed = duration_minutes // self.block_duration_minutes
        
        # Try to find a gap
        for i in range(len(day_schedule.blocks) - blocks_needed + 1):
            gap = all(
                not day_schedule.blocks[i + j].task_name 
                for j in range(blocks_needed)
            )
            if gap:
                # Place the event
                for j in range(blocks_needed):
                    block = day_schedule.blocks[i + j]
                    block.task_name = event_name
                    block.category = "breaks"
                    block.is_flexible = False
                return True
        
        return False
    
    def _schedule_task(self, task: Task) -> bool:
        """
        Schedule a single task into the weekly schedule
        Returns True if successfully scheduled
        """
        duration_blocks = (task.estimated_duration or 60) // self.block_duration_minutes
        
        # Try to find a suitable time slot
        for day_name in self.schedule.schedules:
            day_schedule = self.schedule.schedules[day_name]
            
            # Find the best time to place this task (afternoon/evening for projects)
            if task.category.lower() == "projects":
                # Prefer afternoon/evening (12:00 onwards)
                suitable_times = [
                    i for i, block in enumerate(day_schedule.blocks)
                    if block.start_time >= "12:00" and not block.task_name
                ]
            else:
                # Can be anytime
                suitable_times = [
                    i for i, block in enumerate(day_schedule.blocks)
                    if not block.task_name
                ]
            
            # Try to find consecutive blocks
            for start_idx in suitable_times:
                consecutive_blocks = self._find_consecutive_blocks(
                    day_schedule, start_idx, duration_blocks
                )
                
                if len(consecutive_blocks) >= duration_blocks:
                    # Place the task
                    for idx in consecutive_blocks[:duration_blocks]:
                        block = day_schedule.blocks[idx]
                        block.task_name = task.title
                        block.task_id = task.id
                        block.category = task.category
                        block.is_flexible = False
                    
                    return True
        
        return False
    
    def _find_consecutive_blocks(self, day_schedule: DailySchedule, 
                                start_idx: int, num_blocks: int) -> List[int]:
        """Find consecutive empty blocks starting from start_idx"""
        consecutive = []
        for i in range(start_idx, len(day_schedule.blocks)):
            if not day_schedule.blocks[i].task_name:
                consecutive.append(i)
                if len(consecutive) == num_blocks:
                    break
            else:
                break
        
        return consecutive
