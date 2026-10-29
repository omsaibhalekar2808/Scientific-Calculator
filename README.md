# 🧮 Scientific Calculator

A modern, interactive scientific calculator built using **Python, Flask, HTML, CSS, and JavaScript**. It combines a calculator-inspired interface with mathematical functions, scientific constants, and multiple calculation modes.

## ✨ Features

- **Scientific calculations** — trigonometric, inverse trigonometric, hyperbolic, logarithmic, and exponential functions.
- **Advanced mathematics** — powers, roots, factorials, permutations, and combinations.
- **Multiple angle modes** — degrees, radians, and gradians.
- **Complex number support** — perform calculations involving imaginary numbers.
- **Scientific constants** — access 23 mathematical and physical constants.
- **Memory and variables** — use previous answers and variables in calculations.
- **Multiple result formats** — decimal, fraction, and scientific notation where supported.
- **Modern user interface** — dark theme, calculator-style buttons, and a digital display.
- **Responsive layout** — designed to provide a usable experience across different screen sizes.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Calculation logic and backend processing |
| Flask | Web application and backend routes |
| HTML5 | Page structure |
| CSS3 | Styling and responsive interface |
| JavaScript | Interactive calculator controls |

## 📂 Project Structure

```text
scientific_calculator/
│
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
│
└── templates/
    └── index.html
```

## 🚀 Getting Started

Follow these instructions to run the project locally.

### Prerequisites

- Python 3.10 or later recommended
- pip (Python package installer)
- Git (optional, for cloning the repository)

### 1. Clone the Repository

```bash
git clone https://github.com/omsaibhalekar2808/Scientific-Calculator.git
```

### 2. Open the Project Directory

```bash
cd Scientific-Calculator
```

### 3. Create a Virtual Environment

**Windows:**

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If you use Command Prompt instead of PowerShell:

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

Open your browser and visit:

http://127.0.0.1:5000

The calculator should now be available on your local machine.

## 🧪 Example Calculations

| Operation | Example | Expected result |
|---|---|---|
| Addition | `25 + 15` | `40` |
| Square root | `sqrt(144)` | `12` |
| Power | `2^5` | `32` |
| Trigonometry | `sin(30)` in degree mode | `0.5` |
| Factorial | `5!` | `120` |
| Logarithm | `log(100)` | `2` |

*Results depend on the selected angle mode and calculator settings where applicable.*

## 🔐 Security Notes

- Keep Flask debug mode disabled when running in any environment accessible to other users.
- Do not commit passwords, API keys, access tokens, or other private credentials.
- Review input validation and computational limits before deploying the application publicly.
- Use an appropriate production WSGI server and deployment configuration for public hosting.

## 🔮 Future Improvements

- Add calculation history with persistent storage.
- Add unit conversion tools.
- Improve keyboard navigation and accessibility.
- Add automated tests for mathematical functions and error handling.
- Deploy the calculator to a public hosting platform.

## 👨‍💻 Author

**Omsai Bhalekar**

GitHub: [@omsaibhalekar2808](https://github.com/omsaibhalekar2808)

## 📄 License

No license has been specified yet. Add a license file if you decide to permit others to reuse, modify, or distribute this project.

---

⭐ If you find this project interesting, consider starring the repository!