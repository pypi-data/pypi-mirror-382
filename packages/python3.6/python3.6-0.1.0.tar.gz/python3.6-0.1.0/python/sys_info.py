import platform
import sys


class SystemInfo:
    @staticmethod
    def check_python_version():
        return {
            "version": platform.python_version(),
            "full_version": sys.version,
            "is_python3": sys.version_info.major >= 3
        }