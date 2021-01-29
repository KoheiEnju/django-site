import cv2
import numpy as np

class VideoProcesser:
    """ グレイスケール前提
    例外処理などは全くやっていないので注意してください
    """
    
    def __init__(self, srcFilePath):
        """動画の全フレームを読み込み、各種パラメータを取得する

        Args:
            srcFilePath (str): 動画ファイルのフルパス
        """
        cap = cv2.VideoCapture(srcFilePath)
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frameNum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.frames = np.empty((self.frameNum, self.height, self.width), dtype='u1')
        for i in range(self.frameNum):
            _, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.frames[i] = frame

    
    def setBrightness(self, brightness):
        """既存のフレームに対しtえ明るさを設定

        Args:
            brightness (int): -255 ~ 255 の整数型

        Returns:
            self: メソッドチェーンできるようにselfを返却
        """
        frames = self.frames.astype('f')
        processed_frames = np.clip((brightness + frames), 0, 255)
        self.frames = processed_frames.astype('u1')
        return self


    def setContrast(self, contrast):
        """既存のフレームに対してコントラストを設定

        Args:
            contrast ([type]): contrastの値は、横軸変換前縦軸返還後のグラフの傾きを表す。0 ~ ∞ 

        Returns:
            self: メソッドチェーンできるようにselfを返却
        """
        frames = self.frames.astype('f')
        processed_frames = np.clip((contrast * (frames - 128) + 128), 0, 255)
        self.frames = processed_frames.astype('u1')
        return self

    
    def removeBackground(self, averageNum):
        """既存のフレームの0 ~ averageNumフレームの平均を取ってバックグラウンドとし、全フレームから引く

        Args:
            averageNum (int): 何フレーム目までをバックグラウンドとするかを指定。なお averageNum > self.frameNum の場合の例外などは投げていない 

        Returns:
            self: メソッドチェーンできるようにselfを返却
        """
        if averageNum == 0:
            return self
        frames = self.frames.astype('u1')
        averageFrame = np.average(frames[:averageNum], axis=0)
        processed_frames = np.clip((frames - averageFrame), 0, 255)
        self.frames = processed_frames.astype('u1')
        return self
    

    def writeVideo(self, outFilePath):
        """既存のフレームを書きだす

        Args:
            outFilePath (str): 書き出すファイルのフルパス
        """
        fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
        video = cv2.VideoWriter(outFilePath, fourcc, self.fps, (self.width, self.height), False)
        for frame in self.frames:
            video.write(frame)
        video.release()


    @staticmethod
    def getFirstFrame(srcFilePath):
        """ ***静的メソッド***
        一フレーム目を取り出すだけ。あえてクラスに属させる必要はない。

        Args:
            srcFilePath (str): 動画のファイルパス

        Returns:
            NdArray: 一フレーム目のnumpy配列
        """
        cap = cv2.VideoCapture(srcFilePath)
        _, firstFrame = cap.read()
        firstFrame = cv2.cvtColor(firstFrame, cv2.COLOR_BGR2GRAY)
        return firstFrame

    
    @staticmethod
    def getHeadFrame(srcFilePath, frameNum=5):
        """ ***静的メソッド

        Args:
            srcFilePath (str): 動画のファイルパス
            frameNum ([type]): 0~frameNum-1 を平均化したフレームを返す

        Returns:
            ndArray: 最初のframeNum枚を平均化したフレーム
        """
        cap = cv2.VideoCapture(srcFilePath)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        headFrames = np.empty((frameNum, height, width)).astype('u1')
        for i in range(frameNum):
            _, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            headFrames[i] = frame
        averageFrame = np.mean(headFrames, axis=0)
        return averageFrame


    @staticmethod
    def getOneFrame(srcFilePath, index=0):
        """ ***静的メソッド***
        一フレーム目を取り出すだけ。あえてクラスに属させる必要はない。

        Args:
            srcFilePath (str): 動画のファイルパス
            index (int): 何フレーム目を取り出すか

        Returns:
            ndArray: 指定のindexのフレーム
        """
        frame = None
        cap = cv2.VideoCapture(srcFilePath)
        for i in range(index+1):
            _, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return frame