import rubigram
import asyncio
import pathlib
import subprocess
import uuid
import os

try:
    import aiortc
    from aiortc.contrib.media import MediaPlayer
except ImportError:
    aiortc = None


class VoiceChatPlayer:
    async def heartbeat(
            self: "rubigram.Client",
            chat_guid: str,
            voice_chat_id: str) -> None:
        while True:
            try:
                await self.get_group_voice_chat_updates(chat_guid, voice_chat_id, int(asyncio.get_event_loop().time()))
                await asyncio.sleep(10)
            except (rubigram.exceptions.InvalidAuth, rubigram.exceptions.InvalidInput):
                break
            except Exception:
                await asyncio.sleep(5)

    async def speaking(
            self: "rubigram.Client",
            chat_guid: str,
            voice_chat_id: str) -> None:
        while True:
            try:
                await self.send_group_voice_chat_activity(chat_guid, voice_chat_id)
                await asyncio.sleep(10)
            except (rubigram.exceptions.InvalidAuth, rubigram.exceptions.InvalidInput):
                break
            except Exception:
                await asyncio.sleep(5)

    async def _cleanup_temp_file(self, path: str) -> None:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    async def voice_chat_player(
        self: "rubigram.Client",
        chat_guid: str,
        media: str | pathlib.Path,
        loop: bool = False,
        start_time: str = "0:00",
        volume: int = 100
    ) -> bool:
        if aiortc is None:
            return False

        media_path = pathlib.Path(media) if isinstance(media, str) else media
        seconds = 0
        try:
            m, s = map(int, start_time.strip().split(":"))
            seconds = m * 60 + s
        except Exception:
            pass

        volume = max(0, min(volume, 100))
        vol_db = -60 if volume == 0 else 20 * (volume / 100) - 20

        temp_path = None
        if seconds > 0 or volume != 100:
            temp_path = f"/storage/emulated/0/temp_{uuid.uuid4().hex}.mp3"
            cmd = [
                "ffmpeg", "-y", "-i", str(media_path),
                "-ss", str(seconds),
                "-vn", "-af", f"volume={vol_db}dB",
                "-acodec", "libmp3lame",
                temp_path
            ]
            try:
                subprocess.run(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True)
                media_path = pathlib.Path(temp_path)
            except Exception:
                return False

        chat_info = await self.get_info(chat_guid)
        voice_chat_id = chat_info.chat.find_keys(
            f"{'group' if chat_guid.startswith('g0') else 'channel'}_voice_chat_id"
        )

        if voice_chat_id is None:
            if chat_guid.startswith("g0"):
                voice_chat = await self.create_group_voice_chat(chat_guid)
                voice_chat_id = voice_chat.find_keys("voice_chat_id") or getattr(
                    voice_chat.group_voice_chat_update, "voice_chat_id", None)
            else:
                voice_chat = await self.create_channel_voice_chat(chat_guid)
                voice_chat_id = voice_chat.find_keys("voice_chat_id") or getattr(
                    voice_chat.channel_voice_chat_update, "voice_chat_id", None)

        pc = aiortc.RTCPeerConnection()
        player = MediaPlayer(str(media_path), format=media_path.suffix[1:])

        class AudioFileTrack(aiortc.MediaStreamTrack):
            kind = "audio"

            def __init__(self, player):
                super().__init__()
                self.player = player

            async def recv(self):
                return await self.player.audio.recv()

        track = AudioFileTrack(player)
        pc.addTrack(track)

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        connect = await self.join_voice_chat(chat_guid, voice_chat_id, offer.sdp)
        sdp_answer = connect.sdp_answer_data

        await self.set_voice_chat_state(chat_guid, voice_chat_id)
        asyncio.create_task(self.speaking(chat_guid, voice_chat_id))
        asyncio.create_task(self.heartbeat(chat_guid, voice_chat_id))

        remote_desc = aiortc.RTCSessionDescription(sdp_answer, "answer")
        await pc.setRemoteDescription(remote_desc)

        def cleanup_on_disconnect():
            asyncio.create_task(self._cleanup_temp_file(temp_path))

        @pc.on("iceconnectionstatechange")
        def on_iceconnectionstatechange():
            if pc.iceConnectionState in ("failed", "disconnected", "closed"):
                cleanup_on_disconnect()

        @pc.on("connectionstatechange")
        def on_connectionstatechange():
            if pc.connectionState in ("failed", "disconnected", "closed"):
                cleanup_on_disconnect()

        return True
