"""
Shared CSS design system + UI helpers — AgriShield-TN.
Clean, modern AI product interface with minimal sidebar.
"""
import sys
from pathlib import Path

_SHARED_FILE  = Path(__file__).resolve()
_APP_DIR      = _SHARED_FILE.parent
_PROJECT_ROOT = _APP_DIR.parent

for _p in [str(_PROJECT_ROOT), str(_APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN SYSTEM CSS
# ─────────────────────────────────────────────────────────────────────────────

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+Tamil:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');

/* ── Tokens ─────────────────────────────────────────────────────────────── */
:root {
  --bg-page    : #F7F9F7;
  --bg-surface : #FFFFFF;
  --bg-raised  : #F3F5F3;
  --bg-sunken  : #F8FAF8;

  --green-950 : #052e16;
  --green-900 : #14532d;
  --green-800 : #166534;
  --green-700 : #15803d;
  --green-600 : #16a34a;
  --green-500 : #22c55e;
  --green-400 : #4ade80;
  --green-100 : #dcfce7;
  --green-50  : #f0fdf4;

  --text-900  : #111827;
  --text-700  : #1F2937;
  --text-600  : #374151;
  --text-500  : #4B5563;
  --text-400  : #6B7280;
  --text-300  : #9CA3AF;
  --text-200  : #D1D5DB;

  --border     : #E5E7EB;
  --border-soft: #F3F4F6;

  --shadow-xs : 0 1px 2px rgba(0,0,0,.04);
  --shadow-sm : 0 1px 4px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.03);
  --shadow-md : 0 4px 14px rgba(0,0,0,.07), 0 2px 4px rgba(0,0,0,.03);
  --shadow-lg : 0 8px 24px rgba(0,0,0,.09), 0 3px 8px rgba(0,0,0,.04);
  --shadow-xl : 0 20px 48px rgba(0,0,0,.11), 0 8px 16px rgba(0,0,0,.05);
  --shadow-green   : 0 4px 14px rgba(22,163,74,.28);
  --shadow-green-lg: 0 8px 28px rgba(22,163,74,.42);

  --font-sans : 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono : 'Courier New', monospace;

  --r-sm  :  6px;
  --r-md  : 10px;
  --r-lg  : 14px;
  --r-xl  : 18px;
  --r-2xl : 24px;
  --r-pill: 999px;

  --t-fast: 0.14s cubic-bezier(.4,0,.2,1);
  --t-med : 0.22s cubic-bezier(.4,0,.2,1);
}

/* ── Animations ──────────────────────────────────────────────────────────── */
@keyframes fadeUp    { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn    { from{opacity:0} to{opacity:1} }
@keyframes float     { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
@keyframes pulse     { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.82)} }
@keyframes shimmer   { 0%{background-position:-200% center} 100%{background-position:200% center} }
@keyframes scanPulse { 0%,100%{opacity:1} 50%{opacity:.35} }
@keyframes scanBeam  { 0%{top:0;opacity:1} 90%{top:100%;opacity:1} 100%{top:100%;opacity:0} }
@keyframes glowPulse { 0%,100%{box-shadow:0 0 18px rgba(22,163,74,.4)} 50%{box-shadow:0 0 36px rgba(22,163,74,.7)} }
@keyframes fillBar   { to { width: 87%; } }
@keyframes orbDrift  { 0%,100%{transform:translate(0,0) scale(1)} 33%{transform:translate(24px,-18px) scale(1.05)} 66%{transform:translate(-16px,12px) scale(.96)} }
@keyframes iconFloat { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-9px)} }

/* ── Hero entrance animations ────────────────────────────────────────────── */
@keyframes heroBadge { from{opacity:0;transform:translateY(-10px) scale(.96)} to{opacity:1;transform:translateY(0) scale(1)} }
@keyframes heroTitle { from{opacity:0;transform:translateY(28px)} to{opacity:1;transform:translateY(0)} }
@keyframes heroSub   { from{opacity:0;transform:translateY(18px)} to{opacity:1;transform:translateY(0)} }
@keyframes heroFlow  { from{opacity:0;transform:translateY(22px)} to{opacity:1;transform:translateY(0)} }
@keyframes heroCta   { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
@keyframes heroPills { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }
@keyframes dotBlink  { 0%,100%{opacity:1} 50%{opacity:.28} }
@keyframes radialGlow{ 0%,100%{opacity:.7;transform:translateX(-50%) scale(1)} 50%{opacity:1;transform:translateX(-50%) scale(1.1)} }

/* ── Farmer & field animations ───────────────────────────────────────────── */
@keyframes farmerWalk { from{left:-140px} to{left:calc(100% + 140px)} }
@keyframes farmerBob  { 0%,100%{transform:translateY(0)} 25%{transform:translateY(-8px)} 75%{transform:translateY(-4px)} }
@keyframes grassSway  { 0%,100%{transform:rotate(-5deg)} 50%{transform:rotate(5deg)} }
@keyframes birdFly    { from{left:-80px;top:18%} 40%{top:13%} 70%{top:16%} to{left:calc(100% + 80px);top:15%} }
@keyframes fpSunGlow  { 0%,100%{filter:drop-shadow(0 0 14px rgba(255,200,50,.6)) drop-shadow(0 0 36px rgba(255,150,30,.3))} 50%{filter:drop-shadow(0 0 28px rgba(255,220,60,1)) drop-shadow(0 0 60px rgba(255,170,50,.6))} }
@keyframes cloudDrift { 0%,100%{transform:translateX(0)} 50%{transform:translateX(22px)} }
@keyframes firefly    { 0%,100%{opacity:0;transform:translateY(0) scale(1)} 30%,70%{opacity:.8} 50%{opacity:1;transform:translateY(-16px) scale(1.3)} }
@keyframes farmerPanelBob { 0%,100%{transform:translateY(0) scale(1)} 50%{transform:translateY(-12px) scale(1.02)} }

/* ── Streamlit theme variable override (sets sidebar bg via CSS custom prop) ── */
:root {
  --secondary-background-color: #0B1A0D !important;
  --sidebar-background-color  : #0B1A0D !important;
}

/* ── Base ────────────────────────────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
  background : var(--bg-page) !important;
  font-family: var(--font-sans) !important;
  color      : var(--text-900) !important;
  -webkit-font-smoothing: antialiased !important;
}
[data-testid="block-container"] {
  padding  : 0 clamp(1.5rem, 3vw, 3rem) 4rem !important;
  max-width: 1140px !important;
}

/* ── Header: transparent background, natural height so expand button works ── */
[data-testid="stHeader"] {
  background    : transparent !important;
  box-shadow    : none !important;
  border-bottom : none !important;
}

/* ── Hide nav dots, toolbar, decoration — leave expand/collapse buttons ── */
[data-testid="stTopNavigation"],
[data-testid="stTopNavigation"] *,
[data-testid="stNavBar"],
[data-testid="stNavBarItem"],
[data-testid="stPageNavItem"],
nav[data-testid="stTopNavigation"],
section[data-testid="stSidebarNav"],
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"],
[role="navigation"],
[class*="st-emotion-cache"][role="navigation"] { display: none !important; }
/* Only hide stPageLink inside Streamlit's OWN nav containers, not our header */
[data-testid="stTopNavigation"] [data-testid="stPageLink"],
[data-testid="stNavBar"] [data-testid="stPageLink"],
[data-testid="stSidebarNav"] [data-testid="stPageLink"] { display: none !important; }

/* ── Sidebar collapse button (inside the open sidebar) ──────────────── */
[data-testid="stSidebarCollapseButton"] {
  visibility     : visible !important;
  display        : flex !important;
  opacity        : 1 !important;
  pointer-events : auto !important;
}
[data-testid="stSidebarCollapseButton"] button {
  background    : rgba(22,163,74,.15) !important;
  border        : 1px solid rgba(22,163,74,.35) !important;
  border-radius : 8px !important;
  color         : #22c55e !important;
}

/* ── Sidebar expand button (renders in header when sidebar is collapsed) ── */
[data-testid="stSidebarCollapsedControl"],
button[data-testid="collapsedControl"] {
  visibility     : visible !important;
  display        : flex !important;
  opacity        : 1 !important;
  pointer-events : auto !important;
}
[data-testid="stSidebarCollapsedControl"] button,
button[data-testid="collapsedControl"] {
  background    : rgba(22,163,74,.18) !important;
  border        : 1.5px solid rgba(22,163,74,.45) !important;
  border-radius : 8px !important;
  color         : #22c55e !important;
  width         : 36px !important;
  height        : 36px !important;
}

[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] { display: none !important; }

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar       { width: 4px; background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(22,163,74,.2); border-radius: 999px; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  SIDEBAR                                                                    */
/* ─────────────────────────────────────────────────────────────────────────── */
/* Sidebar background — wildcard catches any Streamlit version's testid variant */
[data-testid*="Sidebar"],
[data-testid*="Sidebar"] > div,
[data-testid*="Sidebar"] > div > div,
[data-testid*="Sidebar"] > div > div > div {
  background-color : #0B1A0D !important;
  background       : #0B1A0D !important;
}
[data-testid="stSidebar"] {
  border-right: 1px solid rgba(34,197,94,.1) !important;
  min-width   : 224px !important;
  max-width   : 224px !important;
  box-shadow  : 2px 0 16px rgba(0,0,0,.2) !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding       : 0 !important;
  padding-bottom: 96px !important;
  overflow-y    : auto !important;
}

/* Nav buttons — inactive */
section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
  background     : transparent !important;
  border         : none !important;
  border-radius  : 10px !important;
  color          : rgba(255,255,255,.48) !important;
  font-size      : 0.875rem !important;
  font-weight    : 500 !important;
  padding        : 10px 14px !important;
  text-align     : left !important;
  justify-content: flex-start !important;
  box-shadow     : none !important;
  margin-bottom  : 2px !important;
  width          : 100% !important;
  line-height    : 1.4 !important;
  transition     : all 0.16s ease !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
  background : rgba(34,197,94,.1) !important;
  color      : rgba(255,255,255,.88) !important;
  transform  : translateX(2px) !important;
  box-shadow : none !important;
  filter     : none !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button:active {
  background: rgba(34,197,94,.18) !important;
  filter    : none !important;
  transform : translateX(2px) !important;
}

/* Active nav item */
.sb-nav-active {
  display       : flex;
  align-items   : center;
  gap           : 8px;
  padding       : 10px 14px 10px 11px;
  border-radius : 10px;
  background    : rgba(34,197,94,.14);
  border-left   : 3px solid #22c55e;
  color         : #ffffff;
  font-size     : 0.875rem;
  font-weight   : 700;
  margin-bottom : 2px;
  cursor        : default;
  line-height   : 1.4;
}

[data-testid="stSidebarCollapseButton"] button,
button[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
  background    : rgba(22,163,74,.12) !important;
  border        : 1px solid rgba(22,163,74,.25) !important;
  border-radius : 8px !important;
  color         : #22c55e !important;
}

/* Sidebar Radio Selector */
div[data-testid="stSidebarUserContent"] [data-testid="stWidgetLabel"] {
  display: none !important;
}
div[data-testid="stSidebarUserContent"] [data-testid="stRadio"] > div {
  gap: 4px !important;
}
div[data-testid="stSidebarUserContent"] [data-testid="stRadio"] label {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 8px !important;
  padding: 8px 12px !important;
  color: rgba(255,255,255,0.88) !important;
  transition: all 0.2s ease !important;
  font-size: 0.85rem !important;
}
div[data-testid="stSidebarUserContent"] [data-testid="stRadio"] label:hover {
  background: rgba(34,197,94,0.1) !important;
  color: rgba(255,255,255,0.9) !important;
}
div[data-testid="stSidebarUserContent"] [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
  display: none !important; /* Hide the native circle */
}
div[data-testid="stSidebarUserContent"] [data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
  color: inherit !important;
  font-weight: 500 !important;
}
/* Selected state */
div[data-testid="stSidebarUserContent"] [data-testid="stRadio"] label:has(input:checked) {
  background: rgba(34,197,94,0.18) !important;
  border-color: rgba(34,197,94,0.4) !important;
  color: #22c55e !important;
}

/* ── Main Area (Top Header) Radio Selector ────────────────────────────── */

/* Container: soft green-tinted background for clarity */
.top-lang-wrapper {
  background: rgba(46,125,50,0.06) !important;
  border-radius: 12px !important;
  padding: 6px 12px !important;
  display: inline-flex !important;
  align-items: center !important;
}

/* Row layout with spacing */
.top-lang-wrapper [data-testid="stRadio"] > div,
.top-lang-wrapper [data-testid="stRadio"] [role="radiogroup"] {
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  gap: 8px !important;
  justify-content: flex-end !important;
  align-items: center !important;
}

/* Each option pill */
.top-lang-wrapper [data-testid="stRadio"] label {
  background: rgba(255,255,255,0.85) !important;
  border: 1.5px solid #d1d5db !important;
  border-radius: 8px !important;
  padding: 5px 14px !important;
  min-height: auto !important;
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  cursor: pointer !important;
  transition: background 0.18s ease, border-color 0.18s ease !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
}

/* Unselected label text — dark, high-contrast */
.top-lang-wrapper [data-testid="stRadio"] label p,
.top-lang-wrapper [data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p,
.top-lang-wrapper [data-testid="stRadio"] label span,
.top-lang-wrapper [data-testid="stRadio"] label * {
  color: #111827 !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1.4 !important;
  font-family: 'Inter', 'Noto Sans Tamil', 'Noto Sans Devanagari', sans-serif !important;
}

/* Unselected dot */
.top-lang-wrapper [data-testid="stRadio"] label div[data-baseweb="radio"] {
  border-width: 2px !important;
  border-color: #4B5563 !important;
  flex-shrink: 0 !important;
}

/* Hover state */
.top-lang-wrapper [data-testid="stRadio"] label:hover {
  background: rgba(46,125,50,0.10) !important;
  border-color: rgba(46,125,50,0.3) !important;
}
.top-lang-wrapper [data-testid="stRadio"] label:hover p,
.top-lang-wrapper [data-testid="stRadio"] label:hover div[data-testid="stMarkdownContainer"] p,
.top-lang-wrapper [data-testid="stRadio"] label:hover * {
  color: #1B4332 !important;
}

/* Selected option — green fill */
.top-lang-wrapper [data-testid="stRadio"] label:has(input:checked) {
  background: #16a34a !important;
  border-color: #15803d !important;
  box-shadow: 0 2px 8px rgba(22,163,74,0.35) !important;
}
.top-lang-wrapper [data-testid="stRadio"] label:has(input:checked) p,
.top-lang-wrapper [data-testid="stRadio"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p,
.top-lang-wrapper [data-testid="stRadio"] label:has(input:checked) * {
  color: #ffffff !important;
  font-weight: 700 !important;
}

/* Selected dot */
.top-lang-wrapper [data-testid="stRadio"] label:has(input:checked) div[data-baseweb="radio"] {
  border-color: #2E7D32 !important;
}
.top-lang-wrapper [data-testid="stRadio"] label div[data-baseweb="radio"] div:nth-child(2) {
  background: #2E7D32 !important;
}

/* Fallback: any radio in stMain gets dark text */
div[data-testid="stMain"] [data-testid="stRadio"] label p,
div[data-testid="stMain"] [data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
  color: #1B4332 !important;
  margin: 0 !important;
  padding: 0 !important;
  font-weight: 500 !important;
  font-size: 15px !important;
}

/* Tight group spacing */
div[data-testid="stMain"] [data-testid="stRadio"] [role="radiogroup"] {
  gap: 8px !important;
}
div[data-testid="stMain"] [data-testid="stRadio"] [role="radiogroup"] > div {
  margin-right: 0 !important;
}

/* ─────────────────────────────────────────────────────────────────────────── */
/*  FILE UPLOADER                                                              */
/* ─────────────────────────────────────────────────────────────────────────── */
[data-testid="stFileUploader"]         { background: transparent !important; border: none !important; padding: 0 !important; }
[data-testid="stFileUploaderDropzone"] { background: transparent !important; border: none !important; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  GLOBAL BUTTONS                                                             */
/* ─────────────────────────────────────────────────────────────────────────── */
div[data-testid="stButton"] > button {
  background    : linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important;
  border        : none !important;
  border-radius : var(--r-pill) !important;
  color         : #fff !important;
  font-size     : 0.9375rem !important;
  font-weight   : 600 !important;
  padding       : 13px 28px !important;
  box-shadow    : var(--shadow-green) !important;
  transition    : transform var(--t-fast), box-shadow var(--t-fast), filter var(--t-fast) !important;
  width         : 100% !important;
}
div[data-testid="stButton"] > button:hover {
  transform : translateY(-2px) !important;
  box-shadow: var(--shadow-green-lg) !important;
  filter    : brightness(1.06) !important;
}
div[data-testid="stButton"] > button:active {
  transform : translateY(0) !important;
  filter    : brightness(.97) !important;
}

/* ─────────────────────────────────────────────────────────────────────────── */
/*  UTILITY                                                                    */
/* ─────────────────────────────────────────────────────────────────────────── */
.ds-divider {
  border    : none;
  height    : 1px;
  background: linear-gradient(90deg, transparent, var(--border), transparent);
  margin    : 2rem 0;
}
.spacer-xs { height: 24px; }
.spacer-sm { height: 40px; }
.spacer-md { height: 64px; }
.spacer-lg { height: 80px; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  CARDS                                                                      */
/* ─────────────────────────────────────────────────────────────────────────── */
.ds-card {
  background   : var(--bg-surface);
  border       : 1px solid var(--border);
  border-radius: var(--r-lg);
  box-shadow   : var(--shadow-sm);
  overflow     : hidden;
  position     : relative;
}
.ds-card-strip {
  position: absolute; top:0; left:0; right:0;
  height  : 3px;
  border-radius: var(--r-lg) var(--r-lg) 0 0;
}
.ds-card-hd {
  background   : var(--bg-raised);
  border-bottom: 1px solid var(--border);
  padding      : 12px 18px;
  display      : flex;
  align-items  : center;
  gap          : 10px;
}
.ds-card-bd { padding: 18px; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  PAGE HEADER                                                                */
/* ─────────────────────────────────────────────────────────────────────────── */
.ds-ph       { padding: 2.5rem 0 .5rem; }
.ds-ph-title { font-size: clamp(1.6rem,3vw,2.2rem); font-weight:800; color:var(--text-900); letter-spacing:-.8px; margin:0 0 .5rem; line-height:1.15; }
.ds-ph-sub   { font-size:.9375rem; color:var(--text-400); max-width:580px; line-height:1.65; margin:0; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  SECTION LABEL                                                              */
/* ─────────────────────────────────────────────────────────────────────────── */
.ds-lbl { font-size:.68rem; font-weight:700; letter-spacing:1.8px; text-transform:uppercase; color:var(--green-600); margin:2rem 0 .875rem; }
.ds-lbl--center { text-align:center; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  ICON TILE                                                                  */
/* ─────────────────────────────────────────────────────────────────────────── */
.ds-icon-tile {
  width:42px; height:42px; border-radius:11px;
  display:flex; align-items:center; justify-content:center;
  font-size:1.15rem; flex-shrink:0;
}

/* ─────────────────────────────────────────────────────────────────────────── */
/*  PROSE                                                                      */
/* ─────────────────────────────────────────────────────────────────────────── */
.ds-prose       { font-size:.875rem; color:var(--text-600); line-height:1.7; margin:0; }
.ds-prose-muted { font-size:.875rem; color:var(--text-400); line-height:1.7; margin:0; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  ERROR                                                                      */
/* ─────────────────────────────────────────────────────────────────────────── */
.ds-error {
  background:#fef2f2; border:1px solid #fecaca;
  border-radius:var(--r-md); padding:16px 20px;
  color:#dc2626; font-size:.9375rem; line-height:1.65;
}
.ds-error-sub { font-size:.875rem; color:#f87171; margin-top:4px; display:block; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  SCAN PANEL (Diagnose page)                                                 */
/* ─────────────────────────────────────────────────────────────────────────── */
.ds-scan {
  background:var(--bg-surface); border:1px solid var(--border);
  border-radius:var(--r-xl); padding:20px 24px 16px;
  box-shadow:var(--shadow-md); position:relative; overflow:hidden;
  font-family:var(--font-mono);
}
.ds-scan-beam {
  position:absolute; left:0; right:0; height:2px; z-index:10;
  background:linear-gradient(90deg,transparent,#22c55e,transparent);
  animation:scanBeam 1.8s ease-in-out infinite;
}
.ds-scan-header { display:flex; align-items:center; gap:12px; margin-bottom:16px; }
.ds-scan-dot    { width:8px; height:8px; border-radius:50%; background:#22c55e; flex-shrink:0; animation:scanPulse 1s infinite; }
.ds-scan-title  { font-size:.75rem; font-weight:700; color:#15803d; letter-spacing:2px; text-transform:uppercase; }
.ds-scan-ref    { margin-left:auto; font-size:.6875rem; color:var(--text-300); letter-spacing:1px; }
.ds-scan-step   { display:flex; align-items:center; gap:12px; padding:5px 0; border-bottom:1px solid #f3f4f6; font-size:.8125rem; }
.ds-scan-step:last-child { border-bottom:none; }
.ds-step-ico { width:18px; height:18px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:.6rem; flex-shrink:0; }
.ds-step-ico.done    { background:#dcfce7; color:#15803d; }
.ds-step-ico.active  { background:#f0fdf4; color:#16a34a; animation:scanPulse .7s infinite; }
.ds-step-ico.pending { background:#f3f4f6; color:var(--text-300); }
.ds-step-lbl         { flex:1; }
.ds-step-lbl.done    { color:#15803d; }
.ds-step-lbl.active  { color:var(--text-600); }
.ds-step-lbl.pending { color:var(--text-300); }
.ds-step-t           { font-size:.65rem; letter-spacing:.8px; }
.ds-step-t.done      { color:#16a34a; }
.ds-step-t.active    { color:var(--text-400); }
.ds-step-t.pending   { color:var(--border); }
.ds-scan-prog        { margin-top:16px; }
.ds-scan-prog-lbl    { display:flex; justify-content:space-between; font-size:.6875rem; color:var(--text-400); letter-spacing:.8px; margin-bottom:5px; }
.ds-scan-track       { height:4px; background:#dcfce7; border-radius:999px; overflow:hidden; }
.ds-scan-fill        { height:100%; border-radius:999px; background:linear-gradient(90deg,#166534,#22c55e); transition:width .5s cubic-bezier(.4,0,.2,1); }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  HOME — HERO  (cinematic · rice-field photo)                                */
/* ─────────────────────────────────────────────────────────────────────────── */
.hero {
  position      : relative;
  padding       : 0;
  margin        : 0;
  text-align    : center;
  overflow      : hidden;
  height        : 100vh;
  display       : flex;
  flex-direction: column;
  justify-content: center;
}

/* Layer 1 – paddy-field photo */
.hero-bg {
  position           : absolute; inset: 0;
  background-image   : url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1920&q=80');
  background-size    : cover;
  background-position: center 55%;
  filter             : brightness(.58) saturate(1.5);
  transform          : scale(1.04);
}

/* Layer 2 – dark-green overlay (lighter so field shows through) */
.hero-overlay {
  position  : absolute; inset: 0;
  background: linear-gradient(155deg,
    rgba(2,14,6,.72) 0%, rgba(3,18,8,.60) 45%, rgba(5,22,10,.50) 100%);
}

/* Layer 3 – central radial glow */
.hero-radial {
  position : absolute; top:-15%; left:50%; transform:translateX(-50%);
  width:1100px; height:720px;
  background: radial-gradient(ellipse at center,
    rgba(34,197,94,.17) 0%, rgba(22,163,74,.07) 40%, transparent 70%);
  pointer-events:none;
  animation:radialGlow 6s ease-in-out infinite;
}

/* Layer 4 – edge vignette */
.hero-vignette {
  position  : absolute; inset: 0;
  background: radial-gradient(ellipse 100% 100% at 50% 50%,
    transparent 28%, rgba(1,5,2,.68) 100%);
}

/* Ambient orbs */
.hero-orb   { position:absolute; border-radius:50%; pointer-events:none; z-index:1; }
.hero-orb-1 { top:-8%; left:-6%; width:600px; height:600px;
  background:radial-gradient(circle,rgba(22,163,74,.11) 0%,transparent 60%);
  animation:orbDrift 18s ease-in-out infinite; }
.hero-orb-2 { bottom:-12%; right:-6%; width:720px; height:720px;
  background:radial-gradient(circle,rgba(34,197,94,.08) 0%,transparent 60%);
  animation:orbDrift 24s ease-in-out infinite reverse; }
.hero-orb-3 { top:25%; left:8%; width:280px; height:280px;
  background:radial-gradient(circle,rgba(16,185,129,.07) 0%,transparent 60%);
  animation:orbDrift 30s ease-in-out infinite 5s; }

/* Content wrapper — flex-item, sits above farmer zone (200px clearance at bottom) */
.hero-inner { position:relative; z-index:10; max-width:860px; margin:0 auto; padding:40px 32px 220px; }

/* ── Hero — birds ── */
.hero-birds { position:absolute; top:0; left:0; right:0; bottom:0; z-index:4; pointer-events:none; overflow:hidden; }
.hbird { position:absolute; animation:birdFly linear infinite; }
.hbird-1 { font-size:1.1rem; opacity:.55; animation-duration:15s; animation-delay:0s; }
.hbird-2 { font-size:.85rem; opacity:.35; animation-duration:22s; animation-delay:6s; }
.hbird-3 { font-size:.75rem; opacity:.22; animation-duration:28s; animation-delay:14s; }

/* ── Hero — rice field row (bottom of hero, soft silhouette) ── */
.hero-field-row {
  position:absolute; bottom:96px; left:0; right:0; z-index:12;
  display:flex; gap:2px; padding:0 8px; align-items:flex-end;
  overflow:hidden; pointer-events:none;
}
.hstalk {
  font-size:1.6rem; display:inline-block;
  animation:grassSway ease-in-out infinite;
  transform-origin:bottom center;
  filter:brightness(.45) saturate(.6) opacity(.85);
}
.hstalk:nth-child(2n)  { animation-duration:2.4s; animation-delay:.35s; }
.hstalk:nth-child(3n)  { animation-duration:1.9s; animation-delay:.72s; }
.hstalk:nth-child(4n)  { animation-duration:2.8s; animation-delay:1.1s; }
.hstalk:nth-child(5n)  { animation-duration:2.1s; animation-delay:.55s; }
.hstalk:nth-child(6n)  { animation-duration:2.5s; animation-delay:.95s; }
.hstalk:nth-child(7n)  { animation-duration:1.8s; animation-delay:1.45s; }
.hstalk:nth-child(8n)  { animation-duration:2.3s; animation-delay:.2s; }
.hstalk:nth-child(9n)  { animation-duration:2.7s; animation-delay:1.7s; }
.hstalk:nth-child(10n) { animation-duration:2.0s; animation-delay:.6s; }

/* ── Hero — walking farmers ── */
.hero-farmers { position:absolute; bottom:102px; left:0; right:0; height:100px; z-index:13; pointer-events:none; overflow:hidden; }
.hf { position:absolute; bottom:0; animation:farmerWalk linear infinite, farmerBob ease-in-out infinite; }
.hf-1 { font-size:2.8rem; animation-duration:22s,.54s; animation-delay:0s,0s; }
.hf-2 { font-size:2rem; opacity:.72; animation-duration:30s,.47s; animation-delay:8s,.12s; }
.hf-3 { font-size:1.6rem; opacity:.45; animation-duration:38s,.41s; animation-delay:16s,.22s; }
.hf-4 { font-size:2.4rem; opacity:.88; animation-duration:25s,.50s; animation-delay:4s,.06s; }

/* ── Badge ── */
.hero-badge {
  display:inline-flex; align-items:center; gap:9px;
  background:rgba(255,255,255,.05); border:1px solid rgba(34,197,94,.32);
  border-radius:999px; padding:6px 20px; margin-bottom:14px;
  backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
  animation:heroBadge .55s .1s cubic-bezier(.22,1,.36,1) both;
}
.hero-badge-dot {
  width:7px; height:7px; border-radius:50%; background:#22c55e;
  box-shadow:0 0 0 3px rgba(34,197,94,.25), 0 0 14px rgba(34,197,94,.7);
  animation:dotBlink 2.2s ease-in-out infinite; flex-shrink:0;
}
.hero-badge-text { font-size:.7rem; font-weight:700; letter-spacing:2.2px; text-transform:uppercase; color:rgba(255,255,255,.72); }

/* ── Giant title ── */
.hero-title {
  font-size:clamp(2.6rem,6vw,5rem);
  font-weight:900; line-height:.94; letter-spacing:-2.5px;
  margin:0 0 10px; display:block;
  animation:heroTitle .7s .25s cubic-bezier(.22,1,.36,1) both;
}
.ht-agri  { color:#ffffff; }
.ht-shield {
  display:inline-block; font-size:.82em; vertical-align:middle;
  filter:drop-shadow(0 0 24px rgba(34,197,94,.95)) drop-shadow(0 0 52px rgba(34,197,94,.45));
  animation:iconFloat 4.2s ease-in-out infinite;
  margin:0 6px;
}
.ht-ield {
  background:linear-gradient(135deg,#22c55e 0%,#4ade80 45%,#86efac 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  filter:drop-shadow(0 0 24px rgba(34,197,94,.5));
}
.ht-tn { -webkit-text-fill-color:rgba(255,255,255,.28); }

/* ── Subtitle ── */
.hero-subtitle {
  font-size:1rem; font-weight:400; letter-spacing:.5px;
  color:rgba(255,255,255,.5); margin:0 0 22px;
  animation:heroSub .7s .42s cubic-bezier(.22,1,.36,1) both;
}

/* ── Detect → Analyze → Act ── */
.hero-flow {
  display:flex; align-items:center; justify-content:center; gap:0;
  margin-bottom:20px;
  animation:heroFlow .7s .56s cubic-bezier(.22,1,.36,1) both;
}
.hero-flow-step { display:flex; flex-direction:column; align-items:center; gap:8px; }
.hero-flow-icon {
  width:60px; height:60px; border-radius:50%;
  background:rgba(0,0,0,.42); border:1.5px solid rgba(34,197,94,.4);
  display:flex; align-items:center; justify-content:center; font-size:1.6rem;
  backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
  box-shadow:0 0 24px rgba(34,197,94,.24), 0 6px 28px rgba(0,0,0,.45),
             inset 0 1px 0 rgba(255,255,255,.09);
  transition:all .25s ease;
}
.hero-flow-step:nth-child(1) .hero-flow-icon { animation:iconFloat 3.4s      ease-in-out infinite; }
.hero-flow-step:nth-child(3) .hero-flow-icon { animation:iconFloat 3.4s .85s ease-in-out infinite; }
.hero-flow-step:nth-child(5) .hero-flow-icon { animation:iconFloat 3.4s 1.7s ease-in-out infinite; }
.hero-flow-icon:hover {
  background:rgba(22,163,74,.22); border-color:rgba(34,197,94,.75);
  box-shadow:0 0 44px rgba(34,197,94,.6), 0 6px 28px rgba(0,0,0,.45),
             inset 0 1px 0 rgba(255,255,255,.12);
  transform:translateY(-7px) scale(1.08);
}
.hero-flow-label { font-size:.72rem; font-weight:700; letter-spacing:.8px; color:rgba(255,255,255,.68); text-transform:uppercase; }
.hero-flow-arr   { display:flex; align-items:center; padding:0 14px 20px; color:rgba(34,197,94,.42); font-size:1.3rem; }

/* ── Feature mini-cards ── */
.hero-feats {
  display:flex; flex-wrap:nowrap; gap:7px; justify-content:center;
  animation:heroPills .7s .88s cubic-bezier(.22,1,.36,1) both;
}
.hero-feat {
  display:flex; flex-direction:column; align-items:center; gap:5px;
  border-radius:12px; padding:9px 13px; min-width:92px;
  backdrop-filter:blur(18px); -webkit-backdrop-filter:blur(18px);
  border:1px solid rgba(255,255,255,.09);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.07), 0 6px 24px rgba(0,0,0,.35);
  transition:all .22s ease; cursor:default;
}
.hero-feat:hover {
  transform:translateY(-4px); border-color:rgba(34,197,94,.5);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.12),
             0 10px 36px rgba(0,0,0,.45), 0 0 22px rgba(34,197,94,.22);
}
.hero-feat__icon { font-size:1.4rem; line-height:1; }
.hero-feat__text { font-size:.62rem; font-weight:700; color:rgba(255,255,255,.88); letter-spacing:.2px; text-align:center; line-height:1.3; }
.hero-feat--g { background:linear-gradient(150deg,rgba(20,83,45,.78),rgba(22,163,74,.48)); }
.hero-feat--p { background:linear-gradient(150deg,rgba(131,24,67,.78),rgba(219,39,119,.48)); }
.hero-feat--h { background:linear-gradient(150deg,rgba(30,58,138,.68),rgba(220,38,38,.58)); }
.hero-feat--b { background:linear-gradient(150deg,rgba(7,89,133,.75),rgba(2,132,199,.48)); }
.hero-feat--d { background:linear-gradient(150deg,rgba(8,8,14,.88),rgba(30,41,59,.68)); }
.hero-feat--a { background:linear-gradient(150deg,rgba(120,53,15,.78),rgba(217,119,6,.48)); }

/* ── Hero CTA row (inline links — no Streamlit button jank) ── */
.hero-cta-row {
  display:flex; gap:14px; justify-content:center; margin-top:22px;
  animation:heroCta .7s .72s cubic-bezier(.22,1,.36,1) both;
}
.hero-cta-btn {
  display:inline-flex; align-items:center; gap:8px;
  padding:13px 28px; border-radius:12px;
  font-size:.95rem; font-weight:700; text-decoration:none;
  transition:all .2s ease; cursor:pointer; letter-spacing:.1px;
}
.hero-cta-btn--primary {
  background:linear-gradient(135deg,#22c55e,#15803d);
  color:#fff !important;
  box-shadow:0 4px 20px rgba(34,197,94,.45);
}
.hero-cta-btn--primary:hover {
  transform:translateY(-3px);
  box-shadow:0 8px 32px rgba(34,197,94,.65);
}
.hero-cta-btn--ghost {
  background:rgba(255,255,255,.08);
  border:1px solid rgba(255,255,255,.2);
  color:rgba(255,255,255,.88) !important;
  backdrop-filter:blur(12px);
}
.hero-cta-btn--ghost:hover {
  background:rgba(255,255,255,.14);
  border-color:rgba(255,255,255,.35);
  transform:translateY(-3px);
}

/* Bottom fade into page bg */
.hero-fade {
  position:absolute; bottom:0; left:0; right:0; height:96px;
  background:linear-gradient(to bottom,transparent,#F7F9F7);
  z-index:11; pointer-events:none;
}

/* ─────────────────────────────────────────────────────────────────────────── */
/*  HOME — SECTION HEADING                                                     */
/* ─────────────────────────────────────────────────────────────────────────── */
.sec-hd        { text-align:center; margin-bottom:36px; }
.sec-hd__eye   { font-size:.68rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:#16a34a; margin-bottom:10px; }
.sec-hd__title { font-size:clamp(1.7rem,3.5vw,2.3rem); font-weight:800; color:var(--text-900); letter-spacing:-.8px; line-height:1.15; margin:0 0 12px; }
.sec-hd__sub   { font-size:.93rem; color:var(--text-400); max-width:480px; margin:0 auto; line-height:1.7; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  HOME — CAPABILITY CARDS                                                    */
/* ─────────────────────────────────────────────────────────────────────────── */
.cap-card {
  background   : var(--bg-surface);
  border       : 1px solid var(--border);
  border-radius: 18px;
  padding      : 28px 22px 24px;
  box-shadow   : var(--shadow-sm);
  transition   : transform .22s ease, box-shadow .22s ease, border-color .22s ease;
  cursor       : default;
  height       : 100%;
  position     : relative;
  overflow     : hidden;
}
.cap-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:3px;
  background:linear-gradient(90deg,var(--cap-c1,#16a34a),var(--cap-c2,#22c55e));
}
.cap-card:hover {
  transform   : translateY(-6px);
  box-shadow  : var(--shadow-lg);
  border-color: var(--cap-border,var(--border));
}
.cap-card__icon {
  width:50px; height:50px; border-radius:14px;
  display:flex; align-items:center; justify-content:center;
  font-size:1.4rem; margin-bottom:16px;
  background:var(--cap-icon-bg,#f0fdf4);
  border:1px solid var(--cap-border,#dcfce7);
}
.cap-card__title { font-size:.97rem; font-weight:800; color:var(--text-900); margin-bottom:8px; letter-spacing:-.2px; }
.cap-card__desc  { font-size:.81rem; color:var(--text-400); line-height:1.67; margin:0; }
.cap-card__tag   {
  display:inline-flex; align-items:center; margin-top:16px;
  background:var(--cap-icon-bg,#f0fdf4); border:1px solid var(--cap-border,#dcfce7);
  border-radius:999px; padding:3px 10px;
  font-size:.64rem; font-weight:700; color:var(--cap-accent,#16a34a); letter-spacing:.3px;
}

/* colour modifiers */
.cap-green  { --cap-c1:#16a34a; --cap-c2:#22c55e; --cap-icon-bg:#f0fdf4; --cap-border:#bbf7d0; --cap-accent:#16a34a; }
.cap-red    { --cap-c1:#dc2626; --cap-c2:#f87171; --cap-icon-bg:#fef2f2; --cap-border:#fecaca; --cap-accent:#dc2626; }
.cap-blue   { --cap-c1:#2563eb; --cap-c2:#60a5fa; --cap-icon-bg:#eff6ff; --cap-border:#bfdbfe; --cap-accent:#2563eb; }
.cap-amber  { --cap-c1:#d97706; --cap-c2:#fbbf24; --cap-icon-bg:#fffbeb; --cap-border:#fde68a; --cap-accent:#d97706; }
.cap-teal   { --cap-c1:#0d9488; --cap-c2:#2dd4bf; --cap-icon-bg:#f0fdfa; --cap-border:#99f6e4; --cap-accent:#0d9488; }
.cap-purple { --cap-c1:#7c3aed; --cap-c2:#a78bfa; --cap-icon-bg:#faf5ff; --cap-border:#ddd6fe; --cap-accent:#7c3aed; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  HOME — HOW IT WORKS                                                        */
/* ─────────────────────────────────────────────────────────────────────────── */
.hiw {
  background   : linear-gradient(135deg,#0a1f0d 0%,#0d2b15 50%,#081a0c 100%);
  border-radius: 24px;
  padding      : 56px 48px 60px;
  position     : relative;
  overflow     : hidden;
}
.hiw::before {
  content:''; position:absolute; inset:0;
  background-image:
    linear-gradient(rgba(34,197,94,.04) 1px,transparent 1px),
    linear-gradient(90deg,rgba(34,197,94,.04) 1px,transparent 1px);
  background-size:40px 40px; pointer-events:none;
}
.hiw-heading  { text-align:center; margin-bottom:48px; position:relative; z-index:1; }
.hiw-eyebrow  { font-size:.68rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:rgba(34,197,94,.75); margin-bottom:10px; }
.hiw-title    { font-size:clamp(1.5rem,3vw,2rem); font-weight:800; color:#fff; letter-spacing:-.8px; margin:0; }
.hiw-steps    {
  display:grid; grid-template-columns:1fr auto 1fr auto 1fr auto 1fr;
  align-items:start; position:relative; z-index:1;
}
.hiw-step       { text-align:center; transition:transform .22s ease; }
.hiw-step:hover { transform:translateY(-5px); }
.hiw-step:hover .hiw-step__orb {
  background:rgba(34,197,94,.18); border-color:rgba(34,197,94,.55);
  box-shadow:0 0 32px rgba(34,197,94,.4);
}
.hiw-step__orb {
  width:54px; height:54px; border-radius:50%;
  background:rgba(34,197,94,.09); border:1.5px solid rgba(34,197,94,.28);
  display:flex; align-items:center; justify-content:center;
  font-size:1.5rem; margin:0 auto 14px;
  box-shadow:0 0 20px rgba(34,197,94,.15);
  transition:all .22s ease;
}
.hiw-step__num  { font-size:.6rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:rgba(34,197,94,.65); margin-bottom:5px; }
.hiw-step__name { font-size:.88rem; font-weight:800; color:#fff; margin-bottom:6px; }
.hiw-step__desc { font-size:.75rem; color:rgba(255,255,255,.4); line-height:1.6; }
.hiw-arrow      { display:flex; align-items:center; justify-content:center; padding-top:22px; color:rgba(34,197,94,.32); font-size:1.3rem; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  HOME — STATS STRIP                                                         */
/* ─────────────────────────────────────────────────────────────────────────── */
.stats-strip {
  background   : linear-gradient(135deg,#f0fdf4,#dcfce7,#f0fdf4);
  border       : 1px solid #bbf7d0;
  border-radius: 22px;
  padding      : 36px 32px;
}
.stats-grid                { display:grid; grid-template-columns:repeat(4,1fr); gap:24px; text-align:center; }
.stat-cell                 { border-left:1px solid #bbf7d0; }
.stat-cell:first-child     { border-left:none; }
.stat-value                { font-size:2.2rem; font-weight:900; color:#16a34a; letter-spacing:-2px; line-height:1; }
.stat-label                { font-size:.78rem; color:#64748b; margin-top:5px; line-height:1.4; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  HOME — BOTTOM CTA                                                          */
/* ─────────────────────────────────────────────────────────────────────────── */
.btm-cta        { text-align:center; padding:72px 24px 24px; }
.btm-cta__title { font-size:clamp(1.8rem,4vw,2.8rem); font-weight:900; color:var(--text-900); letter-spacing:-1.2px; margin:0 0 14px; line-height:1.1; }
.btm-cta__sub   { font-size:.95rem; color:var(--text-400); margin:0 0 40px; }
.btm-cta__perks { display:inline-flex; align-items:center; gap:16px; flex-wrap:wrap; justify-content:center; margin-top:20px; }
.btm-cta__perk  { font-size:.75rem; color:var(--text-300); }
.btm-cta__sep   { color:var(--border); }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  DIAGNOSE PAGE                                                               */
/* ─────────────────────────────────────────────────────────────────────────── */
@keyframes pulseRing      { 0%,100%{opacity:.5;transform:scale(1)} 50%{opacity:1;transform:scale(1.1)} }
@keyframes pulseRingReady { 0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,.5)} 70%{box-shadow:0 0 0 16px rgba(34,197,94,0)} }

.diag-eyebrow {
  font-size:.72rem; font-weight:700; letter-spacing:2px; text-transform:uppercase;
  color:#16a34a; padding:2.4rem 0 1.2rem;
}

.diag-card-hd {
  font-size:.63rem; font-weight:800; letter-spacing:2.8px; text-transform:uppercase;
  color:#374151; margin-bottom:24px; padding-bottom:14px;
  border-bottom:1.5px solid #f3f4f6;
  display:flex; align-items:center; gap:10px;
}
.diag-card-hd::before {
  content:''; display:inline-block; width:4px; height:15px;
  background:linear-gradient(135deg,#16a34a,#4ade80);
  border-radius:999px; flex-shrink:0;
}

.diag-step-hd {
  display:flex; align-items:center; gap:8px;
  font-size:.63rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;
  color:#9ca3af; margin-bottom:12px;
}
.diag-step-num {
  background:#111827; color:#fff; border-radius:5px;
  padding:2px 8px; font-size:.58rem; font-weight:800; letter-spacing:1px;
}

.diag-upload-zone {
  border:2px dashed #bbf7d0; border-radius:14px; padding:14px;
  background:#fafffe; min-height:60px;
}
.diag-tip {
  font-size:.73rem; color:#9ca3af; margin-top:9px;
  display:flex; align-items:flex-start; gap:5px; line-height:1.55;
}

.diag-status-wrap {
  display:flex; flex-direction:column; align-items:center;
  justify-content:center; padding:20px 0 14px; gap:11px; text-align:center;
}
.diag-pulse-ring {
  width:84px; height:84px; border-radius:50%;
  border:2.5px solid rgba(34,197,94,.3); background:rgba(34,197,94,.06);
  display:flex; align-items:center; justify-content:center; position:relative;
  animation:pulseRing 2.4s ease-in-out infinite;
}
.diag-pulse-inner {
  font-size:2rem; position:absolute;
  top:50%; left:50%; transform:translate(-50%,-50%);
}
.diag-ready-ring {
  width:84px; height:84px; border-radius:50%;
  border:2.5px solid #22c55e; background:rgba(34,197,94,.12);
  display:flex; align-items:center; justify-content:center;
  animation:pulseRingReady 1.8s ease-in-out infinite;
}
.diag-ready-inner {
  font-size:1.7rem; color:#22c55e; font-weight:800; line-height:1;
}
.diag-status-lbl { font-size:.68rem; font-weight:800; letter-spacing:1.5px; text-transform:uppercase; color:#9ca3af; }
.diag-status-lbl--ready { color:#22c55e; }
.diag-status-sub { font-size:.72rem; color:#9ca3af; line-height:1.5; max-width:156px; }

.diag-info-box {
  background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px;
  padding:12px 14px; font-size:.75rem; color:#374151; line-height:1.7;
  margin-top:14px;
}

/* CTA big green pill */
.diag-cta-wrap { margin:20px 0 4px; }
.diag-cta-wrap div[data-testid="stButton"] > button {
  font-size:1.08rem !important; font-weight:700 !important;
  padding:17px 36px !important; letter-spacing:.4px !important;
  box-shadow:0 6px 30px rgba(22,163,74,.42) !important;
}
div[data-testid="stButton"] > button:disabled {
  background:linear-gradient(135deg,#cbd5e1,#94a3b8) !important;
  box-shadow:none !important; opacity:.7 !important;
}

/* Diagnostic parameters */
.diag-params-strip  { margin-top:18px; }
.diag-param-card {
  background:#FFFFFF; border:1px solid #e5e7eb; border-radius:16px;
  padding:22px 14px; text-align:center;
  box-shadow:0 2px 10px rgba(0,0,0,.05);
  transition:transform .2s ease, box-shadow .2s ease;
}
.diag-param-card:hover { transform:translateY(-4px); box-shadow:0 8px 24px rgba(0,0,0,.09); }
.diag-param-icon { font-size:1.5rem; margin-bottom:8px; }
.diag-param-val  { font-size:1.65rem; font-weight:900; color:#111827; line-height:1.1; }
.diag-param-lbl  { font-size:.68rem; color:#6b7280; font-weight:600; margin-top:5px; letter-spacing:.2px; }

/* ── Diagnose hero V2 (2-column with photo) ─────────────────────────────── */
@keyframes farmerSlideIn { from{opacity:0;transform:translateX(36px)} to{opacity:1;transform:translateX(0)} }
@keyframes welcomeFadeUp { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }
@keyframes riceWave { 0%,100%{transform:rotate(-3deg) translateY(0)} 50%{transform:rotate(3deg) translateY(-4px)} }

.diag-welcome { background:linear-gradient(135deg,#f0fdf4 0%,#dcfce7 60%,#bbf7d0 100%); border:1.5px solid #86efac; border-radius:24px; display:flex; align-items:stretch; min-height:190px; margin-bottom:20px; overflow:hidden; position:relative; box-shadow:0 4px 24px rgba(22,163,74,.13); }
.diag-welcome::before { content:"🌾  🌾  🌾  🌾  🌾  🌾  🌾  🌾  🌾  🌾"; position:absolute; bottom:6px; left:0; right:0; font-size:1.1rem; opacity:.12; letter-spacing:10px; text-align:center; pointer-events:none; }
.diag-welcome-text { flex:1; padding:26px 28px 22px; display:flex; flex-direction:column; justify-content:center; z-index:1; animation:welcomeFadeUp .5s ease both; }
.diag-welcome-badge { font-size:.58rem; font-weight:800; letter-spacing:2px; text-transform:uppercase; color:#16a34a; margin-bottom:10px; display:flex; align-items:center; gap:5px; }
.diag-welcome-badge-dot { width:6px; height:6px; border-radius:50%; background:#16a34a; display:inline-block; animation:pulse 2s ease-in-out infinite; }
.diag-welcome-greeting { font-size:1.8rem; font-weight:900; color:#111827; line-height:1.1; margin-bottom:5px; }
.diag-welcome-sub { font-size:.88rem; font-weight:500; color:#374151; margin-bottom:5px; line-height:1.4; }
.diag-welcome-ta { font-size:.75rem; color:#4b5563; font-family:"Noto Sans Tamil",sans-serif; line-height:1.5; }
.diag-welcome-rice { margin-top:12px; font-size:1.1rem; letter-spacing:4px; }
.diag-welcome-rice span { display:inline-block; animation:riceWave 2.5s ease-in-out infinite; }
.diag-welcome-rice span:nth-child(2) { animation-delay:.3s; }
.diag-welcome-rice span:nth-child(3) { animation-delay:.6s; }
.diag-welcome-rice span:nth-child(4) { animation-delay:.9s; }
.diag-welcome-farmer { flex:0 0 200px; display:flex; align-items:flex-end; justify-content:center; padding:0 8px 0; position:relative; z-index:1; }
.diag-welcome-farmer-img { width:190px; height:190px; object-fit:contain; animation:farmerSlideIn .65s ease both, farmerBob 3.2s .65s ease-in-out infinite; filter:drop-shadow(0 6px 18px rgba(22,163,74,.22)); }

.diag-hero-v2 { background:#052e16; border-radius:20px; overflow:hidden; display:flex; min-height:140px; margin-bottom:18px; position:relative; box-shadow:0 8px 32px rgba(5,46,22,.35); }
.diag-hero-v2-left { flex:0 0 60%; padding:26px 28px; display:flex; flex-direction:column; justify-content:center; gap:6px; z-index:1; }
.diag-hero-v2-badge { font-size:.58rem; font-weight:800; letter-spacing:2px; text-transform:uppercase; color:rgba(34,197,94,.8); margin-bottom:4px; }
.diag-hero-v2-title { font-size:1.45rem; font-weight:900; color:#fff; letter-spacing:-.5px; line-height:1.15; }
.diag-hero-v2-sub { font-size:.65rem; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; color:rgba(255,255,255,.5); }
.diag-hero-v2-ta { font-size:.72rem; color:rgba(255,255,255,.4); font-family:"Noto Sans Tamil",sans-serif; }
.diag-hero-v2-right { flex:1; background-image:url('https://images.unsplash.com/photo-1589923188651-268a99638e78?w=600&q=80&auto=format&fit=crop'); background-size:cover; background-position:center; position:relative; }
.diag-hero-v2-right::before { content:""; position:absolute; inset:0; background:linear-gradient(to right,#052e16 0%,rgba(5,46,22,.3) 55%,transparent 100%); }

/* ── Step flow strip ─────────────────────────────────────────────────────── */
.diag-steps-strip { display:flex; align-items:center; gap:0; background:#fff; border:1px solid #e5e7eb; border-radius:14px; padding:12px 20px; margin-bottom:18px; }
.diag-step-item { display:flex; align-items:center; gap:10px; flex:1; }
.diag-step-circle { width:32px; height:32px; border-radius:50%; background:#e5e7eb; color:#6b7280; font-size:.8rem; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.diag-step-text { font-size:.72rem; color:#6b7280; line-height:1.4; font-family:"Noto Sans Tamil",sans-serif; }
.diag-step-text small { font-size:.6rem; color:#9ca3af; font-family:"Inter",sans-serif; display:block; }
.diag-step-item--active .diag-step-circle { background:#16a34a; color:#fff; box-shadow:0 0 0 4px rgba(22,163,74,.2); }
.diag-step-item--active .diag-step-text { color:#111827; font-weight:600; }
.diag-step-connector { flex:0 0 28px; height:2px; background:#e5e7eb; margin:0 4px; }

/* ── Upload card ─────────────────────────────────────────────────────────── */
.diag-upload-card {
  border: 2.5px dashed #bbf7d0;
  border-radius: 18px;
  padding: 0;
  background: linear-gradient(145deg, #fafffd, #f0fdf4);
  min-height: 240px;
  position: relative;
  overflow: hidden;
  transition: border-color .25s, box-shadow .25s;
}
.diag-upload-card:hover {
  border-color: #4ade80;
  box-shadow: 0 4px 20px rgba(34,197,94,.18);
}
.diag-upload-card--filled {
  border-style: solid; border-color: #22c55e;
  background: #f0fdf4;
}
.diag-upload-placeholder {
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  padding:28px 20px 8px;
  pointer-events:none;
}
.diag-upload-big-icon {
  font-size:3.2rem;
  filter:drop-shadow(0 4px 10px rgba(22,163,74,.3));
  margin-bottom:10px;
  animation:pulseRing 3s ease-in-out infinite;
}
.diag-upload-hint-en {
  font-size:.88rem; font-weight:700; color:#374151; text-align:center; line-height:1.4;
}
.diag-upload-hint-ta {
  font-size:.78rem; color:#6b7280; font-family:"Noto Sans Tamil",sans-serif;
  text-align:center; margin-top:5px; line-height:1.5;
}
.diag-upload-formats {
  font-size:.62rem; color:#9ca3af; letter-spacing:1.5px; font-weight:700;
  text-transform:uppercase; margin-top:8px;
  background:#f3f4f6; border-radius:999px; padding:3px 12px;
}
.diag-preview-wrap { padding:8px; }
.diag-preview-badge {
  font-size:.7rem; font-weight:700; color:#16a34a;
  background:#f0fdf4; border:1px solid #bbf7d0;
  border-radius:999px; padding:3px 12px;
  margin:6px 4px 4px; display:inline-block;
}

/* ── Native file uploader dropzone styling ───────────────────────────────── */
.diag-upload-card [data-testid="stFileUploaderDropzone"] { background:linear-gradient(145deg,#fafffd,#f0fdf4) !important; border:2.5px dashed #bbf7d0 !important; border-radius:14px !important; min-height:180px !important; }
.diag-upload-card [data-testid="stFileUploaderDropzone"]:hover { border-color:#4ade80 !important; background:#f0fdf4 !important; }

/* ── Example leaf photos strip ───────────────────────────────────────────── */
.diag-examples-strip { margin-top:10px; }
.diag-ex-label { font-size:.65rem; font-weight:700; color:#9ca3af; text-transform:uppercase; letter-spacing:.8px; margin-bottom:6px; }
.diag-ex-photos { display:flex; gap:8px; }
.diag-ex-photo { flex:1; height:70px; border-radius:10px; background-size:cover; background-position:center; position:relative; overflow:hidden; }
.diag-ex-badge { position:absolute; bottom:5px; left:50%; transform:translateX(-50%); font-size:.55rem; font-weight:800; border-radius:999px; padding:2px 8px; white-space:nowrap; }
.diag-ex-badge--bad  { background:#fecaca; color:#dc2626; }
.diag-ex-badge--good { background:#bbf7d0; color:#15803d; }

/* ── Field photo header (right panel) ────────────────────────────────────── */
.diag-field-header { height:80px; border-radius:14px; background-size:cover; background-position:center; position:relative; overflow:hidden; margin-bottom:10px; }
.diag-field-header-overlay { position:absolute; bottom:0; left:0; right:0; background:linear-gradient(to top,rgba(5,46,22,.8),transparent); padding:6px 12px; font-size:.6rem; font-weight:700; color:rgba(255,255,255,.85); letter-spacing:.5px; }

/* ── Status card ─────────────────────────────────────────────────────────── */
.diag-status-card {
  background:#fff; border:1.5px solid #e5e7eb; border-radius:16px;
  padding:22px 14px; text-align:center;
  display:flex; flex-direction:column; align-items:center; gap:10px;
  margin-bottom:14px;
}
.diag-status-card--ready {
  background:#f0fdf4; border-color:#bbf7d0;
}
.diag-status-ta {
  font-size:.7rem; color:#9ca3af; font-family:"Noto Sans Tamil",sans-serif;
  margin-top:2px;
}
.diag-status-card--ready .diag-status-ta { color:#16a34a; }

/* ── Details card ────────────────────────────────────────────────────────── */
.diag-det-card {
  background:#fff; border:1.5px solid #e5e7eb; border-radius:16px;
  padding:14px 14px 4px; margin-bottom:12px;
}
.diag-det-label {
  font-size:.75rem; font-weight:700; color:#374151; margin-bottom:8px;
  display:flex; align-items:center; gap:4px;
}
.diag-det-ta { font-size:.68rem; color:#9ca3af; font-family:"Noto Sans Tamil",sans-serif; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  HOME — FARMER ILLUSTRATION PANEL                                            */
/* ─────────────────────────────────────────────────────────────────────────── */
.fp-wrap {
  background:
    linear-gradient(180deg,rgba(2,14,5,.55) 0%,rgba(4,24,8,.45) 30%,rgba(8,46,16,.4) 60%,rgba(14,76,28,.55) 80%,rgba(24,102,40,.7) 100%),
    url('https://images.unsplash.com/photo-1599790977917-b63cf93b7e59?w=800&q=75&auto=format&fit=crop') center/cover no-repeat;
  border-radius:24px; min-height:400px; position:relative; overflow:hidden;
  display:flex; flex-direction:column; align-items:center; justify-content:flex-end;
}
.fp-wrap::before {
  content:''; position:absolute; inset:0; z-index:1;
  background: linear-gradient(to top, rgba(5,46,22,.65) 0%, transparent 55%);
}
.fp-moon {
  position:absolute; top:24px; left:50%; transform:translateX(-50%);
  font-size:2.8rem; z-index:3;
  animation:fpSunGlow 5s ease-in-out infinite;
}
.fp-stars { position:absolute; top:0; left:0; right:0; z-index:2; padding:14px 20px; }
.fp-star {
  display:inline-block; font-size:.6rem; color:#fff; opacity:.7; margin:5px;
  animation:firefly ease-in-out infinite;
}
.fp-star:nth-child(2n)  { animation-duration:3.2s; animation-delay:.8s; opacity:.5; }
.fp-star:nth-child(3n)  { animation-duration:4.1s; animation-delay:1.6s; opacity:.6; }
.fp-star:nth-child(4n)  { animation-duration:2.8s; animation-delay:2.4s; opacity:.4; }
.fp-star:nth-child(5n)  { animation-duration:3.7s; animation-delay:.4s; opacity:.65; }
.fp-clouds { position:absolute; top:60px; left:0; right:0; z-index:2; display:flex; gap:20px; padding:0 20px; justify-content:space-around; }
.fp-cloud { font-size:1.3rem; opacity:.28; filter:brightness(.7); animation:cloudDrift ease-in-out infinite; }
.fp-cloud:nth-child(2) { animation-duration:9s; animation-delay:2s; opacity:.18; }
.fp-cloud:nth-child(3) { animation-duration:12s; animation-delay:4s; opacity:.22; font-size:1rem; }
.fp-farmer-fig {
  position:relative; z-index:6; font-size:7rem; line-height:1; text-align:center;
  filter:drop-shadow(0 8px 24px rgba(0,0,0,.7));
  animation:farmerPanelBob 2.8s ease-in-out infinite;
  margin-bottom:12px;
}
.fp-field-row {
  position:absolute; bottom:0; left:0; right:0; z-index:5;
  display:flex; gap:1px; padding:0 6px; align-items:flex-end; overflow:hidden;
}
.fp-stalk {
  font-size:2.5rem; display:inline-block;
  animation:grassSway ease-in-out infinite; transform-origin:bottom center;
  filter:brightness(.7) saturate(.9);
}
.fp-stalk:nth-child(2n)  { animation-duration:2.3s; animation-delay:.4s; }
.fp-stalk:nth-child(3n)  { animation-duration:1.8s; animation-delay:.85s; }
.fp-stalk:nth-child(4n)  { animation-duration:2.7s; animation-delay:1.25s; }
.fp-stalk:nth-child(5n)  { animation-duration:2.1s; animation-delay:.65s; }
.fp-stalk:nth-child(6n)  { animation-duration:2.5s; animation-delay:1.05s; }
.fp-stalk:nth-child(7n)  { animation-duration:1.7s; animation-delay:1.55s; }
.fp-stalk:nth-child(8n)  { animation-duration:2.9s; animation-delay:.25s; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  HOME — "BUILT FOR FARMERS" SECTION                                          */
/* ── Home crop photo gallery strip ──────────────────────────────────────── */
.home-crop-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 14px;
  margin: 0 0 8px;
}
.home-crop-photo {
  border-radius: 14px;
  overflow: hidden;
  border: 1.5px solid #e5e7eb;
  box-shadow: 0 2px 10px rgba(0,0,0,.06);
  transition: transform .2s, box-shadow .2s;
}
.home-crop-photo:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,.1); }
.home-crop-photo-label { padding: 8px 10px 10px; background: #fff; }

/* ─────────────────────────────────────────────────────────────────────────── */
.bff-eyebrow { font-size:.68rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:#16a34a; margin-bottom:10px; }
.bff-title { font-size:clamp(1.5rem,3vw,2.1rem); font-weight:800; color:#111827; letter-spacing:-.8px; line-height:1.2; margin:0 0 12px; }
.bff-sub { font-size:.9rem; color:#6b7280; line-height:1.75; margin:0 0 28px; }
.bff-benefit {
  background:#FFFFFF; border:1px solid #e5e7eb; border-radius:16px;
  padding:20px 22px; display:flex; gap:16px; align-items:flex-start;
  margin-bottom:14px; transition:transform .2s ease, box-shadow .2s ease, border-color .2s ease;
  box-shadow:0 2px 8px rgba(0,0,0,.04);
}
.bff-benefit:hover { transform:translateX(6px); box-shadow:0 4px 18px rgba(0,0,0,.08); border-color:#bbf7d0; }
.bff-benefit-icon { width:48px; height:48px; border-radius:12px; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:1.5rem; }
.bff-benefit-title { font-size:.95rem; font-weight:800; color:#111827; margin-bottom:5px; }
.bff-benefit-desc { font-size:.82rem; color:#6b7280; line-height:1.6; margin:0; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  HOME — IMPACT STRIP (dark)                                                  */
/* ─────────────────────────────────────────────────────────────────────────── */
.impact-strip {
  background:linear-gradient(135deg,#052e16 0%,#0a4a1e 50%,#052e16 100%);
  border-radius:24px; overflow:hidden; position:relative;
}
.impact-strip::before {
  content:''; position:absolute; inset:0;
  background-image:
    linear-gradient(rgba(34,197,94,.05) 1px,transparent 1px),
    linear-gradient(90deg,rgba(34,197,94,.05) 1px,transparent 1px);
  background-size:32px 32px; pointer-events:none;
}
.impact-grid { display:grid; grid-template-columns:repeat(4,1fr); position:relative; z-index:1; }
.impact-cell {
  padding:40px 20px; text-align:center;
  border-right:1px solid rgba(34,197,94,.12);
  transition:background .2s ease;
}
.impact-cell:last-child { border-right:none; }
.impact-cell:hover { background:rgba(34,197,94,.08); }
.impact-icon  { font-size:2rem; margin-bottom:12px; display:block; }
.impact-value { font-size:2.2rem; font-weight:900; color:#22c55e; letter-spacing:-2px; line-height:1; margin-bottom:8px; }
.impact-label { font-size:.75rem; color:rgba(255,255,255,.42); line-height:1.5; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  HOME — DISEASE PREVIEW TEASER                                               */
/* ─────────────────────────────────────────────────────────────────────────── */
.dprev-card {
  background:#FFFFFF; border:1px solid #e5e7eb; border-radius:18px;
  padding:24px 20px; transition:transform .22s ease, box-shadow .22s ease, border-color .22s ease;
  cursor:default; position:relative; overflow:hidden; height:100%;
}
.dprev-card:hover { transform:translateY(-7px); box-shadow:0 16px 40px rgba(0,0,0,.1); border-color:#bbf7d0; }
.dprev-card::before { content:''; position:absolute; top:0; left:0; right:0; height:4px; border-radius:18px 18px 0 0; }
.dprev-card--blast::before  { background:linear-gradient(90deg,#dc2626,#f87171); }
.dprev-card--blight::before { background:linear-gradient(90deg,#d97706,#fbbf24); }
.dprev-card--spot::before   { background:linear-gradient(90deg,#7c3aed,#a78bfa); }
.dprev-icon  { font-size:2.8rem; margin-bottom:14px; }
.dprev-title { font-size:1.02rem; font-weight:800; color:#111827; margin-bottom:8px; }
.dprev-sev   { display:inline-flex; align-items:center; gap:5px; font-size:.68rem; font-weight:700; border-radius:999px; padding:3px 11px; margin-bottom:13px; }
.dprev-sev--critical { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
.dprev-sev--high     { background:#fffbeb; color:#d97706; border:1px solid #fde68a; }
.dprev-sev--moderate { background:#faf5ff; color:#7c3aed; border:1px solid #ddd6fe; }
.dprev-desc  { font-size:.82rem; color:#6b7280; line-height:1.65; margin:0 0 18px; }
.dprev-link  { font-size:.78rem; font-weight:700; color:#16a34a; display:flex; align-items:center; gap:5px; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  HOME — BOTTOM CTA V2 (dark premium)                                         */
/* ─────────────────────────────────────────────────────────────────────────── */
.btm-cta-v2 {
  background:linear-gradient(135deg,#020e05 0%,#0a2e12 40%,#052014 70%,#020e05 100%);
  border-radius:28px; padding:72px 48px 64px; text-align:center;
  position:relative; overflow:hidden;
}
.btm-cta-v2::before {
  content:''; position:absolute; inset:0;
  background-image:
    linear-gradient(rgba(34,197,94,.055) 1px,transparent 1px),
    linear-gradient(90deg,rgba(34,197,94,.055) 1px,transparent 1px);
  background-size:36px 36px; pointer-events:none;
}
.btm-cta-v2::after {
  content:''; position:absolute; top:-30%; left:50%; transform:translateX(-50%);
  width:800px; height:500px;
  background:radial-gradient(ellipse at center,rgba(34,197,94,.14) 0%,transparent 65%);
  pointer-events:none;
}
.btm-cta-v2__farmer {
  font-size:4.5rem; margin-bottom:18px; display:block;
  animation:farmerPanelBob 2.5s ease-in-out infinite; position:relative; z-index:1;
  filter:drop-shadow(0 4px 16px rgba(34,197,94,.3));
}
.btm-cta-v2__title {
  font-size:clamp(2rem,4.5vw,3rem); font-weight:900; color:#fff;
  letter-spacing:-1.5px; margin:0 0 14px; line-height:1.05; position:relative; z-index:1;
}
.btm-cta-v2__title span {
  background:linear-gradient(135deg,#22c55e 0%,#4ade80 50%,#86efac 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.btm-cta-v2__sub { font-size:.96rem; color:rgba(255,255,255,.48); margin:0 0 40px; position:relative; z-index:1; }
.btm-cta-v2__perks { display:inline-flex; align-items:center; gap:24px; flex-wrap:wrap; justify-content:center; margin-top:22px; position:relative; z-index:1; }
.btm-cta-v2__perk { font-size:.76rem; color:rgba(255,255,255,.38); display:flex; align-items:center; gap:5px; }
.btm-cta-v2__perk::before { content:'✓'; color:#22c55e; font-weight:700; margin-right:3px; }

/* ─────────────────────────────────────────────────────────────────────────── */
/*  FOOTER                                                                     */
/* ─────────────────────────────────────────────────────────────────────────── */
.ds-footer {
  margin-top:3.5rem; padding:1.5rem 0 1rem;
  border-top:1px solid var(--border); text-align:center;
}
.ds-footer-brand { display:inline-flex; align-items:center; gap:7px; font-size:.875rem; font-weight:700; color:#16a34a; margin-bottom:.5rem; }
.ds-footer-note  { font-size:.74rem; color:var(--text-300); margin-top:.375rem; }

/* ── Top Header ──────────────────────────────────────────────────────────── */
.top-nav-container {
  position: absolute;
  top: -48px;
  right: 0;
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 100;
  height: 48px;
}
.top-nav-bg { display: none; }
.hnav-scope { display: none; }
.hnav-rule  { display: none; }

/* ═══════════════════════════════════════════════════════════════════════════
   FIXED HORIZONTAL NAVBAR  (single-row st.columns approach)
   Sentinel: .hnav-root inside brand column → targets stHorizontalBlock parent
   ═══════════════════════════════════════════════════════════════════════════ */
@keyframes hnavSlideDown {
  from { opacity: 0; transform: translateY(-64px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes hnavLinkGlow {
  0%,100% { box-shadow: 0 0 0 rgba(34,197,94,0); }
  50%      { box-shadow: 0 0 12px rgba(34,197,94,.4); }
}

/* ── The columns row becomes the fixed navbar ─────────────────────────────── */
.hnav-root { display: none !important; }

[data-testid="stHorizontalBlock"]:has(.hnav-root) {
  position         : fixed !important;
  top              : 0 !important;
  left             : 0 !important;
  right            : 0 !important;
  z-index          : 9000 !important;
  height           : 64px !important;
  background       : rgba(5, 30, 14, 0.96) !important;
  backdrop-filter  : blur(18px) !important;
  -webkit-backdrop-filter: blur(18px) !important;
  border-bottom    : 1px solid rgba(34,197,94,.2) !important;
  box-shadow       : 0 4px 28px rgba(0,0,0,.35) !important;
  animation        : hnavSlideDown .4s cubic-bezier(.22,.61,.36,1) both !important;
  padding          : 0 32px !important;
  align-items      : center !important;
  gap              : 4px !important;
}

/* Strip all inner padding / borders from every column wrapper inside navbar */
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"] {
  display         : flex !important;
  align-items     : center !important;
  padding         : 0 !important;
  gap             : 0 !important;
}
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  [data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  [data-testid="stVerticalBlockBorderWrapper"] {
  padding : 0 !important;
  gap     : 0 !important;
  border  : none !important;
  width   : 100% !important;
}

/* ── Brand ──────────────────────────────────────────────────────────────── */
.hnav-brand {
  display         : flex;
  align-items     : center;
  gap             : 10px;
  text-decoration : none;
  white-space     : nowrap;
}
.hnav-brand-logo { font-size: 1.3rem; line-height: 1; }
.hnav-brand-text { display: flex; flex-direction: column; line-height: 1; }
.hnav-brand-name { font-size: .88rem; font-weight: 800; color: #fff; letter-spacing: -.3px; }
.hnav-tn         { color: #22c55e; }
.hnav-brand-sub  { font-size: .54rem; color: rgba(255,255,255,.38); letter-spacing: .3px; margin-top: 1px; }

/* ── Nav buttons (st.button inside nav columns 2-5) ─────────────────────── */

/* Make stHeader pointer-events:none so it never intercepts navbar clicks */
[data-testid="stHeader"] { pointer-events: none !important; }
[data-testid="stHeader"] * { pointer-events: none !important; }

/* Strip Streamlit's default button chrome inside the navbar */
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"]:not(:first-child):not(:last-child)
  [data-testid="stBaseButton-secondary"],
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"]:not(:first-child):not(:last-child)
  [data-testid="stButton"] {
  width: 100% !important;
}

[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"]:not(:first-child):not(:last-child)
  button {
  background      : transparent !important;
  border          : 1px solid transparent !important;
  border-radius   : 9px !important;
  padding         : 7px 14px !important;
  color           : rgba(255,255,255,.72) !important;
  font-size       : .8rem !important;
  font-weight     : 600 !important;
  width           : 100% !important;
  min-height      : 36px !important;
  white-space     : nowrap !important;
  box-shadow      : none !important;
  cursor          : pointer !important;
  transition      : background .17s, border-color .17s, color .17s, transform .14s !important;
  line-height     : 1 !important;
}
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"]:not(:first-child):not(:last-child)
  button:hover {
  background   : rgba(34,197,94,.15) !important;
  border-color : rgba(34,197,94,.45) !important;
  color        : #4ade80             !important;
  transform    : scale(1.04)         !important;
}
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"]:not(:first-child):not(:last-child)
  button:active { transform: scale(0.97) !important; }

/* Active page pill — driven by data-page attr on .hnav-cur sentinel */
[data-testid="stHorizontalBlock"]:has(.hnav-cur[data-page="home"])
  > [data-testid="stColumn"]:nth-child(2) button,
[data-testid="stHorizontalBlock"]:has(.hnav-cur[data-page="diagnose"])
  > [data-testid="stColumn"]:nth-child(3) button,
[data-testid="stHorizontalBlock"]:has(.hnav-cur[data-page="action_plan"])
  > [data-testid="stColumn"]:nth-child(4) button,
[data-testid="stHorizontalBlock"]:has(.hnav-cur[data-page="field_guide"])
  > [data-testid="stColumn"]:nth-child(5) button {
  background   : rgba(34,197,94,.22) !important;
  border-color : rgba(34,197,94,.65) !important;
  color        : #4ade80             !important;
  animation    : hnavLinkGlow 2.8s ease-in-out infinite !important;
}

/* ── Language radio (last column) ──────────────────────────────────────── */
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"]:last-child {
  justify-content : flex-end !important;
  flex-shrink     : 0 !important;
}
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"]:last-child [data-testid="stRadio"] > div {
  flex-direction : row    !important;
  flex-wrap      : nowrap !important;
  gap            : 4px    !important;
}
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"]:last-child [data-testid="stRadio"] label {
  background    : rgba(255,255,255,.07) !important;
  border        : 1px solid rgba(255,255,255,.16) !important;
  border-radius : 8px  !important;
  padding       : 5px 12px !important;
  min-height    : 0    !important;
  cursor        : pointer !important;
  transition    : background .15s, border-color .15s !important;
}
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"]:last-child [data-testid="stRadio"] label * {
  color       : rgba(255,255,255,.82) !important;
  font-size   : .74rem !important;
  font-weight : 600    !important;
}
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"]:last-child [data-testid="stRadio"] label
  div[data-baseweb="radio"] { display: none !important; }
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"]:last-child [data-testid="stRadio"] label:has(input:checked) {
  background   : rgba(34,197,94,.28) !important;
  border-color : rgba(34,197,94,.8)  !important;
}
[data-testid="stHorizontalBlock"]:has(.hnav-root)
  > [data-testid="stColumn"]:last-child [data-testid="stRadio"] label:has(input:checked) * {
  color       : #4ade80 !important;
  font-weight : 700     !important;
}

/* ── Push page content below 64px navbar ─────────────────────────────── */
[data-testid="stMainBlockContainer"] { padding-top: 76px; }

/* ── Sidebar language radio ─────────────────────────────────────────────── */
.sb-lang-wrap { padding: 0 18px; }
.sb-lang-wrap [data-testid="stRadio"] > div { flex-direction: column !important; gap: 2px !important; }
.sb-lang-wrap [data-testid="stRadio"] label {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  color: rgba(255,255,255,.8) !important;
  font-size: .85rem !important;
  padding: 7px 12px !important;
  border-radius: 10px !important;
  border: 1px solid transparent !important;
  transition: all .15s ease;
  cursor: pointer !important;
}
.sb-lang-wrap [data-testid="stRadio"] label p,
.sb-lang-wrap [data-testid="stRadio"] label span {
  color: rgba(255,255,255,.8) !important;
  font-size: .85rem !important;
  font-weight: 500 !important;
}
.sb-lang-wrap [data-testid="stRadio"] label > div:first-child {
  display: flex !important;
  flex-shrink: 0 !important;
  align-items: center !important;
  justify-content: center !important;
}
.sb-lang-wrap [data-testid="stRadio"] label > div:first-child div[data-baseweb="radio"] {
  border-color: rgba(34,197,94,.55) !important;
  width: 16px !important;
  height: 16px !important;
}
.sb-lang-wrap [data-testid="stRadio"] label:hover {
  background: rgba(34,197,94,.12) !important;
  border-color: rgba(34,197,94,.25) !important;
}
.sb-lang-wrap [data-testid="stRadio"] label:hover p,
.sb-lang-wrap [data-testid="stRadio"] label:hover span { color: #fff !important; }
.sb-lang-wrap [data-testid="stRadio"] label:has(input:checked) {
  background: rgba(34,197,94,.18) !important;
  border-color: rgba(34,197,94,.45) !important;
}
.sb-lang-wrap [data-testid="stRadio"] label:has(input:checked) p,
.sb-lang-wrap [data-testid="stRadio"] label:has(input:checked) span {
  color: #22c55e !important;
  font-weight: 700 !important;
}
.sb-lang-wrap [data-testid="stRadio"] label:has(input:checked) div[data-baseweb="radio"] {
  border-color: #22c55e !important;
}
.sb-lang-wrap [data-testid="stRadio"] label div[data-baseweb="radio"] div:nth-child(2) {
  background: #22c55e !important;
}

/* ── What To Do Now visual action cards ─────────────────────────────────── */
.wtdn-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin: 12px 0;
}
.wtdn-card {
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  min-height: 195px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 12px;
  background-size: cover;
  background-position: center;
  cursor: default;
  box-shadow: 0 4px 14px rgba(0,0,0,.18);
  transition: transform .18s ease, box-shadow .18s ease;
}
.wtdn-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,.25);
}
.wtdn-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,.08) 0%, rgba(0,0,0,.72) 100%);
  border-radius: 16px;
}
.wtdn-card-icon {
  font-size: 2.6rem;
  line-height: 1;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -68%);
  filter: drop-shadow(0 2px 8px rgba(0,0,0,.6));
  z-index: 1;
}
.wtdn-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  border-radius: 999px;
  padding: 3px 9px;
  font-size: .56rem;
  font-weight: 800;
  letter-spacing: .8px;
  text-transform: uppercase;
  z-index: 1;
}
.wtdn-badge--today    { background: #dc2626; color: #fff; }
.wtdn-badge--week     { background: #d97706; color: #fff; }
.wtdn-badge--wet      { background: #2563eb; color: #fff; }
.wtdn-badge--daily    { background: #16a34a; color: #fff; }
.wtdn-badge--directed { background: #7c3aed; color: #fff; }
.wtdn-badge--now      { background: #dc2626; color: #fff; }
.wtdn-card-title {
  font-size: .82rem;
  font-weight: 800;
  color: #fff;
  position: relative;
  z-index: 1;
  line-height: 1.25;
  margin-bottom: 3px;
  text-shadow: 0 1px 4px rgba(0,0,0,.6);
}
.wtdn-card-bilingual {
  font-size: .7rem;
  color: rgba(255,255,255,.82);
  position: relative;
  z-index: 1;
  line-height: 1.45;
  font-family: "Noto Sans Tamil", sans-serif;
  text-shadow: 0 1px 3px rgba(0,0,0,.5);
}

/* ── Why It Happened banner ─────────────────────────────────────────────── */
.wtdn-why-banner {
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
  border: 1.5px solid #fde68a;
  border-radius: 14px;
  padding: 16px 20px;
  display: flex;
  gap: 14px;
  align-items: flex-start;
  margin: 14px 0 0;
}
.wtdn-why-icon { font-size: 2rem; flex-shrink: 0; margin-top: 2px; }
.wtdn-why-title {
  font-size: .64rem;
  font-weight: 800;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: #b45309;
  margin-bottom: 5px;
}
.wtdn-why-text {
  font-size: .875rem;
  color: #374151;
  font-weight: 500;
  line-height: 1.65;
}
.wtdn-why-ta {
  font-size: .77rem;
  color: #78716c;
  font-family: "Noto Sans Tamil", sans-serif;
  margin-top: 6px;
  line-height: 1.55;
  border-top: 1px solid #fde68a;
  padding-top: 6px;
}

/* ── Treatment icon pills ────────────────────────────────────────────────── */
.wtdn-pill-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid #e5e7eb;
}
.wtdn-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  padding: 6px 14px 6px 8px;
  font-size: .74rem;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}
.wtdn-pill-icon { font-size: 1.05rem; }
.wtdn-pill-lbl-ta {
  font-size: .65rem;
  color: #6b7280;
  font-family: "Noto Sans Tamil", sans-serif;
  margin-left: 3px;
}

/* ── Dashboard cards ─────────────────────────────────────────────────────── */
.dash-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 18px 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,.05);
  height: 100%;
  min-height: 200px;
}
.dash-card-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.dash-card-icon { font-size: 1.5rem; flex-shrink: 0; }
.dash-card-title {
  font-size: .65rem;
  font-weight: 800;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: #374151;
  line-height: 1.2;
}
.dash-wx-cell {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px 10px;
}
.dash-wx-lbl {
  font-size: .58rem;
  color: #9ca3af;
  font-weight: 600;
  letter-spacing: .3px;
  text-transform: uppercase;
  margin-bottom: 3px;
}
.dash-wx-val {
  font-size: .95rem;
  font-weight: 800;
  color: #111827;
}

/* ── What To Do Now page ─────────────────────────────────────────────────── */
.wtdn-page-hero {
  background: linear-gradient(135deg, #052e16 0%, #14532d 55%, #1a6b38 100%);
  border-radius: 20px;
  padding: 24px 32px;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 28px rgba(5,46,22,.4);
}
.wtdn-page-hero::after {
  content: "";
  position: absolute;
  inset: 0;
  background: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=60&auto=format&fit=crop") center/cover no-repeat;
  opacity: .15;
  pointer-events: none;
}
.wtdn-page-hero-content {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 1;
}
.wtdn-page-hero-title {
  font-size: 1.6rem;
  font-weight: 900;
  color: #fff;
  letter-spacing: -.5px;
  text-shadow: 0 2px 8px rgba(0,0,0,.4);
}
.wtdn-page-hero-sep {
  font-size: 1.6rem;
  color: rgba(255,255,255,.4);
}
.wtdn-page-hero-ta {
  font-size: 1rem;
  font-weight: 700;
  color: rgba(255,255,255,.8);
  font-family: "Noto Sans Tamil", sans-serif;
}
.wtdn-page-hero-sub {
  font-size: .72rem;
  color: rgba(255,255,255,.5);
  margin-top: 6px;
  position: relative;
  z-index: 1;
}

/* ── Large action cards (What To Do Now page) ────────────────────────────── */
.wtdn-cards-scroll {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding: 4px 2px 14px;
  scrollbar-width: thin;
  scrollbar-color: rgba(34,197,94,.3) transparent;
}
.wtdn-cards-scroll::-webkit-scrollbar { height: 4px; }
.wtdn-cards-scroll::-webkit-scrollbar-thumb { background: rgba(34,197,94,.3); border-radius: 999px; }

.wtdn-action-card-lg {
  min-width: 210px;
  max-width: 230px;
  flex-shrink: 0;
  border-radius: 16px;
  overflow: hidden;
  border: 1.5px solid #e5e7eb;
  box-shadow: 0 4px 16px rgba(0,0,0,.08);
  background: #fff;
  transition: transform .2s, box-shadow .2s;
}
.wtdn-action-card-lg:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 28px rgba(0,0,0,.13);
}
.wtdn-action-card-img {
  height: 200px;
  background-size: cover;
  background-position: center;
  position: relative;
}
.wtdn-action-card-img::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,.1) 0%, rgba(0,0,0,.55) 100%);
}
.wtdn-action-card-icon-lg {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -60%);
  font-size: 2.8rem;
  filter: drop-shadow(0 2px 8px rgba(0,0,0,.5));
}
.wtdn-action-card-body {
  padding: 14px 14px 16px;
  background: #fff;
}
.wtdn-action-card-en {
  font-size: .82rem;
  font-weight: 900;
  color: #111827;
  text-transform: uppercase;
  line-height: 1.2;
  margin-bottom: 5px;
  letter-spacing: .3px;
}
.wtdn-action-card-ta {
  font-size: .75rem;
  color: #374151;
  font-family: "Noto Sans Tamil", sans-serif;
  line-height: 1.4;
}

/* ── Advisory sidebar ────────────────────────────────────────────────────── */
.wtdn-adv-sidebar {
  background: #fff;
  border: 1.5px solid #e5e7eb;
  border-radius: 16px;
  padding: 18px 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,.05);
}
.wtdn-adv-sidebar-hd {
  font-size: .6rem;
  font-weight: 800;
  letter-spacing: 1.8px;
  text-transform: uppercase;
  color: #0d9488;
  margin-bottom: 14px;
}
.wtdn-adv-pills-hd {
  font-size: .7rem;
  font-weight: 700;
  color: #374151;
  margin: 14px 0 10px;
  border-top: 1px solid #f3f4f6;
  padding-top: 12px;
}
.wtdn-adv-pills-wrap { display: flex; flex-direction: column; gap: 8px; }
.wtdn-adv-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 10px 12px;
}
.wtdn-adv-pill-icon { font-size: 1.5rem; flex-shrink: 0; }
.wtdn-adv-pill-en { font-size: .78rem; font-weight: 700; color: #111827; line-height: 1.2; }
.wtdn-adv-pill-ta { font-size: .65rem; color: #6b7280; font-family: "Noto Sans Tamil",sans-serif; }

@keyframes sadBounce { 0%,100%{transform:translateY(0) rotate(-5deg)} 50%{transform:translateY(-8px) rotate(5deg)} }

.sg-banner { background:linear-gradient(135deg,#f0fdf4,#ecfdf5); border:1.5px solid #bbf7d0; border-radius:20px; padding:20px 28px; display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; overflow:hidden; animation:fadeUp .45s ease both; }
.sg-text { flex:1; }
.sg-title { font-size:1.45rem; font-weight:900; color:#111827; line-height:1.2; }
.sg-sub { font-size:.9rem; color:#4b5563; margin-top:5px; }
.sg-farmer { width:120px; height:120px; object-fit:contain; animation:farmerBob 3s ease-in-out infinite; flex-shrink:0; }
.sg-farmer-emoji { font-size:5rem; animation:farmerBob 3s ease-in-out infinite; flex-shrink:0; }

.story-card { background:#fff; border:1.5px solid #e5e7eb; border-radius:20px; padding:22px 24px; margin-bottom:16px; display:flex; align-items:flex-start; gap:20px; }
.story-card--d1 { animation:fadeUp .5s .1s ease both; }
.story-card--d2 { animation:fadeUp .5s .2s ease both; }
.sc-illus { flex:0 0 108px; }
.sc-illus-circle { width:108px; height:108px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:2.8rem; }
.sc-illus-plants { width:108px; min-height:88px; border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:2rem; line-height:1.5; padding:8px; text-align:center; }
.sc-body { flex:1; min-width:0; }
.sc-title { font-size:1.05rem; font-weight:800; color:#111827; margin-bottom:5px; }
.sc-sub { font-size:.84rem; color:#6b7280; margin-bottom:12px; line-height:1.5; }
.sc-risk { display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:12px; margin-bottom:10px; flex-wrap:wrap; }
.sc-risk--high { background:#fef2f2; border:1.5px solid #fecaca; }
.sc-risk--mod  { background:#fffbeb; border:1.5px solid #fde68a; }
.sc-risk--low  { background:#f0fdf4; border:1.5px solid #bbf7d0; }
.sc-risk-badge { font-size:.7rem; font-weight:800; padding:3px 10px; border-radius:999px; white-space:nowrap; }
.sc-risk-badge--high { background:#dc2626; color:#fff; }
.sc-risk-badge--mod  { background:#d97706; color:#fff; }
.sc-risk-badge--low  { background:#16a34a; color:#fff; }
.sc-risk-text { font-size:.82rem; color:#374151; font-weight:500; line-height:1.4; flex:1; }
.sc-sad-leaf { font-size:2.6rem; animation:sadBounce 2.2s ease-in-out infinite; flex-shrink:0; align-self:center; }
.sc-wx-row { display:flex; gap:10px; margin-top:12px; }
.sc-wx-card { flex:1; background:#f8fafc; border:1px solid #e5e7eb; border-radius:12px; padding:10px 14px; display:flex; align-items:center; gap:10px; }
.sc-wx-icon { font-size:1.6rem; line-height:1; }
.sc-wx-lbl { font-size:.6rem; font-weight:700; color:#9ca3af; text-transform:uppercase; letter-spacing:.5px; }
.sc-wx-val { font-size:.9rem; font-weight:800; color:#111827; }

.sa-section-hd { font-size:1.05rem; font-weight:800; color:#111827; margin:20px 0 4px; }
.sa-section-sub { font-size:.84rem; color:#6b7280; margin-bottom:14px; }
.sa-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:18px; }
.sa-card { background:#fff; border:1.5px solid #e5e7eb; border-radius:16px; overflow:hidden; cursor:pointer; transition:transform .22s,box-shadow .22s,border-color .22s; opacity:0; animation:fadeUp .5s ease forwards; }
.sa-card:hover { transform:translateY(-5px); box-shadow:0 12px 32px rgba(0,0,0,.1); border-color:#4ade80; }
.sa-card:nth-child(1){animation-delay:.1s} .sa-card:nth-child(2){animation-delay:.2s} .sa-card:nth-child(3){animation-delay:.3s} .sa-card:nth-child(4){animation-delay:.4s}
.sa-header { display:flex; align-items:center; gap:8px; padding:10px 12px 0; }
.sa-num { width:24px; height:24px; border-radius:50%; background:#16a34a; color:#fff; font-size:.7rem; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.sa-label { font-size:.77rem; font-weight:700; color:#111827; line-height:1.3; }
.sa-illus { height:100px; margin:8px 10px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:3rem; position:relative; overflow:hidden; }
.sa-check { position:absolute; bottom:8px; left:8px; width:26px; height:26px; border-radius:50%; background:#16a34a; color:#fff; font-size:.75rem; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 8px rgba(22,163,74,.45); }

.sw-section { border-radius:20px; padding:20px 24px; margin-bottom:16px; display:flex; align-items:center; gap:20px; animation:fadeUp .5s .35s ease both; }
.sw-section--good { background:linear-gradient(135deg,#fefce8,#fef9c3); border:1.5px solid #fde68a; }
.sw-section--bad  { background:linear-gradient(135deg,#fef2f2,#fee2e2); border:1.5px solid #fecaca; }
.sw-section--mod  { background:linear-gradient(135deg,#fffbeb,#fef3c7); border:1.5px solid #fde68a; }
.sw-section--unk  { background:#f8fafc; border:1.5px solid #e5e7eb; }
.sw-icon { font-size:4rem; flex-shrink:0; }
.sw-icon--sun   { animation:fpSunGlow 3s ease-in-out infinite; }
.sw-icon--cloud { animation:float 3s ease-in-out infinite; }
.sw-content { flex:1; }
.sw-title { font-size:1rem; font-weight:800; color:#111827; margin-bottom:5px; }
.sw-msg { font-size:.88rem; color:#374151; line-height:1.5; margin-bottom:10px; }
.sw-badge { display:inline-flex; align-items:center; gap:6px; background:rgba(255,255,255,.85); border:1px solid rgba(0,0,0,.08); border-radius:999px; padding:5px 14px; font-size:.8rem; font-weight:700; color:#374151; }

.story-tip { background:linear-gradient(135deg,#f0fdf4,#dcfce7); border:1.5px solid #86efac; border-radius:18px; padding:16px 22px; display:flex; align-items:center; gap:16px; animation:fadeUp .5s .45s ease both; margin-bottom:4px; }
.st-tip-icon { font-size:1.2rem; flex-shrink:0; }
.st-tip-text { font-size:.9rem; font-weight:600; color:#166534; flex:1; line-height:1.4; }
.st-tip-farmer { font-size:2.8rem; animation:farmerBob 2.5s ease-in-out infinite; flex-shrink:0; }

/* ── Expanders ──────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
  border: 1.5px solid #e5e7eb !important;
  border-radius: 14px !important;
  overflow: hidden !important;
  background: #fff !important;
  margin-bottom: 8px !important;
  box-shadow: 0 1px 4px rgba(0,0,0,.04) !important;
}
[data-testid="stExpander"] details > summary {
  padding: 14px 18px !important;
  background: #f8fafb !important;
  font-weight: 600 !important;
  font-size: .9rem !important;
  color: #374151 !important;
  cursor: pointer !important;
  transition: background .15s, color .15s !important;
}
[data-testid="stExpander"] details > summary:hover {
  background: #f0fdf4 !important;
  color: #15803d !important;
}
[data-testid="stExpander"] details[open] > summary {
  background: #f0fdf4 !important;
  color: #15803d !important;
  border-bottom: 1px solid #e5e7eb !important;
}
[data-testid="stExpanderDetails"] {
  padding: 16px 18px !important;
}

/* ── Select box ─────────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border-radius: 10px !important;
  border: 1.5px solid #e5e7eb !important;
  background: #fff !important;
  min-height: 42px !important;
  transition: border-color .18s, box-shadow .18s !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
  border-color: #4ade80 !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div {
  border-color: #16a34a !important;
  box-shadow: 0 0 0 3px rgba(22,163,74,.12) !important;
}

/* ── Disease Library: fuse card visually with its View Details button ───── */
[data-testid="stColumn"]:has(.dl-card) .dl-card {
  border-radius: 14px 14px 0 0 !important;
  border-bottom: none !important;
  margin-bottom: 0 !important;
}
[data-testid="stColumn"]:has(.dl-card) [data-testid="stButton"] {
  margin-top: 0 !important;
}
[data-testid="stColumn"]:has(.dl-card) [data-testid="stButton"] > button {
  border-radius: 0 0 14px 14px !important;
  border: 1.5px solid #e5e7eb !important;
  border-top: none !important;
  background: #f8fafb !important;
  color: #374151 !important;
  font-size: .78rem !important;
  font-weight: 700 !important;
  letter-spacing: .2px !important;
  box-shadow: none !important;
  padding: 10px 16px !important;
  transition: background .18s, color .18s, border-color .18s !important;
  transform: none !important;
}
[data-testid="stColumn"]:has(.dl-card) [data-testid="stButton"] > button:hover {
  background: #16a34a !important;
  border-color: #16a34a !important;
  color: #fff !important;
  transform: none !important;
  box-shadow: none !important;
  filter: none !important;
}
[data-testid="stColumn"]:has(.dl-card.active) [data-testid="stButton"] > button {
  background: #f0fdf4 !important;
  color: #15803d !important;
  border-color: #bbf7d0 !important;
}

/* ── Advisory pill hover ─────────────────────────────────────────────────── */
.wtdn-adv-pill {
  transition: background .18s, border-color .18s, transform .14s;
}
.wtdn-adv-pill:hover {
  background: #f0fdf4;
  border-color: #bbf7d0;
  transform: translateX(3px);
}

/* ── Action card hover glow ──────────────────────────────────────────────── */
.sa-card:hover .sa-illus {
  filter: brightness(1.06);
}

/* ── Story card entrance shadow ──────────────────────────────────────────── */
.story-card {
  box-shadow: 0 2px 12px rgba(0,0,0,.04);
  transition: box-shadow .22s, transform .22s;
}
.story-card:hover {
  box-shadow: 0 6px 24px rgba(0,0,0,.08);
  transform: translateY(-2px);
}
"""


def inject_css() -> None:
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


# ── Nav definitions ───────────────────────────────────────────────────────────
_NAV = [
    ("home",        "🏠", "nav.home",        "pages/1_Home.py"),
    ("diagnose",    "🩺", "nav.diagnose",    "pages/2_Analyze_Leaf.py"),
    ("action_plan", "⚡", "nav.action_plan", "pages/3_What_To_Do.py"),
    ("field_guide", "📖", "nav.field_guide", "pages/6_Disease_Library.py"),
]


def inject_sidebar_brand() -> None:
    cur = st.session_state.get("_cur_page", "home")

    with st.sidebar:
        st.markdown(
            '<style>'
            ':root{--secondary-background-color:#0B1A0D !important;}'
            '[data-testid*="Sidebar"],'
            '[data-testid*="Sidebar"]>div,'
            '[data-testid*="Sidebar"]>div>div,'
            '[data-testid*="Sidebar"]>div>div>div'
            '{background-color:#0B1A0D !important;background:#0B1A0D !important;}'
            '</style>',
            unsafe_allow_html=True,
        )

        # ── Brand ────────────────────────────────────────────────────────────
        st.markdown(
            '<div style="padding:28px 18px 20px;">'
            '<div style="display:flex;align-items:center;gap:12px;margin-bottom:30px;">'
            '<div style="width:40px;height:40px;border-radius:12px;flex-shrink:0;'
            'background:linear-gradient(145deg,#22c55e,#15803d);'
            'display:flex;align-items:center;justify-content:center;'
            'font-size:1.2rem;box-shadow:0 3px 12px rgba(34,197,94,.4);">&#127806;</div>'
            '<div>'
            '<div style="font-size:1rem;font-weight:800;color:#ffffff;letter-spacing:-.3px;line-height:1.15;">AgriShield-TN</div>'
            '<div style="font-size:.66rem;color:rgba(255,255,255,.32);margin-top:2px;letter-spacing:.2px;">AI Crop Health Assistant</div>'
            '</div>'
            '</div>'
            '<div style="font-size:.57rem;font-weight:700;letter-spacing:2.5px;'
            'text-transform:uppercase;color:rgba(255,255,255,.18);margin-bottom:8px;">Navigation</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # ── i18n helpers ──────────────────────────────────────────────────────
        try:
            from i18n import t as _t, get_lang as _gl
        except ImportError:
            _t = lambda k, **kw: k
            _gl = lambda: "en"

        # ── Nav items ─────────────────────────────────────────────────────────
        for key, icon, label_key, path in _NAV:
            label = _t(label_key)
            if key == cur:
                st.markdown(
                    f'<div class="sb-nav-active">{icon}&nbsp;&nbsp;{label}</div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button(f"{icon}  {label}", key=f"_nav_{path}", use_container_width=True):
                    st.switch_page(path)

        # ── Language selector ─────────────────────────────────────────────────
        st.markdown(
            '<div style="margin:20px 18px 6px;border-top:1px solid rgba(34,197,94,.1);padding-top:16px;">'
            '<div style="font-size:.57rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;'
            'color:rgba(255,255,255,.28);margin-bottom:10px;">&#127758; Language</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        _lang_display = {"en": "🇬🇧 English", "ta": "🇮🇳 தமிழ்", "hi": "🇮🇳 हिन्दी"}
        _cur_lang = _gl()
        st.markdown('<div class="sb-lang-wrap">', unsafe_allow_html=True)
        _sb_lang = st.radio(
            "sb_lang",
            options=list(_lang_display.keys()),
            format_func=lambda x: _lang_display[x],
            index=list(_lang_display.keys()).index(_cur_lang),
            label_visibility="collapsed",
            key="_sb_lang_radio",
        )
        st.markdown('</div>', unsafe_allow_html=True)
        if _sb_lang != _cur_lang:
            st.session_state["lang"] = _sb_lang
            st.rerun()

        # ── Sidebar footer ────────────────────────────────────────────────────
        st.markdown(
            '<div style="position:absolute;bottom:0;left:0;right:0;">'

            '<div style="height:28px;background:linear-gradient(to bottom,transparent,'
            'rgba(11,26,13,.95));pointer-events:none;"></div>'

            '<div style="background:#0B1A0D;border-top:1px solid rgba(34,197,94,.1);'
            'padding:14px 18px 20px;">'

            '<div style="display:flex;align-items:center;gap:7px;margin-bottom:6px;">'
            '<span style="width:6px;height:6px;border-radius:50%;background:#22c55e;'
            'flex-shrink:0;box-shadow:0 0 0 2px rgba(34,197,94,.2);'
            'animation:pulse 2.5s ease-in-out infinite;"></span>'
            '<span style="font-size:.72rem;font-weight:700;color:#22c55e;">Models ready</span>'
            '</div>'

            '<div style="font-size:.65rem;color:rgba(255,255,255,.24);line-height:1.7;">'
            'ResNet-18 &nbsp;&middot;&nbsp; Grad-CAM &nbsp;&middot;&nbsp; Groq AI'
            '</div>'
            '</div>'

            '</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def ui_divider() -> None:
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)


def inject_header() -> None:
    """Fixed horizontal top navbar: brand | page nav | language switcher.

    Navigation uses st.button + st.switch_page so clicks work correctly
    even when the row is CSS position:fixed outside Streamlit's scroll flow.

    Active-page detection uses st.context.url_pathname (Streamlit ≥ 1.37)
    with a session-state fallback so the correct pill is always highlighted.
    """
    try:
        from i18n import get_lang as _gl, t as _t
    except ImportError:
        _gl = lambda: "en"
        _t = lambda k, **kw: k

    _cur_lang = _gl()
    _LANG_OPTS = {"en": "EN", "ta": "தமிழ்", "hi": "हिन्दी"}

    # Detect active page from URL first; fall back to session state
    _URL_MAP = {
        "/":            "home",
        "/diagnose":    "diagnose",
        "/action-plan": "action_plan",
        "/field-guide": "field_guide",
        # file-name fallbacks Streamlit sometimes uses
        "/1_home":             "home",
        "/2_analyze_leaf":     "diagnose",
        "/3_what_to_do":       "action_plan",
        "/6_disease_library":  "field_guide",
    }
    try:
        _cur_page = _URL_MAP.get(
            getattr(st.context, "url_pathname", None) or "",
            st.session_state.get("_cur_page", "home"),
        )
    except Exception:
        _cur_page = st.session_state.get("_cur_page", "home")

    # Single row: brand | Home | Diagnose | Action Plan | Field Guide | lang
    _cb, _c1, _c2, _c3, _c4, _cl = st.columns([2, 1, 1, 1, 1, 2], gap="small")

    with _cb:
        # .hnav-root  → CSS selects this stHorizontalBlock and position:fixed it
        # .hnav-cur   → CSS uses data-page attr to highlight the active button
        st.markdown(
            f'<div class="hnav-root"></div>'
            f'<div class="hnav-cur" data-page="{_cur_page}"></div>'
            '<div class="hnav-brand">'
            '  <span class="hnav-brand-logo">🌾</span>'
            '  <div class="hnav-brand-text">'
            '    <span class="hnav-brand-name">'
            '      AgriShield<span class="hnav-tn">-TN</span>'
            '    </span>'
            '    <span class="hnav-brand-sub">AI Crop Doctor</span>'
            '  </div>'
            '</div>',
            unsafe_allow_html=True,
        )

    _nav_btns = [
        ("home",        _c1, "🏠", "nav.home",        "pages/1_Home.py"),
        ("diagnose",    _c2, "🩺", "nav.diagnose",    "pages/2_Analyze_Leaf.py"),
        ("action_plan", _c3, "⚡", "nav.action_plan", "pages/3_What_To_Do.py"),
        ("field_guide", _c4, "📖", "nav.field_guide", "pages/6_Disease_Library.py"),
    ]
    for _key, _col, _icon, _lk, _path in _nav_btns:
        with _col:
            if st.button(
                f"{_icon} {_t(_lk)}",
                key=f"_hnav_{_key}",
                use_container_width=True,
            ):
                st.switch_page(_path)

    with _cl:
        _chosen = st.radio(
            "Language",
            options=list(_LANG_OPTS.keys()),
            format_func=lambda x: _LANG_OPTS[x],
            index=list(_LANG_OPTS.keys()).index(_cur_lang),
            label_visibility="collapsed",
            horizontal=True,
            key="_top_lang_radio",
        )
        if _chosen != _cur_lang:
            st.session_state["lang"] = _chosen
            st.rerun()



def ui_error(msg: str) -> None:
    try:
        from i18n import t as _t
    except ImportError:
        _t = lambda k, **kw: k
    st.markdown(
        '<div class="ds-error">'
        f'&#9888;&#65039; <strong>{_t("common.error_title")}</strong> {msg}'
        f'<span class="ds-error-sub">{_t("common.error_sub")}</span>'
        '</div>',
        unsafe_allow_html=True,
    )


def ui_footer() -> None:
    try:
        from i18n import t as _t
    except ImportError:
        _t = lambda k, **kw: k
    st.markdown(
        '<div class="ds-footer">'
        '<div class="ds-footer-brand">'
        '<span style="font-size:.9rem;">&#127806;</span>'
        'AgriShield-TN'
        '<span style="width:3px;height:3px;border-radius:50%;background:#E2E8F0;display:inline-block;"></span>'
        f'<span style="font-size:.8rem;color:#64748B;font-weight:400;">{_t("common.footer_tagline")}</span>'
        '</div>'
        '<div style="font-size:.8rem;color:#94A3B8;">'
        'ResNet-18 &nbsp;&middot;&nbsp; Grad-CAM &nbsp;&middot;&nbsp; '
        'Groq AI &nbsp;&middot;&nbsp; PyTorch &nbsp;&middot;&nbsp; Streamlit'
        '</div>'
        f'<div class="ds-footer-note">{_t("common.footer_note")}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  SCAN PANEL  (2_Analyze_Leaf.py)
# ─────────────────────────────────────────────────────────────────────────────

_STEPS = [
    ("&#128269;", "scan.s0", "INIT"),
    ("&#129516;", "scan.s1", "FEAT"),
    ("&#9889;",   "scan.s2", "ANOM"),
    ("&#129302;", "scan.s3", "INFER"),
    ("&#128293;", "scan.s4", "XAI"),
    ("&#9989;",   "scan.s5", "DONE"),
]


def draw_scan(slot, active: int, pct: int) -> None:
    try:
        from i18n import t as _t
        progress_lbl = _t("scan.progress")
    except ImportError:
        _t = lambda k, **kw: k
        progress_lbl = "PROGRESS"
    rows = ""
    for i, (icon, i18n_key, tag) in enumerate(_STEPS):
        label = _t(i18n_key)
        if   i < active:  state, ts, ico = "done",    f"0.{i+1}s", "&#10003;"
        elif i == active: state, ts, ico = "active",  "...",         icon
        else:             state, ts, ico = "pending",  "&mdash;",    icon
        rows += (
            '<div class="ds-scan-step">'
            f'<div class="ds-step-ico {state}">{ico}</div>'
            f'<span class="ds-step-lbl {state}">[{tag}] {label}</span>'
            f'<span class="ds-step-t {state}">{ts}</span>'
            '</div>'
        )
    slot.markdown(
        '<div class="ds-scan">'
        '<div class="ds-scan-beam"></div>'
        '<div class="ds-scan-header">'
        '<div class="ds-scan-dot"></div>'
        '<span class="ds-scan-title">AgriShield &middot; Analysis</span>'
        '<span class="ds-scan-ref">AGS-TN-2025</span>'
        '</div>'
        + rows +
        '<div class="ds-scan-prog">'
        f'<div class="ds-scan-prog-lbl"><span>{progress_lbl}</span><span>{pct}%</span></div>'
        f'<div class="ds-scan-track"><div class="ds-scan-fill" style="width:{pct}%;"></div></div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
