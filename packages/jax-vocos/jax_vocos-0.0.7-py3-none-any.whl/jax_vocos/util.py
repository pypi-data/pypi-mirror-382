
from functools import partial
import jax.numpy as jnp
import audax.core.functional
def dynamic_range_compression_jax(x, C=1, clip_val=1e-7):
    return jnp.log(jnp.clip(x,min=clip_val) * C)

def get_mel(y, n_mels=100,n_fft=1024,win_size=1024,hop_length=256,fmin=0,fmax=None,clip_val=1e-7,sampling_rate=24000):

    pad_left = (win_size - hop_length) //2
    pad_right = max((win_size - hop_length + 1) //2, win_size - y.shape[-1] - pad_left)
    y = jnp.pad(y, ((0,0),(pad_left, pad_right)))
    # _,_,spec = jax.scipy.signal.stft(y,nfft=n_fft,noverlap=win_size-hop_length,nperseg=win_size,boundary=None)
    # spectrum_win = jnp.sin(jnp.linspace(0, jnp.pi, win_size, endpoint=False)) ** 2
    # spec *= spectrum_win.sum()
    window = jnp.hanning(win_size)
    spec_func = partial(audax.core.functional.spectrogram, pad=0, window=window, n_fft=n_fft,
                   hop_length=hop_length, win_length=win_size, power=1.,
                   normalized=False, center=True, onesided=True)
    fb = audax.core.functional.melscale_fbanks(n_freqs=(n_fft//2)+1, n_mels=n_mels,
                         sample_rate=sampling_rate, f_min=fmin, f_max=fmax)
    mel_spec_func = partial(audax.core.functional.apply_melscale, melscale_filterbank=fb)
    spec = spec_func(y)
    spec = mel_spec_func(spec)
    spec = dynamic_range_compression_jax(spec, clip_val=clip_val)
    return spec