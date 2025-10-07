/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use crate::testcase;

testcase!(
    test_double_name_match,
    r#"
match 42:
    case x:  # E: name capture `x` makes remaining patterns unreachable
        pass
    case y:
        pass
print(y)  # E: `y` may be uninitialized
    "#,
);

testcase!(
    test_guard_narrowing_in_match,
    r#"
from typing import assert_type
def test(x: int | bytes | str):
    match x:
        case int():
            assert_type(x, int)
        case _ if isinstance(x, str):
            assert_type(x, str)
    "#,
);

testcase!(
    test_pattern_crash,
    r#"
# Used to crash, see https://github.com/facebook/pyrefly/issues/490
match None:
    case {a: 1}: # E: # E: # E:
        pass
"#,
);

testcase!(
    test_pattern_dict_key_enum,
    r#"
from enum import StrEnum

class MyEnumType(StrEnum):
    A = "a"
    B = "b"

def my_func(x: dict[MyEnumType, int]) -> int:
    match x:
        case {MyEnumType.A: a, MyEnumType.B: b}:
            return a + b
        case _:
            return 0
"#,
);
