// based on the generalize function
function assign() {
	stage.innerHTML = '';	
	//Make raw unordered presentation list
	var presentationorderT = [];
	var categoryorderT = []	
	var presentationorder = [];
	var categoryorder = [];

	var shuffleidx = [];
	for (i=0; i<data.info.stimuli.length; i++){
		shuffleidx.push(i)
	}

	for (i=0; i<assignment.nblocks; i++){		
		presentationorderT = data.info.stimuli
		categoryorderT = data.info.categories
		//Shuffle the order within each block
		shuffle(shuffleidx)
		for (j=0; j<presentationorderT.length; j++){
			presentationorder.push(presentationorderT[shuffleidx[j]]);
			categoryorder.push(categoryorderT[shuffleidx[j]]);
		}
	}
	//console.log(presentationorder);

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
			//Enable buttons
			alphabutton.disabled = false;
			betabutton.disabled = false;
			}, assignment.isi
		);

	};

	function classifyhandler(selection) {
		//disable buttons
		alphabutton.disabled = true;
		betabutton.disabled = true;
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
			setTimeout(function(){			
				inserthtml(goodness.instructions);
			},assignment.isi * assignment.isi_multiplier)

		
		} else {	// start next trial after 2 isi
			setTimeout(function(){			
				init();
			},assignment.isi * assignment.isi_multiplier)
		}

	}

	// start first trial
	init()
}
