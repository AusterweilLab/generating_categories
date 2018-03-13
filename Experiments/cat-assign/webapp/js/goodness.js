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
	var stimulus_surround;
	var goodness_control;
	var sliderfeedback;
	var okgo;
	var goodnesstxt;
	var slidertxt;
	
	//randomise whether beta or alpha is being queried on the alst two trials
	var shuffleABbase = ['Alpha','Beta']
	var shuffleABidx = [0,1];
	var shuffleAB = [];
	shuffle(shuffleABidx)
	for (i=0;i<2;i++){
		shuffleAB.push(shuffleABbase[shuffleABidx[i]]);
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
		stimulus_surround = document.getElementById('stimulus');
		goodness_control = document.getElementById('goodness_control');
		sliderfeedback = document.getElementById('sliderfeedback');
		goodnesstxt = document.getElementById('goodnesstxt');
		slidertxt = document.getElementById('slidertxt');
		// configure controls
		goodness_control.setAttribute('max', 10);
		//Rewrite instructions
		goodnesstxt.innerHTML = '<br>This was category <u><font class=\'alphabeta\'>Alpha</font></u>:';		
		slidertxt.innerHTML = '<br>As a whole, how well do you think the <font class=\'alphabeta\'>Alpha</font> category was represented by all of its members? Please provide your rating with the slider below, where 0 indicates that the category was very poorly represented and 10 indicates that the category was very well represented.<br><br>'
		//Clear stimulus surround and build 4 inner divs
		stimulus_surround.innerHTML = '';
		//stage.style = 'width:1000px';
		//Enlarge body so that all four divs can fit
		document.getElementsByTagName("body")[0].style = ' width:30cm'
		stimulusdiv = [];
		for (var i = 0; i < 4; i++){
			stimulusdiv[i] = document.createElement('div')
			stimulusdiv[i].id = 'stimDiv' + i
			//Get stim size so its vert position can be adjusted
			stimulusdiv[i].style = 'float:left;' + 
				'margin-left:5px;' + 
				'margin-right:5px;' + 
				//'margin-top:auto;' + 
				//'margin-bottom:auto;' + 
				//'line-height:6.5cm' +
				'position:relative;';			
			stimulus_surround.appendChild(stimulusdiv[i]);
		}

		//'Goodness Rating for Category <font id=\'alphabeta2\'>Alpha</font>';
		
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
				//stimulusdiv.outerHTML = '';
				//Draw all category stimuli into 4 stimdivs within stim surround
				var drawcount = 0
				for (var i = 0; i < presentationorder.length; i++){
					var currCat = shuffleAB[goodness.postcounter];
					var currCatMatch =  shuffleABbase.indexOf(currCat);
					if (categoryorder[i]==currCatMatch){
						var stimId = presentationorder[i]; 
						var currStim = stimuli.ilookup([stimId])[0];
						currStim.draw(stimulusdiv[drawcount])
						//Adjust vertical positions of stim
						var height = currStim.size//stimulusdiv[drawcount].clientHeight;

						var vertAdj = (6.5-height)/2; //6.5 is the original height of stimulus surround
						stimulusdiv[drawcount].style.top = vertAdj + 'cm';
						drawcount++;
					}
				}
				var alphabetac = document.getElementsByClassName('alphabeta');
				for (var i = 0;i<alphabetac.length; i++){
					var element = alphabetac[i];
					element.innerHTML = shuffleAB[goodness.postcounter];
				}
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
				//Reset body width so that final page isn't weird
				document.getElementsByTagName("body")[0].style = ' width:16cm'
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
