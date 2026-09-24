"""Review screen: one self-contained HTML page over a dossier run and a valuation run.

Every number on the page is read from run.json / valuation.json; the page computes
nothing except formatting. Clicking a figure shows where it came from.
"""

from __future__ import annotations

import json
from pathlib import Path

from .dossier import ROWS

GROUPS = [("Growth and profitability", "growth"), ("EPS", "eps"), ("Cash conversion", "cash"),
          ("Investment", "investment"), ("Quality, capital and debt", "quality")]
FMT = {"money": ["revenue", "net_income", "cfo", "capex", "fcf", "fcf_after_sbc", "dna", "sbc", "buybacks", "dividends",
                 "total_debt", "liquid_investments", "net_debt", "operating_lease_liability"],
       "shares": ["shares_diluted"], "ps": ["eps_diluted"],
       "signed": ["revenue_growth", "eps_growth", "diluted_share_change"],
       "times": ["cash_conversion", "capex_to_depreciation"]}


def _fmt_kind(metric: str) -> str:
    for k, ms in FMT.items():
        if metric in ms:
            return k
    return "pct"


def build(run_json: Path, valuation_json: Path | None) -> str:
    run = json.loads(run_json.read_text())
    val = json.loads(valuation_json.read_text()) if valuation_json and valuation_json.exists() else None
    labels = run["run"]["config"]["fiscal_years"]
    data = {
        "company": run["company"], "digest": run["outputs_digest"], "created": run["run"]["created_at"],
        "commit": run["run"]["code_version"]["commit"], "labels": [f"FY{y}" for y in labels],
        "facts": {r["key"]: r for r in run["facts"]},
        "what_if": {r["key"]: r for r in run["what_if_facts"]},
        "groups": [{"title": t, "rows": [{"metric": m, "name": n, "fmt": _fmt_kind(m)} for m, n, _ in ROWS[g]]}
                   for t, g in GROUPS],
        "review": [i for i in run["review"] if i["severity"] != "info"],
        "adjustments": run["adjustments"], "observations": run["observations"],
        "recon": {}, "valuation": None,
    }
    for r in run["reconciliation"]:
        data["recon"][r["outcome"]] = data["recon"].get(r["outcome"], 0) + 1
    if val:
        scen = {k: v["value_per_share"] for k, v in val["scenarios"].items()}
        data["valuation"] = {
            "scenarios": scen,
            "prices": {k: v[val["config"]["headline_class"]] for k, v in val["prices"].items() if k != "risk_free"},
            "risk_free": val["prices"]["risk_free"], "wacc": val["wacc"], "grids": val["grids"],
            "reverse": val["reverse"], "assumptions": val["config"]["assumptions"], "evidence": val["evidence"],
            "valuation_date": val["valuation_date"], "problems": val["problems"],
            "tv_share": {k: v["terminal_share"] for k, v in val["scenarios"].items()},
        }
    from plotly.offline import get_plotlyjs  # the plotly.js pinned by uv.lock; the page works offline

    return (TEMPLATE.replace("/*DATA*/null", json.dumps(data, default=str).replace("</", "<\\/"))
            .replace("__TITLE__", f"{run['company']['legal_name']} research review")
            .replace("/*PLOTLYJS*/", get_plotlyjs()))


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__</title>
<script>/*PLOTLYJS*/</script>
<style>
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;
--axis:#c3c2b7;--ring:rgba(11,11,11,.10);--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--good:#006300;--crit:#d03b3b;--warn:#fab219;
--seq0:#cde2fb;--seq1:#2a78d6;--seq2:#0d366b;--mid:#f0efec}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;
--ink2:#c3c2b7;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--s1:#3987e5;--s2:#d95926;--s3:#199e70;--good:#0ca30c;
--seq0:#184f95;--seq1:#5598e7;--seq2:#cde2fb;--mid:#383835}}
:root[data-theme="dark"]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--grid:#2c2c2a;--axis:#383835;
--ring:rgba(255,255,255,.10);--s1:#3987e5;--s2:#d95926;--s3:#199e70;--good:#0ca30c;--seq0:#184f95;--seq1:#5598e7;--seq2:#cde2fb;--mid:#383835}
*{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:36px 0 4px}h3{font-size:14px;margin:0 0 8px}
.sub{color:var(--ink2);margin:0 0 12px}.muted{color:var(--muted)}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.chip{border:1px solid var(--ring);border-radius:999px;padding:3px 10px;background:var(--surface);font-size:12px;color:var(--ink2)}
.chip b{color:var(--ink)}.ok::before{content:"✓ ";color:var(--good)}.bad::before{content:"✕ ";color:var(--crit)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:16px 0}
.tile{background:var(--surface);border:1px solid var(--ring);border-radius:10px;padding:14px}
.tile .l{color:var(--ink2);font-size:12px}.tile .v{font-size:26px;font-weight:600;margin:4px 0}.tile .d{font-size:12px;color:var(--ink2)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:16px}
@media (max-width:520px){.grid2{grid-template-columns:1fr}}
.card{background:var(--surface);border:1px solid var(--ring);border-radius:10px;padding:14px;min-width:0}
.card p{margin:0 0 6px;color:var(--ink2);font-size:13px}.plot{width:100%;height:300px}
.tablewrap{overflow-x:auto;border:1px solid var(--ring);border-radius:10px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:6px 10px;border-bottom:1px solid var(--grid);text-align:right;white-space:nowrap}
th:first-child,td:first-child{text-align:left}thead th{color:var(--ink2);font-weight:600;position:sticky;top:0;background:var(--surface)}
tr.grp td{font-weight:600;color:var(--ink2);background:var(--page)}td.v{cursor:pointer;font-variant-numeric:tabular-nums}
td.v:hover,td.v:focus{outline:2px solid var(--s1);outline-offset:-2px}td.v.sel{background:color-mix(in srgb,var(--s1) 12%,transparent)}
.st{font-size:10px;color:var(--muted);margin-left:3px}
#panel{position:sticky;top:12px;background:var(--surface);border:1px solid var(--ring);border-radius:10px;padding:14px;font-size:13px}
#panel dt{color:var(--ink2);font-size:12px;margin-top:8px}#panel dd{margin:2px 0 0;word-break:break-word}
.layout{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:16px}@media (max-width:900px){.layout{grid-template-columns:1fr}}
a{color:var(--s1)}ul.q{padding-left:18px}ul.q li{margin:4px 0}.sev{font-size:11px;font-weight:600;text-transform:uppercase}
.toggle{display:inline-flex;gap:4px;border:1px solid var(--ring);border-radius:8px;padding:2px;background:var(--surface)}
.toggle button{border:0;background:none;color:var(--ink2);padding:4px 10px;border-radius:6px;cursor:pointer;font:inherit}
.toggle button[aria-pressed="true"]{background:var(--page);color:var(--ink);font-weight:600}
.warnbox{border-left:3px solid var(--warn);padding:8px 12px;background:var(--surface);border-radius:6px;color:var(--ink2);margin:8px 0}
</style></head><body><main>
<h1 id="title"></h1><p class="sub" id="meta"></p>
<div class="chips" id="chips"></div>
<div class="tiles" id="tiles"></div>

<h2>What the filings show</h2><p class="sub">Annual figures from 10-Ks; H1 figures from 10-Qs. Hover any mark for values.</p>
<div class="grid2">
 <div class="card"><h3>Revenue</h3><p>Fiscal years, USD bn.</p><div class="plot" id="c_rev"></div></div>
 <div class="card"><h3>Operating and cash FCF margins</h3><p>Share of revenue.</p><div class="plot" id="c_margin"></div></div>
 <div class="card"><h3>Capex outran depreciation; cash FCF stalled</h3><p>USD bn. Cash FCF = operating cash flow − capex.</p><div class="plot" id="c_capex"></div></div>
 <div class="card"><h3>What pretax income is made of</h3><p>USD bn. Equity-securities gains are mark-to-market, mostly unrealized.</p><div class="plot" id="c_pretax"></div></div>
</div>

<h2>Fundamentals with provenance</h2>
<p class="sub">Click a figure to see its source, formula and reconciliation. <span class="toggle" role="group" aria-label="view"><button id="t_rep" aria-pressed="true">Reported</button><button id="t_wi" aria-pressed="false">All proposed adjustments</button></span></p>
<div class="layout"><div class="tablewrap"><table id="facts"></table></div>
<aside id="panel" aria-live="polite"><h3>Provenance</h3><p class="muted">Select a figure.</p></aside></div>

<h2>Accounting review ledger</h2><p class="sub">Proposed by the engine, quoted from filings; nothing applies until a teammate approves it.</p>
<div class="tablewrap"><table id="ledger"></table></div><ul class="q" id="obs"></ul>

<div id="valsec"></div>

<h2>Review queue</h2><ul class="q" id="queue"></ul>
<p class="muted" id="foot"></p>
</main>
<script>
const D=/*DATA*/null;
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const bn=v=>v==null?"—":(Math.abs(v)>=1e9?(v<0?"-":"")+"$"+(Math.abs(v)/1e9).toLocaleString(undefined,{maximumFractionDigits:1,minimumFractionDigits:1})+"bn":(v<0?"-":"")+"$"+(Math.abs(v)/1e6).toLocaleString(undefined,{maximumFractionDigits:0})+"m");
const F={money:bn,pct:v=>v==null?"—":(v*100).toFixed(1)+"%",signed:v=>v==null?"—":(v>=0?"+":"")+(v*100).toFixed(1)+"%",
 times:v=>v==null?"—":v.toFixed(2)+"x",ps:v=>v==null?"—":"$"+v.toFixed(2),shares:v=>v==null?"—":(v/1e6).toLocaleString(undefined,{maximumFractionDigits:0})+"m"};
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const val=(m,l,src)=>{const f=(src||D.facts)[m+"@"+l]||D.facts[m+"@"+l];return f?f.value:null};
const L=D.labels;

document.getElementById("title").textContent=D.company.legal_name+" ("+D.company.tickers[0]+")";
document.getElementById("meta").textContent=`${L[0]}–${L[L.length-1]} · run ${D.digest.slice(0,12)} · code ${(D.commit||"").slice(0,8)} · built ${D.created}`;
const rc=D.recon, chips=[["matched on filed statements",(rc.matched||0)+(rc["matched-negated"]||0),1],["matched in note tables",rc["matched-in-notes"]||0,1],
 ["unverified (notes, by hand)",rc["from-notes"]||0,0],["mismatches",(rc.mismatch||0)+(rc.ambiguous||0),(rc.mismatch||0)+(rc.ambiguous||0)===0],
 ["blocking review items",D.review.filter(i=>i.severity==="block").length,D.review.filter(i=>i.severity==="block").length===0]];
document.getElementById("chips").innerHTML=chips.map(([t,n,ok])=>`<span class="chip ${ok?"ok":"bad"}"><b>${n}</b> ${t}</span>`).join("");

// tiles from the valuation evidence (10-Q) when present
const tiles=[];const last=L[L.length-1];
tiles.push(["Revenue "+last,bn(val("revenue",last)),"growth "+F.signed(val("revenue_growth",last))]);
if(D.valuation){const e=D.valuation.evidence,r=e.ratios,row=e.rows;
 tiles.push(["Capex, YTD "+e.period_end,bn(row.capex.ytd),"vs "+bn(row.capex.ytd_prior)+" a year earlier"]);
 tiles.push(["Cash FCF, YTD "+e.period_end,bn(r.cash_fcf_ytd),"vs "+bn(r.cash_fcf_ytd_prior)+" a year earlier"]);
 tiles.push(["Equity-securities gains / YTD net income",F.pct(r.equity_gains_share_of_net_income_ytd),bn(row.equity_securities_gain.ytd)+" of "+bn(row.net_income.ytd)]);}
document.getElementById("tiles").innerHTML=tiles.map(([l,v,d])=>`<div class="tile"><div class="l">${esc(l)}</div><div class="v">${esc(v)}</div><div class="d">${esc(d)}</div></div>`).join("");

function layout(extra){return Object.assign({margin:{l:48,r:12,t:8,b:32},paper_bgcolor:"rgba(0,0,0,0)",plot_bgcolor:"rgba(0,0,0,0)",
 font:{family:"system-ui,-apple-system,Segoe UI,sans-serif",size:12,color:css("--ink2")},showlegend:true,legend:{orientation:"h",y:-0.18},
 xaxis:{gridcolor:css("--grid"),linecolor:css("--axis"),zeroline:false},yaxis:{gridcolor:css("--grid"),linecolor:css("--axis"),zerolinecolor:css("--axis")},
 hoverlabel:{bgcolor:css("--surface"),bordercolor:css("--axis"),font:{color:css("--ink")}},bargap:0.55,bargroupgap:0.12},extra||{})}
const cfg={displayModeBar:false,responsive:true};
const B=v=>v==null?null:v/1e9;
function charts(){
 Plotly.react("c_rev",[{type:"bar",x:L,y:L.map(l=>B(val("revenue",l))),marker:{color:css("--s1")},name:"Revenue",
   hovertemplate:"%{x}: $%{y:.1f}bn<extra></extra>",text:L.map((l,i)=>i===L.length-1?bn(val("revenue",l)):""),textposition:"outside",textfont:{color:css("--ink2")}}],
   layout({showlegend:false,yaxis:{title:{text:"USD bn"},gridcolor:css("--grid"),rangemode:"tozero"}}),cfg);
 const line=(m,n,c)=>({type:"scatter",mode:"lines+markers",x:L,y:L.map(l=>val(m,l)),name:n,line:{color:css(c),width:2},marker:{size:8,color:css(c),line:{color:css("--surface"),width:2}},hovertemplate:n+" %{x}: %{y:.1%}<extra></extra>"});
 Plotly.react("c_margin",[line("operating_margin","Operating margin","--s1"),line("fcf_margin","Cash FCF margin","--s2")],layout({yaxis:{tickformat:".0%",gridcolor:css("--grid"),rangemode:"tozero"}}),cfg);
 const bar=(m,n,c)=>({type:"bar",x:L,y:L.map(l=>B(val(m,l))),name:n,marker:{color:css(c)},hovertemplate:n+" %{x}: $%{y:.1f}bn<extra></extra>"});
 Plotly.react("c_capex",[bar("capex","Capex","--s1"),bar("dna","Depreciation","--s2"),bar("fcf","Cash FCF","--s3")],layout({barmode:"group",yaxis:{title:{text:"USD bn"},gridcolor:css("--grid")}}),cfg);
 const other=L.map(l=>{const n=val("nonoperating_income",l),g=val("equity_securities_gain",l);return n==null||g==null?null:B(n-g)});
 Plotly.react("c_pretax",[bar("operating_income","Operating income","--s1"),bar("equity_securities_gain","Equity-securities gains","--s2"),
   {type:"bar",x:L,y:other,name:"Other non-operating",marker:{color:css("--s3")},hovertemplate:"Other non-operating %{x}: $%{y:.1f}bn<extra></extra>"}],
   layout({barmode:"relative",yaxis:{title:{text:"USD bn"},gridcolor:css("--grid")}}),cfg);
 if(D.valuation) valCharts();
}

// fundamentals table
let mode="rep";
function table(){
 const src=mode==="wi"?D.what_if:null;
 let h="<thead><tr><th>Metric</th>"+L.map(l=>`<th>${l}</th>`).join("")+"</tr></thead><tbody>";
 for(const g of D.groups){h+=`<tr class="grp"><td colspan="${L.length+1}">${esc(g.title)}</td></tr>`;
  for(const r of g.rows){h+=`<tr><td>${esc(r.name)}</td>`+L.map(l=>{const k=r.metric+"@"+l;const f=(src&&src[k])||D.facts[k];if(!f)return"<td>—</td>";
   const na=f.status==="missing"&&f.formula;const tag=f.status==="reported"||f.status==="derived"?"":`<span class="st">${f.status==="analyst-adjusted"?"adj":na?"n/a":f.status}</span>`;
   return `<td class="v" tabindex="0" data-k="${k}">${F[r.fmt](f.value)}${tag}</td>`}).join("")+"</tr>"}}
 document.getElementById("facts").innerHTML=h+"</tbody>";
}
function show(k){const f=(mode==="wi"&&D.what_if[k])||D.facts[k];if(!f)return;
 document.querySelectorAll("td.v.sel").forEach(e=>e.classList.remove("sel"));document.querySelector(`td.v[data-k="${k}"]`)?.classList.add("sel");
 const row=(t,v)=>v?`<dt>${t}</dt><dd>${v}</dd>`:"";
 const inputs=(f.inputs||"").split(";").filter(Boolean).map(i=>`<a href="#" data-k="${esc(i)}">${esc(i)}</a>`).join(", ");
 document.getElementById("panel").innerHTML=`<h3>${esc(f.metric)} · ${esc(f.fiscal_label)}</h3><dl>`+
  row("Value",esc(String(f.value))+" "+esc(f.unit))+row("Status",esc(f.status))+row("Formula",esc(f.formula))+row("Inputs",inputs)+
  row("Filing",f.accession?`<a href="${esc(f.source_url)}" target="_blank" rel="noopener">${esc(f.accession)}</a> · ${esc(f.locator)}`:"")+
  row("Statement line",f.statement_line?`<a href="${esc(f.statement_url)}" target="_blank" rel="noopener">${esc(f.statement_line)}</a> · ${esc((f.statement||"").split(" - ")[0])}`:"")+
  row("Reconciliation",esc(f.reconciliation))+row("Period",esc((f.period_start||"")+" → "+f.period_end))+
  row("Restated from",esc(f.restated_from))+row("Notes",esc(f.notes))+`</dl><p class="muted">snapshot ${esc(f.snapshot_id)}</p>`;
 document.querySelectorAll("#panel a[data-k]").forEach(a=>a.onclick=e=>{e.preventDefault();show(a.dataset.k)});}
document.getElementById("facts").addEventListener("click",e=>{const td=e.target.closest("td.v");if(td)show(td.dataset.k)});
document.getElementById("facts").addEventListener("keydown",e=>{const td=e.target.closest("td.v");if(td&&(e.key==="Enter"||e.key===" ")){e.preventDefault();show(td.dataset.k)}});
for(const [id,m] of [["t_rep","rep"],["t_wi","wi"]])document.getElementById(id).onclick=()=>{mode=m;
 document.getElementById("t_rep").setAttribute("aria-pressed",m==="rep");document.getElementById("t_wi").setAttribute("aria-pressed",m==="wi");table()};

// ledger + observations + queue
document.getElementById("ledger").innerHTML="<thead><tr><th>ID</th><th>Year</th><th>Metric</th><th>Original</th><th>Adjustment</th><th>Result</th><th>Status</th></tr></thead><tbody>"+
 D.adjustments.map(a=>`<tr><td title="${esc(a.rationale)}">${esc(a.id)}</td><td>${a.fiscal_label}</td><td>${a.metric}</td><td>${bn(a.original)}</td><td>${bn(a.delta)}</td><td>${bn(a.resulting)}</td><td>${a.status}</td></tr>`).join("")+"</tbody>";
document.getElementById("obs").innerHTML=D.observations.map(o=>`<li><b>${esc(o.id)}</b> — ${esc(o.note)} <span class="muted">“${esc(o.quote)}”</span></li>`).join("");
document.getElementById("queue").innerHTML=D.review.length?D.review.map(i=>`<li><span class="sev" style="color:${i.severity==="block"?"var(--crit)":"var(--ink2)"}">${i.severity==="block"?"✕ block":"! warn"}</span> ${esc(i.message)}</li>`).join(""):"<li>Nothing open.</li>";
document.getElementById("foot").textContent="Generated by the Fundamentals Research Engine from pinned SEC snapshots. No figure on this page is typed by hand.";

// valuation
function valSection(){const V=D.valuation;if(!V)return;const p=V.prices, a=V.assumptions;
 const rv=[];for(const [lab,d] of Object.entries(V.reverse))for(const [v,s] of Object.entries(d))rv.push(`<tr><td>$${p[lab].close.toFixed(2)} (${p[lab].date})</td><td>${v}</td><td>${s.roots.length?s.roots.map(x=>(x*100).toFixed(2)+"%").join(", "):"no solution in bounds"}</td><td>${(s.lo*100).toFixed(1)}% … ${(s.hi*100).toFixed(1)}%</td></tr>`);
 const asum=Object.entries(a).map(([k,x])=>`<tr><td>${esc(k)}</td><td>${Array.isArray(x.value)?x.value.map(v=>(v*100).toFixed(1)+"%").join(", "):esc(x.value)}</td><td>${esc(x.status)}</td><td style="text-align:left;white-space:normal">${esc(x.rationale)}</td></tr>`).join("");
 document.getElementById("valsec").innerHTML=`<h2>Valuation (FCFF DCF)</h2><div class="warnbox">Every judgment input is <b>proposed and unapproved</b>; equity risk premium and beta are placeholders without a source. These results show what the inputs imply — not a price target.</div>
 <div class="grid2"><div class="card"><h3>Value per share by scenario vs market price</h3><p>WACC ${(V.wacc.wacc*100).toFixed(2)}% · valuation date ${V.valuation_date} (price that day $${p.valuation_date.close.toFixed(2)})</p><div class="plot" id="c_val"></div></div>
 <div class="card"><h3>Value per share: growth × operating margin</h3><p>Every forecast year set to the column growth; margin applies to forecast and terminal years. The line marks combinations worth the latest price ($${p.latest.close.toFixed(2)}).</p><div class="plot" id="c_heat"></div></div></div>
 <h3 style="margin-top:16px">Reverse DCF — assumptions consistent with price under this model</h3><div class="tablewrap"><table><thead><tr><th>Price</th><th>Solve for</th><th>Result</th><th>Bounds</th></tr></thead><tbody>${rv.join("")}</tbody></table></div>
 <h3 style="margin-top:16px">Assumptions</h3><div class="tablewrap"><table><thead><tr><th>Assumption</th><th>Value</th><th>Status</th><th style="text-align:left">Rationale</th></tr></thead><tbody>${asum}</tbody></table></div>`;}
function valCharts(){const V=D.valuation;const names=Object.keys(V.scenarios);
 const px=Object.entries(V.prices);
 const lq=V.prices.latest;const shapes=[{type:"line",xref:"paper",x0:0,x1:1,y0:lq.close,y1:lq.close,line:{color:css("--ink2"),width:1}}];
 const ann=[{xref:"paper",x:1,y:lq.close,xanchor:"right",yanchor:"bottom",text:`market price ${lq.date}: $${lq.close.toFixed(2)}`,showarrow:false,font:{color:css("--ink2"),size:11}}];
 const top=Math.max(...px.map(([k,q])=>q.close),...names.map(n=>V.scenarios[n]))*1.15;
 Plotly.react("c_val",[{type:"scatter",mode:"markers+text",x:names,y:names.map(n=>V.scenarios[n]),marker:{size:12,color:css("--s1"),line:{color:css("--surface"),width:2}},
  text:names.map(n=>"$"+V.scenarios[n].toFixed(0)),textposition:"middle right",textfont:{color:css("--ink2")},name:"Model value",
  customdata:names.map(n=>(V.tv_share[n]*100).toFixed(0)),hovertemplate:"%{x}: $%{y:.2f}/share<br>terminal value %{customdata}% of EV<extra></extra>"}],
  layout({showlegend:false,shapes,annotations:ann,xaxis:{range:[-0.5,names.length-0.1],gridcolor:"rgba(0,0,0,0)"},yaxis:{title:{text:"USD per share"},gridcolor:css("--grid"),range:[0,top]}}),cfg);
 const g=V.grids.growth_x_margin;const price=px[px.length-1][1].close;
 Plotly.react("c_heat",[{type:"heatmap",x:g.xs,y:g.ys,z:g.values,
  colorscale:[[0,css("--seq0")],[0.5,css("--seq1")],[1,css("--seq2")]],xgap:2,ygap:2,colorbar:{title:{text:"$/share"},outlinewidth:0,tickfont:{color:css("--ink2")}},
  hovertemplate:"growth %{x:.0%}, margin %{y:.0%}: $%{z:.0f}/share<extra></extra>"},
  {type:"contour",x:g.xs,y:g.ys,z:g.values,showscale:false,contours:{start:price,end:price,size:1,coloring:"none",showlabels:true,labelformat:"$.0f",labelfont:{color:css("--ink")}},
  line:{color:css("--ink"),width:2},hoverinfo:"skip",name:"latest price"}],
  layout({showlegend:false,margin:{l:56,r:12,t:8,b:44},xaxis:{title:{text:"revenue growth, every forecast year"},tickformat:".0%",gridcolor:"rgba(0,0,0,0)"},yaxis:{title:{text:"operating margin"},tickformat:".0%",gridcolor:"rgba(0,0,0,0)"}}),cfg);}

valSection();table();charts();
matchMedia("(prefers-color-scheme: dark)").addEventListener("change",charts);
new MutationObserver(charts).observe(document.documentElement,{attributes:true,attributeFilter:["data-theme"]});
</script></body></html>
"""


def write(run_json: Path, valuation_json: Path | None, out: Path) -> Path:
    out.write_text(build(run_json, valuation_json))
    return out
