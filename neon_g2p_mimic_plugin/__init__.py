import subprocess
from distutils.spawn import find_executable
from os.path import expanduser

from ovos_plugin_manager.templates.g2p import Grapheme2PhonemePlugin, OutOfVocabulary
from ovos_utils.lang.visimes import VISIMES


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

    def get_arpa(self, word, lang, ignore_oov=False):
        if lang.lower().startswith("en"):
            return [p[0].upper() for p in self.get_mimic_phonemes(word)]
        if ignore_oov:
            return None
        raise OutOfVocabulary

    def utterance2visemes(self, utterance, lang="en", default_dur=0.4):
        phonemes = self.get_mimic_phonemes(utterance, normalize=False)
        return [(VISIMES.get(pho[0], '4'), float(pho[1])) for pho in phonemes]

    @property
    def available_languages(self):
        """Return languages supported by this G2P implementation in this state
        This property should be overridden by the derived class to advertise
        what languages that engine supports.
        Returns:
            set: supported languages
        """
        return {"en"}

# sample valid configurations per language
# "display_name" and "offline" provide metadata for UI
# "priority" is used to calculate position in selection dropdown
#       0 - top, 100-bottom
# all keys represent an example valid config for the plugin
MimicG2PConfig = {
    "en-us": [{"lang": "en-us",
               "display_name": "Mimic G2P",
               "priority": 50,
               "native_alphabet": "ARPA",
               "durations": True,
               "offline": True}]
} if find_executable("mimic") else {}
