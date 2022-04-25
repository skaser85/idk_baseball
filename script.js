const docPitcherName = document.querySelector(".pitcher-name");
const docPitchSpeed = document.querySelector(".pitch-speed");

const docBatterName = document.querySelector(".batter-name");
const docBattingOrderNo = document.querySelector(".batting-order-number");
const docBattingAvg = document.querySelector(".batting-average");

const docTopTeamName = document.querySelector(".top-team-name");
const docTopTeamScore = document.querySelector(".top-team-score");
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

docCreateGameBtn.addEventListener("click", async (e) => {
    // e.preventDefault();

    let response = await axios({
        method: "get",
        url: "http://192.168.1.4:8008/creategame",
        responseType: "JSON"
    });

    await updateTeamSelects(response.data);
});

const updateTeamSelects = async data => {
    console.log(data);
    docGameNo.value = data.game_no;
    await updateTeamSelect(docHomeTeamSelect, data.teams);
    await updateTeamSelect(docAwayTeamSelect, data.teams);
}

const updateTeamSelect = async (select, teams) => {
    for (let team of teams) {
        let teamName = `${team.city} ${team.name}`
        let opt = document.createElement("option");
        opt.value = teamName;
        opt.innerHTML = teamName;
        select.add(opt);
    }
}