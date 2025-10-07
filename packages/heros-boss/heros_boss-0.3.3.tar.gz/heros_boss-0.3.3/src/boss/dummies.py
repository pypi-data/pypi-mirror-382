import random


class Dummy:
    def __init__(self):
        self.val = 3
        print("call me maybe")

    def read_temp(self, min: int, max: int) -> float:
        result = random.randint(min, max)
        print(f"returning result {result}")
        print(f"btw, foovar is {self.foovar}")
        return result

    def hello(self) -> str:
        self.testme += 1
        return "world"


class PolledDatasourceDummy(Dummy):
    foovar: str = ""
    testme: int = 0

    def _observable_data(self):
        print("new data got called")
        return self.testme
