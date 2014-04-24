# -*- coding: utf-8 -*-
'''
import geojson
import sqlite3
import os
'''
import logging as log
import dimtanc as dt
'''
def get_homes(format='json'):
	path =  os.path.dirname(os.path.abspath(__file__))

	con = sqlite3.connect(path+'\\zap.db' )
	con.row_factory = sqlite3.Row

	print 'Quering home'
	rows = con.execute('select id_home, price_m2,  condo, bedrooms, suites, garage, lat_home, lng_home, glat, glng from vw_price_m2 where lat_home is not null ').fetchall()

	if format=='json':
		homes = []
		lat,lng,price_m2,id_home = None,None,None,None
		for row in rows:
			point = {
				'lat':row['lat_home'], 
				'lng': row['lng_home'], 
				'price_m2':row['price_m2'],
				'id_home': row['id_home']}
			print point
			homes.append(point)
		con.close()
		return simplejson.dumps(homes)
	

	if format=='geojson':
		features = []
		for row in rows:
			point = geojson.Point(coordinates=[row['lat_home'],row['lng_home']])
			prop = {'price_m2':row['price_m2']}
			feature = geojson.Feature(id=row['id_home'], geometry=point, properties=prop)
			features.append(feature)
		homes = geojson.FeatureCollection(features=features)
		con.close()
		return geojson.dumps(homes)
	
	if format=='csv':
		txt = ''
		for row in rows:
			txt += str(row['lat_home'])+';'+str(row['lng_home'])+';'+str(row['price_m2'])+';'+str(row['id_home'])+'\n'
			
		con.close()
		return txt
'''        
def teste():
    cen = dt.CenarioDimensionamento(
                    nome = 'Cenario_Teste',                       
                    producao_mensal = 60000,
                    capacidade_tanque = 30000,
                    tempo_preparo = 0, # Unidades de Tempo.
                    tipo_modal_entrada = dt.TIPO_MODAL_CONTINUO,  
                    tipo_modal_saida = dt.TIPO_MODAL_DISCRETO,
                    numero_unidades_tempo = 10,
                    vazao_modal_entrada = None, 
                    vazao_modal_saida = 30000, 
                    volume_modal_entrada = None, 
                    volume_modal_saida = 30000
                  )
    
    cen.dimensiona_tanques()
    
    return cen.exporta_json()
		
		
if __name__ == "__main__":
	teste()


def cenario(nome, 
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
		atraso_modal_saida):
	
	cen = dt.CenarioDimensionamento(
					nome = nome,					   
					producao_mensal = int(producao_mensal),
					capacidade_tanque = capacidade_tanque,
					tempo_preparo = tempo_preparo,
					tipo_modal_entrada = tipo_modal_entrada,
					tipo_modal_saida = tipo_modal_saida,
					numero_unidades_tempo = numero_unidades_tempo,
					vazao_modal_entrada = vazao_modal_entrada,
					vazao_modal_saida = vazao_modal_saida,
					volume_modal_entrada = volume_modal_entrada,
					volume_modal_saida = volume_modal_saida,
					atraso_modal_entrada = atraso_modal_entrada,
					atraso_modal_saida = atraso_modal_saida
				  )
	
	cen.dimensiona_tanques()
	
	return cen.exporta_json()


