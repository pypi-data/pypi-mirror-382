import timeit
from astroforge.coordinates import nutate

# warm start
_ = nutate(60000.0)

def f(n: int) -> None:
    for i in range(n):
        nutate(60000 + i / 86400.0)

eval_time = timeit.timeit(lambda: f(1000), number=1000) / 1000
print(f"nutate() takes {eval_time} sec per call")
