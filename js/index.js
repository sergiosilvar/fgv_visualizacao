var cenario = null
var chart_linha = null
var chart_barra = null

function calcula_cenario(){
	
	$.getJSON("/cenario", function(json) {
		ljson = json
		//console.log(ljson); // this will show the info it in firebug console
		load_limits(json,type)
	});

}


$(document).ready(function(){
	//alert('im ready')
    

	$("#form_cenario").submit(function(e){
		var postData = $(this).serialize();
		var formURL = $(this).attr("action");
		$.ajax(
				{
					url : formURL,
					type: "GET",
					data : postData,
					contentType: "application/json; charset=utf-8",
				    dataType: "json",
					success:function(data, textStatus, jqXHR) 
					{
						
						grafico_linha(data)
						
					},
					error: function(jqXHR, textStatus, errorThrown) 
					{
						//if fails      
					}
				});
		e.preventDefault(); //STOP default action
		//e.unbind(); //unbind. to stop multiple form submit.
	});
	

	
	
	chart_linha = c3.generate({
		bindto: '#chart_linha',
	    data: {
	        columns: []
	    }
	});	
});

function grafico_linha(cen){
	cenario = cen;
	var tanques = [];
	data_col = [];
	
	col_names = []
	for(var k in chart_linha.xs())
		col_names.push(k)
/*	
	for(var k in col_names)
		chart_linha.unload()
*/	
	for (var tanque in cen.volume){
		//tanques.push(k)
		//console.log('tanque: ' + tanque + ' - volume: ' + cen.volume[tanque])
		var col = [];
		col.push(tanque);
		for (var unid_tempo in cen.volume[tanque])
			col.push(cen.volume[tanque][unid_tempo]);
		//console.log('vetor: ' + col)
		data_col.push(col) 
	}
		//[tanques[0],cen.volume[tanques[0]]]
	chart_linha.load({'columns':data_col, 'unload' : col_names})
	//chart.load({'columns':[['dataN', 1, 2, 3, 4]]});
	//alert(data_col)
}


