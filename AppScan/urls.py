from django.conf.urls import include, url
from django.conf import settings



urlpatterns = [
    # Examples:
    # url(r'^$', 'AppScan.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$','AppScan.views.login', name='index'),
    url(r'^up2ana/$', 'AppScan.views.up2ana', name='up2ana'),
    url(r'^Upload/$', 'AppScan.views.Upload', name='Upload'),
    url(r'^download/', 'AppScan.views.Download', name='download'),
    url(r'^about/$', 'AppScan.views.about', name='about'),
    url(r'^RecentScans/$', 'AppScan.views.RecentScans', name='RecentScans'),
    url(r'^Search/$', 'AppScan.views.Search', name='Search'),
    url(r'^error/$', 'AppScan.views.error', name='error'),
    url(r'^NotFound/$', 'AppScan.views.NotFound', name='NotFound'),
    url(r'^ZIP_FORMAT/$', 'AppScan.views.ZIP_FORMAT', name='ZIP_FORMAT'),
    #url(r'^MAC_ONLY/$', 'AppScan.views.MAC_ONLY', name='MAC_ONLY'),
    url(r'^StaticAnalyzer/$', 'StaticAnalyzer.views.StaticAnalyzer', name='StaticAnalyzer'),
    url(r'^ViewSource/$', 'StaticAnalyzer.views.ViewSource', name='ViewSource'),
    url(r'^PDF/$', 'StaticAnalyzer.views.PDF', name='PDF'),
    #url(r'^ViewFile/$', 'StaticAnalyzer.views.ViewFile', name='ViewFile'),
    url(r'^Smali/$', 'StaticAnalyzer.views.Smali', name='Smali'),
    url(r'^Java/$', 'StaticAnalyzer.views.Java', name='Java'),
    url(r'^Find/$', 'StaticAnalyzer.views.Find', name='Find'),
    url(r'^ManifestView/$', 'StaticAnalyzer.views.ManifestView', name='ManifestView'),
    url(r'^delete/$', 'AppScan.views.delete', name='delete'),
	url(r'^users/$', 'AppScan.views.Users', name='users'),
url(r'^delUser/$', 'AppScan.views.delUser', name='delusers'),
    # url(r'^DynamicAnalyzer/$', 'DynamicAnalyzer.views.DynamicAnalyzer', name='DynamicAnalyzer'),
    # url(r'^GetEnv/$', 'DynamicAnalyzer.views.GetEnv', name='GetEnv'),
    # url(r'^GetRes/$', 'DynamicAnalyzer.views.GetRes', name='GetRes'),
    # url(r'^AppScanCA/$', 'DynamicAnalyzer.views.AppScanCA', name='AppScanCA'),
    # url(r'^TakeScreenShot/$', 'DynamicAnalyzer.views.TakeScreenShot', name='TakeScreenShot'),
    # url(r'^ExportedActivityTester/$', 'DynamicAnalyzer.views.ExportedActivityTester', name='ExportedActivityTester'),
    # url(r'^ActivityTester/$', 'DynamicAnalyzer.views.ActivityTester', name='ActivityTester'),
    # url(r'^FinalTest/$', 'DynamicAnalyzer.views.FinalTest', name='FinalTest'),
    # url(r'^DumpData/$', 'DynamicAnalyzer.views.DumpData', name='DumpData'),
    # url(r'^ExecuteADB/$', 'DynamicAnalyzer.views.ExecuteADB', name='ExecuteADB'),
    # url(r'^Report/$', 'DynamicAnalyzer.views.Report', name='Report'),
    # url(r'^View/$', 'DynamicAnalyzer.views.View', name='View'),
    # url(r'^ScreenCast/$', 'DynamicAnalyzer.views.ScreenCast', name='ScreenCast'),
    # url(r'^Touch/$', 'DynamicAnalyzer.views.Touch', name='Touch'),
    # url(r'^APIFuzzer/$', 'APITester.views.APIFuzzer', name='APIFuzzer'),
    # url(r'^StartScan/$', 'APITester.views.StartScan', name='StartScan'),
    # url(r'^NoAPI/$', 'APITester.views.NoAPI', name='NoAPI'),
    url(r'^index/$', 'AppScan.views.login', name = 'index1'),
    url(r'^login/$', 'AppScan.views.login', name = 'login'),
    url(r'^logout/$', 'AppScan.views.logout', name = 'logout'),
    url(r'^register/$', 'AppScan.views.register', name = 'register'),
]


if settings.DEBUG is False:
    print "[xxoo] DEBUG is Fasle"
    urlpatterns += [url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT, }), ]
