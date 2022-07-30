# Copyright 2021-2022 Steven Kearnes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utility functions for working in Jupyter/Colab notebooks."""
import pandas as pd
import scipy.stats


def assign_ranks(scores: dict[str, float]) -> pd.DataFrame:
    """Assigns ranks to per-object scores."""
    rows = []
    for key, value in scores.items():
        rows.append({'key': key, 'score': value})
    df = pd.DataFrame(rows)
    df['rank'] = scipy.stats.rankdata(-1 * df.score.values, method='min')
    return df.sort_values(['rank', 'key'], ignore_index=True)
