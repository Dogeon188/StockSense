import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

def test_format(x) -> bool:
    benchmark, model = x.split('-')
    if benchmark in ['stock1', 'stock2', 'crypto'] and model in ["a2c", "dqn_short", "dqn_long"]:
        return True
    else:
        return False

def read_model(models: list):
    results = {}
    for model in models:
        file_path = os.path.join("output", model, "results.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            results[model] = df
        else:
            print(f"The file {file_path} is not exist.")
    return results

def show_plot(dfs):
    plt.figure(figsize=(10, 6))
    for model, df in dfs.items():
        # print(df['date'][0])
        if 'date' in df.columns and 'history' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            plt.plot(df['date'], df['history'], label=model)
        else:
            print(f"{model} doesn't have the required 'date' or 'history' columns.")

    plt.title("Portfolio Comparison Across Models")
    plt.xlabel("date")
    plt.ylabel("Portfolio")
    plt.legend()
    plt.grid()
    plt.show()


def main():
    models = []
    while True:
        err = ""
        try:
            model_list = input("Enter the models you want to compare (ex. stock1-dqn_short), and seperate with space or 'all': \n").split()
            if model_list[0] == "all":
                models = ["stock1-a2c", "stock1-dqn_short", "stock1-dqn_long", "stock2-a2c", "stock2-dqn_short", "stock2-dqn_long"]
                break
            for x in model_list:
                err = x
                assert test_format(x)
                models.append(x)
            break
        except AssertionError:
            print(f"{err} is with wrong format. Try again !")
    res = read_model(models)
    # print(res)
    show_plot(res)

if __name__ == "__main__":
    main()
    