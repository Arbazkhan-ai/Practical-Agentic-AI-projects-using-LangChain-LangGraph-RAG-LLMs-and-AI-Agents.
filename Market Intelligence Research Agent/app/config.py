"""
Configuration settings, regional registries, and authoritative data sources.
"""

from typing import List, Dict, Any

# Regional coverage registry for fallback when specific geography is not provided
DEFAULT_CARIBBEAN_MARKETS: List[Dict[str, Any]] = [
    {"market": "Antigua and Barbuda", "iso_code": "ATG", "languages": ["en"], "active": True},
    {"market": "Bahamas", "iso_code": "BHS", "languages": ["en"], "active": True},
    {"market": "Barbados", "iso_code": "BRB", "languages": ["en"], "active": True},
    {"market": "Belize", "iso_code": "BLZ", "languages": ["en", "es"], "active": True},
    {"market": "Cuba", "iso_code": "CUB", "languages": ["es"], "active": True},
    {"market": "Dominica", "iso_code": "DMA", "languages": ["en"], "active": True},
    {"market": "Dominican Republic", "iso_code": "DOM", "languages": ["es"], "active": True},
    {"market": "Grenada", "iso_code": "GRD", "languages": ["en"], "active": True},
    {"market": "Guadeloupe", "iso_code": "GLP", "languages": ["fr"], "active": True},
    {"market": "Guyana", "iso_code": "GUY", "languages": ["en"], "active": True},
    {"market": "Haiti", "iso_code": "HTI", "languages": ["fr"], "active": True},
    {"market": "Jamaica", "iso_code": "JAM", "languages": ["en"], "active": True},
    {"market": "Martinique", "iso_code": "MTQ", "languages": ["fr"], "active": True},
    {"market": "Puerto Rico", "iso_code": "PRI", "languages": ["es", "en"], "active": True},
    {"market": "Saint Kitts and Nevis", "iso_code": "KNA", "languages": ["en"], "active": True},
    {"market": "Saint Lucia", "iso_code": "LCA", "languages": ["en"], "active": True},
    {"market": "Saint Vincent and the Grenadines", "iso_code": "VCT", "languages": ["en"], "active": True},
    {"market": "Suriname", "iso_code": "SUR", "languages": ["nl"], "active": True},
    {"market": "Trinidad and Tobago", "iso_code": "TTO", "languages": ["en"], "active": True},
    {"market": "Aruba", "iso_code": "ABW", "languages": ["nl", "en"], "active": True},
    {"market": "Curacao", "iso_code": "CUW", "languages": ["nl", "en"], "active": True},
]

# Authoritative source registry with tier rankings and domain metadata
SOURCE_REGISTRY: List[Dict[str, Any]] = [
    # English & Regional / International
    {"name": "CARICOM", "domain": "caricom.org", "tier": 1, "region": "regional", "topic_tags": ["trade", "agriculture", "policy"]},
    {"name": "OECS", "domain": "oecs.int", "tier": 1, "region": "regional", "topic_tags": ["integration", "agriculture", "economy"]},
    {"name": "Caribbean Development Bank", "domain": "caribank.org", "tier": 1, "region": "regional", "topic_tags": ["finance", "infrastructure", "growth"]},
    {"name": "ECCB", "domain": "eccb-centralbank.org", "tier": 1, "region": "regional", "topic_tags": ["monetary", "banking", "statistics"]},
    {"name": "Caribbean Tourism Organization", "domain": "onecaribbean.org", "tier": 1, "region": "regional", "topic_tags": ["tourism", "visitor_arrivals", "receipts"]},
    {"name": "FAO", "domain": "fao.org", "tier": 1, "region": "international", "topic_tags": ["food", "agriculture", "fisheries"]},
    {"name": "IICA", "domain": "iica.int", "tier": 1, "region": "international", "topic_tags": ["agriculture", "rural_development"]},
    {"name": "World Bank", "domain": "worldbank.org", "tier": 1, "region": "international", "topic_tags": ["gdp", "macroeconomics", "trade"]},
    {"name": "ECLAC / CEPAL", "domain": "cepal.org", "tier": 1, "region": "international", "topic_tags": ["latin_america", "caribbean", "trade", "statistics"]},
    {"name": "Inter-American Development Bank", "domain": "iadb.org", "tier": 1, "region": "international", "topic_tags": ["development", "investment", "finance"]},
    {"name": "IMF", "domain": "imf.org", "tier": 1, "region": "international", "topic_tags": ["monetary", "fiscal", "inflation"]},
    {"name": "UN Tourism", "domain": "untourism.int", "tier": 1, "region": "international", "topic_tags": ["global_tourism", "trends"]},

    # French Caribbean
    {"name": "INSEE", "domain": "insee.fr", "tier": 1, "region": "french_caribbean", "topic_tags": ["statistics", "demographics", "economy"]},
    {"name": "IEDOM", "domain": "iedom.fr", "tier": 1, "region": "french_caribbean", "topic_tags": ["monetary", "overseas_departments"]},
    {"name": "Data Gouv France", "domain": "data.gouv.fr", "tier": 2, "region": "french_caribbean", "topic_tags": ["open_data"]},
    {"name": "European Commission", "domain": "ec.europa.eu", "tier": 2, "region": "international", "topic_tags": ["outermost_regions", "agri_policy"]},

    # Spanish Caribbean
    {"name": "ONE Dominican Republic", "domain": "one.gob.do", "tier": 1, "region": "national", "topic_tags": ["national_statistics", "census"]},
    {"name": "ONEI Cuba", "domain": "onei.gob.cu", "tier": 1, "region": "national", "topic_tags": ["national_statistics", "agriculture", "tourism"]},

    # Dutch Caribbean
    {"name": "CBS Netherlands / Caribbean", "domain": "cbs.nl", "tier": 1, "region": "national", "topic_tags": ["statistics", "dutch_caribbean"]},
    {"name": "Centrale Bank van Curacao en Sint Maarten", "domain": "centralbank.cw", "tier": 1, "region": "national", "topic_tags": ["monetary", "economy"]},
    {"name": "Centrale Bank van Aruba", "domain": "cbaruba.org", "tier": 1, "region": "national", "topic_tags": ["monetary", "economy"]},
]

# Standard World Bank Indicators for macroeconomic, tourism, and agricultural intelligence
WORLD_BANK_INDICATORS: List[Dict[str, str]] = [
    {"code": "ST.INT.ARVL", "name": "International tourism, number of arrivals"},
    {"code": "ST.INT.RCPT.CD", "name": "International tourism, receipts (current US$)"},
    {"code": "ST.INT.XPND.CD", "name": "International tourism, expenditures (current US$)"},
    {"code": "NV.AGR.TOTL.ZS", "name": "Agriculture, forestry, and fishing, value added (% of GDP)"},
    {"code": "AG.PRD.FOOD.XD", "name": "Food production index (2014-2016 = 100)"},
    {"code": "TM.VAL.MRCH.CD.WT", "name": "Merchandise imports (current US$)"},
    {"code": "NY.GDP.MKTP.CD", "name": "GDP (current US$)"},
]

WB_SUPPORTED_ISO = {
    "ATG", "BHS", "BRB", "BLZ", "CUB", "DMA", "DOM", "GRD", "GUY", "HTI", "JAM", "KNA", "LCA",
    "VCT", "SUR", "TTO", "ABW", "VGB", "CYM", "CUW", "PRI", "SXM", "TCA", "VIR", "BMU"
}
