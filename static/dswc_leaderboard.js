Vue.prototype.$http = 'axios'

var dataSource = "";

/* If the api engine is not running locally, to do development on:

       o templates/index.html
       o static/dswc_leaderboar.js

   use file:///..../dev.html in the browser, as it is symlinked to templates/index.html 
   but the below code will switch the API source to Heroku */
   
if (window.location.href.search(/dev.html/) != -1) {
    var dataSource = "https://dswcregatta.herokuapp.com";
}

function mkDisplayData(obj, data, summary=false) {
    var dData = [];
    var fields = [
        {'key': 'crew', stickyColumn: true},
        {'key': 'place', class: 'text-center'}, 
        /* {'key': 'boatNum', class: 'text-center'}, */ 
        {'key': 'points', class: 'text-center'},
    ];
    for (var b in data) {
        var dRec = {};
        dRec.crew = data[b].crew.join(', ');
        /* dRec.boatNum = data[b].boatNum; */
        dRec.points = data[b].points;
        dRec.place = data[b].place;
        dRec._cellVariants = {};
        for (var r in data[b].races) {
            var raceStr = parseInt(r, 10) + 1;
            raceStr = 'R' + raceStr;
            var fRec = {
                key: raceStr,
                class: 'text-center'
            };
            fields.push(fRec);
            if (data[b].races[r].discard) {
                dRec[raceStr] = '(' + data[b].races[r].place + ')';
            } else {
                dRec[raceStr] = data[b].races[r].place;
            }
            if (data[b].races[r].flag) {
                dRec._cellVariants[raceStr] = 'success';
            }
        }
        dData.push(dRec);
    }
   obj.items = dData;
   obj.fields = fields;
}

var appAxios = new Vue({
    el: '#summary',
    data () {
        return {
            items: null,
            /* fields: ['crew', 'place', 'boatNum', 'points', 'races'] */
            fields: ['crew', 'place', 'boatNum', 'points', 'races']
        };
    },
    mounted () {
        axios
            .get(dataSource + '/api/v1.0/getSeriesResult?seriesName=Frostbite_2020')
            .then(response => (mkDisplayData(this, response.data)))
    }
});
    