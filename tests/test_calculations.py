import subprocess
import os
from pathlib import Path
import pytest

ROOT_DIRECTORY = Path('.').resolve()
PYTHON = f'{ROOT_DIRECTORY}/.venv/bin/python3'
COSTPLANNER_CLI = f'{ROOT_DIRECTORY}/costplanner_cli.py'
PRICES_PATH = f'{ROOT_DIRECTORY}/data/prices.csv'

def sum_output(filepath):
    with open(filepath, encoding="utf-8", mode='r') as file:
        results = 0
        next(file)  # Skip header
        for line in file:
            total = line.split(',')[-1]
            results += float(total)
        return results

proportions = {
    '100ond': ['1 0 0 0', '8935.2', '20104.2', '329330.4', '12.6'],
    '100allup': ['0 0 0 1', '5255.0', '11825.0', '193794.0', '13905.0'],
    '100partialup': ['0 0 1 0', '5360.6', '12061.3', '197748.8', '7109.1'],
    '100noup': ['0 1 0 0', '5628.3', '12662.6', '207637.2', '17.01'],
    '40ond60part': ['0.4 0 0.6 0', '6790.4', '15278.4', '285389.9056', '4215.0'],
    '20part20all20no40ond': ['0.4 0.2 0.2 0.2', '6816.7', '15351.4', '329330.448', '3897.25']
}

@pytest.mark.parametrize("mode, props", proportions.items())
@pytest.mark.parametrize("mock_number", range(1, 5))
def test_proportions(mock_number, mode, props):
    file = Path(f'{ROOT_DIRECTORY}/tests/mock_data/mock_{mock_number}.csv').resolve()
    print(f'\nTESTING: tests/mock_data/mock_{mock_number}.csv with proportions {mode}')

    filename = f'test{mock_number}-{mode}'
    os.makedirs(f"/tmp/{filename}", exist_ok=True)

    split_proportions = props[0].split()
    run_command = [
        PYTHON,
        COSTPLANNER_CLI,
        file,
        f"/tmp/{filename}",
        '--prices_path', PRICES_PATH,
        '--m', 'classic',
        '--p', 'proportion'
    ] + split_proportions + ['--no_savings_plans', '--summarize']

    run = subprocess.run(run_command, capture_output=True, text=True)
    output = sum_output(f"/tmp/{filename}/{filename}.csv")
    expected = float(props[mock_number])
    threshold = 0.01

    difference = abs(output - expected)
    error = difference / expected

    assert error <= threshold, f'FAILED {float(props[mock_number])} ~= {float(output)} with {error * 100:.4f}% error'

