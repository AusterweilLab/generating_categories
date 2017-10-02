// THIS FILE CONTAINS VARIOUS UTILITY FUNCTIONS TO MAKE LIFE EASIER

// ------------------------------------------ //
// function to parse the query string in terms
// of key: value pairs
function parsequery() {
  var vars = {};

  // Build the associative array
  var hashes = window.location.search.substring(1).split('&');
  for (var i = 0; i < hashes.length; i++) {
    var sep = hashes[i].indexOf('=');
    if (sep <= 0)
      continue;
    var key = decodeURIComponent(hashes[i].slice(0, sep));
    var val = decodeURIComponent(hashes[i].slice(sep + 1));
    vars[key] = val;
  }

  return vars;
}

// ------------------------------------------ //
// Random integer in range min-max (inclusive)
function randi(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// ------------------------------------------ //
// return a random permutation of range 0:X
function randperm(X) {
    var result = new Array(X);
    for(var i = 0; i < X; i++){
        result[i] = i;
    }
    for (var i = (X - 1); i >= 0; --i){
        var randpos = Math.floor(i * Math.random());
        var tmpstore = result[i];
        result[i] = result[randpos];
        result[randpos] = tmpstore;
    }
    return result;
}

// ------------------------------------------ //
// return a random shuffle of array
function shuffle(array) {
    for (var i = array.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
    return array;
}

// ------------------------------------------ //
// basic python-like range function
function range(n) {
    var result = [];
    for (var i = 0; i<n; i++) {result.push(i)}
    return result;
}

// ------------------------------------------ //
// convert 1d matrix to 2d
function matrixify(arr, slices) {
    var matrix = [];
    for(var i = 0; i < arr.length; i+= slices) {
        matrix.push(arr.slice(i, slices + i));
    }
    return matrix;
};

// ------------------------------------------ //
// convert 2d matrix to 1d
function flatten(arrays) {
    return [].concat.apply([], arrays);
}


// ------------------------------------------ //
// transpose a 2d matrix
function transpose(array) {
    var newArray = array[0].map(function(col, i) { 
      return array.map(function(row) { 
        return row[i] 
      })
    });
    return newArray
}

// ------------------------------------------ //
// function to reverse all rows of a 2d matrix 
function reverserows(array) {
    var out = array;
    for(var i = 0; i < out.length; i++) {
        out[i].reverse() 
    }
    return out
}

// ------------------------------------------ //
// linspace implementation. 
// Create an array from start to stop, using n points.
function linspace(start,stop,n) {
	var result = range(n);
	var D = stop - start
	for(var i = 0; i < n; i += 1 ) {
		result[i] = result[i] * (1/(n-1)) * D + start;
	}
	return result;
}

// ------------------------------------------ //
// cartesian product of arrays
function cartesian(arr) {
    return arr.reduce( function(a,b) {
        return a.map(function(x) {
            return b.map(function(y) {
                return x.concat(y);
            })
        }).reduce(function(a,b) { return a.concat(b) },[])
    }, [[]])
}

// inserts html text into the stage div
function inserthtml(f) {

	// clear out div
	stage.innerHTML = '';

	// just use jquery this time
	$(stage).load(f);
}
