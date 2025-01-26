import math
import script
import pytest

@pytest.fixture
def ctx():
  return script.Interpreter()

@pytest.mark.parametrize(
  "source, expected",
  [
    ('[foo] B', '[foo] [foo]'),
    ('[foo] C', ''),
    ('[foo] [bar] D', '[bar] [foo]'),
    ('[foo] [bar] F', '[foo bar]'),
    ('[foo] G', '[[foo]]'),
    ('[foo] H', 'foo'),
    ('[foo] [bar] [value] J H', '[value] foo'),
    ('[foo] [bar] [value] K H', '[value] bar'),
    ('[foo] [bar] L H', '[foo] [bar]'),
    ('"Hello" "world" D', '"world" "Hello"'),
    ('{ Hello, world. }', '{ Hello, world. }'),
  ],
)
def test_eval(ctx, source, expected):
  source = ctx.read(source)
  actual = ctx.rewrite(source)
  assert str(actual) == expected
