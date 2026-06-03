# -*- coding: utf-8 -*-
"""
Python Music Player - v3 (Premium Player)
"""

import sys, os, random, json

# QtAwesome'un PyQt6'yı sorunsuz algılaması için çevre değişkeni ekliyoruz.
os.environ["QT_API"] = "pyqt6"

from PyQt6.QtWidgets import QApplication

# QTAwesome yüklenmeden ÖNCE bir QApplication örneği yaratıyoruz.
_app = QApplication.instance()
if _app is None:
    _app = QApplication(sys.argv)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QStyle,
    QLineEdit, QComboBox, QFileDialog, QFrame,
    QSystemTrayIcon, QMenu, QSlider, QAbstractItemView, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QUrl, QMimeData, QRectF, QSize
from PyQt6.QtGui import (QIcon, QAction, QPixmap, QShortcut, QKeySequence,
                          QDrag, QPainter, QColor, QLinearGradient, QBrush)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices

try:
    import qtawesome as qta
    QTA = True
except ImportError:
    QTA = False

try:
    from mutagen import File as MutagenFile
    MUTAGEN_VAR = True
except ImportError:
    MUTAGEN_VAR = False

def ana_klasoru_bul():
    if getattr(sys, 'frozen', False): return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

AYAR_DOSYASI       = os.path.join(ana_klasoru_bul(), "ayarlar.json")
DESTEKLENEN_FORMAT  = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.opus')

WIN_W, WIN_H       = 840, 620   
# ÇÖZÜM 1: Render hatasını (ghosting) engellemek için mini modun dikey alanını biraz artırıyoruz.
MINI_W, MINI_H     = 250, 460   

FADE_ADIM_MS  = 30
FADE_SURE_MS  = 1500
CROSSFADE_MS  = 4000

# ── İkon yardımcısı ──────────────────────────────────────────────────────────
_ICON_CACHE: dict = {}

def _ikon(name: str, renk: str = "#ffffff", boyut: int = 16) -> "QIcon":
    key = (name, renk, boyut)
    if key not in _ICON_CACHE:
        if QTA:
            try:
                _ICON_CACHE[key] = qta.icon(name, color=renk, scale_factor=1.0)
            except Exception:
                _ICON_CACHE[key] = QIcon()
        else:
            _ICON_CACHE[key] = QIcon()
    return _ICON_CACHE[key]

def _ikon_temizle():
    _ICON_CACHE.clear()

# ─────────────────────────────────────────────────────────────────────────────
def ayarlari_yukle():
    v = {"tema": "dark", "dil": "tr", "son_klasor": "", "son_sarki": "",
         "son_konum": 0, "ses_aygiti": "", "crossfade": True}
    if os.path.exists(AYAR_DOSYASI):
        try:
            with open(AYAR_DOSYASI, "r", encoding="utf-8") as f:
                v.update(json.load(f))
        except: pass
    return v

def ayarlari_kaydet(a):
    try:
        with open(AYAR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(a, f, ensure_ascii=False, indent=2)
    except: pass

# ─────────────────────────────────────────────────────────────────────────────
LANG = {
    "tr": {
        "title"        : "Python Music Player",
        "folder"       : "Klasör",
        "save_pl"      : "Kaydet",
        "load_pl"      : "Yükle",
        "mini_on"      : "Mini",
        "mini_off"     : "Büyüt",
        "tray_btn"     : "Arka Plan",
        "search"       : "Ara...",
        "vol"          : "Ses",
        "mute"         : "Sessiz",
        "play"         : "Oynat",
        "pause"        : "Duraklat",
        "stop"         : "Durdur",
        "shuffle_on"   : "Karışık",
        "shuffle_off"  : "Sıralı",
        "repeat_on"    : "Döngü: Açık",
        "repeat_off"   : "Döngü: Kapalı",
        "waiting"      : "Müzik Bekleniyor...",
        "loaded"       : "{} şarkı yüklendi",
        "playing"      : "🎵 ",
        "theme"        : "Tema",
        "lang"         : "Dil",
        "sleep_off"    : "Uyku: Kapalı",
        "sleep_on"     : "Uyku: {} dk",
        "tray_show"    : "Arayüzü Göster",
        "tray_quit"    : "Tamamen Kapat",
        "crossfade_on" : "Crossfade: Açık",
        "crossfade_off": "Crossfade: Kapalı",
        "sort_az"      : "A→Z",
        "sort_za"      : "Z→A",
        "sort_new"     : "Yeni→Eski",
        "sort_old"     : "Eski→Yeni",
        "sort_manual"  : "Manuel",
        "unknown_art"  : "Bilinmeyen Sanatçı",
        "unknown_alb"  : "Bilinmeyen Albüm",
        "waiting_song" : "Şarkı Bekleniyor",
        "drag_hint"    : "Sürükle & Bırak ile Ekle",
        "saved"        : "Kaydedildi: {}",
        "prev"         : "Önceki",
        "next"         : "Sonraki",
        "restart"      : "Baştan",
    },
    "en": {
        "title"        : "Python Music Player",
        "folder"       : "Folder",
        "save_pl"      : "Save",
        "load_pl"      : "Load",
        "mini_on"      : "Mini",
        "mini_off"     : "Expand",
        "tray_btn"     : "To Tray",
        "search"       : "Search...",
        "vol"          : "Vol",
        "mute"         : "Mute",
        "play"         : "Play",
        "pause"        : "Pause",
        "stop"         : "Stop",
        "shuffle_on"   : "Shuffle",
        "shuffle_off"  : "Ordered",
        "repeat_on"    : "Loop: On",
        "repeat_off"   : "Loop: Off",
        "waiting"      : "Waiting for Music...",
        "loaded"       : "{} songs loaded",
        "playing"      : "🎵 ",
        "theme"        : "Theme",
        "lang"         : "Lang",
        "sleep_off"    : "Sleep: Off",
        "sleep_on"     : "Sleep: {} min",
        "tray_show"    : "Show Interface",
        "tray_quit"    : "Quit",
        "crossfade_on" : "Crossfade: On",
        "crossfade_off": "Crossfade: Off",
        "sort_az"      : "A→Z",
        "sort_za"      : "Z→A",
        "sort_new"     : "New→Old",
        "sort_old"     : "Old→New",
        "sort_manual"  : "Manual",
        "unknown_art"  : "Unknown Artist",
        "unknown_alb"  : "Unknown Album",
        "waiting_song" : "Waiting for Song",
        "drag_hint"    : "Drag & Drop to Add",
        "saved"        : "Saved: {}",
        "prev"         : "Prev",
        "next"         : "Next",
        "restart"      : "Restart",
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Temalar
# ─────────────────────────────────────────────────────────────────────────────
_BASE = """
QWidget      {{ background-color:{bg};  color:{fg}; font-family:{ff}; font-size:13px; }}
QPushButton  {{ background-color:{btn}; border:1px solid {brd}; border-radius:6px;
               padding:5px 9px; font-weight:bold; color:{fg}; }}
QPushButton:hover {{ background-color:{bhv}; color:{hfg}; }}
QListWidget  {{ background-color:{lst}; border:1px solid {brd}; border-radius:6px; color:{fg}; }}
QListWidget::item        {{ padding:2px 4px; }}
QListWidget::item:hover  {{ background-color:{bhv}; }}
QListWidget::item:selected {{ background-color:{acc}; color:{afg}; border-radius:3px; }}
QLineEdit,QComboBox {{ background-color:{inp}; border:1px solid {brd};
                       padding:5px; border-radius:4px; color:{fg}; }}
QComboBox::drop-down {{ border:0; }}
QSlider::groove:horizontal {{ border:1px solid {brd}; height:6px; background:{inp}; border-radius:3px; }}
QSlider::sub-page:horizontal {{ background:{acc}; border-radius:3px; }}
QSlider::handle:horizontal  {{ background:{hnd}; border:2px solid {acc}; width:14px; margin:-4px 0; border-radius:7px; }}
#lblKapak {{ background-color:{lst}; border-radius:10px; border:1px solid {brd}; }}
"""

_TERM_EXTRA = """
QPushButton  {{ border-radius:0; border:1px solid {brd}; }}
QPushButton:hover {{ background-color:{bhv}; color:{hfg}; border-color:{hfg}; }}
QListWidget  {{ border-radius:0; }}
QListWidget::item:selected {{ border-radius:0; }}
QLineEdit,QComboBox {{ border-radius:0; }}
QSlider::groove:horizontal {{ border-radius:0; height:4px; }}
QSlider::handle:horizontal {{ border-radius:0; width:10px; margin:-4px 0; }}
#lblKapak {{ border-radius:0; border:2px solid {brd}; }}
"""

_RUSTIC_EXTRA = """
QWidget      {{ font-family:'Georgia','Times New Roman',serif; }}
QPushButton  {{ border-radius:3px; border:2px solid {brd2}; border-bottom:3px solid {brd2}; }}
QPushButton:hover {{ border-color:{acc}; }}
QPushButton:pressed {{ border-bottom-width:1px; margin-top:2px; }}
QListWidget  {{ border:2px solid {brd2}; border-radius:4px; }}
QListWidget::item:selected {{ border-radius:2px; }}
QSlider::groove:horizontal {{ height:8px; border-radius:4px; }}
QSlider::handle:horizontal {{ width:16px; margin:-5px 0; border-radius:8px; border:2px solid {brd2}; }}
#lblKapak {{ border:3px solid {brd2}; border-radius:6px; }}
"""

def _t(bg, fg, btn, brd, bhv, hfg, lst, acc, afg, inp, hnd, ff="'Segoe UI',Arial"):
    return _BASE.format(bg=bg,fg=fg,btn=btn,brd=brd,bhv=bhv,hfg=hfg,
                        lst=lst,acc=acc,afg=afg,inp=inp,hnd=hnd,ff=ff)

def _tt(bg, fg, btn, brd, bhv, hfg, lst, acc, afg, inp, hnd, ff):
    return (_t(bg,fg,btn,brd,bhv,hfg,lst,acc,afg,inp,hnd,ff)
            + _TERM_EXTRA.format(brd=brd, bhv=bhv, hfg=hfg))

def _tr(bg, fg, btn, brd, brd2, bhv, hfg, lst, acc, afg, inp, hnd):
    return (_t(bg,fg,btn,brd,bhv,hfg,lst,acc,afg,inp,hnd)
            + _RUSTIC_EXTRA.format(brd2=brd2, acc=acc))

THEMES = {
    "light":
        _t("#f5f5f7","#1d1d1f","#e8e8ed","#d2d2d7","#c8c8cc","#1d1d1f",
           "#ffffff","#0071e3","#ffffff","#ffffff","#ffffff"),

    "dark":
        _t("#1c1c1e","#f5f5f7","#2c2c2e","#3a3a3c","#48484a","#f5f5f7",
           "#000000","#0a84ff","#ffffff","#2c2c2e","#ffffff"),

    "cyberpunk":
        _t("#0b0813","#00ff66","#1a103c","#ff007f","#ff007f","#0b0813",
           "#120e24","#ff007f","#ffffff","#1a103c","#00ffff"),

    "amber-crt":
        _tt("#0e0700","#e8a000","#0e0700","#c47a00","#271500","#ffc107",
            "#080400","#c47a00","#0e0700","#0e0700","#e8a000",
            "'Courier New',Consolas,monospace"),

    "rustic":
        _tr("#2c1f0e","#e8d5b0","#3d2b14","#6b4c2a","#8b6340","#1a0e00","#f5e6c8",
            "#221508","#c8853a","#f5e6c8","#f0e0c0","#3d2b14"),

    "parchment":
        _tr("#f2e8d0","#3a2a12","#e8dabb","#b89860","#8b6340","#2a1a08","#faf4e4",
            "#f2e8d0","#8b4513","#faf4e4","#faf4e4","#e8dabb"),

    "forest":
        _t("#1a2614","#c8e6b0","#243318","#3d5c28","#4a7030","#e8f5d8",
           "#111c0d","#5a9e32","#0e1a0a","#1e2e18","#c8e6b0"),

    "midnight-ink":
        _t("#0d0d1a","#c8c0e8","#14142b","#2a2850","#2e2c60","#e8e4ff",
           "#070714","#7c6fc0","#f0eeff","#14142b","#c8c0e8"),
}

# ─────────────────────────────────────────────────────────────────────────────
# Equalizer görselleştirici
# ─────────────────────────────────────────────────────────────────────────────
class EqualizerWidget(QWidget):
    BAR_COUNT = 16
    BAR_GAP   = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setMinimumWidth(100)
        self._heights   = [0.0] * self.BAR_COUNT
        self._targets   = [0.0] * self.BAR_COUNT
        self._aktif     = False
        self._acc_renk  = "#0a84ff" 

        self._timer = QTimer(self)
        self._timer.setInterval(40)  
        self._timer.timeout.connect(self._adim)
        self._timer.start()

        self._hedef_timer = QTimer(self)
        self._hedef_timer.setInterval(120)
        self._hedef_timer.timeout.connect(self._yeni_hedefler)
        self._hedef_timer.start()

    def set_aktif(self, aktif: bool):
        self._aktif = aktif

    def set_renk(self, renk: str):
        self._acc_renk = renk
        self.update()

    def _yeni_hedefler(self):
        if not self._aktif:
            self._targets = [0.0] * self.BAR_COUNT
            return
        import random
        for i in range(self.BAR_COUNT):
            center = self.BAR_COUNT / 2
            dist   = abs(i - center) / center
            peak   = max(0.1, 1.0 - dist * 0.5)
            base   = random.random() * peak
            if random.random() < 0.12:
                base = min(1.0, base + random.uniform(0.3, 0.6))
            self._targets[i] = base

    def _adim(self):
        degisti = False
        for i in range(self.BAR_COUNT):
            diff = self._targets[i] - self._heights[i]
            if abs(diff) > 0.005:
                hiz = 0.18 if diff > 0 else 0.08
                self._heights[i] += diff * hiz
                degisti = True
            else:
                self._heights[i] = self._targets[i]
        if degisti:
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        n = self.BAR_COUNT
        bar_w = max(2, (w - (n - 1) * self.BAR_GAP) / n)

        base_color = QColor(self._acc_renk)

        for i in range(n):
            x     = int(i * (bar_w + self.BAR_GAP))
            bar_h = max(2, int(self._heights[i] * (h - 2)))
            y     = h - bar_h

            grad = QLinearGradient(x, h, x, y)
            grad.setColorAt(0.0, base_color)
            lighter = base_color.lighter(170)
            lighter.setAlpha(220)
            grad.setColorAt(1.0, lighter)

            p.fillRect(int(x), y, int(bar_w), bar_h, QBrush(grad))

            peak_color = QColor(255, 255, 255, 160)
            p.fillRect(int(x), y, int(bar_w), 2, peak_color)

        p.end()

# ─────────────────────────────────────────────────────────────────────────────
# Sürükle-bırak destekli liste
# ─────────────────────────────────────────────────────────────────────────────
class SurukleBirakListe(QListWidget):
    def __init__(self, parent_player):
        super().__init__()
        self.parent_player = parent_player
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAcceptDrops(True)
        self.model().rowsMoved.connect(self._ic_siralama_degisti)

    def _ic_siralama_degisti(self, parent, start, end, dest, dest_row):
        self.parent_player._liste_widget_senkronize()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.parent_player._harici_drop(event.mimeData().urls())
        else:
            super().dropEvent(event)

# ─────────────────────────────────────────────────────────────────────────────
class PremiumPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.ayarlar          = ayarlari_yukle()
        self.sarki_listesi    = []
        self.mevcut_cihazlar  = []
        self.gecerli_klasor   = self.ayarlar.get("son_klasor", "")
        self.mevcut_indeks    = -1
        self.restore_konum    = 0
        self.manuel_siralama  = False

        self.karisik_cal = False
        self.tekrarla    = False
        self.mini_mod    = False
        self.sessiz_mi   = False
        self.onceki_ses  = 50

        # ── Player ──────────────────────────────────────────────
        self.player       = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self._hedef_volume = 0.5
        self.audio_output.setVolume(self._hedef_volume)

        self.player.mediaStatusChanged.connect(self._durum_kontrolu)
        self.player.positionChanged.connect(self._zaman_guncelle)
        self.player.durationChanged.connect(self._sure_guncelle)
        self.player.errorOccurred.connect(lambda *a: self.player.stop())

        # ── Crossfade / Fade ─────────────────────────────────────
        self._fade_in_aktif            = False
        self._fade_out_aktif           = False
        self._crossfade_tetiklendi     = False
        self._sonraki_indeks_bekleyen  = None
        self._fade_adim_boyutu         = 0.0

        self._fade_timer = QTimer(self)
        self._fade_timer.setInterval(FADE_ADIM_MS)
        self._fade_timer.timeout.connect(self._fade_adim)

        # ── Uyku ────────────────────────────────────────────────
        self.uyku_suresi = 0
        self._uyku_timer = QTimer(self)
        self._uyku_timer.timeout.connect(self._uyku_gerisayim)

        # ── Başlık kaydırma ─────────────────────────────────────
        self._durum_metni      = ""
        self._kaydirma_idx     = 0
        self._scroll_timer     = QTimer(self)
        self._scroll_timer.timeout.connect(self._yazi_kaydir)
        self._scroll_timer.start(280)

        self.slider_aktif_mi = False

        self._arayuzu_kur()
        self._klavye_kisayollarini_bagla()
        self._tepsi_kur()

        self._cihaz_izleyici = QMediaDevices()
        self._cihaz_izleyici.audioOutputsChanged.connect(self._ses_aygitlarini_guncelle)
        self._ses_aygitlarini_guncelle()
        self.arayuzu_guncelle()
        self._hafizadan_yukle()

    # ═══════════════════════════════════════════════════════════════
    # Fade / Crossfade
    # ═══════════════════════════════════════════════════════════════
    def _fade_adim(self):
        mevcut = self.audio_output.volume()

        if self._fade_out_aktif:
            yeni = max(0.0, mevcut - self._fade_adim_boyutu)
            self.audio_output.setVolume(yeni)
            if yeni <= 0.001:
                self._fade_out_aktif = False
                self.player.stop()
                if self._sonraki_indeks_bekleyen is not None:
                    self.mevcut_indeks = self._sonraki_indeks_bekleyen
                    self._sonraki_indeks_bekleyen = None
                    self._baslat_ve_fade_in()
                else:
                    self.audio_output.setVolume(self._hedef_volume)
                    self._fade_timer.stop()
            return

        if self._fade_in_aktif:
            yeni = min(self._hedef_volume, mevcut + self._fade_adim_boyutu)
            self.audio_output.setVolume(yeni)
            if yeni >= self._hedef_volume - 0.001:
                self.audio_output.setVolume(self._hedef_volume)
                self._fade_in_aktif = False
                self._fade_timer.stop()

    def _fade_adim_hesapla(self):
        adim_sayisi = FADE_SURE_MS / FADE_ADIM_MS
        self._fade_adim_boyutu = max(self._hedef_volume / adim_sayisi, 0.005)

    def _fade_out_ve_gec(self, hedef_indeks):
        self._fade_adim_hesapla()
        self._sonraki_indeks_bekleyen = hedef_indeks
        self._fade_in_aktif  = False
        self._fade_out_aktif = True
        self._fade_timer.start()

    def _baslat_ve_fade_in(self):
        if not self.sarki_listesi or not (0 <= self.mevcut_indeks < len(self.sarki_listesi)):
            return
        self._fade_adim_hesapla()
        sarki = self.sarki_listesi[self.mevcut_indeks]
        yol   = self._tam_yol(sarki)
        self._sarki_bilgi_goster(yol, os.path.basename(sarki))
        self._liste_secimi_guncelle()
        self.audio_output.setVolume(0.0)
        self.player.setSource(QUrl.fromLocalFile(yol))
        self.player.play()
        
        self.set_durum(LANG[self.ayarlar["dil"]]["playing"] + os.path.basename(sarki), "#34c759")
        self._fade_in_aktif  = True
        self._fade_out_aktif = False
        self._crossfade_tetiklendi = False
        self._fade_timer.start()
        self.equalizer.set_aktif(True)
        self.arayuzu_guncelle()

    def _crossfade_kontrol(self, position):
        if not self.ayarlar.get("crossfade", True): return
        if self._fade_out_aktif or self._crossfade_tetiklendi: return
        duration = self.player.duration()
        if duration <= 0: return
        if (duration - position) <= CROSSFADE_MS:
            self._crossfade_tetiklendi = True
            hedef = self._sonraki_indeks_hesapla()
            self._fade_out_ve_gec(hedef)

    def _sonraki_indeks_hesapla(self):
        if self.tekrarla: return self.mevcut_indeks
        if self.karisik_cal and len(self.sarki_listesi) > 1:
            h = self.mevcut_indeks
            while h == self.mevcut_indeks:
                h = random.randint(0, len(self.sarki_listesi) - 1)
            return h
        return (self.mevcut_indeks + 1) % len(self.sarki_listesi)

    def _pencere_boyut_kilitle(self, w, h):
        self.setMinimumSize(w, h)
        self.setMaximumSize(w, h)
        self.resize(w, h)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def dropEvent(self, event):
        self._harici_drop(event.mimeData().urls())

    def _harici_drop(self, urls):
        eklendi = 0
        for url in urls:
            yol = url.toLocalFile()
            if os.path.isdir(yol):
                dosyalar = sorted([f for f in os.listdir(yol)
                                   if f.lower().endswith(DESTEKLENEN_FORMAT)])
                if dosyalar:
                    self.gecerli_klasor = yol
                    self.sarki_listesi  = dosyalar
                    self.mevcut_indeks  = -1
                    self.player.stop()
                    self._fade_durdur()
                    eklendi = len(dosyalar)
                break
            elif os.path.isfile(yol) and yol.lower().endswith(DESTEKLENEN_FORMAT):
                if not self.sarki_listesi:
                    self.gecerli_klasor = os.path.dirname(yol)

                if self.gecerli_klasor and not os.path.isabs(self.sarki_listesi[0] if self.sarki_listesi else ""):
                    if os.path.dirname(yol) != self.gecerli_klasor:
                        self.sarki_listesi = [
                            os.path.join(self.gecerli_klasor, s) for s in self.sarki_listesi
                        ]
                        self.gecerli_klasor = ""

                eklenecek = yol if not self.gecerli_klasor else os.path.basename(yol)
                if eklenecek not in self.sarki_listesi:
                    self.sarki_listesi.append(eklenecek)
                    eklendi += 1

        if eklendi:
            self.manuel_siralama = False
            self._listeyi_yenile()
            self.set_durum(LANG[self.ayarlar["dil"]]["loaded"].format(len(self.sarki_listesi)), "#0a84ff")

    # ═══════════════════════════════════════════════════════════════
    # Arayüz kurulum
    # ═══════════════════════════════════════════════════════════════
    def _arayuzu_kur(self):
        self.setAcceptDrops(True)
        self._pencere_boyut_kilitle(WIN_W, WIN_H)
        try: self.setWindowIcon(QIcon(os.path.join(ana_klasoru_bul(), "muzik.ico")))
        except: pass

        ana = QVBoxLayout(self)
        ana.setSpacing(6)
        ana.setContentsMargins(8, 8, 8, 8)

        # ── Üst bar ──────────────────────────────────────────────
        ust = QHBoxLayout()
        self.btn_mini       = QPushButton(); self.btn_mini.clicked.connect(self._mini_degistir)
        self.btn_tepsi      = QPushButton(); self.btn_tepsi.clicked.connect(self._tepsiye_kucult)
        
        # ÇÖZÜM 2: Üst barın titrememesi ve genişlememesi için metin kısıtlanıyor.
        self.lbl_durum      = QLabel()
        self.lbl_durum.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lbl_durum.setMinimumWidth(50)
        
        self.btn_uyku       = QPushButton(); self.btn_uyku.clicked.connect(self._uyku_ayarla)
        self.btn_crossfade  = QPushButton(); self.btn_crossfade.clicked.connect(self._crossfade_toggle)
        self.btn_tema       = QPushButton(); self.btn_tema.clicked.connect(self._tema_degistir)
        self.btn_dil        = QPushButton(); self.btn_dil.clicked.connect(self._dil_degistir)
        for btn in (self.btn_mini, self.btn_tepsi, self.btn_uyku,
                    self.btn_crossfade, self.btn_tema, self.btn_dil):
            btn.setFixedHeight(30)
        for w in (self.btn_mini, self.btn_tepsi):
            ust.addWidget(w)
        ust.addWidget(self.lbl_durum, stretch=1)
        for w in (self.btn_uyku, self.btn_crossfade, self.btn_tema, self.btn_dil):
            ust.addWidget(w)
        ana.addLayout(ust)

        # ── Orta bölüm ───────────────────────────────────────────
        orta = QHBoxLayout()

        # Sol panel
        sol_w = QWidget(); sol_w.setFixedWidth(232)
        sol   = QVBoxLayout(sol_w)
        sol.setContentsMargins(0, 0, 4, 0); sol.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.lbl_kapak = QLabel()
        self.lbl_kapak.setObjectName("lblKapak")
        self.lbl_kapak.setFixedSize(220, 220)
        self.lbl_kapak.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sol.addWidget(self.lbl_kapak)

        bilgi = QFrame(); bilgi.setFixedWidth(220)
        bl = QVBoxLayout(bilgi); bl.setContentsMargins(0,8,0,0); bl.setSpacing(4)

        self.lbl_baslik  = QLabel("Şarkı Bekleniyor")
        self.lbl_baslik.setWordWrap(True)
        self.lbl_baslik.setStyleSheet("font-size:15px;font-weight:bold;")
        self.lbl_baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_sanatci = QLabel("Sürükle & Bırak ile Ekle")
        self.lbl_sanatci.setWordWrap(True)
        self.lbl_sanatci.setStyleSheet("font-size:13px;color:#888;")
        self.lbl_sanatci.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_album   = QLabel("-")
        self.lbl_album.setWordWrap(True)
        self.lbl_album.setStyleSheet("font-size:12px;font-style:italic;color:#888;")
        self.lbl_album.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_kalite  = QLabel("")
        self.lbl_kalite.setStyleSheet("font-size:11px;font-weight:bold;color:#0a84ff;")
        self.lbl_kalite.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for w in (self.lbl_baslik, self.lbl_sanatci, self.lbl_album, self.lbl_kalite):
            bl.addWidget(w)
        sol.addWidget(bilgi)

        self.equalizer = EqualizerWidget()
        sol.addWidget(self.equalizer)

        orta.addWidget(sol_w)

        # Sağ panel — liste
        self.sag_widget = QWidget()
        sag = QVBoxLayout(self.sag_widget); sag.setContentsMargins(0,0,0,0); sag.setSpacing(4)

        arac = QHBoxLayout()
        self.btn_klasor  = QPushButton(); self.btn_klasor.clicked.connect(self._klasor_sec)
        self.btn_kaydet  = QPushButton(); self.btn_kaydet.clicked.connect(self._playlist_kaydet)
        self.btn_yukle   = QPushButton(); self.btn_yukle.clicked.connect(self._playlist_yukle)
        self.combo_sirala = QComboBox()
        self.combo_sirala.currentIndexChanged.connect(self._siralama_degisti)
        for w in (self.btn_klasor, self.btn_kaydet, self.btn_yukle, self.combo_sirala):
            arac.addWidget(w)
        sag.addLayout(arac)

        self.arama_kutusu = QLineEdit()
        self.arama_kutusu.textChanged.connect(self._listeyi_filtrele)
        sag.addWidget(self.arama_kutusu)

        self.liste_kutusu = SurukleBirakListe(self)
        self.liste_kutusu.itemDoubleClicked.connect(self._listeden_sec)
        sag.addWidget(self.liste_kutusu)

        orta.addWidget(self.sag_widget, stretch=1)
        ana.addLayout(orta)

        # ── Zaman slider ─────────────────────────────────────────
        zbar = QHBoxLayout()
        self.zaman_slider = QSlider(Qt.Orientation.Horizontal)
        self.zaman_slider.sliderPressed.connect(lambda: setattr(self, 'slider_aktif_mi', True))
        self.zaman_slider.sliderReleased.connect(self._slider_birakildi)
        self.lbl_zaman = QLabel("00:00 / 00:00")
        zbar.addWidget(self.zaman_slider)
        zbar.addWidget(self.lbl_zaman)
        ana.addLayout(zbar)

        # ── Kontrol butonları ─────────────────────────────────────
        bbar = QHBoxLayout()
        self.btn_karistir = QPushButton(); self.btn_karistir.clicked.connect(self._karistir_toggle)
        self.btn_onceki   = QPushButton(); self.btn_onceki.clicked.connect(self.onceki_sarki)
        self.btn_cal      = QPushButton(); self.btn_cal.clicked.connect(self._oynat_tikla) 
        self.btn_duraklat = QPushButton(); self.btn_duraklat.clicked.connect(self.duraklat_devam) 
        self.btn_durdur   = QPushButton(); self.btn_durdur.clicked.connect(self.durdur)
        self.btn_sonraki  = QPushButton(); self.btn_sonraki.clicked.connect(self.sonraki_sarki)
        self.btn_tekrarla = QPushButton(); self.btn_tekrarla.clicked.connect(self._tekrarla_toggle)
        self.btn_ses_ikon = QPushButton(); self.btn_ses_ikon.clicked.connect(self._sustur_toggle)

        for btn in (self.btn_karistir, self.btn_onceki, self.btn_cal,
                    self.btn_duraklat, self.btn_durdur, self.btn_sonraki, self.btn_tekrarla, self.btn_ses_ikon):
            btn.setFixedHeight(34)

        self.ses_slider = QSlider(Qt.Orientation.Horizontal)
        self.ses_slider.setFixedWidth(90)
        self.ses_slider.setRange(0, 100)
        self.ses_slider.setValue(50)
        self.ses_slider.valueChanged.connect(self._ses_degisti)

        self.combo_ses = QComboBox()
        self.combo_ses.setFixedWidth(145)
        self.combo_ses.currentIndexChanged.connect(self._ses_aygiti_degistir)

        # 1. Grup: Oynatma kontrolleri
        for w in (self.btn_karistir, self.btn_onceki, self.btn_duraklat,
                  self.btn_durdur, self.btn_sonraki, self.btn_cal,
                  self.btn_tekrarla):
            bbar.addWidget(w)

        # Esneme payı (stretch)
        bbar.addStretch()

        # 2. Grup: Ses ayarları
        bbar.addWidget(self.btn_ses_ikon)
        bbar.addWidget(self.ses_slider)
        bbar.addWidget(self.combo_ses)
        ana.addLayout(bbar)

    # ═══════════════════════════════════════════════════════════════
    # Ses & Cihaz
    # ═══════════════════════════════════════════════════════════════
    def _ses_aygitlarini_guncelle(self):
        self.combo_ses.blockSignals(True)
        self.combo_ses.clear()
        self.mevcut_cihazlar = QMediaDevices.audioOutputs()
        varsayilan = QMediaDevices.defaultAudioOutput()
        for c in self.mevcut_cihazlar:
            self.combo_ses.addItem(c.description())
        kayitli = self.ayarlar.get("ses_aygiti", "")
        secildi = False
        for i, c in enumerate(self.mevcut_cihazlar):
            if c.description() == kayitli:
                self.combo_ses.setCurrentIndex(i)
                self.audio_output.setDevice(c); secildi = True; break
        if not secildi:
            for i, c in enumerate(self.mevcut_cihazlar):
                if c.description() == varsayilan.description():
                    self.combo_ses.setCurrentIndex(i)
                    self.audio_output.setDevice(c); break
        self.combo_ses.blockSignals(False)

    def _ses_aygiti_degistir(self, idx):
        if 0 <= idx < len(self.mevcut_cihazlar):
            c = self.mevcut_cihazlar[idx]
            self.audio_output.setDevice(c)
            self.ayarlar["ses_aygiti"] = c.description()
            ayarlari_kaydet(self.ayarlar)

    def _ses_degisti(self, v):
        self._hedef_volume = v / 100.0
        if self.sessiz_mi and v > 0:
            self.sessiz_mi = False
            self.arayuzu_guncelle()
        if not (self._fade_in_aktif or self._fade_out_aktif):
            self.audio_output.setVolume(self._hedef_volume)

    def _sustur_toggle(self):
        self.sessiz_mi = not self.sessiz_mi
        if self.sessiz_mi:
            self.onceki_ses = self.ses_slider.value()
            self.ses_slider.setValue(0)
        else:
            self.ses_slider.setValue(self.onceki_ses if self.onceki_ses > 0 else 50)
        self.arayuzu_guncelle()

    # ═══════════════════════════════════════════════════════════════
    # Oynatma
    # ═══════════════════════════════════════════════════════════════
    def _tam_yol(self, sarki):
        if os.path.isabs(sarki): return sarki
        return os.path.join(self.gecerli_klasor, sarki)

    def _fade_durdur(self):
        self._fade_timer.stop()
        self._fade_in_aktif = self._fade_out_aktif = False
        self._crossfade_tetiklendi = False
        self._sonraki_indeks_bekleyen = None
        self.audio_output.setVolume(self._hedef_volume)

    def _oynat_tikla(self):
        self.sarkiyi_baslat(True)

    def sarkiyi_baslat(self, otomatik=True):
        if not self.sarki_listesi or not (0 <= self.mevcut_indeks < len(self.sarki_listesi)):
            return
        self._fade_durdur()
        self.player.stop()
        self.player.setSource(QUrl())

        sarki    = self.sarki_listesi[self.mevcut_indeks]
        yol      = self._tam_yol(sarki)
        dosya_adi = os.path.basename(sarki)

        self._sarki_bilgi_goster(yol, dosya_adi)
        self._liste_secimi_guncelle()

        if otomatik:
            self._fade_adim_hesapla()
            self.audio_output.setVolume(0.0)
            self.player.setSource(QUrl.fromLocalFile(yol))
            self.player.play()
            self.set_durum(LANG[self.ayarlar["dil"]]["playing"] + dosya_adi, "#34c759")
            self._fade_in_aktif = True
            self._crossfade_tetiklendi = False
            self._fade_timer.start()
            self.equalizer.set_aktif(True)
        else:
            self.player.setSource(QUrl.fromLocalFile(yol))
            self.audio_output.setVolume(self._hedef_volume)
            self.equalizer.set_aktif(False)
        self.arayuzu_guncelle()

    def duraklat_devam(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.equalizer.set_aktif(False)
        elif self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self.player.play()
            self.equalizer.set_aktif(True)
        elif self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
             if self.player.source().isValid():
                 self._fade_adim_hesapla()
                 self.audio_output.setVolume(0.0)
                 self.player.play()
                 self.set_durum(LANG[self.ayarlar["dil"]]["playing"] + os.path.basename(self.sarki_listesi[self.mevcut_indeks]), "#34c759")
                 self._fade_in_aktif = True
                 self._crossfade_tetiklendi = False
                 self._fade_timer.start()
                 self.equalizer.set_aktif(True)
             else:
                 self.sarkiyi_baslat(True)
             
        self.arayuzu_guncelle()

    def durdur(self):
        self._fade_durdur()
        self.player.stop()
        self.zaman_slider.setValue(0)
        self.lbl_zaman.setText("00:00 / 00:00")
        self.equalizer.set_aktif(False)
        self.arayuzu_guncelle()

    def sonraki_sarki(self):
        if not self.sarki_listesi: return
        self.mevcut_indeks = self._sonraki_indeks_hesapla()
        self.sarkiyi_baslat()

    def onceki_sarki(self):
        if not self.sarki_listesi: return
        self.mevcut_indeks = (self.mevcut_indeks - 1) % len(self.sarki_listesi)
        self.sarkiyi_baslat()

    # ═══════════════════════════════════════════════════════════════
    # Media durum / zaman
    # ═══════════════════════════════════════════════════════════════
    def _durum_kontrolu(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self._fade_out_aktif: return
            if self.tekrarla: self.sarkiyi_baslat()
            else: self.sonraki_sarki()
        elif status in (QMediaPlayer.MediaStatus.LoadedMedia,
                        QMediaPlayer.MediaStatus.BufferedMedia):
            if getattr(self, 'restore_konum', 0) > 0:
                self.player.setPosition(self.restore_konum)
                self.restore_konum = 0

    def _sure_guncelle(self, d): self.zaman_slider.setRange(0, d)

    def _zaman_guncelle(self, pos):
        if not self.slider_aktif_mi:
            self.zaman_slider.setValue(pos)
        dur = max(self.player.duration(), 0); pos = max(pos, 0)
        g, t = pos // 1000, dur // 1000
        self.lbl_zaman.setText(f"{g//60:02d}:{g%60:02d} / {t//60:02d}:{t%60:02d}")
        self._crossfade_kontrol(pos)

    def _slider_birakildi(self):
        self.slider_aktif_mi = False
        self.player.setPosition(self.zaman_slider.value())

    # ═══════════════════════════════════════════════════════════════
    # Liste yönetimi
    # ═══════════════════════════════════════════════════════════════
    def _liste_secimi_guncelle(self):
        if not (0 <= self.mevcut_indeks < len(self.sarki_listesi)): return
        adi = os.path.basename(self.sarki_listesi[self.mevcut_indeks])
        for i in range(self.liste_kutusu.count()):
            if self.liste_kutusu.item(i).text() == adi:
                self.liste_kutusu.setCurrentRow(i); return

    def _listeyi_filtrele(self):
        arama = self.arama_kutusu.text().lower()
        self.liste_kutusu.setUpdatesEnabled(False)
        self.liste_kutusu.blockSignals(True)
        self.liste_kutusu.clear()
        for sarki in self.sarki_listesi:
            if arama in os.path.basename(sarki).lower():
                self.liste_kutusu.addItem(os.path.basename(sarki))
        self._liste_secimi_guncelle()
        self.liste_kutusu.blockSignals(False)
        self.liste_kutusu.setUpdatesEnabled(True)

    def _listeyi_yenile(self):
        if not self.manuel_siralama:
            self._sirala_uygula()
        else:
            self._listeyi_filtrele()

    def _siralama_degisti(self, idx):
        self.manuel_siralama = (idx == 4) 
        if not self.manuel_siralama:
            self._sirala_uygula()

    def _sirala_uygula(self):
        if not self.sarki_listesi: return
        suanki = (self.sarki_listesi[self.mevcut_indeks]
                  if 0 <= self.mevcut_indeks < len(self.sarki_listesi) else None)
        idx = self.combo_sirala.currentIndex()
        key = lambda x: os.path.basename(x).lower()
        if   idx == 0: self.sarki_listesi.sort(key=key)
        elif idx == 1: self.sarki_listesi.sort(key=key, reverse=True)
        elif idx == 2: self.sarki_listesi.sort(
            key=lambda x: os.path.getmtime(self._tam_yol(x)), reverse=True)
        elif idx == 3: self.sarki_listesi.sort(
            key=lambda x: os.path.getmtime(self._tam_yol(x)))
        if suanki in self.sarki_listesi:
            self.mevcut_indeks = self.sarki_listesi.index(suanki)
        self._listeyi_filtrele()

    def _liste_widget_senkronize(self):
        arama = self.arama_kutusu.text().lower()
        if arama:
            return 
        suanki = (self.sarki_listesi[self.mevcut_indeks]
                  if 0 <= self.mevcut_indeks < len(self.sarki_listesi) else None)
        yeni_liste = []
        basename_to_full = {os.path.basename(s): s for s in self.sarki_listesi}
        for i in range(self.liste_kutusu.count()):
            adi = self.liste_kutusu.item(i).text()
            if adi in basename_to_full:
                yeni_liste.append(basename_to_full[adi])
        if len(yeni_liste) == len(self.sarki_listesi):
            self.sarki_listesi = yeni_liste
            self.manuel_siralama = True
            self.combo_sirala.blockSignals(True)
            self.combo_sirala.setCurrentIndex(4)
            self.combo_sirala.blockSignals(False)
        if suanki and suanki in self.sarki_listesi:
            self.mevcut_indeks = self.sarki_listesi.index(suanki)

    def _listeden_sec(self, item):
        adi = item.text()
        for i, sarki in enumerate(self.sarki_listesi):
            if os.path.basename(sarki) == adi:
                self.mevcut_indeks = i; break
        self.sarkiyi_baslat()

    # ═══════════════════════════════════════════════════════════════
    # Klasör / Playlist
    # ═══════════════════════════════════════════════════════════════
    def _klasor_sec(self):
        k = QFileDialog.getExistingDirectory(self, LANG[self.ayarlar["dil"]]["folder"])
        if k:
            self.gecerli_klasor = k
            self.sarki_listesi  = [f for f in os.listdir(k) if f.lower().endswith(DESTEKLENEN_FORMAT)]
            self.mevcut_indeks  = -1
            self.player.stop(); self._fade_durdur()
            self.manuel_siralama = False
            self._listeyi_yenile()
            self.set_durum(LANG[self.ayarlar["dil"]]["loaded"].format(len(self.sarki_listesi)), "#0a84ff")

    def _playlist_kaydet(self):
        if not self.sarki_listesi: return
        dosya, _ = QFileDialog.getSaveFileName(
            self, LANG[self.ayarlar["dil"]]["save_pl"], self.gecerli_klasor, "Playlist (*.m3u)")
        if dosya:
            with open(dosya, "w", encoding="utf-8") as f:
                for s in self.sarki_listesi: f.write(self._tam_yol(s) + "\n")
            self.set_durum(LANG[self.ayarlar["dil"]]["saved"].format(os.path.basename(dosya)), "#34c759")

    def _playlist_yukle(self):
        dosya, _ = QFileDialog.getOpenFileName(
            self, LANG[self.ayarlar["dil"]]["load_pl"], "", "Playlist (*.m3u)")
        if dosya:
            with open(dosya, "r", encoding="utf-8") as f: satirlar = f.readlines()
            yeni, ilk = [], ""
            for satir in satirlar:
                satir = satir.strip()
                if satir and not satir.startswith("#") and os.path.exists(satir):
                    if not ilk: ilk = os.path.dirname(satir)
                    if os.path.dirname(satir) == ilk: yeni.append(os.path.basename(satir))
            if yeni:
                self.gecerli_klasor = ilk
                self.sarki_listesi  = yeni
                self.mevcut_indeks  = -1
                self.player.stop()
                self.manuel_siralama = False
                self._listeyi_filtrele()
                self.set_durum(LANG[self.ayarlar["dil"]]["loaded"].format(len(yeni)), "#0a84ff")

    # ═══════════════════════════════════════════════════════════════
    # Şarkı metadata
    # ═══════════════════════════════════════════════════════════════
    def _sarki_bilgi_goster(self, yol, dosya_adi):
        d = LANG[self.ayarlar["dil"]]
        baslik, sanatci, album, kalite = dosya_adi, d["unknown_art"], d["unknown_alb"], ""
        kapak_bulundu = False

        if MUTAGEN_VAR:
            try:
                audio = MutagenFile(yol)
                if audio:
                    if hasattr(audio.info, 'bitrate') and audio.info.bitrate:
                        kalite = f"{audio.info.bitrate // 1000} kbps"
                    tags = getattr(audio, 'tags', None)
                    if tags:
                        def _tag(*keys):
                            for k in keys:
                                if k in tags:
                                    v = tags[k]
                                    return str(v[0] if isinstance(v, list) else v)
                            return None
                        baslik  = _tag('TIT2','title','©nam') or baslik
                        sanatci = _tag('TPE1','artist','©ART') or sanatci
                        album   = _tag('TALB','album','©alb') or album
                        for key in tags.keys():
                            try:
                                if key.startswith('APIC'): data = tags[key].data
                                elif key == 'covr':        data = bytes(tags[key][0])
                                else: continue
                                px = QPixmap()
                                if px.loadFromData(data):
                                    self.lbl_kapak.setPixmap(px.scaled(
                                        220, 220,
                                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                        Qt.TransformationMode.SmoothTransformation))
                                    kapak_bulundu = True
                                break
                            except: continue
            except: pass

        if not kapak_bulundu:
            self.lbl_kapak.clear()
            fg_renk = getattr(self, '_guncel_fg', "#ffffff")
            cd_ikon = _ikon("fa5s.compact-disc", fg_renk)
            if QTA and not cd_ikon.isNull():
                self.lbl_kapak.setPixmap(cd_ikon.pixmap(120, 120))
            else:
                self.lbl_kapak.setText("O")

        self.lbl_baslik.setText(baslik)
        self.lbl_sanatci.setText(sanatci)
        self.lbl_album.setText(album)
        self.lbl_kalite.setText(kalite)

    # ═══════════════════════════════════════════════════════════════
    # Tray / Mini / Kapat
    # ═══════════════════════════════════════════════════════════════
    def _tepsi_kur(self):
        self.tray = QSystemTrayIcon(self)
        ikon = QIcon(os.path.join(ana_klasoru_bul(), "muzik.ico"))
        if ikon.isNull():
            ikon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)
        self.tray.setIcon(ikon)
        m = QMenu()
        self.act_goster = QAction("", self); self.act_goster.triggered.connect(self._goster_gizle)
        self.act_kapat  = QAction("", self); self.act_kapat.triggered.connect(self.tamamen_kapat)
        m.addAction(self.act_goster); m.addAction(self.act_kapat)
        self.tray.setContextMenu(m)
        self.tray.activated.connect(
            lambda r: self._goster_gizle() if r == QSystemTrayIcon.ActivationReason.DoubleClick else None)
        self.tray.show()

    def _tepsiye_kucult(self):
        self.hide()
        self.tray.showMessage("Premium Player", "Arka planda çalışıyor.",
                              QSystemTrayIcon.MessageIcon.Information, 2000)

    def _goster_gizle(self):
        if self.isVisible(): self.hide()
        else: self.showNormal(); self.activateWindow()

    def _mini_degistir(self):
        self.mini_mod = not self.mini_mod
        
        # ÇÖZÜM 3: EqualizerWidget, dikey alanda çok yer kapladığı için mini modda gizleniyor.
        gizlenecek = [
            self.sag_widget, self.btn_tepsi, self.btn_tema,
            self.btn_dil, self.btn_uyku, self.btn_crossfade,
            self.btn_karistir, self.btn_tekrarla, self.btn_cal, 
            self.btn_ses_ikon, self.ses_slider, self.combo_ses,
            self.equalizer
        ]
        
        if self.mini_mod:
            for w in gizlenecek: w.hide()
            self.lbl_kapak.setFixedSize(220, 220)
            self._pencere_boyut_kilitle(MINI_W, MINI_H)
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        else:
            for w in gizlenecek: w.show()
            self._pencere_boyut_kilitle(WIN_W, WIN_H)
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.show(); self.arayuzu_guncelle()

    def closeEvent(self, event): self.tamamen_kapat(); event.accept()

    def tamamen_kapat(self):
        self.ayarlar["son_klasor"] = self.gecerli_klasor
        if 0 <= self.mevcut_indeks < len(self.sarki_listesi):
            self.ayarlar["son_sarki"] = os.path.basename(self.sarki_listesi[self.mevcut_indeks])
            self.ayarlar["son_konum"] = self.player.position()
        ayarlari_kaydet(self.ayarlar)
        self.player.stop(); self.tray.hide()
        QApplication.quit(); os._exit(0)

    def _hafizadan_yukle(self):
        if self.gecerli_klasor and os.path.exists(self.gecerli_klasor):
            self.sarki_listesi = [f for f in os.listdir(self.gecerli_klasor)
                                  if f.lower().endswith(DESTEKLENEN_FORMAT)]
            self._listeyi_yenile()
            son = self.ayarlar.get("son_sarki", "")
            if son in self.sarki_listesi:
                self.mevcut_indeks = self.sarki_listesi.index(son)
                self.restore_konum = self.ayarlar.get("son_konum", 0)
                self.sarkiyi_baslat(otomatik=False)
                self.set_durum(LANG[self.ayarlar["dil"]]["waiting"], "#fbbf24")

    # ═══════════════════════════════════════════════════════════════
    # Uyku zamanlayıcı
    # ═══════════════════════════════════════════════════════════════
    def _uyku_ayarla(self):
        secs = [0, 15, 30, 60]
        self.uyku_suresi = secs[(secs.index(self.uyku_suresi) + 1) % len(secs)
                                if self.uyku_suresi in secs else 0]
        if self.uyku_suresi == 0: self._uyku_timer.stop()
        else: self._uyku_timer.start(60000)
        self.arayuzu_guncelle()

    def _uyku_gerisayim(self):
        self.uyku_suresi -= 1
        if self.uyku_suresi <= 0: self._uyku_timer.stop(); self.tamamen_kapat()
        self.arayuzu_guncelle()

    # ═══════════════════════════════════════════════════════════════
    # Toggle metodları
    # ═══════════════════════════════════════════════════════════════
    def _karistir_toggle(self):
        self.karisik_cal = not self.karisik_cal; self.arayuzu_guncelle()
    def _tekrarla_toggle(self):
        self.tekrarla = not self.tekrarla; self.arayuzu_guncelle()
    def _crossfade_toggle(self):
        self.ayarlar["crossfade"] = not self.ayarlar.get("crossfade", True)
        self.arayuzu_guncelle()
    def _tema_degistir(self):
        lista = list(THEMES.keys())
        self.ayarlar["tema"] = lista[(lista.index(self.ayarlar.get("tema","dark")) + 1) % len(lista)]
        self.arayuzu_guncelle()
    def _dil_degistir(self):
        self.ayarlar["dil"] = "en" if self.ayarlar["dil"] == "tr" else "tr"
        self.arayuzu_guncelle()

    # ═══════════════════════════════════════════════════════════════
    # Durum metni & kaydırma
    # ═══════════════════════════════════════════════════════════════
    def set_durum(self, metin, renk):
        self._durum_metni = metin; self._kaydirma_idx = 0
        self.lbl_durum.setStyleSheet(f"color:{renk};font-weight:bold;font-size:14px;")

    def _yazi_kaydir(self):
        if len(self._durum_metni) > 35:
            b = self._durum_metni + "   *** "
            self.lbl_durum.setText((b[self._kaydirma_idx:] + b[:self._kaydirma_idx])[:35])
            self._kaydirma_idx = (self._kaydirma_idx + 1) % len(b)
        else:
            self.lbl_durum.setText(self._durum_metni)

    # ═══════════════════════════════════════════════════════════════
    # Klavye
    # ═══════════════════════════════════════════════════════════════
    def _klavye_kisayollarini_bagla(self):
        def k(seq, fn): s = QShortcut(QKeySequence(seq), self); s.activated.connect(fn)
        k(Qt.Key.Key_Space,                lambda: self.duraklat_devam() if not self.arama_kutusu.hasFocus() else None)
        k(Qt.Key.Key_MediaPlay,            self.duraklat_devam)
        k(Qt.Key.Key_MediaTogglePlayPause, self.duraklat_devam)
        k(Qt.Key.Key_MediaNext,            self.sonraki_sarki)
        k(Qt.Key.Key_MediaPrevious,        self.onceki_sarki)
        k(Qt.Key.Key_Right, lambda: self.player.setPosition(min(self.player.position()+5000, self.player.duration())))
        k(Qt.Key.Key_Left,  lambda: self.player.setPosition(max(self.player.position()-5000, 0)))

    # ═══════════════════════════════════════════════════════════════
    # Arayüz güncelle
    # ═══════════════════════════════════════════════════════════════
    def arayuzu_guncelle(self):
        tema_adi = self.ayarlar.get("tema", "dark")
        tema = THEMES.get(tema_adi, THEMES["dark"])
        self.setStyleSheet(tema)

        hedef_w, hedef_h = (MINI_W, MINI_H) if self.mini_mod else (WIN_W, WIN_H)
        self._pencere_boyut_kilitle(hedef_w, hedef_h)

        import re as _re
        m = _re.search(r'sub-page:horizontal \{ background:([^;]+);', tema)
        acc = m.group(1).strip() if m else "#0a84ff"
        self.equalizer.set_renk(acc)

        fg_m = _re.search(r'QWidget\s*\{[^}]*color:([^;]+);', tema)
        fg   = fg_m.group(1).strip() if fg_m else "#ffffff"
        self._guncel_fg = fg
        _ikon_temizle()  

        d = LANG[self.ayarlar["dil"]]
        self.setWindowTitle(d["title"])
        self.act_goster.setText(d["tray_show"])
        self.act_kapat.setText(d["tray_quit"])

        def _btn_ikon_metin(btn, ad_qta, metin, renk=fg):
            ikon = _ikon(ad_qta, renk)
            if QTA and not ikon.isNull():
                btn.setIcon(ikon)
                btn.setIconSize(QSize(16, 16))
            else:
                btn.setIcon(QIcon())
            btn.setText(f" {metin}")
            btn.setMinimumWidth(50)
            btn.setMaximumWidth(16777215) 

        # ── Üst bar ──
        _btn_ikon_metin(self.btn_mini, "fa5s.chevron-down" if self.mini_mod else "fa5s.chevron-up", d["mini_off"] if self.mini_mod else d["mini_on"])
        _btn_ikon_metin(self.btn_tepsi, "fa5s.arrow-down", d["tray_btn"])
        _btn_ikon_metin(self.btn_crossfade, "fa5s.random", d["crossfade_on"] if self.ayarlar.get("crossfade", True) else d["crossfade_off"])
        _btn_ikon_metin(self.btn_uyku, "fa5s.clock", d["sleep_off"] if self.uyku_suresi == 0 else d["sleep_on"].format(self.uyku_suresi))
        _btn_ikon_metin(self.btn_tema, "fa5s.palette", d["theme"])
        _btn_ikon_metin(self.btn_dil, "fa5s.globe", d["lang"])

        # ── Araç bar ──
        _btn_ikon_metin(self.btn_klasor, "fa5s.folder-open", d["folder"])
        _btn_ikon_metin(self.btn_kaydet, "fa5s.save", d["save_pl"])
        _btn_ikon_metin(self.btn_yukle, "fa5s.file-upload", d["load_pl"])
        self.arama_kutusu.setPlaceholderText(d["search"])

        cur = self.combo_sirala.currentIndex()
        self.combo_sirala.blockSignals(True)
        self.combo_sirala.clear()
        self.combo_sirala.addItems([d["sort_az"], d["sort_za"],
                                    d["sort_new"], d["sort_old"], d["sort_manual"]])
        self.combo_sirala.setCurrentIndex(max(cur, 0))
        self.combo_sirala.blockSignals(False)

        # ── Kontrol butonları — qtawesome ikonları ──
        cal_durumu = self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

        def _btn_ikon(btn, ad_qta, fallback_txt, renk=fg):
            ikon = _ikon(ad_qta, renk)
            if QTA and not ikon.isNull():
                btn.setIcon(ikon)
                btn.setIconSize(QSize(18, 18))
                btn.setText("")
                btn.setFixedWidth(44) 
            else:
                btn.setIcon(QIcon())
                btn.setText(fallback_txt)
                btn.setMinimumWidth(50)
                btn.setMaximumWidth(16777215) 

        _btn_ikon(self.btn_onceki,   "fa5s.step-backward", d["prev"])
        _btn_ikon(self.btn_sonraki,  "fa5s.step-forward",  d["next"])
        _btn_ikon(self.btn_cal,      "msc.debug-restart",   d["restart"]) 
        _btn_ikon(self.btn_duraklat,
                  "fa5s.pause" if cal_durumu else "fa5s.play",
                  d["pause"] if cal_durumu else d["play"])
        _btn_ikon(self.btn_durdur,   "fa5s.stop",           d["stop"])

        if self.sessiz_mi:
            _btn_ikon(self.btn_ses_ikon, "fa5s.volume-mute", d["mute"], "#f87171")
            self.btn_ses_ikon.setStyleSheet("background-color:#f87171;color:white;")
        else:
            _btn_ikon(self.btn_ses_ikon, "fa5s.volume-up", d["vol"])
            self.btn_ses_ikon.setStyleSheet("")

        if self.karisik_cal:
            _btn_ikon_metin(self.btn_karistir, "fa5s.random", d["shuffle_on"], "#4ade80")
            self.btn_karistir.setStyleSheet("background-color:#4ade80;color:#000;")
        else:
            _btn_ikon_metin(self.btn_karistir, "fa5s.random", d["shuffle_off"])
            self.btn_karistir.setStyleSheet("")

        if self.tekrarla:
            _btn_ikon_metin(self.btn_tekrarla, "fa5s.redo", d["repeat_on"], "#0a84ff")
            self.btn_tekrarla.setStyleSheet("background-color:#0a84ff;color:#fff;")
        else:
            _btn_ikon_metin(self.btn_tekrarla, "fa5s.redo", d["repeat_off"])
            self.btn_tekrarla.setStyleSheet("")

if __name__ == "__main__":
    _app.setQuitOnLastWindowClosed(False)
    w = PremiumPlayer()
    w.show()
    sys.exit(_app.exec())