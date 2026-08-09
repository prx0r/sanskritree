#!/bin/bash
# Phase 2: Render 80 VB dev verses across C0, C1, C2
# Run: nohup bash scripts/phase2_render.sh > proof/phase2_render.log 2>&1 &

export OPENAI_API_KEY="sk-SDjjQ8NtTdpM2OmWl3GXDrPlhcQiLvZln60mSVVcJQ3rkg7trYHQoLKshcKSeg0Y"
export PYTHONPATH=src
cd /root/projects/sanskritree

echo "=== Phase 2 render started at $(date) ==="

python3 scripts/phase2_render.py --system c2 --limit 80
echo "C2 done at $(date)"

python3 scripts/phase2_render.py --system c1 --limit 80
echo "C1 done at $(date)"

python3 scripts/phase2_render.py --system c0 --limit 80
echo "C0 done at $(date)"

echo "=== All done at $(date) ==="
