from .visit_log import LogVisitor
from .transform_log import LogTransformer
import sys
from .decisao import Decisao
import argparse
import types
import ast
import shlex
import pickle
import unittest
import time
import os
import importlib.util


exec_decisoes = []
exec_linhas = []

def init_bool_register(linha, coluna, ret):
	#print('Iniciando {}'.format( (linha,coluna)))
	exec_decisoes.append({})
	exec_linhas.append((linha,coluna))
	return ret 


def bool_register(result, linha, coluna, condicao):
	#print('Decisao: {} Condição: {} Resultado: {}'.format((linha,coluna), condicao, result))
	lc = (linha,coluna)
	if lc != exec_linhas[-1]:
		raise ValueError('Numero de linha inesperado {}'.format(lc)) 
	r = 1 if result else 0
	dic = exec_decisoes[-1]
	dic[condicao] = r
	
	return result


def _to_module_name(key: str) -> str:
	# "dir/arquivo.py" -> "dir.arquivo"
	# "dir\\arquivo.py" (Windows) -> "dir.arquivo"
	# "arquivo.py" -> "arquivo"
	# "dir.arquivo" -> "dir.arquivo"
	if key.endswith(".py"):
		key = os.path.splitext(key)[0]
	key = key.replace(os.sep, ".")
	return key

def _ensure_module_hierarchy(module_name: str):
	parts = module_name.split(".")
	parent = None
	fullname = ""
	for part in parts[:-1]:
		fullname = f"{fullname}.{part}" if fullname else part
		if fullname in sys.modules:
			parent = sys.modules[fullname]
			continue
		# verifica se é um pacote real no disco
		if importlib.util.find_spec(fullname) is not None:
			# importa o pacote de verdade
			__import__(fullname)
			parent = sys.modules[fullname]
			continue
		# cria pacote "fake" só se não existe nem no sys.modules nem no disco
		pkg = types.ModuleType(fullname)
		pkg.__path__ = []  # pacote vazio
		sys.modules[fullname] = pkg
		if parent is not None:
			setattr(parent, part, pkg)
		parent = pkg
	return parent, parts
	

def _install_module(module_name: str, code_obj, inject: dict | None = None):
	"""
	Cria a hierarquia, executa code_obj no módulo final e registra em sys.modules.
	inject: dict com símbolos extras a injetar no módulo antes do exec.
	"""
	parent, parts = _ensure_module_hierarchy(module_name)
	mod = types.ModuleType(module_name)
	if inject:
		mod.__dict__.update(inject)
	exec(code_obj, mod.__dict__)
	sys.modules[module_name] = mod
	if parent is not None:
		setattr(parent, parts[-1], mod)
	return mod

def run_ast_tests(modules: dict, test_modules: dict, *, runner=None, verbosity=1):
	"""
	Compila e executa módulos e testes em memória usando ASTs.

	- modules: dict nome|path -> AST (ex: {'x.py': ast_x, 'pkg/aux.py': ast_aux})
	- test_modules: dict nome|path -> AST (ex: {'test_x.py': ast_tx})

	Retorna: unittest result object
	"""
	loaded_test_mods = []

	# === Etapa 1: carrega módulos normais (CUTs) ===
	for key, tree in modules.items():
		mod_name = _to_module_name(key)
		ast.fix_missing_locations(tree)
		code_obj = compile(tree, f"<{mod_name}>", "exec")
		# injeta dependências (ajuste se as funções tiverem outro nome/escopo)
		inject = {}
		if "bool_register" in globals():
			inject["bool_register"] = globals()["bool_register"]
		if "init_bool_register" in globals():
			inject["init_bool_register"] = globals()["init_bool_register"]
		_install_module(mod_name, code_obj, inject=inject)

	# === Etapa 2: carrega módulos de teste ===
	for key, tree in test_modules.items():
		mod_name = _to_module_name(key)
		ast.fix_missing_locations(tree)
		code_obj = compile(tree, f"<{mod_name}>", "exec")
		test_mod = _install_module(mod_name, code_obj)
		loaded_test_mods.append(test_mod)

	# === Etapa 3: executa os testes ===
	suite = unittest.TestSuite()
	loader = unittest.defaultTestLoader
	for test_mod in loaded_test_mods:
		suite.addTests(loader.loadTestsFromModule(test_mod))

	if runner is None:
		runner = unittest.TextTestRunner(verbosity=verbosity)
	result = runner.run(suite)
	return result



def parse_args():
	parser = argparse.ArgumentParser(
	description="Executa ASTs em memória com suporte a unittest e múltiplos caminhos."
)

	group = parser.add_mutually_exclusive_group()

	group.add_argument(
		'--run',
		action='store_true',
		help='Executa o arquivo como script principal'
	)

	group.add_argument(
		'--unittest',
		action='append',
		metavar='TESTE',
		help='Arquivos de teste a executar (pode repetir)'
	)
	
	parser.add_argument(
		'--append',
		action='store_true',
		help='Adiciona dados de cobertura às execuções anteriores'
	)

	parser.add_argument(
		'--path',
		action='append',
		default=[],
		help='Caminhos adicionais para sys.path (pode repetir)'
	)


	parser.add_argument(
		'--args',
		action='append',
		default=[],
		help='Argumentos para execução'
	)
	
	parser.add_argument(
		'arquivo',
		help='Arquivo principal do programa (ex: x.py)'
	)

	args = parser.parse_args()
	return args

def __ignore():
	i = 2
	n = len(sys.argv)
	arquivo = sys.argv[-1]
	vetig = []
	try: 
		while i < n - 1:
			s = sys.argv[i]
			if s.startswith('+'):
				l = int(s[1:])
				i += 1
				c = int(sys.argv[i])
				i += 1
				g = int(sys.argv[i])
				i += 1
				vetig.append(('+', l, c, g))
			elif s.startswith('-'):
				l = int(s[1:])
				i += 1
				c = int(sys.argv[i])
				i += 1
				g = int(sys.argv[i])
				i += 1
				vetig.append(('-', l, c, g))
			else:
				raise ValueError(f'Invalid argumet {s}')
	except Exception as ex:
		print(red('Invalid argumet'))
		print(red(ex))
		return

	
	try:
		with open(arquivo+'.mdc','rb') as f:
			dic_decisoes = pickle.load(f)
	except Exception as ex:
		print(red('Can´t read execution log file'))
		print(red(ex))
		return


	for op,l,c,oq in vetig:
		exect = op == '+'
		achou = False
		for _, dec in dic_decisoes.items():
			if dec.linha == (l,c):
				achou = True
				try:
					dec.executado[oq-1] = exect
					#print(dec)
				except:
					print(red(f'Not found requirement {(l,c,oq)}'))
				break
		if not achou:
			print(red(f'Not found decision {(l,c)}'))

	print_all_conditions(dic_decisoes)

	with open(arquivo+'.mdc','wb') as f:
		pickle.dump(dic_decisoes, f)


def print_all_conditions(conditions_list):
	totcov = totreq = 0
	for _,dec in conditions_list.items():
		print('Line number: {}'.format(dec.linha))
		print('Decicion:', dec.texto)
		print('Combinations to be covered: ')
		print(dec)
		cov,req = dec.get_covered_requirements()
		totcov += cov
		totreq += req
	percent = totcov * 100 // totreq if totreq != 0 else 100
	print(green('''\nCovered {} out of {} requirements in {} decisions ({}%)
	      '''.format(totcov, totreq, len(conditions_list),percent)))

def main():
	
	if len(sys.argv) < 2:
		sys.exit()
	if sys.argv[1] == '--cover':
		__ignore()
		sys.exit()

	args = parse_args()
	arquivo = args.arquivo

	# print("args.unittest:", args.unittest)
	# print("args.run:", args.run)
	# print("args.path:", args.path)
	# print("args.append:", args.append)
	# print("args.args:", args.args)
	# print("args.arquivo:", args.arquivo)
 	

	if not (args.run or args.unittest):
		inicio = time.time()
		try:
			mv = LogVisitor(file=arquivo)
		except Exception as ex:
			print(red('Error using {}. {}'.format(arquivo, str(ex))))
			sys.exit()
		mv.go_visit()
		
		dic_decisoes = {}
		for linha,cond in mv.decisoes.items():
			texto = mv.textos[linha]
			dic_decisoes[linha] = (Decisao(linha, cond, texto))
		
		
		
		print_all_conditions(dic_decisoes)
			
		with open(args.arquivo+'.mdc','wb') as f:
			pickle.dump(dic_decisoes, f)
		fim = time.time()
		print('Run time: {:.5f} '.format( fim-inicio))
							
	elif args.run:
		try:
			mv = LogTransformer(file=arquivo)
		except Exception as ex:
			print(red('Error using {}. {}'.format(arquivo, str(ex))))
			sys.exit()
		mv.go_visit()
		
		# insere os caminhos para include
		for caminho in args.path:
			if caminho not in sys.path:
				sys.path.insert(0, caminho)
				
		# Cria um módulo virtual e injeta o canal no namespace
		mod = types.ModuleType("__main__")
		mod.__dict__['bool_register'] = bool_register  # injeta a função
		mod.__dict__['init_bool_register'] = init_bool_register  # injeta a função

		mv.tree = ast.fix_missing_locations(mv.tree)

		oldargv = sys.argv
		sys.argv = [args.arquivo]
		if args.args != []:
			sys.argv += shlex.split(args.args[-1])


		# Executa a AST no namespace do módulo
		exec(compile(mv.tree, "<main>", "exec"), mod.__dict__)
		
		sys.argv = oldargv
		
		leu = False
		if args.append:
			try:
				with open(args.arquivo+'.mdc','rb') as f:
					dic_decisoes = pickle.load(f)
				leu = True
			except:
				print(red('Can´t read execution log file'))

		if not leu:
			dic_decisoes = {}
			for linha,cond in mv.decisoes.items():
				texto = mv.textos[linha]
				dic_decisoes[linha] = (Decisao(linha, cond, texto))
			
			
		for i  in range(len(exec_linhas)):
			linha = exec_linhas[i]
			dec = dic_decisoes[linha]
			dec.executa(exec_decisoes[i])

		print_all_conditions(dic_decisoes)

		with open(args.arquivo+'.mdc','wb') as f:
			pickle.dump(dic_decisoes, f)
		
	elif args.unittest:
		try:
			mv = LogTransformer(file=arquivo)
		except Exception as ex:
			print(red('Error using {}. {}'.format(arquivo, str(ex))))
			sys.exit()
		mv.go_visit()
		
		# insere os caminhos para include
		for caminho in args.path:
			if caminho not in sys.path:
				sys.path.insert(0, caminho)
		
		mod_dic = {arquivo:mv.tree}
		test_dic = {}
		for name in args.unittest:
			try: 
				f = open(name)
				source = f.read()
				f.close()
				code = ast.parse(source)
			except Exception as ex:
				print(red('Error using {}. {}'.format(arquivo, str(ex))))
				sys.exit()
			test_dic[name] = code
			
		result = run_ast_tests(mod_dic,test_dic)
		
		leu = False
		if args.append:
			try:
				with open(args.arquivo+'.mdc','rb') as f:
					dic_decisoes = pickle.load(f)
				leu = True
			except:
				print(red('Can´t read execution log file'))

		if not leu:
			dic_decisoes = {}
			for linha,cond in mv.decisoes.items():
				texto = mv.textos[linha]
				dic_decisoes[linha] = (Decisao(linha, cond, texto))
			
		for i  in range(len(exec_linhas)):
			linha = exec_linhas[i]
			dec = dic_decisoes[linha]
			dec.executa(exec_decisoes[i])

		print_all_conditions(dic_decisoes)
			
		with open(args.arquivo+'.mdc','wb') as f:
			pickle.dump(dic_decisoes, f)		
		
RED = '\033[31m'
GREEN = '\033[032m'
RESET = '\033[0m'

def red(s):
	if os.getenv('PYMCDCCOLOR') != None :
		return RED + str(s) + RESET
	return s 

def green(s):
	if os.getenv('PYMCDCCOLOR') != None :
		return GREEN + str(s) + RESET
	return s 

if __name__ == '__main__':
	main()
		

	
