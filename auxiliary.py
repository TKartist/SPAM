import ast
import pandas as pd


def read_output():
    with open("output.txt", "r") as f:
        stringData = f.readlines()
        data = [ast.literal_eval(line.strip()) for line in stringData]
    return data
