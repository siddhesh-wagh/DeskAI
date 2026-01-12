"""
System Skills - OS-level operations with platform abstraction
"""
from skills.base import BaseSkill, SkillResult
from core.dispatcher import command
from core.context import AssistantContext
from utils.os_utils import OSManager
from typing import Dict, Any
import psutil
from datetime import datetime


class SystemInfoSkill(BaseSkill):
    """Get system resource information"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            battery = psutil.sensors_battery()
            
            info_parts = [
                f"CPU usage is at {cpu}%",
                f"Memory usage is {memory.percent}%",
                f"Disk usage is {disk.percent}%"
            ]
            
            if battery:
                info_parts.append(f"Battery is at {battery.percent}%")
                if battery.power_plugged:
                    info_parts.append("and charging")
                elif battery.secsleft > 0:
                    hours = int(battery.secsleft / 3600)
                    info_parts.append(f"with approximately {hours} hours remaining")
            
            response = ". ".join(info_parts) + "."
            
            return SkillResult()\
                .with_message(response)\
                .with_data({
                    'cpu': cpu,
                    'memory': memory.percent,
                    'disk': disk.percent,
                    'battery': battery.percent if battery else None
                })\
                .build()
        
        except Exception as e:
            return self.error_response(f"Could not retrieve system info: {e}")


class BatterySkill(BaseSkill):
    """Check battery status"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            battery = psutil.sensors_battery()
            
            if not battery:
                return self.success_response("No battery detected. System appears to be a desktop.")
            
            status = f"Battery is at {battery.percent}%"
            
            if battery.power_plugged:
                status += " and currently charging"
            elif battery.secsleft > 0:
                hours = int(battery.secsleft / 3600)
                minutes = int((battery.secsleft % 3600) / 60)
                status += f" with approximately {hours} hours and {minutes} minutes remaining"
            
            return self.success_response(status + ".")
        
        except Exception as e:
            return self.error_response(f"Battery check failed: {e}")


class SystemControlSkill(BaseSkill):
    """System power operations (shutdown, restart, etc.)"""
    
    def __init__(self):
        super().__init__()
        self.os_manager = OSManager()
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        q = query.lower()
        
        try:
            if "shutdown" in q:
                self.os_manager.shutdown()
                return SkillResult()\
                    .with_message("Shutting down. Goodbye!")\
                    .with_action("exit")\
                    .build()
            
            elif "restart" in q:
                self.os_manager.restart()
                return SkillResult()\
                    .with_message("Restarting the system")\
                    .with_action("exit")\
                    .build()
            
            elif "log off" in q or "logout" in q:
                self.os_manager.logout()
                return SkillResult()\
                    .with_message("Logging off")\
                    .with_action("exit")\
                    .build()
            
            elif "sleep" in q:
                self.os_manager.sleep()
                return self.success_response("Putting system to sleep")
            
            else:
                return self.error_response("Unknown system command")
        
        except Exception as e:
            return self.error_response(f"System control failed: {e}")


class ProcessListSkill(BaseSkill):
    """List running applications"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            processes = []
            
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] and proc.info['cpu_percent'] > 0:
                        processes.append((
                            proc.info['name'], 
                            proc.info['cpu_percent']
                        ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x[1], reverse=True)
            top_5 = processes[:5]
            
            if not top_5:
                return self.success_response("No active applications detected")
            
            app_list = "\n".join([
                f"• {name}: {cpu:.1f}% CPU" 
                for name, cpu in top_5
            ])
            
            return SkillResult()\
                .with_message(f"Top 5 active applications:\n{app_list}")\
                .with_data({'processes': top_5})\
                .build()
        
        except Exception as e:
            return self.error_response(f"Could not list processes: {e}")


class TimeSkill(BaseSkill):
    """Get current time"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        time_str = datetime.now().strftime('%I:%M %p')
        return self.success_response(f"It's {time_str}")


class DateSkill(BaseSkill):
    """Get current date"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        date_str = datetime.now().strftime("%B %d, %Y")
        return self.success_response(f"Today is {date_str}")


# Register commands using dispatcher
@command(["system info", "system status"], priority=10)
def cmd_system_info(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return SystemInfoSkill().execute(ctx, query)


@command(["battery", "battery status"], priority=10)
def cmd_battery(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return BatterySkill().execute(ctx, query)


@command(["shutdown", "restart", "log off", "logout", "sleep"], priority=100)
def cmd_system_control(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return SystemControlSkill().execute(ctx, query)


@command(["running app", "active app", "list processes"], priority=10)
def cmd_process_list(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return ProcessListSkill().execute(ctx, query)


@command(["time", "what time"], priority=10)
def cmd_time(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return TimeSkill().execute(ctx, query)


@command(["date", "what date", "today"], priority=10)
def cmd_date(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return DateSkill().execute(ctx, query)