import abc

from toucan.reporter.application_result import ApplicationResult


class Reporter(metaclass=abc.ABCMeta):
    """
    The Abstract Base Class defining a Reporter used by Toucan to report all results to.
    """

    def __init__(self, report_root):
        self.report_root = report_root

    @abc.abstractmethod
    def report_results(self, application_results: list[ApplicationResult]) -> None:
        """
        This method can be used to report application results after a Toucan run.
        The reporter gets all results, and depending on the implementation handles them accordingly, for example write
        them to a file, upload them to a web service, or generate a human-readable report.

        See markdown_reporter.py for an example implementation.

        :param application_results: the application results that should be reported.
        """
        raise NotImplementedError
