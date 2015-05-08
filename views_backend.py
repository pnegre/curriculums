# -*- coding: utf-8 -*-

import os

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.core.mail import send_mail
from django.template import RequestContext
from django.core.servers.basehttp import FileWrapper

from django.contrib.auth.decorators import login_required, permission_required

from django import forms

from curriculums.models import *

import storage as stor

# Quan treiem les pàgines amb RequestContext, fem visibles a la template
# algunes variables que no estarien disponibles.
# Les altres funcions cridaran a aquesta en haver de fer el render de les templates
def renderResponse(request,tmpl,dic):
    return render_to_response(tmpl, dic, context_instance=RequestContext(request))

# Torna els currículums, afegint un atribut si son preferits
def getCurriculumsPreferits(user):
    crs = Curriculum.objects.filter(valid=True)
    curriculums = []
    for c in crs:
        try:
            p = Preferits.objects.get(usuari=user, curriculum=c)
            c.preferit = True
        except Preferits.DoesNotExist:
            c.preferit = False
            pass

        curriculums.append(c)

    return curriculums


def removeUTF(text):
    return ''.join([i if ord(i) < 128 else '_' for i in text])


@permission_required('curriculums.veure_curriculums_docents')
def index(request):
    curriculums = getCurriculumsPreferits(request.user)
    return renderResponse(
        request,
        'curriculums/backend/llista.html', {
            'curriculums': curriculums,
        }
    )


@permission_required('curriculums.veure_curriculums_docents')
def download(request, idc):
    cr = Curriculum.objects.get(id=idc)
    # Passem els caràcters del fitxer a ascii
    filename = cr.file.name.split('/')[-1]
    filename = removeUTF(filename)

    # Content/type????
    response = HttpResponse(cr.file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


@permission_required('curriculums.veure_curriculums_docents')
def show(request, idc):
    cr = Curriculum.objects.get(id=idc)
    return renderResponse(
        request,
        'curriculums/backend/curriculum.html', {
            'cr': cr,
        }
    )


@permission_required('curriculums.veure_curriculums_docents')
def setPreferit(request, idc, yn):
    cr = Curriculum.objects.get(id=idc)
    if yn == 'y':
        try:
            p = Preferits.objects.get(curriculum=cr, usuari=request.user)
        except Preferits.DoesNotExist:
            p = Preferits(curriculum=cr, usuari=request.user)
            p.save()
    else:
        try:
            p = Preferits.objects.get(curriculum=cr, usuari=request.user)
            p.delete()
        except Preferits.DoesNotExist:
            pass

    return HttpResponse()
