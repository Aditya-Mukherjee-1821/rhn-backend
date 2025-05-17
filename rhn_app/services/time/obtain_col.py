from datetime import datetime
import pytz

def obtain_time_and_col():
    # Define Finland's timezone
    finland_tz = pytz.timezone('Europe/Helsinki')

    # Get current time in Finland
    finland_time = datetime.now(finland_tz)

    if finland_time.hour == 23:
        return 8
    col = finland_time.hour + 9

    return col  

