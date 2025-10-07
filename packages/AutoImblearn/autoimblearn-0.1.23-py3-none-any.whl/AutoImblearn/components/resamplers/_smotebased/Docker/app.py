from AutoImblearn.components.api import BaseTransformerAPI
from imblearn.over_sampling import SMOTE, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler, OneSidedSelection, CondensedNearestNeighbour
from imblearn.combine import SMOTEENN
import numpy as np

import logging


rsps = {
    'rus': RandomUnderSampler(random_state=42),
    'ros': RandomOverSampler(random_state=42),
    'smote': SMOTE(random_state=42),
    # 'mwmote': MWMOTE(random_state=42),

    # 'combined': SMOTEENN(random_state=42, n_jobs=-1),
}

class RunImblearnSamplerAPI(BaseTransformerAPI):

    def get_hyperparameter_search_space(self):
        return {
        }

    def fit(self, args, X_train, y_train, X_test, y_test):
        resampler = rsps[self.params.model]

        params = self.dict_to_namespace()
        params.metric = args.metric


        logging.info("finished parameter setting")

        return

    def transform(self, X):
        return X
