"""
LangChain agent for intelligent task scheduling
"""
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from schedule_models import Task, TimeBlock, DailySchedule, WeeklySchedule
from task_parser import round_to_nearest_30_min
import json


class SchedulingAgent:
    """
    Intelligent scheduling agent using context-aware logic
    Preferences: Night owl (prefers later times), Project > School bias
    """
    
    def __init__(self, week_schedule: WeeklySchedule):
        self.schedule = week_schedule
        self.max_continuous_minutes = 120  # 2 hours before splitting
        self.block_duration_minutes = 30
    
    def schedule_tasks(self, tasks: List[Task], flexible_events: List[Tuple[str, int]]) -> bool:
        """
        Main scheduling method
        Args:
            tasks: List of tasks to schedule
            flexible_events: List of (event_name, duration_minutes) for flexible placement
        Returns:
            bool: Whether scheduling was successful
        """
        try:
            # First, place flexible daily events intelligently
            self._place_flexible_events(flexible_events)
            
            # Then schedule tasks with intelligence
            for task in sorted(tasks, key=lambda t: self._task_priority(t), reverse=True):
                self._schedule_task(task)
            
            return True
        
        except Exception as e:
            print(f"Error during scheduling: {e}")
            return False
    
    def _task_priority(self, task: Task) -> float:
        """
        Calculate task priority score (higher = more important)
        Factors:
        - Importance level
        - Category (projects > school > personal)
        - Time constraints (fixed times get higher priority)
        """
        priority = 0.0
        
        # Importance boost
        if task.importance == 'high':
            priority += 3.0
        
        # Category bias (Project > School > Personal)
        if task.category == 'projects':
            priority += 2.0
        elif task.category == 'school':
            priority += 1.0
        else:
            priority += 0.5
        
        # Time constraints get priority (fixed schedules should be placed first)
        if task.has_time_constraint:
            priority += 1.5
        
        return priority
    
    def _schedule_task(self, task: Task) -> bool:
        """
        Schedule a single task intelligently
        """
        # If task has time constraint, respect it
        if task.has_time_constraint:
            return self._schedule_time_constrained_task(task)
        
        # Otherwise, find best slot based on preferences
        return self._schedule_flexible_task(task)
    
    def _schedule_time_constrained_task(self, task: Task) -> bool:
        """
        Schedule task with specific time constraint
        """
        start_time = task.constraint_start_time
        end_time = task.constraint_end_time
        
        if not start_time or not end_time:
            return False
        
        # Try all days of the week
        for day_name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            daily_schedule = self.schedule.schedules.get(day_name)
            if not daily_schedule:
                continue
            
            # Find blocks matching this time range
            matching_blocks = self._find_blocks_by_time_range(
                daily_schedule,
                start_time,
                end_time
            )
            
            if matching_blocks and all(b.task_name is None for b in matching_blocks):
                # Place the task
                for block in matching_blocks:
                    block.task_name = task.title
                    block.task_id = task.id
                    block.category = task.category
                    block.is_flexible = False
                
                return True
        
        # If specific time not available, try to fit it somewhere
        print(f"Warning: Could not place time-constrained task '{task.title}' at specified time")
        return self._schedule_flexible_task(task)
    
    def _schedule_flexible_task(self, task: Task) -> bool:
        """
        Schedule task without time constraint, using intelligent placement
        """
        required_blocks = max(1, (task.estimated_duration or 45) // self.block_duration_minutes)
        
        # If task is longer than 2 hours, decide whether to split or skip
        if required_blocks > 4:  # 4 blocks = 2 hours
            if required_blocks <= 8:  # Can be split into 2 parts
                # Split the task
                return self._split_and_schedule_task(task, required_blocks)
            else:
                # Too long, skip
                print(f"Warning: Task '{task.title}' is too long ({task.estimated_duration} min). Skipping.")
                return False
        
        # Find best slot for this task
        best_slot = self._find_best_slot(required_blocks, task.category)
        
        if best_slot:
            day_name, block_indices = best_slot
            daily_schedule = self.schedule.schedules[day_name]
            
            for idx in block_indices:
                block = daily_schedule.blocks[idx]
                block.task_name = task.title
                block.task_id = task.id
                block.category = task.category
                block.is_flexible = False
            
            return True
        
        print(f"Warning: Could not find suitable slot for task '{task.title}'")
        return False
    
    def _split_and_schedule_task(self, task: Task, required_blocks: int) -> bool:
        """
        Split a long task into 2 parts and schedule each
        """
        half_blocks = required_blocks // 2
        
        # Create first part
        task1 = Task(
            id=f"{task.id}_part1",
            title=f"{task.title} (Part 1)",
            estimated_duration=half_blocks * self.block_duration_minutes,
            category=task.category,
            importance=task.importance
        )
        
        # Create second part
        task2 = Task(
            id=f"{task.id}_part2",
            title=f"{task.title} (Part 2)",
            estimated_duration=(required_blocks - half_blocks) * self.block_duration_minutes,
            category=task.category,
            importance=task.importance
        )
        
        success1 = self._schedule_flexible_task(task1)
        success2 = self._schedule_flexible_task(task2)
        
        return success1 and success2
    
    def _find_best_slot(self, required_blocks: int, task_category: str) -> Optional[Tuple[str, List[int]]]:
        """
        Find the best slot for a task
        Night owl preference: prefer later times (after 3 PM)
        Project preference: allocate better hours for projects
        """
        best_slot = None
        best_score = -1
        
        for day_name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            daily_schedule = self.schedule.schedules[day_name]
            
            for i in range(len(daily_schedule.blocks) - required_blocks + 1):
                blocks_slice = daily_schedule.blocks[i:i + required_blocks]
                
                # Check if all blocks are available
                if all(b.task_name is None for b in blocks_slice):
                    # Calculate score for this slot
                    score = self._calculate_slot_score(blocks_slice, task_category, i, len(daily_schedule.blocks))
                    
                    if score > best_score:
                        best_score = score
                        best_slot = (day_name, list(range(i, i + required_blocks)))
        
        return best_slot
    
    def _calculate_slot_score(self, blocks: List[TimeBlock], task_category: str, block_index: int, total_blocks: int) -> float:
        """
        Calculate score for a potential slot
        Higher score = better slot
        """
        score = 0.0
        
        # Extract hour from first block
        start_time = blocks[0].start_time
        hour = int(start_time.split(':')[0])
        
        # Night owl preference: prefer evening/night (after 15:00 / 3 PM)
        # Score increases from 9 AM to midnight
        hour_score = max(0, (hour - 9) * 0.5)  # Increases with time of day
        score += hour_score
        
        # Project preference: give projects slightly better slots
        if task_category == 'projects':
            score += 1.0
        elif task_category == 'school':
            score += 0.5
        
        # Prefer slots without adjacent events (isolation bonus)
        has_clear_before = block_index == 0 or blocks[0] != blocks[0]
        has_clear_after = block_index + len(blocks) >= total_blocks
        
        if has_clear_before or has_clear_after:
            score += 0.5
        
        return score
    
    def _place_flexible_events(self, flexible_events: List[Tuple[str, int]]):
        """
        Place flexible daily events (prayer, cooking, breaks)
        Spreads them throughout the day intelligently
        """
        for event_name, duration_minutes in flexible_events:
            blocks_needed = max(1, duration_minutes // self.block_duration_minutes)
            
            # Find best time for this event
            for day_name in self.schedule.schedules.keys():
                daily_schedule = self.schedule.schedules[day_name]
                
                # Prefer morning for prayer, afternoon for other activities
                preferred_hour = 10 if 'prayer' in event_name.lower() else 18
                
                best_slot = None
                best_distance = float('inf')
                
                for i in range(len(daily_schedule.blocks) - blocks_needed + 1):
                    blocks_slice = daily_schedule.blocks[i:i + blocks_needed]
                    
                    if all(b.task_name is None for b in blocks_slice):
                        block_hour = int(blocks_slice[0].start_time.split(':')[0])
                        distance = abs(block_hour - preferred_hour)
                        
                        if distance < best_distance:
                            best_distance = distance
                            best_slot = (day_name, list(range(i, i + blocks_needed)))
                
                if best_slot:
                    day_name, block_indices = best_slot
                    daily_schedule = self.schedule.schedules[day_name]
                    
                    for idx in block_indices:
                        block = daily_schedule.blocks[idx]
                        block.task_name = event_name
                        block.category = 'personal'
                        block.is_flexible = False
                    break
    
    def _find_blocks_by_time_range(
        self,
        daily_schedule: DailySchedule,
        start_time: str,
        end_time: str
    ) -> List[TimeBlock]:
        """
        Find all blocks within a specific time range
        """
        matching_blocks = []
        
        for block in daily_schedule.blocks:
            block_start = int(block.start_time.replace(':', ''))
            block_end = int(block.end_time.replace(':', ''))
            range_start = int(start_time.replace(':', ''))
            range_end = int(end_time.replace(':', ''))
            
            if block_start >= range_start and block_end <= range_end:
                matching_blocks.append(block)
        
        return matching_blocks
