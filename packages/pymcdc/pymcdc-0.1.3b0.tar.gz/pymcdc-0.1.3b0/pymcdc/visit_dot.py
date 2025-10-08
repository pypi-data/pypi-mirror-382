import ast

class DotASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.output = ["digraph ast {"]
        self.node_id = 0
        self.stack = []

    def _gen_id(self):
        self.node_id += 1
        return f"n{self.node_id}"

    def _format_label(self, node):
        # Começa com o nome da classe
        label = type(node).__name__

        # Enriquecer com informação relevante
        if isinstance(node, ast.Name):
            label += f'\\nid={node.id}'
        elif isinstance(node, ast.Constant):
            label += f'\\nvalue={repr(node.value)}'
        elif isinstance(node, ast.arg):
            label += f'\\narg={node.arg}'
        elif isinstance(node, ast.FunctionDef):
            label += f'\\nname={node.name}'
        elif isinstance(node, ast.ClassDef):
            label += f'\\nname={node.name}'
        elif isinstance(node, ast.Attribute):
            label += f'\\nattr={node.attr}'

        return label

    def visit(self, node):
        cur_id = self._gen_id()
        label = self._format_label(node)
        self.output.append(f'{cur_id} [label="{label}"];')

        if self.stack:
            parent_id = self.stack[-1]
            self.output.append(f"{parent_id} -> {cur_id};")

        self.stack.append(cur_id)
        super().visit(node)
        self.stack.pop()

    def get_dot(self):
        return "\n".join(self.output) + "\n}"

if __name__ == '__main__':

	f = open('1.py')
	codigo = f.read()
	f.close()

	arvore = ast.parse(codigo)
	visitor = DotASTVisitor()
	visitor.visit(arvore)
	dot_output = visitor.get_dot()

	f = open('3.dot', 'w')
	f.write(dot_output)
	f.close()
