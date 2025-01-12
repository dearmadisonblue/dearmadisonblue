import re
import math
import dataclasses
from typing import Optional

@dataclasses.dataclass(frozen=True)
class Block:
  @property
  def name(self) -> 'Block':
    raise NoSuchProperty('name', self)

  @property
  def body(self) -> 'Block':
    raise NoSuchProperty('body', self)

  @property
  def fst(self) -> 'Block':
    raise NoSuchProperty('fst', self)

  @property
  def snd(self) -> 'Block':
    raise NoSuchProperty('snd', self)

  @property
  def enum(self) -> 'Block':
    raise NoSuchProperty('enum', self)

  @property
  def children(self) -> 'Block':
    raise NoSuchProperty('children', self)

@dataclasses.dataclass(frozen=True)
class Id(Block):
  pass

@dataclasses.dataclass(frozen=True)
class Constant(Block):
  _name: str

  @property
  def name(self) -> str:
    return self._name

  def __str__(self) -> str:
    return self._name

@dataclasses.dataclass(frozen=True)
class Variable(Block):
  _name: str

  @property
  def name(self) -> str:
    return self._name

  def __str__(self) -> str:
    return self._name

@dataclasses.dataclass(frozen=True)
class Catenate(Block):
  _children: list[Block]

  @property
  def children(self) -> list[Block]:
    return self._children

  def __str__(self) -> str:
    children = [f'{child}' for child in self._children]
    return ' '.join(children)

@dataclasses.dataclass(frozen=True)
class Quote(Block):
  _body: Block

  @property
  def body(self) -> Block:
    return self._body

  def __str__(self) -> str:
    return f'[{self._body}]'

@dataclasses.dataclass(frozen=True)
class Inl(Block):
  _enum: Block

  @property
  def enum(self) -> Block:
    return self._enum

  @property
  def body(self) -> Block:
    return RunInl(self._enum)

  def __str__(self) -> str:
    return f'{self._enum} J'

@dataclasses.dataclass(frozen=True)
class Inr(Block):
  _enum: Block

  @property
  def enum(self) -> Block:
    return self._enum

  @property
  def body(self) -> Block:
    return RunInr(self._enum)

  def __str__(self) -> str:
    return f'{self._enum} K'

@dataclasses.dataclass(frozen=True)
class Pair(Block):
  _fst: Block
  _snd: Block

  @property
  def fst(self) -> Block:
    return self._fst

  @property
  def snd(self) -> Block:
    return self._snd

  @property
  def body(self) -> Block:
    return RunPair(self._fst, self._snd)

  def __str__(self) -> str:
    return f'{self._fst} {self._snd} L'

@dataclasses.dataclass(frozen=True)
class RunInl(Block):
  _enum: Block

  @property
  def enum(self) -> Block:
    return self._enum

  def __str__(self) -> str:
    return f'{self._enum} J H'

@dataclasses.dataclass(frozen=True)
class RunInr(Block):
  _enum: Block

  @property
  def enum(self) -> Block:
    return self._enum

  def __str__(self) -> str:
    return f'{self._enum} K H'

@dataclasses.dataclass(frozen=True)
class RunPair(Block):
  _fst: Block
  _snd: Block

  @property
  def fst(self) -> Block:
    return self._fst

  @property
  def snd(self) -> Block:
    return self._snd

  def __str__(self) -> str:
    return f'{self._fst} {self._snd} L H'

@dataclasses.dataclass(frozen=True)
class String(Block):
  _value: str

  @property
  def string(self) -> str:
    return self._value

  def __str__(self) -> str:
    return f'"{self._value}"'

@dataclasses.dataclass(frozen=True)
class Prompt(Block):
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
  block: Block

@dataclasses.dataclass
class Unreadable(Panic):
  source: str
  message: str

@dataclasses.dataclass
class Unexpected(Panic):
  expected: str
  actual: Block

@dataclasses.dataclass
class Unknown(Panic):
  block: Block
  state: 'State'

def _is_separator(char: str) -> bool:
  return char.isspace() or char in ['[', ']']

class Interpreter:
  def __init__(self):
    pass
  
  @property
  def id(self) -> Block:
    return Id()

  @property
  def unit(self) -> Block:
    return self.quote(self.id)

  def constant(self, name: str) -> Variable:
    return Constant(name)

  def variable(self, name: str) -> Variable:
    return Variable(name)

  def quote(self, block: Block) -> Quote:
    return Quote(block)

  def pair(self, fst: Block, snd: Block) -> Pair:
    return Pair(fst, snd)

  def inl(self, body: Block) -> Inl:
    return Inl(body)

  def inr(self, body: Block) -> Inr:
    return Inr(body)

  def string(self, value: str) -> String:
    return String(value)

  def prompt(self, value: str) -> Prompt:
    return Prompt(value)

  def catenate(self, *blocks: list[Block]) -> Catenate:
    buf = []
    for block in blocks:
      match block:
        case Id():
          pass
        case Catenate(body):
          buf.extend(body)
        case _:
          buf.append(block)
    return Catenate(buf)

  def read(
    self,
    src: str,
    parse_strings: bool = True,
  ) -> Block:
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
        block = self.quote(self.catenate(*build))
        build = stack.pop()
        build.append(block)
        index += 1
      elif src[index] == '"':
        index += 1
        start = index
        while index < len(src) and not src[index] == '"':
          index += 1
        if index >= len(src):
          raise Unreadable(f'Unbalanced quotes', src)
        value = src[start:index]
        block = self.string(value)
        build.append(block)
        index += 1
      elif src[index] == '{':
        index += 1
        start = index
        while index < len(src) and not src[index] == '}':
          index += 1
        if index >= len(src):
          raise Unreadable(f'Unbalanced braces', src)
        value = src[start:index]
        block = self.prompt(value)
        build.append(block)
        index += 1
      elif src[index].isalpha() and src[index].isupper():
        start = index
        index += 1
        while index < len(src) and not _is_separator(src[index]):
          index += 1
        name = src[start:index]
        if not re.match(r'^[A-Z]$', name):
          raise Unreadable(f'Unknown symbol: {name}', src)
        block = self.constant(name)
        build.append(block)
      else:
        start = index
        index += 1
        while index < len(src) and not _is_separator(src[index]):
          index += 1
        name = src[start:index]
        # TODO: Is it a good idea to accept arbitrary variable names
        # like this?
        block = self.variable(name)
        build.append(block)
    if len(stack) > 0:
      raise Unreadable(f'Unbalanced brackets', src)
    return self.catenate(*build)

  def eval(
    self,
    init: str | Block,
    gas: int = 1_000_000,
  ) -> str | Block:
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
        case Variable(_):
          state.thunk()
          gas = 0
          continue
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
          # TODO: Prompts
          state.thunk()
          gas = 0
          continue
        case RunInl(block):
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
          state.push_data(block)
        case RunInr(block):
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
          state.push_data(block)
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
    block = self.catenate(*state.sink, *state.data, *reversed(state.code))
    return block

class State:
  code: list[Block]
  data: list[Block]
  sink: list[Block]

  def __init__(self, block: Block):
    self.code = [block]
    self.data = []
    self.sink = []

  def get_data(self, index: int = 0) -> Block:
    assert index >= 0
    if index >= len(self.data):
      raise NoMoreData(self)
    return self.data[len(self.data)-1-index]

  def pop_data(self, length: int = 1):
    assert length > 0
    if length > len(self.data):
      raise NoMoreData(self)
    self.data = self.data[:len(self.data)-length]

  def push_data(self, block: Block | list[Block]):
    if isinstance(block, list):
      self.data.extend(reversed(block))
    else:
      self.data.append(block)

  def get_code(self, index: int) -> Block:
    if index >= len(self.code):
      raise NoMoreCode(self)
    return self.code[len(self.code)-1-index]

  def pop_code(self):
    if len(self.code) == 0:
      raise NoMoreCode(self)
    self.code.pop()

  def push_code(self, block: Block | list[Block]):
    if isinstance(block, list):
      self.code.extend(reversed(block))
    else:
      self.code.append(block)

  def thunk(self):
    self.sink.extend(self.data)
    self.data = []
    if len(self.code) > 0:
      hand = self.code.pop()
      self.sink.append(hand)
