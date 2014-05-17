function sentiment(a,b){
  var chart = c3.generate({
         size: {
                 height: b,
                 width: a
             },
    
    data: {
             x: 'x',
              columns: [
                  ['x', '2013-01-01', '2013-01-02', '2013-01-03', '2013-01-04', '2013-01-05', '2013-01-06', '2013-01-07', '2013-01-08', '2013-01-09', '2013-01-10'],
                  ['SentimientoPositivo', 4, 3, 3, 4, 6, 6,7.5,7,9,10],
                  ['SentimientoNegativo',10, 9, 7, 7, 4, 5,2,3,2,1],
                  ['SentimientoNeutro',4,5,1,7,8,7,6,2,4,8],
                  /*['Menciones',10343,11323,23355,22211,53211,43211,42322,55754,12222,12223]*/
              ],
              type: 'spline',
              axes: {
                          SentimientoPositivo: 'y',
                          SentimientoNegativo: 'y',
                          SentimientoNeutro: 'y',
                          /*Menciones: 'y2',*/
                      },
    },
    axis: {
        x: {
            type: 'timeseries',
            label: 'Periodo',
            position: 'outer-center',
            tick: {
                format: '%Y-%m-%d'
            }
        },
        y: {
                    max: 10,
                    min: 0,
                    label: {
                           text: 'Sentimiento',
                           position: 'outer-middle'
                    }
             },
        y2: {
                    show: false,
                    position: 'outer-middle',
                    label: {
                           text: 'Menciones',
                           position: 'outer-middle',
                    }
                }
    },
    zoom: {
      enabled: true
    },
    subchart: {
            show: true
    },
    grid: {
            x: {
                lines: [{value: '2013-01-05', text: 'Barcenas Imputado'}]
            }
        }
  });
  
  setTimeout(function () {
      chart.toAreaSpline('SentimientoNegativo');
  }, 500);
  setTimeout(function () {
      chart.toAreaSpline('SentimientoPositivo');
  }, 1000);
  setTimeout(function () {
      chart.toAreaSpline('SentimientoNeutro');
  }, 1500);

  /*setTimeout(function () {
      chart.toAreaSpline('Menciones');
  }, 6000);*/
}