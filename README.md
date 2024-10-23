# Vispy

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Vispy** is a Python package that analyzes class hierarchies in Python files, extracts methods and variables, identifies shared elements among classes (including inherited ones), and generates visualizations to help developers understand their code structure more effectively.

## Installation

### Using Conda

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/lckylke/vispy.git
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
   git clone https://github.com/lckylke/vispy.git
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

Analyze Python files and generate visualizations:

```bash
vispy --files <input_file1.py> <input_file2.py> ... --focus <ClassA> <ClassB> [<ClassC> ...] [--include-inherited]
```

- `--files` or `-f`: **(Required)** List of Python files to analyze.
- `--focus` or `-c`: **(Required)** List of classes to focus on in the visualization (at least 2).
- `--include-inherited` or `-i`: **(Optional)** Include inherited methods and variables in the analysis.

**Example:**

```bash
vispy --files examples/sample_input.py --focus ClassA ClassB --include-inherited
```

This command analyzes `sample_input.py`, focuses on `ClassA` and `ClassB`, includes inherited methods and variables, and generates enhanced and original visualizations.

### As a Python Module

Use Vispy within your scripts to programmatically analyze classes and generate visualizations:

```python
from vispy.analyzer import parse_files
from vispy.visualizer import generate_visualizations

# Parse the Python files
classes = parse_files(['examples/sample_input.py'])

# Define focus classes
focus_classes = ['ClassA', 'ClassB']

# Generate visualizations
generate_visualizations(classes, focus_classes, include_inherited=True)
```

## Features

- **Class Hierarchy Analysis:** Parses Python files to extract class definitions, their methods, variables, and inheritance relationships.
- **Inherited Elements Handling:** When enabled, inherited methods and variables are treated as if they belong to the focus classes, allowing for comprehensive analysis.
- **Shared Elements Identification:** Identifies methods and variables shared among multiple focus classes, including those inherited from superclasses.
- **Consistent Coloring:** Applies consistent color coding to shared methods and variables across focus classes, enhancing the clarity of visualizations.
- **Enhanced Visualization:** Generates detailed class tables with color-coded sections indicating shared and unique methods/variables.
- **Original Visualization:** Produces standard class hierarchy diagrams with clear inheritance links and method/variable associations.

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
vispy --files examples/sample_input.py --focus ClassA ClassB --include-inherited
```

This command generates two PDFs:

- `class_hierarchy_enhanced.gv.pdf`: Enhanced visualization with color-coded shared and unique methods/variables. Shared methods like `method_shared_all` and `method_shared_ab` are colored consistently across `ClassA` and `ClassB`.
- `class_hierarchy_original.gv.pdf`: Original visualization with standard connections, showing inheritance and method/variable associations.

## Visualization Details

### Enhanced Visualization (`class_hierarchy_enhanced.gv.pdf`)

- **Focus Classes:** Highlighted with distinct colors.
- **Shared Methods/Variables:** Color-coded sections indicate methods and variables shared among specified focus classes. Consistent coloring across classes helps identify shared elements quickly.
- **Unique Methods/Variables:** Clearly separated to show elements unique to each focus class.
- **Inherited Elements:** When `--include-inherited` is used, inherited methods and variables are treated as if they belong to the focus classes, ensuring they are included in shared and unique analyses.

### Original Visualization (`class_hierarchy_original.gv.pdf`)

- **Class Boxes:** Represent classes with connections to their methods and variables.
- **Inheritance Arrows:** Clearly depict inheritance relationships between classes.
- **Method/Variable Nodes:** Differentiated by shape and color based on sharing and uniqueness.

## Contributing

Contributions are welcome! Please follow these steps:


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

- **Author:** Luke Friedrichs
- **Email:** [lukefriedrichs@gmail.com](mailto:lukefriedrichs@gmail.com)
- **GitHub:** [LckyLke](https://github.com/lckylke)
