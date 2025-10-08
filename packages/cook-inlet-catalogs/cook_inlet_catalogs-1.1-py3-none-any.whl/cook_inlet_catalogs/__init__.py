# import cook_inlet_catalogs.utils
# import cook_inlet_catalogs.generate_catalogs
from . import utils
from . import generate_catalogs

import cmocean.cm as cmo


cmap = {}
cmap["salt"] = "cmo.haline"
cmap["temp"] = "cmo.thermal"
cmap["u"] = "cmo.delta"
cmap["diff"] = "cmo.balance"
cmap["speed"] = "cmo.tempo"

# Comprehensive list of dataset slugs
# used for catalog generation. Are used for data page generation if "included" in catalog metadata.
slugs = [
        "adcp_moored_noaa_coi_2005",
        "adcp_moored_noaa_coi_other",
        "adcp_moored_noaa_kod_1",
        "adcp_moored_noaa_kod_2",
        "ctd_profiles_2005_noaa",
        "ctd_profiles_ecofoci",  # after v1.0.1
        "ctd_profiles_emap_2002",
        "ctd_profiles_emap_2008",
        "ctd_profiles_kachemack_kuletz_2005_2007",
        "ctd_profiles_kb_small_mesh_2006",
        "ctd_profiles_kbay_osu_2007",
        "ctd_profiles_piatt_speckman_1999",
        "ctd_profiles_usgs_boem",
        "ctd_towed_otf_kbnerr",
        "ctd_towed_ferry_noaa_pmel",
        "ctd_towed_gwa",
        "ctd_towed_gwa_temp",
        "ctd_transects_barabara_to_bluff_2002_2003",
        "ctd_transects_cmi_kbnerr",
        "ctd_transects_cmi_uaf",
        "ctd_transects_gwa",
        "ctd_transects_misc_2002",
        "ctd_transects_otf_kbnerr",
        "ctd_transects_uaf",
        "hfradar",
        "moorings_aoos_cdip",
        "moorings_circac",
        "moorings_kbnerr",
        "moorings_kbnerr_bear_cove_seldovia",
        "moorings_kbnerr_historical",
        "moorings_kbnerr_homer",
        "moorings_noaa",
        "moorings_nps",
        "moorings_uaf",
        "drifters_ecofoci",
        "drifters_uaf",
        "drifters_epscor",  # after v1.0.1
        "drifters_lake_clark",  # after v1.0.1
]