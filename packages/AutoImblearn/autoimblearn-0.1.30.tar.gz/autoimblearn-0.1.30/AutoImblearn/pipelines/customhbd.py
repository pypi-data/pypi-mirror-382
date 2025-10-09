import numpy as np



# from .hybrids.runspe import RunSPE
# from .hybrids.runmesa import RunMESA
from ..components.hybrids import RunAutoSmote
from ..processing.utils import ArgsNamespace


hbds = {
    "autosmote": RunAutoSmote(),
    # "spe": RunSPE(),
    # "mesa": RunMESA(),
}

class CustomHybrid:
    def __init__(self, args: ArgsNamespace, pipe=None):
        self.args = args
        imp, hbd = pipe
        if hbd in hbds.keys():
            self.hbd = hbds[hbd]
            if not hasattr(self.hbd, "data_folder_path"):
                raise Exception("Model {} does not have data_folder_path attribute".format(self.hbd))
            setattr(self.hbd, "data_folder_path", self.args.path)
        else:
            raise Exception("Model {} not defined in model.py".format(hbd))
        self.imp = imp
        self.result = None

    def train(self, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray = None, y_test: np.ndarray = None):
        # Train classifier

        self.hbd.fit(X_train, y_train, X_test, y_test, args=self.args, imp=self.imp)

        # Sample for asynchronize code
        # async def main():
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get('https://api.example.com') as response:
        #             print("Requested!")
        #             return response
        #
        # asyncio.run(main())

        # async def get_responses(n):
        #     async with aiohttp.ClientSession() as session:
        #         responses = await asyncio.gather(session.post(url))
        #         assert all(r.status == 200 for r in responses)
        #         return [await r.text() for r in responses]

    def predict(self, X_test: np.ndarray, y_test: np.ndarray):

        result = self.hbd.predict(X_test, y_test)
        self.result = result
        return result


if __name__ == "__main__":
    class Arguments:
        def __init__(self):
            self.dataset = "nhanes.csv"
            self.metric = "auroc"

            self.device = "cpu"
            self.cuda = "0"

            self.val_ratio=0.1,
            self.test_raito=0.1,
    args = Arguments()

    tmp = CustomHybrid(args, ['median', 'autosmote'])
    tmp.train(None, None)
