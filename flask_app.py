from flask import Flask, render_template_string, request, escape
from sympy import symbols, solve, sympify, latex
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import re

app = Flask(__name__)

# Security: Set max input length
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
        form {
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 10px;
            align-items: end;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
            font-size: 14px;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 4px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #FF9800;
        }
        .variable-input {
            width: 80px;
            text-align: center;
            font-weight: 500;
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
        button:hover {
            background: #F57C00;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            background: #f9f9f9;
            border-left: 4px solid #4CAF50;
            border-radius: 4px;
        }
        .result-label {
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .error {
            margin-top: 30px;
            padding: 20px;
            background: #ffebee;
            border-left: 4px solid #f44336;
            border-radius: 4px;
            color: #c62828;
        }
        .example {
            margin-top: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 4px;
            font-size: 14px;
        }
        .example strong {
            color: #1976d2;
        }
        code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        .tips {
            margin-top: 15px;
            padding: 15px;
            background: #fff3e0;
            border-radius: 4px;
            font-size: 13px;
            color: #e65100;
        }
        .ad-space {
            margin-top: 25px;
            padding: 15px;
            background: #fafafa;
            border: 1px dashed #ddd;
            border-radius: 4px;
            text-align: center;
            color: #999;
            font-size: 12px;
            min-height: 90px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #999;
            font-size: 13px;
        }
        .footer a {
            color: #FF9800;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .seo-content {
            margin-top: 40px;
            padding: 25px;
            background: #fafafa;
            border-radius: 4px;
            font-size: 14px;
            color: #666;
            line-height: 1.8;
        }
        .seo-content h2 {
            color: #333;
            font-size: 20px;
            margin-bottom: 15px;
        }
        .seo-content p {
            margin-bottom: 12px;
        }
        @media (max-width: 600px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            .variable-input {
                width: 100%;
            }
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
                       maxlength="{{ max_length }}"
                       required>
            </div>

            <div class="form-group">
                <div class="form-row">
                    <div>
                        <label for="variable">Solve for variable:</label>
                        <input type="text" 
                               id="variable" 
                               name="variable" 
                               class="variable-input"
                               placeholder="x" 
                               value="{{ variable or 'x' }}"
                               maxlength="{{ max_var_length }}"
                               pattern="[a-zA-Z]+"
                               title="Enter a variable name (letters only)"
                               required>
                    </div>
                </div>
            </div>

            <button type="submit">Solve Equation</button>
        </form>

        {% if result %}
        <div class="result">
            <div class="result-label">Solving for <strong>{{ variable }}</strong>:</div>
            <div style="margin-top: 10px; font-size: 18px;">
                $${{ result }}$$
            </div>
        </div>
        {% endif %}

        {% if error %}
        <div class="error">
            <strong>Error:</strong> {{ error }}
        </div>
        {% endif %}

        <div class="example">
            <strong>Example Equations:</strong><br>
            • <code>2x + 5 = 11</code> (Linear equation)<br>
            • <code>y² - 4 = 0</code> (Quadratic equation)<br>
            • <code>3(t - 2) = 15</code> (With parentheses)<br>
            • <code>√z = 4</code> (Square root)<br>
            • <code>a² + 2a + 1 = 0</code> (Any variable name)
        </div>

        <div class="tips">
            <strong>Input Tips:</strong><br>
            • Use ² or ^2 for powers • Write 2x instead of 2*x<br>
            • Use √ or sqrt() for square roots<br>
            • Functions: sin, cos, tan, log, ln, exp<br>
            • You can use any variable name (x, y, z, theta, etc.)
        </div>

        <div class="ad-space">
            <!-- Ad space reserved for future use -->
            <span>Supporting tools for learners 🐝</span>
        </div>

        <div class="footer">
            Made with 🐝 by Zoom Bee Apps<br>
            <a href="https://github.com/zombimann" target="_blank" rel="noopener">GitHub: @zombimann</a> | 
            Empowering learners and knowledge workers
        </div>
    </div>

    <div class="container seo-content">
        <h2>About This Equation Solver</h2>
        <p>
            Our free online equation solver helps students, teachers, and professionals solve mathematical equations quickly and accurately. 
            Whether you're working on homework, studying for exams, or solving real-world problems, this tool makes equation solving simple and accessible.
        </p>
        <p>
            <strong>Perfect for:</strong> Algebra homework, quadratic equations, trigonometric problems, calculus assignments, and professional calculations. 
            The solver supports multiple variable names, implicit multiplication, and natural mathematical notation, making it intuitive for users of all levels.
        </p>
        <p>
            <strong>Features:</strong> Instant solutions, step-by-step capability, support for square roots, exponents, trigonometric functions, 
            and both simple and complex equations. All calculations are performed using advanced symbolic mathematics for precise results.
        </p>
    </div>
</body>
</html>
"""

def convert_natural_to_sympy(equation):
    """Convert natural math notation to SymPy-compatible format"""
    # Replace common symbols
    equation = equation.replace('√', 'sqrt')
    equation = equation.replace('×', '*')
    equation = equation.replace('÷', '/')
    equation = equation.replace('^', '**')
    equation = equation.replace('²', '**2')
    equation = equation.replace('³', '**3')
    
    # Handle ln as natural log
    equation = equation.replace('ln(', 'log(')
    
    return equation

def is_safe_input(text):
    """Basic security check for malicious input"""
    # Check for dangerous patterns
    dangerous_patterns = [
        '__', 'import', 'eval', 'exec', 'compile', 
        'open', 'file', 'input', 'raw_input', 'globals', 
        'locals', 'vars', 'dir'
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if pattern in text_lower:
            return False
    
    return True

def is_valid_variable(var):
    """Check if variable name is valid (letters only)"""
    return bool(re.match(r'^[a-zA-Z]+$', var))

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    equation = None
    variable = 'x'
    
    if request.method == 'POST':
        equation = request.form.get('equation', '').strip()
        variable = request.form.get('variable', 'x').strip()
        
        # Security: Check input length
        if len(equation) > MAX_EQUATION_LENGTH:
            error = "Equation is too long. Please keep it under 500 characters."
            return render_template_string(HTML_TEMPLATE, 
                                         error=error,
                                         equation=None,
                                         variable=variable,
                                         max_length=MAX_EQUATION_LENGTH,
                                         max_var_length=MAX_VARIABLE_LENGTH)
        
        # Security: Validate variable
        if len(variable) > MAX_VARIABLE_LENGTH or not is_valid_variable(variable):
            error = "Variable name must contain only letters (a-z, A-Z) and be under 10 characters."
            return render_template_string(HTML_TEMPLATE, 
                                         error=error,
                                         equation=equation,
                                         variable='x',
                                         max_length=MAX_EQUATION_LENGTH,
                                         max_var_length=MAX_VARIABLE_LENGTH)
        
        # Security: Check for malicious input
        if not is_safe_input(equation) or not is_safe_input(variable):
            error = "Invalid input detected. Please use standard mathematical notation."
            return render_template_string(HTML_TEMPLATE, 
                                         error=error,
                                         equation=None,
                                         variable='x',
                                         max_length=MAX_EQUATION_LENGTH,
                                         max_var_length=MAX_VARIABLE_LENGTH)
        
        try:
            # Convert natural notation to SymPy format
            converted_equation = convert_natural_to_sympy(equation)
            
            # Parse with implicit multiplication (so 2x works)
            transformations = (standard_transformations + 
                             (implicit_multiplication_application,))
            
            # Parse the equation
            if '=' in converted_equation:
                parts = converted_equation.split('=')
                if len(parts) != 2:
                    raise ValueError("Equation must have exactly one equals sign")
                lhs, rhs = parts
                expr = parse_expr(lhs, transformations=transformations) - parse_expr(rhs, transformations=transformations)
            else:
                expr = parse_expr(converted_equation, transformations=transformations)
            
            # Create symbol for the user-supplied variable
            var_symbol = symbols(variable)
            
            # Solve for the selected variable
            solutions = solve(expr, var_symbol)
            
            # Format solutions
            if not solutions:
                result = "\\text{No solution found}"
            elif len(solutions) == 1:
                result = f"{variable} = {latex(solutions[0])}"
            else:
                result = f"{variable} = " + ", \\quad ".join([latex(sol) for sol in solutions])
                
        except Exception as e:
            error = "Unable to solve equation. Please check your syntax and try again."
    
    return render_template_string(HTML_TEMPLATE, 
                                 result=result, 
                                 error=error,
                                 equation=equation,
                                 variable=variable,
                                 max_length=MAX_EQUATION_LENGTH,
                                 max_var_length=MAX_VARIABLE_LENGTH)

if __name__ == '__main__':
    app.run(debug=True)