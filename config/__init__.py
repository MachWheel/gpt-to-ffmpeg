import os
import re
from concurrent.futures import ThreadPoolExecutor
from os.path import basename

import PySimpleGUI as sg  # noqa

from . import params, txt, history, download

sg.user_settings_filename(params.UI_SETTINGS_FILE)


def openai_model_cfg():
    """
    Returns the contents of the 'openai-model.cfg' file.
    If the file doesn't exist, creates it with the line 'o1-mini' and returns that line.
    """
    filename = "openai-model.cfg"
    default_model = "o1-mini"
    if not os.path.exists(filename):
        with open(filename, "wt") as file:
            file.write(default_model)
        return default_model

    with open(filename, "rt") as file:
        return file.read().strip()


def existing_ffmpeg_binary():
    return os.path.isfile('ffmpeg.exe')


def get_ffmpeg_binary():
    try:
        with ThreadPoolExecutor() as executor:
            download_task = executor.submit(download.ffmpeg_binary)
            download.show_task(download_task)
    except Exception as err:
        sg.popup('', err, no_titlebar=True)


def update_prompt_history(prompt: str) -> None:
    history.update(
        filename=params.PROMPT_HISTORY_FILE,
        line=prompt
    )


def update_ffmpeg_history(ffmpeg_cmd: str) -> None:
    history.update(
        filename=params.FFMPEG_HISTORY_FILE,
        line=_strip_file_names(ffmpeg_cmd)
    )


def _strip_file_names(ffmpeg_cmd: str):
    """
    Replaces file paths in ffmpeg_cmd with their base names.
    Handles paths in single or double quotation marks.
    """
    pattern = r'["\']([^"\']*)["\']'
    matches = re.findall(pattern, ffmpeg_cmd)
    for match in matches:
        ffmpeg_cmd = ffmpeg_cmd.replace(
            '"' + match + '"',
            '"' + basename(match) + '"'
        )
        ffmpeg_cmd = ffmpeg_cmd.replace(
            "'" + match + "'",
            "'" + basename(match) + "'"
        )
    return ffmpeg_cmd
