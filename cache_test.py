# %%

import subprocess
import os

# with open('/proc/sys/vm/drop_caches', 'w') as stream:
#     stream.write('1\n')

os.system('sudo sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"')

# os.system("echo Oitn1bitw! | sudo -S echo 3 > /proc/sys/vm/drop_caches")
# os.system(f"echo 3 > /proc/sys/vm/drop_caches")

# %%

print("test")