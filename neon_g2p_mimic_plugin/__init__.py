from ovos_plugin_manager.g2p import Grapheme2PhonemePlugin
from distutils.spawn import find_executable
from os.path import expanduser
from ovos_utils.lang.visimes import VISIMES
import subprocess


class MimicPhonemesPlugin(Grapheme2PhonemePlugin):

    def __init__(self, config=None):
        super().__init__(config)
        self.mimic_bin = expanduser(self.config.get("binary") or \
                         find_executable("mimic") or \
                         "mimic")

    @staticmethod
    def parse_phonemes(phonemes, normalize=False):
        """Parse mimic phoneme string into a list of phone, duration pairs.
        Arguments
            phonemes (bytes): phoneme output from mimic
        Returns:
            (list) list of phoneme duration pairs
        """
        phon_str = phonemes.decode()
        pairs = phon_str.replace("pau", ".").split(' ')
        phones = [pair.split(':') for pair in pairs if ':' in pair]
        # remove silence at start/end/repeated
        if normalize:
            for idx, (pho, dur) in enumerate(phones):
                next_pho = phones[idx + 1][0] if idx + 1 < len(phones) else None
                if pho == ".":
                    if idx == 0 or idx == len(phones) - 1 or next_pho == ".":
                        phones[idx] = None
        return [p for p in phones if p is not None]

    def get_mimic_phonemes(self, sentence, normalize=True):
        args = [self.mimic_bin, '-psdur', '-ssml', '-t', sentence, '-o', '/tmp/mimic.pho']
        phonemes = subprocess.check_output(args)
        return self.parse_phonemes(phonemes, normalize)

    def get_arpa(self, word, lang):
        if lang.lower().startswith("en"):
            return [p[0].upper() for p in self.get_mimic_phonemes(word)]
        return None

    def utterance2visemes(self, utterance, lang="en", default_dur=0.4):
        phonemes = self.get_mimic_phonemes(utterance, normalize=False)
        return [(VISIMES.get(pho[0], '4'), pho[1]) for pho in phonemes]


