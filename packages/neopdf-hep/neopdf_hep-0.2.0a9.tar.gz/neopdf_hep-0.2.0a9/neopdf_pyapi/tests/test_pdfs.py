import pytest
import numpy as np

from itertools import product
from neopdf.pdf import ForcePositive


@pytest.mark.parametrize("pdfname", ["NNPDF40_nnlo_as_01180", "MSHT20qed_an3lo"])
class TestPDF:
    def test_mkpdfs(self, neo_pdfs, pdfname):
        pdfs = neo_pdfs(pdfname)
        assert len(pdfs) > 0

    def test_pdf_methods(self, neo_pdf, pdfname):
        neopdf = neo_pdf(pdfname)
        assert len(neopdf.pids()) > 0
        assert len(neopdf.subgrids()) > 0
        assert neopdf.x_min() > 0
        assert neopdf.x_max() > 0
        assert neopdf.q2_min() > 0
        assert neopdf.q2_max() > 0


class TestPDFInterpolations:
    @pytest.mark.parametrize(
        "pdfname",
        [
            "NNPDF40_nnlo_as_01180",
            "MSHT20qed_an3lo",
            "CT18NNLO_as_0118",
            "NNPDFpol20_nnlo_as_01180",
            "nNNPDF30_nlo_as_0118_A56_Z26",
        ],
    )
    @pytest.mark.parametrize("pid", [nf for nf in range(-5, 6) if nf != 0])
    def test_xfxq2(self, neo_pdf, lha_pdf, xq2_points, pdfname, pid):
        neopdf = neo_pdf(pdfname)
        lhapdf = lha_pdf(pdfname)

        params_range = {
            "xmin": lhapdf.xMin,
            "xmax": lhapdf.xMax,
            "q2min": lhapdf.q2Min,
            "q2max": lhapdf.q2Max,
        }
        xs, q2s = xq2_points(**params_range)

        for x, q2 in product(xs, q2s):
            ref = lhapdf.xfxQ2(pid, x, q2)
            res = neopdf.xfxQ2(pid, x, q2)
            np.testing.assert_equal(res, ref)

    @pytest.mark.parametrize("pdfname", ["NNPDF40_nnlo_as_01180", "MSHT20qed_an3lo"])
    @pytest.mark.parametrize("pid", [21])
    def test_xfxq2s(self, neo_pdf, lha_pdf, xq2_points, pdfname, pid):
        neopdf = neo_pdf(pdfname)
        lhapdf = lha_pdf(pdfname)

        params_range = {
            "xmin": lhapdf.xMin,
            "xmax": lhapdf.xMax,
            "q2min": lhapdf.q2Min,
            "q2max": lhapdf.q2Max,
        }
        xs, q2s = xq2_points(**params_range)

        res = neopdf.xfxQ2s([pid], xs, q2s)
        ref = [lhapdf.xfxQ2(pid, x, q2) for x, q2 in product(xs, q2s)]
        np.testing.assert_equal(res, [ref])


class TestAlphaSInterpolations:
    @pytest.mark.parametrize("pdfname", ["NNPDF40_nnlo_as_01180", "MSHT20qed_an3lo"])
    def test_alphasQ2(self, neo_pdf, lha_pdf, pdfname):
        neopdf = neo_pdf(pdfname)
        lhapdf = lha_pdf(pdfname)
        qs = neopdf.metadata().alphas_q()
        q2_points = [q * q for q in np.linspace(qs[0], qs[-1], num=300)]

        for q2_point in q2_points:
            ref = lhapdf.alphasQ2(q2_point)
            res = neopdf.alphasQ2(q2_point)
            np.testing.assert_equal(res, ref)

    @pytest.mark.parametrize(
        "pdfname",
        ["ABMP16_5_nnlo", "ABMP16als118_5_nnlo", "MSHT20nlo_as_smallrange_nf4"],
    )
    def test_alphasQ2_member(self, neo_pdfs, lha_pdfs, pdfname):
        neopdf = neo_pdfs(pdfname)
        lhapdf = lha_pdfs(pdfname)

        for idx in range(len(neopdf)):
            qs = neopdf[idx].metadata().alphas_q()
            q2_points = [q * q for q in np.linspace(qs[0], qs[-1], num=100)]

            for q2_point in q2_points:
                ref = lhapdf[idx].alphasQ2(q2_point)
                res = neopdf[idx].alphasQ2(q2_point)
                np.testing.assert_equal(res, ref)


class TestLazyLoader:
    @pytest.mark.parametrize("pdfname", ["NNPDF40_nnlo_as_01180.neopdf.lz4"])
    def test_lazy_loader(self, neo_pdfs_lazy, pdfname):
        neopdfs = neo_pdfs_lazy(pdfname)

        for pdf in neopdfs:
            res = pdf.xfxQ2(21, 1e-5, 1e2)
            assert isinstance(res, float)


class TestForcePositive:
    def test_force_positive(self, neo_pdf):
        neopdf = neo_pdf("nNNPDF30_nlo_as_0118_A56_Z26")
        assert neopdf.is_force_positive() == ForcePositive.NoClipping
        neg_interp = neopdf.xfxQ2(21, 0.9, 1e2)
        assert neg_interp < 0.0

        # Clip negative values to zero
        neopdf.set_force_positive(ForcePositive.ClipNegative)
        assert neopdf.is_force_positive() == ForcePositive.ClipNegative
        zero_interp = neopdf.xfxQ2(21, 0.9, 1e2)
        assert zero_interp == 0.0

        # Clip negative values to small positive definite
        neopdf.set_force_positive(ForcePositive.ClipSmall)
        assert neopdf.is_force_positive() == ForcePositive.ClipSmall
        small_interp = neopdf.xfxQ2(21, 0.9, 1e2)
        assert small_interp == 1e-10
