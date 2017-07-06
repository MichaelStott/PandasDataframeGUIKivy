#!/usr/bin/env python
# -*- encoding: utf-8

from __future__ import absolute_import, division, print_function

from kivy.app import App

import datetime
import numpy as np
import pandas as pd
from dfguik import DfguiWidget


def create_dummy_data(size):

    user_ids = np.random.randint(1, 1000000, 10)
    product_ids = np.random.randint(1, 1000000, 100)

    def choice(*values):
        return np.random.choice(values, size)

    random_dates = [
        datetime.date(2016, 1, 1) + datetime.timedelta(days=int(delta))
        for delta in np.random.randint(1, 50, size)
    ]
    return pd.DataFrame.from_items([
        ("Date", random_dates),
        ("UserID", choice(*user_ids)),
        ("ProductID", choice(*product_ids)),
        ("IntColumn", choice(1, 2, 3)),
        ("FloatColumn", choice(np.nan, 1.0, 2.0, 3.0)),
        ("StringColumn", choice("A", "B", "C")),
        ("Gaussian 1", np.random.normal(0, 1, size)),
        ("Gaussian 2", np.random.normal(0, 1, size)),
        ("Uniform", np.random.uniform(0, 1, size)),
        ("Binomial", np.random.binomial(20, 0.1, size)),
        ("Poisson", np.random.poisson(1.0, size)),
    ])

class DataFrameApp(App):
    def build(self):
        df = create_dummy_data(1000)
        return DfguiWidget(df)
    
if __name__ == '__main__':
    DataFrameApp().run()
    
