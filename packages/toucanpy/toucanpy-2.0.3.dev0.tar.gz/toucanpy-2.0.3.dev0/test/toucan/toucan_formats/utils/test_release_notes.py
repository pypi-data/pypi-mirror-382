import re
import unittest

import git

from toucan import version
from toucan.utils import PROJECT_ROOT


def get_issue_number_from_current_branch_name() -> str:
    """
    Get the name of the current Git branch.
    :return: The name of the current branch.
    """
    repo = git.Repo(search_parent_directories=True)
    return repo.active_branch.name.split('-')[0]


def read_release_notes(file_path: str) -> list[str]:
    """
    Read the content of the release notes file.
    :param file_path: The path to the release notes file.
    :return: The content of the release notes file.
    """
    with open(file_path, 'r') as file:
        return file.read().splitlines()


class TestReleaseNotes(unittest.TestCase):
    def setUp(self):
        self.issue_number = get_issue_number_from_current_branch_name()
        self.release_notes_path = f"{PROJECT_ROOT}/RELEASE_NOTES"
        self.release_notes = read_release_notes(self.release_notes_path)
        self.exclusion_patterns = ["rc", "master", "main"]

    def test_release_notes_format_correct(self):
        invalid_lines = []
        # Valid version line: either a version number or just a line full of dashes
        version_pattern = re.compile('(^Version [\\d.]+$)|(^-+$)')
        # Issue: starts with a dash, then one space, then an uppercase issue, then a colon, then ONE space, then any text
        issue_entry = re.compile('^\d+\..*[^.\s]$')
        # indented line: starts with a multiple of 2 spaces, then a dash, then ONE space, then any text
        indented_entry = re.compile('^( {2})+- \S.*$')
        empty_line = re.compile('^$')
        for i, line in enumerate(self.release_notes):
            if version_pattern.match(line):
                continue
            if empty_line.match(line):
                continue
            if issue_entry.match(line):
                continue
            if indented_entry.match(line):
                continue
            # doesn't match anything: invalid line
            invalid_lines.append((i, line))
        invalid_lines = "\n".join([f'line {i+1}: "{line}"' for i, line in invalid_lines])
        self.assertTrue(len(invalid_lines) == 0, f'invalid lines:\n{invalid_lines}')

    def test_branch_in_release_notes(self):
        if not any(exclusion in self.issue_number for exclusion in self.exclusion_patterns):
            self.assertTrue(self.issue_number in "\n".join(self.release_notes))

    def test_version_in_release_notes_same_as_setup(self):
        first_line = self.release_notes[0]
        match = re.search(r'(\d+\.\d+\.\d+)', first_line)
        first_version_in_release_notes = match.group(1) if match else None
        self.assertIsNotNone(first_version_in_release_notes)
        self.assertEqual(first_version_in_release_notes, version.__version__,
                         "Version in release notes is not equal to setup version")


if __name__ == '__main__':
    unittest.main()
