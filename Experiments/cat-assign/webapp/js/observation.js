function observe() {
	stage.innerHTML = '';	

	// set observation items
	observation.alphas = []
	var nstim = data.info.stimuli.length
	for (var i = 0; i < nstim; i++){
		if (data.info.categories[i]==0){
			observation.alphas.push(data.info.stimuli[i])
		}
	}	
	observation.betas = []
	for (var i = 0; i < nstim; i++){
		if (data.info.categories[i]==1){
			observation.betas.push(data.info.stimuli[i])
		}
	}

	// make presentation order
	//Randomise the list matched by the other participant
	//First show the alphas
	var presentationorderA = []
	for (var blocknum = 0; blocknum < observation.nblocks; blocknum++) {
			presentationorderA.push.apply(
				presentationorderA, shuffle(observation.alphas)
			);
	}
	// Then do the same for betas
	var presentationorderB = []	
	for (var blocknum = 0; blocknum < observation.nblocks; blocknum++) {
			presentationorderB.push.apply(
				presentationorderB, shuffle(observation.betas)
			);
	}
	var presentationorder = presentationorderA.concat(presentationorderB)
	// put elements in div, hide it
	stage.innerHTML = observation.ui;
	stage.style.visibility = 'hidden';

	// define some frequently used DOM elements
	var stimulusdiv = document.getElementById('stimulus')
	var continuebutton = document.getElementById('continuebutton')
	var alpha = true
	// Set description of each alpha trial (this gets changed when showing betas)
	var stimDesc = document.getElementById('stimDesc');
	stimDesc.innerHTML = observation.trialDesc[0]
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
			if (data.info.lab){console.log('Stim ID: ' + id)} //for debugging
			}, observation.isi
		);
		// wait 2 isi to allow continue button
	  setTimeout(function(){
	  		continuebutton.style.visibility = 'visible';
		  }, observation.isi * 2
  	)
	}
	function break2beta(){
		alpha = false;
		// clear out stage
		stimuli.blank.draw(stimulusdiv)
		stage.style.visibility = 'hidden';
		stimulusdiv.innerHTML = '';
		//$('#stimulus').load(observation.breakDec) //jquery doesn't seem to work for some reason

		//Argh such a hacky way to fix this.
		stimDesc.innerHTML = observation.breakDesc;
		stage.style.visibility = 'visible';
		var continuebuttonbreak = document.getElementById('continuebuttonbreak')
		continuebuttonbreak.onclick = function(){
			//clear out stuff
			stimuli.blank.draw(stimulusdiv)
			stage.style.visibility = 'hidden';
			stimulusdiv.innerHTML = '';
			stimDesc.innerHTML = observation.trialDesc[1]
			init()
		}		
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
		// move to betas if no alpha trials remain
		observation.counter += 1;
		if (observation.counter == presentationorderA.length) {
			break2beta()
		} else if (observation.counter == (presentationorder.length)){
			savedata(data);
			inserthtml(assignment.instructions);			
		// start next trial
		} else { init(); }

	}



	// start first trial
	init();

}
