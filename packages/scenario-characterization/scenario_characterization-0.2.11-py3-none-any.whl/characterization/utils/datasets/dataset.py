import math
from abc import ABC, abstractmethod
from typing import Any

from omegaconf import DictConfig
from torch.utils.data import Dataset

from characterization.schemas import Scenario
from characterization.utils.common import SUPPORTED_SCENARIO_TYPES
from characterization.utils.io_utils import get_logger

logger = get_logger(__name__)


class BaseDataset(Dataset, ABC):  # pyright: ignore[reportMissingTypeArgument, reportUntypedBaseClass]
    """Base class for datasets that handle scenario data."""

    def __init__(self, config: DictConfig) -> None:
        """Initializes the BaseDataset with configuration.

        Args:
            config (DictConfig): Configuration for the dataset, including paths, scenario type,
                sharding, batching, and other parameters.

        Raises:
            ValueError: If the scenario type is not supported.
            Exception: If loading scenario information fails.
        """
        super().__init__()

        self.scenario_type = config.scenario_type
        if self.scenario_type not in SUPPORTED_SCENARIO_TYPES:
            error_message = (
                f"Scenario type {self.scenario_type} not supported. Supported types are: {SUPPORTED_SCENARIO_TYPES}"
            )
            raise ValueError(error_message)

        self.scenario_base_path = config.scenario_base_path
        self.scenario_meta_path = config.scenario_meta_path

        self.conflict_points_path = config.conflict_points_path
        self.conflict_points_cfg = config.get("conflict_points", None)

        self.parallel = config.get("parallel", True)
        self.batch_size = config.get("batch_size", 4)
        self.step = config.get("step", 1)
        self.num_scenarios = config.get("num_scenarios", -1)
        self.num_workers = config.get("num_workers", 0)
        self.num_shards = config.get("num_shards", 1)
        self.shard_index = config.get("shard_index", 0)
        self.config = config

        self.data = DictConfig(
            {
                "scenarios": [],
                "scenarios_ids": [],
                "conflict_points": [],
                "metas": [],
            },
        )

    @property
    def name(self) -> str:
        """Returns the name and base path of the dataset.

        Returns:
            str: The name of the dataset class and its base path.
        """
        return f"{self.__class__.__name__} (loaded from: {self.scenario_base_path})"

    def shard(self) -> None:
        """Shards the dataset into smaller parts for distributed or parallel processing.

        This method updates the internal data attributes to only include the shard assigned
        to this instance, based on the number of shards and the shard index.
        """
        if self.num_shards > 1:
            n_per_shard = math.ceil(len(self.data.metas) / self.num_shards)
            shard_start = int(n_per_shard * self.shard_index)
            shard_end = int(n_per_shard * (self.shard_index + 1))

            self.data.metas = self.data.metas[shard_start:shard_end]
            self.data.scenarios = self.data.scenarios[shard_start:shard_end]
            self.data.scenarios_ids = self.data.scenarios_ids[shard_start:shard_end]

        if self.num_scenarios != -1:
            self.data.metas = self.data.metas[: self.num_scenarios]
            self.data.scenarios = self.data.scenarios[: self.num_scenarios]
            self.data.scenarios_ids = self.data.scenarios_ids[: self.num_scenarios]

    def __len__(self) -> int:
        """Returns the number of scenarios in the dataset.

        Returns:
            int: The number of scenarios in the dataset.
        """
        return len(self.data.scenarios)

    @abstractmethod
    def load_data(self) -> None:
        """Loads the dataset and populates the data attribute.

        This method should be implemented by subclasses to load all required data.
        """

    @abstractmethod
    def collate_batch(self, batch_data: dict[str, Any]) -> dict[str, dict[str, Any]]:  # pyright: ignore[reportMissingParameterType]
        """Collates a batch of data into a single dictionary.

        Args:
            batch_data: The batch data to collate.

        Returns:
            dict: The collated batch.
        """

    @abstractmethod
    def load_scenario_information(self, index: int) -> dict[str, dict[str, Any]]:
        """Loads scenario information for a given index.

        Args:
            index (int): The index of the scenario to load.

        Returns:
            dict: The loaded scenario information.
        """

    @abstractmethod
    def transform_scenario_data(
        self,
        scenario_data: dict[str, Any],
        conflict_points_data: dict[str, Any] | None = None,
    ) -> Scenario:
        """Transforms scenario data and conflict points into a model-ready format.

        Args:
            scenario_data (dict): The scenario data to transform.
            conflict_points_data (dict): Conflict points associated with the scenario.

        Returns:
            dict: Transformed scenario data.
        """

    def __getitem__(self, index: int) -> Scenario:
        """Retrieves a single scenario by index.

        Args:
            index (int): Index of the scenario to retrieve.

        Returns:
            Scenario: A Scenario object constructed from the scenario data.

        Raises:
            ValidationError: If the scenario data does not pass schema validation.
        """
        scenario_information = self.load_scenario_information(index)
        scenario = scenario_information.get("scenario", None)
        if scenario is None:
            error_message = f"Scenario information for index {index} is missing or invalid."
            raise ValueError(error_message)

        conflict_points = scenario_information.get("conflict_points", None)
        return self.transform_scenario_data(scenario, conflict_points)
