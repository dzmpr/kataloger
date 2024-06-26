from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from kataloger.data.configuration_data import ConfigurationData


@dataclass(frozen=True)
class KatalogerArguments:
    configuration_path: Optional[Path]
    configuration_data: ConfigurationData
