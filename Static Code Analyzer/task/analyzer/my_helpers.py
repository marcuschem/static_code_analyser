import ast


def my_tree_input(filename):
    with open(filename, "r") as file_in_analysis:
        tree = ast.parse(file_in_analysis.read())
    return tree


def dict_of_nodes(tree):
    dict_nodes = {}
    for node in list(ast.walk(tree))[0].body:
        dict_nodes[node.lineno] = node
    return dict_nodes


def lines_as_str(filename):
    dict_lines = {}
    with open(filename, "r") as studied_file:
        for key, line in enumerate(studied_file.readlines()):
            dict_lines[key + 1] = line
    return dict_lines




