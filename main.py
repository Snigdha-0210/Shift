import pygame
import random
import math
import os
import array
import asyncio

# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()

try:
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except:
    SOUND_AVAILABLE = False

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHIFT")

clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BLACK = (8, 10, 18)
WHITE = (245, 245, 250)
GRAY = (120, 125, 140)
DARK_GRAY = (45, 48, 65)

ROAD = (24, 27, 38)
ROAD_LINE = (75, 80, 100)

BLUE = (60, 180, 255)
LIGHT_BLUE = (120, 220, 255)

RED = (255, 75, 75)
ORANGE = (255, 160, 60)

GREEN = (80, 230, 140)
YELLOW = (255, 220, 80)

PURPLE = (180, 100, 255)

# ============================================================
# FONTS
# ============================================================

FONT_SMALL = pygame.font.SysFont("arial", 22)
FONT_MEDIUM = pygame.font.SysFont("arial", 32, bold=True)
FONT_LARGE = pygame.font.SysFont("arial", 58, bold=True)
FONT_HUGE = pygame.font.SysFont("arial", 90, bold=True)

# ============================================================
# GAME STATES
# ============================================================

MENU = "menu"
COUNTDOWN = "countdown"
PLAYING = "playing"
GAME_OVER = "game_over"
SETTINGS = "settings"
CONTROLS = "controls"

game_state = MENU

# ============================================================
# SETTINGS
# ============================================================

sound_enabled = True

settings_selection = 0

settings_options = [
    "SOUND",
    "CONTROLS",
    "BACK"
]

# ============================================================
# INPUT SYSTEM
# ============================================================

SHIFT_LEFT = -1
SHIFT_RIGHT = 1

input_commands = []


def submit_input(direction):

    if direction in (
        SHIFT_LEFT,
        SHIFT_RIGHT
    ):
        input_commands.append(direction)


def process_input_commands():

    while input_commands:

        direction = input_commands.pop(0)

        if game_state != PLAYING:
            continue

        if direction == SHIFT_LEFT:
            move_player(-1)

        elif direction == SHIFT_RIGHT:
            move_player(1)


# ============================================================
# FUTURE HARDWARE INPUT
# ============================================================

def read_hardware_input():

    # Future Arduino / ESP32 / Bluetooth input
    # will be processed here.

    pass


# ============================================================
# SOUND SYSTEM
# ============================================================

def create_tone(
    frequency,
    duration,
    volume=0.25
):

    if not SOUND_AVAILABLE:
        return None

    sample_rate = 44100

    samples = int(
        sample_rate * duration
    )

    buffer = array.array("h")

    for i in range(samples):

        time = i / sample_rate

        wave = math.sin(
            2 * math.pi *
            frequency *
            time
        )

        fade = 1.0

        if time > duration * 0.8:

            fade = (
                1.0 -
                (
                    time -
                    duration * 0.8
                )
                /
                (duration * 0.2)
            )

        value = int(
            32767 *
            volume *
            wave *
            fade
        )

        buffer.append(value)

    return pygame.mixer.Sound(
        buffer=buffer
    )


shift_sound = None
score_sound = None
collision_sound = None
level_sound = None
click_sound = None


def initialize_sounds():

    global shift_sound
    global score_sound
    global collision_sound
    global level_sound
    global click_sound

    if not SOUND_AVAILABLE:
        return

    shift_sound = create_tone(
        500,
        0.08,
        0.18
    )

    score_sound = create_tone(
        800,
        0.10,
        0.20
    )

    collision_sound = create_tone(
        90,
        0.40,
        0.30
    )

    level_sound = create_tone(
        1100,
        0.25,
        0.25
    )

    click_sound = create_tone(
        650,
        0.06,
        0.15
    )


initialize_sounds()


def play_sound(sound):

    if not sound_enabled:
        return

    if sound is None:
        return

    try:
        sound.play()
    except:
        pass


# ============================================================
# PLAYER
# ============================================================

LANE_X = [
    300,
    500,
    700
]

player_lane = 1

player_x = LANE_X[player_lane]

player_target_x = player_x

PLAYER_Y = 570

PLAYER_WIDTH = 70
PLAYER_HEIGHT = 100

player_rect = pygame.Rect(
    0,
    0,
    PLAYER_WIDTH,
    PLAYER_HEIGHT
)


# ============================================================
# OBSTACLES
# ============================================================

obstacles = []

OBSTACLE_WIDTH = 85
OBSTACLE_HEIGHT = 100

spawn_timer = 0

# ============================================================
# PATTERN SYSTEM
# ============================================================
#
# Every pattern is a list of lanes.
#
# Example:
#
# [0]
#
# means:
#
#       █
#       LEFT
#
#
# [0, 2]
#
# means:
#
#       █       █
#       LEFT    RIGHT
#
# The player can use the remaining lane.
# ============================================================

last_pattern = None


def get_allowed_patterns():

    # --------------------------------------------------------
    # LEVEL 1
    # --------------------------------------------------------
    #
    # Very easy patterns.
    # --------------------------------------------------------

    if current_level == 1:

        return [

            [0],
            [1],
            [2],

        ]

    # --------------------------------------------------------
    # LEVEL 2
    # --------------------------------------------------------

    elif current_level == 2:

        return [

            [0],
            [1],
            [2],

            [0],
            [2],

        ]

    # --------------------------------------------------------
    # LEVEL 3
    # --------------------------------------------------------

    elif current_level == 3:

        return [

            [0],
            [1],
            [2],

            [0, 1],
            [1, 2],

        ]

    # --------------------------------------------------------
    # LEVEL 4
    # --------------------------------------------------------

    elif current_level == 4:

        return [

            [0],
            [1],
            [2],

            [0, 1],
            [1, 2],

            [0, 2],

        ]

    # --------------------------------------------------------
    # LEVEL 5
    # --------------------------------------------------------

    elif current_level == 5:

        return [

            [0],
            [1],
            [2],

            [0, 1],
            [1, 2],
            [0, 2],

            [0, 1],
            [1, 2],

        ]

    # --------------------------------------------------------
    # LEVEL 6+
    # --------------------------------------------------------

    else:

        return [

            [0],
            [1],
            [2],

            [0, 1],
            [1, 2],
            [0, 2],

            [0],
            [2],

            [0, 1],
            [1, 2],

        ]


def choose_pattern():

    global last_pattern

    patterns = get_allowed_patterns()

    # --------------------------------------------------------
    # Prevent the exact same pattern repeatedly.
    # --------------------------------------------------------

    available = [

        pattern

        for pattern in patterns

        if pattern != last_pattern

    ]

    if not available:

        available = patterns

    pattern = random.choice(
        available
    )

    last_pattern = pattern

    return pattern


# ============================================================
# FAIRNESS CHECK
# ============================================================

def pattern_is_fair(pattern):

    # There are three lanes.
    #
    # At least one lane must remain open.

    if len(pattern) >= 3:

        return False

    return True


def spawn_pattern():

    pattern = choose_pattern()

    # Safety check

    if not pattern_is_fair(pattern):

        return

    for lane in pattern:

        spawn_obstacle(lane)


# ============================================================
# SCORE / HISTORY
# ============================================================

score = 0

high_score = 0

current_level = 1

level_message_timer = 0

HIGH_SCORE_FILE = "highscore.txt"


def load_high_score():

    if not os.path.exists(
        HIGH_SCORE_FILE
    ):

        return 0

    try:

        with open(
            HIGH_SCORE_FILE,
            "r"
        ) as file:

            return int(
                file.read().strip()
            )

    except:

        return 0


def save_high_score(value):

    try:

        with open(
            HIGH_SCORE_FILE,
            "w"
        ) as file:

            file.write(
                str(value)
            )

    except:

        pass


high_score = load_high_score()


# ============================================================
# DIFFICULTY
# ============================================================

obstacle_speed = 300

spawn_interval = 1.25


def update_difficulty():

    global obstacle_speed
    global spawn_interval
    global current_level

    new_level = min(
        10,
        1 + score // 5
    )

    current_level = new_level

    obstacle_speed = min(
        750,
        300 +
        (current_level - 1) * 50
    )

    spawn_interval = max(
        0.45,
        1.25 -
        (current_level - 1) * 0.08
    )


# ============================================================
# PARTICLES
# ============================================================

particles = []


def create_particles(
    x,
    y,
    amount=25
):

    for _ in range(amount):

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            80,
            300
        )

        particles.append({

            "x": x,
            "y": y,

            "vx":
                math.cos(angle) *
                speed,

            "vy":
                math.sin(angle) *
                speed,

            "life":
                random.uniform(
                    0.4,
                    0.9
                ),

            "size":
                random.randint(
                    3,
                    8
                )
        })


def update_particles(dt):

    for particle in particles[:]:

        particle["x"] += (
            particle["vx"] * dt
        )

        particle["y"] += (
            particle["vy"] * dt
        )

        particle["vy"] += (
            500 * dt
        )

        particle["life"] -= dt

        if particle["life"] <= 0:

            particles.remove(
                particle
            )


def draw_particles():

    for particle in particles:

        pygame.draw.circle(

            screen,

            ORANGE,

            (
                int(
                    particle["x"]
                ),

                int(
                    particle["y"]
                )
            ),

            particle["size"]
        )


# ============================================================
# SCREEN SHAKE
# ============================================================

shake_timer = 0
shake_strength = 0


def trigger_shake(
    duration,
    strength
):

    global shake_timer
    global shake_strength

    shake_timer = duration
    shake_strength = strength


def update_shake(dt):

    global shake_timer

    if shake_timer > 0:

        shake_timer -= dt


def get_screen_offset():

    if shake_timer <= 0:

        return 0, 0

    return (

        random.randint(
            -shake_strength,
            shake_strength
        ),

        random.randint(
            -shake_strength,
            shake_strength
        )
    )


# ============================================================
# FLASH
# ============================================================

flash_timer = 0


def trigger_flash():

    global flash_timer

    flash_timer = 0.25


def update_flash(dt):

    global flash_timer

    flash_timer = max(
        0,
        flash_timer - dt
    )


def draw_flash():

    if flash_timer <= 0:
        return

    alpha = int(
        150 *
        (
            flash_timer /
            0.25
        )
    )

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (255, 60, 60, alpha)
    )

    screen.blit(
        overlay,
        (0, 0)
    )


# ============================================================
# SCORE POPUPS
# ============================================================

score_popups = []


def create_score_popup(
    x,
    y
):

    score_popups.append({

        "x": x,

        "y": y,

        "life": 0.8
    })


def update_score_popups(dt):

    for popup in score_popups[:]:

        popup["y"] -= (
            40 * dt
        )

        popup["life"] -= dt

        if popup["life"] <= 0:

            score_popups.remove(
                popup
            )


def draw_score_popups():

    for popup in score_popups:

        text = FONT_SMALL.render(

            "+1",

            True,

            GREEN
        )

        screen.blit(

            text,

            (
                int(
                    popup["x"]
                ),

                int(
                    popup["y"]
                )
            )
        )


# ============================================================
# LEVEL UP
# ============================================================

def trigger_level_up():

    global level_message_timer

    level_message_timer = 1.5

    create_particles(

        WIDTH // 2,

        180,

        45
    )

    play_sound(
        level_sound
    )


def update_level_message(dt):

    global level_message_timer

    level_message_timer = max(
        0,
        level_message_timer - dt
    )


def draw_level_message():

    if level_message_timer <= 0:
        return

    text = FONT_LARGE.render(

        f"LEVEL {current_level}!",

        True,

        YELLOW
    )

    screen.blit(

        text,

        text.get_rect(

            center=(
                WIDTH // 2,
                180
            )
        )
    )


# ============================================================
# PLAYER MOVEMENT
# ============================================================

def move_player(direction):

    global player_lane
    global player_target_x

    new_lane = (
        player_lane +
        direction
    )

    new_lane = max(
        0,
        min(
            2,
            new_lane
        )
    )

    if new_lane != player_lane:

        player_lane = new_lane

        player_target_x = LANE_X[
            player_lane
        ]

        play_sound(
            shift_sound
        )


def update_player(dt):

    global player_x

    distance = (
        player_target_x -
        player_x
    )

    movement_speed = 1200

    if abs(distance) < 2:

        player_x = player_target_x

    else:

        player_x += math.copysign(

            min(
                abs(distance),
                movement_speed * dt
            ),

            distance
        )


# ============================================================
# OBSTACLE SPAWNING
# ============================================================

def spawn_obstacle(lane):

    obstacles.append({

        "lane": lane,

        "x": LANE_X[lane],

        "y": -150,

        "passed": False
    })


# ============================================================
# OBSTACLE UPDATE
# ============================================================

def update_obstacles(dt):

    global spawn_timer
    global score
    global high_score
    global current_level

    spawn_timer += dt

    if spawn_timer >= spawn_interval:

        spawn_timer = 0

        spawn_pattern()

    for obstacle in obstacles[:]:

        obstacle["y"] += (
            obstacle_speed * dt
        )

        # ----------------------------------------------------
        # SUCCESSFULLY PASSED
        # ----------------------------------------------------

        if (

            not obstacle["passed"]

            and obstacle["y"] >
            PLAYER_Y + 100

        ):

            obstacle["passed"] = True

            score += 1

            create_score_popup(

                obstacle["x"],

                PLAYER_Y - 80
            )

            play_sound(
                score_sound
            )

            previous_level = (
                current_level
            )

            update_difficulty()

            if current_level > previous_level:

                trigger_level_up()

            if score > high_score:

                high_score = score

                save_high_score(
                    high_score
                )

        # ----------------------------------------------------
        # REMOVE
        # ----------------------------------------------------

        if obstacle["y"] > HEIGHT + 150:

            obstacles.remove(
                obstacle
            )


# ============================================================
# COLLISION
# ============================================================

def check_collision():

    player_rect.center = (

        int(player_x),

        PLAYER_Y
    )

    for obstacle in obstacles:

        obstacle_rect = pygame.Rect(

            int(
                obstacle["x"] -
                OBSTACLE_WIDTH / 2
            ),

            int(
                obstacle["y"]
            ),

            OBSTACLE_WIDTH,

            OBSTACLE_HEIGHT
        )

        if player_rect.colliderect(
            obstacle_rect
        ):

            return True

    return False


# ============================================================
# BACKGROUND
# ============================================================

stars = []

for _ in range(80):

    stars.append({

        "x": random.randint(
            0,
            WIDTH
        ),

        "y": random.randint(
            0,
            HEIGHT
        ),

        "speed": random.uniform(
            20,
            80
        ),

        "size": random.randint(
            1,
            3
        )
    })


def update_background(dt):

    for star in stars:

        star["y"] += (
            star["speed"] * dt
        )

        if star["y"] > HEIGHT:

            star["y"] = 0

            star["x"] = random.randint(
                0,
                WIDTH
            )


def draw_background():

    screen.fill(
        BLACK
    )

    for star in stars:

        pygame.draw.circle(

            screen,

            (90, 95, 115),

            (
                int(
                    star["x"]
                ),

                int(
                    star["y"]
                )
            ),

            star["size"]
        )


# ============================================================
# SPEED LINES
# ============================================================

speed_lines = []

for _ in range(20):

    speed_lines.append({

        "x": random.randint(
            180,
            820
        ),

        "y": random.randint(
            0,
            HEIGHT
        ),

        "length": random.randint(
            30,
            100
        ),

        "speed": random.randint(
            300,
            600
        )
    })


def update_speed_lines(dt):

    for line in speed_lines:

        line["y"] += (
            line["speed"] * dt
        )

        if line["y"] > HEIGHT:

            line["y"] = (
                -line["length"]
            )

            line["x"] = random.randint(
                180,
                820
            )


def draw_speed_lines():

    for line in speed_lines:

        pygame.draw.line(

            screen,

            (40, 44, 60),

            (
                line["x"],
                line["y"]
            ),

            (
                line["x"],
                line["y"] +
                line["length"]
            ),

            2
        )


# ============================================================
# ROAD
# ============================================================

def draw_road():

    road_left = 180
    road_right = 820

    pygame.draw.rect(

        screen,

        ROAD,

        (
            road_left,
            0,
            road_right - road_left,
            HEIGHT
        )
    )

    pygame.draw.line(

        screen,

        ROAD_LINE,

        (393, 0),

        (393, HEIGHT),

        3
    )

    pygame.draw.line(

        screen,

        ROAD_LINE,

        (607, 0),

        (607, HEIGHT),

        3
    )

    pygame.draw.line(

        screen,

        ROAD_LINE,

        (road_left, 0),

        (road_left, HEIGHT),

        5
    )

    pygame.draw.line(

        screen,

        ROAD_LINE,

        (road_right, 0),

        (road_right, HEIGHT),

        5
    )


# ============================================================
# PLAYER DRAWING
# ============================================================

def draw_player():

    x = int(player_x)

    y = PLAYER_Y

    pygame.draw.ellipse(

        screen,

        (5, 5, 10),

        (
            x - 45,
            y + 35,
            90,
            25
        )
    )

    pygame.draw.polygon(

        screen,

        BLUE,

        [

            (x, y - 55),

            (x - 32, y + 45),

            (x, y + 30),

            (x + 32, y + 45)
        ]
    )

    pygame.draw.polygon(

        screen,

        LIGHT_BLUE,

        [

            (x, y - 45),

            (x - 8, y + 25),

            (x + 8, y + 25)
        ]
    )

    pygame.draw.circle(

        screen,

        ORANGE,

        (
            x,
            y + 40
        ),

        9
    )


# ============================================================
# OBSTACLE DRAWING
# ============================================================

def draw_obstacles():

    for obstacle in obstacles:

        x = int(
            obstacle["x"]
        )

        y = int(
            obstacle["y"]
        )

        rect = pygame.Rect(

            x -
            OBSTACLE_WIDTH // 2,

            y,

            OBSTACLE_WIDTH,

            OBSTACLE_HEIGHT
        )

        pygame.draw.rect(

            screen,

            RED,

            rect,

            border_radius=10
        )

        pygame.draw.rect(

            screen,

            ORANGE,

            rect.inflate(
                -12,
                -12
            ),

            4,

            border_radius=6
        )


# ============================================================
# HUD
# ============================================================

def draw_hud():

    score_text = FONT_MEDIUM.render(

        f"SCORE  {score}",

        True,

        WHITE
    )

    screen.blit(

        score_text,

        (
            30,
            25
        )
    )

    high_text = FONT_SMALL.render(

        f"BEST  {high_score}",

        True,

        GRAY
    )

    screen.blit(

        high_text,

        (
            30,
            65
        )
    )

    level_text = FONT_SMALL.render(

        f"LEVEL  {current_level}",

        True,

        YELLOW
    )

    screen.blit(

        level_text,

        (
            WIDTH - 160,
            30
        )
    )

    progress = score % 5

    bar_width = 130

    pygame.draw.rect(

        screen,

        (45, 48, 65),

        (
            WIDTH - 160,
            65,
            bar_width,
            10
        ),

        border_radius=5
    )

    pygame.draw.rect(

        screen,

        YELLOW,

        (
            WIDTH - 160,
            65,

            int(
                bar_width *
                progress /
                5
            ),

            10
        ),

        border_radius=5
    )


# ============================================================
# MENU
# ============================================================

def draw_menu():

    draw_background()

    title = FONT_HUGE.render(

        "SHIFT",

        True,

        WHITE
    )

    screen.blit(

        title,

        title.get_rect(

            center=(
                WIDTH // 2,
                150
            )
        )
    )

    subtitle = FONT_MEDIUM.render(

        "DODGE. SHIFT. SURVIVE.",

        True,

        LIGHT_BLUE
    )

    screen.blit(

        subtitle,

        subtitle.get_rect(

            center=(
                WIDTH // 2,
                230
            )
        )
    )

    best = FONT_SMALL.render(

        f"HIGH SCORE: {high_score}",

        True,

        YELLOW
    )

    screen.blit(

        best,

        best.get_rect(

            center=(
                WIDTH // 2,
                285
            )
        )
    )

    start = FONT_MEDIUM.render(

        "SPACE  →  START GAME",

        True,

        GREEN
    )

    screen.blit(

        start,

        start.get_rect(

            center=(
                WIDTH // 2,
                380
            )
        )
    )

    settings = FONT_MEDIUM.render(

        "S  →  SETTINGS",

        True,

        WHITE
    )

    screen.blit(

        settings,

        settings.get_rect(

            center=(
                WIDTH // 2,
                435
            )
        )
    )

    quit_text = FONT_SMALL.render(

        "ESC  →  QUIT",

        True,

        GRAY
    )

    screen.blit(

        quit_text,

        quit_text.get_rect(

            center=(
                WIDTH // 2,
                500
            )
        )
    )


# ============================================================
# SETTINGS
# ============================================================

def draw_settings():

    draw_background()

    title = FONT_LARGE.render(

        "SETTINGS",

        True,

        WHITE
    )

    screen.blit(

        title,

        title.get_rect(

            center=(
                WIDTH // 2,
                100
            )
        )
    )

    sound_value = (

        "ON"

        if sound_enabled

        else "OFF"
    )

    options = [

        f"SOUND        : {sound_value}",

        "CONTROLS",

        "BACK"
    ]

    y = 250

    for index, option in enumerate(
        options
    ):

        if index == settings_selection:

            color = YELLOW

            pygame.draw.rect(

                screen,

                (35, 40, 58),

                (
                    250,
                    y - 10,
                    500,
                    55
                ),

                border_radius=10
            )

        else:

            color = WHITE

        text = FONT_MEDIUM.render(

            option,

            True,

            color
        )

        screen.blit(

            text,

            text.get_rect(

                center=(
                    WIDTH // 2,
                    y + 15
                )
            )
        )

        y += 80

    help_text = FONT_SMALL.render(

        "UP / DOWN = SELECT     ENTER = CHANGE     ESC = BACK",

        True,

        GRAY
    )

    screen.blit(

        help_text,

        help_text.get_rect(

            center=(
                WIDTH // 2,
                600
            )
        )
    )


# ============================================================
# CONTROLS
# ============================================================

def draw_controls_panel():

    overlay = pygame.Surface(

        (WIDTH, HEIGHT),

        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 210)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title = FONT_LARGE.render(

        "CONTROLS",

        True,

        WHITE
    )

    screen.blit(

        title,

        title.get_rect(

            center=(
                WIDTH // 2,
                130
            )
        )
    )

    controls = [

        "LEFT ARROW / A",

        "SHIFT LEFT",

        "",

        "RIGHT ARROW / D",

        "SHIFT RIGHT",

        "",

        "SPACE",

        "START / RESTART",

        "",

        "ESC",

        "BACK / QUIT"
    ]

    y = 220

    for line in controls:

        if "SHIFT" in line:

            color = LIGHT_BLUE

        elif (

            "ARROW" in line

            or line == "SPACE"

            or line == "ESC"

        ):

            color = YELLOW

        else:

            color = WHITE

        text = FONT_MEDIUM.render(

            line,

            True,

            color
        )

        screen.blit(

            text,

            text.get_rect(

                center=(
                    WIDTH // 2,
                    y
                )
            )
        )

        y += 40

    back = FONT_SMALL.render(

        "PRESS ESC TO RETURN",

        True,

        GRAY
    )

    screen.blit(

        back,

        back.get_rect(

            center=(
                WIDTH // 2,
                620
            )
        )
    )


# ============================================================
# COUNTDOWN
# ============================================================

countdown_timer = 0


def draw_countdown():

    draw_background()

    draw_road()

    draw_player()

    number = max(

        1,

        3 -
        int(countdown_timer)
    )

    text = FONT_HUGE.render(

        str(number),

        True,

        WHITE
    )

    screen.blit(

        text,

        text.get_rect(

            center=(
                WIDTH // 2,
                HEIGHT // 2
            )
        )
    )


# ============================================================
# GAME OVER
# ============================================================

def draw_game_over():

    draw_background()

    draw_road()

    draw_speed_lines()

    draw_obstacles()

    draw_particles()

    overlay = pygame.Surface(

        (WIDTH, HEIGHT),

        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 150)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title = FONT_LARGE.render(

        "GAME OVER",

        True,

        RED
    )

    screen.blit(

        title,

        title.get_rect(

            center=(
                WIDTH // 2,
                170
            )
        )
    )

    score_text = FONT_MEDIUM.render(

        f"SCORE: {score}",

        True,

        WHITE
    )

    screen.blit(

        score_text,

        score_text.get_rect(

            center=(
                WIDTH // 2,
                260
            )
        )
    )

    best_text = FONT_SMALL.render(

        f"BEST: {high_score}",

        True,

        YELLOW
    )

    screen.blit(

        best_text,

        best_text.get_rect(

            center=(
                WIDTH // 2,
                305
            )
        )
    )

    restart = FONT_MEDIUM.render(

        "SPACE  →  RESTART",

        True,

        GREEN
    )

    screen.blit(

        restart,

        restart.get_rect(

            center=(
                WIDTH // 2,
                420
            )
        )
    )

    menu = FONT_SMALL.render(

        "ESC  →  MENU",

        True,

        GRAY
    )

    screen.blit(

        menu,

        menu.get_rect(

            center=(
                WIDTH // 2,
                475
            )
        )
    )


# ============================================================
# RESET GAME
# ============================================================

def reset_game():

    global player_lane
    global player_x
    global player_target_x

    global score
    global spawn_timer

    global current_level
    global last_pattern

    player_lane = 1

    player_x = LANE_X[1]

    player_target_x = LANE_X[1]

    obstacles.clear()

    particles.clear()

    score_popups.clear()

    input_commands.clear()

    score = 0

    spawn_timer = 0

    current_level = 1

    last_pattern = None

    update_difficulty()


# ============================================================
# START GAME
# ============================================================

def start_game():

    global game_state
    global countdown_timer

    reset_game()

    countdown_timer = 0

    game_state = COUNTDOWN


# ============================================================
# SETTINGS INPUT
# ============================================================

def settings_move_selection(
    direction
):

    global settings_selection

    settings_selection += direction

    settings_selection %= len(
        settings_options
    )


def activate_settings_option():

    global game_state
    global sound_enabled

    option = settings_options[
        settings_selection
    ]

    if option == "SOUND":

        sound_enabled = (
            not sound_enabled
        )

        if sound_enabled:

            play_sound(
                click_sound
            )

    elif option == "CONTROLS":

        game_state = CONTROLS

    elif option == "BACK":

        game_state = MENU


# ============================================================
# MAIN LOOP
# ============================================================

async def main():
    global game_state
    global settings_selection
    global countdown_timer
    global screen

    running = True

    while running:

        dt = clock.tick(60) / 1000.0

        # ====================================================
        # EVENTS
        # ====================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            if event.type == pygame.KEYDOWN:

                # --------------------------------------------
                # PLAYING
                # --------------------------------------------

                if game_state == PLAYING:

                    if event.key in (
                        pygame.K_LEFT,
                        pygame.K_a
                    ):

                        submit_input(
                            SHIFT_LEFT
                        )

                    elif event.key in (
                        pygame.K_RIGHT,
                        pygame.K_d
                    ):

                        submit_input(
                            SHIFT_RIGHT
                        )

                # --------------------------------------------
                # MENU
                # --------------------------------------------

                elif game_state == MENU:

                    if event.key == pygame.K_SPACE:

                        start_game()

                    elif event.key == pygame.K_s:

                        settings_selection = 0

                        game_state = SETTINGS

                    elif event.key == pygame.K_ESCAPE:

                        running = False

                # --------------------------------------------
                # GAME OVER
                # --------------------------------------------

                elif game_state == GAME_OVER:

                    if event.key == pygame.K_SPACE:

                        start_game()

                    elif event.key == pygame.K_ESCAPE:

                        game_state = MENU

                # --------------------------------------------
                # SETTINGS
                # --------------------------------------------

                elif game_state == SETTINGS:

                    if event.key in (
                        pygame.K_UP,
                        pygame.K_w
                    ):

                        settings_move_selection(
                            -1
                        )

                    elif event.key in (
                        pygame.K_DOWN,
                        pygame.K_s
                    ):

                        settings_move_selection(
                            1
                        )

                    elif event.key in (
                        pygame.K_RETURN,
                        pygame.K_KP_ENTER
                    ):

                        activate_settings_option()

                    elif event.key == pygame.K_ESCAPE:

                        game_state = MENU

                # --------------------------------------------
                # CONTROLS
                # --------------------------------------------

                elif game_state == CONTROLS:

                    if event.key == pygame.K_ESCAPE:

                        game_state = SETTINGS

        # ====================================================
        # FUTURE HARDWARE
        # ====================================================

        read_hardware_input()

        # ====================================================
        # INPUT SYSTEM
        # ====================================================

        process_input_commands()

        # ====================================================
        # GLOBAL UPDATES
        # ====================================================

        update_background(dt)

        update_speed_lines(dt)

        update_particles(dt)

        update_score_popups(dt)

        update_level_message(dt)

        update_shake(dt)

        update_flash(dt)

        # ====================================================
        # COUNTDOWN
        # ====================================================

        if game_state == COUNTDOWN:

            countdown_timer += dt

            if countdown_timer >= 3:

                game_state = PLAYING

        # ====================================================
        # PLAYING
        # ====================================================

        elif game_state == PLAYING:

            update_player(dt)

            update_obstacles(dt)

            if check_collision():

                create_particles(
                    player_x,
                    PLAYER_Y,
                    60
                )

                trigger_shake(
                    0.5,
                    15
                )

                trigger_flash()

                play_sound(
                    collision_sound
                )

                game_state = GAME_OVER

        # ====================================================
        # DRAW
        # ====================================================

        offset_x, offset_y = (
            get_screen_offset()
        )

        world_surface = pygame.Surface(
            (WIDTH, HEIGHT)
        )

        world_surface.fill(
            BLACK
        )

        old_screen = screen

        screen = world_surface

        # ----------------------------------------------------
        # DRAW STATE
        # ----------------------------------------------------

        if game_state == MENU:

            draw_menu()

        elif game_state == COUNTDOWN:

            draw_countdown()

        elif game_state == PLAYING:

            draw_background()

            draw_road()

            draw_speed_lines()

            draw_obstacles()

            draw_player()

            draw_particles()

            draw_score_popups()

            draw_hud()

            draw_level_message()

        elif game_state == GAME_OVER:

            draw_game_over()

        elif game_state == SETTINGS:

            draw_settings()

        elif game_state == CONTROLS:

            draw_settings()

            draw_controls_panel()

        # ----------------------------------------------------
        # RESTORE SCREEN
        # ----------------------------------------------------

        screen = old_screen

        screen.fill(
            BLACK
        )

        screen.blit(
            world_surface,
            (
                offset_x,
                offset_y
            )
        )

        draw_flash()

        pygame.display.flip()

        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())