//Return the number of shots to deduct for calculating
//stableford score for hole stroke index <si> with a handicap of <hcap>
function freeShots(si, hcap) {
    var s = 0;
    if (si <= hcap) {
        s += 1;
    }
    if (hcap > 18) {
        if (si <= hcap-18) {
            s += 1;
            }
    }
    if (hcap > 36) {
        if (si <= hcap-36) {
            s += 1;
            }
    }
    return s;
}

function minShotsForNoScore(hole){
        var par = getItemValueForHole(hole, 'par');
        var si = getItemValueForHole(hole, 'si');
        var hcap = Math.round(document.getElementById('handicap').innerHTML);
        var free = freeShots(si, hcap)
        return par + free + 2 // min required for no score
}

//Calculate stableford points for <shots> with a handicap of <hcap>
//at a hole with stroke index <si> and par <par>
function stableford(shots, si, par, hcap){
    var free = freeShots(si, hcap);
    var net = shots - free;
    var p = par - net;
    var points = Math.max(0, p + 2);
    return points;
}

function updatePoints(elm){
    var c = elm.children;
    var id = c[0].id; // scores{In|Out}-{hole-1}-shots
    var inOut = id.match(/([A-Z])\w+/g);
    var i = Number(id.match(/(?:\d*\.)?\d+/g));
    var hole = (inOut == 'Out') ? i + 1 : i + 10;
    updatePointsForHole(hole);
}

function updatePointsForHole(hole){
    normaliseShotsForHole(hole);
    var hcap = Math.round(document.getElementById('handicap').innerHTML);
    var shots = getShotsForHole(hole);
    var par = getItemValueForHole(hole, 'par');
    var si = getItemValueForHole(hole, 'si');

    var points = stableford(shots, si, par, hcap);
    setItemValueForHole(hole, 'points', points);
}

//Update all totals: shots and points
function updateTotals(){
    var totalInShots, totalInPoints, totalOutShots, totalOutPoints, totalShots, totalPoints;
    totalInShots = totalInPoints = totalOutShots = totalOutPoints = totalShots = totalPoints = 0;
    var i = 0;
    var hole, shots, points;
    while (i < 9) {
        hole = i + 1;
        shots = getShotsForHole(hole);
        points = getItemValueForHole(hole, 'points');;
        totalOutShots += shots;
        totalOutPoints += points;
        totalShots += shots;
        totalPoints += points;

        hole = i + 10;
        shots = getShotsForHole(hole);
        points = getItemValueForHole(hole, 'points');;
        totalInShots += shots;
        totalInPoints += points;
        totalShots += shots;
        totalPoints += points;
        i++;
        }
    document.getElementById('scoresOut-totalShots').innerHTML = totalOutShots;
    document.getElementById('scoresOut-totalPoints').innerHTML = totalOutPoints;
    document.getElementById('scoresIn-totalShots').innerHTML = totalInShots;
    document.getElementById('scoresIn-totalPoints').innerHTML = totalInPoints;
    document.getElementById('totalShots').innerHTML = totalShots;
    document.getElementById('totalPoints').innerHTML = totalPoints;
    document.getElementById('totalShotsReturn').value = totalShots;
    document.getElementById('totalPointsReturn').value = totalPoints;}

function updateParTotals(){
    var totalInPar, totalOutPar, totalPar;
    totalInPar = totalOutPar = totalPar = 0;
    var i = 0;
    var hole, par;
    while (i < 9) {
        hole = i + 1;
        var par = getParForHole(hole);
        totalOutPar += par;
        totalPar += par;
        hole = i + 10;
        var par = getParForHole(hole);
        totalInPar += par;
        totalPar += par;
        i++;
        }
    document.getElementById('holesOut-totalPar').innerHTML = totalOutPar;
    document.getElementById('holesIn-totalPar').innerHTML = totalInPar;
    document.getElementById('totalPar').innerHTML = totalPar;
}

//on loading event card, update all automatic fields
function updateAll(){
    var i = 0;
    while (i < 9) {
        updatePointsForHole(i + 1);
        updatePointsForHole(i + 10);
        i++;
    }
    updateTotals();
    document.getElementById('scoresOut-0-shots').focus();
}

//get the id for <item> (shots/par/si/points) for hole <hole>
function getItemIdForHole(hole, item){
    var inOut = (hole > 9) ? 'In' : 'Out';
    hole = (hole > 9) ? hole - 10 : hole - 1;
    var id = 'scores' + inOut + '-' + hole + '-' + item;
    return id
}

//get the id for <item> (shots/par/si/points) for hole <hole>
function getParForHole(hole, item){
    var inOut = (hole > 9) ? 'In' : 'Out';
    hole = (hole > 9) ? hole - 10 : hole - 1;
    var id = 'holes' + inOut + '-' + hole + '-par';
    var elm = document.getElementById(id);
    var value;
        value = elm.value;
    return Number(value);
}

//get the value for <item> (shots/par/si/points) for hole <hole>
function getItemValueForHole(hole, item){
    var id = getItemIdForHole(hole, item);
    var elm = document.getElementById(id);
    var value;
    if (formIsEditable() && item == 'shots')
        value = elm.value;
    else
        value = elm.innerHTML;
    return Number(value);
}

function normaliseShotsForHole(hole){
    var shots = getItemValueForHole(hole, 'shots');
    if (shots == 0 || isNaN(shots)){
        setItemValueForHole(hole, 'shots', '-');
        }
}

function getShotsForHole(hole){
    var shots = getItemValueForHole(hole, 'shots');
    if (shots == 0 || isNaN(shots)){
        shots = minShotsForNoScore(hole);
        }
    return shots;
}

//set the value for <item> (shots/par/si/points) for hole <hole>
function setItemValueForHole(hole, item, value){
    var id = getItemIdForHole(hole, item);
    var elm = document.getElementById(id);
    if (formIsEditable() && item == 'shots')
        elm.value = value;
    else
        elm.innerHTML = value;
}

function formIsEditable(){
    var editable = document.getElementById('editable');
    return editable.value == 'True';
}
