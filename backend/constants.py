"""All domain constants used across the Philos Orientation system."""

ANONYMOUS_ALIASES = [
    "Explorer", "Builder", "Seeker", "Navigator", "Pioneer",
    "Guardian", "Visionary", "Pathfinder", "Strategist", "Catalyst",
    "Dreamer", "Architect", "Sentinel", "Wanderer", "Alchemist",
    "Sage", "Herald", "Beacon", "Anchor", "Voyager"
]

DIRECTION_FORCE_MAP = {
    'contribution': {'cognitive': 0.2, 'emotional': 0.4, 'physical': 0.1, 'personal': 0.1, 'social': 0.8, 'drives': 0.3},
    'recovery': {'cognitive': 0.3, 'emotional': 0.6, 'physical': 0.5, 'personal': 0.7, 'social': 0.1, 'drives': 0.2},
    'order': {'cognitive': 0.7, 'emotional': 0.2, 'physical': 0.3, 'personal': 0.4, 'social': 0.3, 'drives': 0.6},
    'exploration': {'cognitive': 0.8, 'emotional': 0.5, 'physical': 0.2, 'personal': 0.3, 'social': 0.4, 'drives': 0.7}
}

DIRECTION_VECTOR_MAP = {
    'contribution': {'internal': 0.2, 'external': 0.5, 'collective': 0.8},
    'recovery': {'internal': 0.8, 'external': 0.1, 'collective': 0.2},
    'order': {'internal': 0.5, 'external': 0.4, 'collective': 0.4},
    'exploration': {'internal': 0.4, 'external': 0.7, 'collective': 0.3}
}

FORCE_LABELS_HE = {
    'cognitive': 'Cognitive', 'emotional': 'Emotional', 'physical': 'Physical',
    'personal': 'Personal', 'social': 'Social', 'drives': 'Drives'
}

VECTOR_LABELS_HE = {
    'internal': 'Internal', 'external': 'External', 'collective': 'Collective'
}

DIRECTION_THEORY = {
    'contribution': {
        'label_he': 'Contribution', 'symbol': 'Giving',
        'explanation_he': 'The Contribution direction expresses the desire to give, help, and impact your surroundings. It is the force that connects the individual to the collective.',
        'meaning_he': 'When you act in the Contribution direction, you strengthen the collective field and create value beyond the boundaries of self.',
        'symbolic_meaning_he': 'The symbol of Contribution is giving — an outward flow. Like a river nourishing the fields around it, Contribution creates value that spreads beyond the individual.',
        'behavior_example_he': 'Helping a friend in crisis, volunteering in the community, sharing knowledge with a colleague, listening to someone who needs a caring ear.',
        'field_effect_he': 'Contribution actions strengthen the bond between parts of the field. The more people act in the Contribution direction, the more connected and stable the collective field becomes.'
    },
    'recovery': {
        'label_he': 'Recovery', 'symbol': 'Restoration',
        'explanation_he': 'The Recovery direction expresses the need for recharging, rest, and inner restoration. It is the force that enables a return to balance.',
        'meaning_he': 'When you act in the Recovery direction, you build the inner foundation from which every other action begins.',
        'symbolic_meaning_he': 'The symbol of Recovery is restoration — the inward movement. Like a tree shedding leaves in autumn to conserve energy for spring, Recovery is the preparation for the next growth.',
        'behavior_example_he': 'Taking a break after a busy day, getting proper sleep, going for a nature walk, quietly drinking a cup of tea, saying no when you are out of energy.',
        'field_effect_he': 'Recovery actions stabilize the foundation of the field. When people allow themselves recovery, they return to the field with more energy and clarity.'
    },
    'order': {
        'label_he': 'Order', 'symbol': 'Structure',
        'explanation_he': 'The Order direction expresses the desire to organize, plan, and create structure. It is the force that brings stability and clarity.',
        'meaning_he': 'When you act in the Order direction, you create a framework that allows all other directions to function effectively.',
        'symbolic_meaning_he': 'The symbol of Order is structure — the skeleton that holds everything together. Like an architect designing a building, Order creates the infrastructure on which everything else is built.',
        'behavior_example_he': 'Organizing your schedule, planning your week, tidying your workspace, writing a to-do list, setting clear goals.',
        'field_effect_he': 'Order actions create structure in the collective field. When there is order, all other directions operate more effectively — the field becomes clear and navigable.'
    },
    'exploration': {
        'label_he': 'Exploration', 'symbol': 'Discovery',
        'explanation_he': 'The Exploration direction expresses curiosity, the desire to learn and discover. It is the force that drives change and growth.',
        'meaning_he': 'When you act in the Exploration direction, you open new doors and expand the boundaries of awareness.',
        'symbolic_meaning_he': 'The symbol of Exploration is discovery — the forward movement toward the unknown. Like an explorer setting sail for the open sea, Exploration requires courage and openness.',
        'behavior_example_he': 'Learning a new subject, trying a different approach to a problem, asking tough questions, stepping out of your comfort zone, meeting new people.',
        'field_effect_he': 'Exploration actions expand the field. They add new dimensions and possibilities that did not exist before — the field becomes dynamic and full of potential.'
    }
}

GLOBE_COUNTRY_COORDS = {
    "BR": {"lat": -14.2, "lng": -51.9}, "IN": {"lat": 20.6, "lng": 78.9}, "DE": {"lat": 51.2, "lng": 10.5},
    "US": {"lat": 37.1, "lng": -95.7}, "JP": {"lat": 36.2, "lng": 138.3}, "NG": {"lat": 9.1, "lng": 8.7},
    "IL": {"lat": 31.1, "lng": 34.8}, "FR": {"lat": 46.2, "lng": 2.2}, "AU": {"lat": -25.3, "lng": 133.8},
    "KR": {"lat": 35.9, "lng": 127.8}, "MX": {"lat": 23.6, "lng": -102.6}, "GB": {"lat": 55.4, "lng": -3.4},
    "CA": {"lat": 56.1, "lng": -106.3}, "IT": {"lat": 41.9, "lng": 12.6}, "ES": {"lat": 40.5, "lng": -3.7},
    "AR": {"lat": -38.4, "lng": -63.6}, "TR": {"lat": 39.0, "lng": 35.2}, "TH": {"lat": 15.9, "lng": 100.5},
    "PL": {"lat": 51.9, "lng": 19.1}, "NL": {"lat": 52.1, "lng": 5.3}
}

GLOBE_COLOR_MAP = {
    'contribution': '#22c55e', 'recovery': '#3b82f6', 'order': '#6366f1', 'exploration': '#f59e0b'
}

GLOBE_DIR_LABELS = {'recovery': 'Recovery', 'order': 'Order', 'contribution': 'Contribution', 'exploration': 'Exploration'}

BASE_DEFINITIONS = {
    'heart': {
        'name_he': 'Connection',
        'description_he': 'What center are you operating from today?',
        'allocations_he': ['Relationships & Connections', 'Empathy & Listening', 'Giving & Contributing', 'Emotional Healing'],
        'allocations_keys': ['relationships', 'empathy', 'contribution', 'emotional_repair']
    },
    'head': {
        'name_he': 'Mind',
        'description_he': 'What center are you operating from today?',
        'allocations_he': ['Order & Planning', 'Learning & Inquiry', 'Decision Making', 'Strategic Thinking'],
        'allocations_keys': ['order', 'learning', 'decision_making', 'strategic_thinking']
    },
    'body': {
        'name_he': 'Body',
        'description_he': 'What center are you operating from today?',
        'allocations_he': ['Movement & Health', 'Practical Action', 'Discipline & Commitment', 'Physical Order'],
        'allocations_keys': ['movement', 'practical_action', 'discipline', 'physical_order']
    }
}

DIRECTION_TO_DEPT = {
    'contribution': 'heart', 'recovery': 'body', 'order': 'head', 'exploration': 'head'
}

DEPT_LABELS_HE = {'heart': 'Connection', 'head': 'Mind', 'body': 'Body'}

MISSION_DESCRIPTIONS = {
    'contribution': {'mission_he': 'Mission of the Day: Contribution', 'description_he': 'Do a small action to help someone else today'},
    'recovery': {'mission_he': 'Mission of the Day: Recovery', 'description_he': 'Take a moment of rest and self-recharging today'},
    'order': {'mission_he': 'Mission of the Day: Order', 'description_he': 'Organize one small thing in your environment today'},
    'exploration': {'mission_he': 'Mission of the Day: Exploration', 'description_he': 'Try something new or learn one new thing today'}
}

MISSION_TARGET = 5000
MAX_INVITE_CODES = 5

VALUE_NICHES = {
    'builder_of_order': {
        'label_he': 'Builder of Order', 'description_he': 'You create structure and stability. Your actions organize the field.',
        'dominant_direction': 'order', 'threshold': 35,
        'strengthening_actions_he': ['Plan your week', 'Set priorities', 'Write a task list']
    },
    'explorer': {
        'label_he': 'Explorer', 'description_he': 'You open new doors. Your curiosity expands the field.',
        'dominant_direction': 'exploration', 'threshold': 35,
        'strengthening_actions_he': ['Learn something new', 'Ask a tough question', 'Try a different approach']
    },
    'contributor': {
        'label_he': 'Contributor', 'description_he': 'You give to the world. Your giving strengthens the bond in the field.',
        'dominant_direction': 'contribution', 'threshold': 35,
        'strengthening_actions_he': ['Help someone', 'Share knowledge', 'Listen to a friend']
    },
    'regenerator': {
        'label_he': 'Regenerator', 'description_he': 'You build the inner foundation. Your recovery stabilizes the field.',
        'dominant_direction': 'recovery', 'threshold': 35,
        'strengthening_actions_he': ['Take a break', 'Get proper sleep', 'Go for a walk']
    },
    'social_connector': {
        'label_he': 'Social Connector', 'description_he': 'You bridge people and directions. Your presence unifies the field.',
        'dominant_direction': None, 'threshold': 20,
        'strengthening_actions_he': ['Invite a friend', 'Join a collective mission', 'Share your orientation']
    },
    'deep_thinker': {
        'label_he': 'Deep Thinker', 'description_he': 'You balance all directions. Your depth enriches the field.',
        'dominant_direction': None, 'threshold': 20,
        'strengthening_actions_he': ['Consider your steps', 'Revisit an old decision', 'Write down an insight']
    }
}

BADGES = [
    {'id': 'first_action', 'label_he': 'First Step', 'desc_he': 'You performed your first action', 'condition': lambda p: p.get('total_actions', 0) >= 1},
    {'id': 'first_globe_point', 'label_he': 'Field Point', 'desc_he': 'You sent a point to the globe', 'condition': lambda p: p.get('globe_points', 0) >= 1},
    {'id': 'streak_3', 'label_he': '3-Day Streak', 'desc_he': 'You maintained a 3-day streak', 'condition': lambda p: p.get('current_streak', 0) >= 3},
    {'id': 'streak_7', 'label_he': 'Weekly Presence', 'desc_he': '7 consecutive days in the field', 'condition': lambda p: p.get('current_streak', 0) >= 7},
    {'id': 'streak_30', 'label_he': 'Monthly Presence', 'desc_he': '30 consecutive days', 'condition': lambda p: p.get('current_streak', 0) >= 30},
    {'id': 'actions_10', 'label_he': 'Active', 'desc_he': '10 actions', 'condition': lambda p: p.get('total_actions', 0) >= 10},
    {'id': 'actions_50', 'label_he': 'Committed', 'desc_he': '50 actions', 'condition': lambda p: p.get('total_actions', 0) >= 50},
    {'id': 'actions_100', 'label_he': 'Regular Contributor', 'desc_he': '100 actions', 'condition': lambda p: p.get('total_actions', 0) >= 100},
    {'id': 'all_directions', 'label_he': 'Multi-directional', 'desc_he': 'You acted in all 4 directions', 'condition': lambda p: all(p.get('dir_counts', {}).get(d, 0) > 0 for d in ['contribution', 'recovery', 'order', 'exploration'])},
    {'id': 'niche_found', 'label_he': 'Found Your Niche', 'desc_he': 'Your niche has been identified', 'condition': lambda p: p.get('dominant_niche') is not None},
]

SUBSCRIPTION_PLANS = {
    'free': {'label_he': 'Free', 'price': 0.0, 'features_he': ['Daily Orientation', 'Basic Compass', 'Globe', 'Community'], 'limits': {'feed_cards': 5, 'value_detail': False, 'niche_insights': False, 'weekly_report': False, 'globe_regions': 3}},
    'plus': {'label_he': 'Plus', 'price': 9.99, 'features_he': ['All Free Features', 'Full Personalized Feed', 'Full Value Analytics', 'In-depth Weekly Report', 'Niche Insights'], 'limits': {'feed_cards': 50, 'value_detail': True, 'niche_insights': True, 'weekly_report': True, 'globe_regions': 20}},
    'collective': {'label_he': 'Collective', 'price': 24.99, 'features_he': ['All Plus Features', 'Private Circles', 'Premium Globe Insights', 'Extended Profile', 'Full Niche Progress'], 'limits': {'feed_cards': -1, 'value_detail': True, 'niche_insights': True, 'weekly_report': True, 'globe_regions': -1}}
}

FEED_ACTIONS_HE = ['Organized my work environment', 'Helped a friend', 'Learned a new topic', 'Took a break', 'Planned the week', 'Shared knowledge', 'Tried a different approach', 'Slept 8 hours', 'Wrote a goals list', 'Met a new person', 'Volunteered in the community', 'Went for a nature walk', 'Read an article', 'Listened to someone', 'Set priorities']
FEED_QUESTIONS_HE = ['What force guides you today?', 'What is your next step?', 'What did you learn about yourself this week?', 'Where do you feel stuck?', 'What would you like to change tomorrow?']
FEED_REFLECTIONS_HE = ['I noticed my direction was mostly inward. Need to balance.', 'The global field is moving towards contribution — maybe it is time to join.', 'I discovered that order helps me more than I thought.', 'Recovery was the most important this week.']

CIRCLE_DEFS = {
    'builders_of_order': {'label_he': 'Builders of Order', 'direction': 'order', 'color': '#6366f1', 'desc_he': 'A community of people who create structure and stability in the field.'},
    'explorers': {'label_he': 'Explorers', 'direction': 'exploration', 'color': '#f59e0b', 'desc_he': 'A community of curious minds who expand the boundaries of the field.'},
    'contributors': {'label_he': 'Contributors', 'direction': 'contribution', 'color': '#22c55e', 'desc_he': 'A community of givers who strengthen the bond in the field.'},
    'regenerators': {'label_he': 'Regenerators', 'direction': 'recovery', 'color': '#3b82f6', 'desc_he': 'A community of people who stabilize the inner foundation.'},
    'social_connectors': {'label_he': 'Social Connectors', 'direction': None, 'color': '#ec4899', 'desc_he': 'A community of bridges who unite different directions.'},
    'deep_thinkers': {'label_he': 'Deep Thinkers', 'direction': None, 'color': '#8b5cf6', 'desc_he': 'A community of people who balance all directions.'}
}

COMPASS_SUGGESTIONS = {
    'order': {'weak': 'exploration', 'suggestion_he': 'Try learning something completely new today — step out of your usual structure.'},
    'exploration': {'weak': 'order', 'suggestion_he': 'Give structure to what you discovered — write a list or plan the next step.'},
    'contribution': {'weak': 'recovery', 'suggestion_he': 'Take time for yourself today — even givers need to recharge.'},
    'recovery': {'weak': 'contribution', 'suggestion_he': 'Do something small for someone else — giving strengthens after recovery.'}
}

ACTION_MEANINGS = {
    'contribution': {
        'personal_he': 'An action that expands your presence beyond yourself',
        'social_he': 'Strengthening social bonds — giving that connects people',
        'value_he': 'The value of contribution — the world is built from acts of giving',
        'system_he': 'Contribution force in the field — increases collective direction'
    },
    'recovery': {
        'personal_he': 'An action that strengthens your inner foundation',
        'social_he': 'A model of self-care — showing others that it is okay to stop',
        'value_he': 'The value of recovery — building requires rest',
        'system_he': 'Balancing force in the field — inner stability that radiates outward'
    },
    'order': {
        'personal_he': 'An action that creates structure and clarity in your life',
        'social_he': 'Contributing to framework — personal order impacts the environment',
        'value_he': 'The value of order — stability as a foundation for growth',
        'system_he': 'Organizing force in the field — increases global stability'
    },
    'exploration': {
        'personal_he': 'An action that opens new doors in your world',
        'social_he': 'Expanding horizons — curiosity that invites others to discover',
        'value_he': 'The value of exploration — discovery as a driver of change',
        'system_he': 'Expansion force in the field — increases the map of possibilities'
    }
}

DEMO_COUNTRIES = [
    ("Brazil", "BR"), ("India", "IN"), ("Germany", "DE"), ("USA", "US"),
    ("Japan", "JP"), ("Nigeria", "NG"), ("Israel", "IL"), ("France", "FR"),
    ("Australia", "AU"), ("South Korea", "KR"), ("Mexico", "MX"), ("UK", "GB"),
    ("Canada", "CA"), ("Italy", "IT"), ("Spain", "ES"), ("Argentina", "AR"),
    ("Turkey", "TR"), ("Thailand", "TH"), ("Poland", "PL"), ("Netherlands", "NL")
]

DEMO_ALIASES = [
    "Atlas", "Nova", "Sage", "Drift", "Ember", "Coral", "Zenith", "Flux",
    "Prism", "Echo", "Nimbus", "Pulse", "Aether", "Crest", "Dusk", "Fern",
    "Glint", "Haven", "Iris", "Jade", "Kite", "Lumen", "Mist", "Nest",
    "Opal", "Pine", "Quill", "Reef", "Spark", "Thorn", "Ursa", "Vale",
    "Wren", "Zephyr", "Amber", "Brook", "Cedar", "Dawn", "Elm", "Frost",
    "Grove", "Haze", "Ivy", "Jet", "Kelp", "Lark", "Moss", "Nyx",
    "Orion", "Peak"
]

DIRECTIONS = ['contribution', 'recovery', 'order', 'exploration']
