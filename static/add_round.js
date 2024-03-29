var dataSource = '';
if (window.location.href.search(/dev.html/) != -1) {
    dataSource = 'https://dswcregatta.herokuapp.com';
}

var app = new Vue({ 
    el: '#app', 
    data() {
        return {
            numRaces: 1,
            numBoats: 1,
            numCrew: 1,
            password: "",
            roundName: "",
            roundDate: "",
            weather: "",
            comment: "",
            newUser: "",
            addUserMsg: "",
            seriesList: [],
            seriesName: "",
            crewOptions: [''],
            raceOptions: [
                {value: 1, text: "1"},
                {value: "DNF", text: "DNF"},
                {value: "DNS", text: "DNS"},
                {value: "DSQ", text: "DSQ"},
            ],
            fields: [
                {
                    label: "Crew",
                    key: "c1"
                }, 
                {
                    label: "Boat",
                    key: "boat",
                },
                {
                    label: "R1",
                    key: "r1",
                },
            ],
            items: [
                {c1:null, boat: null, r1: "DNS"},
            ]

        };
    },
    mounted() {
        axios
            .get(dataSource + '/api/v1.0/listSeries')
            .then(response => {
                this.seriesList = response.data;
            });
        axios
            .get(dataSource + '/api/v1.0/listUsers')
            .then(response => {
                this.crewOptions.push(...response.data);
            });
    },
    methods: {
        addRace() {
            this.numRaces++;
            // Vue doesn't notice object changes, so use $set
            for (i=0, len=this.items.length; i < len; i++) {
                this.$set(this.items[i], "r" + this.numRaces, "DNS");
            };
            this.fields.push({
                label: "R" + this.numRaces,
                key: "r" + this.numRaces,
            });
        },
        addBoat() {
            this.numBoats++;
            this.raceOptions.splice(this.numBoats - 1, 0, this.numBoats);
            var newBoat = {};
            for (var i = 1; i <= this.numCrew; i++) {
                newBoat["c" + i] = null;
            };
            newBoat["boat"] = null;
            for (var i = 1; i <= this.numRaces; i++) {
                newBoat["r" + i] = "DNS";
            };
            this.items.push(newBoat);
        },
        addCrew() {
            if (this.numCrew == 4) { return };
            this.numCrew++;
            for (line of this.items) {
                line["c" + this.numCrew] = null;
            };
            this.fields.splice(this.numCrew -1, 0, {
                label: "",
                key: "c" + this.numCrew,
            });
        },
        addUser() {
            if (!this.crewOptions.includes(this.newUser)) {
                this.crewOptions.push(this.newUser)
                this.crewOptions.sort()
                this.addUserMsg = this.newUser + " added"
            } else {
                this.addUserMsg = this.newUser + " already exists"
            }
        },
        submit() {
            let boats = [];
            let boat = {};
            let validation = true
            outer:
                for (let line of this.items) {
                    console.log(line)
                    let crew = [];
                    for (let i = 1; i <= this.numCrew; i++) {
                        if ( i == 1 && !line["c" + i]) {
                            alert("All boats must have at least 1 named crew menber");
                            validation = false;
                            break outer;
                        }
                        crew.push(line["c" + i]);
                    }
                    boatNum = line["boat"]
                    let races = [];
                    for (let i = 1; i <= this.numRaces; i++) {
                        races.push(line["r" + i]);
                    }
                    boat = {
                        "crew": crew,
                        "races": races,
                        "boatNum": boatNum
                    }
                    boats.push(boat);
                }
            this.data = {
                "name": this.roundName,
                "weather": this.weather,
                "rounddate": this.roundDate,
                "comment": this.comment,
                "boats": boats,
                "admin_pw": this.password
            };
            console.log(this.data)
            if (!this.seriesName){
                validation = false
                alert ("Please select a Series")
            }
            if (!this.roundName){
                validation = false
                alert ("Please add a Round Name")
            }
            if (!this.weather){
                validation = false
                alert ("Please add weather similar to the form \"Showers SSW 6 - 20 kts\"")
            }
            if (!this.roundDate){
                validation = false
                alert ("Please select the Round Date")
            }
            if (!this.password){
                validation = false
                alert ("Please enter the password")
            }
            if (validation) {
                axios
                    .post(dataSource + encodeURI('/api/v1.0/addRound?seriesName=' + this.seriesName), this.data)
                    .then(response => {
                        alert("Round added" + "\n" + response.data.message)
                    })
                    .catch(error => {
                        alert(error + "\n" + error.response.data.message)
                    });
            }

        },
    }
})