function topDailyCategories(a,b){
        
var width = a,
    height = b,
    format = d3.format(",d"),
    color = d3.scale.category20c();

var picture = d3.layout.pack()
    .sort(null)
    .size([width, height])
    .padding(1.5);

var svg = d3.select(".topDailyCategories").append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("class", "topDailyCategories");

var data = {{categories|tojson|safe}};

d3.json(data, function(error, root) {
  root = data;
  console.log(root);
  var node = svg.selectAll(".node")
      .data(picture.nodes(classes(root))
      .filter(function(d) { return !d.children; }))
      .enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });


  node.append("title")
      .text(function(d) { return d.categoryName + ": " + format(d.value); });

  node.append("circle")
      .attr("r", function(d) { return d.r; })
      .style("fill", function(d) {
             var rgbScale = d3.scale.linear().domain([-10,0,10]).range(["#A396EC", "#96BBEC", "#96ECEB"]);
             return rgbScale(d.color);

      })
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
    if (node.topDailyCategories) 
           node.topDailyCategories.forEach(function(child) { recurse(node.name, child); });
    else 
           classes.push({
                  packageName: "", 
                  className: node.categoryName, 
                  value: node.mentions, 
                  color: node.sentiment
           });
  }
  recurse(null, root);
  return {children: classes};
}

d3.select(self.frameElement).style("height", height + "px");
}