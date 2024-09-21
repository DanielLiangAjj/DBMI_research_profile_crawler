from openai import OpenAI
import json
from dotenv import load_dotenv
import os
import csv
load_dotenv()
GPT_API_KEY = os.getenv("GPT_API_KEY")
client = OpenAI(api_key=GPT_API_KEY)
def get_chatgpt_response(research_summary):
    response = client.chat.completions.create(model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful Researcher research summary filtering assistant."},
        {"role": "user", "content": """Given the following researcher's research summary, remove the researcher's background and acknowledgment related information. (Remember do not modify anything from the text, only remove background and acknowledgement related information): Dr. Chunhua Weng is a Professor of Biomedical Informatics at Columbia University. Before arriving at Columbia, she completed a Ph.D. in Biomedical and Health Informatics from the University of Washington at Seattle. The Weng Lab is focused on clinical research informatics. Her lab develops novel methods to improve the efficiency and generalizability of clinical trials research, to facilitate human phenotyping using electronic health records data, and to automate clinical evidence computing. They invent data-driven methods to optimize the inclusiveness and safety of clinical trial eligibility criteria for COVID-19 clinical trials. They discover knowledge of common clinical trial eligibility criteria from all the studies in ClinicalTrials.gov. They discover clinical trial recruitment success factors. They develop user-friendly software tools to help clinical trialists identify eligible study cohorts in the EHR data and help patients search for clinical trial studies with minimized information overload. They advance human phenotyping using clinical text combined with the Human Phenotype Ontology. They develop neuro-symbolic methods to automate medical evidence comprehension (making PubMed computable). They collaborate closely with clinical investigators, biostatisticians, rare disease experts, and translational researchers at CUIMC and beyond. The National Library of Medicine, the Human Genome Research Institute, FDA, and the Patient-Centered Outcomes Research Institute have supported Dr. Weng’s research. Also, Dr. Weng has received several signature awards from Columbia University, including an Irving Fellowship (2007–2010), a two-phase Collaborative and Multidisciplinary Pilot Research Award (CaMPR) (2008–2010), a Columbia University Diversity Research Fellowship (2009), a Florence Irving Professorship (2010–2013), and a multidisciplinary collaborative award (2021-2022). Dr. Weng was a finalist in the 2010 Microsoft Faculty Fellowship Award. Dr. Weng is currently an Associate Editor for Journal of Biomedical Informatics.
"""},
         {"role": "assistant", "content": """
                The Weng Lab is focused on clinical research informatics. Her lab develops novel methods to improve the efficiency and generalizability of clinical trials research, to facilitate human phenotyping using electronic health records data, and to automate clinical evidence computing. They invent data-driven methods to optimize the inclusiveness and safety of clinical trial eligibility criteria for COVID-19 clinical trials. They discover knowledge of common clinical trial eligibility criteria from all the studies in ClinicalTrials.gov. They discover clinical trial recruitment success factors. They develop user-friendly software tools to help clinical trialists identify eligible study cohorts in the EHR data and help patients search for clinical trial studies with minimized information overload. They advance human phenotyping using clinical text combined with the Human Phenotype Ontology. They develop neuro-symbolic methods to automate medical evidence comprehension (making PubMed computable). 
                """
         },
        {"role": "user", "content": "Now do the same for the following researcher's research summary: "+research_summary}
    ])
    return response.choices[0].message.content

comparison_csv_path = 'columbia_research_faculty_extracted.csv'
comparison_names = {}
with open(comparison_csv_path, mode='r', newline='', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        if row['Research Introduction'] != 'N/A':
            comparison_names[row['Name']] = row['Research Introduction']

output_folder = 'Filtered Human Research Summary'  # Specify your output folder name

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for name, research_summary in comparison_names.items():
    print("Working on", name)
    filtered_summary = get_chatgpt_response(research_summary)
    # Sanitize the name to create a valid filename
    filename = ''.join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    file_path = os.path.join(output_folder, filename + '.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(filtered_summary)