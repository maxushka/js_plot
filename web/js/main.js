		var plot = $.plot("#placeholder", [ [getRandomData()] ], {
			series: {
                shadowSize: 0	// Drawing is faster without shadows
			},
			yaxis: {
				min: 0,
				max: 100
			},
			xaxis: {
				show: false
			}
		});

$(document).ready(function() {
	websocket = create_connection_websocket();



});

function getRandomData() {
	var data = [], totalPoints = 300;
	if (data.length > 0)
		data = data.slice(1);
	// Do a random walk
	while (data.length < totalPoints) {
		var prev = data.length > 0 ? data[data.length - 1] : 50,
			y = prev + Math.random() * 10 - 5;
		if (y < 0) {
			y = 0;
		} else if (y > 100) {
			y = 100;
		}
		data.push(y);
	}
	// Zip the generated y values with the x values
	var res = [];
	for (var i = 0; i < data.length; ++i) {
		res.push([i, data[i]])
	}
	return res;
}


	// $(function() {
	// 	var data = [], totalPoints = 300;
	// 	// Set up the control widget
	// 	var plot = $.plot("#placeholder", [ getRandomData() ], {
	// 		series: {
 //                shadowSize: 0	// Drawing is faster without shadows
	// 		},
	// 		yaxis: {
	// 			min: 0,
	// 			max: 100
	// 		},
	// 		xaxis: {
	// 			show: false
	// 		}
	// 	});

	// 	function update() {

	// 		plot.setData([getRandomData()]);
	// 		// Since the axes don't change, we don't need to call plot.setupGrid()
	// 		plot.draw();
	// 		setTimeout(update, 30);
	// 	}

	// 	update();

	// 	// Add the Flot version string to the footer

	// });





function ws_receive_string(data) {
	// body...
}

function ws_receive_bytes(data) {
	// body...
}


function create_connection_websocket() {

	var socket = new WebSocket("ws://"+window.location.hostname+":8765");

	socket.onopen = function(e) {
		console.log("Connect to server");
	};

	socket.onmessage = function(event) {
		var data = JSON.parse(event.data);
		try{

			console.log(data.arr)
			let res = [];
			for (var i = 0; i < data.arr.length; ++i) {
				res.push([i, data.arr[i]])
			}
			plot.setData([res]);
			plot.draw();
		}
		catch{
			console.log('error')
		}
	};

	socket.onclose = function(event) {
		console.log('Server disconnect');
	};

	socket.onerror = function(error) {
		console.log(`[error] ${error.message}`);
	};
	return socket;
}