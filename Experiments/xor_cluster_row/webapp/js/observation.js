function observe() {
	stage.innerHTML = '';	

	// set observation items
	observation.alphas = exemplars[data.info.condition];

	// make presentation order
	var presentationorder = []
	for (var blocknum = 0; blocknum < observation.nblocks; blocknum++) {
			presentationorder.push.apply(
				presentationorder, shuffle(observation.alphas)
			);
	}

	// put elements in div, hide it
	stage.innerHTML = observation.ui;
	stage.style.visibility = 'hidden';

	// define some frequently used DOM elements
	var stimulusdiv = document.getElementById('stimulus')
	var continuebutton = document.getElementById('continuebutton')

	// ---------------------------------
	// function executed prior to each observation trial
	function init() {

		// get trial info
		var id = presentationorder[observation.counter]
		observation.stimulus = stimuli.ilookup([id])[0]

		// clear out stage
		stimuli.blank.draw(stimulusdiv)
		stage.style.visibility = 'hidden';

		// insert fix cross into stimulus div, then show it
		stimulusdiv.innerHTML = fixcross;
		stimulusdiv.style.visibility = 'visible';

		// mark participant as exposed to stimuli
		if (observation.counter == 0) {
			markexposed();
			data.info.exposed = true;
			savedata(data);
		}

		
		// wait 1 isi, then draw new items
		setTimeout( function() {
				stimulusdiv.innerHTML = '';		
				observation.stimulus.draw(stimulusdiv)

				timer = Date.now();
				stage.style.visibility = 'visible';
			}, observation.isi
		);

		// wait 2 isi to allow continue button
	  setTimeout(function(){
	  		continuebutton.style.visibility = 'visible';
		  }, observation.isi * 2
  	)
	}

	// ------------------------------
	// function for clicking the continue button
	continuebutton.onclick = function() {
		continuebutton.style.visibility = 'hidden';
		observation.rt = Date.now() - timer;
		
		data.observation[observation.counter] = {
				trial: observation.counter, 
				stimulus: observation.stimulus.id, 
				rt: observation.rt
			};

		// exit if no trials remain
		observation.counter += 1;
		if (observation.counter == presentationorder.length) {
			savedata(data);
			inserthtml(generation.instructions);
			
		// start next trial
		} else { init(); }

	}


	// start first trial
	init();

}