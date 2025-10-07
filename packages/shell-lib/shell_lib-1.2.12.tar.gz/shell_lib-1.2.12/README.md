### Introduction

`shell-lib` is designed to simplify the writing of shell-like scripts.

This module was co-created with [Google Gemini](https://gemini.google.com/).

[Changelog](https://bitbucket.org/wjssz/shell_lib/src/main/changelog.md)

### Why shell-lib?

- **Clean and readable syntax**: Write scripts in readable Python, freeing from complex shell command syntax.
- **Reliable error handling**: Use Python's exception to manage command failure. If a command fails, by default, it raises a `subprocess.CalledProcessError` exception. For commands that may fail, user can also only check the exit-code.
- **Unified file system operations**: Provide a consistent and intuitive file system operations API, that clearly distinguish between file and directory operations.
- **Cross-platform compatibility**: Write a single script that works across Linux, macOS, and Windows platforms.
- **Rich ecosystem integration**: Easily integrate with both the CLI tool and Python library ecosystems.
- **Lightweight and portable**: Only use Python standard library.
- **Well tested**: Consistent and reliable behavior on different platforms and Python versions.

### Usage

```python
#!/usr/bin/python3
from shell_lib import sh

PROJECT_PATH = "my_project"
FILE = "hello.txt"

# `with sh:` is a *top-level* context manager.
# Its main purpose is, if `sh()` or `sh.safe_run()` fails, return the error
# exit-code from the command. If you don't need this, don't use it.
with sh:
    sh.create_dir(PROJECT_PATH)
    # sh.cd() context manager restores the previous working directory when
    # exiting the code block, even if an exception raised within the code block.
    with sh.cd(PROJECT_PATH):
        sh(f"echo 'Hello, World!' > {FILE}")
        print(f"File size: {sh.get_path_info(FILE).size} bytes")
    sh.remove_dir(PROJECT_PATH)
```
There is a demo script at the bottom of this page.

### API Reference


#### File and Directory Operations

Path parameters can be `str`, `bytes` or `pathlib.Path` object.

- `sh.home_dir() -> Path`: Get the current user's home directory, a `pathlib.Path` object.
- `sh.path(path) -> Path`: Convert a `str`/`bytes` path to a `pathlib.Path` object. Can utilize the rich features of [pathlib](https://docs.python.org/3/library/pathlib.html) module.

- `sh.create_dir(path, *, exist_ok=False)`: Create directory, make all intermediate-level directories needed to contain the leaf directory.
- `sh.remove_file(path, *, ignore_missing=False)`: Remove a file.
- `sh.remove_dir(path, *, ignore_missing=False)`: Recursively remove a directory.
- `sh.clear_dir(path) -> None`: Clear the contents of a directory.
- `sh.copy_file(src, dst, *, remove_existing_dst=False)`: Copy a file.
- `sh.copy_dir(src, dst, *, remove_existing_dst=False)`: Copy a directory.
- `sh.move_file(src, dst, *, remove_existing_dst=False)`: Move a file.
- `sh.move_dir(src, dst, *, remove_existing_dst=False)`: Move a directory.
- `sh.rename_file(src, dst)`: Rename a file.
- `sh.rename_dir(src, dst)`: Rename a directory.

- `sh.list_dir(path)`: List all entry names within a directory.
- `sh.walk_dir(path, top_down=True)`: A generator that traverses a directory tree, yield a tuple(directory_path, file_name).
- `sh.cd(path: str|bytes|Path|None)`: Change the working directory. Can be used as a context manager.

- `sh.split_path(path)`: [os.path.split()](https://docs.python.org/3/library/os.path.html#os.path.split) alias.
- `sh.join_path(*paths)`: [os.path.join()](https://docs.python.org/3/library/os.path.html#os.path.join) alias.

- `sh.path_exists(path) -> bool`: Check if a path exists.
- `sh.is_file(path) -> bool`: Check if a path is a file, or a symlink pointing to a file.
- `sh.is_dir(path) -> bool`: Check if a path is a directory, or a symlink pointing to a directory.
- `sh.is_link(path) -> bool`: Check if a path is a symlink.
- `sh.get_file_size(path) -> int`: Get file size.
- `sh.get_path_info(path) -> PathInfo`: Retrieve detailed information about an existing file or directory:

```text
>>> sh.get_path_info('/usr/bin/')  # directory
PathInfo(path=/usr/bin/, size=69632, ctime=2025-09-16 08:18:21.992288,
mtime=2025-09-16 08:18:21.992288, atime=2025-09-17 09:43:29.210739,
is_dir=True, is_file=False, is_link=False,
is_readable=True, is_writable=False, is_executable=True)

>>> sh.get_path_info('/usr/bin/python3')  # file
PathInfo(path=/usr/bin/python3, size=8021824, ctime=2025-08-29 13:12:47.657879,
mtime=2025-08-15 01:47:21, atime=2025-09-16 15:42:37.201079,
is_dir=False, is_file=True, is_link=True,
is_readable=True, is_writable=False, is_executable=True)
```

#### Shell Command Execution

Execute a command with `shell=True`. Allow shell features like pipe (|) and redirection (>).
```python
sh(command: str, *,
   text: bool = True,
   input: str|bytes|None = None,
   timeout: int|float|None = None,
   alternative_title: str|None = None,
   print_output: bool = True,
   fail_on_error: bool = True) -> subprocess.CompletedProcess

# alternative_title:
#     Print this title instead of the command.
#     Used for commands containing sensitive information.
# print_output:
#     True: streams stdout and stderr to the console.
#     False: stdout and stderr are saved in return value's `stdout`/`stderr` attributes.
# fail_on_error:
#     True: raises a subprocess.CalledProcessError on failure.
#     False: doesn't raise exception, need to check return value's `returncode` attribute
#            to see if it has failed.
```

Compared with sh() above, it runs with `shell=False`. It only accepts a list of strings to prevent shell injection. Use this method when the command contains external input.
```python
sh.safe_run(command: list[str], *,
            text: bool = True,
            input: str|bytes|None = None,
            timeout: int|float|None = None,
            alternative_title: str|None = None,
            print_output: bool = True,
            fail_on_error: bool = True) -> subprocess.CompletedProcess

# Need to use this to run complex PowerShell command:
cmd = "pip freeze | foreach-object { pip install --upgrade $_.split('==')[0] }"
sh.safe_run(['powershell', '-Command', cmd])
```

#### User interaction

- `sh.ask_choice(title: str, *choices: str) -> int`: Display a menu and get a 1-based index from the user's choice.
- `sh.ask_yes_no(title: str) -> bool`: Ask user to answer yes or no.
- `sh.ask_regex_input(title: str, pattern: str, *, print_pattern: bool = False) -> re.Match`: Ask user to input a string, and verify it with a regex pattern.
- `sh.ask_password(title: str = "Please input password") -> str`: Ask user to input a password, not echo on screen. No need to add `:` at the end of `title`.
- `sh.pause(msg: str|None = None) -> None`: Prompt the user to press any key to continue.
- `sh.exit(exit_code: int = 0)`: Exit the script with a specified exit code.

#### Get system information

- `sh.get_preferred_encoding() -> str`: Get the preferred encoding, used for subprocess output or files that don't specify an encoding. If Python UTF-8 mode is enabled, return utf-8. Otherwise, return the system locale encoding.
- `sh.get_locale_encoding() -> str`: Get the system locale encoding. It's not affected by Python UTF-8 mode.
- `sh.get_filesystem_encoding() -> str`: Get the encoding used to convert between str filenames and bytes filenames. On Windows, return utf-8, unless use legacy mode, see PEP-529.
- `sh.get_env(key: str, default: str|None = None) -> str|None`: Get an environment variable. It's more reliable than `os.getenv()`.
- `sh.set_env(key: str, value: str|None, /)` or `sh.set_env(dict: Dict[str, str|None], /)`: Set environment variable(s), `None` means delete, the changes affect the current process and subprocesses. Can also be used as a context manager for automatically restore.
- `sh.get_hostname(hostname_type=sh.HOSTNAME_TYPE_Host) -> str`: Get the host name. hostname_type can be `sh.HOSTNAME_TYPE_Host` or `sh.HOSTNAME_TYPE_FQDN`.
- `sh.get_username() -> str`: Get the current username. On POSIX, if running a script with sudo, see the docstring to learn how to get the username.
- `sh.is_elevated() -> bool`: If the script is running with elevated (admin/root) privilege.
- `sh.is_os(os_mask: int) -> bool`: Test whether it's the OS specified by the parameter.

```python
# os_mask can be:
sh.OS_Windows
sh.OS_Cygwin
sh.OS_Linux
sh.OS_macOS
sh.OS_Unix
sh.OS_Unix_like  # It's (OS_Linux | OS_macOS | OS_Unix | OS_Cygwin)

# Support bit OR (|) combination:
if sh.is_os(sh.OS_Linux | sh.OS_macOS):
    ...
elif sh.is_os(sh.OS_Windows):
    ...
```

### Demo script
```python
#!/usr/bin/python3
import os
from shell_lib import sh
# shell-lib demo script: Build and install cpython on Linux
# Need to install build dependencies first:
# https://devguide.python.org/getting-started/setup-building/#install-dependencies

# Input Python version
m = sh.ask_regex_input('Please input Python version to install (such as 3.13.7)',
                       r'\s*(((\d+)\.(\d+))\.\d+)\s*')
ver = m.group(1)
ver_2 = m.group(2)
ver_info = int(m.group(3)), int(m.group(4))

# Variables
work_dir = sh.home_dir() / 'build_python'
xz_filename = sh.path(f'Python-{ver}.tar.xz')
compile_dir = f'Python-{ver}'
install_dir = sh.path(f'/opt/python{ver_2}')
url = f'https://www.python.org/ftp/python/{ver}/Python-{ver}.tar.xz'

# Check existing installed Python
msg = (f'Install path `{install_dir}` is exsiting, '
       f'overwrite install(yes) or exit(no)?')
if install_dir.is_dir() and not sh.ask_yes_no(msg):
    sh.exit()

# Build options
config = f'./configure --prefix={install_dir}'
optimize = sh.ask_choice('Please choose build options',
                         'PGO + LTO (very slow)',
                         'LTO (slow)',
                         'No optimization',
                         'Debug build')
if optimize == 1:
    config += ' --enable-optimizations --with-lto'
elif optimize == 2:
    config += ' --with-lto'
elif optimize == 3:
    pass
elif optimize == 4:
    config += ' --with-pydebug'

if ver_info >= (3, 13) and sh.ask_yes_no("Build Free-threaded build?"):
    config += ' --disable-gil'

sh.create_dir(work_dir, exist_ok=True)
with sh.cd(work_dir):
    if not xz_filename.is_file() or sh.get_file_size(xz_filename) == 0:
        sh(f'wget --no-proxy -O {xz_filename} {url}')

    password = sh.ask_password('Please input sudo password')
    sh(f'echo {password} | sudo -S rm -rf {compile_dir}',
       alternative_title='Clear building directory')
    sh(f'tar -xvf {xz_filename}', print_output=False)

    with sh.cd(compile_dir):
        # Compile
        with sh.set_env('CFLAGS', '-O2'):
            sh(config, print_output=False)
        sh('make clean')
        sh(f'make -j{os.cpu_count()}')
        sh.pause('Please check for missing modules')

        # Install
        sh(f'echo {password} | sudo -S rm -rf {install_dir}',
           alternative_title='Remove existing install directory')
        sh(f'echo {password} | sudo -S make install',
           alternative_title='Install compiled Python')

    if sh.ask_yes_no('Run unit-tests? (very slow)'):
        sh(f'{install_dir}/bin/python{ver_2} -m test', fail_on_error=False)

    if sh.ask_yes_no('Remove building directory?'):
        sh(f'echo {password} | sudo -S rm -rf {compile_dir}',
           alternative_title='Remove building directory')
```