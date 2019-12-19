import pickle
import nltk
import ast
import requests
import HTMLParser
import time
from operator import itemgetter
from selenium import webdriver
from nltk.corpus import stopwords
stop = set(stopwords.words('english'))

def find_co_matrix(query):
	#Change num_query 
	num_query = 300

	start = time.time()

	details = solr_data(query, num_query)
	print(time.time() - start)
	#print "Solr data gathered..."
	skill_list = []

	for i in range(len(details)):
		try:
			skills = ast.literal_eval(details[i])['skills']
		except:
			continue	

		for skill in skills:
			skill = skill.lower()
			if skill not in skill_list:
				skill_list.append(skill)


	skill_list.sort()

	row = []
	for i in range(len(skill_list)):
		row.append(0)

	co_matrix_num = []
	for i in range(len(skill_list)):
		co_matrix_num.append(row)

	skill_dict = {}

	for i in range(len(skill_list)):
		skill_dict[skill_list[i]] = i



	co_matrix_num = ast.literal_eval(str(co_matrix_num))

	#print "co matrix started..."
	for i in range(len(details)):
		try:
			skills = ast.literal_eval(details[i])['skills']
			for skill1 in skills:
				skill1 = skill1.lower()
				for skill2 in skills:
					skill2 = skill2.lower()
					index1 = skill_dict[skill1]
					index2 = skill_dict[skill2]
				
				
					co_matrix_num[index1][index2] = co_matrix_num[index1][index2] + 1
				

		except:
			continue
	#print "co matrix finished..."

	return co_matrix_num, skill_list

	

def find_nearest_neighbour(query, co_matrix_num, skill_list):

	skill_dict = {}

	for i in range(len(skill_list)):
		skill_dict[skill_list[i]] = i

	co_mat_list = []				


	for skill1 in skill_list:
		for skill2 in skill_list:
			if co_matrix_num[ skill_dict[skill1] ][ skill_dict[skill2] ] > 2:
				co_mat_list.append([ skill1 + '-' + skill2, co_matrix_num[ skill_dict[skill1] ][ skill_dict[skill2] ]])
	print("Linear co_mat list built...")
	co_mat_list = sorted(co_mat_list, key = itemgetter(1))
	print("Final list sorted...")

	#co_mat_list.pop()
	co_mat_list.pop()
	print(len(co_mat_list))
	#print co_mat_list
	
	for row in co_mat_list:
		if query not in row[0]:
			co_mat_list.pop(co_mat_list.index(row))
	print("rows cleaned...")
	last_row_skills = co_mat_list[len(co_mat_list) - 2][0]

	nearest_neighbour = ""
	if last_row_skills.split('-')[0] == query:
		nearest_neighbour = last_row_skills.split('-')[1]
	else:
		nearest_neighbour = last_row_skills.split('-')[0]

	#print query + "->" + nearest_neighbour		
	#print time.time() - start
	print("nearest neighbour returned..")
	return nearest_neighbour




def solr_data(query, num):
	#url = 'http://159.203.124.117:8983/solr/fastnext/select?wt=json&q=' + query + '&start=0&rows=' +  str(num)
	url = 'http://104.154.240.12:8984/solr/fastnext/select?wt=json&q=' + query + '&start=0&rows=' + str(num)

	a = requests.get(url)
	a = ast.literal_eval(a.text.strip('\n'))

	people = a['response']['docs']
	html_parser = HTMLParser.HTMLParser()

	details = []

	for person in people:
		result = html_parser.unescape(person['text'].strip('\n'))
		details.append(result)
	return details

def rank_cand_old(jd, candidate_list, primary_skill):

	num_query = 500
	details = solr_data(primary_skill, num_query)
	co_matrix, primary_skill_list = find_co_matrix(query)

	print("Solr data gathered...")
	skill_list = []

	for i in range(len(details)):
		try:
			skills = ast.literal_eval(details[i])['skills']
	#		print skills 
		except:
			continue	

		for skill in skills:
			if skill.lower() not in skill_list:

				skill_list.append(skill.lower())


	skill_list.sort()
	print("skill list sorted...")

	candidate_tuple = []

	for candidate in candidate_list:
		try:
			skills = ast.literal_eval(details[i])['skills']
	
		except:	
			continue
		candidate_tuple.append([candidate, skills, 0])	

	jd_skills_list = []
	jd = jd.split(" ")

	cleaned_jd = []
	'''
	for word in jd:
		word = word.lower()
		if word not in stop and word in skill_list:
			cleaned_jd.append(word)
	'''
	print(skill_list)
	for skill in skill_list:
		if skill in jd:
			cleaned_jd.append(skill)

	print("jd cleaned...")
	print(cleaned_jd)

	for candidate in candidate_tuple:
		skills = candidate[1]

		for skill in cleaned_jd:
			if skill in skills:
				candidate[2] += 100
			elif find_nearest_neighbour(skill, co_matrix, primary_skill_list) in skills:
				candidate[2] += 50

		candidate[2] = candidate[2]/len(cleaned_jd)
		print(candidate[2])

	candidate_tuple = sorted(candidate_tuple, key = itemgetter(2))
	interns = []
	for candidate in candidate_tuple:
		interns.append(candidate[0])

	return interns							

def rank_cand(jd, candidate_list, query):

	num_query = 300
	co_matrix,universal_skill_set = find_co_matrix(query)
	#print co_matrix
	#print universal_skill_set
	for i in range(len(universal_skill_set)):
		universal_skill_set[i] = universal_skill_set[i].lower()
	candidates = []

	jd_skill_list = []
	jd_single_words = jd.split(" ")
	for i in range(len(jd_single_words)):
		jd_single_words[i] = jd_single_words[i].lower()

	jd_double_words = []
	jd_triple_words = []
	jd_quad_words = []

	for i in range(1, len(jd_single_words)):
		jd_double_words.append(jd_single_words[i-1] + ' ' + jd_single_words[i])
		if i + 1 < len(jd_single_words):
			jd_triple_words.append(jd_double_words[i-1] + ' ' + jd_single_words[i+1])
		if i + 2 < len(jd_single_words):	
			jd_quad_words.append(jd_triple_words[i-1] + ' ' + jd_single_words[i+2])
	
	#I assumed the number of word in a match b/w JD and skillset won't be likely more than 4		
	print(jd_single_words)
	print(jd_double_words)
	print(jd_triple_words)
	print(jd_quad_words)

	for skill in universal_skill_set:
		if skill in jd_single_words or skill in jd_double_words or skill in jd_triple_words or skill in jd_quad_words:
			jd_skill_list.append(skill)

	print(jd_skill_list)

	candidate_tuple = []
	for candidate in candidate_list:
		skills = []
		try:
			
			temp_skills = ast.literal_eval(candidate)['skills']
			#if "," in skill, then it has multiple skills in it
			for skill in temp_skills:
				if "," in skill:
					#print skill
					skill = skill.replace(","," ").split(" ")
					skills = skills + skill
					#print skill
				else:
					skills.append(skill)
		except:
			continue
		#print len(skills)
		for skill in skills:
			if skill == "":
				skills.pop(skills.index(skill))
		#print skills		

		candidate_tuple.append([candidate, skills, 0])

	print(len(candidate_list))
	print(len(candidate_tuple))

	nearest_neighbour = {}
	for skill in jd_skill_list:
		co_matrix, universal_skill_set = find_co_matrix(skill)
		nearest_neighbour[skill] = find_nearest_neighbour(skill, co_matrix, universal_skill_set)
	print(nearest_neighbour)

	for candidate in candidate_tuple:
		skills = candidate[1]
		for i in range(len(skills)):
			skills[i] = skills[i].lower()
		for skill in jd_skill_list:
	#		if skill in skills:
				
			for s in skills:
				if skill in s:
					candidate[2] += 100
					break
				elif nearest_neighbour[skill] in s and nearest_neighbour[skill] not in jd_skill_list:
					candidate[2] += 50
					break	
	#		elif nearest_neighbour[skill] in skills and nearest_neighbour[skill] not in jd_skill_list:
	#			candidate[2] += 50
				
			
			#print jd_skill_list
			#print skills
			#print candidate[2]	
		print(candidate[2])
		candidate[2] = candidate[2]/len(jd_skill_list)

	candidate_tuple = sorted(candidate_tuple, key = itemgetter(2))
	for candidate in candidate_tuple:
		print(candidate[1])
		print(candidate[2])
	candidates = []
	for candidate in candidate_tuple:
		candidates.append(candidate[0])
	print(candidates)
	return candidates







def find_skill_from_jd(jd, query):
	num_query = 300
	co_matrix,universal_skill_set = find_co_matrix(query)
	#print co_matrix
	#print universal_skill_set
	for i in range(len(universal_skill_set)):
		universal_skill_set[i] = universal_skill_set[i].lower()
	candidates = []

	jd_skill_list = []
	jd_single_words = jd.split(" ")
	for i in range(len(jd_single_words)):
		jd_single_words[i] = jd_single_words[i].lower()

	jd_double_words = []
	jd_triple_words = []
	jd_quad_words = []

	for i in range(1, len(jd_single_words)):
		jd_double_words.append(jd_single_words[i-1] + ' ' + jd_single_words[i])
		if i + 1 < len(jd_single_words):
			jd_triple_words.append(jd_double_words[i-1] + ' ' + jd_single_words[i+1])
		if i + 2 < len(jd_single_words):	
			jd_quad_words.append(jd_triple_words[i-1] + ' ' + jd_single_words[i+2])
	
	#I assumed the number of word in a match b/w JD and skillset won't be likely more than 4		
	print(jd_single_words)
	print(jd_double_words)
	print(jd_triple_words)
	print(jd_quad_words)

	for skill in universal_skill_set:
		if skill in jd_single_words or skill in jd_double_words or skill in jd_triple_words or skill in jd_quad_words:
			jd_skill_list.append(skill)
    
	
	return jd_skill_list		







'''
jd = "Mandatory Skillset Criteria. Candidates who servedserving for Captive or Product units in the recent tenures           Consistency in employment tenure 3 to 4 years in  current or previous company          Must have experience as Manager from last 4 to 6 years          Hands on Experience in Production support environment with Cloud  Devops platform and Agile  Responsibilities  Manage 25 to 35 member team of automation engineers define short term  long term goals for teams  Lead DevOps includes Dev  24x7 Ops teams responsible for delivery of programs in Wireline  Wireless Network Operations team  Define Measure and drive the teams to achieve KPIs  Lead and Drive the charter of Agile DevOps Cloud  Security to reflect in the adoption and implementation of practices across the delivery pipeline  Lead the team to deliver projects related to SDNNFV  Stay closely connected with the industry and bring in insights to solve business problems or implement innovative ideas  Identify areas of opportunities and drive efficiencies in existing teams  Engage with all employees on a regular basis by having a structure and schedule for employee engagement activities  Represent project and programs in internal and external forums clearly articulating on the value creation and significance of the deliverables  Ensure completion of Infrastructure projects implementation aligned to the needs of key business priorities  Demonstrate leadership in determining and driving strategy decisions  Working with developers and product managersstakeholder to conceptualize build test and realize value based solutions  Influence and get buy in from external and internal stakeholders by effectively balancing the social system  Sr Program Manager Verizon Job Location Hyderabad Experience10 to 14 Years        Looking for candidates with strong NetworkingCloud experience with Telecom background         Candidate should possess technicaldevelopment knowledge and not from testing back ground        Heshe should have managed at least 30 40 people  JD Required Qualifications          Bachelors Degree Higher degrees preferred with 10 years of industry experience working for networking  software development routing  switching protocols or network management applications          Experience in Datacom technologies  Optical  Wireline networking          Experience of working for startups and established network equipment vendors          Significant experience designingbuilding and architectingrefactoring software applications          Experience building highly scalable service applications in Internet or telecommunication space          Operating systems and computer networks background including new technology areas such as SDNNFV and Cloud          Knowledge of Agile Methodology and Devops toolchain for Continuous Integration  Continuous Deployment CICD          Programing in C  C Java          Highly selfmotivated individual and a gogetter          Need for demonstrating extraordinary technology leadership and people skills          Excellent communication skills  Desired SkillsExperience          Micro services architecture web programming designs and paradigms          Technology expertise in Apache J2EE JavaScript Tomcat JBoss          Restful APIs  SOAP programming          Experience in Databases MySQL NoSQL Cassandra etc          Focus on SDLC Metrics          Experience in Open Stack Open vSwitch Linux Containers  Dockers Open Daylight  ONOS Controllers"

print find_skill_from_jd(jd, "java")

jd = "java machine learning deep learning django and python and flask j2ee web services"
query = "C++"

test_candidates = solr_data(query, 100)
obj =  rank_cand(jd, test_candidates, query)	

#print obj[1]


for ob in obj:
	try:
		print ast.literal_eval(ob)['skills']
	except:
		continue	 



a = solr_data("Java+C", 1000)
comma_skill_list = []
for i in range(len(a)):
	try:
		skills = ast.literal_eval(a[i])['skills']
#		print skills 
	except:
		continue	

	for skill in skills:
		if skill.lower() not in comma_skill_list:
			if "," in skill.lower():
				comma_skill_list.append(skill.lower())

for skill in comma_skill_list:
	print skill		

print len(comma_skill_list)			

'''
