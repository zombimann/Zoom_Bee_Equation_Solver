from flask import Flask, render_template_string, request, escape
from sympy import symbols, solve, sympify, latex
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import re

app = Flask(__name__)

MAX_EQUATION_LENGTH = 500
MAX_VARIABLE_LENGTH = 10

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Free online equation solver for students and professionals. Solve algebraic, quadratic, trigonometric equations instantly. Perfect for homework, learning, and quick calculations.">
    <meta name="keywords" content="equation solver, math solver, algebra calculator, quadratic equation solver, solve equations online, free math calculator, homework helper">
    <meta name="author" content="Zoom Bee Apps">
    <meta property="og:title" content="Equation Solver - Free Online Math Calculator">
    <meta property="og:description" content="Solve any equation instantly with our free online calculator. Perfect for students and knowledge workers.">
    <meta property="og:type" content="website">
    <title>Free Equation Solver - Solve Math Equations Online | Zoom Bee Apps</title>
    <link rel="canonical" href="https://yourusername.pythonanywhere.com/">

    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 700px;
            margin: 40px auto;
            background: white;
            padding: 35px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        .brand {
            color: #FF9800;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        h1 {
            color: #333;
            margin-bottom: 8px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            font-size: 15px;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #FF9800;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover { background: #F57C00; }

        .toggle-btn {
            margin-top: 10px;
            background: #4CAF50;
        }
        .toggle-btn:hover { background: #449d48; }

        .result {
            margin-top: 30px;
            padding: 20px;
            background: #f9f9f9;
            border-left: 4px solid #4CAF50;
            border-radius: 4px;
        }

        .result-section { display: none; }
        .result-section.active { display: block; }

        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 4px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus { border-color: #FF9800; }

        .variable-input {
            width: 80px;
            text-align: center;
            font-weight: 500;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 10px;
            align-items: end;
        }

        @media (max-width: 600px) {
            .form-row { grid-template-columns: 1fr; }
            .variable-input { width: 100%; }
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="header">
            <div class="brand">🐝 Zoom Bee Apps</div>
            <h1>Equation Solver</h1>
            <p class="subtitle">A learning tool for students and knowledge workers</p>
        </div>

        <form method="POST">
            <div class="form-group">
                <label for="equation">Enter your equation:</label>
                <input type="text" id="equation" name="equation"
                       placeholder="e.g., 2x + 5 = 11"
                       value="{{ equation or '' }}"
                       maxlength="{{ max_length }}" required>
            </div>

            <div class="form-group">
                <div class="form-row">
                    <div>
                        <label for="variable">Solve for variable:</label>
                        <input type="text" id="variable" name="variable"
                               class="variable-input" placeholder="x"
                               value="{{ variable or 'x' }}"
                               maxlength="{{ max_var_length }}"
                               pattern="[a-zA-Z]+" required>
                    </div>
                </div>
            </div>

            <button type="submit">Solve Equation</button>
        </form>

        {% if result %}
        <div class="result">
            <div class="result-label">Solving for <strong>{{ variable }}</strong>:</div>

            <button class="toggle-btn" type="button" onclick="toggleOutput()">
                Toggle Exact / Numeric
            </button>

            <div id="exact" class="result-section active" style="font-size: 18px; margin-top: 15px;">
                $${{ result }}$$
            </div>

            <div id="numeric" class="result-section" style="font-size: 18px; margin-top: 15px;">
                $${{ numeric }}$$
            </div>
        </div>
        {% endif %}

        {% if error %}
        <div class="error" style="margin-top: 30px; padding: 20px; background:#ffebee; border-left:4px solid #f44336;">
            <strong>Error:</strong> {{ error }}
        </div>
        {% endif %}
    </div>

<script>
function toggleOutput() {
    const exact = document.getElementById("exact");
    const numeric = document.getElementById("numeric");

    exact.classList.toggle("active");
    numeric.classList.toggle("active");

    if (window.MathJax) { MathJax.typesetPromise(); }
}
</script>

</body>
</html>
"""

def convert_natural_to_sympy(eq):
    eq = eq.replace("√", "sqrt")
    eq = eq.replace("×", "*").replace("÷", "/")
    eq = eq.replace("^", "**").replace("²", "**2").replace("³", "**3")
    eq = eq.replace("ln(", "log(")
    return eq

def is_safe_input(text):
    forbidden = ["__", "import", "eval", "exec", "compile", "open",
                 "file", "input", "globals", "locals", "vars", "dir"]
    t = text.lower()
    return not any(x in t for x in forbidden)

def is_valid_variable(v):
    return bool(re.match(r"^[a-zA-Z]+$", v))

@app.route("/", methods=["GET","POST"])
def index():
    result = None
    numeric_result = None
    error = None
    equation = None
    variable = "x"

    if request.method == "POST":
        equation = request.form.get("equation","").strip()
        variable = request.form.get("variable","x").strip()

        if len(equation) > MAX_EQUATION_LENGTH:
            error = "Equation is too long. Keep under 500 characters."
            return render_template_string(HTML_TEMPLATE, error=error,
                                          equation=None, variable=variable,
                                          max_length=MAX_EQUATION_LENGTH,
                                          max_var_length=MAX_VARIABLE_LENGTH)

        if len(variable) > MAX_VARIABLE_LENGTH or not is_valid_variable(variable):
            error = "Variable must be letters only and under 10 characters."
            return render_template_string(HTML_TEMPLATE, error=error,
                                          equation=equation, variable="x",
                                          max_length=MAX_EQUATION_LENGTH,
                                          max_var_length=MAX_VARIABLE_LENGTH)

        if not is_safe_input(equation) or not is_safe_input(variable):
            error = "Invalid input detected."
            return render_template_string(HTML_TEMPLATE, error=error,
                                          equation=None, variable="x",
                                          max_length=MAX_EQUATION_LENGTH,
                                          max_var_length=MAX_VARIABLE_LENGTH)

        try:
            converted = convert_natural_to_sympy(equation)
            transformations = (standard_transformations +
                               (implicit_multiplication_application,))

            if "=" in converted:
                left, right = converted.split("=")
                expr = parse_expr(left, transformations=transformations) \
                       - parse_expr(right, transformations=transformations)
            else:
                expr = parse_expr(converted, transformations=transformations)

            sym = symbols(variable)
            solutions = solve(expr, sym)

            if not solutions:
                result = "\\text{No solution found}"
                numeric_result = "\\text{No numeric form}"
            else:
                if len(solutions) == 1:
                    result = f"{variable} = {latex(solutions[0])}"
                    numeric_result = f"{variable} ≈ {latex(solutions[0].evalf())}"
                else:
                    result = f"{variable} = " + ",\\;".join(latex(s) for s in solutions)
                    numeric_result = f"{variable} ≈ " + ",\\;".join(latex(s.evalf()) for s in solutions)

        except:
            error = "Unable to solve equation. Please check syntax."

    return render_template_string(HTML_TEMPLATE,
                                  result=result,
                                  numeric=numeric_result,
                                  error=error,
                                  equation=equation,
                                  variable=variable,
                                  max_length=MAX_EQUATION_LENGTH,
                                  max_var_length=MAX_VARIABLE_LENGTH)

if __name__ == "__main__":
    app.run(debug=True)
