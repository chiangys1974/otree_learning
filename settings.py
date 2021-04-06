from os import environ

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = {
    'real_world_currency_per_point': 10,
    'participation_fee': 150,
    'doc': "",
}

SESSION_CONFIGS = [
    {
        'name': 'DominanceGameLow',
        'display_name': "DominanceGameLow",
        'num_demo_participants': 4,
        'app_sequence': ['DominanceGame'],
        'talent_variation': '低',
    },
    {
        'name': 'DominanceGameHigh',
        'display_name': "DominanceGameHigh",
        'num_demo_participants': 4,
        'app_sequence': ['DominanceGame'],
        'talent_variation': '高',
    },
]


# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'TWD'
USE_POINTS = True

ROOMS = [
    {
         'name': 'DominanceGameLow',
         'display_name': 'DominanceGameLow',
         'participant_label_file': './players_labels.txt',
    },
    {
        'name': 'DominanceGameHigh',
        'display_name': 'DominanceGameHigh',
        'participant_label_file': './players_labels.txt',
    }
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = 'ar_2##*yir9&#z#k5k^b06@yk8e@zd_+l!ibo+79lh)tv^dcd&'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
