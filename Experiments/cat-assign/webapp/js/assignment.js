// based on the generalize function
function assign() {
	stage.innerHTML = '';	

	//Make raw unordered presentation list
	var presentationorderT = [];
	var categoryorderT = []	
	for (i=0; i<assignment.nblocks; i++){
		presentationorderT = presentationorderT.concat(data.info.stimuli)
		categoryorderT = categoryorderT.concat(data.info.categories)		
	}

	shuffleidx = [];
	var presentationorder = [];
	var categoryorder = [];
	for (i=0; i<presentationorderT.length; i++){
		shuffleidx.push(i)
	}
	shuffle(shuffleidx)

	// Shuffle presentation and category order according to the fixed shuffleindex
	for (i=0; i<shuffleidx.length; i++){
		curridx = shuffleidx[i];
		presentationorder.push(presentationorderT[curridx]);
		categoryorder.push(categoryorderT[curridx]);
	}
	//var presentationorder = randperm(stimuli.nstimuli);

	// put elements in div, hide it
	stage.innerHTML = assignment.ui;
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
		var id = presentationorder[assignment.counter]
		assignment.correctcat = categoryorder[assignment.counter]
		assignment.stimulus = stimuli.ilookup([id])[0]
		// clear out stage
		stimuli.blank.draw(stimulusdiv)
		stage.style.visibility = 'hidden';

		// insert fix cross into stimulus div, then show it
		stimulusdiv.innerHTML = fixcross;
		stimulusdiv.style.visibility = 'visible';

		// wait 1 isi, then draw new items
		setTimeout( function() {
				stimulusdiv.innerHTML = '';		
				assignment.stimulus.draw(stimulusdiv);
				stage.style.visibility = 'visible';
				timer = Date.now(); // start timer
			}, assignment.isi
		);

	};

	function classifyhandler(selection) {
		assignment.rt = Date.now() - timer;

		if (data.info.lab){ //for debugging
			console.log('Prev: Stim ID, Response, Correct Cat: ' +
						assignment.stimulus.id + ', ' +
						selection + ', ' +
					    assignment.correctcat);
		} 

		// add row of data
		data.assignment[assignment.counter] = {	
			trial: assignment.counter,
			stimulus: assignment.stimulus.id, 
			response: selection,
			correctcat: assignment.correctcat,
			rt: assignment.rt,			
		}

		assignment.counter += 1
		if (assignment.counter == presentationorder.length) {
			savedata(data);
			finishup();

			// start next trial
		} else { 	init()	}

	}

	// start first trial
	init()
}
