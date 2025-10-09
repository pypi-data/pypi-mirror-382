# PW Language Guide

**The Universal Programming Language**

Write once in PW, compile to Python, Go, Rust, TypeScript, or C#.

---

## Table of Contents

- [What is PW?](#what-is-pw)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Language Syntax](#language-syntax)
- [For Human Developers](#for-human-developers)
- [For AI Agents](#for-ai-agents)
- [VS Code Setup](#vs-code-setup)
- [Examples](#examples)
- [CLI Reference](#cli-reference)
- [FAQ](#faq)

---

## What is PW?

**PW (Promptware)** is a universal programming language that compiles to multiple target languages. Write your code once in PW, then compile it to:

- **Python** - For data science, scripting, web apps
- **Go** - For microservices, CLI tools, performance
- **Rust** - For systems programming, safety-critical code
- **TypeScript** - For web frontends, Node.js backends
- **C#** - For .NET applications, Unity games

### Two Use Cases

**1. Human Developers** - Write `.pw` files, compile directly to your target language
```bash
pw build calculator.pw --lang python -o calculator.py
```

**2. AI Agents** - Compose PW via MCP tools, share code between agents
```python
# Agent composes PW programmatically
pw_tree = pw_function(name="add", params=[...], body=[...])
# Share PW tree with other agents
```

---

## Installation

### Prerequisites

- **Python 3.8+** (for the PW compiler)
- **Git** (to clone the repository)

### Install PW

```bash
# Clone the repository
git clone https://github.com/Promptware-dev/promptware.git
cd promptware

# Install dependencies
pip install -e .

# Verify installation
pw --version
```

### Install VS Code Extension

**Option 1: Automatic (Workspace)**

The extension is included in `.vscode/extensions/pw-language/` and loads automatically when you open the Promptware workspace.

1. Open the Promptware folder in VS Code
2. Press `Cmd+Shift+P` → `Developer: Reload Window`
3. Open any `.pw` file - syntax highlighting should work!

**Option 2: Manual Installation**

```bash
# Package the extension
cd .vscode/extensions/pw-language
npm install -g vsce
vsce package

# Install globally
code --install-extension pw-language-0.1.0.vsix
```

**Option 3: From Marketplace** (Coming Soon!)

Search for "PW Language Support" in the VS Code Extensions marketplace.

---

## Quick Start

### Your First PW Program

Create `hello.pw`:

```pw
// hello.pw - Your first PW program
function greet(name: string) -> string {
    return "Hello, " + name + "!";
}

function main() {
    let message = greet("World");
    // In target language, this would print
}
```

### Compile to Python

```bash
pw build hello.pw --lang python -o hello.py
python hello.py
```

### Compile to Go

```bash
pw build hello.pw --lang go -o hello.go
go run hello.go
```

### Compile to All Languages

```bash
pw build hello.pw --lang python -o hello.py
pw build hello.pw --lang go -o hello.go
pw build hello.pw --lang rust -o hello.rs
pw build hello.pw --lang typescript -o hello.ts
pw build hello.pw --lang csharp -o hello.cs
```

---

## Language Syntax

### Functions

```pw
// Basic function
function add(x: int, y: int) -> int {
    return x + y;
}

// Function with logic
function calculate_price(base: float, tax: float) -> float {
    let subtotal = base;
    let tax_amount = subtotal * tax;
    return subtotal + tax_amount;
}

// Function with no return (void)
function log_message(msg: string) {
    // This prints in the target language
}
```

### Variables

```pw
// Type annotations (explicit)
let name: string = "Alice";
let age: int = 30;
let price: float = 99.99;
let active: bool = true;

// Type inference (types inferred from values)
let count = 10;              // int
let message = "Hello";       // string
let pi = 3.14;               // float
```

### Conditionals

```pw
// If-else statement
function classify(score: int) -> string {
    if (score >= 90) {
        return "A";
    } else if (score >= 80) {
        return "B";
    } else if (score >= 70) {
        return "C";
    } else {
        return "F";
    }
}

// Nested conditions
function check_eligibility(age: int, has_license: bool) -> bool {
    if (age >= 18) {
        if (has_license) {
            return true;
        }
    }
    return false;
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
let and_result = (a > 0) && (b > 0);  // Not yet implemented
let or_result = (a > 0) || (b > 0);   // Not yet implemented
```

### Types

**Primitive Types:**
- `int` - Integer numbers (32-bit)
- `float` - Floating-point numbers (64-bit)
- `string` - Text strings
- `bool` - Boolean values (`true`, `false`)
- `void` - No return value

**Collection Types** (Coming Soon):
- `array<T>` - Ordered list: `array<int>`
- `map<K, V>` - Key-value map: `map<string, int>`
- `set<T>` - Unique values: `set<string>`

### Comments

```pw
// Single-line comment

/*
 * Multi-line comment
 * Spans multiple lines
 */

function calculate(x: int) -> int {
    // This is a helper comment
    let result = x * 2;
    return result;
}
```

### Code Style

**PW supports flexible syntax:**

```pw
// Semicolons are optional
let x = 10;
let y = 20    // Both work

// Parentheses around conditions are optional
if (x > 10) { }   // C-style
if x > 10 { }     // Also valid (not yet implemented)
```

---

## For Human Developers

### Workflow: Write → Compile → Run

**1. Write PW Code**

Create `calculator.pw`:

```pw
function add(x: int, y: int) -> int {
    return x + y;
}

function multiply(x: int, y: int) -> int {
    return x * y;
}
```

**2. Compile to Target Language**

```bash
# Compile to Python
pw build calculator.pw --lang python -o calculator.py

# Compile to Go
pw build calculator.pw --lang go -o calculator.go
```

**3. Run the Generated Code**

```bash
# Python
python calculator.py

# Go
go run calculator.go
```

### Best Practices

**✅ DO:**
- Use type annotations for clarity
- Write descriptive function names
- Add comments to explain complex logic
- Test in your target language

**❌ DON'T:**
- Mix PW syntax versions (use C-style consistently)
- Rely on language-specific features not in PW spec
- Forget to compile after changes

### Project Structure

```
my-project/
├── src/
│   ├── calculator.pw       # PW source files
│   ├── user_service.pw
│   └── utils.pw
├── build/
│   ├── python/             # Compiled Python
│   ├── go/                 # Compiled Go
│   └── rust/               # Compiled Rust
├── tests/
│   └── test_calculator.pw  # PW test files
└── README.md
```

### Sharing PW Code

**On GitHub:**

```bash
# Share your .pw files
git add src/*.pw
git commit -m "Add calculator in PW"
git push
```

**Others can compile to their preferred language:**

```bash
git clone your-repo
pw build src/calculator.pw --lang rust -o calculator.rs
```

---

## For AI Agents

### Overview

AI agents should **compose PW programmatically** using MCP tools, not write raw `.pw` text files.

### MCP Tool Composition

**Available MCP Tools:**

- `pw_function` - Create function definition
- `pw_parameter` - Define function parameter
- `pw_type` - Type reference
- `pw_return` - Return statement
- `pw_if` - If statement
- `pw_assignment` - Variable assignment
- `pw_binary_op` - Binary operation (+, -, *, /, ==, etc.)
- `pw_call` - Function call
- `pw_literal` - Literal value
- `pw_identifier` - Variable reference
- `pw_module` - Module definition

### Example: Agent Composing PW

```python
# Agent composing a simple add function
from pw_composer import *

# Compose the function
add_func = pw_function(
    name="add",
    params=[
        pw_parameter("x", pw_type("int")),
        pw_parameter("y", pw_type("int"))
    ],
    return_type=pw_type("int"),
    body=[
        pw_return(
            pw_binary_op(
                "+",
                pw_identifier("x"),
                pw_identifier("y")
            )
        )
    ]
)

# This creates a PW MCP tree (JSON)
# Agents share this tree, not raw code
```

### Agent Workflow

**1. Agent A: Compose PW**

```python
# Agent A composes business logic in PW
pw_tree = pw_function(...)
```

**2. Share PW MCP Tree**

```python
# Send to Agent B (JSON format)
send_to_agent_b(pw_tree)
```

**3. Agent B: Generate Target Language**

```python
# Agent B generates Go code to execute
go_code = pw_to_go(pw_tree)
execute(go_code)
```

**4. Agent C: Generate Different Language**

```python
# Agent C generates Python from same PW tree
python_code = pw_to_python(pw_tree)
execute(python_code)
```

### Why Use MCP Tools?

**✅ Benefits:**
- **No parser bugs** - Composition is always valid
- **Zero degradation** - PW tree never changes
- **Language agnostic** - Agents don't need to know target language
- **Efficient** - JSON is compact, only generate when executing

**❌ Don't:**
- Parse raw code strings (Python → PW)
- Use PW as a translation layer between languages
- Generate PW text then parse it back

### MCP Server Integration

Connect to the PW MCP server:

```python
import mcp

# Connect to PW MCP server
client = mcp.Client("pw-syntax-mcp-server")

# Use MCP tools
result = await client.call("pw_function", {
    "name": "calculate",
    "params": [...],
    "body": [...]
})
```

---

## VS Code Setup

### Syntax Highlighting

The PW VS Code extension provides:
- **Keyword highlighting** - `function`, `if`, `return`, `let`
- **Type highlighting** - `int`, `float`, `string`, `bool`
- **String highlighting** - `"hello"`
- **Comment highlighting** - `// comment`
- **Operator highlighting** - `+`, `-`, `==`, `->`

### Enable Extension

**Automatic (Workspace):**

1. Open Promptware folder in VS Code
2. Press `Cmd+Shift+P` → `Developer: Reload Window`
3. Open `examples/calculator.pw`
4. See syntax highlighting!

**Enable File Icons:**

1. Press `Cmd+Shift+P` → `Preferences: File Icon Theme`
2. Select `PW Icons`
3. See purple "PW" icon next to `.pw` files

### Editor Features

**Auto-Closing:**
- Type `{` → automatically adds `}`
- Type `(` → automatically adds `)`
- Type `"` → automatically adds `"`

**Comment Toggle:**
- `Cmd+/` (Mac) or `Ctrl+/` (Windows) → Toggle `//` comment

**Bracket Matching:**
- Click on `{` → highlights matching `}`

### Download Extension

**Current Status: Private (Workspace Only)**

The extension is currently included in the Promptware repository at:
```
.vscode/extensions/pw-language/
```

**To share with others:**

```bash
# Package the extension
cd .vscode/extensions/pw-language
npm install -g vsce
vsce package

# This creates: pw-language-0.1.0.vsix
# Share this file with others
```

**Install the .vsix file:**

```bash
code --install-extension pw-language-0.1.0.vsix
```

**Future: VS Code Marketplace**

We plan to publish to the VS Code Marketplace so anyone can install with one click!

### Extension Files

Download/access from GitHub:

```bash
# Clone the repository
git clone https://github.com/Promptware-dev/promptware.git
cd promptware/.vscode/extensions/pw-language/

# Files included:
# - package.json                    Extension manifest
# - syntaxes/pw.tmLanguage.json    Syntax rules
# - icons/pw-icon.svg              PW logo
# - language-configuration.json    Editor config
```

**Logo/Icon:** `.vscode/extensions/pw-language/icons/pw-icon.svg`

Purple square with white "PW" text - feel free to use this for branding!

---

## Examples

### Example 1: Calculator

**File:** `examples/calculator.pw`

```pw
// Basic calculator functions
function add(x: int, y: int) -> int {
    return x + y;
}

function subtract(x: int, y: int) -> int {
    return x - y;
}

function multiply(x: int, y: int) -> int {
    return x * y;
}

function divide(num: int, denom: int) -> float {
    if (denom != 0) {
        return num / denom;
    } else {
        return 0.0;
    }
}
```

**Compile:**

```bash
pw build examples/calculator.pw --lang python -o calculator.py
```

### Example 2: User Validation

**File:** `examples/user_service.pw`

```pw
// User validation functions
function validate_email(email: string) -> bool {
    // Simplified validation
    if (email != "") {
        return true;
    } else {
        return false;
    }
}

function validate_password(password: string) -> bool {
    // Check minimum length
    let min_length = 8;
    // Would use password.length in full implementation
    return true;
}

function create_user(username: string, email: string, password: string) -> string {
    if (username == "") {
        return "Error: Username required";
    }

    if (!validate_email(email)) {
        return "Error: Invalid email";
    }

    if (!validate_password(password)) {
        return "Error: Password too short";
    }

    return "User created: " + username;
}
```

### Example 3: Business Logic

```pw
// E-commerce pricing
function calculate_discount(subtotal: float, customer_type: string) -> float {
    if (customer_type == "premium") {
        return subtotal * 0.15;
    } else if (customer_type == "regular") {
        if (subtotal > 100.0) {
            return subtotal * 0.10;
        } else {
            return subtotal * 0.05;
        }
    } else {
        return 0.0;
    }
}

function apply_discount(price: float, discount_percent: float) -> float {
    let discount_amount = price * (discount_percent / 100.0);
    return price - discount_amount;
}
```

---

## CLI Reference

### `pw build`

Compile PW to target language (most common command).

```bash
pw build <input.pw> --lang <language> -o <output>
```

**Arguments:**
- `<input.pw>` - Path to PW source file
- `--lang` - Target language: `python`, `go`, `rust`, `typescript`, `csharp`
- `-o` - Output file path

**Examples:**

```bash
# Python
pw build calculator.pw --lang python -o calculator.py

# Go
pw build calculator.pw --lang go -o calculator.go

# Rust
pw build calculator.pw --lang rust -o calculator.rs

# TypeScript
pw build calculator.pw --lang typescript -o calculator.ts

# C#
pw build calculator.pw --lang csharp -o Calculator.cs
```

### `pw compile`

Compile PW to MCP JSON (for AI agents/advanced use).

```bash
pw compile <input.pw> -o <output.pw.json>
```

**Example:**

```bash
pw compile calculator.pw -o calculator.pw.json
```

### `pw unfold`

Convert MCP JSON to target language (rarely needed).

```bash
pw unfold <input.pw.json> --lang <language> -o <output>
```

**Example:**

```bash
pw unfold calculator.pw.json --lang go -o calculator.go
```

### `pw run`

Execute PW code directly (coming soon).

```bash
pw run <input.pw>
```

### `pw --version`

Show PW compiler version.

```bash
pw --version
```

### `pw --help`

Show help information.

```bash
pw --help
```

---

## FAQ

### General Questions

**Q: Is PW a real programming language?**

A: Yes! PW has formal syntax, a compiler, type system, and generates real code in 5 languages.

**Q: Why use PW instead of writing directly in Python/Go/Rust?**

A: Write once, deploy anywhere. Share code with teams using different languages. Future-proof your code.

**Q: Can I use PW in production?**

A: The core features (functions, if/else, types) are stable and tested. Advanced features (loops, classes) are coming soon.

**Q: Does PW add runtime overhead?**

A: No! PW compiles to native code in each language. There's no runtime, no VM, no interpreter.

### Technical Questions

**Q: What's the difference between `.pw` files and `.pw.json` files?**

A: `.pw` files are human-readable source code. `.pw.json` is the internal MCP format used by AI agents and the compiler.

**Q: Do I ever need to see `.pw.json` files?**

A: No! For human developers, just work with `.pw` files. The JSON format is for AI agents.

**Q: Can I write PW code by hand?**

A: Yes! That's the whole point. PW has C-style syntax designed for humans to read and write.

**Q: Can AI agents write PW?**

A: Yes, but they should compose PW programmatically using MCP tools, not generate text strings.

**Q: Is PW open source?**

A: Yes! MIT licensed. Contribute at: https://github.com/Promptware-dev/promptware

### VS Code Extension Questions

**Q: Is the VS Code extension public?**

A: Currently **workspace-only** (included in the repo). Publishing to VS Code Marketplace is planned.

**Q: How do I share the extension with my team?**

A:
1. Share the repo - extension is in `.vscode/extensions/pw-language/`
2. Or package as `.vsix`: `vsce package` and share the file

**Q: Can I customize the syntax highlighting colors?**

A: Yes! The extension uses standard TextMate scopes, so your VS Code theme controls the colors.

**Q: Will there be extensions for other editors?**

A: Planned! Sublime Text, Vim, and IntelliJ support coming soon.

### Feature Questions

**Q: Does PW support loops?**

A: `for` and `while` loops are in the specification but parser implementation is in progress.

**Q: Does PW support classes?**

A: Class syntax is specified but parser implementation is coming soon.

**Q: Does PW support imports/modules?**

A: Import syntax exists for MCP servers. General-purpose imports are planned.

**Q: Can I call external libraries?**

A: In generated code, yes! The generated Python/Go/Rust can use their standard libraries.

**Q: Is there a standard library for PW?**

A: Planned! Common functions like `print()`, `len()`, `range()` are coming.

### Troubleshooting

**Q: Syntax highlighting not working in VS Code**

A:
1. Reload window: `Cmd+Shift+P` → `Developer: Reload Window`
2. Check language mode in bottom-right corner
3. Manually select "PW" if it says "Plain Text"

**Q: No file icon appearing**

A: Select icon theme: `Cmd+Shift+P` → `Preferences: File Icon Theme` → `PW Icons`

**Q: Compilation errors**

A: Check your syntax matches the examples. Some features (loops, classes) aren't implemented yet.

**Q: Generated code doesn't compile**

A: Report an issue! Include your `.pw` file and target language: https://github.com/Promptware-dev/promptware/issues

---

## Getting Help

### Documentation

- **Language Spec:** `docs/PW_NATIVE_SYNTAX.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **This Guide:** `docs/PW_LANGUAGE_GUIDE.md`

### Community

- **GitHub Issues:** https://github.com/Promptware-dev/promptware/issues
- **Discussions:** https://github.com/Promptware-dev/promptware/discussions
- **Discord:** (Coming soon!)

### Contributing

Want to help make PW better?

- Add features (loops, classes, etc.)
- Improve code generation
- Write tests
- Create examples
- Improve documentation

See `CONTRIBUTING.md` for guidelines.

---

## License

PW is open source under the MIT License.

```
Copyright (c) 2024 Promptware Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

See `LICENSE` for full text.

---

## Credits

**Created by:** Promptware Contributors

**Powered by:**
- Python (compiler implementation)
- Tree-sitter (parsing libraries)
- MCP Protocol (AI agent integration)

**Thanks to:**
- All contributors and early adopters
- The open source community

---

**Happy coding in PW!** 🚀

Write once, run everywhere.
