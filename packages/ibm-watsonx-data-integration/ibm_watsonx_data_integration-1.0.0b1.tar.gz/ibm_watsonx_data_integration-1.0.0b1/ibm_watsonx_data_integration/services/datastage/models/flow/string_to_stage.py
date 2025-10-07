from ibm_watsonx_data_integration.services.datastage.models.stage_names import STAGE_NAMES


def clean_stage_name(stage_name: str) -> str:
    """Convert a stage name to a form that is easily comparable."""
    return stage_name.replace(" ", "").replace("/", "").lower()


# Cached mapping of cleaned stage names to their corresponding full names
CLEAN_STAGE_NAMES = {clean_stage_name(name): name for name in STAGE_NAMES.keys()}


def string_to_stage_class(string: str):
    """Converts a string to a StageType enum. The string is stripped of whitespace and case is ignored during comparison.

    If the string is close to a valid stage type but not an exact match, a ValueError is raised with a suggestion.

    Args:
        string (str): The string representation of the stage type.

    Returns:
        StageType: The corresponding StageType enum value.
    """
    # First check for exact stage name match
    if string in STAGE_NAMES:
        return STAGE_NAMES[string]

    # Then try to clean the string and check against cleaned names
    clean_string = clean_stage_name(string)
    if clean_string in CLEAN_STAGE_NAMES:
        return STAGE_NAMES[CLEAN_STAGE_NAMES[clean_string]]

    # If no exact match, calculate Damerau-Levenshtein distance to find close matches
    scored = [
        (damerau_levenshtein(clean_string, candidate), CLEAN_STAGE_NAMES[candidate])
        for candidate in CLEAN_STAGE_NAMES.keys()
    ]
    scored.sort()

    # If the closest match is a probable typo, suggest it
    if scored and scored[0][0] <= 2:  # Allow a maximum distance of 2 for typos
        raise ValueError(f'Invalid stage type string: "{string}". Did you mean "{scored[0][1]}"?')

    raise ValueError(f"Invalid stage type string: {string}")


def is_probable_typo(s1: str, s2: str, max_ratio: float = 0.2) -> tuple[int, bool]:
    """Check if two strings are likely to be typos of each other based on the Damerau-Levenshtein distance."""
    if not s1 and not s2:
        return 0, False

    dist = damerau_levenshtein(s1, s2)
    max_len = max(len(s1), len(s2))
    ratio = dist / max_len
    return dist, (ratio <= max_ratio)


def damerau_levenshtein(s1: str, s2: str) -> int:
    """Compute the Damerau–Levenshtein distance between strings s1 and s2.
    This counts insertions, deletions, substitutions, and transposition of two adjacent characters.

    https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance
    """
    len1, len2 = len(s1), len(s2)
    maxdist = len1 + len2

    # Create the distance matrix with extra padding for the algorithm
    d = [[0] * (len2 + 2) for _ in range(len1 + 2)]
    d[0][0] = maxdist
    for i in range(len1 + 1):
        d[i + 1][0] = maxdist
        d[i + 1][1] = i
    for j in range(len2 + 1):
        d[0][j + 1] = maxdist
        d[1][j + 1] = j

    # Track the last row each character was encountered in s1 or s2
    last_row = {ch: 0 for ch in set(s1 + s2)}

    for i in range(1, len1 + 1):
        last_match_col = 0
        for j in range(1, len2 + 1):
            i1 = last_row[s2[j - 1]]
            j1 = last_match_col
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            if cost == 0:
                last_match_col = j

            # substitution, insertion, deletion
            d[i + 1][j + 1] = min(
                d[i][j] + cost,
                d[i + 1][j] + 1,
                d[i][j + 1] + 1,
                # transposition
                d[i1][j1] + (i - i1 - 1) + 1 + (j - j1 - 1),
            )

        last_row[s1[i - 1]] = i

    return d[len1 + 1][len2 + 1]
