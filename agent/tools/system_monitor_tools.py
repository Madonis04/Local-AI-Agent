# agent/tools/system_monitor_tools.py
import psutil
import platform
from datetime import datetime
from agent.tools.base_tool import BaseTool
from logger import logger

class SystemInfoTool(BaseTool):
    @property
    def name(self) -> str:
        return "system info"

    @property
    def description(self) -> str:
        return "Displays comprehensive system information including OS, CPU, RAM, and disk usage."

    def execute(self, argument: str) -> str:
        try:
            # System information
            uname = platform.uname()
            
            # CPU information
            cpu_freq = psutil.cpu_freq()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # Boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            
            info = f"""
🖥️  SYSTEM INFORMATION
{'='*50}

💻 Operating System
   OS: {uname.system}
   Release: {uname.release}
   Version: {uname.version}
   Architecture: {uname.machine}
   Processor: {uname.processor}

🧠 CPU Information
   Physical cores: {psutil.cpu_count(logical=False)}
   Total cores: {psutil.cpu_count(logical=True)}
   Max Frequency: {cpu_freq.max:.2f} MHz
   Current Frequency: {cpu_freq.current:.2f} MHz
   CPU Usage: {cpu_percent}%

💾 Memory Information
   Total: {self._bytes_to_gb(memory.total)} GB
   Available: {self._bytes_to_gb(memory.available)} GB
   Used: {self._bytes_to_gb(memory.used)} GB
   Usage: {memory.percent}%

💿 Disk Information
   Total: {self._bytes_to_gb(disk.total)} GB
   Used: {self._bytes_to_gb(disk.used)} GB
   Free: {self._bytes_to_gb(disk.free)} GB
   Usage: {disk.percent}%

⏰ System Boot Time
   {boot_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            logger.info("Retrieved system information")
            return info.strip()
        
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return f"Error retrieving system information: {str(e)}"
    
    def _bytes_to_gb(self, bytes_value):
        """Convert bytes to gigabytes."""
        return round(bytes_value / (1024**3), 2)


class CPUMonitorTool(BaseTool):
    @property
    def name(self) -> str:
        return "cpu usage"

    @property
    def description(self) -> str:
        return "Shows current CPU usage percentage and per-core breakdown."

    def execute(self, argument: str) -> str:
        try:
            # Overall CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Per-core usage
            per_cpu = psutil.cpu_percent(interval=1, percpu=True)
            
            result = f"🧠 CPU USAGE\n{'='*40}\n\n"
            result += f"Overall Usage: {cpu_percent}%\n\n"
            result += "Per-Core Usage:\n"
            
            for i, percent in enumerate(per_cpu):
                bar = '█' * int(percent / 5)
                result += f"Core {i}: {percent:5.1f}% [{bar:<20}]\n"
            
            logger.info("Retrieved CPU usage")
            return result
        
        except Exception as e:
            logger.error(f"Error monitoring CPU: {e}")
            return f"Error monitoring CPU: {str(e)}"


class MemoryMonitorTool(BaseTool):
    @property
    def name(self) -> str:
        return "memory usage"

    @property
    def description(self) -> str:
        return "Shows current RAM usage and availability."

    def execute(self, argument: str) -> str:
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            result = f"""
💾 MEMORY USAGE
{'='*40}

RAM:
   Total:     {self._bytes_to_gb(memory.total)} GB
   Available: {self._bytes_to_gb(memory.available)} GB
   Used:      {self._bytes_to_gb(memory.used)} GB
   Free:      {self._bytes_to_gb(memory.free)} GB
   Usage:     {memory.percent}%

SWAP:
   Total:     {self._bytes_to_gb(swap.total)} GB
   Used:      {self._bytes_to_gb(swap.used)} GB
   Free:      {self._bytes_to_gb(swap.free)} GB
   Usage:     {swap.percent}%
"""
            logger.info("Retrieved memory usage")
            return result.strip()
        
        except Exception as e:
            logger.error(f"Error monitoring memory: {e}")
            return f"Error monitoring memory: {str(e)}"
    
    def _bytes_to_gb(self, bytes_value):
        """Convert bytes to gigabytes."""
        return round(bytes_value / (1024**3), 2)


class DiskMonitorTool(BaseTool):
    @property
    def name(self) -> str:
        return "disk usage"

    @property
    def description(self) -> str:
        return "Shows disk space usage for all mounted drives."

    def execute(self, argument: str) -> str:
        try:
            partitions = psutil.disk_partitions()
            
            result = f"💿 DISK USAGE\n{'='*40}\n\n"
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    result += f"Drive: {partition.device}\n"
                    result += f"  Mountpoint: {partition.mountpoint}\n"
                    result += f"  File System: {partition.fstype}\n"
                    result += f"  Total: {self._bytes_to_gb(usage.total)} GB\n"
                    result += f"  Used: {self._bytes_to_gb(usage.used)} GB\n"
                    result += f"  Free: {self._bytes_to_gb(usage.free)} GB\n"
                    result += f"  Usage: {usage.percent}%\n\n"
                except PermissionError:
                    continue
            
            logger.info("Retrieved disk usage")
            return result.strip()
        
        except Exception as e:
            logger.error(f"Error monitoring disk: {e}")
            return f"Error monitoring disk: {str(e)}"
    
    def _bytes_to_gb(self, bytes_value):
        """Convert bytes to gigabytes."""
        return round(bytes_value / (1024**3), 2)


class ProcessListTool(BaseTool):
    @property
    def name(self) -> str:
        return "list processes"

    @property
    def description(self) -> str:
        return "Lists running processes sorted by CPU or memory usage. Argument: 'cpu' or 'memory' (default: cpu)."

    def execute(self, argument: str) -> str:
        try:
            sort_by = argument.lower() if argument else "cpu"
            
            # Get all processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort processes
            if sort_by == "memory":
                processes.sort(key=lambda x: x['memory_percent'], reverse=True)
                title = "MEMORY"
            else:
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
                title = "CPU"
            
            result = f"🔄 TOP PROCESSES (by {title})\n{'='*50}\n\n"
            result += f"{'PID':<8} {'CPU%':<8} {'MEM%':<8} {'NAME'}\n"
            result += "-" * 50 + "\n"
            
            # Show top 15 processes
            for proc in processes[:15]:
                result += f"{proc['pid']:<8} {proc['cpu_percent']:<8.1f} {proc['memory_percent']:<8.1f} {proc['name']}\n"
            
            logger.info(f"Listed processes sorted by {sort_by}")
            return result
        
        except Exception as e:
            logger.error(f"Error listing processes: {e}")
            return f"Error listing processes: {str(e)}"


class KillProcessTool(BaseTool):
    @property
    def name(self) -> str:
        return "kill process"

    @property
    def description(self) -> str:
        return "Terminates a process by PID. Argument should be the process ID. USE WITH CAUTION!"

    def execute(self, argument: str) -> str:
        try:
            if not argument or not argument.isdigit():
                return "Error: Please provide a valid process ID (PID)."
            
            pid = int(argument)
            
            # Check if process exists
            if not psutil.pid_exists(pid):
                return f"Error: No process found with PID {pid}."
            
            # Get process info before killing
            process = psutil.Process(pid)
            proc_name = process.name()
            
            # Terminate process
            process.terminate()
            
            logger.warning(f"Terminated process: {proc_name} (PID: {pid})")
            return f"✅ Terminated process '{proc_name}' (PID: {pid})"
        
        except psutil.AccessDenied:
            return f"Error: Permission denied to kill process {argument}. Try running as administrator."
        except Exception as e:
            logger.error(f"Error killing process: {e}")
            return f"Error killing process: {str(e)}"