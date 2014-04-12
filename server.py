# -*- coding: latin-1 -*-


# http://bottlepy.org/docs/dev/index.html
from bottle import route, get,post,run, static_file, request, response
import service
import logging
log = logging
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format('./', 'log.txt'))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

@route('/')
def hello():
    return static_file('index.html', root='./')

@route('/teste')
def teste():
	return service.teste()
	
    
#@route('/cenario', method='POST')
@get('/cenario')
def cenario():

    nome = request.params.nome
    producao_mensal = verifica_inteiro(request.params.producao_mensal)
    capacidade_tanque = verifica_inteiro(request.params.capacidade_tanque)
    tempo_preparo = verifica_inteiro(request.params.tempo_preparo)
    tipo_modal_entrada  = request.params.tipo_modal_entrada
    tipo_modal_saida = request.params.tipo_modal_saida
    numero_unidades_tempo = verifica_inteiro(request.params.numero_unidades_tempo)
    vazao_modal_entrada = verifica_inteiro(request.params.vazao_modal_entrada)
    vazao_modal_saida = verifica_inteiro(request.params.vazao_modal_saida)
    volume_modal_entrada = verifica_inteiro(request.params.volume_modal_entrada)
    volume_modal_saida = verifica_inteiro(request.params.volume_modal_saida)
    atraso_modal_entrada = verifica_inteiro(request.params.atraso_modal_entrada)
    atraso_modal_saida = verifica_inteiro(request.params.atraso_modal_saida)
    s = 'Recebido Cenario\nNome:\t%s\nProducao Mensal:\t%s\nCapacidade Tanque:\t%s\nUnidades Tempo:\t%s\nTempo Preparo:\t%s\nModal Entrada:\t%s\nModal Saida:\t%s\nVazao Modal Entrada:\t%s\nVazao Modal Saida:\t%s\nVolume Modal Entrada:\t%s\nVolume Modal Saida:\t%s\nAtraso Modal Entrada:\t%s\nAtraso Modal Saida:\t%s' % (
		nome,
		producao_mensal,
		capacidade_tanque,
		tempo_preparo,
		tipo_modal_entrada,  
		tipo_modal_saida,
		numero_unidades_tempo,
		vazao_modal_entrada, 
		vazao_modal_saida, 
		volume_modal_entrada, 
		volume_modal_saida,
        atraso_modal_entrada,
        atraso_modal_saida)
    log.debug(s)
	
    #response.content_type = "application/json"
    response.headers['Content-Type'] = 'application/json'
    return service.cenario(
		nome,
		producao_mensal,
		capacidade_tanque,
		tempo_preparo,
		tipo_modal_entrada,  
		tipo_modal_saida,
		numero_unidades_tempo,
		vazao_modal_entrada, 
		vazao_modal_saida, 
		volume_modal_entrada, 
		volume_modal_saida,
        atraso_modal_entrada,
        atraso_modal_saida
		)
    
@route('/<filename:path>')
def server_static(filename):
	print 'serving very well ... ' + filename
	return static_file(filename, root='./')	

def verifica_inteiro(str):
    try:
        return int(str)
    except ValueError:
        return None
        
	
run(host='localhost', port=8080, debug=True, reloader=True)

