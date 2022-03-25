import re
import pytesseract as pt
#################### MÉTODOS DE EXTRAÇÃO ####################

"""
FORTALEZA
"""
def extractNFCodeFortaleza(df):
    """
    Casos:
    (1) Só será aceito um número no campo de leitura. Se mais de uma linha for detectada, retorna False.
    (2) Se só detectar uma linha, então é a linha do número da nota. Retorna True
    :param df: dataframe com a leitura dos campos de número da nota fiscal
    :return: número da nota fiscal

    """
    df = df.dropna(axis=0, subset=['text'])
    def findNumber(text):
        find = re.findall("\d+", text)
        if len(find) > 0:
            return True
        return False

    def findASCII(text):
        find = re.findall("^[A-Za-z]*$", text)
        if len(find) > 0:
            return True
        return False

    df = df[df['text'].apply(findNumber) == True]
    if len(df) > 1:
        return False, '[ERRO] problema no número da nota fiscal: mais de uma linha encontrada'
    elif len(df) == 0:
        return False, '[ERRO] problema no número da nota fiscal: nenhuma linha encontrada'

    return True, int(df['text'].values[0])

def extractRazaoSocialFortaleza(df):

    def findASCII(text):
        find = re.findall("^[A-Za-z]*$", text)
        if len(find) > 0:
            return True
        return False

    df = df.dropna(axis=0, subset=['text'])
    df = df[df['text'].apply(findASCII) == True]
    if len(df) == 0:
        return False, '[ERRO] problema na razão social: nenhum caractere ASCII encontrado'

    name = ''
    for idr, row in df.iterrows():
        name += row['text'] + " "

    return True, name[:-1]

def extractCNPJFortaleza(df):
    def findCNPJ(text):
        find = re.findall("\d{2}.\d{3}.\d{3}/\d{4}-\d{2}", text)
        if len(find) > 0:
            return True
        return False

    df = df.dropna(axis=0, subset=['text'])
    df = df[df['text'].apply(findCNPJ) == True]
    if len(df) == 0:
        return False, '[ERRO] problema no CNPJ: nenhum padrão XX.YYY.ZZZ/PPPP-QQ encontrado'
    if len(df) > 1:
        return False, '[ERRO] problema no CNPJ: dois padrões XX.YYY.ZZZ/PPPP-QQ encontrados no mesmo campo'
    return True, str(df['text'].values[0])

def extractValorNotaFortaleza(df):
    def stripNonMoneyCharacters(x):
        text = re.sub("[^0123456789\.,]", "", x["text"])
        x["text"] = text
        return x

    df = df.dropna(axis=0, subset=['text'])
    df = df.apply(stripNonMoneyCharacters, axis=1)
    df = df[df['text'] != ""]
    if len(df) == 0:
        return False, '[ERRO] problema no valor da nota: nenhum padrão de dígitos encontrado'
    if len(df) > 1:
        return False, '[ERRO] problema no valor da nota: dois padrões de dígitos encontrados no mesmo campo'
    split = df['text'].values[0].split(",")
    if len(split) < 2:
        return False, '[ERRO] problema no valor da nota: não há vírgula no valor da nota. ' \
                      'Padrão correto, ex., R$ 1.369,54'
    left, right = split[0], split[1]
    left = float(re.sub("[^0123456789]", "", left))
    right = float(right) / 100
    money = float(left + right)
    return True, money

def extractISSFortaleza(df):
    flag, money = extractValorNotaFortaleza(df)
    return flag, money

"""
RECIFE
"""
def extractISSRecife(df):
    def stripNonMoneyCharacters(x):
        text = re.sub("[^0123456789\.,]", "", x["text"])
        x["text"] = text
        return x

    # flag, money = extractValorNotaFortaleza(df)
    df = df.dropna(axis=0, subset=['text'])
    df = df.apply(stripNonMoneyCharacters, axis=1)
    df = df[df['text'] != ""]
    if len(df) == 0:
        return True, 0.0
    split = df['text'].values[0].split(",")
    left, right = split[0], split[1]
    left = float(re.sub("[^0123456789]", "", left))
    right = float(right) / 100
    money = left + right
    return True, money
    # return flag, money

def extractEmissaoFortaleza(df):
    def findData(text):
        find = re.findall("\d{2}/\d{2}/\d+", text)
        if len(find) > 0:
            return True
        return False

    df = df.dropna(axis=0, subset=['text'])
    df = df[df['text'].apply(findData) == True]
    if len(df) == 0:
        return False, '[ERRO] problema na Data de Emissão: nenhum padrão DD/MM/YYYY encontrado'
    if len(df) > 1:
        return False, '[ERRO] problema na Data de Emissã: mais de um padrão DD/MM/YYYY encontrado no mesmo campo'
    return True, str(df['text'].values[0])
#################### CLASSES EXTRATORAS  ####################
class DefaultExtractorNF:
    def __init__(self):
        self.methods = {
            'nfCode': extractNFCodeFortaleza, 'razaoSocial': extractRazaoSocialFortaleza,
            'CNPJ': extractCNPJFortaleza, 'valorNota': extractValorNotaFortaleza,
            'ISS': extractISSFortaleza, 'dataEmissao': extractEmissaoFortaleza
        }

    def addMethod(self, key, method):
        if key in self.methods.keys():
            del self.methods[key]
        self.methods[key] = method

"""

Seção destinada à criação dos extratores. 

"""
# Fortaleza
fortalezaExtractor = DefaultExtractorNF()
# Recife
recifeExtractor = DefaultExtractorNF()
recifeExtractor.addMethod('ISS', extractISSRecife)
extractors = {
    'Fortaleza': fortalezaExtractor,
    'Recife': recifeExtractor,
    'Natal': recifeExtractor,
    'Belém': recifeExtractor,
    'Salvador': recifeExtractor,
    'Maceió': fortalezaExtractor
}
