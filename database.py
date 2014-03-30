# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

# -*- coding: utf-8 -*-
import os
import json

DIR = 'g:/Mestrado FGV/Dissertacao/fipezap/json/'

# <codecell>

def dataset(estado, cidade, bairro, num_quartos):
    fname = DIR+''+estado+'/'+cidade+'/'+bairro+'/%d_indices.json' % (num_quartos)
    f = open(fname,'r')
    ind = json.load(f)
    #ind = pd.io.json.read_json(fname)     
    f.close()
    return ind
    
def indices(estado=None, cidade=None, bairro=None, num_quartos=None):
    if num_quartos == None:
        num_quartos = 0
    ds =  dataset(estado, cidade, bairro, num_quartos)
    mes,ind = ['%d-%02d'%(x['Ano'],x['Mes']) for x in ds],[x['Valor'] for x in ds]
    return mes,ind


# <codecell>

def lista_estados():
    return os.listdir(DIR)

def lista_cidades(estado=None):
    return os.listdir(DIR+'/'+estado)

def lista_bairros(estado,cidade):
    return os.listdir(DIR+'/'+estado+'/'+cidade)

# <codecell>

class Indice(object):
    def __init__(self):
        pass
    
class Bairro(Indice):
    def __init__(self,estado,cidade,bairro):
        index_indice = 1
        index_mes = 0
        self.nome = bairro
        self.cidade = cidade
        self.estado = estado
        self.indices = [indices(estado,cidade,bairro,i)[index_indice] for i in range(4)]
        self.mes = indices(estado,cidade,bairro,0)[index_mes]
    
    def qt1(self):
        return self.indices[1]
    
    def qt2(self):
        return self.indices[2]
    
    def qt3(self):
        return self.indices[3]
    
    def qt0(self):
        return self.indices[0]
    
    def __repr__(self):
        return self.nome
    
class Cidade(Indice):
    def __init__(self, estado, cidade):
        self.nome = cidade
        self.estado = estado
        self.bairros = {}
    
    def lista_bairros(self):
        return lista_bairros(self.estado,self.nome)
    
    def bairro(self,nome_bairro):
        return self.bairros.get(nome_bairro,Bairro(self.estado,self.nome,nome_bairro))

# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


