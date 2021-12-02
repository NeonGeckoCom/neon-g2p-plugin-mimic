from neon_g2p_mimic_plugin import MimicPhonemesPlugin



print(MimicPhonemesPlugin().utterance2arpa("hello world", "en"))
print(MimicPhonemesPlugin().utterance2visemes("hello world"))