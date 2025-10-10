""" runvenv init """
import os
import sys
import pathlib
import hashlib
import argparse
import platform
import subprocess

__version__ = "0.5.1"

REQUIREMENTS_FILES = [
    "requirements.txt",
    ".requirements.txt",
    ".requirements.venv",
]


def _get_venv_path(venv_name):
    if not venv_name:
        venv_name = ".venv"

    venv_path = pathlib.Path(venv_name).absolute()
    return venv_path


def _check_if_up_to_date(venv_name, requirements):
    up_to_date = False
    venv_available = False
    requirements_hash = ""
    venv_path = _get_venv_path(venv_name)
    requirement_path = _get_requirement_path(requirements)

    if requirement_path and requirement_path.exists():
        with open(requirement_path, encoding="utf8") as requirement_file:
            content = requirement_file.read().encode()
            requirements_hash = hashlib.md5(content).hexdigest()

    if venv_path.exists():
        venv_available = True

        if (venv_path / ".runvenv_hash").exists():
            with open(venv_path / ".runvenv_hash", encoding="utf8") as hash_file:
                existing_hash = hash_file.read()
                if existing_hash == requirements_hash:
                    up_to_date = True

    return up_to_date, venv_available, requirements_hash


def _get_requirement_path(requirements):
    cwd_path = pathlib.Path(os.getcwd())
    requirement_path = None
    if requirements:
        requirement_path = pathlib.Path(requirements).absolute()
    else:
        for file in REQUIREMENTS_FILES:
            if (cwd_path / file).exists():
                requirement_path = cwd_path / file
                break

    return requirement_path


def run(venv_name, arguments):
    """ run a list of python arguments inside a venv """
    if not arguments or len(arguments) < 1:
        return

    venv_path = _get_venv_path(venv_name)
    is_windows = platform.system() == "Windows"

    env = os.environ
    venv_bin = venv_path / ("Scripts" if is_windows else "bin")
    env["PATH"] = str(venv_bin) + os.pathsep + env["PATH"]
    env["VIRTUAL_ENV"] = str(venv_path)
    python_exe = pathlib.Path(sys.executable).stem
    arguments = [str(venv_bin / python_exe)] + arguments
    completed = subprocess.run(args=arguments, env=env, check=False)
    if completed.returncode != 0:
        sys.exit(completed.returncode)


def create(venv_name, requirements):
    """ create a venv """
    venv_path = _get_venv_path(venv_name)
    requirement_path = _get_requirement_path(requirements)

    up_to_date, venv_available, requirements_hash = _check_if_up_to_date(
        venv_name, requirement_path)

    if not venv_available:
        subprocess.check_call(
            [sys.executable, "-m", "venv", venv_path]
        )

    if not up_to_date and requirement_path:
        run(
            venv_name=venv_name,
            arguments=["-m", "pip", "install", "-r", str(requirement_path)]
        )

        with open(venv_path / ".runvenv_hash", "w", encoding="utf8") as hash_file:
            hash_file.write(requirements_hash)


def main():
    """ main function called from __main__ """
    parser = argparse.ArgumentParser(
        prog="runvenv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Runs a script or module in a venv and forwards *any* parameter.
This includes non positional arguments like --help, --init, --path, --check, --requirements, etc.

With no parameters given this help will be shown. To only create a venv and not run anything \
you can use the --init parameter. If the venv does not exist yet, it will create it and also install \
all requirements in either reqirements.txt, .requirements.txt or .requirements.venv if available.

To check if a venv is already set up use the parameter --check. \
Depending on the status exit code is:
    0 = up-to-date
    1 = available but not up-to-date
    2 = not available

A custom venv path or requirements file can be configured via parameters.
"""
    )

    parser.add_argument(
        "--init",
        action="store_true",
        help="only initialize the venv"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="check if the venv is set up properly"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=__version__
    )

    parser.add_argument(
        "--path",
        default=".venv",
        help="venv path, either relative to cwd or absolute"
    )

    parser.add_argument(
        "--requirements",
        default=None,
        help="path file with requirements to install in venv"
    )

    parser.add_argument(
        "--module",
        "-m",
        action="store_true",
        help="run a module instead of a python script"
    )

    parser.add_argument(
        "forwards",
        nargs=argparse.REMAINDER,
        help="all remaining arguments will be forwarded"
    )

    args = sys.argv
    if len(args) == 1:
        parser.print_help()
        sys.exit()

    arguments = parser.parse_args(args[1:])

    if arguments.check:
        if arguments.init:
            print("parameter --init has been ignored")

        up_to_date, venv_available, _requirements_hash = _check_if_up_to_date(
            venv_name=arguments.path,
            requirements=arguments.requirements
        )

        if up_to_date:
            sys.exit()
        elif venv_available:
            sys.exit(1)

        sys.exit(2)

    create(
        venv_name=arguments.path,
        requirements=arguments.requirements
    )

    argument_list = ["-m"] if arguments.module else []
    argument_list.extend(arguments.forwards)
    run(
        venv_name=arguments.path,
        arguments=argument_list
    )
