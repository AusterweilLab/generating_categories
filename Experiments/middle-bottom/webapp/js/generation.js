function generate() {
	stage.innerHTML = '';	

	// some function globals
	var dupemessage;
	var continuebutton;
	var stimulusdiv;
	var color_control
	var size_control


	// function to start a new trial
	function init() {

		// replace existing ui.
		stage.innerHTML = generation.ui;
		stage.style.visibility = 'hidden'; // hide everything during setup

		// define UI elements
		continuebutton = document.getElementById('continuebutton');
		stimulusdiv = document.getElementById('stimulus');
		dupemessage = document.getElementById('dupemessage');
		color_control = document.getElementById('color_control');
		size_control = document.getElementById('size_control');

		// configure controls
		size_control.setAttribute('max', stimuli.side-1);
		color_control.setAttribute('max', stimuli.side-1);

		// assign functions
		continuebutton.onclick = function() { end_trial() };
		size_control.oninput =  function() { generate_handler() };
		color_control.oninput =  function() { generate_handler() };

		// draw ui, start interface after delay
		setTimeout( function() {
				stage.style.visibility = 'visible' // show ui
				timer = Date.now(); // start timer
		 }, generation.isi	)
	}


	function generate_handler() {

		// get values of color / size
		var values = {
			color: stimuli.color[color_control.value],
			size: stimuli.size[size_control.value]
		};

		// find new stimulus, check if it is in the generated list
		generation.stimulus = stimuli.plookup(values.color, values.size)[0];

		// check for dupes, draw new stimulus
		duplicate_handler();
		generation.stimulus.draw(stimulusdiv);
		
	}

	// function to hide continue button, display dupe message if needed
	function duplicate_handler() {

		if ( generation.generated.includes(generation.stimulus.id) ) {
			dupemessage.style.visibility = 'visible';
			continuebutton.style.visibility = 'hidden';
		} else {

			dupemessage.style.visibility = 'hidden';
			continuebutton.style.visibility = 'visible';
		}

	}

	function end_trial() {
		generation.rt = Date.now() - timer; // set rt

		// add stimulus to generated list
		generation.generated.push(generation.stimulus.id);

		// add a row of data
		data.generation[generation.counter] = {
			trial: generation.counter,
			stimulus: generation.stimulus.id,
			rt: generation.rt,
		};

		// add one to counter
		generation.counter += 1;

		if (generation.counter >= generation.ntrials) {
			savedata(data);
			inserthtml(generalization.instructions);

		// start next trial	
		} else { init() }


	}

	// start first trial
	init();
}
