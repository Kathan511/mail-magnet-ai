from langgraph.graph import END
from langchain_core.messages import SystemMessage, HumanMessage
from typing import TypedDict, Annotated, List
# from pydantic import BaseModel,
import operator
from langgraph.constants import Send
from llama_index.readers.web import BeautifulSoupWebReader




#activate the Scraping loader
loader=BeautifulSoupWebReader()

class ScrapeMaster(TypedDict):
    target_urls: Annotated[List,"The list of tartget URLs"]
    summerized_url_text: Annotated[List[str],operator.add]
    target_summmary: Annotated[str,"The final summary"]
    source_text:Annotated[str,"the source text of the organization"]
    draft_email: Annotated[str,"The final draft email"]
    human_reviewer_feedback: str
    llm: object



class SummerizeURLs(TypedDict):
    url_to_scrape: Annotated[str,"The URL to scrape"]
    llm:object


def scrape_and_summerize_text(state:SummerizeURLs):
    """This function scrapes the text from the given URL"""
    
    url_to_scrape= state['url_to_scrape']

    #scrape the url
    scraped_text = loader.load_data([url_to_scrape])[0].text

    sys_msg="""You are a professional text summarizer specializing in business insights. For the given text, generate a concise  summary highlighting the business aspects, such as the solutions being provided, the target audience, and the value proposition."""

    result_summary=state['llm'].invoke([SystemMessage(content=sys_msg)] + [SystemMessage(content=f"Give me summary of {scraped_text}")])

    return {'summerized_url_text': [result_summary.content]}

def summerized_all_summaries(state:ScrapeMaster):
    """This function Gives summary from all URL's summaries"""
    
    summerized_url_text = state['summerized_url_text']

    sys_msg="""You are a professional text summarizer specializing in business insights. For the given text, generate a concise summary highlighting the business aspects, such as the solutions being provided, the target audience, and the value proposition."""

    result= state['llm'].invoke([SystemMessage(content=sys_msg)] +  [HumanMessage(content="\n".join(f"{summary}" for summary in summerized_url_text))])

    return {'target_summmary':result.content}


    
def scrape_summeries(state:ScrapeMaster):
    """This function scrapes the given URLs and returns the summary"""

    target_urls = state['target_urls'] 

    print(target_urls)

    #call the function for each 
    return [Send("scrape_and_summerize_text", {"url_to_scrape": url,"llm":state['llm']}) for url in target_urls]


def generate_draft_email(state:ScrapeMaster):
    """This function gives a draft email"""

    #Fetch the source text
    source_text = state['source_text']
    target_text=state['target_summmary']
    print("done")
    human_reviewer_feedback = state.get("human_reviewer_feedback",None)
    print(human_reviewer_feedback)

    sys_msg=f"""Draft a professional and persuasive email from [Source Text] to [Target Text], highlighting how the services offered by [Source Text] can enhance or complement the services provided by [Target Text]. 
                Ensure the email is engaging, value-driven, and customized to the recipient’s industry. Maintain a polite and professional tone while clearly outlining the key benefits of collaboration. In the subject include Source text's company name.
                Include a compelling introduction, specific advantages, and a call to action that encourages further discussion. Only give an email as an output, Nothing else.
                
                Examine any editorial feedback that has been optionally provided to guide creation on email. (The feedback can be None):
                {human_reviewer_feedback}

               Source Text:{source_text} 
               Target Text: {target_text}""".format(human_reviewer_feedback=human_reviewer_feedback, source_text=source_text,target_text=target_text)
    
    result = state['llm'].invoke([SystemMessage(content=sys_msg)] + [HumanMessage(content='Give me a draft email.')])

    return {'draft_email':result.content}


def human_feedback_func(state:ScrapeMaster):
    pass

def should_continue(state:ScrapeMaster):
    human_reviewer_feedback = state.get('human_reviewer_feedback',None)

    if human_reviewer_feedback:
        print("In generate email")
        return "generate_draft_email"
    
    else:
        return END
