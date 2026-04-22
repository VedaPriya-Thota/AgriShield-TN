import re

file_path = "c:/Users/pujar/OneDrive/Desktop/AgriShield-TN/app/pages/2_Analyze_Leaf.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update CSS
css_additions = """
.card-struct {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    border: 1px solid #E5E7EB;
    margin-bottom: 12px;
}
.header-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.header-left { flex: 1; }
.header-right { margin-left: 20px; flex-shrink: 0; }
.header-farmer { width: 100px; height: auto; opacity: 0.95; }
.sum-val { font-size: 1.1rem; font-weight: 800; color: #111827; }
.sum-lbl { font-size: 0.75rem; color: #6B7280; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
.action-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
.action-item { background: #F9FAF8; border: 1px solid #F3F4F6; padding: 12px; border-radius: 8px; display: flex; align-items: flex-start; gap: 10px; }
.action-ico { font-size: 1.4rem; }
.action-title { font-size: 0.85rem; font-weight: 700; color: #111827; margin-bottom: 2px; }
.action-desc { font-size: 0.75rem; color: #4B5563; line-height: 1.4; }
.adv-sec-title { font-size: 0.75rem; font-weight: 700; color: #16a34a; text-transform: uppercase; margin-bottom: 2px; margin-top: 12px; }
.adv-sec-title:first-child { margin-top: 0; }
.adv-sec-text { font-size: 0.85rem; color: #374151; line-height: 1.5; margin-bottom: 0; }
"""
if ".card-struct" not in content:
    content = content.replace('</style>', css_additions + '\n</style>')

start_marker = "# ── 1. HERO STATUS CARD ───────────────────────────────────────────────"
end_marker = "# ── 4. VISUAL ANALYSIS (expander) ─────────────────────────────────────"

part1, rest = content.split(start_marker, 1)
middle, part2 = rest.split(end_marker, 1)

new_results = """
        # ── 1. RESULT HEADER CARD ─────────────────────────────────────────────
        ui_divider()
        st.markdown('<div class="section-lbl">&#10004;&#65039; AI CROP DIAGNOSTIC TOOL</div>', unsafe_allow_html=True)

        conf_pct = round(confidence * 100)
        
        if sev in ("NONE", "LOW"):
            badge_color = "#16a34a"
            badge_bg = "#f0fdf4"
            status_title = "Crop Health is Good"
            icon = "&#9989;"
        elif sev == "MODERATE":
            badge_color = "#d97706"
            badge_bg = "#fffbeb"
            status_title = "Caution Needed"
            icon = "&#9888;&#65039;"
        else:
            badge_color = "#dc2626"
            badge_bg = "#fef2f2"
            status_title = "Action Required"
            icon = "&#128680;"

        farmer_img = "https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/People/Man%20Farmer.png"
        
        hdr_html = f'''
        <div class="header-card">
            <div class="header-left">
                <div style="font-size: 1.4rem; font-weight: 800; color: #111827; margin-bottom: 6px;">{status_title}</div>
                <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 0.85rem; font-weight: 700; background: {badge_bg}; color: {badge_color}; padding: 4px 10px; border-radius: 6px; border: 1px solid {badge_color}33;">
                        {icon} Severity: {sev}
                    </span>
                    <span style="font-size: 0.85rem; color: #4B5563; font-weight: 600;">{conf_pct}% Confidence</span>
                </div>
                <div style="font-size: 0.9rem; color: #4B5563;">
                    <strong>Disease Detected:</strong> {disease_name if sev not in ("NONE", "LOW") else "None detected. Safe."}
                </div>
            </div>
            <div class="header-right">
                <img src="{farmer_img}" class="header-farmer" />
            </div>
        </div>
        '''
        st.markdown(hdr_html, unsafe_allow_html=True)

        # ── 2. SUMMARY CARDS ROW ──────────────────────────────────────────────
        c1, c2, c3 = st.columns(3, gap="medium")
        
        with c1:
            st.markdown(f'''
            <div class="card-struct" style="height: 100%;">
                <div class="sum-lbl">Crop Health</div>
                <div class="sum-val" style="color: {badge_color};">{disease_name}</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with c2:
            if wx.get("available"):
                wx_str = f'{wx["temp"]}°C, {wx["humidity"]}%'
                wx_icon = "&#9728;&#65039;" if wx["risk_level"] == "LOW" else "&#9928;&#65039;"
            else:
                wx_str = "Data unavailable"
                wx_icon = "&#127780;&#65039;"
                
            st.markdown(f'''
            <div class="card-struct" style="height: 100%;">
                <div class="sum-lbl">Weather Risk</div>
                <div class="sum-val">{wx_icon} {wx_str}</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with c3:
            _pri = "Routine" if sev in ("NONE", "LOW") else ("Elevated" if sev == "MODERATE" else "Immediate")
            _pri_ico = "&#128197;"
            st.markdown(f'''
            <div class="card-struct" style="height: 100%;">
                <div class="sum-lbl">Action Priority</div>
                <div class="sum-val">{_pri_ico} {_pri}</div>
            </div>
            ''', unsafe_allow_html=True)

        # ── 3. WHAT TO DO NOW ─────────────────────────────────────────────────
        st.markdown('<div class="section-lbl">&#128640; WHAT TO DO NOW</div>', unsafe_allow_html=True)
        
        actions = insight.immediate_actions[:4]
        if not actions:
             actions = ["Keep monitoring the field regularly.", "Ensure proper hydration for the crop."]
        
        actions_html = '<div class="action-grid">'
        icons = ["&#128167;", "&#129514;", "&#128269;", "&#9889;"]
        
        for i, act in enumerate(actions):
            ico = icons[i % len(icons)]
            title_part = act.split()[0] + (" Handling" if len(act.split()[0]) > 4 else " Action")
            actions_html += f'''
            <div class="action-item">
                <div class="action-ico">{ico}</div>
                <div>
                    <div class="action-title">Step {i+1}</div>
                    <div class="action-desc">{act}</div>
                </div>
            </div>
            '''
        actions_html += '</div>'
        st.markdown(actions_html, unsafe_allow_html=True)

        # ── 4. EXPERT ADVISORY CARD ───────────────────────────────────────────
        st.markdown('<div class="section-lbl">&#128214; EXPERT ADVISORY</div>', unsafe_allow_html=True)
        
        adv_summary = insight.summary.split('.')[0] + "."
        adv_cause = ". ".join(insight.cause.split(". ")[:2]) + "."
        adv_prev = ". ".join(insight.prevention.split(". ")[:2]) + "."
        
        st.markdown(f'''
        <div class="card-struct" style="background: #F8FAF8;">
            <div class="adv-sec-title">Summary</div>
            <p class="adv-sec-text">{adv_summary}</p>
            
            <div class="adv-sec-title">Likely Cause</div>
            <p class="adv-sec-text">{adv_cause}</p>
            
            <div class="adv-sec-title">Treatment & Prevention</div>
            <p class="adv-sec-text">{adv_prev}</p>
        </div>
        ''', unsafe_allow_html=True)

"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(part1 + start_marker + "\n" + new_results + "\n        " + end_marker + part2)

print("Done replacing.")
