// ------------------------------------------------------ //
// This function begins the experiment
function startup() {

	// construct stimulus set
	var Color = linspace(25, 230, 9);
	var Size = linspace(3.0, 5.8, 9);
	stimuli = new StimulusSet(Color, Size);
	stimuli.make_stimuli()
	
	// load templates
	load_template("html/templates/observe.html", observation);
	load_template("html/templates/generate.html", generation);
	load_template("html/templates/generalize.html", generalization);

	// get start time
	data.info.start = Date.now();

	// save the data
	savedata(data)

	// BEGIN EXPERIMENT
	inserthtml(observation.instructions);
};

// ------------------------------------------------------ //
// This function finishes the experiment
function finishup() {

	// store finish time
	data.info.finish = Date.now();

	// send data to server
	savedata(data);
	markcomplete();

	stage.style.visibility = 'visible';

	// load submission UI
	inserthtml('html/submit.html')
	
}



