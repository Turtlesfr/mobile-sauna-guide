#!/usr/bin/env python3
"""Generate the mobile-sauna mini-site: English, metric, images, diagrams, calculator."""
import json, html, base64, datetime, glob, os, re

R = json.load(open('research-data.json'))['result']

# ---------------------------------------------------------------- normalization
# Convert imperial -> metric (the data carried some imperial units).
METRIC = [
    ('5x8 ft sauna can be built under 2000 lb gross, but a 6x12 ft build runs 2500-3000 lb',
     '1.5×2.4 m sauna can be built under ~900 kg gross, but a 1.8×3.7 m build runs 1150–1360 kg'),
    ('a 3500 lb (1588 kg) single axle', 'a 1588 kg single axle'),
    ('~500 lb (227 kg)', '~227 kg'),
    ('~3000 lb (1360 kg)', '~1360 kg'),
    ('1.350 kg (3000 lb)', '1.350 kg (~1,35 t)'),
    ('2/32 in', '1,6 mm'),
    ('about 18 inches (~460 mm)', 'about 460 mm'),
    ('25 sq inches (about 160 cm2), with 30 sq inches (about 195 cm2)', '160 cm², with 195 cm²'),
    ('~25-30 sq inches', '~160–195 cm²'),
    ('at least 25 sq inches', 'at least 160 cm²'),
    ('12-24 inches (300-600 mm)', '300–600 mm'),
    ('5-8 cm (2-3 inches)', '5–8 cm'),
    ('2-4 inches across', '5–10 cm across'),
    ('overlap seams 2-3 inches', 'overlap seams 5–8 cm'),
    ('under 2000 lb / ~907 kg', 'under ~907 kg'),
    ('1 kW per 50 cubic feet (about 1.4 m3)', '1 kW per ~1,4 m³'),
    ('6 mm per 30 cm (1/4 in per foot, roughly 1:50 to 1:30)', '6 mm per 30 cm (a 1:50–1:30 fall)'),
    ('2x4 at 16" (≈400 mm) on centre', '2x4 at 400 mm on centre'),
    ("('every inch counts')", "('every centimetre counts')"),
    ('3/4" plywood core', '18 mm plywood core'),
    ('A solid 1.5-2" wood door', 'A solid 40–50 mm wood door'),
    ('400-600 mm / 18 in figures', '400–600 mm figures'),
    ('threaded rod (≈5/8" / 16 mm)', 'threaded rod (≈16 mm)'),
    ('1 cm (3/8"-1/2") gap', '1 cm gap'),
    ('Use 24-gauge-or-thicker sheet metal OR cement board 1/2 inch+',
     'Use 0,6 mm-or-thicker sheet metal OR cement board 12 mm+'),
    ('66% (18 in becomes 6 in)', '66% (460 mm becomes ~150 mm)'),
    ('4-6 inch (100-150 mm) duct', '100–150 mm duct'),
    ('12"x12" is typical', '30×30 cm is typical'),
    ('~26" x 6\'5" giving ~24.5" x 6\'4" of actual opening',
     '~660 mm × 1.96 m giving ~620 mm × 1.93 m of actual opening'),
    ('Pino Seco Machihembrado 3/4" x 5" 3,2 m', 'Pino Seco Machihembrado 19×125 mm × 3,2 m'),
    ('Pino Tinglado Seco Cepillado 3/4x5 cm x 3.2 m', 'Pino Tinglado Seco Cepillado 19×125 mm × 3,2 m'),
    ('Pino Tinglado Seco Cepillado 3/4x5 cm 3,2 m', 'Pino Tinglado Seco Cepillado 19×125 mm × 3,2 m'),
    ('Pino Tinglado Seco Cepillado 3/4x5 cm', 'Pino Tinglado Seco Cepillado 19×125 mm'),
    ('Pino Tinglado Seco Cepillado 3/4x5', 'Pino Tinglado Seco Cepillado 19×125 mm'),
]
# Translate the Spanish chileNotes (wood-vs-electric section) + stray Spanish.
SPANISH = {
 "Empalme monofásico estándar en Chile llega hasta 40 A / ~8.8 kW para toda la casa (fuente CGE). Un calefactor de 6 kW solo ya consume ~28 A: deja casi sin margen al resto de la casa.":
 "A standard Chilean single-phase connection (empalme monofásico) maxes out at 40 A / ~8.8 kW for the WHOLE house (source: CGE). A 6 kW heater alone already draws ~28 A, leaving almost nothing for the rest of the house.",
 "Para 9 kW o uso intenso conviene 380V trifásico, lo que implica aumento de potencia ante la distribuidora (CGE, Enel, Chilquinta, CGE según zona) y un instalador autorizado SEC. No es legal hacerlo uno mismo en Chile.":
 "For 9 kW or heavy use you really want 380V three-phase (trifásico), which means a power-capacity upgrade with your utility (CGE, Enel or Chilquinta depending on the zone) and a licensed SEC installer. Doing this yourself is not legal in Chile.",
 "Calefactores eléctricos de sauna en Chile: ProSauna (prosauna.cl) y Piscineria venden modelos Keya de 3/4.5/6/9/12 kW; precios por cotización (WhatsApp/teléfono), no publicados online.":
 "Electric sauna heaters in Chile: ProSauna (prosauna.cl) and Piscineria sell Keya-type units in 3 / 4.5 / 6 / 9 / 12 kW; prices by quote (WhatsApp/phone), not published online.",
 "Harvia tiene representación en Chile (harvia.cl, Estación Central, Santiago) para quienes prefieran marca premium, pero a mayor costo que los genéricos Keya.":
 "Harvia has a Chilean representative (harvia.cl, Estación Central, Santiago) if you prefer a premium brand, but at a higher cost than the generic Keya units.",
 "Estufas a leña para sauna hechas en Chile: BuenaCaldera (Estufa Leña Sauna 15A-15D) $504.000-$660.000 CLP; Nordicasa (diseño finlandés, 8-18 m3) $1.290.000 CLP. Kit de chimenea BuenaCaldera ~$386.000 CLP.":
 "Chilean-made sauna wood stoves: BuenaCaldera (Estufa Leña Sauna 15A–15D) $504.000–$660.000 CLP; Nordicasa (Finnish design, 8–18 m³) $1.290.000 CLP. BuenaCaldera chimney kit ~$386.000 CLP.",
 "Piedras volcánicas para sauna se venden por saco de 25 kg (~$16.000 CLP en BuenaCaldera); también en tinascalientes.cl. Necesitas 20-30 kg según el calefactor.":
 "Volcanic sauna stones are sold by the 25 kg sack (~$16.000 CLP at BuenaCaldera; also tinascalientes.cl). You need 20–30 kg depending on the heater.",
 "Madera de banca: álamo es la opción local de bajo costo y sin resina. Pino radiata abunda y es barato (Sodimac/Easy/Construmart/barracas) pero solo para estructura, no para superficies en contacto con la piel.":
 "Bench wood: álamo (poplar) is the low-cost, resin-free local choice. Radiata pine is abundant and cheap (Sodimac / Easy / Construmart / barracas) but for the structure only, never for skin-contact surfaces.",
 "Estufas a leña genéricas (salamandras) también aparecen en MercadoLibre Chile desde ~$57.000 CLP, pero las de sauna con depósito de piedras y/o agua son las correctas; una salamandra común no está diseñada para sostener piedras ni alcanzar el perfil térmico de sauna.":
 "Generic wood stoves (salamandras) also appear on MercadoLibre Chile from ~$57.000 CLP, but a proper sauna stove with a stone box and/or water tank is the right tool; an ordinary salamandra isn't designed to hold stones or reach sauna temperatures.",
 "Cotización (no publicado)": "Quote only (not listed)",
 "Cotización (no publicado)": "Quote only (not listed)",
}

def norm(s):
    if SPANISH.get(s):
        return SPANISH[s]
    for a, b in METRIC:
        s = s.replace(a, b)
    return s

def walk_norm(o):
    if isinstance(o, str):
        return norm(o)
    if isinstance(o, list):
        return [walk_norm(x) for x in o]
    if isinstance(o, dict):
        return {k: walk_norm(v) for k, v in o.items()}
    return o

R = walk_norm(R)
findings = R['findings']
budget = R['budget']
by_key = {f['sectionKey']: f for f in findings}

def esc(s):
    return html.escape(str(s), quote=True)

def img_uri(name):
    with open(f'img/{name}.jpg', 'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()

# ---------------------------------------------------------------- section meta
META = {
    'trailer':       ('01', 'The trailer', 'Buying & prepping a second-hand trailer', '🚚'),
    'structure':     ('02', 'Structure', 'Framing & anchoring to the chassis', '🏗️'),
    'insulation':    ('03', 'Insulation', 'Insulation & the all-important vapor barrier', '🧱'),
    'woodvselectric':('04', 'Heater', 'Wood stove vs electric — the decision', '🔥'),
    'stovesafety':   ('05', 'Fire safety', 'Clearances, heat shields, flue & CO', '⚠️'),
    'woodspecies':   ('06', 'Woods', 'Chilean wood species for benches & cladding', '🪵'),
    'interior':      ('07', 'Interior', 'Benches, door, glass, lighting, fixtures', '🛋️'),
    'ventilation':   ('08', 'Ventilation', 'Ventilation & löyly (the steam experience)', '💨'),
    'sourcing':      ('09', 'Where to buy', 'Local sourcing map for Santiago / RM', '🛒'),
    'pitfalls':      ('10', 'Mistakes', 'Common mistakes, maintenance & winterizing', '🧯'),
}
ORDER = list(META.keys())

# ---------------------------------------------------------------- SVG diagrams
DIAG = {}
DIAG['weight'] = ('''
<svg viewBox="0 0 780 280" class="diagram" role="img" aria-label="Weight distribution on the trailer">
 <defs><marker id="aw" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto">
   <path d="M0 0 L6 3 L0 6 Z" fill="#e8732c"/></marker>
 <marker id="ag" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto">
   <path d="M0 0 L6 3 L0 6 Z" fill="#7fb685"/></marker></defs>
 <line x1="20" y1="246" x2="760" y2="246" stroke="#3a2e24" stroke-width="2"/>
 <line x1="150" y1="166" x2="60" y2="198" stroke="#6b5a48" stroke-width="6" stroke-linecap="round"/>
 <circle cx="54" cy="200" r="8" fill="#6b5a48"/>
 <rect x="150" y="158" width="470" height="16" fill="#4a3a2c"/>
 <circle cx="505" cy="214" r="30" fill="#2a211a" stroke="#9a8a78" stroke-width="3"/>
 <circle cx="505" cy="214" r="6" fill="#9a8a78"/>
 <line x1="505" y1="174" x2="505" y2="186" stroke="#9a8a78" stroke-dasharray="4 4"/>
 <text x="505" y="170" text-anchor="middle" class="dg-s">axle</text>
 <rect x="200" y="84" width="360" height="74" rx="4" fill="#caa472"/>
 <rect x="248" y="56" width="14" height="30" fill="#2a211a"/>
 <text x="380" y="128" text-anchor="middle" class="dg-b" fill="#1b1612">sauna cabin</text>
 <line x1="452" y1="84" x2="452" y2="158" stroke="#e8732c" stroke-width="2" stroke-dasharray="5 4"/>
 <circle cx="452" cy="84" r="6" fill="#e8732c"/>
 <text x="452" y="76" text-anchor="middle" class="dg-e">centre of gravity</text>
 <line x1="458" y1="206" x2="500" y2="206" stroke="#e8732c" stroke-width="2" marker-end="url(#aw)"/>
 <text x="455" y="222" text-anchor="end" class="dg-s" fill="#f4a259">forward of axle</text>
 <line x1="72" y1="210" x2="72" y2="238" stroke="#7fb685" stroke-width="3" marker-end="url(#ag)"/>
 <text x="86" y="228" class="dg-s" fill="#7fb685">tongue weight 10–15%</text>
</svg>''', 'Keep the centre of gravity slightly forward of the axle and tongue weight at 10–15% of total — this is what stops a single-axle trailer from fishtailing.')

DIAG['floorplan'] = ('''
<svg viewBox="0 0 720 420" class="diagram" role="img" aria-label="Top-view floor plan">
 <defs><marker id="af" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#9a8a78"/></marker></defs>
 <rect x="90" y="70" width="540" height="270" rx="6" fill="#221b15" stroke="#caa472" stroke-width="2.5"/>
 <!-- benches L -->
 <rect x="100" y="80" width="150" height="250" fill="#4a3a2c" opacity=".85"/>
 <line x1="175" y1="80" x2="175" y2="330" stroke="#2a211a" stroke-width="2"/>
 <text x="175" y="210" text-anchor="middle" class="dg-s" transform="rotate(-90 175 210)">two-tier benches</text>
 <!-- stove -->
 <rect x="540" y="262" width="68" height="68" rx="4" fill="#1b1612" stroke="#e8732c" stroke-width="2"/>
 <circle cx="574" cy="280" r="4" fill="#9a8a78"/><circle cx="586" cy="288" r="4" fill="#9a8a78"/><circle cx="562" cy="290" r="4" fill="#9a8a78"/>
 <text x="574" y="320" text-anchor="middle" class="dg-e">stove</text>
 <!-- door -->
 <path d="M630 150 a60 60 0 0 1 -60 60" fill="none" stroke="#7fb685" stroke-width="2" stroke-dasharray="4 4"/>
 <rect x="626" y="150" width="8" height="60" fill="#7fb685"/>
 <text x="600" y="135" text-anchor="middle" class="dg-s" fill="#7fb685">door (opens out)</text>
 <!-- vents -->
 <rect x="600" y="322" width="30" height="10" fill="#8fc0f0"/><text x="585" y="332" text-anchor="end" class="dg-s" fill="#8fc0f0">low intake</text>
 <rect x="90" y="78" width="30" height="10" fill="#8fc0f0"/><text x="126" y="70" class="dg-s" fill="#8fc0f0">high exhaust (opposite)</text>
 <!-- dims -->
 <line x1="90" y1="360" x2="630" y2="360" stroke="#9a8a78" marker-start="url(#af)" marker-end="url(#af)"/>
 <text x="360" y="378" text-anchor="middle" class="dg-s">length ≈ 3,0 m</text>
 <line x1="660" y1="70" x2="660" y2="340" stroke="#9a8a78" marker-start="url(#af)" marker-end="url(#af)"/>
 <text x="676" y="210" text-anchor="middle" class="dg-s" transform="rotate(90 676 210)">width ≈ 1,7 m</text>
</svg>''', 'A workable 1,7 × 3,0 m layout: L-shaped benches along two walls, stove by the door, fresh-air intake low next to the stove and an adjustable exhaust high on the opposite wall.')

DIAG['wall'] = ('''
<svg viewBox="0 0 720 300" class="diagram" role="img" aria-label="Wall cross-section layers">
 <text x="60" y="40" class="dg-s" fill="#9a8a78">◀ cold / exterior</text>
 <text x="660" y="40" text-anchor="end" class="dg-e">hot / interior ▶</text>
 <!-- layers L->R -->
 <rect x="60"  y="60" width="34" height="190" fill="#6b5a48"/>
 <rect x="98"  y="60" width="10" height="190" fill="#2a211a"/>
 <rect x="112" y="60" width="150" height="190" fill="#caa472" opacity=".35"/>
 <g stroke="#caa472" stroke-width="2"><line x1="120" y1="60" x2="120" y2="250"/><line x1="254" y1="60" x2="254" y2="250"/></g>
 <rect x="266" y="60" width="12" height="190" fill="#d9d2c4"/>
 <rect x="282" y="60" width="40" height="190" fill="#1b1612"/>
 <rect x="326" y="60" width="34" height="190" fill="#caa472"/>
 <!-- labels -->
 <g class="dg-lab">
  <line x1="77" y1="250" x2="77" y2="268" stroke="#3a2e24"/><text x="77" y="282" text-anchor="middle" class="dg-s">ext. cladding<tspan x="77" dy="13">pino impreg.</tspan></text>
  <line x1="187" y1="250" x2="187" y2="266" stroke="#3a2e24"/><text x="187" y="282" text-anchor="middle" class="dg-s">frame + mineral wool</text>
  <line x1="272" y1="60" x2="272" y2="46" stroke="#3a2e24"/><text x="272" y="40" text-anchor="middle" class="dg-e">foil vapor barrier</text>
  <line x1="302" y1="250" x2="302" y2="266" stroke="#3a2e24"/><text x="302" y="282" text-anchor="middle" class="dg-s">air gap 19–25 mm</text>
  <line x1="343" y1="250" x2="343" y2="266" stroke="#3a2e24"/><text x="343" y="282" text-anchor="middle" class="dg-s">álamo lining</text>
 </g>
 <text x="470" y="120" class="dg-cap2">Layer order (inside → out):</text>
 <text x="470" y="146" class="dg-s">cladding · air gap · FOIL · wool · frame · wrap · cladding</text>
 <text x="470" y="184" class="dg-cap2">R-value targets:</text>
 <text x="470" y="208" class="dg-s">walls R-15–21 · ceiling R-26–30</text>
 <text x="470" y="240" class="dg-e">Foil on the HOT side only. Tape every seam.</text>
</svg>''', 'The wall “sandwich”, in order: interior álamo lining → 19–25 mm air gap → continuous aluminium foil on the hot side → mineral/glass wool in the frame → breathable wrap → exterior cladding. Foil seams and every penetration get foil-taped.')

DIAG['clearance'] = ('''
<svg viewBox="0 0 720 360" class="diagram" role="img" aria-label="Stove clearances, heat shield and flue">
 <!-- roof -->
 <line x1="80" y1="70" x2="430" y2="40" stroke="#6b5a48" stroke-width="8"/>
 <!-- wall -->
 <rect x="92" y="70" width="22" height="250" fill="#6b5a48"/>
 <text x="103" y="338" text-anchor="middle" class="dg-s">wood wall</text>
 <!-- heat shield with air gap -->
 <rect x="132" y="150" width="10" height="150" fill="#9a8a78"/>
 <text x="170" y="138" class="dg-s" fill="#8fc0f0">heat shield (fibrocemento / metal)</text>
 <line x1="114" y1="312" x2="142" y2="312" stroke="#8fc0f0"/><text x="128" y="328" text-anchor="middle" class="dg-s" fill="#8fc0f0">25 mm gap</text>
 <!-- stove -->
 <rect x="190" y="200" width="120" height="100" rx="4" fill="#1b1612" stroke="#e8732c" stroke-width="2"/>
 <ellipse cx="250" cy="200" rx="46" ry="10" fill="#2a211a" stroke="#9a8a78"/>
 <circle cx="236" cy="197" r="5" fill="#9a8a78"/><circle cx="252" cy="200" r="5" fill="#9a8a78"/><circle cx="266" cy="196" r="5" fill="#9a8a78"/>
 <text x="250" y="258" text-anchor="middle" class="dg-e">wood stove</text>
 <!-- hearth -->
 <rect x="160" y="300" width="200" height="14" fill="#9a8a78"/>
 <text x="260" y="334" text-anchor="middle" class="dg-s">non-combustible hearth — 300 mm sides / 450 mm front</text>
 <!-- flue -->
 <rect x="238" y="60" width="24" height="140" fill="#2a211a" stroke="#9a8a78"/>
 <rect x="232" y="52" width="36" height="12" fill="#9a8a78"/>
 <text x="300" y="86" class="dg-cap2">double-wall insulated flue</text>
 <text x="300" y="108" class="dg-s">through ceiling &amp; roof, with</text>
 <text x="300" y="126" class="dg-s">flashing + storm collar + spark cap</text>
 <text x="430" y="210" class="dg-e">A ventilated shield cuts</text>
 <text x="430" y="232" class="dg-e">clearance up to 66%</text>
 <text x="430" y="254" class="dg-s">(≈460 mm → ~150 mm).</text>
 <text x="430" y="284" class="dg-s">Always follow the stove's</text>
 <text x="430" y="302" class="dg-s">own rating plate.</text>
</svg>''', 'In a 1,7 m-wide cabin you can rarely keep 460 mm of bare clearance — so a fibrocemento or metal heat shield on a 25 mm ventilated air gap is mandatory. Stove sits on a non-combustible hearth; the flue is double-wall where it crosses the roof.')

DIAG['ventilation'] = ('''
<svg viewBox="0 0 720 320" class="diagram" role="img" aria-label="Ventilation airflow">
 <defs><marker id="av" markerWidth="10" markerHeight="10" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#8fc0f0"/></marker></defs>
 <rect x="80" y="60" width="560" height="220" rx="6" fill="#221b15" stroke="#caa472" stroke-width="2.5"/>
 <rect x="120" y="190" width="80" height="90" rx="4" fill="#1b1612" stroke="#e8732c" stroke-width="2"/>
 <text x="160" y="240" text-anchor="middle" class="dg-e">stove</text>
 <!-- intake low -->
 <line x1="40" y1="262" x2="120" y2="262" stroke="#8fc0f0" stroke-width="3" marker-end="url(#av)"/>
 <text x="40" y="252" class="dg-s" fill="#8fc0f0">fresh-air intake (low, by stove)</text>
 <!-- exhaust high -->
 <line x1="600" y1="92" x2="680" y2="92" stroke="#8fc0f0" stroke-width="3" marker-end="url(#av)"/>
 <text x="430" y="84" class="dg-s" fill="#8fc0f0">adjustable exhaust (high, opposite wall)</text>
 <!-- convection loop -->
 <path d="M210 250 C300 250 300 110 420 110 C520 110 540 150 560 110" fill="none" stroke="#f4a259" stroke-width="2.5" stroke-dasharray="6 5"/>
 <path d="M560 130 C520 230 360 230 230 250" fill="none" stroke="#f4a259" stroke-width="2.5" stroke-dasharray="6 5"/>
 <text x="380" y="180" text-anchor="middle" class="dg-cap2">convection loop</text>
 <text x="360" y="306" text-anchor="middle" class="dg-s">Both vents closeable — open to breathe the room dry after each session.</text>
</svg>''', 'Air enters low beside the stove, rises through the heat, and leaves high on the opposite wall. The same loop that feeds combustion and prevents CO build-up also gives a good, even löyly.')

DIAG['bench'] = ('''
<svg viewBox="0 0 700 340" class="diagram" role="img" aria-label="Two-tier bench heights">
 <defs><marker id="ab" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#9a8a78"/></marker></defs>
 <line x1="40" y1="300" x2="660" y2="300" stroke="#3a2e24" stroke-width="2"/>
 <!-- lower bench -->
 <rect x="120" y="250" width="430" height="16" fill="#caa472"/>
 <rect x="130" y="266" width="10" height="34" fill="#6b5a48"/><rect x="530" y="266" width="10" height="34" fill="#6b5a48"/>
 <!-- upper bench -->
 <rect x="120" y="150" width="300" height="16" fill="#caa472"/>
 <rect x="130" y="166" width="10" height="84" fill="#6b5a48"/><rect x="400" y="166" width="10" height="84" fill="#6b5a48"/>
 <!-- reclining figure hint -->
 <circle cx="160" cy="138" r="10" fill="#9a8a78"/><rect x="170" y="142" width="170" height="8" rx="4" fill="#9a8a78"/>
 <!-- stove/stones to the right -->
 <rect x="560" y="200" width="70" height="100" fill="#1b1612" stroke="#e8732c" stroke-width="2"/>
 <ellipse cx="595" cy="200" rx="30" ry="8" fill="#2a211a" stroke="#9a8a78"/>
 <text x="595" y="250" text-anchor="middle" class="dg-e">stones</text>
 <!-- dims -->
 <line x1="80" y1="150" x2="80" y2="300" stroke="#9a8a78" marker-start="url(#ab)" marker-end="url(#ab)"/>
 <text x="74" y="225" text-anchor="end" class="dg-s">90–105 cm</text>
 <line x1="450" y1="250" x2="450" y2="300" stroke="#9a8a78" marker-start="url(#ab)" marker-end="url(#ab)"/>
 <text x="462" y="280" class="dg-s">~45 cm</text>
 <text x="270" y="190" text-anchor="middle" class="dg-cap2">upper bench — sit/lie in the heat</text>
 <text x="320" y="328" text-anchor="middle" class="dg-s">Upper tier near the top of the stones · hidden fasteners (no hot metal on skin) · álamo wood</text>
</svg>''', 'Two tiers: a high bench (90–105 cm) where you actually sit or lie in the hot zone near the top of the stones, and a low step bench (~45 cm). All álamo, with hidden fasteners so no metal touches skin.')

# ---------------------------------------------------------------- materials
MATERIALS = [
 ('mat_pino','Pino radiata — framing','Cheap structural studs (2×2 / 2×3). Frame & hidden parts only, never on skin.','Sodimac · Construmart · barraca'),
 ('mat_alamo','Álamo (poplar) — benches & lining','Pale, resin-free, stays cool to the touch. The Chilean bench/lining wood.','Barracas · Hidrotinas · Madefan'),
 ('mat_cladding','Machihembrado — interior lining','Tongue-and-groove boards for walls & ceiling, nailed over the air gap.','Sodimac · Easy · barraca'),
 ('mat_impregnado','Pino impregnado — exterior','Green-tinted pressure-treated pine for the outer skin & deck. Outdoor only.','Sodimac · Arauco Deck'),
 ('mat_fibrocemento','Fibrocemento / Volcanboard','Rot-proof grey board for exterior skin and stove heat shields.','Sodimac · Construmart'),
 ('mat_osb','OSB structural panel','Subfloor and wall bracing for towing stiffness. ~$5.500+/sheet.','Sodimac · MercadoLibre'),
 ('mat_glasswool','Lana de vidrio (glass wool)','Cheapest insulation — buy unfaced (libre). ~$2.500/m².','Sodimac'),
 ('mat_mineralwool','Lana mineral (rock wool)','Better, more fire-resistant insulation. ~$4.500/m².','Sodimac'),
 ('mat_foil','Aluminium foil vapor barrier','Goes on the HOT side: reflects heat + blocks moisture. Foil, not plastic.','Sodimac · Aislacel'),
 ('mat_foiltape','Foil tape','Seals every foil seam & penetration. Aluminium tape, not duct tape.','Sodimac'),
 ('stove','Estufa de sauna (wood stove)','Chilean-made stove with a stone box. ~$504–660k.','BuenaCaldera · Nordicasa'),
 ('mat_flue','Double-wall insulated flue','Mandatory where the chimney crosses ceiling/roof. Spark cap on top.','BuenaCaldera · ferretería'),
 ('mat_stones','Volcanic sauna stones','20–30 kg on the heater for löyly. ~$16.000 / 25 kg sack.','BuenaCaldera · tinascalientes'),
 ('mat_glassdoor','Tempered glass door','Outward-opening, no lock, tempered glass only.','MercadoLibre · ProSauna'),
]
MAT_URI = {m[0]: img_uri(m[0]) for m in MATERIALS}

# which material thumbs to echo inside a section
SEC_THUMBS = {
 'insulation': ['mat_foil','mat_glasswool','mat_mineralwool','mat_foiltape'],
 'woodvselectric': ['stove','mat_flue','mat_stones'],
 'stovesafety': ['mat_flue','mat_fibrocemento','mat_stones'],
 'woodspecies': ['mat_alamo','mat_pino','mat_cladding','mat_impregnado'],
 'interior': ['mat_glassdoor','mat_cladding','mat_alamo'],
}
# big photo per section
SEC_PHOTO = {
 'trailer': ('trailer', 'A used single-axle carro de arrastre — the kind of base you are hunting on Yapo / MercadoLibre.'),
 'woodvselectric': ('stove', 'A compact Chilean sauna wood stove with a stone box and double-wall flue.'),
 'interior': ('interior', 'The goal: light álamo benches, a stove crowned with volcanic stones, soft low light.'),
}
SEC_DIAG = {
 'trailer': 'weight', 'structure': 'floorplan', 'insulation': 'wall',
 'stovesafety': 'clearance', 'ventilation': 'ventilation', 'interior': 'bench',
}

# ---------------------------------------------------------------- source index
sources, src_index = [], {}
def cite(url, title):
    if not url: return None
    if url not in src_index:
        src_index[url] = len(sources) + 1
        sources.append((title or url, url))
    return src_index[url]
for k in ORDER:
    f = by_key[k]
    for kp in f.get('keyPoints', []):
        cite(kp.get('sourceUrl'), kp.get('sourceTitle'))
    for c in f.get('costNotes', []):
        cite(c.get('sourceUrl'), c.get('item'))

# ---------------------------------------------------------------- render helpers
def fig_svg(key):
    svg, cap = DIAG[key]
    return f'<figure class="fig">{svg}<figcaption>{esc(cap)}</figcaption></figure>'

def fig_photo(name, cap):
    return (f'<figure class="fig photo"><img loading="lazy" src="{img_uri(name)}" alt="{esc(cap)}">'
            f'<figcaption>{esc(cap)}</figcaption></figure>')

def thumbs(keys):
    cards = ''
    lk = {m[0]: m for m in MATERIALS}
    for k in keys:
        _, name, what, where = lk[k]
        cards += (f'<figure class="thumb"><img loading="lazy" src="{MAT_URI[k]}" alt="{esc(name)}">'
                  f'<figcaption><b>{esc(name)}</b><span>{esc(what)}</span></figcaption></figure>')
    return f'<div class="thumbrow">{cards}</div>'

def kp_html(kp):
    n = src_index.get(kp.get('sourceUrl'))
    src = ''
    if kp.get('sourceUrl'):
        src = (f'<a class="src" href="{esc(kp["sourceUrl"])}" target="_blank" rel="noopener">'
               f'<span class="src-n">[{n}]</span> {esc(kp.get("sourceTitle","source"))} ↗</a>')
    return (f'<div class="kp"><h4>{esc(kp.get("heading",""))}</h4>'
            f'<p>{esc(kp.get("detail",""))}</p>{src}</div>')

def list_block(title, items, cls):
    if not items: return ''
    lis = ''.join(f'<li>{esc(x)}</li>' for x in items)
    return f'<div class="callout {cls}"><h5>{title}</h5><ul>{lis}</ul></div>'

def cost_table(rows):
    if not rows: return ''
    body = ''
    for c in rows:
        n = src_index.get(c.get('sourceUrl'))
        ref = f' <a class="reflink" href="{esc(c["sourceUrl"])}" target="_blank" rel="noopener">[{n}]</a>' if n else ''
        body += (f'<tr><td class="ci">{esc(c.get("item",""))}{ref}</td>'
                 f'<td class="cp">{esc(c.get("estimateCLP",""))}</td>'
                 f'<td class="cn">{esc(c.get("note",""))}</td></tr>')
    return (f'<div class="table-wrap"><table class="cost"><thead><tr>'
            f'<th>Item</th><th>Price (CLP)</th><th>Note</th></tr></thead><tbody>{body}</tbody></table></div>')

def section_html(k):
    f = by_key[k]
    num, en_label, en_sub, icon = META[k]
    media = ''
    if k in SEC_PHOTO:
        media += fig_photo(*SEC_PHOTO[k])
    if k in SEC_DIAG:
        media += fig_svg(SEC_DIAG[k])
    kps = ''.join(kp_html(x) for x in f.get('keyPoints', []))
    th = thumbs(SEC_THUMBS[k]) if k in SEC_THUMBS else ''
    th = (f'<h3 class="sub">What it looks like</h3>{th}') if th else ''
    costs = f.get('costNotes', [])
    cost_sec = f'<h3 class="sub">Reference costs</h3>{cost_table(costs)}' if costs else ''
    chile = list_block('🇨🇱 Chile / Santiago specifics', f.get('chileNotes', []), 'chile')
    tips = list_block('✅ Tips', f.get('tips', []), 'tips')
    pit = list_block('⛔ Mistakes to avoid', f.get('pitfalls', []), 'pitfall')
    return f'''
<section id="{k}" class="section">
  <div class="sec-head"><span class="sec-num">{num}</span>
    <div><h2>{icon} {esc(en_label)}</h2><p class="sec-es">{esc(en_sub)}</p></div></div>
  <p class="overview">{esc(f.get("overview",""))}</p>
  {media}
  <div class="kps">{kps}</div>
  {th}
  {cost_sec}
  <div class="callouts">{chile}{tips}{pit}</div>
</section>'''

# ---- materials gallery section
gallery_cards = ''
for k, name, what, where in MATERIALS:
    gallery_cards += (f'<figure class="matcard"><img loading="lazy" src="{MAT_URI[k]}" alt="{esc(name)}">'
                      f'<figcaption><b>{esc(name)}</b><p>{esc(what)}</p>'
                      f'<span class="where">📍 {esc(where)}</span></figcaption></figure>')
gallery_html = f'''
<section id="materials" class="section">
  <div class="sec-head"><span class="sec-num">◔</span>
    <div><h2>🧰 Materials at a glance</h2><p class="sec-es">So you recognise it at the barraca — “oh, <em>that</em>!”</p></div></div>
  <p class="overview">Every key material, what it is, and where to find it in the RM. Prices are indicative (2026, CLP).</p>
  <div class="gallery">{gallery_cards}</div>
</section>'''

# ---- budget tiers
def tier_table(t):
    body = ''
    for li in t['lineItems']:
        body += (f'<tr><td>{esc(li.get("item",""))}</td><td class="cp">{esc(li.get("costCLP",""))}</td>'
                 f'<td class="cn">{esc(li.get("note",""))}</td></tr>')
    return (f'<div class="tier"><div class="tier-head"><h3>{esc(t["label"])}</h3>'
            f'<span class="tier-total">{esc(t["totalCLP"])}</span></div>'
            f'<div class="table-wrap"><table class="cost"><thead><tr><th>Item</th><th>CLP</th><th>Note</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div></div>')
b_assump = ''.join(f'<li>{esc(x)}</li>' for x in budget.get('assumptions', []))
b_tips = ''.join(f'<li>{esc(x)}</li>' for x in budget.get('moneySavingTips', []))
budget_html = f'''
<section id="budget" class="section">
  <div class="sec-head"><span class="sec-num">$</span>
    <div><h2>💰 Budget breakdown</h2><p class="sec-es">Two reference tiers from the research</p></div></div>
  <div class="callout chile"><h5>Assumptions</h5><ul>{b_assump}</ul></div>
  <div class="tiers">{tier_table(budget["leanTier"])}{tier_table(budget["comfortTier"])}</div>
  <div class="callout tips"><h5>💡 How to save money</h5><ul>{b_tips}</ul></div>
</section>'''

# ---- nav
nav = ''.join(f'<li><a href="#{k}"><span class="n">{META[k][0]}</span>{esc(META[k][1])}</a></li>' for k in ORDER[:8])
nav += '<li><a href="#materials"><span class="n">◔</span>Materials</a></li>'
nav += ''.join(f'<li><a href="#{k}"><span class="n">{META[k][0]}</span>{esc(META[k][1])}</a></li>' for k in ORDER[8:])
nav += ('<li class="sep"></li>'
        '<li><a href="#calculator"><span class="n">∑</span>Calculator</a></li>'
        '<li><a href="#budget"><span class="n">$</span>Budget</a></li>'
        '<li><a href="#sources"><span class="n">¶</span>Sources</a></li>')

sources_html = ''.join(
    f'<li><span class="rn">[{n}]</span> <a href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a>'
    f'<span class="rurl">{esc(u)}</span></li>' for n, (t, u) in enumerate(sources, 1))

sections_html = ''.join(section_html(k) for k in ORDER[:8]) + gallery_html + ''.join(section_html(k) for k in ORDER[8:])
today = datetime.date(2026, 6, 13).strftime('%d %b %Y')
n_src = len(sources)
n_kp = sum(len(by_key[k].get('keyPoints', [])) for k in ORDER)
HERO_URI = img_uri('hero')

CSS = open('site_css.css').read()
JS = open('site_js.js').read()
CALC = open('calculator.html').read()

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mobile sauna on a trailer · DIY guide (Santiago, Chile)</title>
<style>{CSS}</style>
</head>
<body>
<div class="mobilebar">
  <span class="mb-brand"><span class="fire">🔥</span> Mobile sauna</span>
  <button class="mb-toggle" id="navToggle" aria-label="Open menu" aria-expanded="false">☰ Menu</button>
</div>
<div class="nav-backdrop" id="navBackdrop"></div>
<div class="wrap">
  <nav id="sidenav">
    <div class="brand"><span class="fire">🔥</span> Mobile sauna</div>
    <div class="tag">DIY guide · Santiago, Chile</div>
    <ul>{nav}</ul>
  </nav>
  <main>
    <header class="hero" id="top">
      <img class="hero-img" src="{HERO_URI}" alt="A small mobile sauna built on a trailer">
      <div class="eyebrow">Project · sourced research</div>
      <h1>Building a <span class="fire">mobile sauna</span> on a second-hand trailer</h1>
      <p class="lede">A practical, budget guide adapted to the Chilean market and Santiago's climate,
        for mounting a family sauna on a used carro de arrastre. All units metric, all prices in CLP.</p>
      <div class="chips">
        <span class="chip">📍 <b>Santiago / RM</b></span>
        <span class="chip">🚚 Trailer ~<b>$500.000 CLP</b></span>
        <span class="chip">📐 <b>1,7 × 3,0 m</b></span>
        <span class="chip">👨‍👩‍👧 Family use</span>
        <span class="chip">🔌 220V available</span>
        <span class="chip">🛠️ Intermediate DIY</span>
      </div>
      <div class="herobtns">
        <a class="btn primary" href="#calculator">∑ Open the budget calculator</a>
        <a class="btn" href="#materials">🧰 See the materials</a>
      </div>
      <div class="verdict">
        <h3>Headline recommendation</h3>
        <p><b>Wood stove, not electric.</b> A real electric heater (6–9 kW) eats almost an entire Chilean
        single-phase supply (max ~40 A / 8.8 kW for the whole house) and forces an SEC electrician plus a
        likely three-phase upgrade. A Chilean-made wood stove is cheaper, works off-grid and gives a better
        sauna. And the one rule above all others: respect the trailer's <b>weight budget</b> — a finished
        sauna easily reaches 600–800 kg before stove, stones, water and people.</p>
      </div>
    </header>

    {sections_html}

    {CALC}

    {budget_html}

    <section id="sources" class="section">
      <div class="sec-head"><span class="sec-num">¶</span>
        <div><h2>📚 Sources</h2><p class="sec-es">{n_src} references · original links</p></div></div>
      <ol class="srclist">{sources_html}</ol>
    </section>

    <footer>
      Generated {today} from verified multi-agent research · {n_kp} sourced findings · {n_src} references.
      CLP prices are indicative (2026) and subject to quotation. Always confirm heater clearances against the
      manufacturer's rating plate and current SEC / revisión técnica rules. The calculator is an estimate, not a quote.
    </footer>
  </main>
</div>
<script>{JS}</script>
</body>
</html>'''

open('sauna-guide.html', 'w', encoding='utf-8').write(page)
# residual imperial check
resid = [t for t in [' lb ', ' lbs', 'inches', 'cubic feet', 'sq inches', '/32', ' ft ', 'gauge-or'] if t in page]
print(f'Wrote sauna-guide.html · {len(page)//1024} KB · {len(ORDER)} sections · {n_kp} key points · '
      f'{n_src} sources · {len(MATERIALS)} materials · 6 diagrams')
print('residual imperial tokens:', resid or 'none')
