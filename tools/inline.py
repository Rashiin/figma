"""Inline icons and product art into the HTML pages.

In the pages:  <i data-ic="search"></i>   or   <i data-art="laptop:silver"></i>
This script replaces each tag with an inline SVG, so the pages have no
external dependencies and import cleanly into Figma (html.to.design).
Run:  python3 tools/inline.py
"""
import glob
import re
import zlib

I = {
    'search': '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.6-3.6"/>',
    'cart': '<path d="M3 4h2l2.4 11.1a1.6 1.6 0 0 0 1.6 1.3h8.5a1.6 1.6 0 0 0 1.5-1.2L21 8H6.1"/><circle cx="9.5" cy="20" r="1.3"/><circle cx="17" cy="20" r="1.3"/>',
    'home': '<path d="M4 10.5 12 4l8 6.5V19a1 1 0 0 1-1 1h-4.5v-6h-5v6H5a1 1 0 0 1-1-1z"/>',
    'grid': '<rect x="4" y="4" width="6.5" height="6.5" rx="1.5"/><rect x="13.5" y="4" width="6.5" height="6.5" rx="1.5"/><rect x="4" y="13.5" width="6.5" height="6.5" rx="1.5"/><rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.5"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4.5 20c1.4-3.4 4.3-5 7.5-5s6.1 1.6 7.5 5"/>',
    'bell': '<path d="M6 16v-5a6 6 0 0 1 12 0v5l1.5 2h-15z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
    'heart': '<path d="M12 20s-7.5-4.6-7.5-10.2A4.2 4.2 0 0 1 12 7.3a4.2 4.2 0 0 1 7.5 2.5C19.5 15.4 12 20 12 20z"/>',
    'share': '<circle cx="17.5" cy="5.5" r="2.3"/><circle cx="6.5" cy="12" r="2.3"/><circle cx="17.5" cy="18.5" r="2.3"/><path d="M8.5 10.9l7-4.2M8.5 13.1l7 4.2"/>',
    'back': '<path d="M9 5l7 7-7 7"/>',
    'chev': '<path d="M15 6l-6 6 6 6"/>',
    'down': '<path d="M6 9l6 6 6-6"/>',
    'laptop': '<rect x="4.5" y="5" width="15" height="10.5" rx="1.5"/><path d="M2.5 19h19"/>',
    'monitor': '<rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M9 20h6M12 16v4"/>',
    'cpu': '<rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4"/>',
    'mouse': '<rect x="7" y="3" width="10" height="18" rx="5"/><path d="M12 7v3"/>',
    'case': '<rect x="7" y="3" width="10" height="18" rx="1.5"/><circle cx="12" cy="15" r="1.6"/><path d="M9.5 6.5h5"/>',
    'truck': '<path d="M3 6h11v10H3zM14 9.5h4l3 3.5v3h-7"/><circle cx="7" cy="18" r="1.8"/><circle cx="17" cy="18" r="1.8"/>',
    'shield': '<path d="M12 3l7 3v5c0 4.6-3 8-7 10-4-2-7-5.4-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'minus': '<path d="M5 12h14"/>',
    'trash': '<path d="M5 7h14M10 7V5h4v2M7 7l1 13h8l1-13"/>',
    'pin': '<path d="M12 21s-6.5-5.7-6.5-11a6.5 6.5 0 0 1 13 0c0 5.3-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
    'clock': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    'phone': '<path d="M5 4h3.5l1.5 4-2 1.3a10.5 10.5 0 0 0 6.7 6.7L16 14l4 1.5V19a1.5 1.5 0 0 1-1.6 1.5A16 16 0 0 1 3.5 5.6 1.5 1.5 0 0 1 5 4z"/>',
    'chat': '<path d="M4 5.5h16v10.5H9.5L5 19.5V16H4z"/>',
    'check': '<path d="M5 12.5l4.2 4.2L19 7"/>',
    'upload': '<path d="M12 15.5V4.5M7.5 9 12 4.5 16.5 9M4.5 19.5h15"/>',
    'oil': '<path d="M12 3.5c3 4.2 6 7.6 6 11a6 6 0 0 1-12 0c0-3.4 3-6.8 6-11z"/>',
    'car': '<path d="M4 15.5 5.8 10A2 2 0 0 1 7.7 8.6h8.6a2 2 0 0 1 1.9 1.4L20 15.5v3.5h-2.5M4 15.5V19h2.5M4 15.5h16"/><circle cx="8" cy="16.5" r="1.3"/><circle cx="16" cy="16.5" r="1.3"/>',
    'drops': '<path d="M8 4c2 2.7 4 5 4 7.3a4 4 0 0 1-8 0C4 9 6 6.7 8 4zM17 9.5c1.4 1.9 2.8 3.5 2.8 5.1a2.8 2.8 0 0 1-5.6 0c0-1.6 1.4-3.2 2.8-5.1z"/>',
    'battery': '<rect x="3" y="7" width="16" height="10" rx="1.8"/><path d="M21 10.5v3M7 12h4M9 10v4M14 12h2"/>',
    'disc': '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="3"/><path d="M12 3.5v3M20.5 12h-3"/>',
    'snow': '<path d="M12 3v18M4.2 7.5l15.6 9M4.2 16.5l15.6-9M9.5 4.5 12 6.5l2.5-2M9.5 19.5 12 17.5l2.5 2"/>',
    'clipboard': '<rect x="5.5" y="4.5" width="13" height="16" rx="2"/><path d="M9 4.5h6V7H9zM9 13l2 2 4-4"/>',
    'card': '<rect x="3" y="6" width="18" height="13" rx="2"/><path d="M3 10h18M7 15h4"/>',
    'calendar': '<rect x="4" y="5.5" width="16" height="14.5" rx="2"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h10"/>',
    'filter': '<path d="M4 6h16M7 12h10M10 18h4"/>',
    'tag': '<path d="M4 12.5V5a1 1 0 0 1 1-1h7.5L20 11.5 12.5 19z"/><circle cx="8.5" cy="8.5" r="1.4"/>',
    'school': '<path d="M3 9.5 12 5l9 4.5-9 4.5z"/><path d="M7 11.5V16c1.4 1.4 3 2 5 2s3.6-.6 5-2v-4.5M21 9.5v5"/>',
    'doc': '<path d="M7 3.5h7l4.5 4.5v12.5h-11.5z"/><path d="M14 3.5V8h4.5M9.5 13h5M9.5 16.5h5"/>',
    'info': '<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5.5M12 7.8v.4"/>',
    'nav': '<path d="M12 3 19 20l-7-3.8L5 20z"/>',
    'wrench': '<path d="M14.5 5.5a4 4 0 0 0 4.8 5.2L12 18a2.1 2.1 0 0 1-3-3l7.3-7.3a4 4 0 0 0-1.8-2.2z"/>',
}
FILLED = {
    'star': '<path d="M12 3.6l2.5 5.2 5.7.8-4.1 4 1 5.7L12 16.6l-5.1 2.7 1-5.7-4.1-4 5.7-.8z"/>',
}


def icon(name, cls):
    if name in FILLED:
        return f'<svg class="ic {cls}" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{FILLED[name]}</svg>'
    return (f'<svg class="ic {cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{I[name]}</svg>')


# ---------- product art: flat product shots on a light ground ----------
LAPTOP = {
    'silver': ('#d5d9df', '#bfc4cc', '#a9b0ba', ('#6f8ee8', '#c9d6ff')),
    'navy':   ('#4a5568', '#3b4453', '#2e3542', ('#2bb3a3', '#c5f1ea')),
    'gray':   ('#c7c9ce', '#b3b6bc', '#9ea2a9', ('#e38a5c', '#ffd9bf')),
    'black':  ('#2d3036', '#23262b', '#1a1c20', ('#d8364b', '#ffb3bd')),
}


def art(kind, variant, cls):
    uid = zlib.crc32((kind + variant + cls).encode()) % 100000
    if kind == 'laptop':
        body, base, edge, (s1, s2) = LAPTOP[variant]
        inner = f'''<defs><linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{s2}"/><stop offset="1" stop-color="{s1}"/></linearGradient></defs>
<ellipse cx="80" cy="101" rx="66" ry="4.5" fill="#000" opacity=".08"/>
<rect x="30" y="14" width="100" height="66" rx="5" fill="{body}"/>
<rect x="34" y="18" width="92" height="58" rx="2.5" fill="#15171b"/>
<rect x="37" y="21" width="86" height="52" rx="1.5" fill="url(#g{uid})"/>
<path d="M37 60 Q62 44 84 55 T123 48 V73 H37 Z" fill="#fff" opacity=".22"/>
<path d="M18 82 H142 L148 93 Q148 96 145 96 H15 Q12 96 12 93 Z" fill="{base}"/>
<path d="M12 93 H148 Q148 96 145 96 H15 Q12 96 12 93 Z" fill="{edge}"/>
<rect x="68" y="82" width="24" height="3" rx="1.5" fill="{edge}" opacity=".6"/>'''
    elif kind == 'monitor':
        inner = f'''<defs><linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffd2a8"/><stop offset="1" stop-color="#5e7ce2"/></linearGradient></defs>
<ellipse cx="80" cy="101" rx="40" ry="4" fill="#000" opacity=".08"/>
<rect x="14" y="8" width="132" height="76" rx="4" fill="#1f2227"/>
<rect x="17" y="11" width="126" height="70" rx="2" fill="url(#g{uid})"/>
<path d="M72 84 h16 l3 12 h-22z" fill="#3a3e45"/><rect x="56" y="95" width="48" height="4" rx="2" fill="#2a2d33"/>'''
    elif kind == 'mouse':
        inner = '''<ellipse cx="80" cy="99" rx="30" ry="4" fill="#000" opacity=".08"/>
<rect x="56" y="16" width="48" height="82" rx="24" fill="#3d4148"/><path d="M56 46 Q56 16 80 16 V46 Z" fill="#4a4f57"/>
<path d="M80 16 V46 M56 46 H104" stroke="#2b2e33" stroke-width="2"/><rect x="77" y="25" width="6" height="12" rx="3" fill="#8a9099"/>'''
    elif kind == 'keyboard':
        keys = ''.join(f'<rect x="{22+c*12.2}" y="{38+r*12}" width="10" height="9" rx="2" fill="#f4f5f7"/>' for r in range(4) for c in range(10))
        inner = f'''<ellipse cx="80" cy="92" rx="70" ry="4" fill="#000" opacity=".08"/>
<rect x="14" y="30" width="132" height="60" rx="7" fill="#d6d9de"/>{keys}<rect x="46" y="74" width="68" height="9" rx="2" fill="#f4f5f7"/>'''
    elif kind == 'case':
        inner = '''<ellipse cx="80" cy="101" rx="42" ry="4" fill="#000" opacity=".08"/>
<rect x="46" y="8" width="68" height="90" rx="4" fill="#24272c"/><rect x="52" y="14" width="40" height="78" rx="2" fill="#30343a"/>
<rect x="55" y="18" width="34" height="70" rx="1.5" fill="#1a1d22" stroke="#4fd1c5" stroke-opacity=".5"/>
<circle cx="72" cy="40" r="11" fill="none" stroke="#4fd1c5" stroke-width="2.5" opacity=".8"/><circle cx="72" cy="66" r="11" fill="none" stroke="#a78bfa" stroke-width="2.5" opacity=".8"/>
<circle cx="104" cy="18" r="2.4" fill="#9aa1ab"/><rect x="99" y="26" width="10" height="2.5" rx="1.2" fill="#4a4f57"/>'''
    else:
        raise ValueError(kind)
    return f'<svg class="art {cls}" viewBox="0 0 160 110" aria-hidden="true">{inner}</svg>'


IC_RE = re.compile(r'<i data-ic="([\w-]+)"(?: class="([^"]*)")?></i>')
ART_RE = re.compile(r'<i data-art="(\w+):?(\w*)"(?: class="([^"]*)")?></i>')

for path in glob.glob('computer-store/*.html') + glob.glob('car-service/*.html'):
    s = open(path, encoding='utf-8').read()
    n = len(IC_RE.findall(s)) + len(ART_RE.findall(s))
    s = IC_RE.sub(lambda m: icon(m.group(1), m.group(2) or ''), s)
    s = ART_RE.sub(lambda m: art(m.group(1), m.group(2), m.group(3) or ''), s)
    open(path, 'w', encoding='utf-8').write(s)
    print(f'{path}: {n} inlined')
