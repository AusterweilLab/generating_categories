// class for each individual stimulus
function Stimulus(dim1, dim2, number) {
	this.id = number;
	this.dim1 = dim1; //color for squares, orientation for circles
	this.dim2 = dim2; // always size for both squares and circles
	this.border = '2px solid #000000';
}

// draw the stimulus using DOM id DIV
Stimulus.prototype.draw = function(DIV) {
	if (data.info.stimtype == 'Squares') {
		//dim1 = color, dim2 = size
		var color = this.dim1
		var size = this.dim2
		// round color to integer
		var CR = Math.round(color)
		// draw it
		DIV.style.border = this.border;
		DIV.style.backgroundColor = 'rgb('+ [CR,CR,CR].join(',') + ')';
		DIV.style.width = size + 'cm';
		DIV.style.height= size + 'cm';
	} else if (data.info.stimtype == 'Circles') {
		//dim1 = orientation, dim2 = size
		var orientation = this.dim1
		var size = this.dim2
		//Insert canvas
		DIV.innerHTML = '<canvas id="myCanvas' + DIV.id + '" ' + 
			'width = "' + cm2px(size) + '" ' +
			'height = "' + cm2px(size) + '"></canvas>'
		var cvs = document.getElementById('myCanvas'+DIV.id)
		var ctx = cvs.getContext('2d');
		var cvsWd = cvs.width;
		var cvsHt = cvs.height;

		//Draw circle
		ctx.beginPath();
		var radius = cm2px(size)/2 - 2; //subtract small number of pickles to prevent cropping effect	
		ctx.arc(radius+1,radius+1,radius,0,Math.PI*2,false);//the +1 seems to center the circle better than without
		//ctx.fillStyle = 'rgb('+ [CR,CR,CR].join(',') + ')';
		//ctx.fill();		
		ctx.lineWidth = 2;
		ctx.strokeStyle = "#000000";
		ctx.stroke();
		//Draw angled line
		var orient_adj = 2.587//Math.random() * Math.PI*2
		angle = orientation + orient_adj;
		var xchange = radius * Math.cos(angle)
		var ychange = radius * Math.sin(angle)
		ctx.beginPath();
		ctx.moveTo(radius,radius)
		ctx.lineTo(radius+xchange,radius+ychange)
		ctx.stroke();
		
		//This can create circles by rounding the corners of the boxes.
		//However, the radial line will be an issue. May be best to use canvas
		// DIV.style.borderRadius = '50%';
		// DIV.style.MozBoxSizing = 'border-box';
		// DIV.style.BoxSizing = 'border-box';

	}
};

// ----- class for the stimulus set:
// Color/Orientation and Size are arrays of possible values
function StimulusSet(dim1, dim2) {
	//Define some attributes
	this.dim1 = dim1; //Color for squares, orientation for circles
	this.dim2 = dim2;
	this.stimtype = data.info.stimtype
	this.nstimuli = this.dim1.length * this.dim2.length;
	if (this.dim1.length == this.dim2.length) {
		this.side = this.dim1.length;
	}
	this.stimuli = {};
	if (data.info.stimtype == 'Squares'){
		this.dim1name = 'color'
	} else if (data.info.stimtype == 'Circles') {
		this.dim1name = 'orientation'
	}
	// add blank stimulus
	this.blank = new Stimulus(255, 1.0);
	this.blank.border = 'none';
}

// function to find items based on color and or size 
// returns a array of stimuli with matching values
StimulusSet.prototype.plookup = function(dim1, dim2) {
	var ret = [];
	for(var i = 0; i < this.nstimuli; i++) {
		
		if (dim1 === null) { matchdim1 = true;
		} else { matchdim1 = this.stimuli[i].dim1 === dim1;
		}

		if (dim2 === null) { matchdim2 = true;
		} else { matchdim2 = this.stimuli[i].dim2 === dim2;
		}

		if (matchdim1 & matchdim2) {ret.push(this.stimuli[i])};
	}

	return(ret)
}

// function to find items based on a vector of ids
// returns a array of stimuli with ids in 'ids'
StimulusSet.prototype.ilookup = function(ids) {
	var ret = [];
	for( var i = 0; i < ids.length; i++) {
		ret.push(this.stimuli[ids[i]])
	}
	return(ret)
}

// make the stimulus set
 // 72 73 74 75 76 77 78 79 80
 // 63 64 65 66 67 68 69 70 71
 // 54 55 56 57 58 59 60 61 62
 // 45 46 47 48 49 50 51 52 53
 // 36 37 38 39 40 41 42 43 44
 // 27 28 29 30 31 32 33 34 35
 // 18 19 20 21 22 23 24 25 26
 //  9 10 11 12 13 14 15 16 17
 //  0  1  2  3  4  5  6  7  8

// function to generate a stimulus set
StimulusSet.prototype.make_stimuli = function() {

	// set counterbalance if not specified
	if (data.info.counterbalance === undefined) {
		data.info.counterbalance = randi(0, counterbalance.length - 1);
	}

  var counterbalance_order = get_stimulus_order(this.side, data.info.counterbalance)

  // add each stimulus
	var coordinates = cartesian([this.dim1, this.dim2])
	for(var i = 0; i < coordinates.length; i++) {
		var dim1 = coordinates[i][0]
		var dim2 = coordinates[i][1]
		var id = counterbalance_order[i]
		this.stimuli[id] = new Stimulus(dim1, dim2, id)
	}
}


// FUNCTION TO PRODUCE A COUNTERBALANCE STIMULUS ORDER
function get_stimulus_order(side, counterbalance) {

	var conditions = [
		{order: "regular", reversed: [false,	false]},
		{order: "regular", reversed: [false,	true]},
		{order: "regular", reversed: [true,	false]},
		{order: "regular", reversed: [true,	true]},
		{order: "flipped", reversed: [false,	false]},
		{order: "flipped", reversed: [false,	true]},
		{order: "flipped", reversed: [true,	false]},
		{order: "flipped", reversed: [true,	true]},
	]

	var counterbalance_info = conditions[counterbalance]
	var objective_order = range(side * side);
	var objective_space = matrixify(objective_order, side);
	var final_space = objective_space;

	// flip dimensions if needed
	if (counterbalance_info.order == 'flipped') {
		final_space = transpose(final_space);
	}

	// reverse each row of current space
	if (counterbalance_info.reversed[0]) {
		final_space = reverserows(final_space);
	}	

	// reverse each row of current space
	if (counterbalance_info.reversed[1]) {
		final_space = transpose(reverserows(transpose(final_space)));
	}	

	// return 1d version of the space
	return flatten(final_space)
}

// function get_stim_linear(condition){
// 	var length = stimsteps;
// 	var area = length**2;
// 	if (condition=='XOR'){
		
// 	}

// }
