#!/usr/bin/env python3
"""
Normalizador do modelo de dados agnostico para o setor Social.

Le todos os JSON exportados do BigQuery (conector Fivetran / Facebook Pages),
classifica cada tabela pelo seu esquema e emite uma unica base em formato longo:

    data | plataforma | conta | nivel | objeto_id | metrica_canonica | valor | etapa_funil | categoria

O mesmo script serve para Facebook (hoje) e Instagram (futuro): basta acrescentar
entradas no DICIONARIO. A tabela fato e o dashboard nao mudam.
"""

import json, os, glob, csv
from datetime import datetime

UPLOADS = "/mnt/user-data/uploads"
OUT_DIR = "/home/claude"

# ---------------------------------------------------------------------------
# DICIONARIO DE METRICAS  ->  o coracao agnostico.
# campo_bruto : (metrica_canonica, etapa_funil, categoria)
# ---------------------------------------------------------------------------
DICIONARIO = {
    # -------- TOPO / visibilidade --------
    "page_video_views":      ("visualizacoes_video", "topo", "visibilidade"),
    "post_video_views":      ("visualizacoes_video", "topo", "visibilidade"),
    "page_media_view":       ("visualizacoes_midia", "topo", "visibilidade"),
    "post_media_view":       ("visualizacoes_midia", "topo", "visibilidade"),
    "page_impressions":      ("impressoes",          "topo", "visibilidade"),
    "post_impressions":      ("impressoes",          "topo", "visibilidade"),

    # -------- MEIO / engajamento --------
    "page_post_engagements": ("interacoes",          "meio", "engajamento"),
    "post_clicks_engaj":     ("interacoes",          "meio", "engajamento"),
    "like_count":            ("reacoes",             "meio", "engajamento"),
    "comment_count":         ("comentarios",         "meio", "engajamento"),
    "share_count":           ("compartilhamentos",   "meio", "engajamento"),
    "post_video_complete_views_organic": ("videos_completos", "meio", "engajamento"),

    # -------- MEIO / audiencia --------
    "page_follows":          ("seguidores",          "meio", "audiencia"),
    "page_daily_follows":    ("novos_seguidores",    "meio", "audiencia"),
    "page_views_total":      ("visualizacoes_perfil","meio", "audiencia"),

    # -------- FUNDO / acao --------
    "post_clicks":           ("cliques",             "fundo", "acao"),
    "page_total_actions":    ("acoes_pagina",        "fundo", "acao"),
}

# reacoes agregadas (soma das reacoes por tipo) -> uma metrica canonica so
REACAO_PREFIXOS_PAGE = "page_actions_post_reactions_"
REACAO_PREFIXOS_POST = "post_reactions_"


def parse_data(v):
    if not v:
        return None
    v = str(v).replace(" UTC", "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%d"):
        try:
            return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return v[:10]


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def classificar(row):
    """Descobre o tipo de tabela pela assinatura de campos."""
    k = set(row.keys())
    if {"metric_name", "value", "page_id"} <= k:
        return "page_metric_long"
    if "page_post_engagements" in k:
        return "page_insights"
    if "post_clicks" in k and "post_video_views" in k:
        return "post_insights"
    if {"like_count", "comment_count", "share_count"} <= k:
        return "post_stats"
    if {"fan_count", "followers_count", "category"} <= k:
        return "page_dim"
    if "page_media_view" in k and "is_from_ads" in k:
        return "page_media_split"
    if "post_media_view" in k and ("is_from_ads" in k or "is_from_followers" in k):
        return "post_media_split"
    return "dimensao_conteudo"  # attachments, tags, media props


def emit(base, **kw):
    base.append(kw)


def normalizar():
    base = []
    conta = "Atacadão SA"      # default; sobrescrito quando o campo existir
    dim_conta = {}
    ignoradas = {}

    for path in sorted(glob.glob(os.path.join(UPLOADS, "*.json"))):
        rows = json.load(open(path, encoding="utf-8"))
        if isinstance(rows, dict):
            rows = [rows]
        for row in rows:
            tipo = classificar(row)

            if tipo == "page_dim":
                dim_conta = {
                    "conta": row.get("name"),
                    "categoria_pagina": row.get("category"),
                    "seguidores_total": num(row.get("followers_count")),
                    "falando_sobre": num(row.get("talking_about_count")),
                }
                conta = row.get("name") or conta
                continue

            if tipo in ("page_media_split", "post_media_split", "dimensao_conteudo"):
                ignoradas[tipo] = ignoradas.get(tipo, 0) + 1
                continue  # detalhamentos / dimensoes: nao entram no total p/ evitar dupla contagem

            data = parse_data(row.get("date") or row.get("created_date") or row.get("created_time"))
            nome = row.get("page_name") or conta
            pid = row.get("page_id") or row.get("id")
            postid = row.get("post_id")
            nivel = "post" if postid else "conta"
            objeto = postid or pid

            def add(campo_dic, valor):
                if valor is None:
                    return
                mc, etapa, cat = DICIONARIO[campo_dic]
                emit(base, data=data, plataforma="facebook", conta=nome,
                     nivel=nivel, objeto_id=objeto, metrica_canonica=mc,
                     valor=valor, etapa_funil=etapa, categoria=cat)

            if tipo == "page_metric_long":
                mn = row.get("metric_name")
                if mn in DICIONARIO:
                    add(mn, num(row.get("value")))
                continue

            if tipo == "page_stats" if False else False:
                pass

            if tipo in ("page_insights", "post_insights"):
                for campo in DICIONARIO:
                    if campo in row and campo not in ("post_clicks_engaj",):
                        add(campo, num(row.get(campo)))
                # soma de reacoes
                pref = REACAO_PREFIXOS_PAGE if tipo == "page_insights" else REACAO_PREFIXOS_POST
                total_reac = sum(num(v) or 0 for k, v in row.items()
                                 if k.startswith(pref) and k.endswith("_total"))
                if total_reac:
                    emit(base, data=data, plataforma="facebook", conta=nome,
                         nivel=nivel, objeto_id=objeto, metrica_canonica="reacoes",
                         valor=total_reac, etapa_funil="meio", categoria="engajamento")

            if tipo == "post_stats":
                for campo in ("like_count", "comment_count", "share_count"):
                    add(campo, num(row.get(campo)))

    return base, dim_conta, ignoradas


# metricas de ESTOQUE (snapshot): nao se somam entre datas -> pega o valor mais recente
METRICAS_SNAPSHOT = {"seguidores"}


def deduplicar(base):
    """Remove linhas identicas (mesma data/objeto/metrica) — trata tabelas repetidas."""
    visto, limpa = set(), []
    for r in base:
        chave = (r["data"], r["plataforma"], r["nivel"], r["objeto_id"], r["metrica_canonica"])
        if chave in visto:
            continue
        visto.add(chave)
        limpa.append(r)
    return limpa


def agregar(base):
    """Agrega por etapa/categoria/metrica. Fluxo = soma; estoque = valor mais recente."""
    por_metrica, por_etapa = {}, {}
    for r in base:
        m = r["metrica_canonica"]
        d = por_metrica.setdefault(m, {"valor": 0, "etapa": r["etapa_funil"],
                                        "cat": r["categoria"], "_data": ""})
        if m in METRICAS_SNAPSHOT:
            if r["data"] >= d["_data"]:      # mantem o snapshot mais recente
                d["valor"], d["_data"] = r["valor"], r["data"]
        else:
            d["valor"] += r["valor"]         # fluxo: acumula
    for m, d in por_metrica.items():
        d.pop("_data", None)
        por_etapa[d["etapa"]] = por_etapa.get(d["etapa"], 0) + d["valor"]
    return por_metrica, por_etapa


if __name__ == "__main__":
    base, dim, ign = normalizar()
    base = deduplicar(base)

    # grava base longa
    with open(os.path.join(OUT_DIR, "base_agnostica.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["data", "plataforma", "conta", "nivel",
                                          "objeto_id", "metrica_canonica", "valor",
                                          "etapa_funil", "categoria"])
        w.writeheader()
        for r in base:
            w.writerow(r)

    por_metrica, por_etapa = agregar(base)

    print("=" * 60)
    print(f"Conta: {dim.get('conta')}  |  categoria: {dim.get('categoria_pagina')}")
    print(f"Seguidores (dimensao): {dim.get('seguidores_total'):,.0f}")
    print("=" * 60)
    print(f"Linhas na base agnostica: {len(base)}")
    print(f"Tabelas de detalhe ignoradas (evita dupla contagem): {ign}")
    print("-" * 60)
    print("Por etapa de funil:")
    for e in ("topo", "meio", "fundo"):
        print(f"  {e:6} -> {por_etapa.get(e, 0):,.0f}")
    print("-" * 60)
    print("Por metrica canonica:")
    for m, d in sorted(por_metrica.items(), key=lambda x: -x[1]["valor"]):
        print(f"  [{d['etapa']:5}/{d['cat']:12}] {m:24} {d['valor']:,.0f}")

    # exporta agregados p/ o dashboard
    json.dump({"conta": dim, "por_metrica": por_metrica, "por_etapa": por_etapa},
              open(os.path.join(OUT_DIR, "agregados.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
