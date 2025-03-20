import pickle
import json
import numpy as np

import warnings
warnings.filterwarnings("ignore")

__model = None


def load_saved_artifacts():
    print("loading saved artifacts...start")

    global __model

    if __model is None:
        with open('./model/random_forest_model (1).pkl', 'rb') as f:
            __model = pickle.load(f)
    print("loading saved artifacts...done")


def getRiskScore(location,sqft,bhk,bath):
    # try:
    #     loc_index = __data_columns.index(location.lower())
    # except:
    #     loc_index = -1

    # x = np.zeros(len(__data_columns))
    # x[0] = sqft
    # x[1] = bath
    # x[2] = bhk
    # if loc_index>=0:
    #     x[loc_index] = 1

    # return round(__model.predict([x])[0], 2)
    pass


if __name__ == '__main__':
    load_saved_artifacts()
    print(getRiskScore('1st Phase JP Nagar',1000, 3, 3))
    print(getRiskScore('1st Phase JP Nagar', 1000, 2, 2))