"""
Tek dosyalık atölye takip uygulaması.

Bu dosya, araç giriş-çıkış, bayi gelir/borç, haftalık ödemeler,
gelir-gider ve stok takibini tek başına çalıştırmak için hazırlandı.
"""
from __future__ import annotations

import json
import uuid
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional


def _resolve_data_file() -> Path:
    """Return the JSON path; can be overridden via WORKSHOP_DATA_FILE."""

    override = os.environ.get("WORKSHOP_DATA_FILE")
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parent / "workshop_data.json"


DATA_FILE = _resolve_data_file()


def now_ts() -> str:
    return datetime.now().isoformat()


# ----------------------------- Veri modelleri ------------------------------


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


# -------------------------- Depolama yardımcıları --------------------------


def _default_payload() -> Dict[str, object]:
    return {
        "vehicles": [],
        "dealer_transactions": [],
        "wages": [],
        "income_expenses": [],
        "stock": [],
    }


def _with_defaults(payload: Dict[str, object]) -> Dict[str, object]:
    template = _default_payload()
    for key, default_value in template.items():
        payload.setdefault(key, default_value)
    return payload


def load_data() -> Dict[str, object]:
    if not DATA_FILE.exists():
        return _default_payload()
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _default_payload()
    if not isinstance(loaded, dict):
        return _default_payload()
    return _with_defaults(loaded)


def save_data(payload: Dict[str, object]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(_with_defaults(payload), f, ensure_ascii=False, indent=2)


# --------------------------- İş mantığı sınıfı -----------------------------


class WorkshopTracker:
    def __init__(self) -> None:
        self.data = load_data()
        # Dosya yoksa hemen oluştur
        if not DATA_FILE.exists():
            save_data(self.data)

    # Araç işlemleri
    def add_vehicle_entry(
        self, brand: str, model: str, plate: str, notes: str = ""
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
        save_data(self.data)
        return vehicle

    def mark_vehicle_exit(self, vehicle_id: str, notes: str = "") -> Optional[VehicleRecord]:
        for raw in self.data["vehicles"]:
            if raw["vehicle_id"] == vehicle_id:
                raw["exit_date"] = now_ts()
                if notes:
                    raw["notes"] = notes
                save_data(self.data)
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
        save_data(self.data)
        return transaction

    def dealer_report(self) -> Dict[str, Dict[str, float]]:
        summary: Dict[str, Dict[str, float]] = {}
        for raw in self.data["dealer_transactions"]:
            dealer = raw["dealer_name"]
            summary.setdefault(dealer, {"gelir": 0.0, "borc": 0.0, "net": 0.0})
            summary[dealer][raw["direction"]] += float(raw["amount"])
        for dealer, row in summary.items():
            row["net"] = row["gelir"] - row["borc"]
        return summary

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
        save_data(self.data)
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
        save_data(self.data)
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
        save_data(self.data)
        return StockItem.from_dict(next(item for item in self.data["stock"] if item["name"].lower() == key))

    def stock_report(self) -> List[StockItem]:
        return [StockItem.from_dict(raw) for raw in self.data["stock"]]


# ---------------------------- CLI yardımcıları -----------------------------


def prompt_input(label: str) -> str:
    return input(f"{label}: ").strip()


def print_header(title: str) -> None:
    line = "=" * len(title)
    print(f"\n{title}\n{line}")


def print_vehicle(vehicle: VehicleRecord) -> None:
    print(
        dedent(
            f"""
            ID: {vehicle.vehicle_id}
            Marka/Model: {vehicle.brand} / {vehicle.model}
            Plaka: {vehicle.plate}
            Giriş: {vehicle.entry_date}
            Çıkış: {vehicle.exit_date or '-'}
            Not: {vehicle.notes or '-'}
            """
        ).strip()
    )


def print_stock(item: StockItem) -> None:
    print(
        dedent(
            f"""
            Ürün: {item.name}
            Miktar: {item.quantity} {item.unit}
            Güncelleme: {item.last_updated}
            Not: {item.notes or '-'}
            """
        ).strip()
    )


def handle_vehicle_entry(tracker: WorkshopTracker) -> None:
    brand = prompt_input("Marka")
    model = prompt_input("Model")
    plate = prompt_input("Plaka")
    notes = prompt_input("Not (opsiyonel)")
    vehicle = tracker.add_vehicle_entry(brand, model, plate, notes)
    print(f"Kayıt alındı. ID: {vehicle.vehicle_id}")


def handle_vehicle_exit(tracker: WorkshopTracker) -> None:
    vehicle_id = prompt_input("Çıkış yapılacak araç ID")
    notes = prompt_input("Not (opsiyonel)")
    vehicle = tracker.mark_vehicle_exit(vehicle_id, notes)
    if vehicle:
        print("Araç çıkışı kaydedildi.")
    else:
        print("Araç bulunamadı.")


def list_vehicles(tracker: WorkshopTracker) -> None:
    only_open = prompt_input("Sadece atölyedeki araçlar? (e/h)").lower() == "e"
    vehicles = tracker.list_vehicles(only_open=only_open)
    if not vehicles:
        print("Kayıt yok.")
        return
    for vehicle in vehicles:
        print_vehicle(vehicle)
        print("-" * 20)


def handle_dealer_transaction(tracker: WorkshopTracker) -> None:
    dealer_name = prompt_input("Bayi adı")
    description = prompt_input("Açıklama")
    direction = prompt_input("Gelir mi borç mu? (gelir/borc)").lower()
    amount = float(prompt_input("Tutar"))
    transaction = tracker.add_dealer_transaction(dealer_name, description, amount, direction)
    print(f"İşlem kaydedildi: {transaction.transaction_id}")


def show_dealer_report(tracker: WorkshopTracker) -> None:
    report = tracker.dealer_report()
    if not report:
        print("Kayıt yok.")
        return
    for dealer, row in report.items():
        print(f"{dealer}: Gelir {row['gelir']:.2f} | Borç {row['borc']:.2f} | Net {row['net']:.2f}")


def handle_wage(tracker: WorkshopTracker) -> None:
    staff_name = prompt_input("Personel adı")
    week_ending = prompt_input("Hafta bitiş tarihi (örn 2024-09-20)")
    amount = float(prompt_input("Tutar"))
    notes = prompt_input("Not (opsiyonel)")
    tracker.add_wage_record(staff_name, week_ending, amount, notes)
    print("Ödeme kaydedildi.")


def list_wages(tracker: WorkshopTracker) -> None:
    wages = tracker.list_wages()
    if not wages:
        print("Kayıt yok.")
        return
    for wage in wages:
        print(
            f"{wage.staff_name} | Hafta Sonu: {wage.week_ending} | Tutar: {wage.amount:.2f} | Not: {wage.notes or '-'}"
        )


def handle_income_expense(tracker: WorkshopTracker) -> None:
    category = prompt_input("Kategori")
    description = prompt_input("Açıklama")
    kind = prompt_input("Gelir mi gider mi? (gelir/gider)").lower()
    amount = float(prompt_input("Tutar"))
    tracker.add_income_expense(category, description, amount, kind)
    print("Kayıt eklendi.")


def show_income_expense_report(tracker: WorkshopTracker) -> None:
    report = tracker.income_expense_report()
    print(
        f"Toplam Gelir: {report['gelir']:.2f}\nToplam Gider: {report['gider']:.2f}\nNet: {report['net']:.2f}"
    )


def handle_stock(tracker: WorkshopTracker) -> None:
    name = prompt_input("Ürün adı")
    unit = prompt_input("Birim (adet, litre vb.)")
    qty = float(prompt_input("Miktar değişimi (+/-)"))
    notes = prompt_input("Not (opsiyonel)")
    tracker.upsert_stock(name, unit, qty, notes)
    print("Stok güncellendi.")


def list_stock(tracker: WorkshopTracker) -> None:
    items = tracker.stock_report()
    if not items:
        print("Stok boş.")
        return
    for item in items:
        print_stock(item)
        print("-" * 20)


def menu() -> None:
    tracker = WorkshopTracker()
    actions = {
        "1": handle_vehicle_entry,
        "2": handle_vehicle_exit,
        "3": list_vehicles,
        "4": handle_dealer_transaction,
        "5": show_dealer_report,
        "6": handle_wage,
        "7": list_wages,
        "8": handle_income_expense,
        "9": show_income_expense_report,
        "10": handle_stock,
        "11": list_stock,
    }

    while True:
        print_header("Atölye Yönetimi (Tek Dosya)")
        print(
            dedent(
                """
                1) Araç giriş kaydı
                2) Araç çıkışı
                3) Araç listesi
                4) Bayi işlem kaydı (gelir/borç)
                5) Bayi raporu
                6) Haftalık ödeme ekle
                7) Haftalık ödemeleri listele
                8) Gelir/Gider kaydı
                9) Gelir/Gider raporu
                10) Stok güncelle
                11) Stok listesini göster
                0) Çıkış
                """
            )
        )
        choice = input("Seçiminiz: ").strip()
        if choice == "0":
            print("Güle güle!")
            break
        action = actions.get(choice)
        if action:
            try:
                action(tracker)
            except ValueError as exc:
                print(f"Hata: {exc}")
        else:
            print("Geçersiz seçim.")


if __name__ == "__main__":
    menu()
