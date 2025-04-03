import pandas as pd


for i in range(1, 12):
    df = pd.read_csv(f"../topic_split/topic_{i}.csv")
    val = ""
    for index, issue in df.iterrows():
        issue["issue"] = issue["issue"].replace("\r", " ")
        issue["issue"] = issue["issue"].replace("\t", " ")
        issue["issue"] = issue["issue"].replace("  ", " ")
        val += issue["issue"] + "\n"
        val += "\n=====================================================\n\n"
    with open("../topic_split/topic_" + str(i) + ".txt", "w") as f:
        f.write(val)


    print(f"Processed topic_{i}.csv")