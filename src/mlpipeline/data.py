"""Module data dealing with all data maters"""
import pandas as pd


class Data:

    def __init__(self, *, train, test, target, features):

        if not isinstance(train, pd.DataFrame):
            raise TypeError("Train must be a pd.Dataframe.")

        if not isinstance(test, pd.DataFrame):
            raise TypeError("Test must be a pd.DataFrame.")

        if features not in list(train.columns):
            raise TypeError(f"{features} not found in pd.DataFrames.")

        if target not in list(train.columns) or target not in list(test.columns):
            raise ValueError(f"{target} column not found in pd.DataFrames.")

        self.train_X = train[features]
        self.train_Y = train[target]
        self.test_X = test[features]
        self.test_Y = test[target]