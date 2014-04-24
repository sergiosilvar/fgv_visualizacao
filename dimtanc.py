# -*- coding: latin-1 -*-

'''
Created on 14/02/2014

@author: sergio
'''

from __future__ import division
import logging as log
import math
import sys
import os.path
import ConfigParser
from collections import OrderedDict

LIMITE_ERRO = 0.0001
TIPO_MODAL_CONTINUO = 'continuo'
TIPO_MODAL_DISCRETO = 'discreto'
TIPO_MODAL_NAVIO = 'navio'
ESTADO_TANQUE_PARADO = 'par'
ESTADO_TANQUE_RECEBENDO = 'rec'
ESTADO_TANQUE_EM_PREPARO = 'emp'
ESTADO_TANQUE_PREPARADO = 'pre'
ESTADO_TANQUE_ENVIANDO = 'env'


log.basicConfig(format='%(levelname)s :> %(asctime)s :> %(message)s', 
                level=log.DEBUG)


class DimTancError(Exception):
    """Classe base para exce��es do algoritmo"""
    pass

class ProducaoMensalImpossivelError(DimTancError):
    '''
    N�o � poss�vel atingir a produ��o mensal para entrada os par�metros de 
    volume e vaz�o do modal em quest�o. 
    '''


    def __init__(self, nome_cenario, producao_mensal, vazao_modal, volume_modal,
                  unidades_tempo_cenario, unidades_tempo_necessario):
        '''
        Constructor
        '''
        msg = 'N�o � poss�vel atingir a produ��o mensal de %d do cen�rio "%s" "\
            "com os par�metros do modal volume %.2f, vaz�o %.2f. S�o " \
            "necess�rios %d unidades de tempo ao inv�s de %d informado.' % \
              (producao_mensal, nome_cenario, volume_modal, vazao_modal, 
                unidades_tempo_necessario, unidades_tempo_cenario)
        self.message = msg
        self.args= [msg]




class Tanque(object):
    '''
    Tanque para armazenamento de um produto.
    '''

    def __init__(self, nome, capacidade, unidade_tempo, preparado=False):
        '''
        Constructor
        '''
        if capacidade <= 0:
            raise Exception('Capacidade do Tanque n�o poder ser um n�mero ' \
                            'menor ou igual a zero. Capcidade encontrada: ' + 
                            str(capacidade))
        self.capacidade = capacidade


        self.nome = nome
        
        # Lista interna para registro do volume ocupado e estado do tanque em 
        # cada unidade de tempo.
        self.ocupacao = {}
        
        
        # RN:29
        estado_inicial = ESTADO_TANQUE_PARADO
        volume_ocupado_inicial = 0
        if preparado:
            estado_inicial = ESTADO_TANQUE_PREPARADO
            volume_ocupado_inicial = self.capacidade
            
        self.fim_preparo = None
        
        self.vol = []
        self.est = []

        for i in range(1, unidade_tempo + 1):
            self.registra_situacao(i, volume_ocupado_inicial, estado_inicial)
        
        
    def volume_ocupado(self, unidade_tempo=None):
        '''
        Retorna o volume ocupado em uma determinada unidade de tempo. Se a 
        unidade de tempo n�o for informada, retorna o volume ocupado para a 
        �ltima unidade de tempo.
        
        :param unidade_tempo: 
        '''
        # RN: 31
        if len(self.ocupacao) == 0 or unidade_tempo == 0: return 0
        if unidade_tempo == None: 
            unidade_tempo = max(self.ocupacao.keys())
        return self.ocupacao[unidade_tempo][1]
        
    def volume_disponivel(self, unidade_tempo=None):
        '''
        Retorna o volume disponivel_recebimento em uma determinada unidade de 
        tempo. Se a unidade de tempo n�o for informada, retorna o volume 
        dispon�vel para a �ltima unidade de tempo.
        :param unidade_tempo:
        '''
        if unidade_tempo == None: 
            unidade_tempo = max(self.ocupacao.keys())
        return self.capacidade - self.volume_ocupado(unidade_tempo)
    
    def completa_volume(self, unidade_tempo):  
        '''
        Completa todo o volume dispon�vel do tanque com produto para a 
        unidade de tempo informada.
        :param unidade_tempo:
        '''
        self.registra_situacao(unidade_tempo, self.capacidade, 
                               ESTADO_TANQUE_RECEBENDO)
        
    def esvazia(self, unidade_tempo):  
        '''
        Esvazia todo o volume ocupado do tanque para a unidade de tempo 
        informada. 
        :param unidade_tempo:
        '''
        self.registra_situacao(unidade_tempo, 0, ESTADO_TANQUE_ENVIANDO)
        
    
    def recebe_volume(self, unidade_tempo, volume_a_receber):  
        '''
        Recebe o volume informado ou at� o limite de volume disponivel_recebimento, o que
        for menor, para a unidade de tempo informada. Retorna o volume 
        efetivamente recebido.
        :param unidade_tempo:
        :param volume_a_receber:
        '''
        volume_recebido = min(volume_a_receber, 
                              self.volume_disponivel(unidade_tempo))
        novo_volume_ocupado = self.volume_ocupado(unidade_tempo - 1) + volume_recebido
        self.registra_situacao(unidade_tempo, novo_volume_ocupado, 
                               ESTADO_TANQUE_RECEBENDO)
        return volume_recebido
        
    def envia_volume(self, unidade_tempo, volume_a_enviar):  
        '''
        Envia volume informado ou o volume ocupado para a unidade de tempo
        informada, o que for menor. Retorna o volume efetivamente enviado. 
        :param unidade_tempo: 
        :param volume_a_enviar: Volume a enviar.
        '''
        volume_enviado = min(volume_a_enviar, self.volume_ocupado(unidade_tempo))
        
        novo_volume_ocupado = self.volume_ocupado(unidade_tempo) - volume_enviado
        
        self.registra_situacao(unidade_tempo, novo_volume_ocupado, 
                               ESTADO_TANQUE_ENVIANDO)
        return volume_enviado
        
    def registra_situacao(self, unidade_tempo, volume_ocupado, estado):
        '''
        Registra o volume ocupado e o estado do tanque para a unidade de tempo
        informada.
        :param unidade_tempo:
        :param volume_ocupado:
        :param estado:
        '''
        self.ocupacao[unidade_tempo] = (unidade_tempo, volume_ocupado, estado)
        if len(self.vol) >= unidade_tempo:
            self.vol[unidade_tempo-1] = volume_ocupado
            self.est[unidade_tempo-1] = estado 
        else:
            self.vol.append(volume_ocupado)
            self.est.append(estado)

    def __repr__(self):
        '''
        M�todo interno para identifica��o do tanque em depura��o.
        '''
        return '[Nome: %s, Vol Ocup: %.2f,  Vol Disp: %.2f]' % \
            (self.nome, self.volume_ocupado(), self.volume_disponivel())
        
        
    def estado(self, unidade_tempo):
        '''
        Retorna o estado do tanque para a unidade de tempo informada.
        :param unidade_tempo:
        '''
        return self.situacao(unidade_tempo)[2]
    
    def situacao(self, unidade_tempo):
        '''
        M�todo interno que retorna o o volume ocupado e estado do tanque para
        a unidade de tempo informada.
        :param unidade_tempo:
        '''
        return self.ocupacao[unidade_tempo]

    def disponivel_recebimento(self, unidade_tempo):
        '''
        Indica se o tanque est� dispon�vel para recebimento.
        '''
        return self.estado(unidade_tempo) == ESTADO_TANQUE_PARADO  \
            and self.volume_disponivel(unidade_tempo) > 0

    def disponivel_envio(self, unidade_tempo):
        '''
        Indica se o tanque est� dispon�vel para envio.
        '''
        return self.estado(unidade_tempo) == ESTADO_TANQUE_PREPARADO \
            and self.volume_ocupado(unidade_tempo) > 0
    
    
class ParqueTancagem(object):
    '''
    Parque de tanques. 
    '''
    
    def __init__(self, capacidade_tanque):
        '''
        Construtor da classe.
        :param capacidade_tanque: capacidade de volume de todos os tanques do 
        parque.
        '''
        self.tanques = []
        self.capacidade_tanque = capacidade_tanque
        
    
    def proximo_tanque_recebimento(self, unidade_tempo):
        '''
        Retorna o tanque adequado para recebimento na unidade de tempo 
        informada. 
        '''
        tanques_disponiveis = [t for t in self.tanques 
                               if t.disponivel_recebimento(unidade_tempo)]
        if len(tanques_disponiveis) > 0:
            tanques_disponiveis = sorted(tanques_disponiveis, \
                                key=lambda tanque: tanque.volume_ocupado())
            t = tanques_disponiveis[-1]
        else:
            t = self.cria_tanque(unidade_tempo)
        return t
            
    def proximo_tanque_envio(self, unidade_tempo):
        '''
        Retorna o tanque adequado para envio na unidade de tempo informada.
        '''
        #tanques_preparados = [t for t in self.tanques if t.estado(unidade_tempo) == ESTADO_TANQUE_PREPARADO]
        #tanques_disponiveis = [t for t in tanques_preparados if t.volume_ocupado(unidade_tempo) > 0]
        tanques_disponiveis = [t for t in self.tanques \
                               if t.disponivel_envio(unidade_tempo)]
        if len(tanques_disponiveis) > 0:
            tanques_disponiveis = sorted(tanques_disponiveis, \
                                key=lambda tanque: tanque.volume_disponivel())
            t = tanques_disponiveis[-1]
        else:
            t = self.cria_tanque_ocupado(unidade_tempo)
            
        return t
            
            
    def capacidade_total(self):
        '''
        Retorna a soma da capacidade em volume de todos os tanques do parque. �
        o voluem total que pode ser armazenado no parque.
        '''
        return sum([t.capacidade for t in  self.tanques])
        
        
    def cria_tanque(self, unidade_tempo):
        '''
        Retorna um novo tanque vazio na unidade de tempo informada,cuja 
        capacidade � a definida para o parque.
        :param unidade_tempo:
        '''
        nome = 'TQ' + str(len(self.tanques) + 1)
        tanque = Tanque(nome, self.capacidade_tanque, unidade_tempo)
        self.tanques.append(tanque)
        return tanque
    
    def cria_tanque_ocupado(self, unidade_tempo):
        '''
        Retorna um novo tanque totalmente ocupado na  uniade de tempo informada,
        cuja capacidade � a definida para o parque de tancagem. 
        :param unidade_tempo:
        '''
        nome = 'TQ' + str(len(self.tanques) + 1)
        tanque = Tanque(nome, self.capacidade_tanque, unidade_tempo, \
                        preparado=True)
        self.tanques.append(tanque)
        return tanque
    
        
    
    def quantidade_tanques(self):
        '''
        Retorna o quantidade de tanques no parque.
        '''
        return len(self.tanques)
    

                
    
class CenarioDimensionamento(object):
    '''
    Cen�rio de dimensionamento de parque de tancagem.
    '''
    
    
    
    def __init__(
            self,
            nome,
            producao_mensal,
            capacidade_tanque,
            tempo_preparo,
            tipo_modal_entrada,
            tipo_modal_saida,
            numero_unidades_tempo,
            volume_modal_entrada=None,
            volume_modal_saida=None,
            vazao_modal_entrada=None,
            vazao_modal_saida=None,
            atraso_modal_entrada=0,
            atraso_modal_saida=0,
            pasta_arquivos=None):
        '''
        Construtor da classe.
        
        :param nome: Nome do cen�rio.
        :param producao_mensal: Produ��o mensal do produto.
        :param capacidade_tanque: Capacidade em voluem do tanque. 
        :param tempo_preparo: Quantidade de unidades de tempo necess�rios para a fase de preparo do produto.
        :param tipo_modal_entrada: Identifica o modal de entrada. Os valores poss�veis s�o 'navio','discreto','continuo'.
        :param tipo_modal_saida: Identifica o modal de sa�da. Os valores poss�veis s�o 'navio','discreto','continuo'.
        :param numero_unidades_tempo: N�mero de unidades de tempo para a simula��o.
        :param volume_modal_entrada: Volume do modal de entrada.
        :param volume_modal_saida: Volume do modal de sa�da.
        :param vazao_modal_entrada: Vaz�o do modal de entrada.
        :param vazao_modal_saida: Vaz�o do modal de sa�da.
        :param pasta_arquivos: Pasta onde os arquivos ser�o criados. 
        '''
        
        
        
        # Verifica se os par�metros necess�rios ao tipo de modal est�o cont�m
        # valores.
        if (tipo_modal_entrada in (TIPO_MODAL_NAVIO,TIPO_MODAL_DISCRETO) ) and \
            (volume_modal_entrada == None or volume_modal_entrada <=0):
            raise Exception('N�o foi definido volume de entrada para o modal Navio')
            
        if (tipo_modal_saida in (TIPO_MODAL_NAVIO,TIPO_MODAL_DISCRETO) ) and \
            (volume_modal_saida == None or volume_modal_saida <=0):
            raise Exception('N�o foi definido volume de saida para o modal Navio')
            
        if tipo_modal_entrada == TIPO_MODAL_DISCRETO  and \
            (vazao_modal_entrada == None or volume_modal_entrada <=0):
            raise Exception('N�o foi definido vaz�o de entrada para o modal Discreto.')
 
        if tipo_modal_saida == TIPO_MODAL_DISCRETO  and \
            (vazao_modal_saida == None or volume_modal_saida <=0):
            raise Exception('N�o foi definido vaz�o de sa�da para o modal Discreto.')
 
        
        self.nome = nome
        self.producao_mensal = producao_mensal
        self.capacidade_tanque = capacidade_tanque 
        self.tempo_preparo = tempo_preparo
        self.tipo_modal_entrada = tipo_modal_entrada
        self.tipo_modal_saida = tipo_modal_saida 
        self.volume_modal_entrada = volume_modal_entrada
        self.volume_modal_saida = volume_modal_saida
        self.vazao_modal_entrada = vazao_modal_entrada
        self.vazao_modal_saida = vazao_modal_saida
        self.numero_unidades_tempo = numero_unidades_tempo
        self.atraso_modal_entrada = atraso_modal_entrada
        self.atraso_modal_saida = atraso_modal_saida
        
        self.parque = ParqueTancagem(self.capacidade_tanque)
        
        self.ocupacao = None
        self.pasta_arquivos = pasta_arquivos
        self.dist_vazao_entrada = []
        self.dist_vazao_saida = []
        
        
        # Calcula a distribui��o.
        self.calcula_distribuicao_vazao()

    


    def fim_simulacao(self, unidade_tempo):
        '''
        Indica se a simula��o chegou a fim para a unidade de tempo informada.
        :param unidade_tempo:
        '''
        # TODO: O fim da simula��o deve ser quando n�o se cria mais tanques?
        
        # Hoje o fim � quando se atinge o n�mero de unidades de tempo do cen�rio.
        return unidade_tempo > self.numero_unidades_tempo
        
        
    def dimensiona_tanques(self):
        '''
        Rotina principal que executa a an�lise do estado dos tanques,
        recebimento e envio de produto at� a condi��o de fim da simula��o.
        '''
        
        log.info('In�cio da simula��o de dimensionamento.')
        unidade_tempo = 1
        
        # Enquanto n�o se atinge o fim da simula��o...
        while not self.fim_simulacao(unidade_tempo):
            
            # Volume a receber na unidade de tempo.
            volume_a_receber = self.dist_vazao_entrada[unidade_tempo - 1]
            
            # Volume a enviar na unidade de tempo.  
            volume_a_enviar = self.dist_vazao_saida[unidade_tempo - 1]

            # Executa a an�lise de estado dos tanques.
            self.analise_estado_tanques(unidade_tempo)
            
            # Executa a an�lise de recebimetno de produto.
            self.analise_recebimento_produto(unidade_tempo, volume_a_receber)
            
            # Executa a an�lise de envio de produto.
            self.analise_envio_produto(unidade_tempo, volume_a_enviar)
            
            # Avan�a a unidade de tempo.
            unidade_tempo += 1
            
        # Salva o resultado em um arquivo.
        self.exporta_estado(unidade_tempo - 1)

        # Salva a distribui��o de vaz�o.
        self.exporta_distibuicao_vazao(unidade_tempo - 1)
            
        log.info('Fim da simula��o de dimensionamento com %d tanques.' % (self.qtd_tanques()))


    
    def analise_estado_tanques(self, unidade_tempo):
        '''
        An�lise de estados dos tanques para a unidade de tempo informada.
        :param unidade_tempo:
        '''
        unidade_tempo_anterior = unidade_tempo - 1
        
        for tanque in self.parque.tanques:
            
            volume_ocupado_anterior = tanque.volume_ocupado(unidade_tempo_anterior)
            novo_estado = None
        
            # RN:17
            if tanque.estado(unidade_tempo_anterior) == ESTADO_TANQUE_PARADO:
                # N�o altera.
                novo_estado = ESTADO_TANQUE_PARADO

    
            # RN:18
            if tanque.estado(unidade_tempo_anterior) == ESTADO_TANQUE_RECEBENDO and tanque.volume_disponivel() == 0:
                novo_estado = ESTADO_TANQUE_EM_PREPARO
                tanque.fim_preparo = unidade_tempo_anterior + self.tempo_preparo 
                if tanque.fim_preparo == unidade_tempo_anterior:
                    novo_estado = ESTADO_TANQUE_PREPARADO

    
            # RN:19
            if tanque.estado(unidade_tempo_anterior) == ESTADO_TANQUE_RECEBENDO and tanque.volume_disponivel() > 0:
                novo_estado = ESTADO_TANQUE_PARADO

            
            # RN:20
            if tanque.estado(unidade_tempo_anterior) == ESTADO_TANQUE_EM_PREPARO and unidade_tempo <= tanque.fim_preparo: 
                novo_estado = ESTADO_TANQUE_EM_PREPARO

            
            # RN:21
            if (tanque.estado(unidade_tempo_anterior) == ESTADO_TANQUE_EM_PREPARO  and unidade_tempo >= tanque.fim_preparo):
                novo_estado = ESTADO_TANQUE_PREPARADO
                tanque.fim_preparo = None

            
#             # FIXME: NOVA REGRA    
#             if (tanque.fim_preparo != None and  tanque.estado(unidade_tempo) == ESTADO_TANQUE_EM_PREPARO  and unidade_tempo > tanque.fim_preparo):
#                 novo_estado = ESTADO_TANQUE_PREPARADO
#                 tanque.fim_preparo = None
                
                
            # RN:22
            if tanque.estado(unidade_tempo_anterior) == ESTADO_TANQUE_PREPARADO :
                novo_estado = ESTADO_TANQUE_PREPARADO

                
            # RN:23
            if tanque.estado(unidade_tempo_anterior) == ESTADO_TANQUE_ENVIANDO and tanque.volume_ocupado() > 0:
                novo_estado = ESTADO_TANQUE_PREPARADO

                
            # RN:24
            if tanque.estado(unidade_tempo_anterior) == ESTADO_TANQUE_ENVIANDO and tanque.volume_ocupado() == 0:
                novo_estado = ESTADO_TANQUE_PARADO
                
            if novo_estado == None:
                raise Exception("N�o foi definido novo estado do tanque.")
                
            
            tanque.registra_situacao(unidade_tempo, volume_ocupado_anterior, novo_estado)

                
                
    def analise_recebimento_produto(self, unidade_tempo, volume_a_receber):
        '''
        An�lise de recebimento de produto para a unidade de tempo informada.
        :param unidade_tempo: unidade de tempo em an�lise.
        :param volume_a_receber: volume para ser armazenado no parque.
        '''
        volume_recebido = 0

        while volume_a_receber != volume_recebido  :
            tanque = self.parque.proximo_tanque_recebimento(unidade_tempo)
            
            # Necess�rio calcular a diferen�a dentro de um erro esperado.
            if math.fabs(tanque.volume_disponivel(unidade_tempo) - volume_a_receber) < LIMITE_ERRO:
                tanque.completa_volume(unidade_tempo)
                volume_recebido = volume_a_receber 
            else:
                vol_rec = tanque.recebe_volume(unidade_tempo, volume_a_receber - volume_recebido)
                volume_recebido += vol_rec

        if volume_recebido > volume_a_receber:
            raise Exception("Volume recebido %f maior que volume a receber %f." 
                            % (volume_recebido, volume_a_receber))
            

        
    
    def analise_envio_produto(self, unidade_tempo, volume_a_enviar):
        '''
        An�lise de envio de produto para a unidade de tempo informada.
        :param unidade_tempo: unidade de tempo em an�lise.
        :param volume_a_enviar: volume a ser enviado do parque.
        '''
        volume_enviado = 0
        
        while volume_a_enviar != volume_enviado:
            tanque = self.parque.proximo_tanque_envio(unidade_tempo)
            
            # Necess�rio calcular a diferen�a detro de um erro esperado.
            if math.fabs(
                         tanque.volume_ocupado(unidade_tempo) 
                         - volume_a_enviar) < LIMITE_ERRO:
                tanque.esvazia(unidade_tempo)
                volume_enviado = volume_a_enviar 
            else:
                vol_env = tanque.envia_volume(unidade_tempo, volume_a_enviar 
                                              - volume_enviado)
                volume_enviado += vol_env

        if volume_enviado > volume_a_enviar:
            raise Exception("Volume enviado %f maior que volume a enviar%f." 
                            % (volume_enviado, volume_a_enviar))

    def exporta_estado(self, unidade_tempo):
        '''
        Exporta as informa��es de volume e estados do parque do in�cio da 
        simula��o at� a unidade de tempo informada.
        :param unidade_tempo: unidade de tempo final para a exporta��o dos 
        dados.
        '''
        if self.pasta_arquivos != None:
            nome_arquivo = self.nome + '.csv'
            if self.pasta_arquivos != None:
                nome_arquivo = self.pasta_arquivos + '/' + nome_arquivo
            
            arquivo = open(nome_arquivo, 'w')
            
            nome_colunas = 'unid_tempo'
            for t in self.parque.tanques:
                nome_colunas += ';vol_' + t.nome + ';' + 'est_' + t.nome
            arquivo.write(nome_colunas + '\n')
            
            for i in range(1, unidade_tempo + 1):
                linha = '%d' % (i) 
                for t in self.parque.tanques:
                    unid_tempo, vol_ocup, estado = t.situacao(i)
                    x = ';%.2f;%s' % (vol_ocup, estado)
                    x = x.replace('.', ',')
                    linha += x
                arquivo.write(linha + '\n')
            arquivo.close()

    def exporta_json(self ):
        '''
        '''
        json = {}
        json['nome'] = self.nome

        json['volume'] = {}
        json['situacao'] = {}
        json['qtd_tanques'] = self.qtd_tanques()
        json['nome_tanques'] = [t.nome for t in self.parque.tanques]
        json['num_unid_tempo'] = self.numero_unidades_tempo
        for t in self.parque.tanques:
            # Exporta volume da forma como est�.
            json['volume'][t.nome] = t.vol

            # Exporta os estados em uma forma mais reduzida.
            lista = [];
            situacao = {'inicio':0, 'fim':0, 'tam':1,'estado':t.est[0]};
            for i in range(1, len(t.est)):
                # Se a i-�sima situa��o � diferente da atual...
                if (situacao['estado'] != t.est[i]):
                    # ... registra o fim da situa��o atual.
                    situacao['fim'] = i-1;
                    situacao['tam'] = situacao['fim'] - situacao['inicio'] + 1;   
                    # Armazena na lista de situa��es.
                    lista.append(situacao);
                    # Cria uma nova siuta��o com o estado novo.
                    situacao = {'inicio':i, 'fim':i, 'tam':1,'estado':t.est[i]}
            
                # Armazena a �ltima situa��o.
                if (i == len(t.est)-1):
                    situacao['fim'] = i;
                    situacao['tam'] = situacao['fim'] - situacao['inicio'] + 1;   
                    lista.append(situacao)
            json['situacao'][t.nome] = lista
        return json

    def exporta_distibuicao_vazao(self, unidade_tempo):
        '''
        Exporta as informa��es de distribui��o de vaz�o de entrada e sa�da da 
        simula��o at� a unidade de tempo informada.
        :param unidade_tempo: unidade de tempo final para a exporta��o dos 
        dados.
        '''
        if self.pasta_arquivos != None:
            nome_arquivo = self.nome + '_dist_vazao.csv'
            if self.pasta_arquivos != None:
                nome_arquivo = self.pasta_arquivos + '/' + nome_arquivo
            
            arquivo = open(nome_arquivo, 'w')
            
            nome_colunas = 'unid_tempo;entrada;saida\n'
            arquivo.write(nome_colunas)
            for i in range(unidade_tempo):
                x = '%d;%.10f;%s' % (i+1,self.dist_vazao_entrada[i], self.dist_vazao_saida[i])
                x = x.replace('.', ',')
                arquivo.write(x + '\n')
            arquivo.close()

    

    def __calculo_distribuicao_vazao_continua(self, producao_mensal, numero_unidades_tempo):
        '''
        Calcula a distribui��o de vaz�o para o tipo de modal TIPO_MODAL_CONTINUO.
        :param producao_mensal:
        :param numero_unidades_tempo:
        '''
        return [producao_mensal / numero_unidades_tempo for i in range(1, numero_unidades_tempo + 1)]

    def __calculo_distribuicao_vazao_navio(self, producao_mensal, numero_unidades_tempo, volume_modal):
        '''
        Retorna a distribiu��o de vaz�o para o TIPO_MODAL_NAVIO.
        :param producao_mensal:
        :param numero_unidades_tempo:
        :param volume_modal:
        '''
        
        dist_vazao = [0 for i in range(numero_unidades_tempo)]

        qtd_chegadas = producao_mensal / volume_modal
        intervalo_entrada = int(numero_unidades_tempo / qtd_chegadas)
        
        qtd_chegadas_ajustada = None
        if qtd_chegadas - int(qtd_chegadas) > 0: 
            qtd_chegadas_ajustada = int(qtd_chegadas) + 1
            intervalo_entrada = int(numero_unidades_tempo / qtd_chegadas_ajustada)
        
        

        for i in range(int(qtd_chegadas)):
            dist_vazao[i*intervalo_entrada] = volume_modal 

        # Se a quantidade de chegadas foi ajustada, ent�o a �ltima 
        # chegada deve trazer o volume restante para completar a 
        # produ��o mensal.
        if qtd_chegadas_ajustada != None:
            fator = qtd_chegadas - int(qtd_chegadas)
            try:
                dist_vazao[(qtd_chegadas_ajustada-1)*intervalo_entrada] = volume_modal * fator 
            except IndexError as e:
                log.error('�ndice %d da vaz�o maior que capacidade %d no cen�rio %s' %(qtd_chegadas_ajustada*intervalo_entrada,len(dist_vazao),self.nome))
                raise e
            
        return dist_vazao
    
    def __distribui_transferencia(self,volume_modal,vazao_modal):
        '''
        Retorna a distribui��o de volume em um vetor cujo tamanho depende
        do volume e vaz�o do modal. 
        :param volume_modal:
        :param vazao_modal:
        '''
        # Calcula o n�mero de unidades de tempo necess�rios para transferir
        # todo o volume do modal conforme sua vaz�o. Caso esse n�mero seja
        # n�o inteiro, esse n�mero � arredondado para cima. Cria um vetor
        # com o n�mero de unidades de tempo calculado e em cada entrada do vetor
        # � armazenado o voluem a ser transferido naquela undiade de tempo. Caso
        # tenha ocorrido o arredondamento, a �ltima posi��o do vetor cont�m
        # o volume restante para completar o "volume_modal".
        numero_transferencias = volume_modal/vazao_modal
        resto = 0
        if numero_transferencias - int(numero_transferencias) > LIMITE_ERRO:
            resto = numero_transferencias-int(numero_transferencias) 
        transferencia = [vazao_modal for i in range(int(numero_transferencias))]
        if resto > 0:
            transferencia = transferencia + [volume_modal-sum(transferencia)]
        return transferencia

#     def __calculo_distribuicao_vazao_discreta(self, producao_mensal, numero_unidades_tempo, volume_modal,vazao_modal, atraso=0):
#         '''
#         Retorna a distribui��o de vaz�o para o TIPO_MODAL_DISCRETO.
#         :param producao_mensal:
#         :param numero_unidades_tempo:
#         :param volume_modal:
#         :param vazao_modal:
#         '''
#         dist_vazao = [0 for i in range(numero_unidades_tempo)]
# 
#         qtd_chegadas = producao_mensal / volume_modal
#         qtd_chegadas_ajustada = self.__proximo_inteiro_divisao(producao_mensal, volume_modal)
# 
#         intervalo_entrada = self.__proximo_inteiro_divisao(numero_unidades_tempo,qtd_chegadas) 
#         
#         
# 
#         if qtd_chegadas_ajustada > qtd_chegadas:
#             intervalo_entrada = self.__proximo_inteiro_divisao(numero_unidades_tempo, qtd_chegadas_ajustada)
# 
#         for i in range(int(qtd_chegadas)):
#             transferencia =  self.__distribui_transferencia(volume_modal, vazao_modal)
#             if qtd_chegadas*(len(transferencia)+intervalo_entrada) > self.numero_unidades_tempo:
#                 raise ProducaoMensalImpossivelError(self.nome,self.producao_mensal,vazao_modal,volume_modal,numero_unidades_tempo,qtd_chegadas*len(transferencia))
#             inicio = i*intervalo_entrada
#             fim = inicio + len(transferencia)   
#             dist_vazao[inicio:fim] = transferencia
# 
# 
#         # Se a quantidade de chegadas foi ajustada, ent�o a �ltima 
#         # chegada deve trazer o volume restante para completar a 
#         # produ��o mensal.
#         if qtd_chegadas_ajustada != None:
#             fator = qtd_chegadas - int(qtd_chegadas)
#             transferencia = self.__distribui_transferencia(volume_modal*fator, vazao_modal)
#             inicio = (qtd_chegadas_ajustada-1)*intervalo_entrada
#             fim = inicio+len(transferencia)
#             dist_vazao[inicio:fim] = transferencia 
#             
#                 
#         return dist_vazao
    
    
    def __calculo_distribuicao_vazao_discreta(self, producao_mensal, numero_unidades_tempo, volume_modal,vazao_modal, atraso_modal=0):
        '''
        Retorna a distribui��o de vaz�o para o TIPO_MODAL_DISCRETO.
        :param producao_mensal:
        :param numero_unidades_tempo:
        :param volume_modal:
        :param vazao_modal:
        '''
        
        dist_vazao = [0 for i in range(numero_unidades_tempo)]
        
        # Determinar o n�mero de bateladas (envios ou chegadas) e se a �ltima 
        # batelada � diferente das demais.
        qtd_batelada = producao_mensal / volume_modal
        qtd_batelada_ajustada = self.__proximo_inteiro_divisao(producao_mensal, volume_modal)
        periodo_batelada = numero_unidades_tempo / qtd_batelada

        
        transferencia =  self.__distribui_transferencia(volume_modal, vazao_modal)
        tam_transferencia = len(transferencia)
        if qtd_batelada*len(transferencia) > numero_unidades_tempo:
            raise Exception('Cenario',producao_mensal,vazao_modal,volume_modal,numero_unidades_tempo,qtd_batelada*len(transferencia))

        
        for i in range(int(qtd_batelada)):
            inicio = int(i*periodo_batelada)
            fim = inicio + len(transferencia)
            dist_vazao[inicio:fim] = transferencia
        
         
        

        # Se a quantidade de chegadas foi ajustada, ent�o a �ltima 
        # chegada deve trazer o volume restante para completar a 
        # produ��o mensal.
        if qtd_batelada - int(qtd_batelada) > LIMITE_ERRO:
            fator = qtd_batelada - int(qtd_batelada)
            transferencia = self.__distribui_transferencia(volume_modal*fator, vazao_modal)
            inicio = int((qtd_batelada_ajustada-1)*periodo_batelada)
            fim = inicio+len(transferencia)
            max_atraso = fim
            dist_vazao[inicio:fim] = transferencia 


        # Ajustar o vetor de distribu��o considerando o atraso informado.
        if atraso_modal > 0 :
            # Determinar a �ltima pois��o diferente de zero e o m�ximo atraso
            # permitido.
            ultima_pos = len(dist_vazao)-1
            max_atraso = 0
            for i in range(len(dist_vazao)-1,-1, -1):
                if dist_vazao[i] > 0:
                    max_atraso = len(dist_vazao)-i-1
                    ultima_pos = i
                    break
            
            # Limitar o atraso informado ao m�ximo atraso permitido.
            if atraso_modal > max_atraso:
                atraso_modal = max_atraso

            # Reconstruir a distribui��o considerando o atraso.
            dist_vazao = [0 for j in range(atraso_modal)] + dist_vazao[:ultima_pos+1]+[0 for j in range(len(dist_vazao)-ultima_pos-atraso_modal-1)]

        return dist_vazao
    
    
    def calcula_distribuicao_vazao(self):
        '''
        Retorna a distribui��o de vaz�o para os modais de entrada e sa�da
        conforme seu tipo.
        '''
        
        if self.tipo_modal_entrada == TIPO_MODAL_CONTINUO:
            self.dist_vazao_entrada = self.__calculo_distribuicao_vazao_continua(self.producao_mensal, self.numero_unidades_tempo)  
        if self.tipo_modal_saida == TIPO_MODAL_CONTINUO:
            self.dist_vazao_saida = self.__calculo_distribuicao_vazao_continua(self.producao_mensal, self.numero_unidades_tempo)

        if self.tipo_modal_entrada == TIPO_MODAL_NAVIO:
            # Troquei distribui��o da vaz�o de navio pela distribui��o da vaz�o discreta.
            #self.dist_vazao_entrada = self.__calculo_distribuicao_vazao_navio(self.producao_mensal, self.numero_unidades_tempo, self.volume_modal_entrada)

            # A distribui��o da vaz�o discreta para um navio assume que a vaz�o em cada unidade de tempo � igual ao volume do navio.  
            self.dist_vazao_entrada = self.__calculo_distribuicao_vazao_discreta(self.producao_mensal, self.numero_unidades_tempo, self.volume_modal_entrada, self.volume_modal_entrada, self.atraso_modal_entrada)
         
        if self.tipo_modal_saida == TIPO_MODAL_NAVIO:
            # Troquei distribui��o da vaz�o de navio pela distribui��o da vaz�o discreta.
            #self.dist_vazao_saida = self.__calculo_distribuicao_vazao_navio(self.producao_mensal, self.numero_unidades_tempo, self.volume_modal_saida)
            
            # A distribui��o da vaz�o discreta para um navio assume que a vaz�o em cada unidade de tempo � igual ao volume do navio.  
            self.dist_vazao_saida = self.__calculo_distribuicao_vazao_discreta(self.producao_mensal, self.numero_unidades_tempo, self.volume_modal_saida, self.volume_modal_saida, self.atraso_modal_saida)

        if self.tipo_modal_entrada == TIPO_MODAL_DISCRETO:
            self.dist_vazao_entrada = self.__calculo_distribuicao_vazao_discreta(self.producao_mensal, self.numero_unidades_tempo, self.volume_modal_entrada, self.vazao_modal_entrada, self.atraso_modal_entrada)

        if self.tipo_modal_saida == TIPO_MODAL_DISCRETO:
            self.dist_vazao_saida = self.__calculo_distribuicao_vazao_discreta(self.producao_mensal, self.numero_unidades_tempo, self.volume_modal_saida, self.vazao_modal_saida, self.atraso_modal_saida)


        
        return self.dist_vazao_entrada, self.dist_vazao_saida
        
    def __proximo_inteiro_divisao(self,dividendo,divisor):    
        '''
        Retorna o menor inteiro maior que o resultado da divis�o 
        dividendo/divisor.
        :param dividendo:
        :param divisor:
        '''
        quociente = dividendo/divisor
        if quociente - int(quociente) > 0:
            quociente = int(quociente) + 1
        return int(quociente)    
    
    def qtd_tanques(self):
        '''
        Retorna a quantidade de tanques necess�rios para atender a produ��o 
        mensal conforme os tipos de modais de entrada e sa�da, seu volume e 
        sua vaz�o.
        '''
        return len(self.parque.tanques)



if __name__ == '__main__':
    cen = CenarioDimensionamento(
                    nome = 'Cenario_adriana_20140410',                       
                    producao_mensal = 60000,
                    capacidade_tanque = 30000,
                    tempo_preparo = 0, # Unidades de Tempo.
                    tipo_modal_entrada = TIPO_MODAL_CONTINUO,  
                    tipo_modal_saida = TIPO_MODAL_DISCRETO,
                    numero_unidades_tempo = 720,
                    vazao_modal_entrada = None, 
                    vazao_modal_saida = 30000, 
                    volume_modal_entrada = None, 
                    volume_modal_saida = 30000
                  )
    
    cen.dimensiona_tanques()
    # Depurar a partir daqui.
    print cen.exporta_json()
        
