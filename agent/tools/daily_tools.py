# agent/tools/daily_tools.py
import math
import re
import pyperclip
import requests
from datetime import datetime, timedelta
from pathlib import Path
from PIL import ImageGrab
import threading
import time

from agent.tools.base_tool import BaseTool
from config_manager import config
from logger import logger

try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except:
    NOTIFICATIONS_AVAILABLE = False
    logger.warning("Plyer not available. Reminders will be logged only.")


class CalculatorTool(BaseTool):
    """Advanced calculator with support for complex expressions and functions."""
    
    name = "calculate"
    description = "Perform mathematical calculations. Argument: math expression (e.g., '15% of 2500', 'sqrt(144)', '2^8', 'sin(45)')"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
    
    def execute(self, argument: str) -> str:
        try:
            if not argument or argument.strip() == "":
                return "Error: Please provide a mathematical expression."
            
            expression = argument.strip()
            logger.info(f"Calculating: {expression}")
            
            # Handle percentage calculations
            if "%" in expression and " of " in expression.lower():
                match = re.search(r'(\d+\.?\d*)\s*%\s*of\s*(\d+\.?\d*)', expression, re.IGNORECASE)
                if match:
                    percent = float(match.group(1))
                    number = float(match.group(2))
                    result = (percent / 100) * number
                    return f"{percent}% of {number} = {result}"
            
            # Replace common functions with Python equivalents
            expression = expression.replace('^', '**')  # Power operator
            expression = expression.replace('√', 'sqrt')
            
            # Safe math functions
            safe_dict = {
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
                'pow': pow,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'pi': math.pi,
                'e': math.e,
                'ceil': math.ceil,
                'floor': math.floor,
                'factorial': math.factorial,
            }
            
            # Evaluate expression
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            
            # Format result
            if isinstance(result, float):
                # Round to reasonable precision
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)
            
            return f"{argument} = {result}"
            
        except ZeroDivisionError:
            return "Error: Division by zero"
        except SyntaxError as e:
            return f"Error: Invalid mathematical expression - {str(e)}"
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return f"Error: Could not calculate '{argument}' - {str(e)}"


class TimerReminderTool(BaseTool):
    """Set timers and reminders with background execution."""
    
    name = "set_reminder"
    description = "Set a reminder or timer. Argument: time in minutes followed by message (e.g., '5 take a break', '30 meeting with team')"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        self.active_reminders = []
    
    def execute(self, argument: str) -> str:
        try:
            if not argument or argument.strip() == "":
                return "Error: Please provide time and message (e.g., '5 take a break')"
            
            # Parse argument: "5 take a break" or "30 meeting"
            parts = argument.strip().split(maxsplit=1)
            if len(parts) < 1:
                return "Error: Invalid format. Use: 'minutes message' (e.g., '5 take a break')"
            
            try:
                minutes = float(parts[0])
                message = parts[1] if len(parts) > 1 else "Reminder"
            except ValueError:
                return "Error: First argument must be a number (minutes)"
            
            if minutes <= 0 or minutes > 1440:  # Max 24 hours
                return "Error: Minutes must be between 0 and 1440 (24 hours)"
            
            # Calculate trigger time
            trigger_time = datetime.now() + timedelta(minutes=minutes)
            
            # Start reminder thread
            reminder_thread = threading.Thread(
                target=self._reminder_worker,
                args=(minutes, message, trigger_time),
                daemon=True
            )
            reminder_thread.start()
            
            self.active_reminders.append({
                'message': message,
                'trigger_time': trigger_time,
                'thread': reminder_thread
            })
            
            logger.info(f"Reminder set: {message} in {minutes} minutes at {trigger_time.strftime('%I:%M %p')}")
            
            return f"✓ Reminder set for {trigger_time.strftime('%I:%M %p')} ({minutes} min): {message}"
            
        except Exception as e:
            logger.error(f"Error setting reminder: {e}")
            return f"Error: Could not set reminder - {str(e)}"
    
    def _reminder_worker(self, minutes, message, trigger_time):
        """Background worker that waits and triggers reminder."""
        try:
            # Wait for specified time
            time.sleep(minutes * 60)
            
            # Trigger reminder
            logger.info(f"⏰ REMINDER: {message}")
            
            # Show system notification if available
            if NOTIFICATIONS_AVAILABLE:
                try:
                    notification.notify(
                        title="AI Agent Reminder",
                        message=message,
                        app_name="Local AI Agent",
                        timeout=10
                    )
                except Exception as e:
                    logger.error(f"Could not show notification: {e}")
            
            # Also log to console
            print(f"\n\n{'='*60}")
            print(f"⏰ REMINDER at {datetime.now().strftime('%I:%M %p')}")
            print(f"📝 {message}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"Reminder worker error: {e}")


class ClipboardTool(BaseTool):
    """Manage clipboard operations - copy, paste, and history."""
    
    name = "clipboard"
    description = "Clipboard operations. Argument: 'copy <text>' to copy text, 'paste' to get clipboard content, 'clear' to clear clipboard"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        self.history = []
        self.max_history = 10
    
    def execute(self, argument: str) -> str:
        try:
            if not argument or argument.strip() == "":
                return "Error: Please specify operation: 'copy <text>', 'paste', or 'clear'"
            
            parts = argument.strip().split(maxsplit=1)
            operation = parts[0].lower()
            
            if operation == "copy":
                if len(parts) < 2:
                    return "Error: Please provide text to copy"
                
                text = parts[1]
                pyperclip.copy(text)
                
                # Add to history
                self.history.append({
                    'text': text,
                    'timestamp': datetime.now().strftime('%I:%M %p')
                })
                if len(self.history) > self.max_history:
                    self.history.pop(0)
                
                logger.info(f"Copied to clipboard: {text[:50]}...")
                return f"✓ Copied to clipboard: {text[:100]}{'...' if len(text) > 100 else ''}"
            
            elif operation == "paste":
                content = pyperclip.paste()
                if not content:
                    return "Clipboard is empty"
                logger.info(f"Retrieved from clipboard: {content[:50]}...")
                return f"Clipboard content:\n{content}"
            
            elif operation == "clear":
                pyperclip.copy("")
                logger.info("Clipboard cleared")
                return "✓ Clipboard cleared"
            
            elif operation == "history":
                if not self.history:
                    return "No clipboard history available"
                
                output = "Clipboard History (last 10 items):\n\n"
                for i, item in enumerate(reversed(self.history), 1):
                    output += f"{i}. [{item['timestamp']}] {item['text'][:80]}...\n"
                
                return output.strip()
            
            else:
                return f"Error: Unknown operation '{operation}'. Use: copy, paste, clear, or history"
            
        except Exception as e:
            logger.error(f"Clipboard error: {e}")
            return f"Error: Clipboard operation failed - {str(e)}"


class WeatherTool(BaseTool):
    """Get current weather information using OpenWeatherMap API."""
    
    name = "weather"
    description = "Get current weather for a city. Argument: city name (e.g., 'Mumbai', 'New York', 'London')"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        # Get API key from config or use default (you'll need to add this to config.ini)
        self.api_key = config.get('Weather', 'api_key', fallback='')
        
        if not self.api_key:
            logger.warning("Weather API key not configured. Get free key from: https://openweathermap.org/api")
    
    def execute(self, argument: str) -> str:
        try:
            if not self.api_key:
                return """Weather API key not configured. 

To enable weather:
1. Get free API key from: https://openweathermap.org/api
2. Add to config.ini:
   [Weather]
   api_key = YOUR_API_KEY_HERE

3. Restart the agent"""
            
            if not argument or argument.strip() == "":
                return "Error: Please provide a city name (e.g., 'Mumbai', 'London')"
            
            city = argument.strip()
            logger.info(f"Fetching weather for: {city}")
            
            # Call OpenWeatherMap API
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 404:
                return f"Error: City '{city}' not found"
            elif response.status_code == 401:
                return "Error: Invalid API key. Please check your configuration."
            elif response.status_code != 200:
                return f"Error: Weather service returned status {response.status_code}"
            
            data = response.json()
            
            # Extract weather information
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description'].title()
            wind_speed = data['wind']['speed']
            
            # Format output
            output = f"🌤️ Weather in {city.title()}\n"
            output += f"{'='*40}\n"
            output += f"🌡️  Temperature: {temp}°C (Feels like {feels_like}°C)\n"
            output += f"☁️  Conditions: {description}\n"
            output += f"💧 Humidity: {humidity}%\n"
            output += f"💨 Wind Speed: {wind_speed} m/s\n"
            
            logger.info(f"Weather fetched successfully for {city}")
            return output.strip()
            
        except requests.Timeout:
            return "Error: Weather service request timed out"
        except requests.RequestException as e:
            logger.error(f"Weather API request error: {e}")
            return f"Error: Could not connect to weather service"
        except Exception as e:
            logger.error(f"Weather error: {e}")
            return f"Error: Could not fetch weather - {str(e)}"


class ScreenshotTool(BaseTool):
    """Capture screenshots and save to file."""
    
    name = "screenshot"
    description = "Take a screenshot. Argument: optional filename (default: auto-generated with timestamp)"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        
        # Create screenshots directory
        data_dir = Path(config.get('Paths', 'data_directory', fallback='.agent_data'))
        self.screenshots_dir = data_dir / 'screenshots'
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, argument: str) -> str:
        try:
            # Generate filename
            if argument and argument.strip():
                filename = argument.strip()
                if not filename.endswith('.png'):
                    filename += '.png'
            else:
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                filename = f"screenshot_{timestamp}.png"
            
            filepath = self.screenshots_dir / filename
            
            logger.info(f"Taking screenshot: {filename}")
            
            # Capture screenshot
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            # Get file size
            file_size = filepath.stat().st_size / 1024  # KB
            
            logger.info(f"Screenshot saved: {filepath}")
            
            return f"✓ Screenshot saved successfully\n📁 File: {filepath}\n📊 Size: {file_size:.1f} KB\n🖼️  Resolution: {screenshot.size[0]}x{screenshot.size[1]}"
            
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return f"Error: Could not capture screenshot - {str(e)}"
