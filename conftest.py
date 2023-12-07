import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from time import perf_counter
from itertools import cycle

import duckdb
import numpy as np
import pytest


class PerformanceTimer:

    def __init__(self):
        self.measurements = []
        result_dir = Path(os.getenv('PERF_REPORT_DIR') or 'perfreport')
        result_dir.mkdir(parents=True, exist_ok=True)
        self.report_file = result_dir.joinpath(
            f"perfreport-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")


    def record_timings(self, name):
        '''
        Test fixture to run a function repeatedly and recording the result
        '''
        def fixture(test_function, test_function_args=None, number=1, repeat=20):
            if not test_function_args == None:
                args_generator = cycle(test_function_args)
            else:
                args_generator = cycle([[]])

            timings = []
            function_results = []
            for outer in range(repeat):
                for inner in range(number):
                    individual_times = []
                    args = next(args_generator)
                    start_time = perf_counter()
                    res = test_function(*args)
                    end_time = perf_counter()
                    individual_times.append(end_time - start_time)
                    function_results.append(res)
                timings.append(sum(individual_times))
            self.measurements.append((name, timings))
            return function_results

        return fixture

    @staticmethod
    def stats(result):
        (name, timings_list) = result
        timings = np.array(timings_list)

        return dict(zip(
            [
                'test',
                'min',
                'median',
                '90%ile',
                '95%ile',
                'max',
                'timings'],
            [
                name,
                np.min(timings),
                np.median(timings),
                np.percentile(timings, 90),
                np.percentile(timings, 95),
                np.max(timings),
                timings_list,
            ]
        ))

    def write_report(self):
        '''
        Processes the results with the stats static method,
        before saving in a JSON file in the `perfreport` directory.
        '''
        perfreport = [
            self.stats(r)
            for r
            in self.measurements
        ]

        with open(self.report_file, 'w') as f:
            f.write(json.dumps(perfreport, indent=2))


results = PerformanceTimer()


@pytest.fixture
def record_timings(request):
    return results.record_timings(request.node.nodeid)


def pytest_sessionfinish():
    '''
    Hook that runs once the test session has finished.
    '''
    results.write_report()


@pytest.fixture
def sqlite_cursor():
    '''
    Creates a sqlite cursor and yields it to a python test.
    When it returns, closes the cursor and connection.
    '''
    con = sqlite3.connect(os.getenv('SQLITE_DB_PATH'))
    cur = con.cursor()
    yield cur
    cur.close()
    con.close()


@pytest.fixture
def duckdb_cursor():
    '''
    Creates a duckdb cursor and yields it to a python test.
    When it returns, closes the cursor and connection.
    '''
    con = duckdb.connect(os.getenv('DUCKDB_DB_PATH'), read_only=True)
    cur = con.cursor()
    yield cur
    cur.close()
    con.close()
