def subuh(lat,long,ele,tz,y,m,d):
  from datetime import datetime, timedelta, date
  from skyfield.api import load, wgs84
  from skyfield import almanac
  import numpy as np

  # -------- Settings --------
  lat_location = lat
  long_location = long
  ele = ele
  timezone = tz                 # UTC+8 (Malaysia)
  year = y
  month = m
  day = d

  the_day = date(year, month, day)

  target_alt_deg = -17.99       # e.g., astronomical twilight
  tolerance_alt = 0.01          # ± degrees around target altitude


  # -------- Skyfield setup --------
  ts = load.timescale()
  eph = load('de440s.bsp')
  earth, sun = eph['earth'], eph['sun']
  location = earth + wgs84.latlon(lat_location, long_location, elevation_m=ele)

  def make_altitude_predicate(target_alt_deg: float, tolerance_alt: float):
    """True when Sun altitude is within [target - tol, target + tol]."""
    lo = target_alt_deg - tolerance_alt
    hi = target_alt_deg + tolerance_alt

    def in_alt_band(t):
        alt, az, _ = location.at(t).observe(sun).apparent().altaz()
        return (alt.degrees >= lo) & (alt.degrees <= hi)

    # hints for Skyfield’s search
    in_alt_band.step_days = 0.00001     
    in_alt_band.rough_period = 0.5    # ≈12 h between crossings
    return in_alt_band

  pred = make_altitude_predicate(target_alt_deg, tolerance_alt)

  def local_from_utc(dt_utc):
    return dt_utc + timedelta(hours=timezone)

  def sun_altitude_intervals_for_day(d: date):
    """Return [(entry_time_utc, exit_time_utc)] for one local day where altitude is in band."""
    t0 = ts.utc(year, month, day, 0 - timezone, 0, 0)
    t1 = ts.utc(year, month, day, 12 - timezone, 0, 0)

    times, states = almanac.find_discrete(t0, t1, pred)
    intervals = []

    # if we start inside True state, prepend opening time
    is_true_at_start = bool(pred(t0)) if np.isscalar(pred(t0)) else bool(pred(t0).any())
    if is_true_at_start:
        times = ts.tt_jd(np.insert(times.tt, 0, t0.tt))
        states = np.insert(states, 0, True)

    # build [entry, exit) pairs for True segments
    for i in range(len(times) - 1):
        if states[i]:
            intervals.append((times[i], times[i + 1]))

    # if last state continues to t1
    if len(times) > 0 and states[-1]:
        intervals.append((times[-1], t1))

    return intervals

  # -------- Run for one day --------
  intervals = sun_altitude_intervals_for_day(the_day)

  #print(f"Sun altitude windows for {the_day.isoformat()} (local UTC{timezone:+d}), "
  #    f"alt ≈ {target_alt_deg}° ±{tolerance_alt}°")

  if not intervals:
    print("  — none —")
  else:
    for idx, (entry, exit_) in enumerate(intervals, start=1):
        utc_entry = entry.utc_datetime()
        utc_exit  = exit_.utc_datetime()
        loc_entry = local_from_utc(utc_entry)
        loc_exit  = local_from_utc(utc_exit)
        duration_min = (utc_exit - utc_entry).total_seconds() / 60.0

        # optional: altitude & azimuth at entry
        alt_e, az_e, _ = location.at(entry).observe(sun).apparent().altaz()

  #      print(f"  #{idx}: {loc_entry.strftime('%H:%M:%S')} → {loc_exit.strftime('%H:%M:%S')}"
   #           f"  | duration: {duration_min:.2f} min"
   #           f"  | alt_entry: {alt_e.degrees:.2f}°  az: {az_e.degrees:.2f}°")
        z=loc_entry.strftime('%H:%M:%S')
  return z

def syuruk(lat,long,ele,tz,y,m,d):
  from datetime import datetime, timedelta, date
  from skyfield.api import load, wgs84
  from skyfield import almanac
  import numpy as np

  # -------- Settings --------
  lat_location = lat
  long_location = long
  ele = ele
  timezone = tz                 # UTC+8 (Malaysia)
  year = y
  month = m
  day = d

  ts = load.timescale()
  eph = load('de440s.bsp')
  planets = load('de440s.bsp')
  earth = planets['earth']
  sun = planets['sun']
  location = earth + wgs84.latlon(lat_location, long_location, elevation_m=ele)

  t0 = ts.utc(year, month, day-1)
  t1 = ts.utc(year, month, day)

  from skyfield.units import Angle
  from numpy import arccos
  from skyfield.earthlib import refraction

  altitude_m = ele
  earth_radius_m = 6378136.6
  side_over_hypotenuse = earth_radius_m / (earth_radius_m + altitude_m)
  h = Angle(radians=-arccos(side_over_hypotenuse))
  solar_radius_degrees = 16 / 60
  r = refraction(0.0, temperature_C=15.0, pressure_mbar=1030.0)

  t, y = almanac.find_risings(location, sun, t0, t1, horizon_degrees=-r + h.degrees - solar_radius_degrees)
  h, m, s = t.utc.hour, t.utc.minute, t.utc.second
  syuruk_time = float(np.array(h).item() + np.array(m).item()/60 + np.array(s).item()/3600 + timezone)
  syuruk_time %= 24  # Ensure 24-hour clock format

  syuruk_time = float(syuruk_time)
  degrees = int(syuruk_time)
  decimal_part = syuruk_time  - degrees
  minutes_total = decimal_part * 60
  minutes = int(minutes_total)
  seconds = round((minutes_total - minutes) * 60)
  sun_astro = location.at(ts.utc(year, month, day, h, m, s)).observe(sun)
  sun_alt, _, _ = sun_astro.apparent().altaz()
  sun_alt, _, _ = sun_astro.apparent().altaz()
  if sun_alt.degrees >= 0:
      syuruk = "Syuruk Does Not Occur"
  else:
      syuruk = f"{degrees}:{minutes}:{seconds}"

  return syuruk

def zuhur(lat,long,ele,tz,y,m,d):
  from datetime import datetime, timedelta, date
  from skyfield.api import load, wgs84
  from skyfield import almanac
  import numpy as np

  # -------- Settings --------
  lat_location = lat
  long_location = long
  ele = ele
  timezone = tz                 # UTC+8 (Malaysia)
  year = y
  month = m
  day = d

  ts = load.timescale()
  eph = load('de440s.bsp')
  planets = load('de440s.bsp')
  earth = planets['earth']
  sun = planets['sun']
  location = earth + wgs84.latlon(lat_location, long_location, elevation_m=ele)

  t0 = ts.utc(year, month, day-1)
  t1 = ts.utc(year, month, day)

  from skyfield.units import Angle
  from numpy import arccos
  from skyfield.earthlib import refraction

  t = almanac.find_transits(location, sun, t0, t1)
  h = t.utc.hour
  m = t.utc.minute
  s = t.utc.second

  #print(hour_solar_transit)
  #print(minutes_solar_transit )
  #print(second_solar_transit)
  #zuhur_time = hour_solar_transit + (minutes_solar_transit / 60) + (second_solar_transit / 3600 ) + timezone + 0.017778
  zuhur_time = float(np.array(h).item() + np.array(m).item()/60 + np.array(s).item()/3600 + timezone+ 0.017778)


  zuhur_time = float(zuhur_time)
  degrees = int(zuhur_time )
  decimal_part = zuhur_time  - degrees
  minutes_total = decimal_part * 60
  minutes = int(minutes_total)

  seconds = round((minutes_total - minutes) * 60)
  #print(f"{degrees}° {minutes}′ {seconds}″")

  sun_astro = location.at(ts.utc(year, month, day, h, m, s)).observe(sun)
  sun_alt, _, _ = sun_astro.apparent().altaz()
  alt_deg = float(np.atleast_1d(sun_alt.degrees)[0])   # <- force scalar

  # Check if the sun is above the horizon at zuhur time
  if sun_alt.degrees <= 0:
      zuhur = "Zuhur Does Not Occur"
  else:
      zuhur = f"{degrees}:{minutes}:{seconds}"
  altitude_zuhur = alt_deg

  return zuhur,altitude_zuhur

def asar(lat,long,ele,tz,y,m,d):
  from datetime import datetime, timedelta, date
  from skyfield.api import load, wgs84
  from skyfield import almanac
  import numpy as np
  import math

  # -------- Settings --------
  lat_location = lat
  long_location = long
  ele = ele
  timezone = tz                 # UTC+8 (Malaysia)
  year = y
  month = m
  day = d

  the_day = date(year, month, day)

  _, altitude_zuhur = zuhur(lat,long,ele,tz,y,m,d)

    # Noon shadow and Asar target altitude
  s0 = 1.0 / math.tan(math.radians(altitude_zuhur))
  h_asar = math.degrees(math.atan(1.0 / (1.0 + s0))) 

  target_alt_deg = h_asar       # angle asar
  tolerance_alt = 0.01          # ± degrees around target altitude


  # -------- Skyfield setup --------
  ts = load.timescale()
  eph = load('de440s.bsp')
  earth, sun = eph['earth'], eph['sun']
  location = earth + wgs84.latlon(lat_location, long_location, elevation_m=ele)

  def make_altitude_predicate(target_alt_deg: float, tolerance_alt: float):
    """True when Sun altitude is within [target - tol, target + tol]."""
    lo = target_alt_deg - tolerance_alt
    hi = target_alt_deg + tolerance_alt

    def in_alt_band(t):
        alt, az, _ = location.at(t).observe(sun).apparent().altaz()
        return (alt.degrees >= lo) & (alt.degrees <= hi)

    # hints for Skyfield’s search
    in_alt_band.step_days = 0.00001     
    in_alt_band.rough_period = 0.5    # ≈12 h between crossings
    return in_alt_band

  pred = make_altitude_predicate(target_alt_deg, tolerance_alt)

  def local_from_utc(dt_utc):
    return dt_utc + timedelta(hours=timezone)

  def sun_altitude_intervals_for_day(d: date):
    """Return [(entry_time_utc, exit_time_utc)] for one local day where altitude is in band."""
    t0 = ts.utc(year, month, day, 12 - timezone, 0, 0)
    t1 = ts.utc(year, month, day, 24 - timezone, 0, 0)

    times, states = almanac.find_discrete(t0, t1, pred)
    intervals = []

    # if we start inside True state, prepend opening time
    is_true_at_start = bool(pred(t0)) if np.isscalar(pred(t0)) else bool(pred(t0).any())
    if is_true_at_start:
        times = ts.tt_jd(np.insert(times.tt, 0, t0.tt))
        states = np.insert(states, 0, True)

    # build [entry, exit) pairs for True segments
    for i in range(len(times) - 1):
        if states[i]:
            intervals.append((times[i], times[i + 1]))

    # if last state continues to t1
    if len(times) > 0 and states[-1]:
        intervals.append((times[-1], t1))

    return intervals

  # -------- Run for one day --------
  intervals = sun_altitude_intervals_for_day(the_day)

  #print(f"Sun altitude windows for {the_day.isoformat()} (local UTC{timezone:+d}), "
  #    f"alt ≈ {target_alt_deg}° ±{tolerance_alt}°")

  if not intervals:
    print("  — none —")
  else:
    for idx, (entry, exit_) in enumerate(intervals, start=1):
        utc_entry = entry.utc_datetime()
        utc_exit  = exit_.utc_datetime()
        loc_entry = local_from_utc(utc_entry)
        loc_exit  = local_from_utc(utc_exit)
        duration_min = (utc_exit - utc_entry).total_seconds() / 60.0

        # optional: altitude & azimuth at entry
        alt_e, az_e, _ = location.at(entry).observe(sun).apparent().altaz()

   #     print(f"  #{idx}: {loc_entry.strftime('%H:%M:%S')} → {loc_exit.strftime('%H:%M:%S')}"
   #           f"  | duration: {duration_min:.2f} min"
   #           f"  | alt_entry: {alt_e.degrees:.2f}°  az: {az_e.degrees:.2f}°")
        z=loc_entry.strftime('%H:%M:%S')
  return z

def maghrib(lat,long,ele,tz,y,m,d):
  from datetime import datetime, timedelta, date
  from skyfield.api import load, wgs84
  from skyfield import almanac
  import numpy as np

  # -------- Settings --------
  lat_location = lat
  long_location = long
  ele = ele
  timezone = tz                 # UTC+8 (Malaysia)
  year = y
  month = m
  day = d

  ts = load.timescale()
  eph = load('de440s.bsp')
  planets = load('de440s.bsp')
  earth = planets['earth']
  sun = planets['sun']
  location = earth + wgs84.latlon(lat_location, long_location, elevation_m=ele)

  t0 = ts.utc(year, month, day-1)
  t1 = ts.utc(year, month, day)

  from skyfield.units import Angle
  from numpy import arccos
  from skyfield.earthlib import refraction

  altitude_m = ele
  earth_radius_m = 6378136.6
  side_over_hypotenuse = earth_radius_m / (earth_radius_m + altitude_m)
  h = Angle(radians=-arccos(side_over_hypotenuse))
  solar_radius_degrees = 16 / 60
  r = refraction(0.0, temperature_C=15.0, pressure_mbar=1030.0)

  t, y = almanac.find_settings(location, sun, t0, t1, horizon_degrees=-r + h.degrees - solar_radius_degrees)
  h, m, s = t.utc.hour, t.utc.minute, t.utc.second
  maghrib_time = float(np.array(h).item() + np.array(m).item()/60 + np.array(s).item()/3600 + timezone)
  maghrib_time %= 24  # Ensure 24-hour clock format

  maghrib_time = float(maghrib_time)
  degrees = int(maghrib_time)
  decimal_part = maghrib_time  - degrees
  minutes_total = decimal_part * 60
  minutes = int(minutes_total)
  seconds = round((minutes_total - minutes) * 60)
  sun_astro = location.at(ts.utc(year, month, day, h, m, s)).observe(sun)
  sun_alt, _, _ = sun_astro.apparent().altaz()
  sun_alt, _, _ = sun_astro.apparent().altaz()
  if sun_alt.degrees >= 0:
      maghrib = "Maghrib Does Not Occur"
  else:
      maghrib = f"{degrees}:{minutes}:{seconds}"

  return maghrib

def isyak(lat,long,ele,tz,y,m,d):
  from datetime import datetime, timedelta, date
  from skyfield.api import load, wgs84
  from skyfield import almanac
  import numpy as np

  # -------- Settings --------
  lat_location = lat
  long_location = long
  ele = ele
  timezone = tz                 # UTC+8 (Malaysia)
  year = y
  month = m
  day = d

  the_day = date(year, month, day)

  target_alt_deg = -17.99       # e.g., astronomical twilight
  tolerance_alt = 0.01          # ± degrees around target altitude


  # -------- Skyfield setup --------
  ts = load.timescale()
  eph = load('de440s.bsp')
  earth, sun = eph['earth'], eph['sun']
  location = earth + wgs84.latlon(lat_location, long_location, elevation_m=ele)

  def make_altitude_predicate(target_alt_deg: float, tolerance_alt: float):
    """True when Sun altitude is within [target - tol, target + tol]."""
    lo = target_alt_deg - tolerance_alt
    hi = target_alt_deg + tolerance_alt

    def in_alt_band(t):
        alt, az, _ = location.at(t).observe(sun).apparent().altaz()
        return (alt.degrees >= lo) & (alt.degrees <= hi)

    # hints for Skyfield’s search
    in_alt_band.step_days = 0.00001     
    in_alt_band.rough_period = 0.5    # ≈12 h between crossings
    return in_alt_band

  pred = make_altitude_predicate(target_alt_deg, tolerance_alt)

  def local_from_utc(dt_utc):
    return dt_utc + timedelta(hours=timezone)

  def sun_altitude_intervals_for_day(d: date):
    """Return [(entry_time_utc, exit_time_utc)] for one local day where altitude is in band."""
    t0 = ts.utc(year, month, day, 12 - timezone, 0, 0)
    t1 = ts.utc(year, month, day, 24 - timezone, 0, 0)

    times, states = almanac.find_discrete(t0, t1, pred)
    intervals = []

    # if we start inside True state, prepend opening time
    is_true_at_start = bool(pred(t0)) if np.isscalar(pred(t0)) else bool(pred(t0).any())
    if is_true_at_start:
        times = ts.tt_jd(np.insert(times.tt, 0, t0.tt))
        states = np.insert(states, 0, True)

    # build [entry, exit) pairs for True segments
    for i in range(len(times) - 1):
        if states[i]:
            intervals.append((times[i], times[i + 1]))

    # if last state continues to t1
    if len(times) > 0 and states[-1]:
        intervals.append((times[-1], t1))

    return intervals

  # -------- Run for one day --------
  intervals = sun_altitude_intervals_for_day(the_day)

 # print(f"Sun altitude windows for {the_day.isoformat()} (local UTC{timezone:+d}), "
  #    f"alt ≈ {target_alt_deg}° ±{tolerance_alt}°")

  if not intervals:
    print("  — none —")
  else:
    for idx, (entry, exit_) in enumerate(intervals, start=1):
        utc_entry = entry.utc_datetime()
        utc_exit  = exit_.utc_datetime()
        loc_entry = local_from_utc(utc_entry)
        loc_exit  = local_from_utc(utc_exit)
        duration_min = (utc_exit - utc_entry).total_seconds() / 60.0

        # optional: altitude & azimuth at entry
        alt_e, az_e, _ = location.at(entry).observe(sun).apparent().altaz()

   #     print(f"  #{idx}: {loc_entry.strftime('%H:%M:%S')} → {loc_exit.strftime('%H:%M:%S')}"
   #           f"  | duration: {duration_min:.2f} min"
   #           f"  | alt_entry: {alt_e.degrees:.2f}°  az: {az_e.degrees:.2f}°")
        z=loc_entry.strftime('%H:%M:%S')
  return z



def singleday(lat, lon, ele, tz, y, m, d, csv_filename="prayer_times.csv"):

    import csv
    from datetime import date
    """
    Generate prayer times for one date, print as table, and also save as CSV.
    """
    # --- get each prayer time ---
    subuh_time    = subuh(lat, lon, ele, tz, y, m, d)
    syuruk_time   = syuruk(lat, lon, ele, tz, y, m, d)
    zuhur_time, _ = zuhur(lat, lon, ele, tz, y, m, d)
    asar_time     = asar(lat, lon, ele, tz, y, m, d)
    maghrib_time  = maghrib(lat, lon, ele, tz, y, m, d)
    isyak_time    = isyak(lat, lon, ele, tz, y, m, d)

    # --- Prepare data row ---
    date_str = date(y, m, d).strftime("%Y-%m-%d")
    header = ["Date", "Subuh", "Syuruk", "Zuhur", "Asar", "Maghrib", "Isyak"]
    row = [date_str, subuh_time, syuruk_time, zuhur_time, asar_time, maghrib_time, isyak_time]

    # --- Print table to screen ---
    print("\n+------------+----------+----------+----------+----------+----------+----------+")
    print("|    Date    |  Subuh   |  Syuruk  |  Zuhur   |   Asar   | Maghrib  |  Isyak   |")
    print("+------------+----------+----------+----------+----------+----------+----------+")
    print(f"| {date_str} | {subuh_time:8} | {syuruk_time:8} | {zuhur_time:8} | "
          f"{asar_time:8} | {maghrib_time:8} | {isyak_time:8} |")
    print("+------------+----------+----------+----------+----------+----------+----------+")

    # --- Write to CSV file ---
    with open(csv_filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow(row)

    print(f"\n✅ Saved to CSV file: {csv_filename}")





