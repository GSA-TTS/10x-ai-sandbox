import{p as M,d as _,s as R}from"./styles-b83b31c9.a7990815.js";import{l as d,c,h as w,A as B,v as G,q as D,u as E,p as A,j as C}from"./Messages.6031e370.js";import{G as q}from"./graph.2e4574cc.js";import{r as z}from"./index-01f381cb.8ceb087d.js";import"./dayjs.min.75d9117a.js";import"./layout.b6dc4c0d.js";const S=s=>C.sanitizeText(s,c());let k={dividerMargin:10,padding:5,textHeight:10,curve:void 0};const P=function(s,t,y,a){const e=Object.keys(s);d.info("keys:",e),d.info(s),e.forEach(function(i){var o,r;const l=s[i],p={shape:"rect",id:l.id,domId:l.domId,labelText:S(l.id),labelStyle:"",style:"fill: none; stroke: black",padding:((o=c().flowchart)==null?void 0:o.padding)??((r=c().class)==null?void 0:r.padding)};t.setNode(l.id,p),$(l.classes,t,y,a,l.id),d.info("setNode",p)})},$=function(s,t,y,a,e){const i=Object.keys(s);d.info("keys:",i),d.info(s),i.filter(o=>s[o].parent==e).forEach(function(o){var r,l;const n=s[o],p=n.cssClasses.join(" "),f=D(n.styles),v=n.label??n.id,b=0,h="class_box",u={labelStyle:f.labelStyle,shape:h,labelText:S(v),classData:n,rx:b,ry:b,class:p,style:f.style,id:n.id,domId:n.domId,tooltip:a.db.getTooltip(n.id,e)||"",haveCallback:n.haveCallback,link:n.link,width:n.type==="group"?500:void 0,type:n.type,padding:((r=c().flowchart)==null?void 0:r.padding)??((l=c().class)==null?void 0:l.padding)};t.setNode(n.id,u),e&&t.setParent(n.id,e),d.info("setNode",u)})},F=function(s,t,y,a){d.info(s),s.forEach(function(e,i){var o,r;const l=e,n="",p={labelStyle:"",style:""},f=l.text,v=0,b="note",h={labelStyle:p.labelStyle,shape:b,labelText:S(f),noteData:l,rx:v,ry:v,class:n,style:p.style,id:l.id,domId:l.id,tooltip:"",type:"note",padding:((o=c().flowchart)==null?void 0:o.padding)??((r=c().class)==null?void 0:r.padding)};if(t.setNode(l.id,h),d.info("setNode",h),!l.class||!(l.class in a))return;const u=y+i,x={id:`edgeNote${u}`,classes:"relation",pattern:"dotted",arrowhead:"none",startLabelRight:"",endLabelLeft:"",arrowTypeStart:"none",arrowTypeEnd:"none",style:"fill:none",labelStyle:"",curve:E(k.curve,A)};t.setEdge(l.id,l.class,x,u)})},H=function(s,t){const y=c().flowchart;let a=0;s.forEach(function(e){var i;a++;const o={classes:"relation",pattern:e.relation.lineType==1?"dashed":"solid",id:`id_${e.id1}_${e.id2}_${a}`,arrowhead:e.type==="arrow_open"?"none":"normal",startLabelRight:e.relationTitle1==="none"?"":e.relationTitle1,endLabelLeft:e.relationTitle2==="none"?"":e.relationTitle2,arrowTypeStart:N(e.relation.type1),arrowTypeEnd:N(e.relation.type2),style:"fill:none",labelStyle:"",curve:E(y==null?void 0:y.curve,A)};if(d.info(o,e),e.style!==void 0){const r=D(e.style);o.style=r.style,o.labelStyle=r.labelStyle}e.text=e.title,e.text===void 0?e.style!==void 0&&(o.arrowheadStyle="fill: #333"):(o.arrowheadStyle="fill: #333",o.labelpos="c",((i=c().flowchart)==null?void 0:i.htmlLabels)??c().htmlLabels?(o.labelType="html",o.label='<span class="edgeLabel">'+e.text+"</span>"):(o.labelType="text",o.label=e.text.replace(C.lineBreakRegex,`
`),e.style===void 0&&(o.style=o.style||"stroke: #333; stroke-width: 1.5px;fill:none"),o.labelStyle=o.labelStyle.replace("color:","fill:"))),t.setEdge(e.id1,e.id2,o,a)})},V=function(s){k={...k,...s}},W=async function(s,t,y,a){d.info("Drawing class - ",t);const e=c().flowchart??c().class,i=c().securityLevel;d.info("config:",e);const o=(e==null?void 0:e.nodeSpacing)??50,r=(e==null?void 0:e.rankSpacing)??50,l=new q({multigraph:!0,compound:!0}).setGraph({rankdir:a.db.getDirection(),nodesep:o,ranksep:r,marginx:8,marginy:8}).setDefaultEdgeLabel(function(){return{}}),n=a.db.getNamespaces(),p=a.db.getClasses(),f=a.db.getRelations(),v=a.db.getNotes();d.info(f),P(n,l,t,a),$(p,l,t,a),H(f,l),F(v,l,f.length+1,p);let b;i==="sandbox"&&(b=w("#i"+t));const h=i==="sandbox"?w(b.nodes()[0].contentDocument.body):w("body"),u=h.select(`[id="${t}"]`),x=h.select("#"+t+" g");if(await z(x,l,["aggregation","extension","composition","dependency","lollipop"],"classDiagram",t),B.insertTitle(u,"classTitleText",(e==null?void 0:e.titleTopMargin)??5,a.db.getDiagramTitle()),G(l,u,e==null?void 0:e.diagramPadding,e==null?void 0:e.useMaxWidth),!(e!=null&&e.htmlLabels)){const T=i==="sandbox"?b.nodes()[0].contentDocument:document,I=T.querySelectorAll('[id="'+t+'"] .edgeLabel .label');for(const g of I){const L=g.getBBox(),m=T.createElementNS("http://www.w3.org/2000/svg","rect");m.setAttribute("rx",0),m.setAttribute("ry",0),m.setAttribute("width",L.width),m.setAttribute("height",L.height),g.insertBefore(m,g.firstChild)}}};function N(s){let t;switch(s){case 0:t="aggregation";break;case 1:t="extension";break;case 2:t="composition";break;case 3:t="dependency";break;case 4:t="lollipop";break;default:t="none"}return t}const J={setConf:V,draw:W},j={parser:M,db:_,renderer:J,styles:R,init:s=>{s.class||(s.class={}),s.class.arrowMarkerAbsolute=s.arrowMarkerAbsolute,_.clear()}};export{j as diagram};
//# sourceMappingURL=classDiagram-v2-a2b738ad.fd0d5f39.js.map