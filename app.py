import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit_echarts import st_echarts
import base64

# ================== CONFIG ==================
st.set_page_config(page_title="Aging - Filtros", layout="wide")

# ================== LOGIN (pantalla previa, SOLO recuadro) ==================
def get_users_from_secrets():
    try:
        return dict(st.secrets.get("users", {}))  # [users] user="pass" en .streamlit/secrets.toml
    except Exception:
        return {}

USERS = get_users_from_secrets() or {"admin": "changeme"}  # fallback para dev

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "whoami" not in st.session_state:
    st.session_state["whoami"] = ""

def render_login():
    # CSS: oculta TODO (header/toolbar/menú), quita padding y centra el recuadro
    st.markdown("""
        <style>
            header, footer, #MainMenu, div[role="banner"], div[data-testid="stToolbar"] {
                display: none !important;
            }
            .block-container {
                padding: 0 !important;
                margin: 0 !important;
            }
            body, .block-container { background: #f0f2f6; }
            .login-wrap{
                display:flex; flex-direction:column; align-items:center; justify-content:center;
                height:100vh; width:100%;
            }
            .login-card{
                width: 380px; border: 1px solid rgba(0,0,0,0.08);
                border-radius: 12px; padding: 18px 18px 14px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.06); background: #fff;
            }
            .login-title{ font-size: 1.1rem; font-weight: 700; margin: 0 0 10px 0; text-align:center; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-wrap"><div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Ingresá para ver el tablero</div>', unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar", use_container_width=True)
        if submit:
            if user in USERS and pwd == USERS[user]:
                st.session_state["logged_in"] = True
                st.session_state["whoami"] = user
                st.success("Autenticado correctamente.")
            else:
                st.error("Usuario o contraseña inválidos.")

    st.markdown('</div></div>', unsafe_allow_html=True)

# Mostrar login si no está autenticado (sin st.rerun)
if not st.session_state["logged_in"]:
    render_login()
    if not st.session_state["logged_in"]:
        st.stop()

# ================== ESTILOS DEL TABLERO (se cargan sólo si hay login) ==================
st.markdown(
    """
    <style>
      header {visibility: hidden;}
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      /* Restauramos padding para el tablero (el login lo había puesto en 0) */
      .block-container { padding: 0.5rem 1rem 0 1rem !important; }

      /* Tarjetas métricas (compactas) */
      .metric-card {
          border-radius: 12px;
          padding: 8px 10px;
          box-shadow: 0 1px 6px rgba(0,0,0,0.05);
          border: 1px solid rgba(0,0,0,0.05);
          display: inline-block;
          margin: 0 6px 6px 0;
          min-width: 120px;
          vertical-align: top;
      }
      .metric-label { font-size: 10px; opacity: 0.7; margin-bottom: 2px; }
      .metric-value { font-size: 16px; font-weight: 700; line-height: 1.1; }

      /* Mini tablas */
      .mini-title { font-weight: 600; margin: 0 0 6px 2px; }
      .table-box { 
          height: 320px; 
          overflow-y: auto; 
          overflow-x: hidden; 
          flex: 1;
      }
      .table-compact { width: 100%; table-layout: fixed; border-collapse: collapse; }
      .table-compact th, .table-compact td {
          padding: 6px 8px; border-bottom: 1px solid #eee; font-size: 12px; vertical-align: top;
      }
      .table-compact th { position: sticky; top: 0; background: #fafafa; z-index: 1; }
      .table-compact th:first-child, .table-compact td:first-child { width: 68%; }
      .table-compact th:last-child, .table-compact td:last-child { 
          width: 32%; 
          text-align: right; 
          white-space: nowrap; /* una sola línea para los montos */
      }
      .table-compact td { word-break: break-word; white-space: normal; }

      /* Tres rectángulos iguales con GRID */
      .three-cards {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 5px;
          width: 100%;
          margin-right: -14px; /* come el padding derecho del contenedor para que Cliente no deje hueco */
      }
      div[data-testid="column"]:has(.three-cards) {
          padding-right: 0 !important;
      }
      .three-cards > .card {
          border: 1px solid rgba(0,0,0,0.05);
          border-radius: 8px;
          padding: 4px;
          box-shadow: 0 1px 4px rgba(0,0,0,0.04);
          display: flex;
          flex-direction: column;
          min-width: 0;
          height: 350px;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== LOGO Y TÍTULO ==================
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_base64 = get_base64_image("logorelleno (1).png")

st.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: center; position: relative; margin-bottom: 0.75rem;">
        <h1 style="font-size:1.5rem; margin:0;">Draft Biosidus Aging</h1>
        <img src="data:image/png;base64,{logo_base64}" alt="Logo"
             style="height:50px; position: absolute; right: -25px; top: 13px;">
    </div>
    """,
    unsafe_allow_html=True
)

# Botón de logout
with st.sidebar:
    st.write(f"👤 {st.session_state['whoami']}")
    if st.button("Cerrar sesión", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["whoami"] = ""
        st.experimental_set_query_params()  # limpia posibles params
        st.success("Sesión cerrada. Actualizá la página para volver a ingresar.")
        st.stop()

# ================== CARGA DE DATOS (SIN UPLOAD) ==================
REQUIRED_COLUMNS = [
    "BUKRS_TXT", "KUNNR_TXT", "PRCTR", "VKORG_TXT", "VTWEG_TXT",
    "NOT_DUE_AMOUNT_USD", "DUE_30_DAYS_USD", "DUE_60_DAYS_USD", "DUE_90_DAYS_USD",
    "DUE_120_DAYS_USD", "DUE_180_DAYS_USD", "DUE_270_DAYS_USD", "DUE_360_DAYS_USD", "DUE_OVER_360_DAYS_USD"
]
metric_cols = REQUIRED_COLUMNS[5:]

@st.cache_data(show_spinner=False)
def load_excel(path_or_buffer):
    df = pd.read_excel(path_or_buffer)
    df.columns = [str(c).strip() for c in df.columns]
    return df

default_path = Path("AGING AL 2025-01-28.xlsx")
if not default_path.exists():
    st.error(f"No se encontró el archivo por defecto: {default_path.resolve()}")
    st.stop()

df = load_excel(default_path)

missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing:
    st.error(f"Faltan columnas requeridas: {', '.join(missing)}")
    st.stop()

# ================== PARSEO NUMÉRICO ==================
def smart_to_numeric(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        return s.fillna(0)
    s1 = pd.to_numeric(s, errors="coerce")
    if s1.isna().mean() > 0.5:
        s2 = (
            s.astype(str)
             .str.replace(r"\.", "", regex=True)
             .str.replace(",", ".", regex=False)
        )
        s1 = pd.to_numeric(s2, errors="coerce")
    return s1.fillna(0)

for col in metric_cols:
    df[f"_{col}_NUM"] = smart_to_numeric(df[col])

# ================== FILTROS ==================
if "filters_version" not in st.session_state:
    st.session_state["filters_version"] = 0
filters_version = st.session_state["filters_version"]

with st.sidebar:
    st.markdown("**Filtros**")

    def dropdown(label, colname):
        vals = pd.Series(df[colname].dropna().unique())
        try:
            vals = vals.sort_values()
        except Exception:
            pass
        options = ["Todos"] + vals.astype(str).tolist()
        key = f"sel_{colname}_{filters_version}"
        return st.selectbox(label, options=options, index=0, key=key)

    sel_BUKRS_TXT = dropdown("Sociedad", "BUKRS_TXT")
    sel_KUNNR_TXT = dropdown("Cliente",  "KUNNR_TXT")
    sel_PRCTR     = dropdown("Cen.Ben",  "PRCTR")
    sel_VKORG_TXT = dropdown("Mercado",  "VKORG_TXT")
    sel_VTWEG_TXT = dropdown("Canal",    "VTWEG_TXT")

    if st.button("🧹 Limpiar filtros", use_container_width=True):
        st.session_state["filters_version"] += 1

# ================== TARJETAS ==================
df_for_metrics = df if sel_KUNNR_TXT == "Todos" else df[df["KUNNR_TXT"].astype(str) == str(sel_KUNNR_TXT)]
def format_usd_millions(x: float) -> str:
    millones = x / 1_000_000
    return f"US$ {millones:,.2f}M".replace(",", "X").replace(".", ",").replace("X", ".")

cards_html = ""
for col in metric_cols:
    val = df_for_metrics[f"_{col}_NUM"].sum()
    cards_html += f"""
    <div class="metric-card">
        <div class="metric-label">{col}</div>
        <div class="metric-value">{format_usd_millions(val)}</div>
    </div>
    """
st.markdown(cards_html, unsafe_allow_html=True)

# ================== PIE CHART ==================
label_map = {
    "NOT_DUE_AMOUNT_USD": "No vencido",
    "DUE_30_DAYS_USD": "30",
    "DUE_60_DAYS_USD": "60",
    "DUE_90_DAYS_USD": "90",
    "DUE_120_DAYS_USD": "120",
    "DUE_180_DAYS_USD": "180",
    "DUE_270_DAYS_USD": "270",
    "DUE_360_DAYS_USD": "360",
    "DUE_OVER_360_DAYS_USD": "+360",
}
reverse_label_map = {v: k for k, v in label_map.items()}

col_sums = {col: float(df_for_metrics[f"_{col}_NUM"].sum()) for col in metric_cols}
pie_data = [{"name": label_map.get(k, k), "value": float(v)} for k, v in col_sums.items() if v > 0]

echarts_colors = ["#5470C6", "#91CC75", "#FAC858", "#EE6666", "#73C0DE",
                  "#3BA272", "#FC8452", "#9A60B4", "#EA7CCC"]

# Columnas: pie chart y tablas
col_chart, col_tables = st.columns([2.3, 2.7])

with col_chart:
    st.caption("Distribución por buckets")
    pie_options = {
        "color": echarts_colors,
        "tooltip": {"trigger": "item", "formatter": "{b}<br/>Valor: {c} USD<br/>{d}%"},
        "legend": {"show": False},
        "series": [{
            "name": "Buckets",
            "type": "pie",
            "radius": ["40%", "70%"],
            "selectedMode": "single",
            "avoidLabelOverlap": True,
            "itemStyle": {"borderRadius": 6, "borderColor": "#fff", "borderWidth": 1},
            "label": {"show": True, "position": "inside", "formatter": "{b}\n{d}%"},
            "labelLine": {"show": False},
            "data": pie_data
        }]
    }
    click_ret = st_echarts(
        options=pie_options,
        height="360px",
        key=f"pie_{filters_version}",
        events={"click": "function(p){ return {name: p.name, value: p.value}; }"}
    )
    clicked_bucket_es = click_ret["name"] if isinstance(click_ret, dict) and "name" in click_ret else None

# ================== APLICAR FILTROS A TABLA DETALLE ==================
df_filtered = df.copy()
def apply_eq_filter(frame, column, selected_value):
    if selected_value != "Todos":
        return frame[frame[column].astype(str) == str(selected_value)]
    return frame

for col_f, sel in [
    ("BUKRS_TXT", sel_BUKRS_TXT),
    ("KUNNR_TXT", sel_KUNNR_TXT),
    ("PRCTR", sel_PRCTR),
    ("VKORG_TXT", sel_VKORG_TXT),
    ("VTWEG_TXT", sel_VTWEG_TXT)
]:
    df_filtered = apply_eq_filter(df_filtered, col_f, sel)

if clicked_bucket_es in reverse_label_map:
    col_original = reverse_label_map[clicked_bucket_es]
    if col_original in metric_cols:
        df_filtered = df_filtered[smart_to_numeric(df_filtered[col_original]) > 0]
        st.success(f"Filtrado por sector: {clicked_bucket_es}")

# ================== TABLAS MERCADO / CANAL / CLIENTE ==================
def summarize_in_millions(frame: pd.DataFrame, group_col: str, label: str) -> pd.DataFrame:
    num_cols = [f"_{c}_NUM" for c in metric_cols]
    tmp = frame.copy()
    tmp["_TOTAL_USD_NUM"] = tmp[num_cols].sum(axis=1)
    out = (
        tmp.groupby(group_col, dropna=False)["_TOTAL_USD_NUM"]
           .sum()
           .sort_values(ascending=False)
           .reset_index()
    )
    out.rename(columns={group_col: label}, inplace=True)
    out["M USD"] = (out["_TOTAL_USD_NUM"] / 1_000_000).round(2)
    return out[[label, "M USD"]]

def render_table_html(df_small: pd.DataFrame) -> str:
    html = ['<div class="table-box"><table class="table-compact">']
    html.append("<thead><tr>")
    for col in df_small.columns:
        html.append(f"<th>{col}</th>")
    html.append("</tr></thead>")
    html.append("<tbody>")
    for _, row in df_small.iterrows():
        label_val = str(row.iloc[0])
        num_val = row.iloc[1]
        if isinstance(num_val, (int, float)):
            num_txt = f"{num_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            num_txt = str(num_val)
        html.append(f"<tr><td>{label_val}</td><td>{num_txt}</td></tr>")
    html.append("</tbody></table></div>")
    return "".join(html)

with col_tables:
    st.markdown(
        '<div class="three-cards">'
        + '<div class="card">'
            '<div class="mini-title">Mercado</div>'
            f'{render_table_html(summarize_in_millions(df_filtered, "VKORG_TXT", "Mercado"))}'
          '</div>'
        + '<div class="card">'
            '<div class="mini-title">Canal</div>'
            f'{render_table_html(summarize_in_millions(df_filtered, "VTWEG_TXT", "Canal"))}'
          '</div>'
        + '<div class="card">'
            '<div class="mini-title">Cliente</div>'
            f'{render_table_html(summarize_in_millions(df_filtered, "KUNNR_TXT", "Cliente"))}'
          '</div>'
        + '</div>',
        unsafe_allow_html=True
    )

# ================== TABLA DETALLE ==================
drop_aux = [f"_{col}_NUM" for col in metric_cols]
st.dataframe(
    df_filtered.drop(columns=drop_aux, errors="ignore"),
    use_container_width=True, hide_index=True
)
