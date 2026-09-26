import ast
import json
import math
import operator
import re
from pathlib import Path

from flask import Flask, render_template, request

app = Flask(__name__)
app.config["SECRET_KEY"] = "todo-playground"
DATA_FILE = Path(__file__).resolve().parent / "tasks.json"


class CalculationError(ValueError):
    pass


_ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

_ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _normalize_expression(expression):
    expression = (expression or "").strip()
    if not expression:
        raise CalculationError("Enter an expression to calculate.")

    replacements = {
        "×": "*",
        "÷": "/",
        "^": "**",
        "π": "pi",
        "√": "sqrt",
        "−": "-",
        "–": "-",
        "—": "-",
    }
    for source, target in replacements.items():
        expression = expression.replace(source, target)

    expression = re.sub(r"(?i)\bpi\b", "pi", expression)
    expression = re.sub(r"(?i)\bpow\b", "pow", expression)
    expression = re.sub(r"(?i)\broot\b", "root", expression)
    expression = re.sub(r"\s+", " ", expression)
    expression = expression.replace(" ", "")
    return expression


def _evaluate_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise CalculationError("Only numeric constants are supported.")

    if isinstance(node, ast.Name):
        name = node.id.lower()
        if name == "pi":
            return math.pi
        if name == "e":
            return math.e
        raise CalculationError(f"Unsupported variable or constant: {node.id}")

    if isinstance(node, ast.BinOp):
        if type(node.op) not in _ALLOWED_BINARY_OPERATORS:
            raise CalculationError("Unsupported operator used in the expression.")
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)
        return _ALLOWED_BINARY_OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in _ALLOWED_UNARY_OPERATORS:
            raise CalculationError("Unsupported unary operator used in the expression.")
        operand = _evaluate_node(node.operand)
        return _ALLOWED_UNARY_OPERATORS[type(node.op)](operand)

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise CalculationError("Only direct function calls are supported.")

        func_name = node.func.id.lower()
        args = [_evaluate_node(arg) for arg in node.args]

        if func_name in {"sin", "cos", "tan", "asin", "acos", "atan", "sqrt", "log", "ln", "log10", "exp", "abs", "floor", "ceil", "cbrt"}:
            if len(args) != 1:
                raise CalculationError(f"Function {func_name} expects one argument.")
            if func_name == "log":
                return math.log10(args[0])
            if func_name == "ln":
                return math.log(args[0])
            if func_name == "log10":
                return math.log10(args[0])
            func = getattr(math, func_name, None)
            if func is None:
                raise CalculationError(f"Function {func_name} is not supported.")
            return func(args[0])

        if func_name == "pow":
            if len(args) != 2:
                raise CalculationError("The pow function expects two arguments: pow(base, exponent).")
            return math.pow(args[0], args[1])

        if func_name == "root":
            if len(args) != 2:
                raise CalculationError("The root function expects two arguments: root(value, degree).")
            value, degree = args
            if degree == 0:
                raise CalculationError("Root degree cannot be zero.")
            return value ** (1 / degree)

        raise CalculationError(f"Unsupported function: {func_name}")

    raise CalculationError("This expression contains unsupported syntax.")


def evaluate_expression(expression):
    normalized_expression = _normalize_expression(expression)
    try:
        parsed = ast.parse(normalized_expression, mode="eval")
    except SyntaxError as exc:
        raise CalculationError("Invalid expression. Please check the syntax and try again.") from exc

    return _evaluate_node(parsed.body)


def format_value(value):
    if isinstance(value, float):
        if math.isclose(value, round(value), rel_tol=1e-12, abs_tol=1e-12):
            return str(int(round(value)))
        return format(value, ".10g")
    return str(value)


def _load_tasks():
    if not DATA_FILE.exists():
        return []

    try:
        raw_tasks = json.loads(DATA_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        return []

    if isinstance(raw_tasks, list):
        return raw_tasks
    return []


def _save_tasks(tasks):
    DATA_FILE.write_text(json.dumps(tasks, indent=2))


def _next_task_id(tasks):
    return max((task.get("id", -1) for task in tasks), default=-1) + 1


@app.route("/", methods=["GET", "POST"])
def index():
    tasks = _load_tasks()
    filter_name = request.args.get("filter", "all")
    editing_task_id = request.args.get("edit_id", type=int)

    if request.method == "POST":
        filter_name = request.form.get("filter", filter_name)
        action = request.form.get("action")

        if action == "add":
            title = (request.form.get("title") or "").strip()
            if title:
                tasks.append(
                    {
                        "id": _next_task_id(tasks),
                        "title": title,
                        "due_date": (request.form.get("due_date") or "").strip(),
                        "completed": False,
                    }
                )
                _save_tasks(tasks)
        elif action == "toggle":
            task_id = request.form.get("task_id", type=int)
            for task in tasks:
                if task.get("id") == task_id:
                    task["completed"] = not task.get("completed", False)
                    break
            _save_tasks(tasks)
        elif action == "start_edit":
            editing_task_id = request.form.get("task_id", type=int)
        elif action == "save_edit":
            task_id = request.form.get("task_id", type=int)
            title = (request.form.get("title") or "").strip()
            due_date = (request.form.get("due_date") or "").strip()
            for task in tasks:
                if task.get("id") == task_id:
                    if title:
                        task["title"] = title
                    task["due_date"] = due_date
                    break
            _save_tasks(tasks)
            editing_task_id = None
        elif action == "delete":
            task_id = request.form.get("task_id", type=int)
            tasks = [task for task in tasks if task.get("id") != task_id]
            _save_tasks(tasks)
        elif action == "clear_completed":
            tasks = [task for task in tasks if not task.get("completed", False)]
            _save_tasks(tasks)

    if filter_name == "active":
        visible_tasks = [task for task in tasks if not task.get("completed", False)]
    elif filter_name == "completed":
        visible_tasks = [task for task in tasks if task.get("completed", False)]
    else:
        visible_tasks = tasks

    return render_template(
        "index.html",
        tasks=visible_tasks,
        filter_name=filter_name,
        total_tasks=len(tasks),
        active_count=sum(1 for task in tasks if not task.get("completed", False)),
        completed_count=sum(1 for task in tasks if task.get("completed", False)),
        editing_task_id=editing_task_id,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
