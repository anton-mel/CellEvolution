# Developed by Anton Melnychuk          March 1st 2024
# For ASTR 330 Class                    Yale University

# Configurations
FODLER_PATH = "./full2"
ORGANIC_THRESHOLD = 0.8
ENERGY_THRESHOLD = 0.8
SECTOR_SIZE_X = 800
SECTOR_SIZE_Y = 800
FAMILIES_COUNT = 4
SECTOR_BORDER = 0
DISPLAY = "color"
CELL_SIZE = 8
FINISH = 500
TICK = 300

ENERGIC_TOXIC = (135, 206, 235)
ORGANIC_TOXIC = (255, 68, 51)
REPROD_MIN = 0.002
BG = (0, 0, 0)

# Colors
LIGHT_GRAY = (245, 245, 245)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (30, 144, 255)    # Radio
BROWN = (139, 69, 19)    # Root
GREEN = (0, 128, 0)      # Leaf
COLONIES_COLOR = {}
BLACK = (0, 0, 0)

fields = {
    "mutation_rate",
    "rotate_skills",
    "rotate_rate",
    "radio_rate",
    "root_rate",
    "leaf_rate"
    "newb_rate",
}

LIFELENGTH = 10
ENERGY_START = 30
ENERGY_RELEASED = 0.001
SOIL_RELEASED = 0.001
AGE_INCREASE = 1
FREEZE_THRESHOLD = 5

# Directions
LEFT, TOP, RIGHT, BOTTOM = 1, 2, 3, 4
DIRECTIONS = [LEFT, TOP, RIGHT, BOTTOM]
