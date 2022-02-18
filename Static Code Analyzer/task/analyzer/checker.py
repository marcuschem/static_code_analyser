import ast
import os
import re
from my_helpers import my_tree_input, dict_of_nodes, lines_as_str


class StyleChecker:

    def __init__(self, base_path, base):
        self.base_path = base_path
        self.node_dict = dict_of_nodes(my_tree_input(base_path))
        self.work_dict = {}
        self.work_dict_str = lines_as_str(base_path)
        self.total_check(base)

    def total_check(self, base):
        self.work_dict = self.adding_lines()
        for key, node in self.work_dict_str.items():
            self.s001(base, key, node)
            self.s002(base, key, node)
            self.s003(base, key, node)
            self.s004(base, key, node)
            self.s005(base, key, node)
            self.s006(base, key)
            self.s007(base, key, node)
            self.s008(base, key, node)
            self.s009(base, key, node)
            if key in self.node_dict:
                self.s010(base, key, self.node_dict[key])
                self.s011(base, self.node_dict[key])
                self.s012(base, key, self.node_dict[key])

    def adding_lines(self):
        dict_lines = {}
        for key, node in self.node_dict.items():
            dict_lines[key] = ast.unparse(node)
        return dict_lines

    @staticmethod
    def s001(base, key, line, max_length=79):
        if len(line) > max_length:
            print(f"{base}: line {key}: S001 Too long")
        return None

    @staticmethod
    def s002(base, key, line):
        if line != "":
            symbol = line[0]
            count_space = 0
            while symbol == ' ':
                count_space += 1
                symbol = line[count_space]
            if count_space % 4 != 0:
                print(f"{base}: line {key}: S002 Indentation is not a multiple of four")
        return None

    @staticmethod
    def s003(base, key, line):
        regex1 = re.compile(r"(.*)((;(\s)*#)|(;$))")
        regex2 = re.compile("#.*;")
        if regex1.search(line) and not regex2.search(line):
            print(f"{base}: line {key}: S003 Unnecessary semicolon")
        return None

    @staticmethod
    def s004(base, key, line):
        comment = line.find('#')
        if comment > 0 and (line[comment - 1] != ' ' or line[comment - 2] != ' '):
            print(f"{base}: line {key}: S004 At least two spaces required before inline comments")
        return None

    @staticmethod
    def s005(base, key, line):
        regex = re.compile("#(.*)todo", flags=re.IGNORECASE)
        if regex.search(line):
            print(f"{base}: line {key}: S005 TODO found")
        return None

    def s006(self, base, key):
        list_keys = self.node_dict.keys()
        list_ancestral_keys = []
        for keys in list_keys:
            if keys < key - 3:
                list_ancestral_keys.append(keys)
        if list_ancestral_keys:
            studied_key = list_ancestral_keys[-1]
            if key - 1 not in self.node_dict and key - 2 not in self.node_dict and key - 3 not in self.node_dict:
                if not isinstance(self.node_dict[studied_key], (ast.FunctionDef, ast.ClassDef)):
                    print(f"{base}: line {key}: S006 More than two blank lines used before this line")
        return None

    @staticmethod
    def s007(base, key, line):
        result = re.match(r"( {4})?(class|def)( {2})+[\w]", line)
        if result:
            print(f"{base}: line {key}: S007 Too many spaces after '{result.groups(2)[1]}'")
        return None

    @staticmethod
    def s008(base, key, line):
        result = re.match(r"class[ ]+([a-z]+[0-9]*_?[a-z0-9]+_?[a-z0-9]*)", line)
        if result:
            print(f"{base}: line {key}: S008 Class name '{result.groups(1)[0]}' should use CamelCase")

    @staticmethod
    def s009(base, key, line):
        result = re.match(r"[ ]*def[ ]+([A-Z][a-z0-9]*[A-Z]*[a-z0-9]*[A-Z]*[a-z0-9]*)", line)
        if result:
            print(f"{base}: line {key}: S009 Function name '{result.groups(1)[0]}' should use snake_case")

    @staticmethod
    def s010(base, key, node):
        if isinstance(node, ast.FunctionDef):
            arguments = [argument.arg for argument in node.args.args]
            for alias in arguments:
                if re.match(r"([A-Z][a-z0-9]*[A-Z]*[a-z0-9]*[A-Z]*[a-z0-9]*)", alias):
                    print(f"{base}: line {key}: S010 Argument name {alias} should be written in snake_case")
        if isinstance(node, ast.ClassDef):
            for nodes in node.body:
                if isinstance(nodes, (ast.FunctionType, ast.AsyncFunctionDef, ast.FunctionDef, ast.GeneratorExp)):
                    arguments = [argument.arg for argument in nodes.args.args]
                    for alias in arguments:
                        if re.match(r"([A-Z][a-z0-9]*[A-Z]*[a-z0-9]*[A-Z]*[a-z0-9]*)", alias):
                            print(f"{base}: line {nodes.lineno}: S010 Argument name '{alias}' should be written in snake_case")

    def s011(self, base, node):
        if isinstance(node, ast.Assign):
            result = re.match(r"([a-z]+[0-9]*_?[a-z0-9]+_?[a-z0-9]*)", ast.unparse(node.targets))
            if not result:
                print(f"{base}: line {node.lineno}: S011 Variable name '{ast.unparse(node.targets)}' should be written in snake_case")
        if isinstance(node, ast.FunctionDef):
            for sub_nodes in node.body:
                self.s011(base, sub_nodes)
        if isinstance(node, ast.ClassDef):
            for sub_nodes in node.body:
                self.s011(base, sub_nodes)

    def s012(self, base, key, node):
        if isinstance(node, ast.FunctionDef):
            arguments = [argument for argument in node.args.args]
            for parameter in arguments:
                if isinstance(parameter, ast.List):
                    print(f"{base}: line {key}: S012 Default argument value is mutable")
        if isinstance(node, ast.ClassDef):
            for nodes in node.body:
                if isinstance(nodes, ast.FunctionDef):
                    arguments = [parameter for parameter in nodes.args.defaults]
                    for alias in arguments:
                        if isinstance(alias, ast.List):
                            print(f"{base}: line {nodes.lineno}: S012 Default argument value is mutable")


def static_analyzer(base_path):
    base = os.path.join(os.getcwd(), base_path)
    if os.path.isfile(base):
        StyleChecker(base, base_path)
    elif os.path.isdir(base):
        for entry in os.listdir(base):
            output = os.path.join(base, entry)
            if os.path.isfile(output):
                StyleChecker(output, output)
    return None









