import ast
import sys
import graphviz
import itertools
import os

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

def main():
    if len(sys.argv) < 4:
        print("Usage: python script.py input_file.py [focus_class1 focus_class2 ...]")
        print("Provide at least 2 focus classes to compare.")
        return
    input_file = sys.argv[1]
    focus_classes = sys.argv[2:]  # Classes to be highlighted
    with open(input_file, 'r') as f:
        source = f.read()
    tree = ast.parse(source)
    extractor = HierarchyExtractor()
    extractor.visit(tree)
    classes = extractor.classes

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
                focus_methods[class_name] = classes[class_name]['methods']
                focus_variables[class_name] = classes[class_name]['variables']
            else:
                print(f"Warning: Focus class '{class_name}' not found in the input file.")

        # Find shared methods and variables among all combinations
        all_focus_methods = {}
        all_focus_variables = {}
        # Generate combinations of focus classes
        for r in range(2, len(focus_classes)+1):
            for combo in itertools.combinations(focus_classes, r):
                common_methods = set.intersection(*(focus_methods[c] for c in combo))
                if common_methods:
                    all_focus_methods[combo] = common_methods
                common_variables = set.intersection(*(focus_variables[c] for c in combo))
                if common_variables:
                    all_focus_variables[combo] = common_variables

        # Unique methods and variables for each focus class
        unique_methods = {}
        unique_variables = {}
        for class_name in focus_classes:
            methods_in_other_classes = set.union(*(focus_methods[c] for c in focus_classes if c != class_name))
            variables_in_other_classes = set.union(*(focus_variables[c] for c in focus_classes if c != class_name))
            unique_methods[class_name] = focus_methods[class_name] - methods_in_other_classes
            unique_variables[class_name] = focus_variables[class_name] - variables_in_other_classes

    # Define color palette
    color_palette = ['palegoldenrod', 'lightgreen', 'lightpink', 'lightcyan', 'lavender', 'lightcoral', 'aquamarine']
    sharing_colors = {}
    combo_to_color = {}
    color_index = 0

    # Generate enhanced visualization (same as before)
   # Generate enhanced visualization
    dot = graphviz.Digraph(comment='Class Hierarchy Enhanced')
    dot.attr(rankdir='TB')  # Top to bottom layout

    # Define colors
    focus_color = 'lightblue'
    non_focus_color = 'lightgray'
    inheritance_edge_color = 'black'

    # Assign colors for different levels of sharing
    color_palette = ['lightyellow', 'lightgreen', 'lightpink', 'lightcyan', 'lavender']
    sharing_colors = {}

    # Create subgraphs for layout
    with dot.subgraph(name='cluster_focus') as focus_cluster:
        focus_cluster.attr(rank='same', label='Focus Classes', color='blue')
        for class_name in focus_classes:
            if class_name in classes:
                class_info = classes[class_name]
                # Build the label
                label = f"<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0'>"
                label += f"<TR><TD BGCOLOR='lightblue'><B>{class_name}</B></TD></TR>"

                if class_info['bases']:
                    bases = ', '.join(class_info['bases'])
                    label += f"<TR><TD><I>Bases: {bases}</I></TD></TR>"

                # Shared Methods
                for combo, methods in all_focus_methods.items():
                    if class_name in combo:
                        shared_method_set = methods
                        combo_name = ', '.join(combo)
                        if len(combo) == len(focus_classes):
                            section_title = f"Methods shared among all focus classes"
                            bgcolor = 'palegoldenrod'
                        else:
                            if combo not in sharing_colors:
                                sharing_colors[combo] = color_palette[len(sharing_colors) % len(color_palette)]
                            bgcolor = sharing_colors[combo]
                            section_title = f"Methods shared among: {combo_name}"
                        label += f"<TR><TD BGCOLOR='{bgcolor}'><U>{section_title}</U></TD></TR>"
                        for method in sorted(shared_method_set):
                            label += f"<TR><TD BGCOLOR='{bgcolor}'>{method}</TD></TR>"
                        # Remove methods from unique_methods
                        unique_methods[class_name] -= shared_method_set

                # Unique Methods
                if unique_methods[class_name]:
                    label += f"<TR><TD BGCOLOR='white'><U>Unique Methods</U></TD></TR>"
                    for method in sorted(unique_methods[class_name]):
                        label += f"<TR><TD>{method}</TD></TR>"

                # Shared Variables
                for combo, variables in all_focus_variables.items():
                    if class_name in combo:
                        shared_variable_set = variables
                        combo_name = ', '.join(combo)
                        if len(combo) == len(focus_classes):
                            section_title = f"Variables shared among all focus classes"
                            bgcolor = 'palegoldenrod'
                        else:
                            if combo not in sharing_colors:
                                sharing_colors[combo] = color_palette[len(sharing_colors) % len(color_palette)]
                            bgcolor = sharing_colors[combo]
                            section_title = f"Variables shared among: {combo_name}"
                        label += f"<TR><TD BGCOLOR='{bgcolor}'><U>{section_title}</U></TD></TR>"
                        for var in sorted(shared_variable_set):
                            label += f"<TR><TD BGCOLOR='{bgcolor}'>{var}</TD></TR>"
                        # Remove variables from unique_variables
                        unique_variables[class_name] -= shared_variable_set

                # Unique Variables
                if unique_variables[class_name]:
                    label += f"<TR><TD BGCOLOR='white'><U>Unique Variables</U></TD></TR>"
                    for var in sorted(unique_variables[class_name]):
                        label += f"<TR><TD>{var}</TD></TR>"

                label += "</TABLE>>"
                focus_cluster.node(class_name, label=label, shape='plaintext')

    # Non-focus classes
    with dot.subgraph(name='cluster_non_focus') as non_focus_cluster:
        non_focus_cluster.attr(rank='same', label='Other Classes', color='gray')
        for class_name, class_info in classes.items():
            if class_name in focus_classes:
                continue
            # Build the label
            label = f"<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0'>"
            label += f"<TR><TD BGCOLOR='lightgray'><B>{class_name}</B></TD></TR>"

            if class_info['bases']:
                bases = ', '.join(class_info['bases'])
                label += f"<TR><TD><I>Bases: {bases}</I></TD></TR>"

            # Methods
            if class_info['methods']:
                label += f"<TR><TD><U>Methods</U></TD></TR>"
                for method in sorted(class_info['methods']):
                    label += f"<TR><TD>{method}</TD></TR>"

            # Variables
            if class_info['variables']:
                label += f"<TR><TD><U>Variables</U></TD></TR>"
                for var in sorted(class_info['variables']):
                    label += f"<TR><TD>{var}</TD></TR>"

            label += "</TABLE>>"
            non_focus_cluster.node(class_name, label=label, shape='plaintext')

    # Add inheritance edges
    for class_name, class_info in classes.items():
        for base in class_info['bases']:
            if base in classes:
                dot.edge(base, class_name, label='inherits', color=inheritance_edge_color)

    # Adjust the rank of focus and non-focus clusters
    dot.body.append('{ rank=min; ' + '; '.join(focus_classes) + ' }')

    # Render the enhanced graph to a file
    dot.render('class_hierarchy_enhanced.gv', view=False)

    # Generate original visualization with adjusted layout and coloring
  

    dot_original = graphviz.Digraph(comment='Class Hierarchy Original')
    dot_original.attr(rankdir='TB')  # Top to bottom layout

    # Define colors
    focus_class_color = 'lightblue'
    unique_method_color = 'white'
    unique_variable_color = 'white'

    # Assign colors for different levels of sharing
    for combo in all_focus_methods.keys() | all_focus_variables.keys():
        if combo not in sharing_colors:
            sharing_colors[combo] = color_palette[color_index % len(color_palette)]
            color_index += 1

    # Add focus class nodes
    for class_name in focus_classes:
        if class_name in classes:
            color = focus_class_color
            dot_original.node(class_name, shape='box', style='filled', fillcolor=color)
        else:
            continue

    # Add shared method nodes
    added_methods = set()
    for combo, methods in all_focus_methods.items():
        color = sharing_colors[combo]
        for method in methods:
            if method not in added_methods:
                dot_original.node(method, shape='ellipse', style='filled', fillcolor=color)
                added_methods.add(method)
            for class_name in combo:
                dot_original.edge(class_name, method)
    # Add unique method nodes
    for class_name in focus_classes:
        for method in unique_methods[class_name]:
            method_node = f"{method}_{class_name}"
            dot_original.node(method_node, shape='ellipse', style='filled', fillcolor=unique_method_color)
            dot_original.edge(class_name, method_node)

    # Add shared variable nodes
    added_variables = set()
    for combo, variables in all_focus_variables.items():
        color = sharing_colors[combo]
        for var in variables:
            if var not in added_variables:
                dot_original.node(var, shape='diamond', style='filled', fillcolor=color)
                added_variables.add(var)
            for class_name in combo:
                dot_original.edge(class_name, var)
    # Add unique variable nodes
    for class_name in focus_classes:
        for var in unique_variables[class_name]:
            var_node = f"{var}_{class_name}"
            dot_original.node(var_node, shape='diamond', style='filled', fillcolor=unique_variable_color)
            dot_original.edge(class_name, var_node)

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

    # Render the original graph to a file
    dot_original.render('class_hierarchy_original.gv', view=False)

    # Inform the user about the generated files
    print("Generated 'class_hierarchy_original.gv.pdf' with the adjusted original visualization.")

    # Automatically open the original visualization
    if sys.platform == 'win32':
        os.startfile('class_hierarchy_original.gv.pdf')
    else:
        os.system('open class_hierarchy_original.gv.pdf')

if __name__ == '__main__':
    main()
