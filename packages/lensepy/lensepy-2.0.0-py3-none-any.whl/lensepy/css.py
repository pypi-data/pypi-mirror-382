
#### Style Sheet for LEnsE API

# Colors
# ------
BLUE_IOGS = '#0A3250'
ORANGE_IOGS = '#FF960A'
GREEN_IOGS = (0, 180, 0)
RED_IOGS = (200, 0, 0)
WHITE = '#000000'
GRAY = '#727272'
BLACK = '#FFFFFF'

# Styles
# ------
styleH1 = f"font-size:18px; padding:0px; color:{BLUE_IOGS};font-weight: bold;"
styleH2 = f"font-size:16px; padding:0px; color:{BLUE_IOGS}; font-weight: bold;"
styleH3 = f"font-size:14px; padding:0px; color:{BLUE_IOGS};"
styleCheckbox = f"font-size: 14px; padding: 3px; color: {BLUE_IOGS}; font-weight: normal;"
no_style = f"background-color:{GRAY}; color:{BLACK}; font-size:14px;"

disabled_button = f"background-color:{GRAY}; color:{BLACK}; font-size:14px; border-radius: 10px;"
unactived_button = f"background-color:{BLUE_IOGS}; color:white; font-size:14px; font-weight:bold; border-radius: 10px;"
actived_button = f"background-color:{ORANGE_IOGS}; color:white; font-size:14px; font-weight:bold; border-radius: 10px;"

BUTTON_HEIGHT = 37 #px
OPTIONS_BUTTON_HEIGHT = 18 #pxn = f"background-color:{ORANGE_IOGS}; color:white; font-size:15px; font-weight:bold;
# border-radius: 10px;"


StyleSheet = '''
#IOGSProgressBar {
    text-align: center;
    color: white;
    width: 10px; 
    min-height: 16px;
    max-height: 16px;
    border-radius: 6px;
}
#IOGSProgressBar::chunk {
    border-radius: 6px;
    background-color: #FF960A;
}
'''