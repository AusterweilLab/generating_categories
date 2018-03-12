// based on the generalize function
function goodnessrating() {
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

	for (i=0; i<goodness.nblocks; i++){		
		presentationorderT = data.info.stimuli
		categoryorderT = data.info.categories
		//Shuffle the order within each block
		shuffle(shuffleidx)
		for (j=0; j<presentationorderT.length; j++){
			presentationorder.push(presentationorderT[shuffleidx[j]]);
			categoryorder.push(categoryorderT[shuffleidx[j]]);
		}
	}
	goodness.ntrials = presentationorder.length

	// put elements in div, hide it
	stage.innerHTML = goodness.ui;
	stage.style.visibility = 'hidden';

	// some function globals
	var continuebutton;
	var stimulusdiv;
	var goodness_control;
	var sliderfeedback;
	var okgo;
	var goodnesstxt;
	var slidertxt;
	
	//randomise whether beta or alpha is being queried on the alst two trials
	var shuffleABt = ['Alpha','Beta']
	var shuffleABidx = [0,1];
	var shuffleAB = [];
	shuffle(shuffleABidx)
	for (i=0;i<2;i++){
		shuffleAB.push(shuffleABt[shuffleABidx[i]]);
	}
	// function to start a new trial
	function init() {

		// replace existing ui.
		stage.innerHTML = goodness.ui;
		stage.style.visibility = 'hidden'; // hide everything during setup

		// define UI elements
		continuebutton = document.getElementById('continuebutton');
		stimulusdiv = document.getElementById('stimulus');
		goodness_control = document.getElementById('goodness_control');
		sliderfeedback = document.getElementById('sliderfeedback');
		// configure controls
		goodness_control.setAttribute('max', 10);

		//Don't allow progress without clicking on slider at least once
		okgo = false;
		// assign functions
		continuebutton.onclick = function() { end_trial() };
		goodness_control.oninput =  function() { goodness_handler() };

		// get stimulus
		var id = presentationorder[goodness.counter]
		goodness.stimulus = stimuli.ilookup([id])[0]
		// draw ui, start interface after page load
		waitUntil(
			function(){
				// Run this after stage is done loading
				goodness.stimulus.draw(stimulusdiv)
				stage.style.visibility = 'visible' // show ui
				timer = Date.now(); // start timer		
			},
			function(){
			// the code that tests here... (return true if test passes; false otherwise)
					return !!(stage.innerHTML !== '');
			},
			50 // Amount to wait between checks
		)();
	}

	// function to show the final trial
	function finaltrial() {
		// replace existing ui.
		stage.innerHTML = goodness.ui;
		stage.style.visibility = 'hidden'; // hide everything during setup

		// define UI elements
		continuebutton = document.getElementById('continuebutton');
		stimulusdiv = document.getElementById('stimulus_surround');
		goodness_control = document.getElementById('goodness_control');
		sliderfeedback = document.getElementById('sliderfeedback');
		goodnesstxt = document.getElementById('goodnesstxt');
		slidertxt = document.getElementById('slidertxt');
		// configure controls
		goodness_control.setAttribute('max', 10);
		//Rewrite instructions
		goodnesstxt.innerHTML = '<br>As a whole, how well do you think the <u><font id=\'alphabeta\'>Alpha</font></u> category was represented by all its members? Please provide your rating with the slider below, where 0 indicates that the category was very poorly represented and 10 indicates that the category was very well represented.<br><br>'
		slidertxt.innerHTML = 'Goodness Rating for Category <font id=\'alphabeta2\'>Alpha</font>';

		//Don't allow progress without clicking on slider at least once
		okgo = false;

		// assign functions
		continuebutton.onclick = function() { end_trial() };
		goodness_control.oninput =  function() { goodness_handler() };

		// draw ui, start interface after page load
		waitUntil(
			function(){
				// Run this after stage is done loading
				//stimulusdiv.innerHTML = ('Heya')
				//goodness.stimulus.draw(stimulusdiv)
				//Erase stimulus space
				stimulusdiv.outerHTML = '';
				// Insert alpha or beta query
				var alphabeta = document.getElementById('alphabeta');
				var alphabeta2 = document.getElementById('alphabeta2');
				alphabeta.innerHTML = shuffleAB[goodness.postcounter];
				alphabeta2.innerHTML = shuffleAB[goodness.postcounter];
				stage.style.visibility = 'visible' // show ui
				timer = Date.now(); // start timer		
			},
			function(){
			// the code that tests here... (return true if test passes; false otherwise)
					return !!(stage.innerHTML !== '');
			},
			50 // Amount to wait between checks
		)();
	}


	function goodness_handler() {
		//Present the slider number from 1 to 10		
		sliderfeedback.innerHTML = goodness_control.value;
		//Allow progress to next trial
		okgo = true;
		//console.log(goodness_control.value)		
	}

	function end_trial() {
		if (okgo){

			goodness.rt = Date.now() - timer; // set rt

			if (goodness.postcounter>=0){
				var category_rating = shuffleAB[goodness.postcounter];
				var stimID = -1;
			} else {
				var category_rating = 'NA'
				var stimID = goodness.stimulus.id;
			}
			var sliderval = Number(goodness_control.value);
			if (data.info.lab){ //for debugging
				console.log('Prev: Stim ID, Rating, Category: ' +
							stimID + ', ' +
							sliderval + ', ' +
							category_rating);
			} 
			
			// add a row of data
			data.goodness[goodness.counter] = {
				trial: goodness.counter,
				stimulus: stimID,
				rating: sliderval,
				rt: goodness.rt,
				categoryRate: category_rating,
			};

			// add one to counter
			goodness.counter += 1;
			goodness.postcounter = goodness.counter-goodness.ntrials;
			//console.log(goodness.counter)
			if (goodness.counter > goodness.ntrials+1) {
				savedata(data);
				//inserthtml(generalization.instructions);
				finishup();
			} else if (goodness.postcounter>=0){			
				//go to final trial
				finaltrial();
			} else {
				// start next trial
				init()
			}

		}
	}

	// start first trial
	init();
}
