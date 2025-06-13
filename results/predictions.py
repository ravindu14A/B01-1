import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.optimize import curve_fit, bisect
import pickle
from scipy.stats import norm
from datetime import datetime
from dateutil.relativedelta import relativedelta

def monte(country, station, N, years_predict, confidence_level, offset, pred_pos, unc_pos):
    ####----Processing----####
    alpha = 1 - confidence_level/100
    confidence = norm.ppf(1 - alpha / 2)
    print(confidence)

    PCA = pd.read_pickle(f"../data/pca/{country}.pkl")
    t_fit = np.arange(50, int(years_predict * 365.25) , 7)
    v = PCA[station]

    data_df = pd.read_pickle(f"../data/processed/{country}/{station}.pkl")
    data_df = data_df.drop(columns=['long'])
    data_df = data_df.rename(columns={'lat': 'pos'})
    # Convert 'date' column to datetime
    data_df['date'] = pd.to_datetime(data_df['date'])

    # Define reference date
    quake_date = pd.to_datetime('2004-11-15')

    # Find the closest date in the column
    data_df['date'] = pd.to_datetime(data_df['date']).dt.normalize()
    quake_date = pd.to_datetime(quake_date).normalize()

    # Get the index of the last date before quake_date
    mask = data_df['date'] < quake_date
    quake_date = data_df.loc[mask].iloc[-1]['date']
    quake_pos = data_df.loc[data_df['date'] == quake_date, 'pos'].values[0]

    data_df["pos"] = data_df["pos"].apply(lambda x: x-quake_pos)

    # Create 'days' column as difference from reference
    data_df['days'] = (data_df['date'] - quake_date).dt.days
    origianl_df = data_df.copy()

    cov_df = pd.read_pickle(f"../data/partially_processed_steps/{country}/filtered_cm_normalised/{station}.pkl")
    cov_df["cov_2D"] = cov_df["covariance matrix"].apply(lambda x: x[:2, :2])

    cov_df["var"] = cov_df["cov_2D"].apply(lambda x: v.T @ x @ v)
    data_df["var"] = cov_df["var"].apply(lambda x: x*10000)


    predictions = []
    coefs = []
    slopes = []

    means = data_df["pos"].values           # shape (n,)
    stds = np.sqrt(data_df["var"].values)   # convert variance to std dev
    n = len(data_df)
    np.random.seed(1)
    samples = np.random.normal(loc=means, scale=stds, size=(N, n))

    for row in samples:
        data_df["pos"] = row
        ###---- Linear Fite before Earthquake ----####
        lin_start_date =pd.to_datetime('2000-12-01')
        lin_end_date = quake_date


        mask = (data_df['date'] >= lin_start_date) & (data_df['date'] <= lin_end_date)
        df_lin = data_df.loc[mask]
        X = df_lin['days'].values.reshape(-1, 1)
        y = df_lin['pos'].values

        model = LinearRegression()
        model.fit(X, y)
        slope_per_day = model.coef_[0] # cm per day
        slope_mm_per_year = slope_per_day * 10 * 365

        t_lin = df_lin["days"]
        y_lin = model.predict(X)

        ####-----Model Fit -----####
        df_fit = data_df.loc[data_df['date'] > lin_end_date]

        t_data = df_fit['days'].values
        y_data = df_fit['pos'].values

        def model_func(t, A, B, c1, c2, d):
            return A * np.exp(-c1 * t) + B * np.exp(-c2 * t) + d + slope_per_day * (t - 365.25* offset)

        inital = [ 2.55295460e+01,  4.01106511e+01,  1.58786793e-02,  3.02663867e-04,
 -4.66967803e+01]
        popt, pcov = curve_fit(model_func, t_data, y_data, maxfev = 10000, p0 = inital)

        #####---- Prediction ----#####
        y_fit = model_func(t_fit, *popt)
        pred_index = np.abs(y_fit).argmin()
        prediction = t_fit[pred_index]

        slopes.append(slope_per_day)
        predictions.append(prediction)
        coefs.append(popt)

    ####-----Preparing Visuals----#####
    def func(t, A, B, c1, c2, d, v):
        return A * np.exp(-c1 * t) + B * np.exp(-c2 * t) + d + v * (t - 365.25* offset)

    predictions = np.array(predictions) /365.25

    mean = np.mean(predictions)
    std = np.std(predictions)
    confidence_interval = std * confidence


    print("Mean:", mean)
    print("Standard Deviation:", std)
    print(f"{confidence_level}% Confidence Interval: +/-", confidence_interval)


    mean_closest_index = np.abs((predictions - mean)).argmin()
    low_closest_index = np.abs((predictions - (mean - confidence_interval))).argmin()

    high_closest_index = np.abs((predictions - (mean + confidence_interval))).argmin()

    mean_fit = func(t_fit, *coefs[mean_closest_index], slopes[mean_closest_index])
    low_fit = func(t_fit, *coefs[low_closest_index],slopes[low_closest_index])
    high_fit = func(t_fit, *coefs[high_closest_index],slopes[high_closest_index])


    # for i in range(N):  # or however many bad results
    #     y_fit = func(t_fit, *coefs[i], slopes[i])
    #     plt.plot(t_fit / 365.25, y_fit, label=f"sample {i}")
    # plt.axhline(0, linestyle='--', color='gray')

    # plt.title("Predictions for quick check")
    # plt.show()


    ####-----Plotting-----#####
    label_date = 2005 + int(mean)

    plt.figure(figsize=(8,6))
    plt.axhline(y=0, color = "black", linestyle = "--")
    plt.plot(origianl_df["days"]/365.25, origianl_df["pos"], color = "green", label = "Original Data")

    plt.plot(t_fit / 365.25, mean_fit, color="blue", label="Mean Prediction")

    plt.fill_between(
        t_fit / 365.25,
        low_fit,
        high_fit,
        color="red",
        alpha=0.3,
        label="95% CI"
    )

    x_err = [[mean - predictions[low_closest_index]], [predictions[high_closest_index]- mean]]

    # Plot the point with horizontal error bar
    plt.errorbar(
        mean, 0,              # x, y
        xerr=x_err,                # asymmetric error bar in x-direction
        fmt='o', color='blue',     # marker style
        ecolor='black', elinewidth=1, capsize=6
    )

    plt.text(
        mean, pred_pos,  # x and y coordinates
        f"Mean Prediction: {label_date}",
        ha='center', va='bottom',
        fontsize=10,
        color='blue',
        bbox=dict(facecolor='white', edgecolor='none', alpha=1, pad=1.5)
    )

    plt.text(
        mean, pred_pos+unc_pos,  # x and y coordinates
        f"Uncertainty: +/- {round(confidence_interval, 1)}",
        ha='center', va='bottom',
        fontsize=8,
        color='black',
        bbox=dict(facecolor='white', edgecolor='none', alpha=1, pad=1)
    )
    plt.title(f"Prediction for {station} | Years from 2004 Earthquake on 2004-12-26")
    plt.xlabel("Years - centered at 2004 Earthquake date")
    plt.ylabel("Pos (cm) - centered at 2004 Earthquake position")
    plt.legend()
    plt.grid()
    plt.show()










