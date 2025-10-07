import pandas as pd

# from ..model_client.base_model_client import BaseDockerModelClient
from AutoImblearn.components.model_client.base_estimator import BaseEstimator
import os


class RunAutoSmote(BaseEstimator):
    def __init__(self):
        super().__init__(
            image_name="autosmote-api",
            container_name="autosmote_container",
            container_port=8080,
            volume_mounts={
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "autosmote"):
                    "/code/AutoImblearn/Docker",
            },  # mount current dir
            dockerfile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "autosmote"),
        )

    @property
    def payload(self):
        return {
            "metric": self.args.metric,
        }


if __name__ == "__main__":

    input_csv = "pima-indians-diabetes-missing.csv "
    label_col = "Status"

    runner = RunAutoSmote()

    print("[✓] Training model...")
    runner.fit(input_csv, y_train=label_col)

    print("[✓] Predicting (generating balanced data)...")
    result_df = runner.predict(input_csv)

    output_csv = input_csv.replace(".csv", "_balanced.csv")
    result_df.to_csv(output_csv, index=False)
    print(f"[✓] Saved balanced output to: {output_csv}")
