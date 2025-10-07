var socket = null,
    handshake = false,
    protocol = null,
    progressivis_run_number,
    progressivis_data,
    refresh, error;

function ack(json) {
    if (json.type == "pong")
        console.log("Ack received");
    else
        console.log("Unexpected reply");
    handshake = true;
}

function progressivis_websocket_open(msg, handler, refresh) {
    //socket = new WebSocket("ws://" + document.domain + ":5000/websocket/", "new");
    socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function() {
        socket.emit('join', {"type": "ping", "path": msg}, function(x){ack(x);refresh();});
    });
    socket.on('disconnect', function() { handshake = false; });
    socket.on('tick', function(msg) {
        console.log('socketio tick');
        if (handler) handler(msg);
        return 1;
    });
}

function progressivis_update(data) {
    progressivis_data = data;
    progressivis_run_number = data['run_number'];
    $('#run_number').text(progressivis_run_number);
}

function progressivis_websocket_submit(text) {
    if (handshake == true)
        socket.send(text);
}

function layout_dict(dict, order, value_func={}) {
    var i, k, v, layout = '';

    if (! order)
	order = Object.keys(dict).sort();
    layout += '<dl class="dl-horizontal">';
    for (i = 0; i < order.length; i++) {
	k = order[i];
	v = dict[k];
	layout += ' <dt>'+k.toString()+':</dt>';
	layout += ' <dd>';
    if(value_func[k]){
	    layout += value_func[k](v);            
    } else {
	    layout += layout_value(v);
    }
	layout += '</dd>';
    }
    layout += '</dl>';
    return layout;
}

function escapeHTML(s) {
    return $('<div>').text(s).html();
}

function layout_value(v) {
    var i, layout = "";
    if (v == null) return "";
    if (Array.isArray(v)) {
	if (v.length === 0) return "";
	for (i = 0; i < v.length; i++) {
	    if (layout.length != 0)
		layout += "<br>";
	    layout += layout_value(v[i]);
	}
        return layout;
    }
    if (typeof(v) === "string" && v.startsWith('<div')) {
        return v;
    }
    if (typeof(v) === "object") {
	var keys = Object.keys(v);
	if (keys.length == 0) return "";
	return layout_dict(v, keys.sort());
    }
    return escapeHTML(v.toString()); // escape
}

function progressivis_post(path, success, error, param) {
    var init = {method: "POST"},
        url = $SCRIPT_ROOT+path;
    if (param) {
        url += '/'+param;
    }
    return fetch(url, init)
        .then(response => response.json())
        .then(success)
        .catch(error);
}

function progressivis_get(path, success, error, param) {
    if (handshake) {
        console.log("socketio request "+path);
        return new Promise((resolve, reject) =>
                           param ? socket.emit(path, param, resolve)
                           : socket.emit(path, resolve))
            .then(success)
            .catch(error);
    }
    else {
        console.log("Ajax request "+path);
        return progressivis_post(path, success, error, param);
    }
}

function b64(e) {
    var t="",
        n=new Uint8Array(e),
        r=n.byteLength,
        i;
    for(i=0;i<r;i++) {
        t+=String.fromCharCode(n[i]);
    }
    return window.btoa(t);
}

function progressivis_get_image(path, success, error, param) {
    return progressivis_get(path, (data) => {
        var img = new Image(),
            src = "data:image/png;base64,"+b64(data.image);
        img.setAttribute("src", src);
        return img;
    },
                     error, param);
}

function progressivis_start(success, error) {
    progressivis_get('/progressivis/scheduler/start', success, error);
}

function progressivis_stop(success, error) {
    progressivis_get('/progressivis/scheduler/stop', success, error);
}

function progressivis_step(success, error) {
    progressivis_get('/progressivis/scheduler/step', success, error);
}

function progressivis_error(ev, msg) {
    var contents = '<div class="alert alert-danger alert-dismissible" role="alert">Error: ';
    if (msg)
        contents += msg;
    contents += '</div>';
  $('#error').html(contents);
}

function progressivis_socketmsg(json) {
    var run_number = json.run_number;
    if (refresh == null) {
        console.log('ERROR: refresh is not defined');
        return;
    }

    if (run_number > progressivis_run_number) {
        progressivis_run_number = run_number;
        refresh(json);
    }
}

function progressivis_ready(socket_name) {
    if (error === null) 
        error = progressivis_error;
    if (refresh === null) {
        console.log('ERROR: refresh is not defined');
    } else {
        progressivis_websocket_open(socket_name, progressivis_socketmsg, refresh);
    }
    $('#start').click(function() { progressivis_start(refresh, error); });
    $('#stop' ).click(function() { progressivis_stop (refresh, error); });
    $('#step' ).click(function() { progressivis_step (refresh, error); });
}

//window.addEventListener('visibilitychange', function() {if(!document.hidden){refresh();}});
