import re
import dataclasses

############################################################
# Combinators
############################################################

@dataclasses.dataclass(frozen=True)
class Combinator:
  pass

@dataclasses.dataclass(frozen=True)
class Id(Combinator):
  def __str__(self):
    return ''

@dataclasses.dataclass(frozen=True)
class Basic(Combinator):
  name: str

  def __str__(self):
    return self.name

@dataclasses.dataclass(frozen=True)
class Catenate(Combinator):
  body: list[Combinator]

  def __str__(self):
    return ' '.join([str(child) for child in self.body])

@dataclasses.dataclass(frozen=True)
class Quote(Combinator):
  body: Combinator

  def __str__(self):
    return f'[{self.body}]'

def read(code: str) -> Combinator:
  hidden = code
  hidden = hidden.replace('[', '[ ')
  hidden = hidden.replace(']', ' ]')
  hidden = hidden.replace('\t', ' ')
  hidden = hidden.replace('\r', ' ')
  hidden = hidden.replace('\n', ' ')
  words = hidden.split(' ')
  build = []
  stack = []
  for word in words:
    if re.match(r'^[a-z]+$', word):
      comb = Basic(word)
      build.append(comb)
    elif word == '[':
      stack.append(build)
      build = []
    elif word == ']':
      if len(stack) == 0:
        raise ValueError(f'Unbalanced brackets in code:\n```\n{code}\n```')
      comb = Quote(Catenate(build))
      build = stack.pop()
      build.append(comb)
    elif len(word) == 0:
      pass
    else:
      raise ValueError(f'Unknown word `{word}` in code:\n```\n{code}\n```')
  if len(stack) > 0:
    raise ValueError(f'Unbalanced brackets in code:\n```\n{code}\n```')
  return Catenate(build)

def evaluate(state: Combinator) -> Combinator:
  code = [state]
  data = []
  sink = []
  hand = None

  def thunk():
    nonlocal data
    nonlocal sink
    nonlocal hand
    sink.extend(data)
    data = []
    sink.append(hand)

  while len(code) > 0:
    hand = code.pop()
    match hand:
      case Id():
        pass
      case Quote(_):
        data.append(hand)
      case Catenate(body):
        code.extend(reversed(body))
      case Basic(name):
        match name:
          case 'cpy':
            if len(data) == 0:
              thunk()
              continue
            value = data[-1]
            data.append(value)
          case 'drp':
            if len(data) == 0:
              thunk()
              continue
            data.pop()
          case 'swp':
            if len(data) < 2:
              thunk()
              continue
            fst = data[-1]
            snd = data[-2]
            data = data[:-2]
            data.append(fst)
            data.append(snd)
          case 'abs':
            if len(data) == 0:
              thunk()
              continue
            body = data.pop()
            data.append(Quote(body))
          case 'app':
            if len(data) == 0:
              thunk()
              continue
            comb = data[-1]
            match comb:
              case Quote(body):
                data.pop()
                code.append(body)
              case _:
                thunk()
                continue
          case 'cat':
            if len(data) < 2:
              thunk()
              continue
            fst = data[-2]
            snd = data[-1]
            match (fst, snd):
              case Quote(fst), Quote(snd):
                comb = Quote(Catenate([fst, snd]))
                data = data[:-2]
                data.append(comb)
              case _, _:
                thunk()
                continue
          case 'jmp':
            if len(data) == 0:
              thunk()
              continue
            buf = []
            handler = data[-1]
            match handler:
              case Quote(body):
                index = 1
                while index < len(code):
                  point = code[-index]
                  match point:
                    case Basic(name):
                      match name:
                        case 'env':
                          break
                        case _:
                          buf.append(point)
                    case _:
                      buf.append(point)
                  index += 1
                if index > len(code):
                  thunk()
                  continue
                continuation = Quote(Catenate(buf))
                code = code[:-index-1]
                data.pop()
                data.append(continuation)
                code.append(body)
              case _:
                thunk()
                continue
          case 'env':
            thunk()
            continue
          case _:
            thunk()
            continue
  return Catenate(sink+data+list(reversed(code)))

############################################################
# Tests
############################################################

import pytest

@pytest.mark.parametrize(
  "source, expected",
  [
    ('[foo] cpy', '[foo] [foo]'),
    ('[foo] drp', ''),
    ('[foo] [bar] swp', '[bar] [foo]'),
    ('[foo] [bar] cat', '[foo bar]'),
    ('[foo] abs', '[[foo]]'),
    ('[foo] app', 'foo'),
    ('[foo] jmp bar qux env', '[bar qux] foo'),
  ],
)
def test_evaluate(source, expected):
  assert str(evaluate(read(source))) == expected
