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

@permission_required('curriculums.veure_curriculums_docents')
def index(request):
    curriculums = Curriculum.objects.all()
    return renderResponse(
        request,
        'curriculums/backend/llista.html', {
            'curriculums': curriculums,
        }
    )

def removeUTF(text):
    return ''.join([i if ord(i) < 128 else '_' for i in text])

@permission_required('curriculums.veure_curriculums_docents')
def download(request, idc):
    cr = Curriculum.objects.get(id=idc)
    # Hi pot haver problemes si el nom del fitxer té caràcters UTF
    # Convendria passar a ascii
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
