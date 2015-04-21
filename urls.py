# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',

	(r'^$', 'curriculums.views.primerPas', {}, 'curr-primerpas'),
	(r'^next$', 'curriculums.views.segonPas'),
	(r'^final$', 'curriculums.views.final'),

)
