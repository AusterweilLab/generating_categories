// class for each individual stimulus
function Stimulus(color, size, number) {
	this.id = number;
	this.color = color;
	this.size = size;
	this.border = '2px solid #000000';
}

// draw the stimulus using DOM id DIV
Stimulus.prototype.draw = function(DIV) {
    // round color to integer
		var CR = Math.round(this.color)

		// draw it
		DIV.style.border = this.border;
	  DIV.style.backgroundColor = 'rgb('+ [CR,CR,CR].join(',') + ')';
	  DIV.style.width = this.size + 'cm';
	  DIV.style.height= this.size + 'cm';
};

// ----- class for the stimulus set:
// Color and Size are arrays of possible values
function StimulusSet(Color, Size) {
	this.color = Color;
	this.size = Size;
	this.nstimuli = this.color.length * this.size.length;
	if (this.color.length == this.size.length) {
		this.side = this.color.length;
	}
	this.stimuli = {};

	// add blank stimulus
	this.blank = new Stimulus(255, 1.0);
	this.blank.border = 'none';
}

// function to find items based on color and or size 
// returns a array of stimuli with matching values
StimulusSet.prototype.plookup = function(color, size) {
	var ret = [];
	for(var i = 0; i < this.nstimuli; i++) {
		
		if (color === null) { matchcolor = true;
		} else { matchcolor = this.stimuli[i].color === color;
		}

		if (size === null) {	matchsize = true;
		} else { matchsize = this.stimuli[i].size === size;
		}

		if (matchcolor & matchsize) {ret.push(this.stimuli[i])};
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
	var coordinates = cartesian([this.color, this.size])
	for(var i = 0; i < coordinates.length; i++) {
		var color = coordinates[i][0]
		var size = coordinates[i][1]
		var id = counterbalance_order[i]
		this.stimuli[id] = new Stimulus(color, size, id)
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

