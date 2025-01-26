// script_test.ts

import * as script from "./script.ts";
import { assertEquals } from "https://deno.land/std@0.190.0/testing/asserts.ts";

const testCases = [
  { source: '[foo] B', expected: '[foo] [foo]' },
  { source: '[foo] C', expected: '' },
  { source: '[foo] [bar] D', expected: '[bar] [foo]' },
  { source: '[foo] [bar] F', expected: '[foo bar]' },
  { source: '[foo] G', expected: '[[foo]]' },
  { source: '[foo] H', expected: 'foo' },
  { source: '[inl] [inr] [value] J H', expected: '[value] inl' },
  { source: '[inl] [inr] [value] K H', expected: '[value] inr' },
  { source: '[fst] [snd] L H', expected: '[fst] [snd]' },
  { source: '"Hello" "world" D', expected: '"world" "Hello"' },
  { source: '{ Hello, world. }', expected: '{ Hello, world. }' },
];

testCases.forEach(({ source, expected }, index) => {
  Deno.test(`Test case #${index + 1}: ${source} → ${expected}`, () => {
    const interpreter = new script.Interpreter();
    const parsed = interpreter.read(source);
    const actual = interpreter.rewrite(parsed);
    assertEquals(actual.toString(), expected);
  });
});
