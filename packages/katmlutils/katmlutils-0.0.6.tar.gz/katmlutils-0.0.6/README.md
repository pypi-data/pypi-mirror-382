# SARAO Machine Learning Utility functions 

Machine Learning utils is a library for a convenient experience. It consists of helper functions for creating astronomy/machine learning tools.

## Installation 

```
pip install katmlutils

```

## Example 1

```
from katmlutils.utils import get_night_window
from datetime import datetime

# Get the night window for the proposed date
nightwindow = get_night_window(datetime.datetime.now())

nightwindow
```

## Example 2

```
from katmlutils.utils import get_UTC_sunrise_sunset_times
from datetime import datetime

date = datetime.today()

num_days = 7
sunrise_sunset_times = get_UTC_sunrise_sunset_times(date, num_days)
for entry in sunrise_sunset_times:
    print(
        f"Date: {entry['date']}, Sunrise: {entry['sunrise']}, Sunset: {entry['sunset']}"
    )
```
## Example 3 

```
from katmlutils.utils import SKA_LATITUDE, SKA_LONGITUDE, MINUTES_IN_SIDEREAL_DAY, MINUTES_IN_SOLAR_DAY

print(f"SKA Latitude: {SKA_LATITUDE} degrees")
print(f"SKA Longitude: {SKA_LONGITUDE} degrees") 
print(f"Minutes in Sidereal Day: {MINUTES_IN_SIDEREAL_DAY}")
print(f"Minutes in Solar Day: {MINUTES_IN_SOLAR_DAY}")

```

## Example 4

```
from katmlutils.utils import SKA_LONGITUDE, lst_to_utc
from datetime import datetime

date = datetime.now()

# Example Usage of lst_to_utc function with float input
lst_time = 1 + 59 / 60 + 0 / 3600
utc_time = lst_to_utc(date, lst_time, SKA_LONGITUDE)
print(f"UTC Time: {int(utc_time)}:{int((utc_time % 1) * 60):02}")

# Example Usage of lst_to_utc function with time input
lst_time = time(12, 30, 45)
utc_time = lst_to_utc(date, lst_time, SKA_LONGITUDE)
print(f"UTC Time: {utc_time}")

```