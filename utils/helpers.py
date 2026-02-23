from datetime import datetime
import plotly.express as px
from scipy.stats import describe
import pandas as pd
import numpy as np
import json
import os
import requests
import pandas as pd
from .constants import DATA_FOLDER_PATH 
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

# --------------------------------------------------------------------------

def load_report_data(series_id, update=False):
    report_path = os.path.join(DATA_FOLDER_PATH, f'{series_id}.csv')

    if os.path.exists(report_path) and not update:
        df =  pd.read_csv(report_path)
    else :
        url = "https://api.stlouisfed.org/fred/series/observations"

        params = {
            "series_id": series_id,
            "api_key": API_KEY,
            "file_type": "json"
        }

        response = requests.get(url, params=params)

        data = response.json()

        df = pd.DataFrame(data['observations'])

        df = df[['date', 'value']]

        df.columns = ['DATE', series_id]

        df = df[df[series_id] != '.']

        df.to_csv(report_path)

    df.set_index('DATE', inplace=True)
    df.index = pd.to_datetime(df.index)

    return df

# --------------------------------------------------------------------------

def ms_to_date(_ms):
    return datetime.fromtimestamp(_ms / 1000).date()

def save_to_csv_file(filename, content):
    with open(filename, "w") as file:
        file.write(content)

# --------------------------------------------------------------------------

def pmi_json_to_csv():
    with open(os.path.join(DATA_FOLDER_PATH, "ism-pmi.json"), "r") as file:
        pmiData = json.load(file)

    pmiOut = 'DATE,ISM(PMI)'

    for item in pmiData:
        pmiOut += f"\n{ms_to_date(item[0])},{item[1]}"

    save_to_csv_file(os.path.join(DATA_FOLDER_PATH, "ISM-PMI.csv"), pmiOut)

# --------------------------------------------------------------------------

def nmi_json_to_csv():
    with open(os.path.join(DATA_FOLDER_PATH, "ism-nmi.json"), "r") as file:
        nmiData = json.load(file)

    nmiOut = 'DATE,ISM(NMI)'

    for item in nmiData:
        nmiOut += f"\n{ms_to_date(item[0])},{item[1]}"

    save_to_csv_file(os.path.join(DATA_FOLDER_PATH, "ISM-NMI.csv"), nmiOut)

# --------------------------------------------------------------------------

def get_frequency_table(data):
#     num_bins = 8

#     bins = np.linspace(data.min(), data.max(), num_bins + 1)
#     bins = np.round(bins * 2) / 2
#     bins = np.unique(bins)

#     # Make sure edges include all data
#     bins[0] = data.min()
#     bins[-1] = data.max()

#     labels = [f"{bins[i]:.2f}% to {bins[i+1]:.2f}%" for i in range(len(bins)-1)]

#     df_bins = pd.cut(data, bins=bins, labels=labels, include_lowest=True)

#     freq = df_bins.value_counts(sort=False)

#     prob = 100 * freq / freq.sum()

#     cum_prob = prob.cumsum()

#     freq_table = pd.DataFrame({
#         "Frequency": freq,
#         "Probability %": prob,
#         "Cumulative Probability %": cum_prob
#     })

#     return freq_table

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    N = 6

    alpha = (data.max() - data.min()) / N

    bins = [data.min() + i * alpha for i in range(N + 1)]

    bin_labels = [f"{round(bins[i], 2)}% to {round(bins[i+1], 2)}%" for i in range(len(bins) - 1)]
    bin_labels[0] = f"Less than {round(bins[1],2)}%"
    bin_labels[-1] = f"Greater than {round(bins[-2], 2)}%"

    # Assign data to bins
    binned = pd.cut(data, bins=bins, labels=bin_labels, include_lowest=True)

    # Calculate frequency, probability, and cumulative probability
    frequency = binned.value_counts().sort_index()
    probability = 100 * frequency / frequency.sum()
    cumulative_probability = probability.cumsum()

    occurrence_frequencies = pd.DataFrame({
        'Frequency': frequency.values,
        'Probability %': probability.values,
        'Cumulative Probability %': cumulative_probability.values
    }, index=bin_labels)

    return occurrence_frequencies

# --------------------------------------------------------------------------

def describe_data(df_col: pd.Series):
    stats = describe(df_col)

    obj = {
        'nobs': str(stats.nobs),
        'Min %': stats.minmax[0],
        'Max %': stats.minmax[1],
        'Mean %': stats.mean,
        'Median %': df_col.median(),
        'Mode %': df_col.mode(dropna=True)[0],
        'Variance': stats.variance,
        'Skewness': stats.skewness,
        'Kurtosis': stats.kurtosis
    }

    df_stats = (
        pd.DataFrame(list(obj.items()), columns=["Metric", "Value"])
        .set_index("Metric")
    )

    return df_stats, stats

# --------------------------------------------------------------------------

def plot_df_chart(
        df,
        chart_title: str = "Chart Title",
        chart_type: str = "line",   # 🔥 new parameter ("line" or "bar")
        yaxis_title: str = "",
        draw=True,
        save_to_html=False,
        save_file_name="plot",
        use_markers=True,
        width=1300,
        height=600,
        show_rangeslider=True,
        fill=False
):
    # 🔥 Choose chart type
    if chart_type == "line":
        fig = px.line(df, markers=use_markers)
    elif chart_type == "bar":
        fig = px.bar(df)
    else:
        raise ValueError("chart_type must be 'line' or 'bar'")

    fig.update_layout(
        title=chart_title,
        template="plotly_dark",
        paper_bgcolor="black",
        plot_bgcolor="black",
        height=height,
        width=width,
        dragmode="zoom",
        font=dict(color="white", size=12),
        legend=dict(
            itemclick="toggle",
            itemdoubleclick="toggleothers",
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            rangeslider=dict(visible=show_rangeslider),  # 🔥 only for line
            # rangeslider=dict(visible=(chart_type == "line")),  # 🔥 only for line
        ),
        yaxis=dict(
            title=yaxis_title,
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            fixedrange=False
        )
    )

    # 🔥 Only update traces for line charts
    if chart_type == "line":
        fig.update_traces(
            mode=f"lines{'+markers' if use_markers else ''}",
            line=dict(width=1),
            fill="tozeroy" if fill else None,   # 👈 fills area to y=0
            hovertemplate="<b>%{fullData.name}</b><br>%{y:.2f}<extra></extra>"
        )
    else:  # bar
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>%{y:.2f}<extra></extra>"
        )

    if save_to_html:
        fig.write_html(f"plots/{save_file_name}.html")

    if draw:
        return fig.show()
    else:
        return fig