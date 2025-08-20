import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit_echarts import st_echarts
import base64

# ================== CONFIG GLOBAL ==================
st.set_page_config(page_title="Aging - Filtros", layout="wide", initial_sidebar_state="expanded")

# Estado de autenticación
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ================== LOGIN ==================
def show_login():
    # Oculta header, menú, footer y sidebar SOLO en login
    st.markdown("""
        <style>
          header, #MainMenu, footer {visibility: hidden;}
          [data-testid="stSidebar"] { display: none !important; }

          /* Página centrada */
          .login-page {
              position: fixed;
              inset: 0;
              display: flex;
              align-items: center;
              justify-content: center;
              background: #ffffff; /* fondo liso */
              padding: 0 16px;
          }
          /* Tarjeta del login */
          .login-card {
              width: 340px;
              max-width: 94vw;
              border: 1px solid rgba(0,0,0,0.08);
              border-radius: 14px;
              box-shadow: 0 10px 30px rgba(0,0,0,0.06);
              padding: 0 16px 16px;    /* 👈 sin padding arriba */
              background: #fff;
          }

          /* ====== FIX del “rectángulo blanco” arriba del título ====== */
          .login-card .stMarkdown { margin: 0 !important; padding: 0 !important; }
          .login-card .stMarkdown p { margin: 0 !important; padding: 0 !important; }
          .login-card [data-testid="stVerticalBlock"] > div:first-child {
              margin-top: 0 !important; padding-top: 0 !important;
          }

          /* Título y subtítulo */
          .login-title {
              margin: 0 0 12px 0 !important;   /* 👈 sin margen arriba */
              padding-top: 0 !important;
              font-size: 18px;
              font-weight: 700;
              text-align: center;
          }
          .login-sub {
              margin: -6px 0 14px 0;
              font-size: 12px;
              opacity: .65;
              text-align: center;
          }

          /* Form sin espacio extra arriba */
          .login-card form, .login-card [data-testid="stForm"] {
              margin-top: 0 !important;
              padding-top: 0 !important;
          }

          .login-btn > button { width: 100% !important; }
        </style>
    """, unsafe_allow_html=True)

    # Estructura visual del login
    st.markdown('<div class="login-page"><div class="login-card">', unsafe_allow_html=True)

    # Título + subtítulo (markdown sin márgenes por CSS)
    st.markdown('<div class="login-title">Ingresá para ver el tablero</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Usuario y contraseña</div>', unsafe_allow_html=True)

    # Form de login
    with st.form("login_form", clear_on_submit=False):
        user = st.text_input("Usuario", key="login_user")
        pwd  = st.text_input("Contraseña", type="password", key="login_pass")
        submitted = st.form_submit_button("Ingresar", use_container_width=True)

    # Carga de credenciales: primero secrets, sino fallback
    auth_cfg = st.secrets.get("auth", {"users": {"admin": "1234"}})
    users = auth_cfg.get("users", {})

    if submitted:
        if user in users and str(pwd) == str(users[user]):
            st.session_state.authenticated = True
            st.success("Token generado. Haga click nuevamente en Ingresar")
        else:
            st.error("Usuario o contraseña incorrectos.")

    st.markdown('</div></div>', unsafe_allow_html=True)  # /login-card + /login-page

# ================== APP PRINCIPAL ==================
def main_app():
    # Ocultar cabecera/menú/footer + estilos globales del tablero
    st.markdown(
        """
        <style>
          header {visibility: hidden;}
          #MainMenu {visibility: hidden;}
          footer {visibility: hidden;}

          /* Evitar cortes horizontales */
          html, body, [data-testid="stAppViewContainer"] { overflow-x: auto !important; }

          .block-container { padding-top: 0.5rem; }

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
              overflow-x: auto;   /* 👈 antes estaba hidden */
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
              white-space: nowrap;
          }
          .table-compact td { word-break: break-word; white-space: normal; }

          /* Tres rectángulos iguales con GRID */
          .three-cards {
              display: grid;
              grid-template-columns: repeat(3, 1fr);
              gap: 6px;
              width: 100%;
              /* margin-right: -14px;  <-- eliminado */
          }
          .three-cards > .card {
              border: 1px solid rgba(0,0,0,0.05);
              border-radius: 8px;
              padding: 6px;
              box-shadow: 0 1px 4px rgba(0,0,0,0.04);
              display: flex;
              flex-direction: column;
              min-width: 0;
              height: 350px;
          }

          /* Responsive: 3 -> 2 -> 1 columnas */
          @media (max-width: 960px){ .three-cards { grid-template-columns: repeat(2, 1fr); } }
          @media (max-width: 520px){ .three-cards { grid-template-columns: 1fr; } }
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
                 .str.replace(r"\.", "", regex=True)   # <-- fix: antes era "\\."
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

    def render_filters(container, key_prefix):
        with container:
            st.markdown("**Filtros**")
            def dropdown(label, colname):
                vals = pd.Series(df[colname].dropna().unique())
                try:
                    vals = vals.sort_values()
                except Exception:
                    pass
                options = ["Todos"] + vals.astype(str).tolist()
                key = f"{key_prefix}_{colname}_{filters_version}"
                return st.selectbox(label, options=options, index=0, key=key)

            sels = {
                "BUKRS_TXT": dropdown("Sociedad", "BUKRS_TXT"),
                "KUNNR_TXT": dropdown("Cliente",  "KUNNR_TXT"),
                "PRCTR":     dropdown("Cen.Ben",  "PRCTR"),
                "VKORG_TXT": dropdown("Mercado",  "VKORG_TXT"),
                "VTWEG_TXT": dropdown("Canal",    "VTWEG_TXT"),
            }
            clear = st.button("🧹 Limpiar filtros", use_container_width=True, key=f"{key_prefix}_clear_{filters_version}")
        return sels, clear

    # Sidebar
    side_sel, side_clear = render_filters(st.sidebar, "side")

    # Fallback arriba para móvil (si no ves sidebar)
    exp = st.expander("Filtros (si no ves la pestaña lateral, usá este)")
    mob_sel, mob_clear = render_filters(exp, "mob")  # 👉 le pasamos el expander (sí es un container)


    def any_selected(sels: dict) -> bool:
        return any(v != "Todos" for v in sels.values())

    active = mob_sel if any_selected(mob_sel) else side_sel

    if side_clear or mob_clear:
        st.session_state["filters_version"] += 1
        try:
            st.rerun()
        except Exception:
            st.experimental_rerun()

    sel_BUKRS_TXT = active["BUKRS_TXT"]
    sel_KUNNR_TXT = active["KUNNR_TXT"]
    sel_PRCTR     = active["PRCTR"]
    sel_VKORG_TXT = active["VKORG_TXT"]
    sel_VTWEG_TXT = active["VTWEG_TXT"]

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

# ================== ROUTING ==================
if not st.session_state.authenticated:
    show_login()
    st.stop()  # Evita que se renderice el tablero detrás del login

# Si llegó acá, es porque autenticó
main_app()
