//SERVER AND SOCKET
var http = require('http');
var io = require('socket.io')(http);
var socket_server = http.createServer();
var web_server = http.createServer(handleRequest);
var dispatcher = require('httpdispatcher');
var sizeof = require('sizeof');
var fs = require('fs');
var ip, os = require('os'), ifaces = os.networkInterfaces();

// Iterate over interfaces ...
for (var dev in ifaces) {

    // ... and find the one that matches the criteria
    var iface = ifaces[dev].filter(function(details) {
        return details.family === 'IPv4' && details.internal === false;
    });

    if(iface.length > 0) ip = iface[0].address;
}

 
//YOUR HOST MACHINE'S IP ADDRESS FOR THE SLAVES/REMOTE MACHINES TO CONNECT TO-----------------------------------------------------
//HARDCODE YOUR IP ADDRESS HERE---------------------------------
//ip = '192.168.2.142';
var socket_port = 8081;
var web_port = 8080;
//---------------------------------------------------------------------------------------------------------------------------------
socket_server.listen(socket_port, ip);

var socket = io.listen(socket_server);

var incoming_address;

var accesslist = [];
accesslist.push('localhost');

//LOG STRUCTURE
//logs = array of machine objects
//machine object = name and data_array
//data_array = array of gpu_data arrays
//gpu_data array = array of arrays for each gpu's data
var logs = [];



//Lets use our dispatcher
function handleRequest(request, response){
    try {
        //Disptach
        dispatcher.dispatch(request, response);
        
		dispatcher.onGet("/", function(req, res) {

		     fs.readFile('index.html',function (err, data){
		        res.writeHead(200, {'Content-Type': 'text/html','Content-Length':data.length});
		        res.write(data);
		        res.end();
		    });
		});   

		dispatcher.onGet("/graphs", function(req, res) {

		     fs.readFile('graphs.html',function (err, data){
		        res.writeHead(200, {'Content-Type': 'text/html','Content-Length':data.length});
		        res.write(data);
		        res.end();
		    });
		});  

		dispatcher.onGet("/ip", function(req, res) {

		     fs.readFile('ip.html',function (err, data){
		        res.writeHead(200, {'Content-Type': 'text/html','Content-Length':data.length});
		        res.write(data);
		        res.end();
		    });
		});  

		if(request.url.indexOf('.css') >= 0)
		{
			 fs.readFile(request.url , function (err, data){
			 	if(data)
			 	{
			 		response.writeHead(200, {'Content-Type': 'text/css','Content-Length':data.length});
			        response.write(data);
			        response.end();	
			 	}
		    });
		}
		else if(request.url.indexOf('.js') >= 0)
		{
			 fs.readFile(request.url , function (err, data){
			 	if(data)
			 	{
			 		response.writeHead(200, {'Content-Type': 'text/javascript','Content-Length':data.length});
			        response.write(data);
			        response.end();	
			 	}
			 });
		}
		else if(request.url.indexOf('.html') >= 0)
		{
			fs.readFile(request.url , function (err, data){
			 	if(data)
			 	{
			 		response.writeHead(200, {'Content-Type': 'text/html','Content-Length':data.length});
			        response.write(data);
			        response.end();	
			 	}
			 });
		}


		dispatcher.onGet("/logs", function(req, res) {
		    res.writeHead(200, {'Content-Type': 'application/json'});
		    var json = JSON.stringify(logs);
		    res.end(json);
		});    

		//A sample POST request
		dispatcher.onPost("/addIP", function(req, res) {
		    var ip = req.params.IP;
		    if(ip.length > 0){
		    	var index = accesslist.indexOf(req.params.IP );
				if( index < 0)
				{
					accesslist.push(ip);
					console.log('added')
				}
		    }
		    res.writeHead(200, {'Content-Type': 'application/json'});
		    res.end(JSON.stringify('success'));
		});

		//A sample POST request
		dispatcher.onGet("/getIPs", function(req, res) {
		    res.writeHead(200, {'Content-Type': 'application/json'});
		    var json = JSON.stringify(accesslist);
		    res.end(json);
		});

		//A sample POST request
		dispatcher.onPost("/deleteIP", function(req, res) {
			var ip = req.params.IP;
			if(ip.length > 0)
			{
				var index = accesslist.indexOf(req.params.IP );
				if( index > -1)
				{
					accesslist.splice(index, 1);
					console.log('removed');
				}
			}
			res.writeHead(200, {'Content-Type': 'application/json'});
		    res.end(JSON.stringify('success'));
		});

    } catch(err) {
        console.log(err);
    }
}


web_server.listen(web_port, function(){
    //Callback triggered when server is successfully listening. Hurray!
    console.log("Web server listening on: http://%s:%d", ip, web_port);
});


io.on('connection', function (socket) {
  console.log('machine connected');
  incoming_address = socket.request.connection.remoteAddress;
  	if(accesslist.indexOf(incoming_address) >= 0)
 	{

	  socket.on('gpu_data', function (msg){
	    parser(msg);
	   });

	  socket.on('disconnect', function(){
	    console.log('user disconnected');
	  });
 	}
});



function parser(data){
	data = JSON.parse(data);

	var isNew = true;

	for(var i = 0; i < logs.length; i++)
	{
		if(logs[i].name == data.machine )
		{
			for(var j = 0; j < logs[i].data_array.length; j++)
			{
				console.log(data.index);
				console.log(logs[i].data_array[j][0].index);

				if(parseInt(logs[i].data_array[j][0].index) == data.index)
				{
					logs[i].data_array[j].push(data);
					console.log('old gpu, new data');
					if(sizeof.sizeof(logs) > 20000000)
					{
						logs[i][data.index].data_array.shift();
					}
					isNew = false;
					break;
				}
			}
		}	
	}

	if(isNew)
	{
		var d_array = [];
		var d = [data];
		d_array.push(d);
		logs.push({'name':data.machine, data_array:d_array});
		console.log('new gpu, new data');
	}
}

