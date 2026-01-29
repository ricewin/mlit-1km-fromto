"""Unit tests for app/common/region_builder.py"""

import pandas as pd
import pytest

from common.region_builder import prefcode_to_name


class TestPrefcodeToName:
    """Test prefcode_to_name function"""

    @pytest.mark.unit
    def test_returns_two_dicts(self):
        """Test that function returns two dictionaries"""
        result = prefcode_to_name()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        pref_dict, city_dict = result
        assert isinstance(pref_dict, dict)
        assert isinstance(city_dict, dict)

    @pytest.mark.unit
    def test_pref_dict_structure(self):
        """Test prefecture dictionary has correct structure"""
        pref_dict, _ = prefcode_to_name()
        
        # Check that dictionary is not empty
        assert len(pref_dict) > 0
        
        # Check that all keys are integers (prefcodes)
        for key in pref_dict.keys():
            assert isinstance(key, (int, type(pd.NA)))
        
        # Check that all values are strings (prefnames)
        for value in pref_dict.values():
            assert isinstance(value, (str, type(pd.NA)))

    @pytest.mark.unit
    def test_city_dict_structure(self):
        """Test city dictionary has correct structure"""
        _, city_dict = prefcode_to_name()
        
        # Check that dictionary is not empty
        assert len(city_dict) > 0
        
        # Check that all keys are integers (citycodes)
        for key in city_dict.keys():
            assert isinstance(key, (int, type(pd.NA)))
        
        # Check that all values are strings (citynames)
        for value in city_dict.values():
            assert isinstance(value, (str, type(pd.NA)))

    @pytest.mark.unit
    def test_caching(self):
        """Test that function results are cached"""
        # Call function twice
        result1 = prefcode_to_name()
        result2 = prefcode_to_name()
        
        # Results should be identical (cached)
        assert result1[0] == result2[0]
        assert result1[1] == result2[1]

    @pytest.mark.unit
    def test_more_cities_than_prefectures(self):
        """Test that there are more cities than prefectures"""
        pref_dict, city_dict = prefcode_to_name()
        
        # There should be 47 prefectures in Japan
        # and many more cities
        assert len(city_dict) > len(pref_dict)
