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



function grafico_linha(data){
	
	// LINHA NVD3!!!
	/*These lines are all chart setup.  Pick and choose which chart features you want to utilize. */
	nv.addGraph(function() {
	  var chart = nv.models.lineChart()
					.margin({left: 100})  //Adjust chart margins to give the x-axis some breathing room.
					.useInteractiveGuideline(true)  //We want nice looking tooltips and a guideline!
					.transitionDuration(350)  //how fast do you want the lines to transition?
					.showLegend(true)       //Show the legend, allowing users to turn on/off line series.
					.showYAxis(true)        //Show the y-axis
					.showXAxis(true)        //Show the x-axis
	  ;

	  chart.xAxis     //Chart x-axis settings
		  .axisLabel('Unid. de Tempo')
		  //.tickFormat(d3.format(',r'));
		  .tickFormat(function(d){return d+1});

	  chart.yAxis     //Chart y-axis settings
		  .axisLabel('Volume (m^3)')
		  .tickFormat(d3.format(',.02f'));

	  d3.select('#chart_linhanv')    //Select the <svg> element you want to render the chart in.   
		  .datum(data)         //Populate the <svg> element with chart data...
		  .call(chart);          //Finally, render the chart!

	  //Update the chart when window resizes.
	  nv.utils.windowResize(function() { chart.update() });
	  return chart;
	});	
	


}

function grafico_area(data){
	
	
	/*These lines are all chart setup.  Pick and choose which chart features you want to utilize. */
	nv.addGraph(function() {
	  var chart = nv.models.stackedAreaChart()
					.margin({left: 100})  //Adjust chart margins to give the x-axis some breathing room.
					.useInteractiveGuideline(true)  //We want nice looking tooltips and a guideline!
					.transitionDuration(350)  //how fast do you want the lines to transition?
					.showLegend(true)       //Show the legend, allowing users to turn on/off line series.
					.showYAxis(true)        //Show the y-axis
					.showXAxis(true)        //Show the x-axis
					.showControls(true)
	  ;

	  chart.xAxis     //Chart x-axis settings
		  .axisLabel('Unid. de Tempo')
		  //.tickFormat(d3.format(',r'));
		  .tickFormat(function(d){return d+1});

	  chart.yAxis     //Chart y-axis settings
		  .axisLabel('Volume (m^3)')
		  .tickFormat(d3.format(',.02f'));

	  d3.select('#chart_areanv')    //Select the <svg> element you want to render the chart in.   
		  .datum(data)         //Populate the <svg> element with chart data...
		  .call(chart);          //Finally, render the chart!

	  //Update the chart when window resizes.
	  nv.utils.windowResize(function() { chart.update() });
	  return chart;
	});	
	


}

function grafico_barra(data){
	
	
	/*These lines are all chart setup.  Pick and choose which chart features you want to utilize. */
	nv.addGraph(function() {
	  var chart = nv.models.multiBarChart()
	  //.useInteractiveGuideline(true) // dá erro.
      .transitionDuration(350)
      .reduceXTicks(true)   //If 'false', every single x-axis tick label will be rendered.
      .rotateLabels(0)      //Angle to rotate x-axis labels.
      .showControls(true)   //Allow user to switch between 'Grouped' and 'Stacked' mode.
      .groupSpacing(0.1)    //Distance between each group of bars.
    ;


	  chart.xAxis     //Chart x-axis settings
		  .axisLabel('Unid. de Tempo')
		  //.tickFormat(d3.format(',r'));
		  .tickFormat(function(d){return d+1});

	  chart.yAxis     //Chart y-axis settings
		  .axisLabel('Volume (m^3)')
		  .tickFormat(d3.format(',.02f'));

	  d3.select('#chart_barranv')    //Select the <svg> element you want to render the chart in.   
		  .datum(data)         //Populate the <svg> element with chart data...
		  .call(chart);          //Finally, render the chart!

	  //Update the chart when window resizes.
	  nv.utils.windowResize(function() { chart.update() });
	  return chart;
	});	
	


}


function converte_nvd3(cen) {

	var series = [];
		
	  
	//Data is represented as an array of {x,y} pairs.
	for (var tanque in cen.volume){
		var serie = {};
		var xy = [];
		for (var i = 0; i < cen.volume[tanque].length; i++) {
			xy.push({x: i, y: cen.volume[tanque][i]});
		}
		serie['key'] = tanque;
		serie['values'] = xy;
		serie['area'] = true;
		series.push(serie);
		
	}
	
	return series
}

/*
function grafico_gantt(cen){	
	var  qtd_tanques = cen.nome_tanques.length;
	var height = 300,
        left = 100,
		width = 900,
		margin = 25,
        row_height = 30,
        row_space = 5,
		x_axis_length = width -  margin-left
        y_axis_length = qtd_tanques*(row_height+row_space),
        chart_height = y_axis_length + 2*margin
        ;
        //y_axis_length = height - 2*margin;
		
	var x = d3.scale.linear()
        .domain([0, cen.num_unid_tempo])
        .range([0,x_axis_length])
        ;

//    var y = d3.scale.linear()
//        .domain([cen.qtd_tanques+1, 1])
//        .range([0, y_axis_length]);

    var y = d3.scale.ordinal()
        .domain([y_axis_length,0])
        .range([0,y_axis_length]);
        
    var svg = d3.select('svg#chart_gantt')
		.attr('class','axis')
		.attr('width', width)
		.attr('height', chart_height)
        ;
	
    var row = svg.selectAll('.row')
        .data(cen.nome_tanques)
        .enter()
        .append('svg:g')
        
        .attr('id', function(d){return 'row-'+d;})
        .attr('tanque', function(d){return d;})
        //.attr('y', function(d,i){return y(i+1);})
        //.attr('y', y(30))
        .attr('class', 'row')
        .attr('transform', function(d,i){
            return 'translate('+(left)+','+(i)*(row_height+row_space)+')'; 
        
        });


    var col = row.selectAll('.estado')
    .data(function (d,i) {return cen.situacao[cen.nome_tanques[i]]})
    .enter()
    .append('svg:rect')
    .attr('class', function(d){return 'estado estado-'+d.estado})
    .attr('id',function(d,i){return i})
    .attr('inicio',function(d){return d.inicio})
    .attr('fim',function(d){return d.fim})
    .attr('estado',function(d){return d.estado})
    .attr('tam',function(d){return d.tam})
    .attr('x', function(d) {return x(d.inicio)})
    //.attr('y', 150)
    .attr('width', function(d){return x(d.fim+1)-x(d.inicio)})
    .attr('height', row_height);
	





      
    var x_axis = d3.svg.axis()
            .scale(x)
            .orient("bottom");
            
    svg.append("g")       
        .attr("class", "x-axis")
        .attr("transform", function(){ // <-A
            return "translate(" + left + "," + (chart_height - margin) + ")";
        })
        .call(x_axis);
        
    d3.selectAll("g.x-axis g.tick") // <-B
        .append("line") // <-C
            .classed("grid-line", true)
            .attr("x1", 0) // <-D
            .attr("y1", 0)
            .attr("x2", 0)
            .attr("y2", - y_axis_length);  // <-E
    
    
    
    var y_axis = d3.svg.axis()
            .scale(y)
            .orient("left");
        
    svg.append("g")       
        .attr("class", "y-axis")
        .attr("transform", function(){
            return "translate(" + left + "," + margin + ")";
        })
        .call(y_axis);
        
    d3.selectAll("g.y-axis g.tick")
        .append("line")
            .classed("grid-line", true)
            .attr("x1", 0)
            .attr("y1", 0)
            .attr("x2", x_axis_length) // <-F
            .attr("y2", 0);
} 
*/

function gantt_d3(cen){
    
    tasks = []
    for (k in cen.situacao){
        for(var i in d3.range(cen.situacao[k].length)){
            sit = cen.situacao[k][i];
            tasks.push({
                'taskName':k, 
                'status':sit.estado,
                'inicio': sit.inicio,
                'fim': sit.fim,
                'tam': sit.tam});
        }
    
    }
    
	var taskStatus = {
		"rec" : "estado-rec",
		"env" : "estado-env",
		"emp" : "estado-emp",
		"par" : "estado-par",
        'pre': 'estado-pre'
	};

	//var taskNames = [ "D Job", "P Job", "E Job", "A Job", "N Job" ];
    taskNames = cen.nome_tanques;
/*
	tasks.sort(function(a, b) {
		return a.endDate - b.endDate;
	});
	var maxDate = tasks[tasks.length - 1].endDate;
	tasks.sort(function(a, b) {
		return a.startDate - b.startDate;
	});
	var minDate = tasks[0].startDate;

	var format = "%H:%M";
*/
	var gantt = d3.gantt().taskTypes(taskNames).taskStatus(taskStatus);//.tickFormat(format);
	gantt(tasks);

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
						// variável global para debug!
						cenario = data
						
						datum = converte_nvd3(data);
						grafico_linha(datum);
						grafico_area(datum);
						grafico_barra(datum);
						//grafico_gantt(data);
						gantt_d3(data);
					},
					error: function(jqXHR, textStatus, errorThrown) 
					{
						//if fails      
					}
				});
		e.preventDefault(); //STOP default action
	});

});


