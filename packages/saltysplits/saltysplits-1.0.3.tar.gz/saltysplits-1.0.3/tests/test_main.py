import pytest  # noqa: F401
import numpy as np
import lxml.etree as ET
from saltysplits import SaltySplits as ss
from saltysplits.enums import TimeType
    
class TestSaltySplits:
    def test_read_lss(self, livesplit_vicecity):
        tree = ET.parse(livesplit_vicecity)
        element = tree.getroot()
        model_from_tree = ss.from_xml_tree(element)
        model_from_lss = ss.read_lss(livesplit_vicecity)
        assert model_from_tree == model_from_lss
    
    def test_to_df(self, livesplit_vicecity):
        splits = ss.read_lss(livesplit_vicecity)
        splits_df = splits.to_df(
            time_type=TimeType.REAL_TIME,
            allow_partial=True,
            allow_empty=True,
            cumulative=False,
            lss_repr=False
        )
        assert set(splits_df.columns) == set(splits._collect_ids())

    def test_to_df_cumulative(self, livesplit_vicecity):
        splits = ss.read_lss(livesplit_vicecity)
        cumulative_splits = splits.to_df(
            time_type=TimeType.REAL_TIME,
            allow_partial=False,
            cumulative=True,
            lss_repr=False
        )

        isolated_splits = splits.to_df(
            time_type=TimeType.REAL_TIME,
            allow_partial=False,
            cumulative=False,
            lss_repr=False
        )
        
        assert np.array_equal(cumulative_splits.iloc[-1, :].values, isolated_splits.sum().values )



        