"""Page bodies. Each builder takes one language's content and returns the <main> element."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Final
from urllib.parse import quote_plus

from blog import blog_teaser, page_blog
from components import (
    cta_band, default_cta, e, eyebrow, icon_cards, img, iso_badges, page_hero, phone_role, phone_text, photo,
    quote_buttons, section_head,
)
from data import CERTS, EMAIL, INSTAGRAM, INSTAGRAM_URL, MAP_QUERY, PHONES
from i18n import Content, fmt_number, fmt_weight, local_digits
from icons import icon
from scene import hero_scene
from spec import DIAMETERS, MATERIALS, PRESSURES, SERIES, SPEC, Cell

PRICE_API: Final[str] = "../api/price.php"
CALC_DEFAULT: Final[tuple[str, int, str, int]] = ("pe100", 110, "10", 100)  # material, OD, pressure, length (m)


def _chips(items: list[str], icon_name: str, variant: str = "neu") -> str:
    return "".join(f'<li class="chip chip--{variant}">{icon(icon_name)}{e(x)}</li>' for x in items)


def _unique_clients(t: Content) -> list[str]:
    return list(dict.fromkeys(item for block in t["projects"]["timeline"] for item in block["items"]))


# ---------------------------------------------------------------- home

def _stat(s: Content, lang: str) -> str:
    raw = s["value"]
    value = fmt_number(int(raw), 0, lang, group=lang == "en") if raw.isdigit() else local_digits(raw, lang)
    count = f' data-count="{raw}"' if s["count"] else ""
    return (
        f'<li class="stat neu" data-reveal><strong class="stat__value">'
        f'<span class="stat__affix">{e(s["prefix"])}</span><span{count}>{value}</span><span class="stat__affix">{e(s["suffix"])}</span>'
        f'</strong><span class="stat__label">{e(s["label"])}</span></li>'
    )


def page_index(t: Content) -> str:
    h = t["home"]
    lang = t["lang"]
    stats = "".join(_stat(s, lang) for s in h["stats"])
    apps = "".join(
        f'<li class="app-card neu" data-reveal><span class="app-card__pipe" aria-hidden="true"><i></i></span>'
        f'<span class="feature__icon neu-inset">{icon(a["icon"])}</span><h3>{e(a["title"])}</h3><p>{e(a["text"])}</p></li>'
        for a in h["apps"]
    )
    journey = "".join(
        f'<li class="journey__step" data-reveal><span class="journey__node neu">{icon(j["icon"])}<b>{local_digits(str(i), lang)}</b></span>'
        f'<h3>{e(j["title"])}</h3><p>{e(j["text"])}</p></li>'
        for i, j in enumerate(h["journey"], start=1)
    )
    clients = _chips(_unique_clients(t), "sprout")
    return f"""
<main id="main">
<section class="hero" data-hero>
  <div class="hero__scene" data-scene>{hero_scene()}</div>
  <div class="hero__veil" aria-hidden="true"></div>
  <div class="container hero__inner">
    <div class="hero__copy glass glass--paper">
      {eyebrow(h['eyebrow'])}
      <h1 class="hero__title">{e(h['title_a'])} <em>{e(h['title_em'])}</em> {e(h['title_b'])}</h1>
      <p class="hero__lead">{e(h['lead'])}</p>
      <div class="hero__actions">
        <a class="btn btn--primary btn--lg" href="products.html">{icon('drop')}<span>{e(t['ui']['all_products'])}</span></a>
        <a class="btn btn--neu btn--lg" href="products.html#calculator">{icon('scale')}<span>{e(t['ui']['calc'])}</span></a>
      </div>
      <ul class="hero__badges" role="list">{_chips(h['badges'], 'check', 'glass')}</ul>
    </div>
    <aside class="hero__water glass glass--water" aria-label="{e(h['water_card_label'])}">
      <span class="hero__water-liquid" aria-hidden="true"><i></i><i></i></span>
      <span class="hero__water-label">{e(h['water_card_label'])}</span>
      <strong class="hero__water-value">{e(h['water_card_value'])}</strong>
      <span class="hero__water-unit">{e(h['water_card_unit'])}</span>
    </aside>
  </div>
</section>

<section class="section section--stats">
  <div class="container"><ul class="stats" role="list">{stats}</ul></div>
</section>

<section class="section">
  <div class="container split">
    <div class="split__media" data-reveal>{photo('factory', t['about']['factory_caption'], 1400, 1030, 'pin')}</div>
    <div class="split__copy">
      {section_head(h['intro_eyebrow'], h['intro_title'])}
      <p class="prose" data-reveal>{e(h['intro_text'])}</p>
      <a class="btn btn--neu" href="about.html" data-reveal><span>{e(t['ui']['more'])}</span>{icon('arrow', 'icon--dir')}</a>
    </div>
  </div>
</section>

<section class="section section--tint">
  <div class="container">
    {section_head(h['features_eyebrow'], h['features_title'], center=True)}
    <ul class="grid grid--3" role="list">{icon_cards(h['features'])}</ul>
  </div>
</section>

<section class="section">
  <div class="container">
    {section_head(h['apps_eyebrow'], h['apps_title'], h['apps_text'], center=True)}
    <ul class="grid grid--3 apps" role="list">{apps}</ul>
    <p class="center" data-reveal><a class="btn btn--primary" href="products.html">{icon('drop')}<span>{e(t['ui']['all_products'])}</span></a></p>
  </div>
</section>

<section class="section section--tint journey" data-flow>
  <div class="container">
    {section_head(h['journey_eyebrow'], h['journey_title'], center=True)}
    <div class="journey__track">
      <div class="journey__pipe" aria-hidden="true"><span class="journey__water"></span></div>
      <ol class="journey__steps">{journey}</ol>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">{section_head(h['clients_eyebrow'], h['clients_title'], center=True)}</div>
  <div class="marquee" data-reveal>
    <ul class="marquee__track" role="list">{clients}</ul>
    <ul class="marquee__track" role="list" aria-hidden="true">{clients}</ul>
  </div>
  <p class="center"><a class="btn btn--neu" href="projects.html"><span>{e(t['ui']['view_all'])}</span>{icon('arrow', 'icon--dir')}</a></p>
</section>

<section class="section section--tint">
  <div class="container">
    {section_head(h['certs_eyebrow'], h['certs_title'], center=True)}
    {iso_badges(t)}
  </div>
</section>
{blog_teaser(t)}
{default_cta(t)}
</main>"""


# ---------------------------------------------------------------- about

def page_about(t: Content) -> str:
    a = t["about"]
    lang = t["lang"]
    story = "".join(f"<p data-reveal>{e(p)}</p>" for p in a["story"])
    timeline = "".join(
        f'<li class="timeline__item" data-reveal><span class="timeline__dot" aria-hidden="true"></span>'
        f'<div class="timeline__card neu"><span class="timeline__year">{e(i["year"])}</span><h3>{e(i["title"])}</h3><p>{e(i["text"])}</p></div></li>'
        for i in a["timeline"]
    )
    lines = "".join(
        f'<li class="line-card neu" data-reveal><span class="line-card__num neu-inset">{local_digits(str(n), lang)}</span>'
        f'<span class="line-card__pipe" aria-hidden="true"><i></i></span><h3>{e(l["title"])}</h3><p>{e(l["text"])}</p></li>'
        for n, l in enumerate(a["lines"], start=1)
    )
    facts = "".join(
        f'<li class="fact neu-inset" data-reveal><strong>{e(f["value"])}</strong><span>{e(f["label"])}</span></li>' for f in a["facts"]
    )
    return f"""
<main id="main">
{page_hero(t, 'about')}
<section class="section">
  <div class="container split">
    <div class="split__copy">
      {section_head(a['eyebrow'], a['story_title'])}
      <div class="prose">{story}</div>
      <div class="founder neu" data-reveal>
        <span class="founder__icon neu-inset">{icon('user')}</span>
        <span><small>{e(a['founder_label'])}</small><strong>{e(a['founder_name'])}</strong></span>
      </div>
    </div>
    <div class="split__media" data-reveal>{photo('factory', a['factory_caption'], 1400, 1030, 'pin')}</div>
  </div>
</section>

<section class="section section--tint" data-flow>
  <div class="container">
    {section_head(a['eyebrow'], a['timeline_title'], center=True)}
    <ol class="timeline">
      <li class="timeline__pipe" aria-hidden="true"><span class="timeline__water"></span></li>
      {timeline}
    </ol>
  </div>
</section>

<section class="section">
  <div class="container">
    {section_head(a['facility_eyebrow'], a['facility_title'], center=True)}
    <ul class="grid grid--3" role="list">{lines}</ul>
    <ul class="facts" role="list">{facts}</ul>
  </div>
</section>

<section class="section section--tint">
  <div class="container split split--reverse">
    <div class="split__media" data-reveal>{photo('team', a['team_caption'], 1400, 1040, 'users')}</div>
    <div class="split__copy">
      {section_head(a['facility_eyebrow'], a['team_title'], a['team_text'])}
      <h3 class="subhead" data-reveal>{e(a['honors_title'])}</h3>
      <ul class="chips" role="list" data-reveal>{_chips(a['honors'], 'award')}</ul>
    </div>
  </div>
</section>
{default_cta(t)}
</main>"""


# ---------------------------------------------------------------- products: calculator and spec tables

def _plain(value: float, lang: str) -> str:
    """Wall thickness as printed on the factory sheet (2, 2.4, 11.8)."""
    return local_digits(f"{value:g}", lang)


def _trimmed(value: float, max_decimals: int, lang: str) -> str:
    """Like Intl.NumberFormat with maximumFractionDigits: whole numbers lose their decimals."""
    rounded = round(value, max_decimals)
    return fmt_number(rounded, 0 if rounded.is_integer() else max_decimals, lang)


def _pressure_label(pn: str, t: Content) -> str:
    return f"{local_digits(pn, t['lang'])} {e(t['ui']['pressure_unit'])}"


def _sdr_of(material: str, pn: str) -> str:
    return next(s.sdr for s in SERIES[material] if s.pn == pn)


def _cell(material: str, od: int, pn: str) -> Cell | None:
    return SPEC[material][od][PRESSURES.index(pn)]


def _calc_data(t: Content) -> str:
    p = t["products"]
    data = {
        "pressures": list(PRESSURES),
        "sdr": {m: [s.sdr for s in SERIES[m]] for m in MATERIALS},
        "spec": {m: {str(od): [list(c) if c else None for c in row] for od, row in SPEC[m].items()} for m in MATERIALS},
        "priceUrl": PRICE_API,
        "text": {
            "loading": p["price_loading"],
            "unavailable": p["price_unavailable"],
            "updated": p["price_updated"],
        },
    }
    return f'<script type="application/json" id="pipe-data">{json.dumps(data, ensure_ascii=False, separators=(",", ":"))}</script>'


def _seg(name: str, options: list[tuple[str, str]], checked: str) -> str:
    items = "".join(
        f'<label class="seg__item"><input type="radio" name="{name}" value="{value}"{" checked" if value == checked else ""}>'
        f"<span>{label}</span></label>"
        for value, label in options
    )
    return f'<div class="seg neu-inset">{items}</div>'


def _readout(label: str, out: str, value: str, unit: str) -> str:
    return (
        f'<div class="readout neu-inset"><dt>{e(label)}</dt>'
        f'<dd><b data-out="{out}">{value}</b> <small>{e(unit)}</small></dd></div>'
    )


def _calculator(t: Content) -> str:
    p = t["products"]
    ui = t["ui"]
    lang = t["lang"]
    material, od, pn, length = CALC_DEFAULT
    cell = _cell(material, od, pn)
    if cell is None:
        raise ValueError(f"CALC_DEFAULT {CALC_DEFAULT} points at a size that is not made")
    weight_total = cell.weight * length
    materials = _seg("material", [(m, m.upper()) for m in MATERIALS], material)
    pressures = _seg("pn", [(x, local_digits(x, lang)) for x in PRESSURES], pn)
    ods = "".join(
        f'<option value="{d}"{" selected" if d == od else ""}>{local_digits(str(d), lang)}</option>' for d in DIAMETERS
    )
    inner_scale = (od - 2 * cell.wall) / od
    currency = e(ui["currency"])
    return f"""
    <div class="calc" data-calc>
      <form class="calc__controls neu" data-calc-form novalidate data-reveal>
        <h3>{e(p['calc_title'])}</h3>
        <p>{e(p['calc_text'])}</p>
        <fieldset class="field"><legend class="field__label">{e(p['calc_material'])}</legend>{materials}</fieldset>
        <label class="field"><span class="field__label">{e(p['calc_od'])}</span>
          <span class="select neu-inset"><select name="od">{ods}</select>{icon('chevron', 'select__chev')}</span></label>
        <fieldset class="field"><legend class="field__label">{e(p['calc_pn'])}</legend>{pressures}</fieldset>
        <label class="field"><span class="field__label">{e(p['calc_length'])}</span>
          <input class="input neu-inset" name="length" type="text" inputmode="decimal" autocomplete="off" dir="ltr" value="{local_digits(str(length), lang)}" aria-describedby="calc-length-error">
          <span class="field__error" id="calc-length-error" data-calc-error>{e(p['length_invalid'])}</span></label>
      </form>
      <div class="calc__result neu" data-reveal>
        <div class="calc__visual">
          <svg class="xsection" viewBox="0 0 220 220" aria-hidden="true" focusable="false">
            <defs><radialGradient id="xs-water" cx=".4" cy=".35" r=".75"><stop offset="0" stop-color="#e3f6ff"/><stop offset=".6" stop-color="#63bfe6"/><stop offset="1" stop-color="#1f7fb6"/></radialGradient></defs>
            <circle cx="110" cy="110" r="100" fill="#1b2023"/>
            <circle cx="110" cy="110" r="100" fill="none" stroke="#2f86d6" stroke-width="3" stroke-dasharray="40 588" transform="rotate(-100 110 110)"/>
            <circle class="xsection__water" cx="110" cy="110" r="100" fill="url(#xs-water)" style="transform:scale({inner_scale:.3f})" data-xs-inner/>
            <ellipse cx="80" cy="78" rx="18" ry="9" fill="#fff" opacity=".45" transform="rotate(-30 80 78)"/>
          </svg>
          <p class="calc__badge glass"><b data-out="material">{material.upper()}</b><span data-out="sdr">SDR {local_digits(_sdr_of(material, pn), lang)}</span></p>
        </div>
        <div aria-live="polite">
          <dl class="readouts">
            {_readout(p['calc_wall'], 'wall', _plain(cell.wall, lang), ui['mm'])}
            {_readout(p['calc_id'], 'id', _trimmed(od - 2 * cell.wall, 1, lang), ui['mm'])}
            {_readout(p['calc_weight'], 'weight', fmt_weight(cell.weight, lang), ui['kg'])}
            {_readout(p['calc_total_weight'], 'total-weight', _trimmed(weight_total, 1, lang), ui['kg'])}
          </dl>
          <p class="calc__na" data-out="na" hidden>{e(p['calc_na'])}</p>
          <div class="price glass glass--water" data-price>
            <h4 class="price__title">{icon('scale')}{e(p['price_title'])}</h4>
            <dl class="price__rows">
              <div><dt>{e(p['price_per_kg'])}</dt><dd><b data-out="price-kg">–</b> <small>{currency}</small></dd></div>
              <div><dt>{e(p['price_per_m'])}</dt><dd><b data-out="price-m">–</b> <small>{currency}</small></dd></div>
              <div class="price__total"><dt>{e(p['price_total'])}</dt><dd><b data-out="price-total">–</b> <small>{currency}</small></dd></div>
            </dl>
            <p class="price__status" data-out="price-status">{e(p['price_unavailable'])}</p>
          </div>
          <p class="note">{icon('flask')}<span>{e(p['price_note'])}</span></p>
          <div class="price-call"><span>{e(t['contact']['roles']['quote'])}</span>{quote_buttons(t, 'btn btn--neu btn--sm')}</div>
        </div>
      </div>
    </div>
    {_calc_data(t)}"""


def _spec_table(t: Content, material: str) -> str:
    p = t["products"]
    lang = t["lang"]
    caption = p["table_caption"].replace("{material}", material.upper())
    top = "".join(
        f'<th scope="colgroup" colspan="2" data-col="{s.pn}">{_pressure_label(s.pn, t)}<small>SDR {local_digits(s.sdr, lang)}</small></th>'
        for s in SERIES[material]
    )
    sub = "".join(
        f'<th scope="col" data-col="{x}">{e(p["table_wall"])}</th><th scope="col" data-col="{x}">{e(p["table_weight"])}</th>'
        for x in PRESSURES
    )
    rows = []
    for od, row in SPEC[material].items():
        cells = "".join(
            f'<td data-col="{x}">{_plain(c.wall, lang)}</td><td data-col="{x}">{fmt_weight(c.weight, lang)}</td>'
            if c else f'<td data-col="{x}" class="is-na">–</td><td data-col="{x}" class="is-na">–</td>'
            for x, c in zip(PRESSURES, row)
        )
        rows.append(f'<tr data-row="{od}"><th scope="row">{local_digits(str(od), lang)}</th>{cells}</tr>')
    return f"""
      <div class="table-wrap neu-inset" tabindex="0" role="region" aria-label="{e(caption)}" data-spec-table="{material}">
        <table class="dim-table">
          <caption>{e(caption)}</caption>
          <thead>
            <tr><th scope="col" rowspan="2">{e(p['table_od'])}<small>{e(t['ui']['mm'])}</small></th>{top}</tr>
            <tr>{sub}</tr>
          </thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </div>"""


def page_products(t: Content) -> str:
    p = t["products"]
    mm = t["ui"]["mm"]
    pack_imgs = ("coils-blue", "coils-stack")
    pack = "".join(
        f'<li class="pack-card neu" data-reveal><figure class="photo">{img(name, it["title"], 1400, 1100, "photo__img", "(min-width: 900px) 40vw, 100vw")}</figure>'
        f'<div class="pack-card__body"><h3>{e(it["title"])}</h3><p>{e(it["text"])}</p></div></li>'
        for name, it in zip(pack_imgs, p["pack"])
    )
    tables = "".join(_spec_table(t, m) for m in MATERIALS)
    return f"""
<main id="main">
{page_hero(t, 'products')}
<section class="section">
  <div class="container split">
    <div class="split__copy">
      {section_head(p['what_eyebrow'], p['what_title'])}
      <p class="prose" data-reveal>{e(p['what_text'])}</p>
      <ul class="chips" role="list" data-reveal>
        <li class="chip chip--neu">{icon('ruler')}{e(p['range_label'])}: {e(p['range_value'])} {e(mm)}</li>
        <li class="chip chip--neu">{icon('layers')}PE100 · PE80</li>
        <li class="chip chip--neu">{icon('shield')}{e(t['quality']['standard_title'])}</li>
      </ul>
    </div>
    <div class="split__media" data-reveal>
      <div class="pipe-hero neu">
        <svg class="pipe-hero__svg" viewBox="0 0 400 300" aria-hidden="true" focusable="false">
          <defs>
            <linearGradient id="ph-body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a4247"/><stop offset=".45" stop-color="#15191c"/><stop offset="1" stop-color="#262c30"/></linearGradient>
            <radialGradient id="ph-water" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#d6f2ff"/><stop offset=".6" stop-color="#4fb3e0"/><stop offset="1" stop-color="#1f7fb6"/></radialGradient>
          </defs>
          <rect x="40" y="95" width="260" height="110" fill="url(#ph-body)"/>
          <rect x="40" y="108" width="260" height="4" fill="#2f86d6"/>
          <ellipse cx="40" cy="150" rx="26" ry="55" fill="#1a1f22"/>
          <ellipse cx="300" cy="150" rx="26" ry="55" fill="#2a3035"/>
          <ellipse class="pipe-hero__water" cx="300" cy="150" rx="19" ry="44" fill="url(#ph-water)"/>
          <ellipse cx="294" cy="132" rx="5" ry="13" fill="#fff" opacity=".7"/>
          <g class="pipe-hero__drops" fill="url(#ph-water)"><circle cx="336" cy="170" r="7"/><circle cx="352" cy="196" r="5"/><circle cx="342" cy="226" r="4"/></g>
        </svg>
        <div class="pipe-hero__label glass glass--water"><span>{e(p['range_label'])}</span><strong>{e(p['range_value'])}</strong><small>{e(mm)}</small></div>
      </div>
    </div>
  </div>
</section>

<section class="section section--tint" id="calculator">
  <div class="container">
    {section_head(p['spec_eyebrow'], p['spec_title'], p['spec_text'], center=True)}
    {_calculator(t)}
    <div class="table-block" data-reveal>
      <h3 class="subhead">{e(p['table_title'])}</h3>{tables}
      <p class="note">{icon('flask')}<span>{e(p['table_note'])}</span></p>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    {section_head(p['eyebrow'], p['apps_title'], center=True)}
    <ul class="grid grid--4" role="list">{icon_cards(p['apps'])}</ul>
  </div>
</section>

<section class="section section--tint">
  <div class="container">
    {section_head(p['eyebrow'], p['adv_title'], center=True)}
    <ul class="grid grid--3" role="list">{icon_cards(p['advantages'], 'feature--compact')}</ul>
  </div>
</section>

<section class="section">
  <div class="container">
    {section_head(p['eyebrow'], p['pack_title'], center=True)}
    <ul class="grid grid--2" role="list">{pack}</ul>
  </div>
</section>
{cta_band(t, p['cta_title'], p['cta_text'])}
</main>"""


# ---------------------------------------------------------------- quality

def _cert(i: int, key: str, caption: str, t: Content) -> str:
    wide = key == "award"
    thumb = (
        f'<img src="../assets/img/award.webp" width="338" height="199" alt="{e(caption)}" loading="lazy" decoding="async">'
        if wide else
        f'<img src="../assets/img/{key}-sm.webp" width="360" height="520" alt="{e(caption)}" loading="lazy" decoding="async">'
    )
    return (
        f'<li class="cert neu" data-reveal><button class="cert__btn" type="button" data-lightbox-item data-index="{i}" '
        f'data-full="../assets/img/{key}.webp" data-caption="{e(caption)}" aria-label="{e(t["ui"]["enlarge"])}: {e(caption)}">'
        f'<span class="cert__frame neu-inset{" cert__frame--wide" if wide else ""}">{thumb}</span>'
        f'<span class="cert__zoom glass">{icon("zoom")}</span></button><p>{e(caption)}</p></li>'
    )


def page_quality(t: Content) -> str:
    q = t["quality"]
    certs = "".join(_cert(i, key, q["certs"][key], t) for i, key in enumerate(CERTS))
    iso = "".join(
        f'<li class="iso-card neu" data-reveal><strong dir="ltr">{e(x["code"])}</strong><span>{e(x["text"])}</span></li>' for x in q["iso"]
    )
    return f"""
<main id="main">
{page_hero(t, 'quality')}
<section class="section">
  <div class="container split">
    <div class="split__copy">
      {section_head(q['eyebrow'], q['standard_title'], q['standard_text'])}
      <ul class="iso-list" role="list">{iso}</ul>
    </div>
    <div class="split__media" data-reveal>{photo('extrusion-line', q['lab_title'], 1400, 1180, 'flask')}</div>
  </div>
</section>

<section class="section section--tint">
  <div class="container">
    {section_head(q['eyebrow'], q['lab_title'], q['lab_text'], center=True)}
    <ul class="grid grid--4" role="list">{icon_cards(q['equipment'], 'feature--compact')}</ul>
  </div>
</section>

<section class="section">
  <div class="container">
    {section_head(q['eyebrow'], q['certs_title'], q['certs_text'], center=True)}
    <ul class="certs" role="list" data-lightbox>{certs}</ul>
    {iso_badges(t)}
  </div>
</section>
<dialog class="lightbox" data-lightbox-dialog aria-label="{e(q['certs_title'])}">
  <div class="lightbox__inner glass">
    <button class="lightbox__close btn btn--icon" type="button" data-lightbox-close aria-label="{e(t['ui']['close'])}">{icon('close')}</button>
    <figure class="lightbox__figure"><img src="" alt="" data-lightbox-img><figcaption data-lightbox-caption></figcaption></figure>
    <div class="lightbox__nav">
      <button class="btn btn--icon" type="button" data-lightbox-prev aria-label="{e(t['ui']['prev'])}">{icon('arrow', 'icon--dir-rev')}</button>
      <button class="btn btn--icon" type="button" data-lightbox-next aria-label="{e(t['ui']['next'])}">{icon('arrow', 'icon--dir')}</button>
    </div>
  </div>
</dialog>
{default_cta(t)}
</main>"""


# ---------------------------------------------------------------- projects

def page_projects(t: Content) -> str:
    pr = t["projects"]
    stats = "".join(
        f'<li class="stat neu" data-reveal><strong class="stat__value">{e(s["value"])}</strong><span class="stat__label">{e(s["label"])}</span></li>'
        for s in pr["stats"]
    )
    timeline = "".join(
        f'<li class="timeline__item" data-reveal><span class="timeline__dot" aria-hidden="true"></span>'
        f'<div class="timeline__card neu"><span class="timeline__year">{e(b["year"])}</span>'
        f'<ul class="chips chips--sm" role="list">{_chips(b["items"], "sprout")}</ul></div></li>'
        for b in pr["timeline"]
    )
    gallery = "".join(
        f'<figure class="photo neu" data-reveal>{img(name, pr["gallery_title"], 1400, 1100, "photo__img", "(min-width: 900px) 33vw, 100vw")}</figure>'
        for name in ("coils-stack", "coils-blue", "extrusion-line")
    )
    return f"""
<main id="main">
{page_hero(t, 'projects')}
<section class="section section--stats">
  <div class="container"><ul class="stats stats--3" role="list">{stats}</ul></div>
</section>
<section class="section section--tint" data-flow>
  <div class="container">
    {section_head(pr['eyebrow'], pr['timeline_title'], center=True)}
    <ol class="timeline timeline--wide">
      <li class="timeline__pipe" aria-hidden="true"><span class="timeline__water"></span></li>
      {timeline}
    </ol>
  </div>
</section>
<section class="section">
  <div class="container">
    {section_head(pr['eyebrow'], pr['provinces_title'], center=True)}
    <ul class="chips chips--center" role="list" data-reveal>{_chips(pr['provinces'], 'pin', 'glass')}</ul>
    <h3 class="subhead center" data-reveal>{e(pr['gallery_title'])}</h3>
    <div class="gallery">{gallery}</div>
  </div>
</section>
{default_cta(t)}
</main>"""


# ---------------------------------------------------------------- contact

def _contact_card(icon_name: str, role: str, value_html: str, copy_value: str, t: Content) -> str:
    copy = (
        f'<button class="copy-btn" type="button" data-copy="{e(copy_value)}" data-copied="{e(t["ui"]["copied"])}">'
        f'{icon("copy")}<span>{e(t["ui"]["copy"])}</span></button>'
        if copy_value else ""
    )
    return (
        f'<li class="contact-card neu" data-reveal><span class="feature__icon neu-inset">{icon(icon_name)}</span>'
        f'<span class="contact-card__role">{e(role)}</span>{value_html}{copy}</li>'
    )


def page_contact(t: Content) -> str:
    c = t["contact"]
    lang = t["lang"]
    phone_icons = {"fax": "fax", "ceo": "user"}
    cards = [
        _contact_card(
            phone_icons.get(p["key"], "phone"), phone_role(p, t),
            f'<a class="contact-card__value" href="tel:{p["tel"]}" dir="ltr">{phone_text(p, lang)}</a>',
            p["display"].replace(" ", ""), t,
        )
        for p in PHONES
    ]
    cards.append(_contact_card(
        "mail", c["email_label"], f'<a class="contact-card__value" href="mailto:{EMAIL}" dir="ltr">{EMAIL}</a>', EMAIL, t,
    ))
    cards.append(_contact_card(
        "instagram", c["insta_label"],
        f'<a class="contact-card__value" href="{INSTAGRAM_URL}" target="_blank" rel="noopener" dir="ltr">@{INSTAGRAM}</a>', "", t,
    ))
    subjects = "".join(f"<option>{e(s)}</option>" for s in c["f_subjects"])
    map_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(MAP_QUERY)}"
    return f"""
<main id="main">
{page_hero(t, 'contact')}
<section class="section">
  <div class="container"><ul class="grid grid--3 contact-cards" role="list">{''.join(cards)}</ul></div>
</section>
<section class="section section--tint">
  <div class="container split split--top">
    <div class="split__copy">
      <div class="address glass glass--water" data-reveal>
        <span class="feature__icon neu-inset">{icon('pin')}</span>
        <h2>{e(c['address_label'])}</h2>
        <p class="address__text">{e(c['address'])}</p>
        <p>{e(c['map_hint'])}</p>
        <a class="btn btn--primary" href="{e(map_url)}" target="_blank" rel="noopener">{icon('map')}<span>{e(c['map_button'])}</span></a>
      </div>
      <div class="regions neu" data-reveal>
        <h3>{e(c['regions_title'])}</h3>
        <p>{e(c['regions_text'])}</p>
        <ul class="chips" role="list">{_chips(c['regions'], 'pin', 'glass')}</ul>
      </div>
    </div>
    <form class="contact-form neu" data-contact-form data-mailto="{EMAIL}" novalidate data-reveal>
      <h2>{e(c['form_title'])}</h2>
      <p>{e(c['form_text'])}</p>
      <label class="field"><span class="field__label">{e(c['f_name'])}</span>
        <input class="input neu-inset" name="name" type="text" autocomplete="name" required>
        <span class="field__error" data-error="name">{e(c['f_required'])}</span></label>
      <label class="field"><span class="field__label">{e(c['f_phone'])}</span>
        <input class="input neu-inset" name="phone" type="tel" inputmode="tel" autocomplete="tel" dir="ltr" required>
        <span class="field__error" data-error="phone" data-msg-invalid="{e(c['f_phone_invalid'])}" data-msg-required="{e(c['f_required'])}">{e(c['f_required'])}</span></label>
      <label class="field"><span class="field__label">{e(c['f_subject'])}</span>
        <span class="select neu-inset"><select name="subject">{subjects}</select>{icon('chevron', 'select__chev')}</span></label>
      <label class="field"><span class="field__label">{e(c['f_message'])}</span>
        <textarea class="input neu-inset" name="message" rows="5" placeholder="{e(c['f_message_ph'])}" required></textarea>
        <span class="field__error" data-error="message">{e(c['f_required'])}</span></label>
      <button class="btn btn--primary btn--lg btn--block" type="submit">{icon('mail')}<span>{e(c['f_send'])}</span></button>
      <p class="form-status" data-form-status role="status" hidden>{e(c['f_ok'])}</p>
    </form>
  </div>
</section>
</main>"""


PAGE_BUILDERS: Final[dict[str, Callable[[Content], str]]] = {
    "index": page_index,
    "about": page_about,
    "products": page_products,
    "quality": page_quality,
    "projects": page_projects,
    "blog": page_blog,
    "contact": page_contact,
}
