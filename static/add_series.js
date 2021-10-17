var dataSource = '';
if (window.location.href.search(/dev.html/) != -1) {
    dataSource = 'https://dswcregatta.herokuapp.com';
}

var app = new Vue({
    el: '#app',
    data() {
        return {
            isSubmitted: false,
            password: "",
            seriesName: "",
            seriesSummType: "",
            seriesSummTypes: ["allRaces", "roundResults"],
            roundDiscardType: "",
            roundDiscardTypes: ["discardWorst", "discardWorst1inX", "keepBest"],
            roundDiscardNum: "",
            seriesDiscardType: "",
            seriesDiscardTypes: ["discardWorst", "discardWorst1inX", "keepBest"],
            seriesDiscardNum: "",
            seriesStartDate: "",
            comment: ""
        };
    },
    methods: {
        submit() {
            this.isSubmitted = !this.isSubmitted;
            let data = {
                "seriesName": this.seriesName,
                "seriesSummType": this.seriesSummType,
                "roundDiscardType": this.roundDiscardType,
                "roundDiscardNum": this.roundDiscardNum,
                "seriesDiscardType": this.seriesDiscardType,
                "seriesDiscardNum": this.seriesDiscardNum,
                "seriesStartDate": this.seriesStartDate,
                "comment": this.comment,
                "admin_pw": this.password
            };
            console.log(data)
            axios
                .post(dataSource + encodeURI('/api/v1.0/addSeries'), data)
                .then(response => {
                    alert("Series added" + "\n" + response.data.message)
                })
                .catch(error => {
                    alert(error + "\n" + error.response.data.message)
                });

        },
    }
})
