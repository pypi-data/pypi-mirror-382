from jinja2 import Template
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename, TextLexer
from pygments.formatters import HtmlFormatter
import orjson
from collections import defaultdict

def _highlight_code(filename: str, code: str) -> str:
    try:
        lexer = guess_lexer_for_filename(filename, code)
    except Exception:
        lexer = TextLexer()
    formatter = HtmlFormatter(nowrap=False)
    return highlight(code, lexer, formatter)

def generate_reports(duplicates, html_out: str | None, json_out: str | None):
    if html_out:
        _generate_html(duplicates, html_out)
        grouped_html = html_out.replace('.html', '_grouped.html')
        _generate_grouped_html(duplicates, grouped_html)
    if json_out:
        _generate_json(duplicates, json_out)

def _generate_json(duplicates, output_path: str):
    payload = {
        "total": len(duplicates),
        "items": duplicates
    }
    with open(output_path, "wb") as f:
        f.write(orjson.dumps(payload, option=orjson.OPT_INDENT_2))

def _group_by_similarity(duplicates):
    """Group duplicates by similarity ranges"""
    groups = defaultdict(list)
    
    for d in duplicates:
        sim = d['similarity']
        if sim >= 0.95:
            groups['Exact matches (95-100%)'].append(d)
        elif sim >= 0.90:
            groups['Very similar (90-95%)'].append(d)
        elif sim >= 0.80:
            groups['Similar (80-90%)'].append(d)
        elif sim >= 0.70:
            groups['Moderately similar (70-80%)'].append(d)
        else:
            groups['Slightly similar (<70%)'].append(d)
    
    return groups

def _generate_grouped_html(duplicates, output_path: str):
    formatter = HtmlFormatter()
    css = formatter.get_style_defs(".codehilite")
    
    grouped_duplicates = _group_by_similarity(duplicates)

    html_template = """
    <html>
    <head>
        <meta charset="utf-8"/>
        <title>Code Duplicates Report - Grouped by Similarity</title>
        <style>
            body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 24px;}
            .meta { margin-bottom: 16px; }
            .group { margin-bottom: 32px; }
            .group-header { background: #f3f4f6; padding: 16px; border-radius: 8px; margin-bottom: 16px; }
            .group-title { font-size: 18px; font-weight: 600; margin: 0; }
            .group-count { color: #6b7280; font-size: 14px; margin-top: 4px; }
            .pair { border: 1px solid #e5e7eb; border-radius: 10px; margin-bottom: 18px; overflow: hidden; }
            .pair-header { display: flex; justify-content: space-between; background: #f9fafb; padding: 12px 14px; font-weight: 600; }
            .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }
            .col { border-top: 1px solid #e5e7eb; padding: 14px; overflow-x: auto; }
            .path { color: #374151; font-size: 12px; margin-bottom: 8px; }
            .sim { font-variant-numeric: tabular-nums; }
            .toc { background: #f8fafc; padding: 16px; border-radius: 8px; margin-bottom: 24px; }
            .toc h3 { margin-top: 0; }
            .toc a { text-decoration: none; color: #3b82f6; }
            .toc a:hover { text-decoration: underline; }
            """ + css + """
            pre { margin: 0; }
        </style>
    </head>
    <body>
        <h2>🔁 Code Duplicates Report - Grouped by Similarity</h2>
        <div class="meta">Total detected: <b>{{ total_duplicates }}</b></div>

        <div class="toc">
            <h3>📋 Table of Contents by Similarity</h3>
            {% for group_name, group_items in groups.items() %}
            <div><a href="#{{ group_name|replace(' ', '_')|replace('(', '')|replace(')', '')|replace('%', 'pct')|replace('-', '_')|replace('<', 'lt') }}">{{ group_name }}</a> - {{ group_items|length }} duplicates</div>
            {% endfor %}
        </div>

        {% for group_name, group_items in groups.items() %}
        <div class="group" id="{{ group_name|replace(' ', '_')|replace('(', '')|replace(')', '')|replace('%', 'pct')|replace('-', '_')|replace('<', 'lt') }}">
            <div class="group-header">
                <div class="group-title">{{ group_name }}</div>
                <div class="group-count">{{ group_items|length }} duplicates found</div>
            </div>
            
            {% for d in group_items %}
            <div class="pair">
                <div class="pair-header">
                    <div>Similarity: <span class="sim">{{ '%.2f'|format(d.similarity) }}</span></div>
                    <div>{{ d.a.language }} • {{ d.a.type }}</div>
                </div>
                <div class="cols">
                    <div class="col">
                        <div class="path">{{ d.a.file }} — lines {{ d.a.lines[0] }}-{{ d.a.lines[1] }}</div>
                        {{ d.a_code|safe }}
                    </div>
                    <div class="col">
                        <div class="path">{{ d.b.file }} — lines {{ d.b.lines[0] }}-{{ d.b.lines[1] }}</div>
                        {{ d.b_code|safe }}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    </body>
    </html>
    """

    template = Template(html_template)

    enriched_groups = {}
    for group_name, group_items in grouped_duplicates.items():
        enriched = []
        for d in group_items:
            a_code = _highlight_code(d["a"]["file"], d["a"]["code"])
            b_code = _highlight_code(d["b"]["file"], d["b"]["code"])
            e = dict(d)
            e["a_code"] = a_code
            e["b_code"] = b_code
            enriched.append(e)
        enriched_groups[group_name] = enriched

    html = template.render(
        groups=enriched_groups,
        total_duplicates=len(duplicates)
    )

    with open(output_path, "w", encoding="utf8") as f:
        f.write(html)

def _generate_html(duplicates, output_path: str):
    formatter = HtmlFormatter()
    css = formatter.get_style_defs(".codehilite")

    html_template = """
    <html>
    <head>
        <meta charset="utf-8"/>
        <title>Code Duplicates Report</title>
        <style>
            body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 24px;}
            .meta { margin-bottom: 16px; }
            .pair { border: 1px solid #e5e7eb; border-radius: 10px; margin-bottom: 18px; overflow: hidden; }
            .pair-header { display: flex; justify-content: space-between; background: #f9fafb; padding: 12px 14px; font-weight: 600; }
            .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }
            .col { border-top: 1px solid #e5e7eb; padding: 14px; overflow-x: auto; }
            .path { color: #374151; font-size: 12px; margin-bottom: 8px; }
            .sim { font-variant-numeric: tabular-nums; }
            """ + css + """
            pre { margin: 0; }
        </style>
    </head>
    <body>
        <h2>🔁 Code Duplicates Report</h2>
        <div class="meta">Total detectados: <b>{{ duplicates|length }}</b></div>

        {% for d in duplicates %}
          <div class="pair">
            <div class="pair-header">
              <div>Similarity: <span class="sim">{{ '%.2f'|format(d.similarity) }}</span></div>
              <div>{{ d.a.language }} • {{ d.a.type }}</div>
            </div>
            <div class="cols">
              <div class="col">
                <div class="path">{{ d.a.file }} — lines {{ d.a.lines[0] }}-{{ d.a.lines[1] }}</div>
                {{ d.a_code|safe }}
              </div>
              <div class="col">
                <div class="path">{{ d.b.file }} — lines {{ d.b.lines[0] }}-{{ d.b.lines[1] }}</div>
                {{ d.b_code|safe }}
              </div>
            </div>
          </div>
        {% endfor %}
    </body>
    </html>
    """

    template = Template(html_template)

    enriched = []
    for d in duplicates:
        a_code = _highlight_code(d["a"]["file"], d["a"]["code"])
        b_code = _highlight_code(d["b"]["file"], d["b"]["code"])
        e = dict(d)
        e["a_code"] = a_code
        e["b_code"] = b_code
        enriched.append(e)

    html = template.render(duplicates=enriched)

    with open(output_path, "w", encoding="utf8") as f:
        f.write(html)
