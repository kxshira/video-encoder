import sys
import os
import subprocess
import re
import time
import json
from pathlib import Path
from collections import deque

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QLineEdit, QFileDialog, QTextEdit, QProgressBar, QGroupBox,
    QTabWidget, QSlider, QCheckBox, QSplitter, QFrame, QScrollArea,
    QMessageBox, QSizePolicy, QStackedWidget
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSize, QMimeData,
    QRect, QRectF, QUrl, QPointF
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QDragEnterEvent, QDropEvent,
    QLinearGradient, QPainter, QPen, QBrush, QPolygonF, QCursor
)

# Try multimedia — graceful fallback if unavailable
HAS_MULTIMEDIA = False
try:
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PyQt6.QtMultimediaWidgets import QVideoWidget
    HAS_MULTIMEDIA = True
except ImportError:
    pass

# ─── Theme ────────────────────────────────────────────────────────────────────

DARK_STYLE = """
QMainWindow { background-color: #0d1117; }
QWidget {
    background-color: #0d1117; color: #c9d1d9;
    font-family: 'Segoe UI','Helvetica Neue',Arial,sans-serif; font-size: 13px;
}
QGroupBox {
    border: 1px solid #21262d; border-radius: 8px; margin-top: 14px;
    padding: 16px 12px 12px 12px; font-weight: 600; font-size: 12px;
    text-transform: uppercase; letter-spacing: 0.8px; color: #58a6ff;
}
QGroupBox::title {
    subcontrol-origin: margin; left: 14px; padding: 0 6px;
    background-color: #0d1117;
}
QComboBox {
    background-color: #161b22; border: 1px solid #30363d; border-radius: 6px;
    padding: 7px 12px; color: #c9d1d9; min-height: 20px;
}
QComboBox:hover { border-color: #58a6ff; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow {
    image: none; border-left: 5px solid transparent;
    border-right: 5px solid transparent; border-top: 6px solid #58a6ff; margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #161b22; border: 1px solid #30363d; border-radius: 6px;
    selection-background-color: #1f6feb; color: #c9d1d9; outline: none;
}
QSpinBox, QDoubleSpinBox, QLineEdit {
    background-color: #161b22; border: 1px solid #30363d; border-radius: 6px;
    padding: 7px 12px; color: #c9d1d9; min-height: 20px;
}
QSpinBox:hover, QDoubleSpinBox:hover, QLineEdit:hover { border-color: #58a6ff; }
QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus { border-color: #58a6ff; outline: none; }
QPushButton {
    background-color: #21262d; border: 1px solid #30363d; border-radius: 8px;
    padding: 8px 18px; color: #c9d1d9; font-weight: 500; min-height: 18px;
}
QPushButton:hover { background-color: #30363d; border-color: #58a6ff; }
QPushButton:pressed { background-color: #0d1117; }
QPushButton:disabled { background-color: #161b22; color: #484f58; border-color: #21262d; }
QPushButton#primaryBtn {
    background-color: #238636; border-color: #2ea043; color: #fff;
    font-weight: 600; font-size: 14px; padding: 10px 28px;
}
QPushButton#primaryBtn:hover { background-color: #2ea043; border-color: #3fb950; }
QPushButton#primaryBtn:disabled { background-color: #161b22; border-color: #21262d; color: #484f58; }
QPushButton#dangerBtn {
    background-color: #da3633; border-color: #f85149; color: #fff; font-weight: 600;
}
QPushButton#dangerBtn:hover { background-color: #f85149; }
QPushButton#dangerBtn:disabled { background-color: #161b22; border-color: #21262d; color: #484f58; }
QPushButton#iconBtn {
    background-color: transparent; border: 1px solid #30363d; border-radius: 6px;
    padding: 6px; min-width: 34px; max-width: 34px; min-height: 30px; max-height: 30px;
}
QPushButton#iconBtn:hover { background-color: #21262d; border-color: #58a6ff; }
QPushButton#smallBtn {
    background-color: #21262d; border: 1px solid #30363d; border-radius: 6px;
    padding: 4px 10px; color: #c9d1d9; font-size: 11px; min-height: 14px;
}
QPushButton#smallBtn:hover { background-color: #30363d; border-color: #58a6ff; }
QPushButton#playBtn {
    background-color: #1f6feb; border-color: #58a6ff; border-radius: 8px;
    padding: 6px 16px; color: #fff; font-weight: 600; min-height: 18px;
}
QPushButton#playBtn:hover { background-color: #388bfd; }
QProgressBar {
    background-color: #161b22; border: none; border-radius: 6px;
    min-height: 10px; max-height: 10px; text-align: center;
    color: #c9d1d9; font-size: 10px; font-weight: 600;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1f6feb,stop:0.5 #58a6ff,stop:1 #79c0ff);
    border-radius: 6px;
}
QSlider::groove:horizontal { background: #161b22; height: 6px; border-radius: 3px; }
QSlider::handle:horizontal {
    background: #58a6ff; width: 16px; height: 16px; margin: -5px 0;
    border-radius: 8px; border: 2px solid #0d1117;
}
QSlider::sub-page:horizontal { background: #1f6feb; border-radius: 3px; }
QCheckBox { spacing: 8px; color: #c9d1d9; }
QCheckBox::indicator {
    width: 18px; height: 18px; border-radius: 4px;
    border: 1px solid #30363d; background-color: #161b22;
}
QCheckBox::indicator:checked { background-color: #1f6feb; border-color: #58a6ff; }
QCheckBox::indicator:hover { border-color: #58a6ff; }
QTextEdit {
    background-color: #0d1117; border: 1px solid #21262d; border-radius: 8px;
    padding: 10px; color: #7ee787;
    font-family: 'Cascadia Code','Fira Code','Consolas',monospace;
    font-size: 12px; line-height: 1.5;
}
QTabWidget::pane {
    border: 1px solid #21262d; border-radius: 8px; top: -1px; background-color: #0d1117;
}
QTabBar::tab {
    background-color: transparent; border: 1px solid transparent; border-bottom: none;
    padding: 10px 20px; margin-right: 2px; border-top-left-radius: 8px;
    border-top-right-radius: 8px; color: #8b949e; font-weight: 500;
}
QTabBar::tab:hover { color: #c9d1d9; background-color: #161b22; }
QTabBar::tab:selected {
    background-color: #0d1117; border-color: #21262d; color: #58a6ff; font-weight: 600;
}
QScrollArea { border: none; background-color: transparent; }
QScrollBar:vertical { background: transparent; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #30363d; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #484f58; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: transparent; height: 8px; border-radius: 4px; }
QScrollBar::handle:horizontal { background: #30363d; border-radius: 4px; min-width: 30px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QLabel#headerLabel { font-size: 22px; font-weight: 700; color: #f0f6fc; }
QLabel#subLabel { font-size: 12px; color: #8b949e; }
QLabel#sectionLabel {
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.8px; color: #8b949e; margin-bottom: 6px;
}
QLabel#valueLabel {
    font-size: 13px; color: #58a6ff; font-weight: 600;
    font-family: 'Cascadia Code','Fira Code',monospace;
}
QLabel#statValue { font-size: 20px; font-weight: 700; color: #f0f6fc; }
QLabel#statLabel {
    font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px;
}
QFrame#separator { background-color: #21262d; max-height: 1px; }
QFrame#dropZone {
    background-color: #161b22; border: 2px dashed #30363d; border-radius: 12px;
}
QFrame#previewFrame {
    background-color: #010409; border: 1px solid #21262d; border-radius: 10px;
}
QToolTip {
    background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d;
    border-radius: 6px; padding: 6px 10px; font-size: 12px;
}
"""

# ─── Drop Zone ────────────────────────────────────────────────────────────────

class DropZone(QFrame):
    fileDropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(90)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label = QLabel("📁")
        self.icon_label.setFont(QFont("Segoe UI Emoji", 28))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)
        self.title_label = QLabel("Drop media files here")
        self.title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: #c9d1d9;")
        layout.addWidget(self.title_label)
        self.file_label = QLabel("")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("color: #58a6ff; font-size: 12px; margin-top: 4px;")
        layout.addWidget(self.file_label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.setStyleSheet(self.styleSheet().replace(
                "border: 2px dashed #30363d", "border: 2px dashed #58a6ff"
            ).replace("background-color: #161b22", "background-color: #1f6feb11"))
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(DARK_STYLE)

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet(DARK_STYLE)
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.set_file(path)
            self.fileDropped.emit(path)

    def set_file(self, path: str):
        self.file_label.setText(f"✓ {Path(path).name}")
        self.title_label.setText("File loaded")
        self.icon_label.setText("🎬")

    def clear(self):
        self.file_label.setText("")
        self.title_label.setText("Drop media files here")
        self.icon_label.setText("📁")


# ─── Timeline Widget ──────────────────────────────────────────────────────────

class TimelineWidget(QWidget):
    position_changed = pyqtSignal(float)
    in_changed = pyqtSignal(float)
    out_changed = pyqtSignal(float)

    BAR_MARGIN = 18
    BAR_HEIGHT = 30
    HANDLE_W = 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self.duration = 0.0
        self.position = 0.0
        self.in_point = 0.0
        self.out_point = 0.0
        self._dragging = None
        self.setFixedHeight(64)
        self.setMinimumWidth(200)
        self.setMouseTracking(True)

    def set_duration(self, d: float):
        self.duration = d
        self.out_point = d
        self.update()

    def set_position(self, p: float):
        self.position = max(0, min(p, self.duration))
        self.update()

    def set_in(self, t: float):
        self.in_point = max(0, min(t, self.out_point))
        self.update()

    def set_out(self, t: float):
        self.out_point = max(self.in_point, min(t, self.duration))
        self.update()

    def reset_cut(self):
        self.in_point = 0.0
        self.out_point = self.duration
        self.update()

    def _time_to_x(self, t: float) -> float:
        if self.duration <= 0:
            return self.HANDLE_W
        pad = self.HANDLE_W
        return pad + (t / self.duration) * (self.width() - 2 * pad)

    def _x_to_time(self, x: float) -> float:
        if self.duration <= 0:
            return 0
        pad = self.HANDLE_W
        ratio = (x - pad) / (self.width() - 2 * pad)
        return max(0, min(ratio * self.duration, self.duration))

    def _hit_test(self, pos) -> str:
        bar_y = self.BAR_MARGIN
        bar_h = self.BAR_HEIGHT
        in_x = self._time_to_x(self.in_point)
        out_x = self._time_to_x(self.out_point)

        in_rect = QRectF(in_x - 7, bar_y - 4, 14, bar_h + 8)
        out_rect = QRectF(out_x - 7, bar_y - 4, 14, bar_h + 8)

        if in_rect.contains(pos):
            return "in"
        if out_rect.contains(pos):
            return "out"
        if QRectF(self.HANDLE_W, bar_y, self.width() - 2 * self.HANDLE_W, bar_h).contains(pos):
            return "bar"
        return ""

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton or self.duration <= 0:
            return
        hit = self._hit_test(event.position())
        if hit in ("in", "out", "bar"):
            self._dragging = hit
            if hit == "bar":
                t = self._x_to_time(event.position().x())
                self.position = t
                self.position_changed.emit(t)
            self.update()

    def mouseMoveEvent(self, event):
        if self.duration <= 0:
            return
        if self._dragging == "bar":
            t = self._x_to_time(event.position().x())
            self.position = t
            self.position_changed.emit(t)
            self.update()
        elif self._dragging == "in":
            t = self._x_to_time(event.position().x())
            self.in_point = max(0, min(t, self.out_point - 0.01))
            self.in_changed.emit(self.in_point)
            self.update()
        elif self._dragging == "out":
            t = self._x_to_time(event.position().x())
            self.out_point = max(self.in_point + 0.01, min(t, self.duration))
            self.out_changed.emit(self.out_point)
            self.update()
        else:
            hit = self._hit_test(event.position())
            if hit in ("in", "out"):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif hit == "bar":
                self.setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self._dragging = None

    def mouseDoubleClickEvent(self, event):
        if self.duration <= 0:
            return
        hit = self._hit_test(event.position())
        if hit == "bar":
            t = self._x_to_time(event.position().x())
            self.position = t
            self.position_changed.emit(t)

    @staticmethod
    def _fmt(t: float) -> str:
        if t < 0:
            t = 0
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = t % 60
        if h > 0:
            return f"{h}:{m:02d}:{s:05.2f}"
        return f"{m}:{s:05.2f}"

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        bar_y = self.BAR_MARGIN
        bar_h = self.BAR_HEIGHT
        pad = self.HANDLE_W
        bar_w = w - 2 * pad

        # Background bar
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#161b22"))
        p.drawRoundedRect(pad, bar_y, bar_w, bar_h, 6, 6)

        if self.duration <= 0:
            p.setPen(QColor("#484f58"))
            p.setFont(QFont("Segoe UI", 11))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Load a file to see timeline")
            p.end()
            return

        # Selection region
        in_x = self._time_to_x(self.in_point)
        out_x = self._time_to_x(self.out_point)
        sel_w = max(out_x - in_x, 0)

        if sel_w > 1:
            grad = QLinearGradient(in_x, 0, out_x, 0)
            grad.setColorAt(0, QColor("#1f6feb55"))
            grad.setColorAt(0.5, QColor("#58a6ff44"))
            grad.setColorAt(1, QColor("#1f6feb55"))
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(QRectF(in_x, bar_y, sel_w, bar_h), 4, 4)

            # Selection border
            p.setPen(QPen(QColor("#58a6ff66"), 1))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(QRectF(in_x, bar_y, sel_w, bar_h), 4, 4)

        # In handle
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#f0883e"))
        p.drawRoundedRect(QRectF(in_x - 4, bar_y - 2, 8, bar_h + 4), 3, 3)
        tri_in = QPolygonF([QPointF(in_x, bar_y - 7), QPointF(in_x - 6, bar_y - 1), QPointF(in_x + 6, bar_y - 1)])
        p.drawPolygon(tri_in)

        # Out handle
        p.setBrush(QColor("#f0883e"))
        p.drawRoundedRect(QRectF(out_x - 4, bar_y - 2, 8, bar_h + 4), 3, 3)
        tri_out = QPolygonF([QPointF(out_x, bar_y - 7), QPointF(out_x - 6, bar_y - 1), QPointF(out_x + 6, bar_y - 1)])
        p.drawPolygon(tri_out)

        # Playhead
        pos_x = self._time_to_x(self.position)
        p.setPen(QPen(QColor("#f0f6fc"), 2))
        p.drawLine(QPointF(pos_x, bar_y + 2), QPointF(pos_x, bar_y + bar_h - 2))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#f0f6fc"))
        p.drawEllipse(QPointF(pos_x, bar_y - 3), 4, 4)

        # Time ticks
        p.setPen(QColor("#484f58"))
        p.setFont(QFont("Segoe UI", 8))
        num_ticks = max(2, min(int(w / 100), 25))
        for i in range(num_ticks + 1):
            t = (i / num_ticks) * self.duration
            x = self._time_to_x(t)
            tick_h = 4 if i % 5 == 0 else 2
            p.drawLine(QPointF(x, bar_y + bar_h), QPointF(x, bar_y + bar_h + tick_h))
            if i % max(1, num_ticks // 8) == 0 or i == num_ticks:
                p.drawText(QRectF(x - 30, 0, 60, bar_y - 6), Qt.AlignmentFlag.AlignCenter, self._fmt(t))

        # In/Out labels on the bar
        p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        if sel_w > 60:
            p.setPen(QColor("#f0883e"))
            p.drawText(QRectF(in_x + 8, bar_y + 4, sel_w - 16, 12), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"In {self._fmt(self.in_point)}")
            p.drawText(QRectF(in_x + 8, bar_y + 16, sel_w - 16, 12), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"Out {self._fmt(self.out_point)}")

        p.end()


# ─── FFmpeg Worker ────────────────────────────────────────────────────────────

class FFmpegWorker(QThread):
    progress = pyqtSignal(float, str, float, float)
    output = pyqtSignal(str)
    finished_signal = pyqtSignal(int, str)
    duration_found = pyqtSignal(float)

    def __init__(self, cmd: list, duration: float = 0):
        super().__init__()
        self.cmd = cmd
        self.duration = duration
        self._process = None
        self._running = True

    def run(self):
        try:
            self._process = subprocess.Popen(
                self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            time_re = re.compile(r'time=(\d+:\d+:\d+\.\d+)')
            speed_re = re.compile(r'speed=\s*([\d.]+)x')
            bitrate_re = re.compile(r'bitrate=\s*([\d.]+)([kM]?bits/s)')
            dur_re = re.compile(r'Duration:\s*(\d+:\d+:\d+\.\d+)')

            for line in self._process.stdout:
                if not self._running:
                    self._process.terminate()
                    break
                line = line.strip()
                self.output.emit(line)
                if self.duration == 0:
                    m = dur_re.search(line)
                    if m:
                        self.duration = self._parse_time(m.group(1))
                        self.duration_found.emit(self.duration)
                m_t = time_re.search(line)
                m_s = speed_re.search(line)
                m_b = bitrate_re.search(line)
                if m_t:
                    cur = self._parse_time(m_t.group(1))
                    if self.duration > 0:
                        pct = min((cur / self.duration) * 100, 100)
                        spd = float(m_s.group(1)) if m_s else 0
                        eta = ((self.duration - cur) / spd) if spd > 0 else 0
                        br = float(m_b.group(1)) if m_b else 0
                        self.progress.emit(pct, f"{spd:.2f}x", eta, br)
            self._process.wait()
            self.finished_signal.emit(self._process.returncode, "Encoding complete.")
        except FileNotFoundError:
            self.finished_signal.emit(-1, "FFmpeg not found!")
        except Exception as e:
            self.finished_signal.emit(-1, str(e))

    def stop(self):
        self._running = False
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass

    @staticmethod
    def _parse_time(t: str) -> float:
        p = t.split(":")
        return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2])


def probe_media(path: str) -> dict:
    info = {"duration": 0, "video": {}, "audio": {}, "format": {}}
    try:
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10,
                           creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        data = json.loads(r.stdout)
        fmt = data.get("format", {})
        info["format"] = {"name": fmt.get("format_name", ""), "size": int(fmt.get("size", 0)),
                          "bit_rate": int(fmt.get("bit_rate", 0)), "duration": float(fmt.get("duration", 0))}
        info["duration"] = info["format"]["duration"]
        for s in data.get("streams", []):
            if s["codec_type"] == "video" and not info["video"]:
                info["video"] = {"codec": s.get("codec_name", ""), "width": int(s.get("width", 0)),
                                 "height": int(s.get("height", 0)), "fps": s.get("r_frame_rate", "")}
            elif s["codec_type"] == "audio" and not info["audio"]:
                info["audio"] = {"codec": s.get("codec_name", ""), "sample_rate": s.get("sample_rate", ""),
                                 "channels": int(s.get("channels", 0))}
    except Exception:
        pass
    return info


# ─── Presets ──────────────────────────────────────────────────────────────────

PRESETS = {
    "Custom": {},
    "Web (H.264)": {"vcodec": "libx264", "acodec": "aac", "format": "mp4", "crf": 23, "preset": "medium",
                    "audio_bitrate": 128, "resolution": "source", "extra": ["-movflags", "+faststart"]},
    "Web (H.265)": {"vcodec": "libx265", "acodec": "aac", "format": "mp4", "crf": 28, "preset": "medium",
                    "audio_bitrate": 128, "resolution": "source", "extra": ["-movflags", "+faststart"]},
    "YouTube 1080p": {"vcodec": "libx264", "acodec": "aac", "format": "mp4", "crf": 20, "preset": "slow",
                      "audio_bitrate": 192, "resolution": "1920x1080", "extra": ["-movflags", "+faststart"]},
    "YouTube 4K": {"vcodec": "libx264", "acodec": "aac", "format": "mp4", "crf": 18, "preset": "slow",
                   "audio_bitrate": 256, "resolution": "3840x2160", "extra": ["-movflags", "+faststart"]},
    "Mobile 720p": {"vcodec": "libx264", "acodec": "aac", "format": "mp4", "crf": 26, "preset": "fast",
                    "audio_bitrate": 96, "resolution": "1280x720", "extra": ["-movflags", "+faststart"]},
    "Discord 8MB": {"vcodec": "libx264", "acodec": "aac", "format": "mp4", "crf": 30, "preset": "fast",
                    "audio_bitrate": 64, "resolution": "source",
                    "extra": ["-movflags", "+faststart", "-fs", "8388608"]},
    "GIF Output": {"vcodec": "gif", "acodec": "none", "format": "gif", "crf": 0, "preset": "",
                   "audio_bitrate": 0, "resolution": "480:-1", "extra": []},
    "Audio MP3": {"vcodec": "none", "acodec": "libmp3lame", "format": "mp3", "crf": 0, "preset": "",
                  "audio_bitrate": 192, "resolution": "none", "extra": []},
    "Audio FLAC": {"vcodec": "none", "acodec": "flac", "format": "flac", "crf": 0, "preset": "",
                   "audio_bitrate": 0, "resolution": "none", "extra": []},
    "Lossless H.264": {"vcodec": "libx264", "acodec": "flac", "format": "mkv", "crf": 0, "preset": "veryslow",
                       "audio_bitrate": 0, "resolution": "source", "extra": []},
    "VP9 WebM": {"vcodec": "libvpx-vp9", "acodec": "libopus", "format": "webm", "crf": 30, "preset": "",
                 "audio_bitrate": 128, "resolution": "source", "extra": ["-b:v", "0", "-cpu-used", "4"]},
}


# ─── Main Window ──────────────────────────────────────────────────────────────

class EncoderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFmpeg Encoder")
        self.setMinimumSize(1150, 860)
        self.resize(1250, 900)
        self.input_path = ""
        self.media_info = {}
        self.worker = None
        self._queue = deque()
        self._build_ui()
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(DARK_STYLE)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 16)
        root.setSpacing(10)

        # ── Header ─────────────────────────────────────────────────
        hdr = QHBoxLayout()
        hl = QLabel("FFmpeg Encoder")
        hl.setObjectName("headerLabel")
        hdr.addWidget(hl)
        hdr.addStretch()
        self.ff_label = QLabel("FFmpeg: checking...")
        self.ff_label.setObjectName("subLabel")
        hdr.addWidget(self.ff_label)
        root.addLayout(hdr)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)

        # ── Preview Section (top) ──────────────────────────────────
        preview_frame = QFrame()
        preview_frame.setObjectName("previewFrame")
        pf_layout = QHBoxLayout(preview_frame)
        pf_layout.setContentsMargins(12, 10, 12, 10)
        pf_layout.setSpacing(14)

        # Video widget / placeholder
        self.preview_stack = QStackedWidget()
        self.preview_stack.setMinimumSize(380, 214)
        self.preview_stack.setMaximumHeight(220)

        # Placeholder
        ph = QWidget()
        ph.setStyleSheet("background-color: #010409;")
        ph_l = QVBoxLayout(ph)
        ph_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_icon = QLabel("🎬")
        ph_icon.setFont(QFont("Segoe UI Emoji", 36))
        ph_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_icon.setStyleSheet("color: #21262d;")
        ph_l.addWidget(ph_icon)
        ph_txt = QLabel("Video Preview")
        ph_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_txt.setStyleSheet("color: #30363d; font-size: 13px;")
        ph_l.addWidget(ph_txt)
        self.preview_stack.addWidget(ph)

        # Actual video widget
        if HAS_MULTIMEDIA:
            self.video_widget = QVideoWidget()
            self.video_widget.setStyleSheet("background-color: #000;")
            self.preview_stack.addWidget(self.video_widget)

            self.player = QMediaPlayer()
            self.audio_out = QAudioOutput()
            self.player.setAudioOutput(self.audio_out)
            self.player.setVideoOutput(self.video_widget)
            self.player.positionChanged.connect(self._on_player_pos)
            self.player.durationChanged.connect(self._on_player_dur)
        else:
            self.player = None
            self.video_widget = None
            no_mm = QWidget()
            no_mm.setStyleSheet("background-color: #010409;")
            nol = QVBoxLayout(no_mm)
            nol.setAlignment(Qt.AlignmentFlag.AlignCenter)
            nol_txt = QLabel("⚠ PyQt6-Multimedia not available\nInstall: pip install PyQt6[speech]")
            nol_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            nol_txt.setStyleSheet("color: #484f58; font-size: 12px;")
            nol.addWidget(nol_txt)
            self.preview_stack.addWidget(no_mm)

        pf_layout.addWidget(self.preview_stack, stretch=0)

        # Right side: controls + cut
        ctrl_widget = QWidget()
        ctrl_lay = QVBoxLayout(ctrl_widget)
        ctrl_lay.setContentsMargins(0, 0, 0, 0)
        ctrl_lay.setSpacing(8)

        # Playback controls
        pb_row = QHBoxLayout()
        pb_row.setSpacing(4)
        self.btn_skip_in = QPushButton("⏮")
        self.btn_skip_in.setObjectName("iconBtn")
        self.btn_skip_in.setToolTip("Skip to In point")
        self.btn_skip_in.clicked.connect(self._skip_to_in)
        pb_row.addWidget(self.btn_skip_in)

        self.btn_back = QPushButton("◀◀")
        self.btn_back.setObjectName("iconBtn")
        self.btn_back.setToolTip("Back 5 seconds")
        self.btn_back.clicked.connect(lambda: self._seek_rel(-5))
        pb_row.addWidget(self.btn_back)

        self.btn_play = QPushButton("▶")
        self.btn_play.setObjectName("playBtn")
        self.btn_play.setFixedSize(44, 34)
        self.btn_play.setToolTip("Play / Pause (Space)")
        self.btn_play.clicked.connect(self._toggle_play)
        pb_row.addWidget(self.btn_play)

        self.btn_fwd = QPushButton("▶▶")
        self.btn_fwd.setObjectName("iconBtn")
        self.btn_fwd.setToolTip("Forward 5 seconds")
        self.btn_fwd.clicked.connect(lambda: self._seek_rel(5))
        pb_row.addWidget(self.btn_fwd)

        self.btn_skip_out = QPushButton("⏭")
        self.btn_skip_out.setObjectName("iconBtn")
        self.btn_skip_out.setToolTip("Skip to Out point")
        self.btn_skip_out.clicked.connect(self._skip_to_out)
        pb_row.addWidget(self.btn_skip_out)

        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setObjectName("iconBtn")
        self.btn_stop.setToolTip("Stop")
        self.btn_stop.clicked.connect(self._stop_play)
        pb_row.addWidget(self.btn_stop)

        ctrl_lay.addLayout(pb_row)

        # Time display
        self.time_label = QLabel("00:00.00 / 00:00.00")
        self.time_label.setObjectName("valueLabel")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ctrl_lay.addWidget(self.time_label)

        # Volume
        vol_row = QHBoxLayout()
        vol_row.setSpacing(6)
        vol_row.addWidget(QLabel("🔊"))
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(80)
        self.vol_slider.setMaximumWidth(140)
        self.vol_slider.valueChanged.connect(self._set_volume)
        vol_row.addWidget(self.vol_slider)
        vol_row.addStretch()
        ctrl_lay.addLayout(vol_row)

        # Separator
        sep2 = QFrame()
        sep2.setObjectName("separator")
        sep2.setFrameShape(QFrame.Shape.HLine)
        ctrl_lay.addWidget(sep2)

        # Cut controls
        self.cut_check = QCheckBox(" ✂  Enable Cut / Trim")
        self.cut_check.toggled.connect(self._on_cut_toggle)
        ctrl_lay.addWidget(self.cut_check)

        cut_grid = QGridLayout()
        cut_grid.setSpacing(6)
        cut_grid.setContentsMargins(8, 0, 0, 0)

        cut_grid.addWidget(QLabel("In:"), 0, 0)
        self.in_spin = QDoubleSpinBox()
        self.in_spin.setRange(0, 99999)
        self.in_spin.setDecimals(3)
        self.in_spin.setSuffix(" s")
        self.in_spin.setSingleStep(0.1)
        self.in_spin.valueChanged.connect(self._on_in_spin)
        cut_grid.addWidget(self.in_spin, 0, 1)

        self.btn_set_in = QPushButton("Set")
        self.btn_set_in.setObjectName("smallBtn")
        self.btn_set_in.setToolTip("Set In point at current position (I)")
        self.btn_set_in.clicked.connect(self._set_in_at_pos)
        cut_grid.addWidget(self.btn_set_in, 0, 2)

        cut_grid.addWidget(QLabel("Out:"), 1, 0)
        self.out_spin = QDoubleSpinBox()
        self.out_spin.setRange(0, 99999)
        self.out_spin.setDecimals(3)
        self.out_spin.setSuffix(" s")
        self.out_spin.setSingleStep(0.1)
        self.out_spin.valueChanged.connect(self._on_out_spin)
        cut_grid.addWidget(self.out_spin, 1, 1)

        self.btn_set_out = QPushButton("Set")
        self.btn_set_out.setObjectName("smallBtn")
        self.btn_set_out.setToolTip("Set Out point at current position (O)")
        self.btn_set_out.clicked.connect(self._set_out_at_pos)
        cut_grid.addWidget(self.btn_set_out, 1, 2)

        cut_grid.addWidget(QLabel("Duration:"), 2, 0)
        self.cut_dur_label = QLabel("—")
        self.cut_dur_label.setObjectName("valueLabel")
        cut_grid.addWidget(self.cut_dur_label, 2, 1, 1, 2)

        self.btn_reset_cut = QPushButton("Reset")
        self.btn_reset_cut.setObjectName("smallBtn")
        self.btn_reset_cut.clicked.connect(self._reset_cut)
        cut_grid.addWidget(self.btn_reset_cut, 0, 3, 2, 1)

        self.cut_widgets = [self.in_spin, self.out_spin, self.btn_set_in,
                            self.btn_set_out, self.cut_dur_label, self.btn_reset_cut]
        for w in self.cut_widgets:
            w.setEnabled(False)

        ctrl_lay.addLayout(cut_grid)
        ctrl_lay.addStretch()

        pf_layout.addWidget(ctrl_widget, stretch=1)
        root.addWidget(preview_frame)

        # ── Timeline ───────────────────────────────────────────────
        self.timeline = TimelineWidget()
        self.timeline.position_changed.connect(self._on_timeline_seek)
        self.timeline.in_changed.connect(self._on_timeline_in)
        self.timeline.out_changed.connect(self._on_timeline_out)
        root.addWidget(self.timeline)

        # ── Main Splitter ──────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background: #21262d; }")

        # LEFT
        left = QWidget()
        left.setMaximumWidth(340)
        left.setMinimumWidth(280)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(8)

        self.drop_zone = DropZone()
        self.drop_zone.fileDropped.connect(self._on_file_dropped)
        ll.addWidget(self.drop_zone)

        browse_btn = QPushButton("📂  Browse Files")
        browse_btn.clicked.connect(self._browse_file)
        ll.addWidget(browse_btn)

        info_group = QGroupBox("Source Info")
        ig = QGridLayout(info_group)
        ig.setSpacing(5)
        labels = ["File:", "Duration:", "Video:", "Resolution:", "Audio:", "Size:"]
        self.info_vals = []
        for i, lbl in enumerate(labels):
            la = QLabel(lbl)
            la.setObjectName("sectionLabel")
            v = QLabel("—")
            v.setObjectName("valueLabel")
            v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            ig.addWidget(la, i, 0)
            ig.addWidget(v, i, 1)
            self.info_vals.append(v)
        ll.addWidget(info_group)

        preset_group = QGroupBox("Presets")
        pl = QVBoxLayout(preset_group)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(PRESETS.keys())
        self.preset_combo.currentTextChanged.connect(self._apply_preset)
        pl.addWidget(self.preset_combo)
        ll.addWidget(preset_group)
        ll.addStretch()
        splitter.addWidget(left)

        # RIGHT
        right_w = QWidget()
        rl = QVBoxLayout(right_w)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(8)

        tabs = QTabWidget()

        # ── Video Tab ─────────────────────────────────────────────
        vs = QScrollArea()
        vs.setWidgetResizable(True)
        vw = QWidget()
        vg = QVBoxLayout(vw)
        vg.setSpacing(8)

        vcg = QGroupBox("Video Codec")
        vcl = QGridLayout(vcg)
        vcl.addWidget(QLabel("Codec:"), 0, 0)
        self.vcodec_combo = QComboBox()
        self.vcodec_combo.addItems(["libx264 (H.264)", "libx265 (H.265/HEVC)", "libvpx-vp9 (VP9)",
                                     "libsvtav1 (AV1)", "libaom-av1 (AV1)", "copy (no re-encode)", "none (disable)"])
        vcl.addWidget(self.vcodec_combo, 0, 1)
        vcl.addWidget(QLabel("Preset:"), 1, 0)
        self.preset_enc = QComboBox()
        self.preset_enc.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast",
                                   "medium", "slow", "slower", "veryslow", "placebo"])
        self.preset_enc.setCurrentText("medium")
        vcl.addWidget(self.preset_enc, 1, 1)
        vg.addWidget(vcg)

        qg = QGroupBox("Quality")
        ql = QGridLayout(qg)
        ql.addWidget(QLabel("Mode:"), 0, 0)
        self.quality_mode = QComboBox()
        self.quality_mode.addItems(["CRF (Constant Quality)", "2-Pass Bitrate", "1-Pass Bitrate"])
        self.quality_mode.currentIndexChanged.connect(self._toggle_qmode)
        ql.addWidget(self.quality_mode, 0, 1)
        ql.addWidget(QLabel("CRF:"), 1, 0)
        cr = QHBoxLayout()
        self.crf_slider = QSlider(Qt.Orientation.Horizontal)
        self.crf_slider.setRange(0, 51)
        self.crf_slider.setValue(23)
        self.crf_label = QLabel("23")
        self.crf_label.setObjectName("valueLabel")
        self.crf_label.setMinimumWidth(28)
        self.crf_slider.valueChanged.connect(lambda v: self.crf_label.setText(str(v)))
        cr.addWidget(self.crf_slider)
        cr.addWidget(self.crf_label)
        ql.addLayout(cr, 1, 1)
        ql.addWidget(QLabel("Bitrate:"), 2, 0)
        br = QHBoxLayout()
        self.bitrate_spin = QSpinBox()
        self.bitrate_spin.setRange(100, 100000)
        self.bitrate_spin.setValue(5000)
        self.bitrate_spin.setSuffix(" kbps")
        self.bitrate_spin.setEnabled(False)
        br.addWidget(self.bitrate_spin)
        ql.addLayout(br, 2, 1)
        vg.addWidget(qg)

        rg = QGroupBox("Resolution")
        rl2 = QGridLayout(rg)
        rl2.addWidget(QLabel("Scale:"), 0, 0)
        self.res_combo = QComboBox()
        self.res_combo.addItems(["source", "3840x2160 (4K)", "2560x1440 (2K)", "1920x1080 (FHD)",
                                  "1280x720 (HD)", "854x480 (SD)", "640x360", "480:-1 (GIF)", "Custom"])
        self.res_combo.currentTextChanged.connect(self._toggle_cres)
        rl2.addWidget(self.res_combo, 0, 1)
        self.cres_w = QWidget()
        crl = QHBoxLayout(self.cres_w)
        crl.setContentsMargins(0, 0, 0, 0)
        crl.addWidget(QLabel("W:"))
        self.cw = QSpinBox()
        self.cw.setRange(1, 7680)
        self.cw.setValue(1920)
        crl.addWidget(self.cw)
        crl.addWidget(QLabel("H:"))
        self.ch = QSpinBox()
        self.ch.setRange(1, 4320)
        self.ch.setValue(1080)
        crl.addWidget(self.ch)
        self.cres_w.hide()
        rl2.addWidget(self.cres_w, 1, 0, 1, 2)
        self.lanczos_check = QCheckBox("Use lanczos scaling filter")
        self.lanczos_check.setChecked(True)
        rl2.addWidget(self.lanczos_check, 2, 0, 1, 2)
        vg.addWidget(rg)

        fg = QGroupBox("Framerate")
        fl = QHBoxLayout(fg)
        fl.addWidget(QLabel("FPS:"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["source", "60", "50", "30", "29.97", "25", "24", "23.976", "15", "Custom"])
        fl.addWidget(self.fps_combo)
        self.cfps = QDoubleSpinBox()
        self.cfps.setRange(1, 120)
        self.cfps.setValue(30)
        self.cfps.hide()
        fl.addWidget(self.cfps)
        self.fps_combo.currentTextChanged.connect(lambda t: self.cfps.setVisible(t == "Custom"))
        vg.addWidget(fg)

        exg = QGroupBox("Extra Video Options")
        exl = QVBoxLayout(exg)
        self.extra_video = QLineEdit()
        self.extra_video.setPlaceholderText("e.g. -tune film -x264-params bframes=5")
        exl.addWidget(self.extra_video)
        vg.addWidget(exg)
        vg.addStretch()
        vs.setWidget(vw)
        tabs.addTab(vs, "🎬  Video")

        # ── Audio Tab ─────────────────────────────────────────────
        ascroll = QScrollArea()
        ascroll.setWidgetResizable(True)
        aw = QWidget()
        ag = QVBoxLayout(aw)
        ag.setSpacing(8)
        acg = QGroupBox("Audio Codec")
        acl = QGridLayout(acg)
        acl.addWidget(QLabel("Codec:"), 0, 0)
        self.acodec_combo = QComboBox()
        self.acodec_combo.addItems(["aac", "libmp3lame (MP3)", "libopus (Opus)", "flac",
                                     "libvorbis (Vorbis)", "copy (no re-encode)", "none (disable)"])
        acl.addWidget(self.acodec_combo, 0, 1)
        acl.addWidget(QLabel("Bitrate:"), 1, 0)
        self.audio_br = QComboBox()
        self.audio_br.addItems(["64", "96", "128", "160", "192", "256", "320"])
        self.audio_br.setCurrentText("128")
        acl.addWidget(self.audio_br, 1, 1)
        acl.addWidget(QLabel("Sample Rate:"), 2, 0)
        self.sr_combo = QComboBox()
        self.sr_combo.addItems(["source", "48000", "44100", "32000", "22050", "16000"])
        acl.addWidget(self.sr_combo, 2, 1)
        acl.addWidget(QLabel("Channels:"), 3, 0)
        self.ch_combo = QComboBox()
        self.ch_combo.addItems(["source", "2 (stereo)", "1 (mono)", "6 (5.1)"])
        acl.addWidget(self.ch_combo, 3, 1)
        ag.addWidget(acg)
        aexg = QGroupBox("Extra Audio Options")
        aexl = QVBoxLayout(aexg)
        self.extra_audio = QLineEdit()
        self.extra_audio.setPlaceholderText("e.g. -volume 1.5")
        aexl.addWidget(self.extra_audio)
        ag.addWidget(aexg)
        ag.addStretch()
        ascroll.setWidget(aw)
        tabs.addTab(ascroll, "🎵  Audio")

        # ── Output Tab ────────────────────────────────────────────
        oscroll = QScrollArea()
        oscroll.setWidgetResizable(True)
        ow = QWidget()
        og = QVBoxLayout(ow)
        og.setSpacing(8)
        fmtg = QGroupBox("Container Format")
        fmtl = QGridLayout(fmtg)
        fmtl.addWidget(QLabel("Format:"), 0, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "mkv", "webm", "avi", "mov", "flv", "ts", "gif", "mp3", "flac", "ogg", "wav"])
        fmtl.addWidget(self.format_combo, 0, 1)
        og.addWidget(fmtg)

        outg = QGroupBox("Output File")
        outl = QVBoxLayout(outg)
        orow = QHBoxLayout()
        self.out_path = QLineEdit()
        self.out_path.setPlaceholderText("Auto-generated if empty")
        orow.addWidget(self.out_path)
        ob = QPushButton("📂")
        ob.setObjectName("iconBtn")
        ob.setToolTip("Browse output location")
        ob.clicked.connect(self._browse_output)
        orow.addWidget(ob)
        outl.addLayout(orow)
        self.auto_name = QCheckBox("Auto-generate output filename")
        self.auto_name.setChecked(True)
        self.auto_name.toggled.connect(self._toggle_auto)
        outl.addWidget(self.auto_name)
        og.addWidget(outg)

        glg = QGroupBox("Global Options")
        gll = QVBoxLayout(glg)
        self.overwrite = QCheckBox("Overwrite output without asking")
        self.overwrite.setChecked(True)
        gll.addWidget(self.overwrite)
        self.faststart = QCheckBox("Add faststart flag (web streaming)")
        self.faststart.setChecked(True)
        gll.addWidget(self.faststart)
        self.hwaccel = QCheckBox("Enable hardware acceleration (auto-detect)")
        gll.addWidget(self.hwaccel)
        self.strip_meta = QCheckBox("Strip all metadata")
        gll.addWidget(self.strip_meta)
        og.addWidget(glg)

        gexg = QGroupBox("Extra Global Options")
        gexl = QVBoxLayout(gexg)
        self.extra_global = QLineEdit()
        self.extra_global.setPlaceholderText("e.g. -threads 8")
        gexl.addWidget(self.extra_global)
        og.addWidget(gexg)
        og.addStretch()
        oscroll.setWidget(ow)
        tabs.addTab(oscroll, "💾  Output")

        # ── Command Tab ───────────────────────────────────────────
        cw = QWidget()
        cl = QVBoxLayout(cw)
        cl.setSpacing(8)
        cl.addWidget(QLabel("Generated FFmpeg Command"))
        self.cmd_text = QTextEdit()
        self.cmd_text.setReadOnly(True)
        self.cmd_text.setMaximumHeight(140)
        self.cmd_text.setPlaceholderText("Configure settings to see the command...")
        cl.addWidget(self.cmd_text)
        cb = QPushButton("📋  Copy Command")
        cb.clicked.connect(self._copy_cmd)
        cl.addWidget(cb)
        cl.addStretch()
        tabs.addTab(cw, "⌨️  Command")

        rl.addWidget(tabs)

        # ── Progress ──────────────────────────────────────────────
        pg = QGroupBox("Encoding Progress")
        pgl = QVBoxLayout(pg)
        pgl.setSpacing(6)
        sr = QHBoxLayout()
        sr.setSpacing(16)
        self.s_pct = QLabel("0%")
        self.s_pct.setObjectName("statValue")
        self.s_pct.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.s_pct.setMinimumWidth(65)
        self.s_spd = QLabel("—")
        self.s_spd.setObjectName("statValue")
        self.s_spd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.s_spd.setMinimumWidth(65)
        self.s_eta = QLabel("—")
        self.s_eta.setObjectName("statValue")
        self.s_eta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.s_eta.setMinimumWidth(65)
        self.s_br = QLabel("—")
        self.s_br.setObjectName("statValue")
        self.s_br.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.s_br.setMinimumWidth(85)
        for val, lbl in [(self.s_pct, "Progress"), (self.s_spd, "Speed"),
                          (self.s_eta, "ETA"), (self.s_br, "Bitrate")]:
            col = QVBoxLayout()
            col.addWidget(val)
            la = QLabel(lbl)
            la.setObjectName("statLabel")
            la.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.addWidget(la)
            sr.addLayout(col)
        pgl.addLayout(sr)
        self.pbar = QProgressBar()
        self.pbar.setValue(0)
        self.pbar.setTextVisible(False)
        pgl.addWidget(self.pbar)
        br2 = QHBoxLayout()
        self.enc_btn = QPushButton("▶  Start Encoding")
        self.enc_btn.setObjectName("primaryBtn")
        self.enc_btn.clicked.connect(self._start_enc)
        self.enc_btn.setEnabled(False)
        br2.addWidget(self.enc_btn)
        self.stop_btn = QPushButton("⏹  Stop")
        self.stop_btn.setObjectName("dangerBtn")
        self.stop_btn.clicked.connect(self._stop_enc)
        self.stop_btn.setEnabled(False)
        br2.addWidget(self.stop_btn)
        self.q_btn = QPushButton("➕  Queue")
        self.q_btn.clicked.connect(self._add_queue)
        self.q_btn.setEnabled(False)
        br2.addWidget(self.q_btn)
        pgl.addLayout(br2)
        rl.addWidget(pg)

        # ── Log ───────────────────────────────────────────────────
        logg = QGroupBox("Log Output")
        logl = QVBoxLayout(logg)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(130)
        logl.addWidget(self.log)
        lr = QHBoxLayout()
        clr = QPushButton("Clear Log")
        clr.clicked.connect(self.log.clear)
        lr.addWidget(clr)
        lr.addStretch()
        self.q_label = QLabel("Queue: 0 items")
        self.q_label.setObjectName("subLabel")
        lr.addWidget(self.q_label)
        logl.addLayout(lr)
        rl.addWidget(logg)

        splitter.addWidget(right_w)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter)

        # ── Signal wiring for live command ────────────────────────
        for w in [self.vcodec_combo, self.preset_enc, self.quality_mode,
                   self.crf_slider, self.bitrate_spin, self.res_combo,
                   self.cw, self.ch, self.lanczos_check, self.fps_combo, self.cfps,
                   self.extra_video, self.acodec_combo, self.audio_br,
                   self.sr_combo, self.ch_combo, self.extra_audio,
                   self.format_combo, self.out_path, self.overwrite,
                   self.faststart, self.hwaccel, self.strip_meta,
                   self.extra_global, self.cut_check, self.in_spin, self.out_spin]:
            if isinstance(w, QComboBox):
                w.currentTextChanged.connect(self._update_cmd)
            elif isinstance(w, QCheckBox):
                w.toggled.connect(self._update_cmd)
            elif isinstance(w, QSlider):
                w.valueChanged.connect(self._update_cmd)
            elif isinstance(w, (QSpinBox, QDoubleSpinBox)):
                w.valueChanged.connect(self._update_cmd)
            elif isinstance(w, QLineEdit):
                w.textChanged.connect(self._update_cmd)

        QTimer.singleShot(500, self._check_ff)

    # ── FFmpeg Check ──────────────────────────────────────────────────

    def _check_ff(self):
        try:
            r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5,
                               creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            self.ff_label.setText(f"✅ {r.stdout.split(chr(10))[0]}")
            self.ff_label.setStyleSheet("color: #3fb950; font-size: 11px;")
        except FileNotFoundError:
            self.ff_label.setText("❌ FFmpeg not found!")
            self.ff_label.setStyleSheet("color: #f85149; font-size: 11px;")
            QMessageBox.warning(self, "FFmpeg Not Found",
                                "FFmpeg is not installed or not in PATH.\n\n"
                                "Install from:\n  • https://ffmpeg.org/download.html\n"
                                "  • https://www.gyan.dev/ffmpeg/builds/ (Windows)\n"
                                "  • brew install ffmpeg (macOS)\n"
                                "  • sudo apt install ffmpeg (Linux)")
        except Exception as e:
            self.ff_label.setText(f"⚠ {e}")
            self.ff_label.setStyleSheet("color: #d29922; font-size: 11px;")

    # ── Player Controls ───────────────────────────────────────────────

    def _toggle_play(self):
        if not self.player or not self.input_path:
            return
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.btn_play.setText("▶")
        else:
            self.player.play()
            self.btn_play.setText("⏸")

    def _stop_play(self):
        if not self.player:
            return
        self.player.stop()
        self.btn_play.setText("▶")
        self.timeline.set_position(0)

    def _seek_rel(self, delta: float):
        if not self.player or self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            return
        new = self.player.position() / 1000.0 + delta
        new = max(0, min(new, self.player.duration() / 1000.0))
        self.player.setPosition(int(new * 1000))

    def _skip_to_in(self):
        if not self.player:
            return
        self.player.setPosition(int(self.timeline.in_point * 1000))

    def _skip_to_out(self):
        if not self.player:
            return
        self.player.setPosition(int(self.timeline.out_point * 1000))

    def _set_volume(self, v):
        if self.player and self.audio_out:
            self.audio_out.setVolume(v / 100.0)

    def _on_player_pos(self, ms):
        t = ms / 1000.0
        self.timeline.set_position(t)
        dur = self.player.duration() / 1000.0
        self.time_label.setText(f"{self._fmt(t)} / {self._fmt(dur)}")

    def _on_player_dur(self, ms):
        self.timeline.set_duration(ms / 1000.0)

    def _on_timeline_seek(self, t):
        if self.player:
            self.player.setPosition(int(t * 1000))

    # ── Cut Controls ──────────────────────────────────────────────────

    def _on_cut_toggle(self, on):
        for w in self.cut_widgets:
            w.setEnabled(on)
        self._update_cmd()

    def _on_timeline_in(self, t):
        self.in_spin.blockSignals(True)
        self.in_spin.setValue(t)
        self.in_spin.blockSignals(False)
        self._update_cut_dur()
        self._update_cmd()

    def _on_timeline_out(self, t):
        self.out_spin.blockSignals(True)
        self.out_spin.setValue(t)
        self.out_spin.blockSignals(False)
        self._update_cut_dur()
        self._update_cmd()

    def _on_in_spin(self, v):
        self.timeline.set_in(v)
        self._update_cut_dur()
        self._update_cmd()

    def _on_out_spin(self, v):
        self.timeline.set_out(v)
        self._update_cut_dur()
        self._update_cmd()

    def _set_in_at_pos(self):
        if self.player:
            t = self.player.position() / 1000.0
            self.in_spin.setValue(t)
            self.timeline.set_in(t)

    def _set_out_at_pos(self):
        if self.player:
            t = self.player.position() / 1000.0
            self.out_spin.setValue(t)
            self.timeline.set_out(t)

    def _reset_cut(self):
        self.timeline.reset_cut()
        self.in_spin.setValue(0)
        self.out_spin.setValue(self.timeline.duration)
        self._update_cut_dur()
        self._update_cmd()

    def _update_cut_dur(self):
        d = self.out_spin.value() - self.in_spin.value()
        self.cut_dur_label.setText(f"{d:.3f} s" if d > 0 else "—")

    # ── File Handling ─────────────────────────────────────────────────

    def _browse_file(self):
        p, _ = QFileDialog.getOpenFileName(self, "Select Media File", "",
            "Media Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.ts *.mp3 *.flac *.wav *.ogg *.m4a *.gif *.wmv);;All Files (*)")
        if p:
            self._load_file(p)

    def _on_file_dropped(self, p):
        self._load_file(p)

    def _load_file(self, path: str):
        # Stop previous playback
        if self.player:
            self.player.stop()
            self.btn_play.setText("▶")

        self.input_path = path
        self.drop_zone.set_file(path)
        self.enc_btn.setEnabled(True)
        self.q_btn.setEnabled(True)

        self.log.append(f"<span style='color:#8b949e;'>Probing: {Path(path).name}...</span>")
        QApplication.processEvents()
        self.media_info = probe_media(path)

        p = Path(path)
        dur = self.media_info.get("duration", 0)
        v = self.media_info.get("video", {})
        a = self.media_info.get("audio", {})
        fmt = self.media_info.get("format", {})

        self.info_vals[0].setText(p.name)
        self.info_vals[1].setText(self._fmt(dur))
        self.info_vals[2].setText(v.get("codec", "N/A") or "N/A")
        self.info_vals[3].setText(f"{v.get('width','?')}x{v.get('height','?')}" if v.get("width") else "N/A")
        self.info_vals[4].setText(f"{a.get('codec','N/A')} {a.get('sample_rate','')}" if a.get("codec") else "N/A")
        sz = fmt.get("size", 0)
        self.info_vals[5].setText(self._fmt_size(sz) if sz else "N/A")

        self.log.append(f"<span style='color:#3fb950;'>✔ {p.name} ({self._fmt(dur)})</span>")

        # Set up preview
        self.timeline.set_duration(dur)
        self.in_spin.setMaximum(dur if dur > 0 else 99999)
        self.out_spin.setMaximum(dur if dur > 0 else 99999)
        self.out_spin.setValue(dur)
        self._update_cut_dur()

        if self.player:
            self.preview_stack.setCurrentIndex(1)
            self.player.setSource(QUrl.fromLocalFile(path))
        else:
            self.preview_stack.setCurrentIndex(2)

        if self.auto_name.isChecked():
            self._gen_out_name()
        self._update_cmd()

    def _browse_output(self):
        ext = self.format_combo.currentText()
        p, _ = QFileDialog.getSaveFileName(self, "Output", f"output.{ext}", f"Files (*.{ext});;All (*)")
        if p:
            self.auto_name.setChecked(False)
            self.out_path.setText(p)
            self._update_cmd()

    def _gen_out_name(self):
        if not self.input_path:
            return
        p = Path(self.input_path)
        ext = self.format_combo.currentText()
        suffix = ""
        if self.cut_check.isChecked():
            s = self.in_spin.value()
            e = self.out_spin.value()
            suffix = f"_cut_{s:.1f}s-{e:.1f}s"
        self.out_path.setText(str(p.with_suffix(f"{suffix}.encoded.{ext}")))
        self._update_cmd()

    def _toggle_auto(self, on):
        if on:
            self._gen_out_name()

    # ── Presets ───────────────────────────────────────────────────────

    def _apply_preset(self, name: str):
        pr = PRESETS.get(name, {})
        if not pr:
            return
        vc_map = {"libx264": "libx264 (H.264)", "libx265": "libx265 (H.265/HEVC)",
                  "libvpx-vp9": "libvpx-vp9 (VP9)", "libsvtav1": "libsvtav1 (AV1)",
                  "libaom-av1": "libaom-av1 (AV1)", "copy": "copy (no re-encode)", "none": "none (disable)"}
        vc = pr.get("vcodec", "")
        if vc in vc_map:
            idx = self.vcodec_combo.findText(vc_map[vc])
            if idx >= 0: self.vcodec_combo.setCurrentIndex(idx)
        p = pr.get("preset", "")
        if p:
            idx = self.preset_enc.findText(p)
            if idx >= 0: self.preset_enc.setCurrentIndex(idx)
        self.crf_slider.setValue(pr.get("crf", 23))
        abr = pr.get("audio_bitrate", 128)
        idx = self.audio_br.findText(str(abr))
        if idx >= 0: self.audio_br.setCurrentIndex(idx)
        ac_map = {"aac": "aac", "libmp3lame": "libmp3lame (MP3)", "libopus": "libopus (Opus)",
                  "flac": "flac", "libvorbis": "libvorbis (Vorbis)", "copy": "copy (no re-encode)",
                  "none": "none (disable)"}
        ac = pr.get("acodec", "")
        if ac in ac_map:
            idx = self.acodec_combo.findText(ac_map[ac])
            if idx >= 0: self.acodec_combo.setCurrentIndex(idx)
        fmt = pr.get("format", "mp4")
        idx = self.format_combo.findText(fmt)
        if idx >= 0: self.format_combo.setCurrentIndex(idx)
        res = pr.get("resolution", "source")
        if res in ("source", "none"):
            self.res_combo.setCurrentText("source")
        else:
            found = False
            for i in range(self.res_combo.count()):
                if res in self.res_combo.itemText(i):
                    self.res_combo.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                self.res_combo.setCurrentText("Custom")
                parts = res.split("x")
                if len(parts) == 2:
                    self.cw.setValue(int(parts[0]))
                    self.ch.setValue(int(parts[1]))
        self.faststart.setChecked("-movflags" in " ".join(pr.get("extra", [])) or self.faststart.isChecked())
        self._update_cmd()

    def _toggle_qmode(self, idx):
        self.crf_slider.setEnabled(idx == 0)
        self.crf_label.setEnabled(idx == 0)
        self.bitrate_spin.setEnabled(idx != 0)
        self._update_cmd()

    def _toggle_cres(self, t):
        self.cres_w.setVisible(t == "Custom")

    # ── Command Builder ───────────────────────────────────────────────

    def _build_cmd(self) -> list:
        cmd = ["ffmpeg"]
        if self.overwrite.isChecked():
            cmd.append("-y")
        if self.hwaccel.isChecked():
            cmd.extend(["-hwaccel", "auto"])
        eg = self.extra_global.text().strip()
        if eg:
            cmd.extend(eg.split())
        if self.input_path:
            cmd.extend(["-i", self.input_path])

        # Cut
        if self.cut_check.isChecked():
            inp = self.in_spin.value()
            outp = self.out_spin.value()
            if outp > inp:
                cmd.extend(["-ss", f"{inp:.3f}", "-to", f"{outp:.3f}"])

        # Video
        vc_text = self.vcodec_combo.currentText()
        vc = vc_text.split(" ")[0]
        if vc not in ("copy", "none"):
            filters = []
            res_text = self.res_combo.currentText()
            if res_text == "Custom":
                filters.append(f"scale={self.cw.value()}:{self.ch.value()}")
            elif res_text != "source":
                m = re.match(r'(\d+)x(\d+)', res_text)
                if m:
                    w, h = m.group(1), m.group(2)
                    if self.lanczos_check.isChecked() and vc in ("libx264", "libx265"):
                        filters.append(f"scale={w}:{h}:flags=lanczos")
                    else:
                        filters.append(f"scale={w}:{h}")
            fps_text = self.fps_combo.currentText()
            if fps_text == "Custom":
                filters.append(f"fps={self.cfps.value()}")
            elif fps_text != "source":
                filters.append(f"fps={fps_text}")
            if filters:
                cmd.extend(["-vf", ",".join(filters)])
            cmd.extend(["-c:v", vc])
            pr = self.preset_enc.currentText()
            if vc in ("libx264", "libx265") and pr:
                cmd.extend(["-preset", pr])
            qm = self.quality_mode.currentIndex()
            if qm == 0:
                cmd.extend(["-crf", str(self.crf_slider.value())])
            elif qm == 1:
                cmd.extend(["-b:v", f"{self.bitrate_spin.value()}k", "-pass", "1"])
            else:
                cmd.extend(["-b:v", f"{self.bitrate_spin.value()}k"])
            ev = self.extra_video.text().strip()
            if ev:
                cmd.extend(ev.split())
        elif vc == "copy":
            cmd.extend(["-c:v", "copy"])
        else:
            cmd.extend(["-vn"])

        # Audio
        ac_text = self.acodec_combo.currentText()
        ac = ac_text.split(" ")[0]
        if ac not in ("copy", "none"):
            cmd.extend(["-c:a", ac, "-b:a", f"{self.audio_br.currentText()}k"])
            sr = self.sr_combo.currentText()
            if sr != "source":
                cmd.extend(["-ar", sr])
            ch = self.ch_combo.currentText()
            if ch != "source":
                cmd.extend(["-ac", ch.split(" ")[0]])
            ea = self.extra_audio.text().strip()
            if ea:
                cmd.extend(ea.split())
        elif ac == "copy":
            cmd.extend(["-c:a", "copy"])
        else:
            cmd.extend(["-an"])

        if self.faststart.isChecked() and self.format_combo.currentText() in ("mp4", "mov"):
            cmd.extend(["-movflags", "+faststart"])
        if self.strip_meta.isChecked():
            cmd.extend(["-map_metadata", "-1"])

        out = self.out_path.text().strip()
        if not out and self.input_path:
            p = Path(self.input_path)
            ext = self.format_combo.currentText()
            out = str(p.with_suffix(f".encoded.{ext}"))
        if out:
            cmd.append(out)
        return cmd

    def _update_cmd(self, *_):
        try:
            self.cmd_text.setPlainText(" ".join(self._build_cmd()))
        except Exception:
            pass

    def _copy_cmd(self):
        c = self.cmd_text.toPlainText()
        if c:
            QApplication.clipboard().setText(c)
            self.log.append("<span style='color:#d2a8ff;'>📋 Command copied.</span>")

    # ── Encoding ──────────────────────────────────────────────────────

    def _start_enc(self):
        if not self.input_path:
            return
        cmd = self._build_cmd()
        qm = self.quality_mode.currentIndex()
        if qm == 1:
            self._run_pass(cmd, 1)
        else:
            self._run_pass(cmd, 0)

    def _run_pass(self, base_cmd, pass_num):
        cmd = list(base_cmd)
        if pass_num == 1:
            cmd[-1] = "NUL" if sys.platform == "win32" else "/dev/null"
        label = f"Pass {pass_num}" if pass_num else "Encoding"
        self.log.append(f"<span style='color:#58a6ff;'>═══ {label} ═══</span>")
        self.log.append(f"<span style='color:#8b949e;'>$ {' '.join(cmd)}</span>")
        dur = self.media_info.get("duration", 0)
        if self.cut_check.isChecked():
            dur = self.out_spin.value() - self.in_spin.value()
        self.worker = FFmpegWorker(cmd, dur)
        self.worker.progress.connect(self._on_prog)
        self.worker.output.connect(self._on_log)
        self.worker.finished_signal.connect(lambda c, m: self._on_fin(c, m, base_cmd, pass_num))
        self.worker.duration_found.connect(self._on_dur_found)
        self.enc_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.q_btn.setEnabled(False)
        self.pbar.setValue(0)
        self.s_pct.setText("0%")
        self.s_spd.setText("—")
        self.s_eta.setText("—")
        self.s_br.setText("—")
        self.worker.start()

    def _on_dur_found(self, d):
        self.media_info["duration"] = d

    def _on_prog(self, pct, spd, eta, br):
        self.pbar.setValue(int(pct))
        self.s_pct.setText(f"{pct:.1f}%")
        self.s_spd.setText(spd)
        self.s_eta.setText(self._fmt(eta) if eta > 0 else "—")
        self.s_br.setText(f"{br/1000:.1f} Mbps" if br >= 1000 else f"{br:.0f} kbps" if br > 0 else "—")

    def _on_log(self, line):
        if line and not line.startswith("frame="):
            self.log.append(f"<span style='color:#484f58;'>{line}</span>")

    def _on_fin(self, code, msg, base_cmd, pass_num):
        self.enc_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.q_btn.setEnabled(bool(self.input_path))
        for f in ["ffmpeg2pass-0.log", "ffmpeg2pass-0.log.mbtree"]:
            try: Path(f).unlink(missing_ok=True)
            except: pass
        if code == 0:
            self.log.append(f"<span style='color:#3fb950;'>✔ {msg}</span>")
            self.pbar.setValue(100)
            self.s_pct.setText("100%")
            if pass_num == 1:
                self.log.append("<span style='color:#d2a8ff;'>Starting pass 2...</span>")
                cmd2 = list(base_cmd)
                if "-pass" in cmd2:
                    i = cmd2.index("-pass")
                    cmd2[i + 1] = "2"
                else:
                    for i, c in enumerate(cmd2):
                        if c == "-b:v" and i + 2 < len(cmd2):
                            cmd2.insert(i + 2, "-pass")
                            cmd2.insert(i + 3, "2")
                            break
                self._run_pass(cmd2, 2)
            elif self._queue:
                nxt = self._queue.popleft()
                self.q_label.setText(f"Queue: {len(self._queue)} items")
                self._load_file(nxt)
                self._start_enc()
        else:
            self.log.append(f"<span style='color:#f85149;'>✘ Failed (code {code}): {msg}</span>")

    def _stop_enc(self):
        if self.worker:
            self.worker.stop()
            self.log.append("<span style='color:#d29922;'>⏹ Stopped by user.</span>")

    def _add_queue(self):
        if self.input_path:
            self._queue.append(self.input_path)
            self.q_label.setText(f"Queue: {len(self._queue)} items")
            self.log.append(f"<span style='color:#d2a8ff;'>➕ Queued: {Path(self.input_path).name}</span>")

    # ── Keyboard Shortcuts ────────────────────────────────────────────

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space and self.player and self.input_path:
            # Don't toggle play if a text widget is focused
            fw = self.focusWidget()
            if not isinstance(fw, (QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox)):
                self._toggle_play()
                return
        if event.key() == Qt.Key.Key_I and self.cut_check.isChecked() and self.player:
            self._set_in_at_pos()
            return
        if event.key() == Qt.Key.Key_O and self.cut_check.isChecked() and self.player:
            self._set_out_at_pos()
            return
        if event.key() == Qt.Key.Key_Left and self.player:
            self._seek_rel(-5)
            return
        if event.key() == Qt.Key.Key_Right and self.player:
            self._seek_rel(5)
            return
        super().keyPressEvent(event)

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _fmt(seconds: float) -> str:
        if seconds <= 0:
            return "00:00.00"
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        if h > 0:
            return f"{h}:{m:02d}:{s:05.2f}"
        return f"{m:02d}:{s:05.2f}"

    @staticmethod
    def _fmt_size(b: int) -> str:
        if b >= 1_073_741_824:
            return f"{b / 1_073_741_824:.2f} GB"
        if b >= 1_048_576:
            return f"{b / 1_048_576:.1f} MB"
        if b >= 1024:
            return f"{b / 1024:.1f} KB"
        return f"{b} B"


def main():
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor("#0d1117"))
    pal.setColor(QPalette.ColorRole.WindowText, QColor("#c9d1d9"))
    pal.setColor(QPalette.ColorRole.Base, QColor("#161b22"))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor("#21262d"))
    pal.setColor(QPalette.ColorRole.ToolTipBase, QColor("#161b22"))
    pal.setColor(QPalette.ColorRole.ToolTipText, QColor("#c9d1d9"))
    pal.setColor(QPalette.ColorRole.Text, QColor("#c9d1d9"))
    pal.setColor(QPalette.ColorRole.Button, QColor("#21262d"))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor("#c9d1d9"))
    pal.setColor(QPalette.ColorRole.Highlight, QColor("#1f6feb"))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(pal)
    w = EncoderApp()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
