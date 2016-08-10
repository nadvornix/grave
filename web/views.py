# Create your views here.
from django.template import Context, loader, RequestContext
from django.http import HttpResponse,HttpResponseRedirect

def index(request):
    context={}
    #tagy = Tag.objects.usage_for_model(Navod, counts=True)
    #tagcloud = calculate_cloud(tagy)
    #context['tagcloud'] = tagcloud
    try:
        context['nick']=request.GET['nick'] or ''
    except KeyError:
        context['nick'] = ''
    t = loader.get_template('web/index.html')
    c = RequestContext(request,context)
    return HttpResponse(t.render(c))
