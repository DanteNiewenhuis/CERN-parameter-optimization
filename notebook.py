# %%

import numpy as np


num_variables = 4

x = np.arange(num_variables) + 1
print(f"{x = }")
prop = x[::-1] / np.sum(x)
print(f"{prop = }")
number_of_changes = np.random.choice(x, p=prop)

last_prop = [1, 0, 0, 0]

# %%

steps = np.linspace(prop, last_prop, 100)
# %%

steps[1]