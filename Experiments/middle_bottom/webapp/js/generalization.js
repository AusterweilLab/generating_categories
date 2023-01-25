function generalize() {
	stage.innerHTML = '';	

	// make presentation order
	var presentationorder = randperm(stimuli.nstimuli);

	// put elements in div, hide it
	stage.innerHTML = generalization.ui;
	stage.style.visibility = 'hidden';

	// define variables
	var stimulusdiv = document.getElementById('stimulus');
	var alphabutton = document.getElementById('classify_alpha');
	var betabutton  = document.getElementById('classify_beta');

	// define button functions
	alphabutton.onclick = function() {classifyhandler('Alpha')};
	betabutton.onclick = function() {classifyhandler('Beta')};

	// function to set up a single trial
	function init() {

		// get stimulus
		var id = presentationorder[generalization.counter]
		generalization.stimulus = stimuli.ilookup([id])[0]

		// clear out stage
		stimuli.blank.draw(stimulusdiv)
		stage.style.visibility = 'hidden';

		// insert fix cross into stimulus div, then show it
		stimulusdiv.innerHTML = fixcross;
		stimulusdiv.style.visibility = 'visible';

		// wait 1 isi, then draw new items
		setTimeout( function() {
				stimulusdiv.innerHTML = '';		
				generalization.stimulus.draw(stimulusdiv);
				stage.style.visibility = 'visible';
				timer = Date.now(); // start timer
			}, generalization.isi
		);

	};

	function classifyhandler(selection) {
		generalization.rt = Date.now() - timer;

		// add row of data
		data.generalization[generalization.counter] = {	
			trial: generalization.counter,
			stimulus: generalization.stimulus.id, 
			response: selection,
			rt: generalization.rt,
		}

		generalization.counter += 1
		if (generalization.counter == presentationorder.length) {
			savedata(data);
			finishup();

			// start next trial
		} else { 	init()	}

	}

	// start first trial
	init()
}
