from django.shortcuts import redirect, render
from .forms import FileUploadForm
from .models import Video
from .utils.functions import *
import cv2
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import base64
from django.urls import reverse

# Create your views here.
def index(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('processer:index'))
    else:
        objs = Video.objects.all()
        form = FileUploadForm()
        return render(request, 'processer/index.html', {'form': form, 'objs': objs})


def detail(request, pk):
    if request.method == "GET":
        obj = Video.objects.get(pk=pk)
        url = obj.upload.url
        fullPath = str(settings.BASE_DIR) + str(Path(url))
        pngFullPath = fullPath.replace(".avi", ".png")
        if not Path(pngFullPath).exists():
            firstFrame = getFirstFrame(fullPath, gray=True)
            cv2.imwrite(pngFullPath, firstFrame)
        context = {
            'obj': obj, 
            'png': str(Path(url)).replace(".avi", ".png"),
            'processed': None,
        }
        return render(request, 'processer/detail.html', context)
    elif request.method == "POST":
        brightness = int(request.POST["brightness"])
        contrast = int(request.POST["contrast"])
        diffNum = int(request.POST["diffNum"])
        obj = Video.objects.get(pk=pk)
        url = obj.upload.url
        fullPath = str(settings.BASE_DIR) + str(Path(url))
        frames, width, height, num, fps, outFile = load(fullPath, gray=True)
        frames = setBrightness(frames, brightness)
        frames = setContrast(frames, contrast)
        frames = rmBackground(frames, diffNum, gray=True)
        processedFullPath = fullPath.replace(".avi", "_processed.avi")
        writeVideo(processedFullPath, fps, width, height, frames, gray=True, kernel=1)
        processedPath = url.replace(".avi", "_processed.avi")
        context = {
            'obj': obj, 
            'png': str(Path(url)).replace(".avi", ".png"),
            'processedPath': processedPath,
        }
        return render(request, 'processer/detail.html', context)

def getFrameViaAjax(request, pk):
    obj = Video.objects.get(pk=pk)
    url = obj.upload.url
    fullPath = str(settings.BASE_DIR) + str(Path(url))
    pngFullPath = fullPath.replace(".avi", ".png")
    firstFrame = cv2.imread(pngFullPath, cv2.IMREAD_GRAYSCALE)
    firstFrame = setBrightness(firstFrame, int(request.POST["brightness"]))
    firstFrame = setContrast(firstFrame, int(request.POST["contrast"]))
    imgbytes = cv2.imencode('.png', firstFrame)[1].tobytes()
    img_b64 = base64.b64encode(imgbytes)
    img_str = img_b64.decode("utf-8")
    d = {
        "img": "data:image/png;base64," + img_str,
        "brightness": request.POST["brightness"],
        "contrast": request.POST["contrast"]
    }
    return JsonResponse(d)