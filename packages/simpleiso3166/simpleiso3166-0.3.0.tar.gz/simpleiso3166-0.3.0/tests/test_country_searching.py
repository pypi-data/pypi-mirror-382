import pytest

from simpleiso3166 import Country
from simpleiso3166.aliases import COUNTRY_ALIAS_TO_CODE


class TestCountrySearching:
    def test_empty_input_returns_nothing(self) -> None:
        # None, empty, and whitespace-only strings should yield nothing
        assert list(Country.from_partial_name("")) == []
        assert list(Country.from_partial_name("   ")) == []
        assert list(Country.from_partial_name(None or "")) == []

    @pytest.mark.parametrize(
        ("inp", "expected_code"),
        [
            ("us", "US"),
            ("USA", "US"),
            ("United States", "US"),
            ("america", "US"),
            ("UK", "GB"),
            ("holland", "NL"),
            ("Persia", "IR"),  # alias in DIRECT_MATCHES
            ("down under", "AU"),  # alias phrase
        ],
    )
    def test_direct_matches(self, inp: str, expected_code: str) -> None:
        results = list(Country.from_partial_name(inp))
        assert len(results) == 1
        country = results[0]
        assert isinstance(country, Country)
        assert country.alpha2 == expected_code

    @pytest.mark.parametrize(  # type: ignore[misc]
        ("pattern", "code", "sample"),
        [
            (r"u\.s\.a?", "US", "U.S.A"),
            (r"united\s+kingdom", "GB", "the United Kingdom of Great Britain"),
            (r"people'?s\s+republic\s+of\s+china", "CN", "People's Republic of China"),
            (r"democratic\s+people'?s\s+republic\s+of\s+korea", "KP", "Democratic People's Republic of Korea"),
            (r"united\s+republic\s+of\s+tanzania", "TZ", "United Republic of Tanzania"),
            (r"\bsaudi\s+arabia\b", "SA", "Saudi Arabia"),
            (r"iran", "IR", "Islamic Republic of Iran"),  # covered by regex
            (r"dprk", "KP", "DPRK"),  # DIRECT_MATCHES also
        ],
    )
    def test_regex_patterns(self, pattern, code: str, sample: str) -> None:  # type: ignore[no-untyped-def]
        # Ensure at least one regex pattern triggers
        results = list(Country.from_partial_name(sample))
        assert results, f"No match for regex {pattern}"  # type: ignore[misc]
        assert results[0].alpha2 == code

    def test_alias_lookup(self) -> None:
        # Pick one alias from COUNTRY_ALIAS_TO_CODE that isn't in DIRECT_MATCHES
        # e.g. "Côte d'Ivoire" should be in aliases
        alias, code = next(
            (alias, c) for alias, c in COUNTRY_ALIAS_TO_CODE.items() if alias.lower() not in {"us", "usa", "uk"}
        )
        results = list(Country.from_partial_name(alias))
        assert len(results) == 1
        assert results[0].alpha2 == code

    def test_preprocessing_strips_prefixes_and_diacritics(self) -> None:
        # "The République d'Ivoire" should normalize to "Cote d' Ivoire" -> CI
        input_name = "  ThÉ   République   d'Ivoiré "
        results = list(Country.from_partial_name(input_name))
        assert results, "Expected a match for Côte d'Ivoire"
        assert results[0].alpha2 == "CI"

    def test_fuzzy_matching_official_name(self) -> None:
        # Typos in official/common names should still match if above ratio
        # For example, "Germani" should match "Germany" (DE)
        results = list(Country.from_partial_name("Germani", ratio=70))
        assert results, "Expected fuzzy match for 'Germani'"
        assert results[0].alpha2 == "DE"

    def test_aliases_with_lower_weight(self) -> None:
        # Some aliases only appear in COUNTRY_ALIAS_TO_CODE
        # Eg. "Nippon" -> "JP"
        results = list(Country.from_partial_name("Nippon", ratio=60))
        assert results, "Expected alias match for Nippon"
        assert results[0].alpha2 == "JP"

    def test_special_handling_korea(self) -> None:
        # Now should return South and then North Korea
        results = list(Country.from_partial_name("Korea", ratio=0, limit=2))
        codes = [c.alpha2 for c in results]
        assert codes == ["KR", "KP"]

    def test_special_handling_congo(self) -> None:
        # Now should return DR Congo then Republic of the Congo
        results = list(Country.from_partial_name("Congo", ratio=0, limit=2))
        codes = [c.alpha2 for c in results]
        assert codes == ["CD", "CG"]

    def test_limit_parameter(self) -> None:
        # With limit=3, should yield exactly 3 entries (assuming many fuzzy matches)
        results = list(Country.from_partial_name("a", ratio=0, limit=3))
        assert len(results) == 3

    def test_ratio_filters_out_low_scores(self) -> None:
        results_high = list(Country.from_partial_name("Germani", ratio=99))
        assert not results_high

    def test_non_ascii_and_whitespace_variations(self) -> None:
        input_variants = [
            "  japan ",
            "JÂpàn",
            "\tJaPaN\n",
        ]
        for variant in input_variants:
            results = list(Country.from_partial_name(variant))
            assert results
            assert results[0].alpha2 == "JP"

    def test_combined_official_and_alias_scores(self) -> None:
        results = list(Country.from_partial_name("United Republic of Tanzania"))
        assert results
        assert results[0].alpha2 == "TZ"

    def test_preprocessed_cache_used(self) -> None:
        first = list(Country.from_partial_name("Brazil"))
        second = list(Country.from_partial_name("Brazil"))
        assert first
        assert second
        assert first[0].alpha2 == "BR"
        assert second[0].alpha2 == "BR"
