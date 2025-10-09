"""class RemoveBg - Remove background (make background transparent) in image file(s)
Copyright © 2025 John Liu
"""

import os
from pathlib import Path

import piexif
import pillow_heif
from loguru import logger as log
from PIL import Image
from rembg import remove

from batch_img.common import Common
from batch_img.const import EXIF, REPLACE

pillow_heif.register_heif_opener()


class RemoveBg:
    @staticmethod
    def remove_bg_image(args: tuple) -> tuple:
        """Remove background (make background transparent) in an image file

        Args:
            args: tuple of the below params:
            in_path: input file path
            out_path: output dir path or REPLACE

        Returns:
            tuple: bool, output file path
        """
        in_path, out_path = args
        Common.set_log_by_process()
        try:
            with Image.open(in_path) as img:
                a_img = img.convert("RGBA")
                a_img = remove(a_img)  # remove background
                file = Common.set_out_file(in_path, out_path, "NoBg")
                i_format = img.format
                if i_format == "JPEG":
                    i_format = "PNG"
                    file = Path(f"{file.parent}/{file.stem}.png")
                    log.debug(f"Revised {file=}")
                if EXIF in img.info:
                    exif_dict = piexif.load(img.info[EXIF])
                    exif_bytes = piexif.dump(exif_dict)
                    a_img.save(file, format=i_format, optimize=True, exif=exif_bytes)
                else:
                    a_img.save(file, format=i_format, optimize=True)
            log.debug(f"Saved the new image to {file}")
            if out_path == REPLACE:
                os.replace(file, in_path)
                log.debug(f"Replaced {in_path} with the new tmp_file")
                file = in_path
            return True, file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            log.error(e)
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def remove_all_images_bg(in_path: Path, out_path: Path | str) -> bool:
        """Remove background for all image files in the given dir

        Args:
            in_path: input dir path
            out_path: output dir path or REPLACE

        Returns:
            bool: True - Success. False - Error
        """
        image_files = Common.prepare_all_files(in_path, out_path)
        tasks = [(f, out_path) for f in image_files]
        files_cnt = len(tasks)
        if files_cnt == 0:
            log.error(f"No image files at {in_path}")
            return False

        log.debug(f"Remove background on {files_cnt} image files in multiprocess ...")
        success_cnt = Common.executor_progress(
            RemoveBg.remove_bg_image, "Remove background", tasks
        )
        log.info(f"\nDone - removed background on {success_cnt}/{files_cnt} files")
        return True
