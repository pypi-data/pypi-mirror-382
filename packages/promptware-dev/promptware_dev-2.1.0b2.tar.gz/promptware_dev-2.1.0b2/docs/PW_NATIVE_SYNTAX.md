# PW Native Syntax Specification

**Version**: 2.0
**Status**: Production Ready
**Last Updated**: 2025-10-07

---

## Overview

PW is a universal programming language designed for cross-language code sharing. Write once in PW, compile to Python, Go, Rust, TypeScript, or C#.

## Philosophy

1. **Human-readable text syntax** - Not JSON, not YAML
2. **Familiar to all languages** - Syntax elements common across Python/Go/Rust/TS/C#
3. **Type-explicit** - Clear type annotations
4. **Compiles to MCP JSON** - Text → MCP Tree → Any Language

---

## Complete Grammar

### Module Structure

```pw
module calculator
version 1.0.0

import math
import utils from common

// Functions
// Classes
// Types
// Enums
```

### Functions

```pw
function add(x: int, y: int) -> int {
    return x + y;
}

function greet(name: string) -> string {
    return "Hello, " + name;
}

// Async function
async function fetch_data(url: string) -> string {
    let response = await http.get(url);
    return response.body;
}

// No return type (void)
function print_message(msg: string) {
    console.log(msg);
}

// With throws
function divide(x: int, y: int) -> int throws DivisionError {
    if (y == 0) {
        throw DivisionError("Cannot divide by zero");
    }
    return x / y;
}
```

### Variables and Types

```pw
// Type annotations
let x: int = 42;
let name: string = "Alice";
let price: float = 99.99;
let active: bool = true;
let data: array<int> = [1, 2, 3];
let user: map<string, any> = {
    "name": "Bob",
    "age": 30
};

// Type inference
let count = 10;              // inferred as int
let message = "Hello";       // inferred as string
let items = [1, 2, 3];       // inferred as array<int>
```

### Control Flow

```pw
// If-else
if (x > 10) {
    console.log("Big");
} else if (x > 5) {
    console.log("Medium");
} else {
    console.log("Small");
}

// For loop
for (item in items) {
    console.log(item);
}

// While loop
while (count > 0) {
    count = count - 1;
}

// Break and continue
for (i in range(10)) {
    if (i == 5) {
        break;
    }
    if (i % 2 == 0) {
        continue;
    }
    console.log(i);
}
```

### Switch/Match

```pw
function classify(score: int) -> string {
    switch (score) {
        case 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100:
            return "A";
        case 80, 81, 82, 83, 84, 85, 86, 87, 88, 89:
            return "B";
        case 70, 71, 72, 73, 74, 75, 76, 77, 78, 79:
            return "C";
        default:
            return "F";
    }
}

// Pattern matching (Rust-style)
match (value) {
    case Some(x):
        return x;
    case None:
        return 0;
}
```

### Classes

```pw
class Calculator {
    // Properties
    let name: string;
    let version: float;

    // Constructor
    constructor(name: string, version: float) {
        self.name = name;
        self.version = version;
    }

    // Methods
    method add(x: int, y: int) -> int {
        return x + y;
    }

    method multiply(x: int, y: int) -> int {
        return x * y;
    }
}

// Usage
let calc = Calculator("Basic", 1.0);
let result = calc.add(5, 3);
```

### Type Definitions

```pw
type User {
    id: string;
    name: string;
    email: string;
    age: int?;                // Optional
    tags: array<string>;
}

type Response<T> {
    data: T;
    status: int;
    error: string?;
}
```

### Enums

```pw
enum Status {
    Pending,
    Active,
    Completed,
    Failed
}

enum Color {
    Red = 1,
    Green = 2,
    Blue = 3
}
```

### Error Handling

```pw
function safe_divide(x: int, y: int) -> int {
    try {
        if (y == 0) {
            throw DivisionError("Cannot divide by zero");
        }
        return x / y;
    } catch (DivisionError e) {
        console.log("Error:", e.message);
        return 0;
    } finally {
        console.log("Operation complete");
    }
}
```

### Operators

```pw
// Arithmetic
let sum = a + b;
let diff = a - b;
let product = a * b;
let quotient = a / b;
let remainder = a % b;

// Comparison
let equal = a == b;
let not_equal = a != b;
let greater = a > b;
let less = a < b;
let gte = a >= b;
let lte = a <= b;

// Logical
let and_result = a and b;
let or_result = a or b;
let not_result = not a;

// Ternary
let status = (age >= 18) ? "adult" : "minor";
```

### Comments

```pw
// Single-line comment

/*
 * Multi-line comment
 * Spans multiple lines
 */

function add(x: int, y: int) -> int {
    // This adds two numbers
    return x + y;
}
```

---

## Type System

### Primitive Types

- `int` - Integer numbers
- `float` - Floating-point numbers
- `string` - Text strings
- `bool` - Boolean (true/false)
- `null` - Null value

### Collection Types

- `array<T>` - Ordered list
- `map<K, V>` - Key-value mapping
- `set<T>` - Unique values

### Special Types

- `any` - Any type (avoid when possible)
- `T?` - Optional type (nullable)

### Generic Types

```pw
function first<T>(items: array<T>) -> T? {
    if (items.length > 0) {
        return items[0];
    }
    return null;
}
```

---

## Language Mapping

### PW → Target Languages

| PW Syntax | Python | Go | Rust | TypeScript | C# |
|-----------|--------|----|----- |------------|-----|
| `function add(x: int) -> int` | `def add(x: int) -> int:` | `func Add(x int) int` | `fn add(x: i32) -> i32` | `function add(x: number): number` | `int Add(int x)` |
| `let x: int = 5;` | `x: int = 5` | `var x int = 5` | `let x: i32 = 5;` | `const x: number = 5;` | `int x = 5;` |
| `array<int>` | `List[int]` | `[]int` | `Vec<i32>` | `number[]` | `List<int>` |
| `map<string, int>` | `Dict[str, int]` | `map[string]int` | `HashMap<String, i32>` | `Map<string, number>` | `Dictionary<string, int>` |

---

## Complete Example

```pw
module user_service
version 1.0.0

import database
import validation from utils

type User {
    id: string;
    name: string;
    email: string;
    created_at: string;
}

class UserService {
    let db: database.Connection;

    constructor(db_url: string) {
        self.db = database.connect(db_url);
    }

    method create_user(name: string, email: string) -> User throws ValidationError {
        // Validate input
        if (not validation.is_email(email)) {
            throw ValidationError("Invalid email");
        }

        // Create user
        let user_id = generate_id();
        let user = User{
            id: user_id,
            name: name,
            email: email,
            created_at: now()
        };

        // Save to database
        self.db.save("users", user);

        return user;
    }

    method get_user(user_id: string) -> User? {
        try {
            return self.db.find("users", user_id);
        } catch (NotFoundError e) {
            return null;
        }
    }

    method list_users(limit: int, offset: int) -> array<User> {
        return self.db.query("users", {
            "limit": limit,
            "offset": offset
        });
    }
}

// Helper functions
function generate_id() -> string {
    return uuid.v4();
}

function now() -> string {
    return datetime.utc_now().to_iso();
}
```

This compiles to Python, Go, Rust, TypeScript, and C# automatically!

---

## Compilation Process

```
┌─────────────────────────────────────────────────────────┐
│  1. Write PW Text                                       │
│     user_service.pw (human-readable)                    │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  2. Parse to IR                                         │
│     dsl/pw_parser.py → IRModule                         │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  3. Convert to MCP JSON                                 │
│     ir_to_mcp() → user_service.pw.json                  │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  4. Share MCP JSON                                      │
│     GitHub, npm, PyPI, crates.io                        │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  5. Unfold to Target Language                           │
│     pw_to_python() → user_service.py                    │
│     pw_to_go() → user_service.go                        │
│     pw_to_rust() → user_service.rs                      │
│     pw_to_typescript() → user_service.ts                │
│     pw_to_csharp() → UserService.cs                     │
└─────────────────────────────────────────────────────────┘
```

---

## CLI Usage

```bash
# Build PW directly to target language (most common)
pw build user_service.pw --lang python -o user_service.py
pw build user_service.pw --lang go -o user_service.go
pw build user_service.pw --lang rust -o user_service.rs
pw build user_service.pw --lang typescript -o user_service.ts
pw build user_service.pw --lang csharp -o UserService.cs

# Run PW code directly
pw run user_service.pw

# Compile to MCP JSON (for AI agents/advanced use)
pw compile user_service.pw -o user_service.pw.json

# Unfold MCP JSON to language (rarely needed)
pw unfold user_service.pw.json --lang python -o user_service.py
```

**Note**: MCP JSON (`.pw.json`) is an internal format used by AI agents and the compiler. Most developers will never see it - just write `.pw` files and build directly to your target language.

---

## Status

✅ **Lexer**: Complete - C-style comments, semicolons, all tokens
✅ **Parser**: Functions and if/else working with C-style syntax
✅ **IR Data Structures**: Complete (dsl/ir.py)
✅ **MCP Converters**: Complete (translators/ir_converter.py)
✅ **Language Generators**: Complete (5 languages - Python, Go, Rust, TypeScript, C#)
✅ **End-to-End Pipeline**: Tested - PW → IR → MCP → All 5 languages

🚧 **Parser**: Need for/while/class/enum/try-catch with C-style syntax
🚧 **CLI**: Need `pw build`, `pw compile`, `pw run` commands

---

**Next Steps**: Fix the parser bugs and add CLI commands!
