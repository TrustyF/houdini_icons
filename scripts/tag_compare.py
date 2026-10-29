"""Tags a fixed sample of icons with the production tagging request on
several Claude models, to check a prompt or model change before running
index_images.tag_icons on every drawing.

    python tag_compare.py <out.json> [variant prefixes, e.g. "Claude Haiku"]

Writes every variant's tags, token usage and timing per icon, plus the
rendered images, to out.json for side-by-side review. Requests are sent
directly (not through the Batch API) so results come back immediately.
"""
import sys
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor

import anthropic
from db_loader import session
from icon_model import Icon
from icon_render import render_svg
from index_images import ICONS_PER_REQUEST, TAG_LIMITS, tag_request, parse_tags, encode_image, icon_names

claude = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY (index_images loads .env)

SAMPLE_SEED = 7


def run_claude(model, fallbacks):
    def run(items):
        extra = {}
        if fallbacks:
            # Re-runs a safety-declined request on Anthropic's recommended model instead of failing
            extra = {"extra_headers": {"anthropic-beta": "server-side-fallback-2026-07-01"},
                     "extra_body": {"fallbacks": "default"}}
        response = claude.messages.create(**tag_request(items, model), **extra)
        usage = {"input": response.usage.input_tokens / len(items), "output": response.usage.output_tokens / len(items)}
        return parse_tags(response, len(items)), usage
    return run


VARIANTS = {
    # Sonnet is what index_images.tag_icons runs
    "Claude Sonnet 5.5": run_claude("claude-sonnet-5-5", fallbacks=True),
    "Claude Haiku 5.5": run_claude("claude-haiku-5-5", fallbacks=False),
    "Claude Opus 5.5": run_claude("claude-opus-5-5", fallbacks=True),
}


def luminance(svg):
    img = render_svg(svg, 64)
    px = [p for p in img.getdata() if p[3] > 128]
    return sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b, _ in px) / max(len(px), 1)


def pick_sample():
    rng = random.Random(SAMPLE_SEED)
    icons = session.query(Icon).order_by(Icon.id).all()
    keys = {}
    for icon in icons:
        keys.setdefault((icon.category, icon.name), []).append(icon)
    versions = {i.id: {v.version for v in i.versions} for i in icons}

    nodes = [i for i in icons if i.id <= 4075 and i.category in ('SOP', 'VOP', 'DOP', 'LOP', 'COP', 'OBJ', 'CHOP', 'TOP')]
    skin = [i for i in icons if versions[i.id] == {'22'} and len(keys[(i.category, i.name)]) > 1]
    new = [i for i in icons if len(keys[(i.category, i.name)]) == 1 and not versions[i.id] & {'19.5', '20', '20.5'}]

    sample = rng.sample(nodes, 8) + rng.sample(skin, 8) + rng.sample(new, 8)
    light_pool = [i for i in rng.sample(icons, 400) if i not in sample]
    sample += sorted(light_pool, key=lambda i: -luminance(i.svg))[:6]
    groups = ['node'] * 8 + ['H22 skin'] * 8 + ['new'] * 8 + ['light'] * 6
    return list(zip(groups, sample))


def main(out_path, only=None):
    sample = pick_sample()
    names = [n for n in VARIANTS if not only or any(n.startswith(o) for o in only)]
    items = [(icon.svg, icon_names([icon], 1)) for _, icon in sample]
    chunks = [list(range(k, min(k + ICONS_PER_REQUEST, len(items)))) for k in range(0, len(items), ICONS_PER_REQUEST)]
    jobs = [(name, chunk) for name in names for chunk in chunks]

    def run(job):
        name, chunk = job
        start = time.time()
        try:
            tags, usage = VARIANTS[name]([items[k] for k in chunk])
            seconds = round((time.time() - start) / len(chunk), 1)
            return name, chunk, [{"tags": t, "usage": usage, "seconds": seconds} if t else {"error": "missing from response"}
                                 for t in tags]
        except Exception as e:
            return name, chunk, [{"error": f'{type(e).__name__}: {e}'}] * len(chunk)

    results = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        for name, chunk, chunk_results in executor.map(run, jobs):
            for k, result in zip(chunk, chunk_results):
                results.setdefault(k, {})[name] = result
            print(f'{name:20} icons {chunk[0]}-{chunk[-1]}: {sum("error" not in r for r in chunk_results)}/{len(chunk)} ok')

    out = {
        "variants": names,
        "icons": [{
            "id": icon.id, "group": group, "category": icon.category, "name": icon.name,
            "versions": sorted(v.version for v in icon.versions),
            "existing_tags": {kind: [[a.tag.name, a.weight] for a in icon.tags if a.type + 's' == kind]
                              for kind in TAG_LIMITS},
            "image": encode_image(icon.svg, 512),
            "results": results[k],
        } for k, (group, icon) in enumerate(sample)],
    }
    with open(out_path, 'w') as f:
        json.dump(out, f)


if __name__ == '__main__':
    # Optional second argument: comma-separated variant name prefixes to run
    main(sys.argv[1], sys.argv[2].split(',') if len(sys.argv) > 2 else None)
