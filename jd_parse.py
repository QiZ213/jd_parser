import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
import numpy as np
from scipy import stats
import re


class JDParser:
# find paras which contain skills
	def get_skill_paras(self, paras):
		para_word_counts = [(i, len(word_tokenize(paras[i]))) for i in range(len(paras))]
		counts = np.array([j for (i,j) in para_word_counts])
		mean_count  = list(stats.describe(counts))[2]
		skill_paras = [paras[i] for i in range(len(paras)) if counts[i] > mean_count]

		return skill_paras

	# cleans the skill list
	def format_skills(self, skills):
		skill_list = []
		for skill in skills:
			skill = str(skill).replace(")", "(").split("(")[1].split(" ")[1:]
			skill = " ".join([i.split("/")[0] for i in skill])
			skill_list.append(skill)
		return skill_list

	# find skills using chunking
	def find_skills_chunked(self, tagged_jd):
		skill_list = []
		chunkGram = r"""Skill: {<NNP><NN.*>*}"""
		chunkParser = nltk.RegexpParser(chunkGram)
		for sent in tagged_jd:
			chunked = chunkParser.parse(sent)
			for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Skill'):
				skill_list.append(subtree)

		skill_list = self.format_skills(skill_list)
		return skill_list

	# not in use anymore
	def find_skills(self, tagged_jd):
		skill_list = []
		for sent in tagged_jd:
			i = 0
			while i < len(sent):
				if sent[i][1] == "NNP":
					word = sent[i][0]
					try:
						if 'NN' in sent[i+1][1]:
							word += ' ' + sent[i+1][0]
							i += 1
							try:
								if 'NN' in sent[i+2][1]:
									word += ' ' + sent[i+2][0]
									i += 2
							except:
								pass
					except:
						pass
					skill_list.append(word)
				i += 1
		return skill_list

	# recursive function to get all combination of sentence structure
	def get_all_combinations(self, prev, n):
		if n == 0:
			return prev
		all_strings = self.get_all_combinations("0", n-1) + self.get_all_combinations("1", n-1)
		all_combinations = [prev+string for string in all_strings]
		return all_combinations


	def parse_slash(self, sent):
		optional_words = []
		parsed_sents = []
		if '/' in sent or ' or ' in sent:
			slices = sent.replace(" or ", "/").split('/')
			slices = [slice.split(" ") for slice in slices]
			print slices
			for i in range(len(slices)-1):
				optional_words.append((slices[i][-1], slices[i+1][0]))
				slices[i].pop(-1)
				slices[i+1].pop(0)

			num_slashes = len(slices) - 1
			combinations = self.get_all_combinations("", num_slashes )
			for comb in combinations:
				sent = ""
				for i in range(len(optional_words)):
					slice = slices[i] + [optional_words[i][int(comb[i])]]
					#print optional_words[i][int(comb[i])]
					#print slice
					sent += " " + " ".join(slice)
				sent += " " +" ".join(slices[-1])
				parsed_sents.append(sent)

			print parsed_sents
			return parsed_sents
		return [sent]

	# returns jd
	def get_jd(self):
		file = open('test1', 'rb')
		jd = file.read()
		file.close()
		return jd

	# wrapper function
	def get_skills_from_para(self, para):
		para = re.sub(r'[^\x00-\x7f]+', r"'", para)

		sents = sent_tokenize(para)
		for sent in sents:
			parsed_sents = self.parse_slash(sent)
			if len(parsed_sents) > 1:
				sents.pop(sents.index(sent))
				sents += parsed_sents
		tagged_jd = []
		for sent in sents:
			try:
				tagged_words = pos_tag(sent.split(" "))
				tagged_jd.append(tagged_words)
			except Exception as e:
				print(str(e))
				print sent


		print tagged_jd
		skill_list = self.find_skills_chunked(tagged_jd)
		return list(set(skill_list))


def main():

	jp = JDParser()
	jd = jp.get_jd()
	jd_paras = jd.replace('\n\n', '<p>').split('<p>')
	skill_paras = jp.get_skill_paras(jd_paras)
	all_skills =[]

	for skill_para in skill_paras:
		skill_list = jp.get_skills_from_para(skill_para)
		all_skills += skill_list

	return list(set(all_skills))



if __name__ == '__main__':
	main()
