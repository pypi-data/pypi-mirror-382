from intuned_browser.helpers import filter_empty_values


def test_filter_empty_values_fields():
    input_data = {
        "field1": "value1",
        "field2": "",
        "field3": None,
        "field4": 0,
        "field5": [],
        "field6": {},
        "field7": "value2",
    }
    expected_output = {
        "field1": "value1",
        "field4": 0,
        "field7": "value2",
    }
    filtered_results = filter_empty_values(input_data)
    print(filtered_results)
    assert filtered_results == expected_output


def test_nested_filter_empty_values_fields():
    input_data = {
        "field1": "value1",
        "field2": {
            "subfield1": "",
            "subfield2": None,
            "subfield3": "value3",
        },
        "field3": [],
        "field4": {
            "subfield4": 0,
            "subfield5": {},
        },
    }
    expected_output = {
        "field1": "value1",
        "field2": {
            "subfield3": "value3",
        },
        "field4": {
            "subfield4": 0,
        },
    }
    filtered_results = filter_empty_values(input_data)
    print(filtered_results)
    assert filtered_results == expected_output
