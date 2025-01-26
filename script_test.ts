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
  { source: '[foo] [bar] [value] J H', expected: '[value] foo' },
  { source: '[foo] [bar] [value] K H', expected: '[value] bar' },
  { source: '[foo] [bar] L H', expected: '[foo] [bar]' },
  { source: '"Hello" "world" D', expected: '"world" "Hello"' },
  { source: '{ Hello, world. }', expected: '{ Hello, world. }' },
];

testCases.forEach(({ source, expected }, index) => {
  Deno.test(`Test case #${index + 1}: ${source} → ${expected}`, () => {
    const interpreter = new script.Interpreter();
    const parsed = interpreter.read(source);
    const result = interpreter.rewrite(parsed);
    assertEquals(result.toString(), expected);
  });
});
