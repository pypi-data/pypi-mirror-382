import lark.exceptions


class GDToolkitError(Exception):
    pass


def lark_unexpected_input_to_str(exception: lark.exceptions.UnexpectedInput):
    return str(exception).strip()


def lark_unexpected_token_to_str(exception: lark.exceptions.UnexpectedToken, code: str):
    try:
        return f"{exception.get_context(code)}\n{exception}"
    except:  # pylint: disable=bare-except # noqa: E722, B001
        return f"{exception}".strip()
