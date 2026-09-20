import io
import wave

SILENCE_PADDING_MS = 150


def concatenate_wav_segments(segments: list[bytes]) -> bytes:
    if not segments:
        return b""
    if len(segments) == 1:
        return segments[0]

    combined_frames: list[bytes] = []
    reference_params = None
    silence_bytes = b""

    for segment in segments:
        with wave.open(io.BytesIO(segment), "rb") as wav_file:
            params = wav_file.getparams()
            frames = wav_file.readframes(wav_file.getnframes())

            if reference_params is None:
                reference_params = params
                silence_bytes = _generate_silence(params, SILENCE_PADDING_MS)
            elif _format_signature(params) != _format_signature(reference_params):
                raise ValueError("Audio segments have mismatched parameters.")

            combined_frames.append(frames)

    stitched: list[bytes] = []
    for idx, frames in enumerate(combined_frames):
        stitched.append(frames)
        if idx < len(combined_frames) - 1 and silence_bytes:
            stitched.append(silence_bytes)

    output = io.BytesIO()
    with wave.open(output, "wb") as wav_out:
        wav_out.setnchannels(reference_params.nchannels)
        wav_out.setsampwidth(reference_params.sampwidth)
        wav_out.setframerate(reference_params.framerate)
        wav_out.writeframes(b"".join(stitched))

    return output.getvalue()


def _generate_silence(params: wave._wave_params, duration_ms: int) -> bytes:
    if duration_ms <= 0:
        return b""
    frame_count = int(params.framerate * (duration_ms / 1000.0))
    return b"\x00" * frame_count * params.sampwidth * params.nchannels


def _format_signature(params: wave._wave_params) -> tuple[int, int, int, str, str]:
    """Return audio format fields relevant for concatenation (ignore frame count)."""
    return (
        params.nchannels,
        params.sampwidth,
        params.framerate,
        params.comptype,
        params.compname,
    )
