#!/usr/bin/env python3
"""Build a local, animated four-node SVG career timeline.

Edit the values in NODES, then run from the repository root:
    python3 scripts/career_timeline.py
README embeds the generated SVG files, not this Python script.
No dependencies, JavaScript, or external resources are needed.
"""
from html import escape
from pathlib import Path
from textwrap import wrap

ROOT = Path(__file__).resolve().parents[1]
LOOP_SECONDS = 12
ARRIVAL_PHASES = (0, 0.30, 0.60, 0.90)
NODES = [
    {'chapter': 'BEGIN', 'dates': ('Oct 2025', 'Mar 2026'), 'company': 'SwanLab', 'role': 'Backend Engineer/SRE'},
    {'chapter': 'BUILD', 'dates': ('Mar 2026', 'Aug 2026'), 'company': 'SenseTime', 'role': 'AI Infra Engineer'},
    {'chapter': 'GROW', 'dates': ('Sep 2026', 'Oct 2026'), 'company': 'ByteDance', 'role': 'AI Agent Engineer'},
    {'chapter': 'NOW', 'dates': ('Nov 2026', 'Present'), 'company': 'Looking for a new opportunity', 'role': ''},
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


def timeline(mobile=False, reduced=False):
    company_columns, role_columns = (12, 14) if mobile else (23, 27)
    company_y, company_leading = (214, 24) if mobile else (192, 22)
    company_rows = max(1, max(len(text_lines(node['company'], company_columns)) for node in NODES))
    role_rows = max(1, max(len(text_lines(node['role'], role_columns)) for node in NODES))
    role_y = company_y + company_rows * company_leading + 7
    width = 480 if mobile else 900
    height = role_y + (role_rows - 1) * company_leading + 34
    positions = (60, 180, 300, 420) if mobile else (105, 335, 565, 795)
    line_y = 110
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
    .heading { fill: var(--text); font-size: 24px; font-weight: 600; }
    .chapter { fill: var(--muted); font-size: 12px; font-weight: 500; letter-spacing: 2px; }
    .date { fill: var(--muted); font-size: 14px; font-family: ui-monospace, 'SF Mono', Consolas, monospace; }
    /* Keep company labels bright even if an editor does not forward its dark theme to SVG images. */
    .company { fill: #70a5fd; font-size: 17px; font-weight: 500; }
    .role { fill: var(--muted); font-size: 14px; }
    .current { fill: var(--accent); }
    /* Arrival phases match each node's negative delay: 0%, 30%, 60%, 90%. */
    .traveler { animation: journey var(--loop-duration) linear infinite; }
    @keyframes journey {
      0%, 8% { transform: translateX(0); opacity: 1; }
      30%, 38% { transform: translateX(var(--journey-step-1)); opacity: 1; }
      60%, 68% { transform: translateX(var(--journey-step-2)); opacity: 1; }
      90%, 98% { transform: translateX(var(--journey-distance)); opacity: 1; }
      100% { transform: translateX(var(--journey-distance)); opacity: 0; }
    }
    .node-dot, .arrival-halo, .company {
      transform-box: fill-box; transform-origin: center;
      animation-duration: var(--loop-duration);
      animation-delay: var(--hit-delay);
      animation-timing-function: ease-in-out;
      animation-iteration-count: infinite;
    }
    .node-dot { animation-name: node-arrival; }
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
      .node-dot, .company { animation: none; transform: none; }
      .arrival-halo { animation: none; opacity: 0; }
    }
    '''
    if mobile:
        styles += '''
    .heading { font-size: 28px; }
    .chapter { font-size: 16px; letter-spacing: 1px; }
    .date, .role { font-size: 16px; }
    .company { font-size: 18px; }
    '''
    if reduced:
        styles += '''
    .traveler { display: none; animation: none; } .breathing { animation: none; opacity: .22; }
    .node-dot, .company { animation: none; transform: none; }
    .arrival-halo { animation: none; opacity: 0; }
'''
    description = 'Career timeline, left to right: ' + '; '.join(
        f'{node["chapter"]}: {node["dates"][0]} to {node["dates"][1]}, {node["company"]}, {node["role"]}'
        for node in NODES)
    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="career-title career-description">
  <title id="career-title">Career Journey</title>
  <desc id="career-description">{escape(description)}</desc>
  <style>:root {{ --loop-duration: {LOOP_SECONDS}s; --journey-step-1: {positions[1] - positions[0]}px; --journey-step-2: {positions[2] - positions[0]}px; --journey-distance: {positions[-1] - positions[0]}px; }}{styles}</style>
  <text class="heading" x="{width // 2}" y="38" text-anchor="middle">Career Journey</text>
  <path d="M {positions[0]} {line_y} H {positions[-1]}" stroke="var(--line)" stroke-width="1.5" fill="none" />
  <g class="traveler" aria-hidden="true">
    <circle cx="{positions[0]}" cy="{line_y}" r="3" fill="var(--accent)" opacity=".75" />
  </g>''']
    for index, (node, x) in enumerate(zip(NODES, positions)):
        current = index == len(NODES) - 1
        active = ' current' if current else ''
        # Negative delays put all nodes on the same loop, even on first load.
        hit_delay = 0 if index == 0 else (ARRIVAL_PHASES[index] - 1) * LOOP_SECONDS
        rest_fill = 'var(--accent)' if current else 'var(--surface)'
        rest_stroke = 'var(--accent)' if current else 'var(--node)'
        svg.append(f'  <g data-node="{index + 1}" text-anchor="middle" style="--hit-delay: {hit_delay:g}s; --rest-fill: {rest_fill}; --rest-stroke: {rest_stroke};">')
        svg.append(f'    <text class="chapter{active}" x="{x}" y="82">{escape(node["chapter"])}</text>')
        svg.append(f'    <circle class="arrival-halo" cx="{x}" cy="{line_y}" r="12" fill="var(--accent)" aria-hidden="true" />')
        if current:
            svg.append(f'    <circle class="breathing" cx="{x}" cy="{line_y}" r="13" fill="var(--accent)" aria-hidden="true" />')
            svg.append(f'    <circle class="node-dot" cx="{x}" cy="{line_y}" r="5.5" fill="var(--accent)" stroke="var(--accent)" stroke-width="1.5" />')
        else:
            svg.append(f'    <circle class="node-dot" cx="{x}" cy="{line_y}" r="5" fill="var(--surface)" stroke="var(--node)" stroke-width="1.5" />')
        start, end = node['dates']
        if mobile:
            svg.append(f'    <text class="date" x="{x}" y="151">{escape(start)}</text>')
            svg.append(f'    <text class="date" x="{x}" y="173">to {escape(end)}</text>')
        else:
            svg.append(f'    <text class="date" x="{x}" y="153">{escape(start)} — {escape(end)}</text>')
        svg.append(svg_label(node['company'], 'company', x, company_y, company_columns, company_leading))
        svg.append(svg_label(node['role'], 'role', x, role_y, role_columns, company_leading))
        svg.append('  </g>')
    svg.append('</svg>\n')
    return '\n'.join(svg)


if __name__ == '__main__':
    for mobile in (False, True):
        for reduced in (False, True):
            suffix = ('-mobile' if mobile else '') + ('-static' if reduced else '')
            path = ROOT / 'assets' / f'career-journey{suffix}.svg'
            path.write_text(timeline(mobile, reduced), encoding='utf-8')
            print(f'Generated {path}')
