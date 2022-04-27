const docPitcherName = document.querySelector(".pitcher-name");
const docPitchSpeed = document.querySelector(".pitch-speed");
const docPitchCount = document.querySelector(".pitch-count");

const docBatterName = document.querySelector(".batter-name");
const docBattingOrderNo = document.querySelector(".batting-order-number");
const docBattingAvg = document.querySelector(".batting-average");

const docTopTeamContainer = document.querySelector(".top-team-container");
const docTopTeamName = document.querySelector(".top-team-name");
const docTopTeamScore = document.querySelector(".top-team-score");
const docBottomTeamContainer = document.querySelector(".bottom-team-container");
const docBottomTeamName = document.querySelector(".bottom-team-name");
const docBottomTeamScore = document.querySelector(".bottom-team-score");

const docFirstBase = document.querySelector(".first-base");
const docSecondBase = document.querySelector(".second-base");
const docThirdBase = document.querySelector(".third-base")

const docInningArrow = document.querySelector(".inning-arrow");
const docInningNo = document.querySelector(".inning-number");
const docOutsNo = document.querySelector(".outs-number");
const docBalls = document.querySelector(".balls");
const docStrikes = document.querySelector(".strikes");

const docCreateGameBtn = document.querySelector("#create-game");

const docGameNo = document.querySelector("#game-number");

const docHomeTeamSelect = document.querySelector("#home-team-select");
const docAwayTeamSelect = document.querySelector("#away-team-select");

const docCreateHomeLineup = document.querySelector("#create-home-lineup");
const docCreateAwayLineup = document.querySelector("#create-away-lineup");

const docPlayerSelects = document.querySelectorAll(".player-select");

let gameData = {};

docCreateGameBtn.addEventListener("click", async e => {
    let response = await axios({
        method: "get",
        url: "http://192.168.1.4:8008/creategame",
        responseType: "JSON"
    });

    gameData = response.data.game_data;

    await updateTeamSelect(docHomeTeamSelect, response.data.teams_in_leagues_and_divisions);
    await updateTeamSelect(docAwayTeamSelect, response.data.teams_in_leagues_and_divisions);
    await updateScoreBug();
});

docHomeTeamSelect.addEventListener("change", async e => {
    let teamName = e.target.value;
    if (teamName === "")
        return
    
    let response = await axios({
        method: "post",
        url: "http://192.168.1.4:8008/addteam",
        responseType: "JSON",
        data: { teamName, "gameID": docGameNo.value, "side": "Home" }
    });
    
    gameData = response.data.game_data;

    await updateScoreBug();
});

docAwayTeamSelect.addEventListener("change", async e => {
    let teamName = e.target.value;
    if (teamName === "")
        return
    
    let response = await axios({
        method: "post",
        url: "http://192.168.1.4:8008/addteam",
        responseType: "JSON",
        data: { teamName, "gameID": docGameNo.value, "side": "Away" }
    });

    gameData = response.data.game_data;

    await updateScoreBug();
});

docCreateHomeLineup.addEventListener("click", async e => {
    let response = await axios({
        method: "post",
        url: "http://192.168.1.4:8008/getplayers",
        responseType: "JSON",
        data: { teamID: gameData.homeTeam.id }
    });

    console.log(response.data);

    for (let i=1; i<11; i++) {
        if (i < 10) {
            let el = document.querySelector(`#batting-order-${i}`);
            addBatters(el, response.data.batting_order_data);
            el.addEventListener("change", async e => {
                let batter = e.target.value;
                if (batter === "")
                    return

                let response = await axios({
                    method: "post",
                    url: "http://192.168.1.4:8008/addplayertolineup",
                    responseType: "JSON",
                    data: {
                        gameID: gameData.id,
                        teamID: gameData.homeTeam.id,
                        playerID: batter.split('-')[0],
                        orderNo: i
                    }
                });


                
            });
        } else {
            let el = document.querySelector('#starting-pitcher');
            addSP(el, response.data.batting_order_data.Pitchers);
        }
    }
});

const updateTeamSelect = async (select, teamsLeaguesDivs) => {
    for (let leagueDiv of Object.keys(teamsLeaguesDivs)) {
        let teams = teamsLeaguesDivs[leagueDiv];
        let optgroup = document.createElement("optgroup");
        optgroup.label = leagueDiv;
        select.add(optgroup);
        for (let team of teams) {
            let opt = document.createElement("option");
            opt.value = team;
            opt.innerHTML = team;
            select.add(opt);
        }
    }
}

const addBatters = async (select, battingOrderData) => {
    for (let playerType of Object.keys(battingOrderData)) {
        let players = battingOrderData[playerType];
        let optgroup = document.createElement("optgroup");
        optgroup.label = playerType;
        select.add(optgroup);
        for (let player of players) {
            let opt = document.createElement("option");
            opt.value = player;
            opt.innerHTML = player;
            select.add(opt);
        }
    }
}

const addSP = async (select, pitchers) => {
    for (let pitcher of pitchers) {
        let opt = document.createElement("option");
        opt.value = pitcher;
        opt.innerHTML = pitcher;
        select.add(opt);
    }
}

const updateScoreBug = async () => {
    console.log(gameData);
    return new Promise((resolve, reject) => {
        docPitcherName.innerHTML = ""
        if (!isEmptyObject(gameData.pitcher)) {
            docPitcherName.innerHTML = gameData.pitcher.lastName;
        }
        docPitchSpeed.innerHTML = 0;
        docPitchCount.innerHTML = gameData.pitches;
    
        let lineupOrderNo = 1; // temporary!!!
        docBattingOrderNo.innerHTML = "";
        docBatterName.innerHTML = ""
        if (!isEmptyObject(gameData.batter)) {
            docBattingOrderNo.innerHTML = `${lineupOrderNo}.`
            docBatterName.innerHTML = `${gameData.batter.lastName}`;
        }
        docBattingAvg.innerHTML = gameData.battingAvg;
    
        docTopTeamName.innerHTML = ""
        docTopTeamContainer.style.backgroundColor = "#000";
        if (!isEmptyObject(gameData.awayTeam)) {
            docTopTeamName.innerHTML = gameData.awayTeam.shortName;
            let color = "#000";
            if (!isEmptyObject(gameData.awayTeam.colors)) 
                color = `#${gameData.awayTeam.colors[0].hex}`
            docTopTeamContainer.style.backgroundColor = color;
        }
        docTopTeamScore.innerHTML = gameData.awayScore;
            
        docBottomTeamName.innerHTML = ""
        docBottomTeamContainer.style.backgroundColor = "#000";
        if (!isEmptyObject(gameData.homeTeam)) {
            docBottomTeamName.innerHTML = gameData.homeTeam.shortName;
            let color = "#000";
            if (!isEmptyObject(gameData.homeTeam.colors)) 
                color = `#${gameData.homeTeam.colors[0].hex}`
            docBottomTeamContainer.style.backgroundColor = color;
        }
        docBottomTeamScore.innerHTML = gameData.homeScore;
    
        handleBase(docFirstBase, gameData.firstBaseOccupied);
        handleBase(docSecondBase, gameData.secondBaseOccupied);
        handleBase(docThirdBase, gameData.thirdBaseOccupied);
    
        handleInningArrow(gameData.topOfInning);
        docInningNo.innerHTML = gameData.inningNo;
    
        docOutsNo.innerHTML = gameData.outs;
    
        docBalls.innerHTML = gameData.balls;
        docStrikes.innerHTML = gameData.strikes;

        docGameNo.value = gameData.id;

        resolve(true);
    });
}

const handleBase = (baseEl, baseOccupied) => {
    baseEl.classList.remove("occupied");
    if (baseOccupied)
        baseEl.classList.add("occupied");
}

const handleInningArrow = (topOfInning) => {
    docInningArrow.classList.remove("arrow-down", "arrow-up");
    docInningArrow.classList.add(topOfInning ? "arrow-up" : "arrow-down");
}

const isEmptyObject = (obj) => {
    return obj && Object.keys(obj).length === 0 && obj.constructor === Object;
}