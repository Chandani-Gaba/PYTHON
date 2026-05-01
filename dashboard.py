"""
╔══════════════════════════════════════════════════════════════════╗
║   AI & AUTOMATION WORKFORCE DASHBOARD  —  CSV Upload Edition    ║
║   Upload the matching CSV per question → Chart renders live     ║
╚══════════════════════════════════════════════════════════════════╝

HOW TO USE
──────────
1.  Run:  python dashboard.py
2.  Open: http://127.0.0.1:8050
3.  Click any Q1–Q8 in the sidebar
4.  Upload the matching CSV file
5.  Chart appears instantly!

CSV FILES NEEDED (in same folder)
──────────────────────────────────
  Q1 → q1_industry_automation_risk.csv
  Q2 → q2_job_market_trends.csv
  Q3 → q3_country_ai_readiness.csv
  Q4 → q4_salary_comparison.csv
  Q5 → q5_education_automation.csv
  Q6 → q6_ai_skills_demand.csv
  Q7 → q7_remote_ai_adoption.csv
  Q8 → q8_ai_investment.csv
"""

import base64, io
import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────────────────────
#  COLOUR PALETTE  ·  Cyberpunk / Deep Space
# ─────────────────────────────────────────────────────────────
BG       = "#04091e"
SIDE_BG  = "#060d28"
CARD_BG  = "#0b1535"
CARD2    = "#081020"
CYAN     = "#00e5ff"
PURPLE   = "#7c3aed"
GOLD     = "#f5c518"
PINK     = "#ff4d8d"
GREEN    = "#00ffaa"
ORANGE   = "#ff8c42"
TEXT     = "#dce8ff"
MUTED    = "#617799"
BORDER   = "#162040"
WHITE    = "#ffffff"

# ─────────────────────────────────────────────────────────────
#  RESEARCH QUESTIONS METADATA
# ─────────────────────────────────────────────────────────────
QUESTIONS = [
    {
        "id": "q1", "icon": "⚙️", "label": "Automation Risk",
        "full": "Which industries face the highest AI-driven automation risk?",
        "csv":  "q1_industry_automation_risk.csv",
        "cols": ["Industry", "Automation_Risk_Percent", "Jobs_at_Risk_Millions", "Avg_Wage_USD", "Timeline_Years"],
        "insight": "Data Entry (95%) and Transportation (88%) are most at risk. Creative Arts and Legal Services remain resilient below 20%.",
        "chart_type": "Horizontal Bar Chart",
    },
    {
        "id": "q2", "icon": "📈", "label": "Job Market Trend",
        "full": "How have AI job postings trended vs. traditional roles (2020–2026)?",
        "csv":  "q2_job_market_trends.csv",
        "cols": ["Year", "AI_Job_Postings", "Traditional_Job_Postings", "AI_Salary_Avg_USD", "Traditional_Salary_Avg_USD"],
        "insight": "AI job postings grew ~860% while traditional postings dropped ~36%, signalling a structural labour market shift.",
        "chart_type": "Dual-Area Line Chart",
    },
    {
        "id": "q3", "icon": "🌍", "label": "Country Readiness",
        "full": "Which nations lead in AI workforce readiness and adoption?",
        "csv":  "q3_country_ai_readiness.csv",
        "cols": ["Country", "AI_Readiness_Score", "AI_Investment_Billion", "AI_Researchers_k", "Workforce_Reskilled_Pct"],
        "insight": "USA (93), China (89), and Singapore (86) dominate. India rapidly closing the gap at 67 with the world's largest AI research community.",
        "chart_type": "Gradient Bar Chart",
    },
    {
        "id": "q4", "icon": "💰", "label": "Salary Gap",
        "full": "What is the salary premium for AI-augmented roles vs. traditional ones?",
        "csv":  "q4_salary_comparison.csv",
        "cols": ["Role", "AI_Augmented_Salary_USD", "Traditional_Salary_USD", "Experience_Years"],
        "insight": "AI-augmented roles command 30–45% salary premiums. ML Engineers ($158k) and AI Researchers ($178k) see the widest gaps.",
        "chart_type": "Grouped Bar Chart",
    },
    {
        "id": "q5", "icon": "🎓", "label": "Education vs Risk",
        "full": "How does education level influence a worker's automation vulnerability?",
        "csv":  "q5_education_automation.csv",
        "cols": ["Education_Level", "Automation_Risk_Percent", "Avg_Annual_Income_USD", "Population_Share_Pct"],
        "insight": "Workers without a diploma face 91% automation risk vs only 13% for PhD holders. Each educational rung correlates strongly with income and safety.",
        "chart_type": "Bubble Scatter Plot",
    },
    {
        "id": "q6", "icon": "🔧", "label": "In-Demand Skills",
        "full": "What AI technical skills are most in-demand in the 2026 job market?",
        "csv":  "q6_ai_skills_demand.csv",
        "cols": ["Skill", "Demand_Score", "Job_Postings_k", "Avg_Salary_k", "Growth_YoY_Pct"],
        "insight": "Python (97) and Data Analysis (90) top charts. Prompt Engineering & AI Ethics are fastest growing — up 112% and 88% YoY respectively.",
        "chart_type": "Color-Tiered Bar + Scatter",
    },
    {
        "id": "q7", "icon": "🏠", "label": "Remote × AI",
        "full": "Is there a correlation between remote work adoption and AI tool usage?",
        "csv":  "q7_remote_ai_adoption.csv",
        "cols": ["Sector", "Remote_Work_Pct", "AI_Tool_Adoption_Pct", "Productivity_Gain_Pct", "Employee_Count"],
        "insight": "Strong positive correlation (r ≈ 0.72). Companies with >70% remote workforce show highest AI adoption and up to 68% productivity gains.",
        "chart_type": "Multi-Sector Scatter Plot with Trend",
    },
    {
        "id": "q8", "icon": "💼", "label": "Sector Investment",
        "full": "How is the $251B global AI investment distributed across sectors?",
        "csv":  "q8_ai_investment.csv",
        "cols": ["Sector", "Investment_Billion_USD", "YoY_Growth_Pct", "No_of_Startups", "Govt_Share_Pct"],
        "insight": "Healthcare leads at $45.2B, Finance at $40.8B. Education shows highest YoY growth (+55%). Defence spending surprises at $33.5B.",
        "chart_type": "Donut Pie + Bar Combo",
    },
]

# ─────────────────────────────────────────────────────────────
#  CHART LAYOUT HELPER
# ─────────────────────────────────────────────────────────────
def base_layout(title="", height=440):
    return dict(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(color=TEXT, size=14, family="Rajdhani, Orbitron, monospace"),
            x=0.5, xanchor="center", y=0.97,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, family="Rajdhani, monospace"),
        height=height,
        margin=dict(l=55, r=30, t=55, b=60),
        legend=dict(
            font=dict(color=TEXT, size=11),
            bgcolor="rgba(0,0,0,0)",
            bordercolor=BORDER, borderwidth=1,
        ),
    )

def ax_x(showgrid=True, **kw):
    return dict(showgrid=showgrid, gridcolor="#132040", gridwidth=0.5,
                zeroline=False, tickfont=dict(color=MUTED, size=11),
                linecolor=BORDER, **kw)

def ax_y(showgrid=True, **kw):
    return dict(showgrid=showgrid, gridcolor="#132040", gridwidth=0.5,
                zeroline=False, tickfont=dict(color=MUTED, size=11),
                linecolor=BORDER, **kw)

# ─────────────────────────────────────────────────────────────
#  CHART BUILDERS  (accept a DataFrame)
# ─────────────────────────────────────────────────────────────

def build_q1(df):
    df = df.sort_values("Automation_Risk_Percent")
    r = df["Automation_Risk_Percent"].tolist()
    colors = [
        f"rgba({min(255,int(255*v/100))},{max(30,int(180-v*1.3))},{max(20,int(255*(1-v/100)))},0.88)"
        for v in r
    ]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=r, y=df["Industry"], orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.04)", width=0.4)),
        text=[f" {v}%" for v in r],
        textposition="outside", textfont=dict(color=TEXT, size=11),
        customdata=df[["Jobs_at_Risk_Millions","Avg_Wage_USD","Timeline_Years"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Automation Risk: <b>%{x}%</b><br>"
            "Jobs at Risk: <b>%{customdata[0]}M</b><br>"
            "Avg Wage: <b>$%{customdata[1]:,}</b><br>"
            "Timeline: <b>%{customdata[2]} yrs</b><extra></extra>"
        ),
    ))
    fig.update_layout(**base_layout("Industry Automation Risk — AI Disruption Index", height=470))
    fig.update_xaxes(**ax_x(), range=[0, 115],
                     title_text="Automation Risk (%)", title_font=dict(color=MUTED, size=11))
    fig.update_yaxes(showgrid=False, zeroline=False, linecolor=BORDER,
                     tickfont=dict(color=TEXT, size=11))
    return fig


def build_q2(df):
    df = df.dropna(subset=["Year"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["AI_Job_Postings"],
        name="AI / Tech Jobs", mode="lines+markers",
        line=dict(color=CYAN, width=3),
        marker=dict(size=9, color=CYAN, line=dict(width=2, color=BG)),
        fill="tozeroy", fillcolor="rgba(0,229,255,0.10)",
        customdata=df["AI_Salary_Avg_USD"],
        hovertemplate="Year: <b>%{x}</b><br>AI Jobs: <b>%{y:,}</b><br>Avg Salary: <b>$%{customdata:,}</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["Traditional_Job_Postings"],
        name="Traditional Jobs", mode="lines+markers",
        line=dict(color=PINK, width=3),
        marker=dict(size=9, color=PINK, line=dict(width=2, color=BG)),
        fill="tozeroy", fillcolor="rgba(255,77,141,0.09)",
        customdata=df["Traditional_Salary_Avg_USD"],
        hovertemplate="Year: <b>%{x}</b><br>Traditional: <b>%{y:,}</b><br>Avg Salary: <b>$%{customdata:,}</b><extra></extra>",
    ))
    fig.update_layout(**base_layout("AI vs Traditional Job Postings — 2020 to 2026"))
    fig.update_xaxes(**ax_x(), tickvals=df["Year"].tolist())
    fig.update_yaxes(**ax_y())
    return fig


def build_q3(df):
    df = df.sort_values("AI_Readiness_Score", ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["AI_Readiness_Score"], y=df["Country"], orientation="h",
        marker=dict(
            color=df["AI_Readiness_Score"],
            colorscale=[[0, PURPLE], [0.5, CYAN], [1, GREEN]],
            showscale=True,
            colorbar=dict(title="Score", tickfont=dict(color=TEXT),
                          title_font=dict(color=TEXT)),
        ),
        text=[f" {v}" for v in df["AI_Readiness_Score"]],
        textposition="outside", textfont=dict(color=TEXT, size=11),
        customdata=df[["AI_Investment_Billion","AI_Researchers_k","Workforce_Reskilled_Pct"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "AI Readiness: <b>%{x}/100</b><br>"
            "Investment: <b>$%{customdata[0]}B</b><br>"
            "Researchers: <b>%{customdata[1]}k</b><br>"
            "Workforce Reskilled: <b>%{customdata[2]}%</b><extra></extra>"
        ),
    ))
    fig.update_layout(**base_layout("Global AI Workforce Readiness Index (2026)", height=450))
    fig.update_xaxes(**ax_x(), range=[0, 105],
                     title_text="Readiness Score", title_font=dict(color=MUTED, size=11))
    fig.update_yaxes(showgrid=False, zeroline=False, tickfont=dict(color=TEXT, size=11))
    return fig


def build_q4(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="AI-Augmented Role", x=df["Role"],
        y=(df["AI_Augmented_Salary_USD"] / 1000).round(1),
        marker=dict(color=CYAN, opacity=0.9,
                    line=dict(color="rgba(255,255,255,0.07)", width=0.5)),
        hovertemplate="<b>%{x}</b><br>AI Role: <b>$%{y}k/yr</b><extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Traditional Role", x=df["Role"],
        y=(df["Traditional_Salary_USD"] / 1000).round(1),
        marker=dict(color=PURPLE, opacity=0.88,
                    line=dict(color="rgba(255,255,255,0.07)", width=0.5)),
        hovertemplate="<b>%{x}</b><br>Traditional: <b>$%{y}k/yr</b><extra></extra>",
    ))
    # Salary gap annotation line
    diff = ((df["AI_Augmented_Salary_USD"] - df["Traditional_Salary_USD"]) / 1000).round(1)
    for i, (role, d) in enumerate(zip(df["Role"], diff)):
        fig.add_annotation(
            x=role,
            y=(df["AI_Augmented_Salary_USD"].iloc[i] / 1000) + 8,
            text=f"+${d}k",
            font=dict(color=GOLD, size=9, family="Rajdhani, monospace"),
            showarrow=False,
        )
    fig.update_layout(**base_layout("Salary Premium — AI-Augmented vs Traditional Roles"), barmode="group")
    fig.update_xaxes(**ax_x(False), tickangle=-30)
    fig.update_yaxes(**ax_y(), title_text="Annual Salary ($k)",
                     title_font=dict(color=MUTED, size=11))
    return fig


def build_q5(df):
    sizes = (df["Population_Share_Pct"] * 5).tolist()
    fig = go.Figure(go.Scatter(
        x=df["Avg_Annual_Income_USD"],
        y=df["Automation_Risk_Percent"],
        mode="markers+text",
        marker=dict(
            size=sizes,
            color=df["Automation_Risk_Percent"],
            colorscale=[[0, GREEN], [0.5, GOLD], [1, PINK]],
            showscale=True,
            colorbar=dict(title="Risk %", tickfont=dict(color=TEXT),
                          title_font=dict(color=TEXT)),
            line=dict(width=2, color=BG), opacity=0.9,
        ),
        text=df["Education_Level"],
        textposition="top center",
        textfont=dict(color=TEXT, size=10),
        customdata=df["Population_Share_Pct"],
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Income: <b>$%{x:,}/yr</b><br>"
            "Automation Risk: <b>%{y}%</b><br>"
            "Population Share: <b>%{customdata}%</b><extra></extra>"
        ),
    ))
    fig.update_layout(**base_layout("Education Level vs Automation Risk & Average Income"))
    fig.update_xaxes(**ax_x(), title_text="Average Annual Income (USD)",
                     title_font=dict(color=MUTED, size=11),
                     tickformat="$,.0f")
    fig.update_yaxes(**ax_y(), title_text="Automation Risk (%)",
                     title_font=dict(color=MUTED, size=11))
    return fig


def build_q6(df):
    df = df.sort_values("Demand_Score", ascending=False)
    palette = ([CYAN]*3 + [PURPLE]*3 + [GOLD]*2 + [ORANGE]*2)[:len(df)]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Skill"], y=df["Demand_Score"],
        marker=dict(color=palette, line=dict(color="rgba(255,255,255,0.06)", width=0.5)),
        text=df["Demand_Score"], textposition="outside",
        textfont=dict(color=TEXT, size=11),
        customdata=df[["Job_Postings_k","Avg_Salary_k","Growth_YoY_Pct"]].values,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Demand Score: <b>%{y}</b><br>"
            "Job Postings: <b>%{customdata[0]}k</b><br>"
            "Avg Salary: <b>$%{customdata[1]}k</b><br>"
            "YoY Growth: <b>%{customdata[2]}%</b><extra></extra>"
        ),
        name="Demand Score",
    ))
    fig.update_layout(**base_layout("Top AI Skills — Demand Score & Market Data (2026)"))
    fig.update_xaxes(**ax_x(False), tickangle=-30)
    fig.update_yaxes(**ax_y(), range=[0, 110])
    return fig


def build_q7(df):
    sector_colors = {
        "Tech": CYAN, "Finance": GOLD, "Healthcare": GREEN,
        "Education": PURPLE, "Retail": PINK, "Manufacturing": ORANGE,
    }
    fig = go.Figure()
    for sec, col in sector_colors.items():
        mask = df["Sector"] == sec
        d = df[mask]
        if d.empty:
            continue
        fig.add_trace(go.Scatter(
            x=d["Remote_Work_Pct"], y=d["AI_Tool_Adoption_Pct"],
            mode="markers", name=sec,
            marker=dict(
                size=(d["Productivity_Gain_Pct"] * 0.45 + 5).tolist(),
                color=col, opacity=0.82,
                line=dict(width=1, color=BG),
            ),
            customdata=d[["Productivity_Gain_Pct","Employee_Count"]].values,
            hovertemplate=(
                f"<b>{sec}</b><br>"
                "Remote Work: <b>%{x:.1f}%</b><br>"
                "AI Adoption: <b>%{y:.1f}%</b><br>"
                "Productivity Gain: <b>%{customdata[0]:.1f}%</b><br>"
                "Employees: <b>%{customdata[1]:,}</b><extra></extra>"
            ),
        ))
    # Trend line
    z = np.polyfit(df["Remote_Work_Pct"], df["AI_Tool_Adoption_Pct"], 1)
    xr = np.linspace(df["Remote_Work_Pct"].min(), df["Remote_Work_Pct"].max(), 100)
    fig.add_trace(go.Scatter(
        x=xr, y=np.poly1d(z)(xr),
        mode="lines", name="Trend Line",
        line=dict(color=GOLD, width=2, dash="dash"), showlegend=True,
    ))
    fig.update_layout(**base_layout("Remote Work (%) vs AI Tool Adoption — Bubble = Productivity Gain"))
    fig.update_xaxes(**ax_x(), title_text="Remote Work (%)",
                     title_font=dict(color=MUTED, size=11))
    fig.update_yaxes(**ax_y(), title_text="AI Tool Adoption (%)",
                     title_font=dict(color=MUTED, size=11))
    return fig


def build_q8(df):
    total = df["Investment_Billion_USD"].sum()
    colors = [CYAN, GOLD, GREEN, PINK, PURPLE, ORANGE, "#00bcd4", "#e040fb"]
    fig = go.Figure(go.Pie(
        labels=df["Sector"],
        values=df["Investment_Billion_USD"],
        hole=0.52,
        marker=dict(colors=colors[:len(df)], line=dict(color=BG, width=3)),
        textfont=dict(color=WHITE, size=11),
        textinfo="label+percent",
        customdata=df[["YoY_Growth_Pct","No_of_Startups","Govt_Share_Pct"]].values,
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Investment: <b>$%{value}B</b><br>"
            "YoY Growth: <b>%{customdata[0]}%</b><br>"
            "Startups: <b>%{customdata[1]}</b><br>"
            "Govt Share: <b>%{customdata[2]}%</b><extra></extra>"
        ),
        rotation=40,
    ))
    fig.update_layout(
        **base_layout(f"Global AI Investment by Sector — Total ${total:.0f}B (2026)"),
        annotations=[dict(
            text=f"<b>${total:.0f}B</b><br>Total",
            x=0.5, y=0.5,
            font=dict(size=16, color=GOLD, family="Rajdhani, monospace"),
            showarrow=False,
        )],
    )
    return fig


CHART_BUILDERS = {
    "q1": build_q1, "q2": build_q2, "q3": build_q3, "q4": build_q4,
    "q5": build_q5, "q6": build_q6, "q7": build_q7, "q8": build_q8,
}

# ─────────────────────────────────────────────────────────────
#  HELPER: parse uploaded CSV content
# ─────────────────────────────────────────────────────────────
def parse_csv(contents, filename):
    """Decode base64 Dash upload and return DataFrame or error string."""
    if contents is None:
        return None, None
    try:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        return df, None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────────────────────
#  SIDEBAR BUTTON STYLE
# ─────────────────────────────────────────────────────────────
def btn_style(is_active):
    return {
        "display": "flex", "alignItems": "center",
        "width": "100%", "textAlign": "left", "cursor": "pointer",
        "borderRadius": "10px", "padding": "10px 13px", "marginBottom": "7px",
        "transition": "all 0.25s ease",
        "background": "linear-gradient(90deg,rgba(124,58,237,0.28),rgba(0,229,255,0.07))"
                      if is_active else "transparent",
        "border": f"1px solid {CYAN}" if is_active else f"1px solid {BORDER}",
        "boxShadow": "0 0 12px rgba(0,229,255,0.22)" if is_active else "none",
        "color": TEXT,
    }


# ─────────────────────────────────────────────────────────────
#  UPLOAD ZONE COMPONENT
# ─────────────────────────────────────────────────────────────
def upload_zone(q_meta):
    return html.Div([
        dcc.Upload(
            id="csv-upload",
            children=html.Div([
                html.Div("📂", style={"fontSize": "40px", "marginBottom": "10px"}),
                html.Div(f"Drop or Click to Upload CSV", style={
                    "fontSize": "15px", "fontWeight": "700", "color": CYAN,
                    "fontFamily": "Orbitron, monospace", "letterSpacing": "1px",
                }),
                html.Div(f"Expected file:  {q_meta['csv']}", style={
                    "fontSize": "11px", "color": MUTED, "marginTop": "8px",
                    "fontFamily": "Rajdhani, monospace",
                }),
                html.Div(
                    f"Required columns: {', '.join(q_meta['cols'][:4])}...",
                    style={"fontSize": "10px", "color": MUTED, "marginTop": "4px",
                           "fontFamily": "Rajdhani, monospace"}
                ),
            ], style={"textAlign": "center"}),
            style={
                "border": f"2px dashed {PURPLE}",
                "borderRadius": "14px",
                "padding": "40px 20px",
                "cursor": "pointer",
                "background": "rgba(124,58,237,0.06)",
                "transition": "all 0.3s",
            },
            multiple=False,
            accept=".csv",
        ),
    ])


# ─────────────────────────────────────────────────────────────
#  DASH APP
# ─────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="AI Workforce Dashboard — Upload Edition")
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Store(id="active-q",    data="q1"),
    dcc.Store(id="upload-data", data={}),      # {qid: csv_json_string}

    # ═══════════════════════════════════════════
    #  HEADER
    # ═══════════════════════════════════════════
    html.Div([
        html.Div([
            html.Span("🤖", style={"fontSize": "32px", "marginRight": "14px"}),
            html.Div([
                html.Div("AI & AUTOMATION WORKFORCE IMPACT", style={
                    "fontFamily": "Orbitron, monospace",
                    "fontSize": "16px", "fontWeight": "900", "letterSpacing": "2px",
                    "background": f"linear-gradient(90deg,{CYAN},{PURPLE})",
                    "WebkitBackgroundClip": "text", "WebkitTextFillColor": "transparent",
                }),
                html.Div(
                    "Upload CSV per Question  ·  8 Research Questions  ·  Python & Plotly Dash",
                    style={"fontSize": "11px", "color": MUTED, "letterSpacing": "0.8px",
                           "fontFamily": "Rajdhani, monospace"}),
            ]),
        ], style={"display": "flex", "alignItems": "center"}),

        html.Div([
            html.Span(id="upload-status-header",
                      children="0 / 8 CSV Files Uploaded",
                      style={"color": MUTED, "fontSize": "11px",
                             "fontFamily": "Orbitron, monospace",
                             "background": "rgba(255,255,255,0.04)",
                             "border": f"1px solid {BORDER}",
                             "padding": "5px 14px", "borderRadius": "20px"}),
        ]),
    ], style={
        "background": f"linear-gradient(135deg,{SIDE_BG},#08122a)",
        "padding": "13px 30px",
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "borderBottom": f"2px solid {PURPLE}",
        "boxShadow": f"0 4px 28px rgba(124,58,237,0.4)",
    }),

    # ═══════════════════════════════════════════
    #  BODY
    # ═══════════════════════════════════════════
    html.Div([

        # ── SIDEBAR ───────────────────────────
        html.Div([
            html.Div("RESEARCH  QUESTIONS", style={
                "fontFamily": "Orbitron, monospace", "fontSize": "8px",
                "fontWeight": "900", "letterSpacing": "3px",
                "color": GOLD, "marginBottom": "18px", "paddingLeft": "2px",
            }),

            html.Div(id="sidebar-btns"),

            html.Hr(style={"border": f"1px solid {BORDER}", "margin": "18px 0"}),

            html.Div("DATASET OVERVIEW", style={
                "fontFamily": "Orbitron, monospace", "fontSize": "8px",
                "fontWeight": "900", "letterSpacing": "2px",
                "color": MUTED, "marginBottom": "10px",
            }),
            html.Div(id="sidebar-stats", children=[
                html.Div("Upload CSVs to view stats",
                         style={"color": MUTED, "fontSize": "10px",
                                "fontFamily": "Rajdhani, monospace"})
            ]),

        ], style={
            "width": "210px", "minWidth": "210px",
            "background": SIDE_BG,
            "padding": "20px 13px",
            "borderRight": f"2px solid {BORDER}",
            "overflowY": "auto",
            "fontFamily": "Rajdhani, monospace",
        }),

        # ── MAIN CONTENT ─────────────────────
        html.Div([

            # Question header
            html.Div(id="q-header", style={
                "background": f"linear-gradient(135deg,{CARD_BG},{CARD2})",
                "border": f"1px solid {BORDER}",
                "borderLeft": f"4px solid {CYAN}",
                "borderRadius": "12px",
                "padding": "14px 22px",
                "marginBottom": "16px",
                "boxShadow": f"0 4px 18px rgba(0,229,255,0.07)",
            }),

            # Upload zone OR chart (toggles based on data)
            html.Div(id="main-content",
                     style={"marginBottom": "16px"}),

            # Stats / column preview row
            html.Div(id="data-preview", style={
                "background": f"linear-gradient(135deg,{CARD_BG},{CARD2})",
                "border": f"1px solid {BORDER}",
                "borderRadius": "10px",
                "padding": "13px 20px",
                "marginBottom": "16px",
            }),

            # Insight banner
            html.Div(id="insight-bar", style={
                "background": "rgba(0,229,255,0.04)",
                "border": f"1px solid {BORDER}",
                "borderLeft": f"4px solid {GOLD}",
                "borderRadius": "10px",
                "padding": "12px 20px",
            }),

        ], style={
            "flex": "1", "padding": "20px 24px",
            "overflowY": "auto",
            "fontFamily": "Rajdhani, monospace",
        }),

    ], style={
        "display": "flex",
        "height": "calc(100vh - 62px)",
        "overflow": "hidden",
    }),

], style={
    "backgroundColor": BG, "color": TEXT,
    "minHeight": "100vh",
    "fontFamily": "Rajdhani, monospace",
})


# ─────────────────────────────────────────────────────────────
#  CALLBACK 1 — switch active question via sidebar
# ─────────────────────────────────────────────────────────────
@app.callback(
    Output("active-q", "data"),
    [Input(f"btn-{q['id']}", "n_clicks") for q in QUESTIONS],
    prevent_initial_call=True,
)
def set_active(*_):
    ctx = callback_context
    if not ctx.triggered:
        return "q1"
    return ctx.triggered[0]["prop_id"].split(".")[0].replace("btn-", "")


# ─────────────────────────────────────────────────────────────
#  CALLBACK 2 — save uploaded CSV to store
# ─────────────────────────────────────────────────────────────
@app.callback(
    Output("upload-data", "data"),
    Input("csv-upload", "contents"),
    State("csv-upload", "filename"),
    State("active-q", "data"),
    State("upload-data", "data"),
    prevent_initial_call=True,
)
def save_upload(contents, filename, active_q, store):
    if contents is None:
        return store
    df, err = parse_csv(contents, filename)
    if err or df is None:
        return store
    store = store or {}
    store[active_q] = df.to_json(orient="records")
    return store


# ─────────────────────────────────────────────────────────────
#  CALLBACK 3 — render everything
# ─────────────────────────────────────────────────────────────
@app.callback(
    Output("sidebar-btns",       "children"),
    Output("sidebar-stats",      "children"),
    Output("upload-status-header","children"),
    Output("q-header",           "children"),
    Output("main-content",       "children"),
    Output("data-preview",       "children"),
    Output("insight-bar",        "children"),
    Input("active-q",   "data"),
    Input("upload-data","data"),
)
def render_all(active_q, store):
    store = store or {}
    q_meta = next(x for x in QUESTIONS if x["id"] == active_q)
    idx    = next(i for i, x in enumerate(QUESTIONS) if x["id"] == active_q) + 1
    uploaded_ids = set(store.keys())

    # ── Sidebar buttons ──────────────────────
    sidebar_btns = []
    for q in QUESTIONS:
        is_a     = (q["id"] == active_q)
        has_data = q["id"] in uploaded_ids
        tick     = html.Span("✓ ", style={"color": GREEN, "fontSize": "10px"}) if has_data else html.Span("○ ", style={"color": MUTED, "fontSize": "10px"})
        sidebar_btns.append(
            html.Button(
                [tick,
                 html.Span(q["icon"], style={"fontSize": "16px", "marginRight": "8px"}),
                 html.Span(q["label"], style={
                     "fontSize": "11px", "fontWeight": "700",
                     "color": CYAN if is_a else (GREEN if has_data else TEXT),
                 })],
                id=f"btn-{q['id']}", n_clicks=0,
                style=btn_style(is_a),
            )
        )

    # ── Sidebar dataset stats ─────────────────
    if uploaded_ids:
        stats_items = []
        for qid in uploaded_ids:
            qn = next(x for x in QUESTIONS if x["id"] == qid)
            df_tmp = pd.read_json(io.StringIO(store[qid]), orient="records")
            stats_items.append(html.Div(
                f"✓ {qn['label']} — {len(df_tmp)} rows",
                style={"color": GREEN, "fontSize": "10px", "marginBottom": "4px",
                       "fontFamily": "Rajdhani, monospace"}
            ))
        sidebar_stats = stats_items
    else:
        sidebar_stats = [html.Div("Upload CSVs to view stats",
                                  style={"color": MUTED, "fontSize": "10px"})]

    # ── Header status count ───────────────────
    header_status = f"{len(uploaded_ids)} / 8 CSV Files Uploaded"

    # ── Question header card ──────────────────
    q_header = html.Div([
        html.Div([
            html.Span(f"Q{idx}", style={
                "background": f"linear-gradient(135deg,{CYAN},{PURPLE})",
                "color": WHITE, "padding": "3px 13px", "borderRadius": "20px",
                "fontSize": "10px", "fontWeight": "700", "marginRight": "14px",
                "fontFamily": "Orbitron, monospace",
            }),
            html.Span(q_meta["full"],
                      style={"fontSize": "14px", "fontWeight": "600", "color": TEXT}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
        html.Div([
            html.Span(f"📊 {q_meta['chart_type']}  ·  ", style={"color": MUTED, "fontSize": "11px"}),
            html.Span(f"📁 {q_meta['csv']}", style={"color": PURPLE, "fontSize": "11px"}),
        ]),
    ])

    # ── Main content: upload zone OR chart ───
    if active_q in uploaded_ids:
        df = pd.read_json(io.StringIO(store[active_q]), orient="records")
        try:
            fig = CHART_BUILDERS[active_q](df)
            main_content = html.Div([
                html.Div([
                    html.Span("✅  CSV Loaded Successfully", style={
                        "color": GREEN, "fontSize": "11px", "fontWeight": "700",
                        "fontFamily": "Orbitron, monospace", "marginRight": "16px",
                    }),
                    dcc.Upload(
                        id="csv-upload",
                        children=html.Span("↺ Re-upload", style={
                            "color": CYAN, "fontSize": "11px", "cursor": "pointer",
                            "textDecoration": "underline",
                        }),
                        multiple=False, accept=".csv",
                    ),
                ], style={"marginBottom": "10px"}),
                html.Div([
                    dcc.Graph(
                        figure=fig,
                        config={"displayModeBar": True, "displaylogo": False,
                                "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
                    ),
                ], style={
                    "background": f"linear-gradient(145deg,{CARD_BG},{CARD2})",
                    "border": f"1px solid {BORDER}",
                    "borderRadius": "12px",
                    "padding": "16px",
                    "boxShadow": f"0 6px 28px rgba(124,58,237,0.14)",
                }),
            ])
        except Exception as e:
            main_content = html.Div([
                html.Div(f"⚠️  Error building chart: {str(e)}", style={
                    "color": PINK, "fontSize": "13px", "marginBottom": "12px"
                }),
                upload_zone(q_meta),
                dcc.Upload(id="csv-upload", children=html.Div(), multiple=False, accept=".csv",
                           style={"display": "none"}),
            ])
    else:
        main_content = html.Div([
            upload_zone(q_meta),
        ])

    # ── Data preview / column info ────────────
    if active_q in uploaded_ids:
        df = pd.read_json(io.StringIO(store[active_q]), orient="records")
        col_tags = [
            html.Span(col, style={
                "background": "rgba(0,229,255,0.08)",
                "border": f"1px solid {CYAN}33",
                "color": CYAN, "fontSize": "10px", "fontWeight": "700",
                "padding": "3px 10px", "borderRadius": "12px", "marginRight": "6px",
                "marginBottom": "4px", "display": "inline-block",
                "fontFamily": "Rajdhani, monospace",
            }) for col in df.columns
        ]
        preview = [
            html.Div([
                html.Span("📋 Dataset: ", style={"color": MUTED, "fontSize": "11px"}),
                html.Span(f"{len(df)} rows  ×  {len(df.columns)} columns", style={
                    "color": TEXT, "fontSize": "11px", "fontWeight": "700",
                    "marginRight": "20px",
                }),
                html.Span("Columns: ", style={"color": MUTED, "fontSize": "11px"}),
                *col_tags,
            ], style={"display": "flex", "flexWrap": "wrap", "alignItems": "center"}),
        ]
    else:
        col_tags = [
            html.Span(col, style={
                "background": "rgba(124,58,237,0.08)",
                "border": f"1px solid {PURPLE}44",
                "color": PURPLE, "fontSize": "10px", "fontWeight": "700",
                "padding": "3px 10px", "borderRadius": "12px", "marginRight": "6px",
                "marginBottom": "4px", "display": "inline-block",
                "fontFamily": "Rajdhani, monospace",
            }) for col in q_meta["cols"]
        ]
        preview = [
            html.Div([
                html.Span("📋 Expected Columns: ", style={"color": MUTED, "fontSize": "11px",
                                                            "marginRight": "8px"}),
                *col_tags,
            ], style={"display": "flex", "flexWrap": "wrap", "alignItems": "center"}),
        ]

    # ── Insight banner ────────────────────────
    insight = html.Div([
        html.Span("💡 KEY INSIGHT  ", style={
            "color": GOLD, "fontWeight": "700", "fontSize": "11px",
            "fontFamily": "Orbitron, monospace", "letterSpacing": "1px",
        }),
        html.Span(q_meta["insight"],
                  style={"color": MUTED, "fontSize": "12px"}),
    ])

    return (sidebar_btns, sidebar_stats, header_status,
            q_header, main_content, preview, insight)


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "═"*60)
    print("  🤖  AI WORKFORCE DASHBOARD  (Upload Edition)")
    print("  ▸  Open → http://127.0.0.1:8050")
    print("  ▸  Upload q1_*.csv … q8_*.csv per question")
    print("═"*60 + "\n")
    app.run(debug=False, port=8050)
