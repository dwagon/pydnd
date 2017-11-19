con_hp_adjustment = {
        3: (-2, -2),
        4: (-1, -1),
        5: (-1, -1),
        6: (-1, -1),
        7: (0, 0),
        8: (0, 0),
        9: (0, 0),
        10: (0, 0),
        11: (0, 0),
        12: (0, 0),
        13: (0, 0),
        14: (0, 0),
        15: (1, 1),
        16: (2, 2),
        17: (2, 3),
        18: (2, 4)
        }

str_mods = {
        3: {'hitprob': -3, 'dmgadj': -1, 'weight': 5},
        4: {'hitprob': -2, 'dmgadj': -1, 'weight': 10},
        5: {'hitprob': -2, 'dmgadj': 0, 'weight': 10},
        6: {'hitprob': -1, 'dmgadj': 0, 'weight': 20},
        7: {'hitprob': -1, 'dmgadj': 0, 'weight': 20},
        8: {'hitprob': 0, 'dmgadj': 0, 'weight': 35},
        9: {'hitprob': 0, 'dmgadj': 0, 'weight': 35},
        10: {'hitprob': 0, 'dmgadj': 0, 'weight': 40},
        11: {'hitprob': 0, 'dmgadj': 0, 'weight': 40},
        12: {'hitprob': 0, 'dmgadj': 0, 'weight': 45},
        13: {'hitprob': 0, 'dmgadj': 0, 'weight': 45},
        14: {'hitprob': 0, 'dmgadj': 0, 'weight': 55},
        15: {'hitprob': 0, 'dmgadj': 0, 'weight': 55},
        16: {'hitprob': 0, 'dmgadj': 1, 'weight': 70},
        17: {'hitprob': 1, 'dmgadj': 1, 'weight': 85},
        18: {'hitprob': 1, 'dmgadj': 2, 'weight': 110},
        }

bonus_str_mods = {
        '50': {'hitprob': 1, 'dmgadj': 3, 'weight': 135},
        '75': {'hitprob': 2, 'dmgadj': 3, 'weight': 160},
        '90': {'hitprob': 2, 'dmgadj': 4, 'weight': 185},
        '99': {'hitprob': 2, 'dmgadj': 5, 'weight': 235},
        '100': {'hitprob': 3, 'dmgadj': 6, 'weight': 335},
        }

race = {
        'HU': {'movement': 12},
        'EL': {'movement': 12},
        'DW': {'movement': 6},
        'HE': {'movement': 12},
        'GN': {'movement': 6},
        'HL': {'movement': 6}
        }

# EOF
