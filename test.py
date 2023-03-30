# %%

import numpy as np

import matplotlib.pyplot as plt

# %%

def get_temp_log(c, t):
    return c / np.log(2+t)
# %%

x = np.arange(100)

temps = [get_temp_log(1, t) for t in x]

c =  -.5 
y = [np.exp(c/t) for t in temps]

plt.plot(x, y)
plt.show()
# %%

num_pars = 5
x = np.arange(num_pars) + 1
prop = x[::-1] / np.sum(x)

# %%

num_variables = 5

x = np.arange(num_variables) + 1
print(f"{x = }")
prop = x[::-1] / np.sum(x)
print(f"{prop = }")
number_of_changes = np.random.choice(x, p=prop)

print(f"{number_of_changes = }")

idxs_to_change = np.random.choice(x-1, number_of_changes)

print(f"{idxs_to_change}")
# %%
