import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import json, os
from datetime import datetime, date
import calendar

st.set_page_config(page_title="Family Expense Tracker", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #faf7f2; }
h1,h2,h3 { font-family: 'Playfair Display', serif !important; color: #1a1a2e !important; }

div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%) !important;
    border-right: none !important;
}

/* Top summary cards */
.sum-card {
    background: white;
    border-radius: 20px;
    padding: 24px 20px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    border-top: 4px solid var(--accent);
    margin: 4px 0;
    transition: transform 0.2s;
}
.sum-card:hover { transform: translateY(-3px); box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
.sum-card .lbl { font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: #aaa; margin-bottom: 8px; font-family: 'DM Sans'; }
.sum-card .amt { font-family: 'Playfair Display', serif; font-size: 32px; font-weight: 700; color: #1a1a2e; }
.sum-card .sub { font-size: 12px; color: #bbb; margin-top: 4px; }

/* Category pills */
.cat-pill {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 600;
    margin: 2px;
}

/* Expense row */
.exp-row {
    background: white;
    border-radius: 14px;
    padding: 14px 18px;
    margin: 6px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    border-left: 4px solid var(--cat-color, #e2e8f0);
    transition: all 0.2s;
}
.exp-row:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.08); transform: translateX(2px); }
.exp-row .name { font-weight: 600; color: #1a1a2e; font-size: 14px; }
.exp-row .meta { color: #aaa; font-size: 12px; margin-top: 2px; }
.exp-row .amount { font-family: 'Playfair Display', serif; font-size: 18px; font-weight: 700; }

/* Section header */
.sec-head {
    font-family: 'Playfair Display', serif;
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #0f3460;
    margin: 28px 0 14px 0;
    padding-bottom: 10px;
    border-bottom: 2px solid #f0ebe3;
}

/* Input card */
.input-card {
    background: white;
    border-radius: 20px;
    padding: 28px 24px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    margin: 8px 0;
}

/* Insight box */
.insight {
    border-radius: 14px;
    padding: 16px 20px;
    margin: 8px 0;
    font-size: 13px;
    line-height: 1.7;
    border-left: 4px solid;
}
.insight-good  { background: #f0fdf4; border-color: #22c55e; color: #166534; }
.insight-warn  { background: #fffbeb; border-color: #f59e0b; color: #92400e; }
.insight-info  { background: #eff6ff; border-color: #3b82f6; color: #1e40af; }
.insight-bad   { background: #fef2f2; border-color: #ef4444; color: #991b1b; }

/* Month badge */
.month-badge {
    background: linear-gradient(135deg, #0f3460, #16213e);
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    font-family: 'Playfair Display', serif;
    font-size: 18px;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 16px;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #0f3460, #e94560) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'DM Sans' !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 12px !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s !important;
}
.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(233,69,96,0.35) !important;
}

/* Sidebar elements */
div[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
div[data-testid="stSidebar"] h1,
div[data-testid="stSidebar"] h2,
div[data-testid="stSidebar"] h3 { color: white !important; }

/* Big total banner */
.total-banner {
    background: linear-gradient(135deg, #0f3460 0%, #e94560 100%);
    border-radius: 24px;
    padding: 36px 32px;
    color: white;
    text-align: center;
    margin: 12px 0;
    position: relative;
    overflow: hidden;
}
.total-banner::before {
    content: '₹';
    position: absolute;
    font-size: 180px;
    font-family: 'Playfair Display', serif;
    opacity: 0.05;
    top: -30px; right: -10px;
    color: white;
}
.total-banner .t-label { font-size: 11px; letter-spacing: 4px; text-transform: uppercase; opacity: 0.7; margin-bottom: 8px; }
.total-banner .t-amount { font-family: 'Playfair Display', serif; font-size: 52px; font-weight: 900; }
.total-banner .t-sub { opacity: 0.6; font-size: 13px; margin-top: 8px; }

/* Savings rate circle */
.savings-ring {
    text-align: center;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────
CATEGORIES = {
    "🍛 Food & Dining":    {"color": "#f97316", "bg": "#fff7ed"},
    "🏠 Rent & Housing":   {"color": "#8b5cf6", "bg": "#f5f3ff"},
    "🚗 Transport":        {"color": "#3b82f6", "bg": "#eff6ff"},
    "💊 Health & Medical": {"color": "#ef4444", "bg": "#fef2f2"},
    "🎓 Education":        {"color": "#06b6d4", "bg": "#ecfeff"},
    "🛒 Groceries":        {"color": "#22c55e", "bg": "#f0fdf4"},
    "👗 Clothing":         {"color": "#ec4899", "bg": "#fdf2f8"},
    "📱 Bills & Utilities":{"color": "#f59e0b", "bg": "#fffbeb"},
    "🎉 Entertainment":    {"color": "#a855f7", "bg": "#faf5ff"},
    "✈️ Travel":           {"color": "#14b8a6", "bg": "#f0fdfa"},
    "💝 Family & Gifts":   {"color": "#f43f5e", "bg": "#fff1f2"},
    "📦 Other":            {"color": "#64748b", "bg": "#f8fafc"},
}

MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]

DATA_FILE = "expenses_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f: return json.load(f)
    return {"expenses": [], "budget": {}, "name": ""}

def save_data(d):
    with open(DATA_FILE, "w") as f: json.dump(d, f, indent=2)

def fmt(n):
    """Format number as Indian currency"""
    if n >= 100000: return f"₹{n/100000:.1f}L"
    if n >= 1000:   return f"₹{n/1000:.1f}K"
    return f"₹{n:,.0f}"

def get_df(data):
    if not data["expenses"]: return pd.DataFrame()
    df = pd.DataFrame(data["expenses"])
    df["date"]  = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["year"]  = df["date"].dt.year
    df["month_name"] = df["date"].dt.strftime("%B")
    df["day"]   = df["date"].dt.day
    return df

# ── Load ──────────────────────────────────────────────────────────
data = load_data()
now  = datetime.now()

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:24px 0 16px'>
        <div style='font-size:40px'>💰</div>
        <div style='font-family:Playfair Display,serif;font-size:22px;font-weight:700;color:white'>
            Expense Tracker
        </div>
        <div style='color:#64748b;font-size:12px;margin-top:4px'>Smart Money Management</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "🏠  Home",
        "➕  Add Expense",
        "📅  Monthly View",
        "📆  Yearly Report",
        "💡  Insights & Tips",
        "⚙️  Budget Settings",
    ], label_visibility="collapsed")

    st.markdown("---")
    with st.expander("👤 Profile"):
        nm = st.text_input("Your Name", value=data.get("name",""), placeholder="e.g. Ramesh Kumar")
        if st.button("Save"):
            data["name"] = nm; save_data(data); st.success("Saved!")

    dn = data.get("name") or "Friend"
    df_all = get_df(data)
    if not df_all.empty:
        total_today = df_all[df_all["date"].dt.date == date.today()]["amount"].sum()
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.05);border-radius:12px;padding:14px 16px;margin-top:8px'>
            <div style='color:#64748b;font-size:10px;letter-spacing:2px;text-transform:uppercase'>Today's Spending</div>
            <div style='font-family:Playfair Display,serif;font-size:24px;font-weight:700;color:white;margin-top:4px'>{fmt(total_today)}</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════
if "Home" in page:
    st.markdown(f"# 👋 Namaste, {dn}!")
    st.markdown(f"<div style='color:#94a3b8;margin-bottom:28px'>{now.strftime('%A, %d %B %Y')}</div>", unsafe_allow_html=True)

    df = get_df(data)
    cur_month = now.month; cur_year = now.year

    if not df.empty:
        dm = df[(df["month"]==cur_month) & (df["year"]==cur_year)]
        dy = df[df["year"]==cur_year]
        dt = df[df["date"].dt.date == date.today()]

        # Summary cards
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class='sum-card' style='--accent:#e94560'>
                <div class='lbl'>Today</div>
                <div class='amt'>{fmt(dt["amount"].sum())}</div>
                <div class='sub'>{len(dt)} transactions</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            budget_m = data.get("budget", {}).get(str(cur_month), 0)
            m_total  = dm["amount"].sum()
            pct_used = (m_total/budget_m*100) if budget_m>0 else 0
            over_col = "#ef4444" if pct_used>100 else "#e94560"
            st.markdown(f"""<div class='sum-card' style='--accent:{over_col}'>
                <div class='lbl'>This Month</div>
                <div class='amt'>{fmt(m_total)}</div>
                <div class='sub'>{"⚠️ Over budget!" if pct_used>100 else f"{pct_used:.0f}% of budget used" if budget_m>0 else f"{len(dm)} expenses"}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class='sum-card' style='--accent:#8b5cf6'>
                <div class='lbl'>This Year</div>
                <div class='amt'>{fmt(dy["amount"].sum())}</div>
                <div class='sub'>{now.strftime("%Y")} total</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            avg_daily = dm["amount"].sum() / now.day if now.day > 0 else 0
            st.markdown(f"""<div class='sum-card' style='--accent:#22c55e'>
                <div class='lbl'>Daily Average</div>
                <div class='amt'>{fmt(avg_daily)}</div>
                <div class='sub'>this month</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")
        col_l, col_r = st.columns([1.3, 1])

        with col_l:
            # Monthly total banner
            st.markdown(f"""<div class='total-banner'>
                <div class='t-label'>Total Spent — {now.strftime("%B %Y")}</div>
                <div class='t-amount'>{fmt(m_total)}</div>
                <div class='t-sub'>{len(dm)} transactions this month</div>
            </div>""", unsafe_allow_html=True)

            # Category breakdown chart
            if not dm.empty:
                st.markdown("<div class='sec-head'>This Month by Category</div>", unsafe_allow_html=True)
                cat_sum = dm.groupby("category")["amount"].sum().sort_values(ascending=True).tail(7)
                fig, ax = plt.subplots(figsize=(7, 3.5))
                fig.patch.set_facecolor('white'); ax.set_facecolor('white')
                colors = [CATEGORIES.get(c, {"color":"#64748b"})["color"] for c in cat_sum.index]
                bars = ax.barh(cat_sum.index, cat_sum.values, color=colors, height=0.55, edgecolor='none')
                ax.set_xlabel("Amount (₹)", fontsize=9, color='#94a3b8')
                ax.tick_params(colors='#475569', labelsize=9)
                [sp.set_visible(False) for sp in ax.spines.values()]
                ax.grid(axis='x', color='#f1f5f9', linewidth=1)
                for bar, val in zip(bars, cat_sum.values):
                    ax.text(bar.get_width()+max(cat_sum.values)*0.01, bar.get_y()+bar.get_height()/2,
                            fmt(val), va='center', fontsize=9, color='#475569', fontweight='600')
                plt.tight_layout(); st.pyplot(fig); plt.close()

        with col_r:
            # Recent transactions
            st.markdown("<div class='sec-head'>Recent Transactions</div>", unsafe_allow_html=True)
            recent = df.sort_values("date", ascending=False).head(8)
            for _, row in recent.iterrows():
                cat_info = CATEGORIES.get(row["category"], {"color":"#64748b","bg":"#f8fafc"})
                st.markdown(f"""
                <div class='exp-row' style='--cat-color:{cat_info["color"]}'>
                    <div>
                        <div class='name'>{row["description"]}</div>
                        <div class='meta'>{row["category"]} · {row["date"].strftime("%d %b")}</div>
                    </div>
                    <div class='amount' style='color:{cat_info["color"]}'>₹{row["amount"]:,.0f}</div>
                </div>""", unsafe_allow_html=True)

        # Budget progress bars
        if data.get("budget"):
            st.markdown("<div class='sec-head'>Budget Status This Month</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i, (month_num, bgt) in enumerate(data["budget"].items()):
                if int(month_num) == cur_month and bgt > 0:
                    spent = dm["amount"].sum()
                    pct = min(spent/bgt*100, 100)
                    bar_col = "#22c55e" if pct < 70 else "#f59e0b" if pct < 90 else "#ef4444"
                    remaining = max(bgt - spent, 0)
                    with cols[0]:
                        st.markdown(f"""
                        <div style='background:white;border-radius:16px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.06)'>
                            <div style='display:flex;justify-content:space-between;margin-bottom:8px'>
                                <span style='color:#1a1a2e;font-weight:600'>{now.strftime("%B")} Budget</span>
                                <span style='color:{bar_col};font-weight:700'>{pct:.0f}%</span>
                            </div>
                            <div style='background:#f1f5f9;border-radius:8px;height:10px'>
                                <div style='width:{pct}%;height:10px;border-radius:8px;background:linear-gradient(90deg,{bar_col}88,{bar_col})'></div>
                            </div>
                            <div style='display:flex;justify-content:space-between;margin-top:8px;font-size:12px;color:#94a3b8'>
                                <span>Spent: {fmt(spent)}</span>
                                <span>Left: {fmt(remaining)}</span>
                            </div>
                        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:white;border-radius:24px;padding:60px;text-align:center;box-shadow:0 4px 24px rgba(0,0,0,0.06)'>
            <div style='font-size:64px;margin-bottom:16px'>💸</div>
            <div style='font-family:Playfair Display,serif;font-size:24px;color:#1a1a2e;margin-bottom:8px'>No expenses yet!</div>
            <div style='color:#94a3b8'>Click "➕ Add Expense" in the sidebar to get started</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# ADD EXPENSE
# ══════════════════════════════════════════════════════════════════
elif "Add" in page:
    st.markdown("# ➕ Add Expense")
    st.markdown("<div style='color:#94a3b8;margin-bottom:24px'>Record a new expense quickly</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown("<div style='background:white;border-radius:20px;padding:28px 24px;box-shadow:0 4px 24px rgba(0,0,0,0.06)'>", unsafe_allow_html=True)
        st.markdown("<div class='sec-head' style='margin-top:0'>Expense Details</div>", unsafe_allow_html=True)

        desc = st.text_input("📝 What did you spend on?", placeholder="e.g. Lunch at Dhaba, Electricity Bill...")
        amount = st.number_input("💵 Amount (₹)", min_value=1.0, max_value=1000000.0, value=100.0, step=10.0)
        category = st.selectbox("🏷️ Category", list(CATEGORIES.keys()))
        exp_date = st.date_input("📅 Date", value=date.today())
        note = st.text_input("📌 Note (optional)", placeholder="e.g. Paid in cash, Monthly bill...")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("💾 Save Expense"):
                if desc.strip() and amount > 0:
                    entry = {
                        "id": len(data["expenses"]) + 1,
                        "description": desc.strip(),
                        "amount": float(amount),
                        "category": category,
                        "date": str(exp_date),
                        "note": note.strip()
                    }
                    data["expenses"].append(entry)
                    save_data(data)
                    st.success(f"✅ ₹{amount:,.0f} saved for '{desc}'!")
                    st.balloons()
                else:
                    st.error("Please fill description and amount.")
        with col_b2:
            if st.button("🗑️ Clear Form"):
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='sec-head'>Quick Add — Common Expenses</div>", unsafe_allow_html=True)
        quick = [
            ("☕ Morning Tea", 20, "🍛 Food & Dining"),
            ("🚌 Auto/Bus", 50, "🚗 Transport"),
            ("🛒 Vegetables", 100, "🛒 Groceries"),
            ("🍱 Lunch", 80, "🍛 Food & Dining"),
            ("💊 Medicine", 200, "💊 Health & Medical"),
            ("📱 Mobile Recharge", 299, "📱 Bills & Utilities"),
        ]
        for qname, qamt, qcat in quick:
            if st.button(f"{qname}  —  ₹{qamt}", key=f"q_{qname}"):
                data["expenses"].append({
                    "id": len(data["expenses"]) + 1,
                    "description": qname,
                    "amount": float(qamt),
                    "category": qcat,
                    "date": str(date.today()),
                    "note": "Quick add"
                })
                save_data(data)
                st.success(f"✅ Added {qname} — ₹{qamt}")
                st.rerun()

        # Today's summary
        df = get_df(data)
        if not df.empty:
            today_df = df[df["date"].dt.date == date.today()]
            if not today_df.empty:
                st.markdown("<div class='sec-head'>Today's Expenses</div>", unsafe_allow_html=True)
                for _, row in today_df.iterrows():
                    cat_info = CATEGORIES.get(row["category"], {"color":"#64748b"})
                    st.markdown(f"""<div class='exp-row' style='--cat-color:{cat_info["color"]}'>
                        <div><div class='name'>{row["description"]}</div><div class='meta'>{row["category"]}</div></div>
                        <div class='amount' style='color:{cat_info["color"]}'>₹{row["amount"]:,.0f}</div>
                    </div>""", unsafe_allow_html=True)
                st.markdown(f"""<div style='background:#0f3460;color:white;border-radius:12px;padding:12px 18px;
                    display:flex;justify-content:space-between;margin-top:8px'>
                    <span style='font-weight:600'>Today's Total</span>
                    <span style='font-family:Playfair Display,serif;font-size:18px;font-weight:700'>
                        ₹{today_df["amount"].sum():,.0f}
                    </span>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MONTHLY VIEW
# ══════════════════════════════════════════════════════════════════
elif "Monthly" in page:
    st.markdown("# 📅 Monthly View")
    df = get_df(data)

    c1, c2 = st.columns([1, 4])
    with c1:
        years = sorted(df["year"].unique().tolist(), reverse=True) if not df.empty else [now.year]
        sel_year  = st.selectbox("Year",  years)
        avail_months = sorted(df[df["year"]==sel_year]["month"].unique().tolist()) if not df.empty else [now.month]
        sel_month = st.selectbox("Month", avail_months, format_func=lambda x: MONTHS[x-1])

    if not df.empty:
        dm = df[(df["month"]==sel_month) & (df["year"]==sel_year)]

        if not dm.empty:
            st.markdown(f"<div class='month-badge'>📅 {MONTHS[sel_month-1]} {sel_year}</div>", unsafe_allow_html=True)

            # Month stats
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.markdown(f"<div class='sum-card' style='--accent:#e94560'><div class='lbl'>Total Spent</div><div class='amt'>{fmt(dm['amount'].sum())}</div><div class='sub'>{len(dm)} expenses</div></div>", unsafe_allow_html=True)
            with c2:
                top_cat = dm.groupby("category")["amount"].sum().idxmax()
                st.markdown(f"<div class='sum-card' style='--accent:#f97316'><div class='lbl'>Top Category</div><div class='amt' style='font-size:18px'>{top_cat.split()[1] if len(top_cat.split())>1 else top_cat}</div><div class='sub'>{fmt(dm.groupby('category')['amount'].sum().max())}</div></div>", unsafe_allow_html=True)
            with c3:
                days_in_month = calendar.monthrange(sel_year, sel_month)[1]
                avg_d = dm["amount"].sum() / days_in_month
                st.markdown(f"<div class='sum-card' style='--accent:#8b5cf6'><div class='lbl'>Daily Average</div><div class='amt'>{fmt(avg_d)}</div><div class='sub'>per day</div></div>", unsafe_allow_html=True)
            with c4:
                budget_m = data.get("budget",{}).get(str(sel_month),0)
                if budget_m>0:
                    saved = max(budget_m - dm["amount"].sum(), 0)
                    st.markdown(f"<div class='sum-card' style='--accent:#22c55e'><div class='lbl'>Saved</div><div class='amt'>{fmt(saved)}</div><div class='sub'>from {fmt(budget_m)} budget</div></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='sum-card' style='--accent:#22c55e'><div class='lbl'>Biggest Expense</div><div class='amt'>{fmt(dm['amount'].max())}</div><div class='sub'>{dm.loc[dm['amount'].idxmax(),'description'][:15]}</div></div>", unsafe_allow_html=True)

            st.markdown("")
            col_l, col_r = st.columns([1, 1.2])

            with col_l:
                # Pie chart
                st.markdown("<div class='sec-head'>Spending by Category</div>", unsafe_allow_html=True)
                cat_sum = dm.groupby("category")["amount"].sum().sort_values(ascending=False)
                fig, ax = plt.subplots(figsize=(5, 5))
                fig.patch.set_facecolor('white')
                colors = [CATEGORIES.get(c,{"color":"#64748b"})["color"] for c in cat_sum.index]
                wedges, texts, autotexts = ax.pie(
                    cat_sum.values, labels=None, autopct='%1.1f%%',
                    colors=colors, startangle=90,
                    wedgeprops=dict(edgecolor='white', linewidth=2.5),
                    pctdistance=0.75
                )
                for at in autotexts: at.set_fontsize(9); at.set_color('white'); at.set_fontweight('bold')
                centre = plt.Circle((0,0), 0.5, color='white')
                ax.add_patch(centre)
                ax.text(0, 0.1, fmt(dm["amount"].sum()), ha='center', va='center',
                        fontsize=16, fontweight='bold', color='#1a1a2e', fontfamily='DejaVu Serif')
                ax.text(0, -0.15, 'Total', ha='center', va='center', fontsize=10, color='#94a3b8')
                legend_labels = [f"{c.split(' ',1)[1] if ' ' in c else c} — {fmt(v)}" for c, v in zip(cat_sum.index, cat_sum.values)]
                ax.legend(wedges, legend_labels, loc='lower center', bbox_to_anchor=(0.5,-0.25),
                          ncol=2, fontsize=8, frameon=False)
                plt.tight_layout(); st.pyplot(fig); plt.close()

            with col_r:
                # Daily spending line chart
                st.markdown("<div class='sec-head'>Daily Spending Pattern</div>", unsafe_allow_html=True)
                daily = dm.groupby("day")["amount"].sum()
                all_days = pd.Series(0, index=range(1, calendar.monthrange(sel_year,sel_month)[1]+1))
                daily = (all_days + daily).fillna(0)

                fig, ax = plt.subplots(figsize=(6, 3))
                fig.patch.set_facecolor('white'); ax.set_facecolor('white')
                ax.fill_between(daily.index, daily.values, alpha=0.15, color='#e94560')
                ax.plot(daily.index, daily.values, color='#e94560', lw=2, marker='o',
                        markersize=4, markerfacecolor='white', markeredgewidth=1.5)
                ax.set_xlabel("Day of Month", fontsize=9, color='#94a3b8')
                ax.set_ylabel("₹", fontsize=9, color='#94a3b8')
                ax.tick_params(colors='#94a3b8', labelsize=8)
                [sp.set_visible(False) for sp in ax.spines.values()]
                ax.grid(axis='y', color='#f1f5f9', linewidth=1)
                avg_line = dm["amount"].sum() / calendar.monthrange(sel_year,sel_month)[1]
                ax.axhline(avg_line, color='#8b5cf6', ls='--', alpha=0.6, lw=1.2, label=f'Avg: {fmt(avg_line)}/day')
                ax.legend(fontsize=8, frameon=False)
                plt.tight_layout(); st.pyplot(fig); plt.close()

                # All expenses list
                st.markdown("<div class='sec-head'>All Transactions</div>", unsafe_allow_html=True)
                for _, row in dm.sort_values("date", ascending=False).iterrows():
                    cat_info = CATEGORIES.get(row["category"],{"color":"#64748b"})
                    st.markdown(f"""<div class='exp-row' style='--cat-color:{cat_info["color"]}'>
                        <div>
                            <div class='name'>{row["description"]}</div>
                            <div class='meta'>{row["category"]} · {row["date"].strftime("%d %b")}{" · "+row["note"] if row.get("note") else ""}</div>
                        </div>
                        <div class='amount' style='color:{cat_info["color"]}'>₹{row["amount"]:,.0f}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info(f"No expenses recorded for {MONTHS[sel_month-1]} {sel_year}.")
    else:
        st.info("No expense data yet. Add expenses first!")

# ══════════════════════════════════════════════════════════════════
# YEARLY REPORT
# ══════════════════════════════════════════════════════════════════
elif "Yearly" in page:
    st.markdown("# 📆 Yearly Report")
    df = get_df(data)

    if not df.empty:
        years = sorted(df["year"].unique().tolist(), reverse=True)
        sel_year = st.selectbox("Select Year", years)
        dy = df[df["year"]==sel_year]

        if not dy.empty:
            # Big total
            st.markdown(f"""<div class='total-banner'>
                <div class='t-label'>Total Expenditure — {sel_year}</div>
                <div class='t-amount'>{fmt(dy["amount"].sum())}</div>
                <div class='t-sub'>{len(dy)} transactions across {dy["month"].nunique()} months</div>
            </div>""", unsafe_allow_html=True)

            # Yearly cards
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.markdown(f"<div class='sum-card' style='--accent:#e94560'><div class='lbl'>Yearly Total</div><div class='amt'>{fmt(dy['amount'].sum())}</div><div class='sub'>{sel_year}</div></div>", unsafe_allow_html=True)
            with c2:
                monthly_avg = dy.groupby("month")["amount"].sum().mean()
                st.markdown(f"<div class='sum-card' style='--accent:#8b5cf6'><div class='lbl'>Monthly Average</div><div class='amt'>{fmt(monthly_avg)}</div><div class='sub'>per month</div></div>", unsafe_allow_html=True)
            with c3:
                best_month_num = dy.groupby("month")["amount"].sum().idxmin()
                st.markdown(f"<div class='sum-card' style='--accent:#22c55e'><div class='lbl'>Best Month</div><div class='amt' style='font-size:20px'>{MONTHS[best_month_num-1][:3]}</div><div class='sub'>lowest spending</div></div>", unsafe_allow_html=True)
            with c4:
                worst_month_num = dy.groupby("month")["amount"].sum().idxmax()
                st.markdown(f"<div class='sum-card' style='--accent:#ef4444'><div class='lbl'>Highest Month</div><div class='amt' style='font-size:20px'>{MONTHS[worst_month_num-1][:3]}</div><div class='sub'>most spending</div></div>", unsafe_allow_html=True)

            col_l, col_r = st.columns([1.3,1])
            with col_l:
                # Monthly bar chart
                st.markdown("<div class='sec-head'>Month-by-Month Spending</div>", unsafe_allow_html=True)
                monthly = dy.groupby("month")["amount"].sum().reindex(range(1,13), fill_value=0)
                fig, ax = plt.subplots(figsize=(8, 4))
                fig.patch.set_facecolor('white'); ax.set_facecolor('white')
                bar_colors = ['#ef4444' if m==worst_month_num else '#22c55e' if m==best_month_num else '#0f3460' for m in range(1,13)]
                bars = ax.bar([MONTHS[m-1][:3] for m in range(1,13)], monthly.values,
                              color=bar_colors, edgecolor='none', width=0.6)
                ax.tick_params(colors='#475569', labelsize=9)
                [sp.set_visible(False) for sp in ax.spines.values()]
                ax.grid(axis='y', color='#f1f5f9', linewidth=1)
                for bar, val in zip(bars, monthly.values):
                    if val > 0:
                        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(monthly.values)*0.01,
                                fmt(val), ha='center', fontsize=7.5, color='#475569', fontweight='600')
                red_patch = mpatches.Patch(color='#ef4444', label='Highest')
                green_patch = mpatches.Patch(color='#22c55e', label='Lowest')
                ax.legend(handles=[red_patch,green_patch], fontsize=8, frameon=False)
                plt.tight_layout(); st.pyplot(fig); plt.close()

            with col_r:
                # Category donut
                st.markdown("<div class='sec-head'>Category Breakdown</div>", unsafe_allow_html=True)
                cat_y = dy.groupby("category")["amount"].sum().sort_values(ascending=False).head(8)
                fig, ax = plt.subplots(figsize=(5,4))
                fig.patch.set_facecolor('white')
                colors = [CATEGORIES.get(c,{"color":"#64748b"})["color"] for c in cat_y.index]
                ax.pie(cat_y.values, labels=None, colors=colors, startangle=90,
                       wedgeprops=dict(edgecolor='white',linewidth=2), autopct='%1.0f%%',
                       pctdistance=0.78)
                centre = plt.Circle((0,0),0.55,color='white')
                ax.add_patch(centre)
                ax.text(0,0.08,fmt(dy["amount"].sum()),ha='center',va='center',
                        fontsize=14,fontweight='bold',color='#1a1a2e',fontfamily='DejaVu Serif')
                ax.text(0,-0.12,'Total',ha='center',va='center',fontsize=9,color='#94a3b8')
                plt.tight_layout(); st.pyplot(fig); plt.close()

                # Top categories list
                for cat, amt in cat_y.items():
                    pct = amt / dy["amount"].sum() * 100
                    col = CATEGORIES.get(cat,{"color":"#64748b"})["color"]
                    st.markdown(f"""<div style='display:flex;justify-content:space-between;align-items:center;
                        padding:8px 0;border-bottom:1px solid #f1f5f9'>
                        <span style='font-size:13px;color:#475569'>{cat}</span>
                        <span style='font-weight:700;color:{col}'>{fmt(amt)} <span style='color:#cbd5e1;font-weight:400'>({pct:.0f}%)</span></span>
                    </div>""", unsafe_allow_html=True)
    else:
        st.info("No expenses yet!")

# ══════════════════════════════════════════════════════════════════
# INSIGHTS & TIPS
# ══════════════════════════════════════════════════════════════════
elif "Insights" in page:
    st.markdown("# 💡 Insights & Savings Tips")
    df = get_df(data)

    if not df.empty:
        cur_month = now.month; cur_year = now.year
        dm = df[(df["month"]==cur_month) & (df["year"]==cur_year)]
        dy = df[df["year"]==cur_year]

        if not dm.empty:
            # Auto insights
            st.markdown("<div class='sec-head'>Smart Insights This Month</div>", unsafe_allow_html=True)

            top_cat = dm.groupby("category")["amount"].sum().idxmax()
            top_amt = dm.groupby("category")["amount"].sum().max()
            total_m = dm["amount"].sum()
            top_pct = top_cat / total_m * 100 if total_m > 0 else 0

            st.markdown(f"<div class='insight insight-info'>📊 Your biggest spending category this month is <b>{top_cat}</b> at <b>{fmt(top_amt)}</b> ({top_amt/total_m*100:.0f}% of total spending).</div>", unsafe_allow_html=True)

            food_spend = dm[dm["category"]=="🍛 Food & Dining"]["amount"].sum()
            if food_spend > total_m * 0.35:
                st.markdown(f"<div class='insight insight-warn'>🍛 You're spending <b>{fmt(food_spend)}</b> on food this month — that's <b>{food_spend/total_m*100:.0f}%</b> of your budget. Try cooking at home more often to save ₹3,000–5,000/month!</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='insight insight-good'>✅ Food spending is under control at {food_spend/total_m*100:.0f}% of total. Great discipline!</div>", unsafe_allow_html=True)

            budget_m = data.get("budget",{}).get(str(cur_month),0)
            if budget_m > 0:
                remaining = budget_m - total_m
                if remaining < 0:
                    st.markdown(f"<div class='insight insight-bad'>🚨 You've exceeded your budget by <b>{fmt(abs(remaining))}</b>! Avoid non-essential spending for the rest of the month.</div>", unsafe_allow_html=True)
                elif remaining < budget_m * 0.15:
                    st.markdown(f"<div class='insight insight-warn'>⚠️ Only <b>{fmt(remaining)}</b> left in your budget ({remaining/budget_m*100:.0f}%). Be careful with spending.</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='insight insight-good'>💚 You have <b>{fmt(remaining)}</b> remaining in budget. On track!</div>", unsafe_allow_html=True)

            # Daily average vs last month
            if now.month > 1:
                prev = df[(df["month"]==cur_month-1) & (df["year"]==cur_year)]
                if not prev.empty:
                    curr_daily = total_m / now.day
                    prev_daily = prev["amount"].sum() / calendar.monthrange(cur_year,cur_month-1)[1]
                    diff = ((curr_daily - prev_daily)/prev_daily*100) if prev_daily>0 else 0
                    if diff > 10:
                        st.markdown(f"<div class='insight insight-warn'>📈 Daily spending is <b>{diff:.0f}% higher</b> than last month ({fmt(curr_daily)}/day vs {fmt(prev_daily)}/day). Review your recent expenses.</div>", unsafe_allow_html=True)
                    elif diff < -10:
                        st.markdown(f"<div class='insight insight-good'>📉 Daily spending is <b>{abs(diff):.0f}% lower</b> than last month. Excellent savings habit! 🎉</div>", unsafe_allow_html=True)

        # Savings tips
        st.markdown("<div class='sec-head'>💰 Money Saving Tips</div>", unsafe_allow_html=True)
        tips = [
            ("🛒 Groceries", "Buy groceries weekly not daily. Plan meals in advance. Buy from local sabzi mandi instead of supermarkets — saves 20–30%."),
            ("🍛 Food", "Cook at home at least 5 days/week. One home-cooked meal saves ₹80–150 compared to eating out."),
            ("📱 Bills", "Switch to annual plans for OTT/subscriptions — typically 30–40% cheaper than monthly billing."),
            ("🚗 Transport", "Use public transport or carpool for regular commutes. Save ₹2,000–5,000/month vs daily auto/cab."),
            ("💊 Health", "Get a health insurance policy — it covers big medical expenses and premiums are tax deductible."),
            ("🏠 Utilities", "Turn off lights/AC when not in room. Use 5-star rated appliances. Can save ₹500–1,500/month on electricity."),
        ]
        c1, c2 = st.columns(2)
        for i, (cat, tip) in enumerate(tips):
            with (c1 if i%2==0 else c2):
                st.markdown(f"""<div style='background:white;border-radius:16px;padding:18px 20px;
                    margin:8px 0;box-shadow:0 2px 12px rgba(0,0,0,0.05);border-left:4px solid {list(CATEGORIES.values())[i]["color"]}'>
                    <div style='font-weight:700;color:#1a1a2e;margin-bottom:6px'>{cat}</div>
                    <div style='color:#64748b;font-size:13px;line-height:1.6'>{tip}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("Add expenses first to get personalised insights!")

# ══════════════════════════════════════════════════════════════════
# BUDGET SETTINGS
# ══════════════════════════════════════════════════════════════════
elif "Budget" in page:
    st.markdown("# ⚙️ Budget Settings")
    st.markdown("<div style='color:#94a3b8;margin-bottom:24px'>Set monthly spending limits to track how well you stay on budget</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("<div class='sec-head'>Set Monthly Budgets</div>", unsafe_allow_html=True)
        st.markdown("<div style='background:white;border-radius:20px;padding:24px;box-shadow:0 4px 24px rgba(0,0,0,0.06)'>", unsafe_allow_html=True)
        new_budgets = {}
        for i, month in enumerate(MONTHS, 1):
            cur = data.get("budget", {}).get(str(i), 0)
            val = st.number_input(f"{month}", min_value=0, max_value=1000000, value=int(cur), step=500, key=f"b{i}")
            new_budgets[str(i)] = val
        if st.button("💾 Save All Budgets"):
            data["budget"] = new_budgets; save_data(data); st.success("✅ Budgets saved!")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='sec-head'>Budget vs Actual</div>", unsafe_allow_html=True)
        df = get_df(data)
        if not df.empty and data.get("budget"):
            for i, month in enumerate(MONTHS, 1):
                bgt = data["budget"].get(str(i), 0)
                if bgt > 0:
                    spent = df[(df["month"]==i) & (df["year"]==now.year)]["amount"].sum()
                    pct = min(spent/bgt*100, 100) if bgt>0 else 0
                    bar_col = "#22c55e" if pct<70 else "#f59e0b" if pct<90 else "#ef4444"
                    remaining = max(bgt-spent, 0)
                    status = "✅ On track" if pct<70 else "⚠️ Watch out" if pct<90 else "🚨 Over budget"
                    st.markdown(f"""<div style='background:white;border-radius:14px;padding:14px 18px;
                        margin:6px 0;box-shadow:0 2px 12px rgba(0,0,0,0.04)'>
                        <div style='display:flex;justify-content:space-between;margin-bottom:8px'>
                            <span style='font-weight:600;color:#1a1a2e'>{month}</span>
                            <span style='font-size:12px;color:{bar_col}'>{status}</span>
                        </div>
                        <div style='background:#f1f5f9;border-radius:6px;height:8px'>
                            <div style='width:{pct:.0f}%;height:8px;border-radius:6px;background:{bar_col}'></div>
                        </div>
                        <div style='display:flex;justify-content:space-between;margin-top:6px;font-size:11px;color:#94a3b8'>
                            <span>Spent: {fmt(spent)}</span>
                            <span>Budget: {fmt(bgt)}</span>
                            <span style='color:{bar_col}'>Left: {fmt(remaining)}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Set budgets on the left and add expense data to see comparison.")

        # Delete data option
        st.markdown("<div class='sec-head'>Danger Zone</div>", unsafe_allow_html=True)
        with st.expander("🗑️ Delete Data"):
            st.warning("This will permanently delete all expenses!")
            if st.button("🗑️ Delete ALL Expenses"):
                data["expenses"] = []; save_data(data); st.success("All expenses deleted."); st.rerun()
