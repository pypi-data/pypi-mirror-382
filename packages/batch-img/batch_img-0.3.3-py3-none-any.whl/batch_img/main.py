"""class Main: the entry point of the tool
Copyright © 2025 John Liu
"""

import json
from pathlib import Path
from time import time

from loguru import logger as log

from batch_img.auto import Auto
from batch_img.border import Border
from batch_img.common import Common
from batch_img.const import PKG_NAME, REPLACE
from batch_img.do_effect import DoEffect
from batch_img.log import Log
from batch_img.no_gps import NoGps
from batch_img.remove_bg import RemoveBg
from batch_img.resize import Resize
from batch_img.rotate import Rotate
from batch_img.transparent import Transparent


class Main:
    @staticmethod
    def _prepare(options: dict) -> float:
        """Prepare the start for all (internal helper)

        Args:
            options: input options dict

        Returns:
            float: start timestamp in seconds
        """
        Log.init_log_file()
        log.debug(f"{json.dumps(options, indent=2)}")
        return time()

    @staticmethod
    def _conclude(start_ts: float) -> str:
        """Conclude the end for all (internal helper)

        Args:
            start_ts: float

        Returns:
            str: human-readable elapsed time string
        """
        Common.check_latest_version(PKG_NAME)
        duration = Common.human_readable_time(time() - start_ts)
        log.info(f"Elapsed time: {duration}")
        return duration

    @staticmethod
    def auto(options: dict) -> bool:
        """Auto process image file(s):
        * Resize to 1920-pixel max length
        * Add 5-pixel width black color border
        * Remove GPS location info

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        start_ts = Main._prepare(options)
        in_path = Path(options["src_path"])
        auto_rotate = options.get("auto_rotate")
        output = options.get("output")
        out = Path(output) if output else REPLACE
        log.info(
            "Resize to 1920-pixel max length. Remove GPS location info."
            " Add 5-pixel width black color border."
        )
        if in_path.is_file():
            ok, _ = Auto.auto_do_1_image((in_path, out, auto_rotate))
        else:
            ok = Auto.auto_on_all(in_path, out, auto_rotate)
        Main._conclude(start_ts)
        return ok

    @staticmethod
    def border(options: dict) -> bool:
        """Add border to the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        start_ts = Main._prepare(options)
        in_path = Path(options["src_path"])
        bd_width = options.get("border_width")
        if not bd_width or bd_width == 0:
            log.error(f"Bad border width: {bd_width=}")
            return False
        bd_color = options.get("border_color")
        if not bd_color:
            log.error(f"Bad border color: {bd_color=}")
            return False
        output = options.get("output")
        out = Path(output) if output else REPLACE
        if in_path.is_file():
            ok, _ = Border.border_1_image((in_path, out, bd_width, bd_color))
        else:
            ok = Border.border_all_in_dir(in_path, out, bd_width, bd_color)
        Main._conclude(start_ts)
        return ok

    @staticmethod
    def do_effect(options: dict) -> bool:
        """Add a special effect to the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        start_ts = Main._prepare(options)
        in_path = Path(options["src_path"])
        effect = options.get("effect")
        if not effect:
            log.error(f"Bad border width: {effect=}")
            return False
        output = options.get("output")
        out = Path(output) if output else ""
        if in_path.is_file():
            ok, _ = DoEffect.apply_1_image((in_path, out, effect))
        else:
            ok = DoEffect.apply_all_in_dir(in_path, out, effect)
        Main._conclude(start_ts)
        return ok

    @staticmethod
    def remove_bg(options) -> bool:
        """Remove background (make background transparent)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        start_ts = Main._prepare(options)
        in_path = Path(options["src_path"])
        output = options.get("output")
        out = Path(output) if output else REPLACE
        if in_path.is_file():
            ok, _ = RemoveBg.remove_bg_image((in_path, out))
        else:
            ok = RemoveBg.remove_all_images_bg(in_path, out)
        Main._conclude(start_ts)
        return ok

    @staticmethod
    def remove_gps(options) -> bool:
        """Remove GPS location info in image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        start_ts = Main._prepare(options)
        in_path = Path(options["src_path"])
        output = options.get("output")
        out = Path(output) if output else REPLACE
        if in_path.is_file():
            ok, _ = NoGps.remove_1_image_gps((in_path, out))
        else:
            ok = NoGps.remove_all_images_gps(in_path, out)
        Main._conclude(start_ts)
        return ok

    @staticmethod
    def resize(options: dict) -> bool:
        """Resize the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        start_ts = Main._prepare(options)
        in_path = Path(options["src_path"])
        length = options.get("length")
        if not length or length == 0:
            log.error(f"No resize due to bad {length=}")
            return False
        output = options.get("output")
        out = Path(output) if output else REPLACE
        if in_path.is_file():
            ok, _ = Resize.resize_an_image((in_path, out, length))
        else:
            ok = Resize.resize_all_progress_bar(in_path, out, length)
        Main._conclude(start_ts)
        return ok

    @staticmethod
    def rotate(options: dict) -> bool:
        """Rotate the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        start_ts = Main._prepare(options)
        in_path = Path(options["src_path"])
        angle = options.get("angle")
        if not angle or angle == 0:
            log.error(f"No rotate due to bad {angle=}")
            return False
        output = options.get("output")
        out = Path(output) if output else REPLACE
        if in_path.is_file():
            ok, _ = Rotate.rotate_1_image((in_path, out, angle))
        else:
            ok = Rotate.rotate_all_in_dir(in_path, out, angle)
        Main._conclude(start_ts)
        return ok

    @staticmethod
    def transparent(options: dict) -> bool:
        """Set transparency the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        start_ts = Main._prepare(options)
        in_path = Path(options["src_path"])
        transparency = options.get("transparency")
        if not transparency or transparency < 0 or transparency > 255:
            log.error(f"Skip due to bad data {transparency=}")
            return False
        white = options.get("white", False)
        output = options.get("output")
        out = Path(output) if output else REPLACE
        if in_path.is_file():
            args = (in_path, out, transparency, white)
            ok, _ = Transparent.do_1_image_transparency(args)
        else:
            ok = Transparent.all_images_transparency(in_path, out, transparency, white)
        Main._conclude(start_ts)
        return ok
