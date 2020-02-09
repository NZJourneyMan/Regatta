Vue.prototype.$http = 'axios';

var dataSource = '';

/* If the api engine is not running locally, to do development on:

       o templates/index.html
       o static/dswc_leaderboar.js

   use file:///..../dev.html in the browser, as it is symlinked to templates/index.html 
   but the below code will switch the API source to Heroku */

if (window.location.href.search(/dev.html/) != -1) {
    dataSource = 'https://dswcregatta.herokuapp.com';
}


var allSeries = new Vue({
    el: '#allSeries',
    data: {
        seriesList: []
    },
    mounted() {
        axios
            .get(dataSource + '/api/v1.0/listSeries')
            .then(response => (this.seriesList = response.data));
    }
});

Vue.component('result-table', {
    props: ['title', 'tabledata'],
    template: `
        <div class='result-table'>
            <h3><span class="text-primary">{{ title }}</span></h3>
            <b-table responsive striped hover sticky-header=90vh 
                :fields="tabledata.fields" :items="tabledata.items">
            </b-table>
        </div>
    `
});

function mkTitle(str) {
    return str.replace('_', ' ')
}

var resultsPane = new Vue({
    el: '#resultsPane',
    data: {
        showResults: false,
        summary: null,
        raceDays: null,
        summaryTitle: null,
        series: "",
        len: 0,
        summaryData: {
            items: null,
            fields: ['crew', 'place', 'boatNum', 'points', 'races']
        }
    },
    methods: {
        displaySeriesData: function(series) {
            this.showResults = true;
            this.series = mkTitle(series);
            this.raceDays = [];
            axios
                .get(
                    dataSource +
                        encodeURI(
                            `/api/v1.0/getSeriesResult?seriesName=${series}`
                        )
                )
                .then(response => {
                    this.raceDays.push({
                        raceTitle: "Leaderboard",
                        raceData: this.mkDisplayData(response.data, true)
                    });
                    axios
                        .get(dataSource + "/api/v1.0/listRounds", {
                            params: {seriesName: series}
                        })
                        .then(response => {
                            for (var i in response.data) {
                                axios
                                    .get(
                                        dataSource + "/api/v1.0/getRoundResult", {
                                            params: {
                                                seriesName: series,
                                                roundName: response.data[i],
                                                count: i  // track position in case return is out of order
                                            }
                                        }
                                    )
                                    .then(response => {
                                        this.raceDays[parseInt(response.config.params.count) + 1] = {
                                            raceTitle: mkTitle(response.config.params.roundName),
                                            raceData: this.mkDisplayData(response.data),
                                        };
                                        this.len++;  // Force Vue to update
                                    });
                            }
                        });
                })
        },
        mkDisplayData: function(data, summary=false) {
            var dData = [];
            var fields = [
                { key: 'crew', stickyColumn: true },
                { key: 'place', class: 'text-center' },
                { key: 'points', class: 'text-center' }
            ];
            if (!summary) {
                fields.push( {'key': 'boatNum', class: 'text-center'} )
            };
            for (var result of data) {
                var dRec = {};
                if (!summary) {
                    dRec.boatNum = result.boatNum;
                };

                dRec.place = result.place;
                dRec.points = result.points;
                dRec.crew =
                    (result.place === 1
                        ? '🥇'
                        : result.place === 2
                        ? '🥈'
                        : result.place === 3
                        ? '🥉'
                        : '') + result.crew.join(', ');

                // First, second and third positions
                var highlightResult =
                    result.place === 1
                        ? 'primary'
                        : result.place === 2 || result.place === 3
                        ? 'success'
                        : '';
                dRec._cellVariants = { place: highlightResult };

                for (var r in result.races) {
                    var raceStr = 'R' + (parseInt(r) + 1);
                    var fRec = {
                        key: raceStr,
                        class: 'text-center'
                    };
                    fields.push(fRec);

                    dRec[raceStr] = result.races[r].place;

                    if (result.races[r].discard) {
                        dRec[raceStr] = '(' + dRec[raceStr] + ')';
                        // dRec._cellVariants[raceStr] = 'danger';
                    };
                    if (result.races[r].flag) {
                        dRec._cellVariants[raceStr] = 'warning';
                    } else {
                        dRec._cellVariants[raceStr] = 'info';
                    }
                }
                dData.push(dRec);
            };
            return {
                "items": dData,
                "fields": fields,
            }
        }
    }
});
