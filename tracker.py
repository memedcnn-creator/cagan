import uuid
from collections import defaultdict
from typing import Dict, List, Optional

from models import (
    DealerTransaction,
    IncomeExpenseEntry,
    StockItem,
    VehicleRecord,
    WageRecord,
    now_ts,
)
from storage import load_data, save_data


class WorkshopTracker:
    def __init__(self) -> None:
        self.data, repaired = load_data()
        # Boş veya onarılan veri seti ile başlandıysa dosyayı hemen oluştur.
        if repaired:
            self._persist()

    def _persist(self) -> None:
        save_data(self.data)

    # Araç işlemleri
    def add_vehicle_entry(
        self,
        brand: str,
        model: str,
        plate: str,
        notes: str = "",
    ) -> VehicleRecord:
        vehicle = VehicleRecord(
            vehicle_id=str(uuid.uuid4()),
            brand=brand,
            model=model,
            plate=plate,
            entry_date=now_ts(),
            exit_date=None,
            notes=notes,
        )
        self.data["vehicles"].append(vehicle.to_dict())
        self._persist()
        return vehicle

    def mark_vehicle_exit(self, vehicle_id: str, notes: str = "") -> Optional[VehicleRecord]:
        for raw in self.data["vehicles"]:
            if raw["vehicle_id"] == vehicle_id:
                raw["exit_date"] = now_ts()
                if notes:
                    raw["notes"] = notes
                self._persist()
                return VehicleRecord.from_dict(raw)
        return None

    def list_vehicles(self, only_open: bool = False) -> List[VehicleRecord]:
        vehicles = [VehicleRecord.from_dict(raw) for raw in self.data["vehicles"]]
        if only_open:
            return [v for v in vehicles if v.exit_date is None]
        return vehicles

    # Bayi gelir/borç
    def add_dealer_transaction(
        self, dealer_name: str, description: str, amount: float, direction: str
    ) -> DealerTransaction:
        direction_norm = direction.lower()
        if direction_norm not in {"gelir", "borc"}:
            raise ValueError("direction 'gelir' veya 'borc' olmalı")
        transaction = DealerTransaction(
            transaction_id=str(uuid.uuid4()),
            dealer_name=dealer_name,
            description=description,
            amount=float(amount),
            direction=direction_norm,
            date=now_ts(),
        )
        self.data["dealer_transactions"].append(transaction.to_dict())
        self._persist()
        return transaction

    def dealer_report(self) -> Dict[str, Dict[str, float]]:
        summary: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"gelir": 0.0, "borc": 0.0, "net": 0.0}
        )
        for raw in self.data["dealer_transactions"]:
            dealer = raw["dealer_name"]
            summary[dealer][raw["direction"]] += float(raw["amount"])
        for dealer, row in summary.items():
            row["net"] = row["gelir"] - row["borc"]
        return dict(summary)

    # Haftalık ödemeler
    def add_wage_record(
        self, staff_name: str, week_ending: str, amount: float, notes: str = ""
    ) -> WageRecord:
        record = WageRecord(
            record_id=str(uuid.uuid4()),
            staff_name=staff_name,
            week_ending=week_ending,
            amount=float(amount),
            notes=notes,
            created_at=now_ts(),
        )
        self.data["wages"].append(record.to_dict())
        self._persist()
        return record

    def list_wages(self) -> List[WageRecord]:
        return [WageRecord.from_dict(raw) for raw in self.data["wages"]]

    # Gelir gider
    def add_income_expense(
        self, category: str, description: str, amount: float, kind: str
    ) -> IncomeExpenseEntry:
        kind_norm = kind.lower()
        if kind_norm not in {"gelir", "gider"}:
            raise ValueError("kind 'gelir' veya 'gider' olmalı")
        entry = IncomeExpenseEntry(
            entry_id=str(uuid.uuid4()),
            category=category,
            description=description,
            amount=float(amount),
            kind=kind_norm,
            date=now_ts(),
        )
        self.data["income_expenses"].append(entry.to_dict())
        self._persist()
        return entry

    def income_expense_report(self) -> Dict[str, float]:
        income = sum(
            float(raw["amount"]) for raw in self.data["income_expenses"] if raw["kind"] == "gelir"
        )
        expense = sum(
            float(raw["amount"]) for raw in self.data["income_expenses"] if raw["kind"] == "gider"
        )
        return {"gelir": income, "gider": expense, "net": income - expense}

    def list_income_expenses(self) -> List[IncomeExpenseEntry]:
        return [IncomeExpenseEntry.from_dict(raw) for raw in self.data["income_expenses"]]

    # Stok
    def upsert_stock(self, name: str, unit: str, quantity_change: float, notes: str = "") -> StockItem:
        stock_items = {item["name"].lower(): item for item in self.data["stock"]}
        key = name.lower()
        if key in stock_items:
            stock_items[key]["quantity"] = float(stock_items[key]["quantity"]) + float(quantity_change)
            stock_items[key]["last_updated"] = now_ts()
            if notes:
                stock_items[key]["notes"] = notes
            # replace in original list
            for idx, item in enumerate(self.data["stock"]):
                if item["name"].lower() == key:
                    self.data["stock"][idx] = stock_items[key]
                    break
        else:
            new_item = StockItem(
                name=name,
                unit=unit,
                quantity=float(quantity_change),
                last_updated=now_ts(),
                notes=notes,
            )
            self.data["stock"].append(new_item.to_dict())
        self._persist()
        return StockItem.from_dict(next(item for item in self.data["stock"] if item["name"].lower() == key))

    def stock_report(self) -> List[StockItem]:
        return [StockItem.from_dict(raw) for raw in self.data["stock"]]


__all__ = ["WorkshopTracker"]
