# 🧠 NeuraPython — Unified Scientific and AI Python Framework

**Author:** Ibrahim Shahid  
**Version:** 1.1.0  
**License:** MIT  

---

## 📘 Overview

**NeuraPython** is a powerful, all-in-one Python module that integrates *Artificial Intelligence, Machine Learning, Physics, Chemistry, Mathematics, Databases, Media Handling, Web Servers, Speech Recognition,* and much more — all inside one unified framework.  
It is designed for developers, data scientists, educators, and researchers who want a single tool for advanced computation, visualization, automation, and AI integration.

---

## 🚀 Key Features

| Category | Description |
|-----------|-------------|
| **Artificial Intelligence** | Access Google Gemini and OpenAI GPT APIs directly. |
| **Machine Learning** | Unified wrapper over Scikit-Learn: data preprocessing, model training, evaluation, and persistence. |
| **Neural Networks** | Dual backend (PyTorch & TensorFlow) with a universal API for model creation and training. |
| **Mathematics** | Advanced arithmetic, algebra, probability, and calculus using symbolic math. |
| **Physics** | Complete suite for classical, relativistic, and quantum physics equations and constants. |
| **Chemistry** | Periodic table, atomic data lookup, and molecular computation. |
| **Database** | Simplified SQLite3 interface with auto schema creation and CRUD support. |
| **Web Development** | Built-in Flask-powered server for quick web apps and JSON APIs. |
| **Speech & Media** | Text-to-speech, voice recognition, and media (image, audio, video) handling. |
| **Visualization** | 2D and 3D graphing powered by Matplotlib. |
| **File Conversion** | Convert between PDF, DOCX, Excel, JSON, CSV, and Markdown/HTML seamlessly. |
| **QR Codes** | Generate and decode QR codes easily. |
| **Readers** | Built-in file readers for multiple formats: PDF, DOCX, JSON, HTML, XML, CSV, etc. |

---

## 🧩 Installation

> Requires **Python 3.9+**

Install from PyPI:

```bash
pip install neurapython
```

Upgrade if already installed:
```bash
pip install --upgrade neurapython
```

Then import the module:
```python
from neurapython import *
```

---

## 🧠 Example Usage

### 🧩 Machine Learning
```python
ml = NeuraPython_ML()
X, y = ml.load_builtin_dataset("iris")
X_train, X_test, y_train, y_test = ml.split(X, y)

ml.create_model("random_forest")
ml.train("random_forest", X_train, y_train)
pred = ml.predict("random_forest", X_test)
print(ml.evaluate(y_test, pred))
```

### 🔬 Neural Network
```python
nn = NeuralNetwork(backend='torch')
nn.Sequential([4, 8, 3])
nn.compile()
nn.fit([[0.1, 0.2, 0.3, 0.4]], [[1, 0, 0]], epochs=3)
```

### ⚛️ Physics
```python
phy = Physics()
print(phy.mass_energy_equivalence(0.001))  # E = mc²
```

### ⚗️ Chemistry
```python
chem = Chemistry()
print(chem._elements[0])  # Hydrogen info
```

### 📊 Visualization
```python
viz = Visualizer2D(["A","B","C"], [10,20,15], title="Example Bar Graph")
viz.bar_graph()
viz.show()
```

### 🔈 Speech & Media
```python
speak("Hello, this is NeuraPython in action!")
text = voice_input("Say something:")
print("You said:", text)
```

### 🧮 Calculus
```python
calc = Calculus()
print(calc.derivative("x**2 + 3*x", "x"))
```

---

## 🧱 Module Structure

```
neurapython/
│
├── AI                    # API access (ChatGPT, Gemini)
├── Advanced_Maths        # Arithmetic, algebra, statistics
├── Calculus              # Symbolic calculus and differentiation
├── Chemistry             # Periodic table and constants
├── Converter             # File format converters
├── Database              # SQLite handler
├── Media                 # Audio, video, and image tools
├── Matrices, Vectors     # Linear algebra utilities
├── NeuraPython_ML        # Scikit-learn unified wrapper
├── NeuralNetwork         # TensorFlow / PyTorch integration
├── Physics               # Mechanics, relativity, quantum
├── Reader                # File readers (txt, pdf, json, etc.)
├── Visualizer2D / 3D     # Graph plotting
├── WebServer             # Flask API server
└── QR_Code               # Generate and read QR codes
```

---

## ⚙️ Requirements

- `torch`
- `tensorflow`
- `scikit-learn`
- `flask`
- `pyttsx3`
- `speechrecognition`
- `pygame`
- `opencv-python`
- `pandas`
- `numpy`
- `matplotlib`
- `sympy`
- `pdfplumber`
- `docx2pdf`
- `pdf2docx`
- `markdown`
- `fpdf`
- `joblib`
- `requests`
- `bs4`

Install dependencies manually (if needed):
```bash
pip install neurapython
```

---

## 📚 Additional Information

- Fully modular — import only what you need.  
- Cross-platform (Windows, macOS, Linux).  
- Integrated TensorFlow and PyTorch support.  
- Built-in physics constants and quantum utilities.  
- File conversion utilities for automation workflows.  
- Speech and multimedia integration for interactive projects.  
- Database and web utilities for backend development.  

---

## 🧠 Author

**Ibrahim Shahid**  
📧 Email: *ibrahimshahid7767@gmail.com*   

---

## ⚖️ License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute with proper credit.

---

## 🌟 Contribution

Contributions are welcome!  
1. Fork this repository  
2. Create your branch (`git checkout -b feature/YourFeature`)  
3. Commit changes (`git commit -m "Add new feature"`)  
4. Push (`git push origin feature/YourFeature`)  
5. Open a Pull Request  

---

## 🧩 Future Enhancements

- Web-based dashboard for AI/ML models  
- Extended NLP and Vision utilities  
- Integrated scientific simulator  

---

## 💬 Credits

Developed with ❤️ by **Ibrahim Shahid**  
Powered by: TensorFlow · PyTorch · Flask · Scikit-learn · SymPy · Pandas · NumPy · OpenCV · Matplotlib and more.

---
