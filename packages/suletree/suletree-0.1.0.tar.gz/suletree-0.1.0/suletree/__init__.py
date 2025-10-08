import ast
import os
import sys
import argparse


# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_FOLDER = "\033[1;33m"    # Bold Yellow
COLOR_FILE = "\033[95m"      # Magenta
COLOR_CLASS = "\033[96m"       # Cyan
COLOR_FUNCTION = "\033[92m"    # Green
COLOR_ASYNC_FUNCTION = "\033[38;2;0;255;127m"  # Spring Green


def get_function_signature(node: ast.AST) -> str:
    """
    Returns the signature of a function or async function, including arguments and default values.
    """
    # Detect if it's async
    is_async = isinstance(node, ast.AsyncFunctionDef)
    
    args = []
    for arg in node.args.args:
        args.append(arg.arg)

    # Handle defaults
    defaults = [None] * (len(node.args.args) - len(node.args.defaults)) + node.args.defaults
    for i, default in enumerate(defaults):
        if default is not None:
            try:
                default_str = ast.unparse(default)
            except Exception:
                default_str = "..."
            args[i] = f"{args[i]}={default_str}"

    # Handle *args and **kwargs
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")

    # Build the signature
    prefix = "async " if is_async else ""
    return f"{prefix}{node.name}({', '.join(args)})"


def list_classes_and_functions(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    classes = []
    functions = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [(n, get_function_signature(n)) for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            classes.append((node.name, methods))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append((node, get_function_signature(node)))
    
    return classes, functions


def print_tree(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # skip __pycache__, .git, and other hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "__pycache__"]
        
        level = dirpath.replace(root_dir, "").count(os.sep)
        indent = "│   " * level
        print(f"{indent}{COLOR_FOLDER}{os.path.basename(dirpath)}/{COLOR_RESET}")

        subindent = "│   " * (level + 1)
        py_files = sorted([f for f in filenames if f.endswith(".py")])
        for i, filename in enumerate(py_files):
            last_file = (i == len(py_files) - 1)
            file_prefix = "└── " if last_file else "├── "
            filepath = os.path.join(dirpath, filename)
            print(f"{subindent}{file_prefix}{COLOR_FILE}{filename}{COLOR_RESET}")

            classes, functions = list_classes_and_functions(filepath)

            # Print classes with methods
            for j, (cls_name, methods) in enumerate(classes):
                last_class = (j == len(classes) - 1 and not functions)
                cls_prefix = "└── " if last_class else "├── "
                print(f"{subindent}│   {cls_prefix}{COLOR_CLASS}class {cls_name}{COLOR_RESET}")

                for k, (method_node, method_sig) in enumerate(methods):
                    last_method = (k == len(methods) - 1)
                    method_prefix = "└── " if last_method else "├── "
                    color = COLOR_ASYNC_FUNCTION if isinstance(method_node, ast.AsyncFunctionDef) else COLOR_FUNCTION
                    print(f"{subindent}│   │   {method_prefix}{color}{method_sig}{COLOR_RESET}")

            # Print top-level functions
            for f_idx, (func_node, func_sig) in enumerate(functions):
                last_func = (f_idx == len(functions) - 1)
                func_prefix = "└── " if last_func else "├── "
                color = COLOR_ASYNC_FUNCTION if isinstance(func_node, ast.AsyncFunctionDef) else COLOR_FUNCTION
                print(f"{subindent}│   {func_prefix}{color}{func_sig}{COLOR_RESET}")


def main():
    parser = argparse.ArgumentParser(
        description="Print the structure of Python modules in a tree-like format",
        epilog="Example: suletree ."
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the directory or Python file to analyze"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="suletree 0.1.0",
        help="Show version information"
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Your existing logic here
    if os.path.exists(args.path):
        print_tree(args.path)
    else:
        print(f"Error: Path '{args.path}' does not exist")
        sys.exit(1)


if __name__ == "__main__":
    main()
