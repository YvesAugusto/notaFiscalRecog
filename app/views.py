from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http.response import JsonResponse


import time
import urllib3
import certifi
import numpy as np
import regex as re
from app.classes import *
from app.models import Scheme
from rest_framework import status
from app.extractors import extractors
from pdf2image import convert_from_path
from app.serializers import SchemeSerializer

SAVE_PDF="/media/yves/HD/Applications/notaFiscalRecog/data/myPdf.pdf"
#TODO CRIAR UM DECORATOR PARA VALIDAR OS DADOS DA REQUEST
def validateNota(data):
    try:
        url = data['url']
    except:
        response = JsonResponse(
            {"message": "falha",
             "erros": "o post carece da chave \'url\'",
             "data": {}},
            status=status.HTTP_400_BAD_REQUEST)
        return response

    try:
        nomeMunicipio = data['nomeMunicipio']
    except:
        response = JsonResponse(
            {"message": "falha",
             "erros": "o post carece da chave \'nomeMunicipio\'",
             "data": {}},
            status=status.HTTP_400_BAD_REQUEST)
        return response

    # TROCAR POR QUERY
    schemes = Scheme.objects.filter(nomeMunicipio__startswith=nomeMunicipio).all()
    if len(schemes) == 0:
        response = JsonResponse(
            {"message": "falha",
             "erros": "município \'{}\' não cadastrado".format(nomeMunicipio),
             "data": {}},
            status=status.HTTP_406_NOT_ACCEPTABLE)
        return False, response
    found = 0
    index = 0
    for ids, scheme in enumerate(schemes):
        if scheme.nomeMunicipio == nomeMunicipio:
            found = 1
            index = ids
            break
    if found == 0:
        response = JsonResponse(
            {"message": "falha",
             "erros": "município \'{}\' não cadastrado".format(nomeMunicipio),
             "data": {}},
            status=status.HTTP_406_NOT_ACCEPTABLE)
        return False, response

    return True, schemes[index]

class SchemePOST(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if request.method == 'POST':
            data = JSONParser().parse(request)
            schemeSerializer = SchemeSerializer(data=data)
            if schemeSerializer.is_valid():
                schemeSerializer.save()
                return JsonResponse(schemeSerializer.data, status=status.HTTP_201_CREATED, safe=False)
            return JsonResponse(schemeSerializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)


class SchemeGPD(APIView):
    queryset = Scheme.objects.all()
    serializer_class = SchemeSerializer
    lookup_field = 'pk'
    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            pk = int(request.path.split("/")[-1])
            if pk == 0:
                schemes = Scheme.objects.all()
                nomeMunicipio = request.GET.get('title', None)
                if nomeMunicipio is not None:
                    schemes = schemes.filter(nomeMunicipio__icontains=nomeMunicipio)
                schemeSerializer = SchemeSerializer(schemes, many=True)
                return JsonResponse(schemeSerializer.data, safe=False)
            if pk > 0:
                try:
                    scheme = Scheme.objects.get(pk=pk)
                except:
                    return JsonResponse({"message": "usuario não existe"},
                                        status=status.HTTP_406_NOT_ACCEPTABLE)
                schemeSerializer = SchemeSerializer(scheme)
                return JsonResponse(schemeSerializer.data, safe=False)
            else:
                return JsonResponse({"message": "id inválido"},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)


    def put(self, request, *args, **kwargs):
        if request.method == 'PUT':
            try:
                pk = int(request.path.split("/")[-1])
            except:
                return JsonResponse({"message": "id inválido"},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
            if pk > 0:
                try:
                    scheme = Scheme.objects.get(pk=pk)
                except:
                    return JsonResponse({"message": "usuario não existe"},
                                        status=status.HTTP_406_NOT_ACCEPTABLE)
                schemeData = JSONParser().parse(request)
                tutorial_serializer = SchemeSerializer(scheme, data=schemeData)
                if tutorial_serializer.is_valid():
                    tutorial_serializer.save()
                    return JsonResponse(tutorial_serializer.data)
                return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({"message": "id inválido"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

    def delete(self, request):

        if request.method=='DELETE':
            try:
                pk = int(request.path.split("/")[-1])
            except:
                return JsonResponse({"message": "id inválido"},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
            try:
                scheme = Scheme.objects.get(pk=pk)
            except:
                return JsonResponse({"message": "não existe município com id {}".format(pk)},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
            try:
                scheme.delete()
            except:
                return JsonResponse({"message": "não foi possível efetuar a remoção"},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
            schemeSerializer = SchemeSerializer(scheme, many=False)
            return JsonResponse(schemeSerializer.data, status=status.HTTP_204_NO_CONTENT, safe=False)

class ValidateNota(APIView):
    permission_classes = (IsAuthenticated,)

    def decodeCoordinates(self, coordinates):
        split = coordinates.split(",")
        integers = [int(re.search(r'\d+', s).group()) for s in split]
        return ((integers[0], integers[1]), (integers[2], integers[3]))

    def decodeScheme(self, scheme):
        del scheme['_state']
        del scheme['id']
        del scheme['nomeMunicipio']
        decodedScheme = {}
        for key, values in scheme.items():
            decodedScheme[key] = {
                'coordinates': self.decodeCoordinates(scheme[key]['coordinates']),
                'OPTIONS': scheme[key]['OPTIONS']
            }
        return decodedScheme

    def downloadPDF(self, url):
        global SAVE_PDF
        try:
            print("[INFO] tentando efetuar o download...")
            http = urllib3.PoolManager(ca_certs=certifi.where())  # 10, headers={'User-Agent': 'Mozilla/6.0'})
            response = http.request('GET', url, headers={'User-Agent': 'Mozilla/6.0'}, preload_content=False)
            with open(SAVE_PDF, 'wb') as f:
                for chunk in response.stream(1024):
                    f.write(chunk)
            response.release_conn()
            print("[INFO] download concluído...")
            return True, {}
        except:
            response = JsonResponse(
                {"message": "falha",
                 "erros": "incapaz de efetuar o download",
                 "data": {}},
                 status=status.HTTP_406_NOT_ACCEPTABLE)
            return False, response

    def post(self, request):
        if request.method == 'POST':
            data = JSONParser().parse(request)

            flag, response = validateNota(data)
            if not flag:
                return response
            nomeMunicipio = data['nomeMunicipio']
            url = data['url']
            response = self.decodeScheme(response.__dict__)
            nota = makeNote(data, response)
            start = time.time()

            downloadTime = time.time() - start
            downloaded, response = self.downloadPDF(url)
            if not downloaded:
                return response
            pdf = '/media/yves/HD/Applications/notaFiscalRecog/data/myPdf.pdf'
            # pdf = '/home/yves/PycharmProjects/captureBox/fortaleza.pdf'
            try:
                image = np.array(convert_from_path(pdf)[0])
            except:
                response = JsonResponse(
                    {"message": "falha",
                     "erros": "incapaz de transformar pdf em imagem",
                     "data": {}},
                    status=status.HTTP_406_NOT_ACCEPTABLE)

                return response

            start = time.time()
            try:
                json, camposFailed = nota.recogOCR(image, extractors[nomeMunicipio])
            except:
                response = JsonResponse(
                    {"message": "falha",
                     "erros": "houve algum problema no reconhecimento; "
                              "verifique se a nota enviada realmente pertence ao município submetido,"
                              "ou se o template da nota do município sofreu alguma alteração.",
                     "data": {}},
                    status=status.HTTP_406_NOT_ACCEPTABLE)
                return response

            tempoOCR = time.time() - start
            if camposFailed == '':
                response = JsonResponse(
                    {"message": "sucesso",
                     "data": json,
                     "tempoDownload": downloadTime,
                     "tempoRecog": tempoOCR},
                    status=status.HTTP_200_OK)
                return response

            response = JsonResponse(
                {"message": "falha",
                 "data": {},
                 "erros": camposFailed,
                 "tempoDownload": downloadTime
                 },
                status=status.HTTP_200_OK)
            return response

        response = Response(
            {"message": "método \'{}\' autorizado".format(request.method),
             "data": {}}
        )
        response.status_code = 405
        return response

