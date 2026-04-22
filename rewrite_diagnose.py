import re

file_path = "c:/Users/pujar/OneDrive/Desktop/AgriShield-TN/app/pages/2_Analyze_Leaf.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Insert CSS before `# ── Page hero banner V2`
css_string = """
# ── Custom CSS for Redesign ───────────────────────────────────────────────────
st.markdown('''
<style>
.premium-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    position: relative;
    overflow: hidden;
    margin-bottom: 16px;
    border: 1px solid #E5E7EB;
}
.section-lbl {
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #16a34a;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.hero-card--safe {
    background: linear-gradient(135deg, #14532d, #16a34a);
    color: white;
    border: none;
    box-shadow: 0 8px 30px rgba(22,163,74,0.3);
}
.hero-card--caution {
    background: linear-gradient(135deg, #78350f, #d97706);
    color: white;
    border: none;
    box-shadow: 0 8px 30px rgba(217,119,6,0.3);
}
.hero-card--action {
    background: linear-gradient(135deg, #7f1d1d, #dc2626);
    color: white;
    border: none;
    box-shadow: 0 8px 30px rgba(220,38,38,0.3);
}
.hero-title {
    font-size: 1.8rem;
    font-weight: 800;
    margin-bottom: 4px;
    letter-spacing: -0.5px;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1rem;
    font-weight: 600;
    opacity: 0.95;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.hero-badge {
    background: rgba(255,255,255,0.2);
    border-radius: 999px;
    padding: 6px 14px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
    font-weight: 700;
    backdrop-filter: blur(8px);
}
.hero-farmer-img {
    position: absolute;
    bottom: -10px;
    right: 10px;
    width: 150px;
    height: auto;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.2));
}

.wx-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.3rem;
    font-weight: 800;
    color: #111827;
    margin-bottom: 10px;
}
.wx-card-sub {
    font-size: 0.9rem;
    color: #4B5563;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 16px;
}
.wx-data-row {
    display: flex;
    gap: 8px;
    border-top: 1px solid #F3F4F6;
    padding-top: 16px;
}
.wx-data-col {
    flex: 1;
    text-align: center;
    background: #F9FAF8;
    border-radius: 12px;
    padding: 10px 4px;
    border: 1px solid #E5E7EB;
}
.wx-val { font-size: 1.1rem; font-weight: 800; color: #111827; margin-bottom: 2px; }
.wx-lbl { font-size: 0.65rem; color: #6B7280; font-weight: 700; text-transform: uppercase; }

.adv-card {
    background: linear-gradient(to right, #F0FDF4, #DCFCE7);
    border: 1px solid #BBF7D0;
}
.adv-card-header {
    font-size: 1.3rem;
    font-weight: 800;
    color: #14532D;
    margin-bottom: 8px;
}
.adv-card-text {
    font-size: 0.95rem;
    color: #166534;
    line-height: 1.6;
    max-width: 65%;
    font-weight: 500;
    margin-bottom: 20px;
}
.adv-card-tamil {
    font-family: 'Noto Sans Tamil', sans-serif;
    font-size: 0.85rem;
    opacity: 0.85;
    margin-top: 8px;
}
.adv-farmer-img {
    position: absolute;
    bottom: -10px;
    right: 0px;
    width: 140px;
}
.adv-footer-brand {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(22,163,74,0.15);
    color: #15803d;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 700;
}
</style>
''', unsafe_allow_html=True)
"""
if "# ── Custom CSS for Redesign" not in content:
    content = content.replace('# ── Page hero banner V2 ──────────────────────────', css_string + '\n# ── Page hero banner V2 ──────────────────────────')


# 2. Replace the diagnosis header results part.
# The area ranges from `# ── 1. DIAGNOSIS HEADER (3 columns) ───────────────────────────────────` 
# all the way to before `# ── 4. VISUAL ANALYSIS (expander) ─────────────────────────────────────`

start_marker = "# ── 1. DIAGNOSIS HEADER (3 columns) ───────────────────────────────────"
end_marker = "# ── 4. VISUAL ANALYSIS (expander) ─────────────────────────────────────"

if start_marker in content and end_marker in content:
    part1, rest = content.split(start_marker, 1)
    middle, part2 = rest.split(end_marker, 1)

    new_results = """
        # ── 1. HERO STATUS CARD ───────────────────────────────────────────────
        ui_divider()
        st.markdown('<div class="section-lbl">&#10004;&#65039; AI CROP DIAGNOSTIC TOOL</div>', unsafe_allow_html=True)

        if sev in ("NONE", "LOW"):
            card_class = "hero-card--safe"
            hero_title = "CROP HEALTH IS GOOD"
            hero_sub = "&#127811; No Disease Detected"
            icon = "&#9989;"
            farmer_img = "https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Smiling%20Face%20with%20Sunglasses.png"
        elif sev == "MODERATE":
            card_class = "hero-card--caution"
            hero_title = "CAUTION NEEDED"
            hero_sub = f"&#9888;&#65039; {disease_name}"
            icon = "&#9888;&#65039;"
            farmer_img = "https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Thinking%20Face.png"
        else:
            card_class = "hero-card--action"
            hero_title = "ACTION REQUIRED"
            hero_sub = f"&#128308; {disease_name}"
            icon = "&#128680;"
            farmer_img = "https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Face%20Screaming%20in%20Fear.png"

        conf_pct = round(confidence * 100)
        
        st.markdown(f'''
        <div class="premium-card {card_class}">
            <div class="hero-title">{hero_title}</div>
            <div class="hero-subtitle">{hero_sub}</div>
            <div class="hero-badge">
                <span>{icon} SAFE</span>
                <span style="opacity:0.5;">&rarr;</span>
                <span>Confident {conf_pct}%</span>
            </div>
            <img src="{farmer_img}" class="hero-farmer-img" />
        </div>
        ''', unsafe_allow_html=True)

        # ── 2. WEATHER RISK CARD ──────────────────────────────────────────────
        st.markdown('<div class="section-lbl">&#127780;&#65039; WEATHER RISK TODAY</div>', unsafe_allow_html=True)
        
        if wx.get("available"):
            _rl = wx["risk_level"]
            _wx_title = "All Clear! Low Spread Risk" if _rl == "LOW" else ("Caution! Conditions favor spread" if _rl == "MODERATE" else "High Risk of Disease Spread!")
            _wx_icon = "&#9728;&#65039;" if _rl == "LOW" else "&#9928;&#65039;"
            _wx_sub = "Hot & Dry: Less Spread" if wx["temp"] > 30 and wx["humidity"] < 60 else "Conditions may increase spread"
            _chk = "&#10004;&#65039;" if _rl == "LOW" else "&#9888;&#65039;"
            
            st.markdown(f'''
            <div class="premium-card">
                <div class="wx-card-header">{_wx_icon} {_wx_title} <span style="color:#16a34a;margin-left:auto;">{_chk}</span></div>
                <div class="wx-card-sub"><span style="color:#16a34a;font-size:1rem;">&#11093;</span> {_wx_sub} <span style="color:#16a34a;margin-left:auto;">{_chk}</span></div>
                <div class="wx-data-row">
                    <div class="wx-data-col">
                        <div style="font-size:1.5rem;margin-bottom:6px;">&#127777;&#65039;</div>
                        <div class="wx-val">{wx["temp"]}°C</div>
                        <div class="wx-lbl">Temperature</div>
                    </div>
                    <div class="wx-data-col">
                        <div style="font-size:1.5rem;margin-bottom:6px;">&#128167;</div>
                        <div class="wx-val">{wx["humidity"]}%</div>
                        <div class="wx-lbl">Humidity</div>
                    </div>
                    <div class="wx-data-col">
                        <div style="font-size:1.5rem;margin-bottom:6px;">&#9729;&#65039;</div>
                        <div class="wx-val">{wx["rain_now"]} mm</div>
                        <div class="wx-lbl">Rain Today</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="premium-card">
                <div class="wx-card-header">&#9728;&#65039; Weather Data Unavailable</div>
                <div class="wx-card-sub">Please select a district to view weather risk.</div>
            </div>
            ''', unsafe_allow_html=True)

        # ── 3. TODAY'S ADVICE CARD ────────────────────────────────────────────
        st.markdown('<div class="section-lbl">&#127807; TODAY\\'S ADVICE</div>', unsafe_allow_html=True)
        
        advice_en = insight.summary.split('.')[0] + "!"
        # Simple tamil extraction or fallback
        advice_ta = "நல்ல வானிலை! தொடர்ந்து கண்காணிக்கவும்." if sev in ("NONE", "LOW") else "பாதிப்பு உள்ளது. உடனடியாக நடவடிக்கை எடுக்கவும்!"
        
        st.markdown(f'''
            <div class="premium-card adv-card">
                <div class="adv-card-header">{advice_en}</div>
                <div class="adv-card-text">
                    Keep monitoring the field and ensure proper crop health management.
                    <div class="adv-card-tamil">{advice_ta}</div>
                </div>
                <div class="adv-footer-brand">&#127806; AgriShield-TN</div>
                <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/People/Man%20Farmer.png" class="adv-farmer-img" />
            </div>
        ''', unsafe_allow_html=True)

        """

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(part1 + start_marker + "\n" + new_results + "\n        " + end_marker + part2)
    print("Done replacing.")
else:
    print("Failed to find markers")
