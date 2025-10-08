# QR Payment CZ

Tool to generate QR code pictures in PNG format (410x410px) for QR payments in Czech Republic 
based on standart https://qr-platba.cz/pro-vyvojare/specifikace-formatu/

## CLI TOOL

```bash
qr-payment-cz --help
```

```
usage: qr-payment-cz [-h] [-a ACCOUNT] [-i IBAN_ACC] -v AMMOUNT [-m MESSAGE] [-rn RN] [-vs VS] [-ss SS] [-ks KS] [-o OUTPUT_FILE] [-d] [-s] [-fs]

QR payment generator for CZE based on https://qr-platba.cz/pro-vyvojare/specifikace-formatu/

options:
  -h, --help            show this help message and exit
  -a ACCOUNT, --account ACCOUNT
                        Account number std bank account format
  -i IBAN_ACC, --iban-account IBAN_ACC
                        Account number in IBAN format
  -v AMMOUNT, --ammount-value AMMOUNT
                        Payment ammount
  -m MESSAGE, --message MESSAGE
                        Message text for payment
  -rn RN, --receiver-name RN
                        Payment receiver name
  -vs VS, --variable-symbol VS
                        Payment variable symbol
  -ss SS, --specific-symbol SS
                        Payment specific symbol
  -ks KS, --constant-symbol KS
                        Payment contant symbol
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output PNG image file path
  -d, --display-image   Display generated QR code image
  -s, --silent          Silent mode for info messages
  -fs, --force-silent   Stronger silent mode for all messages
```

## WEB APP
```bash
qr-payment-cz-server --help
```
```
usage: qr-payment-cz-server [-h] -a ACCOUNT [--host HOST] [--port PORT] [--url-prefix-dir URL_PREFIX]

Server part of QR payment generator for CZE based on https://qr-platba.cz/pro-vyvojare/specifikace-formatu/

options:
  -h, --help            show this help message and exit
  -a ACCOUNT, --account ACCOUNT
                        Account number std bank account format
  --host HOST           Server host address
  --port PORT           Server port
  --url-prefix-dir URL_PREFIX
                        Server url prefix direcory
```

# Changelog:

## 0.2.5
Server app enhancements / CSS

## 0.2.4
Server app enhancements

## 0.2.0
Flask server added to serve generated images on specified port and host addess for selected account number.
Run server via command `qr-payment-cz-server`

## 0.1.6
-d param added to display generater QR code image via system default PNG viewer app

## 0.1.5
Source code refactorng and tests added

## 0.1.4
Silent mode added.

## 0.1.3
Validation of account number format added.

## 0.1.2
Support for account number defined in usual bank format xxxxxx-xxxxxxxxxx/xxxx.

## 0.1.1
first version supporting IBAN account numbers only.
