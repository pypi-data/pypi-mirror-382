import neopdf.parser as parser
import pytest


@pytest.mark.parametrize("pdf_name", ["NNPDF40_nnlo_as_01180", "MSHT20qed_an3lo"])
def test_lhapdf_set(pdf_name):
    lhapdf_set = parser.LhapdfSet(pdf_name)
    assert lhapdf_set.info() is not None
    assert len(lhapdf_set.members()) > 0
