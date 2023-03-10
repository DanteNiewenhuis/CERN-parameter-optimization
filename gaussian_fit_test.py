# %%

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit


res = []

with open("results/test.csv", "r") as wf:
    for r in wf.readlines():
        res.append(float(r))
        # wf.write(f"{r}\n")

res = np.array(res)
print(res)
# %%

res.mean()
res.std()

def Gauss(x, a, b, c):
    return a * np.exp(-(x - b)**2 / (2*c**2))

# def Gauss(x, mu, sigma):
#     return 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-0.5 * ((x-mu)/sigma)**2)

def plot_gauss(x_hist: np.ndarray, y_hist: np.ndarray, parameters):
    x_data = np.linspace(x_hist.min(), x_hist.max(), 100)

    y = [Gauss(x, *parameters) for x in x_data]

    plt.plot(x_data, y)
    plt.scatter(x_hist, y_hist)
    plt.show()

def get_average(data):
    hist, bin_edges = np.histogram(data, bins=10)

    hist = hist / np.sum(hist)

    n = len(hist)
    x_hist=np.zeros((n),dtype=float) 
    for ii in range(n):
        x_hist[ii]=(bin_edges[ii+1]+bin_edges[ii])/2

    x_hist = np.array(x_hist)
    y_hist=np.array(hist)
    base_parameters = [y_hist.max(), x_hist.mean(), x_hist.std()]
    parameters, covariance = curve_fit(Gauss, x_hist, y_hist, p0=base_parameters)

    # plot_gauss(x_hist, y_hist, parameters)

    return parameters[1]
# %%

from tqdm import tqdm
averages = []
gauss_averages = []

for i in tqdm(range(10, len(res))):
    averages.append(res[:i].mean())
    try:
        gauss_averages.append(get_average(res[:i]))
    except:
        print(f"EXCEPT: {i}")
        gauss_averages.append(gauss_averages[-1])
        

# %%

plt.plot(averages, label="mean")
plt.plot(gauss_averages, label="guass")

plt.legend()
plt.show()

# %%

deviations = []

for size in range(5,len(res)-1):
    print(f"{size = }")
    walking_avg = []

    for i in range(len(res)-size):
        walking_avg.append(res[i:i+size].mean())

    deviations.append(np.std(walking_avg))

# %%

plt.plot(deviations)

# %%

size = 999
for i in range(len(res)-size):
    print(i)

# %%

plt.hist(res)