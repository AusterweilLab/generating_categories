// ------------------------------------------------------ //
// ------------------------------------------------------ //
// initalize participant data. this entire array is saved to json
var data = {
	experiment: {
		Stimuli: 'Size-Color Squares',
		Experiment: 'Assigning-Generated-Categories',
		Paradigm: 'TACL' //hmm what's this? SX 040318
	},
	submit:{}, //data on the final final page, incl demographics
	//observation: {},
	//generation: {},
	//generalization: {},
	assignment: {},
	goodness:{},
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
	Middle:  [30, 32, 48, 50],
	Bottom:  [12, 14, 30, 32],
}



// ------------------------------------------------------ //
// phase-specific settings

var assignment = {
	nblocks: 4,
	counter: 0,
	isi: 500,//500,
	isi_multiplier: 5,
	stimulus: null,
	correctcat: null,
	rt: null,
	ui: null,	
	instructions: 'html/instructions/assignment.html',
	catlist: ['Alpha','Beta'],
	feedback: 'Your answer is <font id=\'rightwrong\'>correct</font>. <br> This figure belongs to the <font id=\'feedcat\'></font> category.'
}

var goodness = {
	nblocks: 1,
	counter: 0,
	postcounter:-1,
	isi: assignment.isi,
	sliderRange: 10,
	stimulus: null,
	correctcat: null,
	rt: null,
	ui: null,	
	instructions: 'html/instructions/goodness.html',
}

// this information is not saved to the same file as "data"
var worker = {}

// quick HTML for a fixcross
var fixcross = "<div id='fixcross'>&nbsp+</div>" // 040318 should try to fix its centering though

// global timer
var timer =  null;

// List of countries
var countries = ['Afghanistan','Albania','Andorra','Angola','Antigua and Barbuda','Argentina','Armenia','Australia','Austria','Azerbaijan','Bahamas','Bahrain','Bangladesh','Barbados','Belarus','Belgium','Belize','Benin','Bhutan','Bolivia','Bosnia and Herzegovina','Botswana','Brazil','Brunei','Bulgaria','Burkina Faso','Burundi','Cambodia','Cameroon','Canada','Cape Verde','Cayman Islands','Central African Republic','Chad','Chile','China','Colombia','Comoros','Costa Rica','CÃ´te dâ€™Ivoire','Croatia','Cuba','Cyprus','Czech Republic','Democratic Republic of the Congo','Denmark','Djibouti','Dominica','Dominican Republic','East Timor','Ecuador','Egypt','El Salvador','Equatorial Guinea','Eritrea','Estonia','Ethiopia','Fiji','Finland','France','French Guiana','Gabon','Georgia','Germany','Ghana','Greece','Grenada','Guatemala','Guinea','Guinea-Bissau','Guyana','Haiti','Honduras','Hong Kong','Hungary','Iceland','India','Indonesia','Iran','Iraq','Israel','Italy','Jamaica','Japan','Jordan','Kazakhstan','Kenya','Kiribati','Kuwait','Kyrgyzstan','Laos','Latvia','Lebanon','Lesotho','Liberia','Libya','Liechtenstein','Lithuania','Luxembourg','Madagascar','Malawi','Malaysia','Maldives','Mali','Malta','Marshall Islands','Mauritania','Mauritius','Mexico','Micronesia','Moldova','Monaco','Mongolia','Montenegro','Morocco','Mozambique','Myanmar','Namibia','Nauru','Nepal','Netherlands','New Zealand','Nicaragua','Niger','Nigeria','North Korea','Norway','Oman','Pakistan','Palau','Palestine','Panama','Papua New Guinea','Paraguay','Peru','Philippines','Poland','Portugal','Puerto Rico','Qatar','Republic of Ireland','Republic of Macedonia','Republic of the Congo','Romania','Russia','Russia','Rwanda','Saint Kitts and Nevis','Saint Lucia','Saint Vincent and the Grenadines','Samoa','San Marino','Sao Tome and Principe','Saudi Arabia','Senegal','Serbia','Seychelles','Sierra Leone','Singapore','Slovakia','Slovenia','Solomon Islands','Somalia','South Africa','South Korea','South Sudan','Spain','Sri Lanka','Sudan','Suriname','Swaziland','Sweden','Switzerland','Syria','Taiwan','Taiwan','Tajikistan','Tanzania','Thailand','The Gambia','Togo','Tonga','Trinidad and Tobago','Tunisia','Turkey','Turkey','Turkmenistan','Turks and Caicos','Tuvalu','Uganda','Ukraine','United Arab Emirates','United Kingdom','United States','Uruguay','Uzbekistan','Vanuatu','Vatican City','Venezuela','Vietnam','Western Sahara','Yemen','Zambia','Zimbabwe']  
