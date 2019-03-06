// ------------------------------------------------------ //
// This function begins the experiment
function startup() {

	// construct stimulus set
	stimsteps = 50
	var Color = linspace(25, 230, stimsteps);
	var Size = linspace(3.0, 5.8, stimsteps);
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
	//inserthtml(generalization.instructions)
	//inserthtml(generation.instructions[data.info.gentype])			
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



