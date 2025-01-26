# interpreter.py

import re
import math
import dataclasses
from typing import Optional

@dataclasses.dataclass(frozen=True)
class Value:
  @property
  def name(self) -> 'Value':
    raise NoSuchProperty('name', self)

  @property
  def body(self) -> 'Value':
    raise NoSuchProperty('body', self)

  @property
  def fst(self) -> 'Value':
    raise NoSuchProperty('fst', self)

  @property
  def snd(self) -> 'Value':
    raise NoSuchProperty('snd', self)

  @property
  def enum(self) -> 'Value':
    raise NoSuchProperty('enum', self)

  @property
  def children(self) -> 'Value':
    raise NoSuchProperty('children', self)

@dataclasses.dataclass(frozen=True)
class Id(Value):
  def __str__(self):
    return ''

@dataclasses.dataclass(frozen=True)
class Constant(Value):
  _name: str

  @property
  def name(self) -> str:
    return self._name

  def __str__(self) -> str:
    return self._name

@dataclasses.dataclass(frozen=True)
class Variable(Value):
  _name: str

  @property
  def name(self) -> str:
    return self._name

  def __str__(self) -> str:
    return self._name

@dataclasses.dataclass(frozen=True)
class Catenate(Value):
  _children: list[Value]

  @property
  def children(self) -> list[Value]:
    return self._children

  def __str__(self) -> str:
    children = [f'{child}' for child in self._children]
    return ' '.join(children)

@dataclasses.dataclass(frozen=True)
class Quote(Value):
  _body: Value

  @property
  def body(self) -> Value:
    return self._body

  def __str__(self) -> str:
    return f'[{self._body}]'

@dataclasses.dataclass(frozen=True)
class Inl(Value):
  _enum: Value

  @property
  def enum(self) -> Value:
    return self._enum

  @property
  def body(self) -> Value:
    return RunInl(self._enum)

  def __str__(self) -> str:
    return f'{self._enum} J'

@dataclasses.dataclass(frozen=True)
class Inr(Value):
  _enum: Value

  @property
  def enum(self) -> Value:
    return self._enum

  @property
  def body(self) -> Value:
    return RunInr(self._enum)

  def __str__(self) -> str:
    return f'{self._enum} K'

@dataclasses.dataclass(frozen=True)
class Unit(Value):
  @property
  def body(self) -> Value:
    return Id()

  def __str__(self) -> str:
    return f'[]'

@dataclasses.dataclass(frozen=True)
class Pair(Value):
  _fst: Value
  _snd: Value

  @property
  def fst(self) -> Value:
    return self._fst

  @property
  def snd(self) -> Value:
    return self._snd

  @property
  def body(self) -> Value:
    return RunPair(self._fst, self._snd)

  def __str__(self) -> str:
    return f'{self._fst} {self._snd} L'

@dataclasses.dataclass(frozen=True)
class RunInl(Value):
  _enum: Value

  @property
  def enum(self) -> Value:
    return self._enum

  def __str__(self) -> str:
    return f'{self._enum} J H'

@dataclasses.dataclass(frozen=True)
class RunInr(Value):
  _enum: Value

  @property
  def enum(self) -> Value:
    return self._enum

  def __str__(self) -> str:
    return f'{self._enum} K H'

@dataclasses.dataclass(frozen=True)
class RunPair(Value):
  _fst: Value
  _snd: Value

  @property
  def fst(self) -> Value:
    return self._fst

  @property
  def snd(self) -> Value:
    return self._snd

  def __str__(self) -> str:
    return f'{self._fst} {self._snd} L H'

@dataclasses.dataclass(frozen=True)
class String(Value):
  _value: str

  @property
  def string(self) -> str:
    return self._value

  def __str__(self) -> str:
    return f'"{self._value}"'

@dataclasses.dataclass(frozen=True)
class Prompt(Value):
  _value: str

  @property
  def prompt(self) -> str:
    return self._value

  def __str__(self) -> str:
    return f'{{{self._value}}}'

@dataclasses.dataclass
class Panic(Exception):
  pass

@dataclasses.dataclass
class NoMoreData(Panic):
  state: 'State'

@dataclasses.dataclass
class NoMoreCode(Panic):
  state: 'State'

@dataclasses.dataclass
class NoSuchProperty(Panic):
  property: str
  value: Value

@dataclasses.dataclass
class Unreadable(Panic):
  source: str
  message: str

@dataclasses.dataclass
class Unexpected(Panic):
  expected: str
  actual: Value

@dataclasses.dataclass
class Unknown(Panic):
  value: Value
  state: 'State'

def _is_separator(char: str) -> bool:
  return char.isspace() or char in ['[', ']']

class Interpreter:
  dictionary: dict[str, Value]

  def __init__(self):
    self.dictionary = {}

  def __getitem__(self, key):
    return self.dictionary[key]

  def __setitem__(self, key, value):
    self.dictionary[key] = value

  @property
  def id(self) -> Value:
    return Id()

  @property
  def unit(self) -> Value:
    return Unit()

  def constant(self, name: str) -> Variable:
    return Constant(name)

  def variable(self, name: str) -> Variable:
    return Variable(name)

  def quote(self, value: Value) -> Quote:
    return Quote(value)

  def pair(self, fst: Value, snd: Value) -> Pair:
    return Pair(fst, snd)

  def inl(self, body: Value) -> Inl:
    return Inl(body)

  def inr(self, body: Value) -> Inr:
    return Inr(body)

  def string(self, value: str) -> String:
    return String(value)

  def prompt(self, value: str) -> Prompt:
    return Prompt(value)

  def catenate(self, *values: list[Value]) -> Catenate:
    buf = []
    for value in values:
      match value:
        case Id():
          pass
        case Catenate(body):
          buf.extend(body)
        case _:
          buf.append(value)
    if len(buf) == 0:
      return Id()
    return Catenate(buf)

  def read(
    self,
    src: str,
  ) -> Value:
    build = []
    stack = []
    index = 0
    while index < len(src):
      if src[index].isspace():
        while index < len(src) and src[index].isspace():
          index += 1
      elif src[index] == '':
        index += 1
      elif src[index] == '[':
        stack.append(build)
        build = []
        index += 1
      elif src[index] == ']':
        if len(stack) == 0:
          raise Unreadable(f'Unbalanced brackets', src)
        body = self.catenate(*build)
        match body:
          case Id():
            value = self.unit
          case _:
            value = self.quote(body)
        build = stack.pop()
        build.append(value)
        index += 1
      elif src[index] == '"':
        index += 1
        start = index
        while index < len(src) and not src[index] == '"':
          index += 1
        if index >= len(src):
          raise Unreadable(f'Unbalanced quotes', src)
        value = src[start:index]
        value = self.string(value)
        build.append(value)
        index += 1
      elif src[index] == '{':
        index += 1
        start = index
        while index < len(src) and not src[index] == '}':
          index += 1
        if index >= len(src):
          raise Unreadable(f'Unbalanced braces', src)
        value = src[start:index]
        value = self.prompt(value)
        build.append(value)
        index += 1
      elif src[index].isalpha() and src[index].isupper():
        start = index
        index += 1
        while index < len(src) and not _is_separator(src[index]):
          index += 1
        name = src[start:index]
        if not re.match(r'^[A-Z][A-Za-z0-9_-]*$', name):
          raise Unreadable(f'Unknown symbol: {name}', src)
        value = self.constant(name)
        build.append(value)
      else:
        start = index
        index += 1
        while index < len(src) and not _is_separator(src[index]):
          index += 1
        name = src[start:index]
        if not re.match(r'^[a-z][a-zA-Z0-9_-]*$', name):
          raise Unreadable(f'Unknown symbol: {name}', src)
        value = self.variable(name)
        build.append(value)
    if len(stack) > 0:
      raise Unreadable(f'Unbalanced brackets', src)
    return self.catenate(*build)

  def rewrite(
    self,
    init: str | Value,
    gas: int = 1_000_000,
  ) -> str | Value:
    if isinstance(init, str):
      init = self.read(init)
    state = State(init)
    while len(state.code) > 0 and gas > 0:
      gas -= 1
      hand = state.get_code(0)
      match hand:
        case Catenate(children):
          state.pop_code()
          state.push_code(children)
        case Variable(name):
          if not name in self.dictionary:
            state.thunk()
            gas = 0
            continue
          binding = self.dictionary[name]
          state.pop_code()
          state.push_code(binding)
        case Quote(_):
          state.pop_code()
          state.push_data(hand)
        case Inl(_):
          state.pop_code()
          state.push_data(hand)
        case Inr(_):
          state.pop_code()
          state.push_data(hand)
        case Pair(_):
          state.pop_code()
          state.push_data(hand)
        case String(_):
          state.pop_code()
          state.push_data(hand)
        case Prompt(_):
          # TODO: What do prompts condition on?
          state.thunk()
          gas = 0
          continue
        case RunInl(value):
          try:
            inl = state.get_data(1).body
            inr = state.get_data(0).body
          except Panic as err:
            state.thunk()
            gas = 0
            continue
          state.pop_code()
          state.pop_data(2)
          state.push_code(inl)
          state.push_data(value)
        case RunInr(value):
          try:
            inl = state.get_data(1).body
            inr = state.get_data(0).body
          except Panic as err:
            state.thunk()
            gas = 0
            continue
          state.pop_code()
          state.pop_data(2)
          state.push_code(inr)
          state.push_data(value)
        case RunPair(fst, snd):
          state.pop_code()
          state.push_data(fst)
          state.push_data(snd)
        case Constant(name):
          match name:
            case 'B':
              try:
                value = state.get_data(0)
              except Panic as err:
                state.thunk()
                continue
              state.pop_code()
              state.push_data(value)
            case 'C':
              try:
                value = state.get_data(0)
              except Panic as err:
                state.thunk()
                continue
              state.pop_code()
              state.pop_data()
            case 'D':
              try:
                fst = state.get_data(0)
                snd = state.get_data(1)
              except Panic as err:
                state.thunk()
                continue
              state.pop_code()
              state.pop_data(2)
              state.push_data(fst)
              state.push_data(snd)
            case 'F':
              try:
                lhs = state.get_data(1).body
                rhs = state.get_data(0).body
              except Panic as err:
                state.thunk()
                continue
              state.pop_code()
              state.pop_data(2)
              state.push_code(self.quote(self.catenate(lhs, rhs)))
            case 'G':
              try:
                value = state.get_data(0)
              except Panic as err:
                state.thunk()
                continue
              state.pop_code()
              state.pop_data()
              state.push_data(self.quote(value))
            case 'H':
              try:
                body = state.get_data(0).body
              except Panic as err:
                state.thunk()
                gas = 0
                continue
              state.pop_code()
              state.pop_data()
              state.push_code(body)
            case 'J':
              try:
                value = state.get_data(0)
              except Panic as err:
                state.thunk()
                continue
              state.pop_code()
              state.pop_data()
              state.push_data(self.inl(value))
            case 'K':
              try:
                value = state.get_data(0)
              except Panic as err:
                state.thunk()
                continue
              state.pop_code()
              state.pop_data()
              state.push_data(self.inr(value))
            case 'L':
              try:
                fst = state.get_data(1)
                snd = state.get_data(0)
              except Panic as err:
                state.thunk()
                continue
              state.pop_code()
              state.pop_data(2)
              state.push_data(self.pair(fst, snd))
            case 'M':
              pass
            case 'N':
              state.thunk()
              gas = 0
              continue
        case _:
          raise Unknown(hand, state)
    value = self.catenate(*state.sink, *state.data, *reversed(state.code))
    return value

class State:
  code: list[Value]
  data: list[Value]
  sink: list[Value]

  def __init__(self, value: Value):
    self.code = [value]
    self.data = []
    self.sink = []

  @property
  def has_code(self) -> bool:
    return len(self.code) > 0

  def get_data(self, index: int = 0) -> Value:
    assert index >= 0
    if index >= len(self.data):
      raise NoMoreData(self)
    return self.data[len(self.data)-1-index]

  def pop_data(self, length: int = 1):
    assert length > 0
    if length > len(self.data):
      raise NoMoreData(self)
    self.data = self.data[:len(self.data)-length]

  def push_data(self, value: Value | list[Value]):
    if isinstance(value, list):
      self.data.extend(reversed(value))
    else:
      self.data.append(value)

  def get_code(self, index: int) -> Value:
    if index >= len(self.code):
      raise NoMoreCode(self)
    return self.code[len(self.code)-1-index]

  def pop_code(self):
    if len(self.code) == 0:
      raise NoMoreCode(self)
    self.code.pop()

  def push_code(self, value: Value | list[Value]):
    if isinstance(value, list):
      self.code.extend(reversed(value))
    else:
      self.code.append(value)

  def thunk(self):
    self.sink.extend(self.data)
    self.data = []
    if len(self.code) > 0:
      hand = self.code.pop()
      self.sink.append(hand)

# test_interpreter.py

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
