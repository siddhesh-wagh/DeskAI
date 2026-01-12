"""
Reminders & Timers Skill - Set reminders and countdown timers
"""
from skills.base import BaseSkill, SkillResult
from core.dispatcher import command
from core.context import AssistantContext
from typing import Dict, Any
import re
import time
from threading import Thread
from plyer import notification


class TimerSkill(BaseSkill):
    """Set countdown timers"""
    
    def _parse_duration(self, duration_str: str) -> tuple:
        """
        Parse duration string to seconds.
        
        Args:
            duration_str: e.g., "5 minutes", "30 seconds", "2 hours"
        
        Returns:
            (total_seconds, value, unit_name)
        """
        time_input_lower = duration_str.lower().strip()
        match = re.search(
            r'(\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?|days?)?', 
            time_input_lower
        )
        
        if not match:
            raise ValueError("Invalid time format")
        
        value = int(match.group(1))
        unit_str = match.group(2) if match.group(2) else 'seconds'
        
        # Convert to seconds
        seconds_in_unit = 1
        if 'minute' in unit_str or 'min' in unit_str:
            seconds_in_unit = 60
            unit_name = "minute" if value == 1 else "minutes"
        elif 'hour' in unit_str or 'hr' in unit_str:
            seconds_in_unit = 3600
            unit_name = "hour" if value == 1 else "hours"
        elif 'day' in unit_str:
            seconds_in_unit = 86400
            unit_name = "day" if value == 1 else "days"
        else:
            unit_name = "second" if value == 1 else "seconds"
        
        total_seconds = value * seconds_in_unit
        
        return (total_seconds, value, unit_name)
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        # Extract duration from params or query
        duration_str = params.get('duration')
        
        if not duration_str:
            # Try to extract from query
            # "set timer for 5 minutes" -> "5 minutes"
            match = re.search(r'(?:for|of)\s+(.+)', query)
            if match:
                duration_str = match.group(1)
            else:
                return self.error_response(
                    "Please specify duration. Example: 'set timer for 5 minutes'"
                )
        
        try:
            total_seconds, value, unit_name = self._parse_duration(duration_str)
            
            # Start timer in background
            def timer_callback():
                time.sleep(total_seconds)
                
                # Show notification
                try:
                    notification.notify(
                        title="⏰ Timer Complete!",
                        message=f"Your {value} {unit_name} timer is up!",
                        timeout=10
                    )
                except Exception as e:
                    self._logger.error(f"Notification failed: {e}")
            
            Thread(target=timer_callback, daemon=True).start()
            
            return SkillResult()\
                .with_message(f"Timer set for {value} {unit_name}")\
                .with_data({
                    'duration_seconds': total_seconds,
                    'value': value,
                    'unit': unit_name
                })\
                .build()
        
        except ValueError as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response(f"Failed to set timer: {e}")


class ReminderSkill(BaseSkill):
    """Set quick reminders"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        # Extract message and time
        message = params.get('message')
        duration_str = params.get('duration')
        
        if not message or not duration_str:
            return self.error_response(
                "Reminder requires message and duration. "
                "Example: 'remind me to call mom in 30 minutes'"
            )
        
        try:
            # Parse duration
            timer_skill = TimerSkill()
            total_seconds, value, unit_name = timer_skill._parse_duration(duration_str)
            
            # Start reminder in background
            def reminder_callback():
                time.sleep(total_seconds)
                
                # Show notification
                try:
                    notification.notify(
                        title="🔔 Reminder!",
                        message=message,
                        timeout=15
                    )
                except Exception as e:
                    self._logger.error(f"Notification failed: {e}")
            
            Thread(target=reminder_callback, daemon=True).start()
            
            return SkillResult()\
                .with_message(
                    f"Reminder set for {value} {unit_name}: {message}"
                )\
                .with_data({
                    'message': message,
                    'duration_seconds': total_seconds
                })\
                .build()
        
        except ValueError as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response(f"Failed to set reminder: {e}")


class SimpleReminderSkill(BaseSkill):
    """Simplified reminder for voice commands"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        # Try to parse: "remind me to X in Y minutes/hours"
        # Or: "set reminder for X"
        
        # Pattern 1: "remind me to X in Y time"
        match = re.search(
            r'remind me to (.+?) in (\d+\s+\w+)', 
            query, 
            re.IGNORECASE
        )
        
        if match:
            message = match.group(1).strip()
            duration_str = match.group(2).strip()
            
            return ReminderSkill().execute(
                context, 
                query, 
                message=message, 
                duration=duration_str
            )
        
        # Pattern 2: Just ask for details
        return SkillResult()\
            .with_message(
                "Reminder feature requires message and time. "
                "Example: 'remind me to call mom in 30 minutes'"
            )\
            .build()


# Register commands
@command(["set timer", "start timer", "timer"], priority=10)
def cmd_set_timer(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return TimerSkill().execute(ctx, query)


@command(["remind me", "set reminder", "reminder"], priority=10)
def cmd_set_reminder(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return SimpleReminderSkill().execute(ctx, query)