class APIRequestError(Exception):
    """API request failed"""
class WrongResponseType(Exception):
    """Getting response not in dictionary form."""


class MissingHomeworkKey(Exception):
    """Homeworks key is missing in response dictionary."""


class HomeworksNotInList(Exception):
    """Getting homeworks not in list."""


class WrongHTTPStatus(Exception):
    """HTTPStatus is not OK"""


class MissingHwrkNameOrStatus(Exception):
    """Homework name or status is missing"""