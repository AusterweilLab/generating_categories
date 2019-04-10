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
	if (data.info.gentype==2){ //beta-gamma condition
		generation.category = generation.bcnames[generation.countbc]
		generation.ntrials = generation.ntrialsbase
	} else {
		if (data.info.gentype==1) { //beta-only condition
			generation.category = 'Beta'
		} else { //not-alpha condition
			generation.category = 'Not-Alpha'
		}
		generation.ntrials = generation.ntrialsbase; //NOTE that in the ABC experiments, this should be set to ntrialsbase*2 (as opposed to just ntrialsbase)
	}

	// function to start a new trial
	function init() {		
		// replace existing ui.
		stage.innerHTML = generation.ui;
		stage.style.visibility = 'hidden'; // hide everything during setup
		if (generation.useknobs){
			document.getElementById('size_holder').innerHTML =
				'<input type = "text"'+
				'class = "dial"'+
				'id = "size_control">'
			document.getElementById('color_holder').innerHTML =
				'<input type = "text"'+
				'class = "dial"'+
				'id = "color_control">'
			cc_old = 10;
			sc_old = 10;
			$(".dial").knob({				
				'min':0,
				'max':stimsteps-1,
				'width':100,
				'cursor':true,
				'thickness':.3,
				'fgColor': "#222222",
				'displayInput':false,
				'change': function() { generate_handler() }
			});
			$(".dial").val(cc_old)
		} else {
			document.getElementById('size_holder').innerHTML =
				'<input type = "range"'+
		  		'class = "feature_range"'+
		  		'id = "size_control"'+
				'min = "0"'+
		  		'max = "10"'+
		  		'step = "1">'
		  					
			document.getElementById('color_holder').innerHTML =
				'<input type = "range"'+
		  		'class = "feature_range"'+
		  		'id = "color_control"'+
		  		'min = "0"'+
		  		'max = "10"'+
		  		'step = "1">'
		}

		//Specify dim1 name, make sentence case
		dim1nameA = stimuli.dim1name.toUpperCase()[0]
		dim1name = dim1nameA + stimuli.dim1name.slice(1,stimuli.dim1name.length)
		document.getElementById('dim1name').innerHTML = dim1name
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
		continuebutton.onclick = function() {
			var isdup = duplicate_handler()
			if (!isdup){
				end_trial()
			}
		};
		size_control.oninput =  function() { generate_handler() };
		color_control.oninput =  function() { generate_handler() };

		// update category label in instruction
		if (data.info.gentype==0){
			document.getElementById('categoryID').innerHTML = 'that is NOT from the Alpha'
		}
		else{
			document.getElementById('categoryID').innerHTML = 'of the ' + generation.bcnames[generation.countbc];
		}
		
		// draw ui, start interface after delay
		setTimeout( function() {
				stage.style.visibility = 'visible' // show ui
				timer = Date.now(); // start timer
		 }, generation.isi	)
	}


	function generate_handler() {
		if (generation.useknobs){
			// get diff
			cc_diff = color_control.value-cc_old
			if (cc_diff<-10){
				cc_diff = 1 //hack
			}
			if (cc_diff>10){
				cc_diff = -1 //hack
			}
			//console.log(cc_diff)
			cc_new = cc_old+cc_diff
			cc_new = Math.min(stimsteps-1,cc_new)
			cc_new = Math.max(0,cc_new)

			sc_diff = size_control.value-sc_old
			if (sc_diff<-10){
				sc_diff = 1 //hack
			}
			if (sc_diff>10){
				sc_diff = -1 //hack
			}
			//console.log(sc_diff)
			sc_new = sc_old+sc_diff
			sc_new = Math.min(stimsteps-1,sc_new)
			sc_new = Math.max(0,sc_new)
			// get values of color / size
			var values = {
				color: stimuli.dim1[cc_new],
				size: stimuli.dim2[sc_new]
			};
		} else {
			// get values of color / size
			var values = {
				color: stimuli.dim1[color_control.value],			
				size: stimuli.dim2[size_control.value]
			};

		}
		// find new stimulus, check if it is in the generated list
		generation.stimulus = stimuli.plookup(values.color, values.size)[0];
		//console.log(values)
		// check for dupes, draw new stimulus
		//duplicate_handler();
		// reset warnings and button every click on slider
		dupemessage.style.visibility = 'hidden';
		continuebutton.style.visibility = 'visible';
		generation.stimulus.draw(stimulusdiv);
		if (generation.useknobs){
			cc_old = cc_new;
			sc_old = sc_new;
		}		
	}

	// function to hide continue button, display dupe message if needed
	// returns boolean on whether is dup or not
	function duplicate_handler() {

		if ( generation.generated.includes(generation.stimulus.id) ) {
			dupemessage.style.visibility = 'visible';
			continuebutton.style.visibility = 'hidden';
			return true
		} else {
			dupemessage.style.visibility = 'hidden';
			continuebutton.style.visibility = 'visible';
			return false
		}

	}

	function end_trial() {
		generation.rt = Date.now() - timer; // set rt

		// add stimulus to generated list
		generation.generated.push(generation.stimulus.id);

		// add a row of data
		var counterbase = generation.countbc*generation.ntrialsbase // should be either 0 or 4
		data.generation[generation.counter+counterbase] = {
			category: generation.category,
			trial: generation.counter+counterbase,
			stimulus: generation.stimulus.id,
			rt: generation.rt,
		};

		// add one to counter
		generation.counter += 1;

		if (generation.counter >= generation.ntrials) {
			savedata(data);
			if (data.info.gentype==2 && generation.countbc==0){ //If bc condition, move on to gamma
				generation.countbc += 1 //add to countbc
				//reset list of generated stim
				generation.generated = []
				inserthtml(generation.instructionsgamma);
			} else { 
				//Proceed to generalization
				inserthtml(generalization.instructions);
			}
		// start next trial	
		} else { init() }


	}

	// start first trial
	init();
}
