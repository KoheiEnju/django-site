from django.shortcuts import redirect, render
from .forms import FileUploadForm
from .models import Video
from .utils.functions import *
import cv2
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import base64

# Create your views here.
def index(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('processer:index')
    else:
        objs = Video.objects.all()
        form = FileUploadForm()
        return render(request, 'processer/index.html', {'form': form, 'objs': objs})


def detail(request, pk):
    obj = Video.objects.get(pk=pk)
    context = {
        'obj': obj, 
    }
    return render(request, 'processer/detail.html', context)


def getFrameViaAjax(request, pk):
    obj = Video.objects.get(pk=pk)
    url = obj.upload.url
    fullPath = str(settings.BASE_DIR) + str(Path(url))
    frames, width, height, num, fps, outFile = load(fullPath, gray=True)
    firstFrame = frames[int(request.POST["frameNum"])]
    firstFrame = setBrightness(firstFrame, int(request.POST["brightness"]))
    firstFrame = setContrast(firstFrame, int(request.POST["contrast"]))
    imgbytes = cv2.imencode('.png', firstFrame)[1].tobytes()
    img_b64 = base64.b64encode(imgbytes)
    img_str = img_b64.decode("utf-8")
    d = {
        "img": "data:image/png;base64," + img_str,
        "frameNum": request.POST["frameNum"],
        "brightness": request.POST["brightness"],
        "contrast": request.POST["contrast"]
    }
    return JsonResponse(d)


# !!! OBSOLETE
# def getFrame(request, pk, frameNum, brightness, contrast):

#     obj = Video.objects.get(pk=pk)
#     url = obj.upload.url
#     fullPath = str(settings.BASE_DIR) + str(Path(url))
#     frames, width, height, num, fps, outFile = load(fullPath, gray=True)
#     firstFrame = frames[frameNum]
#     firstFrame = setBrightness(firstFrame, int(brightness))
#     firstFrame = setContrast(firstFrame, int(contrast))
#     imgbytes = cv2.imencode('.png', firstFrame)[1].tobytes()
#     response = HttpResponse(imgbytes, content_type='image/png')
#     return response
