function sentiment(a,b){
  var margin = {top: 10, right: 80, bottom: 100, left: 40},
      margin2 = {top: 430, right: 80, bottom: 50, left: 0},
      width = a - margin.left - margin.right,
      height = b - margin.top - margin.bottom,
      height2 = b - margin2.top - margin2.bottom;;

var parseDate = d3.time.format("%Y-%m-%d").parse;

var x  = d3.time.scale().range([0, width]),
    x2 = d3.time.scale().range([0, width]);

var y = y = d3.scale.linear().range([height, 0]),
    y2 = d3.scale.linear().range([height2, 0]);

var xAxis  = d3.svg.axis().scale(x).orient("bottom")
    xAxis2 = d3.svg.axis().scale(x2).orient("bottom"),
    yAxis  = d3.svg.axis().scale(y).orient("left");

var brush = d3.svg.brush().x(x2).on("brush", brushed);

var color = d3.scale.category10();

var line = d3.svg.line()
    .interpolate("basis")
    .x(function(d) {return x(d.date); })
    .y(function(d) { return y(d.sentiment); });

var line2 = d3.svg.line()
    .interpolate("monotone")
    .x(function(d) { return x2(d.date); })
    .y(function(d) { return y2(d.mentions); });

var svg = d3.select(".information").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("class", "focus")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var svg2 = d3.select(".information").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height2 + margin2.top + margin2.bottom)
    .append("g")
    .attr("class", "context")
    .attr("transform", "translate(" + margin.left + "," + margin2.top + ")");


/*var context = svg.append("g")
    .attr("class", "context")
    .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");*/

d3.json("/static/data/sentiment.json", function(error, data) {
  color.domain(d3.keys(data[0]).filter(function(key) { return key !== "dateSentiment"; }));

  data.sentiments.forEach(function(d) {
    d.dateSentiment = parseDate(d.dateSentiment);
  });

  var positiveSentiment = ({name: "Positive",values: []});
  var negativeSentiment = ({name: "Negative",values: []});
  var neutralSentiment = ({name: "Neutral",values: []});
  var mentions = ({name: "Mentions",values: []});
  var dateDomain = [];

  data.sentiments.forEach(function(d){
    positiveSentiment.values.push({"date": d.dateSentiment, "sentiment": +d.positiveSentiment});
    negativeSentiment.values.push({"date": d.dateSentiment, "sentiment": +d.negativeSentiment});
    neutralSentiment.values.push({"date": d.dateSentiment, "sentiment": +d.neutralSentiment});
    mentions.values.push({"date": d.dateSentiment, "mentions": +d.totalMentions});
    dateDomain.push(d.dateSentiment);
    
  });
  sentiments = [positiveSentiment,negativeSentiment];
  mentionTotales = [mentions];

  x.domain([d3.min(dateDomain),d3.max(dateDomain)]);
  
  y.domain([
    d3.min(sentiments, function(c) { return d3.min(c.values, function(v) { return v.sentiment; }); }),
    d3.max(sentiments, function(c) { return d3.max(c.values, function(v) { return v.sentiment; }); })
  ]);

  x2.domain(x.domain());
  y2.domain(y.domain());
  y2.domain([
    d3.min(mentions, function(c) { return d3.min(c.values, function(v) { return v.mentions; }); }),
    d3.max(mentions, function(c) { return d3.max(c.values, function(v) { return v.mentions; }); })
  ]);

  /*IMPRESIÓN DE LOS EJES*/
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);
  svg2.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height2 + ")")
      .call(xAxis2);
  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("SENTIMENT ANALYSIS");

  /*IMPRESION DE SENTIMIENTOS*/
  var city = svg.selectAll(".sentiments")
      .data(sentiments)
      .enter().append("g")
      .attr("class", "sentiments");
  
  city.append("path")
      .attr("class", "line")
      .attr("d", function(d) { 
        return line(d.values); 
      })
      .style("stroke", function(d) { return color(d.name); });

  city.append("text")
      .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
      .attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(d.value.sentiment) + ")"; })
      .attr("x", 3)
      .attr("dy", ".35em")
      .text(function(d) { return d.name; });

  /*IMPRESION DE MENCIONES*/
  var city = svg2.selectAll(".mentions")
      .data(mentionTotales)
      .enter().append("g")
      .attr("class", "mentions");
  
  city.append("path")
      .attr("class", "line")
      .attr("d", function(d) { 
        return line2(d.values); 
      })
      .style("stroke", function(d) { return color(d.name); });
  /*context.append("path")
      .data(mentions)
      .attr("class", "area")
      .attr("d", function(d) { 
        return line2(d.values); 
      });

  context.append("g")
      .attr("class", "x brush")
      .call(brush)
      .selectAll("rect")
      .attr("y", -6)
      .attr("height", height2 + 7);*/
});

function brushed() {
  x.domain(brush.empty() ? x2.domain() : brush.extent());
  focus.select(".line").attr("d", line);
  focus.select(".x.axis").call(xAxis);
}
}