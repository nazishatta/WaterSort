#Window + drawing tubes
#Click to select tube
# Move liquid legally
# Win detection
# Restart level
# Next level

LEVELS = [
    # Each tube is bottom -> top
    # 0 = empty tube
    [
        [1, 2, 1, 2],
        [2, 1, 2, 1],
        [],
        [],
    ],
    [
        [1, 2, 3, 1],
        [2, 3, 1, 2],
        [3, 1, 2, 3],
        [],
        [],
    ],
    [
        [1, 2, 3, 4],
        [4, 3, 2, 1],
        [1, 3, 4, 2],
        [2, 4, 1, 3],
        [],
        [],
    ],
]