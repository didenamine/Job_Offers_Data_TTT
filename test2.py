import requests
from bs4 import BeautifulSoup
import re
import sqlite3
from googletrans import Translator
url = "https://www.tanitjobs.com/company/6376/think-tank-Business-Solutions"
response = requests.get(url)
conn=sqlite3.connect('JobOffersData.db')
cursor = conn.cursor()
def extract_details_from_section(section):
    translator = Translator()
    details_dict = {}
    details = section.find_all('dl')   
    for detail in details:
        dt = detail.find('dt').text.strip()
        dd = detail.find('dd').text.strip()
        # Translate keys and values to English
        translated_dt = translator.translate(dt, src='fr', dest='en').text
        translated_dd = translator.translate(dd, src='fr', dest='en').text

        translated_dd = re.sub(r'\blicense\b', lambda match: 'bachelor' if match.group(0).islower() else 'Bachelor', translated_dd, flags=re.IGNORECASE)

        # Remove ':' from the keys
        translated_dt = translated_dt.replace(':', '').strip()

        # Special handling for specific keys
        if translated_dt.lower() == 'desired type of job' :
            if translated_dd.lower() in ['sivp', 'cdd', 'cdi']:
                translated_dd = translated_dd.upper()
        # Adjust key if needed and extract the number of open positions
        if translated_dt.lower() == 'vacant jobs':
            translated_dt = 'open positions'
            # Extract the number of open positions
            num_open_positions = re.search(r'\d+', translated_dd)
            if num_open_positions:
                translated_dd = num_open_positions.group()
        # Adjust value if needed
        if 'years old' in translated_dd:
            translated_dd = translated_dd.replace('years old', 'years')


        details_dict[translated_dt] = translated_dd
    return details_dict

#######################################
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    #Getting how many job offers are they 'articles' 
    search_results_div = soup.find('div', class_='search-results')
    h3_elements = soup.find('h3').get_text()
    JOBOFFERSNUM=0
    for i in h3_elements:
        if i.isnumeric():
            JOBOFFERSNUM=int(i)
            break 

    if search_results_div:
        articles = search_results_div.find_all('article', class_='media')
        numb =0
        for article in articles:
            numb+=1
            link_div = article.find('div', class_='media-heading')
            
            if link_div:
                link = link_div.find('a')
                
                if link:
                    link_url = link.get('href')
                    #Link to open the job descriptions 
                    job_name = link.get_text(strip=True)
                    #Prints the job names scraped from the articles 
                    #print("\n\n",'#######',job_name,"#########","\n\n")
                    job_link = BeautifulSoup(requests.get(link_url).text,'html.parser')
                    job_details_section = job_link.find('div', class_='infos_job_details')
                    JOBOPENPOSITIONS=0
                    JOBTYPE =''
                    JOBSTUDYLEVEL=''
                    JOBPROPOSEDREM =""
                    JOBLANGUAGE=""
                    JOBGENDER=""
                    JOBEXP=""
                    
                    if job_details_section:
                        job_details = extract_details_from_section(job_details_section)
                        #print(job_details)
                        
                        # Check if each key exists in the job_details dictionary and assign its value to the corresponding variable
                        if 'open positions' in job_details:
                            try:
                                JOBOPENPOSITIONS = int(job_details['open positions'])
                            except ValueError:
                                JOBOPENPOSITIONS = 0  # or any default value you prefer if conversion fails
                        else:
                            JOBOPENPOSITIONS = 'none'
                            
                        if 'Desired type of job' in job_details:
                            JOBTYPE = job_details['Desired type of job']
                        else:
                            JOBTYPE = ['none']
                            
                        if 'Experience' in job_details:
                            JOBEXP = job_details['Experience']
                        else:
                            JOBEXP = 'none'
                            
                        if 'Study level' in job_details:
                            JOBSTUDYLEVEL = job_details['Study level']
                        else:
                            JOBSTUDYLEVEL = 'none'
                            
                        if 'Proposed remuneration' in job_details:
                            JOBPROPOSEDREM = job_details['Proposed remuneration']
                        else:
                            JOBPROPOSEDREM = 'none'
                            
                        if 'Language' in job_details:
                            JOBLANGUAGE = job_details['Language']
                        else:
                            JOBLANGUAGE = 'none'
                            
                        if 'Gender' in job_details:
                            JOBGENDER = job_details['Gender']
                        else:
                            JOBGENDER = 'none'
                       

                    #Getting the description of the job
                    description=''
                    Desc_div = job_link.find('div',class_='details-body__content content-text')
                    desc_part = Desc_div.find('p')
                    if desc_part:
                        description= desc_part.get_text()

                    #Getting the Responsibilities of the job ...
                    div = job_link.find('div', class_='details-body__content content-text') # Replace 'example_div' with the actual class or id of the div
                    Responsibilities = ""
                    x=str(div.find_all('strong'))
                    x=re.findall(r'<strong>(.*?)</strong>', x)
                    x = [tag.strip().rstrip(':') for tag in x]
                    next_elem_after_req=''
                    found=[False,0]
                    english_ver="essential responsibilities"
                    french_ver="responsabilités essentielles"
        
                    a=x
                    a=[i.lower() for i in a]
                    if any(english_ver in i for i in a):
                        index = next(i for i, item in enumerate(a) if english_ver in item)
                    elif any(french_ver in i for i in a):
                        index = next(i for i, item in enumerate(a) if french_ver in item)
                    else:
                        index=None
                    if index+1 == len(a):
                        next_elem_after_req=None
                    else :
                        next_elem_after_req=a[index+1]
                    if div:
                        div_content = div.get_text(separator='\n', strip=True)
                        english_ver=["Essential Responsibilities" ,"Essential responsibilities" ,"essential Responsibilities" ,"essential responsibilities"]
                        french_ver=["Responsabilités essentielles" ,"Responsabilités Essentielles" ,"responsabilités Essentielles","responsabilités essentielles"]
                        found=[False,'']
                        for i in english_ver:
                            if i in div_content:found=[True,i]
                        if found[0]==True:pass
                        else:
                            for i in french_ver:
                                if i in div_content:found=[True,i]
                        if found[0]==True :
                                if next_elem_after_req==None:
                                    Responsibilities=div_content[div_content.index(found[1])::]
                                else :
                                    Responsibilities=div_content[div_content.index(found[1]):div_content.lower().index(next_elem_after_req)]
                    
                    #Getting the Exigences de l'emploi in this part 
                    #The Exigence => this part is hard because it never stays the same as all the article 
                    #So  we have to distinguish the parts of it and gather each one then collect them in the same place
                    test = job_link.find('div',class_='detail-offre')
                    strong = test.find_all('strong')
                    elements = [i.get_text() for i in strong]
                    details_offre_text = test.get_text()
                    "Elements is a list of the scrapped 'strong' parts of the selected job offer"
                    inside_elements = []
                    for i in range(len(elements)-1):
                        start_index = details_offre_text.index(elements[i]) + len(elements[i])
                        end_index = details_offre_text.index(elements[i+1])
                        substring = details_offre_text[start_index:end_index].strip()
                        inside_elements.append(substring)
                        
                    last_index = details_offre_text.index(elements[-1]) + len(elements[-1])
                    last_substring = details_offre_text[last_index:].strip()
                    inside_elements.append(last_substring)
                    JOBQUALIFICATIONS=None
                    JOBEDUCATION = None 
                    JOBEXPERIENCE=None
                    JOBTECHSKILLS=None
                    JOBSOFTSKILLS =None
                    'text to use '
                    for i,j in  zip(elements ,inside_elements): 
                        
                        if  'education' or 'educations' in i.lower() :
                            print('YES')
                            JOBEDUCATION = j 
                       





                    JOBNAME = job_name
                    JOBDESCRIPTION = description
                    JOBRESPONSIBILITIES =Responsibilities
                    offers="offers"
                    date="data"
                    linkss=""
                    asap=""
                 

                    data =[    numb,JOBTYPE,JOBLANGUAGE,JOBDESCRIPTION,JOBRESPONSIBILITIES,offers,date,JOBLANGUAGE,linkss,asap,JOBSTUDYLEVEL,JOBPROPOSEDREM,JOBOPENPOSITIONS,JOBEXP,JOBGENDER,JOBNAME 
                    ]

              
                   
"""                   cursor.execute('INSERT INTO  JobOffers(JOB_ID,JOB_TYPE,JOB_LANG,JOB_DESC,JOB_REQ,JOB_OFFERS,JOB_EXP_DATE,JOB_DESC_LANGUAGE,JOB_LINK,JOB_AVA,JOB_STUDY,JOB_PROPOSED_REN,JOB_POSITIONS,JOB_EXP,JOB_GENDRE,JOB_NAME) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',data)                                  
                    print('DONE...')
                    conn.commit()
cursor.close()"""
