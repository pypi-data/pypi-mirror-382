from ..scripts.constants import GENERATOR_FST_PATH, POS_TAGS
from ..tools.utils import add_compound_separators
import kfst
POS_REGEX = '"|"^'.join(POS_TAGS)


generator_fst = kfst.FST.from_kfst_file(GENERATOR_FST_PATH)


def generate_wordform(word: str, pos: str, morphtags: str, homonym: str = ''):

	word = sorted(add_compound_separators(word, pos=pos, normalize_separators=False))[0]

	input_fields = 'Lexicon', word, f'^{pos}', homonym, '', morphtags
	input_string = '^TAB'.join(input_fields)

	forms = set()
	best = 999
	for form, weight in generator_fst.lookup(input_string):
		if weight > best:
			break
		best = weight
	return forms


if __name__ == '__main__':
	print(generate_wordform('suuri', 'adjective', '+sg+gen'))
