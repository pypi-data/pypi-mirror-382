import glob
import os
from argparse import ArgumentParser
from argparse import Namespace
from datetime import datetime

import qrcode
from flask import Flask
from flask import render_template
from flask import request
from flask import send_file
from qrcode.image.pil import PilImage

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
        self.flask.add_url_rule("/qr", view_func=self._qr_image)

    def _index(self):
        data = self._base_data
        return render_template("index.html", **data)

    def _qr_image(self):
        ammount: int = request.args.get("ammount") or 1
        message: str = request.args.get("message") or None

        # remove old QR images
        for f in glob.glob(os.path.join(self.flask.static_folder, "qrcode-*.png")):
            os.remove(f)

        # generate new QR image
        generator = StrGenerator(
            account=self.app_args.account,  # self.app_args.account,
            ammount=ammount,
            message=message,
        )
        qr_code_str = generator.generate_string()

        output_file = os.path.join(self.flask.static_folder, f"qrcode-{datetime.now().timestamp()}.png")
        img: PilImage = qrcode.make(qr_code_str)
        img.save(output_file)
        return send_file(output_file, mimetype="image/png")
