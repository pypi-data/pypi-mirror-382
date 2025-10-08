import pytest
import numpy as np

import pandas as pd

from asodesigner.consts_dataframe import *
from asodesigner.features.feature_names import SENSE_LENGTH
from asodesigner.populate.populate_sense_accessibility import populate_sense_accessibility, SENSE_AVG_ACCESSIBILITY
from asodesigner.util import get_antisense

FLANK_SIZE = 120
ACCESS_SIZE = 13
SEED_SIZE = 13
SEED_SIZES = [SEED_SIZE * m for m in range(1, 4)]
ACCESS_WIN_SIZE = 80

def get_init_df(target_mrna, aso_sizes=[16, 20], canonical_name='DDX11L1'):
    candidates = []
    sense_starts = []
    sense_lengths = []
    sense_starts_from_end = []

    for aso_size in aso_sizes:
        for i in range(0, len(target_mrna) - (aso_size - 1)):
            target = target_mrna[i: i + aso_size]
            candidates.append(get_antisense(str(target)))
            sense_starts.append(i)
            sense_lengths.append(aso_size)
            sense_starts_from_end.append(i)
    df = pd.DataFrame({SEQUENCE: candidates, SENSE_START: sense_starts, SENSE_LENGTH: sense_lengths,
                       SENSE_START_FROM_END: sense_starts_from_end, CANONICAL_GENE: canonical_name})
    return df


def test_regression(short_mrna, n_compare=10, path="avg_sense_access.txt", use_saved=True):
    df = get_init_df(short_mrna.full_mrna, [16])
    print("Length mRNA: ", len(short_mrna.full_mrna))

    populate_sense_accessibility(df, short_mrna)
    avg_sense_predictions = list(df[SENSE_AVG_ACCESSIBILITY])

    if not use_saved:
        # write predictions so they can serve as regression data
        with open(path, "w") as f:
            for val in avg_sense_predictions:
                f.write(f"{val if val is not None else 'nan'}\n")

            avg_sense_regression = np.array(avg_sense_predictions)
    else:
        avg_sense_regression = np.loadtxt(path)
    # compare
    np.testing.assert_allclose(
        np.array(avg_sense_predictions[:n_compare]),
        np.array(avg_sense_regression[:n_compare])
    )