# 🐝 Equation Solver

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A minimalistic web application for solving mathematical equations. Built with Flask and SymPy, designed to help students and knowledge workers solve equations quickly and intuitively.

**Live Demo**: [Your PythonAnywhere URL]

## ✨ Features

- **Natural Math Notation**: Write equations as you would on paper (e.g., `2x + 5 = 11`, `x²`, `√x`)
- **Custom Variables**: Solve for any variable name (x, y, z, theta, alpha, etc.)
- **Multiple Equation Types**: Linear, quadratic, trigonometric, radical, and more
- **Beautiful Math Rendering**: LaTeX-formatted solutions using MathJax
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Secure**: Input validation and sanitization to prevent malicious code execution
- **SEO Optimized**: Structured for search engine visibility

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/zombimann/equation-solver.git
cd equation-solver
```

2. Install dependencies:
```bash
pip install flask sympy
```

3. Run the application:
```bash
python flask_app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## 🌐 Deployment on PythonAnywhere

### Step-by-Step Guide

1. **Create an account** at [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload your application**:
   - Go to the **Files** tab
   - Upload `flask_app.py` to your home directory or `/home/yourusername/mysite/`

3. **Install dependencies**:
   - Open a **Bash console**
   - Run: `pip3 install --user sympy`

4. **Configure the web app**:
   - Go to the **Web** tab
   - Click **Add a new web app**
   - Choose **Flask** and Python 3.x
   - Set the source code directory to where you uploaded the file
   - Edit the WSGI configuration file:

```python
import sys
path = '/home/yourusername/mysite'
if path not in sys.path:
    sys.path.append(path)

from flask_app import app as application
```

5. **Reload the web app**:
   - Click the green **Reload** button
   - Your app will be live at `yourusername.pythonanywhere.com`

## 📖 Usage

### Basic Examples

**Linear Equation**:
```
2x + 5 = 11
Solve for: x
Result: x = 3
```

**Quadratic Equation**:
```
x² - 4 = 0
Solve for: x
Result: x = -2, 2
```

**Custom Variable**:
```
3(theta - 2) = 15
Solve for: theta
Result: theta = 7
```

**Square Root**:
```
√y = 4
Solve for: y
Result: y = 16
```

### Supported Notation

- **Powers**: `x²`, `x³`, `x^2`, `x^3`
- **Multiplication**: `2x` (implicit), `2*x` (explicit)
- **Square Root**: `√x`, `sqrt(x)`
- **Functions**: `sin(x)`, `cos(x)`, `tan(x)`, `log(x)`, `ln(x)`, `exp(x)`
- **Operations**: `+`, `-`, `×`, `÷`, `/`, `*`

## 🛡️ Security Features

- Input length restrictions (500 chars for equations, 10 for variables)
- Pattern matching to prevent code injection
- Variable name validation (letters only)
- Sanitized error messages
- No execution of arbitrary code
- CSRF protection through Flask

## 🏗️ Architecture

```
flask_app.py
├── Flask application setup
├── Route handlers
│   └── index() - Main solver endpoint
├── Utility functions
│   ├── convert_natural_to_sympy() - Notation conversion
│   ├── is_safe_input() - Security validation
│   └── is_valid_variable() - Variable validation
└── HTML template with embedded CSS and JavaScript
```

## 🔧 Technology Stack

- **Backend**: Flask 2.0+
- **Math Engine**: SymPy (symbolic mathematics)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Math Rendering**: MathJax 3
- **Hosting**: PythonAnywhere (recommended)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Zoom Bee Apps**
- GitHub: [@zombimann](https://github.com/zombimann)

## 🙏 Acknowledgments

- [SymPy](https://www.sympy.org/) for the powerful symbolic mathematics library
- [Flask](https://flask.palletsprojects.com/) for the lightweight web framework
- [MathJax](https://www.mathjax.org/) for beautiful math rendering
- [PythonAnywhere](https://www.pythonanywhere.com/) for easy Python hosting

## 📊 Future Enhancements

- [ ] Step-by-step solution explanations
- [ ] Graph plotting for equations
- [ ] System of equations solver
- [ ] Export solutions to PDF
- [ ] Equation history/favorites
- [ ] Dark mode support
- [ ] API endpoint for programmatic access

## 🐛 Bug Reports

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)

## 💡 Support

For support, please open an issue on GitHub or contact through the repository.

---

Made with 🐝 by Zoom Bee Apps | Empowering learners and knowledge workers
