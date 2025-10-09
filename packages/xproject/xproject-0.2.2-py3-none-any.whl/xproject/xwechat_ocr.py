import os
import time
from typing import Callable

from wechat_ocr.ocr_manager import OcrManager


class WechatOCR:
    def __init__(
            self,
            wechat_dir: str,
            wechat_ocr_file_path: str,
            ocr_callback: Callable[[str, dict], None] | None = None,
    ) -> None:
        self.wechat_dir = wechat_dir
        self.wechat_ocr_file_path = wechat_ocr_file_path
        self._default_ocr_callback_results: dict[str, dict] = {}

        def default_ocr_callback(image_file_path: str, results: dict) -> None:
            self._default_ocr_callback_results[image_file_path] = results

        self.ocr_callback = ocr_callback or default_ocr_callback

        self.ocr_manager = OcrManager(self.wechat_dir)
        self.ocr_manager.SetExePath(self.wechat_ocr_file_path)
        self.ocr_manager.SetUsrLibDir(self.wechat_dir)
        self.ocr_manager.SetOcrResultCallback(self.ocr_callback)

    def _start(self) -> None:
        self.ocr_manager.StartWeChatOCR()

    def _stop(self) -> None:
        self.ocr_manager.KillWeChatOCR()

    def _ocr(
            self,
            image_file_paths: str | list[str],
            wait: float = 1.0
    ) -> dict[str, dict]:
        if isinstance(image_file_paths, str):
            image_file_paths = [image_file_paths]
        image_file_paths = list(set(image_file_paths))
        image_file_paths = [image_file_path for image_file_path in image_file_paths if os.path.exists(image_file_path)]

        self._default_ocr_callback_results.clear()

        for image_file_path in image_file_paths:
            self.ocr_manager.DoOCRTask(image_file_path)
            time.sleep(wait)

        while len(self._default_ocr_callback_results) < len(image_file_paths):
            time.sleep(0.1)

        return self._default_ocr_callback_results

    def ocr(self, image_paths: str | list[str]) -> dict[str, dict]:
        try:
            self._start()
            return self._ocr(image_paths)
        finally:
            self._stop()


if __name__ == "__main__":
    def main():
        wechat_ocr_file_path = r"C:\Users\xxx\AppData\Roaming\Tencent\WeChat\XPlugin\Plugins\WeChatOCR\7079\extracted\WeChatOCR.exe"
        wechat_dir = r"C:\Program Files\Tencent\WeChat\[3.9.12.55]"

        client = WechatOCR(wechat_dir, wechat_ocr_file_path)

        from xproject import get_file_assets_dir_path
        print(client.ocr(os.path.join(get_file_assets_dir_path(__file__), "demo.png")))


    main()
