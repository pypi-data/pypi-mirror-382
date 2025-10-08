#!/usr/bin/env python3
"""
lunofetch.py - Custom Neofetch-like system info tool
Works on any Linux distro with minimal dependencies
Embedded custom ASCII logo
"""

import os
import sys
import platform
import shutil
import time
from datetime import timedelta

# Optional dependencies
try:
    import psutil
except ImportError:
    psutil = None

try:
    import distro
except ImportError:
    distro = None


# ---------------- Utility Functions ----------------

CSI = "\033["
RESET = CSI + "0m"


def color(text, code="36"):
    """Return ANSI colored text if terminal supports it"""
    return f"{CSI}{code}m{text}{RESET}" if sys.stdout.isatty() else text


def human_bytes(n):
    """Convert bytes to human-readable format"""
    step = 1024.0
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if n < step:
            return f"{n:.1f}{unit}"
        n /= step
    return f"{n:.1f}PB"


def uptime_str():
    """Return system uptime as string"""
    try:
        if psutil:
            sec = int(time.time() - psutil.boot_time())
            return str(timedelta(seconds=sec)).split('.')[0]
        else:
            # fallback for minimal systems
            with open("/proc/uptime", "r") as f:
                sec = float(f.readline().split()[0])
            return str(timedelta(seconds=int(sec)))
    except Exception:
        return "unknown"


# ---------------- Collectors ----------------

def collect_os():
    if distro:
        return ("OS", f"{distro.name()} {distro.version()}")
    else:
        return ("OS", f"{platform.system()} {platform.release()}")


def collect_host():
    return ("Host", platform.node())


def collect_kernel():
    return ("Kernel", platform.version())


def collect_cpu():
    cores = os.cpu_count() or "unknown"
    cpu_name = platform.processor() or "unknown"
    return ("CPU", f"{cpu_name} ({cores} cores)")


def collect_memory():
    if psutil:
        vm = psutil.virtual_memory()
        return ("Memory", f"{human_bytes(vm.used)}/{human_bytes(vm.total)} ({vm.percent}%)")
    else:
        return ("Memory", "psutil not installed")


def collect_disk():
    try:
        total, used, free = shutil.disk_usage("/")
        return ("Disk", f"{human_bytes(used)}/{human_bytes(total)}")
    except Exception:
        return ("Disk", "unknown")


def collect_uptime():
    return ("Uptime", uptime_str())


def collect_shell():
    shell = os.environ.get("SHELL", "unknown")
    return ("Shell", shell)


def collect_terminal():
    term = os.environ.get("TERM", "unknown")
    return ("Terminal", term)


# ---------------- Display ----------------

def load_logo(path=None):
    """Load ASCII logo from file or use default embedded banner"""
    if path:
        try:
            with open(os.path.expanduser(path), 'r', encoding='utf-8') as f:
                return [line.rstrip("\n") for line in f.readlines()]
        except Exception:
            pass  # If file reading fails, fallback to default logo

    # Default ASCII banner
    return [
        "                                                                ",
        "                                                                ",
        "                                                                ",
        "                                                                ",
        "                                                                ",
        "                                                                ",
        "                                                                ",
        "                              :-==-.                            ",
        "                        .+@@@@@%+-.                              ",
        "                      +@@@@@#.                                   ",
        "                    *@@@@@*                                      ",
        "                  -@@@@@@:                                       ",
        "                 +@@@@@%.                                        ",
        "                :@@@@@@.                                         ",
        "               .@@@@@@*  ==                                      ",
        "               =@@@@@@-  #@+                                     ",
        "               *@@@@@*  *@@@@@%*-                                ",
        "               #@@@. =@@@@@@@@:                                  ",
        "               +@@@%+.   =@@#                                     ",
        "               =@@@@@@@#  .@-                                     ",
        "                @@@@@@@@%  .                    :                ",
        "                 %@@@@@@@@:                   .%.                ",
        "                 .@@@@@@@@@@=               :%%                  ",
        "                   *@@@@@@@@@@%*:       .+%@@+                   ",
        "                    .*@@@@@@@@@@@@@@@@@@@@@#.                    ",
        "                       =%@@@@@@@@@@@@@@@%=                       ",
        "                           =*#@@@@@#*=.                          ",
        "                                                                ",
        "                                                                ",
        "                                                                ",
        "                                                                ",
        "                                                                ",
        "                                                                ",
        "                                                                ",
    ]

def format_display(logo_lines, info_pairs, colors=True):
    """Align ASCII logo with info output"""
    width_logo = max(len(l) for l in logo_lines)
    info_lines = [f"{k}: {v}" for k, v in info_pairs]
    max_lines = max(len(logo_lines), len(info_lines))
    output_lines = []

    for i in range(max_lines):
        left = logo_lines[i] if i < len(logo_lines) else ""
        right = info_lines[i] if i < len(info_lines) else ""
        left = left.ljust(width_logo)
        if colors and right:
            if ":" in right:
                k, v = right.split(":", 1)
                right = f"{color(k + ':', '36')} {color(v.strip(), '37')}"
        output_lines.append(f"{left} {right}")

    return "\n".join(output_lines)


# ---------------- Main ----------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="lunofetch - custom logo system info tool")
    parser.add_argument("--logo", type=str, help="Path to your ASCII logo (optional, overrides default)")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    args = parser.parse_args()

    logo = load_logo(args.logo)
    collectors = [
        collect_os,
        collect_host,
        collect_kernel,
        collect_uptime,
        collect_cpu,
        collect_memory,
        collect_disk,
        collect_shell,
        collect_terminal
    ]

    info_pairs = []
    for c in collectors:
        try:
            info_pairs.append(c())
        except Exception as e:
            info_pairs.append((c.__name__, f"error: {e}"))

    colored = not args.no_color and sys.stdout.isatty()
    print(format_display(logo, info_pairs, colors=colored))


if __name__ == "__main__":
    main()
