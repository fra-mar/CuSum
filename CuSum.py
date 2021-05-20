#CuSum analysis of test logbook
#Basic script

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



#Will load data from excel

file = 'LogbookTest.xlsx'
logbook_data = pd.read_excel (file, sheet_name = 'procedures', header = 6,
                               usecols = [0,1,2,3,4,6,7,8,9,10,12,13,15],
                               keep_default_na= False)
logbook_data.fillna(0)      #substitutes nan with zeros

#Set parameters
def parameters(p0, p1, alfa, beta):             #alfa error, beta error
    P = np.log(p1/p0)
    Q = np.log ( (1-p0)/ (1-p1) )
    a = np.log ( (1-beta)/alfa )
    b = np.log ( (1-alfa)/beta )
    h0 = -b / (P+Q)
    h1 = a / (P+Q)
    s = Q/ (P+Q)
    return h0, h1, s



p0, p1 =  0.3, 0.5                      #p0 = acceptable error, p1 = NON acceptable error
alfa, beta = 0.1, 0.1
h0, h1, s = parameters(p0, p1, alfa, beta)

# Main CuSum function
def calculate_S (proc_data):

    sum, proc_data['cusum'] = 0, 0

    for i in range(0, len (proc_data) ) :
        if proc_data.iloc[i,0] ==1:
            sum -= s
        elif proc_data.iloc[i,0] == -1:
            sum += 1-s
        proc_data.iloc[i,1] = sum

    return proc_data

# Selects a procedure to observe and creates a dataframe with it

proc = 'tube'
df_proc = pd.DataFrame ( logbook_data[proc][(logbook_data[proc] == 1) | (logbook_data[proc] == -1)] )
df_proc.reset_index(inplace = True, drop = True) #consecutive procedures, correlative index starting at 0

df_proc_cusum = calculate_S(df_proc)

#plotting
plt.ion()
plt.style.use('seaborn')
fig = plt.figure ('CuSum for assessing performance')
ax = plt.subplot(1,1,1)
ax.axhline (h0, color = 'gray')
ax.text (1,h0-0.5,'h1', fontsize = 8)
ax.axhline (h1, color = 'gray')
ax.text (1,h1+0.5, 'h0', fontsize = 8)

ax.set_title ('CuSum analysis for procedure '+proc)
ax.set_xlabel ('Successive procedures ({})'.format(proc))
ax.set_ylabel ('CuSum for p0={} p1={} alfa error={} and beta={}'.format(p0,p1,alfa,beta))
ax.text(0.95, 0.01, 'GOOD',
        transform = ax.transAxes, verticalalignment = 'bottom', horizontalalignment = 'right',
        color = 'white', fontsize = 20)
ax.text(0.95, 0.95, 'BAD',
        transform = ax.transAxes, verticalalignment = 'top', horizontalalignment = 'right',
        color = 'white', fontsize = 20)
plt.xlim(0,100); plt.ylim(-12,6)

for i in range (0, len(df_proc_cusum)):
    y = df_proc_cusum.cusum[i]
    ax.plot(i, y, ls='-', c = 'b',  mfc = 'b', marker='o', markersize='3')

    if y > h1:
        ax.text (5,-8,"Correction\nneeded!!", color = 'red', fontsize = 30)
    plt.pause(0.5)
#plt.show()



