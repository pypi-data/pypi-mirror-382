from thefuzz import fuzz

LENGTH_RATIO_THRESHOLD = 0.5


SHORT_TERM_LENGTH = 5


def fuzzy_match(field_value: str, search_term: str, threshold: float = 80) -> bool:
    if not field_value or not search_term:
        return False

    # To prevent short terms like "get" from matching long terms like "getFindItAttempts"
    # we use a combination of different metrics

    # If the search term size is very small compared to the field
    # we dynamically increase the threshold
    length_ratio = len(search_term) / len(field_value) if len(field_value) > 0 else 0

    if length_ratio < LENGTH_RATIO_THRESHOLD and len(search_term) <= SHORT_TERM_LENGTH:
        # For short terms searched in long fields, use token_sort_ratio
        # which is stricter when dealing with substrings
        score = fuzz.token_sort_ratio(field_value.lower(), search_term.lower())
        # Increase threshold for short terms
        adjusted_threshold = threshold + (30 * (1 - length_ratio))
        return bool(score > adjusted_threshold)

    # For other cases, use ratio which compares the complete strings
    # instead of partial_ratio which looks for substrings
    score = fuzz.ratio(field_value.lower(), search_term.lower())

    # If still no match and strings have similar length, try token_set_ratio
    if score <= threshold and length_ratio > LENGTH_RATIO_THRESHOLD:
        score = max(score, fuzz.token_set_ratio(field_value.lower(), search_term.lower()))

    return bool(score > threshold)


def fuzzy_path_match(real_path: str, search_path: str, threshold: float = 70) -> bool:
    if not real_path or not search_path:
        return False

    # 1. Normalize: unify separators and lowercase
    real = real_path.replace("\\", "/").lower()
    search = search_path.replace("\\", "/").lower()

    # 2. If search term contains '/', treat as path comparison
    if "/" in search:
        score_full = fuzz.ratio(real, search)
        score_partial = fuzz.partial_ratio(real, search)
        score_token = fuzz.token_sort_ratio(real, search)
        score = max(score_full, score_partial, score_token)
        return bool(score >= threshold)

    # 3. For simple terms, split into file/directories
    segments = real.split("/")
    filename = segments[-1]
    dirpath = "/".join(segments[:-1])

    # Filename similarity (more important)
    score_fn = max(fuzz.ratio(filename, search), fuzz.partial_ratio(filename, search))
    # Directory path similarity (less weight)
    score_dir = fuzz.partial_ratio(dirpath, search)

    # 4. Combine with weights (70% filename, 30% directories)
    combined_score = score_fn * 0.7 + score_dir * 0.3
    return bool(combined_score >= threshold)


def get_search_terms(*names: str) -> list[str]:
    search_terms: list[str] = []
    for name in names:
        name_parts = name.split(".")

        # If no dot notation, simply use the full name
        if len(name_parts) == 1:
            search_terms.append(name)
            continue

        # Start with individual segments (excluding first segment if likely an import alias)
        for part in reversed(name_parts[1:]):
            if part not in search_terms:
                search_terms.append(part)

        # Then try combined segments starting from the end
        for i in range(2, len(name_parts)):
            term = ".".join(name_parts[-i:])
            if term not in search_terms:
                search_terms.append(term)

        # Finally add the full name as fallback
        if name not in search_terms:
            search_terms.append(name)

    return search_terms
