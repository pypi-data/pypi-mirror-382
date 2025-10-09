#!/usr/bin/env python3

# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************


# The purpose of this script is to be the entrypoint for all jobs running on datatailr.
# The main functions of the script are:
#     1. Create a linux user and group for the job.
#     2. Set the environment variables for the job.
#     3. Run the job in a separate process, as the newly created user and pass all relevant environment variables.
# There are muliple environment variables which are required for the job to run.
# Some of them are necessary for the setup stage, which is executed directly in this script as the linux root user.
# Others are passed to the job script, which is executed in a separate process with only the users' privileges and not as a root user.
#
# Setup environment variables:
#     DATATAILR_USER - the user under which the job will run.
#     DATATAILR_GROUP - the group under which the job will run.
#     DATATAILR_UID - the user ID of the user as it is defined in the system.
#     DATATAILR_GID - the group ID of the group as it is defined in the system.
#     DATATAILR_JOB_TYPE - the type of job to run. (batch\service\app\excel\IDE)
# Job environment variables (not all are always relevant, depending on the job type):
#     DATATAILR_BATCH_RUN_ID - the unique identifier for the batch run.
#     DATATAILR_BATCH_ID - the unique identifier for the batch.
#     DATATAILR_JOB_ID - the unique identifier for the job.


import concurrent.futures
import subprocess
import os
import stat
import shlex
import sysconfig
from typing import Optional, Tuple
from datatailr.logging import DatatailrLogger
from datatailr.utils import is_dt_installed

logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()

if not is_dt_installed():
    logger.error("Datatailr is not installed.")
    # sys.exit(1) # TODO: Uncomment after testing


def get_env_var(name: str, default: str | None = None) -> str:
    """
    Get an environment variable.
    If the variable is not set, raise an error.
    """
    if name not in os.environ:
        if default is not None:
            return default
        logger.error(f"Environment variable '{name}' is not set.")
        raise ValueError(f"Environment variable '{name}' is not set.")
    return os.environ[name]


def create_user_and_group() -> Tuple[str, str]:
    """
    Create a user and group for the job.
    The user and group names are taken from the environment variables DATATAILR_USER and DATATAILR_GROUP.
    The group and user are created with the same uid and gid as passed in the environment variables DATATAILR_UID and DATATAILR_GID.
    If the user or group already exists, do nothing.
    """
    user = get_env_var("DATATAILR_USER")
    group = get_env_var("DATATAILR_GROUP")
    uid = get_env_var("DATATAILR_UID")
    gid = get_env_var("DATATAILR_GID")

    # Create group if it does not exist
    os.system(f"getent group {group} || groupadd {group} -g {gid} -o")

    # Create user if it does not exist
    os.system(
        f"getent passwd {user} || useradd -g {group} -s /bin/bash -m {user} -u {uid} -o"
    )

    permissions = (
        stat.S_IWOTH
        | stat.S_IXOTH
        | stat.S_IWUSR
        | stat.S_IRUSR
        | stat.S_IRGRP
        | stat.S_IWGRP
        | stat.S_IXUSR
        | stat.S_IXGRP
    )

    if os.path.exists(f"/home/{user}"):
        os.chmod(f"/home/{user}", permissions)

    if os.path.exists(f"/home/{user}/tmp/.dt"):
        os.chmod(f"/home/{user}/tmp/.dt", permissions)

    return user, group


def prepare_command_argv(command: str | list, user: str, env_vars: dict) -> list[str]:
    if isinstance(command, str):
        command = shlex.split(command)

    python_libdir = sysconfig.get_config_var("LIBDIR")
    ld_library_path = get_env_var("LD_LIBRARY_PATH", None)

    # Base environment variables setup
    base_env = {
        "PATH": get_env_var("PATH", ""),
        "PYTHONPATH": get_env_var("PYTHONPATH", ""),
        "LD_LIBRARY_PATH": ":".join(filter(None, [python_libdir, ld_library_path])),
    }

    merged_env = base_env | env_vars
    env_kv = [f"{k}={v}" for k, v in merged_env.items()]
    return ["sudo", "-u", user, "env", *env_kv, *command]


def run_single_command_non_blocking(
    command: str | list,
    user: str,
    env_vars: dict,
    log_stream_name: Optional[str | None] = None,
) -> int:
    """
    Runs a single command non-blocking and returns the exit code after it finishes.
    This is designed to be run within an Executor.
    """
    argv = prepare_command_argv(command, user, env_vars)
    cmd_label = " ".join(argv[4:])  # For logging purposes

    try:
        if log_stream_name:
            stdout_file_path = f"/opt/datatailr/var/log/{log_stream_name}.log"
            stderr_file_path = f"/opt/datatailr/var/log/{log_stream_name}_error.log"
            with (
                open(stdout_file_path, "ab", buffering=0) as stdout_file,
                open(stderr_file_path, "ab", buffering=0) as stderr_file,
            ):
                proc = subprocess.Popen(argv, stdout=stdout_file, stderr=stderr_file)
        else:
            proc = subprocess.Popen(argv)
        returncode = proc.wait()

        if returncode != 0:
            logger.error(f"Command '{cmd_label}' failed with exit code {returncode}")
        return returncode
    except Exception as e:
        logger.error(f"Execution error for '{cmd_label}': {e}")
        return 1


def run_commands_in_parallel(
    commands: list[str | list],
    user: str,
    env_vars: dict,
    log_stream_names: Optional[list[str | None]] = None,
) -> int:
    """
    Executes two commands concurrently using a ThreadPoolExecutor.
    Returns a tuple of (return_code_cmd1, return_code_cmd2).
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(commands)) as executor:
        futures = []
        for command, log_stream_name in zip(
            commands, log_stream_names or [None] * len(commands)
        ):
            futures.append(
                executor.submit(
                    run_single_command_non_blocking,
                    command,
                    user,
                    env_vars,
                    log_stream_name,
                )
            )
        results = [
            future.result() for future in concurrent.futures.as_completed(futures)
        ]
        return 0 if all(code == 0 for code in results) else 1


def main():
    user, _ = create_user_and_group()
    job_type = get_env_var("DATATAILR_JOB_TYPE")

    env = {
        "DATATAILR_JOB_TYPE": job_type,
        "DATATAILR_JOB_NAME": get_env_var("DATATAILR_JOB_NAME"),
        "DATATAILR_JOB_ID": get_env_var("DATATAILR_JOB_ID"),
    }

    if job_type == "batch":
        run_id = get_env_var("DATATAILR_BATCH_RUN_ID")
        batch_id = get_env_var("DATATAILR_BATCH_ID")
        entrypoint = get_env_var("DATATAILR_BATCH_ENTRYPOINT")
        env = {
            "DATATAILR_BATCH_RUN_ID": run_id,
            "DATATAILR_BATCH_ID": batch_id,
            "DATATAILR_BATCH_ENTRYPOINT": entrypoint,
        } | env
        run_single_command_non_blocking("datatailr_run_batch", user, env)
    elif job_type == "service":
        port = get_env_var("DATATAILR_SERVICE_PORT", 8080)
        entrypoint = get_env_var("DATATAILR_ENTRYPOINT")
        env = {
            "DATATAILR_ENTRYPOINT": entrypoint,
            "DATATAILR_SERVICE_PORT": port,
        } | env
        run_single_command_non_blocking("datatailr_run_service", user, env)
    elif job_type == "app":
        entrypoint = get_env_var("DATATAILR_ENTRYPOINT")
        env = {
            "DATATAILR_ENTRYPOINT": entrypoint,
        } | env
        run_single_command_non_blocking("datatailr_run_app", user, env)
    elif job_type == "excel":
        host = get_env_var("DATATAILR_HOST", "")
        local = get_env_var("DATATAILR_LOCAL", "")
        entrypoint = get_env_var("DATATAILR_ENTRYPOINT")
        local = get_env_var("DATATAILR_LOCAL", False)
        env = {
            "DATATAILR_ENTRYPOINT": entrypoint,
            "DATATAILR_HOST": host,
            "DATATAILR_LOCAL": local,
        } | env
        run_single_command_non_blocking("datatailr_run_excel", user, env)
    elif job_type == "workspace":
        # Set a custom PS1 for the IDE terminal: 17:38|user@my-ide/~/dir/path:$
        env["PS1"] = (
            r"""\[\e[2m\]\A\[\e[0m\]|\[\e[38;5;40m\]\u\[\e[92m\]@${DATATAILR_JOB_NAME:-datatailr}\[\e[0m\]/\[\e[94;1m\]\w\[\e[0m\]\$"""
        )
        os.makedirs("/opt/datatailr/var/log", exist_ok=True)
        ide_command = [
            "code-server",
            "--auth=none",
            "--bind-addr=0.0.0.0:9090",
            f'--app-name="Datatailr IDE {get_env_var("DATATAILR_USER")}"',
        ]
        job_name = get_env_var("DATATAILR_JOB_NAME")
        jupyter_command = [
            "jupyter-lab",
            "--ip='*'",
            "--port=7070",
            "--no-browser",
            "--NotebookApp.token=''",
            "--NotebookApp.password=''",
            f"--ServerApp.base_url=/workspace/{job_name}/jupyter/",
            f"--ServerApp.static_url_prefix=/workspace/{job_name}/jupyter/static/",
            f"--ServerApp.root_dir=/home/{user}",
        ]
        run_commands_in_parallel(
            [ide_command, jupyter_command], user, env, ["code-server", "jupyter"]
        )

    else:
        raise ValueError(f"Unknown job type: {job_type}")


if __name__ == "__main__":
    try:
        logger.debug("Starting job execution...")
        main()
        logger.debug("Job executed successfully.")
    except Exception as e:
        logger.error(f"Error during job execution: {e}")
        raise
