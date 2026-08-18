import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Pixel Adventure",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    iframe {
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)


game = r"""
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">

<style>
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    overflow: hidden;
    background: #080b20;
    font-family: Arial, sans-serif;
}

#game {
    position: relative;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background:
        linear-gradient(
            180deg,
            #080b2e 0%,
            #15185c 35%,
            #385f9b 70%,
            #7ec8d8 100%
        );
}

canvas {
    width: 100%;
    height: 100%;
    display: block;
    outline: none;
}

#ui {
    position: absolute;
    top: 20px;
    left: 20px;
    right: 20px;
    display: flex;
    justify-content: space-between;
    color: white;
    font-size: 20px;
    font-weight: bold;
    text-shadow: 0 3px 5px #000;
    pointer-events: none;
    z-index: 3;
}

#title {
    position: absolute;
    top: 18px;
    left: 50%;
    transform: translateX(-50%);
    color: #fff;
    font-size: 22px;
    font-weight: bold;
    text-shadow: 0 3px 10px #000;
    pointer-events: none;
    z-index: 3;
}

#message {
    position: absolute;
    inset: 0;
    display: none;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    background: rgba(0, 0, 25, 0.65);
    color: white;
    text-align: center;
    z-index: 5;
}

#message h1 {
    font-size: 60px;
    margin-bottom: 15px;
    text-shadow: 0 5px 20px #000;
}

#message p {
    font-size: 22px;
    margin-bottom: 25px;
}

button {
    border: none;
    padding: 14px 30px;
    border-radius: 12px;
    background: linear-gradient(135deg, #ffcc33, #ff7b00);
    color: #251000;
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 5px 20px rgba(0,0,0,.4);
}

button:hover {
    transform: scale(1.05);
}

#controls {
    position: absolute;
    bottom: 20px;
    left: 20px;
    color: white;
    opacity: .8;
    font-size: 14px;
    text-shadow: 0 2px 4px black;
    pointer-events: none;
    z-index: 3;
}

#focusMessage {
    position: absolute;
    bottom: 20px;
    right: 20px;
    color: white;
    font-size: 14px;
    background: rgba(0,0,0,.35);
    padding: 8px 12px;
    border-radius: 8px;
    text-shadow: 0 2px 4px black;
    pointer-events: none;
    z-index: 3;
    transition: opacity .4s;
}
</style>
</head>

<body>

<div id="game">

    <canvas id="canvas" tabindex="0"></canvas>

    <div id="title">
        🌙 PIXEL ADVENTURE
    </div>

    <div id="ui">
        <div id="stats">
            ❤️ ❤️ ❤️ &nbsp;&nbsp; 🪙 0
        </div>

        <div id="level">
            LEVEL 1
        </div>
    </div>

    <div id="controls">
        WASD / Pfeiltasten = Bewegen &nbsp; | &nbsp; W / ↑ / Leertaste = Springen
    </div>

    <div id="focusMessage">
        🎮 Klicke ins Spiel und los geht's!
    </div>

    <div id="message">

        <h1 id="messageTitle">
            GAME OVER
        </h1>

        <p id="messageText">
            Versuche es noch einmal!
        </p>

        <button onclick="restart()">
            🔄 Neustart
        </button>

    </div>

</div>


<script>

/* =========================================================
   CANVAS
========================================================= */

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

let W;
let H;

function resize() {

    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;

}

window.addEventListener("resize", resize);

resize();


/* =========================================================
   GAME STATE
========================================================= */

let keys = {};

let cameraX = 0;

let score = 0;

let lives = 3;

let gameOver = false;

let won = false;

let lastTime = 0;

const worldWidth = 5000;


/* =========================================================
   PLAYER
========================================================= */

const player = {

    x: 150,

    y: 300,

    w: 38,

    h: 52,

    vx: 0,

    vy: 0,

    speed: 5,

    jump: -14,

    grounded: false,

    color: "#ff4d6d",

    invincible: 0

};


/* =========================================================
   INPUT
========================================================= */

/*
    WICHTIG:

    Streamlit läuft das Spiel in einem iframe.
    Deshalb bekommt das Canvas hier selbst den Tastatur-Fokus.

    Unterstützt werden:

    A
    D
    W
    Pfeil links
    Pfeil rechts
    Pfeil oben
    Pfeil unten
    Leertaste
*/


const movementKeys = [

    "a",
    "d",
    "w",

    "arrowleft",
    "arrowright",
    "arrowup",
    "arrowdown",

    " "

];


/*
    Wenn der Benutzer irgendwo auf das Spiel klickt,
    bekommt das Canvas den Fokus.
*/

canvas.addEventListener("click", function() {

    canvas.focus();

    const focusMessage =
        document.getElementById("focusMessage");

    focusMessage.style.opacity = "0";

});


/*
    Wenn das Canvas fokussiert wird.
*/

canvas.addEventListener("focus", function() {

    const focusMessage =
        document.getElementById("focusMessage");

    focusMessage.style.opacity = "0";

});


/*
    KEYDOWN

    Wir hören direkt auf dem Canvas.
*/

canvas.addEventListener("keydown", function(e) {

    const key = e.key.toLowerCase();

    if (movementKeys.includes(key)) {

        keys[key] = true;

        e.preventDefault();

    }

});


/*
    KEYUP
*/

canvas.addEventListener("keyup", function(e) {

    const key = e.key.toLowerCase();

    if (movementKeys.includes(key)) {

        keys[key] = false;

        e.preventDefault();

    }

});


/*
    Zusätzlich globale Tastatur-Events.

    Dadurch funktioniert die Steuerung auch dann,
    wenn der Browser den Fokus kurz anders behandelt.
*/

window.addEventListener("keydown", function(e) {

    const key = e.key.toLowerCase();

    if (movementKeys.includes(key)) {

        keys[key] = true;

        e.preventDefault();

    }

});


window.addEventListener("keyup", function(e) {

    const key = e.key.toLowerCase();

    if (movementKeys.includes(key)) {

        keys[key] = false;

        e.preventDefault();

    }

});


/*
    Canvas direkt beim Start fokussieren.
*/

setTimeout(function() {

    canvas.focus();

}, 300);


/* =========================================================
   LEVEL
========================================================= */

const platforms = [

    {
        x: 0,
        y: 500,
        w: 800,
        h: 100
    },

    {
        x: 900,
        y: 450,
        w: 450,
        h: 150
    },

    {
        x: 1450,
        y: 520,
        w: 600,
        h: 80
    },

    {
        x: 2150,
        y: 430,
        w: 500,
        h: 170
    },

    {
        x: 2750,
        y: 500,
        w: 650,
        h: 100
    },

    {
        x: 3500,
        y: 420,
        w: 500,
        h: 180
    },

    {
        x: 4150,
        y: 500,
        w: 850,
        h: 100
    }

];


/* =========================================================
   COINS
========================================================= */

const coins = [

    {
        x: 300,
        y: 430,
        collected: false
    },

    {
        x: 600,
        y: 390,
        collected: false
    },

    {
        x: 1000,
        y: 380,
        collected: false
    },

    {
        x: 1200,
        y: 330,
        collected: false
    },

    {
        x: 1600,
        y: 450,
        collected: false
    },

    {
        x: 1850,
        y: 450,
        collected: false
    },

    {
        x: 2300,
        y: 360,
        collected: false
    },

    {
        x: 2500,
        y: 320,
        collected: false
    },

    {
        x: 2950,
        y: 430,
        collected: false
    },

    {
        x: 3250,
        y: 430,
        collected: false
    },

    {
        x: 3650,
        y: 350,
        collected: false
    },

    {
        x: 3900,
        y: 350,
        collected: false
    },

    {
        x: 4350,
        y: 430,
        collected: false
    },

    {
        x: 4650,
        y: 430,
        collected: false
    }

];


/* =========================================================
   ENEMIES
========================================================= */

const enemies = [

    {
        x: 550,
        y: 450,
        w: 40,
        h: 40,
        vx: 1.5,
        min: 450,
        max: 750
    },

    {
        x: 1100,
        y: 400,
        w: 40,
        h: 40,
        vx: 1.8,
        min: 920,
        max: 1300
    },

    {
        x: 1750,
        y: 470,
        w: 40,
        h: 40,
        vx: 1.5,
        min: 1500,
        max: 2000
    },

    {
        x: 2350,
        y: 380,
        w: 40,
        h: 40,
        vx: 2,
        min: 2180,
        max: 2600
    },

    {
        x: 3100,
        y: 450,
        w: 40,
        h: 40,
        vx: 1.7,
        min: 2800,
        max: 3350
    },

    {
        x: 3700,
        y: 370,
        w: 40,
        h: 40,
        vx: 2,
        min: 3550,
        max: 3950
    }

];


/* =========================================================
   BACKGROUND
========================================================= */

function drawSky() {

    const gradient =
        ctx.createLinearGradient(
            0,
            0,
            0,
            H
        );

    gradient.addColorStop(
        0,
        "#070b2f"
    );

    gradient.addColorStop(
        .45,
        "#18215f"
    );

    gradient.addColorStop(
        1,
        "#65b6c7"
    );

    ctx.fillStyle = gradient;

    ctx.fillRect(
        0,
        0,
        W,
        H
    );


    /* Mond */

    ctx.beginPath();

    ctx.arc(
        W - 130,
        100,
        55,
        0,
        Math.PI * 2
    );

    ctx.fillStyle =
        "#fff3b0";

    ctx.shadowBlur = 35;

    ctx.shadowColor =
        "#fff3b0";

    ctx.fill();

    ctx.shadowBlur = 0;


    /* Sterne */

    for (
        let i = 0;
        i < 80;
        i++
    ) {

        const x =
            (i * 157) % W;

        const y =
            (i * 71) %
            (H * .55);

        ctx.fillStyle =
            "rgba(255,255,255,.8)";

        ctx.fillRect(
            x,
            y,
            2,
            2
        );

    }

}


/* =========================================================
   MOUNTAINS
========================================================= */

function drawMountains(
    offset,
    color,
    height
) {

    ctx.fillStyle = color;

    ctx.beginPath();

    ctx.moveTo(
        0,
        H
    );

    for (
        let x = -100;
        x <= W + 200;
        x += 180
    ) {

        const px =
            x -
            (cameraX * offset) % 180;

        ctx.lineTo(
            px,
            H - height
        );

        ctx.lineTo(
            px + 90,
            H - height - 130
        );

        ctx.lineTo(
            px + 180,
            H - height
        );

    }

    ctx.lineTo(
        W,
        H
    );

    ctx.closePath();

    ctx.fill();

}


/* =========================================================
   BACKGROUND
========================================================= */

function drawBackground() {

    drawSky();

    drawMountains(
        .08,
        "#11173d",
        220
    );

    drawMountains(
        .16,
        "#172550",
        170
    );

    drawMountains(
        .25,
        "#213c63",
        130
    );


    /* Nebel */

    const fog =
        ctx.createLinearGradient(
            0,
            H * .55,
            0,
            H
        );

    fog.addColorStop(
        0,
        "rgba(255,255,255,0)"
    );

    fog.addColorStop(
        1,
        "rgba(190,240,240,.25)"
    );

    ctx.fillStyle = fog;

    ctx.fillRect(
        0,
        H * .5,
        W,
        H * .5
    );

}


/* =========================================================
   PLAYER DRAW
========================================================= */

function drawPlayer() {

    const x =
        player.x - cameraX;

    const y =
        player.y;


    /* Schatten */

    ctx.fillStyle =
        "rgba(0,0,0,.3)";

    ctx.beginPath();

    ctx.ellipse(
        x + 19,
        y + 53,
        24,
        7,
        0,
        0,
        Math.PI * 2
    );

    ctx.fill();


    /* Körper */

    ctx.fillStyle =
        player.color;

    ctx.fillRect(
        x + 4,
        y + 15,
        30,
        35
    );


    /* Kopf */

    ctx.fillStyle =
        "#ffd1b3";

    ctx.fillRect(
        x + 7,
        y,
        24,
        23
    );


    /* Haare */

    ctx.fillStyle =
        "#351c46";

    ctx.fillRect(
        x + 5,
        y - 3,
        28,
        8
    );


    /* Augen */

    ctx.fillStyle =
        "#111";

    ctx.fillRect(
        x + 13,
        y + 9,
        3,
        4
    );

    ctx.fillRect(
        x + 23,
        y + 9,
        3,
        4
    );


    /* Beine */

    ctx.fillStyle =
        "#292b63";

    ctx.fillRect(
        x + 6,
        y + 44,
        10,
        10
    );

    ctx.fillRect(
        x + 23,
        y + 44,
        10,
        10
    );

}


/* =========================================================
   PLATFORMS
========================================================= */

function drawPlatforms() {

    for (const p of platforms) {

        const x =
            p.x - cameraX;


        if (
            x + p.w < 0 ||
            x > W
        ) {

            continue;

        }


        /* Erde */

        ctx.fillStyle =
            "#49352a";

        ctx.fillRect(
            x,
            p.y,
            p.w,
            p.h
        );


        /* Gras */

        ctx.fillStyle =
            "#43b047";

        ctx.fillRect(
            x,
            p.y,
            p.w,
            14
        );


        /* helles Gras */

        ctx.fillStyle =
            "#75d66c";

        ctx.fillRect(
            x,
            p.y,
            p.w,
            5
        );


        /* Steine */

        ctx.fillStyle =
            "#70503b";

        for (
            let i = 20;
            i < p.w;
            i += 80
        ) {

            ctx.fillRect(
                x + i,
                p.y + 40,
                12,
                8
            );

        }

    }

}


/* =========================================================
   COINS
========================================================= */

function drawCoins(time) {

    for (const c of coins) {

        if (c.collected) {

            continue;

        }


        const x =
            c.x - cameraX;


        if (
            x < -50 ||
            x > W + 50
        ) {

            continue;

        }


        const bob =
            Math.sin(
                time / 200 + c.x
            ) * 5;


        ctx.beginPath();

        ctx.arc(
            x,
            c.y + bob,
            12,
            0,
            Math.PI * 2
        );

        ctx.fillStyle =
            "#ffd43b";

        ctx.shadowBlur = 15;

        ctx.shadowColor =
            "#ffd43b";

        ctx.fill();

        ctx.shadowBlur = 0;


        ctx.fillStyle =
            "#fff1a3";

        ctx.fillRect(
            x - 3,
            c.y - 7 + bob,
            3,
            10
        );

    }

}


/* =========================================================
   ENEMIES
========================================================= */

function drawEnemies() {

    for (const e of enemies) {

        const x =
            e.x - cameraX;


        /* Körper */

        ctx.fillStyle =
            "#7c3aed";

        ctx.fillRect(
            x,
            e.y,
            e.w,
            e.h
        );


        /* Kopf */

        ctx.fillStyle =
            "#a855f7";

        ctx.fillRect(
            x + 5,
            e.y + 5,
            30,
            15
        );


        /* Augen */

        ctx.fillStyle =
            "white";

        ctx.fillRect(
            x + 8,
            e.y + 13,
            8,
            8
        );

        ctx.fillRect(
            x + 24,
            e.y + 13,
            8,
            8
        );


        /* Pupillen */

        ctx.fillStyle =
            "#111";

        ctx.fillRect(
            x + 11,
            e.y + 16,
            4,
            5
        );

        ctx.fillRect(
            x + 27,
            e.y + 16,
            4,
            5
        );

    }

}


/* =========================================================
   GOAL
========================================================= */

function drawGoal() {

    const x =
        4800 - cameraX;


    /* Fahnenstange */

    ctx.fillStyle =
        "#38220f";

    ctx.fillRect(
        x,
        350,
        15,
        150
    );


    /* Flagge */

    ctx.fillStyle =
        "#ffcf33";

    ctx.beginPath();

    ctx.moveTo(
        x + 15,
        350
    );

    ctx.lineTo(
        x + 100,
        380
    );

    ctx.lineTo(
        x + 15,
        410
    );

    ctx.closePath();

    ctx.fill();


    /* Schrift */

    ctx.fillStyle =
        "white";

    ctx.font =
        "bold 18px Arial";

    ctx.fillText(
        "ZIEL",
        x + 25,
        390
    );

}


/* =========================================================
   COLLISION
========================================================= */

function collision(a, b) {

    return (

        a.x <
        b.x + b.w &&

        a.x + a.w >
        b.x &&

        a.y <
        b.y + b.h &&

        a.y + a.h >
        b.y

    );

}


/* =========================================================
   UPDATE
========================================================= */

function update(dt) {

    if (
        gameOver ||
        won
    ) {

        return;

    }


    /* =====================================================
       MOVEMENT
    ===================================================== */


    /*
        LINKS:

        A
        Pfeil links
    */

    const movingLeft =
        keys["a"] ||
        keys["arrowleft"];


    /*
        RECHTS:

        D
        Pfeil rechts
    */

    const movingRight =
        keys["d"] ||
        keys["arrowright"];


    /*
        Wenn links gedrückt:
    */

    if (movingLeft) {

        player.vx =
            -player.speed;

    }


    /*
        Wenn rechts gedrückt:
    */

    else if (movingRight) {

        player.vx =
            player.speed;

    }


    /*
        Keine Richtung:

        Spieler wird langsamer.
    */

    else {

        player.vx *= 0.8;

    }


    /* =====================================================
       JUMP
    ===================================================== */


    const jumping =
        keys["w"] ||
        keys["arrowup"] ||
        keys[" "];


    if (
        jumping &&
        player.grounded
    ) {

        player.vy =
            player.jump;

        player.grounded =
            false;

    }


    /* =====================================================
       GRAVITY
    ===================================================== */

    player.vy += 0.65;


    /* =====================================================
       PLAYER POSITION
    ===================================================== */

    player.x +=
        player.vx;

    player.y +=
        player.vy;


    /* Weltgrenzen */

    if (
        player.x < 0
    ) {

        player.x = 0;

    }


    if (
        player.x >
        worldWidth - player.w
    ) {

        player.x =
            worldWidth - player.w;

    }


    player.grounded =
        false;


    /* =====================================================
       PLATFORM COLLISION
    ===================================================== */

    for (const p of platforms) {

        const wasAbove =
            player.y +
            player.h -
            player.vy <=
            p.y;


        if (

            player.x +
            player.w >
            p.x &&

            player.x <
            p.x + p.w &&

            player.y +
            player.h >=
            p.y &&

            player.y +
            player.h <=
            p.y + 30 &&

            wasAbove &&

            player.vy >= 0

        ) {

            player.y =
                p.y -
                player.h;

            player.vy =
                0;

            player.grounded =
                true;

        }

    }


    /* =====================================================
       COINS
    ===================================================== */

    for (const c of coins) {

        if (
            c.collected
        ) {

            continue;

        }


        const coinBox = {

            x:
                c.x - 12,

            y:
                c.y - 12,

            w:
                24,

            h:
                24

        };


        if (
            collision(
                player,
                coinBox
            )
        ) {

            c.collected =
                true;

            score++;

        }

    }


    /* =====================================================
       ENEMIES
    ===================================================== */

    for (const e of enemies) {

        e.x +=
            e.vx;


        if (
            e.x < e.min ||
            e.x > e.max
        ) {

            e.vx *= -1;

        }


        if (
            collision(
                player,
                e
            ) &&
            player.invincible <= 0
        ) {


            /*
                Gegner von oben treffen
            */

            if (
                player.vy > 0 &&
                player.y +
                player.h -
                e.y < 25
            ) {

                player.vy =
                    -9;

                /*
                    Gegner entfernen
                */

                e.x =
                    -1000;

                score += 2;

            }


            /*
                Spieler wird getroffen
            */

            else {

                lives--;

                player.invincible =
                    100;

                player.x -=
                    80;


                if (
                    lives <= 0
                ) {

                    endGame(false);

                }

            }

        }

    }


    /* =====================================================
       INVINCIBILITY
    ===================================================== */

    if (
        player.invincible > 0
    ) {

        player.invincible--;

    }


    /* =====================================================
       FALL
    ===================================================== */

    if (
        player.y >
        H + 150
    ) {

        lives--;


        if (
            lives <= 0
        ) {

            endGame(false);

        }


        else {

            player.x -=
                150;

            player.y =
                200;

            player.vy =
                0;

        }

    }


    /* =====================================================
       CAMERA
    ===================================================== */

    const targetCamera =
        player.x -
        W * .35;


    cameraX +=
        (
            targetCamera -
            cameraX
        ) * .08;


    cameraX =
        Math.max(
            0,
            Math.min(
                cameraX,
                worldWidth - W
            )
        );


    /* =====================================================
       WIN
    ===================================================== */

    if (
        player.x > 4750
    ) {

        endGame(true);

    }


    updateUI();

}


/* =========================================================
   UI
========================================================= */

function updateUI() {

    let hearts = "";


    for (
        let i = 0;
        i < lives;
        i++
    ) {

        hearts +=
            "❤️ ";

    }


    document.getElementById(
        "stats"
    ).innerHTML =

        hearts +
        "&nbsp;&nbsp; 🪙 " +
        score;

}


/* =========================================================
   END GAME
========================================================= */

function endGame(win) {

    gameOver =
        true;

    won =
        win;


    const message =
        document.getElementById(
            "message"
        );


    message.style.display =
        "flex";


    if (win) {

        document.getElementById(
            "messageTitle"
        ).innerText =
            "🏆 LEVEL GESCHAFFT!";


        document.getElementById(
            "messageText"
        ).innerText =

            "Du hast " +
            score +
            " Münzen gesammelt!";

    }


    else {

        document.getElementById(
            "messageTitle"
        ).innerText =
            "💀 GAME OVER";


        document.getElementById(
            "messageText"
        ).innerText =

            "Du hast " +
            score +
            " Münzen gesammelt.";

    }

}


/* =========================================================
   RESTART
========================================================= */

function restart() {

    player.x =
        150;

    player.y =
        300;

    player.vx =
        0;

    player.vy =
        0;

    player.grounded =
        false;


    score =
        0;

    lives =
        3;


    cameraX =
        0;


    gameOver =
        false;

    won =
        false;


    /*
        Coins zurücksetzen
    */

    for (const c of coins) {

        c.collected =
            false;

    }


    /*
        Gegner zurücksetzen
    */

    enemies[0].x =
        550;

    enemies[1].x =
        1100;

    enemies[2].x =
        1750;

    enemies[3].x =
        2350;

    enemies[4].x =
        3100;

    enemies[5].x =
        3700;


    /*
        Gegnergeschwindigkeit
        wiederherstellen
    */

    enemies[0].vx =
        1.5;

    enemies[1].vx =
        1.8;

    enemies[2].vx =
        1.5;

    enemies[3].vx =
        2;

    enemies[4].vx =
        1.7;

    enemies[5].vx =
        2;


    /*
        Tastatur zurücksetzen
    */

    keys = {};


    document.getElementById(
        "message"
    ).style.display =
        "none";


    updateUI();


    /*
        Canvas wieder fokussieren
    */

    canvas.focus();

}


/* =========================================================
   GAME LOOP
========================================================= */

function loop(time) {

    const dt =
        Math.min(
            time - lastTime,
            40
        );


    lastTime =
        time;


    update(dt);


    /* =====================================================
       CLEAR
    ===================================================== */

    ctx.clearRect(
        0,
        0,
        W,
        H
    );


    /* =====================================================
       DRAW BACKGROUND
    ===================================================== */

    drawBackground();


    /* =====================================================
       DRAW LEVEL
    ===================================================== */

    drawPlatforms();


    drawCoins(
        time
    );


    drawEnemies();


    drawGoal();


    /* =====================================================
       DRAW PLAYER
    ===================================================== */

    if (

        player.invincible <= 0 ||

        Math.floor(
            player.invincible / 5
        ) % 2 === 0

    ) {

        drawPlayer();

    }


    requestAnimationFrame(
        loop
    );

}


/* =========================================================
   START
========================================================= */

updateUI();

requestAnimationFrame(
    loop
);


/*
    Canvas automatisch fokussieren
*/

setTimeout(function() {

    canvas.focus();

}, 500);


</script>

</body>
</html>
"""


components.html(
    game,
    height=800,
    scrolling=False
)
