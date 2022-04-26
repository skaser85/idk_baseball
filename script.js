const docPitcherName = document.querySelector(".pitcher-name");
const docPitchSpeed = document.querySelector(".pitch-speed");

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
const docThirdBase = docBatterName.querySelector(".third-base")

const docInningArrow = document.querySelector(".inning-arrow");
const docInningNo = document.querySelector(".inning-number");
const docOutsNo = document.querySelector(".outs-number");
const docBalls = document.querySelector(".balls");
const docStrikes = docBalls.querySelector(".strikes");

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

    docGameNo.value = response.data.game_no;
    await updateTeamSelect(docHomeTeamSelect, response.data.teams_in_leagues_and_divisions);
    await updateTeamSelect(docAwayTeamSelect, response.data.teams_in_leagues_and_divisions);
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

docHomeTeamSelect.addEventListener("change", async e => {
    let teamName = e.target.value;
    if (teamName === "")
        return
    
    let response = await axios({
        method: "post",
        url: "http://192.168.1.4:8008/getteamdata",
        responseType: "JSON",
        data: { teamName, "gameID": docGameNo.value, "side": "Home" }
    });

    let data = response.data;

    docBottomTeamName.innerHTML = data.short_name;
    docBottomTeamContainer.style.backgroundColor = `#${data.colors[0].hex}`;
});

docAwayTeamSelect.addEventListener("change", async e => {
    let teamName = e.target.value;
    if (teamName === "")
        return
    
    let response = await axios({
        method: "post",
        url: "http://192.168.1.4:8008/getteamdata",
        responseType: "JSON",
        data: { teamName, "gameID": docGameNo.value, "side": "Away" }
    });

    let data = response.data;

    docTopTeamName.innerHTML = data.short_name;
    docTopTeamContainer.style.backgroundColor = `#${data.colors[0].hex}`;
});