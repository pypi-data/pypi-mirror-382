import asyncio
import sys
import tempfile
import shortuuid
import datetime
from typing import List
import os
import glob as glob_module
import re
_no_ranges_template = r"""
The content of {file_path}:
```
{content}```
"""

_has_ranges_template = r"""
The content of {file_path} in {ranges} lines:
```
{content}
```
"""
_insert_content = r"""
Insert the following content into {file_path} at line {line_num} successfully.
The content of {file_path} in {start}-->{end} lines:
```
{content}
```
"""

_write_content = r"""
Write {file_path} successfully. The new content snippet:
```
{content}```
"""
_run_code = r"""
<returncode>{returncode}</returncode>
<stdout>{stdout_str}</stdout>
<stderr>{stderr_str}</stderr>
"""


def _view_text(file_path: str, ranges: List[str] = None) -> str:
    with open(file_path, "r") as fp:
        lines = fp.readlines()

    r_max = len(lines)
    if ranges:
        l, r = ranges
        if l > r_max:
            raise ValueError(f"Invalid range: {ranges}")
        return "".join(
            [
                f"{idx}: {line}"
                for idx, line in enumerate(lines[l - 1, min(r, r_max)], l)
            ]
        )
    return "".join([f"{idx}: {line}" for idx, line in enumerate(lines, 1)])


def _cal_view_ranges(
    old: int, new: int, start: int, end: int, extra_line: int = 5
) -> tuple[int, int]:
    view_start = max(1, start - extra_line)
    delta_line = new - old
    view_end = min(end + delta_line + extra_line, new)
    return view_start, view_end


def view_text(file_path: str, ranges: List[str] = None) -> str:
    """
    View the file content in the specified range with line numbers.
    If `ranges` is not provided, the entire file will be returned.

    Args:
        file_path: The target file path
        ranges: The range of lines to be viewed (e.g. lines 1 to 100: [1, 100]), inclusive. If not provided, the entire file will be returned. To view the last 100 lines, use [-100, -1].

    Returns:
        The content of the file in the specified range with line numbers.
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")

    try:
        content = _view_text(file_path, ranges)
    except Exception as e:
        raise ValueError(f"Error reading file: {file_path},error: {e}")
    if ranges:
        return _has_ranges_template.format(
            file_path=file_path, ranges=ranges, content=content
        )
    return _no_ranges_template.format(file_path=file_path, content=content)


def insert_text_file(file_path: str, content: str, line_num: int) -> str:
    """
    Insert the content at the specified line number in a text file.
    If the line number exceeds the number of lines in the file, it will be appended to the end of the file.

    Args:
        file_path: The target file path
        content: The content to be inserted
        line_num: The line number at which the content should be inserted, starting from 1. If exceeds the number of lines in the file, it will be appended to the end of the file.

    Returns:
        The content of the file in the specified range with line numbers.
    """
    if line_num <= 0:
        raise ValueError(f"Invalid line number: {line_num}")
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as fp:
            fp.write(content + "\n")

        return ValueError(f"File not found: {file_path},has been created")

    with open(file_path, "r", encoding="utf-8") as fp:
        lines = fp.readlines()
    new_lines: List[str] = None
    if line_num == len(lines) + 1:
        new_lines = lines + ["\n" + content]
    elif line_num < len(lines) + 1:
        new_lines = (
            lines[: line_num - 1] + ["\n" + content + "\n"] + lines[line_num - 1 :]
        )
    else:
        return ValueError(
            f"Invalid line number: {line_num}.correct ranges: 1 to{len(lines)+1}"
        )

    with open(file_path, "w", encoding="utf-8") as fp:
        fp.writelines(new_lines)

    start, end = _cal_view_ranges(
        len(lines), len(new_lines), line_num, line_num, extra_line=5
    )

    show_content = _view_text(file_path, [f"{start},{end}"])
    return _insert_content.format(
        file_path=file_path,
        line_num=line_num,
        start=start,
        end=end,
        content=show_content,
    )


def write_text_file(
    file_path: str, content: str, ranges: None | tuple[int, int] = None
) -> str:
    """
    Create/Replace/Overwrite content in a text file. When `ranges` is provided, the content will be replaced in the specified range. Otherwise, the entire file (if exists) will be overwritten.

    Args:
        file_path: The target file path
        content: The content to be written
        ranges: The range of lines to be replaced. If `None`, the entire file will be overwritten.

    Returns:
        The content of the file in the specified range with line numbers.
    """
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as fp:
            fp.write(content + "\n")
        if ranges:
            return f"create and write {file_path} successfully, ranges: {ranges} cannot be applied ,because the file dos not exist"
        return f"create and write {file_path} successfully"
    with open(file_path, "r", encoding="utf-8") as fp:
        lines = fp.readlines()

    if ranges:
        l, r = ranges
        if l > r:
            raise ValueError(f"Invalid range: {ranges}")
        if l > len(lines):
            raise ValueError(
                f"Invalid range: {ranges},the file only has {len(lines)} lines"
            )

        new_content = lines[: l - 1] + ["\n" + content + "\n"] + lines[r - 1 :]
        with open(file_path, "w", encoding="utf-8") as fp:
            fp.write("".join(new_content))

        with open(file_path, "r", encoding="utf-8") as fp:
            new_lines = fp.readlines()

        start, end = _cal_view_ranges(len(lines), len(new_lines), l, r, extra_line=5)

        show_content = "".join(
            [
                f"{idx+start}: {line}"
                for idx, line in enumerate(new_lines[start - 1, end])
            ]
        )
        return _write_content.format(file_path=file_path, content=show_content)
    with open(file_path, "w", encoding="utf-8") as fp:
        fp.write(content + "\n")

    return f"overwrite {file_path} successfully"

 
async def execute_python_code(
    code: str,
    timeout: float = 300,
) -> str:
    """
    Execute the given python code in a temp file and capture the return code, standard output and error. Note you must `print` the output to get the result, and the tmp file will be removed right after the execution.

    Args:
        code: The Python code to be executed
        timeout: The maximum time (in seconds) allowed for the code to run

    Returns:
        The return code, standard output and error.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, f"tmp_{shortuuid.uuid()}.py")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(code)

        proc = asyncio.create_subprocess_exec(
            sys.executable,
            "-u",
            temp_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            asyncio.wait_for(proc.wait(), timeout=timeout)
            stdout, stderr = proc.communicate()
            stdout_str = stdout.decode("utf-8")
            stderr_str = stderr.decode("utf-8")
            returncode = proc.returncode

        except asyncio.TimeoutError:
            stderr_suffix = f"TimeoutError: The code execution exceeded the timeout of {timeout} seconds."
            returncode = -1
            try:
                proc.terminate()
                stdout, stderr = proc.communicate()
                stdout_str = stdout.decode("utf-8")
                stderr_str = stderr.decode("utf-8")
                if stderr_str:
                    stderr_str += f"\n{stderr_suffix}"
                else:
                    stderr_str = stderr_suffix
            except ProcessLookupError:
                stdout_str = ""
                stderr_str = stderr_suffix

        return _run_code.format(
            returncode=returncode, stdout_str=stdout_str, stderr_str=stderr_str
        )


async def execute_shell_command(
    command: str,
    timeout: int = 300,
) -> str:
    """
    Execute the given command and return the return code, standard output and error within <returncode></returncode>, <stdout></stdout> and <stderr></stderr> tags

    Args:
        command: The shell command to execute
        timeout: The maximum time (in seconds) allowed for the command to run

    Returns:
        The return code, standard output and error.
    """

    proc = asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        bufsize=0,
    )

    try:
        asyncio.wait_for(proc.wait(), timeout=timeout)
        stdout, stderr = proc.communicate()
        stdout_str = stdout.decode("utf-8")
        stderr_str = stderr.decode("utf-8")
        returncode = proc.returncode

    except asyncio.TimeoutError:
        stderr_suffix = f"TimeoutError: The command execution exceeded the timeout of {timeout} seconds."
        returncode = -1
        try:
            proc.terminate()
            stdout, stderr = proc.communicate()
            stdout_str = stdout.decode("utf-8")
            stderr_str = stderr.decode("utf-8")
            if stderr_str:
                stderr_str += f"\n{stderr_suffix}"
            else:
                stderr_str = stderr_suffix
        except ProcessLookupError:
            stdout_str = ""
            stderr_str = stderr_suffix

    return _run_code.format(
        returncode=returncode, stdout_str=stdout_str, stderr_str=stderr_str
    )


def get_current_time(timezone_offset: int = 8) -> dict:
    """
    Get detailed current time with specified timezone offset,if you quickly want to get local time, don't specify this parameter.

    Args:
        timezone_offset: Timezone offset in hours from UTC (default: 8 for China), this is used to convert UTC time to local time.

    Returns:
        The current time in the specified timezone.
    """
    utc_time = datetime.datetime.now(datetime.timezone.utc)
    timezone = datetime.timezone(datetime.timedelta(hours=timezone_offset))
    local_time = utc_time.astimezone(timezone)
    return f"utc_time: \n{utc_time}\nlocal_time: \n{local_time}"


def get_time() -> str:
    """
    Get current time message quickly!!!

    Returns:
        The current time message.
    """
    return f"Current time is {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def ls(path: str = ".", show_hidden: bool = False, long_format: bool = True) -> str:
    """
    List files and directories in the given path (similar to Linux ls command).

    Args:
        path: The directory path to list (default: current directory)
        show_hidden: Whether to show hidden files (starting with .)
        long_format: Whether to show detailed information like permissions, size, date

    Returns:
        A formatted string showing directory contents.
    """
    if not os.path.exists(path):
        return f"ls: cannot access '{path}': No such file or directory"

    if not os.path.isdir(path):
        if long_format:
            try:
                stat_info = os.stat(path)
                import stat
                from datetime import datetime
                mode = stat.filemode(stat_info.st_mode)
                size = stat_info.st_size
                mtime = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

                return f"{mode} {size:>8} {mtime} {os.path.basename(path)}"
            except:
                return os.path.basename(path)
        else:
            return os.path.basename(path)

    try:
        entries = os.listdir(path)
    except PermissionError:
        return f"ls: cannot open directory '{path}': Permission denied"

    if not show_hidden:
        entries = [e for e in entries if not e.startswith('.')]

    dirs = []
    files = []

    for entry in sorted(entries, key=str.lower):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            dirs.append(entry + '/')
        else:
            files.append(entry)

    all_entries = dirs + files

    if long_format:
        result_lines = []
        for entry in all_entries:
            name = entry.rstrip('/')
            full_path = os.path.join(path, name)
            try:
                stat_info = os.stat(full_path)
                import stat
                from datetime import datetime

                mode = stat.filemode(stat_info.st_mode)
                size = stat_info.st_size
                mtime = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

                result_lines.append(f"{mode} {size:>8} {mtime} {entry}")
            except:
                result_lines.append(f"????????? {'?':>8} {'?':>19} {entry}")

        return '\n'.join(result_lines)
    else:
        if not all_entries:
            return ""

        try:
            terminal_width = os.get_terminal_size().columns
        except:
            terminal_width = 80

        max_len = max(len(entry) for entry in all_entries) if all_entries else 0

        col_width = max_len + 2
        num_cols = max(1, terminal_width // col_width)

        result_lines = []
        for i in range(0, len(all_entries), num_cols):
            row_entries = all_entries[i:i + num_cols]
            row = "  ".join(entry.ljust(col_width) for entry in row_entries)
            result_lines.append(row.rstrip())

        return '\n'.join(result_lines)

def tree(path: str = ".", show_hidden: bool = False, max_depth: int = None) -> str:
    """
    Display directory tree structure recursively (similar to Linux tree command).

    Args:
        path: The directory path to display tree for (default: current directory)
        show_hidden: Whether to show hidden files and directories (starting with .)
        max_depth: Maximum depth to traverse (None for unlimited)

    Returns:
        A formatted string showing the directory tree structure.
    """
    if not os.path.exists(path):
        return f"tree: '{path}': No such file or directory"

    if not os.path.isdir(path):
        return f"tree: '{path}': Not a directory"

    path = os.path.abspath(path)
    result = [os.path.basename(path)]

    def _build_tree(current_path: str, prefix: str = "", depth: int = 0) -> list:
        if max_depth is not None and depth >= max_depth:
            return []

        try:
            entries = os.listdir(current_path)
        except PermissionError:
            return [f"{prefix}└── [Permission denied]"]

        if not show_hidden:
            entries = [e for e in entries if not e.startswith('.')]

        dirs = []
        files = []
        for entry in sorted(entries, key=str.lower):
            full_path = os.path.join(current_path, entry)
            if os.path.isdir(full_path):
                dirs.append(entry)
            else:
                files.append(entry)

        entries = dirs + files
        lines = []

        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)
            full_path = os.path.join(current_path, entry)

            if is_last:
                connector = "└── "
                next_prefix = prefix + "    "
            else:
                connector = "├── "
                next_prefix = prefix + "│   "

            if os.path.isdir(full_path):
                lines.append(f"{prefix}{connector}{entry}/")
                subtree = _build_tree(full_path, next_prefix, depth + 1)
                lines.extend(subtree)
            else:
                lines.append(f"{prefix}{connector}{entry}")

        return lines

    tree_lines = _build_tree(path)
    result.extend(tree_lines)

    total_dirs = 0
    total_files = 0

    for root, dirs, files in os.walk(path):
        if max_depth is not None and root.replace(path, '').count(os.sep) >= max_depth:
            continue
        if not show_hidden:
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]
        total_dirs += len(dirs)
        total_files += len(files)

    result.append("")
    result.append(f"{total_dirs} directories, {total_files} files")

    return '\n'.join(result)

def pwd() -> str:
    """
    Get the current working directory.

    Returns:
        The current working directory path.
    """
    return os.getcwd()

def glob(pattern:str,path:str='.')  ->dict:
    """
    Find files matching the given glob pattern, supporting recursive search.

    Args:
        pattern: The glob pattern to match (e.g., "*.py", "**/*.txt")
        path: The base directory to search in (default: current directory)

    Returns:
        A dictionary with 'matched_files' key containing list of matched file paths,
        and 'count' key with the number of matches.
    """
    try:
        base_path = os.path.abspath(path)

        if pattern.startswith('**'):
            full_pattern = os.path.join(base_path, pattern)
            matches = glob_module.glob(full_pattern, recursive=True)
        else:
            full_pattern = os.path.join(base_path, pattern)
            matches = glob_module.glob(full_pattern, recursive=False)

        relative_matches = []
        for match in matches:
            try:
                relative_path = os.path.relpath(match, base_path)
                relative_matches.append(relative_path)
            except ValueError:
                relative_matches.append(match)

        return {
            'matched_files': relative_matches,
            'count': len(relative_matches),
            'pattern': pattern,
            'search_path': path
        }

    except Exception as e:
        return {
            'error': str(e),
            'pattern': pattern,
            'search_path': path,
            'matched_files': [],
            'count': 0
        }

def grep(pattern:str,glob:str,path:str='.') ->dict:
    """
    Search for a pattern in files matching the glob pattern, supporting recursive search.

    Args:
        pattern: The regex pattern to search for in file contents
        glob: The glob pattern to match files (e.g., "*.py", "**/*.txt")
        path: The base directory to search in (default: current directory)

    Returns:
        A dictionary with search results, including matched files, line numbers,
        and matching lines.
    """
    try:
        glob_result = glob(glob, path)
        if 'error' in glob_result:
            return {
                'error': f"Glob error: {glob_result['error']}",
                'search_pattern': pattern,
                'glob_pattern': glob,
                'search_path': path,
                'results': [],
                'total_matches': 0
            }

        matched_files = glob_result['matched_files']
        results = []
        total_matches = 0

        try:
            regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        except re.error as e:
            return {
                'error': f"Invalid regex pattern: {e}",
                'search_pattern': pattern,
                'glob_pattern': glob,
                'search_path': path,
                'results': [],
                'total_matches': 0
            }

        base_path = os.path.abspath(path)
        for file_path in matched_files:
            full_path = os.path.join(base_path, file_path)

            if not os.path.isfile(full_path):
                continue

            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                matches = []
                lines = content.splitlines()
                for line_num, line in enumerate(lines, 1):
                    if regex.search(line):
                        matches.append({
                            'line_number': line_num,
                            'line_content': line.strip(),
                            'match': regex.findall(line)
                        })

                if matches:
                    results.append({
                        'file': file_path,
                        'matches': matches,
                        'match_count': len(matches)
                    })
                    total_matches += len(matches)

            except (IOError, OSError) as e:
                results.append({
                    'file': file_path,
                    'error': str(e),
                    'matches': [],
                    'match_count': 0
                })

        return {
            'search_pattern': pattern,
            'glob_pattern': glob,
            'search_path': path,
            'results': results,
            'total_matches': total_matches,
            'files_searched': len(matched_files)
        }

    except Exception as e:
        return {
            'error': str(e),
            'search_pattern': pattern,
            'glob_pattern': glob,
            'search_path': path,
            'results': [],
            'total_matches': 0
        }
# time_mcp_client = StdIoClient(
#     name="time",
#     command="py",
#     args=["-m", "mcp_server_time"],
#     env={},
#     cwd=None,
#     encoding="utf-8",
#     encoding_error_handler="strict",
# )


# def get_trivily_mcp_client(trivily_api_key: str) -> StdIoClient:

#     trvily_mcp_client = StdIoClient(
#         name="trvily-mcp",
#         command="npx",
#         args=["-y", "trvily-mcp@0.1.4"],
#         env={"TRVILY_API_KEY": trivily_api_key},
#         cwd=None,
#         encoding="utf-8",
#         encoding_error_handler="strict",
#     )
#     return trvily_mcp_client


# sequential_thinking_client = StdIoClient(
#     name="sequential-thinking",
#     command="npx",
#     args=["-y", "@modelcontextprotocol/server-sequential-thinking"],
#     env={},
#     cwd=None,
#     encoding="utf-8",
#     encoding_error_handler="strict",
# )


    