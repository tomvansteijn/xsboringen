# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

LABELS = iter('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
IMAGEFILEFORMAT = 'cross_section_{label:}.png'

# default figure size (width, height) [inch]
FIGSIZE = 21, 11.7

# default plot barwidth factor times cross-section length
PLOT_BARWIDTH = 1.5e-2

# plotting styles
STYLES = {
    'attrs': ('lithology', 'sandmedianclass'),
    'records':
        {'key': ('G',), 'label': 'grind', 'color': 'coral', 'hatch': '', 'edgecolor': 'black'},
        {'key': ('K',), 'label': 'klei', 'color': 'forestgreen', 'hatch': '', 'edgecolor': 'black'},
        {'key': ('L',), 'label': 'leem', 'color': 'darkkhaki', 'hatch': '', 'edgecolor': 'black'},
        {'key': ('V',), 'label': 'veen', 'color': 'sienna', 'hatch': '', 'edgecolor': 'black'},
        {'key': ('Z',), 'label': 'zand geen mediaan', 'color': '#FFFF66', 'hatch': '', 'edgecolor': 'black'},
        {'key': ('Z', 'ZMO'), 'label':'zand onduidelijke mediaan', 'color':'lightgray', 'hatch': '...', 'edgecolor': 'black'},
        {'key': ('Z', 'ZFC'), 'label':'zand fijne categorie', 'color': '#FFFF66', 'hatch': '...', 'edgecolor': 'black'},
        {'key': ('Z', 'ZMC'), 'label':'zand middencategorie', 'color':'gold', 'hatch': '...', 'edgecolor': 'black'},
        {'key': ('Z', 'ZGC'), 'label':'zand grove categorie', 'color':'orange', 'hatch': '...', 'edgecolor': 'black'},
        {'key': ('Z', 'GCZ'), 'label':'glauconietzand', 'color':'mediumseagreen', 'hatch': '...', 'edgecolor': 'black'},
    'default': {'color': 'white', 'hatch': '', 'label': 'onbekend', 'edgecolor': 'black'},
    }

