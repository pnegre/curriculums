# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',

	# URLS FRONT-END
	(r'^$', 'curriculums.views_frontend.primerPas', {}, 'curr-primerpas'),
	(r'^next$', 'curriculums.views_frontend.segonPas'),
	(r'^final$', 'curriculums.views_frontend.final'),

	# URLS BACK-END
	(r'^backend/$', 'curriculums.views_backend.index'),
	(r'^backend/download/(\d+)$', 'curriculums.views_backend.download'),

)
