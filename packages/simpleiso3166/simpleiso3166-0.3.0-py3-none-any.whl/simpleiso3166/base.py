from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Final
from typing import cast

from simpleiso3166.errors import NoCountryBestNameError

if TYPE_CHECKING:
    from collections.abc import Generator

    from simpleiso3166.generated.types import CountryCodeAlpha2Type
    from simpleiso3166.generated.types import CountryCodeAlpha3Type
    from simpleiso3166.generated.types import SubdivisionTypeType

logger = logging.getLogger(__name__)

# Add slots=True if the Python version is 3.10 or higher
if sys.version_info >= (3, 10):
    DATACLASS_BASE_AGS: Final[dict[str, bool]] = {"frozen": True, "slots": True}
else:
    DATACLASS_BASE_AGS: Final[dict[str, bool]] = {"frozen": True}


@dataclass(**DATACLASS_BASE_AGS)
class Country:
    """
    Data object containing information about a single country.

    Subdivisions are accessible via the ``subdivisions`` attribute, which loads lazily.
    """

    alpha2: CountryCodeAlpha2Type
    alpha3: CountryCodeAlpha3Type
    name: str | None
    common_name: str | None
    official_name: str | None
    subdivisions: list[Subdivision] = field(repr=False)

    def contains_subdivision(self, subdivision_code: str) -> bool:
        """
        Returns True if the given subdivision code is a valid subdivision of this country
        """
        return any(subdivision.code == subdivision_code for subdivision in self.subdivisions)

    @property
    def best_name(self) -> str:
        """
        Returns the most common name for a country, based on what is available
        """
        if self.common_name:
            return self.common_name
        if self.name:
            return self.name
        if self.official_name:
            return self.official_name
        raise NoCountryBestNameError("Unable to determine best name option")  # noqa: EM101, TRY003

    def get_subdivision(self, subdivision_code: str) -> Subdivision | None:
        """
        Returns the subdivision with the given code if it exists, otherwise returns None.

        See also contains_subdivision for a more convenient way to check if the given code is valid.
        """
        for subdivision in self.subdivisions:
            if subdivision.code == subdivision_code:
                return subdivision
        return None

    def get_subdivision_name(self, subdivision_code: str) -> str | None:
        """
        Accessor to convert a subdivision code to its name, or None if the given code is not valid for this country.
        """
        for subdivision in self.subdivisions:
            if subdivision.code == subdivision_code:
                return subdivision.name
        return None

    @staticmethod
    def from_alpha2(alpha2: CountryCodeAlpha2Type) -> Country | None:
        """
        Constructs a Country object from an alpha-2 code, if the code is valid.
        """
        from simpleiso3166.generated.mapping import ALPHA2_CODE_TO_COUNTRIES  # noqa: PLC0415

        return ALPHA2_CODE_TO_COUNTRIES.get(alpha2)

    @staticmethod
    def from_alpha3(alpha3: CountryCodeAlpha3Type) -> Country | None:
        """
        Constructs a Country object from an alpha-2 code, if the code is valid.
        """
        from simpleiso3166.generated.mapping import ALPHA3_CODE_TO_COUNTRIES  # noqa: PLC0415

        return ALPHA3_CODE_TO_COUNTRIES.get(alpha3)

    @staticmethod
    def from_name(name: str) -> Country | None:
        """
        Constructs a Country object from an name, if the name is valid.
        """
        from simpleiso3166.generated.mapping import ALPHA2_CODE_TO_COUNTRIES  # noqa: PLC0415

        for country in ALPHA2_CODE_TO_COUNTRIES.values():
            if (
                (country.name is not None and country.name == name)
                or (country.common_name is not None and country.common_name == name)
                or (country.official_name is not None and country.official_name == name)
            ):
                return country
        return None

    @staticmethod
    def is_valid_code(code: str) -> bool:
        from simpleiso3166.generated.mapping import ALPHA2_CODE_TO_COUNTRIES  # noqa: PLC0415
        from simpleiso3166.generated.mapping import ALPHA3_CODE_TO_COUNTRIES  # noqa: PLC0415

        return code in ALPHA2_CODE_TO_COUNTRIES or code in ALPHA3_CODE_TO_COUNTRIES

    @staticmethod
    def from_partial_name(
        country_name: str,
        *,
        ratio: float | int = 75.0,
        limit: int = 5,
    ) -> Generator[Country, None, None]:
        """
        Attempts to locate a country by partial name, using fuzzy matching techniques.
        Returns countries in order of match quality (most similar first).

        The improved version:
        - Uses multiple fuzzy matching algorithms for more accurate results
        - Pre-processes input to handle common variations (abbreviations, "the", etc.)
        - Properly handles aliases with weighted scoring
        - Caches processed names for better performance
        - Normalizes text (lowercase, removes extra spaces, diacritics)
        - Implements special case handling for common problematic country names
        - Expanded aliases database for common country name variations
        - Direct mapping for exact matches to improve performance

        Args:
            country_name: The name (or partial name) of the country to find
            ratio: Minimum similarity threshold (0-100) to consider a match
            limit: Maximum number of countries to return (default: 5)

        Returns:
            Generator yielding Country objects in descending order of match quality
        """
        import re  # noqa: PLC0415
        import unicodedata  # noqa: PLC0415

        from rapidfuzz import fuzz  # noqa: PLC0415
        from rapidfuzz import utils  # noqa: PLC0415

        from simpleiso3166.aliases import COUNTRY_ALIAS_TO_CODE  # noqa: PLC0415
        from simpleiso3166.generated.mapping import ALPHA2_CODE_TO_COUNTRIES  # noqa: PLC0415

        # Empty input handling
        if not country_name or not country_name.strip():
            return

        # Normalize input for exact matching
        normalized_input = country_name.strip().lower()

        # Direct mapping for exact matches (more efficient than regex for simple cases)
        direct_matches: Final[dict[str, CountryCodeAlpha2Type]] = {
            "us": "US",
            "usa": "US",
            "united states": "US",
            "united states of america": "US",
            "america": "US",
            "uk": "GB",
            "britain": "GB",
            "great britain": "GB",
            "united kingdom": "GB",
            "england": "GB",
            "holland": "NL",
            "netherlands": "NL",
            "the netherlands": "NL",
            "russia": "RU",
            "russian federation": "RU",
            "china": "CN",
            "prc": "CN",
            "south korea": "KR",
            "republic of korea": "KR",
            "rok": "KR",
            "north korea": "KP",
            "dprk": "KP",
            "uae": "AE",
            "united arab emirates": "AE",
            "iran": "IR",
            "persia": "IR",
            "japan": "JP",
            "nippon": "JP",
            "vietnam": "VN",
            "viet nam": "VN",  # codespell:ignore nam
            "laos": "LA",
            "myanmar": "MM",
            "burma": "MM",
            "czech republic": "CZ",
            "czechia": "CZ",
            "australia": "AU",
            "down under": "AU",
            "new zealand": "NZ",
            "aotearoa": "NZ",
        }

        # Special case handling using regex for more complex patterns
        regex_patterns: Final[dict[re.Pattern, CountryCodeAlpha2Type]] = {
            re.compile(r"\b(u\.s\.a?|united\s+states)(?:\s+of\s+america)?\b", re.IGNORECASE): "US",  # type: ignore[misc]
            re.compile(
                r"\b(u\.k\.?|united\s+kingdom)(?:\s+of\s+great\s+britain(?:\s+and\s+northern\s+ireland)?)?\b",
                re.IGNORECASE,
            ): "GB",  # type: ignore[misc]
            re.compile(r"\bpeople\'?s\s+republic\s+of\s+china\b", re.IGNORECASE): "CN",  # type: ignore[misc]
            re.compile(r"\bdemocratic\s+people\'?s\s+republic\s+of\s+korea\b", re.IGNORECASE): "KP",  # type: ignore[misc]
            re.compile(r"\bunited\s+republic\s+of\s+tanzania\b", re.IGNORECASE): "TZ",  # type: ignore[misc]
            re.compile(r"\bsaudi\s+arabia\b", re.IGNORECASE): "SA",  # type: ignore[misc]
            re.compile(r"\b(?:islamic\s+republic\s+of\s+)?iran\b", re.IGNORECASE): "IR",  # type: ignore[misc]
            re.compile(r"\b(?:republic\s+of\s+)?south\s+africa\b", re.IGNORECASE): "ZA",  # type: ignore[misc]
            re.compile(r"\bdemocratic\s+republic\s+of\s+(?:the\s+)?congo\b", re.IGNORECASE): "CD",  # type: ignore[misc]
            re.compile(r"\b(?:federated\s+states\s+of\s+)?micronesia\b", re.IGNORECASE): "FM",  # type: ignore[misc]
            re.compile(r"\b(?:kingdom\s+of\s+)?eswatini\b", re.IGNORECASE): "SZ",  # type: ignore[misc]
            re.compile(r"\b(?:republic\s+of\s+)?côte\s+d\'ivoire\b", re.IGNORECASE): "CI",  # type: ignore[misc]
        }

        def normalize_text(text: str) -> str:
            """Normalize text for better matching: lowercase, remove diacritics, extra spaces"""
            if not text:
                return ""
            # Convert to lowercase and remove diacritics
            text = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode("ascii")
            # Replace multiple spaces with a single space and trim
            return re.sub(r"\s+", " ", text).strip()

        def preprocess_country_name(text: str) -> str:
            """Apply specialized preprocessing for country names"""
            processed = normalize_text(text)
            # Remove common prefixes like "the" and "republic of"
            processed = re.sub(r"^the\s+", "", processed)
            processed = re.sub(r"^republic\s+of\s+", "", processed)
            processed = re.sub(r"^democratic\s+republic\s+of\s+", "", processed)
            processed = re.sub(r"^people\'?s\s+republic\s+of\s+", "", processed)
            processed = re.sub(r"^kingdom\s+of\s+", "", processed)
            processed = re.sub(r"^state\s+of\s+", "", processed)
            processed = re.sub(r"^federal\s+republic\s+of\s+", "", processed)
            processed = re.sub(r"^federation\s+of\s+", "", processed)
            return processed

        # Try direct mapping first (fastest)
        if normalized_input in direct_matches:
            yield ALPHA2_CODE_TO_COUNTRIES[direct_matches[normalized_input]]
            return

        # Then check for special cases with regex
        for pattern, code in regex_patterns.items():  # type: ignore[misc]
            if pattern.search(country_name):  # type: ignore[misc]
                yield ALPHA2_CODE_TO_COUNTRIES[code]
                return

        # Check direct match with our expanded aliases dictionary
        for alias, code in COUNTRY_ALIAS_TO_CODE.items():
            if normalized_input == alias.lower():
                yield ALPHA2_CODE_TO_COUNTRIES[code]
                return

        norm = normalize_text(country_name)
        if norm == "korea":
            # Always return South Korea then North Korea
            yield ALPHA2_CODE_TO_COUNTRIES["KR"]
            yield ALPHA2_CODE_TO_COUNTRIES["KP"]
            return
        elif norm == "congo":
            # Always return DR Congo then Republic of the Congo
            yield ALPHA2_CODE_TO_COUNTRIES["CD"]
            yield ALPHA2_CODE_TO_COUNTRIES["CG"]
            return

        # Preprocess the input name
        processed_name = preprocess_country_name(country_name)
        processed_input = utils.default_process(processed_name)

        # Cache for preprocessed country names to avoid redundant processing
        name_cache = {}

        def get_processed_name(text: str) -> str:
            if text not in name_cache:
                name_cache[text] = utils.default_process(text)
            return name_cache[text]

        # Collect results with weighted scoring from multiple algorithms
        results: dict[CountryCodeAlpha2Type, float] = {}

        # Process official names with higher weight
        for country_code, country in ALPHA2_CODE_TO_COUNTRIES.items():
            best_score = 0

            # Check official name and common name with higher weight (1.0)
            for name_field in [country.name, country.common_name]:
                if name_field:
                    # Use multiple similarity metrics for better matching
                    processed_field = get_processed_name(name_field)

                    # Weighted combination of different fuzzy matching algorithms
                    token_score = fuzz.token_set_ratio(processed_input, processed_field)
                    partial_score = fuzz.partial_ratio(processed_input, processed_field)
                    # WRatio includes several matching strategies
                    wratio_score = fuzz.WRatio(processed_input, processed_field)

                    # Combined score with weights
                    combined_score = (token_score * 0.5) + (partial_score * 0.2) + (wratio_score * 0.3)

                    best_score = max(best_score, combined_score)  # type: ignore[assignment]

            if best_score >= ratio:
                results[country_code] = best_score

        # Process aliases with slightly lower weight (0.9) to prioritize official names
        for alias, code in COUNTRY_ALIAS_TO_CODE.items():
            processed_alias = get_processed_name(alias)

            # Weighted combination for aliases
            token_score = fuzz.token_set_ratio(processed_input, processed_alias)
            partial_score = fuzz.partial_ratio(processed_input, processed_alias)
            wratio_score = fuzz.WRatio(processed_input, processed_alias)

            # Combined score with weights, multiplied by alias factor
            combined_score = ((token_score * 0.5) + (partial_score * 0.2) + (wratio_score * 0.3)) * 0.9

            if combined_score >= ratio:
                # Keep the highest score if this country already has a score
                if code in results:
                    results[code] = max(results[code], combined_score)
                else:
                    results[code] = combined_score

        # Sort by score and yield results, limiting to the specified number
        count = 0
        for code, _ in sorted(results.items(), key=lambda x: x[1], reverse=True):  # type: ignore[misc]
            yield ALPHA2_CODE_TO_COUNTRIES[code]
            count += 1  # noqa: SIM113
            if count >= limit:
                break


@dataclass(**DATACLASS_BASE_AGS)
class Subdivision:
    code: str
    name: str
    type_: SubdivisionTypeType

    @property
    def country(self) -> CountryCodeAlpha2Type:
        code = self.code.split("-")[0]
        return cast("CountryCodeAlpha2Type", code)

    @staticmethod
    def search_by_name(
        subdivision_name: str,
        *,
        ratio: float | int | None = 80.0,
        limit: int = 10,
    ) -> Generator[Subdivision, None, None]:
        from rapidfuzz import fuzz  # noqa: PLC0415
        from rapidfuzz import process  # noqa: PLC0415
        from rapidfuzz.utils import default_process  # noqa: PLC0415

        from simpleiso3166.generated.mapping import ALPHA2_CODE_TO_COUNTRIES  # noqa: PLC0415

        def _all_subdivisions() -> Generator[Subdivision, None, None]:
            for country in ALPHA2_CODE_TO_COUNTRIES.values():
                yield from country.subdivisions

        processed_name = default_process(subdivision_name)

        sent = 0
        for _, _, result in process.extract(
            processed_name,
            {x: default_process(x.name) for x in _all_subdivisions()},
            scorer=fuzz.WRatio,
            score_cutoff=ratio,
            limit=None,
        ):
            yield result
            sent += 1  # noqa: SIM113
            if sent >= limit:
                return
