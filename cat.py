import time
from flux import FLUX

while True:
    Flux = FLUX(("122.116.80.243", 1901))
    print(Flux.status)
    time.sleep(1)
