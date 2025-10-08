from __future__ import annotations

import datetime
import sys
from abc import ABCMeta
from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING
from typing import ClassVar

import orjson
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import RootModel
from pydantic import field_serializer
from pydantic import field_validator

from mnemo_lib.constants import MNEMO_SUPPORTED_VERSIONS
from mnemo_lib.constants import Direction
from mnemo_lib.constants import ShotType
from mnemo_lib.intbuffer import IntegerBuffer
from mnemo_lib.utils import convert_to_Int16BE
from mnemo_lib.utils import split_dmp_into_sections

if TYPE_CHECKING:
    from typing_extensions import Self


class MnemoMixin(metaclass=ABCMeta):
    def to_json(self, filepath: str | Path | None = None) -> str:
        json_str = orjson.dumps(
            self.model_dump(), None, option=(orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS)
        ).decode("utf-8")

        if filepath is not None:
            if not isinstance(filepath, Path):
                filepath = Path(filepath)

            with filepath.open(mode="w") as file:
                file.write(json_str)

        return json_str

    def to_dmp(self, filepath: str | Path | None = None) -> list[int]:
        data = self._to_dmp()

        if filepath is not None:
            if not isinstance(filepath, Path):
                filepath = Path(filepath)

            with filepath.open(mode="w") as file:
                # always finish with a trailing ";"
                file.write(f"{';'.join([str(nbr) for nbr in data])};")

        return data

    @abstractmethod
    def _to_dmp(self) -> list[int]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_dmp(cls, *args, **kwargs) -> Self:
        raise NotImplementedError


class Shot(BaseModel, MnemoMixin):
    type: ShotType
    head_in: float
    head_out: float
    length: float
    depth_in: float
    depth_out: float
    pitch_in: float
    pitch_out: float
    marker_idx: int

    # fileVersion >= 4
    left: int | None = None
    right: float | None = None
    up: float | None = None
    down: float | None = None

    # File Version >= 3
    temperature: float | None = 0

    # File Version >= 3
    hours: int | None = 0
    minutes: int | None = 0
    seconds: int | None = 0

    # Magic Values, version >= 5
    shotStartValueA: ClassVar[int] = 57
    shotStartValueB: ClassVar[int] = 67
    shotStartValueC: ClassVar[int] = 77

    shotEndValueA: ClassVar[int] = 95
    shotEndValueB: ClassVar[int] = 25
    shotEndValueC: ClassVar[int] = 35

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def from_dmp(cls, version: int, buffer: list[int]) -> Self:
        if version not in MNEMO_SUPPORTED_VERSIONS:
            raise ValueError(
                f"Invalid File Format: Expected DMP version: {MNEMO_SUPPORTED_VERSIONS}"
                f", got `{version}`."
            )

        buffer = IntegerBuffer(buffer)

        data = {
            "depth_in": None,
            "depth_out": None,
            "down": None,
            "head_in": None,
            "head_out": None,
            "hours": None,
            "left": None,
            "length": None,
            "marker_idx": None,
            "minutes": None,
            "pitch_in": None,
            "pitch_out": None,
            "right": None,
            "seconds": None,
            "temperature": None,
            "type": None,
            "up": None,
        }

        # =========================== Magic Values ========================== #

        if version >= 5:  # magic values checking
            assert buffer.read() == cls.shotStartValueA
            assert buffer.read() == cls.shotStartValueB
            assert buffer.read() == cls.shotStartValueC

        # =============================== TYPE ============================== #

        data["type"] = ShotType(buffer.read())

        # ============================= Shot Data =========================== #

        data["head_in"] = buffer.readInt16BE() / 10.0
        data["head_out"] = buffer.readInt16BE() / 10.0
        data["length"] = buffer.readInt16BE() / 100.0
        data["depth_in"] = buffer.readInt16BE() / 100.0
        data["depth_out"] = buffer.readInt16BE() / 100.0
        data["pitch_in"] = buffer.readInt16BE() / 10.0
        data["pitch_out"] = buffer.readInt16BE() / 10.0

        # =============================== LRUD ============================== #

        if version >= 4:
            data["left"] = buffer.readInt16BE() / 100.0
            data["right"] = buffer.readInt16BE() / 100.0
            data["up"] = buffer.readInt16BE() / 100.0
            data["down"] = buffer.readInt16BE() / 100.0

        # =============================== Env =============================== #

        if version >= 4:
            data["temperature"] = buffer.readInt16BE() / 10.0
            data["hours"] = buffer.read()
            data["minutes"] = buffer.read()
            data["seconds"] = buffer.read()

        # ============================= Markers ============================= #

        data["marker_idx"] = buffer.read()

        # =========================== Magic Values ========================== #

        if version >= 5:  # magic values checking
            assert buffer.read() == cls.shotEndValueA
            assert buffer.read() == cls.shotEndValueB
            assert buffer.read() == cls.shotEndValueC

        return cls(**data)

    def _to_dmp(self, version: int) -> list[int]:
        if version not in MNEMO_SUPPORTED_VERSIONS:
            raise ValueError(
                f"Invalid File Format: Expected DMP version: {MNEMO_SUPPORTED_VERSIONS}"
                f", got `{version}`."
            )

        data = []

        # Magic Numbers
        if version >= 5:
            data += [self.shotStartValueA, self.shotStartValueB, self.shotStartValueC]

        data += [
            self.type.value,
            *convert_to_Int16BE(self.head_in * 10.0),
            *convert_to_Int16BE(self.head_out * 10.0),
            *convert_to_Int16BE(self.length * 100.0),
            *convert_to_Int16BE(self.depth_in * 100.0),
            *convert_to_Int16BE(self.depth_out * 100.0),
            *convert_to_Int16BE(self.pitch_in * 10.0),
            *convert_to_Int16BE(self.pitch_out * 10.0),
        ]

        if version >= 4:
            data += [
                *convert_to_Int16BE(self.left * 100.0),
                *convert_to_Int16BE(self.right * 100.0),
                *convert_to_Int16BE(self.up * 100.0),
                *convert_to_Int16BE(self.down * 100.0),
            ]

        if version >= 3:
            data += [
                *convert_to_Int16BE(self.temperature * 10.0),
                self.hours,
                self.minutes,
                self.seconds,
            ]

        data += [self.marker_idx]

        if version >= 5:
            data += [self.shotEndValueA, self.shotEndValueB, self.shotEndValueC]

        return data


class Section(BaseModel, MnemoMixin):
    date: datetime.datetime
    direction: Direction
    name: str
    shots: list[Shot]
    version: int

    # Magic Values, version >= 2
    sectionStartValueA: ClassVar[int] = 68
    sectionStartValueB: ClassVar[int] = 89
    sectionStartValueC: ClassVar[int] = 101

    model_config = ConfigDict(extra="forbid")

    @field_validator("date", mode="before")
    @classmethod
    def validate_datetime(cls, value: str | datetime.datetime) -> datetime.datetime:
        if isinstance(value, str):
            try:
                return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M").replace(
                    tzinfo=datetime.UTC
                    if sys.version_info >= (3, 11)
                    else datetime.timezone.utc
                )
            except ValueError as e:
                raise ValueError(
                    f"Invalid datetime format: {value}. Expected 'YYYY-MM-DD HH:MM'."
                ) from e

        elif not isinstance(value, datetime.datetime):
            raise TypeError(f"Unknown data type received: {type(value)=}")

        return value

    @field_serializer("date")
    def serialize_datetime(self, value: datetime.datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M")

    @classmethod
    def from_dmp(cls, buffer: list[int]) -> Self:
        buffer = IntegerBuffer(buffer)

        data = {
            "date": None,
            "direction": None,
            "name": None,
            "shots": [],
            "version": None,
        }

        # ============================= VERSION ============================= #

        data["version"] = buffer.read()

        if data["version"] not in MNEMO_SUPPORTED_VERSIONS:
            raise ValueError(
                f"Invalid File Format: Expected DMP version: {MNEMO_SUPPORTED_VERSIONS}"
                f", got `{data['version']}`."
            )

        if data["version"] > 2:  # magic values checking
            assert buffer.read() == cls.sectionStartValueA
            assert buffer.read() == cls.sectionStartValueB
            assert buffer.read() == cls.sectionStartValueC

        # =============================== DATE ============================== #

        year = buffer.read() + 2000
        if year not in range(2016, 2100):
            raise ValueError(f"Invalid year: `{year}`")

        month = buffer.read()
        if month not in range(1, 13):
            raise ValueError(f"Invalid month: `{month}`")

        day = buffer.read()
        if day not in range(1, 31):
            raise ValueError(f"Invalid day: `{day}`")

        hour = buffer.read()
        if hour not in range(24):
            raise ValueError(f"Invalid hour: `{hour}`")

        minute = buffer.read()
        if hour not in range(60):
            raise ValueError(f"Invalid minute: `{minute}`")

        data["date"] = datetime.datetime(  # noqa: DTZ001
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
        )

        # =============================== NAME ============================== #

        data["name"] = "".join([chr(i) for i in buffer.read(3)])

        # ============================ DIRECTION ============================ #

        data["direction"] = Direction(buffer.read())

        # ============================== SHOTS ============================== #
        match data["version"]:
            case 2:
                shot_buff_len = 16
            case 3:
                shot_buff_len = 21
            case 4:
                shot_buff_len = 29
            case 5:
                shot_buff_len = 35
            case _:
                raise ValueError(
                    f"Unknown value received for MNEMO DMP Version: `{data['version']}`"
                )

        # `while True` loop equivalent with exit bound
        # There will never be more than 9999 shots in one section.
        for _ in range(int(9e5)):
            try:
                data["shots"].append(
                    Shot.from_dmp(
                        version=data["version"],
                        buffer=buffer.read(shot_buff_len),
                    )
                )
            except IndexError:  # noqa: PERF203
                break
        else:
            raise RuntimeError("The loop never finished")

        return cls(**data)

    def _to_dmp(self) -> list[int]:
        # =================== DMP HEADER =================== #
        data = [self.version]

        if self.version > 2:  # magic numbers
            data += [
                self.sectionStartValueA,
                self.sectionStartValueB,
                self.sectionStartValueC,
            ]

        data += [
            self.date.year % 100,  # 2023 -> 23
            self.date.month,
            self.date.day,
            self.date.hour,
            self.date.minute,
            ord(self.name[0]),
            ord(self.name[1]),
            ord(self.name[2]),
            self.direction.value,
        ]
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

        for shot in self.shots:
            data += shot._to_dmp(version=self.version)  # noqa: SLF001

        return data


class DMPFile(RootModel[list[Section]], MnemoMixin):
    @classmethod
    def from_dmp(cls, filepath: Path | str) -> Self:
        if not isinstance(filepath, Path):
            filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError

        with filepath.open(mode="r") as file:
            data = [int(i) for i in file.read().strip().split(";") if i != ""]

        dmpfile = cls([])
        for section_dmp in split_dmp_into_sections(data):
            dmpfile.root.append(Section.from_dmp(section_dmp))

        return dmpfile

    def _to_dmp(self) -> list[int]:
        data = [nbr for section in self.root for nbr in section._to_dmp()]  # noqa: SLF001

        file_version = int(data[0])

        if file_version not in MNEMO_SUPPORTED_VERSIONS:
            raise ValueError(
                f"Invalid File Format: Expected DMP version: {MNEMO_SUPPORTED_VERSIONS}"
                f", got `{file_version}`."
            )

        if file_version > 2:  # version > 2
            # adding `MN2OVER` message at the end
            data += [77, 78, 50, 79, 118, 101, 114]

        return data

    @property
    def sections(self):
        return self.root
