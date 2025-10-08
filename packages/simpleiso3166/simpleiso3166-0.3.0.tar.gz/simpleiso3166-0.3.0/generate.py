import json
import sys
from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from io import TextIOWrapper
from itertools import zip_longest
from pathlib import Path
from shutil import rmtree
from typing import Final
from typing import TextIO

import typer  # Import typer
from rich.progress import track

if sys.version_info < (3, 11):
    from typing_extensions import NotRequired
    from typing_extensions import TypedDict

else:
    from typing import NotRequired
    from typing import TypedDict


from httpx import Client

# Constants for ISO 3166 revisions
COUNTRY_REVISION: Final[str] = "d055275324963c9bce5882eaaa93024cf2bf7ed0"
SUBDIVISION_REVISION: Final[str] = "4f5658fa63afce8cd121d41444b28c2294e6b513"

# URLs for ISO 3166 data
ISO_3166_1_JSON_URL = (
    f"https://salsa.debian.org/iso-codes-team/iso-codes/-/raw/main/data/iso_3166-1.json?ref={COUNTRY_REVISION}"
)
ISO_3166_2_JSON_URL = (
    f"https://salsa.debian.org/iso-codes-team/iso-codes/-/raw/main/data/iso_3166-2.json?ref={SUBDIVISION_REVISION}"
)

# Constants for JSON keys
ISO_3166_1_KEY: Final[str] = "3166-1"
ISO_3166_2_KEY: Final[str] = "3166-2"


class Iso3116TypeOneEntry(TypedDict):
    alpha_2: str
    alpha_3: str
    flag: str
    common_name: NotRequired[str]
    official_name: NotRequired[str]
    name: NotRequired[str]
    numeric: NotRequired[str]


class Iso3116TypeTwoEntry(TypedDict):
    code: str
    name: str
    type: str


class CombinedData(TypedDict):
    name: str | None
    common_name: str | None
    official_name: str | None
    alpha_2: str
    alpha_3: str
    subdivisions: list[Iso3116TypeTwoEntry]


def common_header(f: TextIOWrapper) -> None:
    """Writes the common header to a file-like object."""
    f.writelines(
        [
            "# SPDX-FileCopyrightText: 2024-present Trenton H <rda0128ou@mozmail.com>\n",
            "#\n",
            "# SPDX-License-Identifier: MPL-2.0\n",
            "# Generated from:\n",
            f"#  Country Data: {COUNTRY_REVISION}\n",
            f"#  Subdivision Data: {SUBDIVISION_REVISION}\n",
        ],
    )


@contextmanager
def write_file_with_header(file_path: Path) -> Iterator[TextIO]:
    """
    Context manager to open a file for writing, write the common header,
    and yield the file object. Handles closing the file automatically.

    Args:
        file_path: The path to the file to open and write to.

    Yields:
        A file-like object open for writing.

    Raises:
        IOError: If there is an error opening or writing to the file.
    """
    try:
        with file_path.open("w", encoding="utf-8", newline="\n") as f:
            common_header(f)
            yield f
    except OSError as e:
        # Use typer.secho with colors for file writing errors
        typer.secho(f"Error writing to file {file_path}: {e}", fg=typer.colors.RED, bold=True, err=True)
        # Re-raise the exception to halt execution if file writing fails
        raise


def make_literal_from_list(name: str, items: list[str], comments: list[str]) -> list[str]:
    """
    Generates Python code lines for a Literal type from a list of items and comments.

    Args:
        name: The name of the Literal type variable.
        items: A list of strings to be included in the Literal type.
        comments: A list of strings to be included as comments, corresponding to items.

    Returns:
        A list of strings representing the Python code for the Literal definition.
    """
    data = [f"{name} = Literal[\n"]
    for item, comment in zip_longest(items, comments, fillvalue=None):
        if comment:
            data.append(f'    "{item}",  # {comment}\n')
        else:
            data.append(f'    "{item}",\n')
    data.append("]\n\n")
    return data


def get_country_comment_name(country_data: CombinedData) -> str:
    """
    Gets the appropriate name for a country to use in comments, preferring common name.

    Args:
        country_data: A dictionary containing the combined country data.

    Returns:
        The common name, official name, or a default string if neither is available.
    """
    return (
        country_data.get("common_name")
        or country_data.get("name")
        or f"Unknown Country ({country_data.get('alpha_2', 'N/A')})"
    )


def ensure_module_dir(module_dir: Path) -> None:
    """
    Ensures a directory exists by removing it if it does and then creating it.
    Also writes an __init__.py file with the common header to make it a Python package.

    Args:
        module_dir: The path to the directory to ensure exists and initialize as a module.

    Returns:
        None.
    """
    if module_dir.exists():
        rmtree(module_dir)
    module_dir.mkdir(parents=True, exist_ok=True)
    # Use the context manager for the __init__.py file
    with write_file_with_header(module_dir / "__init__.py"):
        # No need to write anything else for an empty __init__.py
        pass


def generate_types_module(module_dir: Path, combined_data: dict[str, CombinedData]) -> None:
    """
    Generates the 'types' Python module (__init__.py) containing Literal types
    for country alpha-2, alpha-3 codes, and subdivision types.

    Args:
        module_dir: The root directory for the generated modules.
        combined_data: A dictionary containing the combined country and subdivision data.

    Returns:
        None.

    Purpose of Data:
        This module defines static types that represent the valid country codes
        and subdivision types based on the downloaded ISO 3166 data. This is used
        for type hinting and potentially runtime validation in the consuming library.
    """
    types_module = module_dir / "types"
    ensure_module_dir(types_module)
    types_file = types_module / "__init__.py"

    with write_file_with_header(types_file) as f:
        f.writelines("from typing import Literal\n\n")

        alpha2_type: list[str] = []
        alpha3_type: list[str] = []
        alphas_comment_strs: list[str] = []
        subdivision_types: set[str] = set()

        for country_code in sorted(combined_data):
            country_data = combined_data[country_code]
            comment_name = get_country_comment_name(country_data)
            alpha2_type.append(country_data["alpha_2"])
            alpha3_type.append(country_data["alpha_3"])
            alphas_comment_strs.append(comment_name)
            for subdivision in country_data["subdivisions"]:
                subdivision_types.add(subdivision["type"])

        f.writelines(
            [
                *make_literal_from_list("CountryCodeAlpha2Type", alpha2_type, alphas_comment_strs),
                *make_literal_from_list("CountryCodeAlpha3Type", alpha3_type, alphas_comment_strs),
                *make_literal_from_list("SubdivisionTypeType", sorted(subdivision_types), []),
            ],
        )


def generate_mapping_module(module_dir: Path, combined_data: dict[str, CombinedData]) -> None:
    """
    Generates the 'mapping' Python module (__init__.py) containing dictionaries
    to map alpha-2 and alpha-3 country codes to their corresponding Country objects.

    Args:
        module_dir: The root directory for the generated modules.
        combined_data: A dictionary containing the combined country and subdivision data.

    Returns:
        None.

    Purpose of Data:
        This module provides lookup structures (dictionaries) that allow
        efficient retrieval of Country objects based on their alpha-2 or alpha-3
        codes. This is the primary way the consuming library will access country data by code.
    """
    mapping_module = module_dir / "mapping"
    ensure_module_dir(mapping_module)
    mapping_file = mapping_module / "__init__.py"

    with write_file_with_header(mapping_file) as f:
        # Imports needed for mapping module
        standard_imports = ["from typing import Final"]
        local_imports = [
            "from simpleiso3166.base import Country",
            "from simpleiso3166.generated.types import CountryCodeAlpha2Type",
            "from simpleiso3166.generated.types import CountryCodeAlpha3Type",
        ]

        # Add imports for each country module
        for country_code in sorted(combined_data.keys()):
            local_imports.append(  # noqa: PERF401
                f"from simpleiso3166.generated.data.{country_code.upper()} import {country_code.upper()}",
            )

        # Sort imports
        standard_imports.sort()
        local_imports.sort()

        # Construct import lines with blank lines between sections
        import_lines: list[str] = [f"{line}\n" for line in standard_imports]
        if standard_imports and local_imports:
            import_lines.append("\n")
        import_lines.extend([f"{line}\n" for line in local_imports])
        import_lines.append("\n")  # Add blank line after imports

        f.writelines(import_lines)

        f.write("ALPHA2_CODE_TO_COUNTRIES: Final[dict[CountryCodeAlpha2Type, Country]] = {\n")
        for country_code in sorted(combined_data):
            comment_name = get_country_comment_name(combined_data[country_code])
            f.write(f'    "{country_code}": {country_code.upper()},  # {comment_name}\n')
        f.write("}\n\n")

        f.write("ALPHA3_CODE_TO_COUNTRIES: Final[dict[CountryCodeAlpha3Type, Country]] = {\n")
        for country_code in sorted(combined_data):
            comment_name = get_country_comment_name(combined_data[country_code])
            country_data = combined_data[country_code]
            f.write(f'    "{country_data["alpha_3"]}": {country_code.upper()},  # {comment_name}\n')
        f.write("}\n")


def generate_country_module(data_module: Path, country_code: str, country_data: CombinedData) -> None:
    """
    Generates a single country-specific Python module (__init__.py) within the 'data' directory.
    Each module contains a constant representing a Country object with its details and subdivisions.

    Args:
        data_module: The root 'data' directory for the generated country modules.
        country_code: The alpha-2 code of the country for which to generate the module.
        country_data: The combined data specifically for this country.

    Returns:
        None.

    Purpose of Data:
        Each country module encapsulates all the detailed information for a specific country,
        including its codes, names, and a list of its subdivisions (if any). This granular
        structure allows for importing and accessing individual country data directly,
        and these objects are used in the 'mapping' module lookups.
    """
    country_module = data_module / f"{country_code.upper()}"
    ensure_module_dir(country_module)
    country_init = country_module / "__init__.py"

    with write_file_with_header(country_init) as f:
        # --- Imports ---
        standard_imports = [
            "from typing import Final",
        ]
        local_imports = [
            "from simpleiso3166.base import Country",
        ]

        subdivision_literal_lines: list[str] = []
        subdivision_class_lines: list[str] = []
        subdivision_data_lines: list[str] = ["[],"]  # Default for subdivisions list in Country constructor

        if country_data["subdivisions"]:
            # Add imports needed only if subdivisions exist
            standard_imports.insert(0, "import dataclasses")
            standard_imports.append("from typing import Literal")
            local_imports.insert(0, "from simpleiso3166.base import DATACLASS_BASE_AGS")
            local_imports.append("from simpleiso3166.base import Subdivision")

            subdivision_data_lines = ["[\n"]  # Start of subdivisions list
            subdivision_literal_lines = make_literal_from_list(
                f"{country_code.upper()}SubdivisionCodeType",
                [subdivision["code"] for subdivision in country_data["subdivisions"]],
                [subdivision["name"] for subdivision in country_data["subdivisions"]],
            )

            # Generate the subclass definition
            subdivision_class_lines = [
                "@dataclasses.dataclass(**DATACLASS_BASE_AGS)\n",  # Apply decorator using imported args
                f"class {country_code.upper()}Subdivision(Subdivision):\n",
                f"    code: {country_code.upper()}SubdivisionCodeType\n\n\n",
            ]

            for subdivision in country_data["subdivisions"]:
                subdivision_data_lines.extend(
                    [
                        f'        {country_code.upper()}Subdivision(code="{subdivision["code"]}",',
                        f' name="{subdivision["name"]}",',
                        f' type_="{subdivision["type"]}"),\n',
                    ],
                )
            subdivision_data_lines.append("    ],")  # End of subdivisions list

        # Construct final import lines with blank lines
        import_lines_output: list[str] = [f"{line}\n" for line in standard_imports]
        if standard_imports and local_imports:
            import_lines_output.append("\n")  # Blank line between standard and local
        import_lines_output.extend([f"{line}\n" for line in local_imports])
        import_lines_output.append("\n")  # Blank line after imports

        # --- Main Content ---
        common_name_str = f'"{country_data["common_name"]}"' if country_data.get("common_name") else "None"
        official_name_str = f'"{country_data["official_name"]}"' if country_data.get("official_name") else "None"
        name_str = f'"{country_data["name"]}"' if country_data.get("name") else "None"

        main_content_lines: list[str] = []

        if subdivision_literal_lines:  # Include Literal type definition if generated
            main_content_lines.extend(subdivision_literal_lines)
            main_content_lines.append("\n")  # Blank line after literal

        if subdivision_class_lines:  # Include subclass definition if generated
            main_content_lines.extend(subdivision_class_lines)
            # Blank line after class definition is already included in subdivision_class_lines

        main_content_lines.extend(
            [
                f"{country_code.upper()}: Final[Country] = Country(\n",
                f'    alpha2="{country_data["alpha_2"]}",\n',
                f'    alpha3="{country_data["alpha_3"]}",\n'
                f"    name={name_str},\n"
                f"    common_name={common_name_str},\n"
                f"    official_name={official_name_str},\n"
                f"    subdivisions=",
            ],
        )
        main_content_lines.extend(subdivision_data_lines)  # Add the subdivisions list data
        main_content_lines.append("\n)\n")  # Close Country constructor

        # Combine imports and main content
        f.writelines(import_lines_output)
        f.writelines(main_content_lines)


def output_data(module_dir: Path, combined_data: dict[str, CombinedData]) -> None:
    """
    Generates the Python modules for the ISO 3166 data within the specified module directory.

    This includes:
    - An __init__.py file for the root generated module.
    - A 'types' module with Literal types for country codes and subdivision types.
    - A 'mapping' module with dictionaries for looking up countries by code.
    - Individual country modules within a 'data' subdirectory, each containing a Country object.

    Args:
        module_dir: The root directory for the generated modules.
        combined_data: The combined country and subdivision data dictionary.

    Returns:
        None.
    """
    ensure_module_dir(module_dir)
    data_module = module_dir / "data"
    ensure_module_dir(data_module)

    generate_types_module(module_dir, combined_data)
    generate_mapping_module(module_dir, combined_data)

    # Generate country-specific modules
    for country_code, country_data in track(
        combined_data.items(),
        description="Generating country modules...",
    ):
        generate_country_module(data_module, country_code, country_data)


def main(
    data_dir: Path = Path(),
    module_dir: Path = Path("src") / "simpleiso3166" / "generated",
    *,
    force_update: bool = False,
) -> None:
    """
    Main function to fetch ISO 3166 country and subdivision data,
    combine it, and generate Python modules based on the data.

    Args:
        data_dir: Directory to store downloaded JSON data. Defaults to the current directory.
        module_dir: Root directory for generated Python modules. Defaults to 'src/simpleiso3166/generated'.
        force_update: Whether to force re-downloading of JSON data even if local files exist.
                      Defaults to False.

    Returns:
        None. Exits the program with a non-zero status code on error.
    """
    country_json = data_dir / "iso_3166-1.json"
    subdivision_json = data_dir / "iso_3166-2.json"

    # Fetch data if needed
    for output_file, url in zip(
        [country_json, subdivision_json],
        [ISO_3166_1_JSON_URL, ISO_3166_2_JSON_URL],
        strict=True,
    ):
        if force_update or not output_file.exists():
            try:
                with Client() as client:
                    response = client.get(url)
                    response.raise_for_status()  # Raise an exception for bad status codes
                    output_file.write_bytes(response.content)
                # Use typer.secho for success message
                typer.secho(f"Downloaded {output_file.name}", fg=typer.colors.GREEN, bold=True)
            except Exception as e:
                # Use typer.secho for download errors
                typer.secho(f"Error downloading {url}: {e}", fg=typer.colors.RED, bold=True, err=True)
                sys.exit(1)  # Exit if data fetching fails

    try:
        subdivision_data: list[Iso3116TypeTwoEntry] = json.loads(
            subdivision_json.read_text(encoding="utf-8"),
        )[ISO_3166_2_KEY]  # type: ignore[misc]
        country_data: list[Iso3116TypeOneEntry] = json.loads(country_json.read_text(encoding="utf-8"))[ISO_3166_1_KEY]  # type: ignore[misc]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        # Use typer.secho for data loading/parsing errors
        typer.secho(f"Error loading or parsing data files: {e}", fg=typer.colors.RED, bold=True, err=True)
        sys.exit(1)  # Exit if data parsing fails
    except Exception as e:
        # Use typer.secho for unexpected loading errors
        typer.secho(f"An unexpected error occurred while loading data: {e}", fg=typer.colors.RED, bold=True, err=True)
        sys.exit(1)

    country_code_to_subdivision: dict[str, list[Iso3116TypeTwoEntry]] = defaultdict(list)

    for subdivision in subdivision_data:
        subdivision_code: str = subdivision["code"]
        country_alpha_2 = subdivision_code.split("-")[0]
        country_code_to_subdivision[country_alpha_2].append(subdivision)

    combined_data: dict[str, CombinedData] = {}

    for country in track(country_data, description="Combining data...            "):
        combined_data[country["alpha_2"]] = {
            "alpha_2": country["alpha_2"],
            "alpha_3": country["alpha_3"],
            "name": country.get("name"),
            "common_name": country.get("common_name"),
            "official_name": country.get("official_name"),
            "subdivisions": country_code_to_subdivision.get(country["alpha_2"], []),
        }

    output_data(module_dir, combined_data)


if __name__ == "__main__":
    typer.run(main)
