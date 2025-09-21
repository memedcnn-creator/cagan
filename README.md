import sys, os, sqlite3, shutil, webbrowser
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QMessageBox, QComboBox, QInputDialog, QMainWindow, QAction, QDateEdit,
    QTableWidget, QTableWidgetItem
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QDate
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import matplotlib.pyplot as plt

DB_NAME = "servis.db"
UPLOAD_DIR = "uploads"
BACKUP_DIR = "backup"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# ----------------------------- Firma Ayarları -----------------------------
class FirmaAyarWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Firma Ayarları")
        self.setGeometry(200, 200, 350, 200)

        self.lbl_ad = QLabel("Firma Adı:")
        self.txt_ad = QLineEdit()
        self.lbl_tel = QLabel("Telefon:")
        self.txt_tel = QLineEdit()
        self.btn_kaydet = QPushButton("Kaydet")
        self.btn_kaydet.clicked.connect(self.kaydet)

        layout = QVBoxLayout()
        layout.addWidget(self.lbl_ad); layout.addWidget(self.txt_ad)
        layout.addWidget(self.lbl_tel); layout.addWidget(self.txt_tel)
        layout.addWidget(self.btn_kaydet)
        self.setLayout(layout)
        self.verileri_yukle()

    def verileri_yukle(self):
        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
        c.execute("SELECT ad, telefon FROM Firma LIMIT 1"); row = c.fetchone(); conn.close()
        if row: self.txt_ad.setText(row[0]); self.txt_tel.setText(row[1])

    def kaydet(self):
        ad, tel = self.txt_ad.text().strip(), self.txt_tel.text().strip()
        if not ad: QMessageBox.warning(self,"Uyarı","Firma adı boş olamaz!"); return
        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
        c.execute("SELECT id FROM Firma LIMIT 1"); row = c.fetchone()
        if row: c.execute("UPDATE Firma SET ad=?, telefon=? WHERE id=?",(ad,tel,row[0]))
        else: c.execute("INSERT INTO Firma(ad,telefon) VALUES(?,?)",(ad,tel))
        conn.commit(); conn.close(); QMessageBox.information(self,"Bilgi","Kaydedildi ✅")

# ----------------------------- Teknisyen Yönetimi -----------------------------
class TeknisyenWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teknisyen Yönetimi")
        self.setGeometry(250, 250, 400, 300)

        self.lbl_ad = QLabel("Teknisyen Adı:")
        self.txt_ad = QLineEdit()
        self.btn_ekle = QPushButton("Ekle"); self.btn_ekle.clicked.connect(self.ekle)
        self.btn_sil = QPushButton("Sil"); self.btn_sil.clicked.connect(self.sil)
        self.list_teknisyen = QListWidget(); self.list_teknisyen.itemSelectionChanged.connect(self.secim_degisti)

        h_box = QHBoxLayout(); h_box.addWidget(self.txt_ad); h_box.addWidget(self.btn_ekle); h_box.addWidget(self.btn_sil)
        layout = QVBoxLayout(); layout.addWidget(self.lbl_ad); layout.addLayout(h_box); layout.addWidget(self.list_teknisyen)
        self.setLayout(layout); self.listele()

    def listele(self):
        self.list_teknisyen.clear(); conn = sqlite3.connect(DB_NAME); c = conn.cursor()
        c.execute("SELECT id, ad FROM Teknisyen ORDER BY ad")
        for row in c.fetchall(): self.list_teknisyen.addItem(f"{row[0]} - {row[1]}")
        conn.close()

    def ekle(self):
        ad = self.txt_ad.text().strip()
        if not ad: return
        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
        c.execute("INSERT INTO Teknisyen(ad) VALUES(?)",(ad,))
        conn.commit(); conn.close(); self.txt_ad.clear(); self.listele()

    def sil(self):
        secili = self.list_teknisyen.currentItem()
        if not secili: return
        teknisyen_id = int(secili.text().split(" - ")[0])
        conn = sqlite3.connect(DB_NAME); c = conn.cursor(); c.execute("DELETE FROM Teknisyen WHERE id=?",(teknisyen_id,))
        conn.commit(); conn.close(); self.listele()

    def secim_degisti(self):
        secili = self.list_teknisyen.currentItem()
        if secili: self.txt_ad.setText(secili.text().split(" - ")[1])
# ----------------------------- Bayi Yönetimi -----------------------------
# ----------------------------- Bayi Yönetimi -----------------------------
class BayiWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bayi Yönetimi")
        self.setGeometry(300, 300, 500, 400)

        # Alanlar
        self.lbl_ad = QLabel("Bayi Adı:")
        self.txt_ad = QLineEdit()
        self.lbl_tel = QLabel("Telefon:")
        self.txt_tel = QLineEdit()
        self.lbl_adres = QLabel("Adres:")
        self.txt_adres = QLineEdit()

        # Butonlar
        self.btn_ekle = QPushButton("Ekle"); self.btn_ekle.clicked.connect(self.ekle)
        self.btn_guncelle = QPushButton("Güncelle"); self.btn_guncelle.clicked.connect(self.guncelle)
        self.btn_sil = QPushButton("Sil"); self.btn_sil.clicked.connect(self.sil)
        self.btn_borc = QPushButton("Borç Ekle"); self.btn_borc.clicked.connect(lambda: self.hareket_ekle(-1))
        self.btn_odeme = QPushButton("Ödeme Ekle"); self.btn_odeme.clicked.connect(lambda: self.hareket_ekle(1))

        self.list_bayi = QListWidget()
        self.list_bayi.itemSelectionChanged.connect(self.secim_degisti)

        # Form düzeni
        form = QVBoxLayout()
        form.addWidget(self.lbl_ad); form.addWidget(self.txt_ad)
        form.addWidget(self.lbl_tel); form.addWidget(self.txt_tel)
        form.addWidget(self.lbl_adres); form.addWidget(self.txt_adres)

        # Buton düzeni
        h_buton1 = QHBoxLayout()
        h_buton1.addWidget(self.btn_ekle)
        h_buton1.addWidget(self.btn_guncelle)
        h_buton1.addWidget(self.btn_sil)

        h_buton2 = QHBoxLayout()
        h_buton2.addWidget(self.btn_borc)
        h_buton2.addWidget(self.btn_odeme)

        # Ana düzen
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(h_buton1)
        layout.addLayout(h_buton2)
        layout.addWidget(self.list_bayi)
        self.setLayout(layout)

        self.listele()

    # ---------------- Fonksiyonlar ----------------
    def listele(self):
        self.list_bayi.clear()
        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
        c.execute("SELECT id, ad, telefon, adres, bakiye FROM Bayi ORDER BY ad")
        for row in c.fetchall():
            self.list_bayi.addItem(f"{row[0]} - {row[1]} | Tel:{row[2]} | Bakiye:{row[4]} ₺")
        conn.close()

    def ekle(self):
        ad,tel,adres=self.txt_ad.text().strip(),self.txt_tel.text().strip(),self.txt_adres.text().strip()
        if not ad: return
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("INSERT INTO Bayi(ad,telefon,adres,bakiye) VALUES(?,?,?,0)",(ad,tel,adres))
        conn.commit(); conn.close(); self.listele()

    def guncelle(self):
        secili=self.list_bayi.currentItem()
        if not secili: return
        bayi_id=int(secili.text().split(" - ")[0])
        ad,tel,adres=self.txt_ad.text().strip(),self.txt_tel.text().strip(),self.txt_adres.text().strip()
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("UPDATE Bayi SET ad=?,telefon=?,adres=? WHERE id=?",(ad,tel,adres,bayi_id))
        conn.commit(); conn.close(); self.listele()

    def sil(self):
        secili=self.list_bayi.currentItem()
        if not secili: return
        bayi_id=int(secili.text().split(" - ")[0])
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("DELETE FROM Bayi WHERE id=?",(bayi_id,))
        conn.commit(); conn.close(); self.listele()

    def hareket_ekle(self,tip):
        secili=self.list_bayi.currentItem()
        if not secili: return
        bayi_id=int(secili.text().split(" - ")[0])
        tutar,ok=QInputDialog.getDouble(self,"Tutar","Miktar:",decimals=2)
        if not ok: return
        aciklama="Ödeme" if tip==1 else "Borç"
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("INSERT INTO Hareket(bayi_id,aciklama,tutar,tarih) VALUES(?,?,?,date('now'))",(bayi_id,aciklama,tutar*tip))
        c.execute("UPDATE Bayi SET bakiye=bakiye+? WHERE id=?",(tutar*tip,bayi_id))
        conn.commit(); conn.close(); self.listele()

    def secim_degisti(self):
        secili=self.list_bayi.currentItem()
        if not secili: return
        bayi_id=int(secili.text().split(" - ")[0])
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("SELECT ad,telefon,adres FROM Bayi WHERE id=?",(bayi_id,))
        row=c.fetchone(); conn.close()
        if row:
            self.txt_ad.setText(row[0])
            self.txt_tel.setText(row[1] or "")
            self.txt_adres.setText(row[2] or "")

# ----------------------------- Yeni Kayıt Penceresi -----------------------------
class ServisEkleWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Servis Kaydı")
        self.setGeometry(250,250,400,600)

        self.txt_musteri_ad = QLineEdit()
        self.txt_musteri_tel = QLineEdit()
        self.txt_plaka,self.txt_marka,self.txt_model=QLineEdit(),QLineEdit(),QLineEdit()
        self.txt_ariza=QTextEdit()
        self.cmb_durum=QComboBox(); self.cmb_durum.addItems(["Beklemede","Tamir Oldu","Parça Bekliyor","İade Edildi"])
        self.cmb_teknisyen=QComboBox(); self.cmb_bayi=QComboBox()

        self.dt_muayene=QDateEdit(); self.dt_muayene.setCalendarPopup(True); self.dt_muayene.setDate(QDate.currentDate())
        self.dt_sigorta=QDateEdit(); self.dt_sigorta.setCalendarPopup(True); self.dt_sigorta.setDate(QDate.currentDate())
        self.dt_egzoz=QDateEdit(); self.dt_egzoz.setCalendarPopup(True); self.dt_egzoz.setDate(QDate.currentDate())

        self.btn_kaydet=QPushButton("Kaydet"); self.btn_kaydet.clicked.connect(self.kaydet)

        layout=QVBoxLayout()
        for lbl,w in [("Müşteri Adı",self.txt_musteri_ad),("Telefon",self.txt_musteri_tel),
                      ("Plaka",self.txt_plaka),("Marka",self.txt_marka),("Model",self.txt_model),
                      ("Arıza",self.txt_ariza),("Durum",self.cmb_durum),
                      ("Teknisyen",self.cmb_teknisyen),("Bayi",self.cmb_bayi),
                      ("Muayene Tarihi",self.dt_muayene),("Sigorta Tarihi",self.dt_sigorta),("Egzoz Tarihi",self.dt_egzoz)]:
            layout.addWidget(QLabel(lbl)); layout.addWidget(w)
        layout.addWidget(self.btn_kaydet)
        self.setLayout(layout)

        self.teknisyenleri_yukle(); self.bayileri_yukle()

    def teknisyenleri_yukle(self):
        self.cmb_teknisyen.clear(); conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("SELECT id,ad FROM Teknisyen ORDER BY ad")
        for row in c.fetchall(): self.cmb_teknisyen.addItem(row[1],row[0])
        conn.close()

    def bayileri_yukle(self):
        self.cmb_bayi.clear(); self.cmb_bayi.addItem("Seçili değil",None)
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("SELECT id,ad FROM Bayi ORDER BY ad")
        for row in c.fetchall(): self.cmb_bayi.addItem(row[1],row[0])
        conn.close()

    def kaydet(self):
        plaka=self.txt_plaka.text().strip()
        if not plaka: 
            QMessageBox.warning(self,"Uyarı","Plaka boş olamaz!"); return

        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("""INSERT INTO Servis(musteri_ad,musteri_tel,plaka,marka,model,ariza,durum,teknisyen_id,bayi_id,
                     muayene_tarih,sigorta_tarih,egzoz_tarih,tarih) 
                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,date('now'))""",
                  (self.txt_musteri_ad.text().strip(), self.txt_musteri_tel.text().strip(),
                   plaka,self.txt_marka.text().strip(),self.txt_model.text().strip(),
                   self.txt_ariza.toPlainText().strip(),self.cmb_durum.currentText(),
                   self.cmb_teknisyen.currentData(),self.cmb_bayi.currentData(),
                   self.dt_muayene.date().toString("yyyy-MM-dd"),
                   self.dt_sigorta.date().toString("yyyy-MM-dd"),
                   self.dt_egzoz.date().toString("yyyy-MM-dd")))
        conn.commit(); conn.close()

        QMessageBox.information(self,"Bilgi","Kayıt eklendi ✅")
        self.close()

        if self.parent(): self.parent().listele()
# ----------------------------- Servis Listesi -----------------------------
class ServisWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Servis Kayıtları")
        self.setGeometry(200,200,800,500)

        self.txt_ara = QLineEdit()
        self.txt_ara.setPlaceholderText("🔍 Müşteri adı, telefon, plaka, marka, model, arıza...")
        self.txt_ara.textChanged.connect(self.listele)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["Müşteri", "Telefon", "Plaka", "Marka", "Model", "Durum", "Teknisyen", "Bayi"]
        )
        self.table.cellDoubleClicked.connect(self.detay_ac)

        layout=QVBoxLayout()
        layout.addWidget(self.txt_ara)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.listele()

    def listele(self):
        arama = self.txt_ara.text().strip()
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        if arama:
            sorgu = """SELECT Servis.id,musteri_ad,musteri_tel,plaka,marka,model,ariza,durum,
                              IFNULL(Teknisyen.ad,'-'),IFNULL(Bayi.ad,'-')
                       FROM Servis
                       LEFT JOIN Teknisyen ON Servis.teknisyen_id=Teknisyen.id
                       LEFT JOIN Bayi ON Servis.bayi_id=Bayi.id
                       WHERE musteri_ad LIKE ? OR musteri_tel LIKE ? OR plaka LIKE ? 
                             OR marka LIKE ? OR model LIKE ? OR ariza LIKE ?
                       ORDER BY Servis.id DESC"""
            like = f"%{arama}%"
            c.execute(sorgu,(like,like,like,like,like,like))
        else:
            c.execute("""SELECT Servis.id,musteri_ad,musteri_tel,plaka,marka,model,ariza,durum,
                                IFNULL(Teknisyen.ad,'-'),IFNULL(Bayi.ad,'-')
                         FROM Servis
                         LEFT JOIN Teknisyen ON Servis.teknisyen_id=Teknisyen.id
                         LEFT JOIN Bayi ON Servis.bayi_id=Bayi.id
                         ORDER BY Servis.id DESC""")
        rows=c.fetchall(); conn.close()

        self.table.setRowCount(len(rows))
        for i,row in enumerate(rows):
            servis_id=row[0]
            data=[row[1],row[2],row[3],row[4],row[5],row[7],row[8],row[9]]
            for j,val in enumerate(data):
                item=QTableWidgetItem(str(val))
                if row[7]=="Beklemede": item.setBackground(QColor("#FFF59D"))
                elif row[7]=="Tamir Oldu": item.setBackground(QColor("#A5D6A7"))
                elif row[7]=="Parça Bekliyor": item.setBackground(QColor("#FFCC80"))
                elif row[7]=="İade Edildi": item.setBackground(QColor("#EF9A9A"))
                self.table.setItem(i,j,item)
            self.table.setVerticalHeaderItem(i,QTableWidgetItem(str(servis_id)))

        if self.parent(): self.parent().update_statusbar()

    def detay_ac(self,row,col):
        servis_id=int(self.table.verticalHeaderItem(row).text())
        self.detay=ServisDetayWindow(servis_id)
        self.detay.show()

# ----------------------------- Servis Detay -----------------------------
class ServisDetayWindow(QWidget):
    def __init__(self,servis_id):
        super().__init__(); self.servis_id=servis_id
        self.setWindowTitle("Servis Detayı"); self.setGeometry(250,250,500,500)

        # Alanlar
        self.txt_plaka,self.txt_marka,self.txt_model=[QLineEdit() for _ in range(3)]
        for w in [self.txt_plaka,self.txt_marka,self.txt_model]: w.setReadOnly(True)
        self.txt_ariza=QTextEdit(); self.txt_ariza.setReadOnly(True)
        self.cmb_durum=QComboBox(); self.cmb_durum.addItems(["Beklemede","Tamir Oldu","Parça Bekliyor","İade Edildi"])

        self.lbl_ucret = QLabel("İşçilik / Ücret (₺):")
        self.txt_ucret = QLineEdit()

        self.btn_kaydet = QPushButton("💾 Kaydet / Güncelle"); self.btn_kaydet.clicked.connect(self.guncelle)

        self.btn_whatsapp=QPushButton("📱 WhatsApp"); self.btn_whatsapp.clicked.connect(self.whatsapp_mesaj)
        self.btn_pdf=QPushButton("📄 Servis Fişi PDF"); self.btn_pdf.clicked.connect(self.servis_pdf)
        self.btn_fatura=QPushButton("🧾 Fatura PDF"); self.btn_fatura.clicked.connect(self.fatura_pdf)

        # Düzen
        layout=QVBoxLayout()
        for lbl,w in [("Plaka",self.txt_plaka),("Marka",self.txt_marka),("Model",self.txt_model),
                      ("Arıza",self.txt_ariza),("Durum",self.cmb_durum),
                      (self.lbl_ucret,self.txt_ucret)]:
            layout.addWidget(QLabel(lbl) if isinstance(lbl,str) else lbl)
            layout.addWidget(w)
        layout.addWidget(self.btn_kaydet)
        for b in [self.btn_whatsapp,self.btn_pdf,self.btn_fatura]: layout.addWidget(b)
        self.setLayout(layout)

        self.yukle()

    def yukle(self):
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("""SELECT musteri_ad,musteri_tel,plaka,marka,model,ariza,durum,
                            IFNULL(teknisyen_id,0),IFNULL(bayi_id,0),
                            IFNULL(Firma.ad,''),IFNULL(Firma.telefon,''),IFNULL(ucret,0)
                     FROM Servis 
                     LEFT JOIN Firma ON Firma.id=1
                     WHERE Servis.id=?""",(self.servis_id,))
        row=c.fetchone(); conn.close()
        if row:
            self.musteri_ad=row[0]; self.musteri_tel=row[1]
            self.txt_plaka.setText(row[2]); self.txt_marka.setText(row[3]); self.txt_model.setText(row[4])
            self.txt_ariza.setPlainText(row[5]); self.cmb_durum.setCurrentText(row[6])
            self.teknisyen_id=row[7]; self.bayi_id=row[8]
            self.firma_ad=row[9]; self.firma_tel=row[10]; self.txt_ucret.setText(str(row[11]))

    def guncelle(self):
        durum=self.cmb_durum.currentText()
        try: ucret=float(self.txt_ucret.text()) if self.txt_ucret.text() else 0
        except: QMessageBox.warning(self,"Hata","Ücret sayısal olmalı!"); return

        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("UPDATE Servis SET durum=?, ucret=? WHERE id=?",(durum,ucret,self.servis_id))

        # Bayi bakiyesi güncelle
        if self.bayi_id:
            if durum=="Tamir Oldu":
                c.execute("UPDATE Bayi SET bakiye=bakiye+? WHERE id=?",(ucret,self.bayi_id))
            elif durum=="İade Edildi":
                c.execute("UPDATE Bayi SET bakiye=bakiye-? WHERE id=?",(ucret,self.bayi_id))

        conn.commit(); conn.close()
        QMessageBox.information(self,"Bilgi","Kayıt güncellendi ✅")

    def whatsapp_mesaj(self):
        mesaj=f"Merhaba {self.musteri_ad},\n🚗 {self.txt_plaka.text()} - {self.txt_marka.text()} {self.txt_model.text()}\n🔧 Durum: {self.cmb_durum.currentText()}\n💰 Ücret: {self.txt_ucret.text()} ₺\n📞 {self.musteri_tel}\n\n{self.firma_ad} ({self.firma_tel})"
        QMessageBox.information(self,"WhatsApp Mesajı",mesaj)

    # servis_pdf ve fatura_pdf fonksiyonları aynı kalabilir

    def servis_pdf(self):
        dosya=f"servis_{self.servis_id}.pdf"; c=canvas.Canvas(dosya,pagesize=A4); w,h=A4
        c.setFont("Helvetica-Bold",14); c.drawString(50,h-50,f"{self.firma_ad} - Servis Fişi")
        c.setFont("Helvetica",10); c.drawString(50,h-70,f"Tel: {self.firma_tel}"); c.line(50,h-80,w-50,h-80)
        c.drawString(50,h-100,f"Müşteri: {self.musteri_ad} / {self.musteri_tel}")
        c.drawString(50,h-120,f"Plaka: {self.txt_plaka.text()}"); c.drawString(50,h-140,f"Marka: {self.txt_marka.text()}")
        c.drawString(50,h-160,f"Model: {self.txt_model.text()}"); c.drawString(50,h-180,f"Durum: {self.cmb_durum.currentText()}")
        c.drawString(50,h-200,f"Teknisyen: {self.teknisyen}"); c.drawString(50,h-220,f"Bayi: {self.bayi}")
        c.drawString(50,h-250,"Arıza:"); c.drawString(60,h-270,self.txt_ariza.toPlainText())
        c.showPage(); c.save(); webbrowser.open(dosya)

    def fatura_pdf(self):
        iscilik,ok=QInputDialog.getDouble(self,"İşçilik","Ücret (₺):",0,0,100000,2)
        if not ok: return
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("SELECT ad,fiyat FROM Malzeme WHERE servis_id=?",(self.servis_id,))
        malzemeler=c.fetchall(); conn.close()
        data=[["Malzeme","Fiyat"]]; toplam=0
        for ad,fiyat in malzemeler: data.append([ad,f"{fiyat:.2f}"]); toplam+=fiyat
        data.append(["İşçilik",f"{iscilik:.2f}"]); toplam+=iscilik
        kdv=toplam*0.20; genel=toplam+kdv
        data.append(["KDV %20",f"{kdv:.2f}"]); data.append(["GENEL TOPLAM",f"{genel:.2f}"])
        dosya=f"fatura_{self.servis_id}.pdf"; pdf=canvas.Canvas(dosya,pagesize=A4); w,h=A4
        pdf.setFont("Helvetica-Bold",14); pdf.drawString(50,h-50,f"{self.firma_ad} - FATURA")
        pdf.setFont("Helvetica",10); pdf.drawString(50,h-70,f"Tel: {self.firma_tel}")
        table=Table(data,colWidths=[300,100])
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightblue),('GRID',(0,0),(-1,-1),1,colors.black)]))
        table.wrapOn(pdf,w,h); table.drawOn(pdf,50,h-300); pdf.showPage(); pdf.save(); webbrowser.open(dosya)

# ----------------------------- Raporlar -----------------------------
class RaporWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raporlar")
        self.setGeometry(300, 300, 500, 400)

        self.btn_teknisyen = QPushButton("👷 Teknisyen Performansı"); self.btn_teknisyen.clicked.connect(self.rapor_teknisyen)
        self.btn_aylik = QPushButton("📅 Aylık İstatistik"); self.btn_aylik.clicked.connect(self.rapor_aylik)
        self.btn_gelir = QPushButton("💰 Gelir – Gider Analizi"); self.btn_gelir.clicked.connect(self.rapor_gelir)

        layout = QVBoxLayout(); layout.addWidget(self.btn_teknisyen); layout.addWidget(self.btn_aylik); layout.addWidget(self.btn_gelir)
        self.setLayout(layout)

    def rapor_teknisyen(self):
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("""SELECT Teknisyen.ad,COUNT(Servis.id),
                            SUM(CASE WHEN durum='Tamir Oldu' THEN 1 ELSE 0 END),
                            SUM(CASE WHEN durum='Beklemede' THEN 1 ELSE 0 END)
                     FROM Servis LEFT JOIN Teknisyen ON Servis.teknisyen_id=Teknisyen.id
                     GROUP BY Teknisyen.ad""")
        rows=c.fetchall(); conn.close()
        if not rows: QMessageBox.information(self,"Bilgi","Kayıt bulunamadı"); return
        txt="Teknisyen Performansı:\n\n"
        for r in rows: txt+=f"{r[0]} → Toplam:{r[1]} | Tamamlanan:{r[2]} | Bekleyen:{r[3]}\n"
        QMessageBox.information(self,"Rapor",txt)

    def rapor_aylik(self):
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("""SELECT strftime('%Y-%m',tarih), COUNT(*) FROM Servis GROUP BY strftime('%Y-%m',tarih)""")
        rows=c.fetchall(); conn.close()
        if not rows: QMessageBox.information(self,"Bilgi","Kayıt yok"); return
        aylar=[r[0] for r in rows]; sayilar=[r[1] for r in rows]
        plt.bar(aylar,sayilar); plt.title("Aylık Servis İstatistikleri")
        plt.xlabel("Ay"); plt.ylabel("Kayıt Sayısı"); plt.xticks(rotation=45); plt.tight_layout(); plt.show()

    def rapor_gelir(self):
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("""SELECT SUM(fiyat) FROM Malzeme"""); malzeme_gelir=c.fetchone()[0] or 0
        c.execute("""SELECT COUNT(*) FROM Servis"""); servis_sayisi=c.fetchone()[0]
        iscilik_gelir=servis_sayisi*500
        c.execute("""SELECT SUM(tutar) FROM Hareket"""); hareket_toplam=c.fetchone()[0] or 0
        conn.close()
        gelir=malzeme_gelir+iscilik_gelir; gider=hareket_toplam if hareket_toplam<0 else 0; net=gelir+gider
        labels=["Gelir","Gider","Net"]; values=[gelir,abs(gider),net]
        plt.bar(labels,values,color=["green","red","blue"]); plt.title("Gelir – Gider Analizi"); plt.show()

# ----------------------------- Hatırlatıcı -----------------------------
class HatirlatmaWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yaklaşan Tarihler"); self.setGeometry(300,300,400,300)
        self.list=QListWidget(); layout=QVBoxLayout(); layout.addWidget(self.list); self.setLayout(layout); self.listele()

    def listele(self):
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("""SELECT musteri_ad,plaka,muayene_tarih,sigorta_tarih,egzoz_tarih 
                     FROM Servis WHERE date(muayene_tarih) <= date('now','+7 day')
                        OR date(sigorta_tarih) <= date('now','+7 day')
                        OR date(egzoz_tarih) <= date('now','+7 day')""")
        rows=c.fetchall(); conn.close()
        self.list.clear()
        for r in rows:
            self.list.addItem(f"{r[0]} - {r[1]} | Muayene:{r[2]} Sigorta:{r[3]} Egzoz:{r[4]}")

# ----------------------------- Ana Menü -----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100,100,1000,600)

        # Firma adını pencere başlığına yaz
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("SELECT ad FROM Firma LIMIT 1"); row=c.fetchone()
        conn.close()
        firma_ad = row[0] if row and row[0] else "Arıza Takip Programı"
        self.setWindowTitle(firma_ad)

        menubar=self.menuBar()
        m1=menubar.addMenu("🏢 Firma"); act1=QAction("Firma Ayarları",self); act1.triggered.connect(self.ac_firma); m1.addAction(act1)
        m2=menubar.addMenu("👷 Teknisyen"); act2=QAction("Teknisyen Yönetimi",self); act2.triggered.connect(self.ac_teknisyen); m2.addAction(act2)
        m3=menubar.addMenu("🏪 Bayi"); act3=QAction("Bayi Yönetimi",self); act3.triggered.connect(self.ac_bayi); m3.addAction(act3)
        m4=menubar.addMenu("🔧 Servis"); actYeni=QAction("➕ Yeni Kayıt",self); actYeni.triggered.connect(self.ac_yeni); m4.addAction(actYeni)
        m5=menubar.addMenu("📊 Raporlar"); act5=QAction("Raporlar",self); act5.triggered.connect(self.ac_rapor); m5.addAction(act5)
        m7=menubar.addMenu("⏰ Hatırlatıcı"); actHatir=QAction("Yaklaşan Tarihler",self); actHatir.triggered.connect(self.ac_hatirlatma); m7.addAction(actHatir)
        m8=menubar.addMenu("💾 Yedekleme"); actBackup=QAction("Yedek Al",self); actBackup.triggered.connect(self.yedek_al); m8.addAction(actBackup)
        actRestore=QAction("Geri Yükle",self); actRestore.triggered.connect(self.yedek_yukle); m8.addAction(actRestore)

        temaMenu=menubar.addMenu("🎨 Tema")
        actLight=QAction("Açık Tema",self); actLight.triggered.connect(self.tema_acik)
        actDark=QAction("Koyu Tema",self); actDark.triggered.connect(self.tema_koyu)
        temaMenu.addAction(actLight); temaMenu.addAction(actDark)

        self.statusBar().showMessage("Hazır")

        # Ana ekrana servis listesi koy
        self.servis = ServisWindow(parent=self)
        self.setCentralWidget(self.servis)

        # Açılışta hatırlatma
        self.kontrol_hatirlatma()

    # ---------------- Menü İşlemleri ----------------
    def ac_firma(self): self.firma=FirmaAyarWindow(); self.firma.show()
    def ac_teknisyen(self): self.teknisyen=TeknisyenWindow(); self.teknisyen.show()
    def ac_bayi(self): self.bayi=BayiWindow(); self.bayi.show()
    def ac_yeni(self):
        self.yeni = ServisEkleWindow()   # parent verme → pencere normal açılır
        self.yeni.show()
        # kapatılınca ana liste yenilensin
        self.yeni.destroyed.connect(self.servis.listele)
    def ac_rapor(self): self.rapor=RaporWindow(); self.rapor.show()
    def ac_hatirlatma(self): self.hatir=HatirlatmaWindow(); self.hatir.show()

    # ---------------- Yedekleme ----------------
    def yedek_al(self):
        hedef=os.path.join(BACKUP_DIR,"servis_yedek.db")
        try:
            shutil.copy(DB_NAME,hedef)
            QMessageBox.information(self,"Yedekleme",f"✅ Yedek alındı: {hedef}")
        except Exception as e:
            QMessageBox.critical(self,"Hata",str(e))
    def yedek_yukle(self):
        kaynak=os.path.join(BACKUP_DIR,"servis_yedek.db")
        try:
            if os.path.exists(kaynak):
                shutil.copy(kaynak,DB_NAME)
                QMessageBox.information(self,"Geri Yükleme","✅ Yedek geri yüklendi.\nProgramı yeniden başlatın.")
            else:
                QMessageBox.warning(self,"Hata","Yedek dosyası bulunamadı!")
        except Exception as e:
            QMessageBox.critical(self,"Hata",str(e))

    # ---------------- Status Bar & Hatırlatıcı ----------------
    def update_statusbar(self):
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("SELECT COUNT(*) FROM Servis"); toplam=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM Servis WHERE tarih=date('now')"); bugun=c.fetchone()[0]
        conn.close()
        self.statusBar().showMessage(f"Toplam Kayıt: {toplam} | Bugün: {bugun}")

    def kontrol_hatirlatma(self):
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("""SELECT COUNT(*) FROM Servis 
                     WHERE date(muayene_tarih) <= date('now','+7 day') 
                     OR date(sigorta_tarih) <= date('now','+7 day') 
                     OR date(egzoz_tarih) <= date('now','+7 day')""")
        sayi=c.fetchone()[0]; conn.close()
        if sayi>0: QMessageBox.warning(self,"⏰ Hatırlatıcı",f"📌 {sayi} aracın tarihi yaklaşıyor!")

    # ---------------- Tema ----------------
    def tema_acik(self): self.setStyleSheet("")
    def tema_koyu(self):
        self.setStyleSheet("""
            QWidget { background-color: #2b2b2b; color: #f0f0f0; }
            QPushButton { background-color: #444; color: white; border-radius: 5px; padding: 5px; }
            QLineEdit, QTextEdit, QComboBox { background-color: #555; color: white; border: 1px solid #777; }
            QListWidget, QTableWidget { background-color: #333; color: white; }
        """)


# ----------------------------- Çalıştır -----------------------------
if __name__=="__main__":
    app=QApplication(sys.argv)
    mainWin=MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
