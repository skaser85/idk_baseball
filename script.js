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

docCreateGameBtn.addEventListener("click", async e => {
    let response = await axios({
        method: "get",
        url: "http://192.168.1.4:8008/creategame",
        responseType: "JSON"
    });

    await updateTeamSelect(docHomeTeamSelect, response.data.teams_in_leagues_and_divisions);
    await updateTeamSelect(docAwayTeamSelect, response.data.teams_in_leagues_and_divisions);
    await updateScoreBug(response.data.game_data);
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
    
    await updateScoreBug(response.data.game_data);
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

    await updateScoreBug(response.data.game_data);
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

const updateScoreBug = async (gameData) => {
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