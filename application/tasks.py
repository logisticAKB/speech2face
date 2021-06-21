import os
import io
import time
import torch
import base64
import librosa
import numpy as np
from math import ceil
from PIL import Image
from celery import shared_task
from .network import Autoencoder, GAN
from speech2face.settings import MODELS_ROOT
from celery.signals import worker_process_init

import matplotlib.pyplot as plt


@worker_process_init.connect()
def on_worker_init(**_):
    global model
    # model = Autoencoder()
    model = GAN()
    checkpoint = torch.load(os.path.join(MODELS_ROOT, 'model.pt'), map_location=torch.device('cpu'))
    # model.load_state_dict(checkpoint['model_state_dict'])
    model.load_state_dict(checkpoint)
    model.eval()


@shared_task
def speech2face_task(file_path):
    audio, sr = librosa.load(file_path)
    audio = np.tile(audio, ceil(sr * 6 / audio.shape[0]))[:sr * 6]
    mel_spec = librosa.feature.melspectrogram(audio, sr=sr, n_fft=2048, hop_length=512, n_mels=128)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    mel_spec_db = mel_spec_db.T

    spec = torch.from_numpy(mel_spec_db)
    spec = torch.unsqueeze(torch.unsqueeze(spec, 0), 0)
    fake = model(spec)
    fake = fake.detach().numpy()
    fake = 0.5 * np.transpose(np.squeeze(fake), (1, 2, 0)) + 0.5
    fake *= 255

    image = Image.fromarray(fake.astype("uint8"))
    raw_bytes = io.BytesIO()
    image.save(raw_bytes, "PNG")
    raw_bytes.seek(0)

    return f'data:image/png;base64,{base64.b64encode(raw_bytes.read()).decode()}'
