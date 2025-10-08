import glob
import os
from argparse import ArgumentParser
from argparse import Namespace
from datetime import datetime

import qrcode
from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory
from qrcode.image.pil import PilImage
from refdatatypes.safedatatypes import safe_int

from qr_payment_cz.libs.str_generator import StrGenerator


class WebServerApp:
    def __init__(self, flask_app):
        self.flask: Flask = flask_app
        self.app_args: Namespace = self._parse_args()
        self.flask.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
        self._routes()
        self._base_data = {"config": self.app_args.__dict__}

    @classmethod
    def _parse_args(cls) -> Namespace:
        arg_parser = ArgumentParser()
        arg_parser.description = "Server part of QR payment generator for CZE based on https://qr-platba.cz/pro-vyvojare/specifikace-formatu/"
        arg_parser.add_argument(
            "-a",
            "--account",
            type=str,
            dest="account",
            required=True,
            help="Account number std bank account format",
        )
        arg_parser.add_argument(
            "--host",
            type=str,
            dest="host",
            required=False,
            default="127.0.0.1",
            help="Server host address",
        )
        arg_parser.add_argument(
            "--port",
            type=int,
            dest="port",
            required=False,
            default=5000,
            help="Server port",
        )
        arg_parser.add_argument(
            "--url-prefix-dir",
            type=str,
            dest="url_prefix",
            required=False,
            default="",
            help="Server url prefix direcory",
        )
        args = arg_parser.parse_args()
        return args

    def _routes(self):
        self.flask.add_url_rule("/", view_func=self._index)
        self.flask.add_url_rule("/static/<path:path>", view_func=self._serve_statics)

    def _index(self):
        ammount: int = safe_int(request.args.get("ammount"), "0")
        message: str = request.args.get("message") or ""

        data = self._base_data.copy()
        data.update({"ammount": ammount, "message": message})
        data.update({"qr_code_url": self._qr_image(ammount, message)})

        return render_template("index.html", **data)

    def _serve_statics(self, path):
        return send_from_directory(self.flask.static_folder, path)

    def _qr_image(self, ammount: int, message: str) -> str | None:
        # remove old QR images
        for f in glob.glob(os.path.join(self.flask.static_folder, "qrcode-*.png")):
            os.remove(f)

        # generate new QR image
        if ammount:
            generator = StrGenerator(
                account=self.app_args.account,  # self.app_args.account,
                ammount=ammount,
                message=message,
            )
            qr_code_str = generator.generate_string()

            now_str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            output_file = f"qrcode-{now_str}.png"
            output_file_path = os.path.join(self.flask.static_folder, output_file)
            output_url_path = os.path.join(self.flask.static_url_path, output_file)
            img: PilImage = qrcode.make(qr_code_str)
            img.save(output_file_path)
            return output_url_path

        return None
