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
	var feedback    = document.getElementById('feedback');
	
	// define button functions
	alphabutton.onclick = function() {classifyhandler(0)}; //classifyhandler('Alpha')
	betabutton.onclick = function() {classifyhandler(1)}; //classifyhandler('Beta')

	// function to set up a single trial
	function init() {
		
		// get stimulus
		var id = presentationorder[assignment.counter]
		assignment.correctcat = categoryorder[assignment.counter]
		assignment.stimulus = stimuli.ilookup([id])[0]
		// clear out stage		
		stimuli.blank.draw(stimulusdiv)
		feedback.style.visibility = 'hidden';
		stage.style.visibility = 'hidden';

		// insert fix cross into stimulus div, then show it
		stimulusdiv.innerHTML = fixcross;
		stimulusdiv.style.visibility = 'visible';

		// mark participant as exposed to stimuli
		if (assignment.counter == 0) {
			markexposed();
			data.info.exposed = true;
			savedata(data);
		}

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

		//Prepare feedback	
		feedback.innerHTML = assignment.feedback;
		var rightwrong = document.getElementById('rightwrong')
		var feedcat    = document.getElementById('feedcat')
		feedcat.innerHTML = assignment.catlist[assignment.correctcat];
		if (selection==assignment.correctcat){
			rightwrong.innerHTML = 'correct';
			rightwrong.style.color = 'green';
		} else {
			rightwrong.innerHTML = 'wrong';
			rightwrong.style.color = 'red';
		}
		
		//Show feedback
		feedback.style.visibility = 'visible';
	
		if (assignment.counter == presentationorder.length) {
			savedata(data);
			finishup();

		
		} else {	// start next trial after 5 isi
			setTimeout(function(){			
				init();
			},assignment.isi * 5)
		}

	}

	// start first trial
	init()
}
