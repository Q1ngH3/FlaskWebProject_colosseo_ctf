$(document).ready(function() {
	   var title = {
	      text: 'TOP10趋势图'   
	   };
	   var subtitle = {
	      text: ''
	   };
	   var xAxis = {
		  title: {
			 text: '时间'
		  },
	      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
	         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	   };
	   var yAxis = {
	      title: {
	         text: '总分'
	      },
	      plotLines: [{
	         value: 0,
	         width: 1,
	         color: '#808080'
	      }]
	   };   
	
	   var tooltip = {
	      valueSuffix: '\xB0C'
	   }
	
	   var legend = {
	      layout: 'vertical',
	      align: 'right',
	      verticalAlign: 'middle',
	      borderWidth: 0,
	   };
	
	   var series =  [
	      {
	         name: 'mtctf',
	         data: [0, 1, 2, 3, 4, 5,6,
	            10, 12, 15, 16, 30]
	      }, 
	      {
	         name: 'tmp1',
	         data: [0, 0.8, 1, 1, 5, 10, 24.8,
	            24.8, 24.8, 24.8, 30, 32.5]
	      },
	      {
	         name: 'tmp2',
	         data: [0, 4.2, 5.7, 8.5, 11.9, 15.2, 17.0, 
	            17.6, 19.2, 20.3, 26.6, 34.8]
	      }
	   ];
	
	   var json = {};
	
	   json.title = title;
	   json.subtitle = subtitle;
	   json.xAxis = xAxis;
	   json.yAxis = yAxis;
	   json.tooltip = tooltip;
	   json.legend = legend;
	   json.series = series;
	
	   $('#container').highcharts(json);
	});