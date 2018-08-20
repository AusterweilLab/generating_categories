function generate() {
	stage.innerHTML = '';	
	
	// some function globals
	var dupemessage;
	var continuebutton;
	var stimulusdiv;
	var color_control
	var size_control

	//reset counter
	generation.counter = 0

	//get category type
	if (session.condition=='bc'){
		generation.category = session.condition[generation.countbc]
		generation.ntrials = generation.ntrialsbase
	} else {
		generation.category = 'b'
		generation.ntrials = generation.ntrialsbase*2
	}

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

		// update category label in instruction
		document.getElementById('categoryID').innerHTML = generation.bcnames[generation.countbc];
		
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
		var counterbase = generation.countbc*generation.ntrialsbase // should be either 0 or 4
		data.generation[session.count][generation.counter+counterbase] = {
			category: generation.category,
			trial: generation.counter+counterbase,
			stimulus: generation.stimulus.id,
			rt: generation.rt,
		};

		// add one to counter
		generation.counter += 1;

		if (generation.counter >= generation.ntrials) {
			savedata(data);
			if (session.condition=='bc' && generation.countbc==0){ //If bc condition, move on to gamma
				generation.countbc += 1 //add to countbc
				inserthtml(generation.instructionsc);
			} else
			{
				if (session.count==0){ //move on to second session
					session.count += 1;
					session.condition = session.types[sessionorderIdx][session.count]
					//reset memory of previously generated examples
					generation.generated = [];
					inserthtml(observation.instructions[session.count]);
				} else { // Else proceed to generalization
					inserthtml(generalization.instructions);
				}
			}
		// start next trial	
		} else { init() }


	}

	// start first trial
	init();
}
