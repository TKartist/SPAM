import matplotlib.pyplot as plt
from auxiliary import read_output
from collections import Counter
import pandas as pd



def plot_issue_frequency():
    data = read_output()
    user_acquisition = [6404, 5608, 5082, 5888, 11483, 8785, 7480, 9647, 7662, 7199,
                    5515, 14892, 9706, 1667, 8143, 9914, 10264, 10874, 11075, 12425, 
                    9995, 9511, 10146, 10856, 10085, 10524, 8186, 7100]
    date_range = pd.date_range(start='2022-10', periods=len(user_acquisition), freq='MS')
    df_2 = pd.DataFrame({"Date": date_range, "User_Acquisition": user_acquisition})
    df_2['Date'] = pd.to_datetime(df_2['Date'], format='%Y-%m')
    df_2['User_Acquisition'] = df_2['User_Acquisition'] / max(user_acquisition) * 30    
    issue_date = [d[-1]["receivedDateTime"][:7] for d in data]
    counter = Counter(issue_date)
    df = pd.DataFrame(list(counter.items()), columns=['Date', 'Frequency'])
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m')
    df = df.sort_values(by='Date')
    df['Moving_Avg'] = df['Frequency'].rolling(window=3, min_periods=1).mean()

    plt.figure(figsize=(15, 8))
    plt.bar(df['Date'], df['Frequency'], color='skyblue', label='Original Frequency', width=20)
    plt.plot(df['Date'], df['Moving_Avg'], marker='o', label='3-Month Moving Average', color='red')
    plt.plot(df_2['Date'], df_2['User_Acquisition'], marker='x', label='Normalized User Acquisition', color='green')
    plt.xlabel("Date (YYYY-MM)")
    plt.ylabel("Frequency")
    plt.title("3-Month Moving Average of Issue Frequencies")
    plt.xticks(rotation=45)
    plt.legend()
    plt.savefig("issue_frequency_analysis.png")

plot_issue_frequency()

