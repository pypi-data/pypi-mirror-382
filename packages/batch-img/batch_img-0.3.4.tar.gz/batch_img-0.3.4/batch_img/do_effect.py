"""class DoEffect: apply OpenCV advanced image effects to image file(s).
Copyright © 2025 John Liu
"""

from pathlib import Path

import piexif
import pillow_heif
from loguru import logger as log
from PIL import Image

from batch_img.common import Common
from batch_img.const import EXIF
from batch_img.effect import Effect

pillow_heif.register_heif_opener()


class DoEffect:
    """
    Apply advanced image effects
    """

    @staticmethod
    def apply_1_image(args: tuple) -> tuple:
        """Apply the special effect to one image file

        Args:
            args: tuple of the below params:
            in_path: input file path
            out_path: output dir path
            effect_name: effect name string, "neon", "hdr", etc.

        Returns:
            tuple: bool, str
        """
        in_path, out_path, effect_name = args
        Common.set_log_by_process()
        try:
            in_path = in_path.expanduser()
            with Image.open(in_path) as img:
                new_img, _ = Effect().apply_effects(img, in_path, effect_name)
                if new_img is None:
                    return False, f"{in_path} got bad image data"
                p_img = Image.fromarray(new_img)
                file = Common.set_out_file(in_path, out_path, effect_name)
                if EXIF in img.info:
                    exif_dict = piexif.load(img.info[EXIF])
                    exif_bytes = piexif.dump(exif_dict)
                    p_img.save(file, img.format, optimize=True, exif=exif_bytes)
                else:
                    p_img.save(file, img.format, optimize=True)
            log.debug(f"Saved {effect_name=} image to {file}")
            return True, file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            log.error(e)
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def apply_all_in_dir(in_path: Path, out_path: Path | str, effect_name: str) -> bool:
        """Apply the special effect to all images in the given dir

        Args:
            in_path: input file path
            out_path: output dir path
            effect_name: effect name string, "neon", "hdr", etc.

        Returns:
            bool: True - Success. False - Error
        """
        image_files = Common.prepare_all_files(in_path, out_path)
        tasks = [(f, out_path, effect_name) for f in image_files]
        files_cnt = len(tasks)
        if files_cnt == 0:
            log.error(f"No image files at {in_path}")
            return False

        log.debug(f"Apply special effect to {files_cnt} image files ...")
        success_cnt = Common.executor_progress(
            DoEffect.apply_1_image, "Apply special effect to image files", tasks
        )
        log.info(f"\nCompleted the special effect to {success_cnt}/{files_cnt} files")
        return True
