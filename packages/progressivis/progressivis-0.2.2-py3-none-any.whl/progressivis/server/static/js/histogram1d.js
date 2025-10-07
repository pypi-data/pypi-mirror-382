var histogram1d = function() {

  var hist = chart();

  function ready(){
    refresh = histogram1d_refresh;
    module_ready();
  }

  function histogram1d_refresh() {
    module_get(update, error);
  }

  function update(data) {
    module_update(data);

    hist = hist.histogram(process_histogram(data.histogram));
    hist.width(600).height(400);
    hist(d3.select("#histogram1d"));
  }

  function error(err) {
    console.log(err);
  }

  /**
   * Converts a Progressivis-style histogram into a d3-style histogram.
   *
   * @param prohist - a Progressivis-style histogram, i.e. an object
   * that contains a n-sized array "values" (histogram frequencies)
   * and a n+1-sized array "edges" (bin edges)
   *
   * @return a d3-style histogram
   */
  function process_histogram(prohist){
    return prohist.values.reduce(function(acc, val, idx, arr){
      // x: lower bound
      // dx: bin width
      // y: bin count
      acc.push({x: prohist.edges[idx], 
                dx: prohist.edges[idx+1] - prohist.edges[idx], 
                y: val});
      return acc;
    }, []);
  }

  /**
   * Histogram; this is the encapsulated component.
   */
  function chart(){
    var histogram = [];
    var margin = { top: 10, bottom: 25, left: 45, right: 15};
    var width = 400; 
    var innerWidth = width - margin.left - margin.right;
    var height = 100;
    var innerHeight = height - margin.top - margin.bottom;
    var xScale = d3.scaleLinear();
    var yScale = d3.scaleLinear();

    function my(selection){
      selection.each(function() {
        //set up scales and svg element
        xScale.domain([histogram[0].x,
                       histogram[histogram.length-1].x + histogram[histogram.length-1].dx])
              .range([0,innerWidth]);
        yScale.domain([0, d3.max(histogram, function(d){ return d.y; })])
              .range([innerHeight,0]);
        var xAxis = d3.axisBottom(xScale);
        var yAxis = d3.axisLeft(yScale).ticks(5);
        
        var svg = d3.select(this).selectAll("svg").data([histogram])
              .enter().append("svg")
              .attr("width", width)
              .attr("height", height);
        var gEnter = svg.append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        //draw bars
        var bar = gEnter.selectAll(".bar").data(histogram);
        bar.enter().append("rect")
          .attr("class", "bar")
          .attr("x", function(d) { return xScale(d.x); })
          .attr("y", function(d) { return yScale(d.y); })
          .attr("width", function(d){ return xScale(d.x + d.dx) - xScale(d.x); })
          .attr("height", function(d) { return innerHeight - yScale(d.y); });

        //draw axes
        var x = svg.selectAll(".x").data([histogram])
           .enter()
           .append("g")
           .attr("class", "x axis")
           .attr("transform", "translate(" + margin.left + "," + (innerHeight + margin.top) + ")");
        x.call(xAxis);

        var y = svg.selectAll(".y").data([histogram])
           .enter()
           .append("g")
           .attr("class", "y axis")
           .attr("transform", "translate(" + margin.left + ", " + margin.top + ")");

        y.call(yAxis);
      });
    }

    my.width = function(value){
      if(!arguments.length){
        return width;
      }
      width = +value;
      innerWidth = width - margin.left - margin.right;
      return my;
    };

    my.height = function(value){
      if(!arguments.length){
        return height;
      }
      height = +value;
      innerHeight = height - margin.top - margin.bottom;
      return my;
    };

    my.histogram = function(value){
      if(!arguments.length){
        return histogram;
      }
      histogram = value;
      return my;
    };

    return my;
  }

  return {
    ready: ready,
    chart: chart,
    process_histogram: process_histogram
  };
}();
