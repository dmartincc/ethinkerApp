function categories(a,b){
        
var width= a,
    height= b,
    format = d3.format(",d"),
    color = d3.scale.category20c();

var bubble = d3.layout.pack()
    .sort(null)
    .size([width, height]);

var svg = d3.select(".information").append("svg")
    .attr("width", width)
    .attr("height", height);

d3.json("data/sentiment.json", function(error, root) {
  var node = svg.selectAll(".node")
      .data(bubble.nodes(classes(root))
      .filter(function(d) { return !d.children; }))
      .enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });


  node.append("title")
      .text(function(d) { return d.className + ": " + format(d.value); });

  node.append("circle")
      .attr("r", function(d) { return d.r; })
      .style("fill", function(d) {
             var rgbScale = d3.scale.linear().domain([-10,0,10]).range(["#F8A5A5", "#F8F4A5", "#A5F8AA"]);
             return rgbScale(d.color);

      } )
      .style("stroke", "#AC7676")
      .attr("opacity",".5");

  node.append("text")
      .attr("dy", ".3em")
      .style("text-anchor", "middle")
      .text(function(d) { return d.className.substring(0, d.r / 3); });
});

// Returns a flattened hierarchy containing all leaf nodes under the root.
function classes(root) {
  var classes = [];

  function recurse(name, node) {
    if (node.sentiments) 
           node.sentiments.forEach(function(child) { recurse(node.name, child); });
    else 
           classes.push({
                  packageName: "", 
                  className: node.category, 
                  value: node.totalMentions, 
                  positiveSentiment: node.positiveSentiment, 
                  negativeSentiment: node.negativeSentiment,
                  color: node.positiveSentiment-node.negativeSentiment
           });
  }
  recurse(null, root);
  return {children: classes};
}

d3.select(self.frameElement).style("height", height + "px");
}