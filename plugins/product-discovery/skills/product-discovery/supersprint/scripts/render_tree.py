#!/usr/bin/env python3
"""Eksport częściowego lub pełnego drzewa Supersprintu bez zależności sieciowych."""
import argparse,copy,hashlib,html,json,os,re
from pathlib import Path
from urllib.parse import urlsplit

TYPES=['goal','opportunity','idea','experiment','result','decision','signal']
UI={
 'en':dict(title='Supersprint',stage='Stage',opportunities='Opportunities',ideas='Ideas',experiments='Experiments',results='Results',signals='Supporting signals',empty='No tree nodes yet. Define the direction first.',source='Full description and sources',close='Close',selected='Selected path',recommended='Recommendation',details='Details',goal='Goal',opportunity='Opportunities',idea='Ideas',experiment='Experiments',result='Observed results',decision='Decision',signal='Signals',hypothesis='Hypothesis',method='How we test',measure='What we measure',draft='Proposed',proposed='Proposed',provisional='Working goal',selected_status='Selected',alternative='Alternative',pending='Pending review',accepted='Accepted',conditional='Conditional test',hint='Scroll to explore the tree. Click a card for a brief preview.'),
 'pl':dict(title='Supersprint',stage='Etap',opportunities='Szanse',ideas='Pomysły',experiments='Eksperymenty',results='Wyniki',signals='Sygnały wspierające',empty='Nie ma jeszcze węzłów drzewa. Najpierw ustalmy kierunek.',source='Pełny opis i źródła',close='Zamknij',selected='Wybrana ścieżka',recommended='Rekomendacja',details='Podgląd',goal='Cel',opportunity='Szanse',idea='Pomysły',experiment='Eksperymenty',result='Zaobserwowane wyniki',decision='Decyzja',signal='Sygnały',hypothesis='Hipoteza',method='Jak sprawdzimy',measure='Co mierzymy',draft='Propozycja',proposed='Propozycja',provisional='Cel roboczy',selected_status='Wybrane',alternative='Alternatywa',pending='Do przeglądu',accepted='Przyjęte',conditional='Test warunkowy',hint='Przewiń, aby obejrzeć drzewo. Kliknij kartę, aby zobaczyć krótki podgląd.')}

def esc(value):return html.escape(str(value),quote=True)
def dump(value):return json.dumps(value,ensure_ascii=False,indent=2)+'\n'
def json_safe(value):return json.dumps(value,ensure_ascii=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
def source_link(raw,cycle,output):
 if not raw:return None
 raw=str(raw)
 if any(ord(c)<32 for c in raw) or '\\' in raw:return None
 scheme=urlsplit(raw).scheme.lower()
 if scheme in ['http','https']:return raw
 if scheme or raw.startswith('//'):return None
 return os.path.relpath((cycle/raw).resolve(),output.parent)

def normalize(state,graph,cycle,output):
 data=copy.deepcopy(graph);lang=str(state.get('language',graph.get('language','en'))).split('-')[0]
 ui={**UI.get(lang,UI['en']),**state.get('tree_ui',{}),**graph.get('tree_ui',{})}
 raw_nodes=data.get('nodes',[]);raw_edges=data.get('edges',[])
 if not isinstance(raw_nodes,list) or not isinstance(raw_edges,list):raise ValueError('nodes and edges must be lists')
 if any(n.get('type')=='assumption' for n in raw_nodes):raise ValueError('Put hypotheses inside experiment nodes, not a separate assumption layer')
 ids=[n.get('id') for n in raw_nodes]
 if any(not isinstance(i,str) or not i.strip() for i in ids) or len(set(ids))!=len(ids):raise ValueError('Node IDs must be unique nonempty strings')
 if any(n.get('type') not in TYPES for n in raw_nodes):raise ValueError('Unknown node type')
 for edge in raw_edges:
  if edge.get('source') not in ids or edge.get('target') not in ids:raise ValueError('Dangling edge')
 selected=set(state.get('selected_idea_ids',[])+state.get('selected_experiment_ids',[]))
 if state.get('selected_opportunity_id'):selected.add(state['selected_opportunity_id'])
 if not selected.issubset(ids):raise ValueError('Selected IDs are missing from the tree')
 recommended=set(state.get('recommended_next_experiment_ids',[]))
 if state.get('recommended_next_experiment_id'):recommended.add(state['recommended_next_experiment_id'])
 nodes=[]
 for raw in raw_nodes:
  n=copy.deepcopy(raw);card=n.get('card',{});title=card.get('title') or n.get('title') or n.get('display_label') or n.get('label')
  if not isinstance(title,str) or not title.strip():raise ValueError('Every node needs a title/label')
  n['title']=title;n['summary']=n.get('summary','')
  selection_key={'opportunity':'selected_opportunity_id','idea':'selected_idea_ids','experiment':'selected_experiment_ids'}.get(n['type'])
  n['selected']=n['id'] in selected if selection_key in state else bool(n.get('selected')) or n.get('status')=='selected'
  n['on_path']=n['selected'] or n['type']=='goal'
  n['recommended']=n['id'] in recommended if 'recommended_next_experiment_ids' in state or 'recommended_next_experiment_id' in state else bool(n.get('recommended'))
  status=n.get('status','draft');status_key='selected_status' if status=='selected' else status
  n['status_label']=n.get('status_label') or ui.get(status_key,status)
  n['link']=source_link(n.get('artifact_path') or n.get('source_path'),cycle,output)
  if n.get('preview_blocks') is not None:preview=n['preview_blocks']
  elif n['type']=='experiment' and card:preview=[dict(label=ui[caption],body=card.get(key,'')) for caption,key in [('hypothesis','hypothesis'),('method','experiment'),('measure','observable')]]
  else:preview=[dict(label='',body=n.get('description') or n['summary'] or title)]
  if not isinstance(preview,list) or any(not isinstance(b,dict) or not isinstance(b.get('body'),str) for b in preview):raise ValueError('Invalid preview_blocks')
  n['preview_blocks']=preview;nodes.append(n)
 by_id={n['id']:n for n in nodes}
 edges=[]
 for e in raw_edges:
  e=copy.deepcopy(e);e['evidence']='evidence' in e.get('type','') or 'reference' in e.get('type','') or by_id[e['source']]['type']=='signal' or e.get('type')=='baseline_source'
  e['on_path']=not e['evidence'] and by_id[e['source']]['on_path'] and by_id[e['target']]['on_path'];edges.append(e)
 return dict(language=lang,ui=ui,nodes=nodes,edges=edges,stage=state.get('current_stage',''),question=state.get('working_question') or state.get('context',{}).get('working_question') or '',revision=state.get('tree',{}).get('revision',1))

LAYOUT='''
.shell{max-width:1800px;margin:auto;padding:24px}.heading{display:flex;justify-content:space-between;align-items:center;gap:24px;margin-bottom:20px}.heading p{color:var(--muted);max-width:850px}.board{position:relative;border:1px solid var(--line);border-radius:16px;background:var(--surface);overflow:auto;padding:32px;max-height:75vh}.world{position:relative;width:max-content;min-width:100%}.axis{display:flex;gap:44px;align-items:stretch;position:relative;z-index:1}.lane{width:280px;flex-shrink:0}.lane h2{font-size:12px;color:var(--muted)}.stack{display:flex;flex-direction:column;justify-content:center;gap:18px;height:calc(100% - 34px)}.node{display:block;width:280px;min-height:155px;padding:18px;border-radius:16px;text-align:left;font-size:13px;background:white}.node.selected-path{padding:16px;border:3px solid var(--ink)}.node.recommended{padding:17px;border:2px dashed var(--muted)}.node.selected-path.recommended{border:3px solid var(--ink);padding:16px}.node:focus-visible{outline-offset:5px}.node h3{font-size:14px;font-weight:500;margin:12px 0 8px}.node p{font-size:13px;color:var(--muted);margin-bottom:0}.node .meta{display:flex;align-items:center;justify-content:space-between;color:var(--quiet);font-size:12px}.node .status-line{display:block;margin-top:14px;color:var(--muted);font-size:12px}.signals{position:relative;z-index:1;margin-top:64px;padding-top:24px;border-top:1px solid var(--line)}.signal-list{display:flex;flex-wrap:wrap;gap:18px}.connections{position:absolute;left:0;top:0;pointer-events:none;overflow:visible}.edge{fill:none;stroke:#C9C9C9;stroke-width:1.2}.edge.evidence{stroke-dasharray:4 5}.edge.on-path{stroke:var(--ink);stroke-width:3}.inspected{box-shadow:0 0 0 4px #29292914}.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:12px;color:var(--muted);margin:16px 0}.legend span{display:inline-flex;gap:8px;align-items:center}.swatch{width:12px;height:12px;border:2px solid var(--ink);border-radius:3px}.swatch.recommendation{border:1px dashed var(--muted)}.detail{position:fixed;right:24px;top:24px;width:420px;max-width:calc(100vw - 48px);max-height:calc(100vh - 48px);overflow:auto;padding:24px;background:white;border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);z-index:5}.detail[hidden]{display:none}.detail-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;color:var(--quiet);font-size:12px}.detail h2{font-size:24px}.detail p{font-size:14px;color:var(--muted)}.detail h3{font-size:13px;margin-top:18px}.empty{padding:24px;color:var(--muted)}.hint{font-size:12px;color:var(--quiet)}@media(max-width:700px){.shell{padding:16px}.heading{align-items:flex-start;flex-direction:column;gap:8px}.board{padding:20px}.detail{top:auto;bottom:12px;left:12px;right:12px;max-width:none;width:auto;max-height:65vh}}@media print{.board{max-height:none;overflow:visible}.detail{display:none}.world{min-width:0}.node{break-inside:avoid}.hint{display:none}}
'''
JS='''
const DATA=JSON.parse(document.getElementById('tree-data').textContent);const buttons=[...document.querySelectorAll('[data-node]')],world=document.getElementById('world'),svg=document.getElementById('connections'),detail=document.getElementById('detail');
const nodes=new Map(DATA.nodes.map(n=>[n.id,n]));
function connect(){const box=world.getBoundingClientRect();svg.replaceChildren();svg.setAttribute('width',world.scrollWidth);svg.setAttribute('height',world.scrollHeight);for(const e of DATA.edges){const a=buttons.find(b=>b.dataset.node===e.source),b=buttons.find(b=>b.dataset.node===e.target);if(!a||!b)continue;const ar=a.getBoundingClientRect(),br=b.getBoundingClientRect();let x1=ar.right-box.left,y1=ar.top+ar.height/2-box.top,x2=br.left-box.left,y2=br.top+br.height/2-box.top;if(e.evidence&&nodes.get(e.source).type==='signal'){x1=ar.left+ar.width/2-box.left;y1=ar.top-box.top;x2=br.left+br.width/2-box.left;y2=br.bottom-box.top;}const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',`M ${x1} ${y1} C ${(x1+x2)/2} ${y1}, ${(x1+x2)/2} ${y2}, ${x2} ${y2}`);p.setAttribute('class','edge'+(e.evidence?' evidence':'')+(e.on_path?' on-path':''));svg.append(p);}}
function close(){detail.hidden=true;buttons.forEach(b=>{b.classList.remove('inspected');b.setAttribute('aria-expanded','false');});}
buttons.forEach(button=>button.addEventListener('click',()=>{close();const n=nodes.get(button.dataset.node);detail.hidden=false;button.classList.add('inspected');button.setAttribute('aria-expanded','true');document.getElementById('detail-kind').textContent=n.id+' · '+n.status_label;document.getElementById('detail-title').textContent=n.title;const content=document.getElementById('detail-copy');content.replaceChildren();for(const block of n.preview_blocks){if(block.label){const h=document.createElement('h3');h.textContent=block.label;content.append(h);}const p=document.createElement('p');p.textContent=block.body;content.append(p);}const source=document.getElementById('detail-source');source.hidden=!n.link;if(n.link)source.setAttribute('href',n.link);}));
document.getElementById('close').addEventListener('click',close);addEventListener('keydown',e=>{if(e.key==='Escape')close();});new ResizeObserver(connect).observe(world);if(document.fonts)document.fonts.ready.then(connect);connect();
'''

def render(data,css):
 ui=data['ui']
 def card(n):
  summary=n['summary'] or n.get('card',{}).get('hypothesis','')
  kind='selected-path' if n['on_path'] else ''
  if n['recommended']:kind+=' recommended'
  mark=' · '+ui['recommended'] if n['recommended'] else ''
  icon='<svg class="card-icon" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M4 3h12v14H4ZM7 7h6M7 11h6"/></svg>'
  return f'<button class="node {kind}" type="button" data-node="{esc(n["id"])}" aria-controls="detail" aria-expanded="false"><span class="meta"><span>{esc(n["id"])}</span>{icon}</span><h3>{esc(n["title"])}</h3><p>{esc(summary)}</p><span class="status-line">{esc(n["status_label"]+mark)}</span></button>'
 columns=[]
 for kind in TYPES[:-1]:
  items=[n for n in data['nodes'] if n['type']==kind]
  if items:columns.append(f'<section class="lane"><h2>{esc(ui[kind])}</h2><div class="stack">'+''.join(card(n) for n in items)+'</div></section>')
 signals=[n for n in data['nodes'] if n['type']=='signal'];signal_html=f'<section class="signals"><h2>{esc(ui["signals"])}</h2><div class="signal-list">'+''.join(card(n) for n in signals)+'</div></section>' if signals else ''
 empty=f'<p class="empty">{esc(ui["empty"])}</p>' if not data['nodes'] else ''
 return f'''<!doctype html><html lang="{esc(data['language'])}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(ui['title'])}</title><style>{css}\n{LAYOUT}</style></head><body><main class="shell"><header class="heading"><div><h1>{esc(ui['title'])}</h1><p>{esc(data['question'])}</p></div><span class="status">{esc(ui['stage'])}: {esc(ui.get(data['stage'],data['stage']))} · r{data['revision']}</span></header><div class="board"><div class="world" id="world"><svg id="connections" class="connections" aria-hidden="true"></svg><div class="axis">{''.join(columns)}</div>{signal_html}{empty}</div></div><div class="legend"><span><i class="swatch"></i>{esc(ui['selected'])}</span><span><i class="swatch recommendation"></i>{esc(ui['recommended'])}</span></div><p class="hint">{esc(ui['hint'])}</p></main><aside class="detail" id="detail" aria-labelledby="detail-title" hidden><div class="detail-head"><span id="detail-kind"></span><button id="close" type="button">{esc(ui['close'])}</button></div><h2 id="detail-title"></h2><div id="detail-copy"></div><a id="detail-source" class="cta">{esc(ui['source'])}</a></aside><script type="application/json" id="tree-data">{json_safe(data)}</script><script>{JS}</script></body></html>'''

def mermaid(data):
 ids={n['id']:'n'+str(i) for i,n in enumerate(data['nodes'])}
 lines=['graph LR','  %% Only existing nodes; hypotheses are inside experiments.']
 for n in data['nodes']:
  text=esc(n['title']).replace('"','#quot;').replace('\n',' ')
  lines.append(f'  {ids[n["id"]]}["{esc(n["id"])}<br/>{text}<br/>{esc(n["status_label"])}"]')
 for e in data['edges']:lines.append(f'  {ids[e["source"]]} '+('-.->' if e['evidence'] else '-->')+f' {ids[e["target"]]}')
 lines+=['  classDef selected fill:#FFFFFF,stroke:#292929,stroke-width:3px;','  classDef recommended fill:#FFFFFF,stroke:#5D5D5D,stroke-width:2px,stroke-dasharray:5 4;']
 for n in data['nodes']:
  if n['on_path']:lines.append(f'  class {ids[n["id"]]} selected;')
  elif n['recommended']:lines.append(f'  class {ids[n["id"]]} recommended;')
 return '\n'.join(lines)+'\n'

def export(state_path,output,snapshot=False,validate_only=False):
 state=json.loads(state_path.read_text(encoding='utf-8'));cycle=state_path.parent
 projection=state.get('tree',{}).get('projection_path');graph=json.loads((cycle/projection).read_text(encoding='utf-8')) if projection else dict(nodes=state.get('nodes',[]),edges=state.get('edges',[]))
 data=normalize(state,graph,cycle,output)
 if validate_only:return data
 css=(Path(__file__).resolve().parents[1]/'assets/html-style.css').read_text(encoding='utf-8');document=render(data,css);mmd=mermaid(data)
 revision=data['revision']
 if not isinstance(revision,int) or isinstance(revision,bool) or revision<1:raise ValueError('tree.revision must be a positive integer')
 files={'state.json':state_path.read_bytes(),'graph.json':dump(data).encode(),'tree.mmd':mmd.encode()}
 snap=output.parent/'snapshots'/f'r{revision:04d}'
 manifest=dict(revision=revision,sha256={name:hashlib.sha256(content).hexdigest() for name,content in files.items()})
 # Nigdy nie nadpisujemy innej migawki pod tym samym numerem.
 if snapshot and snap.exists():
  if not (snap/'manifest.json').exists() or json.loads((snap/'manifest.json').read_text())!=manifest:raise ValueError('Snapshot already exists with different contents; increment tree.revision')
  if any(not (snap/name).exists() or (snap/name).read_bytes()!=content for name,content in files.items()):raise ValueError('Existing snapshot is incomplete or changed; do not overwrite it')
 output.parent.mkdir(parents=True,exist_ok=True)
 if snapshot and not snap.exists():
  snap.mkdir(parents=True)
  for name,content in files.items():(snap/name).write_bytes(content)
  (snap/'manifest.json').write_text(dump(manifest),encoding='utf-8')
 output.write_text(document,encoding='utf-8');output.with_suffix('.mmd').write_text(mmd,encoding='utf-8');return data

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('state',type=Path);p.add_argument('--output',type=Path);p.add_argument('--snapshot',action='store_true');p.add_argument('--validate-only',action='store_true');a=p.parse_args()
 output=a.output or a.state.parent/'tree/tree.html'
 try:
  data=export(a.state,output,a.snapshot,a.validate_only);print(f'{len(data["nodes"])} nodes, {len(data["edges"])} edges; '+('validated' if a.validate_only else str(output)))
 except (ValueError,OSError,KeyError,TypeError) as e:p.exit(1,f'Error: {e}\n')
if __name__=='__main__':main()
