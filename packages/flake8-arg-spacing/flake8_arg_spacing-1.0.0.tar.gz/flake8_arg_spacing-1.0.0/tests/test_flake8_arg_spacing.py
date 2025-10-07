
import ast

import pytest
from flake8_arg_spacing import ArgSpacingChecker


@pytest.mark.parametrize('arg, should_report', [
    ('x=- a', True), ('x=not a', True), ('x=a + b', True), ('x=a and b', True), ('x=a <= b', True), ('x=a if b else c', True),
    ('x=-a', False), ('x=a+b', False), ('x=a**b', False), ('x=a', False), ('x=(a + b)', False), ('x=f(a, b)', False), ('x=lambda: a', False),
    ('x = a + b', False), ('x: int', False), ('x: int = a + b', False)
])
@pytest.mark.parametrize('inner_template', [
    '{}',
    'y, {}',
    '*args, {}',
    '*args, y, {}',
    '{}, z=42',
    '{}, **kwargs',
    '{}, /',
])
@pytest.mark.parametrize('main_template, error_code', [
    ('f({})', 101),
    ('def f({}): pass', 102),
    ('async def f({}): pass', 102),
])
def test_checker(arg, should_report, inner_template, main_template, error_code):
    if error_code == 101:
        if 'x:' in arg:
            pytest.skip("Type annotation doesn't make sense for function calls")
        if ', /' in inner_template:
            pytest.skip("Positional-only syntax doesn't make sense for function calls")

    source = main_template.format(inner_template.format(arg))
    extra_newlines = '\n' * (len(arg) - 3)
    tree = ast.parse(extra_newlines + source)
    errors = list(ArgSpacingChecker(tree).run())

    if should_report:
        assert len(errors) == 1
        error = errors[0]
        assert isinstance(error, tuple)
        assert len(error) == 4
        assert error[0] == len(extra_newlines) + 1
        assert error[1] == source.index(arg) + arg.index('=') + 1
        assert error[2] == f"ARG{error_code} confusing spacing around " + ("keyword argument" if error_code == 101 else "parameter default")
        assert error[3] is ArgSpacingChecker
    else:
        assert len(errors) == 0
