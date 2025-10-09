from typing import Union, Dict
import numpy as np
from datetime import datetime
import rasters as rt
from rasters import Raster, RasterGeometry
from NASADEM import NASADEM
from GEOS5FP import GEOS5FP
from check_distribution import check_distribution

from .constants import *

def water_heat_flux(
        WST_C: Union[Raster, np.ndarray],
        albedo: Union[Raster, np.ndarray] = None,
        Ta_C: Union[Raster, np.ndarray] = None,
        RH: Union[Raster, np.ndarray] = None,
        Td_C: Union[Raster, np.ndarray] = None,
        windspeed_mps: Union[Raster, np.ndarray] = None,
        SWnet: Union[Raster, np.ndarray] = None,
        geometry: RasterGeometry = None,
        time_UTC: datetime = None,
        water: Union[Raster, np.ndarray] = None,
        GEOS5FP_connection: GEOS5FP = None,
        resampling: str = RESAMPLING_METHOD,
        mask_non_water_pixels: bool = MASK_NON_WATER_PIXELS) -> Dict[str, Union[Raster, np.ndarray, float]]:
    """
    Calculate water heat flux based on input parameters.

    This function computes the water heat flux, which represents the energy exchange
    between a water surface and the atmosphere. The calculation is based on the AquaSEBS
    model, which adapts the Surface Energy Balance System (SEBS) for water bodies using
    the equilibrium temperature model (ETM) approach.

    References:
    - Abdelrady, A.; Timmermans, J.; Vekerdy, Z.; Salama, M.S. Surface Energy Balance 
      of Fresh and Saline Waters: AquaSEBS. Remote Sens. 2016, 8, 583. 
      https://doi.org/10.3390/rs8070583
    - Fisher, J.B.; Dohlen, M.B.; Halverson, G.H.; Collison, J.W.; Hook, S.J.; 
      Hulley, G.C. Remotely sensed terrestrial open water evaporation. 
      Sci. Rep. 2023, 13, 8217. https://doi.org/10.1038/s41598-023-34921-2

    Parameters:
    :param WST_C: Water surface temperature in Celsius.
    :param Ta_C: Air temperature in Celsius (optional, can be inferred).
    :param RH: Relative humidity as a fraction (0-1) (optional, can be inferred).
    :param Td_C: Dew-point temperature in Celsius (optional, can be inferred).
    :param windspeed_mps: Wind speed in meters per second (optional, can be inferred).
    :param SWnet: Net shortwave radiation in Watts per square meter (optional, can be inferred).
    :param geometry: Raster geometry for spatial data (optional).
    :param time_UTC: UTC timestamp for temporal data (optional).
    :param GEOS5FP_connection: Connection to GEOS5FP data source (optional).
    :param resampling: Resampling method for spatial data (default: RESAMPLING_METHOD).

    Returns:
    :return: Water heat flux in Watts per square meter.
    """
    # If geometry is not provided, try to infer from surface temperature raster
    if geometry is None and isinstance(WST_C, Raster):
        geometry = WST_C.geometry

    # Create GEOS5FP connection if not provided
    if GEOS5FP_connection is None:
        GEOS5FP_connection = GEOS5FP()

    if WST_C is None:
        raise ValueError("water surface temperature (WST_C) not given")
    
    check_distribution(WST_C, "WST_C")

    if water is None and geometry is not None and mask_non_water_pixels:
        water = NASADEM.swb(geometry=geometry)
        check_distribution(water, "water")
    
    if mask_non_water_pixels:
        WST_C = rt.where(water, WST_C, np.nan)

    if Td_C is None and geometry is not None and time_UTC is not None:
        # Retrieve air temperature if not provided, using GEOS5FP and geometry/time
        if Ta_C is None:
            Ta_C = GEOS5FP_connection.Ta_C(
                time_UTC=time_UTC,
                geometry=geometry,
                resampling=resampling
            )

        check_distribution(Ta_C, "Ta_C")
        
        # Retrieve relative humidity if not provided, using GEOS5FP and geometry/time
        if RH is None and geometry is not None and time_UTC is not None:
            RH = GEOS5FP_connection.RH(
                time_UTC=time_UTC,
                geometry=geometry,
                resampling=resampling
            )

        check_distribution(RH, "RH")

        # Calculate dew-point temperature using simplified approximation
        # Td_C [°C] = dew-point temperature derived from air temperature and relative humidity
        # Ta_C [°C] = air temperature, RH [fraction 0-1] = relative humidity
        # Simplified formula: Td ≈ Ta - ((100 - RH%) / 5) where RH% = RH * 100
        Td_C = Ta_C - ((100 - RH * 100) / 5.0)
    

    if Td_C is None:
        raise ValueError("dew-point temperature (Td_C) not given")

    check_distribution(Td_C, "Td_C")

    if windspeed_mps is None and geometry is not None and time_UTC is not None:
        # Retrieve wind speed in meters per second if not provided, using GEOS5FP and geometry/time
        windspeed_mps = GEOS5FP_connection.wind_speed(
            time_UTC=time_UTC,
            geometry=geometry,
            resampling=resampling
        )

    if windspeed_mps is None:
        raise ValueError("wind-speed (windspeed_mps) not given")

    check_distribution(windspeed_mps, "windspeed_mps")

    if SWnet is None and geometry is not None and time_UTC is not None:
        SWin = GEOS5FP_connection.SWin(
            time_UTC=time_UTC,
            geometry=geometry,
            resampling=resampling
        )

        check_distribution(SWin, "SWin")

        if albedo is None:
            albedo = GEOS5FP_connection.ALBEDO(
                time_UTC=time_UTC,
                geometry=geometry,
                resampling=resampling
            )
        
        check_distribution(albedo, "albedo")

        SWnet = SWin * (1 - albedo)
    
    if SWnet is None:
        raise ValueError("net shortwave radiation (SWnet) not given")

    check_distribution(SWnet, "SWnet")

    # Calculate temperature difference (Tn) - Equation 8 in Abdelrady et al. (2016), Section 2.2.1
    # Also validated in Fisher et al. (2023), Methods section (same formulation for consistency)
    # Tn [°C] = half the difference between water surface temperature and dew-point temperature
    # WST_C [°C] = water surface temperature, Td_C [°C] = dew-point temperature
    Tn = 0.5 * (WST_C - Td_C)
    check_distribution(Tn, "Tn")

    # Calculate evaporation efficiency (η) - Equation 9 in Abdelrady et al. (2016), Section 2.2.1
    # Also validated in Fisher et al. (2023), Methods section (same formulation for consistency)
    # η [dimensionless] = evaporation efficiency accounting for baseline efficiency (0.35), 
    # temperature dependence (0.015 * WST_C), and non-linear temperature difference effects (0.0012 * Tn²)
    # WST_C [°C] = water surface temperature, Tn [°C] = temperature difference
    η = 0.35 + 0.015 * WST_C + 0.0012 * (Tn ** 2)
    check_distribution(η, "η")

    # Scale wind speed (S) - Equation 10 in Abdelrady et al. (2016), Section 2.2.1
    # Also validated in Fisher et al. (2023), Methods section (same formulation for consistency)
    # S [dimensionless] = scaled wind speed factor enhancing evaporation and heat exchange
    # windspeed_mps [m/s] = wind speed at reference height
    S = 3.3 * windspeed_mps
    check_distribution(S, "S")

    # Calculate heat transfer coefficient (β) - Equation 11 in Abdelrady et al. (2016), Section 2.2.1
    # Also validated in Fisher et al. (2023), Methods section (same formulation for consistency)
    # β [W/(m²·°C)] = thermal exchange coefficient combining temperature effects (4.5 + 0.05 * WST_C),
    # evaporation efficiency, and wind enhancement ((η + 0.47) * S)
    # WST_C [°C] = water surface temperature, η [dimensionless] = evaporation efficiency, S [dimensionless] = scaled wind speed
    β = 4.5 + 0.05 * WST_C + (η + 0.47) * S
    check_distribution(β, "β")

    # Calculate equilibrium temperature (Te) - Equation 12 in Abdelrady et al. (2016), Section 2.2.1
    # Also validated in Fisher et al. (2023), Methods section (same formulation for consistency)
    # Te [°C] = hypothetical water surface temperature when net heat flux exchange equals zero
    # Td_C [°C] = dew-point temperature, SWnet [W/m²] = net shortwave radiation, β [W/(m²·°C)] = thermal exchange coefficient
    Te = Td_C + (SWnet / β)
    check_distribution(Te, "Te")

    # Calculate water heat flux (W) - Equation 13 in Abdelrady et al. (2016), Section 2.2.1
    # Also validated in Fisher et al. (2023), Methods section (same formulation for consistency)
    # W_Wm2 [W/m²] = water heat flux representing energy exchange rate between water surface and atmosphere
    # β [W/(m²·°C)] = thermal exchange coefficient, Te [°C] = equilibrium temperature, WST_C [°C] = water surface temperature
    W_Wm2 = β * (Te - WST_C)
    check_distribution(W_Wm2, "W_Wm2")

    return {
        "WST_C": WST_C,
        "Ta_C": Ta_C,
        "RH": RH,
        "Td_C": Td_C,
        "windspeed_mps": windspeed_mps,
        "SWnet": SWnet,
        "Tn": Tn,
        "η": η,
        "S": S,
        "β": β,
        "Te": Te,
        "W_Wm2": W_Wm2
    }
