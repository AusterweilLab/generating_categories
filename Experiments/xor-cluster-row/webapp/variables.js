// ------------------------------------------------------ //
// ------------------------------------------------------ //
// initalize participant data. this entire array is saved to json
var data = {
	experiment: {
		Stimuli: 'Size-Color Squares',
		Experiment: 'Generating-Categories',
		Paradigm: 'TACL'
	},
	observation: {},
	generation: {},
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

 // 72 73 74 75 76 77 78 79 80
 // 63 64 65 66 67 68 69 70 71
 // 54 55 56 57 58 59 60 61 62
 // 45 46 47 48 49 50 51 52 53
 // 36 37 38 39 40 41 42 43 44
 // 27 28 29 30 31 32 33 34 35
 // 18 19 20 21 22 23 24 25 26
 //  9 10 11 12 13 14 15 16 17
 //  0  1  2  3  4  5  6  7  8
var exemplars = {
	XOR:     [ 0, 10, 70, 80],
	Cluster: [14, 16, 32, 34],
	Row:     [10, 12, 14, 16],
}

// ------------------------------------------------------ //
// phase-specific settings
var observation = {
	nblocks: 3,
	counter: 0,
	isi: 500,
	ui: null,
	instructions: 'html/instructions/observe.html'
};

var generation = {
	ntrials: 4,
	counter: 0,
	isi: observation.isi,
	generated: [],
	direction: {color: 1, size: 1},
	stimulus: null,
	rt: null,
	ui: null,
	instructions: 'html/instructions/generate.html'
}

var generalization = {
	counter: 0,
	isi: observation.isi,
	stimulus: null,
	rt: null,
	ui: null,
	instructions: 'html/instructions/generalize.html'
}

// this information is not saved to the same file as "data"
var worker = {}

// quick HTML for a fixcross
var fixcross = "<div id='fixcross'>+</div>"

// global timer
var timer =  null;

