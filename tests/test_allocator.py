from services.data_management import DataManagement


def test_0_instances():
    expected_allocation = {
        "OnDemand": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
        "NoUpFront": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
        "PartialUpFront": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
        "AllUpFront": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
    }
    
    proportions = ['proportion', 0.25, 0.25, 0.25, 0.25]
    
    mock_file = "./mock_data/0_instances.csv"
    
    aux_allocator_test(mock_file, proportions, expected_allocation)


def test_4_instances():
    expected_allocation = {
        "OnDemand": {"c4.large": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]},
        "NoUpFront": {"c4.large": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]},
        "PartialUpFront": {"c4.large": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]},
        "AllUpFront": {"c4.large": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}
    }
    
    proportions = ['proportion', 0.25, 0.25, 0.25, 0.25]
    
    mock_file = "./mock_data/4_instances.csv"
    
    aux_allocator_test(mock_file, proportions, expected_allocation)


def test_max_demand_first_hour():
    expected_allocation = {
        "OnDemand": {"c4.large": [4, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
        "NoUpFront": {"c4.large": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]},
        "PartialUpFront": {"c4.large": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]},
        "AllUpFront": {"c4.large": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]}
    }
    
    proportions = ['proportion', 0.25, 0.25, 0.25, 0.25]
    
    mock_file = "./mock_data/max_demand_first_hour.csv"
    
    aux_allocator_test(mock_file, proportions, expected_allocation)


def test_max_demand_last_hour():
    expected_allocation = {
        "OnDemand": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 0, 0, 4]},
        "NoUpFront": {"c4.large": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]},
        "PartialUpFront": {"c4.large": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]},
        "AllUpFront": {"c4.large": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]}
    }
    
    proportions = ['proportion', 0.25, 0.25, 0.25, 0.25]
    
    mock_file = "./mock_data/max_demand_last_hour.csv"
    
    aux_allocator_test(mock_file, proportions, expected_allocation)

# The tests below, change only the proportions in the same demand
def test_10_ond_20_noup_30_partialup_40_allup():
    expected_allocation = {
        "OnDemand": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 0, 0, 4]},
        "NoUpFront": {"c4.large": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]},
        "PartialUpFront": {"c4.large": [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]},
        "AllUpFront": {"c4.large": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]}
    }
    
    proportions = ['proportion', 0.1, 0.2, 0.3, 0.4]
    
    mock_file = "./mock_data/mock_4.csv"
    
    aux_allocator_test(mock_file, proportions, expected_allocation)


def test_40_ond_30_noup_20_partialup_10_allup():
    expected_allocation = {
        "OnDemand": {"c4.large": [0, 0, 0, 0, 0, 0, 2, 4, 8, 12]},
        "NoUpFront": {"c4.large": [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]},
        "PartialUpFront": {"c4.large": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]},
        "AllUpFront": {"c4.large": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]}
    }
    
    proportions = ['proportion', 0.4, 0.3, 0.2, 0.1]
    
    mock_file = "./mock_data/mock_4.csv"
    
    aux_allocator_test(mock_file, proportions, expected_allocation)


def test_25_ond_25_noup_25_partialup_25_allup():
    expected_allocation = {
        "OnDemand": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 1, 5, 9]},
        "NoUpFront": {"c4.large": [6, 6, 6, 6, 6, 6, 6, 6, 6, 6]},
        "PartialUpFront": {"c4.large": [6, 6, 6, 6, 6, 6, 6, 6, 6, 6]},
        "AllUpFront": {"c4.large": [6, 6, 6, 6, 6, 6, 6, 6, 6, 6]}
    }
    
    proportions = ['proportion', 0.25, 0.25, 0.25, 0.25]
    
    mock_file = "./mock_data/mock_4.csv"
    
    aux_allocator_test(mock_file, proportions, expected_allocation)


def test_0_ond_40_noup_30_partialup_30_allup():
    expected_allocation = {
        "OnDemand": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]},
        "NoUpFront": {"c4.large": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]},
        "PartialUpFront": {"c4.large": [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]},
        "AllUpFront": {"c4.large": [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]}
    }
    
    proportions = ['proportion', 0, 0.4, 0.3, 0.3]
    
    mock_file = "./mock_data/mock_4.csv"
    
    aux_allocator_test(mock_file, proportions, expected_allocation)


def test_30_ond_0_noup_40_partialup_30_allup():
    expected_allocation = {
        "OnDemand": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 1, 5, 9]},
        "NoUpFront": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
        "PartialUpFront": {"c4.large": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]},
        "AllUpFront": {"c4.large": [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]}
    }
    
    proportions = ['proportion', 0.3, 0, 0.4, 0.3]
    
    mock_file = "./mock_data/mock_4.csv"
    
    aux_allocator_test(mock_file, proportions, expected_allocation)


def test_30_ond_40_noup_0_partialup_30_allup():
    expected_allocation = {
        "OnDemand": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 1, 5, 9]},
        "NoUpFront": {"c4.large": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]},
        "PartialUpFront": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
        "AllUpFront": {"c4.large": [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]}
    }
    
    proportions = ['proportion', 0.3, 0.4, 0, 0.3]
    
    mock_file = "./mock_data/mock_4.csv"
    
    aux_allocator_test(mock_file, proportions, expected_allocation)


def test_20_ond_50_noup_30_partialup_0_allup():
    expected_allocation = {
        "OnDemand": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 0, 2, 6]},
        "NoUpFront": {"c4.large": [13, 13, 13, 13, 13, 13, 13, 13, 13, 13]},
        "PartialUpFront": {"c4.large": [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]},
        "AllUpFront": {"c4.large": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
    }
    
    proportions = ['proportion', 0.2, 0.5, 0.3, 0]
    
    mock_file = "./mock_data/mock_4.csv"
    
    aux_allocator_test(mock_file, proportions, expected_allocation)


def aux_allocator_test(mock_file, proportions, expected_allocation):
    datam = DataManagement()
    demand = datam.read_demand(mock_file)
    ond_data, nop_data, pup_data, allup_data, _ = datam.allocate_demand(demand, proportions)

    assert expected_allocation['OnDemand'] == ond_data
    assert expected_allocation['NoUpFront'] == nop_data
    assert expected_allocation['PartialUpFront'] == pup_data
    assert expected_allocation['AllUpFront'] == allup_data