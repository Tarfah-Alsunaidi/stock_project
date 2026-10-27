"""
Nabd Tadawul — an interactive story of the Saudi stock market (2022 – 2025)
Three services: Market Today (live) · Historical Analysis · Developer Corner
Light / dark mode · English / العربية
Author : Tarfah Alsunaidi
Run    : streamlit run app.py
"""

import base64
import json
import io
from datetime import datetime
from itertools import count
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from plotly.subplots import make_subplots

try:                                  
    import yfinance as yf
except ImportError:
    yf = None

_CFG = Path(__file__).parent / ".streamlit" / "config.toml"
if not _CFG.exists():
    try:
        _CFG.parent.mkdir(exist_ok=True)
        _CFG.write_text('[theme]\nbase = "light"\nprimaryColor = "#2F6F62"\nbackgroundColor = "#F6F2EA"\n'
                        'secondaryBackgroundColor = "#FFFDF8"\ntextColor = "#24303A"\nfont = "sans serif"\n\n'
                        '[client]\ntoolbarMode = "minimal"\n')
    except OSError:
        pass


FAVICON_B64 = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAANRUlEQVR4AexZDXBU1RU+971NAgFNwKKCgChSK8g0QgKCIKBQEEu0U0lFBxHrgAKCTBWwOvDSqfKjAyih/DhKbR2wQQUClSAOARTQJIgJ1lrEmtaCfx0IQkKy7/70u2/fbnaz+5LND4FMXd7dc8859+/7zrn3vg0G/Z9/fiCgVSdAgeW7ON8ak7oj20rZkb0kNT97eUq+tSplh/USbK9CbkzNt7ak5Gfnp+zI3oXy+/Y7rEvDMbfqDEj1sycNxrYD0AJG9DgxmsUYe4gRewC2eyHvIsYyGaPRjGgEypMmsUfhCz2tmgClaFAISdwVNTC8aasmAEAKUBr6FIZ3aNUEnPr+uucUU6MBKNtg5h99pu+4aZp+FNswDI4iFCm4I56d4VqrJoCyskSHi1KOtGvb5trkpIQ7E3xG+0TT8PsMw59gmjYjEoxYCC+2TPUp0XFfyIBKqyWgR4GVeuV7z/5O2P5igBit48wYc+LNmJaKpFLvAGPNw2gvjZ1ZXWMgQt9wtRXUcfX12P/cFEpo/wGReogQYUQW39AAnxGkUnk+Yf5EKlkJNfyJSH/taFUE9Hx/6d1XJ120jxHLBsxUcmEzBo2ImGJHSBq3f3PLb+85PnLulzCPpLAPM1hkRsB3wRMwXuWaPz6w/FfXHFi6Dzn9HEB1DcDF6slJfP39LbRHj++uGvjVrfP2ok4pO7P7EzGQRO5HlZePmn/IVULigiVgPID3Lnw+q6TwWAEZajGC3Y0xRpI0aHf9ilUj7Mtkcmq/Y8PmvkKWJV2P5mh4qI6KIsqHiHouOAKu+zDnyt7FKx77uPjrd4FmISPWTWOG1AKHFtPggEe9ybjK+HLo3KePp0+tvdcBlCXhK/SgV9T+184LgoCB779w8fUHc7L6frhiPZNyBwI9BYvrhKhDEDFmALwigNAZsI1JNrxsyJyHy0bM+Zo8PtxgeWDquHYrom/KE2m9rtcu542AQfuXtk0rXT027aM/5FQlmXsAeoEilmYwgHWPdS0IH6WUZIxtJsmHfTH4san/HPqbIzDX+VSMmn9YKuorFLv5VLs2vWiEVaU71C4tSsBwVeDLKF19c3rp6kXV7druwuTPIKxDiTGfXhgj7HGFxNcKCn7olCul1jJePeSzgbNnHr1pzucwRz2p260eqfnZOU5BPdjg+zHWidNj5r9LQ+aeDtpqS6yhtqn59XHFa5KHffjiBP9Hn200yFykGI1ERJMUQqRBI7+JGBIWFQMZAPEpY+pJO5UGH7lx9sJ/DJnrpDJ5fQxmof90p+i6V7sY9nNKwHik+cgP1t1TyRJeRnpPZMxIUdjFDEcZIkvMYMCqiBgBPStnZLzClBr/ScbMzE/6z8o92ivyrY08Phjh+qBLkeoTrMcjzwkBlrKMzPdfGXGGdVxiGurnAJvIgBILxTf2uCaBMVzrsoop2g70Dx8+uvvmw/2mLT6c/sjheBbeXG2anYBf7lnXq2T/1U9IocYzxtpJqZfKnEgzVJUGT+zvUhlPm7Z5y6G0afNK0qa/R1kbBdwt/jQbAfcXrGszoWD9nSZLmAy0l+CnKMAoMpwZnNjb+N7hYzSxuO/UiYd+OuWNg+mx7m90a8HHWV5T53tgV+61XCY+yEzWVyLkBhJdSz0uVE3CZhxuk/anPbh4f9+pn2t7U0u/ktXj0kvXFPYvWV3Rq/Nl/Xtefhn17HwZXXP55enppasr+pWuKsxAm/rmMeprUJd/Wm5u+yk7c2+XSv7MMM22hPTWkdevqwCMM169l+hPmv5Ov1//afcNk8vrGiteX++PV7bvd2jVWqVknhAiAzJZCMyoJElXQk/GDZPBpczTbXUfr/EbRYBlWcYjb+X2Vh3MTE6iix4kEHGDtDQY+48ktXD7jZNf/uvQe096Td4Ye9squ6NUYlIArCKAJYU0c6Sq0UN+Ke7Tfbzm0mv38sWyszlbtnQ50b/PCMVYHyWEaeJKk8HIC+nHcbf1jZsmLts2eNKxWAM01cbJHCuFTFQSswrhgIfuSleHL8yfpPt4zWt4OWrbn3jzzUsAvr8g0cc0WbLjR2+BigESlJCfCkpYuXH4pAMwKRTPZ+GqDT2W5GzI0UXXPRvGcAgu0hQ2VwA07hQn7V1Z2+7qUoi0GEM5JkBwZMwvnerWpk2pT72+tZdPqauV8rcl56XVbS6JTKlOK5/a/Odb79m6cUTWGddTp/AJshij6broOjXgo6Rk2PtOxOOX3vGIRQBbs2ZNwuKXtlzUtu+ALmQbP2I+0cbGIn2+BCLOUQs8TBklL46++7V1wyZ8GbDE+c1U2JsbNejNzdnriGxDpD6XvFYWRYBVUGDyDh2SzEsvdn5PJyVB+IkS8C+A3UfSpn8lnFbbVt12V6nXwOfKrsEgpZEBOu0FZPAs8NYVzgqv9RhRjj3a0onodCCbq6urKSGRkAhCmox95U9os/f5O+4qXZaVdVa3bOmihAJohStPg4eUMqDLWjpAK2SKQxi2qtc6owkYFtnU19Y4K/3+Y21KSkoW3XHH0RVjx1ZHtmhZTQNy9r5z5bmgXbCOHaAd6fodEkTNtq292igCen/3nRLtz9pnqv975ipx5qunxo07ZmVlncCB6D1K7VFj6Os37x732pa9hRs276no1rVr/65XdKFuXa9A6ZIOe8WGTXsK/7L53XExukaYpAvWkS5ICdDhegA0yHH9Wo8YJEyJIiAL/9syE1G2Jk+u0vWwto2q5uYWtH/19V1rpZB5nPMMRCcZEi8wAucpD8pkIUWGLew83Vb38ZpMIeUl0j0Auib9A7oIbYeA7vpxVXqNF0WAV8PG2s8S7whwk2KADoKPlILfp/t4zYfX7gBIJxNkzVng6DgTImTAL0Ga13jnnAAuxFiAT0Tk3YhLV0ZkQBgJMkn38VqwdNJdhpGgYpAQ6VdKeA2HVzhPV/M4AD4tAF6EgRQgQbh6bclJcO755qaQzhIRlYi0BBl6bC0jdemQou0Bv/c1EFcGfDH8zh6fj/pFji663hBqhC0YSCC9EM6DYAESALx0O/DCEXMaGQSPAw7nSigTZF06byIBIoFZith0XXQ95so8jAJXkEDUOEAJB7QGL5EBWgpXRuoK7T2GcyKrEHmJsZQmAweiqkfX5HiNF1cGoHPo1ZUUa9CrK8dCI8EHQXtL3AaYMvajHNDSjbwrYVMOCbF11dQMiL2U+KwiKu3DIx+bBM6V5+CI/KHANgBY548gwvkbhN4OspauQrr6yGvAeDPAq3+9doEtEMiAyDTXIAL2IAk1fmHbnuNyEvlKyGqFqAtsFRmKvMT2QAnTXb9f+Kve8hrwnBNgYwsIlCBYXdfFtgHFsQv3gAzo2icQOa8Fl09YXqakWqTBKZCgI6+ll470X3By0gv/9hrPk4CKR2aPq5w1q/DsrFkVXXp379+ldzdySp9u6ZUzZ1Von27jNXDQLrEFOIoGxkMHoUDaChyANTLCX0cG6HFPTFxqMUGZAF8E8JWQOBMQfWQEdJ0JlZBFmC/z5KRli3QfrxJFwLfTprU/PW3GWiH8eYLj9dTmyZDEdcQAxJFCJENmSGnnfY+2uo/XBDa2gAYnHCmpJvLciXxQj/Ajsl7jBe0nJy/beur+5wegtKPOHQ+yzh1JF+rcoVjbUAacnrxia7C9l4wiwMd5R4CbFAU6CD5K8vt0H68JpJPmAbCICElcW1oK1x5TrycDvOZqjD2KAMHVWCwuESRQnCQk6T5ek9tcHMJ4SPcaEurTkdKep7bXPI21xyCApwXBO+kZFnEvXfi9X10N4vmc8+pw0MLZDiJESi3dr5TwPLXrA9pQfxQB3M/x6orFuXteg+ZhJGhywnXHj3T2mniRNbtMSL5I9wmkO8bW46HE0pF1CxZnP+p5anvN01h7FAECYDRILCTy4MOCtV0D0TLcj/f9Oudf/szjFkjIRL8iIXglCgk9D8Z0pLZxXsQFz1y28LE6T+06J2qEM4oA2xakwdluBnBX1qVj4fVOvWLxvK0rnp03YMWSee26X9n9IArp0q179+Ic2Bwf2tQ7UIwGjOjjoJkR+1uwHo+MIkAAcBB0TKkjhzaapKDf9nv/3o5nEU1uI5VFilbqUmXI+Q0ZL4oA7mYA1y8tSFEeBBvU/dzJkAg/+jRk0uZuW36bVVY+ZsEMXapGZTfo/IgiQHJ+KARag68d8Ri6ze0Wu7aam7woArjk+TiYqjUJPDwDQEZM3Y9LsJpa7No65wTcsDu/jNtiUcQeD6Y/SNB2O0wHKQvS921rUNo1N4imjBeVAXqwjP1vWyAhE5lQBFkpsMe5Bo/0d24DW1TatigCGZkDDrzd8GtLsbBTmxp0auv1NWeJSYCeYFDRrq2DCncNgGzXKTXlYKfUDtQpJZUuTelQrG2DixxfvT829Fi1CzfJUji1dREJZoNO7dpjNVX3JKCpA9fV/4mHJ5TNmTFhhi7zpmad1+1zXgioi5yW9v1AQJyMhw4tYuq8HlpxrjfuZnFlgGkri5Fa6RRlz4979FbQMC4Crtq9uaznzk0znPLOhXXnN5Xj/wEAAP//5efZjQAAAAZJREFUAwBxEUwm9sTgJAAAAABJRU5ErkJggg=="
_LOGO = Path(__file__).parent / "assets" / "logo.png"
_ICON = Image.open(_LOGO) if _LOGO.exists() else Image.open(io.BytesIO(base64.b64decode(FAVICON_B64)))
st.set_page_config(page_title="Nabd Tadawul", page_icon=_ICON, layout="wide", initial_sidebar_state="collapsed")

TADAWUL_LIMIT = 0.105      # Tadawul daily price limit is ±10%
TRADING_DAYS = 250
DATA_FILE = "Saudi_Tadawul_Cleaned_Dataset.csv"


THEMES = {
    "light": dict(                      
        bg="#F6F2EA", card="#FFFDF8", line="#E9E2D4", text="#24303A", muted="#76736C",
        teal="#2F6F62", gold="#A8844F", blue="#4F74A8", up="#2E8B57", down="#C4553E",
        grid="rgba(36,48,58,0.07)", neutral="#F1ECE2", input="#FFFDF8", hover="#FFFDF8",
        tape="linear-gradient(90deg,#26323C 0%,#2E3B45 100%)", tape_line="transparent",
        tape_text="#F6F2EA", tape_muted="#B9B4A9", tape_up="#86D3A6", tape_down="#F0A08C",
        soft="rgba(47,111,98,.08)", soft_line="rgba(47,111,98,.22)",
        shadow="0 1px 2px rgba(60,50,30,.04), 0 6px 18px rgba(60,50,30,.05)",
        glow="radial-gradient(900px 420px at 85% -10%, rgba(168,132,79,.08), transparent 60%)",
        up_soft="#CBE6D5", down_soft="#F2D2C8", bar_neutral="#D9D2C3", nav_active="#26323C",
        template="plotly_white",
        palette=["#2F6F62", "#C2A267", "#5B7DB1", "#C4553E", "#8C7AB5", "#6FA287",
                 "#B5718E", "#4E9BB0", "#A4A65A", "#7B8794", "#D49A5B", "#3E4C59"],
    ),
    "dark": dict(                       
        bg="#13171C", card="#1A1F26", line="#29303A", text="#E8E4DB", muted="#9BA1A8",
        teal="#62B5A2", gold="#D6B77B", blue="#7FA3D6", up="#4DB882", down="#E07B63",
        grid="rgba(255,255,255,0.06)", neutral="#222830", input="#161B21", hover="#1F252D",
        tape="linear-gradient(90deg,#1A1F26 0%,#20262E 100%)", tape_line="#29303A",
        tape_text="#E8E4DB", tape_muted="#9BA1A8", tape_up="#4DB882", tape_down="#E07B63",
        soft="rgba(98,181,162,.10)", soft_line="rgba(98,181,162,.28)", shadow="0 2px 14px rgba(0,0,0,.30)",
        glow="radial-gradient(900px 420px at 85% -10%, rgba(214,183,123,.06), transparent 60%)",
        up_soft="#2C5A44", down_soft="#5E3329", bar_neutral="#3A424D", nav_active="#62B5A2",
        template="plotly_dark",
        palette=["#62B5A2", "#D6B77B", "#7FA3D6", "#E07B63", "#A898D4", "#4DB882",
                 "#D58BA8", "#6DBBD0", "#C4C77A", "#9BA1A8", "#E7B27A", "#E8E4DB"],
    ),
}

SECTOR_AR = {
    "Basic Materials": "المواد الأساسية", "Communication Services": "الاتصالات",
    "Consumer Cyclical": "السلع الكمالية", "Consumer Defensive": "السلع الأساسية",
    "Energy": "الطاقة", "Financial Services": "الخدمات المالية", "Healthcare": "الرعاية الصحية",
    "Industrials": "الصناعة", "Insurance": "التأمين", "Real Estate": "العقارات",
    "Technology": "التقنية", "Utilities": "المرافق العامة",
}

THEMES["contrast"] = dict(           
    bg="#000000", card="#0A0A0A", line="#FFFFFF", text="#FFFFFF", muted="#E6E6E6",
    teal="#00F0D0", gold="#FFD60A", blue="#7CC4FF", up="#3DFF8F", down="#FF6B6B",
    grid="rgba(255,255,255,0.18)", neutral="#1C1C1C", input="#000000", hover="#000000",
    tape="#000000", tape_line="#FFFFFF", tape_text="#FFFFFF", tape_muted="#E6E6E6", tape_up="#3DFF8F",
    tape_down="#FF6B6B", soft="rgba(0,240,208,.16)", soft_line="#00F0D0", shadow="none", glow="none",
    up_soft="#1E7A46", down_soft="#8A2E2E", bar_neutral="#8C8C8C", nav_active="#FFD60A",
    template="plotly_dark",
    palette=["#00F0D0", "#FFD60A", "#7CC4FF", "#FF9F5A", "#D5A6FF", "#3DFF8F",
             "#FF8AC8", "#9BE7FF", "#E8F57A", "#FFFFFF", "#FFC14D", "#B0B0B0"],
)

CVD = {
    "light": dict(up="#1F6FD1", down="#E07B00", up_soft="#B9D3F4", down_soft="#F6D2A6", tape_up="#7CB8FF", tape_down="#FFB255"),
    "dark": dict(up="#5AA9FF", down="#FFA54F", up_soft="#1D3F66", down_soft="#6B4416", tape_up="#5AA9FF", tape_down="#FFA54F"),
    "contrast": dict(up="#6CB8FF", down="#FFAA33", up_soft="#1D4F80", down_soft="#7A4A00", tape_up="#6CB8FF", tape_down="#FFAA33"),
}
OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#999999",
             "#004D80", "#A66F00", "#006B4F", "#8E5577"]


# User preferences
DEFAULTS = dict(lang="en", theme="light", size=100, cvd=False,
                spacing=False)
CHOICES = dict(lang=("en", "ar"), theme=("light", "dark", "contrast"), size=(90, 100, 115, 130))


def _load_prefs():
    p = dict(DEFAULTS)
    qp = st.query_params
    for k, d in DEFAULTS.items():
        if k not in qp:
            continue
        v = qp[k]
        if isinstance(d, bool):
            p[k] = v == "1"
        elif isinstance(d, int):
            p[k] = int(v) if v.isdigit() and int(v) in CHOICES["size"] else d
        else:
            p[k] = v if v in CHOICES.get(k, (v,)) else d
    return p


if not isinstance(st.session_state.get("prefs"), dict):
    st.session_state.prefs = _load_prefs()
P = st.session_state.prefs
# repair any missing or invalid value (e.g. a session left over from an older version of the app)
for _k, _d in DEFAULTS.items():
    _v = P.get(_k, _d)
    if type(_v) is not type(_d) or (_k in CHOICES and _v not in CHOICES[_k]):
        P[_k] = _d


def save_pref(name):
    """Widget callback: copy the widget value into prefs and into the URL (so a bookmark keeps it)."""
    v = st.session_state.get(f"_w_{name}", DEFAULTS[name])
    if name in CHOICES and v not in CHOICES[name]:
        v = DEFAULTS[name]
    st.session_state.prefs[name] = v
    st.query_params[name] = ("1" if v else "0") if isinstance(v, bool) else str(v)


def reset_prefs():
    st.session_state.prefs = dict(DEFAULTS)
    for k in DEFAULTS:
        if k in st.query_params:
            del st.query_params[k]
        st.session_state.pop(f"_w_{k}", None)


AR = P["lang"] == "ar"
MODE = P["theme"]
T = dict(THEMES[MODE])
if P["cvd"]:
    T.update(CVD[MODE])
    T["palette"] = OKABE_ITO if MODE == "light" else T["palette"]
SCALE = P["size"] / 100
_theme_sig = f'{MODE}-{P["cvd"]}'
_need_rerun = False
try:
    from streamlit import config as _stcfg
    if st.session_state.get("_theme_sig") != _theme_sig:
        for _k, _v in {"base": "light" if MODE == "light" else "dark", "primaryColor": T["teal"],
                       "backgroundColor": T["bg"], "secondaryBackgroundColor": T["card"],
                       "textColor": T["text"]}.items():
            _stcfg.set_option(f"theme.{_k}", _v)
        st.session_state["_theme_sig"] = _theme_sig
        _need_rerun = True
except Exception:
    pass
if _need_rerun:
    st.rerun()
BG, CARD, LINE, TEXT, MUTED = T["bg"], T["card"], T["line"], T["text"], T["muted"]
TEAL, GOLD, BLUE, UP, DOWN, GRID, NEUTRAL = T["teal"], T["gold"], T["blue"], T["up"], T["down"], T["grid"], T["neutral"]
PALETTE = T["palette"]
FONT = "IBM Plex Sans Arabic, IBM Plex Sans, sans-serif" if AR else "IBM Plex Sans, sans-serif"
DIR = "rtl" if AR else "ltr"
ON_ACCENT = "#10161B" if MODE != "light" else "#FBF8F2"   
FIELD_LINE = {"light": "#D8CDBA", "dark": "#3A424D", "contrast": "#FFFFFF"}[MODE] 
BANNER = {"light": "linear-gradient(120deg, #FFFDF8 0%, #F8F2E6 100%)",
          "dark": "linear-gradient(120deg, #1A1F26 0%, #1E242B 100%)",
          "contrast": "#0A0A0A"}[MODE]


def L(en, ar):
    """Pick the label for the current language."""
    return ar if AR else en


def N(x):
    """Isolate numbers inside Arabic sentences so signs and % stay in place."""
    return f'<bdi dir="ltr">{x}</bdi>'


def alpha(hex_color, a):
    """'#RRGGBB' + opacity → 'rgba(r,g,b,a)' (Plotly does not accept 8-digit hex)."""
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


TADAWUL_STOCKS = """
2030|SARCO|Energy
2222|Saudi Aramco|Energy
2380|Petro Rabigh|Energy
2381|Arabian Drilling|Energy
2382|ADES|Energy
4030|Bahri|Energy
4200|Aldrees|Energy
1201|Takween|Materials
1202|MEPCO|Materials
1210|BCI|Materials
1211|Maaden|Materials
1301|Aslak|Materials
1304|Alyamamah Steel|Materials
1320|SSP|Materials
1321|East Pipes|Materials
1322|AMAK|Materials
2001|Chemanol|Materials
2010|SABIC|Materials
2020|SABIC Agri-Nutrients|Materials
2060|Tasnee|Materials
2090|NGC|Materials
2150|Zoujaj|Materials
2170|Alujain|Materials
2180|FIPCO|Materials
2200|APC|Materials
2210|Nama Chemicals|Materials
2220|Maadaniyah|Materials
2223|Luberef|Materials
2240|Zamil Industrial|Materials
2250|SIIG|Materials
2290|Yansab|Materials
2300|SPM|Materials
2310|Sipchem|Materials
2330|Advanced Petrochemical|Materials
2350|Saudi Kayan|Materials
2360|SVCP|Materials
3001|HCC|Materials
3002|Najran Cement|Materials
3003|City Cement|Materials
3004|Northern Cement|Materials
3005|UACC|Materials
3007|Oasis|Materials
3008|Alkathiri|Materials
3010|ACC|Materials
3020|YSCC|Materials
3030|Saudi Cement|Materials
3040|QACCO|Materials
3050|SPCC|Materials
3060|YCC|Materials
3080|EPCCO|Materials
3090|TCC|Materials
3091|Jouf Cement|Materials
3092|Riyadh Cement|Materials
1212|Astra Industrial|Capital Goods
1214|Shaker|Capital Goods
1302|Bawan|Capital Goods
1303|EIC|Capital Goods
2040|Saudi Ceramics|Capital Goods
2110|Saudi Cable|Capital Goods
2160|Amiantit|Capital Goods
2320|Albabtain|Capital Goods
2370|MESC|Capital Goods
4110|BATIC|Capital Goods
4140|SIECO|Capital Goods
4141|Alomran|Capital Goods
4142|Riyadh Cables|Capital Goods
1831|Maharah|Commercial & Professional Svcs
1832|Sadr Logistics|Commercial & Professional Svcs
1833|Almawarid|Commercial & Professional Svcs
4270|SPPC|Commercial & Professional Svcs
6004|Catrion|Commercial & Professional Svcs
2190|SISCO Holding|Transportation
4031|SGS|Transportation
4040|SAPTCO|Transportation
4260|Budget Saudi|Transportation
4261|Theeb Rent a Car|Transportation
4262|Lumi Rental|Transportation
4263|SAL|Transportation
1213|Naseej|Consumer Durables & Apparel
2130|SIDC|Consumer Durables & Apparel
2340|Alabdullatif|Consumer Durables & Apparel
4011|Lazurde|Consumer Durables & Apparel
4012|Alaseel|Consumer Durables & Apparel
4180|Fitaihi Group|Consumer Durables & Apparel
1810|Seera|Consumer Services
1820|Alhokair Group|Consumer Services
1830|Fitness Time|Consumer Services
4170|TECO|Consumer Services
4290|Alkhaleej Training|Consumer Services
4291|NCLE|Consumer Services
4292|Ataa|Consumer Services
6002|Herfy Foods|Consumer Services
6012|Raydan|Consumer Services
6013|DWF|Consumer Services
6014|Alamar|Consumer Services
6015|Americana|Consumer Services
4070|TAPRCO|Media and Entertainment
4071|Alarabia|Media and Entertainment
4072|MBC Group|Media and Entertainment
4210|SRMG|Media and Entertainment
4003|Extra|Consumer Discretionary Distribution & Retail
4008|SACO|Consumer Discretionary Distribution & Retail
4050|SASCO|Consumer Discretionary Distribution & Retail
4051|Baazeem|Consumer Discretionary Distribution & Retail
4190|Jarir|Consumer Discretionary Distribution & Retail
4191|Abo Moati|Consumer Discretionary Distribution & Retail
4192|Alsaif Gallery|Consumer Discretionary Distribution & Retail
4240|Cenomi Retail|Consumer Discretionary Distribution & Retail
4001|Abdullah Al Othaim Markets|Consumer Staples Distribution & Retail
4006|Farm Superstores|Consumer Staples Distribution & Retail
4061|Anaam Holding|Consumer Staples Distribution & Retail
4160|Thimar|Consumer Staples Distribution & Retail
4161|Bindawood|Consumer Staples Distribution & Retail
4162|Almunajem|Consumer Staples Distribution & Retail
4163|Aldawaa|Consumer Staples Distribution & Retail
4164|Nahdi|Consumer Staples Distribution & Retail
2050|Savola Group|Food & Beverages
2100|Wafrah|Food & Beverages
2270|Sadafco|Food & Beverages
2280|Almarai|Food & Beverages
2281|Tanmiah|Food & Beverages
2282|Naqi|Food & Beverages
2283|First Mills|Food & Beverages
4080|Sinad Holding|Food & Beverages
6001|Halwani Bros|Food & Beverages
6010|NADEC|Food & Beverages
6020|GACO|Food & Beverages
6040|TADCO|Food & Beverages
6050|SFICO|Food & Beverages
6060|Sharqiyah Development|Food & Beverages
6070|Aljouf|Food & Beverages
6090|JAZADCO|Food & Beverages
2140|Ayyan|Health Care Equipment & Svcs
2230|Saudi Chemical|Health Care Equipment & Svcs
4002|Mouwasat|Health Care Equipment & Svcs
4004|Dallah Health|Health Care Equipment & Svcs
4005|National Medical Care|Health Care Equipment & Svcs
4007|Alhammadi|Health Care Equipment & Svcs
4009|Saudi German Health|Health Care Equipment & Svcs
4013|Sulaiman Alhabib|Health Care Equipment & Svcs
4014|Equipment House|Health Care Equipment & Svcs
2070|Spimaco|Pharma, Biotech & Life Science
4015|Jamjoom Pharma|Pharma, Biotech & Life Science
1010|Riyad Bank|Banks
1020|Bank AlJazira|Banks
1030|Saudi Investment Bank|Banks
1050|Banque Saudi Fransi|Banks
1060|SAB|Banks
1080|ANB|Banks
1120|Al Rajhi Bank|Banks
1140|Bank Albilad|Banks
1150|Alinma Bank|Banks
1180|SNB|Banks
1111|Tadawul Group|Financial Services
1182|Amlak|Financial Services
1183|SHL|Financial Services
2120|SAIC|Financial Services
4081|Nayifat|Financial Services
4082|MRNA|Financial Services
4130|Albaha|Financial Services
4280|Kingdom Holding|Financial Services
8010|Tawuniya|Insurance
8012|Jazira Takaful|Insurance
8020|Malath Insurance|Insurance
8030|Medgulf|Insurance
8040|Allianz SF|Insurance
8050|Salama|Insurance
8060|Walaa|Insurance
8070|Arabian Shield|Insurance
8100|Saico|Insurance
8120|Gulf Union Alahlia|Insurance
8150|ACIG|Insurance
8160|AICC|Insurance
8170|Aletihad|Insurance
8180|Alsagr Insurance|Insurance
8190|UCA|Insurance
8200|Saudi Re|Insurance
8210|Bupa Arabia|Insurance
8230|Alrajhi Takaful|Insurance
8240|Chubb|Insurance
8250|GIG|Insurance
8260|Gulf General|Insurance
8270|Buruj|Insurance
8280|Liva|Insurance
8300|Wataniya|Insurance
8310|Amana Insurance|Insurance
8311|Enaya|Insurance
7200|Al Moammar (MIS)|Software & Services
7201|Arab Sea Information Systems|Software & Services
7202|Solutions by STC|Software & Services
7203|Elm|Software & Services
7204|2P (Perfect Presentation)|Software & Services
7010|STC|Telecommunication Services
7020|Etihad Etisalat|Telecommunication Services
7030|Zain KSA|Telecommunication Services
7040|Atheeb Telecom|Telecommunication Services
2080|GASCO|Utilities
2081|AWPT|Utilities
2082|ACWA Power|Utilities
2083|Marafiq|Utilities
5110|Saudi Electricity|Utilities
4020|Alakaria|Real Estate Mgmt & Dev't
4090|Taiba|Real Estate Mgmt & Dev't
4100|MCDC|Real Estate Mgmt & Dev't
4150|ARDCO|Real Estate Mgmt & Dev't
4220|Emaar EC|Real Estate Mgmt & Dev't
4230|Red Sea|Real Estate Mgmt & Dev't
4250|Jabal Omar|Real Estate Mgmt & Dev't
4300|Dar Alarkan|Real Estate Mgmt & Dev't
4310|KEC|Real Estate Mgmt & Dev't
4320|Alandalus|Real Estate Mgmt & Dev't
4321|Cenomi Centers|Real Estate Mgmt & Dev't
4322|Retal|Real Estate Mgmt & Dev't
4323|Sumou|Real Estate Mgmt & Dev't
"""


EXTRA_STOCKS = """
4330|Riyad REIT|REITs
4331|Aljazira REIT|REITs
4332|Jadwa REIT Alharamain|REITs
4333|Taleem REIT|REITs
4334|Al Maather REIT|REITs
4335|Musharaka REIT|REITs
4336|Mulkia REIT|REITs
4337|SICO Saudi REIT|REITs
4338|Alahli REIT 1|REITs
4339|Derayah REIT|REITs
4340|Al Rajhi REIT|REITs
4342|Jadwa REIT Saudi|REITs
4344|SEDCO Capital REIT|REITs
4345|Alinma Retail REIT|REITs
4346|MEFIC REIT|REITs
4347|Bonyan REIT|REITs
4348|Alkhabeer REIT|REITs
4349|Alinma Hospitality REIT|REITs
2284|Binzagr|Food & Beverages
2285|Arabian Mills|Food & Beverages
2286|Fourth Milling|Food & Beverages
2287|Entaj|Food & Beverages
4016|Avalon Pharma|Pharma, Biotech & Life Science
4017|Fakeeh Care|Health Care Equipment & Svcs
4018|Almoosa|Health Care Equipment & Svcs
4019|SMC Healthcare|Health Care Equipment & Svcs
4021|CMCER|Health Care Equipment & Svcs
4083|Tasheel|Financial Services
4084|Derayah|Financial Services
4324|Bonyan|Real Estate Mgmt & Dev't
4325|Eshraq|Real Estate Mgmt & Dev't
"""

# Tadawul industry groups
GROUP_AR = {
    "Energy": "الطاقة", "Materials": "المواد الأساسية", "Capital Goods": "السلع الرأسمالية",
    "Commercial & Professional Svcs": "الخدمات التجارية والمهنية", "Transportation": "النقل",
    "Consumer Durables & Apparel": "السلع طويلة الأجل", "Consumer Services": "الخدمات الاستهلاكية",
    "Media and Entertainment": "الإعلام والترفيه", "Consumer Discretionary Distribution & Retail": "تجزئة السلع الكمالية",
    "Consumer Staples Distribution & Retail": "تجزئة وتوزيع السلع الاستهلاكية", "Food & Beverages": "إنتاج الأغذية",
    "Health Care Equipment & Svcs": "الرعاية الصحية", "Pharma, Biotech & Life Science": "الأدوية",
    "Banks": "البنوك", "Insurance": "التأمين", "Software & Services": "التطبيقات وخدمات التقنية",
    "Telecommunication Services": "الاتصالات", "Utilities": "المرافق العامة",
    "Real Estate Mgmt & Dev't": "إدارة وتطوير العقارات", "REITs": "صناديق الاستثمار العقاري (ريت)", "Other": "أخرى",
}
GROUP_EN_SHORT = {"Commercial & Professional Svcs": "Commercial & Professional Services",
                  "Consumer Discretionary Distribution & Retail": "Discretionary Retail",
                  "Consumer Staples Distribution & Retail": "Staples Retail",
                  "Health Care Equipment & Svcs": "Health Care", "Pharma, Biotech & Life Science": "Pharma & Biotech",
                  "Real Estate Mgmt & Dev't": "Real Estate", "Telecommunication Services": "Telecom",
                  "Media and Entertainment": "Media & Entertainment"}


def sector_name(s):
    if AR:
        return GROUP_AR.get(s, SECTOR_AR.get(s, s))
    return GROUP_EN_SHORT.get(s, s)


def html(s):
    """Render raw HTML; strip indentation so Markdown never turns it into a code block."""
    st.markdown("".join(line.strip() for line in s.splitlines()), unsafe_allow_html=True)



# CSS 
rtl_css = f"""
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"], [data-testid="stCaptionContainer"],
[data-testid="stExpander"] summary, [data-testid="stAlert"], [data-testid="stHeading"], .stRadio [role="radiogroup"],
label[data-baseweb="checkbox"], [data-baseweb="select"], [data-baseweb="input"] input {{ direction: rtl; text-align: right; }}
[data-testid="stHorizontalBlock"] {{ flex-direction: row-reverse; }}
.kpi .v, .story .big {{ direction:ltr; text-align:right; unicode-bidi: plaintext; }}
.hero .stamp {{ text-align:left !important; }}
.story {{ border-left:1px solid {LINE} !important; border-right:4px solid {GOLD} !important; }}
[data-testid="stCode"], .katex-display {{ direction: ltr; text-align: left; }}
/* widgets sit on the right in Arabic, with the control on the right of its text */
[data-testid="stCheckbox"], .stCheckbox, [data-testid="stButton"], [data-testid="stDownloadButton"],
[data-testid="stLinkButton"], .stRadio, [data-testid="stRadio"] {{ direction: rtl; text-align: right; width:100%; }}
label[data-baseweb="checkbox"], label[data-baseweb="radio"] {{ direction: rtl; }}
label[data-baseweb="checkbox"] > div:first-child, label[data-baseweb="radio"] > div:first-child {{
        margin-right:0 !important; margin-left:10px !important; }}
.stRadio [role="radiogroup"] {{ gap: 6px 22px; }}
""" if AR else ""

html(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');
html, body, .stApp {{ font-family: {FONT}; }}
.stApp {{ background: {T['glow']}, {BG}; color: {TEXT}; }}
.block-container {{ padding-top: 1rem; padding-bottom: 3rem; max-width: 1500px; }}

/* hide Streamlit chrome (Deploy, ⋮ menu, top colour strip, footer) */
header[data-testid="stHeader"] {{ display:none !important; }}
#MainMenu, [data-testid="stMainMenu"], .stDeployButton, .stAppDeployButton, [data-testid="stAppDeployButton"],
[data-testid="stToolbarActions"], [data-testid="stDecoration"] {{ display:none !important; }}
footer {{ visibility:hidden; }}
header button svg, [data-testid="stSidebarCollapseButton"] svg, [data-testid="stExpandSidebarButton"] svg {{ color:{MUTED}; }}

/* ── native widgets follow the theme ── */
[data-testid="stSidebar"] {{ background:{CARD}; border-right:1px solid {LINE}; }}
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h5,
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label, .stRadio label p, .stCheckbox label p,
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, [data-testid="stCaptionContainer"],
[data-testid="stExpander"] summary p, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] p,
button[role="tab"] p {{ color:{TEXT} !important; }}
[data-testid="stCaptionContainer"], [data-testid="stMetricLabel"] p {{ color:{MUTED} !important; }}
/* selection boxes, inputs and their drop-down lists — readable in every theme */
[data-baseweb="select"] > div, [data-baseweb="input"] {{
        background:{CARD} !important; border:1px solid {FIELD_LINE} !important; border-radius:10px !important;
        min-height:42px; box-shadow:none !important; }}
[data-baseweb="base-input"] {{ background:transparent !important; border:none !important; box-shadow:none !important; }}
/* number input: one frame around the value and the − / + buttons */
[data-testid="stNumberInputContainer"] {{ background:{CARD} !important; border:1px solid {FIELD_LINE} !important;
        border-radius:10px !important; overflow:hidden; min-height:42px; }}
[data-testid="stNumberInputContainer"]:hover {{ border-color:{TEAL} !important; }}
[data-testid="stNumberInputContainer"]:focus-within {{ border-color:{TEAL} !important; box-shadow:0 0 0 3px {T['soft']} !important; }}
[data-testid="stNumberInputContainer"] [data-baseweb="input"] {{ border:none !important; border-radius:0 !important;
        background:transparent !important; box-shadow:none !important; }}
[data-baseweb="select"] > div:hover, [data-baseweb="input"]:hover {{ border-color:{TEAL} !important; }}
[data-baseweb="select"] > div:focus-within, [data-baseweb="input"]:focus-within {{
        border-color:{TEAL} !important; box-shadow:0 0 0 3px {T['soft']} !important; }}
[data-baseweb="select"] *, [data-baseweb="input"] input, [data-baseweb="base-input"] input,
.stNumberInput input, .stTextInput input, .stDateInput input {{ color:{TEXT} !important; -webkit-text-fill-color:{TEXT};
        background:transparent !important; font-size:.95rem; }}
[data-baseweb="select"] svg {{ color:{MUTED} !important; fill:{MUTED} !important; }}
[data-baseweb="popover"] > div, [data-baseweb="popover"] ul, [data-baseweb="popover"] [role="listbox"],
[data-baseweb="menu"], [data-testid="stSelectboxVirtualDropdown"] {{
        background:{CARD} !important; border-radius:12px !important; }}
[data-baseweb="popover"] > div {{ border:1px solid {FIELD_LINE} !important; box-shadow:0 10px 30px rgba(0,0,0,.12) !important; }}
[data-baseweb="popover"] li, [role="option"] {{ background:transparent !important; }}
[data-baseweb="popover"] li *, [role="option"], [role="option"] * {{ color:{TEXT} !important; font-size:.92rem; }}
[data-baseweb="popover"] li:hover, [role="option"]:hover, [role="option"][aria-selected="true"],
[data-baseweb="popover"] li[aria-selected="true"] {{ background:{T['soft']} !important; }}
[data-baseweb="tag"] {{ background:{T['soft']} !important; border:1px solid {T['soft_line']} !important; }}
[data-baseweb="tag"] span {{ color:{TEXT} !important; }}
[data-baseweb="tag"] svg {{ color:{MUTED} !important; }}
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {{
        color:{MUTED} !important; font-family:'IBM Plex Mono', monospace; }}
[data-testid="stSlider"] [role="slider"] {{ background:{TEAL} !important; border-color:{TEAL} !important;
        box-shadow: 0 0 0 4px {T['soft']} !important; }}
[data-testid="stExpander"] details {{ background:{CARD}; border:1px solid {LINE} !important; border-radius:12px; }}
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button, [data-testid="stLinkButton"] a,
.stButton button, .stDownloadButton button, .stLinkButton a,
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"] {{
        background:{T['nav_active']} !important; color:{ON_ACCENT} !important; border:1px solid {T['nav_active']} !important;
        border-radius:10px !important; font-weight:600; }}
[data-testid="stButton"] button *, [data-testid="stDownloadButton"] button *, [data-testid="stLinkButton"] a *,
.stButton button *, .stDownloadButton button *, .stLinkButton a *,
[data-testid="stBaseButton-primary"] *, [data-testid="stBaseButton-secondary"] * {{ color:{ON_ACCENT} !important; }}
[data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover, [data-testid="stLinkButton"] a:hover {{
        filter: brightness(1.12); }}
[data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {{ background:transparent !important; color:{TEXT} !important;
        border:none !important; border-inline-start:1px solid {FIELD_LINE} !important; border-radius:0 !important;
        width:40px !important; height:auto !important; align-self:stretch; }}
[data-testid="stNumberInputStepUp"]:hover, [data-testid="stNumberInputStepDown"]:hover {{ background:{T['soft']} !important; }}
[data-testid="stNumberInputStepUp"] svg, [data-testid="stNumberInputStepDown"] svg {{ color:{TEXT} !important; fill:{TEXT} !important; }}
.katex, .katex * {{ color:{TEXT} !important; }}
label[data-baseweb="checkbox"] > div:first-child {{ background:{'#CFC7B6' if MODE == 'light' else '#46505C'} !important; }}
label[data-baseweb="checkbox"]:has(input:checked) > div:first-child {{ background:{TEAL} !important; }}
label[data-baseweb="checkbox"] > div:first-child > div {{ background:#FFFFFF !important; box-shadow:0 1px 3px rgba(0,0,0,.3) !important; }}
[data-testid="stSlider"] div[style*="255, 75, 75"], [data-testid="stSlider"] div[style*="ff4b4b"],
[data-testid="stSlider"] div[style*="FF4B4B"] {{ filter: hue-rotate(160deg) saturate(.45) brightness(.8); }}
[data-testid="stSlider"] div[style*="255, 75, 75"] {{ filter: hue-rotate(160deg) saturate(.45) brightness(.8); }}
input::placeholder {{ color:{MUTED} !important; opacity:1; }}
button[role="tab"][aria-selected="true"] p {{ color:{TEAL} !important; }}
[data-baseweb="tab-highlight"] {{ background:{TEAL} !important; }}
[data-testid="stAlert"] {{ border-radius:12px; }}
[data-testid="stAlert"] > div, [data-testid="stAlertContainer"] {{ background:{alpha(GOLD, .14)} !important;
        border:1px solid {alpha(GOLD, .45)} !important; color:{TEXT} !important; border-radius:12px; }}
[data-testid="stAlert"] * {{ color:{TEXT} !important; }}

.ar {{ font-family: 'IBM Plex Sans Arabic', sans-serif; }}
.mono {{ font-family: 'IBM Plex Mono', monospace; }}

/* hero */
.hero {{ display:flex; justify-content:space-between; align-items:flex-end; gap:24px; flex-wrap:wrap;
        padding: 4px 4px 14px 4px; direction:{DIR}; }}
.hero .kicker {{ color:{GOLD}; font-size:.74rem; letter-spacing:{'0' if AR else '.16em'}; text-transform:uppercase; font-weight:600; }}
.hero h1 {{ font-size: 2.1rem; line-height:1.2; margin:.2rem 0 0 0; font-weight:700; color:{TEXT}; }}
.hero h1 span {{ color:{TEAL}; }}
.hero .sub {{ color:{MUTED}; font-size:1.02rem; margin-top:.35rem; }}
.hero .stamp {{ text-align:right; color:{MUTED}; font-size:.82rem; }}
.hero .stamp b {{ color:{TEXT}; font-size:1rem; }}
.pill {{ display:inline-flex; align-items:center; gap:6px; padding:3px 10px; border-radius:999px;
        background:{T['soft']}; color:{TEXT}; font-size:.78rem; margin-bottom:6px; }}
.live {{ display:inline-block; width:8px; height:8px; border-radius:50%; background:{UP}; animation: pulse 1.8s infinite; }}
@keyframes pulse {{ 0% {{ box-shadow:0 0 0 0 {UP}88; }} 70% {{ box-shadow:0 0 0 9px {UP}00; }} 100% {{ box-shadow:0 0 0 0 {UP}00; }} }}

/* ticker tape — market strip like saudiexchange.sa */
.tape {{ overflow:hidden; white-space:nowrap; background:{T['tape']}; border:1px solid {T['tape_line']};
        border-radius:12px; padding:10px 0; margin-bottom:16px; box-shadow:{T['shadow']}; direction:ltr; }}
.tape .track {{ display:inline-block; animation: scroll 75s linear infinite; }}
.tape:hover .track {{ animation-play-state: paused; }}
.tk {{ display:inline-block; margin:0 22px; font-size:.86rem; color:{T['tape_muted']}; }}
.tk b {{ color:{T['tape_text']}; margin-right:6px; }}
.tk .px {{ color:{T['tape_text']}; margin:0 6px; font-family:'IBM Plex Mono', monospace; }}
.tape .up {{ color:{T['tape_up']} !important; }} .tape .down {{ color:{T['tape_down']} !important; }}
@keyframes scroll {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-50%); }} }}

/* nav pills */
.st-key-nav div[role="radiogroup"] {{ gap:8px; flex-wrap:wrap; }}
.st-key-nav div[role="radiogroup"] > label {{ background:{CARD}; border:1px solid {LINE}; padding:8px 16px;
        border-radius:999px; margin:0; transition: all .2s ease; box-shadow:{T['shadow']}; }}
.st-key-nav div[role="radiogroup"] > label:hover {{ border-color:{TEAL}; }}
.st-key-nav div[role="radiogroup"] > label > div:first-child {{ display:none; }}
.st-key-nav div[role="radiogroup"] > label:has(input:checked) {{ background:{T['nav_active']}; border-color:{T['nav_active']}; }}
.st-key-nav div[role="radiogroup"] > label:has(input:checked) p {{ color:{ON_ACCENT} !important; }}
.st-key-nav div[role="radiogroup"] > label p {{ font-weight:600; font-size:.9rem; color:{TEXT} !important; }}

/* cards: only containers created with card() */
[class*="st-key-card_"] [data-testid="stMarkdown"], [class*="st-key-card_"] .stMarkdown {{ margin-bottom:0 !important; }}
[class*="st-key-card_"] {{ background:{CARD}; border:1px solid {LINE}; border-radius:18px; padding:18px 20px 18px 20px;
        box-shadow:{T['shadow']}; }}

/* KPI tiles */
.kpi {{ background:{CARD}; border:1px solid {LINE}; border-top:2px solid {alpha(TEAL, .45)}; border-radius:16px;
        padding:14px 16px 6px 16px; min-height:150px; box-shadow:{T['shadow']}; }}
.kpi .l {{ color:{MUTED}; font-size:.74rem; letter-spacing:{'0' if AR else '.12em'}; text-transform:uppercase; }}
.kpi .v {{ font-size:1.55rem; font-weight:700; color:{TEXT}; margin-top:2px; line-height:1.25; overflow-wrap:anywhere; }}
.kpi .v.sm {{ font-size:1.15rem; }}
.kpi .s {{ font-size:.8rem; color:{MUTED}; min-height:2.3em; }}
.up {{ color:{UP} !important; }} .down {{ color:{DOWN} !important; }} .gold {{ color:{GOLD} !important; }}

/* chapter header */
.chapter {{ margin: 8px 0 12px 0; }}
.chapter .n {{ color:{GOLD}; font-family:'IBM Plex Mono', monospace; font-size:.8rem; letter-spacing:.15em; }}
.chapter h2 {{ margin:.1rem 0; font-size:1.55rem; color:{TEXT}; font-weight:700; }}
.chapter .q {{ color:{MUTED}; font-size:.95rem; }}

/* story cards & takeaways */
.story {{ border-radius:16px; padding:14px 16px; background:{CARD}; border:1px solid {LINE};
        border-left: 4px solid {GOLD}; color:{TEXT}; font-size:.92rem; min-height:118px; box-shadow:{T['shadow']}; }}
.story .t {{ color:{GOLD}; font-size:.74rem; letter-spacing:{'0' if AR else '.14em'}; text-transform:uppercase; font-weight:600; }}
.story .big {{ font-size:1.35rem; font-weight:700; margin:2px 0; color:{TEXT}; }}
.takeaway {{ border-radius:14px; padding:12px 16px; margin:4px 0 14px 0; background:{T['soft']};
        border:1px solid {T['soft_line']}; color:{TEXT}; font-size:.94rem; line-height:1.7; }}
.takeaway b {{ color:{TEAL}; }}
.note {{ color:{MUTED}; font-size:.85rem; line-height:1.7; margin:0 0 12px 0; padding:10px 14px; border:1px dashed {LINE};
         border-radius:12px; }}
.note b {{ color:{TEXT}; }}
ol.steps {{ margin:8px 0 0 0; padding:0; list-style:none; counter-reset:st; }}
ol.steps li {{ counter-increment:st; position:relative; padding-inline-start:38px; margin:0 0 12px 0; font-size:.86rem;
              color:{MUTED}; line-height:1.6; }}
ol.steps li::before {{ content:counter(st); position:absolute; inset-inline-start:0; top:1px; width:26px; height:26px;
                      border-radius:50%; background:{T['soft']}; color:{TEAL}; font-weight:700; display:flex;
                      align-items:center; justify-content:center; font-size:.8rem; }}
ol.steps li b {{ display:block; color:{TEXT}; font-size:.92rem; }}
.concl {{ color:{TEXT}; font-size:.92rem; line-height:1.75; margin-top:6px; }}
.concl b {{ color:{TEAL}; }}
ul.concl-list {{ margin:8px 0 0 0; padding-inline-start:20px; color:{TEXT}; font-size:.88rem; line-height:1.7; }}
ul.concl-list li {{ margin-bottom:6px; }}
.foot {{ text-align:center; color:{MUTED}; font-size:.78rem; margin-top:30px; }}

/* top navbar — the three services */
.st-key-navd {{ align-items:flex-end; }}
.st-key-navd div[role="radiogroup"] {{ gap:4px; flex-wrap:nowrap; width:fit-content; margin-inline-start:auto; }}
.st-key-navd div[role="radiogroup"] > label {{ padding:9px 18px; border-radius:10px; margin:0; transition: all .2s ease; }}
.st-key-navd div[role="radiogroup"] > label:hover {{ background:{T['soft']}; }}
.st-key-navd div[role="radiogroup"] > label > div:first-child {{ display:none; }}
.st-key-navd div[role="radiogroup"] > label:has(input:checked) {{ background:{T['nav_active']}; }}
.st-key-navd div[role="radiogroup"] > label:has(input:checked) p {{ color:{ON_ACCENT} !important; }}
.st-key-navd div[role="radiogroup"] > label p {{ font-weight:600; font-size:.95rem; color:{TEXT} !important; }}
.brand {{ display:flex; align-items:center; gap:10px; }}
.brand .t {{ font-weight:700; font-size:1.12rem; color:{TEXT}; line-height:1.15; white-space:nowrap; }}
.brand .s {{ white-space:nowrap; }}
.st-key-appbar .brand svg {{ width:34px; height:34px; flex-shrink:0; }}
.brand .s {{ color:{MUTED}; font-size:.8rem; }}
.status {{ display:inline-flex; align-items:center; gap:8px; padding:6px 14px; border-radius:999px;
        font-weight:600; font-size:.88rem; margin-bottom:6px; }}

/* movers lists (like the Tadawul homepage tables) */
.mvbox {{ background:{CARD}; border:1px solid {LINE}; border-radius:16px; padding:12px 16px; box-shadow:{T['shadow']}; }}
.mvh {{ font-weight:700; color:{TEXT}; margin-bottom:4px; font-size:1rem; }}
.mv {{ display:flex; justify-content:space-between; align-items:center; gap:8px; padding:8px 0; border-bottom:1px solid {LINE}; }}
.mv:last-child {{ border-bottom:none; }}
.mv-l {{ overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }}
.mv-l b {{ color:{TEXT}; margin-inline-end:8px; font-family:'IBM Plex Mono', monospace; }}
.mv-l span {{ color:{MUTED}; font-size:.85rem; }}
.mv-r {{ display:flex; gap:10px; align-items:center; direction:ltr; flex-shrink:0; }}
.mv-r .mono {{ color:{TEXT}; font-size:.9rem; }}
.chg {{ padding:3px 8px; border-radius:8px; font-weight:600; font-size:.8rem; font-family:'IBM Plex Mono', monospace;
        min-width:76px; text-align:center; }}
.chg.up {{ background:{alpha(UP, .13)}; }} .chg.down {{ background:{alpha(DOWN, .13)}; }}
.chg.gold {{ background:{alpha(GOLD, .13)}; }}

/* developer corner */
.flow {{ display:flex; align-items:stretch; gap:8px; flex-wrap:wrap; margin:6px 0 16px 0; direction:ltr; }}
.node {{ flex:1; min-width:150px; background:{CARD}; border:1px solid {LINE}; border-top:2px solid {alpha(TEAL, .45)};
        border-radius:14px; padding:12px; box-shadow:{T['shadow']}; }}
.node .h {{ font-weight:700; color:{TEXT}; font-size:.92rem; }}
.node .d {{ color:{MUTED}; font-size:.8rem; margin-top:4px; }}
.arrow {{ align-self:center; color:{GOLD}; font-size:1.4rem; font-weight:700; }}
.chip {{ display:inline-block; padding:4px 12px; border-radius:999px; background:{T['soft']};
        border:1px solid {T['soft_line']}; color:{TEXT}; font-size:.82rem; margin:3px; }}
.step {{ display:flex; gap:12px; align-items:flex-start; margin-bottom:6px; }}
.step .num {{ background:{T['nav_active']}; color:{ON_ACCENT}; width:30px; height:30px;
        border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; flex-shrink:0; }}

/* ── accessibility ── */
html {{ font-size: {16 * SCALE:.1f}px; }}
:focus-visible, .st-key-navd label:has(input:focus-visible), .st-key-nav label:has(input:focus-visible) {{
        outline: 3px solid {GOLD} !important; outline-offset: 2px; }}
.sr-only {{ position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0);
        white-space:nowrap; border:0; }}
a {{ text-decoration: underline; }}
@media (prefers-reduced-motion: reduce) {{
  .tape .track, .live {{ animation:none !important; }} .tape {{ overflow-x:auto; }}
  * {{ transition:none !important; scroll-behavior:auto !important; }}
}}
{(".stApp p, .stApp li, .takeaway, .story, .kpi .s, .chapter .q, .hero .sub, .mvbox, .node .d { line-height:1.9 !important; word-spacing:.12em; "
  + ("" if AR else "letter-spacing:.03em; ") + "}") if P["spacing"] else ""}
{"[class*='st-key-card_'], .kpi, .story, .mvbox, .node, .tape, .st-key-navd div[role='radiogroup'] { border-width:2px !important; } .kpi .l, .story .t, .chapter .q { color:" + TEXT + " !important; }" if MODE == "contrast" else ""}

/* ── layout: no Streamlit sidebar, consistent spacing ── */
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"] {{ display:none !important; }}
.block-container {{ max-width: 1380px; padding: .5rem 2rem 3rem 2rem !important; }}
[class*="st-key-card_"] {{ margin-bottom: .35rem; }}
.gap {{ height: 14px; }}
.st-key-filters {{ background:{CARD}; border:1px solid {LINE}; border-radius:18px; padding:16px 16px 10px 16px;
        box-shadow:{T['shadow']}; }}
[data-testid="stBaseButton-pills"], [data-testid="stBaseButton-pillsActive"] {{ border-radius:999px !important;
        padding:3px 11px !important; min-height:30px !important; }}
[data-testid="stBaseButton-pills"] {{ background:{CARD} !important; border:1px solid {LINE} !important; }}
[data-testid="stBaseButton-pillsActive"] {{ background:{T['soft']} !important; border:1px solid {TEAL} !important; }}
[data-testid="stBaseButton-pills"] *, [data-testid="stBaseButton-pillsActive"] * {{ color:{TEXT} !important; font-size:.82rem !important; }}
[data-testid="stBaseButton-pills"] * {{ color:{MUTED} !important; }}
[data-testid="stHeaderActionElements"], .stMarkdown h1 > a, .stMarkdown h2 > a, .stMarkdown h3 > a {{ display:none !important; }}
.panel-h {{ font-weight:700; color:{TEXT}; font-size:1rem; margin:2px 0 4px 0; }}
.panel-s {{ color:{MUTED}; font-size:.72rem; letter-spacing:{'0' if AR else '.12em'}; text-transform:uppercase; margin:10px 0 2px 0; }}
.st-key-docnav div[role="radiogroup"] {{ gap:8px; flex-wrap:wrap; }}
.st-key-docnav div[role="radiogroup"] > label {{ background:{CARD}; border:1px solid {LINE}; padding:7px 14px;
        border-radius:10px; margin:0; box-shadow:{T['shadow']}; }}
.st-key-docnav div[role="radiogroup"] > label > div:first-child {{ display:none; }}
.st-key-docnav div[role="radiogroup"] > label:has(input:checked) {{ background:{T['nav_active']}; border-color:{T['nav_active']}; }}
.st-key-docnav div[role="radiogroup"] > label:has(input:checked) p {{ color:{ON_ACCENT} !important; }}
.st-key-docnav div[role="radiogroup"] > label p {{ font-weight:600; font-size:.88rem; color:{TEXT} !important; }}
.doc-head {{ margin: 4px 0 14px 0; padding-bottom:10px; border-bottom:1px solid {LINE}; }}
.doc-head h3 {{ margin:0; color:{TEXT}; font-size:1.35rem; font-weight:700; }}
.doc-head p {{ margin:4px 0 0 0; color:{MUTED}; font-size:.95rem; }}
.res-k {{ color:{GOLD}; font-family:'IBM Plex Mono', monospace; font-size:.8rem; }}
.res-t {{ color:{TEXT}; font-weight:700; font-size:1.08rem; margin:2px 0 4px 0; }}
.res-d {{ color:{MUTED}; font-size:.88rem; min-height:3em; margin-bottom:8px; }}
.step-t {{ font-weight:700; color:{TEXT}; }}
.step-d {{ color:{MUTED}; font-size:.9rem; margin-top:2px; }}

/* animated logo: candles rise, trend line draws itself; replays on hover */
.brand {{ cursor: default; }}
.brand svg {{ overflow: visible; transition: filter .3s ease; }}
.lg-anim .lg-c {{ transform-box: fill-box; transform-origin: 50% 100%; animation: lgRise .7s cubic-bezier(.2,.9,.25,1.25) both; }}
.lg-anim .lg-c2 {{ animation-delay: .12s; }} .lg-anim .lg-c3 {{ animation-delay: .24s; }}
.lg-anim .lg-trend {{ stroke-dasharray: 40; stroke-dashoffset: 40; animation: lgDraw .9s .4s ease-out forwards; }}
.lg-anim .lg-head {{ opacity: 0; animation: lgFade .3s 1.15s ease-out forwards; }}
.brand:hover svg {{ filter: drop-shadow(0 0 6px rgba(16,185,129,.45)); }}
.brand:hover .lg-c {{ animation: lgBounce .6s ease both; }}
.brand:hover .lg-c2 {{ animation-delay: .08s; }} .brand:hover .lg-c3 {{ animation-delay: .16s; }}
.brand:hover .lg-trend {{ animation: lgRedraw .8s ease-out both; }}
.brand:hover .lg-head {{ animation: lgPop .45s .55s ease-out both; }}
@keyframes lgRise {{ from {{ transform: scaleY(0); opacity: 0; }} to {{ transform: scaleY(1); opacity: 1; }} }}
@keyframes lgDraw {{ to {{ stroke-dashoffset: 0; }} }}
@keyframes lgRedraw {{ from {{ stroke-dashoffset: 40; }} to {{ stroke-dashoffset: 0; }} }}
@keyframes lgFade {{ to {{ opacity: 1; }} }}
@keyframes lgPop {{ 0% {{ opacity: 0; transform: translate(-2px, 2px); }} 100% {{ opacity: 1; transform: none; }} }}
@keyframes lgBounce {{ 0% {{ transform: scaleY(1); }} 40% {{ transform: scaleY(1.18); }} 70% {{ transform: scaleY(.94); }} 100% {{ transform: scaleY(1); }} }}
@media (prefers-reduced-motion: reduce) {{ .brand svg * {{ animation: none !important; stroke-dashoffset: 0 !important; opacity: 1 !important; }} }}

/* splash screen (first load + switching service) */
.splash {{ position:fixed; inset:0; z-index:1000000; display:flex; align-items:center; justify-content:center;
        background:{BG}; pointer-events:none; opacity:1; transition: opacity .45s ease, visibility .45s ease; }}
.splash.out {{ opacity:0; visibility:hidden; }}
.splash-in {{ text-align:center; animation: splashIn .45s ease both; }}
.splash svg {{ width:104px; height:104px; overflow:visible; filter: drop-shadow(0 6px 18px rgba(16,185,129,.25)); }}
.splash-t {{ font-weight:700; font-size:1.7rem; color:{TEXT}; margin-top:14px; }}
.splash-s {{ color:{MUTED}; font-size:.95rem; margin-top:4px; }}
.splash-bar {{ width:200px; height:4px; border-radius:4px; background:{LINE}; margin:18px auto 0; overflow:hidden; }}
.splash-bar span {{ display:block; height:100%; width:45%; border-radius:4px;
        background: linear-gradient(90deg, {DOWN}, #8B95A7, {UP}); animation: splashBar 1.1s ease-in-out infinite; }}
@keyframes splashOut {{ to {{ opacity:0; visibility:hidden; }} }}
@keyframes splashIn {{ from {{ opacity:0; transform: translateY(10px) scale(.97); }} to {{ opacity:1; transform:none; }} }}
@keyframes splashBar {{ from {{ transform: translateX(-110%); }} to {{ transform: translateX(230%); }} }}

/* "what if I had bought" card in the filter panel */
.wi {{ background:{T['soft']}; border:1px solid {T['soft_line']}; border-radius:14px; padding:12px 14px; margin-top:6px; }}
.wi-l {{ color:{MUTED}; font-size:.8rem; }}
.wi-v {{ font-size:1.5rem; font-weight:700; color:{TEXT}; direction:ltr; unicode-bidi:plaintext; }}
.wi-p {{ font-weight:700; font-size:.95rem; margin-bottom:4px; }}
.wi-row {{ display:flex; justify-content:space-between; gap:8px; font-size:.8rem; color:{MUTED};
        border-top:1px solid {LINE}; padding-top:5px; margin-top:5px; }}
.wi-row b {{ color:{TEXT}; font-weight:600; direction:ltr; unicode-bidi:plaintext; }}

/* ── app shell: sticky app bar, page banner, footer ── */
.st-key-appbar {{ position: sticky; top: .35rem; z-index: 990; background:{alpha(CARD, .92)};
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border:1px solid {LINE};
        border-radius:16px; padding:7px 16px; box-shadow:{T['shadow']}; margin-bottom:16px; }}
.st-key-appbar [data-testid="stVerticalBlock"], .st-key-appbar .stElementContainer {{ gap:0; }}
.st-key-navd div[role="radiogroup"] > label {{ padding:8px 16px !important; white-space:nowrap; }}
.st-key-navd div[role="radiogroup"] > label p {{ font-size:.92rem !important; white-space:nowrap; }}
.st-key-appbar [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap !important; align-items:center; }}
.st-key-appbar [data-testid="stColumn"], .st-key-appbar [data-testid="column"] {{ min-width:0 !important; }}
.st-key-appbar [data-testid="stColumn"]:has(.st-key-navm), .st-key-appbar [data-testid="column"]:has(.st-key-navm) {{ display:none; }}
.st-key-navm {{ align-items:{'flex-start' if AR else 'flex-end'}; }}
.st-key-navm button {{ background:transparent !important; border:1px solid {LINE} !important; color:{TEXT} !important;
        min-height:40px; width:44px; padding:0 !important; border-radius:12px !important; }}
.st-key-navm button * {{ color:{TEXT} !important; }}
[data-testid="stPopoverBody"] {{ background:{CARD} !important; border:1px solid {LINE} !important; border-radius:14px !important; }}
[data-testid="stPopoverBody"] [role="radiogroup"] label {{ padding:8px 4px; }}
.fx, .st-key-fx {{ position:absolute !important; width:0 !important; height:0 !important; overflow:hidden !important; }}
.hero, [class*="st-key-herobox"] {{ background:{BANNER}; border:1px solid {LINE}; border-radius:20px; padding:22px 26px !important;
        box-shadow:{T['shadow']}; margin-bottom:14px; }}
.hero.hero-flat {{ background:none; border:none; box-shadow:none; padding:0 !important; margin:0; }}
.st-key-herobox_h .st-key-nav {{ margin-top:14px; padding-top:14px; border-top:1px solid {LINE}; }}
.st-key-herobox_h .st-key-nav div[role="radiogroup"] > label:not(:has(input:checked)) {{ box-shadow:none; background:transparent; }}
[class*="st-key-herobox"] .stamp-col {{ text-align:{'left' if AR else 'right'}; color:{MUTED}; font-size:.8rem; }}
[class*="st-key-herobox"] .stamp-col .status {{ margin:0; width:150px; height:36px; justify-content:center; box-sizing:border-box; }}
.st-key-herobox {{ position:relative; }}
.st-key-refreshbtn {{ position:absolute !important; top:14px; {'left' if AR else 'right'}:26px; width:auto !important; z-index:3; }}
.st-key-refreshbtn [data-testid="stButton"] button {{ background:transparent !important; border:1px solid {LINE} !important;
        min-height:32px !important; height:32px !important; padding:0 14px !important; border-radius:999px !important; }}
.st-key-refreshbtn [data-testid="stButton"] button * {{ color:{TEXT} !important; font-size:.8rem !important; }}
.st-key-refreshbtn [data-testid="stButton"] button:hover {{ border-color:{TEAL} !important; }}
.st-key-herobox .stamp-col {{ display:flex; direction:ltr; justify-content:{'flex-start' if AR else 'flex-end'}; }}
.hero .src {{ color:{MUTED}; font-size:.8rem; margin-top:4px; }}
.kpi {{ min-height:132px !important; }}
.tp-foot {{ margin-top:34px; background:{CARD}; border:1px solid {LINE}; border-radius:20px; padding:22px 26px 14px 26px;
        box-shadow:{T['shadow']}; color:{MUTED}; font-size:.86rem; }}
.foot-grid {{ display:grid; grid-template-columns: 1.4fr 1fr 1fr; gap:22px; }}
.tp-foot h4 {{ color:{TEXT}; font-size:.9rem; margin:0 0 8px 0; font-weight:700; }}
.tp-foot ul {{ list-style:none; padding:0; margin:0; }} .tp-foot li {{ margin:4px 0; }}
.tp-foot a, .tp-foot a:visited {{ color:{MUTED} !important; text-decoration:none !important; transition:color .15s ease; }}
.tp-foot a:hover, .tp-foot a:focus-visible {{ color:{TEAL} !important; text-decoration:none !important; }}
.tp-foot .brand svg {{ width:30px; height:30px; }}
.foot-bottom {{ border-top:1px solid {LINE}; margin-top:16px; padding-top:10px; display:flex; justify-content:space-between;
        flex-wrap:wrap; gap:8px; font-size:.78rem; }}

/* ── responsive: iPad & phone ── */
@media (max-width: 1100px) {{
  .block-container {{ padding: 1rem 1.2rem 2.5rem 1.2rem; }}
  [data-testid="stHorizontalBlock"] {{ flex-wrap: wrap; }}
  [data-testid="stColumn"], [data-testid="column"] {{ min-width: min(250px, 100%); }}
  .hero h1 {{ font-size: 1.9rem; }}
  .kpi .v {{ font-size: 1.35rem; }}
  .st-key-navd div[role="radiogroup"] > label {{ padding:8px 12px; }}
}}
@media (max-width: 1150px) {{
  .st-key-appbar [data-testid="stColumn"]:has(.st-key-navd), .st-key-appbar [data-testid="column"]:has(.st-key-navd) {{ display:none; }}
  .st-key-appbar [data-testid="stColumn"]:has(.st-key-navm), .st-key-appbar [data-testid="column"]:has(.st-key-navm) {{ display:flex; flex:0 0 56px !important; }}
}}
@media (max-width: 900px) {{
  .st-key-filters {{ position: static; }}
  .foot-grid {{ grid-template-columns: 1fr 1fr; }}
}}
@media (max-width: 640px) {{
  .block-container {{ padding: .6rem .7rem 2rem .7rem; }}
  .st-key-appbar {{ top: .3rem; padding:6px 10px; border-radius:14px; }}
  .st-key-appbar [data-testid="stColumn"], .st-key-appbar [data-testid="column"] {{ width:auto !important; flex:1 1 auto !important; }}
  .hero, [class*="st-key-herobox"] {{ padding: 16px !important; border-radius:16px; }}
  .hero h1 {{ font-size: 1.5rem; }}
  .hero .sub {{ font-size:.9rem; }}
  .kpi {{ min-height: auto !important; }}
  .tk {{ margin: 0 14px; font-size:.8rem; }}
  .chapter h2 {{ font-size:1.25rem; }}
  .st-key-nav div[role="radiogroup"], .st-key-docnav div[role="radiogroup"] {{ flex-wrap:nowrap; overflow-x:auto; padding-bottom:4px; }}
  .st-key-nav label, .st-key-docnav label {{ white-space:nowrap; }}
  .foot-grid {{ grid-template-columns: 1fr; }}
}}

/* settings: mini preview */
.mp {{ background:{BG}; border:1px solid {LINE}; border-radius:14px; padding:10px; font-size:.72rem; }}
.mp-top {{ display:flex; gap:6px; margin-bottom:8px; }}
.mp-pill {{ padding:3px 10px; border-radius:999px; border:1px solid {LINE}; color:{TEXT}; background:{CARD}; }}
.mp-pill.on {{ background:{T['nav_active']}; color:{ON_ACCENT}; border-color:{T['nav_active']}; }}
.mp-kpis {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:6px; }}
.mp-k {{ background:{CARD}; border:1px solid {LINE}; border-radius:10px; padding:6px 8px; display:flex; flex-direction:column; gap:1px; }}
.mp-k span {{ color:{MUTED}; }} .mp-k b {{ font-size:.95rem; color:{TEXT}; direction:ltr; unicode-bidi:plaintext; }}
.mp-k i {{ font-style:normal; font-size:.68rem; direction:ltr; unicode-bidi:plaintext; }}
.mp-chart {{ display:flex; align-items:center; gap:6px; height:58px; margin:8px 0; background:{CARD}; border:1px solid {LINE};
        border-radius:10px; padding:4px 8px; }}
.mp-b {{ flex:1; height:100%; display:flex; flex-direction:column; }}
.mp-h {{ height:50%; display:flex; }} .mp-h.top {{ align-items:flex-end; border-bottom:1px solid {LINE}; }} .mp-h.bot {{ align-items:flex-start; }}
.mp-up, .mp-dn {{ display:block; width:100%; }}
.mp-up {{ background:{UP}; border-radius:3px 3px 0 0; }} .mp-dn {{ background:{DOWN}; border-radius:0 0 3px 3px; }}
.mp-btn {{ display:inline-block; padding:4px 12px; border-radius:8px; background:{T['nav_active']}; color:{ON_ACCENT}; font-weight:600; }}

/* market today: index card, breadth card, stock lookup */
.ix-l {{ color:{MUTED}; font-size:.85rem; }}
.ix-v {{ font-size:2.2rem; font-weight:700; color:{TEXT}; line-height:1.15; direction:ltr; unicode-bidi:plaintext; }}
.ix-c {{ font-weight:600; font-size:.95rem; margin-top:2px; }}
.ix-c span {{ color:{MUTED}; font-weight:400; font-size:.82rem; }}
.ix-sub {{ color:{MUTED}; font-size:.8rem; margin-top:10px; }}
.br-h {{ font-weight:700; color:{TEXT}; font-size:1.05rem; }}
.br-s {{ color:{MUTED}; font-size:.82rem; margin-bottom:12px; }}
.br-row {{ display:flex; justify-content:space-between; align-items:baseline; margin-top:10px; color:{TEXT}; font-size:.9rem; }}
.br-row b {{ font-size:1.25rem; }} .br-row b.flat {{ color:{MUTED}; }}
.br-track {{ height:8px; border-radius:6px; background:{NEUTRAL}; overflow:hidden; margin-top:4px; }}
.br-track i {{ display:block; height:100%; border-radius:6px; }}
.up-bg {{ background:{UP}; }} .down-bg {{ background:{DOWN}; }} .flat-bg {{ background:{T['bar_neutral']}; }}
.br-foot {{ display:flex; justify-content:space-between; gap:10px; border-top:1px solid {LINE}; margin-top:16px; padding-top:10px; }}
.br-foot div {{ display:flex; flex-direction:column; }} .br-foot span {{ color:{MUTED}; font-size:.8rem; }}
.br-foot b {{ color:{TEXT}; font-size:1.05rem; }}
.lk {{ margin-top:6px; }}
.legend-note {{ display:flex; align-items:center; gap:6px; flex-wrap:wrap; color:{MUTED}; font-size:.8rem; }}
.legend-note .dot {{ width:10px; height:10px; border-radius:3px; display:inline-block; margin-inline-start:10px; }}
.lk-n {{ color:{MUTED}; font-size:.85rem; }}
.lk-p {{ display:flex; align-items:center; gap:10px; margin:2px 0 8px 0; }}
.lk-v {{ font-size:1.7rem; font-weight:700; color:{TEXT}; }}
{rtl_css}
</style>
""")

# Streamlit ≥ 1.49 replaced use_container_width with width="stretch"
_V = tuple(int(x) for x in st.__version__.split(".")[:2])
_W = {"width": "stretch"} if _V >= (1, 49) else {"use_container_width": True}
_card_ids = count()


LOGO_SVG = ("<svg class=\"lg-anim\" width=\"40\" height=\"40\" viewBox=\"0 0 32 32\" role=\"img\" aria-label=\"Nabd Tadawul logo\">"
            "<defs>"
            "<linearGradient id=\"lg-g\" x1=\"0\" y1=\"1\" x2=\"0\" y2=\"0\"><stop offset=\"0\" stop-color=\"#0E9F6E\"/><stop offset=\"1\" stop-color=\"#34D399\"/></linearGradient>"
            "<linearGradient id=\"lg-r\" x1=\"0\" y1=\"1\" x2=\"0\" y2=\"0\"><stop offset=\"0\" stop-color=\"#C53340\"/><stop offset=\"1\" stop-color=\"#F87171\"/></linearGradient>"
            "<linearGradient id=\"lg-s\" x1=\"0\" y1=\"1\" x2=\"0\" y2=\"0\"><stop offset=\"0\" stop-color=\"#6B7487\"/><stop offset=\"1\" stop-color=\"#A9B2C3\"/></linearGradient>"
            "<linearGradient id=\"lg-t\" gradientUnits=\"userSpaceOnUse\" x1=\"2\" y1=\"0\" x2=\"30\" y2=\"0\"><stop offset=\"0\" stop-color=\"#94A3B8\" stop-opacity=\"0\"/><stop offset=\".45\" stop-color=\"#34D399\" stop-opacity=\".8\"/><stop offset=\"1\" stop-color=\"#10B981\"/></linearGradient>"
            "</defs>"
            "<g class=\"lg-c lg-c1\"><path d=\"M5.5 19.5V30.5\" stroke=\"#DC4552\" stroke-width=\"1.8\" stroke-linecap=\"round\"/><rect x=\"2.2\" y=\"21.5\" width=\"6.6\" height=\"7\" rx=\"2.2\" fill=\"url(#lg-r)\"/></g>"
            "<g class=\"lg-c lg-c2\"><path d=\"M15.5 14V28\" stroke=\"#8B95A7\" stroke-width=\"1.8\" stroke-linecap=\"round\"/><rect x=\"12.2\" y=\"16\" width=\"6.6\" height=\"9\" rx=\"2.2\" fill=\"url(#lg-s)\"/></g>"
            "<g class=\"lg-c lg-c3\"><path d=\"M25.5 9V25\" stroke=\"#10B981\" stroke-width=\"1.8\" stroke-linecap=\"round\"/><rect x=\"22.2\" y=\"11\" width=\"6.6\" height=\"11\" rx=\"2.2\" fill=\"url(#lg-g)\"/></g>"
            "<path class=\"lg-trend\" d=\"M1.8 15.5 C 7 15, 10 10.5, 15.5 9 S 23.5 5.5, 28.6 2.6\" fill=\"none\" stroke=\"url(#lg-t)\" stroke-width=\"2\" stroke-linecap=\"round\"/>"
            "<path class=\"lg-head\" d=\"M24.6 2.2 L29.4 2.1 L28.2 6.6\" fill=\"none\" stroke=\"#10B981\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/>"
            "</svg>")


def keep_radio(label, labels, key, **kw):
    """Radio over indices that keeps its selection when the labels change (e.g. language switch)."""
    store = f"_{key}_keep"
    st.session_state.setdefault(store, 0)
    st.session_state[key] = min(st.session_state[store], len(labels) - 1)

    def _save():
        st.session_state[store] = st.session_state[key]
    return st.radio(label, list(range(len(labels))), format_func=lambda i: labels[i], key=key, on_change=_save, **kw)


def gap():
    html('<div class="gap"></div>')


def card():
    """A themed card container (styled through its key class)."""
    return st.container(key=f"card_{next(_card_ids)}")


def chart(fig, target=st):
    target.plotly_chart(fig, config={"displaylogo": False}, **_W)


def table(df, target=st, **kw):
    target.dataframe(df, **_W, **kw)


def style(fig, h=380, title=None, legend=True):
    fig.update_layout(
        template=T["template"], height=h, showlegend=legend,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=TEXT, size=12 * SCALE),
        title=dict(text=title, x=0.99 if AR else 0.01, xanchor="right" if AR else "left", y=0.985, yanchor="top",
                   yref="container", font=dict(size=15 * SCALE, color=TEXT)) if title else None,
        margin=dict(l=8, r=8, t=(92 if legend else 56) if title else (40 if legend else 18), b=8),
        hoverlabel=dict(bgcolor=T["hover"], bordercolor=TEAL, font=dict(color=TEXT, family=FONT)),
        legend=dict(orientation="h", y=1.01, yanchor="bottom", x=1 if AR else 0, font=dict(size=11 * SCALE),
                    xanchor="right" if AR else "left", bgcolor="rgba(0,0,0,0)"),
        colorway=PALETTE,
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=LINE)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=LINE)
    if AR and any(tr.type == "bar" and getattr(tr, "orientation", None) == "h" for tr in fig.data):
        fig.update_yaxes(side="right")
        fig.update_xaxes(autorange="reversed")
   
    outside = [tr for tr in fig.data if tr.type in ("bar", "waterfall") and getattr(tr, "textposition", None) == "outside"]
    if outside:
        for tr in outside:
            tr.cliponaxis = False
        m = fig.layout.margin
        if any(getattr(tr, "orientation", None) == "h" for tr in outside):
            fig.update_layout(margin=dict(l=max(m.l or 0, 60), r=max(m.r or 0, 60)))
        else:
            fig.update_layout(margin=dict(t=(m.t or 0) + 24, b=max(m.b or 0, 24)))
    return fig


def chapter(num, title, question):
    html(f'<div class="chapter" dir="{DIR}"><h2>{title}</h2><div class="q">{question}</div></div>')


def takeaway(text):
    html(f'<div class="takeaway" dir="{DIR}">{text}</div>')


def sparkline(values, color, w=160, h=36):
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) < 2:
        return ""
    if len(v) > 140:
        v = v[np.linspace(0, len(v) - 1, 140).astype(int)]
    lo, hi = v.min(), v.max()
    rng = (hi - lo) or 1.0
    xs = np.linspace(0, w, len(v))
    ys = h - 3 - (v - lo) / rng * (h - 6)
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    trend = L("rising", "صاعد") if v[-1] >= v[0] else L("falling", "هابط")
    return (f'<svg width="100%" height="{h}" viewBox="0 0 {w} {h}" preserveAspectRatio="none" role="img" '
            f'aria-label="{L("trend", "الاتجاه")}: {trend}">'
            f'<polygon points="0,{h} {pts} {w},{h}" fill="{color}" opacity=".14"/>'
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.8"/></svg>')


def kpi(col, label, value, sub="", cls="", spark=""):
    col.markdown(f'<div class="kpi" dir="{DIR}"><div class="l">{label}</div><div class="v {cls}">{value}</div>'
                 f'<div class="s">{sub}</div>{spark}</div>', unsafe_allow_html=True)


def story(col, title, big, text, cls=""):
    col.markdown(f'<div class="story" dir="{DIR}"><div class="t">{title}</div><div class="big {cls}">{big}</div>'
                 f'<div>{text}</div></div>', unsafe_allow_html=True)


def big_num(x):
    for unit, d in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(x) >= d:
            return f"{x / d:,.2f}{unit}"
    return f"{x:,.0f}"


def short(stock_label):
    sym, name = stock_label.split(" · ", 1)
    return f"{name[:16]} ({sym})"


def pct_cls(x):
    return "up" if x >= 0 else "down"


AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
AR_DAYS = {"Sunday": "الأحد", "Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء",
           "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت"}


def ldate(d, weekday=False):
    """Date written in the interface language (e.g. 'الأحد 25 أكتوبر 2026')."""
    t = pd.Timestamp(d)
    if AR:
        return (f"{AR_DAYS[t.day_name()]} " if weekday else "") + f"{t.day} {AR_MONTHS[t.month - 1]} {t.year}"
    return t.strftime("%A %d %b %Y" if weekday else "%d %b %Y")


def fdate(d, fmt="%d %b %Y"):
    return pd.Timestamp(d).strftime(fmt)



# Data

COMPANIES = pd.DataFrame([l.split("|") for l in (TADAWUL_STOCKS + EXTRA_STOCKS).splitlines() if l.strip()],
                         columns=["Stock_Symbol", "Company_Name", "Stock_Sector"])
COMPANIES["Stock_Symbol"] = COMPANIES["Stock_Symbol"].astype(int)
COMPANY_NAME = dict(zip(COMPANIES["Stock_Symbol"], COMPANIES["Company_Name"]))
COMPANY_GROUP = dict(zip(COMPANIES["Stock_Symbol"], COMPANIES["Stock_Sector"]))

def find_data():
    here = Path(__file__).parent
    for p in (here / "data" / DATA_FILE, here / DATA_FILE, Path(DATA_FILE)):
        if p.exists():
            return str(p)
    return None


@st.cache_data(show_spinner="Loading Tadawul data…")
def load_data(path):
    df = pd.read_csv(path)
    df["Date"] = (pd.to_datetime(df["Date"], utc=True).dt.tz_convert("Asia/Riyadh")
                  .dt.tz_localize(None).dt.normalize())
    df["Stock_Symbol"] = df["Stock_Symbol"].astype(int)
   
    df["Company_Name"] = df["Stock_Symbol"].map(COMPANY_NAME).fillna(df["Company_Name"])
    df["Stock_Sector"] = df["Stock_Symbol"].map(COMPANY_GROUP).fillna(df["Stock_Sector"])
    df["Stock"] = df["Stock_Symbol"].astype(str) + " · " + df["Company_Name"]
    df["Non_Trading_Row"] = (df["Trade_Volume"] == 0) & (df["High_Price"] == df["Low_Price"])
    df["Year"] = df["Date"].dt.year
    df["Day_Name"] = df["Date"].dt.day_name()
    return df.sort_values(["Stock_Symbol", "Date"]).reset_index(drop=True)


@st.cache_data(show_spinner="Engineering features…")
def prepare(path, exclude_non_trading, clean_returns):
    df = load_data(path).copy()
    if exclude_non_trading:
        df = df[~df["Non_Trading_Row"]].copy()
    g = df.groupby("Stock_Symbol", sort=False)
    df["Daily_Return"] = g["Close_Price"].pct_change()
    df["Invalid_Return"] = df["Daily_Return"].abs() > TADAWUL_LIMIT
    if clean_returns:
        df.loc[df["Invalid_Return"], "Daily_Return"] = np.nan
    df["Traded_Value"] = df["Close_Price"] * df["Trade_Volume"]
    df["Intraday_Range"] = (df["High_Price"] - df["Low_Price"]) / df["Close_Price"]
   
    base_vol = g["Trade_Volume"].transform(lambda s: s.rolling(20, min_periods=10).mean().shift(1))
    df["Volume_Ratio"] = df["Trade_Volume"] / base_vol.replace(0, np.nan)
    prior_high = g["High_Price"].transform(lambda s: s.rolling(20, min_periods=10).max().shift(1))
    prior_low = g["Low_Price"].transform(lambda s: s.rolling(20, min_periods=10).min().shift(1))
    df["Breakout_Up"] = df["Close_Price"] > prior_high
    df["Breakout_Down"] = df["Close_Price"] < prior_low
    return df


@st.cache_data(show_spinner="Crunching the market…")
def build(path, excl, clean, start, end, sectors, tier="all"):
    data = prepare(path, excl, clean)
    keep = data["Date"].between(start, end) & data["Stock_Sector"].isin(sectors)
    if tier != "all":
        keep &= data["Stock_Symbol"].isin(TIER_SYMBOLS[tier])
    f = data[keep].copy()

    mkt = f.groupby("Date").agg(
        Ret=("Daily_Return", "mean"),
        Breadth=("Daily_Return", lambda x: (x > 0).sum() / max(x.notna().sum(), 1)),
        Value=("Traded_Value", "sum"),
    ).reset_index()
    mkt["Ret"] = mkt["Ret"].fillna(0)
    mkt["Index"] = (1 + mkt["Ret"]).cumprod() * 100
    mkt["Drawdown"] = mkt["Index"] / mkt["Index"].cummax() - 1

    g = f.groupby(["Stock_Symbol", "Stock", "Company_Name", "Stock_Sector"], sort=False)
    st_ = g.agg(First=("Close_Price", "first"), Last=("Close_Price", "last"),
                Mean_Close=("Close_Price", "mean"), Std_Close=("Close_Price", "std"),
                Daily_Vol=("Daily_Return", "std"), Value=("Traded_Value", "sum"),
                Days=("Date", "size")).reset_index()
   
    comp = f.assign(G=1 + f["Daily_Return"].fillna(0)).groupby("Stock_Symbol")["G"].prod() - 1
    st_["Period_Return"] = st_["Stock_Symbol"].map(comp)
    st_["CV"] = st_["Std_Close"] / st_["Mean_Close"]
    st_["Ann_Vol"] = st_["Daily_Vol"] * np.sqrt(TRADING_DAYS)
    wealth = f.assign(G=1 + f["Daily_Return"].fillna(0))
    wealth["W"] = wealth.groupby("Stock_Symbol")["G"].cumprod()
    wealth["DD"] = wealth["W"] / wealth.groupby("Stock_Symbol")["W"].cummax() - 1
    st_["Max_DD"] = st_["Stock_Symbol"].map(wealth.groupby("Stock_Symbol")["DD"].min())
    m = f[["Stock_Symbol", "Date", "Daily_Return"]].merge(mkt[["Date", "Ret"]], on="Date").dropna()
    m["XY"], m["YY"] = m["Daily_Return"] * m["Ret"], m["Ret"] ** 2
    b = m.groupby("Stock_Symbol").agg(XY=("XY", "mean"), X=("Daily_Return", "mean"),
                                      Y=("Ret", "mean"), YY=("YY", "mean"), N=("Ret", "size"))
    beta = (b["XY"] - b["X"] * b["Y"]) / (b["YY"] - b["Y"] ** 2)
    st_["Beta"] = st_["Stock_Symbol"].map(beta.where(b["N"] >= 30))
    return f, mkt, st_


@st.cache_data(show_spinner=False)
def findings(path, excl, clean, start, end, sectors, k, tier="all"):
    """Headline numbers for the four questions (used by the takeaways and the Conclusions tab)."""
    f, mkt, stats = build(path, excl, clean, start, end, sectors, tier)
    out = {}
    sec = f.groupby(["Date", "Stock_Sector"])["Daily_Return"].mean().unstack().fillna(0)
    out["sec_total"] = ((1 + sec).prod() - 1).sort_values()
    out["market"] = mkt["Index"].iloc[-1] / 100 - 1
    out["mkt_year"] = mkt.groupby(mkt["Date"].dt.year)["Ret"].apply(lambda r: (1 + r).prod() - 1)
    v = f.dropna(subset=["Volume_Ratio", "Daily_Return"])
    sp, nm = v[v["Volume_Ratio"] >= k], v[v["Volume_Ratio"] < k]
    out.update(mv_s=sp["Daily_Return"].abs().mean(), mv_n=nm["Daily_Return"].abs().mean(),
               bu_s=sp["Breakout_Up"].mean(), bu_n=nm["Breakout_Up"].mean())
    out["q2_rho"] = v["Volume_Ratio"].rank().corr(v["Daily_Return"].abs().rank())
    labels = ["<0.5×", "0.5–1×", "1–1.5×", "1.5–2×", "2–3×", "3–5×", ">5×"]
    bucket = pd.cut(v["Volume_Ratio"], [0, .5, 1, 1.5, 2, 3, 5, np.inf], labels=labels)
    out["q2_buckets"] = v["Daily_Return"].abs().groupby(bucket, observed=True).mean()
    blue = stats.nlargest(10, "Value")["Stock"].tolist()
    corr = f[f["Stock"].isin(blue)].pivot_table(index="Date", columns="Stock", values="Daily_Return").corr(min_periods=30)
    pairs = corr.where(np.triu(np.ones(corr.shape, bool), 1)).stack().dropna().sort_values(ascending=False)
    out["q3_avg"] = pairs.mean() if len(pairs) else np.nan
    out["q3_top"] = pairs.index[0] if len(pairs) else ("–", "–")
    vv = stats[stats["Days"] >= 60].dropna(subset=["CV", "Ann_Vol"])
    out["q4_cv"] = vv.nlargest(1, "CV")["Stock"].iloc[0] if len(vv) else "–"
    out["q4_av"] = vv.nlargest(1, "Ann_Vol")["Stock"].iloc[0] if len(vv) else "–"
    out["q4_low"] = vv.nsmallest(1, "Ann_Vol")["Stock"].iloc[0] if len(vv) else "–"
    return out


path = find_data()
if path is None:
    st.error(L(f"Could not find **{DATA_FILE}** — place it next to `app.py`.",
               f"لم يتم العثور على الملف **{DATA_FILE}** — ضعيه بجانب `app.py`."))
    st.stop()
raw = load_data(path)
ALL_SECTORS = sorted(raw["Stock_Sector"].unique())

_val = (raw["Close_Price"] * raw["Trade_Volume"]).groupby(raw["Stock_Symbol"]).sum().sort_values(ascending=False)
_third = int(np.ceil(len(_val) / 3))
TIER_SYMBOLS = {"top": tuple(_val.index[:_third]), "mid": tuple(_val.index[_third:2 * _third]),
                "low": tuple(_val.index[2 * _third:])}
SECTOR_COLOR = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(ALL_SECTORS)}
SECTOR_COLOR_LABEL = {sector_name(s): c for s, c in SECTOR_COLOR.items()}



# Live market 
RIYADH = ZoneInfo("Asia/Riyadh")
_official = pd.DataFrame([l.split("|") for l in TADAWUL_STOCKS.strip().splitlines()],
                         columns=["Stock_Symbol", "Company_Name", "Stock_Sector"])
_official["Stock_Symbol"] = _official["Stock_Symbol"].astype(int)
_ds = (raw.sort_values("Date").drop_duplicates("Stock_Symbol", keep="last")
       [["Stock_Symbol", "Company_Name", "Stock_Sector"]])
UNIVERSE = pd.concat([_official, _ds[~_ds["Stock_Symbol"].isin(_official["Stock_Symbol"])]], ignore_index=True)
UNIVERSE = UNIVERSE[UNIVERSE["Stock_Sector"] != "REITs"].reset_index(drop=True)    
UNIVERSE["Yahoo"] = UNIVERSE["Stock_Symbol"].astype(str) + ".SR"


_CAND_RANGES = [(1184, 1190), (1215, 1225), (1323, 1330), (1834, 1840), (2084, 2090), (2284, 2290), (2383, 2390),
                (3093, 3099), (4016, 4029), (4052, 4060), (4073, 4079), (4083, 4089), (4143, 4149), (4165, 4169),
                (4193, 4199), (4211, 4219), (4264, 4269), (4271, 4279), (4293, 4299), (4324, 4329), (5111, 5115),
                (6016, 6019), (6091, 6099), (7031, 7039), (7205, 7215), (8312, 8320)]
CANDIDATES = tuple(f"{c}.SR" for lo, hi in _CAND_RANGES for c in range(lo, hi + 1)
                   if c not in set(UNIVERSE["Stock_Symbol"]))


@st.cache_data(ttl=86400, show_spinner=False)
def discover_new(cands):
    """Find symbols listed after our reference list (Yahoo returns prices for them); name + sector from Yahoo."""
    empty = pd.DataFrame(columns=["Stock_Symbol", "Company_Name", "Stock_Sector", "Yahoo"])
    if yf is None:
        return empty
    try:
        d = yf.download(list(cands), period="5d", interval="1d", group_by="column",
                        auto_adjust=False, progress=False, threads=True)
    except Exception:
        return empty
    if d is None or d.empty:
        return empty
    rows = []
    for t in cands:
        try:
            if d["Close"][t].dropna().empty:
                continue
        except KeyError:
            continue
        name, sector = t[:-3], "Other"
        try:
            info = yf.Ticker(t).get_info()
            name = info.get("shortName") or info.get("longName") or name
            sector = info.get("sector") or "Other"
        except Exception:
            pass
        rows.append((int(t[:-3]), str(name).title() if str(name).isupper() else str(name), sector, t))
    return pd.DataFrame(rows, columns=empty.columns) if rows else empty


def market_status(now):
    """Tadawul main-market hours (Riyadh): pre-open 09:30, continuous 10:00–15:00, closing auction to 15:10, Sun–Thu."""
    if now.weekday() in (4, 5):                   
        return "weekend"
    t = now.hour * 60 + now.minute
    if 570 <= t < 600:
        return "preopen"
    if 600 <= t < 900:
        return "open"
    if 900 <= t < 910:
        return "closing"
    return "closed"


@st.cache_data(ttl=90, show_spinner=False)
def fetch_live(tickers):
    """Latest daily bar for every stock from Yahoo Finance (≈15-min delayed)."""
    if yf is None:
        return None, "yfinance is not installed"
    try:
        d = yf.download(list(tickers), period="5d", interval="1d", group_by="column",
                        auto_adjust=False, progress=False, threads=True)
    except Exception as e:                       
        return None, str(e)
    if d is None or d.empty:
        return None, "empty response from Yahoo Finance"
    rows = []
    for t in tickers:
        try:
            close = d["Close"][t].dropna()
        except KeyError:
            continue
        if len(close) < 2:
            continue
        day = close.index[-1]
        rows.append(dict(Yahoo=t, Last=float(close.iloc[-1]), Prev=float(close.iloc[-2]), Day=day,
                         High=float(d["High"][t].get(day, np.nan)), Low=float(d["Low"][t].get(day, np.nan)),
                         Volume=float(d["Volume"][t].get(day, np.nan))))
    if not rows:
        return None, "no prices returned"
    live = pd.DataFrame(rows)
    live["Day"] = (pd.to_datetime(live["Day"], utc=True).dt.tz_convert("Asia/Riyadh")
                   .dt.tz_localize(None).dt.normalize())
    return live, None


@st.cache_data(ttl=90, show_spinner=False)
def fetch_index():
    """TASI: latest close vs previous close, plus intraday (5-min) bars when Yahoo provides them."""
    if yf is None:
        return None
    try:
        tk, dly = None, None
        for sym in ("^TASI.SR", "^TASI", "TASI.SR"):
            t = yf.Ticker(sym)
            h3 = t.history(period="3mo", interval="1d")
            if h3 is not None and len(h3) >= 2:
                tk, dly = t, h3
                break
    except Exception:
        return None
    if tk is None:
        return None
    if dly.index.tz is not None:
        dly.index = dly.index.tz_convert("Asia/Riyadh").tz_localize(None)
    close = dly["Close"].dropna()
    intra = None
    try:
        h = tk.history(period="5d", interval="5m")
        if h is not None and not h.empty:
            if h.index.tz is not None:
                h.index = h.index.tz_convert("Asia/Riyadh").tz_localize(None)
            day = h.index.normalize().max()
            intra = h.loc[h.index.normalize() == day, "Close"].dropna()
            intra = intra if len(intra) > 1 else None
    except Exception:
        intra = None
    last = float(intra.iloc[-1]) if intra is not None else float(close.iloc[-1])
    day = intra.index[-1].normalize() if intra is not None else close.index[-1].normalize()
    prev_s = close[close.index.normalize() < day]
    prev = float(prev_s.iloc[-1]) if len(prev_s) else float(close.iloc[-2])
    return dict(intra=intra, daily=close, last=last, prev=prev, day=day)


@st.cache_data(show_spinner=False)
def offline_snapshot(path):
    """Fallback when the live feed is unreachable: the last session in the cleaned dataset."""
    d = prepare(path, True, False)
    last2 = d.groupby("Stock_Symbol").tail(2)
    g = last2.groupby("Stock_Symbol")
    snap = pd.DataFrame({"Last": g["Close_Price"].last(), "Prev": g["Close_Price"].first(),
                         "Day": g["Date"].last(), "High": g["High_Price"].last(),
                         "Low": g["Low_Price"].last(), "Volume": g["Trade_Volume"].last()}).reset_index()
    snap["Yahoo"] = snap["Stock_Symbol"].astype(str) + ".SR"
    snap = snap[snap["Day"] == snap["Day"].max()]
    return snap.drop(columns="Stock_Symbol")


def tape_html(df):
    def one(r):
        ch = r.Change if pd.notna(r.Change) else 0.0
        return (f'<span class="tk"><b>{r.Stock_Symbol}</b>{r.Company_Name[:18]}<span class="px">{r.Last:,.2f}</span>'
                f'<span class="{pct_cls(ch)}">{"▲" if ch >= 0 else "▼"} {ch:+.2%}</span></span>')
    items = "".join(one(r) for r in df.itertuples())
    summary = "; ".join(f"{r.Stock_Symbol} {r.Company_Name} {r.Last:,.2f} {r.Change:+.2%}" for r in df.head(10).itertuples())
    return (f'<div class="tape" aria-hidden="true"><div class="track">{items}{items}</div></div>'
            f'<p class="sr-only">{L("Most traded stocks", "الأسهم الأكثر تداولاً")}: {summary}</p>')


def movers_html(df, title, icon, value_col="Change"):
    rows = []
    for r in df.itertuples():
        right = (f'<span class="chg {pct_cls(r.Change)}">{r.Change:+.2%}</span>' if value_col == "Change"
                 else f'<span class="chg gold">SAR {big_num(r.Value)}</span>')
        rows.append(f'<div class="mv"><div class="mv-l"><b>{r.Stock_Symbol}</b><span>{r.Company_Name[:22]}</span></div>'
                    f'<div class="mv-r"><span class="mono">{r.Last:,.2f}</span>{right}</div></div>')
    return f'<div class="mvbox" dir="{DIR}"><div class="mvh">{icon} {title}</div>{"".join(rows)}</div>'


def status_pill(code):
    label, col = {
        "open": (L("Market open", "السوق مفتوح"), UP),
        "preopen": (L("Pre-open session", "جلسة ما قبل الافتتاح"), GOLD),
        "closing": (L("Closing auction", "مزاد الإغلاق"), GOLD),
        "closed": (L("Market closed", "السوق مغلق"), MUTED),
        "weekend": (L("Weekend · market closed", "عطلة نهاية الأسبوع · السوق مغلق"), MUTED),
    }[code]
    dot = f'<span class="live" style="background:{col}"></span>' if code == "open" else \
          f'<span style="width:8px;height:8px;border-radius:50%;background:{col};display:inline-block"></span>'
    return f'<span class="status" role="status" style="background:{alpha(col, .13)};color:{col}">{dot}{label}</span>'


def _clear_live():
    fetch_live.clear()
    fetch_index.clear()


def home_live():
    now = datetime.now(RIYADH)
    status = market_status(now)
    with st.spinner(L("Fetching the latest prices…", "جاري جلب آخر الأسعار…")):
        universe = pd.concat([UNIVERSE, discover_new(CANDIDATES)], ignore_index=True).drop_duplicates("Yahoo")
        live, err = fetch_live(tuple(universe["Yahoo"]))
        idx = fetch_index() if live is not None else None
    source = "live"
    if live is None or live.empty:
        live, source = offline_snapshot(path), "offline"
    if source == "offline":
        universe = UNIVERSE
    live = live.drop(columns=[c for c in ("Stock_Symbol", "Company_Name", "Stock_Sector") if c in live]).merge(
        universe, on="Yahoo", how="inner")
    live["Change"] = live["Last"] / live["Prev"] - 1
    live["Value"] = live["Last"] * live["Volume"].fillna(0)
    live["Sector"] = live["Stock_Sector"].map(sector_name)
    session_day = pd.Timestamp(live["Day"].max())

    #page banner
    src_line = (L("Yahoo Finance · delayed ≈15 min", "Yahoo Finance · متأخرة ≈١٥ دقيقة")
                if source == "live" else L("Offline · last session in the dataset", "بدون اتصال · آخر جلسة في البيانات"))
    with st.container(key="herobox"):
        with st.container(key="refreshbtn"):        
            st.button(L(":material/refresh: Refresh", ":material/refresh: تحديث"), key="refresh", on_click=_clear_live)
        hb1, hb2 = st.columns([3, 1.1], vertical_alignment="center")
        hb1.markdown(f"""<div class="hero hero-flat" dir="{DIR}"><div>
          <div class="kicker">{L("Tadawul · Main Market (TASI)", "تداول · السوق الرئيسية (تاسي)")}</div>
          <h1>{L("Saudi market <span>today</span>", "السوق السعودي <span>اليوم</span>")}</h1>
          <div class="sub">{L("Session", "الجلسة")}: <bdi>{ldate(session_day, True)}</bdi> &nbsp;·&nbsp;
            {L("updated", "آخر تحديث")} <bdi dir="ltr" class="mono">{now:%H:%M}</bdi> {L("Riyadh", "بتوقيت الرياض")}</div>
          <div class="src">{src_line}</div>
        </div></div>""".replace("\n", ""), unsafe_allow_html=True)
        with hb2:
            html(f'<div class="stamp-col">{status_pill(status)}</div>')
    if source == "offline":
        st.warning(L(f"Live feed unavailable ({err}). Showing the last session stored in the dataset. "
                     "Install `yfinance` and check your internet connection to go live.",
                     f"تعذّر الاتصال بالبيانات المباشرة ({err}). نعرض آخر جلسة محفوظة في البيانات. "
                     "ثبّتي `yfinance` وتأكدي من الاتصال بالإنترنت لتفعيل البث المباشر."))

    html(tape_html(live.nlargest(30, "Value")))

    
    n_all = max(len(live), 1)
    adv, dec = int((live["Change"] > 0).sum()), int((live["Change"] < 0).sum())
    unch = len(live) - adv - dec
    avg = float(live["Change"].mean())
    sec = live.groupby("Sector")["Change"].mean().sort_values()
    best_sec, worst_sec = sec.index[-1], sec.index[0]
    avg_s, best_s, worst_s = f"{avg:+.2%}", f"{sec.iloc[-1]:+.2%}", f"{sec.iloc[0]:+.2%}"

    
    if idx:
        ich = idx["last"] / idx["prev"] - 1
        ich_s, last_s, ich_abs = f"{ich:+.2%}", f"{idx['last']:,.2f}", f"{abs(ich):.2%}"
        verb = (L("rose", "ارتفع") if ich > 0 else L("fell", "انخفض") if ich < 0 else L("was flat", "استقر"))
        lead = L(f"The TASI index {verb} <b>{N(ich_abs)}</b> to <b>{N(last_s)}</b> points.",
                 f"مؤشر تاسي {verb} بنسبة <b>{N(ich_abs)}</b> ليصل إلى <b>{N(last_s)}</b> نقطة.")
    else:
        lead = L(f"The average stock moved <b>{N(avg_s)}</b>.", f"تحرّك السهم المتوسط <b>{N(avg_s)}</b>.")
    takeaway(lead + L(
        f" <b>{adv}</b> stocks rose and <b>{dec}</b> fell. Strongest sector: <b>{best_sec}</b> ({N(best_s)}); "
        f"weakest: <b>{worst_sec}</b> ({N(worst_s)}).",
        f" ارتفع <b>{adv}</b> سهماً وانخفض <b>{dec}</b>. أفضل قطاع: <b>{best_sec}</b> ({N(best_s)})، "
        f"والأضعف: <b>{worst_sec}</b> ({N(worst_s)})."))

    
    def brow(label, count, cls):
        share = count / n_all
        return (f'<div class="br-row"><span>{label}</span><b class="{cls}">{count}</b></div>'
                f'<div class="br-track"><i class="{cls}-bg" style="width:{share * 100:.1f}%"></i></div>')
    breadth_html = (f'<div class="br" dir="{DIR}"><div class="br-h">{L("Market breadth", "اتساع السوق")}</div>'
                    f'<div class="br-s">{L("How many stocks went up or down today", "كم سهماً ارتفع أو انخفض اليوم")}</div>'
                    + brow(L("Rising ▲", "مرتفعة ▲"), adv, "up") + brow(L("Falling ▼", "منخفضة ▼"), dec, "down")
                    + brow(L("Unchanged", "بدون تغيير"), unch, "flat")
                    + f'<div class="br-foot"><div><span>{L("Traded value", "قيمة التداول")}</span><b>SAR {big_num(live["Value"].sum())}</b></div>'
                      f'<div><span>{L("Stocks", "الأسهم")}</span><b>{len(live)}</b></div></div></div>')
    if idx:
        c1, c2 = st.columns([2, 1], gap="medium")
        with c1, card():
                col = UP if ich >= 0 else DOWN
                arrow = "▲" if ich >= 0 else "▼"
                html(f'<div class="ix" dir="{DIR}"><div class="ix-l">{L("TASI · Tadawul All Share Index", "تاسي · مؤشر السوق الرئيسية")}</div>'
                     f'<div class="ix-v">{last_s}</div><div class="ix-c {pct_cls(ich)}"><bdi dir="ltr">{arrow} '
                     f'{idx["last"] - idx["prev"]:+,.2f} ({ich_s})</bdi> <span>{L("vs previous close", "مقارنة بإغلاق الجلسة السابقة")}</span></div></div>')
                if idx["intra"] is not None:
                    ser, sub = idx["intra"], L("Today, every 5 minutes", "اليوم، كل ٥ دقائق")
                    hover = "%{x|%H:%M}<br>%{y:,.2f}<extra></extra>"
                else:
                    ser, sub = idx["daily"], L("Last 3 months, daily close", "آخر ٣ أشهر، إغلاق يومي")
                    hover = "%{x|%d %b %Y}<br>%{y:,.2f}<extra></extra>"
                lcol = UP if ser.iloc[-1] >= ser.iloc[0] else DOWN
                fig = go.Figure(go.Scatter(x=ser.index, y=ser.values, mode="lines", line=dict(color=lcol, width=2.2),
                                           fill="tozeroy", fillcolor=alpha(lcol, .08), hovertemplate=hover))
                if idx["intra"] is not None:
                    fig.add_hline(y=idx["prev"], line_dash="dot", line_color=MUTED,
                                  annotation_text=L("previous close", "إغلاق أمس"), annotation_font_color=MUTED)
                lo, hi = float(ser.min()), float(ser.max())
                fig.update_yaxes(range=[lo - (hi - lo) * .12, hi + (hi - lo) * .12], tickformat=",.0f")
                html(f'<div class="ix-sub" dir="{DIR}">{sub}</div>')
                chart(style(fig, 280, legend=False))
        with c2, card():
            html(breadth_html)
    else:
        
        with card():
            k1, k2 = st.columns([1, 1.5], gap="large", vertical_alignment="center")
            with k1:
                html(f'<div class="ix" dir="{DIR}"><div class="ix-l">{L("Average stock today", "متوسط تغيّر الأسهم اليوم")}</div>'
                     f'<div class="ix-v {pct_cls(avg)}">{avg_s}</div>'
                     f'<div class="ix-c"><span>{L("The TASI index feed is not available right now, so this is the average change of all stocks.", "بيانات مؤشر تاسي غير متاحة الآن، لذلك نعرض متوسط تغيّر جميع الأسهم.")}</span></div></div>')
            with k2:
                html(breadth_html)

    
    m = st.columns(3, gap="medium")
    m[0].markdown(movers_html(live.nlargest(8, "Change"), L("Top gainers", "الأكثر ارتفاعاً"), ""), unsafe_allow_html=True)
    m[1].markdown(movers_html(live.nsmallest(8, "Change"), L("Top losers", "الأكثر انخفاضاً"), ""), unsafe_allow_html=True)
    m[2].markdown(movers_html(live.nlargest(8, "Value"), L("Most traded (by value)", "الأكثر تداولاً (بالقيمة)"), "", "Value"),
                  unsafe_allow_html=True)
    gap()

    
    with card():
        fig = go.Figure(go.Bar(x=sec.values, y=sec.index, orientation="h",
                               marker_color=[UP if v >= 0 else DOWN for v in sec.values],
                               text=[f"{v:+.2%}" for v in sec.values], textposition="outside",
                               hovertemplate="%{y}<br>%{x:+.2%}<extra></extra>"))
        fig.update_xaxes(tickformat=".1%")
        chart(style(fig, 26 * len(sec) + 120, L("Sectors today · average change of their stocks",
                                                "القطاعات اليوم · متوسط تغيّر أسهم كل قطاع"), legend=False))
        html(f'<div class="legend-note" dir="{DIR}"><span class="dot up-bg"></span>{L("sector rose today", "القطاع ارتفع اليوم")}'
             f'<span class="dot down-bg"></span>{L("sector fell today", "القطاع انخفض اليوم")}</div>')
    gap()

    
    with card():
        html(f'<div class="br-h" dir="{DIR}">{L("All stocks", "جميع الأسهم")} · {len(live)}</div>'
             f'<div class="br-s" dir="{DIR}">{L("Every share on the main market today. Click a column title to sort.", "كل أسهم السوق الرئيسية اليوم. اضغطي على عنوان العمود للترتيب.")}</div>')
        f1, f2 = st.columns([1.2, 2], gap="medium")
        q = f1.text_input(L("Search by name or symbol", "ابحثي بالاسم أو الرمز"), key="all_q")
        secs = sorted(live["Sector"].unique())
        pick = f2.multiselect(L("Sectors", "القطاعات"), secs, key="all_sec",
                              placeholder=L("All sectors", "كل القطاعات"))
        tbl = live.copy()
        if q:
            tbl = tbl[tbl["Company_Name"].str.contains(q, case=False, na=False)
                      | tbl["Stock_Symbol"].astype(str).str.startswith(q.strip())]
        if pick:
            tbl = tbl[tbl["Sector"].isin(pick)]
        tbl = tbl.sort_values("Value", ascending=False)
        view = pd.DataFrame({
            L("Symbol", "الرمز"): tbl["Stock_Symbol"].astype(str),
            L("Company", "الشركة"): tbl["Company_Name"],
            L("Sector", "القطاع"): tbl["Sector"],
            L("Price", "السعر"): tbl["Last"],
            L("Change %", "التغير %"): tbl["Change"] * 100,
            L("High", "الأعلى"): tbl["High"],
            L("Low", "الأدنى"): tbl["Low"],
            L("Volume", "الكمية"): tbl["Volume"],
            L("Value (SAR)", "القيمة (ريال)"): tbl["Value"],
        })
        chg_col = L("Change %", "التغير %")
        _sty = view.style
        _map = getattr(_sty, "map", None) or _sty.applymap        # pandas < 2.1 uses applymap
        styled = (_map(lambda v: f"color: {UP if v > 0 else DOWN if v < 0 else MUTED}; font-weight: 600",
                       subset=[chg_col])
                  .format({L("Price", "السعر"): "{:,.2f}", chg_col: "{:+.2f}%", L("High", "الأعلى"): "{:,.2f}",
                           L("Low", "الأدنى"): "{:,.2f}", L("Volume", "الكمية"): "{:,.0f}",
                           L("Value (SAR)", "القيمة (ريال)"): "{:,.0f}"}))
        table(styled, hide_index=True, height=520)
        st.caption(L(f"Showing {len(view)} of {len(live)} stocks · sorted by traded value.",
                     f"عرض {len(view)} من {len(live)} سهماً · مرتبة حسب قيمة التداول."))

    st.caption(L("Prices come from Yahoo Finance and are delayed about 15 minutes; this is not Tadawul's official real-time feed. "
                 "Company names and sectors follow Tadawul's official list.",
                 "الأسعار من Yahoo Finance ومتأخرة نحو ١٥ دقيقة، وليست البث الرسمي اللحظي من تداول. "
                 "أسماء الشركات والقطاعات حسب قائمة تداول الرسمية."))



# Top navbar
SERVICES = [L("Market Today", "السوق اليوم"), L("Historical Analysis", "التحليل التاريخي"),
            L("Developer Corner", "زاوية المبرمج"), L("Settings", "الإعدادات")]

if "svc" not in st.session_state:         
    _q = str(st.query_params.get("svc", "0"))
    st.session_state.svc = int(_q) if _q.isdigit() and int(_q) < len(SERVICES) else 0

for _k in ("_nav_d", "_nav_m"):
    st.session_state[_k] = st.session_state.svc


def _nav_changed(src):
    v = st.session_state[src]
    st.session_state.svc = st.session_state["_nav_d"] = st.session_state["_nav_m"] = v
    st.query_params["svc"] = str(v)


def svc_href(i):
    """Link to service i that keeps the user's settings in the URL."""
    q = {k: v for k, v in st.query_params.items() if k != "svc"}
    q["svc"] = str(i)
    return "?" + urlencode(q)


SERVICE = st.session_state.svc

# splash
_splash_nonce = ""
if st.session_state.get("_last_service") != SERVICE:
    st.session_state["_last_service"] = SERVICE
    st.session_state["_splash_n"] = st.session_state.get("_splash_n", 0) + 1
    _splash_nonce = str(st.session_state["_splash_n"])
_splash_html = (f'<div class="splash-in" dir="{DIR}">{LOGO_SVG}<div class="splash-t">{L("Nabd Tadawul", "نبض تداول")}</div>'
                f'<div class="splash-s">{L(f"Opening {SERVICES[SERVICE]}…", f"جاري فتح {SERVICES[SERVICE]}…")}</div>'
                f'<div class="splash-bar"><span></span></div></div>')
with st.container(key="fx"):
    components.html("""<script>(function(){
const d = window.parent.document;
d.querySelectorAll("link[rel*='icon']").forEach(l => l.remove());
const ic = d.createElement('link'); ic.rel = 'icon'; ic.type = 'image/png';
ic.href = 'data:image/png;base64,""" + FAVICON_B64 + """'; d.head.appendChild(ic);
const N = """ + json.dumps(_splash_nonce) + """;
if (!N || d.body.dataset.tpSplash === N) return;
d.body.dataset.tpSplash = N;
const old = d.getElementById('tp-splash'); if (old) old.remove();
const w = d.createElement('div'); w.id = 'tp-splash'; w.className = 'splash'; w.setAttribute('aria-hidden', 'true');
w.innerHTML = """ + json.dumps(_splash_html) + """;
d.body.appendChild(w);
const t0 = Date.now();
const done = () => { w.classList.add('out'); setTimeout(() => w.remove(), 500); };
const tick = () => {
  const busy = d.querySelector('[data-stale="true"]');
  const t = Date.now() - t0;
  if ((t > 900 && !busy) || t > 6000) done(); else setTimeout(tick, 120);
};
setTimeout(tick, 900);
})();</script>""", height=0)

with st.container(key="appbar"):
    ab1, ab2, ab3 = st.columns([1.15, 3.4, .45], vertical_alignment="center")
    ab1.markdown(f"""<div class="brand" dir="{DIR}">{LOGO_SVG}<div><div class="t">{L("Nabd Tadawul", "نبض تداول")}</div>
<div class="s">{L("Saudi market insights", "رؤى السوق السعودي")}</div></div></div>""".replace("\n", ""), unsafe_allow_html=True)
    with ab2, st.container(key="navd"):
        st.radio("Service", list(range(len(SERVICES))), format_func=lambda i: SERVICES[i], horizontal=True,
                 label_visibility="collapsed", key="_nav_d", on_change=_nav_changed, args=("_nav_d",))
    with ab3, st.container(key="navm"):
        with st.popover(":material/menu:"):
            st.radio(L("Go to", "انتقل إلى"), list(range(len(SERVICES))), format_func=lambda i: SERVICES[i],
                     key="_nav_m", on_change=_nav_changed, args=("_nav_m",))



# Market Today

if SERVICE == 0:
    st.fragment(run_every=st.session_state.get("refresh_every", 120))(home_live)()
    gap()
    h1, h2 = st.columns([2.2, 1], gap="large", vertical_alignment="bottom")
    h1.caption(L("Trading hours: Sun–Thu, 10:00–15:00 Riyadh (pre-open 09:30, closing auction until 15:10). "
                 "Prices from Yahoo Finance, delayed about 15 minutes.",
                 "أوقات التداول: الأحد–الخميس، ١٠:٠٠–١٥:٠٠ بتوقيت الرياض (ما قبل الافتتاح ٩:٣٠، ومزاد الإغلاق حتى ١٥:١٠). "
                 "الأسعار من Yahoo Finance ومتأخرة نحو ١٥ دقيقة."))
    h2.select_slider(L("Auto-refresh every", "تحديث تلقائي كل"), options=[30, 60, 120, 300], value=120,
                     format_func=lambda s: L(f"{s // 60} min", f"{s // 60} د") if s >= 60 else L(f"{s} s", f"{s} ث"),
                     key="refresh_every")


# Historical Analysis 
elif SERVICE == 1:
    panel, body = st.columns([1, 3.5], gap="large")
    with panel, st.container(key="filters"):
        html(f'<div class="panel-h" dir="{DIR}">{L("Filters", "الفلاتر")}</div>')
        with st.expander(L("About the data", "عن البيانات"), expanded=False):
            st.markdown(L(
                f"Daily prices (OHLC), volume, dividends and splits for **{raw['Stock_Symbol'].nunique()} stocks** "
                f"on the Saudi Exchange, **{raw['Date'].min():%b %Y} → {raw['Date'].max():%b %Y}**.  \n"
                "Source: Kaggle *Saudi Arabian Stock Market Data*, cleaned in the project notebook. Company names and "
                "industry groups follow Tadawul's official list. Prices are adjusted for dividends & splits.",
                f"أسعار يومية (افتتاح، أعلى، أدنى، إغلاق) وحجم التداول والتوزيعات والتجزئة لـ "
                f"**{raw['Stock_Symbol'].nunique()} سهماً** في السوق المالية السعودية من "
                f"**{raw['Date'].min():%Y/%m}** إلى **{raw['Date'].max():%Y/%m}**.  \n"
                ))

        dmin, dmax = raw["Date"].min().date(), raw["Date"].max().date()
        d_range = st.slider(L("Period", "الفترة"), dmin, dmax, (dmin, dmax), format="MMM YYYY")
        picked = st.multiselect(L("Industry groups", "القطاعات"), ALL_SECTORS, format_func=sector_name, key="sectors",
                                placeholder=L("All groups", "كل القطاعات"),
                                help=L("Leave empty to include every group.", "اتركيه فارغاً لعرض كل القطاعات."))
        sectors = picked or ALL_SECTORS
        tier = st.selectbox(L("Stocks", "الأسهم"), ["all", "top", "mid", "low"], key="tier",
                            format_func=lambda t: {"all": L("All stocks", "كل الأسهم"),
                                                   "top": L("Most traded third", "الثلث الأعلى تداولاً"),
                                                   "mid": L("Middle third", "الثلث الأوسط"),
                                                   "low": L("Least traded third", "الثلث الأقل تداولاً")}[t],
                            help=L("Stocks split into thirds by total traded value (SAR) over 2022 – 2025.",
                                   "الأسهم مقسّمة إلى ثلاث فئات حسب إجمالي قيمة تداولها (ريال) في ٢٠٢٢ – ٢٠٢٥."))
        spike_k = st.slider(L("Volume spike = volume ≥ k × 20-day average", "قفزة الحجم = الحجم ≥ k × متوسط 20 يوماً"),
                            2.0, 6.0, 3.0, 0.5)
        
        excl, clean = True, True

    with body:
        start, end = pd.Timestamp(d_range[0]), pd.Timestamp(d_range[1])
        f, mkt, stats = build(path, excl, clean, start, end, tuple(sectors), tier)
        if f.empty or len(mkt) < 2:
            st.warning(L("Not enough data for these filters — widen the period or add sectors.",
                         "لا توجد بيانات كافية — وسّعي الفترة أو أضيفي قطاعات."))
            st.stop()
        f["Sector"] = f["Stock_Sector"].map(sector_name)
        stats["Sector"] = stats["Stock_Sector"].map(sector_name)

        hero_box = st.container(key="herobox_h")
        with hero_box:
            html(f"""
        <div class="hero hero-flat" dir="{DIR}">
          <div>
            <div class="kicker">{L("Saudi Exchange · Exploratory Data Analysis", "السوق المالية السعودية · تحليل استكشافي للبيانات")}</div>
            <h1>{L("The story of <span>Tadawul</span>, 2022 – 2025", "تحليل <span>تداول</span> ٢٠٢٢ – ٢٠٢٥")}</h1>
            <div class="sub">{L(" Distributions, relationships and the four questions",
                                "التوزيعات، العلاقات، والأسئلة الأربعة")}</div>
          </div>
          <div class="stamp"><span class="pill"><span class="live"></span>{L("Data window", "نافذة البيانات")}</span><br>
            <b class="mono" dir="ltr">{fdate(start)} → {fdate(end)}</b><br>
            {stats.shape[0]} {L("stocks", "سهماً")} · {len(sectors)} {L("sectors", "قطاعات")}</div>
        </div>
        """)

        PAGES = [L("The data", "البيانات"), L("Distributions", "التوزيعات"), L("Relationships", "العلاقات"),
                 L("Sectors", " القطاعات"), L(" Volume spikes", "قفزات الحجم"),
                 L("Correlation", " الارتباط"), L("Volatility", "التذبذب"),
                 L("Conclusions", "الخلاصة"), L("What-If", "ماذا لو")]
        with hero_box, st.container(key="nav"):
            page = keep_radio("Navigate", PAGES, "page", horizontal=True, label_visibility="collapsed")

        FX = findings(path, excl, clean, start, end, tuple(sectors), spike_k, tier)
        DAYS_L = L("Number of days", "عدد الأيام")

        def loghist(s, color, title, xtitle, ytitle=DAYS_L, h=340, bins=50):
            """Histogram on a log scale (counts pre-computed, so the page stays light)."""
            s = np.log10(s[s > 0].dropna())
            cnt, edges = np.histogram(s, bins)
            mid = (edges[:-1] + edges[1:]) / 2
            fig = go.Figure(go.Bar(x=mid, y=cnt, marker_color=color, marker_line_width=0,
                                   customdata=10 ** mid, hovertemplate="≈ %{customdata:,.3s}<br>%{y:,}<extra></extra>"))
            ticks = list(range(int(np.floor(edges[0])), int(np.ceil(edges[-1])) + 1))
            fig.update_xaxes(tickvals=ticks, ticktext=[f"{10 ** t:,.0f}" if t >= 0 else f"{10 ** t:g}" for t in ticks],
                             title=xtitle)
            fig.update_yaxes(title=ytitle)
            fig.update_layout(bargap=0.04)
            return style(fig, h, title, legend=False)

        def hbar(values, labels, title, fmt, color=None, h=None, hover=None):
            """Horizontal bar with value labels; colours by sign unless a colour is given."""
            cols = color or [UP if v >= 0 else DOWN for v in values]
            fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color=cols, marker_line_width=0,
                                   text=[fmt(v) for v in values], textposition="outside",
                                   hovertemplate=hover or "%{y}<br>%{text}<extra></extra>"))
            return style(fig, h or 28 * len(values) + 110, title, legend=False)

      
        # The data 
        if page == 0:
            chapter(1, L("The data", "البيانات"),
                    L("A clean data you are exploring?", " البيانات النظيفة "))
            c = st.columns(4)
            kpi(c[0], L("Rows", "الصفوف"), f"{len(f):,}", L("one stock on one trading day", "سهم واحد في يوم تداول واحد"))
            kpi(c[1], L("Stocks", "الأسهم"), f"{f['Stock_Symbol'].nunique()}", L("listed on Tadawul", "مدرجة في تداول"), "gold")
            kpi(c[2], L("Industry groups", "القطاعات"), f"{f['Stock_Sector'].nunique()}",
                L("Tadawul classification", "حسب تصنيف تداول"))
            kpi(c[3], L("Trading days", "أيام التداول"), f"{f['Date'].nunique():,}",
                L(f"{fdate(f['Date'].min(), '%b %Y')} → {fdate(f['Date'].max(), '%b %Y')}",
                  f"{N(fdate(f['Date'].min(), '%Y/%m'))} ← {N(fdate(f['Date'].max(), '%Y/%m'))}"))
            st.write("")

            prev_cols = ["Date", "Stock_Symbol", "Company_Name", "Sector", "Open_Price", "High_Price", "Low_Price",
                         "Close_Price", "Trade_Volume", "Daily_Return", "Traded_Value"]
            c1, c2 = st.columns([1.5, 1], gap="medium")
            with c1, card():
                html(f'<div class="br-h" dir="{DIR}">{L("Data preview", "معاينة البيانات")}</div>'
                     f'<div class="br-s" dir="{DIR}">{L("The latest rows of the clean data with your filters.", "أحدث صفوف البيانات النظيفة حسب الفلاتر.")}</div>')
                table(f.sort_values(["Date", "Stock_Symbol"], ascending=[False, True])[prev_cols].head(200)
                      .assign(Daily_Return=lambda d_: d_["Daily_Return"] * 100), hide_index=True,
                      height=380, column_config={"Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
                                                 "Daily_Return": st.column_config.NumberColumn(format="%.2f%%"),
                                                 "Stock_Symbol": st.column_config.NumberColumn(format="%d")})
            with c2, card():
                html(f'<div class="br-h" dir="{DIR}">{L("Summary statistics", "الإحصاءات الوصفية")}</div>'
                     f'<div class="br-s" dir="{DIR}">{L("For the numeric columns, with your filters.", "للأعمدة الرقمية، حسب الفلاتر.")}</div>')
                desc = f[["Close_Price", "Trade_Volume", "Daily_Return", "Traded_Value"]].assign(
                    Daily_Return=lambda d_: d_["Daily_Return"] * 100).describe().T
                desc.index = [L("Close", "الإغلاق"), L("Volume", "الحجم"), L("Daily return (%)", "العائد اليومي (%)"),
                              L("Traded value", "قيمة التداول")]
                desc.columns = [L("count", "العدد"), L("mean", "المتوسط"), L("std", "الانحراف"), L("min", "الأدنى"),
                                "25%", L("median", "الوسيط"), "75%", L("max", "الأعلى")]
                table(desc.style.format("{:,.2f}"), height=200)

            per_year = f.groupby("Year").agg(rows=("Date", "size"), days=("Date", "nunique"), stocks=("Stock_Symbol", "nunique"))
            with card():
                fig = go.Figure([go.Bar(x=per_year.index.astype(str), y=per_year["stocks"], name=L("Stocks", "الأسهم"),
                                        marker_color=TEAL, text=per_year["stocks"], textposition="outside"),
                                 go.Bar(x=per_year.index.astype(str), y=per_year["days"], name=L("Trading days", "أيام التداول"),
                                        marker_color=GOLD, text=per_year["days"], textposition="outside")])
                fig.update_layout(barmode="group", bargap=.35)
                chart(style(fig, 330, L("Clean data per year · stocks covered and trading days",
                                        "البيانات النظيفة لكل سنة · عدد الأسهم وأيام التداول")))
            takeaway(L(
                f"After cleaning: <b>{N(f'{len(f):,}')}</b> stock-days for <b>{f['Stock_Symbol'].nunique()}</b> stocks in "
                f"<b>{f['Stock_Sector'].nunique()}</b> industry groups.",
                f"بعد التنظيف: <b>{N(f'{len(f):,}')}</b> سجل يومي لـ <b>{f['Stock_Symbol'].nunique()}</b> سهماً في "
                f"<b>{f['Stock_Sector'].nunique()}</b> مجموعة."))

        
        # Distributions (univariate)
    
        elif page == 1:
            chapter(2, L("Distributions", "التوزيعات"),
                    L("How are prices, trading activity and daily returns spread out?",
                      "كيف تتوزع الأسعار ونشاط التداول والعوائد اليومية؟"))
            p, val = f["Close_Price"], f["Traded_Value"]
            r = f["Daily_Return"].dropna()
            c = st.columns(4)
            kpi(c[0], L("Median close price", "وسيط سعر الإغلاق"), f"SAR {p.median():.1f}",
                L(f"mean SAR {p.mean():.1f} · max SAR {p.max():,.0f}", f"المتوسط {p.mean():.1f} · الأعلى {p.max():,.0f} ريال"))
            kpi(c[1], L("Typical traded value", "قيمة التداول المعتادة"), f"SAR {big_num(val.median())}",
                L("per stock per day (median)", "لكل سهم في اليوم (الوسيط)"))
            kpi(c[2], L("Daily return spread", "تشتت العائد اليومي"), f"{r.std():.2%}",
                L("standard deviation", "الانحراف المعياري"), "gold")
            kpi(c[3], L("Calm days", "أيام هادئة"), f"{(r.abs() <= .02).mean():.0%}",
                L("of days moved less than ±2%", "من الأيام تحركت أقل من ±2%"), "up")
            st.write("")

            c1, c2 = st.columns(2, gap="medium")
            with c1, card():
                chart(loghist(p, TEAL, L("Close price", "سعر الإغلاق"), L("SAR", "ريال")))
            with c2, card():
                cnt, edges = np.histogram(r.clip(-.1, .1), np.linspace(-.1, .1, 81))
                mid = (edges[:-1] + edges[1:]) / 2
                fig = go.Figure(go.Bar(x=mid, y=cnt, marker_color=[UP if m >= 0 else DOWN for m in mid], marker_line_width=0,
                                       hovertemplate="%{x:+.2%}<br>%{y:,}<extra></extra>"))
                fig.update_xaxes(tickformat=".0%", title=L("Daily return", "العائد اليومي"))
                fig.update_yaxes(title=DAYS_L)
                fig.update_layout(bargap=0.04)
                chart(style(fig, 340, L("Daily returns", "العوائد اليومية"), legend=False))
            takeaway(L(
                f"Prices are strongly right-skewed: half of all closes are below <b>SAR {N(f'{p.median():.1f}')}</b>, while a few "
                f"expensive stocks pull the mean up to SAR {N(f'{p.mean():.1f}')}; these are real stocks, not errors. Daily "
                f"returns centre on zero and <b>{N(f'{(r.abs() <= .02).mean():.0%}')}</b> of days move less than ±2%, but the tails "
                "are fat: big moves happen more often than a bell curve suggests.",
                f"الأسعار ملتوية بقوة لليمين: نصف أسعار الإغلاق أقل من <b>{N(f'{p.median():.1f}')} ريال</b>، بينما ترفع أسهم قليلة "
                f"مرتفعة الثمن المتوسط إلى {N(f'{p.mean():.1f}')} ريال، وهي أسهم حقيقية وليست أخطاء. العوائد اليومية تتمركز حول "
                f"الصفر و<b>{N(f'{(r.abs() <= .02).mean():.0%}')}</b> من الأيام تتحرك أقل من ±2%، لكن الأطراف سميكة: الحركات "
                "الكبيرة أكثر تكراراً مما يتوقعه التوزيع الطبيعي."))

            c1, c2 = st.columns(2, gap="medium")
            with c1, card():
                chart(loghist(val, GOLD, L("Traded value per stock per day", "قيمة التداول لكل سهم يومياً"),
                              L("SAR", "ريال"), h=420))
            with c2, card():
                cpg = f.drop_duplicates("Stock_Symbol")["Sector"].value_counts().sort_values()
                chart(hbar(cpg.values, cpg.index, L("Companies per industry group", "عدد الشركات في كل مجموعة"),
                           lambda v: f"{v}", color=TEAL, h=420))
            takeaway(L(
                f"Trading activity spans several orders of magnitude, so medians and log scales are needed. The groups are "
                f"unbalanced: <b>{cpg.index[-1]}</b> has {cpg.iloc[-1]} companies, while some groups have only one or two, so a "
                "single company can drive a whole group's result.",
                f"نشاط التداول يمتد عبر عدة مراتب عددية، لذلك نحتاج الوسيط والمقياس اللوغاريتمي. المجموعات غير متوازنة: "
                f"<b>{cpg.index[-1]}</b> فيها {N(cpg.iloc[-1])} شركة، وبعض المجموعات فيها شركة أو شركتان فقط، فقد تحرّك شركة "
                "واحدة نتيجة المجموعة كاملة."))

            with card():
                days = f.groupby("Stock_Symbol")["Date"].nunique()
                cnt, edges = np.histogram(days, 30)
                mid = (edges[:-1] + edges[1:]) / 2
                fig = go.Figure(go.Bar(x=mid, y=cnt, marker_color=GOLD, marker_line_width=0,
                                       hovertemplate="≈ %{x:.0f}<br>%{y}<extra></extra>"))
                fig.update_xaxes(title=L("Trading days available", "أيام التداول المتاحة"))
                fig.update_yaxes(title=L("Stocks", "الأسهم"))
                fig.update_layout(bargap=0.04)
                chart(style(fig, 300, L("History available per stock", "طول السجل المتاح لكل سهم"), legend=False))
            short_n = int((days < days.max() * .6).sum())
            takeaway(L(f"Most stocks cover the whole period; <b>{short_n}</b> were listed later (IPOs), which is why the analysis "
                       "uses daily returns and equal weights instead of raw prices.",
                       f"أغلب الأسهم تغطي الفترة كاملة، و<b>{N(short_n)}</b> أُدرجت لاحقاً (اكتتابات)، ولهذا يعتمد التحليل على العوائد "
                       "اليومية والأوزان المتساوية بدل الأسعار."))

        
        #  Relationships (bivariate)
      
        elif page == 2:
            chapter(3, L("Relationships", "العلاقات"),
                    L("Which features move together?", "أي الخصائص تتحرك معاً؟"))
            names = {"Open_Price": L("Open", "الافتتاح"), "High_Price": L("High", "الأعلى"), "Low_Price": L("Low", "الأدنى"),
                     "Close_Price": L("Close", "الإغلاق"), "Trade_Volume": L("Volume", "الحجم"),
                     "Daily_Return": L("Daily return", "العائد اليومي"), "Intraday_Range": L("Intraday range", "المدى اليومي")}
            corr = f[list(names)].corr().rename(index=names, columns=names)
            c1, c2 = st.columns([1.1, 1], gap="medium")
            with c1, card():
                fig = px.imshow(corr.values, x=list(corr.columns), y=list(corr.index), zmin=-1, zmax=1, text_auto=".2f",
                                aspect="auto", color_continuous_scale=[[0, DOWN], [.5, NEUTRAL], [1, TEAL]])
                if AR:
                    fig.update_xaxes(autorange="reversed")
                    fig.update_yaxes(side="right")
                chart(style(fig, 430, L("Correlation between the numeric features", "الارتباط بين الخصائص الرقمية"), legend=False))
            with c2, card():
                smp = f.sample(min(len(f), 4000), random_state=1)
                fig = go.Figure(go.Scattergl(x=smp["Open_Price"], y=smp["Close_Price"], mode="markers",
                                             marker=dict(size=4, color=TEAL, opacity=.4),
                                             hovertemplate="%{x:,.2f} → %{y:,.2f}<extra></extra>"))
                lo, hi = float(smp["Open_Price"].min()), float(smp["Open_Price"].max())
                fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", line=dict(color=DOWN, width=1.2, dash="dot"),
                                         hoverinfo="skip"))
                fig.update_xaxes(type="log", title=L("Open (SAR)", "الافتتاح (ريال)"))
                fig.update_yaxes(type="log", title=L("Close (SAR)", "الإغلاق (ريال)"))
                chart(style(fig, 430, L("Open vs close (4,000 random days)", "الافتتاح مقابل الإغلاق (٤٬٠٠٠ يوم عشوائي)"),
                            legend=False))
            iv = corr.iloc[-1]
            takeaway(L(
                "Open, high, low and close are almost perfectly correlated (≈ 1.00) only because they are prices of the same stock "
                "on the same day, so that block tells us nothing new. The useful signal is elsewhere: the intraday range moves "
                f"with volume (<b>{N(f'{iv.iloc[4]:.2f}')}</b>) more than with the price level, and daily returns are almost "
                "independent of price. In the scatter, the points hug the diagonal: within a day the close stays near the open.",
                "الافتتاح والأعلى والأدنى والإغلاق مرتبطة تقريباً بشكل تام (≈ 1.00) فقط لأنها أسعار نفس السهم في نفس اليوم، فلا "
                "تضيف معلومة جديدة. الإشارة المفيدة في مكان آخر: المدى اليومي يرتبط بالحجم "
                f"(<b>{N(f'{iv.iloc[4]:.2f}')}</b>) أكثر من ارتباطه بمستوى السعر، والعائد اليومي شبه مستقل عن السعر. وفي الرسم "
                "النقطي تلتصق النقاط بالقطر: الإغلاق يبقى قريباً من الافتتاح خلال اليوم."))

            c1, c2 = st.columns(2, gap="medium")
            with c1, card():
                q = f.groupby("Sector")["Trade_Volume"].quantile([.25, .5, .75]).unstack().sort_values(.5)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=sum(([a, b, None] for a, b in zip(q[.25], q[.75])), []),
                                         y=sum(([s_, s_, None] for s_ in q.index), []), mode="lines",
                                         line=dict(color=alpha(GOLD, .55), width=9), hoverinfo="skip", showlegend=False))
                fig.add_trace(go.Scatter(x=q[.5], y=q.index, mode="markers", marker=dict(color=TEAL, size=11,
                                         line=dict(color=CARD, width=2)), showlegend=False,
                                         customdata=np.c_[q[.25], q[.75]],
                                         hovertemplate="%{y}<br>" + L("median", "الوسيط") + " %{x:,.0f}<br>"
                                                       "%{customdata[0]:,.0f} – %{customdata[1]:,.0f}<extra></extra>"))
                fig.update_xaxes(type="log", title=L("Shares traded per day", "الأسهم المتداولة يومياً"))
                if AR:
                    fig.update_xaxes(autorange="reversed")
                    fig.update_yaxes(side="right")
                chart(style(fig, 30 * len(q) + 120, L("Daily volume by group · dot = median, bar = middle 50% of days",
                                                      "الحجم اليومي حسب المجموعة · النقطة = الوسيط، الشريط = نصف الأيام الأوسط"),
                            legend=False))
            with c2, card():
                share = (f.groupby("Sector")["Traded_Value"].sum() / f["Traded_Value"].sum()).sort_values()
                chart(hbar(share.values, share.index, L("Share of all money traded by group", "حصة كل مجموعة من إجمالي قيمة التداول"),
                           lambda v: f"{v:.1%}", color=TEAL, h=30 * len(q) + 120))
            takeaway(L(
                f"Liquidity is concentrated: <b>{share.index[-1]}</b> alone accounts for <b>{N(f'{share.iloc[-1]:.0%}')}</b> of all "
                f"money traded and <b>{share.index[-2]}</b> for {N(f'{share.iloc[-2]:.0%}')}. Groups that trade many shares are not "
                "always the ones with the most money traded, because share prices differ a lot between groups.",
                f"السيولة مركّزة: <b>{share.index[-1]}</b> وحدها تستحوذ على <b>{N(f'{share.iloc[-1]:.0%}')}</b> من قيمة التداول، "
                f"و<b>{share.index[-2]}</b> على {N(f'{share.iloc[-2]:.0%}')}. المجموعات الأعلى في عدد الأسهم المتداولة ليست "
                "دائماً الأعلى في قيمة التداول، لأن أسعار الأسهم تختلف كثيراً بين المجموعات."))

        
        # Q1. Sectors
        
        elif page == 3:
            chapter(4, L(" Sector performance", "أداء القطاعات"),
                    L("How have the major Saudi sectors performed from 2022 to 2025?",
                      "كيف كان أداء القطاعات السعودية الرئيسية من ٢٠٢٢ إلى ٢٠٢٥؟"))
            sec = f.groupby(["Date", "Sector"])["Daily_Return"].mean().unstack().fillna(0)
            sec_idx = (1 + sec).cumprod() * 100
            total = (sec_idx.iloc[-1] / 100 - 1).sort_values()
            mret, mdd = mkt["Index"].iloc[-1] / 100 - 1, mkt["Drawdown"].min()
            c = st.columns(4)
            kpi(c[0], L("Average stock", "السهم المتوسط"), f"{mret:+.1%}", L("equal-weighted, whole period", "أوزان متساوية، كامل الفترة"),
                pct_cls(mret), sparkline(mkt["Index"], UP if mret >= 0 else DOWN))
            kpi(c[1], L("Deepest fall", "أعمق هبوط"), f"{mdd:.0%}", L("peak to trough", "من القمة إلى القاع"), "down",
                sparkline(mkt["Drawdown"], DOWN))
            kpi(c[2], L("Best group", "أفضل مجموعة"), f"{total.iloc[-1]:+.0%}", total.index[-1], "up")
            kpi(c[3], L("Worst group", "أضعف مجموعة"), f"{total.iloc[0]:+.0%}", total.index[0], "down")
            st.write("")

            with card():
                best3, worst3 = list(total.index[-3:][::-1]), list(total.index[:3])
                fig = go.Figure()
                for s_ in sec_idx.columns:
                    if s_ in best3 or s_ in worst3:
                        continue
                    fig.add_trace(go.Scatter(x=sec_idx.index, y=sec_idx[s_], name=s_, showlegend=False,
                                             line=dict(color=alpha(MUTED, .35), width=1),
                                             hovertemplate=f"{s_}<br>%{{x|%d %b %Y}} · %{{y:.0f}}<extra></extra>"))
                for grp, shades in ((best3, (UP, alpha(UP, .75), alpha(UP, .5))), (worst3, (DOWN, alpha(DOWN, .75), alpha(DOWN, .5)))):
                    for s_, col in zip(grp, shades):
                        fig.add_trace(go.Scatter(x=sec_idx.index, y=sec_idx[s_], name=f"{s_} ({total[s_]:+.0%})",
                                                 line=dict(color=col, width=2.4),
                                                 hovertemplate=f"<b>{s_}</b><br>%{{x|%d %b %Y}} · %{{y:.0f}}<extra></extra>"))
                fig.add_trace(go.Scatter(x=mkt["Date"], y=mkt["Index"], name=L(f"Whole market ({mret:+.0%})", f"السوق كامل ({mret:+.0%})"),
                                         line=dict(color=TEXT, width=2, dash="dash"),
                                         hovertemplate="%{x|%d %b %Y} · %{y:.0f}<extra></extra>"))
                fig.add_hline(y=100, line_dash="dot", line_color=MUTED)
                fig.update_yaxes(title=L("Index (100 = start)", "المؤشر (100 = البداية)"))
                chart(style(fig, 500, L("Equal-weighted group indices · 3 best in green, 3 worst in red, the rest in grey",
                                        "مؤشرات المجموعات بأوزان متساوية · أفضل ٣ بالأخضر، أضعف ٣ بالأحمر، والباقي رمادي")))

            c1, c2 = st.columns([1, 1.1], gap="medium")
            with c1, card():
                chart(hbar(total.values, total.index, L("Total return by group", "العائد الكلي لكل مجموعة"),
                           lambda v: f"{v:+.0%}", h=520))
            with c2, card():
                yr = sec.groupby(sec.index.year).apply(lambda d: (1 + d).prod() - 1).T * 100
                yr = yr.loc[total.index[::-1]]
                fig = px.imshow(yr, text_auto=".0f", aspect="auto", color_continuous_midpoint=0,
                                color_continuous_scale=[[0, DOWN], [.5, NEUTRAL], [1, UP]], labels=dict(x="", y="", color="%"))
                fig.update_xaxes(type="category", side="top")
                if AR:
                    fig.update_xaxes(autorange="reversed")
                    fig.update_yaxes(side="right")
                chart(style(fig, 520, L("Return by calendar year (%)", "العائد حسب السنة (%)"), legend=False))
            my = FX["mkt_year"]
            n_pos = int((total > 0).sum())
            takeaway(L(
                f"Over the period the average stock moved <b>{N(f'{mret:+.1%}')}</b>, with a deepest fall of {N(f'{mdd:.0%}')} on the "
                f"way, but the groups diverged widely: only <b>{n_pos} of {len(total)}</b> finished positive. "
                f"<b>{total.index[-1]}</b> led ({N(f'{total.iloc[-1]:+.0%}')}) and <b>{total.index[0]}</b> fell the most "
                f"({N(f'{total.iloc[0]:+.0%}')}). The market moved in waves: <b>{my.idxmax()}</b> was the strongest year "
                f"({N(f'{my.max():+.0%}')}) and <b>{my.idxmin()}</b> the weakest ({N(f'{my.min():+.0%}')}). Picking the right "
                "sector mattered far more than simply being in the market.",
                f"خلال الفترة تحرّك السهم المتوسط <b>{N(f'{mret:+.1%}')}</b> مع أعمق هبوط {N(f'{mdd:.0%}')}، لكن المجموعات تباعدت "
                f"كثيراً: <b>{N(n_pos)} من {N(len(total))}</b> فقط أنهت الفترة على ارتفاع. تصدّرت <b>{total.index[-1]}</b> "
                f"({N(f'{total.iloc[-1]:+.0%}')}) وتراجعت <b>{total.index[0]}</b> أكثر من غيرها ({N(f'{total.iloc[0]:+.0%}')}). "
                f"تحرك السوق على شكل موجات: <b>{N(my.idxmax())}</b> كانت أقوى سنة ({N(f'{my.max():+.0%}')}) و<b>{N(my.idxmin())}</b> "
                f"الأضعف ({N(f'{my.min():+.0%}')}). اختيار القطاع الصحيح كان أهم بكثير من مجرد الدخول في السوق."))

        
        #  Q2. Volume spikes
        
        elif page == 4:
            chapter(5, L(" Volume spikes", "قفزات الحجم"),
                    L("Do unusual trading-volume spikes come with price breakouts or bigger moves?",
                      "هل القفزات غير المعتادة في حجم التداول يصاحبها اختراق سعري أو حركة أكبر؟"))
            html(f'<div class="note" dir="{DIR}">' + L(
                f"<b>Volume spike</b> = a day when a stock trades at least <b>{spike_k:g}×</b> its average volume of the previous 20 "
                "sessions (change k in the filters). <b>Breakout</b> = the close is above the highest price of the previous 20 sessions.",
                f"<b>قفزة الحجم</b> = يوم يتداول فيه السهم <b>{spike_k:g}×</b> متوسط حجمه في آخر ٢٠ جلسة على الأقل (غيّر k من "
                "الفلاتر). <b>الاختراق</b> = الإغلاق فوق أعلى سعر في آخر ٢٠ جلسة.") + "</div>")

            ev = f[["Stock_Symbol", "Date", "Daily_Return", "Volume_Ratio", "Breakout_Up", "Breakout_Down"]].copy()
            ev["Spike"] = ev["Volume_Ratio"] >= spike_k
            gr = ev.groupby("Stock_Symbol", sort=False)["Daily_Return"]
            offsets = list(range(-5, 11))
            for o in offsets:
                ev[f"r{o}"] = gr.shift(-o)
            valid = ev.dropna(subset=["Volume_Ratio", "Daily_Return"])
            spikes = valid[valid["Spike"]]
            normal = valid[~valid["Spike"]]
            if len(spikes) < 5 or len(normal) < 5:
                st.info(L("Too few spike days for these filters — lower k or widen the period.",
                          "أيام القفزات قليلة جداً — خفّضي k أو وسّعي الفترة."))
                st.stop()

            p_up, p_up_n = spikes["Breakout_Up"].mean(), normal["Breakout_Up"].mean()
            mv_s, mv_n = spikes["Daily_Return"].abs().mean(), normal["Daily_Return"].abs().mean()
            c = st.columns(4)
            kpi(c[0], L("Spike days found", "أيام القفزات"), f"{len(spikes):,}",
                L(f"{len(spikes) / len(valid):.1%} of all stock-days", f"{len(spikes) / len(valid):.1%} من كل الأيام"), "gold")
            kpi(c[1], L("Avg move on spike days", "متوسط الحركة يوم القفزة"), f"{mv_s:.2%}",
                L(f"vs {mv_n:.2%} on normal days", f"مقابل {N(f'{mv_n:.2%}')} في الأيام العادية"))
            kpi(c[2], L("Breakout probability", "احتمال الاختراق"), f"{p_up:.0%}",
                L(f"normal days: {p_up_n:.0%}", f"الأيام العادية: {N(f'{p_up_n:.0%}')}"), "up")
            kpi(c[3], L("Link strength", "قوة العلاقة"), f"ρ = {FX['q2_rho']:.2f}",
                L("volume vs size of the move (Spearman)", "الحجم مقابل حجم الحركة (سبيرمان)"), "gold")
            st.write("")

            c1, c2 = st.columns([1.1, 1], gap="medium")
            with c1, card():
                b = FX["q2_buckets"]
                fig = go.Figure(go.Bar(x=list(b.index), y=b.values, marker_color=[GOLD if x_ in ("3–5×", ">5×") else TEAL for x_ in b.index],
                                       text=[f"{v:.2%}" for v in b.values], textposition="outside",
                                       hovertemplate="%{x}<br>%{y:.2%}<extra></extra>"))
                fig.update_xaxes(type="category", title=L("Volume ÷ previous 20-day average", "الحجم ÷ متوسط آخر ٢٠ يوماً"))
                fig.update_yaxes(tickformat=".1%", title=L("Average size of the move", "متوسط حجم الحركة"))
                if AR:
                    fig.update_xaxes(autorange="reversed")
                chart(style(fig, 420, L("The more unusual the volume, the bigger the move",
                                        "كلما كان الحجم غير معتاد أكثر، كانت الحركة أكبر"), legend=False))
            with c2, card():
                cats = [L("Breakout ↑", "اختراق ↑"), L("Breakdown ↓", "كسر ↓"), L("Big move > 3%", "حركة > 3%")]
                sp_v = [spikes["Breakout_Up"].mean(), spikes["Breakout_Down"].mean(), (spikes["Daily_Return"].abs() > .03).mean()]
                nm_v = [normal["Breakout_Up"].mean(), normal["Breakout_Down"].mean(), (normal["Daily_Return"].abs() > .03).mean()]
                fig = go.Figure([go.Bar(name=L("Spike days", "أيام القفزة"), x=cats, y=sp_v, marker_color=GOLD,
                                        text=[f"{v:.0%}" for v in sp_v], textposition="outside"),
                                 go.Bar(name=L("Normal days", "أيام عادية"), x=cats, y=nm_v, marker_color=T["bar_neutral"],
                                        text=[f"{v:.0%}" for v in nm_v], textposition="outside")])
                fig.update_yaxes(tickformat=".0%")
                fig.update_layout(barmode="group", bargap=.3)
                if AR:
                    fig.update_xaxes(autorange="reversed")
                chart(style(fig, 420, L("How often does each outcome happen?", "كم مرة تحدث كل نتيجة؟")))

            with card():
                fig = go.Figure()
                after = {}
                for key_, name, sub, col in (("up", L("Spike day closed up", "يوم القفزة أغلق مرتفعاً"), spikes[spikes["Daily_Return"] > 0], UP),
                                             ("down", L("Spike day closed down", "يوم القفزة أغلق منخفضاً"), spikes[spikes["Daily_Return"] < 0], DOWN)):
                    if len(sub) < 5:
                        continue
                    m = sub[[f"r{o}" for o in offsets]].mean().values
                    path_ = np.cumprod(1 + np.nan_to_num(m))
                    path_ = path_ / path_[offsets.index(-1)] - 1
                    after[key_] = (1 + path_[-1]) / (1 + path_[offsets.index(0)]) - 1
                    fig.add_trace(go.Scatter(x=offsets, y=path_, name=f"{name} · n={len(sub):,}", mode="lines+markers",
                                             line=dict(color=col, width=3), hovertemplate="%{x:+d}: %{y:+.2%}<extra></extra>"))
                fig.add_vrect(x0=-.5, x1=.5, fillcolor=GOLD, opacity=.14, line_width=0)
                fig.add_annotation(x=0, y=1.02, yref="paper", text=L("SPIKE DAY", "يوم القفزة"), showarrow=False, font=dict(color=GOLD))
                fig.add_hline(y=0, line_color=MUTED, line_dash="dot")
                fig.update_xaxes(title=L("Trading days from the spike", "أيام التداول قبل/بعد القفزة"), dtick=1)
                fig.update_yaxes(title=L("Cumulative return vs the day before", "العائد التراكمي مقارنة باليوم السابق"), tickformat=".1%")
                if AR:
                    fig.update_xaxes(autorange="reversed")
                chart(style(fig, 430, L("Average price path around a spike (day 0)", "متوسط مسار السعر حول القفزة (اليوم 0)")))

            a_up, a_dn = after.get("up", np.nan), after.get("down", np.nan)
            takeaway(L(
                f"<b>Yes, spikes come with bigger moves, but not with a direction.</b> On spike days the average stock moves "
                f"<b>{N(f'{mv_s:.2%}')}</b>, about {N(f'{mv_s / mv_n:.1f}×')} a normal day, and closes above its 20-day high "
                f"<b>{N(f'{p_up:.0%}')}</b> of the time (normal days: {N(f'{p_up_n:.0%}')}). The bar chart is a staircase: the more "
                f"unusual the volume, the larger the move. After the spike there is little follow-through (next 10 days: "
                f"{N(f'{a_up:+.1%}')} after up-spikes, {N(f'{a_dn:+.1%}')} after down-spikes), so the spike day carries most of the move.",
                f"<b>نعم، القفزات يصاحبها حركة أكبر، لكن بدون اتجاه محدد.</b> في يوم القفزة يتحرك السهم المتوسط "
                f"<b>{N(f'{mv_s:.2%}')}</b>، أي حوالي {N(f'{mv_s / mv_n:.1f}×')} اليوم العادي، ويغلق فوق أعلى سعر لـ ٢٠ يوماً في "
                f"<b>{N(f'{p_up:.0%}')}</b> من الحالات (الأيام العادية: {N(f'{p_up_n:.0%}')}). الأعمدة تشبه الدرج: كلما كان الحجم "
                f"غير معتاد أكثر كانت الحركة أكبر. وبعد القفزة لا تستمر الحركة كثيراً (الأيام العشرة التالية: {N(f'{a_up:+.1%}')} بعد "
                f"القفزات الصاعدة و{N(f'{a_dn:+.1%}')} بعد الهابطة)، فيوم القفزة نفسه يحمل معظم الحركة."))

            with card():
                options = sorted(f["Stock"].unique(), key=lambda s_: int(s_.split(" · ")[0]))
                stock = st.selectbox(L("Pick a stock to see its volume spikes", "اختاري سهماً لرؤية قفزات الحجم فيه"), options,
                                     index=next((i for i, s_ in enumerate(options) if s_.startswith("2222 ")), 0), key="q2_stock")
                s = f[f["Stock"] == stock].copy()
                if s.empty:
                    st.info(L("The spotlight stock has no data in this period.", "لا توجد بيانات للسهم المختار في هذه الفترة."))
                else:
                    s["Spike"] = s["Volume_Ratio"] >= spike_k
                    s["Next5"] = s["Close_Price"].shift(-5) / s["Close_Price"] - 1
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[.72, .28], vertical_spacing=.03)
                    fig.add_trace(go.Candlestick(x=s["Date"], open=s["Open_Price"], high=s["High_Price"],
                                                 low=s["Low_Price"], close=s["Close_Price"], name=L("Price", "السعر"),
                                                 increasing=dict(line=dict(color=UP), fillcolor=UP),
                                                 decreasing=dict(line=dict(color=DOWN), fillcolor=DOWN)), 1, 1)
                    sp = s[s["Spike"]]
                    fig.add_trace(go.Scatter(
                        x=sp["Date"], y=sp["High_Price"] * 1.03, mode="markers", name=L("Volume spike", "قفزة حجم"),
                        marker=dict(symbol="star", size=12, color=GOLD, line=dict(color=CARD, width=1)),
                        customdata=np.c_[sp["Volume_Ratio"], sp["Daily_Return"], sp["Next5"]],
                        hovertemplate="%{x|%d %b %Y}<br>" + L("Volume", "الحجم") + " %{customdata[0]:.1f}×<br>"
                                      + L("Day", "اليوم") + " %{customdata[1]:+.2%}<br>"
                                      + L("Next 5 days", "الخمسة أيام التالية") + " %{customdata[2]:+.2%}<extra></extra>"), 1, 1)
                    vcol = np.where(s["Spike"], GOLD, np.where(s["Close_Price"] >= s["Open_Price"], T["up_soft"], T["down_soft"]))
                    fig.add_trace(go.Bar(x=s["Date"], y=s["Trade_Volume"], marker_color=vcol, name=L("Volume", "الحجم"),
                                         showlegend=False), 2, 1)
                    fig.update_layout(xaxis_rangeslider_visible=False)
                    chart(style(fig, 540, L(f"Example · {stock} — stars mark volume spikes (hover to see what happened next)",
                                            f"مثال · {stock} — النجوم تعني قفزات الحجم (مرّري المؤشر لمعرفة ما حدث بعدها)")))

        
        # Q3. Correlation
        
        elif page == 5:
            chapter(6, L("Blue-chip correlation", "ارتباط الأسهم القيادية"),
                    L("How strongly do the largest stocks move together?", "إلى أي درجة تتحرك الأسهم الكبرى معاً؟"))
            blue_default = stats.nlargest(10, "Value")["Stock"].tolist()
            pick = st.multiselect(L("Blue chips (default = the 10 most traded by value)",
                                    "الأسهم القيادية (افتراضياً أعلى ١٠ أسهم في قيمة التداول)"),
                                  sorted(stats["Stock"]), default=blue_default, key="q3_pick")
            if len(pick) < 3:
                st.info(L("Pick at least three stocks.", "اختاري ثلاثة أسهم على الأقل."))
                st.stop()
            sub = f[f["Stock"].isin(pick)]
            pv = sub.pivot_table(index="Date", columns="Stock", values="Daily_Return")
            order = stats.set_index("Stock").loc[pv.columns].sort_values(["Stock_Sector", "Value"], ascending=[True, False]).index
            pv = pv[order]
            corr = pv.corr(min_periods=30)
            pcorr = sub.pivot_table(index="Date", columns="Stock", values="Close_Price")[order].corr(min_periods=30)
            upper = np.triu(np.ones(corr.shape, bool), 1)
            pairs = corr.where(upper).stack().dropna().sort_values(ascending=False)
            ppairs = pcorr.where(upper).stack().dropna()
            n = len(order)

            c1, c2 = st.columns([1.35, 1], gap="medium")
            with c1, card():
                labels = [short(s_) for s_ in order]
                z = corr.values.copy()
                z[np.triu_indices(n)] = np.nan
                fig = go.Figure(go.Heatmap(z=z, x=labels, y=labels, zmin=-1, zmax=1, xgap=2, ygap=2,
                                           colorscale=[[0, DOWN], [.5, NEUTRAL], [1, TEAL]],
                                           text=np.where(np.isnan(z), "", np.round(np.nan_to_num(z), 2).astype(str)),
                                           texttemplate="%{text}", hovertemplate="%{y} & %{x}<br>ρ = %{z:.2f}<extra></extra>"))
                fig.update_xaxes(tickangle=45, showgrid=False)
                fig.update_yaxes(autorange="reversed", showgrid=False)
                if AR:
                    fig.update_xaxes(autorange="reversed")
                    fig.update_yaxes(side="right")
                chart(style(fig, 520, L("Correlation of daily returns (grouped by sector)",
                                        "ارتباط العوائد اليومية (مرتبة حسب القطاع)"), legend=False))
            with c2, card():
                top5, low5 = pairs.head(5), pairs.tail(5)[::-1]
                rows = "".join(f'<div class="wi-row"><span>{short(a)} & {short(b)}</span><b class="up">{v:.2f}</b></div>'
                               for (a, b), v in top5.items())
                rows2 = "".join(f'<div class="wi-row"><span>{short(a)} & {short(b)}</span><b>{v:.2f}</b></div>'
                                for (a, b), v in low5.items())
                html(f'<div class="lk" dir="{DIR}"><div class="br-h">{L("Move together most", "الأكثر تحركاً معاً")}</div>{rows}'
                     f'<div class="br-h" style="margin-top:16px">{L("Most independent (best for diversifying)", "الأكثر استقلالاً (الأفضل للتنويع)")}</div>{rows2}</div>')

            with card():
                roll = pv.rolling(60, min_periods=40).corr()
                mask = np.triu(np.ones((n, n), bool), 1)
                avg_roll = roll.groupby(level=0).apply(
                    lambda m: np.nanmean(m.values[mask]) if m.shape == (n, n) else np.nan).dropna()
                fig = go.Figure(go.Scatter(x=avg_roll.index, y=avg_roll.values, line=dict(color=GOLD, width=2),
                                           fill="tozeroy", fillcolor=alpha(GOLD, .13),
                                           hovertemplate="%{x|%d %b %Y}<br>ρ̄ %{y:.2f}<extra></extra>"))
                if len(avg_roll):
                    fig.add_hline(y=float(avg_roll.mean()), line_dash="dot", line_color=MUTED,
                                  annotation_text=L("average", "المتوسط"), annotation_font_color=MUTED)
                chart(style(fig, 320, L("How much they move together over time (60-day average correlation)",
                                        "مدى تحركها معاً عبر الزمن (متوسط الارتباط لـ ٦٠ يوماً)"), legend=False))

            s = st.columns(3)
            story(s[0], L("Average correlation of returns", "متوسط ارتباط العوائد"), f"ρ = {pairs.mean():.2f}",
                  L("moderate and positive", "متوسط وموجب"), "up")
            story(s[1], L("Average correlation of prices", "متوسط ارتباط الأسعار"), f"ρ = {ppairs.mean():.2f}",
                  L("misleading: why returns are used", "مضلل: ولهذا نستخدم العوائد"), "gold")
            story(s[2], L("Peak of moving together", "ذروة التحرك معاً"), f"ρ = {avg_roll.max():.2f}" if len(avg_roll) else "–",
                  N(fdate(avg_roll.idxmax(), "%b %Y")) if len(avg_roll) else "", "down")
            st.write("")
            (a1, b1), (a2, b2) = pairs.index[0], pairs.index[-1]
            takeaway(L(
                f"The blue chips are <b>moderately and positively</b> correlated (average <b>{N(f'{pairs.mean():.2f}')}</b>): they "
                f"usually move in the same direction but far from in lock-step. The strongest link is <b>{short(a1)} & {short(b1)}</b> "
                f"({N(f'{pairs.iloc[0]:.2f}')}), typically stocks from the same group, and the most independent pair is "
                f"<b>{short(a2)} & {short(b2)}</b> ({N(f'{pairs.iloc[-1]:.2f}')}). Correlation rises in stressful periods, exactly "
                "when diversification is needed most. Correlation is measured on daily returns: prices of trending stocks look "
                "related by accident, which is why the price correlation above is so different.",
                f"الأسهم القيادية مرتبطة <b>بدرجة متوسطة وموجبة</b> (المتوسط <b>{N(f'{pairs.mean():.2f}')}</b>): غالباً تتحرك في نفس "
                f"الاتجاه لكن ليس بشكل متطابق. أقوى ارتباط بين <b>{short(a1)} و{short(b1)}</b> ({N(f'{pairs.iloc[0]:.2f}')})، وغالباً "
                f"تكون من نفس المجموعة، والأكثر استقلالاً <b>{short(a2)} و{short(b2)}</b> ({N(f'{pairs.iloc[-1]:.2f}')}). يرتفع "
                "الارتباط في فترات الضغط، أي عندما نحتاج التنويع أكثر. الارتباط محسوب على العوائد اليومية لأن أسعار الأسهم ذات "
                "الاتجاه تبدو مرتبطة بالصدفة، ولهذا يختلف ارتباط الأسعار أعلاه كثيراً."))

        
        # Q4. Volatility
        
        elif page == 6:
            chapter(7, L("Volatility relative to price", "التذبذب نسبةً إلى السعر"),
                    L("Which stocks show the highest price volatility relative to their average price?",
                      "أي الأسهم الأعلى تذبذباً في السعر نسبةً إلى متوسط سعرها؟"))
            html(f'<div class="note" dir="{DIR}">' + L(
                "<b>Coefficient of variation (CV)</b> = standard deviation of the price ÷ average price: how widely the price "
                "wandered over the period (trends count too). <b>Annualised volatility</b> = standard deviation of daily returns × √250: "
                "how much the price shakes from day to day. Stocks with at least 60 trading days.",
                "<b>معامل الاختلاف (CV)</b> = الانحراف المعياري للسعر ÷ متوسط السعر: مدى تنقّل السعر خلال الفترة (يشمل الاتجاه). "
                "<b>التذبذب السنوي</b> = الانحراف المعياري للعوائد اليومية × √250: مدى اهتزاز السعر يوماً بيوم. الأسهم التي لها "
                "٦٠ يوم تداول على الأقل.") + "</div>")
            v = stats[stats["Days"] >= 60].dropna(subset=["CV", "Ann_Vol"]).copy()
            v["Label"] = v["Stock"].map(short)
            cn, _ = st.columns([1, 2.5])
            top_n = cn.slider(L("How many stocks in each list", "عدد الأسهم في كل قائمة"), 5, 25, 10, key="q4_n")
            c1, c2 = st.columns(2, gap="medium")
            with c1, card():
                top = v.nlargest(top_n, "CV").iloc[::-1]
                chart(hbar(top["CV"].values, top["Label"], L(f"Top {top_n} by coefficient of variation", f"أعلى {top_n} في معامل الاختلاف"),
                           lambda x_: f"{x_:.0%}", color=GOLD))
            with c2, card():
                top = v.nlargest(top_n, "Ann_Vol").iloc[::-1]
                chart(hbar(top["Ann_Vol"].values, top["Label"], L(f"Top {top_n} by annualised volatility", f"أعلى {top_n} في التذبذب السنوي"),
                           lambda x_: f"{x_:.0%}", color=DOWN))

            c1, c2 = st.columns([1.3, 1], gap="medium")
            with c1, card():
                fig = go.Figure(go.Scatter(x=v["Mean_Close"], y=v["Ann_Vol"], mode="markers", text=v["Label"],
                                           customdata=v["Sector"],
                                           marker=dict(size=9, color=[SECTOR_COLOR[s_] for s_ in v["Stock_Sector"]], opacity=.85,
                                                       line=dict(color=CARD, width=1)),
                                           hovertemplate="<b>%{text}</b><br>%{customdata}<br>SAR %{x:,.1f} · %{y:.0%}<extra></extra>"))
                fig.update_xaxes(type="log", title=L("Average price (SAR)", "متوسط السعر (ريال)"))
                fig.update_yaxes(tickformat=".0%", title=L("Annualised volatility", "التذبذب السنوي"))
                chart(style(fig, 440, L("Volatility vs average price (each dot is a stock)", "التذبذب مقابل متوسط السعر (كل نقطة سهم)"),
                            legend=False))
            with c2, card():
                gv = v.groupby("Sector")["Ann_Vol"].median().sort_values()
                chart(hbar(gv.values, gv.index, L("Typical volatility by group (median)", "التذبذب المعتاد لكل مجموعة (الوسيط)"),
                           lambda x_: f"{x_:.0%}", color=TEAL, h=440))
            hi_cv, hi_av, lo_av = v.nlargest(1, "CV").iloc[0], v.nlargest(1, "Ann_Vol").iloc[0], v.nsmallest(1, "Ann_Vol").iloc[0]
            overlap = len(set(v.nlargest(top_n, "CV")["Stock"]) & set(v.nlargest(top_n, "Ann_Vol")["Stock"]))
            rho = v["Mean_Close"].rank().corr(v["Ann_Vol"].rank())
            rel_en = ("cheaper stocks tend to be more volatile" if rho < -.2 else "pricier stocks tend to be more volatile"
                      if rho > .2 else "the price level says almost nothing about volatility")
            rel_ar = ("الأسهم الأرخص تميل لتذبذب أعلى" if rho < -.2 else "الأسهم الأغلى تميل لتذبذب أعلى"
                      if rho > .2 else "مستوى السعر لا يدل تقريباً على التذبذب")
            takeaway(L(
                f"Relative to its price, <b>{hi_cv['Label']}</b> wandered the most (CV {N(f'{hi_cv.CV:.0%}')}), while "
                f"<b>{hi_av['Label']}</b> was the jumpiest day to day ({N(f'{hi_av.Ann_Vol:.0%}')} a year vs a median of "
                f"{N(f'{v.Ann_Vol.median():.0%}')}). The calmest stock is <b>{lo_av['Label']}</b> ({N(f'{lo_av.Ann_Vol:.0%}')}). "
                f"The two top-{top_n} lists share only {overlap} of {top_n} names: a high CV often means a strong trend, high volatility means "
                f"daily noise. Comparing price and volatility, {rel_en} (ρ = {N(f'{rho:.2f}')}). <b>{gv.index[0]}</b> is the calmest "
                f"group and <b>{gv.index[-1]}</b> the most volatile.",
                f"نسبةً إلى سعره، <b>{hi_cv['Label']}</b> هو الأكثر تنقلاً (معامل الاختلاف {N(f'{hi_cv.CV:.0%}')})، بينما "
                f"<b>{hi_av['Label']}</b> الأكثر اهتزازاً يومياً ({N(f'{hi_av.Ann_Vol:.0%}')} سنوياً مقابل وسيط "
                f"{N(f'{v.Ann_Vol.median():.0%}')}). والأهدأ <b>{lo_av['Label']}</b> ({N(f'{lo_av.Ann_Vol:.0%}')}). القائمتان تشتركان "
                f"في {N(overlap)} أسهم فقط: معامل الاختلاف المرتفع يعني غالباً اتجاهاً قوياً، والتذبذب المرتفع يعني اهتزازاً يومياً. "
                f"وبمقارنة السعر بالتذبذب: {rel_ar} (ρ = {N(f'{rho:.2f}')}). <b>{gv.index[0]}</b> أهدأ مجموعة و<b>{gv.index[-1]}</b> "
                "الأكثر تذبذباً."))

        
        #  Conclusions
        
        elif page == 7:
            chapter(8, L("Conclusions", "الخلاصة"),
                    L("The four questions.", "الأسئلة الأربعة."))
            F = FX
            tot = F["sec_total"]
            m_s, b_s, w_s = f"{F['market']:+.1%}", f"{tot.iloc[-1]:+.0%}", f"{tot.iloc[0]:+.0%}"
            yb, yw = F["mkt_year"].idxmax(), F["mkt_year"].idxmin()
            mult, bus, bun = f"{F['mv_s'] / F['mv_n']:.1f}×", f"{F['bu_s']:.0%}", f"{F['bu_n']:.0%}"
            q3a, (t1, t2) = f"{F['q3_avg']:.2f}", (short(F["q3_top"][0]), short(F["q3_top"][1]))
            bg, wg = sector_name(tot.index[-1]), sector_name(tot.index[0])
            cv_, av_, lo_ = short(F["q4_cv"]), short(F["q4_av"]), short(F["q4_low"])
            answers = [
                (L(" Sector performance", " أداء القطاعات"),
                 L(f"The average stock moved <b>{m_s}</b>, but groups diverged: <b>{bg}</b> {b_s}, <b>{wg}</b> {w_s}. "
                   f"Strongest year {yb}, weakest {yw}.",
                   f"تحرّك السهم المتوسط <b>{N(m_s)}</b>، لكن المجموعات تباعدت: <b>{bg}</b> {N(b_s)}، و<b>{wg}</b> {N(w_s)}. "
                   f"أقوى سنة {N(yb)} وأضعفها {N(yw)}.")),
                (L("Volume spikes", " قفزات الحجم"),
                 L(f"Spike days move about <b>{mult}</b> more than normal days and break out above the 20-day high {bus} of the "
                   f"time (vs {bun}). Spikes signal volatility, not direction.",
                   f"أيام القفزات تتحرك حوالي <b>{N(mult)}</b> أكثر من الأيام العادية، وتخترق أعلى سعر لـ ٢٠ يوماً في {N(bus)} "
                   f"من الحالات (مقابل {N(bun)}). القفزة تعني تذبذباً وليس اتجاهاً.")),
                (L("Blue-chip correlation", " ارتباط الأسهم القيادية"),
                 L(f"Moderate and positive: average <b>{q3a}</b>. Strongest within the same group ({t1} & {t2}); it rises in "
                   "stressful periods.",
                   f"متوسط وموجب: المتوسط <b>{N(q3a)}</b>. أقواه داخل نفس المجموعة ({t1} و{t2})، ويرتفع في فترات الضغط.")),
                (L("Volatility vs price", " التذبذب نسبةً للسعر"),
                 L(f"Highest CV: <b>{cv_}</b>; jumpiest day to day: <b>{av_}</b>; calmest: <b>{lo_}</b>.",
                   f"أعلى معامل اختلاف: <b>{cv_}</b>، والأكثر اهتزازاً يومياً: <b>{av_}</b>، والأهدأ: <b>{lo_}</b>.")),
            ]
            for row in (answers[:2], answers[2:]):
                cols = st.columns(2, gap="medium")
                for col, (t_, a_) in zip(cols, row):
                    with col, card():
                        html(f'<div class="br-h" dir="{DIR}">{t_}</div><div class="concl" dir="{DIR}">{a_}</div>')
            c1, c2 = st.columns(2, gap="medium")

        
        # What-If Simulator
        
        elif page == 8:
            chapter(6, L("What-If Simulator", "محاكي الاستثمار"),
                    L("If I had invested on a given day, where would I be now?",
                      "لو استثمرت في تاريخ معين… كم ستصبح قيمة استثماري؟"))
            c1, c2, c3 = st.columns([2.2, 1, 1])
            default_pf = [s_ for s_ in dict.fromkeys(stats.nlargest(3, "Value")["Stock"].tolist())
                          if s_ in set(stats["Stock"])][:3]
            pf = c1.multiselect(L("Portfolio (equal split, buy & hold)", "المحفظة (توزيع متساوٍ، شراء واحتفاظ)"),
                                sorted(stats["Stock"]), default=default_pf)
            amount = c2.number_input(L("Amount (SAR)", "المبلغ (ريال)"), 1000, 10_000_000, 10_000, step=1000)
            buy = c3.date_input(L("Buy date", "تاريخ الشراء"), value=start.date(), min_value=start.date(), max_value=end.date())
            if not pf:
                st.info(L("Add at least one stock.", "أضيفي سهماً واحداً على الأقل."))
                st.stop()

            p = f[f["Stock"].isin(pf) & (f["Date"] > pd.Timestamp(buy))]
            if p.empty:
                st.info(L("No trading after that date — pick an earlier buy date.", "لا يوجد تداول بعد هذا التاريخ — اختاري تاريخاً اخر."))
                st.stop()
            r = p.pivot_table(index="Date", columns="Stock", values="Daily_Return").fillna(0)
            hold = (1 + r).cumprod() * (amount / len(pf))
            total = hold.sum(axis=1)
            bench = mkt[mkt["Date"] > pd.Timestamp(buy)].set_index("Date")["Ret"]
            bench = (1 + bench).cumprod() * amount
            fv, gain = total.iloc[-1], total.iloc[-1] / amount - 1
            bgain = bench.iloc[-1] / amount - 1
            dd = (total / total.cummax() - 1).min()

            k = st.columns(4)
            kpi(k[0], L("Portfolio today", "قيمة المحفظة الآن"), f"SAR {fv:,.0f}",
                L(f"from SAR {amount:,.0f} on {fdate(buy)}", f"من {N(f'{amount:,.0f}')} ريال في {N(fdate(buy))}"),
                pct_cls(gain), sparkline(total.values, UP if gain >= 0 else DOWN))
            kpi(k[1], L("Profit / loss", "الربح / الخسارة"), f"{gain:+.1%}", N(f"SAR {fv - amount:+,.0f}"), pct_cls(gain))
            kpi(k[2], L("vs. the market", "مقارنة بالسوق"), f"{(gain - bgain) * 100:+.1f} pts",
                L(f"market did {bgain:+.1%}", f"السوق حقق {N(f'{bgain:+.1%}')}"), pct_cls(gain - bgain))
            kpi(k[3], L("Worst dip on the way", "أسوأ هبوط في الطريق"), f"{dd:.1%}",
                L("max drawdown you'd have lived through", "أقصى تراجع كنتِ ستمرين به"), "down")
            st.write("")

            with card():
                fig = go.Figure()
                for i, s_ in enumerate(hold.columns):
                    fig.add_trace(go.Scatter(x=hold.index, y=hold[s_], name=short(s_), stackgroup="pf",
                                             line=dict(width=.5, color=PALETTE[i % len(PALETTE)]),
                                             hovertemplate="%{x|%d %b %Y}<br>SAR %{y:,.0f}<extra>" + short(s_) + "</extra>"))
                fig.add_trace(go.Scatter(x=bench.index, y=bench.values, name=L("Same money in the market", "نفس المبلغ في السوق"),
                                         line=dict(color=TEXT, width=2, dash="dot"),
                                         hovertemplate="%{x|%d %b %Y}<br>SAR %{y:,.0f}<extra></extra>"))
                fig.add_hline(y=amount, line_color=MUTED, line_dash="dash", annotation_text=L("invested", "المستثمر"),
                              annotation_font_color=MUTED)
                fig.update_yaxes(tickprefix="SAR ", tickformat=",.0f")
                chart(style(fig, 470, L("Growth of your money — stacked by holding", "نمو أموالك — مقسّمة حسب السهم")))

            contrib = (hold.iloc[-1] - amount / len(pf)).sort_values()
            with card():
                fig = go.Figure(go.Waterfall(
                    x=[short(s_) for s_ in contrib.index] + [L("Total", "الإجمالي")], y=list(contrib.values) + [0],
                    measure=["relative"] * len(contrib) + ["total"],
                    increasing=dict(marker=dict(color=UP)), decreasing=dict(marker=dict(color=DOWN)),
                    totals=dict(marker=dict(color=GOLD)), connector=dict(line=dict(color=LINE)),
                    text=[f"SAR {v:+,.0f}" for v in contrib.values] + [f"SAR {contrib.sum():+,.0f}"],
                    textposition="outside"))
                _cum = np.r_[0, np.cumsum(contrib.values)]
                _lo, _hi = min(_cum.min(), 0), max(_cum.max(), 0)
                _pad = (_hi - _lo) * .18 or 1
                fig.update_yaxes(range=[_lo - (_pad if _lo < 0 else 0), _hi + (_pad if _hi > 0 else 0)],
                                 tickprefix="SAR ", tickformat=",.0f")
                chart(style(fig, 360, L("Who made (or lost) the money?", "الربح (أو الخسارة)؟"), legend=False))
            st.caption(L("Uses adjusted, cleaned daily returns (dividends reinvested). Educational only — not investment advice.",
                         "يعتمد على العوائد اليومية المعدّلة والمنظفة (مع إعادة استثمار التوزيعات)."))


# Developer Corner 
elif SERVICE == 2:
    here = Path(__file__).parent

    def find_file(patterns):
        for folder in (here, here / "data", here / "notebooks"):
            for pat in patterns:
                hits = sorted(folder.glob(pat))
                if hits:
                    return hits[0]
        return None

    html(f"""
    <div class="hero">
      <div>
        <div class="kicker">{L("Project files", "ملفات المشروع")}</div>
        <h1>{L("Developer <span>Corner</span>", "زاوية <span>المبرمج</span>")}</h1>
        <div class="sub">{L("Download the data and the notebook behind this website.",
                            "حمّل البيانات وملف الكود الذي بُني عليه هذا الموقع.")}</div>
      </div>
    </div>
    """)

    # project files 
    raw_file = find_file(["ALL_SAUDI_STOCKS*.csv", "*raw*.csv"])
    nb_file = find_file(["*.ipynb"])
    comp_file = find_file(["tadawul_companies.csv"])
    r = st.columns(4, gap="medium")
    with r[0], card():
        html(f'<div class="res" dir="{DIR}"><div class="res-k">01</div><div class="res-t">{L("Original dataset", "البيانات الأصلية")}</div>'
             f'<div class="res-d">{L("Raw daily prices from Kaggle, 2022 – 2025.", "الأسعار اليومية  من Kaggle للفترة ٢٠٢٢ – ٢٠٢٥.")}</div></div>')
        st.link_button(L("Open on Kaggle", "فتح في Kaggle"),
                       "https://www.kaggle.com/datasets/abdelrahmanalimo/saudi-arabian-stock-market-data", **_W)
        if raw_file:
            st.download_button(L("Download raw CSV", "تحميل الملف الخام"), raw_file.read_bytes(), raw_file.name,
                               "text/csv", key="dl_raw", **_W)
    with r[1], card():
        html(f'<div class="res" dir="{DIR}"><div class="res-k">02</div><div class="res-t">{L("Cleaned dataset", "البيانات النظيفة")}</div>'
             f'<div class="res-d">{L(f"Output of the notebook used by this app.", f"ناتج النوت بوك الذي يعتمد عليه التطبيق .")}</div></div>')
        st.download_button(L("Download cleaned CSV", "تحميل الملف النظيف"), Path(path).read_bytes(), DATA_FILE,
                           "text/csv", key="dl_clean", **_W)
    with r[2], card():
        html(f'<div class="res" dir="{DIR}"><div class="res-k">03</div><div class="res-t">{L("Jupyter notebook", "ملف جوبتر")}</div>'
             f'<div class="res-d">{L("The full EDA.", "التحليل الاستكشافي كاملاً.")}</div></div>')
        if nb_file:
            st.download_button(L("Download notebook", "تحميل النوت بوك"), nb_file.read_bytes(), nb_file.name,
                               "application/x-ipynb+json", key="dl_nb", **_W)
        else:
            st.caption(L("Place the .ipynb file next to app.py (or in data/) to enable the download.",
                         "ضعي ملف ‎.ipynb بجانب app.py (أو داخل مجلد data) لتفعيل التحميل."))
    with r[3], card():
        html(f'<div class="res" dir="{DIR}"><div class="res-k">04</div><div class="res-t">{L("Company list", "قائمة الشركات")}</div>'
             f'<div class="res-d">{L(f"Company names and industry groups by symbol.", f"أسماء الشركات وقطاعاتها حسب الرمز.")}</div></div>')
        comp_csv = (comp_file.read_bytes() if comp_file else
                    COMPANIES.rename(columns={"Stock_Symbol": "Symbol", "Stock_Sector": "Industry_Group"}).to_csv(index=False).encode())
        st.download_button(L("Download company list", "تحميل قائمة الشركات"), comp_csv, "tadawul_companies.csv",
                           "text/csv", key="dl_comp", **_W)



#  Settings & accessibility

else:
    html(f"""
    <div class="hero">
      <div>
        <div class="kicker">{L("Personalise", "خصّص تجربتك")}</div>
        <h1>{L("Settings & <span>accessibility</span>", "الإعدادات و<span>سهولة الوصول</span>")}</h1>
        <div class="sub">{L("Choose your language, look and reading comfort. Changes apply instantly to every page.",
                            "اختر اللغة والمظهر وراحة القراءة، والتغييرات تُطبّق فوراً على كل الصفحات.")}</div>
      </div>
    </div>
    """)

    def section(title, text):
        html(f'<div dir="{DIR}" style="margin-bottom:8px"><div style="font-weight:700;font-size:1.08rem;color:{TEXT}">'
             f'{title}</div><div style="color:{MUTED};font-size:.86rem">{text}</div></div>')

    def mini_preview():
        bars = [(1.2, 1), (-0.8, 0), (0.5, 1), (-1.6, 0), (0.9, 1), (0.3, 1)]
        bar_html = "".join(
            f'<div class="mp-b"><div class="mp-h top">{f"<i class=mp-up style=height:{abs(v) / 1.6 * 100:.0f}%></i>" if up else ""}</div>'
            f'<div class="mp-h bot">{"" if up else f"<i class=mp-dn style=height:{abs(v) / 1.6 * 100:.0f}%></i>"}</div></div>'
            for v, up in bars)
        return f"""
        <div class="mp" dir="{DIR}">
          <div class="mp-top"><span class="mp-pill on">{L("Market Today", "السوق اليوم")}</span>
            <span class="mp-pill">{L("Historical", "التاريخي")}</span></div>
          <div class="mp-kpis">
            <div class="mp-k"><span>TASI</span><b class="up">11,284</b><i class="up">▲ +0.77%</i></div>
            <div class="mp-k"><span>{L("Loser", "هابط")}</span><b class="down">-2.35%</b><i class="down">▼</i></div>
            <div class="mp-k"><span>{L("Breadth", "الاتساع")}</span><b><span class="up">98▲</span> <span class="down">64▼</span></b></div>
          </div>
          <div class="mp-chart">{bar_html}</div>
          <div class="mp-btn">{L("Button", "زر")}</div>
        </div>"""

    with card():
        d1, d2 = st.columns([1.25, 1], gap="large")
        with d1:
            section(L("Language & appearance", "اللغة والمظهر"),
                    L("Changes apply instantly to every page.", "التغييرات تُطبّق فوراً على كل الصفحات."))
            st.radio(L("Interface language", "لغة الواجهة"), CHOICES["lang"], index=CHOICES["lang"].index(P["lang"]),
                     format_func=lambda v: {"en": "English", "ar": "العربية"}[v], horizontal=True,
                     key="_w_lang", on_change=save_pref, args=("lang",))
            st.radio(L("Theme", "السمة"), CHOICES["theme"], index=CHOICES["theme"].index(P["theme"]),
                     format_func=lambda v: {"light": L("Light", "فاتح"), "dark": L("Dark", "ليلي"),
                                            "contrast": L("High contrast", "تباين عالٍ")}[v],
                     horizontal=True, key="_w_theme", on_change=save_pref, args=("theme",))
            st.select_slider(L("Text size", "حجم الخط"), CHOICES["size"], value=P["size"], format_func=lambda v: f"{v}%",
                             key="_w_size", on_change=save_pref, args=("size",))
        with d2:
            html(f'<div class="panel-s" dir="{DIR}">{L("Preview", "معاينة")}</div>' + mini_preview())

    with card():
        e1, e2 = st.columns([1, 1.1], gap="large")
        with e1:
            section(L("Accessibility", "سهولة الوصول"),
                    L("Options for colour-vision deficiency, dyslexia and low vision.",
                      "خيارات لعمى الألوان وعسر القراءة وضعف البصر."))
            for key, label, help_ in (
                ("cvd", L("Colour-blind friendly colours", "ألوان مناسبة لعمى الألوان"),
                 L("Blue = up and orange = down instead of green / red.", "أزرق للصعود وبرتقالي للهبوط بدل الأخضر والأحمر.")),
                ("spacing", L("Extra text spacing", "مسافات أوسع بين السطور"),
                 L("More space between lines and words — easier for dyslexic readers.",
                   "مسافة أكبر بين السطور والكلمات — أسهل لمن لديهم عسر قراءة.")),
            ):
                st.toggle(label, value=P[key], key=f"_w_{key}", on_change=save_pref, args=(key,))
                st.caption(help_)
            st.button(L("Reset to defaults", "استعادة الإعدادات الافتراضية"), on_click=reset_prefs, key="reset_prefs")
        with e2:
            section(L("Always on", "مفعّل دائماً"), L("Built into every page.", "موجود في كل الصفحات."))
            st.markdown(L(
                "- **Not colour alone**: every gain or loss also has ▲ / ▼ and a + / − sign.\n"
                "- **Right-to-left** layout and Arabic font for Arabic readers.",
                "- **لا نعتمد على اللون وحده**: كل ربح أو خسارة معه ▲ / ▼ وإشارة + / −.\n"
                "- **اتجاه من اليمين لليسار** وخط عربي واضح."))
    st.caption(L("Your choices are saved in the page link — bookmark it to keep them next time.",
                 "إعداداتك محفوظة في رابط الصفحة — احفظي الرابط في المفضلة لتبقى في المرة القادمة."))


html(f"""
<div class="tp-foot" dir="{DIR}">
  <div class="foot-grid">
    <div>
      <div class="brand">{LOGO_SVG}<div><div class="t" style="font-size:1rem">{L("Nabd Tadawul", "نبض تداول")}</div>
      <div class="s">{L("Saudi market insights", "رؤى السوق السعودي")}</div></div></div>
      <p style="margin:10px 0 0 0">{L("An exploratory data analysis of the Saudi Stock Exchange (2022 – 2025), with today's market, an investment simulator.",
                                     "تحليل استكشافي لبيانات السوق المالية السعودية (٢٠٢٢ – ٢٠٢٥)، مع حالة السوق اليوم ومحاكي استثمار.")}</p>
    </div>
    <div><h4>{L("Services", "الخدمات")}</h4><ul>{"".join(f'<li><a href="{svc_href(i)}" target="_self">{x}</a></li>' for i, x in enumerate(SERVICES))}</ul></div>
    <div><h4>{L("Data & tools", "البيانات والأدوات")}</h4><ul>
      <li><a href="https://www.kaggle.com/datasets/abdelrahmanalimo/saudi-arabian-stock-market-data" target="_blank">{L("Kaggle dataset ", "بيانات Kaggle ")}</a></li>
      <li>{L("Yahoo Finance (live, delayed ≈15 min)", "Yahoo Finance (مباشرة، متأخرة ≈١٥ دقيقة)")}</li>
      </ul></div>
  </div>
  <div class="foot-bottom">
    <span>{L("© 2026 Tarfah Alsunaidi. All rights reserved.", "© 2026 طرفه السنيدي. جميع الحقوق محفوظة.")}</span>
    <span>{L("Riyadh, Kingdom of Saudi Arabia", "الرياض، المملكة العربية السعودية")}</span></div>
</div>
""")