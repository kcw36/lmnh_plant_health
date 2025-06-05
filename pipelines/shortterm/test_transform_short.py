# pylint: skip-file
"""Test script for the data transformation functions in `transform_short.py`."""
import pytest
import pandas as pd

from transform import (
    clean_phone_nos, validate_datetime_cols,
    validate_numeric_cols, validate_string_cols,
    drop_irrelevant_columns, extract_nested_columns)


def test_extract_nested_columns():
    """Tests that nested dictionaries are properly flattened into individual 
    columns in the DataFrame."""
    df = pd.DataFrame({
        'botanist': [{'name': 'Kenneth Buckridge',
                      'email': 'kenneth.buckridge@lnhm.co.uk',
                      'phone': '763.914.8635 x57724'}],
        'origin_location': [{'city': 'Stammside', 'country': 'Albania'}]
    })

    extracted_df = extract_nested_columns(df)

    assert list(extracted_df.columns) == ['botanist', 'origin_location', 'botanist_name',
                                          'botanist_email', 'botanist_phone', 'origin_city', 'origin_country']


def test_validate_string_cols():
    """Tests that relevant columns are cast to string objects, and none values
    are filled with empty strings."""
    df = pd.DataFrame({
        'origin_city': [None, 'London', 123],
        'origin_country': ['UK', None, 456],
        'botanist_email': ['test@example.com', None, 789],
        'botanist_phone': ['+441234567890', None, 1234]
    })

    cleaned = validate_string_cols(df)

    assert all(isinstance(val, str) for val in cleaned['origin_city'])
    assert cleaned['origin_country'].isnull().sum() == 0
    assert cleaned['botanist_email'].iloc[2] == '789'


def test_validate_numeric_cols():
    """Tests that numeric columns are correctly converted to numbers."""
    df = pd.DataFrame({
        'temperature': [15.5342, 'nan', None],
        'soil_moisture': ['20.12', 'not good', 16.45],
    })

    cleaned = validate_numeric_cols(df)

    assert pd.isna(cleaned['soil_moisture'].iloc[1])
    assert cleaned['temperature'].iloc[0] == 15.53


def test_validate_datetime_cols():
    """Tests that datetime columns are properly parsed as datetime objects."""
    df = pd.DataFrame({
        'last_watered': ['2025-06-04 15:24:03.882000+00:00', 'not date', None],
        'recording_taken': ['2025-06-04 13:51:41+00:00', 'then', '']
    })

    cleaned = validate_datetime_cols(df)
    assert pd.to_datetime(
        '2025-06-04 13:51:41+00:00') == cleaned['recording_taken'].iloc[0]
    assert pd.isna(cleaned['last_watered'].iloc[1])


def test_drop_irrelevant_columns():
    """Test that checks if irrelevant columns are removed, 
    and important ones are kept."""
    df = pd.DataFrame({
        'plant_id': [1],
        'name': ['Venus flytrap'],
        'origin_city': ['Stammside'],
        'origin_country': ['Albania'],
        'temperature': [13.77],
        'last_watered': ['2025-06-04 13:51:41+00:00'],
        'soil_moisture': [92.33],
        'recording_taken': ['2025-06-04 16:10:03.580000+00:00'],
        'botanist': [{'name': 'Bob'}],
        'origin_location': [{'city': 'Preston'}],
        'images': [{'image_url': 'not_a_url'}],
        'scientific_name': ['some_scientific_name'],
        'botanist_name': ['Kenneth Buckridge'],
        'botanist_email': ['kenneth.buckridge@lnhm.co.uk'],
        'botanist_phone': ['+7639148635']
    })

    cleaned = drop_irrelevant_columns(df)

    for column in ['origin_location',
                   'botanist', 'images', 'scientific_name']:
        assert column not in cleaned.columns

    assert 'botanist_name' in cleaned.columns
    assert 'name' in cleaned.columns
    assert 'origin_city' in cleaned.columns


def test_clean_phone_nos_format_uk():
    """Test that checks if a raw phone number is correctly formatted to 
    lead with +44 or +1."""
    df = pd.DataFrame({
        'botanist_phone': ['763.914.8635 x57724', '673.641.8851']
    })

    cleaned = clean_phone_nos(df)

    assert cleaned['botanist_phone'].iloc[0] == '+447639148635'
    assert cleaned['botanist_phone'].iloc[1] == '+446736418851'


def test_clean_phone_nos_format_us():
    """Test that checks if a raw phone number is correctly formatted to 
    lead with +44 or +1."""
    df = pd.DataFrame({
        'botanist_phone': ['1-730-711-3377', '1-288-382-3655']
    })
    cleaned = clean_phone_nos(df)

    assert cleaned['botanist_phone'].iloc[0] == '+17307113377'
    assert cleaned['botanist_phone'].iloc[1] == '+12883823655'
