import sys
import re
import time
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor, Future
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QProgressBar,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QMenuBar,
)
from PyQt6.QtGui import QPixmap, QFont, QTextCursor, QIcon, QDesktopServices, QAction
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QMutex, QThread, QUrl

# ---- HoyoSophon modules ----
from HoyoSophonDL import HoyoSophonDL, Branch, Region
from HoyoSophonDL.download import GlobalDownloadData
from HoyoSophonDL.help import format_bytes
from HoyoSophonDL.structs.GamesInfo import AvaliableGame
from HoyoSophonDL.structs.SophonManifest import SophonManifestProtoAssets
import sys, os

def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and PyInstaller.
    """
    try:
        # PyInstaller stores temp files in a folder inside _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ------------------ Log Stream ------------------ #
class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._mutex = QMutex()

    def write(self, text):
        if text:
            self._mutex.lock()
            try:
                self.text_written.emit(str(text))
            finally:
                self._mutex.unlock()

    def flush(self):
        pass


# ------------------ Refresh Worker ------------------ #
class RefreshWorker(QThread):
    finished_signal = pyqtSignal(object)
    log_signal = pyqtSignal(str)

    def __init__(self, launcher: HoyoSophonDL, args=None):
        super().__init__()
        self.launcher = launcher
        self.get_assets = args

    def run(self):
        try:
            if isinstance(self.get_assets, AvaliableGame):
                games = self.launcher.get_game_info(self.get_assets)
            elif self.get_assets is not None:
                games = self.launcher.get_assets_info(*self.get_assets)
            else:
                self.log_signal.emit("[INFO] Refreshing games list...")
                games = self.launcher.get_available_games()
            self.finished_signal.emit(games)
        except Exception as e:
            self.log_signal.emit(f"[ERROR] Refresh failed: {e}")
            self.finished_signal.emit(None)


# ------------------ Download Worker ------------------ #
class DownloadWorker(QObject):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(
        self,
        launcher: HoyoSophonDL,
        assets: SophonManifestProtoAssets,
        output_dir: str,
        workers: int = 20,
    ):
        super().__init__()
        self.launcher = launcher
        self.assets = assets
        self.output_dir = output_dir
        self.workers = workers
        self._executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)
        self._future: Future | None = None

    def start(self):
        self.log_signal.emit("[INFO] Starting download...")
        self._future = self._executor.submit(self._run_download)
        QTimer.singleShot(200, self._poll_progress)

    def _run_download(self) -> bool:
        try:
            self.log_signal.emit("[INFO] Download thread running...")

            self.launcher.download_assets(
                self.launcher.set_download_assets(
                    self.assets, self.output_dir, self.workers
                ),
                self._on_progress,
                self._on_finish,
                self._on_cancel,
                self._on_pause,
            )
            self.log_signal.emit("[INFO] Download finished.")
            return True
        except Exception as e:
            self.log_signal.emit(f"[ERROR] {e}")
            return False

    def _emit_status(self, state: str | None, trace: GlobalDownloadData):
        pct = int(getattr(trace, "FloatPercent", 0) or 0)
        self.progress_signal.emit(pct)
        self.status_signal.emit(
            (f"[{state}] ==> " if state else "") + f"({self.assets.GameData.Name}) "
            f"[{trace.CompletedChunks}/{trace.TotalChunksCount} chunks] "
            f"[{trace.CompletedAssets}/{trace.TotalAssetsCount} assets] "
            f"[{format_bytes(trace.TotalDownloadBytes)}/{trace.TotalFSize}] "
            f"{trace.Percent}"
        )

    def _on_progress(self, trace: GlobalDownloadData):
        self._emit_status(None, trace)

    def _on_finish(self, trace: GlobalDownloadData):
        self._emit_status("Completed", trace)

    def _on_cancel(self, trace: GlobalDownloadData):
        self._emit_status("Cancelled", trace)

    def _on_pause(self, trace: GlobalDownloadData):
        # downloader will call pause callback once it's safe to pause
        self._emit_status("Paused", trace)

    def _poll_progress(self):
        if self.launcher.trace_download.cancel_event.is_set():
            self.log_signal.emit("[INFO] Download canceled.")
            self.finished_signal.emit(False)
            return
        if not self._future:
            return
        if self._future.done():
            try:
                success = bool(self._future.result())
            except Exception:
                success = False
            self.finished_signal.emit(success)
            return
        QTimer.singleShot(200, self._poll_progress)


# ------------------ Main GUI ------------------ #
class LauncherGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HoYoPlaySophonDownloader - By: Mr.Jo0x01 ♥")
        self.setWindowIcon(QIcon(resource_path("assets/hoyo.ico")))
        self.resize(920, 750)

        self.main_layout = QVBoxLayout(self)

        # ---- Pause/Waiting flags
        self.is_paused = False  # True when fully paused
        self.waiting_for_pause = (
            False  # True between clicking Pause and downloader confirming pause
        )

        # ---- Menu bar
        menu_bar = QMenuBar(self)
        about_action = QAction(QIcon(), "About", self)
        about_action.triggered.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/Jo0X01")
            )
        )
        menu_bar.addAction(about_action)
        self.main_layout.setMenuBar(menu_bar)

        # ---- Banner
        self.banner = QLabel()
        self.banner.setFixedHeight(360)
        self.banner.setStyleSheet("background:#333; border-radius:10px;")
        self.main_layout.addWidget(self.banner)

        self.overlay_icon = QLabel(self.banner)
        self.overlay_icon.setGeometry(10, 220, 120, 120)
        self.overlay_logo = QLabel(self.banner)
        self.overlay_logo.setGeometry(10, 60, 120, 120)
        self.overlay_name = QLabel("Choose a game to start", self.banner)
        self.overlay_name.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.overlay_name.setStyleSheet("color:white;background:transparent;")
        self.overlay_name.move(150, 180)

        # ---- Controls
        self.controls_layout = QHBoxLayout()
        self.main_layout.addLayout(self.controls_layout)

        self.branch_combo = QComboBox()
        self.branch_combo.addItems([b.value for b in Branch])
        self.region_combo = QComboBox()
        self.region_combo.addItems([r.value for r in Region])
        self.verbose_checkbox = QCheckBox("Verbose")

        self.game_combo = QComboBox()
        self.game_combo.addItem("Select Game...")
        self.category_combo = QComboBox()
        self.category_combo.addItem("Select category")
        self.current_version_combo = QComboBox()
        self.current_version_combo.addItem("Latest version")
        self.update_version_combo = QComboBox()
        self.update_version_combo.addItem("Latest version")

        self.download_btn = QPushButton("Start Download")
        self.pause_btn = QPushButton("Pause")
        self.cancel_btn = QPushButton("Cancel")
        self.pause_btn.hide()
        self.cancel_btn.hide()

        for w in (
            self.game_combo,
            self.category_combo,
            self.current_version_combo,
            self.update_version_combo,
            self.branch_combo,
            self.region_combo,
        ):
            self.controls_layout.addWidget(w)
        self.controls_layout.addWidget(self.download_btn)
        self.controls_layout.addWidget(self.pause_btn)
        self.controls_layout.addWidget(self.cancel_btn)
        self.controls_layout.addWidget(self.verbose_checkbox)

        # ---- Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #444;
                border-radius: 8px;
                background: #222;
                color: white;
                text-align: center;
                height: 28px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4caf50, stop:1 #81c784
                );
                border-radius: 6px;
            }
        """
        )
        self.main_layout.addWidget(self.progress_bar)

        # ---- Status label
        self.status_label = QLabel("Status: Waiting for game selection...")
        self.status_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #00bcd4; padding: 4px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_label)

        # ---- Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.main_layout.addWidget(self.log_output)

        # ---- Loading animation
        self.loading_label = QLabel("")
        self.main_layout.addWidget(self.loading_label)
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self._loading_tick)
        self._loading_step = 0

        # ---- Redirect stdout/stderr
        self.emitter_stdout = EmittingStream()
        self.emitter_stdout.text_written.connect(self.append_log)
        sys.stdout = self.emitter_stdout
        self.emitter_stderr = EmittingStream()
        self.emitter_stderr.text_written.connect(self.append_log)
        sys.stderr = self.emitter_stderr

        # ---- Signals
        self.branch_combo.currentIndexChanged.connect(self._on_launcher_options_changed)
        self.region_combo.currentIndexChanged.connect(self._on_launcher_options_changed)
        self.verbose_checkbox.stateChanged.connect(self._on_launcher_options_changed)
        self.game_combo.currentIndexChanged.connect(self._on_game_selected)
        self.download_btn.clicked.connect(self.start_download)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.cancel_btn.clicked.connect(self.cancel_download)

        # ---- Launcher
        self.launcher = HoyoSophonDL(
            branch=Branch(self.branch_combo.currentText()),
            region=Region(self.region_combo.currentText()),
            verbose=self.verbose_checkbox.isChecked(),
        )

        self.games_dict = {}
        self.worker = None

        self.refresh_games()

    def closeEvent(self, event):
        """Triggered when the window is closed."""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit? Ongoing downloads will be stopped.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            event.ignore()
            return

        # Try to cancel background downloads
        try:
            if self.launcher.trace_download:
                self.launcher.trace_download.cancel_event.set()
                time.sleep(0.3)
        except Exception as e:
            print(f"Error stopping downloader: {e}")
        QApplication.quit()

    # ---------- Loading animation ----------
    def _loading_tick(self):
        dots = "." * (self._loading_step % 4)
        self.loading_label.setText(f"Loading{dots}")
        self._loading_step += 1

    # ---------- Logging ----------
    def append_log(self, text: str):
        text = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]").sub("", str(text))
        up = text.upper()
        if "ERROR" in up:
            color = "red"
        elif "WARN" in up:
            color = "orange"
        elif "INFO" in up:
            color = "cyan"
        elif "DEBUG" in up:
            color = "purple"
        elif "SUCCESS" in up:
            color = "green"
        else:
            color = "white"
        safe_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.log_output.append(f'<span style="color:{color}">{safe_text}</span>')
        cursor = self.log_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_output.setTextCursor(cursor)
        self.log_output.ensureCursorVisible()

    # ---------- Refresh / populate games ----------
    def refresh_games(self):
        self.disable_inputs(True)
        self.loading_label.setText("")
        self._loading_step = 0
        self.loading_timer.start(300)
        self.launcher = HoyoSophonDL(
            branch=Branch(self.branch_combo.currentText()),
            region=Region(self.region_combo.currentText()),
            verbose=self.verbose_checkbox.isChecked(),
        )
        self._refresh_worker = RefreshWorker(self.launcher)
        self._refresh_worker.log_signal.connect(self.append_log)
        self._refresh_worker.finished_signal.connect(self._on_games_refreshed)
        self._refresh_worker.start()

    def _on_games_refreshed(self, games_obj):
        self.loading_timer.stop()
        self.loading_label.setText("")
        self.disable_inputs(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Status: Waiting for game selection...")
        if not games_obj:
            self.append_log("[WARN] Could not fetch games.")
            return
        self.games_dict = {g.Name: g for g in games_obj.Games}
        self.game_combo.clear()
        self.game_combo.addItem("Select Game...")
        for g in games_obj.Games:
            self.game_combo.addItem(g.Name)
        self._on_game_selected(0)

    # ---------- Game info ----------
    def _on_game_selected(self, index):
        self.progress_bar.setValue(0)
        self.status_label.setText("Status: Waiting for game selection...")
        game_name = self.game_combo.currentText()
        if game_name == "Select Game...":
            self._clear_game_info()
            return
        game = self.games_dict.get(game_name)
        if not game:
            return
        self._refresh_worker = RefreshWorker(self.launcher, game)
        self._refresh_worker.log_signal.connect(self.append_log)
        self._refresh_worker.finished_signal.connect(self._on_game_info_fetched)
        self._refresh_worker.start()

    def _on_game_info_fetched(self, info):
        self.disable_inputs(True)
        self.loading_label.setText("")
        self._loading_step = 0
        self.loading_timer.start(300)
        game = info.GameData
        self.overlay_name.setText(game.Name)
        try:
            data = urlopen(game.Background).read()
            pix = QPixmap()
            pix.loadFromData(data)
            self.banner.setPixmap(
                pix.scaled(
                    self.banner.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            data = urlopen(game.Icon).read()
            pix2 = QPixmap()
            pix2.loadFromData(data)
            self.overlay_icon.setPixmap(
                pix2.scaled(
                    self.overlay_icon.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            data = urlopen(game.Logo).read()
            pix2 = QPixmap()
            pix2.loadFromData(data)
            self.overlay_logo.setPixmap(
                pix2.scaled(
                    self.overlay_logo.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        except Exception:
            self.overlay_icon.clear()
            self.overlay_logo.clear()
            self.banner.clear()

        self.category_combo.clear()
        self.category_combo.addItems(info.getCategoryByName())
        self.current_version_combo.clear()
        self.current_version_combo.addItem("Latest version")
        self.current_version_combo.addItems(
            [info.LastVersion] + (info.OtherVersion or [])
        )
        self.update_version_combo.clear()
        self.update_version_combo.addItem("Latest version")
        self.update_version_combo.addItems(
            [info.LastVersion] + (info.OtherVersion or [])
        )
        self.status_label.setText(f"Status: Last Version {info.LastVersion}")
        self.loading_timer.stop()
        self.loading_label.setText("")
        self.disable_inputs(False)

    def _clear_game_info(self):
        self.overlay_name.setText("Choose a game to start")
        self.overlay_icon.clear()
        self.overlay_logo.clear()
        self.banner.clear()
        self.category_combo.clear()
        self.category_combo.addItem("Select category")
        self.current_version_combo.clear()
        self.current_version_combo.addItem("Latest version")
        self.update_version_combo.clear()
        self.update_version_combo.addItem("Latest version")

    # ---------- Download ----------
    def start_download(self):
        game_name = self.game_combo.currentText()
        if game_name == "Select Game...":
            self.append_log("[WARN] Please select a game first.")
            return
        self.download_btn.hide()
        self.disable_inputs(True)
        self.loading_label.setText("")
        self._loading_step = 0
        self.loading_timer.start(300)
        category = self.category_combo.currentText()
        current_version = self.current_version_combo.currentText()
        update_version = self.update_version_combo.currentText()
        info = self.launcher.get_game_by_source(game_name)
        game_info = self.launcher.get_game_info(info)
        if current_version == "Latest version":
            current_version = None
        if update_version == "Latest version":
            update_version = game_info.LastVersion
        self._refresh_worker = RefreshWorker(
            self.launcher, (info, current_version, update_version, category)
        )
        self._refresh_worker.log_signal.connect(self.append_log)
        self._refresh_worker.finished_signal.connect(self._on_assets_fetched)
        self._refresh_worker.start()

    def _on_assets_fetched(self, assets: SophonManifestProtoAssets):
        self.loading_timer.stop()
        self.loading_label.setText("")
        if assets is None:
            QMessageBox.warning(self, "Error", "Failed to fetch assets.")
            self.download_btn.show()
            self.disable_inputs(False)
            return

        reply = QMessageBox.question(
            self,
            "Confirm Download",
            f"Game: {assets.GameData.Name}\nCategory: {assets.AssetCategory}\n"
            f"Current Version: {assets.version or 'Full download'}\n"
            f"Update Version: {assets.update_from}\n"
            f"Download Size: {assets.TotalFSize}\n"
            f"Total Files: {assets.FilesCount}\n"
            f"Total Chunks: {assets.ChunksCount}\n"
            "Start download?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.No:
            self.download_btn.show()
            self.disable_inputs(False)
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if not output_dir:
            QMessageBox.warning(self, "Error", "No output directory selected.")
            self.download_btn.show()
            self.disable_inputs(False)
            return

        self.disable_inputs(True)
        self.loading_label.setText("")
        self._loading_step = 0
        self.loading_timer.start(300)
        self.download_btn.hide()
        self.pause_btn.setDisabled(False)
        self.cancel_btn.setDisabled(False)
        self.pause_btn.show()
        self.cancel_btn.show()
        self.progress_bar.setValue(0)
        self.status_label.setText("Status: Preparing download...")

        # start worker
        self.worker = DownloadWorker(self.launcher, assets, output_dir)
        self.worker.progress_signal.connect(self._update_progress)
        self.worker.status_signal.connect(self._update_status)
        self.worker.log_signal.connect(self.append_log)
        self.worker.finished_signal.connect(self._on_download_finished)
        self.worker.start()

    # ---------- Update slots ----------
    def _update_progress(self, percent: int):
        # always update progress bar (user should see chunk finishing)
        try:
            self.progress_bar.setValue(percent)
        except Exception:
            pass

    def _update_status(self, status: str):
        """
        Handle incoming status updates from worker.
        If we're waiting for pause confirmation, freeze main label until downloader emits 'Paused'.
        Once fully paused, ignore new progress/status updates until resume.
        """
        status_text = status or ""
        # If cancel event set, prefer showing canceled
        if self.launcher.trace_download.cancel_event.is_set():
            self.status_label.setText("✖ Canceling...")
            return

        # If we are waiting for pause (user clicked Pause), show "Pausing..." and ignore worker messages
        if self.waiting_for_pause:
            # if worker confirms paused (it will emit a status containing 'Paused'), catch it
            if "Paused" in status_text or "[Paused]" in status_text:
                self.waiting_for_pause = False
                self.is_paused = True
                self.pause_btn.setText("Resume")
                self.pause_btn.setDisabled(False)
                self.status_label.setText("⏸ Paused")
                self.append_log("[INFO] Download is now paused.")
            else:
                # show temporary pausing message (do not let worker status override it)
                self.status_label.setText("⏸ Pausing current chunk...")
            return

        # If fully paused, ignore status updates (no flicker)
        if self.is_paused:
            return

        # Normal operation: update status label based on worker text
        # Simplify the worker status into a shorter string for readability
        # Try to extract bytes/percent tail
        tail = ""
        m = re.search(r"\[([^\]]+/[^\]]+)\]\s*([0-9.]+%$)", status_text)
        if m:
            tail = f"{m.group(1)} • {m.group(2)}"
        else:
            # fallback to last token if percent present
            if "%" in status_text:
                tail = status_text.strip().split()[-1]
            else:
                tail = status_text

        # set main label (with small icon)
        if "Completed" in status_text or "[Completed]" in status_text:
            self.status_label.setText("✅ Completed")
        elif "Cancelled" in status_text or "[Cancelled]" in status_text:
            self.status_label.setText("✖ Cancelled")
        else:
            # Show active download with basic info
            # Try to extract game name
            gm = re.search(r"\(([^)]+)\)", status_text)
            game_part = gm.group(1) if gm else ""
            if game_part:
                self.status_label.setText(f"⬇ Downloading: {game_part} — {tail}")
            else:
                self.status_label.setText(f"⬇ Downloading — {tail}")

    # ---------- Pause / Cancel ----------
    def toggle_pause(self):
        trace = self.launcher.trace_download
        # if already paused -> resume
        if trace.pause_event.is_set() or self.is_paused:
            # request resume
            trace.pause_event.clear()
            # clear paused state
            self.is_paused = False
            self.waiting_for_pause = False
            self.pause_btn.setDisabled(True)
            self.status_label.setText("▶ Resuming...")
            self.append_log("[INFO] Resume requested.")
            # re-enable after short delay so worker has time to restart
            QTimer.singleShot(600, lambda: self.pause_btn.setDisabled(False))
            self.pause_btn.setText("Pause")
            return

        trace.pause_event.set()
        self.waiting_for_pause = True
        self.is_paused = False
        self.pause_btn.setDisabled(True)
        self.status_label.setText("⏸ Pausing current chunk...")
        self.append_log(
            "[INFO] Pause requested; waiting for current chunk to finish..."
        )
        # if pause confirmation never comes (network issues), re-enable the pause button after a timeout
        QTimer.singleShot(1000, self._pause_timeout)

    def _pause_timeout(self):
        # If still waiting for pause after timeout, allow user to resume/poke again
        if self.waiting_for_pause and not self.is_paused:
            self.waiting_for_pause = False
            self.is_paused = (
                True  # treat as paused to avoid endless waiting (best-effort)
            )
            self.pause_btn.setDisabled(False)
            self.pause_btn.setText("Resume")
            self.status_label.setText("⏸ Paused (forced timeout)")
            self.append_log(
                "[WARN] Pause confirmation timed out; entering best-effort paused state."
            )

    def cancel_download(self):
        trace = self.launcher.trace_download
        trace.cancel_event.set()
        trace.pause_event.clear()
        # reset flags so UI will accept final updates
        self.waiting_for_pause = False
        self.is_paused = False
        self.append_log("[INFO] Cancel requested by user.")
        self.status_label.setText("✖ Canceling...")
        # the worker.poll will catch cancel and finish

    # ---------- Download finished ----------
    def _on_download_finished(self, success: bool):
        # ensure pause flags cleared
        self.waiting_for_pause = False
        self.is_paused = False

        self.loading_timer.stop()
        self.loading_label.setText("")
        self.pause_btn.hide()
        self.cancel_btn.hide()
        self.download_btn.show()
        self.disable_inputs(False)

        if success and not self.launcher.trace_download.cancel_event.is_set():
            self.status_label.setText("✅ Download completed successfully.")
            self.append_log("[SUCCESS] Download completed.")
        elif self.launcher.trace_download.cancel_event.is_set():
            self.status_label.setText("✖ Download canceled.")
            self.append_log("[INFO] Download canceled.")
        else:
            self.status_label.setText("✖ Download failed or cancelled.")
            self.append_log("[ERROR] Download failed or cancelled.")

    # ---------- Utilities ----------
    def disable_inputs(self, disable: bool):
        for w in (
            self.game_combo,
            self.category_combo,
            self.current_version_combo,
            self.update_version_combo,
            self.branch_combo,
            self.region_combo,
            self.verbose_checkbox,
        ):
            w.setDisabled(disable)

    def _on_launcher_options_changed(self):
        self.refresh_games()

def run_gui_pyqt6():
    app = QApplication(sys.argv)
    gui = LauncherGUI()
    gui.show()
    sys.exit(app.exec())
