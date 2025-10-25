from dataclasses import dataclass
from pathlib import Path

from kataloger.data.configuration_data import ConfigurationData


@dataclass(frozen=True)
class KatalogerArguments:
    configuration_path: Path | None
    configuration_data: ConfigurationData
