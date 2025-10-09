from typing import List
from .. import LoadingScript
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn import preprocessing


# From: https://github.com/samuel-yeom/fliptest/blob/master/exact-ot/data.py
def generate_lipton(scale=True, num_pts=1000, seed=0):
    """
    Synthetic data used by Lipton et al. in arXiv:1711.07076
    """
    np.random.seed(seed)
    work_exp_m = np.random.poisson(31, size=num_pts) - np.random.normal(
        20, 0.2, size=num_pts
    )
    work_exp_f = np.random.poisson(25, size=num_pts) - np.random.normal(
        20, 0.2, size=num_pts
    )

    np.random.seed(seed + 1)
    hair_len_m = 35 * np.random.beta(2, 7, size=num_pts)
    hair_len_f = 35 * np.random.beta(2, 2, size=num_pts)

    np.random.seed(seed + 2)
    ym = np.random.uniform(size=num_pts) < 1 / (1 + np.exp(25.5 - 2.5 * work_exp_m))
    yf = np.random.uniform(size=num_pts) < 1 / (1 + np.exp(25.5 - 2.5 * work_exp_f))

    if scale:  # scale the input attributes to zero mean and unit variance
        work_exp = np.concatenate((work_exp_m, work_exp_f))
        work_exp = preprocessing.scale(work_exp)
        work_exp_m = work_exp[:num_pts]
        work_exp_f = work_exp[num_pts:]
        hair_len = np.concatenate((hair_len_m, hair_len_f))
        hair_len = preprocessing.scale(hair_len)
        hair_len_m = hair_len[:num_pts]
        hair_len_f = hair_len[num_pts:]

    # combine the input attributes to create the input matrix
    Xm = np.stack((work_exp_m, hair_len_m), axis=1)
    Xf = np.stack((work_exp_f, hair_len_f), axis=1)
    columns = ["work_exp", "hair_len"]

    return Xm, Xf, ym, yf, columns


class Script(LoadingScript):
    def load(self, locations: List[Path]) -> pd.DataFrame:
        # Generate original dataset
        Xm, Xf, ym, yf, columns = generate_lipton()

        # Convert numpy arrays to pandas dataframes
        df_m = pd.DataFrame(Xm, columns=columns)
        df_f = pd.DataFrame(Xf, columns=columns)

        # Add sex information
        df_m["sex"] = "male"
        df_f["sex"] = "female"

        # Add target to dataframes
        df_m["hired"] = ym.astype(int)
        df_f["hired"] = yf.astype(int)

        # Concatenate dataframes into one
        df = pd.concat([df_m, df_f]).reset_index(drop=True)

        return df
