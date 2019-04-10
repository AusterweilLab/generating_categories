// Functions to handle communication with servers


// see if the worker is eligible
function checkworker() {
	stage.innerHTML =  "Waiting for server...";

	var args = {
		workerId: worker.workerId,
		Stimuli: data.experiment.Stimuli,
		Experiment: data.experiment.Experiment,
		Paradigm: data.experiment.Paradigm
	}

	$.ajax({
			type: "POST",
			url: "cgi-bin/check-worker.cgi",
			data: JSON.stringify(args),
		}).done( function(o) {
			var res = JSON.parse(o);

			// get assignments for experiment
			if (res.status == 'go') {
				getassignments();

			// show a "return HIT" screen
			} else if (res.status == 'exposed') {
				inserthtml('html/return_message.html');
			}
			
		});
}


// get ID, condition, and counterbalance assignments
function getassignments() {
	$.ajax({
		type: "POST",
		url: "cgi-bin/get-assignments.cgi",
		error: function(x,e){console.log('Some ajax error in getassignments(). ' + x.responseText)}
	}).done( function(o) {
		console.log(o)
		var res = JSON.parse(o);		
		data.info.participant = res.data.participant;
		data.info.condition = res.data.condition;
		data.info.counterbalance = res.data.counterbalance;
		data.info.gentype = res.data.gentype;
		data.info.stimtype = res.data.stimtype;
	  	startup()			
	});
}


// function to mark the worker as exposed 
function markexposed() {

	var args = {
		workerId: worker.workerId,
		Stimuli: data.experiment.Stimuli,
		Experiment: data.experiment.Experiment,
		Paradigm: data.experiment.Paradigm
	}

	$.ajax({
			type: "POST",
			url: "cgi-bin/mark-exposed.cgi",
			data: JSON.stringify(args),
		}).done( function(o) {
			
			var res = JSON.parse(o)

			if (res.status == 'lab') {
				console.log('Hi Nolan!')
				data.info.lab = true;
			} else {
				data.info.lab = false;
			}
		})
}


// function to mark the participant as complete on the server
function markcomplete() {
	$.ajax({
			type: "POST",
		  url: "cgi-bin/mark-complete.cgi",
		  data: JSON.stringify(data.info.participant),
		}).done( function(o) {})
}


// load html template from url into ui field of object
function load_template(url, obj) {
	$.get(url, function( F ) {
    obj.ui = F
	}, 'html'); 
}


// send participant data to server
function savedata(data,asynctf){
	if (typeof asynctf==="undefined"){
		asynctf=true
	}
	$.ajax({
		type: "POST",
		async:asynctf,
		url: "cgi-bin/save-data.cgi",
		data: JSON.stringify(data),
		})
}
