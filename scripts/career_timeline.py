#!/usr/bin/env python3
"""Build a local, animated four-node SVG career timeline.

Edit the values in NODES, then run from the repository root:
    python3 scripts/career_timeline.py
README embeds the generated SVG files, not this Python script.
The three PNGs in assets/logos/ are generation inputs, embedded into each SVG.
Official source assets (brand/trademark rights remain with their owners):
  SwanLab: https://swanlab.cn/icon.png?e31c53cba54196fe
  SenseTime: https://static.sensetime.com/images/st_logo_ico.png
  ByteDance: https://avatars.githubusercontent.com/u/4158466?s=200&v=4
ByteDance uses its official GitHub organization mark. These downloads are not
an unrestricted trademark license; SenseTime publishes reuse conditions at
https://www.sensetime.com/cn/legal.
No dependencies, JavaScript, or external image requests are needed at display time.
"""
from base64 import b64encode
from html import escape
from pathlib import Path
from textwrap import wrap

ROOT = Path(__file__).resolve().parents[1]
LOOP_SECONDS = 12
ARRIVAL_PHASES = (0, 0.30, 0.60, 0.90)
NODES = [
    {'dates': ('Oct 2025', 'Mar 2026'), 'company': 'SwanLab', 'role': 'Backend Engineer/SRE', 'logo': 'swanlab.png'},
    {'dates': ('Mar 2026', 'Aug 2026'), 'company': 'SenseTime', 'role': 'AI Infra Engineer', 'logo': 'sensetime.png'},
    {'dates': ('Sep 2026', 'Oct 2026'), 'company': 'ByteDance', 'role': 'AI Agent Engineer', 'logo': 'bytedance.png'},
    {'dates': ('Nov 2026', 'Present'), 'company': 'Available', 'role': ''},
]


def text_lines(value, columns):
    """Wrap user-edited labels without changing the saved career data."""
    return wrap(value, width=columns, break_long_words=True, break_on_hyphens=False)


def svg_label(value, css_class, x, y, columns, line_height):
    lines = text_lines(value, columns)
    if not lines:
        return ''
    spans = ''.join(f'<tspan x="{x}" dy="{0 if index == 0 else line_height}">{escape(line)}</tspan>'
                    for index, line in enumerate(lines))
    return f'    <text class="{css_class}" x="{x}" y="{y}">{spans}</text>'


def logo_uri(filename):
    """Embed local brand assets so SVG images never fetch nested resources."""
    image = (ROOT / 'assets' / 'logos' / filename).read_bytes()
    return 'data:image/png;base64,' + b64encode(image).decode('ascii')


def timeline(reduced=False):
    # A square canvas matches the portrait's aspect ratio and 336px height.
    width = height = 336
    # Saved data stays chronological; render the newest entry at the top.
    # The traveler follows the same oldest-to-newest order, moving upward.
    positions = (278, 206, 134, 62)
    line_x, label_x = 40, 72
    company_columns, role_columns, company_leading = 28, 32, 17
    styles = '''
    :root {
      --surface: #ffffff; --text: #1f2328; --muted: #59636e;
      --line: #d1d9e0; --node: #8493a4; --accent: #087f8c;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --surface: #0d1117; --text: #e6edf3; --muted: #9198a1;
        --line: #303d50; --node: #6e8097; --accent: #7ee7cf;
      }
    }
    text { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; }
    .heading { fill: var(--text); font-size: 20px; font-weight: 600; }
    .date { fill: var(--muted); font-size: 12px; font-family: ui-monospace, 'SF Mono', Consolas, monospace; }
    /* Keep company labels bright even if an editor does not forward its dark theme to SVG images. */
    .company { fill: #70a5fd; font-size: 15px; font-weight: 500; }
    .role { fill: var(--muted); font-size: 12px; }
    /* Arrival phases match each node's negative delay: 0%, 30%, 60%, 90%. */
    .traveler { animation: journey var(--loop-duration) linear infinite; }
    @keyframes journey {
      0%, 8% { transform: translateY(0); opacity: 1; }
      30%, 38% { transform: translateY(var(--journey-step-1)); opacity: 1; }
      60%, 68% { transform: translateY(var(--journey-step-2)); opacity: 1; }
      90%, 98% { transform: translateY(var(--journey-distance)); opacity: 1; }
      100% { transform: translateY(var(--journey-distance)); opacity: 0; }
    }
    .node-dot, .node-logo, .logo-disc, .arrival-halo, .company {
      transform-box: fill-box; transform-origin: center;
      animation-duration: var(--loop-duration);
      animation-delay: var(--hit-delay);
      animation-timing-function: ease-in-out;
      animation-iteration-count: infinite;
    }
    .node-dot { animation-name: node-arrival; }
    .node-logo { animation-name: logo-arrival; }
    .logo-disc { fill: #ffffff; stroke: var(--node); stroke-width: 1; animation-name: logo-ring; }
    @keyframes logo-arrival {
      0%, 8%, 100% { transform: scale(1); }
      2%, 4% { transform: scale(1.12); }
    }
    @keyframes logo-ring {
      0%, 8%, 100% { stroke: var(--node); stroke-width: 1; }
      2%, 4% { stroke: var(--accent); stroke-width: 2; }
    }
    .arrival-halo { opacity: 0; animation-name: halo-arrival; }
    .company { animation-name: company-arrival; }
    @keyframes node-arrival {
      0%, 8%, 100% { transform: scale(1); fill: var(--rest-fill); stroke: var(--rest-stroke); }
      2%, 4% { transform: scale(1.28); fill: var(--accent); stroke: var(--accent); }
    }
    @keyframes halo-arrival {
      0% { opacity: 0; transform: scale(.65); }
      2% { opacity: .30; transform: scale(1); }
      8%, 100% { opacity: 0; transform: scale(1.45); }
    }
    @keyframes company-arrival {
      0%, 8%, 100% { fill: #70a5fd; transform: translateY(0) scale(1); }
      2%, 4% { fill: #b6d6ff; transform: translateY(-2px) scale(1.035); }
    }
    .breathing {
      transform-box: fill-box; transform-origin: center;
      animation: breathe 4s ease-in-out infinite;
    }
    @keyframes breathe {
      0%, 100% { opacity: .18; transform: scale(1); }
      50% { opacity: .42; transform: scale(1.12); }
    }
    @media (prefers-reduced-motion: reduce) {
      .traveler { display: none; }
      .breathing { animation: none; opacity: .22; }
      .node-dot, .node-logo, .logo-disc, .company { animation: none; transform: none; }
      .arrival-halo { animation: none; opacity: 0; }
    }
    '''
    if reduced:
        styles += '''
    .traveler { display: none; animation: none; } .breathing { animation: none; opacity: .22; }
    .node-dot, .node-logo, .logo-disc, .company { animation: none; transform: none; }
    .arrival-halo { animation: none; opacity: 0; }
'''
    description = 'Career timeline, top to bottom: ' + '; '.join(
        f'{node["dates"][0]} to {node["dates"][1]}, {node["company"]}, {node["role"]}'
        for node in reversed(NODES))
    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="career-title career-description">
  <title id="career-title">Career Journey</title>
  <desc id="career-description">{escape(description)}</desc>
  <style>:root {{ --loop-duration: {LOOP_SECONDS}s; --journey-step-1: {positions[1] - positions[0]}px; --journey-step-2: {positions[2] - positions[0]}px; --journey-distance: {positions[-1] - positions[0]}px; }}{styles}</style>
  <text class="heading" x="{label_x}" y="22">Career Journey</text>
  <path d="M {line_x} {positions[0]} V {positions[-1]}" stroke="var(--line)" stroke-width="1.5" fill="none" />
  <g class="traveler" aria-hidden="true">
    <circle cx="{line_x}" cy="{positions[0]}" r="3" fill="var(--accent)" opacity=".75" />
  </g>''']
    for index, (node, y) in enumerate(zip(NODES, positions)):
        x = line_x
        current = index == len(NODES) - 1
        # Negative delays put all nodes on the same loop, even on first load.
        hit_delay = 0 if index == 0 else (ARRIVAL_PHASES[index] - 1) * LOOP_SECONDS
        rest_fill = 'var(--accent)' if current else 'var(--surface)'
        rest_stroke = 'var(--accent)' if current else 'var(--node)'
        svg.append(f'  <g data-node="{index + 1}" style="--hit-delay: {hit_delay:g}s; --rest-fill: {rest_fill}; --rest-stroke: {rest_stroke};">')
        halo_radius = 21 if node.get('logo') else 12
        svg.append(f'    <circle class="arrival-halo" cx="{x}" cy="{y}" r="{halo_radius}" fill="var(--accent)" aria-hidden="true" />')
        if current:
            svg.append(f'    <circle class="breathing" cx="{x}" cy="{y}" r="13" fill="var(--accent)" aria-hidden="true" />')
            svg.append(f'    <circle class="node-dot" cx="{x}" cy="{y}" r="5.5" fill="var(--accent)" stroke="var(--accent)" stroke-width="1.5" />')
        elif node.get('logo'):
            svg.append('    <g class="node-logo">')
            svg.append(f'      <circle class="logo-disc" cx="{x}" cy="{y}" r="16" />')
            svg.append(f'      <image x="{x - 13}" y="{y - 13}" width="26" height="26" preserveAspectRatio="xMidYMid meet" href="{logo_uri(node["logo"])}" />')
            svg.append('    </g>')
        else:
            svg.append(f'    <circle class="node-dot" cx="{x}" cy="{y}" r="5" fill="var(--surface)" stroke="var(--node)" stroke-width="1.5" />')
        company_y = y - 6
        company_rows = max(1, len(text_lines(node['company'], company_columns)))
        date_y = company_y + company_rows * company_leading + 4
        role_y = date_y + 18
        start, end = node['dates']
        svg.append(svg_label(node['company'], 'company', label_x, company_y, company_columns, company_leading))
        svg.append(f'    <text class="date" x="{label_x}" y="{date_y}">{escape(start)} — {escape(end)}</text>')
        svg.append(svg_label(node['role'], 'role', label_x, role_y, role_columns, company_leading))
        svg.append('  </g>')
    svg.append('</svg>\n')
    return '\n'.join(svg)


if __name__ == '__main__':
    for reduced in (False, True):
        suffix = '-static' if reduced else ''
        path = ROOT / 'assets' / f'career-journey{suffix}.svg'
        path.write_text(timeline(reduced), encoding='utf-8')
        print(f'Generated {path}')
