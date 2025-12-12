from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


def now_ts() -> str:
    return datetime.now().isoformat()


@dataclass
class VehicleRecord:
    vehicle_id: str
    brand: str
    model: str
    plate: str
    entry_date: str
    exit_date: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "VehicleRecord":
        return cls(**data)


@dataclass
class DealerTransaction:
    transaction_id: str
    dealer_name: str
    description: str
    amount: float
    direction: str
    date: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DealerTransaction":
        return cls(**data)


@dataclass
class WageRecord:
    record_id: str
    staff_name: str
    week_ending: str
    amount: float
    notes: str
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "WageRecord":
        return cls(**data)


@dataclass
class IncomeExpenseEntry:
    entry_id: str
    category: str
    description: str
    amount: float
    kind: str
    date: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "IncomeExpenseEntry":
        return cls(**data)


@dataclass
class StockItem:
    name: str
    unit: str
    quantity: float
    last_updated: str
    notes: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "StockItem":
        return cls(**data)
