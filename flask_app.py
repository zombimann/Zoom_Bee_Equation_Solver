from flask import Flask, render_template_string, request
from sympy import symbols, solve, latex
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)
from html import unescape
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
    <meta name="description" content="Free online equation solver for students and professionals. Solve algebraic, quadratic, trigonometric equations instantly.">
    <meta name="keywords" content="equation solver, math, algebra, calculator">
    <meta name="author" content="Zoom Bee Apps">
    <title>Equation Solver | Zoom Bee Apps</title>

    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async 
      src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
    </script>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 700px;
            margin: 40px auto;
            background: white;
            padding: 35px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 { margin-bottom: 10px; color: #333; }

        button {
            width: 100%;
            padding: 12px;
            background: #FF9800;
            color: white;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #F57C00; }

        .toggle-btn { margin-top: 10px; background:#4CAF50; }
        .toggle-btn:hover { background:#449d48; }

        .copy-btn { background:#1976d2; padding:10px; font-size:14px; }
        .copy-btn:hover { background:#0d47a1; }

        .copy-buttons {
            display:grid;
            grid-template-columns:repeat(4, 1fr);
            gap:10px;
            margin-top:15px;
        }

        .result {
            margin-top:30px;
            padding:20px;
            background:#f9f9f9;
            border-left:4px solid #4CAF50;
        }

        .result-section { display:none; }
        .result-section.active { display:block; }

        input[type="text"] {
            width:100%;
            padding:12px;
            border:2px solid #e0e0e0;
            border-radius:4px;
            font-size:16px;
        }
        input[type="text"]:focus { border-color:#FF9800; }

        /* ------------ Toast Notification ------------- */
        #toast {
            visibility: hidden;
            min-width: 160px;
            background: #333;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 12px;
            position: fixed;
            left: 50%;
            bottom: 40px;
            transform: translateX(-50%);
            z-index: 9999;
            font-size: 15px;
            opacity: 0;
            transition: opacity .3s ease;
        }

        #toast.show {
            visibility: visible;
            opacity: 1;
        }

        @media (max-width:600px) {
            .copy-buttons { grid-template-columns:1fr; }
        }
    </style>
</head>

<body>

<div id="toast">Copied!</div>

<div class="container">

    <div class="header">
        <div class="brand">🐝 Zoom Bee Apps</div>
        <h1>Equation Solver</h1>
        <p class="subtitle">A learning tool for students and knowledge workers</p>
    </div>

    <form method="POST">
        <div>
            <label>Enter your equation:</label>
            <input type="text" name="equation"
                   placeholder="e.g., 2x + 5 = 11"
                   value="{{ equation or '' }}"
                   maxlength="{{ max_length }}" required>
        </div>

        <div style="margin-top:20px;">
            <label>Solve for variable:</label>
            <input type="text" name="variable"
                   class="variable-input"
                   value="{{ variable or 'x' }}"
                   maxlength="{{ max_var_length }}"
                   pattern="[a-zA-Z]+" required>
        </div>

        <button style="margin-top:20px;" type="submit">Solve Equation</button>
    </form>

    {% if result %}
    <div class="result">
        <div class="result-label">Solving for <strong>{{ variable }}</strong>:</div>

        <button class="toggle-btn" type="button" onclick="toggleOutput()">
            Toggle Exact / Numeric
        </button>

        <div id="exact" class="result-section active" style="margin-top:15px; font-size:18px;">
            $${{ result }}$$
        </div>

        <div id="numeric" class="result-section" style="margin-top:15px; font-size:18px;">
            $${{ numeric }}$$
        </div>

        <div class="copy-buttons">
            <button class="copy-btn" data-copy="{{ copy_latex|e }}" onclick="copyFrom(this)">Copy LaTeX</button>
            <button class="copy-btn" data-copy="{{ copy_markdown|e }}" onclick="copyFrom(this)">Copy Markdown</button>
            <button class="copy-btn" data-copy="{{ copy_plain|e }}" onclick="copyFrom(this)">Copy Text</button>
            <button class="copy-btn" data-copy="{{ copy_html|e }}" onclick="copyFrom(this)">Copy HTML</button>
        </div>
    </div>
    {% endif %}

    {% if error %}
    <div style="margin-top:30px; padding:20px; background:#ffebee; border-left:4px solid #f44336;">
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

    if (window.MathJax) MathJax.typesetPromise();
}

function copyFrom(btn) {
    const text = btn.dataset.copy || "";

    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(showToast);
    } else {
        const t = document.createElement("textarea");
        t.value = text;
        document.body.appendChild(t);
        t.select();
        document.execCommand("copy");
        document.body.removeChild(t);
        showToast();
    }
}

function showToast() {
    const toast = document.getElementById("toast");
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 1800);
}
</script>

</body>
</html>
"""



# ---------- Input Normalization Utilities ----------

_SUPER = {
    '⁰':'**0','¹':'**1','²':'**2','³':'**3','⁴':'**4','⁵':'**5',
    '⁶':'**6','⁷':'**7','⁸':'**8','⁹':'**9'
}

def replace_superscripts(s):
    for k,v in _SUPER.items():
        s = s.replace(k,v)
    return s


def convert_natural_to_sympy(eq):
    if not eq: return eq

    eq = unescape(eq)

    # Remove code fences, HTML tags, markdown, etc.
    eq = re.sub(r'<[^>]+>', ' ', eq)
    eq = re.sub(r'`+', ' ', eq)
    eq = re.sub(r'\$\$|\$|\\[|\\]', ' ', eq)

    # Remove \left, \right
    eq = eq.replace("\\left","").replace("\\right","")

    # LaTeX conversions
    eq = re.sub(r'\\sqrt\s*{([^}]*)}', r'sqrt(\1)', eq)

    def frac(m):
        return f"(({m.group(1)})/({m.group(2)}))"
    eq = re.sub(r'\\frac\s*{([^}]*)}{([^}]*)}', frac, eq)

    eq = eq.replace("\\cdot","*").replace("\\times","*").replace("\\div","/")
    eq = eq.replace("\\ln","log").replace("\\log","log").replace("\\exp","exp")

    # Unicode normalization
    eq = eq.replace("√", "sqrt")
    eq = replace_superscripts(eq)
    eq = eq.replace("·","*").replace("×","*").replace("÷","/")
    eq = eq.replace("π","pi")

    # Spaces
    eq = re.sub(r'\s+',' ', eq).strip()

    return eq


# ---------- Safety Utilities ----------
def is_safe_input(t):
    bad = ["__", "import", "eval", "exec", "compile",
           "open", "input", "globals", "locals", "vars"]
    t = t.lower()
    return not any(b in t for b in bad)

def is_valid_variable(v):
    return bool(re.match(r"^[a-zA-Z]+$", v))


# ---------- Main Route ----------
@app.route("/", methods=["GET","POST"])
def index():
    result = None
    numeric_result = None
    error = None
    equation = None
    variable = "x"

    copy_latex = ""
    copy_markdown = ""
    copy_plain = ""
    copy_html = ""

    if request.method == "POST":
        equation = (request.form.get("equation") or "").strip()
        variable = (request.form.get("variable") or "x").strip()

        if len(equation) > MAX_EQUATION_LENGTH:
            error = "Equation is too long."
        elif len(variable) > MAX_VARIABLE_LENGTH or not is_valid_variable(variable):
            error = "Invalid variable name."
        elif not is_safe_input(equation):
            error = "Invalid input."
        else:
            try:
                conv = convert_natural_to_sympy(equation)
                transforms = (standard_transformations +
                              (implicit_multiplication_application,))

                if "=" in conv:
                    L, R = conv.split("=",1)
                    expr = parse_expr(L, transformations=transforms) - \
                           parse_expr(R, transformations=transforms)
                else:
                    expr = parse_expr(conv, transformations=transforms)

                sym = symbols(variable)
                sols = solve(expr, sym)

                if not sols:
                    result = "\\text{No solution}"
                    numeric_result = "\\text{No numeric form}"
                    copy_plain = copy_latex = copy_markdown = "No solution"
                    copy_html = "<!-- No solution -->"
                else:
                    if len(sols) == 1:
                        exact = sols[0]
                        num = exact.evalf()
                        result = f"{variable} = {latex(exact)}"
                        numeric_result = f"{variable} \\approx {latex(num)}"

                        copy_latex = result
                        copy_markdown = f"${result}$"
                        copy_plain = f"{variable} = {exact}"
                        copy_html = f'<span>{variable} = \\({latex(exact)}\\)</span>'
                    else:
                        exacts = ", ".join(latex(s) for s in sols)
                        nums = ", ".join(latex(s.evalf()) for s in sols)

                        result = f"{variable} = {exacts}"
                        numeric_result = f"{variable} \\approx {nums}"

                        copy_latex = result
                        copy_markdown = f"${result}$"
                        copy_plain = f"{variable} = {', '.join(str(s) for s in sols)}"
                        copy_html = f'<span>{variable} = \\({exacts}\\)</span>'

            except Exception:
                error = "Unable to solve equation."

    return render_template_string(
        HTML_TEMPLATE,
        result=result,
        numeric=numeric_result,
        copy_latex=copy_latex,
        copy_markdown=copy_markdown,
        copy_plain=copy_plain,
        copy_html=copy_html,
        error=error,
        equation=equation,
        variable=variable,
        max_length=MAX_EQUATION_LENGTH,
        max_var_length=MAX_VARIABLE_LENGTH
    )


if __name__ == "__main__":
    app.run(debug=True)
