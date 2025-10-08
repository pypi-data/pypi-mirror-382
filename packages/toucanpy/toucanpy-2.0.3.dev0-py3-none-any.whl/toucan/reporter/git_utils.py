import subprocess
from importlib import resources

from toucan.utils import logger


SCRIPT_DIR = resources.files('toucan.utils.shell_scripts')


def git_checkout_and_pull(repo_root, branch):
    checkout_script = str(SCRIPT_DIR.joinpath('git_checkout.sh'))
    _execute_shell_command(f'{checkout_script} {repo_root} {branch}')


def commit_push_daily(project_root, report_name):
    push_script = str(SCRIPT_DIR.joinpath('git_add_commit_push_daily_summary.sh'))
    _execute_shell_command(f'{push_script} {project_root} {report_name}')


def _execute_shell_command(command):
    """
    Helper function to execute a shell command and log the output. Also checks the returncode and exits if needed.
    :param command: Shell command to execute
    """
    output = subprocess.run(command, shell=True, capture_output=True)  # noqa: S602
    logger.info(f'stdout of command `{command}`:\n{output.stdout.decode()}')
    if output.returncode != 0:
        logger.error(
            f'Command `{command}` exited with return code {output.returncode} and the following output:\n'
            f'{output.stderr.decode()}'
        )
        exit(1)
