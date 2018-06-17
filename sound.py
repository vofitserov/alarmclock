import sys
import wave
import alsaaudio
import threading
import time

from config import *

# Named global logger from config
logger = logging.getLogger("alarmclock")

class PlaySilence(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.done = False
        self.device = alsaaudio.PCM(device=SOUND_DEVICE)
        self.device.setchannels(2)
        self.device.setrate(48000)
        self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        logger.info("silence initialized device.")
        self.setDaemon(True)
        self.start()
        logger.info("silence started")
        return
    
    def run(self):
        logger.info("silence is running.")
        fzero = open("/dev/zero")
        while not self.done:
            data = fzero.read(48000)
            self.device.write(data)
            pass
        fzero.close()
        logger.info("silence is exiting.")
        return

    def shutdown(self):
        self.done = True
        self.join(3)
        return

class PlaySound(threading.Thread):
    def __init__(self, device, sound):
        threading.Thread.__init__(self)
        self.done = False
        self.sound = sound
        self.device = device
        self.setDaemon(True)
        self.start()
        return

    def shutdown(self):
        self.done = True
        self.join(3)
        return
    
    def run(self):
        logger.info("playing %s" % self.sound)
        fwave = wave.open(self.sound, 'rb')
        logger.info('%d channels, %d sampling rate' %
                    (fwave.getnchannels(),fwave.getframerate()))
        # Set attributes
        self.device.setchannels(fwave.getnchannels())
        self.device.setrate(fwave.getframerate())

        # 8bit is unsigned in wav files
        if fwave.getsampwidth() == 1:
            self.device.setformat(alsaaudio.PCM_FORMAT_U8)
            # Otherwise we assume signed data, little endian
        elif fwave.getsampwidth() == 2:
            self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        elif fwave.getsampwidth() == 3:
            self.device.setformat(alsaaudio.PCM_FORMAT_S24_3LE)
        elif fwave.getsampwidth() == 4:
            self.device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
        else:
            logger.error("Unsupported format")
            return

        periodsize = fwave.getframerate() / 8
        self.device.setperiodsize(periodsize)
    
        data = fwave.readframes(periodsize)
        while data and not self.done:
            # Read data from stdin
            self.device.write(data)
            data = fwave.readframes(periodsize)
            pass
        
        fwave.close()
        logger.info("...done playing")
        return

class Player:
    def __init__(self):
        self.play_thread = None
        self.play_silence = PlaySilence()
        self.device = alsaaudio.PCM(device=SOUND_DEVICE)
        self.mixer = alsaaudio.Mixer("PCM")
        self.mixer.setvolume(SOUND_VOLUME)
        logger.info('device:%s' % SOUND_DEVICE)
        return
    
    def is_playing(self):
        return self.play_thread and self.play_thread.is_alive()
    
    def play(self, sound):
        if self.is_playing():
            logger.info("currently playing %s" % self.play_thread.sound)
            return
        self.play_thread = PlaySound(self.device, sound)
        return

    def stop(self):
        if self.is_playing():
            logger.info("stopping playing %s" % self.play_thread.sound)
            self.play_thread.shutdown()
            pass
        self.play_thread = None
        return

    def shutdown(self):
        self.stop()
        self.play_silence.shutdown()
        return
        

if __name__ == '__main__':
    stderrHandler = logging.StreamHandler(sys.stderr)
    logger.removeHandler(daemonHandler)
    logger.addHandler(stderrHandler)
    logger.info("testing sound mode, logging to stderr")
    
    silence = PlaySilence()
    logger.info("silence for 5 seconds.")
    time.sleep(5)
    
    player = Player()
    player.play(SOUND_FILE)
    logger.info("sleeping 3 seconds")
    time.sleep(3)
    logger.info("telling player to shutdown")
    player.stop()
    logger.info("done.")

    
