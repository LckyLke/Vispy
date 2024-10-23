# visualizer.py

import ast
import sys
import graphviz
import itertools
import os
import argparse

class HierarchyExtractor(ast.NodeVisitor):
    def __init__(self):
        self.classes = {}  # class name -> class info

    def visit_ClassDef(self, node):
        class_info = {'methods': set(), 'variables': set(), 'bases': []}
        class_info['bases'] = [self.get_name(base) for base in node.bases]
        # methods and variables
        for body_item in node.body:
            if isinstance(body_item, ast.FunctionDef):
                # method
                method_name = body_item.name
                # Skip trivial methods like __init__
                if not (method_name.startswith('__') and method_name.endswith('__')):
                    class_info['methods'].add(method_name)
                    # process method body to find instance variables
                    self.process_method(body_item, class_info)
            elif isinstance(body_item, ast.Assign):
                # class variable
                for target in body_item.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        class_info['variables'].add(var_name)
                    elif isinstance(target, ast.Tuple):
                        # multiple assignment
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                var_name = elt.id
                                class_info['variables'].add(var_name)
            elif isinstance(body_item, ast.AnnAssign):
                # annotated class variable
                if isinstance(body_item.target, ast.Name):
                    var_name = body_item.target.id
                    class_info['variables'].add(var_name)
        self.classes[node.name] = class_info
        self.generic_visit(node)

    def process_method(self, node, class_info):
        # Process method body to find instance variables
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Attribute):
                        if (isinstance(target.value, ast.Name) and
                            target.value.id == 'self'):
                            # instance variable
                            var_name = target.attr
                            class_info['variables'].add(var_name)
            elif isinstance(stmt, ast.AnnAssign):
                # annotated assignment
                if (isinstance(stmt.target, ast.Attribute) and
                    isinstance(stmt.target.value, ast.Name) and
                    stmt.target.value.id == 'self'):
                    var_name = stmt.target.attr
                    class_info['variables'].add(var_name)

    def get_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self.get_name(node.value) + '.' + node.attr
        else:
            return None

def get_all_bases(class_name, classes, visited=None):
    """
    Recursively collect all base classes for a given class.

    Args:
        class_name (str): The name of the class.
        classes (dict): Dictionary containing class information.
        visited (set): Set of already visited classes to avoid infinite loops.

    Returns:
        set: A set of all base class names.
    """
    if visited is None:
        visited = set()
    bases = set()
    if class_name not in classes:
        return bases
    for base in classes[class_name]['bases']:
        if base and base not in visited:
            visited.add(base)
            bases.add(base)
            bases.update(get_all_bases(base, classes, visited))
    return bases

def collect_inherited_elements(class_name, classes):
    """
    Collect inherited methods and variables for a given class.

    Args:
        class_name (str): The name of the class.
        classes (dict): Dictionary containing class information.

    Returns:
        tuple: A tuple containing two sets (inherited_methods, inherited_variables).
    """
    inherited_methods = set()
    inherited_variables = set()
    base_classes = get_all_bases(class_name, classes)
    for base in base_classes:
        inherited_methods.update(classes.get(base, {}).get('methods', set()))
        inherited_variables.update(classes.get(base, {}).get('variables', set()))
    return inherited_methods, inherited_variables

def main():
    parser = argparse.ArgumentParser(description="Analyze Python class hierarchies and generate visualizations.")
    parser.add_argument(
        '--files', '-f',
        nargs='+',
        required=True,
        help='List of Python files to analyze.'
    )
    parser.add_argument(
        '--focus', '-c',
        nargs='*',
        default=[],
        help='Classes to focus on in the visualization.'
    )
    parser.add_argument(
        '--include-inherited', '-i',
        action='store_true',
        help='Include inherited methods and variables.'
    )
    
    args = parser.parse_args()
    
    input_files = args.files
    focus_classes = args.focus
    include_inherited = args.include_inherited

    # Extract class hierarchy from all input files
    classes = {}
    for input_file in input_files:
        try:
            with open(input_file, 'r') as f:
                source = f.read()
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found.")
            continue
        except Exception as e:
            print(f"Error reading '{input_file}': {e}")
            continue

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            print(f"Error parsing '{input_file}': {e}")
            continue

        extractor = HierarchyExtractor()
        extractor.visit(tree)
        classes.update(extractor.classes)
    
    if not classes:
        print("No classes found in the provided input files.")
        return

    # Write output to a text file
    with open('output.txt', 'w') as output_file:
        for class_name, class_info in classes.items():
            output_file.write(f"Class: {class_name}\n")
            if class_info['bases']:
                output_file.write(f"  Bases: {', '.join(class_info['bases'])}\n")
            output_file.write("  Methods:\n")
            for method in sorted(class_info['methods']):
                output_file.write(f"    {method}\n")
            output_file.write("  Variables:\n")
            for var_name in sorted(class_info['variables']):
                output_file.write(f"    {var_name}\n")
            output_file.write("\n")
    
    # Prepare data for focus classes
    focus_methods = {}
    focus_variables = {}
    if focus_classes:
        for class_name in focus_classes:
            if class_name in classes:
                methods = classes[class_name]['methods']
                variables = classes[class_name]['variables']
                if include_inherited:
                    inherited_methods, inherited_variables = collect_inherited_elements(class_name, classes)
                    methods = methods.union(inherited_methods)
                    variables = variables.union(inherited_variables)
                focus_methods[class_name] = methods
                focus_variables[class_name] = variables
            else:
                print(f"Warning: Focus class '{class_name}' not found in the input files.")
    
        if not focus_methods:
            print("No valid focus classes found. Exiting.")
            return
    
        # Find shared methods and variables among all combinations
        all_focus_methods = {}
        all_focus_variables = {}
        # Generate combinations of focus classes
        for r in range(2, len(focus_classes)+1):
            for combo in itertools.combinations(focus_classes, r):
                methods_sets = [focus_methods[c] for c in combo if c in focus_methods]
                variables_sets = [focus_variables[c] for c in combo if c in focus_variables]
                common_methods = set.intersection(*methods_sets) if methods_sets else set()
                common_variables = set.intersection(*variables_sets) if variables_sets else set()
                if common_methods:
                    all_focus_methods[combo] = common_methods
                if common_variables:
                    all_focus_variables[combo] = common_variables
    
        # Unique methods and variables for each focus class
        unique_methods = {}
        unique_variables = {}
        for class_name in focus_classes:
            methods_in_other_classes = set()
            variables_in_other_classes = set()
            for other in focus_classes:
                if other != class_name and other in focus_methods:
                    methods_in_other_classes.update(focus_methods[other])
                    variables_in_other_classes.update(focus_variables[other])
            unique_methods[class_name] = focus_methods[class_name] - methods_in_other_classes
            unique_variables[class_name] = focus_variables[class_name] - variables_in_other_classes
    
    # Generate enhanced visualization
    if focus_classes:
        generate_enhanced_visualization(classes, focus_classes, include_inherited)
    else:
        print("No focus classes provided. Visualization requires at least one focus class.")
    
    # Generate original visualization
    if focus_classes:
        generate_original_visualization(classes, focus_classes, include_inherited)
    else:
        print("No focus classes provided. Visualization requires at least one focus class.")

def generate_enhanced_visualization(classes, focus_classes, include_inherited=False, output_filename='class_hierarchy_enhanced.gv'):
    """
    Generates the enhanced visualization with color-coded sections in class tables,
    indicating shared and unique methods/variables among focus classes.

    Args:
        classes (dict): Dictionary containing class information.
        focus_classes (list): List of focus class names.
        include_inherited (bool): Whether to include inherited methods/variables.
        output_filename (str): The filename for the generated PDF.
    """
    # Define color palette
    color_palette = ['palegoldenrod', 'lightgreen', 'lightpink', 'lightcyan', 'lavender', 'lightcoral', 'aquamarine']
    sharing_colors = {}
    color_index = 0

    # Prepare combinations of focus classes
    all_focus_methods = {}
    all_focus_variables = {}
    for r in range(2, len(focus_classes)+1):
        for combo in itertools.combinations(focus_classes, r):
            methods_sets = [classes[c]['methods'] for c in combo if c in classes]
            variables_sets = [classes[c]['variables'] for c in combo if c in classes]
            if include_inherited:
                methods_sets = [methods_sets[i].union(collect_inherited_elements(c, classes)[0]) for i, c in enumerate(combo)]
                variables_sets = [variables_sets[i].union(collect_inherited_elements(c, classes)[1]) for i, c in enumerate(combo)]
            common_methods = set.intersection(*methods_sets) if methods_sets else set()
            common_variables = set.intersection(*variables_sets) if variables_sets else set()
            if common_methods:
                all_focus_methods[combo] = common_methods
            if common_variables:
                all_focus_variables[combo] = common_variables

    # Unique methods and variables per class
    unique_methods = {}
    unique_variables = {}
    for class_name in focus_classes:
        if class_name not in classes:
            unique_methods[class_name] = set()
            unique_variables[class_name] = set()
            continue
        other_classes = set(focus_classes) - {class_name}
        methods_in_other_classes = set()
        variables_in_other_classes = set()
        for other in other_classes:
            if other in classes:
                methods_in_other_classes.update(classes[other]['methods'])
                variables_in_other_classes.update(classes[other]['variables'])
                if include_inherited:
                    inherited_methods, inherited_variables = collect_inherited_elements(other, classes)
                    methods_in_other_classes.update(inherited_methods)
                    variables_in_other_classes.update(inherited_variables)
        if include_inherited:
            inherited_methods, inherited_variables = collect_inherited_elements(class_name, classes)
            unique_methods[class_name] = classes[class_name]['methods'].union(inherited_methods) - methods_in_other_classes
            unique_variables[class_name] = classes[class_name]['variables'].union(inherited_variables) - variables_in_other_classes
        else:
            unique_methods[class_name] = classes[class_name]['methods'] - methods_in_other_classes
            unique_variables[class_name] = classes[class_name]['variables'] - variables_in_other_classes

    # Assign colors to combinations
    for combo in all_focus_methods.keys() | all_focus_variables.keys():
        if combo not in sharing_colors:
            sharing_colors[combo] = color_palette[color_index % len(color_palette)]
            color_index += 1

    # Create Graphviz Digraph
    dot = graphviz.Digraph(comment='Class Hierarchy Enhanced', format='pdf')
    dot.attr(rankdir='TB')  # Top to Bottom

    # Create subgraph for focus classes
    with dot.subgraph(name='cluster_focus') as focus_cluster:
        focus_cluster.attr(label='Focus Classes', color='blue')
        focus_cluster.attr(style='filled', color='lightgrey')
        for class_name in focus_classes:
            if class_name not in classes:
                continue
            class_info = classes[class_name]
            if include_inherited:
                inherited_methods, inherited_variables = collect_inherited_elements(class_name, classes)
                methods = class_info['methods'].union(inherited_methods)
                variables = class_info['variables'].union(inherited_variables)
            else:
                methods = class_info['methods']
                variables = class_info['variables']
            label = f"<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0'>"
            label += f"<TR><TD BGCOLOR='lightblue'><B>{class_name}</B></TD></TR>"
            if class_info['bases']:
                bases = ', '.join(class_info['bases'])
                label += f"<TR><TD><I>Bases: {bases}</I></TD></TR>"

            # Shared Methods
            for combo, methods_shared in all_focus_methods.items():
                if class_name in combo:
                    color = sharing_colors.get(combo, 'white')
                    combo_name = ', '.join(combo)
                    if len(combo) == len(focus_classes):
                        section_title = "Methods shared among all focus classes"
                    else:
                        section_title = f"Methods shared among: {combo_name}"
                    label += f"<TR><TD BGCOLOR='{color}'><U>{section_title}</U></TD></TR>"
                    for method in sorted(methods_shared):
                        label += f"<TR><TD BGCOLOR='{color}'>{method}</TD></TR>"

            # Unique Methods
            if unique_methods.get(class_name):
                label += f"<TR><TD BGCOLOR='white'><U>Unique Methods</U></TD></TR>"
                for method in sorted(unique_methods[class_name]):
                    label += f"<TR><TD BGCOLOR='white'>{method}</TD></TR>"

            # Shared Variables
            for combo, variables_shared in all_focus_variables.items():
                if class_name in combo:
                    color = sharing_colors.get(combo, 'white')
                    combo_name = ', '.join(combo)
                    if len(combo) == len(focus_classes):
                        section_title = "Variables shared among all focus classes"
                    else:
                        section_title = f"Variables shared among: {combo_name}"
                    label += f"<TR><TD BGCOLOR='{color}'><U>{section_title}</U></TD></TR>"
                    for var in sorted(variables_shared):
                        label += f"<TR><TD BGCOLOR='{color}'>{var}</TD></TR>"

            # Unique Variables
            if unique_variables.get(class_name):
                label += f"<TR><TD BGCOLOR='white'><U>Unique Variables</U></TD></TR>"
                for var in sorted(unique_variables[class_name]):
                    label += f"<TR><TD BGCOLOR='white'>{var}</TD></TR>"

            label += "</TABLE>>"
            focus_cluster.node(class_name, label=label, shape='plaintext')

    # Create subgraph for other classes
    with dot.subgraph(name='cluster_non_focus') as non_focus_cluster:
        non_focus_cluster.attr(label='Other Classes', color='grey')
        non_focus_cluster.attr(style='filled', color='white')
        for class_name, class_info in classes.items():
            if class_name in focus_classes:
                continue
            label = f"<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0'>"
            label += f"<TR><TD BGCOLOR='lightgrey'><B>{class_name}</B></TD></TR>"
            if class_info['bases']:
                bases = ', '.join(class_info['bases'])
                label += f"<TR><TD><I>Bases: {bases}</I></TD></TR>"

            # Methods
            if class_info['methods']:
                label += f"<TR><TD BGCOLOR='white'><U>Methods</U></TD></TR>"
                for method in sorted(class_info['methods']):
                    label += f"<TR><TD>{method}</TD></TR>"

            # Variables
            if class_info['variables']:
                label += f"<TR><TD BGCOLOR='white'><U>Variables</U></TD></TR>"
                for var in sorted(class_info['variables']):
                    label += f"<TR><TD>{var}</TD></TR>"

            label += "</TABLE>>"
            non_focus_cluster.node(class_name, label=label, shape='plaintext')

    # Add inheritance edges
    for class_name, class_info in classes.items():
        for base in class_info['bases']:
            if base and base in classes:
                dot.edge(base, class_name, label='inherits', color='black')

    # Render and save the enhanced visualization
    dot.render(output_filename, view=False)
    print(f"Enhanced visualization saved as '{output_filename}'.")

def generate_original_visualization(classes, focus_classes, include_inherited, output_filename='class_hierarchy_original.gv'):
    """
    Generates the original visualization with lines connecting classes to methods and variables.
    Shared methods/variables are colored differently and arranged vertically to reduce width.

    Args:
        classes (dict): Dictionary containing class information.
        focus_classes (list): List of focus class names.
        include_inherited (bool): Whether to include inherited methods/variables.
        output_filename (str): The filename for the generated PDF.
    """
    # Define color palette
    color_palette = ['palegoldenrod', 'lightgreen', 'lightpink', 'lightcyan', 'lavender', 'lightcoral', 'aquamarine']
    sharing_colors = {}
    color_index = 0

    # Prepare combinations of focus classes
    all_focus_methods = {}
    all_focus_variables = {}
    for r in range(2, len(focus_classes)+1):
        for combo in itertools.combinations(focus_classes, r):
            methods_sets = [classes[c]['methods'] for c in combo if c in classes]
            variables_sets = [classes[c]['variables'] for c in combo if c in classes]
            if include_inherited:
                methods_sets = [methods_sets[i].union(collect_inherited_elements(c, classes)[0]) for i, c in enumerate(combo)]
                variables_sets = [variables_sets[i].union(collect_inherited_elements(c, classes)[1]) for i, c in enumerate(combo)]
            common_methods = set.intersection(*methods_sets) if methods_sets else set()
            common_variables = set.intersection(*variables_sets) if variables_sets else set()
            if common_methods:
                all_focus_methods[combo] = common_methods
            if common_variables:
                all_focus_variables[combo] = common_variables

    # Unique methods and variables per class
    unique_methods = {}
    unique_variables = {}
    for class_name in focus_classes:
        if class_name not in classes:
            unique_methods[class_name] = set()
            unique_variables[class_name] = set()
            continue
        other_classes = set(focus_classes) - {class_name}
        methods_in_other_classes = set()
        variables_in_other_classes = set()
        for other in other_classes:
            if other in classes:
                methods_in_other_classes.update(classes[other]['methods'])
                variables_in_other_classes.update(classes[other]['variables'])
                if include_inherited:
                    inherited_methods, inherited_variables = collect_inherited_elements(other, classes)
                    methods_in_other_classes.update(inherited_methods)
                    variables_in_other_classes.update(inherited_variables)
        if include_inherited:
            inherited_methods, inherited_variables = collect_inherited_elements(class_name, classes)
            unique_methods[class_name] = classes[class_name]['methods'].union(inherited_methods) - methods_in_other_classes
            unique_variables[class_name] = classes[class_name]['variables'].union(inherited_variables) - variables_in_other_classes
        else:
            unique_methods[class_name] = classes[class_name]['methods'] - methods_in_other_classes
            unique_variables[class_name] = classes[class_name]['variables'] - variables_in_other_classes

    # Assign colors to combinations
    for combo in all_focus_methods.keys() | all_focus_variables.keys():
        if combo not in sharing_colors:
            sharing_colors[combo] = color_palette[color_index % len(color_palette)]
            color_index += 1

    # Create Graphviz Digraph
    dot_original = graphviz.Digraph(comment='Class Hierarchy Original', format='pdf')
    dot_original.attr(rankdir='TB')  # Top to Bottom

    # Define node styles
    focus_class_color = 'lightblue'
    unique_method_color = 'white'
    unique_variable_color = 'white'
    inherited_color = 'lightgreen'  # Color for inherited methods/variables

    # Add focus class nodes
    for class_name in focus_classes:
        if class_name in classes:
            dot_original.node(class_name, shape='box', style='filled', fillcolor=focus_class_color)
        else:
            continue

    # Collect shared methods and variables
    if include_inherited and focus_classes:
        shared_methods = set.intersection(*(classes[c]['methods'].union(collect_inherited_elements(c, classes)[0]) for c in focus_classes))
        shared_variables = set.intersection(*(classes[c]['variables'].union(collect_inherited_elements(c, classes)[1]) for c in focus_classes))
    else:
        shared_methods = set.intersection(*(classes[c]['methods'] for c in focus_classes)) if len(focus_classes) > 0 else set()
        shared_variables = set.intersection(*(classes[c]['variables'] for c in focus_classes)) if len(focus_classes) > 0 else set()

    # Add shared method nodes
    added_methods = set()
    for combo, methods in all_focus_methods.items():
        color = sharing_colors.get(combo, 'white')
        for method in methods:
            if method not in added_methods:
                node_color = color
                dot_original.node(method, shape='ellipse', style='filled', fillcolor=node_color)
                added_methods.add(method)
            for class_name in combo:
                # Determine if the method is inherited
                is_inherited = False
                if include_inherited and method not in classes[class_name]['methods']:
                    inherited_methods, _ = collect_inherited_elements(class_name, classes)
                    if method in inherited_methods:
                        is_inherited = True
                edge_color = 'green'
                pen_width = '2' if is_inherited else '1'
                dot_original.edge(class_name, method, color=edge_color, penwidth=pen_width)

    # Add unique method nodes
    for class_name in focus_classes:
        for method in unique_methods[class_name]:
            method_node = f"{method}_{class_name}"
            dot_original.node(method_node, shape='ellipse', style='filled', fillcolor=unique_method_color)
            dot_original.edge(class_name, method_node, color='black')

    # Add shared variable nodes
    added_variables = set()
    for combo, variables in all_focus_variables.items():
        color = sharing_colors.get(combo, 'white')
        for var in variables:
            if var not in added_variables:
                node_color = color
                dot_original.node(var, shape='diamond', style='filled', fillcolor=node_color)
                added_variables.add(var)
            for class_name in combo:
                # Determine if the variable is inherited
                is_inherited = False
                if include_inherited and var not in classes[class_name]['variables']:
                    _, inherited_variables = collect_inherited_elements(class_name, classes)
                    if var in inherited_variables:
                        is_inherited = True
                edge_color = 'blue'
                pen_width = '2' if is_inherited else '1'
                dot_original.edge(class_name, var, color=edge_color, penwidth=pen_width)

    # Add unique variable nodes
    for class_name in focus_classes:
        for var in unique_variables[class_name]:
            var_node = f"{var}_{class_name}"
            dot_original.node(var_node, shape='diamond', style='filled', fillcolor=unique_variable_color)
            dot_original.edge(class_name, var_node, color='black')

    # Arrange nodes to prevent wide graph
    # Group shared methods and variables
    with dot_original.subgraph() as s:
        s.attr(rank='same')
        for node in added_methods | added_variables:
            s.node(node)
    # Group unique methods and variables under their classes
    for class_name in focus_classes:
        with dot_original.subgraph() as s:
            s.attr(rank='same')
            for method in unique_methods[class_name]:
                method_node = f"{method}_{class_name}"
                s.node(method_node)
            for var in unique_variables[class_name]:
                var_node = f"{var}_{class_name}"
                s.node(var_node)

    # Add inheritance edges
    for class_name, class_info in classes.items():
        for base in class_info['bases']:
            if base and base in classes:
                dot_original.edge(base, class_name, label='inherits', color='black')

    # Render the original graph to a file
    dot_original.render(output_filename, view=False)
    print(f"Original visualization saved as '{output_filename}'.")

def generate_visualizations(classes, focus_classes, include_inherited=False):
    """
    Generates both enhanced and original visualizations based on class information.

    Args:
        classes (dict): Dictionary containing class information.
        focus_classes (list): List of focus class names.
        include_inherited (bool): Whether to include inherited methods/variables.
    """
    generate_enhanced_visualization(classes, focus_classes, include_inherited, 'class_hierarchy_enhanced.gv')
    generate_original_visualization(classes, focus_classes, include_inherited, 'class_hierarchy_original.gv')

if __name__ == "__main__":
    main()
