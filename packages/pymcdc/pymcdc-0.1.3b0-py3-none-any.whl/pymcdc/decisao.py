from .visit_log import LogVisitor
from collections import Counter
from typing import List, Set, Tuple
from functools import lru_cache


class Decisao:
	operadores = ['*','+']

	def __init__(self, linha, decisao, texto):
		self.condicoes = []
		self.linha = linha
		self.texto = texto
		self.decisao = decisao[:]
		s = '{:3} | {:^8}'
		for no in decisao:
			if no in self.operadores:
				continue
			self.condicoes.append(no)
			lein = len(no) if len(no) >= 5 else 5
			s += '{:^'+str(lein+4)+'}'
		s += '{:^8}'
		self.computa_resultados()
		self.computa_pares()
		self.computa_requisitos()
		self.executado = len(self.requisitos) * [False]
		self.format = s
		
	def get_covered_requirements(self):
		return self.executado.count(True), len(self.executado)

		
	def __str__(self):
		l = [' ', 'Result.']
		for cd in self.condicoes:
			l.append(cd)
		l.append('Cover.')
		s = self.format.format(*l)
		r = len(s)
		s += '\n'
		s += r * '-'
		s += '\n'

		j = 0
		for p1 in self.requisitos:
			l = [j+1]
			l.append(str(self.resultados[p1]))
			for r in Decisao.int_to_list(p1,len(self.condicoes)):
				l.append(str(r == 1))

			l.append(str(self.executado[j]))
			j += 1
			s += self.format.format(*l)+'\n'
				
		return s
	
	@staticmethod
	def int_to_list(k, n):
		l = []
		for i in range(n):
			r = k & 1
			l.append(r)
			k >>= 1
		return l
	
	def computa_requisitos(self):
		req = set()
		for p1,p2 in self.pares:
			req.add(p1)
			req.add(p2)
		self.requisitos = sorted(list(req))
	
	def computa_resultados(self):
		self.resultados = []
		max = 2 ** len(self.condicoes)
		for k in range(max):
			if ( len(self.condicoes) > 18) :
				print('Computing: {} of {}.'.format(k,max), end='\r')
			pilha = self.decisao[:]
			blip = k
			for i in range(len(pilha)):
				if pilha[i] in self.operadores:
					continue
				if blip & 1  == 1:
					pilha[i] = True
				else:
					pilha[i] = False
				blip >>= 1
			self.resultados.append(self.computa_decisao(pilha))
		print("")
	
	def computa_decisao(self, pilha):
		i = 0
		while len(pilha) > 1:
			if not pilha[i] in self.operadores:
				i += 1
				continue
			if pilha[i] == '*':
				r = pilha[i-1] and pilha[i-2]
			else:
				r = pilha[i-1] or pilha[i-2]
			pilha[i-2] = r
			del pilha[i-1]
			del pilha[i-1]
			i -= 2
		return pilha[0]
		
		
	def computa_pares(self):
		n = len(self.condicoes) # numero de decisoes é o numero de dígitos
		self.pares = []
		for i in range(n):
			usados = set()
			self.pares.append(set())
			for j in range(2**n):
				if j in usados :
					continue
				usados.add(j)
				par = j + 2**i
				if par >= 2**n:
					break
				usados.add(par)
				if self.resultados[j] != self.resultados[par]:
					self.pares[i].add((j,par))
		self.pares = self.minimiza_pares(self.pares)
				

	def minimiza_pares(self,lista_conjuntos):
		resultado = set()
		usados = Counter()

		for conjunto in lista_conjuntos:
			melhor_par = None
			melhor_pontuacao = -1

			for par in conjunto:
				a, b = par
				pontuacao = usados[a] + usados[b]
				if pontuacao > melhor_pontuacao:
					melhor_pontuacao = pontuacao
					melhor_par = par

			resultado.add(melhor_par)
			usados[melhor_par[0]] += 1
			usados[melhor_par[1]] += 1

		return resultado



# execuções é um dicionário com o valor de cada uma das condições 
	def executa(self, execucoes):
		for i in range(len(self.requisitos)):
			req = self.requisitos[i]
			lreq = Decisao.int_to_list(req, len(self.condicoes))
			executou = True
			for cond,res in execucoes.items():
				if lreq[cond] != res:
					executou = False
					break
			self.executado[i] |= executou
		return


