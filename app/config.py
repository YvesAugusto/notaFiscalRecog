OPTIONS = "-l {} --psm {}".format("por", "4")
PSM6 = "-l {} --psm {}".format("por", "6")
PSM7 = "-l {} --psm {}".format("por", "7")
PSM11 = "-l {} --psm {}".format("por", "11")

NOTA_FISCAL_LIST = {
    'Fortaleza': {
        'nfCode': {'coordinates':((1324, 60), (1595, 199)), 'OPTIONS': OPTIONS},
        'razaoSocial': {'coordinates':((549, 381), (1599, 342)), 'OPTIONS': OPTIONS},
        'CNPJ': {'coordinates':((465, 467), (742, 424)), 'OPTIONS': OPTIONS},
        'valorNota': {'coordinates':((1345, 1625), (1599, 1672)), 'OPTIONS': OPTIONS},
        'ISS': {'coordinates':((1345, 1939), (1595, 2035)), 'OPTIONS': OPTIONS},
    }
}