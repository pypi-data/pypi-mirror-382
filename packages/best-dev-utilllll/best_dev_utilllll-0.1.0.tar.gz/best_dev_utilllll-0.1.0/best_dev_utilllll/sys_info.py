import platform
import psutil
import datetime
from .utils.helpers import format_bytes


class SystemInfo:
    @staticmethod
    def get_system_info():
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version()
        }

    @staticmethod
    def get_memory_info():
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "ram": {
                "total": format_bytes(memory.total),
                "available": format_bytes(memory.available),
                "used": format_bytes(memory.used),
                "percent": f"{memory.percent}%"
            },
            "swap": {
                "total": format_bytes(swap.total),
                "used": format_bytes(swap.used),
                "free": format_bytes(swap.free),
                "percent": f"{swap.percent}%"
            }
        }

    @staticmethod
    def get_disk_info(path="."):
        disk = psutil.disk_usage(path)
        disk_io = psutil.disk_io_counters()

        info = {
            "path": path,
            "total": format_bytes(disk.total),
            "used": format_bytes(disk.used),
            "free": format_bytes(disk.free),
            "percent": f"{disk.percent}%"
        }

        if disk_io:
            info.update({
                "read_bytes": format_bytes(disk_io.read_bytes),
                "write_bytes": format_bytes(disk_io.write_bytes)
            })

        return info

    @staticmethod
    def get_cpu_info():
        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "cpu_usage": f"{psutil.cpu_percent(interval=1)}%",
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }

    @staticmethod
    def get_uptime():
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        return str(uptime).split('.')[0]
