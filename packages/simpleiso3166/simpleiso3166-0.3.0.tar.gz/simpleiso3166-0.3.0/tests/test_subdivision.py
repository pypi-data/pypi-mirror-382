from simpleiso3166 import Subdivision


class TestSubdivisionSearch:
    def test_exact_match(self) -> None:
        # California should match exactly
        results = list(Subdivision.search_by_name("California"))
        assert any("California" in s.name for s in results)

    def test_case_insensitive_match(self) -> None:
        # Should match regardless of case
        results = list(Subdivision.search_by_name("california"))
        assert any("California" in s.name for s in results)

    def test_partial_match(self) -> None:
        # Should match based on partial token match
        results = list(Subdivision.search_by_name("Calif", ratio=0))
        assert any("California" in s.name for s in results)

    def test_no_match(self) -> None:
        # A nonsense name should return no results
        results = list(Subdivision.search_by_name("Nonsenseland"))
        assert results == []

    def test_multiple_matches(self) -> None:
        # "new" should yield multiple results like New York, New Jersey, etc.
        results = list(Subdivision.search_by_name("new", limit=50))
        assert len(results) > 1

        assert any("New York" in s.name for s in results)
        assert any("New Jersey" in s.name for s in results)

    def test_similarity_threshold(self) -> None:
        # Use a high threshold to eliminate weak matches
        results = list(Subdivision.search_by_name("Calif", ratio=95))
        assert all("Calif" in s.name or "California" in s.name for s in results)

    def test_limit_enforced(self) -> None:
        # Check that the result count doesn't exceed the limit
        results = list(Subdivision.search_by_name("new", limit=3, ratio=0))
        assert len(results) <= 3

    def test_deduplication(self) -> None:
        # Repeated close matches should yield unique subdivisions
        results = list(Subdivision.search_by_name("New York"))
        codes = {s.code for s in results}
        assert len(codes) == len(results)
