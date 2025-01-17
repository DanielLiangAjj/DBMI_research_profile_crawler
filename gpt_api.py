import os

import compare_name_matches
# from DBMI_research_profile_crawler import compare_name_matches
from compare_name_matches import *

from openai import OpenAI
import json
from dotenv import load_dotenv
import os
load_dotenv()
GPT_API_KEY = os.getenv("GPT_API_KEY")
client = OpenAI(api_key=GPT_API_KEY)

def get_chatgpt_response(research_articles):
    response = client.chat.completions.create(model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful Researcher profile summarizing assistant."},
        {"role": "user", "content": """Based on the titles and abstracts of the following research articles in json format,
                                        summarize the researcher's Research Overview and Research Interests: {"researcher": "Joseph A. Gogos", "articles": [{"title": "CHD2 Regulates Neuron-glioma Interactions in Pediatric Glioma.", "abstract": "High-grade gliomas (HGG) are deadly diseases for both adult and pediatric patients. Recently, it has been shown that neuronal activity promotes progression of multiple subgroups of HGG. However, epigenetic mechanisms that govern this process remain elusive. Here we report that the chromatin remodeler CHD2 regulates neuron-glioma interactions in diffuse midline glioma (DMG) characterized by onco-histone H3.1K27M. Depletion of CHD2 in H3.1K27M DMG cells compromises cell viability and neuron-to-glioma synaptic connections in vitro, neuron-induced proliferation of H3.1K27M DMG cells in vitro and in vivo, activity-dependent calcium transients in vivo, and extends the survival of H3.1K27M DMG-bearing mice. Mechanistically, CHD2 coordinates with the transcription factor FOSL1 to control the expression of axon-guidance and synaptic genes in H3.1K27M DMG cells. Together, our study reveals a mechanism whereby CHD2 controls the intrinsic gene program of the H3.1K27M DMG subtype, which in turn regulates the tumor growth-promoting interactions of glioma cells with neurons.", "pub_date": "2024-May-20"}, {"title": "Altered corollary discharge signaling in the auditory cortex of a mouse model of schizophrenia predisposition.", "abstract": "The ability to distinguish sensations that are self-generated from those caused by external events is disrupted in schizophrenia patients. However, the neural circuit abnormalities underlying this sensory impairment and its relationship to the risk factors for the disease is not well understood. To address this, we examined the processing of self-generated sounds in male Df(16)A", "pub_date": "2023-Nov-15"}, {"title": "Aberrant pace of cortical neuron development in brain organoids from patients with 22q11.2 deletion syndrome and schizophrenia.", "abstract": "Adults and children afflicted with the 22q11.2 deletion syndrome (22q11.2DS) exhibit cognitive, social, and emotional impairments, and are at significantly heightened risk for schizophrenia (SCZ). The impact of this deletion on early human brain development, however, has remained unclear. Here we harness organoid models of the developing human cerebral cortex, cultivated from subjects with 22q11.2DS and SCZ, as well as unaffected control samples, to identify cell-type-specific developmental abnormalities arising from this genomic lesion. Leveraging single-cell RNA-sequencing in conjunction with experimental validation, we find that the loss of genes within the 22q11.2 locus leads to a delayed development of cortical neurons. This compromised development was reflected in an elevated proportion of actively proliferating neural progenitor cells, coupled with a decreased fraction of more mature neurons. Furthermore, we identify perturbed molecular imprints linked to neuronal maturation, observe the presence of sparser neurites, and note a blunted amplitude in glutamate-induced Ca2+ transients. The aberrant transcription program underlying impaired development contains molecular signatures significantly enriched in neuropsychiatric genetic liability. MicroRNA profiling and target gene investigation suggest that microRNA dysregulation may drive perturbations of genes governing the pace at which maturation unfolds. Using protein-protein interaction network analysis we define complementary effects stemming from additional genes residing within the deleted locus. Our study uncovers reproducible neurodevelopmental and molecular alterations due to 22q11.2 deletions. These findings have the potential to facilitate disease modeling and promote the pursuit of therapeutic interventions.", "pub_date": "2023-Oct-05"}, {"title": "An in vitro model of neuronal ensembles.", "abstract": "Advances in 3D neuronal cultures, such as brain spheroids and organoids, are allowing unprecedented in vitro access to some of the molecular, cellular and developmental mechanisms underlying brain diseases. However, their efficacy in recapitulating brain network properties that encode brain function remains limited, thereby precluding development of effective in vitro models of complex brain disorders like schizophrenia. Here, we develop and characterize a Modular Neuronal Network (MoNNet) approach that recapitulates specific features of neuronal ensemble dynamics, segregated local-global network activities and a hierarchical modular organization. We utilized MoNNets for quantitative in vitro modelling of schizophrenia-related network dysfunctions caused by highly penetrant mutations in SETD1A and 22q11.2 risk loci. Furthermore, we demonstrate its utility for drug discovery by performing pharmacological rescue of alterations in neuronal ensembles stability and global network synchrony. MoNNets allow in vitro modelling of brain diseases for investigating the underlying neuronal network mechanisms and systematic drug discovery.", "pub_date": "2022-Jun-09"}, {"title": "Vascular-derived SPARC and SerpinE1 regulate interneuron tangential migration and accelerate functional maturation of human stem cell-derived interneurons.", "abstract": "Cortical interneurons establish inhibitory microcircuits throughout the neocortex and their dysfunction has been implicated in epilepsy and neuropsychiatric diseases. Developmentally, interneurons migrate from a distal progenitor domain in order to populate the neocortex - a process that occurs at a slower rate in humans than in mice. In this study, we sought to identify factors that regulate the rate of interneuron maturation across the two species. Using embryonic mouse development as a model system, we found that the process of initiating interneuron migration is regulated by blood vessels of the medial ganglionic eminence (MGE), an interneuron progenitor domain. We identified two endothelial cell-derived paracrine factors, SPARC and SerpinE1, that enhance interneuron migration in mouse MGE explants and organotypic cultures. Moreover, pre-treatment of human stem cell-derived interneurons (hSC-interneurons) with SPARC and SerpinE1 prior to transplantation into neonatal mouse cortex enhanced their migration and morphological elaboration in the host cortex. Further, SPARC and SerpinE1-treated hSC-interneurons also exhibited more mature electrophysiological characteristics compared to controls. Overall, our studies suggest a critical role for CNS vasculature in regulating interneuron developmental maturation in both mice and humans.", "pub_date": "2021-Apr-27"}, {"title": "Reset of hippocampal-prefrontal circuitry facilitates learning.", "abstract": "The ability to rapidly\u00a0adapt to novel situations is essential for survival, and this flexibility\u00a0is impaired in many neuropsychiatric disorders", "pub_date": "2021"}, {"title": "Aberrant Cortical Ensembles and Schizophrenia-like Sensory Phenotypes in Setd1a", "abstract": "A breakdown of synchrony within neuronal ensembles leading to destabilization of network \"attractors\" could be a defining aspect of neuropsychiatric diseases such as schizophrenia, representing a common downstream convergence point for the diverse etiological pathways associated with the disease. Using a mouse genetic model, we demonstrated that altered ensembles are associated with pathological sensory cortical processing phenotypes resulting from loss of function mutations in the Setd1a gene, a recently identified rare risk genotype with very high penetrance for schizophrenia.", "pub_date": "2020-Aug-01"}, {"title": "Recapitulation and Reversal of Schizophrenia-Related Phenotypes in Setd1a-Deficient Mice.", "abstract": "SETD1A, a lysine-methyltransferase, is a key schizophrenia susceptibility gene. Mice carrying a heterozygous loss-of-function mutation of the orthologous gene exhibit alterations in axonal branching and cortical synaptic dynamics accompanied by working memory deficits. We show that Setd1a binds both promoters and enhancers with a striking overlap between Setd1a and Mef2 on enhancers. Setd1a targets\u00a0are highly expressed in pyramidal neurons and display a complex pattern of transcriptional up- and downregulations shaped by presumed opposing functions of Setd1a on promoters and Mef2-bound enhancers. Notably, evolutionarily conserved Setd1a targets are associated with neuropsychiatric genetic risk burden. Reinstating Setd1a expression in adulthood rescues cognitive deficits. Finally, we identify LSD1 as a major counteracting demethylase for Setd1a and show that its pharmacological antagonism results in a full rescue of the behavioral and morphological deficits in Setd1a-deficient mice. Our findings advance understanding of how SETD1A mutations predispose to schizophrenia (SCZ) and point to novel therapeutic interventions.", "pub_date": "2019-Nov-06"}, {"title": "The abiding relevance of mouse models of rare mutations to psychiatric neuroscience and therapeutics.", "abstract": "Studies using powerful family-based designs aided by large scale case-control studies, have been instrumental in cracking the genetic complexity of the disease, identifying rare and highly penetrant risk mutations and providing a handle on experimentally tractable model systems. Mouse models of rare mutations, paired with analysis of homologous cognitive and sensory processing deficits and state-of-the-art neuroscience methods to manipulate and record neuronal activity have started providing unprecedented insights into pathogenic mechanisms and building the foundation of a new biological framework for understanding mental illness. A number of important principles are emerging, namely that degradation of the computational mechanisms underlying the ordered activity and plasticity of both local and long-range neuronal assemblies, the building blocks necessary for stable cognition and perception, might be the inevitable consequence and the common point of convergence of the vastly heterogeneous genetic liability, manifesting as defective internally- or stimulus-driven neuronal activation patterns and triggering the constellation of schizophrenia symptoms. Animal models of rare mutations have the unique potential to help us move from \"which\" (gene) to \"how\", \"where\" and \"when\" computational regimes of neural ensembles are affected. Linking these variables should improve our understanding of how symptoms emerge and how diagnostic boundaries are established at a circuit level. Eventually, a better understanding of pathophysiological trajectories at the level of neural circuitry in mice, aided by basic human experimental biology, should guide the development of new therapeutics targeting either altered circuitry itself or the underlying biological pathways.", "pub_date": "2020"}, {"title": "Systems Analysis of the 22q11.2 Microdeletion Syndrome Converges on a Mitochondrial Interactome Necessary for Synapse Function and Behavior.", "abstract": "Neurodevelopmental disorders offer insight into synaptic mechanisms. To unbiasedly uncover these mechanisms, we studied the 22q11.2 syndrome, a recurrent copy number variant, which is the highest schizophrenia genetic risk factor. We quantified the proteomes of 22q11.2 mutant human fibroblasts from both sexes and mouse brains carrying a 22q11.2-like defect, ", "pub_date": "2019-May-01"}, {"title": "Neurocognitive and Perceptual Processing in Genetic Mouse Models of Schizophrenia: Emerging Lessons.", "abstract": "During the past two decades, the number of animal models of psychiatric disorders has grown exponentially. Of these, genetic animal models that are modeled after rare but highly penetrant mutations hold great promise for deciphering critical molecular, synaptic, and neurocircuitry deficits of major psychiatric disorders, such as schizophrenia. Animal models should aim to focus on core aspects rather than capture the entire human disease. In this context, animal models with strong etiological validity, where behavioral and neurophysiological phenotypes and the features of the disease being modeled are in unambiguous homology, are being used to dissect both elementary and complex cognitive and perceptual processing deficits present in psychiatric disorders at the level of neurocircuitry, shedding new light on critical disease mechanisms. Recent progress in neuroscience along with large-scale initiatives that propose a consistent approach in characterizing these deficits across different laboratories will further enhance the efficacy of these studies that will ultimately lead to identifying new biological targets for drug development.", "pub_date": "2019"}, {"title": "Role of Endogenous Metabolite Alterations in Neuropsychiatric Disease.", "abstract": "The potential role in neuropsychiatric disease risk arising from alterations and derangements of endogenous small-molecule metabolites remains understudied. Alterations of endogenous metabolite concentrations can arise in multiple ways. Marked derangements of single endogenous small-molecule metabolites are found in a large group of rare genetic human diseases termed \"inborn errors of metabolism\", many of which are associated with prominent neuropsychiatric symptomology. Whether such metabolites act neuroactively to directly lead to distinct neural dysfunction has been frequently hypothesized but rarely demonstrated unequivocally. Here we discuss this disease concept in the context of our recent findings demonstrating that neural dysfunction arising from accumulation of the schizophrenia-associated metabolite l-proline is due to its structural mimicry of the neurotransmitter GABA that leads to alterations in GABA-ergic short-term synaptic plasticity. For cases in which a similar direct action upon neurotransmitter binding sites is suspected, we lay out a systematic approach that can be extended to assessing the potential disruptive action of such candidate disease metabolites. To address the potentially important and broader role in neuropsychiatric disease, we also consider whether the more subtle yet more ubiquitous variations in endogenous metabolites arising from natural allelic variation may likewise contribute to disease risk but in a more complex and nuanced manner.", "pub_date": "2018-Sep-19"}, {"title": "Altered function and maturation of primary cortical neurons from a 22q11.2 deletion mouse model of schizophrenia.", "abstract": "Given its high penetrance, clearly delineated and evolutionary conserved genomic structure, mouse models of the 22q11.2 deletion provide an ideal organism-based and cell-based model of this well-established disease mutation for schizophrenia. In this study we examined the development of changes in intrinsic properties, action potential firing and synaptic transmission using whole-cell patch-clamp recordings of cultured embryonic cortical neurons from Df(16)A ", "pub_date": "2018-Apr-18"}, {"title": "Hippocampal-prefrontal theta-gamma coupling during performance of a spatial working memory task.", "abstract": "Cross-frequency coupling supports the organization of brain rhythms and is present during a range of cognitive functions. However, little is known about whether and how long-range cross-frequency coupling across distant brain regions subserves working memory. Here we report that theta-slow gamma coupling between the hippocampus and medial prefrontal cortex (mPFC) is augmented in a genetic mouse model of cognitive dysfunction. This increased cross-frequency coupling is observed specifically when the mice successfully perform a spatial working memory task. In wild-type mice, increasing task difficulty by introducing a long delay or by optogenetically interfering with encoding, also increases theta-gamma coupling during correct trials. Finally, epochs of high hippocampal theta-prefrontal slow gamma coupling are associated with increased synchronization of neurons within the mPFC. These findings suggest that enhancement of theta-slow gamma coupling reflects a compensatory mechanism to maintain spatial working memory performance in the setting of increased difficulty.", "pub_date": "2017-Dec-19"}, {"title": "EMC10 (Endoplasmic Reticulum Membrane Protein Complex Subunit 10) Is a Bone Marrow-Derived Angiogenic Growth Factor Promoting Tissue Repair After Myocardial Infarction.", "abstract": "Clinical trials of bone marrow cell-based therapies after acute myocardial infarction (MI) have produced mostly neutral results. Treatment with specific bone marrow cell-derived secreted proteins may provide an alternative biological approach to improving tissue repair and heart function after MI. We recently performed a bioinformatic secretome analysis in bone marrow cells from patients with acute MI and discovered a poorly characterized secreted protein, EMC10 (endoplasmic reticulum membrane protein complex subunit 10), showing activity in an angiogenic screen.", "pub_date": "2017-Nov-07"}]}"""},
        {"role": "assistant", "content": """
                {
                    "Researcher": "Joseph A. Gogos",
                    "Research Overview": "Joseph A. Gogos' research focuses on the genetic and neurobiological mechanisms underlying neuropsychiatric disorders, particularly schizophrenia and autism. He investigates how genetic mutations and disruptions in neural circuits contribute to these conditions. Gogos uses a combination of genetic, molecular, and behavioral approaches to study animal models of neuropsychiatric disorders. His work aims to identify potential therapeutic targets and develop new strategies for treating these disorders.",
                    "Research Interests": [
                      "Neuropsychiatric Disorders",
                      "Schizophrenia",
                      "Autism",
                      "Genetic Mutations",
                      "Neural Circuits",
                      "Behavioral Approaches",
                      "Molecular Neuroscience",
                      "Animal Models",
                      "Therapeutic Targets",
                      "Treatment Strategies"
                    ]
                  }
                """
         },
        {"role": "user", "content": "Now do the same for the following researcher: "+research_articles}
    ])
    return response.choices[0].message.content
def parser_response(response):
    return response[response.index('{'):response.index('}')+1]

def parse_MeSh_keyword(path):
    keywords = []
    mesh_terms = []

    # Load the JSON data from the file
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Iterate over the articles and extract the keywords and MeSH terms
    for article in data:
        keywords.extend(article.get('Keywords', []))
        mesh_terms.extend(article.get('MeSH terms', []))

    return keywords, mesh_terms

def prompt_research_summary_based_on_abstract():
    input_file = "researcher_profile.json"
    with open(input_file, 'r') as file:
        research_articles_list = json.load(file)

    summaries = []
    for articles in research_articles_list:
        articles_json_str = json.dumps(articles)
        response = get_chatgpt_response(articles_json_str)
        response = parser_response(response)
        print(response)
        json_list = json.loads(response)
        summaries.append(json_list)
    output_file = "researcher_summaries.json"

    with open(output_file, 'w') as file:
        json.dump(summaries, file, indent=4)

    print("ChatGPT Responses saved to", output_file)

def prompt_research_interest_based_on_MeSH():
    folder_path = 'researchers_files_new'
    # folder_path = 'output'
    research_txt = []
    for filename in os.listdir("Research Interests"):
        if filename.endswith('.txt'):
            name, _ = os.path.splitext(filename)

            research_txt.append(name)

    for filename in os.listdir(folder_path):
        print(f"Reading {filename}")
        if filename.endswith('.json'):
            name, _ = os.path.splitext(filename)
            # name = compare_name_matches.extract_name_from_filename(filename)
            if name in research_txt:
                continue
        else:
            continue
        json_file_path = os.path.join(folder_path,filename)
        keywords, mesh_terms = parse_MeSh_keyword(json_file_path)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
              {"role": "system",
               "content": "You are a helpful Researcher profile summarizing assistant."},
              {"role": "user", "content": f"Based on the Keywords and MeSH Terms extracted from mulitple research papers from the researcher, summarize them and generate me 10 research interests that conclude the researcher's research. Return the result as a python list."
                                          f"Keywords: {keywords}"
                                          f"MeSH Terms: {mesh_terms}"},


            ]
        )
        content = response.choices[0].message.content
        print(content)
        research_interest = content[content.index('['):content.index(']')+1]

        txt_file_path = os.path.join("Research Interests", f"{name}.txt")
        with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(f"Researcher: {name}\n")
            txt_file.write("Research Interests:\n")
            txt_file.write(research_interest)

        print(f"Research interests saved to {txt_file_path}")

def prompt_research_overview_based_on_MeSH():
    folder_path = 'researchers_files_new'
    # folder_path = 'output'
    research_txt = []
    for filename in os.listdir("Research Overview New"):
        if filename.endswith('.txt'):
            name, _ = os.path.splitext(filename)

            research_txt.append(name)

    for filename in os.listdir(folder_path):
        print(f"Reading {filename}")
        if filename.endswith('.json'):
            name, _ = os.path.splitext(filename)
            # name = compare_name_matches.extract_name_from_filename(filename)
            if name in research_txt:
                continue
        else:
            continue
        json_file_path = os.path.join(folder_path,filename)
        keywords, mesh_terms = parse_MeSh_keyword(json_file_path)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
              {"role": "system",
               "content": "You are a helpful Researcher profile summarizing assistant."},
              {"role": "user", "content": f"Based on the Keywords and MeSH Terms extracted from mulitple research papers from the researcher, summarize them and generate me a paragraph that conclude the researcher's research."
                                          f"Name: {name}"
                                          f"Keywords: {keywords}"
                                          f"MeSH Terms: {mesh_terms}"}


            ]
        )
        content = response.choices[0].message.content
        print(content)

        txt_file_path = os.path.join("Research Overview New", f"{name}.txt")
        with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(f"Researcher: {name}\n")
            txt_file.write("Research Overview:\n")
            txt_file.write(content)

        print(f"Research interests saved to {txt_file_path}")



if __name__ == "__main__":
    prompt_research_overview_based_on_MeSH()
    # prompt_research_interest_based_on_MeSH()