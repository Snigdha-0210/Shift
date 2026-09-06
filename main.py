import pygame
import sys
import random
import math
import array

# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()

WIDTH = 900
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHIFT")

clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BACKGROUND = (10, 12, 18)

ROAD_COLOR = (42, 44, 50)
ROAD_EDGE_COLOR = (150, 153, 160)
LANE_LINE_COLOR = (100, 103, 110)

PLAYER_COLOR = (0, 220, 255)
PLAYER_GLOW = (0, 120, 150)
PLAYER_DARK = (0, 90, 115)

WINDOW_COLOR = (15, 35, 48)
WHEEL_COLOR = (18, 20, 24)

OBSTACLE_COLOR = (220, 55, 55)
OBSTACLE_DARK = (120, 25, 25)
OBSTACLE_GLOW = (120, 30, 30)

WARNING_COLOR = (255, 190, 40)

WHITE = (240, 240, 240)
GREY = (160, 160, 160)

# ============================================================
# AUDIO
# ============================================================

# We attempt to initialize the mixer.
# If the computer has an audio problem, the game
# will still run without sound.

audio_enabled = True

try:

    pygame.mixer.init(
        frequency=44100,
        size=-16,
        channels=1,
        buffer=512
    )

except pygame.error:

    audio_enabled = False


# ------------------------------------------------------------
# CREATE SIMPLE GENERATED SOUNDS
# ------------------------------------------------------------

def create_tone(
    frequency,
    duration,
    volume=0.25
):
    """
    Generates a simple electronic tone.

    We create the sound ourselves rather than requiring
    external sound files.
    """

    if not audio_enabled:
        return None

    sample_rate = 44100

    sample_count = int(
        sample_rate * duration
    )

    samples = array.array(
        "h"
    )

    amplitude = int(
        32767 * volume
    )

    for i in range(sample_count):

        time_value = i / sample_rate

        wave = math.sin(
            2
            * math.pi
            * frequency
            * time_value
        )

        # Small fade-out to prevent clicking.
        fade = 1.0 - (
            i / sample_count
        )

        value = int(
            amplitude
            * wave
            * fade
        )

        samples.append(value)

    return pygame.mixer.Sound(
        buffer=samples.tobytes()
    )


# ============================================================
# GAME SOUNDS
# ============================================================

if audio_enabled:

    move_sound = create_tone(
        520,
        0.08,
        0.20
    )

    score_sound = create_tone(
        850,
        0.12,
        0.25
    )

    countdown_sound = create_tone(
        500,
        0.15,
        0.20
    )

    start_sound = create_tone(
        950,
        0.25,
        0.30
    )

    collision_sound = create_tone(
        90,
        0.45,
        0.35
    )

else:

    move_sound = None
    score_sound = None
    countdown_sound = None
    start_sound = None
    collision_sound = None


def play_sound(sound):
    """
    Safely plays a sound.
    """

    if not audio_enabled:
        return

    if sound is None:
        return

    try:

        sound.play()

    except pygame.error:

        pass


# ============================================================
# ROAD
# ============================================================

ROAD_WIDTH = 600
ROAD_HEIGHT = 600

ROAD_X = (WIDTH - ROAD_WIDTH) // 2
ROAD_Y = 50

LANE_WIDTH = ROAD_WIDTH // 3

LEFT = 0
MIDDLE = 1
RIGHT = 2

LANES = [LEFT, MIDDLE, RIGHT]

# ============================================================
# PLAYER
# ============================================================

PLAYER_WIDTH = 80
PLAYER_HEIGHT = 100

PLAYER_Y = HEIGHT - 140

player_lane = MIDDLE

player_x = 0
target_x = 0

PLAYER_MOVE_SPEED = 900

# ============================================================
# OBSTACLES
# ============================================================

OBSTACLE_WIDTH = 80
OBSTACLE_HEIGHT = 100

obstacle_spawn_y = (
    ROAD_Y
    - OBSTACLE_HEIGHT
    - 20
)

obstacle_timer = 0

patterns = []

# ============================================================
# ROAD ANIMATION
# ============================================================

road_line_offset = 0

ROAD_LINE_HEIGHT = 70
ROAD_LINE_GAP = 70

ROAD_LINE_SPEED_MULTIPLIER = 1.0

# ============================================================
# GAME STATES
# ============================================================

MENU = 0
COUNTDOWN = 1
PLAYING = 2
GAME_OVER = 3

game_state = MENU

# ============================================================
# COUNTDOWN
# ============================================================

countdown_time = 0
countdown_number = 3

last_countdown_number = 3

# ============================================================
# GAME VARIABLES
# ============================================================

score = 0
high_score = 0

# ============================================================
# FONTS
# ============================================================

font_title = pygame.font.SysFont(
    "arial",
    90,
    bold=True
)

font_huge = pygame.font.SysFont(
    "arial",
    110,
    bold=True
)

font_large = pygame.font.SysFont(
    "arial",
    48,
    bold=True
)

font_medium = pygame.font.SysFont(
    "arial",
    32,
    bold=True
)

font_small = pygame.font.SysFont(
    "arial",
    24
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================


def get_lane_x(lane):
    """
    Returns center X coordinate of a lane.
    """

    return (
        ROAD_X
        + lane * LANE_WIDTH
        + LANE_WIDTH // 2
    )


def get_player_x(lane):
    """
    Returns player top-left X coordinate.
    """

    return (
        get_lane_x(lane)
        - PLAYER_WIDTH // 2
    )


def get_obstacle_x(lane):
    """
    Returns obstacle top-left X coordinate.
    """

    return (
        get_lane_x(lane)
        - OBSTACLE_WIDTH // 2
    )


def get_difficulty():
    """
    Returns:

    obstacle speed
    spawn interval
    difficulty level
    """

    if score < 5:

        return 300, 1.20, 1

    elif score < 10:

        return 350, 1.05, 2

    elif score < 15:

        return 400, 0.90, 3

    elif score < 20:

        return 450, 0.80, 4

    else:

        return 500, 0.70, 5


def get_reachable_lane():
    """
    Chooses current or adjacent lane.
    """

    possible_lanes = [
        player_lane
    ]

    if player_lane > LEFT:

        possible_lanes.append(
            player_lane - 1
        )

    if player_lane < RIGHT:

        possible_lanes.append(
            player_lane + 1
        )

    return random.choice(
        possible_lanes
    )


def choose_pattern_type():
    """
    Controls obstacle pattern difficulty.
    """

    if score < 5:

        return "single"

    elif score < 10:

        if random.random() < 0.75:
            return "single"

        return "double"

    elif score < 20:

        if random.random() < 0.60:
            return "single"

        return "double"

    else:

        if random.random() < 0.50:
            return "single"

        return "double"


def spawn_pattern():
    """
    Creates a fair obstacle pattern.
    """

    pattern_type = choose_pattern_type()

    safe_lane = get_reachable_lane()

    rects = []

    # --------------------------------------------------------
    # SINGLE
    # --------------------------------------------------------

    if pattern_type == "single":

        possible_blocked_lanes = [
            lane
            for lane in LANES
            if lane != safe_lane
        ]

        blocked_lane = random.choice(
            possible_blocked_lanes
        )

        obstacle = pygame.Rect(
            get_obstacle_x(
                blocked_lane
            ),
            obstacle_spawn_y,
            OBSTACLE_WIDTH,
            OBSTACLE_HEIGHT
        )

        rects.append(
            obstacle
        )

    # --------------------------------------------------------
    # DOUBLE
    # --------------------------------------------------------

    else:

        blocked_lanes = [
            lane
            for lane in LANES
            if lane != safe_lane
        ]

        for lane in blocked_lanes:

            obstacle = pygame.Rect(
                get_obstacle_x(
                    lane
                ),
                obstacle_spawn_y,
                OBSTACLE_WIDTH,
                OBSTACLE_HEIGHT
            )

            rects.append(
                obstacle
            )

    patterns.append(
        {
            "rects": rects,
            "scored": False
        }
    )


# ============================================================
# PLAYER MOVEMENT
# ============================================================


def move_player(dt):
    """
    Smoothly moves player toward target.
    """

    global player_x

    if player_x < target_x:

        player_x += (
            PLAYER_MOVE_SPEED
            * dt
        )

        if player_x > target_x:

            player_x = target_x

    elif player_x > target_x:

        player_x -= (
            PLAYER_MOVE_SPEED
            * dt
        )

        if player_x < target_x:

            player_x = target_x


def move_left():
    """
    Move one lane left.
    """

    global player_lane
    global target_x

    if player_lane > LEFT:

        player_lane -= 1

        target_x = get_player_x(
            player_lane
        )

        play_sound(
            move_sound
        )


def move_right():
    """
    Move one lane right.
    """

    global player_lane
    global target_x

    if player_lane < RIGHT:

        player_lane += 1

        target_x = get_player_x(
            player_lane
        )

        play_sound(
            move_sound
        )


# ============================================================
# OBSTACLE MOVEMENT
# ============================================================


def move_obstacles(dt):
    """
    Moves obstacles downward.
    """

    obstacle_speed, _, _ = get_difficulty()

    for pattern in patterns:

        for obstacle in pattern["rects"]:

            obstacle.y += int(
                obstacle_speed
                * dt
            )


# ============================================================
# ROAD ANIMATION
# ============================================================


def update_road_animation(dt):
    """
    Moves road markings downward.
    """

    global road_line_offset

    obstacle_speed, _, _ = get_difficulty()

    road_line_speed = (
        obstacle_speed
        * ROAD_LINE_SPEED_MULTIPLIER
    )

    road_line_offset += (
        road_line_speed
        * dt
    )

    line_spacing = (
        ROAD_LINE_HEIGHT
        + ROAD_LINE_GAP
    )

    if road_line_offset >= line_spacing:

        road_line_offset -= line_spacing


# ============================================================
# COLLISION
# ============================================================


def check_collisions():
    """
    Checks player-obstacle collision.
    """

    global game_state

    player_rect = pygame.Rect(
        int(player_x + 8),
        PLAYER_Y + 5,
        PLAYER_WIDTH - 16,
        PLAYER_HEIGHT - 10
    )

    for pattern in patterns:

        for obstacle in pattern["rects"]:

            if player_rect.colliderect(
                obstacle
            ):

                play_sound(
                    collision_sound
                )

                game_state = GAME_OVER

                return


# ============================================================
# SCORE
# ============================================================


def update_score():
    """
    Gives one point per successfully
    passed obstacle pattern.
    """

    global score
    global high_score

    player_bottom = (
        PLAYER_Y
        + PLAYER_HEIGHT
    )

    for pattern in patterns:

        if pattern["scored"]:
            continue

        first_obstacle = (
            pattern["rects"][0]
        )

        if first_obstacle.top > player_bottom:

            pattern["scored"] = True

            score += 1

            play_sound(
                score_sound
            )

            if score > high_score:

                high_score = score


# ============================================================
# REMOVE OLD OBSTACLES
# ============================================================


def remove_old_patterns():
    """
    Removes obstacles after they leave
    the screen.
    """

    patterns_to_remove = []

    for pattern in patterns:

        if all(
            obstacle.top > HEIGHT
            for obstacle in pattern["rects"]
        ):

            patterns_to_remove.append(
                pattern
            )

    for pattern in patterns_to_remove:

        patterns.remove(
            pattern
        )


# ============================================================
# RESET GAME
# ============================================================


def reset_game():
    """
    Resets current run.
    """

    global player_lane
    global player_x
    global target_x
    global obstacle_timer
    global score
    global road_line_offset

    player_lane = MIDDLE

    player_x = get_player_x(
        MIDDLE
    )

    target_x = player_x

    obstacle_timer = 0

    score = 0

    road_line_offset = 0

    patterns.clear()


def start_countdown():
    """
    Starts a new game.
    """

    global game_state
    global countdown_time
    global countdown_number
    global last_countdown_number

    reset_game()

    game_state = COUNTDOWN

    countdown_time = 0

    countdown_number = 3

    last_countdown_number = 3

    play_sound(
        countdown_sound
    )


# ============================================================
# DRAW ROAD
# ============================================================


def draw_road():
    """
    Draws road and moving lane markings.
    """

    pygame.draw.rect(
        screen,
        ROAD_COLOR,
        (
            ROAD_X,
            ROAD_Y,
            ROAD_WIDTH,
            ROAD_HEIGHT
        )
    )

    # Road edges
    pygame.draw.line(
        screen,
        ROAD_EDGE_COLOR,
        (
            ROAD_X,
            ROAD_Y
        ),
        (
            ROAD_X,
            ROAD_Y + ROAD_HEIGHT
        ),
        6
    )

    pygame.draw.line(
        screen,
        ROAD_EDGE_COLOR,
        (
            ROAD_X + ROAD_WIDTH,
            ROAD_Y
        ),
        (
            ROAD_X + ROAD_WIDTH,
            ROAD_Y + ROAD_HEIGHT
        ),
        6
    )

    # Lane markings
    line_spacing = (
        ROAD_LINE_HEIGHT
        + ROAD_LINE_GAP
    )

    y = (
        ROAD_Y
        - line_spacing
        + road_line_offset
    )

    while y < ROAD_Y + ROAD_HEIGHT:

        for divider in [1, 2]:

            x = (
                ROAD_X
                + divider * LANE_WIDTH
            )

            pygame.draw.rect(
                screen,
                LANE_LINE_COLOR,
                (
                    x - 3,
                    int(y),
                    6,
                    ROAD_LINE_HEIGHT
                )
            )

        y += line_spacing


# ============================================================
# DRAW PLAYER
# ============================================================


def draw_player():
    """
    Draws the futuristic player vehicle.
    """

    x = int(player_x)
    y = PLAYER_Y

    # Shadow
    shadow = pygame.Rect(
        x + 5,
        y + 12,
        PLAYER_WIDTH,
        PLAYER_HEIGHT
    )

    pygame.draw.ellipse(
        screen,
        (8, 9, 12),
        shadow
    )

    # Glow
    glow = pygame.Rect(
        x - 10,
        y - 10,
        PLAYER_WIDTH + 20,
        PLAYER_HEIGHT + 20
    )

    pygame.draw.rect(
        screen,
        PLAYER_GLOW,
        glow,
        border_radius=18
    )

    # Main body
    body = pygame.Rect(
        x,
        y,
        PLAYER_WIDTH,
        PLAYER_HEIGHT
    )

    pygame.draw.rect(
        screen,
        PLAYER_DARK,
        body,
        border_radius=15
    )

    inner_body = pygame.Rect(
        x + 6,
        y + 5,
        PLAYER_WIDTH - 12,
        PLAYER_HEIGHT - 10
    )

    pygame.draw.rect(
        screen,
        PLAYER_COLOR,
        inner_body,
        border_radius=12
    )

    # Windshield
    windshield = pygame.Rect(
        x + 16,
        y + 17,
        PLAYER_WIDTH - 32,
        28
    )

    pygame.draw.rect(
        screen,
        WINDOW_COLOR,
        windshield,
        border_radius=8
    )

    pygame.draw.line(
        screen,
        (80, 180, 210),
        (
            x + 23,
            y + 23
        ),
        (
            x + PLAYER_WIDTH - 23,
            y + 23
        ),
        3
    )

    # Center line
    pygame.draw.line(
        screen,
        PLAYER_DARK,
        (
            x + PLAYER_WIDTH // 2,
            y + 48
        ),
        (
            x + PLAYER_WIDTH // 2,
            y + 85
        ),
        4
    )

    # Wheels
    wheel_positions = [
        (
            x - 5,
            y + 20
        ),
        (
            x + PLAYER_WIDTH - 3,
            y + 20
        ),
        (
            x - 5,
            y + 68
        ),
        (
            x + PLAYER_WIDTH - 3,
            y + 68
        )
    ]

    for wheel_x, wheel_y in wheel_positions:

        pygame.draw.rect(
            screen,
            WHEEL_COLOR,
            (
                wheel_x,
                wheel_y,
                10,
                22
            ),
            border_radius=4
        )

    # Front lights
    pygame.draw.rect(
        screen,
        WHITE,
        (
            x + 10,
            y + 7,
            16,
            7
        ),
        border_radius=3
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (
            x + PLAYER_WIDTH - 26,
            y + 7,
            16,
            7
        ),
        border_radius=3
    )


# ============================================================
# DRAW OBSTACLE
# ============================================================


def draw_single_obstacle(obstacle):
    """
    Draws one road barrier.
    """

    x = obstacle.x
    y = obstacle.y

    # Shadow
    shadow = pygame.Rect(
        x + 6,
        y + 10,
        OBSTACLE_WIDTH,
        OBSTACLE_HEIGHT
    )

    pygame.draw.ellipse(
        screen,
        (8, 9, 12),
        shadow
    )

    # Glow
    glow = obstacle.inflate(
        12,
        12
    )

    pygame.draw.rect(
        screen,
        OBSTACLE_GLOW,
        glow,
        border_radius=10
    )

    # Main body
    pygame.draw.rect(
        screen,
        OBSTACLE_DARK,
        obstacle,
        border_radius=10
    )

    inner = pygame.Rect(
        x + 5,
        y + 5,
        OBSTACLE_WIDTH - 10,
        OBSTACLE_HEIGHT - 10
    )

    pygame.draw.rect(
        screen,
        OBSTACLE_COLOR,
        inner,
        border_radius=7
    )

    # Warning stripes
    stripe_width = 16

    for stripe_x in range(
        x - 10,
        x + OBSTACLE_WIDTH + 20,
        stripe_width * 2
    ):

        pygame.draw.polygon(
            screen,
            WARNING_COLOR,
            [
                (
                    stripe_x,
                    y + OBSTACLE_HEIGHT
                ),
                (
                    stripe_x + stripe_width,
                    y + OBSTACLE_HEIGHT
                ),
                (
                    stripe_x + stripe_width + 18,
                    y
                ),
                (
                    stripe_x + 18,
                    y
                )
            ]
        )

    # Warning panel
    panel = pygame.Rect(
        x + 18,
        y + 25,
        OBSTACLE_WIDTH - 36,
        35
    )

    pygame.draw.rect(
        screen,
        OBSTACLE_DARK,
        panel,
        border_radius=5
    )

    # Warning lights
    pygame.draw.circle(
        screen,
        WARNING_COLOR,
        (
            x + 30,
            y + 43
        ),
        5
    )

    pygame.draw.circle(
        screen,
        WARNING_COLOR,
        (
            x + OBSTACLE_WIDTH - 30,
            y + 43
        ),
        5
    )


def draw_obstacles():
    """
    Draws all obstacle patterns.
    """

    for pattern in patterns:

        for obstacle in pattern["rects"]:

            draw_single_obstacle(
                obstacle
            )


# ============================================================
# HUD
# ============================================================


def draw_hud():
    """
    Draws score and level.
    """

    _, _, level = get_difficulty()

    # Score panel
    score_panel = pygame.Rect(
        20,
        18,
        190,
        60
    )

    pygame.draw.rect(
        screen,
        (20, 23, 30),
        score_panel,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        PLAYER_DARK,
        score_panel,
        2,
        border_radius=12
    )

    score_text = font_medium.render(
        f"SCORE  {score}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (
            35,
            32
        )
    )

    # Level panel
    level_panel = pygame.Rect(
        WIDTH - 150,
        18,
        130,
        60
    )

    pygame.draw.rect(
        screen,
        (20, 23, 30),
        level_panel,
        border_radius=12
    )

    level_text = font_small.render(
        f"LEVEL {level}",
        True,
        GREY
    )

    screen.blit(
        level_text,
        level_text.get_rect(
            center=level_panel.center
        )
    )


# ============================================================
# MENU
# ============================================================


def draw_menu():
    """
    Draws main menu.
    """

    screen.fill(
        BACKGROUND
    )

    title = font_title.render(
        "SHIFT",
        True,
        PLAYER_COLOR
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

    subtitle = font_medium.render(
        "DODGE. SURVIVE. SHIFT.",
        True,
        WHITE
    )

    screen.blit(
        subtitle,
        subtitle.get_rect(
            center=(
                WIDTH // 2,
                270
            )
        )
    )

    controls = font_small.render(
        "A / D   or   LEFT / RIGHT",
        True,
        GREY
    )

    screen.blit(
        controls,
        controls.get_rect(
            center=(
                WIDTH // 2,
                350
            )
        )
    )

    start_box = pygame.Rect(
        WIDTH // 2 - 180,
        420,
        360,
        65
    )

    pygame.draw.rect(
        screen,
        PLAYER_DARK,
        start_box,
        border_radius=14
    )

    start_text = font_medium.render(
        "PRESS SPACE TO START",
        True,
        WHITE
    )

    screen.blit(
        start_text,
        start_text.get_rect(
            center=start_box.center
        )
    )

    best_text = font_small.render(
        f"BEST SCORE: {high_score}",
        True,
        GREY
    )

    screen.blit(
        best_text,
        best_text.get_rect(
            center=(
                WIDTH // 2,
                530
            )
        )
    )


# ============================================================
# COUNTDOWN
# ============================================================


def draw_countdown():
    """
    Draws countdown screen.
    """

    screen.fill(
        BACKGROUND
    )

    draw_road()

    draw_obstacles()

    draw_player()

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 120)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    number_text = font_huge.render(
        str(countdown_number),
        True,
        WHITE
    )

    screen.blit(
        number_text,
        number_text.get_rect(
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
    """
    Draws Game Over screen.
    """

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 185)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    game_over_text = font_large.render(
        "GAME OVER",
        True,
        WHITE
    )

    score_text = font_medium.render(
        f"SCORE: {score}",
        True,
        WHITE
    )

    best_text = font_medium.render(
        f"BEST: {high_score}",
        True,
        PLAYER_COLOR
    )

    restart_text = font_small.render(
        "R  →  RESTART",
        True,
        GREY
    )

    menu_text = font_small.render(
        "ESC  →  MENU",
        True,
        GREY
    )

    screen.blit(
        game_over_text,
        game_over_text.get_rect(
            center=(
                WIDTH // 2,
                250
            )
        )
    )

    screen.blit(
        score_text,
        score_text.get_rect(
            center=(
                WIDTH // 2,
                325
            )
        )
    )

    screen.blit(
        best_text,
        best_text.get_rect(
            center=(
                WIDTH // 2,
                370
            )
        )
    )

    screen.blit(
        restart_text,
        restart_text.get_rect(
            center=(
                WIDTH // 2,
                435
            )
        )
    )

    screen.blit(
        menu_text,
        menu_text.get_rect(
            center=(
                WIDTH // 2,
                475
            )
        )
    )


# ============================================================
# INITIAL POSITION
# ============================================================

player_x = get_player_x(
    MIDDLE
)

target_x = player_x

# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    dt = clock.tick(60) / 1000.0

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            # ------------------------------------------------
            # MENU
            # ------------------------------------------------

            if game_state == MENU:

                if event.key == pygame.K_SPACE:

                    start_countdown()

            # ------------------------------------------------
            # COUNTDOWN
            # ------------------------------------------------

            elif game_state == COUNTDOWN:

                pass

            # ------------------------------------------------
            # PLAYING
            # ------------------------------------------------

            elif game_state == PLAYING:

                if event.key in (
                    pygame.K_LEFT,
                    pygame.K_a
                ):

                    move_left()

                elif event.key in (
                    pygame.K_RIGHT,
                    pygame.K_d
                ):

                    move_right()

                elif event.key == pygame.K_ESCAPE:

                    game_state = MENU

                    patterns.clear()

            # ------------------------------------------------
            # GAME OVER
            # ------------------------------------------------

            elif game_state == GAME_OVER:

                if event.key == pygame.K_r:

                    start_countdown()

                elif event.key == pygame.K_ESCAPE:

                    game_state = MENU

                    patterns.clear()

    # ========================================================
    # COUNTDOWN UPDATE
    # ========================================================

    if game_state == COUNTDOWN:

        countdown_time += dt

        if countdown_time < 1:

            countdown_number = 3

        elif countdown_time < 2:

            countdown_number = 2

        elif countdown_time < 3:

            countdown_number = 1

        else:

            game_state = PLAYING

            obstacle_timer = 0

            play_sound(
                start_sound
            )

    # ========================================================
    # PLAYING UPDATE
    # ========================================================

    elif game_state == PLAYING:

        move_player(dt)

        update_road_animation(dt)

        _, spawn_interval, _ = get_difficulty()

        obstacle_timer += dt

        if obstacle_timer >= spawn_interval:

            obstacle_timer = 0

            spawn_pattern()

        move_obstacles(dt)

        check_collisions()

        if game_state == PLAYING:

            update_score()

        remove_old_patterns()

    # ========================================================
    # DRAW
    # ========================================================

    if game_state == MENU:

        draw_menu()

    else:

        screen.fill(
            BACKGROUND
        )

        draw_road()

        draw_obstacles()

        draw_player()

        if game_state in (
            PLAYING,
            GAME_OVER
        ):

            draw_hud()

        if game_state == COUNTDOWN:

            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 100)
            )

            screen.blit(
                overlay,
                (0, 0)
            )

            number_text = font_huge.render(
                str(countdown_number),
                True,
                WHITE
            )

            screen.blit(
                number_text,
                number_text.get_rect(
                    center=(
                        WIDTH // 2,
                        HEIGHT // 2
                    )
                )
            )

        elif game_state == GAME_OVER:

            draw_game_over()

    pygame.display.flip()


# ============================================================
# EXIT
# ============================================================

pygame.quit()

sys.exit()