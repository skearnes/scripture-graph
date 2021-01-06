"""Utility functions for working in Jupyter/Colab notebooks."""

from typing import Mapping

import pandas as pd
import scipy.stats


def assign_ranks(scores: Mapping[str, float]) -> pd.DataFrame:
    """Assigns ranks to per-object scores."""
    rows = []
    for key, value in scores.items():
        rows.append({'key': key, 'score': value})
    df = pd.DataFrame(rows)
    df['rank'] = scipy.stats.rankdata(-1 * df.score.values, method='min')
    return df.sort_values(['rank', 'key'], ignore_index=True)
