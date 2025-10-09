# PW Quick Reference

**Quick reference card for PW (Promptware) language**

---

## For Humans: Write → Compile → Run

### 1. Write PW Code

```pw
function add(x: int, y: int) -> int {
    return x + y;
}
```

### 2. Compile

```bash
pw build calculator.pw --lang python -o calculator.py
```

### 3. Run

```bash
python calculator.py
```

---

## For AI Agents: Compose → Share → Generate

### 1. Compose PW (using MCP tools)

```python
from pw_composer import *

pw_tree = pw_function(
    name="add",
    params=[
        pw_parameter("x", pw_type("int")),
        pw_parameter("y", pw_type("int"))
    ],
    return_type=pw_type("int"),
    body=[
        pw_return(
            pw_binary_op("+", pw_identifier("x"), pw_identifier("y"))
        )
    ]
)
```

### 2. Share PW MCP Tree

```python
# Share JSON tree with other agents
send_to_agent(pw_tree)
```

### 3. Generate Target Language

```python
from translators.python_bridge import pw_to_python
python_code = pw_to_python(pw_tree)
```

---

## Syntax Cheat Sheet

### Functions

```pw
function name(param: type) -> return_type {
    // body
}
```

### Variables

```pw
let x: int = 42;
let name: string = "Alice";
let price: float = 99.99;
let active: bool = true;
```

### Conditionals

```pw
if (condition) {
    // then
} else if (other_condition) {
    // else if
} else {
    // else
}
```

### Types

- `int` - Integers
- `float` - Floating-point
- `string` - Text
- `bool` - Boolean
- `void` - No return

### Operators

- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Assignment: `=`
- Arrow: `->`

### Comments

```pw
// Single-line comment

/*
 * Multi-line comment
 */
```

---

## CLI Commands

### Build (most common)

```bash
pw build <file.pw> --lang <python|go|rust|typescript|csharp> -o <output>
```

### Compile to MCP JSON (agents)

```bash
pw compile <file.pw> -o <file.pw.json>
```

### Unfold MCP JSON (rarely needed)

```bash
pw unfold <file.pw.json> --lang <language> -o <output>
```

---

## VS Code Extension

### Enable Syntax Highlighting

1. Open Promptware folder in VS Code
2. `Cmd+Shift+P` → `Developer: Reload Window`
3. Open any `.pw` file

### Enable File Icons

1. `Cmd+Shift+P` → `Preferences: File Icon Theme`
2. Select `PW Icons`

### Keyboard Shortcuts

- `Cmd+/` or `Ctrl+/` - Toggle comment
- Auto-close: `{`, `(`, `"`

---

## File Structure

```
my-project/
├── src/
│   └── calculator.pw       # PW source
├── build/
│   ├── calculator.py       # Generated Python
│   ├── calculator.go       # Generated Go
│   └── calculator.rs       # Generated Rust
└── README.md
```

---

## Links

- **Full Guide:** `docs/PW_LANGUAGE_GUIDE.md`
- **Language Spec:** `docs/PW_NATIVE_SYNTAX.md`
- **VS Code Extension:** `docs/VS_CODE_EXTENSION.md`
- **Examples:** `examples/calculator.pw`
- **GitHub:** https://github.com/Promptware-dev/promptware

---

## Status

✅ **Working:**
- Functions with parameters
- If/else conditionals
- Variables and assignments
- Basic types (int, float, string, bool)
- Arithmetic and comparison operators
- Comments (// and /* */)
- Compilation to 5 languages

🚧 **In Progress:**
- For/while loops
- Classes and methods
- Type definitions
- Enums
- Try/catch
- Arrays and maps

---

**Quick Start:**

```bash
# 1. Clone repo
git clone https://github.com/Promptware-dev/promptware.git
cd promptware

# 2. Write PW
echo 'function add(x: int, y: int) -> int { return x + y; }' > hello.pw

# 3. Compile
pw build hello.pw --lang python -o hello.py

# 4. Run
python hello.py
```

**That's it!** 🚀
