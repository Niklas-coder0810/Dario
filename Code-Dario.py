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
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

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

html,
body {
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #080b20;
    font-family: Arial, sans-serif;
}

body {
    overflow: hidden;
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

    text-shadow:
        0 3px 5px #000;

    pointer-events: none;

    z-index: 10;
}

#title {

    position: absolute;

    top: 18px;
    left: 50%;

    transform:
        translateX(-50%);

    color: white;

    font-size: 22px;

    font-weight: bold;

    text-shadow:
        0 3px 10px #000;

    pointer-events: none;

    z-index: 10;
}

#controls {

    position: absolute;

    bottom: 20px;
    left: 20px;

    color: white;

    opacity: 0.8;

    font-size: 14px;

    text-shadow:
        0 2px 4px black;

    pointer-events: none;

    z-index: 10;
}

#distance {

    position: absolute;

    bottom: 20px;
    right: 20px;

    color: white;

    opacity: 0.85;

    font-size: 14px;

    text-shadow:
        0 2px 4px black;

    pointer-events: none;

    z-index: 10;
}

#focusMessage {

    position: absolute;

    bottom: 60px;
    left: 50%;

    transform:
        translateX(-50%);

    color: white;

    background:
        rgba(0,0,0,.45);

    padding:
        10px 16px;

    border-radius:
        10px;

    font-size:
        14px;

    text-shadow:
        0 2px 4px black;

    pointer-events:
        none;

    z-index:
        20;

    transition:
        opacity .5s;
}

#message {

    position: absolute;

    inset: 0;

    display: none;

    align-items: center;

    justify-content: center;

    flex-direction: column;

    background:
        rgba(0, 0, 25, 0.70);

    color: white;

    text-align: center;

    z-index: 50;
}

#message h1 {

    font-size:
        60px;

    margin-bottom:
        15px;

    text-shadow:
        0 5px 20px #000;
}

#message p {

    font-size:
        22px;

    margin-bottom:
        25px;
}

button {

    border: none;

    padding:
        14px 30px;

    border-radius:
        12px;

    background:
        linear-gradient(
            135deg,
            #ffcc33,
            #ff7b00
        );

    color:
        #251000;

    font-size:
        20px;

    font-weight:
        bold;

    cursor:
        pointer;

    box-shadow:
        0 5px 20px
        rgba(0,0,0,.4);
}

button:hover {

    transform:
        scale(1.05);
}

</style>

</head>


<body>

<div id="game">

    <canvas
        id="canvas"
        tabindex="0">
    </canvas>


    <div id="title">
        🌙 PIXEL ADVENTURE
    </div>


    <div id="ui">

        <div id="stats">
            ❤️ ❤️ ❤️ &nbsp;&nbsp; 🪙 0
        </div>

        <div id="level">
            ENDLESS WORLD
        </div>

    </div>


    <div id="controls">
        WASD / Pfeiltasten = Bewegen
        &nbsp; | &nbsp;
        W / ↑ / Leertaste = Springen
    </div>


    <div id="distance">
        📏 0 m
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

const canvas =
    document.getElementById("canvas");

const ctx =
    canvas.getContext("2d");


let W = 0;
let H = 0;


function resize() {

    W =
        canvas.width =
        window.innerWidth;

    H =
        canvas.height =
        window.innerHeight;

}


window.addEventListener(
    "resize",
    resize
);

resize();


/* =========================================================
   GAME STATE
========================================================= */

let keys = {};

let cameraX = 0;

let score = 0;

let lives = 3;

let gameOver = false;

let lastTime = 0;

let worldGeneratedUntil = 0;

let highestPlatform = 0;

let distanceTravelled = 0;


/*
    Die Welt wird immer weiter erzeugt.

    Dadurch gibt es kein festes Ende.
*/

const generationDistance = 2500;


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


canvas.addEventListener(
    "click",
    function() {

        canvas.focus();

        document
            .getElementById(
                "focusMessage"
            )
            .style.opacity = "0";

    }
);


canvas.addEventListener(
    "focus",
    function() {

        document
            .getElementById(
                "focusMessage"
            )
            .style.opacity = "0";

    }
);


canvas.addEventListener(
    "keydown",
    function(e) {

        const key =
            e.key.toLowerCase();

        if (
            movementKeys.includes(key)
        ) {

            keys[key] = true;

            e.preventDefault();

        }

    }
);


canvas.addEventListener(
    "keyup",
    function(e) {

        const key =
            e.key.toLowerCase();

        if (
            movementKeys.includes(key)
        ) {

            keys[key] = false;

            e.preventDefault();

        }

    }
);


/*
    Globale Events als zusätzliche
    Absicherung für Streamlit.
*/

window.addEventListener(
    "keydown",
    function(e) {

        const key =
            e.key.toLowerCase();

        if (
            movementKeys.includes(key)
        ) {

            keys[key] = true;

            e.preventDefault();

        }

    }
);


window.addEventListener(
    "keyup",
    function(e) {

        const key =
            e.key.toLowerCase();

        if (
            movementKeys.includes(key)
        ) {

            keys[key] = false;

            e.preventDefault();

        }

    }
);


setTimeout(
    function() {

        canvas.focus();

    },
    500
);


/* =========================================================
   WORLD ARRAYS
========================================================= */

const platforms = [];

const coins = [];

const enemies = [];


/* =========================================================
   RANDOM HELPER
========================================================= */

function random(min, max) {

    return (
        Math.random() *
        (max - min) +
        min
    );

}


function randomInt(min, max) {

    return Math.floor(
        random(min, max + 1)
    );

}


/* =========================================================
   ADD PLATFORM
========================================================= */

function addPlatform(
    x,
    y,
    w,
    h,
    floating = false
) {

    platforms.push({

        x: x,

        y: y,

        w: w,

        h: h,

        floating: floating

    });

}


/* =========================================================
   ADD COIN
========================================================= */

function addCoin(
    x,
    y
) {

    coins.push({

        x: x,

        y: y,

        collected: false

    });

}


/* =========================================================
   ADD ENEMY
========================================================= */

function addEnemy(
    x,
    y,
    min,
    max
) {

    enemies.push({

        x: x,

        y: y,

        w: 40,

        h: 40,

        vx:
            random(1.2, 2.1),

        min: min,

        max: max,

        active: true

    });

}


/* =========================================================
   INITIAL WORLD
========================================================= */


/*
    Startplattform
*/

addPlatform(
    0,
    500,
    1000,
    100,
    false
);


/*
    Einfache Münzen nahe am Boden.
*/

addCoin(
    260,
    455
);

addCoin(
    380,
    455
);

addCoin(
    520,
    455
);

addCoin(
    670,
    455
);

addCoin(
    820,
    455
);


/*
    Erste Gegner.
*/

addEnemy(
    600,
    460,
    450,
    900
);


/*
    Erzeuge direkt die ersten
    Abschnitte.
*/

worldGeneratedUntil = 1000;


/* =========================================================
   GENERATE ENDLESS WORLD
========================================================= */

function generateWorld() {

    while (
        worldGeneratedUntil <
        player.x + generationDistance
    ) {

        const startX =
            worldGeneratedUntil;


        /*
            Normale Bodenplattform.
        */

        const groundWidth =
            randomInt(
                500,
                850
            );


        /*
            Höhe des Bodens
            variiert leicht.
        */

        const groundY =
            randomInt(
                480,
                530
            );


        addPlatform(
            startX,
            groundY,
            groundWidth,
            100,
            false
        );


        /*
            Mehrere leicht erreichbare
            Münzen.

            Sie befinden sich nur
            wenige Pixel über dem Boden.
        */

        const coinCount =
            randomInt(
                4,
                7
            );


        for (
            let i = 0;
            i < coinCount;
            i++
        ) {

            const coinX =
                startX +
                80 +
                i *
                (
                    groundWidth /
                    (coinCount + 1)
                );


            addCoin(
                coinX,
                groundY - 35
            );

        }


        /*
            Gegner nur manchmal.
        */

        if (
            Math.random() < 0.75
        ) {

            const enemyX =
                startX +
                random(
                    180,
                    groundWidth - 100
                );


            addEnemy(
                enemyX,
                groundY - 40,
                startX + 80,
                startX + groundWidth - 80
            );

        }


        /*
            =================================================
            SCHWEBENDE PLATTFORM
            =================================================

            Ein Teil der Welt bekommt
            eine Plattform in der Luft.
        */

        if (
            Math.random() < 0.72
        ) {

            const floatingX =
                startX +
                random(
                    100,
                    Math.max(
                        150,
                        groundWidth - 250
                    )
                );


            const floatingY =
                randomInt(
                    270,
                    390
                );


            const floatingWidth =
                randomInt(
                    180,
                    320
                );


            addPlatform(
                floatingX,
                floatingY,
                floatingWidth,
                28,
                true
            );


            /*
                Münzen auf der
                schwebenden Plattform.

                Dadurch muss der Spieler
                wirklich hochspringen.
            */

            const floatingCoins =
                randomInt(
                    2,
                    4
                );


            for (
                let i = 0;
                i < floatingCoins;
                i++
            ) {

                const coinX =
                    floatingX +
                    45 +
                    i *
                    (
                        (
                            floatingWidth - 90
                        ) /
                        Math.max(
                            1,
                            floatingCoins - 1
                        )
                    );


                addCoin(
                    coinX,
                    floatingY - 32
                );

            }


            /*
                Manchmal noch eine
                zweite, höhere Plattform.
            */

            if (
                Math.random() < 0.35
            ) {

                const upperX =
                    floatingX +
                    random(
                        -60,
                        floatingWidth - 80
                    );


                const upperY =
                    Math.max(
                        170,
                        floatingY - random(
                            100,
                            150
                        )
                    );


                const upperWidth =
                    randomInt(
                        150,
                        240
                    );


                addPlatform(
                    upperX,
                    upperY,
                    upperWidth,
                    26,
                    true
                );


                /*
                    Münzen auch hier.
                */

                addCoin(
                    upperX +
                    upperWidth / 2,
                    upperY - 32
                );

            }

        }


        /*
            Gelegentlich eine
            Münz-Reihe in der Luft.
        */

        if (
            Math.random() < 0.45
        ) {

            const airStartX =
                startX +
                random(
                    100,
                    groundWidth - 150
                );


            const airY =
                randomInt(
                    300,
                    400
                );


            for (
                let i = 0;
                i < 4;
                i++
            ) {

                addCoin(
                    airStartX +
                    i * 45,
                    airY -
                    Math.sin(i * 0.8) * 25
                );

            }

        }


        /*
            Nächster Abschnitt.
        */

        worldGeneratedUntil =
            startX +
            groundWidth +
            randomInt(
                80,
                180
            );

    }

}


/* =========================================================
   DRAW SKY
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
        0.40,
        "#18215f"
    );

    gradient.addColorStop(
        0.72,
        "#385f9b"
    );

    gradient.addColorStop(
        1,
        "#65b6c7"
    );


    ctx.fillStyle =
        gradient;


    ctx.fillRect(
        0,
        0,
        W,
        H
    );


    /*
        Mond
    */

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


    ctx.shadowBlur =
        35;


    ctx.shadowColor =
        "#fff3b0";


    ctx.fill();


    ctx.shadowBlur =
        0;


    /*
        Sterne.
    */

    for (
        let i = 0;
        i < 100;
        i++
    ) {

        const x =
            (
                i * 157
                -
                cameraX * 0.03
            ) % W;


        const y =
            (
                i * 71
            ) %
            (H * 0.55);


        const positiveX =
            x < 0
                ? x + W
                : x;


        ctx.fillStyle =
            "rgba(255,255,255,.8)";


        ctx.fillRect(
            positiveX,
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

    ctx.fillStyle =
        color;


    ctx.beginPath();


    ctx.moveTo(
        0,
        H
    );


    const mountainWidth =
        180;


    const start =
        -mountainWidth;


    for (
        let i = 0;
        i < 30;
        i++
    ) {

        const worldX =
            start +
            i *
            mountainWidth;


        const screenX =
            worldX -
            cameraX *
            offset;


        ctx.lineTo(
            screenX,
            H - height
        );


        ctx.lineTo(
            screenX +
            mountainWidth / 2,
            H -
            height -
            130
        );


        ctx.lineTo(
            screenX +
            mountainWidth,
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
        0.08,
        "#11173d",
        220
    );


    drawMountains(
        0.16,
        "#172550",
        170
    );


    drawMountains(
        0.25,
        "#213c63",
        130
    );


    /*
        Nebel
    */

    const fog =
        ctx.createLinearGradient(
            0,
            H * 0.55,
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


    ctx.fillStyle =
        fog;


    ctx.fillRect(
        0,
        H * 0.5,
        W,
        H * 0.5
    );

}


/* =========================================================
   PLAYER
========================================================= */

function drawPlayer() {

    const x =
        player.x -
        cameraX;


    const y =
        player.y;


    /*
        Schatten
    */

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


    /*
        Körper
    */

    ctx.fillStyle =
        player.color;


    ctx.fillRect(
        x + 4,
        y + 15,
        30,
        35
    );


    /*
        Kopf
    */

    ctx.fillStyle =
        "#ffd1b3";


    ctx.fillRect(
        x + 7,
        y,
        24,
        23
    );


    /*
        Haare
    */

    ctx.fillStyle =
        "#351c46";


    ctx.fillRect(
        x + 5,
        y - 3,
        28,
        8
    );


    /*
        Augen
    */

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


    /*
        Beine
    */

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

    for (
        const p of platforms
    ) {

        const x =
            p.x -
            cameraX;


        if (
            x + p.w < 0 ||
            x > W
        ) {

            continue;

        }


        /*
            Schwebende Plattform
        */

        if (
            p.floating
        ) {

            /*
                Glow
            */

            ctx.shadowBlur =
                12;

            ctx.shadowColor =
                "rgba(100,220,255,.6)";


            /*
                Unterseite
            */

            ctx.fillStyle =
                "#334a70";


            ctx.fillRect(
                x,
                p.y,
                p.w,
                p.h
            );


            /*
                Blaue Kante
            */

            ctx.fillStyle =
                "#5ed6e8";


            ctx.fillRect(
                x,
                p.y,
                p.w,
                6
            );


            ctx.shadowBlur =
                0;


            /*
                kleine Wolken-Partikel
            */

            ctx.fillStyle =
                "rgba(210,250,255,.25)";


            ctx.fillRect(
                x + 20,
                p.y + p.h,
                30,
                8
            );


            ctx.fillRect(
                x + p.w - 70,
                p.y + p.h,
                40,
                7
            );

        }


        /*
            normale Bodenplattform
        */

        else {

            /*
                Erde
            */

            ctx.fillStyle =
                "#49352a";


            ctx.fillRect(
                x,
                p.y,
                p.w,
                p.h
            );


            /*
                Gras
            */

            ctx.fillStyle =
                "#43b047";


            ctx.fillRect(
                x,
                p.y,
                p.w,
                14
            );


            /*
                helles Gras
            */

            ctx.fillStyle =
                "#75d66c";


            ctx.fillRect(
                x,
                p.y,
                p.w,
                5
            );


            /*
                Steine
            */

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

}


/* =========================================================
   COINS
========================================================= */

function drawCoins(time) {

    for (
        const c of coins
    ) {

        if (
            c.collected
        ) {

            continue;

        }


        const x =
            c.x -
            cameraX;


        if (
            x < -50 ||
            x > W + 50
        ) {

            continue;

        }


        /*
            Kleine Animation.
        */

        const bob =
            Math.sin(
                time / 200 +
                c.x
            ) * 5;


        /*
            Glow
        */

        ctx.shadowBlur =
            15;


        ctx.shadowColor =
            "#ffd43b";


        ctx.beginPath();


        ctx.arc(
            x,
            c.y + bob,
            13,
            0,
            Math.PI * 2
        );


        ctx.fillStyle =
            "#ffd43b";


        ctx.fill();


        ctx.shadowBlur =
            0;


        /*
            Glanz
        */

        ctx.fillStyle =
            "#fff1a3";


        ctx.fillRect(
            x - 4,
            c.y - 7 + bob,
            4,
            11
        );


        /*
            kleiner Rand
        */

        ctx.strokeStyle =
            "#e8a900";


        ctx.lineWidth =
            2;


        ctx.stroke();

    }

}


/* =========================================================
   ENEMIES
========================================================= */

function drawEnemies() {

    for (
        const e of enemies
    ) {

        if (
            !e.active
        ) {

            continue;

        }


        const x =
            e.x -
            cameraX;


        if (
            x < -100 ||
            x > W + 100
        ) {

            continue;

        }


        /*
            Schatten
        */

        ctx.fillStyle =
            "rgba(0,0,0,.25)";


        ctx.fillRect(
            x + 3,
            e.y + e.h,
            34,
            6
        );


        /*
            Körper
        */

        ctx.fillStyle =
            "#7c3aed";


        ctx.fillRect(
            x,
            e.y,
            e.w,
            e.h
        );


        /*
            Kopf
        */

        ctx.fillStyle =
            "#a855f7";


        ctx.fillRect(
            x + 5,
            e.y + 5,
            30,
            15
        );


        /*
            Augen
        */

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


        /*
            Pupillen
        */

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
   COLLISION
========================================================= */

function collision(
    a,
    b
) {

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
   PLAYER VS PLATFORM
========================================================= */

function handlePlatforms() {

    player.grounded =
        false;


    for (
        const p of platforms
    ) {

        /*
            Plattformen, die weit hinter
            dem Spieler liegen, ignorieren.
        */

        if (
            p.x + p.w <
            player.x - 100
        ) {

            continue;

        }


        if (
            p.x >
            player.x +
            player.w +
            100
        ) {

            continue;

        }


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
            p.y + 35 &&

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

}


/* =========================================================
   UPDATE COINS
========================================================= */

function updateCoins() {

    for (
        const c of coins
    ) {

        if (
            c.collected
        ) {

            continue;

        }


        const coinBox = {

            x:
                c.x - 14,

            y:
                c.y - 14,

            w:
                28,

            h:
                28

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


            /*
                Kleine Belohnung:
                Münzen lassen den Spieler
                minimal nach oben springen.
            */

            if (
                player.grounded
            ) {

                player.vy =
                    -2;

            }

        }

    }

}


/* =========================================================
   UPDATE ENEMIES
========================================================= */

function updateEnemies() {

    for (
        const e of enemies
    ) {

        if (
            !e.active
        ) {

            continue;

        }


        e.x +=
            e.vx;


        if (
            e.x < e.min ||
            e.x > e.max
        ) {

            e.vx *= -1;

        }


        /*
            Gegner bleibt ungefähr
            auf seiner Plattform.
        */

        const enemyBox = {

            x: e.x,

            y: e.y,

            w: e.w,

            h: e.h

        };


        if (
            collision(
                player,
                enemyBox
            ) &&
            player.invincible <= 0
        ) {


            /*
                Gegner von oben besiegen.
            */

            if (

                player.vy > 0 &&

                player.y +
                player.h -
                e.y <
                25

            ) {

                player.vy =
                    -10;


                e.active =
                    false;


                score += 2;

            }


            /*
                Spieler getroffen.
            */

            else {

                lives--;


                player.invincible =
                    100;


                player.vx =
                    -7;


                player.vy =
                    -8;


                if (
                    lives <= 0
                ) {

                    endGame();

                }

            }

        }

    }

}


/* =========================================================
   UPDATE PLAYER
========================================================= */

function updatePlayer() {


    /*
        LINKS
    */

    const movingLeft =
        keys["a"] ||
        keys["arrowleft"];


    /*
        RECHTS
    */

    const movingRight =
        keys["d"] ||
        keys["arrowright"];


    /*
        Bewegung links
    */

    if (
        movingLeft
    ) {

        player.vx =
            -player.speed;

    }


    /*
        Bewegung rechts
    */

    else if (
        movingRight
    ) {

        player.vx =
            player.speed;

    }


    /*
        Keine Taste.
    */

    else {

        player.vx *=
            0.80;

    }


    /*
        Leichtes Limit.
    */

    if (
        player.vx >
        player.speed
    ) {

        player.vx =
            player.speed;

    }


    if (
        player.vx <
        -player.speed
    ) {

        player.vx =
            -player.speed;

    }


    /*
        SPRINGEN

        W
        Pfeil hoch
        Leertaste
    */

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


    /*
        Schwerkraft
    */

    player.vy +=
        0.65;


    /*
        Position
    */

    player.x +=
        player.vx;


    player.y +=
        player.vy;


    /*
        Welt beginnt bei 0.
    */

    if (
        player.x < 0
    ) {

        player.x =
            0;

    }


    /*
        Plattformen.
    */

    handlePlatforms();


    /*
        Münzen.
    */

    updateCoins();


    /*
        Gegner.
    */

    updateEnemies();


    /*
        Unverwundbarkeit.
    */

    if (
        player.invincible > 0
    ) {

        player.invincible--;

    }


    /*
        Spieler fällt.
    */

    if (
        player.y >
        H + 200
    ) {

        lives--;


        if (
            lives <= 0
        ) {

            endGame();

        }

        else {

            /*
                Respawn auf einer
                sicheren Position.
            */

            player.x =
                Math.max(
                    50,
                    player.x - 300
                );


            player.y =
                250;


            player.vx =
                0;


            player.vy =
                0;


            player.invincible =
                100;

        }

    }

}


/* =========================================================
   CAMERA
========================================================= */

function updateCamera() {

    const targetCamera =
        player.x -
        W * 0.35;


    cameraX +=
        (
            targetCamera -
            cameraX
        ) * 0.08;


    /*
        Kamera darf nicht negativ sein.
    */

    cameraX =
        Math.max(
            0,
            cameraX
        );


    distanceTravelled =
        Math.max(
            distanceTravelled,
            player.x
        );

}


/* =========================================================
   UPDATE UI
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


    document
        .getElementById(
            "stats"
        )
        .innerHTML =

        hearts +
        "&nbsp;&nbsp; 🪙 " +
        score;


    const meters =
        Math.floor(
            distanceTravelled / 10
        );


    document
        .getElementById(
            "distance"
        )
        .innerText =

        "📏 " +
        meters +
        " m";

}


/* =========================================================
   GAME OVER
========================================================= */

function endGame() {

    gameOver =
        true;


    const message =
        document.getElementById(
            "message"
        );


    message.style.display =
        "flex";


    document
        .getElementById(
            "messageTitle"
        )
        .innerText =

        "💀 GAME OVER";


    document
        .getElementById(
            "messageText"
        )
        .innerText =

        "Du bist " +
        Math.floor(
            distanceTravelled / 10
        ) +
        " Meter weit gekommen und hast " +
        score +
        " Münzen gesammelt.";

}


/* =========================================================
   RESTART
========================================================= */

function restart() {

    /*
        Spieler
    */

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


    player.invincible =
        0;


    /*
        Werte
    */

    score =
        0;


    lives =
        3;


    cameraX =
        0;


    distanceTravelled =
        0;


    gameOver =
        false;


    /*
        Welt löschen
    */

    platforms.length =
        0;


    coins.length =
        0;


    enemies.length =
        0;


    /*
        Welt neu aufbauen
    */

    addPlatform(
        0,
        500,
        1000,
        100,
        false
    );


    addCoin(
        260,
        455
    );


    addCoin(
        380,
        455
    );


    addCoin(
        520,
        455
    );


    addCoin(
        670,
        455
    );


    addCoin(
        820,
        455
    );


    addEnemy(
        600,
        460,
        450,
        900
    );


    worldGeneratedUntil =
        1000;


    /*
        Neue Welt generieren.
    */

    generateWorld();


    /*
        Keys leeren.
    */

    keys = {};


    /*
        Game-Over Fenster schließen.
    */

    document
        .getElementById(
            "message"
        )
        .style.display =
        "none";


    /*
        Canvas fokussieren.
    */

    canvas.focus();


    updateUI();

}


/* =========================================================
   CLEAN OLD OBJECTS
========================================================= */

function cleanupWorld() {

    /*
        Objekte weit hinter der Kamera
        können entfernt werden.

        Dadurch bleibt das Spiel auch nach
        langer Spielzeit performant.
    */

    const cleanupBefore =
        cameraX - 1500;


    /*
        Plattformen
    */

    for (
        let i =
            platforms.length - 1;

        i >= 0;

        i--
    ) {

        if (
            platforms[i].x +
            platforms[i].w <
            cleanupBefore
        ) {

            /*
                Startplattform nicht löschen.
            */

            if (
                platforms[i].x >
                0
            ) {

                platforms.splice(
                    i,
                    1
                );

            }

        }

    }


    /*
        Coins
    */

    for (
        let i =
            coins.length - 1;

        i >= 0;

        i--
    ) {

        if (
            coins[i].x <
            cleanupBefore
        ) {

            coins.splice(
                i,
                1
            );

        }

    }


    /*
        Gegner
    */

    for (
        let i =
            enemies.length - 1;

        i >= 0;

        i--
    ) {

        if (
            enemies[i].x <
            cleanupBefore
        ) {

            enemies.splice(
                i,
                1
            );

        }

    }

}


/* =========================================================
   MAIN UPDATE
========================================================= */

function update(dt) {

    if (
        gameOver
    ) {

        return;

    }


    /*
        Neue Welt erzeugen.
    */

    generateWorld();


    /*
        Spieler.
    */

    updatePlayer();


    /*
        Kamera.
    */

    updateCamera();


    /*
        Alte Objekte löschen.
    */

    cleanupWorld();


    /*
        UI.
    */

    updateUI();

}


/* =========================================================
   DRAW
========================================================= */

function draw(time) {

    ctx.clearRect(
        0,
        0,
        W,
        H
    );


    /*
        Hintergrund.
    */

    drawBackground();


    /*
        Plattformen.
    */

    drawPlatforms();


    /*
        Coins.
    */

    drawCoins(
        time
    );


    /*
        Gegner.
    */

    drawEnemies();


    /*
        Spieler.
    */

    if (

        player.invincible <= 0 ||

        Math.floor(
            player.invincible / 5
        ) % 2 === 0

    ) {

        drawPlayer();

    }

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


    draw(time);


    requestAnimationFrame(
        loop
    );

}


/* =========================================================
   START
========================================================= */

generateWorld();

updateUI();

requestAnimationFrame(
    loop
);


setTimeout(
    function() {

        canvas.focus();

    },
    500
);


</script>

</body>
</html>
"""


components.html(
    game,
    height=800,
    scrolling=False
)
