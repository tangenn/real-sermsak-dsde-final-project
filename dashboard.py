import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import matplotlib.font_manager as fm
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
import pydeck as pdk
from pathlib import Path
from province_coords import PROVINCE_COORDS

PARTY_PALETTE = [
    [229, 85, 60, 210],
    [52, 120, 246, 210],
    [245, 164, 38, 210],
    [31, 167, 112, 210],
    [191, 82, 163, 210],
    [94, 94, 219, 210],
    [224, 116, 73, 210],
    [56, 177, 201, 210],
    [144, 107, 255, 210],
    [128, 151, 70, 210],
]
OFFICIAL_PARTY_HEX = {
    "กล้าธรรม": "#138A36",
    "ก้าวไกล": "#F58220",
    "ไทรวมพลัง": "#6F2C91",
    "ประชาชน": "#F58220",
    "เพื่อไทย": "#E31E24",
    "ภูมิใจไทย": "#0057B8",
    "ประชาธิปัตย์": "#00AEEF",
    "พลังประชารัฐ": "#1F3A93",
    "รวมไทยสร้างชาติ": "#1D4ED8",
    "ไทยสร้างไทย": "#6B2DBD",
    "เศรษฐกิจ": "#0F766E",
    "ประชาธิปไตยใหม่": "#F2C230",
    "ไทยก้าวใหม่": "#E85D04",
    "ไทยก้าวหน้า": "#F97316",
    "คลองไทย": "#00A6A6",
    "รวมใจไทย": "#E11D48",
    "รวมพลังประชาชน": "#7C3AED",
    "พลังไทยรักชาติ": "#2563EB",
    "เพื่อชาติไทย": "#C026D3",
    "ประชาชาติ": "#16A34A",
    "อนาคตไทย": "#F59E0B",
    "ไทยภักดี": "#0F4C81",
    "ไทยชนะ": "#DC2626",
    "สร้างอนาคตไทย": "#14B8A6",
    "เสรีรวมไทย": "#C8102E",
}
COMPARISON_PARTY_ALIASES = {
    "ก้าวไกล": "ประชาชน",
}
DEFAULT_FILL = [181, 188, 202, 80]
DEFAULT_LINE = [255, 255, 255, 190]
PROVINCE_ALIASES = {
    'Sakon Nakhon': 'สกลนคร',
}
GEOJSON_PROVINCE_ALIASES = {
    'Amnat Charoen': 'อำนาจเจริญ',
    'Ang Thong': 'อ่างทอง',
    'Bangkok Metropolis': 'กรุงเทพมหานคร',
    'Bueng Kan': 'บึงกาฬ',
    'Buri Ram': 'บุรีรัมย์',
    'Chachoengsao': 'ฉะเชิงเทรา',
    'Chai Nat': 'ชัยนาท',
    'Chaiyaphum': 'ชัยภูมิ',
    'Chanthaburi': 'จันทบุรี',
    'Chiang Mai': 'เชียงใหม่',
    'Chiang Rai': 'เชียงราย',
    'Chon Buri': 'ชลบุรี',
    'Chumphon': 'ชุมพร',
    'Kalasin': 'กาฬสินธุ์',
    'Kamphaeng Phet': 'กำแพงเพชร',
    'Kanchanaburi': 'กาญจนบุรี',
    'Khon Kaen': 'ขอนแก่น',
    'Krabi': 'กระบี่',
    'Lampang': 'ลำปาง',
    'Lamphun': 'ลำพูน',
    'Loei': 'เลย',
    'Lop Buri': 'ลพบุรี',
    'Mae Hong Son': 'แม่ฮ่องสอน',
    'Maha Sarakham': 'มหาสารคาม',
    'Mukdahan': 'มุกดาหาร',
    'Nakhon Nayok': 'นครนายก',
    'Nakhon Pathom': 'นครปฐม',
    'Nakhon Phanom': 'นครพนม',
    'Nakhon Ratchasima': 'นครราชสีมา',
    'Nakhon Sawan': 'นครสวรรค์',
    'Nakhon Si Thammarat': 'นครศรีธรรมราช',
    'Nan': 'น่าน',
    'Narathiwat': 'นราธิวาส',
    'Nong Bua Lam Phu': 'หนองบัวลำภู',
    'Nong Khai': 'หนองคาย',
    'Nonthaburi': 'นนทบุรี',
    'Pathum Thani': 'ปทุมธานี',
    'Pattani': 'ปัตตานี',
    'Phangnga': 'พังงา',
    'Phatthalung': 'พัทลุง',
    'Phayao': 'พะเยา',
    'Phetchabun': 'เพชรบูรณ์',
    'Phetchaburi': 'เพชรบุรี',
    'Phichit': 'พิจิตร',
    'Phitsanulok': 'พิษณุโลก',
    'Phra Nakhon Si Ayutthaya': 'พระนครศรีอยุธยา',
    'Phrae': 'แพร่',
    'Phuket': 'ภูเก็ต',
    'Prachin Buri': 'ปราจีนบุรี',
    'Prachuap Khiri Khan': 'ประจวบคีรีขันธ์',
    'Ranong': 'ระนอง',
    'Ratchaburi': 'ราชบุรี',
    'Rayong': 'ระยอง',
    'Roi Et': 'ร้อยเอ็ด',
    'Sa Kaeo': 'สระแก้ว',
    'Sakon Nakhon': 'สกลนคร',
    'Samut Prakan': 'สมุทรปราการ',
    'Samut Sakhon': 'สมุทรสาคร',
    'Samut Songkhram': 'สมุทรสงคราม',
    'Saraburi': 'สระบุรี',
    'Satun': 'สตูล',
    'Si Sa Ket': 'ศรีสะเกษ',
    'Sing Buri': 'สิงห์บุรี',
    'Songkhla': 'สงขลา',
    'Sukhothai': 'สุโขทัย',
    'Suphan Buri': 'สุพรรณบุรี',
    'Surat Thani': 'สุราษฎร์ธานี',
    'Surin': 'สุรินทร์',
    'Tak': 'ตาก',
    'Trang': 'ตรัง',
    'Trat': 'ตราด',
    'Ubon Ratchathani': 'อุบลราชธานี',
    'Udon Thani': 'อุดรธานี',
    'Uthai Thani': 'อุทัยธานี',
    'Uttaradit': 'อุตรดิตถ์',
    'Yala': 'ยะลา',
    'Yasothon': 'ยโสธร',
}

# Page Config
st.set_page_config(page_title="Thai Election 2026 BI Dashboard", layout="wide")

# Thai Font Setup
thai_font_name = 'Bai Jamjuree'
try:
    if thai_font_name not in [f.name for f in fm.fontManager.ttflist]:
        font_path = os.path.expanduser('~/.local/share/fonts/BaiJamjuree-Regular.ttf')
        if os.path.exists(font_path):
            fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = thai_font_name
except:
    pass

# Title
st.title("Thai Election Dashboard")

UBON2_PROVINCE = "อุบลราชธานี"
UBON2_CONSTITUENCY = 2
UBON2_OCR_PATH = Path("ocr-output/constituency/77. อุบลราชธานี เขต 2.json")
UBON2_PARTY_LIST_OCR_PATH = Path("ocr-output/party_list/77. อุบลราชธานี เขต 2.json")
UBON2_HISTORICAL_PATH = Path("previous_data/historical_2023_ubon2_full.json")
RECENT_CONSTITUENCY_WIDE_PATH = Path("recent_data/constituency_wide.csv")
RECENT_PARTY_LIST_WIDE_PATH = Path("recent_data/party_list_wide.csv")
PREVIOUS_CONSTITUENCY_WIDE_PATH = Path("previous_data/ubon_2_constituency_2566.csv")
PREVIOUS_PARTY_LIST_WIDE_PATH = Path("previous_data/ubon_2_partylist_2566.csv")
THAI_SUBDISTRICT_COORDS_PATH = Path("recent_data/thai_subdistrict_coords.csv")
THAI_SUBDISTRICT_COORDS_URL = "https://raw.githubusercontent.com/spicydog/thailand-province-district-subdistrict-zipcode-latitude-longitude/master/output.csv"
UBON_TAMBON_BOUNDARY_PATH = Path("recent_data/ubon_tambon_boundaries.geojson")
THAI_TAMBON_BOUNDARY_ENDPOINT = (
    "https://services1.arcgis.com/jSaRWj2TDlcN1zOC/arcgis/rest/services/"
    "Thailand_Subdistrict_Boundaries_%28%E0%B8%82%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%B9%E0%B8%A5"
    "%E0%B8%82%E0%B8%AD%E0%B8%9A%E0%B9%80%E0%B8%82%E0%B8%95%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5"
    "%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B9%84%E0%B8%97%E0%B8%A2%29/FeatureServer/1/query"
)
UBON_CENTER = {"lat": 15.2287, "lon": 104.8564}

REAL_RECENT_CANDIDATES = [
    Path("recent_data/all_results.csv"),
    Path("recent_data/ubon2.csv"),
    Path("recent_data/ubon2_recent.csv"),
    Path("data/recent_ubon2.csv"),
    Path("data/ubon2_recent.csv"),
]

# Load Data
@st.cache_data
def load_data():
    df_const = pd.read_csv('analysis/output/constituency_results.csv')
    df_pl = pd.read_csv('analysis/output/party_list_results.csv')
    df_sum = pd.read_csv('analysis/output/constituency_summary.csv')
    
    # Data Cleaning
    df_const['party'] = df_const['party'].fillna('ไม่ทราบพรรค')
    df_pl['party'] = df_pl['party'].fillna('ไม่ทราบพรรค')
    
    # Calculate Winners & Margins
    def get_winner_info(group):
        sorted_g = group.sort_values('votes', ascending=False)
        winner = sorted_g.iloc[0].copy()
        if len(sorted_g) > 1:
            winner['margin'] = sorted_g.iloc[0]['votes'] - sorted_g.iloc[1]['votes']
            winner['margin_pct'] = (winner['margin'] / sorted_g.iloc[0]['votes']) * 100
        else:
            winner['margin'] = winner['votes']
            winner['margin_pct'] = 100
        return winner
    
    const_winners = df_const.groupby(['province', 'constituency']).apply(get_winner_info, include_groups=False).reset_index()
    pl_winners = df_pl.groupby(['province', 'constituency']).apply(get_winner_info, include_groups=False).reset_index()
    
    # Merge for Flow Analysis
    flow_df = const_winners[['province', 'constituency', 'party', 'margin', 'margin_pct', 'name']].copy()
    flow_df.rename(columns={'party': 'Const_Winner', 'margin': 'Const_Margin', 'name': 'Candidate'}, inplace=True)
    
    pl_winners_min = pl_winners[['province', 'constituency', 'party', 'margin']].copy()
    pl_winners_min.rename(columns={'party': 'PL_Winner', 'margin': 'PL_Margin'}, inplace=True)
    
    flow_df = flow_df.merge(pl_winners_min, on=['province', 'constituency'])
    flow_df['is_split'] = flow_df['Const_Winner'] != flow_df['PL_Winner']
    
    return df_const, df_pl, df_sum, flow_df

def _to_number(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)

def _first_existing_column(df, candidates):
    for column in candidates:
        if column in df.columns:
            return column
    return None

def _find_recent_ubon2_file():
    for path in REAL_RECENT_CANDIDATES:
        if path.exists():
            return path
    return None

def _load_real_ubon2_rows(form_type):
    recent_file = _find_recent_ubon2_file()
    if not recent_file:
        return None, None

    raw = pd.read_csv(recent_file)
    province_col = _first_existing_column(raw, ["province", "province_name"])
    constituency_col = _first_existing_column(raw, ["constituency", "constituency_number"])
    form_type_col = _first_existing_column(raw, ["form_type", "type"])

    if province_col:
        raw = raw[raw[province_col].astype(str).str.strip().eq(UBON2_PROVINCE)]
    if constituency_col:
        raw = raw[pd.to_numeric(raw[constituency_col], errors="coerce").eq(UBON2_CONSTITUENCY)]
    if form_type_col:
        raw = raw[raw[form_type_col].astype(str).str.strip().eq(form_type)]

    if raw.empty:
        return None, recent_file
    return raw, recent_file

def _rank_candidates(candidate_df):
    candidate_df = candidate_df.copy()
    candidate_df["votes"] = _to_number(candidate_df["votes"]).astype(int)
    candidate_df = candidate_df.sort_values("votes", ascending=False).reset_index(drop=True)
    candidate_df["rank"] = np.arange(1, len(candidate_df) + 1)
    total_votes = max(int(candidate_df["votes"].sum()), 1)
    candidate_df["vote_share"] = candidate_df["votes"] / total_votes * 100
    return candidate_df

def _clean_thai_admin_name(value):
    text = str(value or "").strip()
    text = text.replace("อ.เมืองฯ", "เมืองอุบลราชธานี")
    text = text.replace("เมืองฯ", "เมืองอุบลราชธานี")
    for token in ["อำเภอ", "อ.", "ตำบล", "เขตเทศบาล และนอกเขต", "เขตตำบล", "เขต"]:
        text = text.replace(token, "")
    text = "".join(ch for ch in text if not ch.isdigit())
    text = " ".join(text.split())
    return text.strip()

def _area_match_keys(row):
    if row.get("match_district_key") and row.get("match_tambon_key"):
        return str(row.get("match_district_key")), str(row.get("match_tambon_key"))
    amphoe_key = _clean_thai_admin_name(row.get("amphoe", ""))
    tambon_key = _clean_thai_admin_name(row.get("tambon", ""))
    if not tambon_key:
        tambon_key = amphoe_key
    return amphoe_key, tambon_key

def _geojson_feature_bounds(features):
    xs = []
    ys = []

    def visit(coords):
        if not coords:
            return
        if isinstance(coords[0], (int, float)):
            xs.append(float(coords[0]))
            ys.append(float(coords[1]))
            return
        for child in coords:
            visit(child)

    for feature in features:
        geometry = feature.get("geometry") or {}
        visit(geometry.get("coordinates"))

    if not xs or not ys:
        return UBON_CENTER["lon"], UBON_CENTER["lat"], UBON_CENTER["lon"], UBON_CENTER["lat"]
    return min(xs), min(ys), max(xs), max(ys)

@st.cache_data
def load_ubon_tambon_boundaries():
    if UBON_TAMBON_BOUNDARY_PATH.exists():
        with UBON_TAMBON_BOUNDARY_PATH.open(encoding="utf-8") as f:
            return json.load(f)

    params = {
        "where": f"NAME1='{UBON2_PROVINCE}'",
        "outFields": "ADMIN_ID3,NAME1,NAME2,NAME3,POPULATION,HOUSE",
        "returnGeometry": "true",
        "outSR": 4326,
        "f": "geojson",
    }
    try:
        response = requests.get(THAI_TAMBON_BOUNDARY_ENDPOINT, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

@st.cache_data
def load_subdistrict_coords():
    if THAI_SUBDISTRICT_COORDS_PATH.exists():
        coords = pd.read_csv(THAI_SUBDISTRICT_COORDS_PATH)
    else:
        try:
            coords = pd.read_csv(THAI_SUBDISTRICT_COORDS_URL)
        except Exception:
            return pd.DataFrame()

    required = {"province", "district", "subdistrict", "latitude", "longitude"}
    if not required.issubset(coords.columns):
        return pd.DataFrame()

    coords = coords.copy()
    coords["lat"] = pd.to_numeric(coords["latitude"], errors="coerce")
    coords["lon"] = pd.to_numeric(coords["longitude"], errors="coerce")
    coords = coords.dropna(subset=["lat", "lon"])
    coords["province_key"] = coords["province"].map(_clean_thai_admin_name)
    coords["district_key"] = coords["district"].map(_clean_thai_admin_name)
    coords["tambon_key"] = coords["subdistrict"].map(_clean_thai_admin_name)
    return coords[["province_key", "district_key", "tambon_key", "lat", "lon"]].drop_duplicates()

def _add_map_positions(area_df):
    area_df = area_df.copy()
    lat_col = _first_existing_column(area_df, ["lat", "latitude"])
    lon_col = _first_existing_column(area_df, ["lon", "lng", "longitude"])
    if lat_col and lon_col:
        area_df["lat"] = pd.to_numeric(area_df[lat_col], errors="coerce")
        area_df["lon"] = pd.to_numeric(area_df[lon_col], errors="coerce")
        area_df["has_geo_coords"] = ~area_df[["lat", "lon"]].isna().any(axis=1)
    else:
        area_df["lat"] = np.nan
        area_df["lon"] = np.nan
        coords = load_subdistrict_coords()
        if not coords.empty and "tambon" in area_df.columns:
            positioned = area_df.reset_index(drop=True).copy()
            positioned["province_key"] = _clean_thai_admin_name(UBON2_PROVINCE)
            positioned["district_key"] = positioned["amphoe"].map(_clean_thai_admin_name) if "amphoe" in positioned.columns else ""
            positioned["tambon_key"] = positioned["tambon"].map(_clean_thai_admin_name)
            blank_tambon = positioned["tambon_key"].eq("")
            positioned.loc[blank_tambon, "tambon_key"] = positioned.loc[blank_tambon, "district_key"]

            exact = positioned.merge(
                coords,
                on=["province_key", "district_key", "tambon_key"],
                how="left",
                suffixes=("", "_coord"),
            )
            missing = exact["lat_coord"].isna()
            if missing.any():
                fallback_coords = coords.drop_duplicates(["province_key", "tambon_key"])
                fallback = positioned.loc[missing].drop(columns=["lat", "lon"], errors="ignore").merge(
                    fallback_coords,
                    on=["province_key", "tambon_key"],
                    how="left",
                    suffixes=("", "_fallback"),
                )
                exact.loc[missing, "lat_coord"] = fallback["lat"].to_numpy()
                exact.loc[missing, "lon_coord"] = fallback["lon"].to_numpy()
                exact.loc[missing, "district_key"] = fallback["district_key"].to_numpy()

            area_df["lat"] = exact["lat_coord"].to_numpy()
            area_df["lon"] = exact["lon_coord"].to_numpy()
            area_df["match_district_key"] = exact["district_key"].to_numpy()
            area_df["match_tambon_key"] = exact["tambon_key"].to_numpy()

        area_df["has_geo_coords"] = ~area_df[["lat", "lon"]].isna().any(axis=1)
    return area_df

def _party_color_map(parties):
    unique_parties = [str(party) for party in pd.Series(parties).dropna().unique().tolist() if str(party).strip()]
    color_map = {}
    fallback_idx = 0
    for party in unique_parties:
        official = OFFICIAL_PARTY_HEX.get(party)
        if official:
            color_map[party] = _hex_to_rgba(official)
        else:
            color_map[party] = PARTY_PALETTE[fallback_idx % len(PARTY_PALETTE)]
            fallback_idx += 1
    return color_map

def _hex_to_rgba(hex_color, alpha=210):
    value = str(hex_color).strip().lstrip("#")
    if len(value) != 6:
        return DEFAULT_FILL
    return [int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha]

def _plotly_party_color_map(parties=None):
    color_map = dict(OFFICIAL_PARTY_HEX)
    if parties is not None:
        fallback_idx = 0
        for party in pd.Series(parties).dropna().astype(str).unique().tolist():
            if party not in color_map:
                rgba = PARTY_PALETTE[fallback_idx % len(PARTY_PALETTE)]
                color_map[party] = f"rgb({rgba[0]},{rgba[1]},{rgba[2]})"
                fallback_idx += 1
    return color_map

def _summary_from_real_rows(raw):
    unit_cols = [col for col in ["amphoe", "tambon", "unit", "form_type", "source"] if col in raw.columns]
    summary_cols = [
        "eligible_voters",
        "turnout",
        "valid_ballots",
        "spoiled_ballots",
        "abstain_ballots",
    ]
    if unit_cols:
        available_summary_cols = [col for col in summary_cols if col in raw.columns]
        unit_df = raw.copy()
        for col in available_summary_cols:
            unit_df[col] = _to_number(unit_df[col])
        unit_df = unit_df.groupby(unit_cols, as_index=False)[available_summary_cols].max()
    else:
        unit_df = raw

    def sum_col(column):
        return int(_to_number(unit_df[column]).sum()) if column in unit_df.columns else None

    return {
        "eligible_voters": sum_col("eligible_voters"),
        "turnout": sum_col("turnout"),
        "valid_ballots": sum_col("valid_ballots"),
        "spoiled_ballots": sum_col("spoiled_ballots"),
        "abstain_ballots": sum_col("abstain_ballots"),
        "vote_sum": int(_to_number(raw["display_votes"]).sum()) if "display_votes" in raw.columns else (int(_to_number(raw["votes"]).sum()) if "votes" in raw.columns else None),
        "good_votes": sum_col("valid_ballots"),
        "sum_diff_pct": None,
    }

def _add_display_votes(raw, votes_col):
    cleaned = raw.copy()
    raw_votes = _to_number(cleaned[votes_col])
    thai_votes = _to_number(cleaned["votes_th_value"]) if "votes_th_value" in cleaned.columns else pd.Series(np.nan, index=cleaned.index)
    has_thai_votes = cleaned["votes_th_value"].notna() if "votes_th_value" in cleaned.columns else pd.Series(False, index=cleaned.index)
    display_votes = raw_votes.where(~has_thai_votes, thai_votes)

    if "valid_ballots" in cleaned.columns:
        valid_ballots = _to_number(cleaned["valid_ballots"])
        display_votes = display_votes.mask(display_votes > valid_ballots, 0)

    if "error_type" in cleaned.columns:
        total_copy = cleaned["error_type"].astype(str).str.contains("total_copy", na=False)
        display_votes = display_votes.mask(total_copy & ~has_thai_votes, 0)

    cleaned["display_votes"] = display_votes.fillna(0)
    return cleaned

@st.cache_data
def load_ubon2_recent():
    raw, recent_file = _load_real_ubon2_rows("constituency")
    if raw is not None:
        number_col = _first_existing_column(raw, ["candidate_number", "number"])
        name_col = _first_existing_column(raw, ["candidate_name", "name"])
        party_col = _first_existing_column(raw, ["party", "party_raw"])
        votes_col = _first_existing_column(raw, ["votes", "votes_th_value"])
        amphoe_col = _first_existing_column(raw, ["amphoe", "district"])
        tambon_col = _first_existing_column(raw, ["tambon", "subdistrict"])
        unit_col = _first_existing_column(raw, ["unit", "polling_unit"])

        if not all([name_col, party_col, votes_col]):
            raise ValueError(f"{recent_file} is missing candidate_name/name, party, or votes columns.")

        raw = _add_display_votes(raw, votes_col)
        candidate_group_cols = [col for col in [number_col, name_col, party_col] if col]
        candidate_df = (
            raw.groupby(candidate_group_cols, as_index=False)
            .agg(votes=("display_votes", "sum"))
            .rename(columns={number_col or "candidate_number": "number", name_col: "name", party_col: "party"})
        )

        area_cols = [col for col in [amphoe_col, tambon_col] if col]
        if not area_cols:
            area_cols = [unit_col] if unit_col else []

        if area_cols:
            area_votes = (
                raw.groupby(area_cols + candidate_group_cols, as_index=False)
                .agg(votes=("display_votes", "sum"))
                .rename(columns={name_col: "name", party_col: "party"})
            )
            idx = area_votes.groupby(area_cols)["votes"].idxmax()
            area_df = area_votes.loc[idx].copy()
            area_df["area_name"] = area_df[area_cols].astype(str).agg(" / ".join, axis=1)
        else:
            candidate_df = _rank_candidates(candidate_df)
            winner = candidate_df.iloc[0]
            area_df = pd.DataFrame([{
                "area_name": "อุบลราชธานี เขต 2",
                "amphoe": "-",
                "tambon": "all reported rows",
                "name": winner["name"],
                "party": winner["party"],
                "votes": winner["votes"],
            }])

        summary = _summary_from_real_rows(raw)
        source_label = f"real schema CSV: {recent_file}"
    else:
        with UBON2_OCR_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
        candidate_df = pd.DataFrame(data["results"]).rename(columns={"number": "number", "name": "name", "party": "party"})
        candidate_df = _rank_candidates(candidate_df)
        winner = candidate_df.iloc[0]
        area_df = pd.DataFrame([{
            "area_name": "OCR constituency total",
            "amphoe": "-",
            "tambon": "No tambon field in OCR JSON yet",
            "name": winner["name"],
            "party": winner["party"],
            "votes": winner["votes"],
        }])
        summary_by_section = data.get("summary_by_section", {})
        summary = {
            "eligible_voters": summary_by_section.get("1.1"),
            "turnout": summary_by_section.get("3.4"),
            "valid_ballots": summary_by_section.get("4.1"),
            "spoiled_ballots": summary_by_section.get("4.2"),
            "abstain_ballots": summary_by_section.get("4.3"),
        }
        source_label = f"OCR JSON: {UBON2_OCR_PATH}"

    candidate_df = _rank_candidates(candidate_df)
    area_df = _add_map_positions(area_df)
    party_colors = _party_color_map(candidate_df["party"])
    area_df["fill_color"] = area_df["party"].map(party_colors).apply(lambda x: x if isinstance(x, list) else DEFAULT_FILL)
    area_df["radius"] = 12000 if len(area_df) == 1 else 3200
    area_df["winner_votes"] = area_df["votes"].astype(int)
    return candidate_df, area_df, summary, source_label, party_colors

@st.cache_data
def load_ubon2_party_list():
    raw, recent_file = _load_real_ubon2_rows("party_list")
    if raw is not None:
        number_col = _first_existing_column(raw, ["candidate_number", "number"])
        party_col = _first_existing_column(raw, ["party", "party_raw"])
        votes_col = _first_existing_column(raw, ["votes", "votes_th_value"])

        if not all([party_col, votes_col]):
            raise ValueError(f"{recent_file} is missing party or votes columns.")

        raw = _add_display_votes(raw, votes_col)
        party_group_cols = [col for col in [number_col, party_col] if col]
        party_df = (
            raw.groupby(party_group_cols, as_index=False)
            .agg(votes=("display_votes", "sum"))
            .rename(columns={number_col or "candidate_number": "number", party_col: "party"})
        )
        party_df = _rank_candidates(party_df)
        summary = _summary_from_real_rows(raw)
        return party_df, summary, f"real schema CSV: {recent_file}"
    else:
        with UBON2_PARTY_LIST_OCR_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
        party_df = _rank_candidates(pd.DataFrame(data["results"]))
        summary_by_section = data.get("summary_by_section", {})
        summary = {
            "eligible_voters": summary_by_section.get("1.1"),
            "turnout": summary_by_section.get("3.4"),
            "valid_ballots": summary_by_section.get("4.1"),
            "spoiled_ballots": summary_by_section.get("4.2"),
            "abstain_ballots": summary_by_section.get("4.3"),
            "vote_sum": data.get("_validation", {}).get("vote_sum"),
            "good_votes": data.get("_validation", {}).get("good_votes"),
            "sum_diff_pct": data.get("_validation", {}).get("sum_diff_pct"),
        }
        return party_df, summary, f"OCR JSON: {UBON2_PARTY_LIST_OCR_PATH}"

@st.cache_data
def load_ubon2_historical():
    with UBON2_HISTORICAL_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    candidate_df = _rank_candidates(pd.DataFrame(data["constituency_results"]).rename(columns={"number": "number", "name": "name", "party": "party"}))
    party_list_df = _rank_candidates(pd.DataFrame(data.get("party_list_results", [])))
    return candidate_df, party_list_df

def get_top_two_metrics(candidate_df):
    if candidate_df.empty:
        return None, None, 0, 0
    winner = candidate_df.iloc[0]
    runner_up = candidate_df.iloc[1] if len(candidate_df) > 1 else None
    margin = int(winner["votes"] - (runner_up["votes"] if runner_up is not None else 0))
    margin_pct = margin / max(int(winner["votes"]), 1) * 100
    return winner, runner_up, margin, margin_pct

def make_dumbbell_chart(comparison_df, title):
    view = comparison_df.sort_values("recent_votes", ascending=True).copy()
    fig = go.Figure()

    for row in view.itertuples():
        line_color = "#16A34A" if row.change >= 0 else "#DC2626"
        fig.add_trace(
            go.Scatter(
                x=[row.previous_votes, row.recent_votes],
                y=[row.party, row.party],
                mode="lines",
                line={"color": line_color, "width": 4},
                opacity=0.55,
                showlegend=False,
                hoverinfo="skip",
            )
        )

    fig.add_trace(
        go.Scatter(
            x=view["previous_votes"],
            y=view["party"],
            mode="markers",
            name="ปี66",
            marker={"size": 11, "color": "#111827", "line": {"color": "white", "width": 1}},
            customdata=np.stack([view["recent_votes"], view["change"]], axis=-1),
            hovertemplate=(
                "Party: %{y}<br>"
                "Previous votes: %{x:,}<br>"
                "Recent votes: %{customdata[0]:,}<br>"
                "Change: %{customdata[1]:+,}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=view["recent_votes"],
            y=view["party"],
            mode="markers",
            name="ปีนี้",
            marker={
                "size": 13,
                "color": "#FFFFFF",
                "line": {"color": "#111827", "width": 1.5},
            },
            customdata=np.stack([view["previous_votes"], view["change"]], axis=-1),
            hovertemplate=(
                "Party: %{y}<br>"
                "Recent votes: %{x:,}<br>"
                "2023 votes: %{customdata[0]:,}<br>"
                "Change: %{customdata[1]:+,}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title={"text": title, "x": 0},
        height=520,
        margin={"r": 20, "t": 45, "l": 0, "b": 0},
        xaxis_title="Votes",
        yaxis_title="",
        legend_title_text="",
        hovermode="closest",
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148, 163, 184, 0.25)", zeroline=False)
    fig.update_yaxes(categoryorder="array", categoryarray=view["party"].tolist())
    return fig

def build_party_comparison(recent_df, historical_df, top_n=10):
    recent = recent_df.copy()
    historical = historical_df.copy()
    recent["comparison_party"] = recent["party"].astype(str).replace(COMPARISON_PARTY_ALIASES)
    historical["comparison_party"] = historical["party"].astype(str).replace(COMPARISON_PARTY_ALIASES)
    recent_party = recent.groupby("comparison_party", as_index=False).agg(recent_votes=("votes", "sum"))
    hist_party = historical.groupby("comparison_party", as_index=False).agg(previous_votes=("votes", "sum"))
    comparison = recent_party.merge(hist_party, on="comparison_party", how="outer").fillna(0)
    comparison = comparison.rename(columns={"comparison_party": "party"})
    comparison["recent_votes"] = comparison["recent_votes"].astype(int)
    comparison["previous_votes"] = comparison["previous_votes"].astype(int)
    comparison["change"] = comparison["recent_votes"] - comparison["previous_votes"]
    return comparison.sort_values("recent_votes", ascending=False).head(top_n)

def _recent_vote_columns(df):
    return [col for col in df.columns if col.endswith("_votes") and not col.startswith("val_")]

def _previous_vote_columns(df, prefix):
    excluded = {
        f"{prefix}บัตรเสีย",
        f"{prefix}ผู้มาใช้สิทธิ์",
        f"{prefix}ผู้มีสิทธิ์",
        f"{prefix}ไม่เลือกผู้ใด",
    }
    return [col for col in df.columns if col.startswith(prefix) and col not in excluded]

def _party_from_recent_col(column):
    return column.removesuffix("_votes")

def _party_from_previous_col(column, prefix):
    return column.replace(prefix, "", 1)

def _normalize_wide_admin_columns(df, previous=False, form_type="constituency"):
    out = df.copy()
    if previous:
        out = out.rename(columns={
            "district": "amphoe",
            "subdistrict": "tambon",
            "station_number": "unit",
            "province_number": "constituency",
        })
        out["form_type"] = form_type
        out["eligible_voters"] = _to_number(out.get("เขต_ผู้มีสิทธิ์", out.get("บช_ผู้มีสิทธิ์", pd.Series(dtype=float))))
        out["turnout"] = _to_number(out.get("เขต_ผู้มาใช้สิทธิ์", out.get("บช_ผู้มาใช้สิทธิ์", pd.Series(dtype=float))))
        out["valid_ballots"] = 0
        out["spoiled_ballots"] = _to_number(out.get("เขต_บัตรเสีย", out.get("บช_บัตรเสีย", pd.Series(dtype=float))))
        out["abstain_ballots"] = _to_number(out.get("เขต_ไม่เลือกผู้ใด", out.get("บช_ไม่เลือกผู้ใด", pd.Series(dtype=float))))
    for col in ["eligible_voters", "turnout", "valid_ballots", "spoiled_ballots", "abstain_ballots"]:
        if col in out.columns:
            out[col] = _to_number(out[col])
    out["amphoe"] = out["amphoe"].fillna("").astype(str)
    out["tambon"] = out["tambon"].fillna("").astype(str)
    out["unit"] = _to_number(out["unit"]).astype(int).astype(str)
    return out

def _wide_party_totals(df, vote_cols, prefix=""):
    rows = []
    for col in vote_cols:
        party = _party_from_previous_col(col, prefix) if prefix else _party_from_recent_col(col)
        votes = int(_to_number(df[col]).sum())
        rows.append({"party": party, "votes": votes})
    return _rank_candidates(pd.DataFrame(rows))

def _wide_area_winners(df, vote_cols, prefix="", level="tambon"):
    group_cols = ["amphoe", "tambon"] if level == "tambon" else ["amphoe", "tambon", "unit"]
    grouped = df.groupby(group_cols, as_index=False)[vote_cols].sum()
    rows = []
    for row in grouped.to_dict("records"):
        scores = []
        for col in vote_cols:
            party = _party_from_previous_col(col, prefix) if prefix else _party_from_recent_col(col)
            scores.append((party, int(row.get(col, 0) or 0)))
        scores.sort(key=lambda item: item[1], reverse=True)
        winner_party, winner_votes = scores[0] if scores else ("-", 0)
        runner_party, runner_votes = scores[1] if len(scores) > 1 else ("-", 0)
        item = {
            "amphoe": row.get("amphoe", ""),
            "tambon": row.get("tambon", ""),
            "area_name": f"{row.get('amphoe', '')} / {row.get('tambon', '')}",
            "name": winner_party,
            "party": winner_party,
            "votes": winner_votes,
            "winner_votes": winner_votes,
            "runner_up_party": runner_party,
            "runner_up_votes": runner_votes,
            "margin_votes": winner_votes - runner_votes,
        }
        if level == "unit":
            item["unit"] = row.get("unit", "")
            item["area_name"] = f"{item['area_name']} / หน่วย {item['unit']}"
        rows.append(item)
    area_df = pd.DataFrame(rows)
    if level == "tambon":
        area_df = _add_map_positions(area_df)
        party_colors = _party_color_map(area_df["party"])
        area_df["fill_color"] = area_df["party"].map(party_colors).apply(lambda x: x if isinstance(x, list) else DEFAULT_FILL)
        area_df["radius"] = 3200
    return area_df

def _wide_summary(df):
    return {
        "eligible_voters": int(_to_number(df.get("eligible_voters", pd.Series(dtype=float))).sum()),
        "turnout": int(_to_number(df.get("turnout", pd.Series(dtype=float))).sum()),
        "valid_ballots": int(_to_number(df.get("valid_ballots", pd.Series(dtype=float))).sum()),
        "spoiled_ballots": int(_to_number(df.get("spoiled_ballots", pd.Series(dtype=float))).sum()),
        "abstain_ballots": int(_to_number(df.get("abstain_ballots", pd.Series(dtype=float))).sum()),
    }

def _format_turnout_rate(summary):
    eligible = summary.get("eligible_voters") or 0
    turnout = summary.get("turnout") or 0
    if not eligible:
        return "-"
    return f"{turnout / eligible * 100:.1f}%"

def _drop_impossible_rate_units(df):
    if not {"eligible_voters", "turnout"}.issubset(df.columns):
        return df.copy()
    out = df.copy()
    eligible = pd.to_numeric(out["eligible_voters"], errors="coerce")
    turnout = pd.to_numeric(out["turnout"], errors="coerce")
    turnout_rate = turnout / eligible.replace(0, np.nan)
    impossible_rate = turnout_rate.gt(1).fillna(False)
    if "spoiled_ballots" in out.columns:
        spoiled = pd.to_numeric(out["spoiled_ballots"], errors="coerce")
        spoiled_rate = spoiled / turnout.replace(0, np.nan)
        impossible_rate = impossible_rate | spoiled_rate.gt(1).fillna(False)
    return out[~impossible_rate].copy()

@st.cache_data
def load_wide_dashboard_data():
    recent_const_raw = _drop_impossible_rate_units(
        _normalize_wide_admin_columns(pd.read_csv(RECENT_CONSTITUENCY_WIDE_PATH), previous=False, form_type="constituency")
    )
    recent_pl_raw = _drop_impossible_rate_units(
        _normalize_wide_admin_columns(pd.read_csv(RECENT_PARTY_LIST_WIDE_PATH), previous=False, form_type="party_list")
    )
    prev_const_raw = _drop_impossible_rate_units(
        _normalize_wide_admin_columns(pd.read_csv(PREVIOUS_CONSTITUENCY_WIDE_PATH), previous=True, form_type="constituency")
    )
    prev_pl_raw = _drop_impossible_rate_units(
        _normalize_wide_admin_columns(pd.read_csv(PREVIOUS_PARTY_LIST_WIDE_PATH), previous=True, form_type="party_list")
    )

    recent_const_cols = _recent_vote_columns(recent_const_raw)
    recent_pl_cols = _recent_vote_columns(recent_pl_raw)
    prev_const_cols = _previous_vote_columns(prev_const_raw, "เขต_")
    prev_pl_cols = _previous_vote_columns(prev_pl_raw, "บช_")

    data = {
        "recent_const_raw": recent_const_raw,
        "recent_pl_raw": recent_pl_raw,
        "prev_const_raw": prev_const_raw,
        "prev_pl_raw": prev_pl_raw,
        "recent_const_totals": _wide_party_totals(recent_const_raw, recent_const_cols),
        "recent_pl_totals": _wide_party_totals(recent_pl_raw, recent_pl_cols),
        "prev_const_totals": _wide_party_totals(prev_const_raw, prev_const_cols, "เขต_"),
        "prev_pl_totals": _wide_party_totals(prev_pl_raw, prev_pl_cols, "บช_"),
        "recent_const_tambon": _wide_area_winners(recent_const_raw, recent_const_cols, level="tambon"),
        "recent_pl_tambon": _wide_area_winners(recent_pl_raw, recent_pl_cols, level="tambon"),
        "prev_const_tambon": _wide_area_winners(prev_const_raw, prev_const_cols, "เขต_", level="tambon"),
        "prev_pl_tambon": _wide_area_winners(prev_pl_raw, prev_pl_cols, "บช_", level="tambon"),
        "recent_const_units": _wide_area_winners(recent_const_raw, recent_const_cols, level="unit"),
        "recent_summary": _wide_summary(recent_const_raw),
        "recent_pl_summary": _wide_summary(recent_pl_raw),
        "prev_summary": _wide_summary(prev_const_raw),
        "prev_pl_summary": _wide_summary(prev_pl_raw),
    }
    return data

def make_tambon_winner_deck(area_df):
    map_df = area_df.dropna(subset=["lat", "lon"]).copy()
    live_party_colors = _party_color_map(map_df["party"])
    map_df["fill_color"] = map_df["party"].map(live_party_colors).apply(lambda x: x if isinstance(x, list) else DEFAULT_FILL)
    center_lat = float(map_df["lat"].mean()) if not map_df.empty else UBON_CENTER["lat"]
    center_lon = float(map_df["lon"].mean()) if not map_df.empty else UBON_CENTER["lon"]
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        pickable=True,
        opacity=0.9,
        stroked=True,
        filled=True,
        radius_scale=1,
        radius_min_pixels=8,
        radius_max_pixels=22,
        line_width_min_pixels=2,
        get_position="[lon, lat]",
        get_fill_color="fill_color",
        get_line_color=DEFAULT_LINE,
        get_radius="radius",
    )
    tooltip = {
        "html": (
            "<div style='font-size:13px'>"
            "<div><b>{area_name}</b></div>"
            "<div>Winner: <b>{name}</b></div>"
            "<div>Party: <b>{party}</b></div>"
            "<div>Winner votes: {winner_votes}</div>"
            "</div>"
        ),
        "style": {"backgroundColor": "#131921", "color": "#f6f6f6", "padding": "10px 12px"},
    }
    return pdk.Deck(
        layers=[layer],
        map_style=None,
        initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=9.2, pitch=0),
        tooltip=tooltip,
    )

def make_tambon_boundary_deck(area_df, party_colors):
    boundary_geojson = load_ubon_tambon_boundaries()
    if not boundary_geojson:
        return None, 0

    live_party_colors = _party_color_map(area_df["party"])
    result_by_exact = {}
    for row in area_df.to_dict("records"):
        amphoe_key, tambon_key = _area_match_keys(row)
        result_by_exact[(amphoe_key, tambon_key)] = row

    features = []
    for feature in boundary_geojson.get("features", []):
        props = dict(feature.get("properties", {}))
        official_amphoe = str(props.get("NAME2", "")).strip()
        official_tambon = str(props.get("NAME3", "")).strip()
        amphoe_key = _clean_thai_admin_name(official_amphoe)
        tambon_key = _clean_thai_admin_name(official_tambon)
        result = result_by_exact.get((amphoe_key, tambon_key))
        if result is None:
            continue

        fill = live_party_colors.get(str(result.get("party")), DEFAULT_FILL)
        props.update(
            {
                "province_name": UBON2_PROVINCE,
                "amphoe_name": official_amphoe,
                "tambon_name": official_tambon,
                "winner_name": result.get("name", "-"),
                "winner_party": result.get("party", "-"),
                "winner_votes": int(result.get("winner_votes", result.get("votes", 0)) or 0),
                "fill_r": fill[0],
                "fill_g": fill[1],
                "fill_b": fill[2],
                "fill_a": 175,
                "line_r": DEFAULT_LINE[0],
                "line_g": DEFAULT_LINE[1],
                "line_b": DEFAULT_LINE[2],
                "line_a": 225,
            }
        )
        features.append(
            {
                "type": "Feature",
                "properties": props,
                "geometry": feature.get("geometry"),
            }
        )

    if not features:
        return None, 0

    min_x, min_y, max_x, max_y = _geojson_feature_bounds(features)
    center_lon = (min_x + max_x) / 2
    center_lat = (min_y + max_y) / 2

    layer = pdk.Layer(
        "GeoJsonLayer",
        id="ubon2-tambon-winners",
        data={"type": "FeatureCollection", "features": features},
        pickable=True,
        auto_highlight=True,
        stroked=True,
        filled=True,
        get_fill_color="[properties.fill_r, properties.fill_g, properties.fill_b, properties.fill_a]",
        get_line_color="[properties.line_r, properties.line_g, properties.line_b, properties.line_a]",
        line_width_min_pixels=1,
    )
    tooltip = {
        "html": (
            "<div style='font-size:13px'>"
            "<div><b>{tambon_name}</b></div>"
            "<div>{amphoe_name}, {province_name}</div>"
            "<hr/>"
            "<div>Winner: <b>{winner_name}</b></div>"
            "<div>Party: <b>{winner_party}</b></div>"
            "<div>Winner votes: {winner_votes}</div>"
            "</div>"
        ),
        "style": {"backgroundColor": "#131921", "color": "#f6f6f6", "padding": "10px 12px"},
    }
    return (
        pdk.Deck(
            layers=[layer],
            map_style=None,
            initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=9.1, pitch=0),
            tooltip=tooltip,
        ),
        len(features),
    )

def make_tambon_winner_treemap(area_df):
    view = area_df.copy()
    view["winner_label"] = view["name"].astype(str) + " / " + view["party"].astype(str)
    fig = px.treemap(
        view,
        path=["party", "area_name"],
        values="votes",
        color="party",
        color_discrete_map=_plotly_party_color_map(view["party"]),
        hover_data={
            "name": True,
            "party": True,
            "votes": ":,",
            "area_name": False,
            "winner_label": False,
        },
        labels={"votes": "Winner votes", "party": "Party"},
    )
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{value:,} votes",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Party: %{customdata[1]}<br>"
            "Candidate: %{customdata[0]}<br>"
            "Winner votes: %{value:,}<extra></extra>"
        ),
    )
    fig.update_layout(height=560, margin={"r": 0, "t": 10, "l": 0, "b": 0})
    return fig

def render_ubon2_recent_page(candidate_df, area_df, summary, source_label, party_colors):
    st.header("อุบลราชธานี เขต 2: Recent Election Result")
    st.caption(f"Current source: {source_label}")

    winner, runner_up, margin, margin_pct = get_top_two_metrics(candidate_df)
    if winner is None:
        st.warning("No Ubon 2 recent results available.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall winner", str(winner["name"]), str(winner["party"]))
    col2.metric("Winner votes", f"{int(winner['votes']):,}", f"{winner['vote_share']:.1f}% of candidate votes")
    col3.metric("Margin", f"{margin:,}", f"{margin_pct:.1f}% of winner votes")
    col4.metric("Reported areas", f"{len(area_df):,}", "tambon rows when real data arrives")

    st.divider()
    map_col, table_col = st.columns([1.25, 1])
    with map_col:
        st.subheader("Winner by Tambon")
        party_colors = _party_color_map(area_df["party"])
        render_party_legend(party_colors)
        boundary_deck, boundary_count = make_tambon_boundary_deck(area_df, party_colors)
        if boundary_deck is not None:
            st.pydeck_chart(boundary_deck, height=560, width="stretch")
            st.caption("Hover each tambon polygon to see the winner, party, and vote total.")
        elif {"lat", "lon"}.issubset(area_df.columns):
            geo_mask = ~area_df[["lat", "lon"]].isna().any(axis=1)
            if bool(geo_mask.any()):
                st.pydeck_chart(make_tambon_winner_deck(area_df), height=560, width="stretch")
                st.caption("Dots are tambon centroids. Hover each dot to see the tambon winner, party, and vote total.")
                missing_count = int((~geo_mask).sum())
                if missing_count:
                    st.warning(f"{missing_count} tambon result(s) do not have coordinates and are not shown on the map.")
            else:
                st.plotly_chart(make_tambon_winner_treemap(area_df), width="stretch")
                st.caption("No tambon coordinates or boundaries are available, so this is a tambon winner treemap rather than a geographic map.")
        else:
            geo_mask = pd.Series(False, index=area_df.index)
            st.plotly_chart(make_tambon_winner_treemap(area_df), width="stretch")
            st.caption("No tambon coordinates or boundaries are available, so this is a tambon winner treemap rather than a geographic map.")
        if len(area_df) == 1 and area_df.iloc[0]["area_name"] == "OCR constituency total":
            st.info("The current OCR JSON has only constituency-level totals. This map will automatically split by tambon when a real row-level CSV with `tambon` arrives.")

    with table_col:
        st.subheader("Candidate Ranking")
        ranking = candidate_df[["rank", "number", "name", "party", "votes", "vote_share"]].copy()
        ranking["vote_share"] = ranking["vote_share"].round(2)
        st.dataframe(
            ranking.rename(columns={
                "rank": "Rank",
                "number": "No.",
                "name": "Candidate",
                "party": "Party",
                "votes": "Votes",
                "vote_share": "Vote share %",
            }),
            hide_index=True,
            width="stretch",
        )

    st.divider()
    stat1, stat2, stat3, stat4 = st.columns(4)
    stat1.metric("Eligible voters", f"{summary['eligible_voters']:,}" if summary.get("eligible_voters") else "-")
    stat2.metric("Turnout / ballots used", f"{summary['turnout']:,}" if summary.get("turnout") else "-")
    stat3.metric("Valid ballots", f"{summary['valid_ballots']:,}" if summary.get("valid_ballots") else "-")
    stat4.metric("Spoiled + abstain", f"{(summary.get('spoiled_ballots') or 0) + (summary.get('abstain_ballots') or 0):,}")

def render_tambon_map_page(title, totals_df, area_df, summary, source_label):
    st.header(title)
    st.caption(source_label)
    winner, _, margin, margin_pct = get_top_two_metrics(totals_df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall winner", str(winner["party"]), f"{int(winner['votes']):,} votes")
    col2.metric("Margin", f"{margin:,}", f"{margin_pct:.1f}%")
    col3.metric("Tambons", f"{len(area_df):,}")
    col4.metric("Turnout", f"{summary.get('turnout', 0):,}")

    st.divider()
    party_colors = _party_color_map(area_df["party"])
    render_party_legend(party_colors)
    boundary_deck, _ = make_tambon_boundary_deck(area_df, party_colors)
    if boundary_deck is not None:
        st.pydeck_chart(boundary_deck, height=680, width="stretch")
        st.caption("Hover each tambon polygon to see the winner, party, and vote total.")
    elif {"lat", "lon"}.issubset(area_df.columns) and bool((~area_df[["lat", "lon"]].isna().any(axis=1)).any()):
        st.pydeck_chart(make_tambon_winner_deck(area_df), height=680, width="stretch")
    else:
        st.plotly_chart(make_tambon_winner_treemap(area_df), width="stretch")

def render_tambon_map_card(area_df, height=620):
    party_colors = _party_color_map(area_df["party"])
    render_party_legend(party_colors)
    boundary_deck, _ = make_tambon_boundary_deck(area_df, party_colors)
    if boundary_deck is not None:
        st.pydeck_chart(boundary_deck, height=height, width="stretch")
    elif {"lat", "lon"}.issubset(area_df.columns) and bool((~area_df[["lat", "lon"]].isna().any(axis=1)).any()):
        st.pydeck_chart(make_tambon_winner_deck(area_df), height=height, width="stretch")
    else:
        st.plotly_chart(make_tambon_winner_treemap(area_df), width="stretch")

def render_map_comparison_page(wide_data):
    st.header("อุบลราชธานี เขต 2: เปรียบเทียบแผนที่รายตำบล")
    ballot_type = st.radio(
        "เลือกประเภทบัตร",
        ["แบ่งเขต", "บัญชีรายชื่อ"],
        horizontal=True,
        key="map_ballot_type",
    )
    if ballot_type == "บัญชีรายชื่อ":
        recent_totals_key = "recent_pl_totals"
        prev_totals_key = "prev_pl_totals"
        recent_tambon_key = "recent_pl_tambon"
        prev_tambon_key = "prev_pl_tambon"
        recent_summary_key = "recent_pl_summary"
        prev_summary_key = "prev_pl_summary"
    else:
        recent_totals_key = "recent_const_totals"
        prev_totals_key = "prev_const_totals"
        recent_tambon_key = "recent_const_tambon"
        prev_tambon_key = "prev_const_tambon"
        recent_summary_key = "recent_summary"
        prev_summary_key = "prev_summary"

    recent_winner, _, recent_margin, recent_margin_pct = get_top_two_metrics(wide_data[recent_totals_key])
    prev_winner, _, prev_margin, prev_margin_pct = get_top_two_metrics(wide_data[prev_totals_key])
    recent_turnout_rate = _format_turnout_rate(wide_data[recent_summary_key])
    prev_turnout_rate = _format_turnout_rate(wide_data[prev_summary_key])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ปีนี้", str(recent_winner["party"]), f"{int(recent_winner['votes']):,} votes")
    m2.metric("Turnout rate ปีนี้", recent_turnout_rate)
    m3.metric("ปี66", str(prev_winner["party"]), f"{int(prev_winner['votes']):,} votes")
    m4.metric("Turnout rate ปี66", prev_turnout_rate)

    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader("ปีนี้")
        render_tambon_map_card(wide_data[recent_tambon_key], height=650)
    with right:
        st.subheader("ปี66")
        render_tambon_map_card(wide_data[prev_tambon_key], height=650)
    st.caption("Hover each tambon polygon to see the winner, party, and vote total. Colors use the party color mapping in the dashboard.")

def render_grouped_bar_page(recent_const_totals, recent_pl_totals):
    st.header("แบ่งเขต vs บัญชีรายชื่อ")
    const = recent_const_totals[["party", "votes"]].rename(columns={"votes": "แบ่งเขต"})
    pl = recent_pl_totals[["party", "votes"]].rename(columns={"votes": "บัญชีรายชื่อ"})
    merged = const.merge(pl, on="party", how="outer").fillna(0)
    merged["total"] = merged["แบ่งเขต"] + merged["บัญชีรายชื่อ"]
    top_parties = merged.sort_values("total", ascending=False).head(12)["party"].tolist()
    chart_df = merged[merged["party"].isin(top_parties)].melt(
        id_vars=["party"],
        value_vars=["แบ่งเขต", "บัญชีรายชื่อ"],
        var_name="ballot_type",
        value_name="votes",
    )
    fig = px.bar(
        chart_df,
        x="party",
        y="votes",
        color="ballot_type",
        barmode="group",
        category_orders={"party": top_parties},
        labels={"votes": "Votes", "party": "Party", "ballot_type": ""},
        color_discrete_map={"แบ่งเขต": "#2563EB", "บัญชีรายชื่อ": "#16A34A"},
    )
    fig.update_layout(height=620, margin={"r": 20, "t": 10, "l": 0, "b": 80})
    fig.update_xaxes(tickangle=-35)
    st.plotly_chart(fig, width="stretch")

def render_unit_treemap_page(unit_df):
    st.header("หน่วยเลือกตั้ง: Treemap")
    view = unit_df.copy()
    view["unit_label"] = "หน่วย " + view["unit"].astype(str)
    render_party_legend(_party_color_map(view["party"]))
    fig = px.treemap(
        view,
        path=["amphoe", "tambon", "unit_label"],
        values="winner_votes",
        color="party",
        color_discrete_map=_plotly_party_color_map(view["party"]),
        hover_data={"party": True, "winner_votes": ":,", "margin_votes": ":,"},
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Winner: %{customdata[0]}<br>"
            "Winner votes: %{customdata[1]:,}<br>"
            "Margin: %{customdata[2]:,}<extra></extra>"
        )
    )
    fig.update_layout(height=760, margin={"r": 0, "t": 10, "l": 0, "b": 0})
    st.plotly_chart(fig, width="stretch")

def render_unit_sunburst_page(unit_df):
    st.header("หน่วยเลือกตั้ง: Sunburst")
    view = unit_df.copy()
    view["unit_label"] = "หน่วย " + view["unit"].astype(str)
    render_party_legend(_party_color_map(view["party"]))
    fig = px.sunburst(
        view,
        path=["amphoe", "tambon", "unit_label"],
        values="winner_votes",
        color="party",
        color_discrete_map=_plotly_party_color_map(view["party"]),
        hover_data={"party": True, "winner_votes": ":,", "margin_votes": ":,"},
    )
    fig.update_layout(height=760, margin={"r": 0, "t": 10, "l": 0, "b": 0})
    st.plotly_chart(fig, width="stretch")

def render_ubon2_comparison_page(recent_df, recent_party_list_df, historical_df, historical_party_list_df):
    st.header("เปรียบเทียบกับปี66")
    ballot_type = st.radio(
        "เลือกประเภทบัตร",
        ["แบ่งเขต", "บัญชีรายชื่อ"],
        horizontal=True,
        key="dumbbell_ballot_type",
    )
    if ballot_type == "บัญชีรายชื่อ":
        selected_recent = recent_party_list_df
        selected_historical = historical_party_list_df
        previous_label = "Previous party-list votes"
        chart_title = "ปี66 vs ปีนี้: บัญชีรายชื่อ"
        subheader = "บัญชีรายชื่อ: Top 10"
    else:
        selected_recent = recent_df
        selected_historical = historical_df
        previous_label = "Previous constituency votes"
        chart_title = "ปี66 vs ปีนี้: แบ่งเขต"
        subheader = "แบ่งเขต: Top 10"

    recent_winner, _, recent_margin, recent_margin_pct = get_top_two_metrics(selected_recent)
    hist_winner, _, hist_margin, hist_margin_pct = get_top_two_metrics(selected_historical)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ผู้ชนะปีนี้", str(recent_winner["party"]), f"{int(recent_winner['votes']):,} votes")
    c2.metric("ผู้ชนะปี66", str(hist_winner["party"]), f"{int(hist_winner['votes']):,} votes")
    c3.metric("ส่วนต่างปีนี้", f"{recent_margin:,}", f"{recent_margin_pct:.1f}%")
    c4.metric("ส่วนต่างปี66", f"{hist_margin:,}", f"{hist_margin_pct:.1f}%")

    st.divider()
    st.subheader(subheader)
    comparison_display = build_party_comparison(selected_recent, selected_historical, top_n=10)
    st.plotly_chart(
        make_dumbbell_chart(comparison_display, chart_title),
        width="stretch",
    )

    st.divider()
    st.subheader("Comparison Table")
    st.dataframe(
        comparison_display.sort_values("recent_votes", ascending=False).rename(columns={
            "party": "Party",
            "recent_votes": "Recent votes",
            "previous_votes": previous_label,
            "change": "Change",
        }),
        hide_index=True,
        width="stretch",
    )

def render_ubon2_metrics_page(candidate_df, party_list_df, constituency_summary, party_list_summary):
    st.header("อุบลราชธานี เขต 2: Metrics")

    const_total = int(candidate_df["votes"].sum())
    pl_total = int(party_list_df["votes"].sum())
    const_valid = constituency_summary.get("valid_ballots") or 0
    pl_valid = party_list_summary.get("valid_ballots") or 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Constituency candidate votes", f"{const_total:,}", f"valid ballots: {const_valid:,}" if const_valid else None)
    m2.metric("Party-list votes in table", f"{pl_total:,}", f"valid ballots: {pl_valid:,}" if pl_valid else None)
    m3.metric("Constituency spoiled + abstain", f"{(constituency_summary.get('spoiled_ballots') or 0) + (constituency_summary.get('abstain_ballots') or 0):,}")
    m4.metric("Party-list spoiled + abstain", f"{(party_list_summary.get('spoiled_ballots') or 0) + (party_list_summary.get('abstain_ballots') or 0):,}")

    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader("Constituency Vote Share")
        fig = px.bar(
            candidate_df.head(10),
            x="votes",
            y="name",
            color="party",
            orientation="h",
            category_orders={"name": candidate_df.head(10)["name"].tolist()[::-1]},
            labels={"votes": "Votes", "name": "Candidate", "party": "Party"},
            color_discrete_map=_plotly_party_color_map(candidate_df["party"]),
        )
        fig.update_layout(height=520, margin={"r": 0, "t": 10, "l": 0, "b": 0})
        st.plotly_chart(fig, width="stretch")

    with right:
        st.subheader("Party-list Vote Share")
        fig = px.bar(
            party_list_df.head(15),
            x="votes",
            y="party",
            color="party",
            orientation="h",
            category_orders={"party": party_list_df.head(15)["party"].tolist()[::-1]},
            labels={"votes": "Votes", "party": "Party"},
            color_discrete_map=_plotly_party_color_map(party_list_df["party"]),
        )
        fig.update_layout(height=520, margin={"r": 0, "t": 10, "l": 0, "b": 0})
        st.plotly_chart(fig, width="stretch")

    st.divider()
    st.subheader("Validation Snapshot")
    validation = pd.DataFrame([
        {"Ballot type": "Constituency", **constituency_summary},
        {"Ballot type": "Party list", **party_list_summary},
    ])
    st.dataframe(validation, hide_index=True, width="stretch")

@st.cache_data
def load_geojson():
    # Public GeoJSON for Thai Provinces
    url = "https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        geojson = response.json()
        for feature in geojson.get('features', []):
            props = feature.setdefault('properties', {})
            raw_name = str(props.get('name', '')).strip()
            props['thai_name'] = GEOJSON_PROVINCE_ALIASES.get(raw_name, raw_name)
        return geojson
    except:
        return None

def add_district_coordinates(df):
    district_df = df.copy()
    max_constituencies = district_df.groupby('province')['constituency'].transform('max').replace(0, 1)
    angles = 2 * np.pi * (district_df['constituency'] - 1) / max_constituencies
    ring = 0.18 + 0.42 * (district_df['constituency'] / max_constituencies)
    province_for_coords = district_df['province'].replace(PROVINCE_ALIASES)
    coords = province_for_coords.map(PROVINCE_COORDS)

    district_df['lat'] = coords.apply(lambda x: x[0] if isinstance(x, list) else np.nan)
    district_df['lon'] = coords.apply(lambda x: x[1] if isinstance(x, list) else np.nan)
    district_df['lat'] = district_df['lat'] + np.sin(angles) * ring
    district_df['lon'] = district_df['lon'] + np.cos(angles) * ring
    district_df['district_id'] = district_df['province'] + " เขต " + district_df['constituency'].astype(str)
    return district_df.dropna(subset=['lat', 'lon'])

def build_party_colors(df, winner_col, margin_col):
    parties = (
        df.groupby(winner_col, as_index=False)
        .agg(districts=(winner_col, 'size'), margin_total=(margin_col, 'sum'))
        .sort_values(['districts', 'margin_total'], ascending=[False, False])[winner_col]
        .tolist()
    )
    return {party: PARTY_PALETTE[idx % len(PARTY_PALETTE)] for idx, party in enumerate(parties)}

def add_party_colors(df, winner_col, margin_col, party_colors):
    map_df = df.copy()
    max_margin = max(float(map_df[margin_col].max()), 1.0)
    map_df['fill_color'] = map_df[winner_col].map(party_colors).apply(lambda x: x if isinstance(x, list) else DEFAULT_FILL)
    map_df['line_color'] = [[255, 255, 255, 230]] * len(map_df)
    map_df['radius'] = 12000 + (map_df[margin_col] / max_margin) * 26000
    map_df['winner_party'] = map_df[winner_col]
    map_df['winner_margin'] = map_df[margin_col].astype(int)
    map_df['candidate_label'] = map_df['Candidate'].fillna('-') if winner_col == 'Const_Winner' else '-'
    return map_df

def geojson_bounds(geojson):
    xs = []
    ys = []

    def visit(coords):
        if not coords:
            return
        if isinstance(coords[0], (int, float)):
            xs.append(float(coords[0]))
            ys.append(float(coords[1]))
            return
        for child in coords:
            visit(child)

    for feature in geojson.get('features', []):
        geometry = feature.get('geometry') or {}
        visit(geometry.get('coordinates'))

    if not xs or not ys:
        return 97.0, 5.5, 106.0, 20.5
    return min(xs), min(ys), max(xs), max(ys)

def build_province_winner_summary(map_df):
    province_map_df = map_df.copy()
    province_map_df['province_for_map'] = province_map_df['province'].replace(PROVINCE_ALIASES)
    rows = []
    for province, group in province_map_df.groupby('province_for_map'):
        const_counts = group['Const_Winner'].value_counts()
        pl_counts = group['PL_Winner'].value_counts()
        const_winner = const_counts.index[0] if not const_counts.empty else 'ไม่มีข้อมูล'
        pl_winner = pl_counts.index[0] if not pl_counts.empty else 'ไม่มีข้อมูล'
        rows.append(
            {
                'province_for_map': province,
                'const_winner': const_winner,
                'const_winner_districts': int(const_counts.iloc[0]) if not const_counts.empty else 0,
                'pl_winner': pl_winner,
                'pl_winner_districts': int(pl_counts.iloc[0]) if not pl_counts.empty else 0,
                'total_districts': int(len(group)),
                'split_districts': int(group['is_split'].sum()),
                'avg_const_margin': int(group['Const_Margin'].mean()) if not group.empty else 0,
                'avg_pl_margin': int(group['PL_Margin'].mean()) if not group.empty else 0,
            }
        )
    return pd.DataFrame(rows)

def attach_province_colors(geojson, province_summary, color_col, party_colors):
    summary_by_province = {
        row['province_for_map']: row
        for row in province_summary.to_dict('records')
    }
    features = []
    selected_provinces = set(province_summary['province_for_map'].unique())
    for feature in geojson.get('features', []):
        props = dict(feature.get('properties', {}))
        province = str(props.get('thai_name') or props.get('name', '')).strip()
        result = summary_by_province.get(province)
        winner = result[color_col] if result else 'ไม่มีข้อมูล'
        fill = party_colors.get(winner, DEFAULT_FILL)
        if selected_provinces and province not in selected_provinces:
            fill = [210, 214, 222, 35]

        props.update(
            {
                'province_name': province,
                'const_winner': result['const_winner'] if result else 'ไม่มีข้อมูล',
                'const_winner_districts': result['const_winner_districts'] if result else 0,
                'pl_winner': result['pl_winner'] if result else 'ไม่มีข้อมูล',
                'pl_winner_districts': result['pl_winner_districts'] if result else 0,
                'total_districts': result['total_districts'] if result else 0,
                'split_districts': result['split_districts'] if result else 0,
                'avg_const_margin': result['avg_const_margin'] if result else 0,
                'avg_pl_margin': result['avg_pl_margin'] if result else 0,
                'fill_r': fill[0],
                'fill_g': fill[1],
                'fill_b': fill[2],
                'fill_a': 85 if winner != 'ไม่มีข้อมูล' else fill[3],
                'line_r': DEFAULT_LINE[0],
                'line_g': DEFAULT_LINE[1],
                'line_b': DEFAULT_LINE[2],
                'line_a': DEFAULT_LINE[3],
            }
        )
        features.append({'type': 'Feature', 'properties': props, 'geometry': feature.get('geometry')})
    return {'type': 'FeatureCollection', 'features': features}

def make_area_winner_map(map_df, thailand_geojson, winner_col, margin_col):
    if not thailand_geojson:
        return None, {}

    party_colors = build_party_colors(map_df, winner_col, margin_col)
    province_summary = build_province_winner_summary(map_df)
    color_col = 'const_winner' if winner_col == 'Const_Winner' else 'pl_winner'
    province_geojson = attach_province_colors(thailand_geojson, province_summary, color_col, party_colors)
    layer = pdk.Layer(
        'GeoJsonLayer',
        id='area-winners',
        data=province_geojson,
        pickable=True,
        auto_highlight=True,
        stroked=True,
        filled=True,
        get_fill_color='[properties.fill_r, properties.fill_g, properties.fill_b, properties.fill_a]',
        get_line_color='[properties.line_r, properties.line_g, properties.line_b, properties.line_a]',
        line_width_min_pixels=1,
    )

    min_x, min_y, max_x, max_y = geojson_bounds(thailand_geojson)
    center_lon = (min_x + max_x) / 2
    center_lat = (min_y + max_y) / 2

    tooltip = {
        'html': (
            "<div style='font-size:13px'>"
            "<div><b>{province_name}</b></div>"
            "<hr/>"
            "<div>Constituency winner: <b>{const_winner}</b></div>"
            "<div>Constituency districts won: {const_winner_districts}/{total_districts}</div>"
            "<div>Avg constituency margin: {avg_const_margin}</div>"
            "<br/>"
            "<div>Party-list winner: <b>{pl_winner}</b></div>"
            "<div>Party-list districts won: {pl_winner_districts}/{total_districts}</div>"
            "<div>Avg party-list margin: {avg_pl_margin}</div>"
            "<div>Split districts: {split_districts}</div>"
            "</div>"
        ),
        'style': {
            'backgroundColor': '#131921',
            'color': '#f6f6f6',
            'padding': '10px 12px',
        },
    }

    return (
        pdk.Deck(
            layers=[layer],
            map_style=None,
            initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=4.6, pitch=0),
            tooltip=tooltip,
        ),
        party_colors,
    )

def render_party_legend(party_colors):
    if not party_colors:
        return
    chips = []
    for party, color in party_colors.items():
        chips.append(
            f"<span style='display:inline-flex;align-items:center;gap:6px;margin:0 10px 8px 0;'>"
            f"<span style='width:12px;height:12px;border-radius:2px;background:rgba({color[0]},{color[1]},{color[2]},0.95);display:inline-block;'></span>"
            f"{party}</span>"
        )
    st.markdown("".join(chips), unsafe_allow_html=True)

try:
    wide_data = load_wide_dashboard_data()
except Exception as e:
    st.error(f"Error loading data: {e}.")
    st.stop()

st.sidebar.header("Scope")
st.sidebar.info("All pages are scoped to อุบลราชธานี เขต 2.")
st.sidebar.caption(f"Recent constituency: {RECENT_CONSTITUENCY_WIDE_PATH}")
st.sidebar.caption(f"Recent party-list: {RECENT_PARTY_LIST_WIDE_PATH}")
st.sidebar.caption(f"Previous constituency: {PREVIOUS_CONSTITUENCY_WIDE_PATH}")
st.sidebar.caption(f"Previous party-list: {PREVIOUS_PARTY_LIST_WIDE_PATH}")

# Main Tabs
main_tab1, main_tab2, main_tab3, main_tab4, main_tab5, main_tab6, main_tab7 = st.tabs([
    "เปรียบเทียบแผนที่",
    "เปรียบเทียบกับปี66",
    "แบ่งเขต vs บช",
    "Treemap หน่วย",
    "Sunburst หน่วย",
    "Raw Data",
    "Summary",
])

# --- TAB 1: Map Comparison ---
with main_tab1:
    render_map_comparison_page(wide_data)

# --- TAB 2: Dumbbell ---
with main_tab2:
    render_ubon2_comparison_page(
        wide_data["recent_const_totals"],
        wide_data["recent_pl_totals"],
        wide_data["prev_const_totals"],
        wide_data["prev_pl_totals"],
    )

# --- TAB 3: Grouped Bar ---
with main_tab3:
    render_grouped_bar_page(wide_data["recent_const_totals"], wide_data["recent_pl_totals"])

# --- TAB 4: Unit Treemap ---
with main_tab4:
    render_unit_treemap_page(wide_data["recent_const_units"])

# --- TAB 5: Unit Sunburst ---
with main_tab5:
    render_unit_sunburst_page(wide_data["recent_const_units"])

# --- TAB 6: Raw Data ---
with main_tab6:
    st.header("อุบลราชธานี เขต 2: Raw Data")
    raw_tab1, raw_tab2, raw_tab3, raw_tab4 = st.tabs(["Recent Constituency", "Recent Party-list", "Previous Constituency", "Previous Party-list"])
    with raw_tab1:
        st.dataframe(wide_data["recent_const_raw"], hide_index=True, width="stretch")
    with raw_tab2:
        st.dataframe(wide_data["recent_pl_raw"], hide_index=True, width="stretch")
    with raw_tab3:
        st.dataframe(wide_data["prev_const_raw"], hide_index=True, width="stretch")
    with raw_tab4:
        st.dataframe(wide_data["prev_pl_raw"], hide_index=True, width="stretch")

# --- TAB 7: Summary ---
with main_tab7:
    render_tambon_map_page(
        "อุบลราชธานี เขต 2: แผนที่ผู้ชนะรายตำบล ปีนี้",
        wide_data["recent_const_totals"],
        wide_data["recent_const_tambon"],
        wide_data["recent_summary"],
        f"Source: {RECENT_CONSTITUENCY_WIDE_PATH}",
    )
