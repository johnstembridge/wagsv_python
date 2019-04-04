function acceptSuggestedHandicaps(){
    var table=document.getElementById("players");
    var r=1;
    var player = 0;
    while(row=table.rows[r++]){
        sugg = document.getElementById('suggested-' + player).innerText;
        document.getElementById('handicap-' + player).firstChild.value = sugg;
        player += 1;
        }
}