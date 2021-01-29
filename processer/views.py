from django.shortcuts import redirect, render
from .forms import FileUploadForm
from .models import Video
from .utils.processer import VideoProcesser, ImageProcesser
import cv2
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
import base64
from django.urls import reverse
from django.views import View
import numpy as np

# Create your views here.
class Index(View):
    """
    インデックスページのView
    GET: UPされた動画の一覧を表示
    POST: 動画をUP, Videoモデルにその他情報を登録し、サムネ画像を保存
    """

    def get(self, request):
        objs = Video.objects.all()
        if 'upload_by' in request.GET.keys():
            objs = objs.filter(upload_by=request.GET['upload_by'])
        form = FileUploadForm()
        context = {
            'form': form,
            'objs': objs[::-1],
        }
        if 'upload_by' in request.GET.keys():
            context['text'] = request.GET['upload_by']
        return render(request, 'processer/index.html', context)


    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            # pkを取得し他の要素をVideoモデルに追加する
            obj = Video.objects.get(pk=post.pk)
            obj.upload_by = request.user.username
            obj.basename = Path(obj.upload.path).name
            # 任意のフレームを保存(仮に10としている)
            pngOneFullPath = obj.upload.path.replace('.avi', '.png')
            oneFrame = VideoProcesser.getOneFrame(obj.upload.path, index=10)
            cv2.imwrite(pngOneFullPath, oneFrame)
            obj.oneFrameURL = post.upload.url.replace('.avi', '.png')
            # 最初の5フレームを引いて128足した任意のフレームを保存
            pngHeadFullPath = obj.upload.path.replace('.avi', '_head.png')
            headFrame = VideoProcesser.getHeadFrame(obj.upload.path)
            subtractedFrame = np.clip(oneFrame.astype('f') - headFrame.astype('f') + 128, 0, 255).astype('u1')
            cv2.imwrite(pngHeadFullPath, subtractedFrame)
            obj.headFrameURL = post.upload.url.replace('.avi', '_head.png')
            obj.save()
            return redirect(reverse('processer:index'))


class Detail(View):
    """
    詳細ページのView
    GET: 詳細を表示
    POST: Contrastなどのパラメータを送信し、動画を処理してリンクを吐き出す
    """

    def get(self, request, pk):
        obj = Video.objects.get(pk=pk)
        context = {
            'obj': obj,
            'processed': None
        }
        return render(request, 'processer/detail.html', context)


    def post(self, request, pk):
        # パラメタを取得
        brightness = int(request.POST["brightness"])
        contrast = int(request.POST["contrast"])
        diffNum = int(request.POST["diffNum"])
        # objを取得
        obj = Video.objects.get(pk=pk)
        fullPath = str(settings.BASE_DIR) + str(Path(obj.upload.url))
        processedFullPath = fullPath.replace(".avi", "_processed.mp4")
        VideoProcesser(fullPath) \
            .subtract(diffNum) \
            .brightness(brightness) \
            .contrast(contrast) \
            .writeVideo(processedFullPath)
        context = {
            'obj': obj, 
            'processedPath': obj.upload.url.replace(".avi", "_processed.mp4")
        }
        return render(request, 'processer/detail.html', context)


def getFrameViaAjax(request, pk):
    """ Contrast, Brightness が変更されるたびに呼び出される。
        上記の値を受け取って画像を編集し、BASE64形式でJSONに格納し返却する
        ※特にこだわりは無いがpng形式としている。
        拡張子を変更する場合は1. imencode(), 2. "data:image/***;base64"を変更すること。
    """
    # パラメタを取得
    brightness = int(request.POST["brightness"])
    contrast = int(request.POST["contrast"])
    # 編集する画像のURLをObjectから取得
    obj = Video.objects.get(pk=pk)
    pngPath = obj.headFrameURL
    pngFullPath = str(settings.BASE_DIR) + str(Path(pngPath))
    # 画像を編集
    ip = ImageProcesser(pngFullPath) \
        .brightness(brightness) \
        .contrast(contrast)
    # JSONレスポンス用に画像をBASE64エンコードする
    # Array -> bytes -> base64 -> str 
    imgbytes = cv2.imencode('.png', ip.frame)[1].tobytes()
    img_b64 = base64.b64encode(imgbytes)
    img_str = img_b64.decode("utf-8")
    d = {
        "img": "data:image/png;base64," + img_str,
        "brightness": str(brightness),
        "contrast": str(contrast)
    }
    return JsonResponse(d)