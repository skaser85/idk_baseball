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
const docGetGamesBtn = document.querySelector("#get-games");

const docGameNo = document.querySelector("#game-number");

const docTeamSelect = document.querySelector("#team-select");

const docSideOptions = document.querySelectorAll("input[name='team']");
let SIDE_SELECTED = "home";

const docSaveLineupBtn = document.querySelector("#save-lineup");

let gameData = {};

docCreateGameBtn.addEventListener("click", async e => {
    let response = await axios({
        method: "get",
        url: "http://192.168.1.4:8008/creategame",
        responseType: "JSON"
    });

    gameData = response.data.game_data;

    clearSelect(docGameNo);
    let opt = document.createElement("option");
    opt.value = gameData.id;
    opt.innerHTML = gameData.id;
    docGameNo.add(opt);

    await updateTeamSelect();
    await updateScoreBug();
});

docGetGamesBtn.addEventListener("click", async e => {
    let response = await axios({
        method: "get",
        url: "http://192.168.1.4:8008/getgames",
        responseType: "JSON"
    });

    let games = response.data.games;

    console.log(games);

    for(let game of games) {
        let opt = document.createElement("option");
        opt.value = game;
        opt.innerHTML = game;
        docGameNo.add(opt);
    }
});

docGameNo.addEventListener("change", async e => {
    let gameID = e.target.value;
    if (gameID === "")
        return

    
    let response = await axios({
        method: "post",
        url: "http://192.168.1.4:8008/getgame",
        responseType: "JSON",
        data: { gameID }
    });
    
    gameData = response.data.game_data;
    console.log(SIDE_SELECTED);

    await updateScoreBug();
    await updateTeamSelect();
    await updateLineup();

    console.log(SIDE_SELECTED);
    if (SIDE_SELECTED === "home") {
        if (!isEmptyObject(gameData.homeTeam)) {
            docTeamSelect.value = gameData.homeTeam.fullTeamName;
        }
    } else {
        if (!isEmptyObject(gameData.awayTeam)) {
            docTeamSelect.value = gameData.awayTeam.fullTeamName;
        }
    }
});

docTeamSelect.addEventListener("change", async e => {
    let teamName = e.target.value;
    if (teamName === "")
        return
    
    let response = await axios({
        method: "post",
        url: "http://192.168.1.4:8008/addteam",
        responseType: "JSON",
        data: {
            teamName,
            "gameID": docGameNo.value,
            "side": SIDE_SELECTED
        }
    });
    
    gameData = response.data.game_data;

    await updateScoreBug();
    await updateLineup();
});

docSaveLineupBtn.addEventListener("click", async e => {
    let teamID = SIDE_SELECTED === "home" ? gameData.homeTeam.id : gameData.awayTeam.id;
    let docPlayerSelects = document.querySelectorAll(".player-select");
    let lineup = [];
    docPlayerSelects.forEach(s => {
        if (s.value.length) {
            let orderNo = 0;
            let isPitcher = true;
            if (s.id !== "starting-pitcher"){
                orderNo = s.id.split("-")[2];
                isPitcher = false;
            }
            let playerID = s.value.split("-")[0];
            lineup.push({ playerID, orderNo, isPitcher });
        } else {
            lineup.push({});
        }
    });
    console.log(lineup);

    let response = await axios({
        method: "post",
        url: "http://192.168.1.4:8008/savelineup",
        responseType: "JSON",
        data: {
            gameID: gameData.id,
            teamID,
            lineup: JSON.stringify(lineup)
        }
    });

    gameData = response.data.game_data;

    await updateScoreBug();
});

for (let opt of docSideOptions) {
    opt.addEventListener("change", async e => {
        let side = e.target;
        SIDE_SELECTED = e.target.id.split("-")[0];
        
        let response = await axios({
            method: "post",
            url: "http://192.168.1.4:8008/getgame",
            responseType: "JSON",
            data: { "gameID": gameData.id }
        });

        gameData = response.data.game_data;

        if (SIDE_SELECTED === "home") {
            if (isEmptyObject(gameData.homeTeam)) {
                updateTeamSelect();
            } else {
                docTeamSelect.value = gameData.homeTeam.fullTeamName;
            }
        } else {
            if (isEmptyObject(gameData.awayTeam)) {
                updateTeamSelect();
            } else {
                docTeamSelect.value = gameData.awayTeam.fullTeamName;
            }
        }

        await updateScoreBug();
        await updateLineup();
    });
}

const updateLineup = async () => {
    return new Promise((resolve, reject) => {
        let battingOrderData = {};
        let pitchers = {};
    
        if (SIDE_SELECTED === "home") {
            if (!isEmptyObject(gameData.homeTeam)) {
                battingOrderData = gameData.homeTeam.battingOrderData.batting_order_data;
                pitchers = gameData.homeTeam.battingOrderData.batting_order_data.Pitchers
                lineup = gameData.homeTeam.lineup;
            }
        } else {
            if (!isEmptyObject(gameData.awayTeam)) {
                battingOrderData = gameData.awayTeam.battingOrderData.batting_order_data;
                pitchers = gameData.awayTeam.battingOrderData.batting_order_data.Pitchers
                lineup = gameData.awayTeam.lineup;
            }
        }

        for (let i=1; i<10; i++) {
            let el = document.querySelector(`#batting-order-${i}`);
            addBatters(el, battingOrderData, lineup);
        }
        
        let el = document.querySelector('#starting-pitcher');
        addSP(el, pitchers);
    });
}

const updateTeamSelect = async () => {
    await clearSelect(docTeamSelect);
    
    let response = await axios({
        method: "get",
        url: "http://192.168.1.4:8008/getteamsforteamselect",
        responseType: "JSON"
    });

    teamsLeaguesDivs = response.data.teamsLeaguesDivs;

    for (let leagueDiv of Object.keys(teamsLeaguesDivs)) {
        let teams = teamsLeaguesDivs[leagueDiv];
        let optgroup = document.createElement("optgroup");
        optgroup.label = leagueDiv;
        docTeamSelect.add(optgroup);
        for (let team of teams) {
            let opt = document.createElement("option");
            opt.value = team;
            opt.innerHTML = team;
            docTeamSelect.add(opt);
        }
    }
}

const clearSelect = async select => {
    return new Promise((resolve, reject) => {
        for (i = select.options.length - 1; i >= 0; i--) {
            select.remove(i);
        }
        let optgroups = select.querySelectorAll("optgroup");
        if (optgroups.length > 0) {
            for (i = optgroups.length - 1; i >= 0; i--) {
                optgroups[i].remove();
            }
        }
        let opt = document.createElement("option");
        opt.value = "";
        opt.innerHTML = "";
        select.add(opt);
        resolve(true);
    });
}

const addBatters = async (select, battingOrderData, lineup) => {
    await clearSelect(select);
    if (isEmptyObject(battingOrderData))
        return
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

    orderNo = select.id.split("-")[2]
    if (!isEmptyObject(lineup)) {
        if (orderNo in lineup) {
            select.value = lineup[orderNo].batting_order_text;
        }
    }
}

const addSP = async (select, pitchers) => {
    await clearSelect(select);
    if (isEmptyObject(pitchers))
        return
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
            if (gameData.awayTeam.colors.length > 0) 
                color = `#${gameData.awayTeam.colors[0].hex}`
            docTopTeamContainer.style.backgroundColor = color;
        }
        docTopTeamScore.innerHTML = gameData.awayScore;
            
        docBottomTeamName.innerHTML = ""
        docBottomTeamContainer.style.backgroundColor = "#000";
        if (!isEmptyObject(gameData.homeTeam)) {
            docBottomTeamName.innerHTML = gameData.homeTeam.shortName;
            let color = "#000";
            if (gameData.homeTeam.colors.length > 0) 
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