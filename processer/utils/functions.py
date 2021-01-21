import numpy as np
import os 
import cv2


def rmBackground(frames, num, single=False, idx=0, gray=True):
    if num == 0:
        if single == False:
            return frames
        else:
            return frames[idx]
    frames = frames.astype('f')
    height = frames.shape[1]
    width = frames.shape[2]
    if not gray:
        ch = frames.shape[3]
    frame = frames[idx]
    num = min(num, frames.shape[0])
    ave = np.average(frames[:num], axis=0)

    if single == False:
        if not gray:
            ave = ave.reshape(1, height, width, ch)
        else:
            ave = ave.reshape(1, height, width)
        proc_frames = np.clip((frames - ave), 0, 255)
    else:
        proc_frames = np.clip((frame - ave), 0, 255)
    return proc_frames.astype('u1')

def setBrightness(frames, brightness):
    frames = frames.astype('f')
    proc_frames = np.clip((brightness + frames), 0, 255)
    return proc_frames.astype('u1')

def setContrast(frames, contrast):
    frames = frames.astype('f')
    factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
    proc_frames = np.clip(((frames - 128) * factor + 128), 0, 255)
    return proc_frames.astype('u1')

def load(srcFile, gray=True):
    outFile = os.path.join(os.path.dirname(srcFile), os.path.splitext(os.path.basename(srcFile))[0] + '_processed.avi')
    cap = cv2.VideoCapture(srcFile)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    num = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ret, firstFrame = cap.read()
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0.0)
    ch = firstFrame.shape[2]
    if gray:
        frames = np.empty((num, height, width), dtype='u1')
    else:
        frames = np.empty((num, height, width, ch), dtype='u1')
    for i in range(num):
        ret, frame = cap.read()
        if gray:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
        frames[i] = frame
    return (frames, width, height, num, fps, outFile)

def writeVideo(outFile, fps, width, height, frames, gray=True, kernel=1):
    fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
    video = cv2.VideoWriter(outFile, fourcc, fps, (width, height), (not gray))
    for i, frame in enumerate(frames):
        if kernel != 1:
            frame = cv2.GaussianBlur(frame, (kernel, kernel), 0)
        video.write(frame)
    video.release()

def getImgBytes(frame, width, height, magnification=0.45):
    small_frame = cv2.resize(frame, (int(width*magnification), int(height*magnification)))
    imgbytes = cv2.imencode('.png', small_frame)[1].tobytes()
    return imgbytes