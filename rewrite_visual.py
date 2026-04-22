import re

file_path = "c:/Users/pujar/OneDrive/Desktop/AgriShield-TN/app/pages/2_Analyze_Leaf.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Provide CSS for visual dominance and remove old CSS
css_visual = """
.v-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.04);
    border: 1px solid #E5E7EB;
    margin-bottom: 16px;
}
.v-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: none;
    border-radius: 16px;
    padding: 24px;
    color: white;
    margin-bottom: 12px;
}
.v-header-safe { background: linear-gradient(135deg, #14532d, #16a34a); box-shadow: 0 8px 30px rgba(22,163,74,0.3); }
.v-header-warn { background: linear-gradient(135deg, #78350f, #d97706); box-shadow: 0 8px 30px rgba(217,119,6,0.3); }
.v-header-crit { background: linear-gradient(135deg, #7f1d1d, #dc2626); box-shadow: 0 8px 30px rgba(220,38,38,0.3); }

.v-msg-card {
    display: flex;
    align-items: center;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 12px;
    padding: 16px 20px;
    gap: 16px;
    margin-bottom: 24px;
}
.v-msg-text { font-size: 1.1rem; font-weight: 700; color: #166534; line-height: 1.4; }
.v-action-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; }
.v-action {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 24px 12px;
    background: #F9FAF8;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    gap: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}
.v-action-ico { font-size: 2.2rem; }
.v-action-txt { font-size: 0.9rem; font-weight: 700; color: #111827; }
"""
if ".v-card" not in content:
    content = content.replace('</style>', css_visual + '\n</style>')

start_marker = "# ── 1. RESULT HEADER CARD ─────────────────────────────────────────────"
end_marker = "# ── 4. VISUAL ANALYSIS (expander) ─────────────────────────────────────"

if start_marker in content and end_marker in content:
    part1, rest = content.split(start_marker, 1)
    middle, part2 = rest.split(end_marker, 1)
else:
    print("Markers not found!")
    exit(1)

new_results = """
        # ── 1. VISUAL RESULT HEADER ───────────────────────────────────────────
        ui_divider()
        st.markdown('<div class="section-lbl">&#10004;&#65039; DIAGNOSIS RESULT</div>', unsafe_allow_html=True)

        conf_pct = round(confidence * 100)
        
        if sev in ("NONE", "LOW"):
            h_cls = "v-header-safe"
            h_msg = f"{disease_name} detected &rarr; Low risk &rarr; Monitor crop" if disease_name != "Healthy" else "Healthy Crop &rarr; Zero risk &rarr; Safe"
            ico = "&#9989;"
        elif sev == "MODERATE":
            h_cls = "v-header-warn"
            h_msg = f"{disease_name} detected &rarr; Moderate risk &rarr; Start treatment"
            ico = "&#9888;&#65039;"
        else:
            h_cls = "v-header-crit"
            h_msg = f"{disease_name} detected &rarr; High risk &rarr; Act today!"
            ico = "&#128680;"

        import base64
        import os
        img_path = "app/assets/farmer_ai.png"
        if os.path.exists(img_path):
            with open(img_path, "rb") as bf:
                farmer_b64 = base64.b64encode(bf.read()).decode()
            farmer_img_src = f"data:image/png;base64,{farmer_b64}"
        else:
            farmer_img_src = "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=100&q=70"

        st.markdown(f'''
<div class="v-header {h_cls}">
<div style="font-size:1.3rem;font-weight:800;letter-spacing:-0.5px;">{ico} {h_msg}</div>
<div style="font-size:1rem;font-weight:700;opacity:0.9;white-space:nowrap;">{conf_pct}% Confident</div>
</div>
''', unsafe_allow_html=True)

        # ── 2. FARMER MESSAGE CARD ────────────────────────────────────────────
        f_msg = "Don\\'t worry, this is common! Just follow the steps below to protect your yield." if sev != "NONE" else "Great job! Your crop looks amazing. Keep up the good work!"
        st.markdown(f'''
<div class="v-msg-card">
<img src="{farmer_img_src}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:2px solid #16a34a;" />
<div class="v-msg-text">{f_msg}</div>
</div>
''', unsafe_allow_html=True)

        # ── 3. VISUAL ACTIONS GRID ────────────────────────────────────────────
        st.markdown('<div class="section-lbl">&#128640; 4 SIMPLE STEPS</div>', unsafe_allow_html=True)
        
        # We enforce ultra-short strings
        def _get_short_action(act_text):
            low = act_text.lower()
            if "drain" in low or "water" in low: return "&#128167;", "Improve drainage"
            if "spray" in low or "fungicide" in low or "chemical" in low: return "&#129514;", "Spray medicine today"
            if "remov" in low or "destroy" in low or "burn" in low: return "&#9889;", "Remove infected leaves"
            if "fertilizer" in low or "nitrogen" in low: return "&#128683;", "Avoid fertilizer"
            if "monitor" in low or "watch" in low: return "&#128269;", "Monitor spread"
            if "spac" in low or "thin" in low: return "&#127807;", "Increase crop spacing"
            return "&#10004;&#65039;", act_text.split('.')[0][:25] + "..."

        actions_html = '<div class="v-action-grid">'
        if sev in ("NONE", "LOW") and disease_name == "Healthy":
            actions_list = [("&#128167;", "Maintain hydration"), ("&#128269;", "Check weekly")]
        else:
            actions_list = [_get_short_action(a) for a in insight.immediate_actions[:4]]
            if not actions_list:
                actions_list = [("&#129514;", "Spray medicine today"), ("&#9889;", "Remove infected leaves"), ("&#128683;", "Avoid fertilizer"), ("&#128269;", "Monitor spread")]

        for ico, txt in actions_list:
            actions_html += f'''
<div class="v-action">
<div class="v-action-ico">{ico}</div>
<div class="v-action-txt">{txt}</div>
</div>
'''
        actions_html += '</div>'
        st.markdown(actions_html, unsafe_allow_html=True)

        # ── 4. SIMPLIFIED WEATHER ─────────────────────────────────────────────
        st.markdown('<div class="section-lbl">&#127780;&#65039; WEATHER FACTOR</div>', unsafe_allow_html=True)
        
        if wx.get("available"):
            if wx["risk_level"] == "HIGH":
                w_msg = "&#9928;&#65039; Rain expected &rarr; disease may spread faster!"
                w_col = "#dc2626"
            elif wx["risk_level"] == "MODERATE":
                w_msg = "&#127781;&#65039; Humid conditions &rarr; monitor closely."
                w_col = "#d97706"
            else:
                w_msg = "&#9728;&#65039; Dry weather &rarr; spread is unlikely."
                w_col = "#16a34a"
        else:
            w_msg = "&#127780;&#65039; Weather unknown &rarr; stay vigilant."
            w_col = "#6b7280"
            
        st.markdown(f'''
<div class="v-card" style="text-align:center;font-size:1.1rem;font-weight:700;color:{w_col};border-left:4px solid {w_col};">
{w_msg}
</div>
''', unsafe_allow_html=True)


        # ── 5. EXPERT ADVISORY HIDDEN CONTENT ──────────────────────────────────
        ui_divider()
        with st.expander("🔬 View Detailed Expert Analysis", expanded=False):
            st.markdown(f"**Disease Overview:** {insight.summary}")
            st.markdown(f"**Causing Factors:** {insight.cause}")
            st.markdown(f"**Prevention Measures:** {insight.prevention}")
"""

# Replace the text "4. VISUAL ANALYSIS (expander)" with "6. VISUAL ANALYSIS (expander)"
# so it flows nicely with the numbers, but I am just appending it before the end_marker

with open(file_path, "w", encoding="utf-8") as f:
    f.write(part1 + start_marker + "\n" + new_results + "\n        " + end_marker + part2)

print("Done replacing.")
