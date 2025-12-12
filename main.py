from textwrap import dedent

from tracker import WorkshopTracker


def prompt_input(label: str) -> str:
    return input(f"{label}: ").strip()


def print_header(title: str) -> None:
    line = "=" * len(title)
    print(f"\n{title}\n{line}")


def print_vehicle(vehicle) -> None:
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


def print_stock(item) -> None:
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
    print(f"Toplam Gelir: {report['gelir']:.2f}\nToplam Gider: {report['gider']:.2f}\nNet: {report['net']:.2f}")


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
        print_header("Atölye Yönetimi")
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
