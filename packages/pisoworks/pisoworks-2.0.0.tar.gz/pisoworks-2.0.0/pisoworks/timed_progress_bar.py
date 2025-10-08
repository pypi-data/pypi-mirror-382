from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QProgressBar
from PySide6.QtCore import QTimer, QElapsedTimer
from typing import Dict
import math


class TimedProgressBar(QProgressBar):
    """
    A progress bar that automatically progresses from 0 to 100 over a specified duration.
    It uses an internal QTimer to update itself at fixed intervals.

    Features:
    - Customizable duration and update interval.
    - Visibility toggling while retaining layout space.
    - Ability to measure actual elapsed time and update duration accordingly (if desired).
    """
    _elapsed_times: Dict[str, int] = {}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        #self.setVisible(False)  # Initially hidden

        self.duration = 5000  # total time to reach 100%
        self.update_interval = 10  # how often to update
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_progress)
        self._elapsed_timer = QElapsedTimer()

        self._steps = self.duration / self.update_interval
        self._step_value = 100 / self._steps
        self._current_value = 0
        self.setMaximum(100)

    def start(self, default_duration: int = 5000, context: str = ""):
        """
        Start the progress bar from 0. Resets any existing state.
        Starts the internal timer and begins tracking elapsed time.
        """
        self.reset()
        self._current_value = 0
        self.setValue(0)
        #self.setVisible(True)  # Initially hidden
        self.duration = self._elapsed_times.get(context, default_duration)
        self.setMaximum(default_duration)

        # Recalculate steps and increment
        self._steps = self.duration / self.update_interval
        self._step_value = self.maximum() / self._steps

        self._timer.start(self.update_interval)
        self._elapsed_timer.start()

    def reset(self):
        """
        Immediately stop the progress bar and hide it.
        Does not update or preserve elapsed time.
        """
        self._timer.stop()
        self._current_value = 0
        super().reset()

    def stop(self, success: bool, context: str = ""):
        """
        Stop the progress bar and optionally update duration if operation was successful.

        Args:
            success (bool): Whether the operation represented by this progress was successful.
                            If True, the elapsed time is used to update the internal duration
                            so that it becomes more precise for future operations.
        """
        if success and self._elapsed_timer.isValid():
            elapsed = self._elapsed_timer.elapsed()
            if elapsed > 0:
                self._elapsed_times[context] = elapsed

        self._current_value = 0
        self.setValue(0)
        self._timer.stop()
        #self.setVisible(False)

    def update_progress(self):
        """
        Internal slot called on each QTimer timeout.
        Increments the progress bar and stops when 100% is reached.
        """
        decay_progress_start = 0.5  # Start slowing down at 50% progress
        step = self._step_value
        if self._current_value >= (self.maximum() * decay_progress_start):
            progress_ratio = self._current_value / self.maximum()
            slowdown_factor = (1.0 - progress_ratio) / (1.0 - decay_progress_start)  # 1 at 50%, 0 at 100%
            aggressiveness = 0.3  # Adjust this to control how quickly the slowdown kicks in
            decay_strength = math.log2(step + 1)  * aggressiveness # +1 to avoid log(0)
            step = step * (slowdown_factor ** decay_strength)
        
        self._current_value += step
        if self._current_value >= self.maximum():
            self._current_value = self.maximum()
            self.setValue(int(self._current_value))
            self._timer.stop()
            #self.setVisible(False)  # Initially hidden
        else:
            self.setValue(int(self._current_value))



# Example usage in a small application
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout()

    progress_bar = TimedProgressBar()
    start_button = QPushButton("Start")

    def on_start():
        progress_bar.start()

    start_button.clicked.connect(on_start)

    layout.addWidget(progress_bar)
    layout.addWidget(start_button)
    window.setLayout(layout)
    window.setWindowTitle("Timed ProgressBar")
    window.resize(300, 100)
    window.show()

    sys.exit(app.exec())