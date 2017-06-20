from nltk import pos_tag
from jd_parse import JDParser

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
