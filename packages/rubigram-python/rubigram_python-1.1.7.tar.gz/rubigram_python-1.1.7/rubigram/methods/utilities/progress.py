
import sys
import time
from .colors import Colors


class Progress:
    def __init__(self, client=None, object_guid=None):
        self.client = client
        self.object_guid = object_guid
        self.start_time = time.time()
        self.total_size = None
        self.last_uploaded = 0
        self.last_time = self.start_time
        self.msg = None

    async def setup(self):
        if self.client and self.object_guid:
            self.msg = await self.client.send_message(
                self.object_guid,
                "CreateTask.Progress"
            )

    def format_speed(self, speed_bps):
        if speed_bps >= 1024**3:
            return speed_bps / (1024**3), "Gb/s"
        elif speed_bps >= 1024**2:
            return speed_bps / (1024**2), "Mb/s"
        elif speed_bps >= 1024:
            return speed_bps / 1024, "Kb/s"
        else:
            return speed_bps, "B/s"

    def format_size(self, size_bytes):
        if size_bytes >= 1024**3:
            return f"{size_bytes/(1024**3):.2f} Gb"
        elif size_bytes >= 1024**2:
            return f"{size_bytes/(1024**2):.2f} Mb"
        elif size_bytes >= 1024:
            return f"{size_bytes/1024:.2f} Kb"
        else:
            return f"{size_bytes} B"

    async def __call__(
            self,
            total_size: int,
            uploaded_bytes: int,
            state="Uploading") -> None:
        if self.total_size is None:
            self.total_size = total_size

        now = time.time()
        delta_bytes = uploaded_bytes - self.last_uploaded
        delta_time = now - self.last_time
        speed_bps = delta_bytes / delta_time if delta_time > 0 else 0

        speed_val, speed_unit = self.format_speed(speed_bps)

        percent = min(uploaded_bytes / self.total_size * 100, 100)
        current_mb = min(
            uploaded_bytes / (1024 ** 2),
            self.total_size / (1024 ** 2))
        total_mb = self.total_size / (1024 ** 2)

        if percent >= 100:
            percent_color = Colors.GREEN
            current_mb_color = Colors.GREEN
        elif percent >= 99:
            percent_color = Colors.GREEN
            current_mb_color = Colors.MAGENTA
        elif percent >= 75:
            percent_color = Colors.MAGENTA
            current_mb_color = Colors.CYAN
        elif percent >= 50:
            percent_color = Colors.YELLOW
            current_mb_color = Colors.YELLOW
        elif percent >= 25:
            percent_color = Colors.ORANGE
            current_mb_color = Colors.ORANGE
        else:
            percent_color = Colors.RED
            current_mb_color = Colors.RED

        percent_str = f"{percent_color}{percent:6.2f}%{Colors.RESET}"
        current_mb_str = f"{current_mb_color}{current_mb:.2f}MB{Colors.RESET}"
        total_mb_str = f"{Colors.MAGENTA}{total_mb:.2f}MB{Colors.RESET}"
        tps_str = f"{Colors.ORANGE}TPS{Colors.RESET}"
        speed_str = f"{
            Colors.GREEN} {
            speed_val: .2f} {
            Colors.RESET}  {
            Colors.CYAN} {speed_unit} {
            Colors.RESET} "

        terminal_str = f"{percent_str}  [{current_mb_str} /{total_mb_str}] {
            tps_str}  {speed_str} "
        sys.stdout.write(f"\r{terminal_str}")
        sys.stdout.flush()

        if self.client and self.object_guid and self.msg:
            msg_str = f"{
                percent: .2f} % [{
                current_mb: .2f} /{
                total_mb: .2f}] {
                speed_val: .2f}  {speed_unit} "
            if uploaded_bytes >= self.total_size:
                total_time = now - self.start_time
                avg_speed_bps = self.total_size / total_time
                avg_speed_val, avg_speed_unit = self.format_speed(
                    avg_speed_bps)
                msg_str = (
                    f"FileProgress\n"
                    f"State: Complete\n"
                    f"Size: {self.format_size(self.total_size)}\n"
                    f"Time: {total_time:.2f}s\n"
                    f"Average Speed: {avg_speed_val:.2f} {avg_speed_unit}"
                )
            await self.client.edit_message(
                self.object_guid,
                self.msg.message_update.message_id,
                msg_str
            )

        self.last_uploaded = uploaded_bytes
        self.last_time = now

        if uploaded_bytes >= self.total_size:
            print()
