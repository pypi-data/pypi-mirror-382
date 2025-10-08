
import ast,sys,inspect
from .visit_dot import DotASTVisitor

class LogTransformer(ast.NodeTransformer):
	
	def __init__(self, file=None, code=None):
		if file:
			f = open(file)
			self.code_snipet = f.read()
			f.close()
		elif code:
			self.code_snipet = code
		else:
			self.code_snippet = ''
			
		self.level = 0
		self.linhas = self.code_snipet.splitlines()
		self.tree = ast.parse(self.code_snipet)
		self.decisoes = {}
		self.textos = {}
		self.keep = -1
		self.mod = False
		

	def visit_BoolOp(self, node):
		newno = None
		if self.level == 0:
			self.linha = (node.lineno,node.col_offset)
			self.decisoes[self.linha] = []
			self.textos[self.linha] = self.to_src(node)
			self.keep = 0
			boolvalue = isinstance(node.op, ast.And)
			newno = ast.Call(
				func=ast.Name(id='init_bool_register', ctx=ast.Load()),
				args=[
					ast.Constant(value=self.linha[0]),
					ast.Constant(value=self.linha[1]),
					ast.Constant(value=boolvalue)
				],
				keywords=[]
			)
		k = 0
		self.mod = False
		for no in node.values:
			if no is newno:
				continue
			if not isinstance(no,ast.BoolOp):
				self.decisoes[self.linha].append(self.to_src(no))
				self.level += 1
				self.mod = True
				self.keep += 1
				new_no = self.visit(no)
				node.values[k] = new_no
				self.mod = False
				self.level -= 1
			else:
				self.level += 1
				self.visit(no)
				self.level -= 1
			if k != 0:
				self.decisoes[self.linha].append('*' if isinstance(node.op,ast.And) else '+')  
			k += 1
		if self.level == 0:
			node.values.insert(0,newno)

		return node

	def visit(self,node):
		if self.mod:
			no = ast.Call(
				func=ast.Name(id='bool_register', ctx=ast.Load()),
				args=[
					node,  # o próprio x
					ast.Constant(value=self.linha[0]),
					ast.Constant(value=self.linha[1]),
					ast.Constant(value=self.keep-1)
				],
				keywords=[]
			)
			return ast.copy_location(no, node)
		return super().visit(node)
	
	def to_src(self, node):
		l = node.lineno-1
		lf = node.end_lineno-1
		s = ''
		c = node.col_offset
		cf = node.end_col_offset
		while l <= lf:
			if l == lf:
				s += self.linhas[l][c:cf].strip()
			else:
				s += self.linhas[l][c:].strip()
			l += 1
			c = 0
		return s
			 
		return generated_code;

	def go_visit(self):
		self.visit(self.tree)

