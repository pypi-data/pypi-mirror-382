def observedata(lat, lon, ele, tz, year, m, d, csv_filename="crescent_data.csv"):
    from datetime import date, timedelta
    import csv
    from skyfield.api import load, wgs84
    from skyfield import almanac
    from skyfield.units import Angle
    from skyfield.earthlib import refraction
    from numpy import arccos

    ts = load.timescale()
    eph = load('de440s.bsp')
    earth, sun, moon = eph['earth'], eph['sun'], eph['moon']

    # Observer (works across Skyfield versions)
    try:
        location = wgs84.latlon(lat, lon, elevation_m=ele, center=earth)
    except TypeError:
        location = earth + wgs84.latlon(lat, lon, elevation_m=ele)

    # Local-day window in UTC
    t0 = ts.utc(year, m, d, 0 - tz, 0, 0)
    t1 = ts.utc(year, m, d, 24 - tz, 0, 0)

    # Apparent horizon for upper-limb sunset, with height & refraction
    earth_radius_m = 6378136.6
    side_over_hyp = earth_radius_m / (earth_radius_m + ele)
    h_geom = Angle(radians=-arccos(side_over_hyp))           # dip from observer height
    r = refraction(0.0, temperature_C=15.0, pressure_mbar=1013.25)
    solar_radius_deg = 16/60
    horizon_deg = -r + h_geom.degrees - solar_radius_deg

    # Sunset within the local-day window
    set_times_sun, _ = almanac.find_settings(location, sun, t0, t1, horizon_degrees=horizon_deg)
    if len(set_times_sun) == 0:
        raise RuntimeError("No sunset found in this local-day window.")
    t_sunset = set_times_sun[0]
    dt_sunset_local = t_sunset.utc_datetime() + timedelta(hours=tz)
    sunset_str = dt_sunset_local.strftime("%H:%M:%S")

    # Moonset within the local-day window (may be missing)
    set_times_moon, _ = almanac.find_settings(location, moon, t0, t1, horizon_degrees=horizon_deg)
    if len(set_times_moon) == 0:
        t_moonset = None
        moonset_str = "—"
        lag_str = "—"
    else:
        t_moonset = set_times_moon[0]
        dt_moonset_local = t_moonset.utc_datetime() + timedelta(hours=tz)
        moonset_str = dt_moonset_local.strftime("%H:%M:%S")

        # Lag = moonset - sunset (ensure positive same-evening)
        lag_td = (t_moonset.utc_datetime() - t_sunset.utc_datetime())
        if lag_td.total_seconds() < 0:
            lag_td += timedelta(days=1)
        hh = int(lag_td.total_seconds() // 3600)
        mm = int((lag_td.total_seconds() % 3600) // 60)
        ss = int(lag_td.total_seconds() % 60)
        lag_str = f"{hh:02d}:{mm:02d}:{ss:02d}"

    # Alt/Az at actual sunset
    alt_moon, az_moon, _ = location.at(t_sunset).observe(moon).apparent().altaz()
    alt_sun,  az_sun,  _ = location.at(t_sunset).observe(sun).apparent().altaz()

    moon_alt_deg = float(alt_moon.degrees)
    daz_deg = abs(float(az_moon.degrees) - float(az_sun.degrees))
    arcv_deg = abs(moon_alt_deg - float(alt_sun.degrees))    # Arc of Vision
    arcl_deg = float(
        location.at(t_sunset).observe(sun).apparent()
        .separation_from(location.at(t_sunset).observe(moon).apparent()).degrees
    )  # Arc of Light

    # Moon age at sunset: (JD_sunset - JD_conjunction_before)*24
    jd_sunset = t_sunset.tt
    # Search ±5 days around date; pick last conjunction BEFORE sunset
    t0c = ts.utc(year, m, d - 5)
    t1c = ts.utc(year, m, d + 5)
    oc_func = almanac.oppositions_conjunctions(eph, eph['Moon'])
    times_oc, events_oc = almanac.find_discrete(t0c, t1c, oc_func)
    jd_conj = None
    for ti, ei in zip(times_oc, events_oc):
        if ei == 1 and ti.tt <= jd_sunset:  # 1 = conjunction
            jd_conj = ti.tt
    moon_age_hours = (jd_sunset - jd_conj) * 24.0 if jd_conj is not None else float('nan')

    # Build row
    date_str = date(year, m, d).strftime("%Y-%m-%d")
    header = ["Date", "Sunset", "Moonset", "Lag Time", "Moon Age", "Moon Alt", "DAZ", "ArcV", "ArcL"]
    row = [
        date_str,
        sunset_str,
        moonset_str,
        lag_str,
        f"{moon_age_hours:.2f}",
        f"{moon_alt_deg:.2f}",
        f"{daz_deg:.2f}",
        f"{arcv_deg:.2f}",
        f"{arcl_deg:.2f}",
    ]

    # Pretty print
    print("\n+------------+----------+----------+----------+----------+----------+----------+----------+----------+")
    print("|    Date    |  Sunset  |  Moonset | LagTime  | MoonAge  | MoonAlt  |   DAZ    |   ArcV   |   ArcL   |")
    print("+------------+----------+----------+----------+----------+----------+----------+----------+----------+")
    print(f"| {date_str} | {sunset_str:8} | {moonset_str:8} | {lag_str:8} | "
          f"{moon_age_hours:8.2f} | {moon_alt_deg:8.2f} | {daz_deg:8.2f} | {arcv_deg:8.2f} | {arcl_deg:8.2f} |")
    print("+------------+----------+----------+----------+----------+----------+----------+----------+----------+")

    # Save CSV
    with open(csv_filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow(row)

    print(f"\n✅ Saved to CSV file: {csv_filename}")

    return {
        "Date": date_str,
        "Sunset": sunset_str,
        "Moonset": moonset_str,
        "Lag Time": lag_str,
        "Moon Age (h)": f"{moon_age_hours:.2f}",
        "Moon Alt (deg)": f"{moon_alt_deg:.2f}",
        "DAZ (deg)": f"{daz_deg:.2f}",
        "ArcV (deg)": f"{arcv_deg:.2f}",
        "ArcL (deg)": f"{arcl_deg:.2f}",
    }
