// ------------------------------------------------------ //
// This function begins the experiment
function startup() {

	// construct stimulus set
	stimsteps = 9//50
	var Color = linspace(25, 230, stimsteps);
	var Size = linspace(3.0, 5.8, stimsteps);
	//Orientation is a little different.
	//Because it's boundless, we want the same number of stimsteps but the maximum should be one step less than the minumum (otherwise they'd be the same value)
	var Orientation = linspace(0,Math.PI*2,stimsteps+1);
	Orientation = Orientation.slice(0,Orientation.length-1)

	if (data.info.stimtype=='Squares'){
		stimuli = new StimulusSet(Color, Size);
	} else if (data.info.stimtype=='Circles'){
		stimuli = new StimulusSet(Orientation, Size);
	}
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



