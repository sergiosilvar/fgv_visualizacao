/**
 * @author Dimitry Kudrayvtsev
 * @version 2.1
 */

d3.gantt = function() {

    var FIT_TIME_DOMAIN_MODE = "fit";
    var FIXED_TIME_DOMAIN_MODE = "fixed";
    
    var margin = {
	top : 25,
	right : 25,
	bottom : 25,
	left : 25
    };

	var timeDomainStart = 0;
	var timeDomainEnd = 29;

    var timeDomainMode = FIT_TIME_DOMAIN_MODE;// fixed or fit
    var taskTypes = [];
    var taskStatus = [];
    
    var height = 300 - margin.top - margin.bottom-5;
	
	//var width = 900 - margin.right - margin.left-5;
    var width = 780;
    

    var keyFunction = function(d) {
		return d.inicio + d.taskName + d.fim;
    };

    var rectTransform = function(d) {
		//return "translate(" + x(d.startDate) + "," + y(d.taskName) + ")";
		return "translate(" + x(d.inicio) + "," + y(d.taskName) + ")";
    };


    var initTimeDomain = function(tasks) {
		if (timeDomainMode === FIT_TIME_DOMAIN_MODE) {
			if (tasks === undefined || tasks.length < 1) {
				timeDomainStart = 0;
				
				timeDomainEnd = tasks[tasks.length-1].fim+1;
				
				return;
			}
			
			tasks.sort(function(a, b) {
			return a.fim  - b.inicio;
			});
			timeDomainEnd = tasks[tasks.length-1].fim+1;
			tasks.sort(function(a, b) {
				return a.fim - b.inicio;
			});
			timeDomainStart = 0;
			
		}
    };

    var initAxis = function() {
		x = d3.scale.linear().domain([ timeDomainStart, timeDomainEnd ]).range([ 0, width ]).clamp(true);
		
		y = d3.scale.ordinal().domain(taskTypes).rangeRoundBands([ 0, height - margin.top - margin.bottom ], .1);
		xAxis = d3.svg.axis().scale(x).orient("bottom").tickSubdivide(true);//.tickFormat(d3.time.format(tickFormat)).tickSubdivide(true).tickSize(8).tickPadding(8);

		yAxis = d3.svg.axis().scale(y).orient("left").tickSize(0);
    };

    function gantt(tasks) {
	
		initTimeDomain(tasks);
		initAxis();
		
		// Remover os anteriores.
		d3.selectAll('.gantt-chart').remove();
		
		var svg = d3.select('#chart_ganttd3')
		.append("g")
		.attr("class", "gantt-chart")
		.attr("height", height + margin.top + margin.bottom)
		.attr("transform", "translate(" + 100/*margin.left*/ + ", " + margin.top + ")");
		
		var div = svg.append('div')
			.attr('class', 'tooltip')
			.style('opacity', 0);
		
		chartgantt = svg.selectAll(".chartgantt")
		

		
		chartgantt.data(tasks, keyFunction)
		.enter()
		.append("rect")
		.attr("rx", 0)
		.attr("ry", 0)
		.attr("class", function(d){ 
			return taskStatus[d.status];
		 }) 
		.attr("y", 0)
		.attr("transform", rectTransform)
		.attr("height", function(d) { return y.rangeBand(); })
		.attr("width", function(d) { 
			return (x(d.fim+1) - x(d.inicio)); 
		 })
		.attr('tanque', function(d){
			return d.taskName;
		})
		.attr('estado', function(d){
			return d.status;
		})
		.attr('inicio', function(d){
			return d.inicio;
		})
		.attr('tam', function(d){
			return d.tam;
		})
		.attr('fim', function(d){
			return d.fim;
		})
		.on("mouseover", function(d) {
            div.transition()        
                .duration(200)      
                .style("opacity", .9);      
            div .html('Texto ' + "<br/>"  + 'xxxx')  
                .style("left", (d3.event.pageX) + "px")     
                .style("top", (d3.event.pageY - 28) + "px");    
        })                  
        .on("mouseout", function(d) {       
            div.transition()        
                .duration(500)      
                .style("opacity", 0)
        })
		;

		 
		svg.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0, " + (height - margin.top - margin.bottom) + ")")
		.transition()
		.call(xAxis);

		svg.append("g").attr("class", "y axis").transition().call(yAxis);

		return gantt;

    };
	

	
/*  //Não está sendo utilizado.
    gantt.redraw = function(tasks) {

		initTimeDomain(tasks);
		initAxis();
		
			var svg = d3.select("svg");

			var ganttChartGroup = svg.select(".gantt-chart");
			var rect = ganttChartGroup.selectAll("rect").data(tasks, keyFunction);
			
			rect.enter()
			 .insert("rect",":first-child")
			 .attr("rx", 0)
			 .attr("ry", 0)
		 .attr("class", function(d){ 
			 if(taskStatus[d.status] == null){ return "bar";}
			 return taskStatus[d.status];
			 }) 
		 .transition()
		 .attr("y", 0)
		 .attr("transform", rectTransform)
		 .attr("height", function(d) { return y.rangeBand(); })
		 .attr("width", function(d) { 
			 return (x(d.endDate) - x(d.startDate)); 
			 });

			rect.transition()
			  .attr("transform", rectTransform)
		 .attr("height", function(d) { return y.rangeBand(); })
		 .attr("width", function(d) { 
			 return (x(d.endDate) - x(d.startDate)); 
			 });
			
		rect.exit().remove();

		svg.select(".x").transition().call(xAxis);
		svg.select(".y").transition().call(yAxis);
		
		return gantt;
    };
*/
    gantt.margin = function(value) {
	if (!arguments.length)
	    return margin;
	margin = value;
	return gantt;
    };

    gantt.timeDomain = function(value) {
		if (!arguments.length)
			return [ timeDomainStart, timeDomainEnd ];
		timeDomainStart = +value[0], timeDomainEnd = +value[1];
		return gantt;
    };

    /**
     * @param {string}
     *                vale The value can be "fit" - the domain fits the data or
     *                "fixed" - fixed domain.
     */
    gantt.timeDomainMode = function(value) {
		if (!arguments.length)
			return timeDomainMode;
		timeDomainMode = value;
		return gantt;

    };

    gantt.taskTypes = function(value) {
		if (!arguments.length)
			return taskTypes;
		taskTypes = value;
		return gantt;
    };
    
    gantt.taskStatus = function(value) {
		if (!arguments.length)
			return taskStatus;
		taskStatus = value;
		return gantt;
    };

    gantt.width = function(value) {
		if (!arguments.length)
			return width;
		width = +value;
		return gantt;
    };

    gantt.height = function(value) {
		if (!arguments.length)
			return height;
		height = +value;
		return gantt;
    };

    gantt.tickFormat = function(value) {
		if (!arguments.length)
			return tickFormat;
		tickFormat = value;
		return gantt;
    };


    
    return gantt;
};
