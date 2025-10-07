import black
from black import FileMode
from notbadai_ide import api
from .common.diff import get_matches


def format_source_code(code: str):
    """
    Format the source code using black
    """
    try:
        # Format the code using black
        formatted_code = black.format_str(code, mode=FileMode())
        return formatted_code
    except Exception as e:
        # If formatting fails, return the original code
        return code


def start():
    code = api.get_current_file().get_content()
    formatted_code = format_source_code(code)

    matches, formatted_code = get_matches(code, formatted_code)
    api.update_file(formatted_code, matches)
