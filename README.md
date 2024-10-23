```markdown
# Vispy

[![PyPI version](https://badge.fury.io/py/vispy.svg)](https://badge.fury.io/py/vispy)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/vispy.svg?style=social&label=Stars)](https://github.com/yourusername/vispy)

**Vispy** is a Python package that analyzes class hierarchies in Python files, extracts methods and variables, identifies shared elements among classes, and generates visualizations to help developers understand their code structure.

## Installation

### Using Conda

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/vispy.git
   cd vispy
   ```

2. **Create and Activate a Conda Environment:**

   ```bash
   conda create -n vispy_env python=3.8
   conda activate vispy_env
   ```

3. **Install Dependencies:**

   ```bash
   conda install graphviz
   pip install graphviz
   ```

4. **Install the Package:**

   ```bash
   pip install -e .
   ```

### Using Pip

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/vispy.git
   cd vispy
   ```

2. **Create and Activate a Virtual Environment:**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install Dependencies:**

   Download and install Graphviz from [Graphviz Download](https://graphviz.org/download/), then:

   ```bash
   pip install graphviz
   ```

4. **Install the Package:**

   ```bash
   pip install -e .
   ```

## Usage

### Command-Line Interface

Analyze a Python file and generate visualizations:

```bash
vispy <input_file.py> [focus_class1 focus_class2 ...]
```

- `<input_file.py>`: Path to the Python file.
- `[focus_class1 focus_class2 ...]`: (Optional) Classes to focus on in the visualization.

**Example:**

```bash
vispy examples/sample_input.py ClassA ClassB
```

### As a Python Module

Use Vispy within your scripts:

```python
from vispy.analyzer import parse_file
from vispy.visualizer import generate_visualizations

# Parse the Python file
classes = parse_file('examples/sample_input.py')

# Define focus classes
focus_classes = ['ClassA', 'ClassB']

# Generate visualizations
generate_visualizations(classes, focus_classes)
```

## Examples

### Sample Input (`examples/sample_input.py`)

```python
class ClassA:
    def method_shared_all(self):
        pass

    def method_shared_ab(self):
        pass

    def method_unique_a(self):
        pass

    def __init__(self):
        self.var_shared_all = 1
        self.var_shared_ab = 2
        self.var_unique_a = 3

class ClassB:
    def method_shared_all(self):
        pass

    def method_shared_ab(self):
        pass

    def method_unique_b(self):
        pass

    def __init__(self):
        self.var_shared_all = 1
        self.var_shared_ab = 2
        self.var_unique_b = 4

class ClassC:
    def method_shared_all(self):
        pass

    def method_unique_c(self):
        pass

    def __init__(self):
        self.var_shared_all = 1
        self.var_unique_c = 5
```

### Running the Analyzer

```bash
vispy examples/sample_input.py ClassA ClassB ClassC
```

This generates two PDFs:
- `class_hierarchy_enhanced.gv.pdf`
- `class_hierarchy_original.gv.pdf`

## Contributing

Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

- **Author:** Luke Friedrichs
- **Email:** [lukefriedrichs@gmail.com](mailto:lukefriedrichs@gmail.com)
- **GitHub:** [LckyLke](https://github.com/lckylke)
