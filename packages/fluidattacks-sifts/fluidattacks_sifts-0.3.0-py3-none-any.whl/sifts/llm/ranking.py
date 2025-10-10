from collections.abc import Iterable

from sifts.common_types.snippets import SnippetHit

MIN_SCORE_THRESHOLD = 0.5


def _build_ranked_maps(
    hits_lists: Iterable[Iterable[SnippetHit]],
) -> list[dict[str, tuple[int, SnippetHit]]]:
    ranked_maps: list[dict[str, tuple[int, SnippetHit]]] = []
    for hit_list in hits_lists:
        ranking: dict[str, tuple[int, SnippetHit]] = {}
        for rank, hit in enumerate(hit_list, start=1):
            vuln_id = hit["_source"]["metadata"]["vulnerability_id"]
            ranking[vuln_id] = (rank, hit)
        ranked_maps.append(ranking)
    return ranked_maps


def _compute_rrf_scores(
    all_ids: set[str],
    ranked_maps: list[dict[str, tuple[int, SnippetHit]]],
    c: int,
) -> tuple[dict[str, float], dict[str, SnippetHit]]:
    re_rank_scores: dict[str, float] = {}
    id_to_any_hit: dict[str, SnippetHit] = {}
    for vuln_id in all_ids:
        rrf_score = 0.0
        for ranking in ranked_maps:
            if vuln_id in ranking:
                rank, hit = ranking[vuln_id]
                rrf_score += 1.0 / (c + rank)
                if vuln_id not in id_to_any_hit:
                    id_to_any_hit[vuln_id] = hit
        re_rank_scores[vuln_id] = rrf_score
    return re_rank_scores, id_to_any_hit


def _filter_and_format_hits(
    sorted_items: list[tuple[str, float]],
    id_to_any_hit: dict[str, SnippetHit],
    top_n: int,
    min_score_threshold: float,
) -> list[SnippetHit]:
    reranked_hits: list[SnippetHit] = []
    for vuln_id, score in sorted_items[:top_n]:
        if score < min_score_threshold:
            continue
        hit = id_to_any_hit[vuln_id].copy()
        hit["ReRankingScore"] = score
        reranked_hits.append(hit)
    return reranked_hits


def reciprocal_rank_fusion(
    hits_lists: Iterable[Iterable[SnippetHit]],
    top_n: int = 10,
    c: int = 60,
    min_score_threshold: float = 0.0,
) -> list[SnippetHit]:
    ranked_maps = _build_ranked_maps(hits_lists)
    if not ranked_maps:
        return []
    all_ids = set().union(*[m.keys() for m in ranked_maps])
    re_rank_scores, id_to_any_hit = _compute_rrf_scores(all_ids, ranked_maps, c)
    sorted_items = sorted(re_rank_scores.items(), key=lambda x: x[1], reverse=True)
    sorted_items = [x for x in sorted_items if x[1] >= min_score_threshold]
    return _filter_and_format_hits(sorted_items, id_to_any_hit, top_n, min_score_threshold)


def _compute_rrf_scores_pure(
    all_ids: set[str],
    ranked_maps: list[dict[str, tuple[int, SnippetHit]]],
) -> tuple[dict[str, float], dict[str, SnippetHit]]:
    pure_scores: dict[str, float] = {}
    id_to_any_hit: dict[str, SnippetHit] = {}
    for vuln_id in all_ids:
        score = 0.0
        for ranking in ranked_maps:
            if vuln_id in ranking:
                rank, hit = ranking[vuln_id]
                score += 1.0 / rank
                if vuln_id not in id_to_any_hit:
                    id_to_any_hit[vuln_id] = hit
        pure_scores[vuln_id] = score
    return pure_scores, id_to_any_hit


def reciprocal_rank_fusion_pure(
    hits_lists: Iterable[Iterable[SnippetHit]],
    top_n: int = 10,
    min_score_threshold: float = 0.0,
) -> list[SnippetHit]:
    ranked_maps = _build_ranked_maps(hits_lists)
    if not ranked_maps:
        return []
    all_ids = set().union(*[m.keys() for m in ranked_maps])
    pure_scores, id_to_any_hit = _compute_rrf_scores_pure(all_ids, ranked_maps)
    sorted_items = sorted(pure_scores.items(), key=lambda x: x[1], reverse=True)
    return _filter_and_format_hits(sorted_items, id_to_any_hit, top_n, min_score_threshold)
