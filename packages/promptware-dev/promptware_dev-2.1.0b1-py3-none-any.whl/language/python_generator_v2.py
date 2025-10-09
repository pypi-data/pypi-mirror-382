"""
Python Generator V2: IR → Idiomatic Python Code

This generator converts the universal Intermediate Representation (IR) into
production-quality, idiomatic Python code. It handles:

- Type hints (PEP 484/585)
- Async/await patterns
- Decorators from metadata
- Proper imports and organization
- PEP 8 style formatting
- List comprehensions and Python idioms
- Exception handling (try/except)
- Classes with properties, methods, constructors
- Dataclasses and Enums

Design Principles:
1. Idiomatic - Generate Pythonic code, not just syntactically correct
2. Type-safe - Full type hint support via typing module
3. Clean - PEP 8 compliant formatting
4. Zero dependencies - Only uses Python stdlib
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set

from dsl.ir import (
    BinaryOperator,
    IRArray,
    IRAssignment,
    IRAwait,
    IRBinaryOp,
    IRBreak,
    IRCall,
    IRCatch,
    IRClass,
    IRComprehension,
    IRContinue,
    IREnum,
    IREnumVariant,
    IRExpression,
    IRFor,
    IRFunction,
    IRIdentifier,
    IRIf,
    IRImport,
    IRIndex,
    IRLambda,
    IRLiteral,
    IRMap,
    IRModule,
    IRParameter,
    IRPass,
    IRProperty,
    IRPropertyAccess,
    IRReturn,
    IRStatement,
    IRTernary,
    IRThrow,
    IRTry,
    IRType,
    IRTypeDefinition,
    IRUnaryOp,
    IRWhile,
    IRWith,
    LiteralType,
    UnaryOperator,
)
from dsl.type_system import TypeSystem
from language.library_mapping import LibraryMapper


class PythonGeneratorV2:
    """
    Generate idiomatic Python code from IR.

    Converts language-agnostic IR into production-quality Python with:
    - Full type hints
    - Proper imports
    - PEP 8 formatting
    - Python-specific idioms
    """

    def __init__(self):
        self.type_system = TypeSystem()
        self.library_mapper = LibraryMapper()
        self.indent_level = 0
        self.indent_size = 4  # PEP 8 standard
        self.required_imports: Set[str] = set()
        self.source_language: Optional[str] = None  # Track source language for mapping

    # ========================================================================
    # Indentation Management
    # ========================================================================

    def indent(self) -> str:
        """Get current indentation string (4 spaces per PEP 8)."""
        return " " * (self.indent_level * self.indent_size)

    def increase_indent(self) -> None:
        """Increase indentation level."""
        self.indent_level += 1

    def decrease_indent(self) -> None:
        """Decrease indentation level."""
        if self.indent_level > 0:
            self.indent_level -= 1

    # ========================================================================
    # Main Entry Point
    # ========================================================================

    def generate(self, module: IRModule) -> str:
        """
        Generate Python code from IR module.

        Args:
            module: IR module to convert

        Returns:
            Python source code as string
        """
        self.required_imports.clear()
        lines = []

        # Module docstring
        if module.metadata.get("doc"):
            lines.append(f'"""{module.metadata["doc"]}"""')
            lines.append("")

        # Collect required imports from types
        self._collect_imports(module)

        # Add future imports first (PEP 563)
        lines.append("from __future__ import annotations")
        lines.append("")

        # Special imports (enum, dataclass) - add to required
        if module.enums:
            self.required_imports.add("from enum import Enum")
        if module.types:
            self.required_imports.add("from dataclasses import dataclass")

        # Standard library imports (non-typing)
        stdlib_imports = sorted([imp for imp in self.required_imports
                                if not imp.startswith("from typing") and imp.startswith("from ")])
        if stdlib_imports:
            for imp in stdlib_imports:
                lines.append(imp)
            lines.append("")

        # Typing imports
        typing_imports = sorted([imp for imp in self.required_imports if imp.startswith("from typing")])
        if typing_imports:
            # Combine typing imports
            all_types = set()
            for imp in typing_imports:
                types = imp.replace("from typing import ", "").split(", ")
                all_types.update(types)
            lines.append(f"from typing import {', '.join(sorted(all_types))}")
            lines.append("")

        # User imports
        for imp in module.imports:
            lines.append(self.generate_import(imp))
        if module.imports:
            lines.append("")

        # Enums
        for enum in module.enums:
            lines.append(self.generate_enum(enum))
            lines.append("")
            lines.append("")

        # Type definitions (dataclasses)
        for type_def in module.types:
            lines.append(self.generate_type_definition(type_def))
            lines.append("")
            lines.append("")

        # Classes
        for cls in module.classes:
            lines.append(self.generate_class(cls))
            lines.append("")
            lines.append("")

        # Module-level variables
        for var in module.module_vars:
            lines.append(self.generate_statement(var))
            lines.append("")

        # Functions
        for func in module.functions:
            lines.append(self.generate_function(func))
            lines.append("")
            lines.append("")

        # Clean up and return
        result = "\n".join(lines)
        # Remove excessive blank lines
        while "\n\n\n\n" in result:
            result = result.replace("\n\n\n\n", "\n\n\n")
        return result.rstrip() + "\n"

    # ========================================================================
    # Import Collection and Generation
    # ========================================================================

    def _collect_imports(self, module: IRModule) -> None:
        """Collect all required imports from types used in module."""
        all_types = []

        # Collect types from functions
        for func in module.functions:
            for param in func.params:
                all_types.append(param.param_type)
            if func.return_type:
                all_types.append(func.return_type)

        # Collect types from classes
        for cls in module.classes:
            for prop in cls.properties:
                all_types.append(prop.prop_type)
            for method in cls.methods:
                for param in method.params:
                    all_types.append(param.param_type)
                if method.return_type:
                    all_types.append(method.return_type)

        # Collect types from type definitions
        for type_def in module.types:
            for field in type_def.fields:
                all_types.append(field.prop_type)

        # Get required imports
        imports = self.type_system.get_required_imports(all_types, "python")
        self.required_imports.update(imports)

    def generate_import(self, imp: IRImport) -> str:
        """
        Generate Python import statement with library mapping.

        If source language is set and library mapping exists, translates to Python equivalent.
        """
        module_name = imp.module

        # Try to translate library if source language is known
        if self.source_language and self.source_language != "python":
            translated = self.library_mapper.translate_import(
                imp.module,
                from_lang=self.source_language,
                to_lang="python"
            )
            if translated:
                module_name = translated["module"]
                # Add comment showing original library
                comment = f"  # from {self.source_language}: {imp.module}"
            else:
                comment = f"  # NOTE: No mapping for {self.source_language} library '{imp.module}'"
        else:
            comment = ""

        # Generate import statement
        if imp.items:
            # from module import item1, item2
            items = ", ".join(imp.items)
            return f"from {module_name} import {items}{comment}"
        elif imp.alias:
            # import module as alias
            return f"import {module_name} as {imp.alias}{comment}"
        else:
            # import module
            return f"import {module_name}{comment}"

    # ========================================================================
    # Type Definition Generation
    # ========================================================================

    def generate_enum(self, enum: IREnum) -> str:
        """Generate Python Enum class."""
        lines = []

        # Docstring
        if enum.doc:
            lines.append(f"class {enum.name}(Enum):")
            self.increase_indent()
            lines.append(f'{self.indent()}"""{enum.doc}"""')
        else:
            lines.append(f"class {enum.name}(Enum):")
            self.increase_indent()

        # Variants
        if not enum.variants:
            lines.append(f"{self.indent()}pass")
        else:
            for i, variant in enumerate(enum.variants):
                if variant.value is not None:
                    if isinstance(variant.value, str):
                        lines.append(f'{self.indent()}{variant.name} = "{variant.value}"')
                    else:
                        lines.append(f'{self.indent()}{variant.name} = {variant.value}')
                else:
                    # Auto-number if no value
                    lines.append(f'{self.indent()}{variant.name} = {i + 1}')

        self.decrease_indent()
        return "\n".join(lines)

    def generate_type_definition(self, type_def: IRTypeDefinition) -> str:
        """Generate Python dataclass."""
        lines = []

        # Decorator
        lines.append("@dataclass")

        # Class definition
        if type_def.doc:
            lines.append(f"class {type_def.name}:")
            self.increase_indent()
            lines.append(f'{self.indent()}"""{type_def.doc}"""')
        else:
            lines.append(f"class {type_def.name}:")
            self.increase_indent()

        # Fields
        if not type_def.fields:
            lines.append(f"{self.indent()}pass")
        else:
            for field in type_def.fields:
                field_line = f"{self.indent()}{field.name}: {self.generate_type(field.prop_type)}"
                if field.default_value:
                    field_line += f" = {self.generate_expression(field.default_value)}"
                lines.append(field_line)

        self.decrease_indent()
        return "\n".join(lines)

    # ========================================================================
    # Class Generation
    # ========================================================================

    def generate_class(self, cls: IRClass) -> str:
        """Generate Python class."""
        lines = []

        # Class signature
        class_sig = f"class {cls.name}"
        if cls.base_classes:
            class_sig += f"({', '.join(cls.base_classes)})"
        class_sig += ":"
        lines.append(class_sig)

        self.increase_indent()

        # Docstring
        if cls.doc:
            lines.append(f'{self.indent()}"""{cls.doc}"""')
            lines.append("")

        # Class-level properties (without default values)
        has_properties = False
        for prop in cls.properties:
            if not prop.default_value:
                prop_line = f"{self.indent()}{prop.name}: {self.generate_type(prop.prop_type)}"
                lines.append(prop_line)
                has_properties = True

        if has_properties:
            lines.append("")

        # Constructor
        if cls.constructor:
            lines.append(self.generate_constructor(cls.constructor, cls.properties))
            lines.append("")

        # Methods
        for method in cls.methods:
            lines.append(self.generate_method(method))
            lines.append("")

        # If empty class, add pass
        if not cls.properties and not cls.constructor and not cls.methods:
            lines.append(f"{self.indent()}pass")

        self.decrease_indent()

        # Remove trailing empty line from class
        while lines and lines[-1] == "":
            lines.pop()

        return "\n".join(lines)

    def generate_constructor(self, constructor: IRFunction, properties: List[IRProperty]) -> str:
        """Generate __init__ method."""
        lines = []

        # Signature
        params = ["self"]
        for param in constructor.params:
            param_str = f"{param.name}: {self.generate_type(param.param_type)}"
            if param.default_value:
                param_str += f" = {self.generate_expression(param.default_value)}"
            params.append(param_str)

        # Return type is None for __init__
        params_str = ", ".join(params)
        lines.append(f"{self.indent()}def __init__({params_str}) -> None:")

        self.increase_indent()

        # Docstring
        if constructor.doc:
            lines.append(f'{self.indent()}"""{constructor.doc}"""')

        # Body
        if constructor.body:
            for stmt in constructor.body:
                lines.append(self.generate_statement(stmt))
        else:
            lines.append(f"{self.indent()}pass")

        self.decrease_indent()
        return "\n".join(lines)

    def generate_method(self, method: IRFunction) -> str:
        """Generate class method."""
        lines = []

        # Decorators (use direct field, fall back to metadata)
        decorators = method.decorators if hasattr(method, 'decorators') else method.metadata.get("decorators", [])
        for dec in decorators:
            lines.append(f"{self.indent()}@{dec}")

        # Static method
        if method.is_static:
            lines.append(f"{self.indent()}@staticmethod")

        # Signature
        params = [] if method.is_static else ["self"]
        for param in method.params:
            param_str = f"{param.name}: {self.generate_type(param.param_type)}"
            if param.default_value:
                param_str += f" = {self.generate_expression(param.default_value)}"
            params.append(param_str)

        params_str = ", ".join(params)

        # Async
        func_def = "async def" if method.is_async else "def"

        # Return type
        return_type = ""
        if method.return_type:
            return_type = f" -> {self.generate_type(method.return_type)}"

        lines.append(f"{self.indent()}{func_def} {method.name}({params_str}){return_type}:")

        self.increase_indent()

        # Docstring
        if method.doc:
            lines.append(f'{self.indent()}"""{method.doc}"""')

        # Body
        if method.body:
            for stmt in method.body:
                lines.append(self.generate_statement(stmt))
        else:
            lines.append(f"{self.indent()}pass")

        self.decrease_indent()
        return "\n".join(lines)

    # ========================================================================
    # Function Generation
    # ========================================================================

    def generate_function(self, func: IRFunction) -> str:
        """Generate standalone function."""
        lines = []

        # Decorators (use direct field, fall back to metadata)
        decorators = func.decorators if hasattr(func, 'decorators') else func.metadata.get("decorators", [])
        for dec in decorators:
            lines.append(f"@{dec}")

        # Signature
        params = []
        for param in func.params:
            param_str = f"{param.name}: {self.generate_type(param.param_type)}"
            if param.default_value:
                param_str += f" = {self.generate_expression(param.default_value)}"
            params.append(param_str)

        params_str = ", ".join(params)

        # Async
        func_def = "async def" if func.is_async else "def"

        # Return type
        return_type = ""
        if func.return_type:
            return_type = f" -> {self.generate_type(func.return_type)}"

        lines.append(f"{func_def} {func.name}({params_str}){return_type}:")

        self.increase_indent()

        # Docstring
        if func.doc:
            lines.append(f'{self.indent()}"""{func.doc}"""')

        # Body
        if func.body:
            for stmt in func.body:
                lines.append(self.generate_statement(stmt))
        else:
            lines.append(f"{self.indent()}pass")

        self.decrease_indent()
        return "\n".join(lines)

    # ========================================================================
    # Type Generation
    # ========================================================================

    def generate_type(self, ir_type: IRType) -> str:
        """Generate Python type hint from IR type."""
        return self.type_system.map_to_language(ir_type, "python")

    # ========================================================================
    # Statement Generation
    # ========================================================================

    def generate_statement(self, stmt: IRStatement) -> str:
        """Generate Python statement from IR."""
        if isinstance(stmt, IRAssignment):
            return self.generate_assignment(stmt)
        elif isinstance(stmt, IRIf):
            return self.generate_if(stmt)
        elif isinstance(stmt, IRFor):
            return self.generate_for(stmt)
        elif isinstance(stmt, IRWhile):
            return self.generate_while(stmt)
        elif isinstance(stmt, IRTry):
            return self.generate_try(stmt)
        elif isinstance(stmt, IRReturn):
            return self.generate_return(stmt)
        elif isinstance(stmt, IRThrow):
            return self.generate_raise(stmt)
        elif isinstance(stmt, IRBreak):
            return f"{self.indent()}break"
        elif isinstance(stmt, IRContinue):
            return f"{self.indent()}continue"
        elif isinstance(stmt, IRPass):
            return f"{self.indent()}pass"
        elif isinstance(stmt, IRWith):
            return self.generate_with(stmt)
        elif isinstance(stmt, IRCall):
            # Expression statement
            return f"{self.indent()}{self.generate_expression(stmt)}"
        else:
            return f"{self.indent()}# Unknown statement: {type(stmt).__name__}"

    def generate_assignment(self, stmt: IRAssignment) -> str:
        """Generate assignment statement."""
        value = self.generate_expression(stmt.value)

        # Handle empty target (shouldn't happen, but be defensive)
        target = stmt.target if stmt.target else "_unknown"

        # Type annotation for declarations (only for simple variables, not attributes)
        if stmt.is_declaration and stmt.var_type and "." not in target:
            type_hint = self.generate_type(stmt.var_type)
            return f"{self.indent()}{target}: {type_hint} = {value}"
        else:
            return f"{self.indent()}{target} = {value}"

    def generate_if(self, stmt: IRIf) -> str:
        """Generate if statement."""
        lines = []

        # If condition
        condition = self.generate_expression(stmt.condition)
        lines.append(f"{self.indent()}if {condition}:")

        # Then body
        self.increase_indent()
        if stmt.then_body:
            for s in stmt.then_body:
                lines.append(self.generate_statement(s))
        else:
            lines.append(f"{self.indent()}pass")
        self.decrease_indent()

        # Else body
        if stmt.else_body:
            lines.append(f"{self.indent()}else:")
            self.increase_indent()
            for s in stmt.else_body:
                lines.append(self.generate_statement(s))
            self.decrease_indent()

        return "\n".join(lines)

    def generate_for(self, stmt: IRFor) -> str:
        """Generate for loop."""
        lines = []

        iterable = self.generate_expression(stmt.iterable)
        lines.append(f"{self.indent()}for {stmt.iterator} in {iterable}:")

        self.increase_indent()
        if stmt.body:
            for s in stmt.body:
                lines.append(self.generate_statement(s))
        else:
            lines.append(f"{self.indent()}pass")
        self.decrease_indent()

        return "\n".join(lines)

    def generate_while(self, stmt: IRWhile) -> str:
        """Generate while loop."""
        lines = []

        condition = self.generate_expression(stmt.condition)
        lines.append(f"{self.indent()}while {condition}:")

        self.increase_indent()
        if stmt.body:
            for s in stmt.body:
                lines.append(self.generate_statement(s))
        else:
            lines.append(f"{self.indent()}pass")
        self.decrease_indent()

        return "\n".join(lines)

    def generate_try(self, stmt: IRTry) -> str:
        """Generate try/except statement."""
        lines = []

        # Try block
        lines.append(f"{self.indent()}try:")
        self.increase_indent()
        if stmt.try_body:
            for s in stmt.try_body:
                lines.append(self.generate_statement(s))
        else:
            lines.append(f"{self.indent()}pass")
        self.decrease_indent()

        # Except blocks
        for catch in stmt.catch_blocks:
            except_line = f"{self.indent()}except"
            if catch.exception_type:
                except_line += f" {catch.exception_type}"
                if catch.exception_var:
                    except_line += f" as {catch.exception_var}"
            except_line += ":"
            lines.append(except_line)

            self.increase_indent()
            if catch.body:
                for s in catch.body:
                    lines.append(self.generate_statement(s))
            else:
                lines.append(f"{self.indent()}pass")
            self.decrease_indent()

        # Finally block
        if stmt.finally_body:
            lines.append(f"{self.indent()}finally:")
            self.increase_indent()
            for s in stmt.finally_body:
                lines.append(self.generate_statement(s))
            self.decrease_indent()

        return "\n".join(lines)

    def generate_with(self, stmt: IRWith) -> str:
        """Generate with statement (context manager)."""
        lines = []

        # Generate: with expr as var:
        context = self.generate_expression(stmt.context_expr)
        with_line = f"{self.indent()}with {context}"

        if stmt.variable:
            with_line += f" as {stmt.variable}"

        with_line += ":"
        lines.append(with_line)

        # Body
        self.increase_indent()
        if stmt.body:
            for s in stmt.body:
                lines.append(self.generate_statement(s))
        else:
            lines.append(f"{self.indent()}pass")
        self.decrease_indent()

        return "\n".join(lines)

    def generate_return(self, stmt: IRReturn) -> str:
        """Generate return statement."""
        if stmt.value:
            value = self.generate_expression(stmt.value)
            return f"{self.indent()}return {value}"
        else:
            return f"{self.indent()}return"

    def generate_raise(self, stmt: IRThrow) -> str:
        """Generate raise statement."""
        exception = self.generate_expression(stmt.exception)
        return f"{self.indent()}raise {exception}"

    # ========================================================================
    # Expression Generation
    # ========================================================================

    def generate_expression(self, expr: IRExpression) -> str:
        """Generate Python expression from IR."""
        if isinstance(expr, IRLiteral):
            return self.generate_literal(expr)
        elif isinstance(expr, IRIdentifier):
            return expr.name
        elif isinstance(expr, IRAwait):
            inner = self.generate_expression(expr.expression)
            return f"await {inner}"
        elif isinstance(expr, IRBinaryOp):
            return self.generate_binary_op(expr)
        elif isinstance(expr, IRUnaryOp):
            return self.generate_unary_op(expr)
        elif isinstance(expr, IRCall):
            return self.generate_call(expr)
        elif isinstance(expr, IRPropertyAccess):
            obj = self.generate_expression(expr.object)
            return f"{obj}.{expr.property}"
        elif isinstance(expr, IRIndex):
            obj = self.generate_expression(expr.object)
            index = self.generate_expression(expr.index)
            return f"{obj}[{index}]"
        elif isinstance(expr, IRArray):
            return self.generate_array(expr)
        elif isinstance(expr, IRMap):
            return self.generate_dict(expr)
        elif isinstance(expr, IRTernary):
            return self.generate_ternary(expr)
        elif isinstance(expr, IRLambda):
            return self.generate_lambda(expr)
        elif isinstance(expr, IRComprehension):
            return self.generate_comprehension(expr)
        else:
            return f"<unknown: {type(expr).__name__}>"

    def generate_literal(self, lit: IRLiteral) -> str:
        """Generate Python literal."""
        if lit.literal_type == LiteralType.STRING:
            # Escape string properly - use repr for Python-safe escaping
            value = str(lit.value)
            # Escape special characters
            value = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
            return f'"{value}"'
        elif lit.literal_type == LiteralType.INTEGER:
            return str(lit.value)
        elif lit.literal_type == LiteralType.FLOAT:
            return str(lit.value)
        elif lit.literal_type == LiteralType.BOOLEAN:
            return "True" if lit.value else "False"
        elif lit.literal_type == LiteralType.NULL:
            return "None"
        else:
            return str(lit.value)

    def generate_binary_op(self, expr: IRBinaryOp) -> str:
        """Generate binary operation."""
        left = self.generate_expression(expr.left)
        right = self.generate_expression(expr.right)

        # Map operator
        op_map = {
            BinaryOperator.ADD: "+",
            BinaryOperator.SUBTRACT: "-",
            BinaryOperator.MULTIPLY: "*",
            BinaryOperator.DIVIDE: "/",
            BinaryOperator.MODULO: "%",
            BinaryOperator.POWER: "**",
            BinaryOperator.EQUAL: "==",
            BinaryOperator.NOT_EQUAL: "!=",
            BinaryOperator.LESS_THAN: "<",
            BinaryOperator.LESS_EQUAL: "<=",
            BinaryOperator.GREATER_THAN: ">",
            BinaryOperator.GREATER_EQUAL: ">=",
            BinaryOperator.AND: "and",
            BinaryOperator.OR: "or",
            BinaryOperator.BIT_AND: "&",
            BinaryOperator.BIT_OR: "|",
            BinaryOperator.BIT_XOR: "^",
            BinaryOperator.LEFT_SHIFT: "<<",
            BinaryOperator.RIGHT_SHIFT: ">>",
            BinaryOperator.IN: "in",
            BinaryOperator.NOT_IN: "not in",
            BinaryOperator.IS: "is",
            BinaryOperator.IS_NOT: "is not",
        }

        op = op_map.get(expr.op, "+")
        return f"({left} {op} {right})"

    def generate_unary_op(self, expr: IRUnaryOp) -> str:
        """Generate unary operation."""
        operand = self.generate_expression(expr.operand)

        if expr.op == UnaryOperator.NOT:
            return f"not {operand}"
        elif expr.op == UnaryOperator.NEGATE:
            return f"-{operand}"
        elif expr.op == UnaryOperator.POSITIVE:
            return f"+{operand}"
        elif expr.op == UnaryOperator.BIT_NOT:
            return f"~{operand}"
        else:
            return operand

    def generate_call(self, expr: IRCall) -> str:
        """Generate function call."""
        func = self.generate_expression(expr.function)

        # Special case: Convert map(lambda, iterable) to comprehension
        if isinstance(expr.function, IRIdentifier):
            # Pattern: list(map(lambda x: expr, iterable)) -> [expr for x in iterable]
            if expr.function.name == "list" and len(expr.args) == 1:
                inner = expr.args[0]
                if isinstance(inner, IRCall) and isinstance(inner.function, IRIdentifier):
                    if inner.function.name == "map" and len(inner.args) == 2:
                        lambda_expr = inner.args[0]
                        iterable_expr = inner.args[1]
                        if isinstance(lambda_expr, IRLambda) and lambda_expr.params:
                            param_name = lambda_expr.params[0].name
                            body_expr = self.generate_expression(lambda_expr.body)
                            iterable = self.generate_expression(iterable_expr)
                            return f"[{body_expr} for {param_name} in {iterable}]"

            # Pattern: map(lambda x: expr, iterable) -> (expr for x in iterable)
            # Used in generator expressions
            elif expr.function.name == "map" and len(expr.args) == 2:
                lambda_expr = expr.args[0]
                iterable_expr = expr.args[1]
                if isinstance(lambda_expr, IRLambda) and lambda_expr.params:
                    param_name = lambda_expr.params[0].name
                    body_expr = self.generate_expression(lambda_expr.body)
                    iterable = self.generate_expression(iterable_expr)
                    # Return generator expression (without list())
                    return f"({body_expr} for {param_name} in {iterable})"

        # Regular function call
        args = [self.generate_expression(arg) for arg in expr.args]
        kwargs = [f"{k}={self.generate_expression(v)}" for k, v in expr.kwargs.items()]

        all_args = args + kwargs
        return f"{func}({', '.join(all_args)})"

    def generate_array(self, expr: IRArray) -> str:
        """Generate list literal."""
        elements = [self.generate_expression(el) for el in expr.elements]
        return f"[{', '.join(elements)}]"

    def generate_dict(self, expr: IRMap) -> str:
        """Generate dict literal."""
        if not expr.entries:
            return "{}"

        entries = [f'"{k}": {self.generate_expression(v)}' for k, v in expr.entries.items()]
        return "{" + ", ".join(entries) + "}"

    def generate_ternary(self, expr: IRTernary) -> str:
        """Generate ternary expression (Python's if-else)."""
        true_val = self.generate_expression(expr.true_value)
        cond = self.generate_expression(expr.condition)
        false_val = self.generate_expression(expr.false_value)
        return f"{true_val} if {cond} else {false_val}"

    def generate_comprehension(self, expr: IRComprehension) -> str:
        """
        Generate Python comprehension from IR.

        Supports list, dict, set, and generator comprehensions.
        """
        iterable = self.generate_expression(expr.iterable)
        iterator = expr.iterator

        # Handle condition (filter)
        condition_str = ""
        if expr.condition:
            condition_str = f" if {self.generate_expression(expr.condition)}"

        # Generate based on comprehension type
        if expr.comprehension_type == "list":
            target = self.generate_expression(expr.target)
            return f"[{target} for {iterator} in {iterable}{condition_str}]"

        elif expr.comprehension_type == "dict":
            # For dict comprehensions, target is an IRMap with __key__ and __value__
            if isinstance(expr.target, IRMap) and "__key__" in expr.target.entries and "__value__" in expr.target.entries:
                key = self.generate_expression(expr.target.entries["__key__"])
                value = self.generate_expression(expr.target.entries["__value__"])
                return f"{{{key}: {value} for {iterator} in {iterable}{condition_str}}}"
            else:
                # Fallback: treat as list comprehension
                target = self.generate_expression(expr.target)
                return f"[{target} for {iterator} in {iterable}{condition_str}]"

        elif expr.comprehension_type == "set":
            target = self.generate_expression(expr.target)
            return f"{{{target} for {iterator} in {iterable}{condition_str}}}"

        elif expr.comprehension_type == "generator":
            target = self.generate_expression(expr.target)
            return f"({target} for {iterator} in {iterable}{condition_str})"

        else:
            # Default to list comprehension
            target = self.generate_expression(expr.target)
            return f"[{target} for {iterator} in {iterable}{condition_str}]"

    def generate_lambda(self, expr: IRLambda) -> str:
        """Generate lambda expression."""
        params = ", ".join(p.name for p in expr.params)

        if isinstance(expr.body, list):
            # Multi-statement lambda (not supported in Python)
            return f"lambda {params}: None  # Multi-statement lambda not supported"
        else:
            body = self.generate_expression(expr.body)
            return f"lambda {params}: {body}"


# ============================================================================
# Public API
# ============================================================================


def generate_python(module: IRModule) -> str:
    """
    Generate Python code from IR module.

    Args:
        module: IR module to convert

    Returns:
        Python source code as string

    Example:
        >>> from dsl.ir import IRModule, IRFunction, IRParameter, IRType
        >>> module = IRModule(name="example", functions=[
        ...     IRFunction(
        ...         name="greet",
        ...         params=[IRParameter(name="name", param_type=IRType(name="string"))],
        ...         return_type=IRType(name="string")
        ...     )
        ... ])
        >>> code = generate_python(module)
        >>> print(code)
    """
    generator = PythonGeneratorV2()
    return generator.generate(module)
