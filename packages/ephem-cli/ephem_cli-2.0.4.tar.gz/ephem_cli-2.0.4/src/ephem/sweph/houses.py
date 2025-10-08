import swisseph as swe
from ephem.utils.signs import sign_from_index
from ephem.constants import HOUSE_SYSTEMS
from .ayanamsas import get_calc_flag


def get_house_system(hsys_index):
    """
    Convert house system index to Swiss Ephemeris house system code.

    Args:
        hsys_index: Integer index 0-23 corresponding to house system

    Returns:
        bytes: Encoded house system character for Swiss Ephemeris
    """
    if not isinstance(hsys_index, int):
        return b"W"  # Default to Whole Sign if not an integer

    if not 0 <= hsys_index <= 23:
        return b"W"  # Default to Whole Sign if out of range

    # Get the house system code from the ordered list of values
    hsys = list(HOUSE_SYSTEMS.values())[hsys_index]
    return hsys.encode()


def get_cusps_degrees(jd_now, lat, lng, house_system=7, offset=None):
    """
    Get raw house cusp degrees for a given time and location.

    Args:
        jd_now: Julian day
        lat: Latitude
        lng: Longitude
        house_system: Integer index 0-23 for house system (default 7 = Whole Sign)
        offset: None for tropical, or integer index for sidereal ayanamsa

    Returns:
        tuple: (cusp_degrees, angles) from swe.houses_ex
    """
    calc_flag = get_calc_flag(offset)
    hsys = get_house_system(house_system)
    houses_data = swe.houses_ex(jd_now, lat, lng, hsys, calc_flag)
    return houses_data[0], houses_data[1]  # returns (cusps, angles)


def format_cusps(cusp_degrees):
    """
    Format house cusp degrees into dictionary format.

    Args:
        cusp_degrees: List of house cusp degrees (from get_cusps_degrees)

    Returns:
        list: List of dictionaries containing formatted house cusp data
    """
    cusps = []

    # Process each house cusp (1-12)
    for i, degree in enumerate(
        cusp_degrees[1:], 1
    ):  # Start from 1 since house numbers start at 1
        dms = swe.split_deg(degree, 8)
        sign_name, sign_data = sign_from_index(dms[4])

        cusps.append(
            {
                "obj_key": f"h{i}",  # h1, h2, etc. for house cusps
                "deg": dms[0],
                "mnt": dms[1],
                "sec": dms[2],
                "sign": sign_name,
                "trunc": sign_data["trunc"],
                "glyph": sign_data["glyph"],
                "trip": sign_data["trip"],
                "quad": sign_data["quad"],
            }
        )

    return cusps
