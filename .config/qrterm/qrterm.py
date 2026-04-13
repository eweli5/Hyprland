import qrcode

data = input(\"Text: \")
qr = qrcode.make(data)
qr.print_ascii()
