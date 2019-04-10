// ------------------------------------------------------ //
// ------------------------------------------------------ //
// initalize participant data. this entire array is saved to json
//global session counter

// var session = {
// 	count: 0, //counter
// 	condition: '', //can be 'b' or 'bc' - initialised in experiment.js,
// 	//types: [['b','bc'],['bc','b']], //should correspond with the order defined in sessionorders	
// 	//sessionorders: ['b-bc','bc-b'] //should correspond with strings specified in cgi-bin/config.py
// 	ntypes: len(gentypes),
	
// }

var data = {
	experiment: {
		Stimuli: 'Size-Color Squares and Size-Orientation Circles',
		Experiment: 'Generating-Multiple-Categories',
		Paradigm: 'TACL'
	},
	submit:{}, //data on the final final page, incl demographics
	//Note the experimental data below have two empty objects, one for each session
	observation: {},
	generation:  {},
	generalization: {},
	info: {
		exposed: false,
		lab: null,
		browser: {
			platform: navigator.platform, 
			userAgent: navigator.userAgent
		}
	},
}
//Old 
 // 72 73 74 75 76 77 78 79 80
 // 63 64 65 66 67 68 69 70 71
 // 54 55 56 57 58 59 60 61 62
 // 45 46 47 48 49 50 51 52 53
 // 36 37 38 39 40 41 42 43 44
 // 27 28 29 30 31 32 33 34 35
 // 18 19 20 21 22 23 24 25 26
 //  9 10 11 12 13 14 15 16 17
 //  0  1  2  3  4  5  6  7  8

//New
//50 by 50

var exemplars = {
	//With a little bit of jitter added
	Corner_S : [0, 8, 72, 80],
	Corner_C : [0, 8, 72, 80]
}

// ------------------------------------------------------ //
// phase-specific settings
var observation = {
	nblocks: 3,
	counter: 0,
	isi: 1000,
	ui: null,
	instructions: 'html/instructions/observe.html'
};

var generation = {
	ntrialsbase: 4,
	ntrials: 0, //specified in generation.js
	counter: 0,
	countbc:0, // counter for bc condition
	bcnames: ['Beta','Gamma'],
	isi: observation.isi,
	generated: [],
	direction: {color: 1, size: 1},
	stimulus: null,
	rt: null,
	ui: null,
	instructions: ['html/instructions/generatenalpha.html',
				   'html/instructions/generatebeta.html',
				   'html/instructions/generatebeta.html'], // generatebeta starts off both conditions 1 and 2
	instructionsgamma: 'html/instructions/generategamma.html',
	useknobs: false,
}

var generalization = {
	counter: 0,
	isi: observation.isi,
	stimulus: null,
	rt: null,
	ui: null,
	instructions: 'html/instructions/generalize.html',
	nstim: 81
}

// this information is not saved to the same file as "data"
var worker = {}

// quick HTML for a fixcross
var fixcross = "<div id='fixcross'>+</div>"

// global timer
var timer =  null;

