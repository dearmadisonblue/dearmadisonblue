// script_test.ts

import * as netcode from "../netcode.ts";
import { assertEquals } from "https://deno.land/std@0.190.0/testing/asserts.ts";

const testCases = [
  { source: '[foo] Copy', expected: '[foo] [foo]' },
  { source: '[foo] Drop', expected: '' },
  { source: '[foo] [bar] Swap', expected: '[bar] [foo]' },
  { source: '[foo] [bar] Cat', expected: '[foo bar]' },
  { source: '[foo] Abs', expected: '[[foo]]' },
  { source: '[foo] App', expected: 'foo' },
  { source: '[inl] [inr] [value] Inl', expected: '[value] inl' },
  { source: '[inl] [inr] [value] Inr', expected: '[value] inr' },
  { source: '[fst] [snd] Pair', expected: '[[fst] [snd]]' },
  { source: '"Hello" "world" Swap', expected: '"world" "Hello"' },
  { source: '{ Hello, world. }', expected: '{ Hello, world. }' },
  { source: '[handler] Shift body0 body1 body2 Reset', expected: '[body0 body1 body2] handler' },
];

testCases.forEach(({ source, expected }, index) => {
  Deno.test(`Test case #${index + 1}: ${source} → ${expected}`, () => {
    const parsed = netcode.read(source);
    const actual = netcode.evaluate(parsed);
    assertEquals(actual.toString(), expected);
  });
});
