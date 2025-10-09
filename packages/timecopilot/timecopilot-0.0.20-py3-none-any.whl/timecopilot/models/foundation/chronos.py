from contextlib import contextmanager

import numpy as np
import pandas as pd
import torch
from chronos import BaseChronosPipeline
from tqdm import tqdm

from ..utils.forecaster import Forecaster, QuantileConverter
from .utils import TimeSeriesDataset


class Chronos(Forecaster):
    """
    Chronos models are large pre-trained models for time series forecasting,
    supporting both probabilistic and point forecasts. See the
    [official repo](https://github.com/amazon-science/chronos-forecasting)
    for more details.
    """

    def __init__(
        self,
        repo_id: str = "amazon/chronos-t5-large",
        batch_size: int = 16,
        alias: str = "Chronos",
    ):
        """
        Args:
            repo_id (str, optional): The Hugging Face Hub model ID or local
                path to load the Chronos model from. Examples include
                "amazon/chronos-t5-tiny", "amazon/chronos-t5-large", or a
                local directory. Defaults to "amazon/chronos-t5-large". See
                the full list of available models at
                [Hugging Face](https://huggingface.co/collections/
                amazon/chronos-models-65f1791d630a8d57cb718444)
            batch_size (int, optional): Batch size to use for inference.
                Larger models may require smaller batch sizes due to GPU
                memory constraints. Defaults to 16. For Chronos-Bolt models,
                higher batch sizes (e.g., 256) are possible.
            alias (str, optional): Name to use for the model in output
                DataFrames and logs. Defaults to "Chronos".

        Notes:
            **Academic Reference:**

            - Paper: [Chronos: Learning the Language of Time Series](https://arxiv.org/abs/2403.07815)

            **Resources:**

            - GitHub: [amazon-science/chronos-forecasting](https://github.com/amazon-science/chronos-forecasting)
            - HuggingFace: [amazon/chronos-models](https://huggingface.co/collections/amazon/chronos-models-65f1791d630a8d57cb718444)

            **Technical Details:**

            - The model is loaded onto the best available device (GPU if
              available, otherwise CPU).
            - For best performance with large models (e.g., "chronos-t5-large"),
              a CUDA-compatible GPU is recommended.
            - The model weights are loaded with torch_dtype=torch.bfloat16 for
              efficiency on supported hardware.

        """
        self.repo_id = repo_id
        self.batch_size = batch_size
        self.alias = alias

    @contextmanager
    def _get_model(self) -> BaseChronosPipeline:
        model = BaseChronosPipeline.from_pretrained(
            self.repo_id,
            device_map="auto",
            torch_dtype=torch.bfloat16,
        )
        try:
            yield model
        finally:
            del model
            torch.cuda.empty_cache()

    def _predict(
        self,
        model: BaseChronosPipeline,
        dataset: TimeSeriesDataset,
        h: int,
        quantiles: list[float] | None,
    ) -> tuple[np.ndarray, np.ndarray | None]:
        """handles distinction between predict and predict_quantiles"""
        if quantiles is not None:
            fcsts = [
                model.predict_quantiles(
                    batch,
                    prediction_length=h,
                    quantile_levels=quantiles,
                )
                for batch in tqdm(dataset)
            ]  # list of tuples
            fcsts_quantiles, fcsts_mean = zip(*fcsts, strict=False)
            fcsts_mean_np = torch.cat(fcsts_mean).numpy()
            fcsts_quantiles_np = torch.cat(fcsts_quantiles).numpy()
        else:
            fcsts = [
                model.predict(
                    batch,
                    prediction_length=h,
                )
                for batch in tqdm(dataset)
            ]
            fcsts = torch.cat(fcsts)
            if "t5" in self.repo_id:
                # for t5 models, `predict` returns a tensor of shape
                # (batch_size, num_samples, prediction_length).
                # notice that the method return samples.
                # see https://github.com/amazon-science/chronos-forecasting/blob/6a9c8dadac04eb85befc935043e3e2cce914267f/src/chronos/chronos.py#L450-L537
                # also for these models, the following is how the mean is computed
                # in the `predict_quantiles` method
                # see https://github.com/amazon-science/chronos-forecasting/blob/6a9c8dadac04eb85befc935043e3e2cce914267f/src/chronos/chronos.py#L554
                fcsts_mean = fcsts.mean(dim=1)  # type: ignore
            elif "bolt" in self.repo_id:
                # for bolt models, `predict` returns a tensor of shape
                # (batch_size, num_quantiles, prediction_length)
                # notice that in this case, the method returns the default quantiles
                # instead of samples
                # see https://github.com/amazon-science/chronos-forecasting/blob/6a9c8dadac04eb85befc935043e3e2cce914267f/src/chronos/chronos_bolt.py#L479-L563
                # for these models, the median is prefered as mean forecasts
                # as it can be seen in
                # https://github.com/amazon-science/chronos-forecasting/blob/6a9c8dadac04eb85befc935043e3e2cce914267f/src/chronos/chronos_bolt.py#L615-L616
                fcsts_mean = fcsts[:, model.quantiles.index(0.5), :]  # type: ignore
            fcsts_mean_np = fcsts_mean.numpy()  # type: ignore
            fcsts_quantiles_np = None
        return fcsts_mean_np, fcsts_quantiles_np

    def forecast(
        self,
        df: pd.DataFrame,
        h: int,
        freq: str | None = None,
        level: list[int | float] | None = None,
        quantiles: list[float] | None = None,
    ) -> pd.DataFrame:
        """Generate forecasts for time series data using the model.

        This method produces point forecasts and, optionally, prediction
        intervals or quantile forecasts. The input DataFrame can contain one
        or multiple time series in stacked (long) format.

        Args:
            df (pd.DataFrame):
                DataFrame containing the time series to forecast. It must
                include as columns:

                    - "unique_id": an ID column to distinguish multiple series.
                    - "ds": a time column indicating timestamps or periods.
                    - "y": a target column with the observed values.

            h (int):
                Forecast horizon specifying how many future steps to predict.
            freq (str, optional):
                Frequency of the time series (e.g. "D" for daily, "M" for
                monthly). See [Pandas frequency aliases](https://pandas.pydata.org/
                pandas-docs/stable/user_guide/timeseries.html#offset-aliases) for
                valid values. If not provided, the frequency will be inferred
                from the data.
            level (list[int | float], optional):
                Confidence levels for prediction intervals, expressed as
                percentages (e.g. [80, 95]). If provided, the returned
                DataFrame will include lower and upper interval columns for
                each specified level.
            quantiles (list[float], optional):
                List of quantiles to forecast, expressed as floats between 0
                and 1. Should not be used simultaneously with `level`. When
                provided, the output DataFrame will contain additional columns
                named in the format "model-q-{percentile}", where {percentile}
                = 100 × quantile value.

        Returns:
            pd.DataFrame:
                DataFrame containing forecast results. Includes:

                    - point forecasts for each timestamp and series.
                    - prediction intervals if `level` is specified.
                    - quantile forecasts if `quantiles` is specified.

                For multi-series data, the output retains the same unique
                identifiers as the input DataFrame.
        """
        freq = self._maybe_infer_freq(df, freq)
        qc = QuantileConverter(level=level, quantiles=quantiles)
        dataset = TimeSeriesDataset.from_df(df, batch_size=self.batch_size)
        fcst_df = dataset.make_future_dataframe(h=h, freq=freq)
        with self._get_model() as model:
            fcsts_mean_np, fcsts_quantiles_np = self._predict(
                model,
                dataset,
                h,
                quantiles=qc.quantiles,
            )
        fcst_df[self.alias] = fcsts_mean_np.reshape(-1, 1)
        if qc.quantiles is not None and fcsts_quantiles_np is not None:
            for i, q in enumerate(qc.quantiles):
                fcst_df[f"{self.alias}-q-{int(q * 100)}"] = fcsts_quantiles_np[
                    ..., i
                ].reshape(-1, 1)
            fcst_df = qc.maybe_convert_quantiles_to_level(
                fcst_df,
                models=[self.alias],
            )
        return fcst_df
