# CuSum analysis of test logbook
# Basic script

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Will load data from excel

file = 'LogbookTest_long_term.xlsx'
logbook_data = pd.read_excel(file, sheet_name='procedures', header=6,
                             usecols=[0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 12, 13, 15],
                             keep_default_na=False)
logbook_data.fillna(0)  # substitutes nan with zeros


# Set parameters
def parameters(p0, p1, alfa, beta):  # alfa error, beta error
    P = np.log(p1 / p0)
    Q = np.log((1 - p0) / (1 - p1))
    a = np.log((1 - beta) / alfa)
    b = np.log((1 - alfa) / beta)
    h0 = -b / (P + Q)
    h1 = a / (P + Q)
    s = Q / (P + Q)
    return h0, h1, s


waypoints = pd.DataFrame(np.array([[0, 0.3, 0.5],
                                   [1, 0.1, 0.2],
                                   [2, 0.07, 0.15],
                                   [3, 0.05, 0.1]]), columns=['wp', 'p0', 'p1', ])
# p0 = acceptable error, p1 = NON acceptable error
alfa, beta = 0.1, 0.1

waypoints['h0'], waypoints['h1'], waypoints['s'] = 0.0, 0.0, 0.0
wp = [(0,0)]

for i in range(0, len(waypoints)):
    waypoints.h0[i] = parameters(waypoints.p0[i], waypoints.p1[i], alfa, beta)[0]
    waypoints.h1[i] = parameters(waypoints.p0[i], waypoints.p1[i], alfa, beta)[1]
    waypoints.s[i] = parameters(waypoints.p0[i], waypoints.p1[i], alfa, beta)[2]


# Main CuSum function
def calculate_S(proc_data):
    sum, proc_data['cusum'], proc_data['stage'], stage = 0, 0, 0, 0

    for i in range(0, len(proc_data)):
        if proc_data.iloc[i, 0] == 1:
            sum -= waypoints.iloc[stage, 5]
        elif proc_data.iloc[i, 0] == -1:
            sum += 1 - waypoints.iloc[stage, 5]
        if stage == 3:
            if sum < 0 or sum > waypoints.iloc[stage, 4]:
                sum = 0
        if stage < 3:
            if sum < waypoints.h0[stage]:
                stage += 1
                sum = 0
                wp.append((stage, i))
        proc_data.iloc[i, 1] = sum
        proc_data.iloc[i, 2] = stage

        print(i, proc_data.iloc[i, 1], proc_data.iloc[i, 2])

    return proc_data


# Selects a procedure to observe and creates a dataframe with it

proc = 'tube'
df_proc = pd.DataFrame(logbook_data[proc][(logbook_data[proc] == 1) | (logbook_data[proc] == -1)])
df_proc.reset_index(inplace=True, drop=True)  # consecutive procedures, correlative index starting at 0

df_proc_cusum = calculate_S(df_proc)

#plotting
plt.ioff()
plt.style.use('seaborn')
fig = plt.figure ('CuSum for assessing performance')
ax = plt.subplot(1,1,1)

'''hlines(y, xmin, xmax, colors=None, linestyles='solid', label='', *, data=None, **kwargs)'''
for l in range(0, len(waypoints)):
    if l < 3:
        ax.hlines(waypoints.h0[l], 1+wp[l][1],wp[l+1][1], ls = ':', color = 'g', alpha = 0.3)
        ax.hlines(waypoints.h1[l], 1 + wp[l][1], wp[l + 1][1], ls=':', color='g', alpha = 0.3)
        ax.axvline(wp[l+1][1], ls = '-', alpha= 0.3)
    elif l== 3:
        ax.hlines ( waypoints.h0[l], wp[l][1], len(df_proc_cusum), ls = ':', color = 'g', alpha=0.3 )
        ax.hlines (waypoints.h1[l], wp[l][1], len(df_proc_cusum), ls=':', color='g', alpha =0.3)

ax.set_xlabel ('Successive training oportunities')
ax.set_ylabel ('Cusum in different stages with different acceptable/non acceptable errors')
ax.set_title ('CuSum analysis for procedure '+proc)

plt.ylim(-6,6)

ax.plot(df_proc_cusum.cusum, ls='-', c = 'b' , marker='o', markersize='3')


    #plt.pause(0.5)
plt.show()

