function wordcloud(data){      
      var w = 350;
      var h = 100;
      var fill = d3.scale.category20c();

      d3.layout.cloud().size([w, h])
          .words(data)
          .padding(10)
          .rotate(function() { return ~~(Math.random() * 1) * 90; })
          .font("Impact")
          .fontSize(function(d) { return d.size; })
          .on("end", draw)
          .start();

      function draw(words) {
        d3.select("#wordCloud").append("svg")
            .attr("width",w)
            .attr("height",h)
            .append("g")
            .attr("transform", "translate(500,180)")
            .selectAll("text")
            .data(words)
            .enter().append("text")
            .style("font-size", function(d) { return d.size*5 + "px"; })
            .style("font-family", "Impact")
            .style("fill", function(d, i) { return fill(i); })
            .attr("text-anchor", "middle")
            .attr("transform", function(d) {
              return "translate(" + [d.x*1.1, d.y*1.1] + ")rotate(" + d.rotate + ")";
            })
            .text(function(d) { return d.text; })
            .on('mouseover', function(d){
                    var word = d3.select(this).style({opacity:'0.8'});
                    word.select(d.size).style({opacity:'1.0'});                
               })
             .on('mouseout', function(d){
              d3.select(this).style({opacity:'1.0',})
              d3.select(d.text).style({opacity:'1.0'});
            });
             
      };
};