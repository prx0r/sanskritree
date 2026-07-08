# Sanskrit Proof Engine — Frontend Design

## Core Concept

**Mandala + layered geometry.** Base: flat gold disk (Layer 0). When nodes connect, vertical geometries rise—each connection creates a layer. See math.md § Mandala Geometry for the formal basis.

**Alternative: 3D proof sculptures.** Nested logic → organic 3D structures. Each derivation tree is a unique sculpture—branches, nodes, connections. Not a rigid diagram; emergent form from structure.

**Abhinavagupta aesthetic layer** (suggestive, not prescriptive):
- **Camatkāra** — wonder, relish; the upsurge of consciousness (saṃrambha) + bliss (ānanda)
- **Rasa** — sui generis, revelatory; spectator-centered, transformative
- **Cosmic imagery** — Śiva's consciousness expanding; lotus petals unfolding; ābhāsa (manifestation)
- **Spectator as center** — you orbit, zoom, enter; the structure reveals itself

---

## Mandala Mode (math.md)

- **Layer 0** — Flat disk, gold text at node positions. Radial placement: θ by tradition sector, r by depth.
- **Layer k** — For each edge (u,v) with d(v)=k, a vertical element (pillar, petal) rises from p(u) to height h·k.
- **Bridges** — Arc connecting two nodes at a distinct height.
- **n-fold** — Traditions → sectors of 2π/n.

## Structure First

The proof graph *is* the geometry:
- **Node** = branch segment / node in 3D space
- **Parent → child** = branch connection (tapering, recursive)
- **Depth** = distance from root; affects thickness, length
- **Status** = material quality (luminous / dim / dormant)
- **Bridge** = two branches that share a Lean type; subtle link, same "species"

**Layout:** Procedural. Root at origin. Children branch outward—angles vary by tradition, depth. Each proof tree grows differently. L-system–like: simple rules, emergent complexity.

---

## Abhinavagupta Palette (suggestive)

| Element | Direction |
|---------|-----------|
| Cosmos | Deep, near-black; subtle gradient (void → faint warmth) |
| Sanskrit nodes | Warm: amber, honey, petal-gold—luminous, not harsh |
| Lean nodes | Cool: moonlight, silver-mist—clarity, precision |
| PROVED | Inner glow; camatkāra—the "bloom" |
| HOLLOW | Dormant; potential, not absence |
| Bridges | Subtle resonance; same frequency, different branches |
| Edges | Organic; tendril, vine—not straight lines |

**Not rigid.** These are directions. The structure drives the form; aesthetics follow.

---

## 3D Interaction

| Action | Result |
|--------|--------|
| Orbit | Mouse drag — rotate around center |
| Zoom | Scroll — move in/out |
| Pan | Right-drag or middle-drag |
| Click node | Select; optional detail panel |
| Zoom in deep | Enter a branch; nested sculpture |

**Zoom levels:**
- **Far** — whole forest; proofs as trees
- **Mid** — single tree; branches visible
- **Close** — single node; text readable

---

## Tech

- **Three.js** — 3D, WebGL
- **Procedural geometry** — cylinders/tubes for branches; spheres or custom for nodes
- **No rigid style** — structure from data; materials/colors as parameters

---

## File Structure

```
frontend/
├── FRONTEND_DESIGN.md
├── index.html           (2D fallback)
├── index3d.html         (3D sculpture view)
├── scene3d.js           (Three.js, proof-tree geometry)
├── styles.css
├── app.js
├── export_nodes.py
└── data/
    └── sample.json
```
