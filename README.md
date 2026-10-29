# 🧮 Scientific Calculator

A modern, interactive scientific calculator built with **Python, Flask, HTML, CSS, and JavaScript**. It provides scientific functions, mathematical constants, and multiple calculation modes through a web-based interface.

## ✨ Features

- **Scientific calculations** — trigonometric, inverse trigonometric, hyperbolic, logarithmic, and exponential functions.
- **Advanced mathematics** — powers, roots, factorials, permutations, and combinations.
- **Multiple angle modes** — degrees, radians, and gradians.
- **Complex number support** — calculations involving imaginary numbers.
- **Scientific constants** — access to mathematical and physical constants.
- **Memory and variables** — reuse previous answers and variables.
- **Multiple result formats** — decimal, fraction, and scientific notation where supported.
- **Modern user interface** — dark theme, calculator-style buttons, and a digital display.
- **Responsive layout** — designed for different screen sizes.

## 🌐 Live Demo

**[Open Scientific Calculator](https://scientific-calculator-578e.onrender.com)**

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend calculation logic |
| Flask | Web application and routing |
| HTML5 | Page structure |
| CSS3 | Styling and layout |
| JavaScript | Interactive calculator controls |

## 📂 Project Structure

```text
Scientific-Calculator/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
└── templates/
    └── index.html
```

## 🚀 Getting Started

Follow these steps to run the project locally.

### Prerequisites

- Python 3.10 or later
- pip (Python package installer)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/omsaibhalekar2808/Scientific-Calculator.git
```

### 2. Open the Project Directory

```bash
cd Scientific-Calculator
```

### 3. Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```bat
.venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

### 6. Open the Calculator

Visit the following address in your browser:

http://127.0.0.1:5000

## 🧪 Example Calculations

| Operation | Example | Expected Result |
|---|---|---|
| Addition | `25 + 15` | `40` |
| Square root | `sqrt(144)` | `12` |
| Power | `2^5` | `32` |
| Sine | `sin(30)` in degree mode | `0.5` |
| Factorial | `5!` | `120` |
| Logarithm | `log(100)` | `2` |

*Results depend on the selected angle mode and calculator settings.*

## 🔐 Security Notes

- Keep Flask debug mode disabled in publicly accessible environments.
- Never commit passwords, API keys, access tokens, or other private credentials.
- Validate mathematical expressions and apply reasonable computation limits before accepting public traffic.
- Use a production WSGI server, such as Gunicorn, when deploying the application.

## 🔮 Future Improvements

- Add calculation history with persistent storage.
- Introduce unit conversion tools.
- Improve keyboard navigation and accessibility.
- Add automated tests for mathematical functions and error handling.

## 👨‍💻 Author

**Omsai Bhalekar**

- GitHub: [@omsaibhalekar2808](https://github.com/omsaibhalekar2808)
- Project Repository: [Scientific Calculator](https://github.com/omsaibhalekar2808/Scientific-Calculator)

## 📄 License

No license has been specified yet. Add a license if you decide to permit others to reuse, modify, or distribute this project.

---

⭐ If you find this project interesting, consider starring the repository!
