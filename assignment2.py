#!/usr/bin/env python3

'''
OPS445 Assignment 2 - Winter 2023
Program: assignment2.py
Author: "Santosh Bhandari"
The python code in this file is original work written by
"Santosh Bhandari". No code in this file is copied from any other source
except those provided by the course instructor, including any person,
textbook, or on-line resource. I have not shared this python script
with anyone or anything except for submission for grading.
I understand that the Academic Honesty Policy will be enforced and
violators will be reported and appropriate action will be taken.

Description: Assignment 2 Milestone 2

Date: 2023/11/29

'''

import argparse
import os
import sys

def parse_command_args() -> object:
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts", epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action='store_true', help="Display memory sizes in human-readable format (KB, MB, GB).")
    parser.add_argument("-r", "--running-only", action='store_true', help="Show memory use of running processes only.")
    parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use is not.")
    args = parser.parse_args()
    return args

def percent_to_graph(percent: float, length: int = 20) -> str:
    """
    Converts a percentage value to a string representing a bar graph.
    """
    hashes = int(percent * length)
    graph = '#' * hashes + ' ' * (length - hashes)
    return graph

def get_sys_mem() -> int:
    """
    Return total system memory (used or available) in kB.
    Reads from '/proc/meminfo' to find 'MemTotal'.
    """
    with open('/proc/meminfo', 'r') as file:
        for line in file:
            if 'MemTotal' in line:
                return int(line.split()[1])
    return 0

def get_avail_mem() -> int:
    """
    Return total memory that is currently available.
    Reads from '/proc/meminfo' to find 'MemAvailable'.
    """
    with open('/proc/meminfo', 'r') as file:
        for line in file:
            if 'MemAvailable' in line:
                return int(line.split()[1])
    return 0

def pids_of_prog(app_name: str) -> list:
    """
    Given an app name, return all PIDs associated with the app.
    """
    pids_output = os.popen(f'pidof {app_name}').read().strip()
    pids = pids_output.split() if pids_output else []
    return pids

def rss_mem_of_pid(proc_id: str) -> int:
    """
    Given a process ID, return the resident memory used, zero if not found.
    """
    rss_memory = 0
    with open(f'/proc/{proc_id}/status', 'r') as file:
        for line in file:
            if 'VmRSS' in line:
                rss_memory = int(line.split()[1])
                break
    return rss_memory

def bytes_to_human_r(kibibytes: int, decimal_places: int = 2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    suf_count = 0
    result = kibibytes
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

if __name__ == "__main__":
    args = parse_command_args()
    total_memory = get_sys_mem()

    if args.program:
        pids = pids_of_prog(args.program)
        if not pids:
            print(f"{args.program} not found.")
            sys.exit()

        total_used_by_program = 0
        for pid in pids:
            rss = rss_mem_of_pid(pid)
            total_used_by_program += rss
            percent = rss / total_memory
            graph = percent_to_graph(percent, args.length)
            mem_display = bytes_to_human_r(rss, 2) if args.human_readable else f"{rss} kB"
            total_mem_display = bytes_to_human_r(total_memory, 2) if args.human_readable else f"{total_memory} kB"
            print(f"{pid}\t\t[{graph} | {percent:.0%}] {mem_display}/{total_mem_display}")

        percent_total = total_used_by_program / total_memory
        graph_total = percent_to_graph(percent_total, args.length)
        total_mem_display = bytes_to_human_r(total_used_by_program, 2) if args.human_readable else f"{total_used_by_program} kB"
        print(f"{args.program}\t\t[{graph_total} | {percent_total:.0%}] {total_mem_display}/{bytes_to_human_r(total_memory, 2) if args.human_readable else f'{total_memory} kB'}")
    else:
        used_memory = total_memory - get_avail_mem()
        percent_used = used_memory / total_memory
        graph = percent_to_graph(percent_used, args.length)
        mem_display = bytes_to_human_r(used_memory, 2) if args.human_readable else f"{used_memory} kB"
        total_mem_display = bytes_to_human_r(total_memory, 2) if args.human_readable else f"{total_memory} kB"
        print(f"Memory\t\t[{graph} | {percent_used:.0%}] {mem_display}/{total_mem_display}")

