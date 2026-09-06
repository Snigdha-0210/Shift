import pygame
import random
import math
from array import array

# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()

# Audio setup
AUDIO_ENABLED = True

try:
    pygame.mixer.init()
except pygame.error:
    AUDIO_ENABLED = False

WIDTH = 900
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHIFT")

clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BLACK = (8, 10, 16)
ROAD_COLOR = (35, 38, 45)
ROAD_EDGE = (75, 80, 90)

WHITE = (240, 240, 245)
GREY = (150, 155, 165)

CYAN = (0, 220, 255)
CYAN_BRIGHT = (100, 245, 255)

RED = (240, 55, 55)
ORANGE = (255, 150, 40)
YELLOW = (255, 220, 70)

DARK_RED = (100, 20, 25)

GREEN = (70, 230, 130)

# ============================================================
# GAME STATES
# ============================================================

MENU = "menu"
COUNTDOWN = "countdown"
PLAYING = "playing"
GAME_OVER = "game_over"

game_state = MENU

# ============================================================
# LANES
# ============================================================

LEFT = 0
MIDDLE = 1
RIGHT = 2

LANE_COUNT = 3

ROAD_LEFT = 180
ROAD_RIGHT = 720

LANE_WIDTH = (ROAD_RIGHT - ROAD_LEFT) / LANE_COUNT

LANE_CENTERS = [
    ROAD_LEFT + LANE_WIDTH * 0.5,
    ROAD_LEFT + LANE_WIDTH * 1.5,
    ROAD_LEFT + LANE_WIDTH * 2.5,
]

# ============================================================
# PLAYER
# ============================================================

player_lane = MIDDLE

player_x = LANE_CENTERS[MIDDLE]
player_y = 570

PLAYER_WIDTH = 70
PLAYER_HEIGHT = 110

target_x = player_x

PLAYER_MOVE_SPEED = 900

# ============================================================
# OBSTACLES
# ============================================================

patterns = []

OBSTACLE_WIDTH = 120
OBSTACLE_HEIGHT = 55

# ============================================================
# SCORE
# ============================================================

score = 0
high_score = 0

# ============================================================
# DIFFICULTY
# ============================================================

obstacle_speed = 300
spawn_timer = 0
spawn_interval = 1.2
current_level = 1

# ============================================================
# ROAD ANIMATION
# ============================================================

road_line_offset = 0

# ============================================================
# COUNTDOWN
# ============================================================

countdown_timer = 0
countdown_number = 3

# ============================================================
# PARTICLE SYSTEM
# ============================================================

particles = []

score_popups = []

# ============================================================
# SCREEN SHAKE
# ============================================================

screen_shake_time = 0
screen_shake_strength = 0

# ============================================================
# IMPACT FLASH
# ============================================================

impact_flash = 0

# ============================================================
# FONTS
# ============================================================

font_large = pygame.font.SysFont("arial", 72, bold=True)
font_title = pygame.font.SysFont("arial", 100, bold=True)

font_medium = pygame.font.SysFont("arial", 36, bold=True)
font_small = pygame.font.SysFont("arial", 24)
font_tiny = pygame.font.SysFont("arial", 18)

# ============================================================
# SOUND GENERATION
# ============================================================


def create_tone(frequency, duration, volume=0.2):
    """
    Creates a simple electronic sound without external files.
    """

    if not AUDIO_ENABLED:
        return None

    sample_rate = 44100
    sample_count = int(sample_rate * duration)

    buffer = array("h")

    for i in range(sample_count):
        time = i / sample_rate

        wave = math.sin(2 * math.pi * frequency * time)

        fade = 1.0

        if i < sample_count * 0.1:
            fade = i / (sample_count * 0.1)

        if i > sample_count * 0.8:
            fade = (sample_count - i) / (sample_count * 0.2)

        value = int(32767 * wave * volume * fade)

        buffer.append(value)

    try:
        return pygame.mixer.Sound(buffer=buffer)
    except pygame.error:
        return None


move_sound = create_tone(500, 0.08, 0.15)
score_sound = create_tone(900, 0.12, 0.18)
countdown_sound = create_tone(600, 0.12, 0.15)
start_sound = create_tone(1100, 0.18, 0.2)
collision_sound = create_tone(100, 0.4, 0.3)


def play_sound(sound):
    if AUDIO_ENABLED and sound is not None:
        sound.play()


# ============================================================
# PARTICLE FUNCTIONS
# ============================================================


def spawn_particle(
    x,
    y,
    color,
    speed_min=50,
    speed_max=200,
    size_min=3,
    size_max=7,
    life_min=0.3,
    life_max=0.7,
    gravity=0,
):
    angle = random.uniform(0, math.pi * 2)
    speed = random.uniform(speed_min, speed_max)

    particle = {
        "x": x,
        "y": y,
        "vx": math.cos(angle) * speed,
        "vy": math.sin(angle) * speed,
        "size": random.uniform(size_min, size_max),
        "life": random.uniform(life_min, life_max),
        "max_life": 1,
        "color": color,
        "gravity": gravity,
    }

    particle["max_life"] = particle["life"]

    particles.append(particle)


def spawn_particles(
    x,
    y,
    count,
    color,
    speed_min=50,
    speed_max=200,
    size_min=3,
    size_max=7,
    life_min=0.3,
    life_max=0.7,
    gravity=0,
):
    for _ in range(count):
        spawn_particle(
            x,
            y,
            color,
            speed_min,
            speed_max,
            size_min,
            size_max,
            life_min,
            life_max,
            gravity,
        )


def update_particles(dt):

    for particle in particles[:]:

        particle["life"] -= dt

        if particle["life"] <= 0:
            particles.remove(particle)
            continue

        particle["vy"] += particle["gravity"] * dt

        particle["x"] += particle["vx"] * dt
        particle["y"] += particle["vy"] * dt


def draw_particles(offset_x=0, offset_y=0):

    for particle in particles:

        life_ratio = particle["life"] / particle["max_life"]

        size = max(1, int(particle["size"] * life_ratio))

        color = tuple(
            max(0, min(255, int(c * life_ratio)))
            for c in particle["color"]
        )

        pygame.draw.circle(
            screen,
            color,
            (
                int(particle["x"] + offset_x),
                int(particle["y"] + offset_y),
            ),
            size,
        )


# ============================================================
# SCORE POPUPS
# ============================================================


def create_score_popup(x, y):

    score_popups.append(
        {
            "x": x,
            "y": y,
            "life": 0.8,
            "max_life": 0.8,
        }
    )


def update_score_popups(dt):

    for popup in score_popups[:]:

        popup["life"] -= dt
        popup["y"] -= 60 * dt

        if popup["life"] <= 0:
            score_popups.remove(popup)


def draw_score_popups(offset_x=0, offset_y=0):

    for popup in score_popups:

        ratio = popup["life"] / popup["max_life"]

        color = (
            255,
            int(220 * ratio),
            int(70 * ratio),
        )

        text = font_medium.render("+1", True, color)

        rect = text.get_rect(
            center=(
                int(popup["x"] + offset_x),
                int(popup["y"] + offset_y),
            )
        )

        screen.blit(text, rect)


# ============================================================
# SCREEN SHAKE
# ============================================================


def trigger_screen_shake(duration, strength):

    global screen_shake_time
    global screen_shake_strength

    screen_shake_time = duration
    screen_shake_strength = strength


def get_screen_shake():

    if screen_shake_time <= 0:
        return 0, 0

    intensity = screen_shake_time

    x = random.uniform(
        -screen_shake_strength,
        screen_shake_strength,
    ) * intensity

    y = random.uniform(
        -screen_shake_strength,
        screen_shake_strength,
    ) * intensity

    return x, y


# ============================================================
# DIFFICULTY
# ============================================================


def update_difficulty():

    global obstacle_speed
    global spawn_interval
    global current_level

    if score < 5:

        obstacle_speed = 300
        spawn_interval = 1.20
        current_level = 1

    elif score < 10:

        obstacle_speed = 350
        spawn_interval = 1.05
        current_level = 2

    elif score < 15:

        obstacle_speed = 400
        spawn_interval = 0.90
        current_level = 3

    elif score < 20:

        obstacle_speed = 450
        spawn_interval = 0.80
        current_level = 4

    else:

        obstacle_speed = 500
        spawn_interval = 0.70
        current_level = 5


# ============================================================
# SAFE LANE
# ============================================================


def get_reachable_lane():

    possible_lanes = [player_lane]

    if player_lane > LEFT:
        possible_lanes.append(player_lane - 1)

    if player_lane < RIGHT:
        possible_lanes.append(player_lane + 1)

    return random.choice(possible_lanes)


# ============================================================
# OBSTACLE PATTERNS
# ============================================================


def spawn_pattern():

    safe_lane = get_reachable_lane()

    blocked_lanes = []

    if score < 5:

        # Only one obstacle
        blocked_lanes = [
            lane
            for lane in range(LANE_COUNT)
            if lane != safe_lane
        ]

        blocked_lanes = [random.choice(blocked_lanes)]

    elif score < 10:

        if random.random() < 0.75:

            blocked_lanes = [
                lane
                for lane in range(LANE_COUNT)
                if lane != safe_lane
            ]

            blocked_lanes = [random.choice(blocked_lanes)]

        else:

            blocked_lanes = [
                lane
                for lane in range(LANE_COUNT)
                if lane != safe_lane
            ]

    elif score < 20:

        if random.random() < 0.60:

            blocked_lanes = [
                lane
                for lane in range(LANE_COUNT)
                if lane != safe_lane
            ]

            blocked_lanes = [random.choice(blocked_lanes)]

        else:

            blocked_lanes = [
                lane
                for lane in range(LANE_COUNT)
                if lane != safe_lane
            ]

    else:

        if random.random() < 0.50:

            blocked_lanes = [
                lane
                for lane in range(LANE_COUNT)
                if lane != safe_lane
            ]

            blocked_lanes = [random.choice(blocked_lanes)]

        else:

            blocked_lanes = [
                lane
                for lane in range(LANE_COUNT)
                if lane != safe_lane
            ]

    rects = []

    for lane in blocked_lanes:

        rect = pygame.Rect(
            0,
            -OBSTACLE_HEIGHT,
            OBSTACLE_WIDTH,
            OBSTACLE_HEIGHT,
        )

        rect.centerx = LANE_CENTERS[lane]
        rect.y = -OBSTACLE_HEIGHT

        rects.append(rect)

    patterns.append(
        {
            "rects": rects,
            "scored": False,
        }
    )


# ============================================================
# PLAYER MOVEMENT
# ============================================================


def move_left():

    global player_lane
    global target_x

    if player_lane > LEFT:

        player_lane -= 1
        target_x = LANE_CENTERS[player_lane]

        play_sound(move_sound)

        # Lane change particles
        spawn_particles(
            player_x,
            player_y + PLAYER_HEIGHT * 0.4,
            10,
            CYAN,
            speed_min=40,
            speed_max=140,
            size_min=2,
            size_max=5,
            life_min=0.2,
            life_max=0.45,
        )


def move_right():

    global player_lane
    global target_x

    if player_lane < RIGHT:

        player_lane += 1
        target_x = LANE_CENTERS[player_lane]

        play_sound(move_sound)

        # Lane change particles
        spawn_particles(
            player_x,
            player_y + PLAYER_HEIGHT * 0.4,
            10,
            CYAN,
            speed_min=40,
            speed_max=140,
            size_min=2,
            size_max=5,
            life_min=0.2,
            life_max=0.45,
        )


# ============================================================
# PLAYER RECT
# ============================================================


def get_player_rect():

    return pygame.Rect(
        int(player_x - PLAYER_WIDTH / 2),
        int(player_y - PLAYER_HEIGHT / 2),
        PLAYER_WIDTH,
        PLAYER_HEIGHT,
    )


# ============================================================
# DRAW ROAD
# ============================================================


def draw_road(offset_x=0, offset_y=0):

    road_rect = pygame.Rect(
        ROAD_LEFT + int(offset_x),
        int(offset_y),
        ROAD_RIGHT - ROAD_LEFT,
        HEIGHT,
    )

    pygame.draw.rect(
        screen,
        ROAD_COLOR,
        road_rect,
    )

    # Road edges
    pygame.draw.line(
        screen,
        ROAD_EDGE,
        (
            ROAD_LEFT + int(offset_x),
            int(offset_y),
        ),
        (
            ROAD_LEFT + int(offset_x),
            HEIGHT + int(offset_y),
        ),
        6,
    )

    pygame.draw.line(
        screen,
        ROAD_EDGE,
        (
            ROAD_RIGHT + int(offset_x),
            int(offset_y),
        ),
        (
            ROAD_RIGHT + int(offset_x),
            HEIGHT + int(offset_y),
        ),
        6,
    )

    # Lane divider animation
    dash_height = 45
    gap = 35

    y = -100 + road_line_offset

    while y < HEIGHT + 100:

        for divider in [1, 2]:

            x = ROAD_LEFT + LANE_WIDTH * divider

            pygame.draw.rect(
                screen,
                (80, 85, 95),
                pygame.Rect(
                    int(x + offset_x - 2),
                    int(y + offset_y),
                    4,
                    dash_height,
                ),
            )

        y += dash_height + gap


# ============================================================
# DRAW PLAYER
# ============================================================


def draw_player(offset_x=0, offset_y=0):

    rect = get_player_rect()

    rect.x += int(offset_x)
    rect.y += int(offset_y)

    # Glow
    glow_rect = rect.inflate(25, 25)

    pygame.draw.rect(
        screen,
        (0, 100, 120),
        glow_rect,
        border_radius=15,
    )

    # Main body
    pygame.draw.rect(
        screen,
        CYAN,
        rect,
        border_radius=12,
    )

    # Inner body
    inner = rect.inflate(-10, -10)

    pygame.draw.rect(
        screen,
        (20, 80, 95),
        inner,
        border_radius=8,
    )

    # Windshield
    windshield = pygame.Rect(
        rect.x + 12,
        rect.y + 18,
        rect.width - 24,
        28,
    )

    pygame.draw.rect(
        screen,
        (10, 30, 40),
        windshield,
        border_radius=6,
    )

    # Wheels
    wheel_width = 8
    wheel_height = 24

    pygame.draw.rect(
        screen,
        BLACK,
        (
            rect.left - 4,
            rect.y + 20,
            wheel_width,
            wheel_height,
        ),
        border_radius=3,
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (
            rect.right - 4,
            rect.y + 20,
            wheel_width,
            wheel_height,
        ),
        border_radius=3,
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (
            rect.left - 4,
            rect.bottom - 44,
            wheel_width,
            wheel_height,
        ),
        border_radius=3,
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (
            rect.right - 4,
            rect.bottom - 44,
            wheel_width,
            wheel_height,
        ),
        border_radius=3,
    )

    # Lights
    pygame.draw.circle(
        screen,
        YELLOW,
        (
            rect.centerx - 18,
            rect.bottom - 12,
        ),
        5,
    )

    pygame.draw.circle(
        screen,
        YELLOW,
        (
            rect.centerx + 18,
            rect.bottom - 12,
        ),
        5,
    )


# ============================================================
# DRAW OBSTACLES
# ============================================================


def draw_obstacles(offset_x=0, offset_y=0):

    for pattern in patterns:

        for rect in pattern["rects"]:

            draw_rect = rect.copy()

            draw_rect.x += int(offset_x)
            draw_rect.y += int(offset_y)

            # Glow
            glow = draw_rect.inflate(10, 10)

            pygame.draw.rect(
                screen,
                (100, 35, 30),
                glow,
                border_radius=6,
            )

            # Main barrier
            pygame.draw.rect(
                screen,
                RED,
                draw_rect,
                border_radius=6,
            )

            # Warning stripes
            stripe_width = 18

            for x in range(
                draw_rect.left,
                draw_rect.right,
                stripe_width * 2,
            ):

                points = [
                    (x, draw_rect.bottom),
                    (x + stripe_width, draw_rect.bottom),
                    (x + stripe_width + 10, draw_rect.top),
                    (x + 10, draw_rect.top),
                ]

                pygame.draw.polygon(
                    screen,
                    YELLOW,
                    points,
                )

            # Center panel
            panel = draw_rect.inflate(-20, -20)

            pygame.draw.rect(
                screen,
                DARK_RED,
                panel,
                border_radius=4,
            )

            # Warning lights
            pygame.draw.circle(
                screen,
                YELLOW,
                (
                    draw_rect.left + 14,
                    draw_rect.centery,
                ),
                5,
            )

            pygame.draw.circle(
                screen,
                YELLOW,
                (
                    draw_rect.right - 14,
                    draw_rect.centery,
                ),
                5,
            )


# ============================================================
# DRAW HUD
# ============================================================


def draw_hud():

    score_text = font_medium.render(
        f"SCORE  {score}",
        True,
        WHITE,
    )

    screen.blit(
        score_text,
        (25, 20),
    )

    level_text = font_small.render(
        f"LEVEL  {current_level}",
        True,
        CYAN,
    )

    screen.blit(
        level_text,
        (25, 65),
    )


# ============================================================
# DRAW MENU
# ============================================================


def draw_menu():

    screen.fill(BLACK)

    title = font_title.render(
        "SHIFT",
        True,
        CYAN,
    )

    title_rect = title.get_rect(
        center=(WIDTH // 2, 190)
    )

    screen.blit(title, title_rect)

    subtitle = font_medium.render(
        "DODGE. SHIFT. SURVIVE.",
        True,
        WHITE,
    )

    subtitle_rect = subtitle.get_rect(
        center=(WIDTH // 2, 280)
    )

    screen.blit(subtitle, subtitle_rect)

    instruction = font_small.render(
        "Press SPACE to start",
        True,
        GREY,
    )

    instruction_rect = instruction.get_rect(
        center=(WIDTH // 2, 370)
    )

    screen.blit(
        instruction,
        instruction_rect,
    )

    controls = font_small.render(
        "LEFT / RIGHT  or  A / D",
        True,
        GREY,
    )

    controls_rect = controls.get_rect(
        center=(WIDTH // 2, 420)
    )

    screen.blit(
        controls,
        controls_rect,
    )

    best = font_small.render(
        f"BEST SCORE: {high_score}",
        True,
        YELLOW,
    )

    best_rect = best.get_rect(
        center=(WIDTH // 2, 500)
    )

    screen.blit(
        best,
        best_rect,
    )


# ============================================================
# DRAW COUNTDOWN
# ============================================================


def draw_countdown():

    # Draw game world behind countdown
    draw_road()
    draw_obstacles()
    draw_player()
    draw_particles()
    draw_hud()

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA,
    )

    overlay.fill((0, 0, 0, 90))

    screen.blit(
        overlay,
        (0, 0),
    )

    number = font_title.render(
        str(countdown_number),
        True,
        CYAN,
    )

    rect = number.get_rect(
        center=(WIDTH // 2, HEIGHT // 2)
    )

    screen.blit(
        number,
        rect,
    )


# ============================================================
# DRAW GAME OVER
# ============================================================


def draw_game_over(offset_x=0, offset_y=0):

    # Game world remains visible behind the overlay
    draw_road(offset_x, offset_y)
    draw_obstacles(offset_x, offset_y)
    draw_particles(offset_x, offset_y)
    draw_player(offset_x, offset_y)

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA,
    )

    overlay.fill((0, 0, 0, 160))

    screen.blit(
        overlay,
        (0, 0),
    )

    title = font_large.render(
        "GAME OVER",
        True,
        RED,
    )

    title_rect = title.get_rect(
        center=(WIDTH // 2, 240)
    )

    screen.blit(
        title,
        title_rect,
    )

    score_text = font_medium.render(
        f"SCORE: {score}",
        True,
        WHITE,
    )

    score_rect = score_text.get_rect(
        center=(WIDTH // 2, 320)
    )

    screen.blit(
        score_text,
        score_rect,
    )

    best_text = font_small.render(
        f"BEST: {high_score}",
        True,
        YELLOW,
    )

    best_rect = best_text.get_rect(
        center=(WIDTH // 2, 370)
    )

    screen.blit(
        best_text,
        best_rect,
    )

    restart = font_small.render(
        "Press R to restart",
        True,
        GREY,
    )

    restart_rect = restart.get_rect(
        center=(WIDTH // 2, 450)
    )

    screen.blit(
        restart,
        restart_rect,
    )

    menu_text = font_small.render(
        "Press ESC for menu",
        True,
        GREY,
    )

    menu_rect = menu_text.get_rect(
        center=(WIDTH // 2, 490)
    )

    screen.blit(
        menu_text,
        menu_rect,
    )


# ============================================================
# RESET GAME
# ============================================================


def reset_game():

    global player_lane
    global player_x
    global target_x

    global score

    global patterns

    global spawn_timer

    global road_line_offset

    global screen_shake_time
    global screen_shake_strength

    global impact_flash

    player_lane = MIDDLE

    player_x = LANE_CENTERS[MIDDLE]

    target_x = player_x

    score = 0

    patterns = []

    spawn_timer = 0

    road_line_offset = 0

    screen_shake_time = 0
    screen_shake_strength = 0

    impact_flash = 0

    particles.clear()
    score_popups.clear()

    update_difficulty()


# ============================================================
# START GAME
# ============================================================


def start_game():

    global game_state
    global countdown_timer
    global countdown_number

    reset_game()

    game_state = COUNTDOWN

    countdown_timer = 0
    countdown_number = 3

    play_sound(countdown_sound)


# ============================================================
# COLLISION EFFECT
# ============================================================


def trigger_collision():

    global game_state
    global high_score
    global impact_flash

    # Prevent duplicate collision handling
    if game_state != PLAYING:
        return

    game_state = GAME_OVER

    if score > high_score:
        high_score = score

    play_sound(collision_sound)

    # Screen shake
    trigger_screen_shake(
        duration=1.0,
        strength=18,
    )

    # Red impact flash
    impact_flash = 255

    # Big explosion
    spawn_particles(
        player_x,
        player_y,
        70,
        RED,
        speed_min=80,
        speed_max=450,
        size_min=3,
        size_max=10,
        life_min=0.4,
        life_max=1.1,
        gravity=350,
    )

    spawn_particles(
        player_x,
        player_y,
        40,
        ORANGE,
        speed_min=100,
        speed_max=500,
        size_min=2,
        size_max=8,
        life_min=0.3,
        life_max=0.9,
        gravity=300,
    )

    spawn_particles(
        player_x,
        player_y,
        20,
        YELLOW,
        speed_min=50,
        speed_max=300,
        size_min=2,
        size_max=6,
        life_min=0.3,
        life_max=0.8,
        gravity=200,
    )


# ============================================================
# UPDATE GAME
# ============================================================


def update_playing(dt):

    global player_x
    global spawn_timer
    global road_line_offset
    global score
    global game_state

    # --------------------------------------------------------
    # Smooth player movement
    # --------------------------------------------------------

    difference = target_x - player_x

    if abs(difference) > 1:

        movement = PLAYER_MOVE_SPEED * dt

        if abs(difference) < movement:
            player_x = target_x
        else:
            player_x += math.copysign(
                movement,
                difference,
            )

    # --------------------------------------------------------
    # Road movement
    # --------------------------------------------------------

    road_line_offset += obstacle_speed * dt

    if road_line_offset > 80:
        road_line_offset -= 80

    # --------------------------------------------------------
    # Spawn obstacles
    # --------------------------------------------------------

    spawn_timer += dt

    if spawn_timer >= spawn_interval:

        spawn_timer = 0

        spawn_pattern()

    # --------------------------------------------------------
    # Move obstacle patterns
    # --------------------------------------------------------

    for pattern in patterns:

        for rect in pattern["rects"]:

            rect.y += obstacle_speed * dt

    # --------------------------------------------------------
    # Collision detection
    # --------------------------------------------------------

    player_rect = get_player_rect()

    for pattern in patterns:

        for rect in pattern["rects"]:

            if player_rect.colliderect(rect):

                trigger_collision()

                return

    # --------------------------------------------------------
    # Score when complete pattern passes player
    # --------------------------------------------------------

    for pattern in patterns:

        if pattern["scored"]:
            continue

        highest_bottom = max(
            rect.bottom
            for rect in pattern["rects"]
        )

        if highest_bottom > player_y + PLAYER_HEIGHT / 2:

            pattern["scored"] = True

            score += 1

            update_difficulty()

            play_sound(score_sound)

            # Score particles
            spawn_particles(
                player_x,
                player_y - 55,
                18,
                YELLOW,
                speed_min=30,
                speed_max=160,
                size_min=2,
                size_max=6,
                life_min=0.3,
                life_max=0.7,
                gravity=-80,
            )

            # Floating +1
            create_score_popup(
                player_x,
                player_y - 70,
            )

    # --------------------------------------------------------
    # Remove old patterns
    # --------------------------------------------------------

    for pattern in patterns[:]:

        if all(
            rect.top > HEIGHT + 100
            for rect in pattern["rects"]
        ):

            patterns.remove(pattern)


# ============================================================
# UPDATE COUNTDOWN
# ============================================================


def update_countdown(dt):

    global countdown_timer
    global countdown_number
    global game_state

    countdown_timer += dt

    if countdown_timer >= 1:

        countdown_timer = 0

        countdown_number -= 1

        if countdown_number > 0:

            play_sound(countdown_sound)

        else:

            game_state = PLAYING

            play_sound(start_sound)

            # Small starting particle burst
            spawn_particles(
                player_x,
                player_y + 50,
                20,
                CYAN,
                speed_min=40,
                speed_max=180,
                size_min=2,
                size_max=5,
                life_min=0.2,
                life_max=0.5,
            )


# ============================================================
# UPDATE EFFECTS
# ============================================================


def update_effects(dt):

    global screen_shake_time
    global impact_flash

    update_particles(dt)
    update_score_popups(dt)

    # Screen shake timer
    if screen_shake_time > 0:

        screen_shake_time -= dt

        if screen_shake_time < 0:
            screen_shake_time = 0

    # Impact flash
    if impact_flash > 0:

        impact_flash -= 700 * dt

        if impact_flash < 0:
            impact_flash = 0


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    dt = clock.tick(60) / 1000.0

    # Prevent giant jumps if the window freezes
    dt = min(dt, 0.05)

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

                    start_game()

            # ------------------------------------------------
            # COUNTDOWN
            # ------------------------------------------------

            elif game_state == COUNTDOWN:

                if event.key == pygame.K_ESCAPE:

                    game_state = MENU

            # ------------------------------------------------
            # PLAYING
            # ------------------------------------------------

            elif game_state == PLAYING:

                if event.key in (
                    pygame.K_LEFT,
                    pygame.K_a,
                ):

                    move_left()

                elif event.key in (
                    pygame.K_RIGHT,
                    pygame.K_d,
                ):

                    move_right()

                elif event.key == pygame.K_ESCAPE:

                    game_state = MENU

            # ------------------------------------------------
            # GAME OVER
            # ------------------------------------------------

            elif game_state == GAME_OVER:

                if event.key == pygame.K_r:

                    start_game()

                elif event.key == pygame.K_ESCAPE:

                    game_state = MENU

    # ========================================================
    # UPDATE
    # ========================================================

    if game_state == COUNTDOWN:

        update_countdown(dt)

    elif game_state == PLAYING:

        update_playing(dt)

    update_effects(dt)

    # ========================================================
    # SCREEN SHAKE
    # ========================================================

    offset_x, offset_y = get_screen_shake()

    # ========================================================
    # DRAW
    # ========================================================

    if game_state == MENU:

        draw_menu()

    elif game_state == COUNTDOWN:

        draw_countdown()

    elif game_state == PLAYING:

        screen.fill(BLACK)

        draw_road(offset_x, offset_y)

        draw_obstacles(offset_x, offset_y)

        draw_particles(offset_x, offset_y)

        draw_player(offset_x, offset_y)

        draw_score_popups(offset_x, offset_y)

        draw_hud()

    elif game_state == GAME_OVER:

        screen.fill(BLACK)

        draw_game_over(
            offset_x,
            offset_y,
        )

        draw_score_popups(
            offset_x,
            offset_y,
        )

    # ========================================================
    # IMPACT FLASH
    # ========================================================

    if impact_flash > 0:

        flash = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA,
        )

        alpha = int(
            min(255, impact_flash)
        )

        flash.fill(
            (255, 30, 30, alpha)
        )

        screen.blit(
            flash,
            (0, 0),
        )

    pygame.display.flip()


pygame.quit()