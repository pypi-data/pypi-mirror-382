from simpleiso3166 import Country


class TestCountryBasic:
    def test_get_country_from_known_code(self) -> None:
        country = Country.from_alpha2("US")

        assert country is not None
        assert country.name == "United States"
        assert country.common_name is None
        assert country.official_name == "United States of America"
        assert country.alpha2 == "US"

    def test_get_invalid_code(self) -> None:
        country = Country.from_alpha2("XX")  # type: ignore[arg-type]

        assert country is None

    def test_country_from_name(self) -> None:
        country = Country.from_name("Hashemite Kingdom of Jordan")

        assert country is not None
        assert country.alpha2 == "JO"
        assert country.common_name is None
        assert country.name == "Jordan"
        assert country.official_name == "Hashemite Kingdom of Jordan"

    def test_invalid_country_from_name(self) -> None:
        country = Country.from_name("Jordanian")

        assert country is None

    def test_code_validation(self) -> None:
        assert Country.is_valid_code("US")
        assert not Country.is_valid_code("XX")


class TestCountrySubdivision:
    def test_country_load_subdivisions(self) -> None:
        country = Country.from_alpha2("US")

        assert country is not None

        subdivisions = list(country.subdivisions)

        assert len(subdivisions) == 57

        code_to_name = {x.code: x.name for x in subdivisions}

        assert "US-CA" in code_to_name
        assert code_to_name["US-CA"] == "California"
        assert "US-NY" in code_to_name
        assert code_to_name["US-NY"] == "New York"

    def test_country_contains_subdivision(self) -> None:
        country = Country.from_alpha2("DE")

        assert country is not None
        assert country.contains_subdivision("DE-BW")
        assert country.contains_subdivision("DE-HH")

    def test_get_subdivision_by_code(self) -> None:
        country = Country.from_alpha2("DE")

        assert country is not None
        subdivision = country.get_subdivision("DE-BW")

        assert subdivision is not None
        assert subdivision.code == "DE-BW"
        assert subdivision.name == "Baden-Württemberg"

    def test_get_subdivision_name(self) -> None:
        country = Country.from_alpha2("TD")

        assert country is not None

        subdivision = country.get_subdivision_name("TD-KA")
        assert subdivision is not None
        assert subdivision == "Kanem"

        subdivision = country.get_subdivision_name("TD-XX")
        assert subdivision is None

    def test_double_subdivisions_load(self) -> None:
        for _ in range(2):
            country = Country.from_alpha2("US")

            assert country is not None

            subdivisions = list(country.subdivisions)

            assert len(subdivisions) == 57

            del country
