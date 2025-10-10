# tests/test_synthetics_recursions.py

from seanox_ai_nlp.synthetics import synthetics
from pathlib import Path
import pytest

TESTS_PATH = Path("./tests") if Path("./tests").is_dir() else Path(".")


def normalize_newlines(text):
    return text.replace("\r\n", "\n").replace("\n\r", "\n").replace("\r", "\n")


@pytest.mark.parametrize("template, expected", [
    (
        "synthetics_recursions.yaml",
        """\
TA: TA@term:a!
TB: TB@term:b! TATA@term:a!!
TC: TD@term:d! TC@term:c! TBTB@term:b! TATA@term:a!!! TATA@term:a!!
TD: TD@term:d! TCTD@term:d! TC@term:c! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! TBTB@term:b! TATA@term:a!!! TATA@term:a!!
TE: TE@term:e! TDTD@term:d! TCTD@term:d! TC@term:c! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! TCTD@term:d! TC@term:c! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! TBTB@term:b! TATA@term:a!!! TATA@term:a!!
TF: TF@term:y! TDTD@term:d! TCTD@term:d! TC@term:c! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! TDTD@term:d! TCTD@term:d! TC@term:c! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! TBTB@term:b! TATA@term:a!!! TATA@term:a!!!
TZ: TZ@term:z
DA: DA@data:a!
DB: DB@data:b! TATA@term:a!!
DC: DD@data:d! TCTD@term:d! TC@term:c! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! DBDB@data:b! TATA@term:a!!! TATA@term:a!!
DD: DD@data:d! TCTD@term:d! TC@term:c! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! DBDB@data:b! TATA@term:a!!! TATA@term:a!!
DE: DE@data:e! TDTD@term:d! TCTD@term:d! TC@term:c! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! DCDD@data:d! TCTD@term:d! TC@term:c! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! DBDB@data:b! TATA@term:a!!! TATA@term:a!!! TBTB@term:b! TATA@term:a!!! DADA@data:a!!
DF: DF@term:y! DDDD@data:d! TCTD@term:d! TC@term:c! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! DBDB@data:b! TATA@term:a!!! TATA@term:a!!! DDDD@data:d! TCTD@term:d! TC@term:c! TBTB@term:b! TATA@term:a!!! TATA@term:a!!! DBDB@data:b! TATA@term:a!!! TATA@term:a!!!
DZ: DZ@data:z
        """
    )
])
def test_synthetics_recursions(template, expected):
    result = synthetics(TESTS_PATH, template, {})
    actual = normalize_newlines(result.text).strip()
    expected = normalize_newlines(expected).strip()
    assert actual == expected
