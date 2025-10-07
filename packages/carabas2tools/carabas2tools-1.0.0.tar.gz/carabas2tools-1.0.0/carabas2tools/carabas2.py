import os
import pandas as pd
import numpy as np
from scipy.signal import fftconvolve
from .mission_info import MISSION_INFO
from .image_info import IMAGE_INFO


class Carabas2:
    """
    Main interface for the CARABAS-II dataset tools.
    """

    def __init__(self, data_path: str):
        self.data_path = os.path.abspath(data_path)
        self.target_lists_dir = os.path.join(self.data_path, "target_lists")
        self.images_dir = os.path.join(self.data_path, "images")

        if not os.path.isdir(self.target_lists_dir):
            raise FileNotFoundError(
                f"Target lists folder not found in {self.target_lists_dir}"
            )
        if not os.path.isdir(self.images_dir):
            raise FileNotFoundError(f"Images folder not found in {self.images_dir}")

    # === DATASET METADATA ===
    def get_mission_info(self) -> pd.DataFrame:
        """
        Returns mission metadata as a pandas DataFrame.
        Indexed by (mission, pass).
        """
        return MISSION_INFO.copy()

    def get_image_info(self) -> dict:
        """
        Returns image spatial and dimensional metadata.
        """
        return IMAGE_INFO.copy()

    # === GET TARGETS ===
    def get_targets(self, m: int, p: int) -> pd.DataFrame:
        target_file = os.path.join(
            self.target_lists_dir, MISSION_INFO.loc[(m, p), "targets_list"]
        )
        targets = pd.read_csv(target_file, sep="\t", header=None)
        targets.columns = ["n_coord", "e_coord", "target"]
        return targets

    # === READ IMAGE ===
    def read_image(self, m: int, p: int) -> np.ndarray:
        file_path = os.path.join(self.images_dir, MISSION_INFO.loc[(m, p), "filename"])
        return self._VHF_read_image(file_path, 2000, 3000, 1, 2000, 1, 3000)

    def _VHF_read_image(
        self, filename, n_cols, n_rows, col_start, col_end, row_start, row_end
    ):
        NC = col_end - col_start + 1
        NR = row_end - row_start + 1
        out = np.zeros((NC, NR), dtype=np.float32)

        with open(filename, "rb") as fid:
            for jj in range(NR):
                fid.seek((n_cols * (row_start - 1 + jj) + (col_start - 1)) * 4)
                out[:, jj] = np.fromfile(fid, dtype=">f4", count=NC)
        return out.T

    # === MAKE TARGET IMAGE ===
    def make_target_image(self, m: int, p: int, radius: int = 5) -> np.ndarray:
        n_rows = IMAGE_INFO["north_max"] - IMAGE_INFO["north_min"] + 1
        n_cols = IMAGE_INFO["east_max"] - IMAGE_INFO["east_min"] + 1
        targets = self.get_targets(m, p)
        target_image = np.zeros((n_rows, n_cols))

        for _, t in targets.iterrows():
            row = int(IMAGE_INFO["north_max"] - np.round(t["n_coord"]) + 1)
            col = int(np.round(t["e_coord"]) - IMAGE_INFO["east_min"] + 1)
            if 1 <= row <= n_rows and 1 <= col <= n_cols:
                target_image[row, col] = 1

        if radius > 1:
            x, y = np.meshgrid(range(-radius, radius + 1), range(-radius, radius + 1))
            kernel = np.sqrt(x**2 + y**2) <= radius
            target_image = fftconvolve(target_image, kernel, mode="same")

        return target_image
