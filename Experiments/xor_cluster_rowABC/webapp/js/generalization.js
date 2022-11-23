function generalize() {
	stage.innerHTML = '';	
	// make presentation order
	var presentationorder_raw = [0];
	var po_step = (stimuli.nstimuli)/(generalization.nstim-1)
	for (var i=1;i<generalization.nstim;i++){
		var poi = Math.round(po_step*i)-1
		presentationorder_raw.push(poi)
	}
	var presentationorder_idx = randperm(generalization.nstim);
	var presentationorder = [];
	for (var i=0; i<generalization.nstim;i++){
		presentationorder.push(presentationorder_raw[presentationorder_idx[i]])
	}

	//reset counter
	generalization.counter = 0
	
	// put elements in div, hide it
	stage.innerHTML = generalization.ui;
	stage.style.visibility = 'hidden';

	// define variables
	var stimulusdiv = document.getElementById('stimulus');
	var alphabutton = document.getElementById('classify_alpha');
	var betabutton  = document.getElementById('classify_beta');
	var gammabutton  = document.getElementById('classify_gamma');		
	

	// define button functions
	alphabutton.onclick = function() {classifyhandler('Alpha')};
	betabutton.onclick = function() {classifyhandler('Beta')};
	gammabutton.onclick = function() {classifyhandler('Gamma')};
	
	//If it's not the beta-gamma condition, remove the gamma button
	if (data.info.gentype!=2){
		//Remove gamma button
		gammabutton.parentNode.removeChild(gammabutton)
		if (data.info.gentype==0) {
			//For not-alpha condition, rewrite the text in the button from beta Not Alpha
			betabutton.innerHTML = 'NOT Alpha'
		}
	}

	// function to set up a single trial
	function init() {
		// get stimulus
		var id = presentationorder[generalization.counter]
		console.log(id)
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
