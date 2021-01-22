from django.db import models
from django.utils import timezone

# Create your models here.
class Video(models.Model):
    """動画を扱うモデル
    データベースには動画ファイル自体を登録することはできないため、
    URL(Path)を登録するほか、他の情報も登録する。

    upload: アップロードされたファイルの情報。.url, .nameなどで情報にアクセスできる
    upload_at: アップロードされた時刻
    upload_by: アップロード者
    firstFrameURL: 動画の一フレーム目の画像が保存されているURL
    """
    upload = models.FileField(upload_to="upload/")
    upload_at = models.DateTimeField(default=timezone.now)
    upload_by = models.CharField(max_length=150, default="")
    firstFrameURL = models.CharField(max_length=200, default="")
    basename = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.upload.name