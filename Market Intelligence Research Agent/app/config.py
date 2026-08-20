"""
Configuration settings, regional registries, and authoritative data sources.
Implements the 6-Tier Source Quality Hierarchy for market intelligence integrity.
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

# 6-Tier Source Quality Hierarchy:
# Tier 1: Multilateral & Supranational Organizations (UN, WB, FAO, CEPAL, CDB, IDB, CARICOM, OECS)
# Tier 2: Official National Statistical Offices, Central Banks & Ministries (INSEE, CBS, BCRD, DAAF, Ministries)
# Tier 3: Specialized Agronomic & Academic Research Institutions (IICA, BAMSI, UWI)
# Tier 4: Corporate / Industry Case Studies & Sector Associations (Sandals Foundation, Kittitian Hill, CHTA)
# Tier 5: Reputable Curated News & Trade Media
# Tier 6: Social Media, User Forums & Informal Content
SOURCE_REGISTRY: List[Dict[str, Any]] = [
    # Tier 1: Multilateral & Regional Supranationals
    {"name": "CARICOM Secretariat", "domain": "caricom.org", "tier": 1, "institution_category": "Multilateral Organization", "document_type": "institutional_pdf", "topic_tags": ["trade", "agriculture", "policy"]},
    {"name": "OECS Commission", "domain": "oecs.int", "tier": 1, "institution_category": "Multilateral Organization", "document_type": "institutional_pdf", "topic_tags": ["integration", "agriculture", "economy"]},
    {"name": "OECS Commission", "domain": "oecs.org", "tier": 1, "institution_category": "Multilateral Organization", "document_type": "institutional_pdf", "topic_tags": ["integration", "agriculture", "economy"]},
    {"name": "Caribbean Development Bank", "domain": "caribank.org", "tier": 1, "institution_category": "Multilateral Financial Institution", "document_type": "institutional_pdf", "topic_tags": ["finance", "infrastructure", "growth"]},
    {"name": "Food and Agriculture Organization (FAO)", "domain": "fao.org", "tier": 1, "institution_category": "UN Specialized Agency", "document_type": "institutional_pdf", "topic_tags": ["food", "agriculture", "fisheries"]},
    {"name": "World Bank Group", "domain": "worldbank.org", "tier": 1, "institution_category": "Multilateral Financial Institution", "document_type": "institutional_pdf", "topic_tags": ["gdp", "macroeconomics", "trade"]},
    {"name": "ECLAC / CEPAL", "domain": "cepal.org", "tier": 1, "institution_category": "UN Regional Commission", "document_type": "institutional_pdf", "topic_tags": ["latin_america", "caribbean", "trade", "statistics"]},
    {"name": "Inter-American Development Bank (IDB)", "domain": "iadb.org", "tier": 1, "institution_category": "Multilateral Financial Institution", "document_type": "institutional_pdf", "topic_tags": ["development", "investment", "finance"]},
    {"name": "IDB Invest", "domain": "idbinvest.org", "tier": 1, "institution_category": "Multilateral Financial Institution", "document_type": "institutional_pdf", "topic_tags": ["private_sector", "cold_chain", "logistics"]},
    {"name": "IMF", "domain": "imf.org", "tier": 1, "institution_category": "Multilateral Financial Institution", "document_type": "institutional_pdf", "topic_tags": ["monetary", "fiscal", "inflation"]},
    {"name": "UN Tourism", "domain": "untourism.int", "tier": 1, "institution_category": "UN Specialized Agency", "document_type": "institutional_pdf", "topic_tags": ["global_tourism", "trends"]},
    {"name": "UNCTAD", "domain": "unctad.org", "tier": 1, "institution_category": "UN Conference", "document_type": "institutional_pdf", "topic_tags": ["trade", "development", "sids_economy"]},
    {"name": "Caribbean Tourism Organization", "domain": "onecaribbean.org", "tier": 1, "institution_category": "Regional Intergovernmental Body", "document_type": "institutional_pdf", "topic_tags": ["tourism", "visitor_arrivals", "receipts"]},

    # Tier 2: Official National Statistical Offices, Central Banks & Ministries
    {"name": "INSEE France", "domain": "insee.fr", "tier": 2, "institution_category": "National Statistical Office", "document_type": "national_bulletin", "topic_tags": ["statistics", "demographics", "economy"]},
    {"name": "IEDOM", "domain": "iedom.fr", "tier": 2, "institution_category": "Central Bank / Monetary Authority", "document_type": "national_bulletin", "topic_tags": ["monetary", "overseas_departments"]},
    {"name": "DAAF Martinique", "domain": "daaf.martinique.agriculture.gouv.fr", "tier": 2, "institution_category": "National Ministry Agency", "document_type": "government_report", "topic_tags": ["agriculture", "food_loss", "circuits_courts"]},
    {"name": "Chambre d'Agriculture de Guadeloupe", "domain": "guadeloupe.chambre-agriculture.fr", "tier": 2, "institution_category": "Public Agricultural Chamber", "document_type": "government_report", "topic_tags": ["agriculture", "short_chains", "agritourism"]},
    {"name": "ONE Dominican Republic", "domain": "one.gob.do", "tier": 2, "institution_category": "National Statistical Office", "document_type": "national_bulletin", "topic_tags": ["national_statistics", "census"]},
    {"name": "Banco Central de la Republica Dominicana", "domain": "bancentral.gov.do", "tier": 2, "institution_category": "Central Bank", "document_type": "national_bulletin", "topic_tags": ["tourist_spend", "balance_of_payments"]},
    {"name": "ONEI Cuba", "domain": "onei.gob.cu", "tier": 2, "institution_category": "National Statistical Office", "document_type": "national_bulletin", "topic_tags": ["national_statistics", "agriculture", "tourism"]},
    {"name": "CBS Netherlands", "domain": "cbs.nl", "tier": 2, "institution_category": "National Statistical Office", "document_type": "national_bulletin", "topic_tags": ["statistics", "dutch_caribbean"]},
    {"name": "CBS Curacao", "domain": "cbs.cw", "tier": 2, "institution_category": "National Statistical Office", "document_type": "national_bulletin", "topic_tags": ["statistics", "curacao_agriculture"]},
    {"name": "Centrale Bank van Curacao en Sint Maarten", "domain": "centralbank.cw", "tier": 2, "institution_category": "Central Bank", "document_type": "national_bulletin", "topic_tags": ["monetary", "economy"]},
    {"name": "Centrale Bank van Aruba", "domain": "cbaruba.org", "tier": 2, "institution_category": "Central Bank", "document_type": "national_bulletin", "topic_tags": ["monetary", "economy"]},
    {"name": "Jamaica Ministry of Tourism (TEF / RADA)", "domain": "mot.gov.jm", "tier": 2, "institution_category": "Government Ministry & Agency", "document_type": "government_report", "topic_tags": ["alex_platform", "agricultural_linkages"]},
    {"name": "Barbados Ministry of Agriculture", "domain": "agriculture.gov.bb", "tier": 2, "institution_category": "Government Ministry", "document_type": "government_report", "topic_tags": ["hotel_sourcing", "cold_storage"]},
    {"name": "Saint Lucia Ministry of Agriculture", "domain": "moa.govt.lc", "tier": 2, "institution_category": "Government Ministry", "document_type": "government_report", "topic_tags": ["agritourism_framework", "procurement"]},
    {"name": "NAMDEVCO Trinidad and Tobago", "domain": "namdevco.com", "tier": 2, "institution_category": "Statutory Marketing Agency", "document_type": "government_report", "topic_tags": ["wholesale_logistics", "cold_chain"]},
    {"name": "Dominica Ministry of Agriculture", "domain": "agriculture.gov.dm", "tier": 2, "institution_category": "Government Ministry", "document_type": "government_report", "topic_tags": ["organic_smallholders", "eco_lodges"]},
    {"name": "Grenada Tourism Authority", "domain": "puregrenada.com", "tier": 2, "institution_category": "National Tourism Authority", "document_type": "government_report", "topic_tags": ["culinary_spice_route", "agritourism"]},
    {"name": "St Vincent & Grenadines Ministry of Agriculture", "domain": "agriculture.gov.vc", "tier": 2, "institution_category": "Government Ministry", "document_type": "government_report", "topic_tags": ["root_crops", "resort_linkages"]},
    {"name": "Antigua & Barbuda Tourism Authority", "domain": "ab.gov.ag", "tier": 2, "institution_category": "National Tourism Authority", "document_type": "government_report", "topic_tags": ["culinary_impact", "tourism"]},

    # Tier 3: Specialized Agronomic & Academic Research Institutions
    {"name": "Inter-American Institute for Cooperation on Agriculture (IICA)", "domain": "iica.int", "tier": 3, "institution_category": "Agronomic Research Body", "document_type": "academic_study", "topic_tags": ["agriculture", "rural_development", "value_chains"]},
    {"name": "BAMSI Bahamas", "domain": "bamsibahamas.com", "tier": 3, "institution_category": "Agronomic Academic Institute", "document_type": "academic_study", "topic_tags": ["resort_procurement", "marine_agriculture"]},
    {"name": "University of the West Indies", "domain": "uwi.edu", "tier": 3, "institution_category": "Academic University", "document_type": "academic_study", "topic_tags": ["agricultural_economics", "sids"]},

    # Tier 4: Corporate / Industry Case Studies & Sector Associations
    {"name": "Sandals Corporate Sustainability / Foundation", "domain": "sandals.com", "tier": 4, "institution_category": "Corporate Sustainability / Private Sector", "document_type": "corporate_case_study", "topic_tags": ["farm_to_table", "hotel_sourcing"]},
    {"name": "Kittitian Hill / Bellemont Farm", "domain": "kittitianhill.com", "tier": 4, "institution_category": "Private Enterprise Case Study", "document_type": "corporate_case_study", "topic_tags": ["luxury_agroecology", "45pct_sourcing"]},
    {"name": "Caribbean Hotel and Tourism Association (CHTA)", "domain": "caribbeanhotelandtourism.com", "tier": 4, "institution_category": "Industry Trade Association", "document_type": "industry_report", "topic_tags": ["hospitality_trends", "sourcing"]},
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

