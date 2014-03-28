# -*- encoding: utf-8 -*-
__author__ = 'ernesto'

from django.shortcuts import render
from .basicauth import BasicAuthMiddleware
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import UploadFileForm
from zipfile import ZipFile
from datetime import date
from django.core.files.uploadedfile import UploadedFile
import os
from django.contrib import messages
from subprocess import call
from .utils import handle_upload, valid_zip_file, call_command
from .pgbackup import PGBackup

@require_http_methods(['GET', 'POST'])
@csrf_exempt
def upload(request):

    #check for auth
    response = BasicAuthMiddleware.process_request(request)
    upload_dir = date.today().strftime(settings.UPLOAD_PATH)
    upload_full_path = os.path.join(settings.UPLOAD_DIR, upload_dir)
    if response:
        return response

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            a = form.cleaned_data
            if a['tipo'] == 'stazioni':
                #upload zip file for stazioni
                if settings.FILE_EXT.match(str(a['file'])).group('ext') in settings.VALID_EXTTENSIONS:
                    file_url = handle_upload(request, a['file'])
                    if valid_zip_file(request, os.path.join(settings.UPLOAD_DIR, file_url),
                                      settings.STAZIONI_NAMES,
                                      'stazioni')[0]:
                        ZipFile(os.path.join(settings.UPLOAD_DIR, file_url)).extractall(upload_full_path)
                        messages.add_message(request, messages.SUCCESS, 'Upload Completato!')
                        os.remove(os.path.join(settings.UPLOAD_DIR, file_url))
                        fpt_file = upload_full_path + '/site.fpt'
                        dbf_file = upload_full_path + '/site.dbf'
                        sql_file = upload_full_path + '/site.sql'

                        cmd = ["-c", "pgdbf -e -m " + fpt_file + " " + dbf_file + " > " + sql_file]
                        call_command(cmd, shell=True)

                        iconv_cmd = ["-c", "iconv -f iso-8859-1 -t utf-8 " + sql_file + " > " + sql_file+".utf8"]
                        call_command(iconv_cmd, shell=True)

                        PGBackup(host=settings.DATABASES['default']['HOST'],
                                 user=settings.DATABASES['default']['USER'],
                                 password=settings.DATABASES['default']['PASSWORD']).pg_file(settings.DATABASES['default']['NAME'], sql_file+".utf8")

                    else:
                        messages.add_message(request,
                                             messages.ERROR,
                                             'Il contenuto del file zip non è conforme alle specifiche!')
                        os.remove(os.path.join(settings.UPLOAD_DIR, file_url))
                        # run -- pgdbf -e -m site.fpt site.dbf > site.sql --

                else:
                    messages.add_message(request,
                                         messages.ERROR,
                                         'Estensione del file errata! Verificare che il file sia .zip')
            elif a['tipo'] == 'dati':
                #upload zip file for dati
                if settings.FILE_EXT.match(str(a['file'])).group('ext') in settings.VALID_EXTTENSIONS:
                    file_url = handle_upload(request, a['file'])
                    if valid_zip_file(request, os.path.join(settings.UPLOAD_DIR, file_url),
                                      settings.DATI_NAMES,
                                      'dati')[0]:
                        ZipFile(os.path.join(settings.UPLOAD_DIR, file_url)).\
                            extractall(upload_full_path,
                                       valid_zip_file(request,
                                                      os.path.join(settings.UPLOAD_DIR, file_url),
                                                      settings.DATI_NAMES,
                                                      str(a['tipo']))[1])
                        messages.add_message(request, messages.SUCCESS, 'Upload Completato!')
                        os.remove(os.path.join(settings.UPLOAD_DIR, file_url))
                        pg = PGBackup(host=settings.DATABASES['default']['HOST'],
                                      user=settings.DATABASES['default']['USER'],
                                      password=settings.DATABASES['default']['PASSWORD'])
                        try:
                            query_rain = "TRUNCATE TABLE import_rain"
                            pg.pg_command('climatlas_dev', query_rain)
                            query_rain2 = "\copy import_rain FROM '/www/climatlas/climaatlas/climaatlas/uploads/files/Pioggia.txt' csv DELIMITER ';'"
                            pg.pg_command('climatlas_dev', query_rain2)
                            messages.add_message(request, messages.SUCCESS, 'Query rain Completata!')
                        except:
                            messages.add_message(request,
                                         messages.ERROR,
                                         'Si è verificato un errore nella scrittura dei dati in DB! Contattare il gestore del sistema!')
                        try:
                            query_tmin = "TRUNCATE TABLE import_tmin"
                            pg.pg_command('climatlas_dev', query_tmin)
                            query_tmin2 = "\copy import_tmin FROM '/www/climatlas/climaatlas/climaatlas/uploads/files/TempMIN.txt' csv DELIMITER ';'"
                            pg.pg_command('climatlas_dev', query_tmin2)
                            messages.add_message(request, messages.SUCCESS, 'Query tmin complettata!')

                        except:
                            messages.add_message(request,
                                         messages.ERROR,
                                         'Si è verificato un errore nella scrittura dei dati in DB! Contattare il gestore del sistema!')
                        try:
                            query_tmax = "TRUNCATE TABLE import_tmax"
                            pg.pg_command('climatlas_dev', query_tmax)
                            query_tmax2 = "\copy import_tmax FROM '/www/climatlas/climaatlas/climaatlas/uploads/files/TempMIN.txt' csv DELIMITER ';'"
                            pg.pg_command('climatlas_dev', query_tmax2)
                            messages.add_message(request, messages.SUCCESS, 'Query tmax Completata!')
                        except:
                            messages.add_message(request,
                                         messages.ERROR,
                                         'Si è verificato un errore nella scrittura dei dati in DB! Contattare il gestore del sistema!')

                    else:
                        messages.add_message(request,
                                             messages.ERROR,
                                             'Il contenuto del file zip non è conforme alle specifiche!')
                        os.remove(os.path.join(settings.UPLOAD_DIR, file_url))
                else:
                    messages.add_message(request,
                                         messages.ERROR,
                                         'Estensione del file errata! Verificare che il file sia .zip')
            else:
                pass
            return render(request, 'dataupload/upload_form.html', {'form': form})
    else:
        form = UploadFileForm()

    return render(request, 'dataupload/upload_form.html', {'form': form})