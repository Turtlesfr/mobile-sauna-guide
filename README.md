# 🔥 Mobile Sauna on a Trailer — DIY Guide (Santiago, Chile)

A practical, budget guide for building a family sauna on a second-hand trailer
(`carro de arrastre`), adapted to the Chilean market and Santiago's climate.
All content in English, all units metric, all prices in CLP.

**▶ Live site: https://turtlesfr.github.io/mobile-sauna-guide/** (mobile-friendly)

## What's inside
- 10 sourced sections: trailer, structure, insulation, heater (wood vs electric),
  fire safety, Chilean wood species, interior, ventilation, sourcing, mistakes.
- A **materials gallery** (photos of every key material + where to buy it).
- **6 technical diagrams**: weight distribution, floor plan, wall cross-section,
  stove clearances, ventilation airflow, bench heights.
- A **live budget calculator**: pick dimensions, build quality and materials →
  itemised CLP estimate, heater sizing, and a built-weight vs axle-rating check.
- **82 references** with original links.

## Rebuilding
`index.html` is a single self-contained file (images base64-embedded).
To regenerate from source:

```bash
python3 build_site.py   # reads research-data.json + img/ + site_css.css + site_js.js + calculator.html
cp sauna-guide.html index.html
```

Research gathered via multi-agent web research; figures indicative (2026) and subject to quotation.
Always confirm heater clearances against the manufacturer's plate and current SEC / revisión técnica rules.
