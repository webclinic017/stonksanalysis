from googleapiclient.discovery import build
from polygon import RESTClient
import pandas as pd
import search_web
import call_ai

def read_search(google_key, polygon_key, search_id, query, prompt_template, model, write_to_dir, **kwargs):
  search_service = build("customsearch", "v1", developerKey=google_key).cse()
  
  all_results=search_web.all_search_pages(
        service=search_service, 
        cse_id=search_id, 
        q=query,
        sort="date",
        num=10,
        **kwargs)
  print(f"{len(all_results)} total results")
  
  valid_results = call_ai.read_results(all_results, prompt_template, model)
  print(f"{len(valid_results)} valid results")
  poly_client = RESTClient(api_key=polygon_key)
  default_data={
    'date': '03/12/2024',
    'symbol': '',
    'strike_price': '',
    'action': 'BUY',
    'order_type': 'MKT',
    'time_in_force': 'OPG',
    'asset_type': 'liquid',
    'companyName':'',
  }
  print("############################ MATCHING RESULTS: "+query)
  enriched_results = [call_ai.enrich_result(r, poly_client) for r in valid_results]
  print(f"{len(enriched_results)} enriched results")
  print(f"{len([x for x in enriched_results if x['match'] ])} matching enriched results")
  already_tracked = pd.DataFrame([default_data])
  for r in enriched_results:
    if r['match'] and not (already_tracked['companyName']==r['companyName']).any():
      model_out=model.generate_content("Reformat the following time as YYYY-MM-DD HH:MM using military time (put 00:00 if no time is provided):"+ r['timePublished'])
      try:
        r['timePublished'] = model_out.text.strip()
      except:
        r['timePublished'] = 'cannot be formatted'
      print(r['timePublished'],r['ticker'],r['link'],r['title'])
      already_tracked=pd.concat([already_tracked, pd.DataFrame([r])], ignore_index=True)
  already_tracked.to_csv(write_to_dir+query.replace('|','_')+'.csv')
  
  print("############################ OTHER RESULTS: "+query)
  for r in enriched_results:
    model_out=model.generate_content("Reformat the following time as YYYY-MM-DD HH:MM using military time:"+ r['timePublished'])
    try:
      r['timePublished'] = model_out.text.strip()
    except:
      r['timePublished'] = 'cannot be formatted'
    if not r['match'] and  not (already_tracked['companyName']==r['companyName']).any():
      print(r['timePublished'],r['ticker'],r['message'])
