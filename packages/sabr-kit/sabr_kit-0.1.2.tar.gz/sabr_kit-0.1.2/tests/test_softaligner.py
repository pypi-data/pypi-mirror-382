import jax.numpy as jnp
import numpy as np

from sabr import constants, softaligner, types

# import pytest


def make_aligner():
    return softaligner.SoftAligner.__new__(softaligner.SoftAligner)


def test_normalize_orders_indices():
    embed = np.vstack(
        [np.full((1, constants.EMBED_DIM), i, dtype=float) for i in range(3)]
    )
    mp = types.MPNNEmbeddings(
        name="demo",
        embeddings=embed,
        idxs=["3", "1", "2"],
    )
    aligner = make_aligner()

    normalized = aligner.normalize(mp)

    assert normalized.idxs == [1, 2, 3]
    expected = np.vstack([embed[1], embed[2], embed[0]])
    assert np.array_equal(normalized.embeddings, expected)


def test_calc_matches_filters_cdr_residues(monkeypatch):
    monkeypatch.setattr(constants, "ADDITIONAL_GAPS", [])
    aligner = make_aligner()
    aln = jnp.array([[1, 0, 0], [0, 1, 0]], dtype=int)
    res1 = ["a1", "a2"]
    res2 = ["b1", "b2", "b3"]

    matches = aligner.calc_matches(aln, res1, res2)

    assert matches == {"a1": "b1", "a2": "b2"}


def test_correct_gap_numbering_places_expected_ones():
    aligner = make_aligner()
    sub_aln = np.zeros((3, 3), dtype=int)

    corrected = aligner.correct_gap_numbering(sub_aln)

    assert corrected[0, 0] == 1
    assert corrected[-1, -1] == 1
    assert corrected.sum() == min(sub_aln.shape)


def test_fix_aln_expands_to_imgt_width():
    aligner = make_aligner()
    old_aln = np.array([[1, 0, 1], [0, 1, 0]], dtype=int)
    expanded = aligner.fix_aln(old_aln, idxs=["1", "3", "5"])

    assert expanded.shape == (2, 128)
    assert np.array_equal(expanded[:, 0], old_aln[:, 0])
    assert np.array_equal(expanded[:, 2], old_aln[:, 1])
