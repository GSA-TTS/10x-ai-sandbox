import{s as Ve,p as ur,X as vr,Q as Tt,A as Lt,f,l as k,a as p,g as u,h as m,m as $,d as c,c as x,S as H,j as i,i as I,w as a,y as hr,n as V,u as dt,v as ct,r as $e,F as pr,G as xr,H as gr,I as _r}from"../chunks/scheduler.2ec89978.js";import{S as De,i as He,f as mr,b as z,d as T,m as L,a as j,t as E,e as S}from"../chunks/index.276f3600.js";import{C as br}from"../chunks/Chat.e6648ef0.js";import{M as wr}from"../chunks/dayjs.min.75d9117a.js";import{T as yr}from"../chunks/Tooltip.3c52e2f2.js";import"../chunks/updater.c075227d.js";import{D as kr,M as fr}from"../chunks/Dropdown.9f1b9537.js";import{M as $r}from"../chunks/menu-trigger.1d870800.js";import{f as Vr}from"../chunks/index.e8e699b3.js";function Dr(n){let e,l,t,s=n[1].t("Keyboard shortcuts")+"",r,o,d,v='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"></path></svg>',D,y,C,w,h,_,Z=n[1].t("Open new chat")+"",J,ft,R,St='<div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Ctrl/⌘</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Shift</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">O</div>',ut,B,de,Ie=n[1].t("Focus chat input")+"",Be,vt,Y,Zt='<div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Shift</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Esc</div>',ht,W,ce,je=n[1].t("Copy last code block")+"",We,mt,ee,Nt='<div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Ctrl/⌘</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Shift</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">;</div>',pt,O,fe,Ee=n[1].t("Copy last response")+"",Oe,xt,te,Bt='<div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Ctrl/⌘</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Shift</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">C</div>',gt,M,A,ue,Ce=n[1].t("Toggle settings")+"",Ae,_t,re,Wt='<div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Ctrl/⌘</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">.</div>',bt,K,ve,Me=n[1].t("Toggle sidebar")+"",Ke,wt,se,Ot='<div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Ctrl/⌘</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Shift</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">S</div>',yt,q,he,ze=n[1].t("Delete chat")+"",qe,kt,le,At='<div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Ctrl/⌘</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Shift</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">⌫</div>',$t,F,me,Te=n[1].t("Show shortcuts")+"",Fe,Vt,ae,Kt='<div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">Ctrl/⌘</div> <div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">/</div>',Dt,pe,xe,Le=n[1].t("Input commands")+"",Ue,Ht,ge,_e,N,U,be,Se=n[1].t("Attach file")+"",Qe,It,ie,qt='<div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">#</div>',jt,Q,we,Ze=n[1].t("Add custom prompt")+"",Ge,Et,ne,Ft='<div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">/</div>',Ct,G,ye,Ne=n[1].t("Select model")+"",Pe,Mt,oe,Ut='<div class="h-fit py-1 px-2 flex items-center justify-center rounded border border-black/10 capitalize text-gray-600 dark:border-white/10 dark:text-gray-300">@</div>',zt,Qt;return{c(){e=f("div"),l=f("div"),t=f("div"),r=k(s),o=p(),d=f("button"),d.innerHTML=v,D=p(),y=f("div"),C=f("div"),w=f("div"),h=f("div"),_=f("div"),J=k(Z),ft=p(),R=f("div"),R.innerHTML=St,ut=p(),B=f("div"),de=f("div"),Be=k(Ie),vt=p(),Y=f("div"),Y.innerHTML=Zt,ht=p(),W=f("div"),ce=f("div"),We=k(je),mt=p(),ee=f("div"),ee.innerHTML=Nt,pt=p(),O=f("div"),fe=f("div"),Oe=k(Ee),xt=p(),te=f("div"),te.innerHTML=Bt,gt=p(),M=f("div"),A=f("div"),ue=f("div"),Ae=k(Ce),_t=p(),re=f("div"),re.innerHTML=Wt,bt=p(),K=f("div"),ve=f("div"),Ke=k(Me),wt=p(),se=f("div"),se.innerHTML=Ot,yt=p(),q=f("div"),he=f("div"),qe=k(ze),kt=p(),le=f("div"),le.innerHTML=At,$t=p(),F=f("div"),me=f("div"),Fe=k(Te),Vt=p(),ae=f("div"),ae.innerHTML=Kt,Dt=p(),pe=f("div"),xe=f("div"),Ue=k(Le),Ht=p(),ge=f("div"),_e=f("div"),N=f("div"),U=f("div"),be=f("div"),Qe=k(Se),It=p(),ie=f("div"),ie.innerHTML=qt,jt=p(),Q=f("div"),we=f("div"),Ge=k(Ze),Et=p(),ne=f("div"),ne.innerHTML=Ft,Ct=p(),G=f("div"),ye=f("div"),Pe=k(Ne),Mt=p(),oe=f("div"),oe.innerHTML=Ut,this.h()},l(b){e=u(b,"DIV",{class:!0});var g=m(e);l=u(g,"DIV",{class:!0});var Xe=m(l);t=u(Xe,"DIV",{class:!0});var Gt=m(t);r=$(Gt,s),Gt.forEach(c),o=x(Xe),d=u(Xe,"BUTTON",{class:!0,"data-svelte-h":!0}),H(d)!=="svelte-745w2y"&&(d.innerHTML=v),Xe.forEach(c),D=x(g),y=u(g,"DIV",{class:!0});var Pt=m(y);C=u(Pt,"DIV",{class:!0});var Je=m(C);w=u(Je,"DIV",{class:!0});var P=m(w);h=u(P,"DIV",{class:!0});var Re=m(h);_=u(Re,"DIV",{class:!0});var Xt=m(_);J=$(Xt,Z),Xt.forEach(c),ft=x(Re),R=u(Re,"DIV",{class:!0,"data-svelte-h":!0}),H(R)!=="svelte-lcmjz9"&&(R.innerHTML=St),Re.forEach(c),ut=x(P),B=u(P,"DIV",{class:!0});var Ye=m(B);de=u(Ye,"DIV",{class:!0});var Jt=m(de);Be=$(Jt,Ie),Jt.forEach(c),vt=x(Ye),Y=u(Ye,"DIV",{class:!0,"data-svelte-h":!0}),H(Y)!=="svelte-1c7wvdz"&&(Y.innerHTML=Zt),Ye.forEach(c),ht=x(P),W=u(P,"DIV",{class:!0});var et=m(W);ce=u(et,"DIV",{class:!0});var Rt=m(ce);We=$(Rt,je),Rt.forEach(c),mt=x(et),ee=u(et,"DIV",{class:!0,"data-svelte-h":!0}),H(ee)!=="svelte-1vgtrzt"&&(ee.innerHTML=Nt),et.forEach(c),pt=x(P),O=u(P,"DIV",{class:!0});var tt=m(O);fe=u(tt,"DIV",{class:!0});var Yt=m(fe);Oe=$(Yt,Ee),Yt.forEach(c),xt=x(tt),te=u(tt,"DIV",{class:!0,"data-svelte-h":!0}),H(te)!=="svelte-m149u9"&&(te.innerHTML=Bt),tt.forEach(c),P.forEach(c),gt=x(Je),M=u(Je,"DIV",{class:!0});var X=m(M);A=u(X,"DIV",{class:!0});var rt=m(A);ue=u(rt,"DIV",{class:!0});var er=m(ue);Ae=$(er,Ce),er.forEach(c),_t=x(rt),re=u(rt,"DIV",{class:!0,"data-svelte-h":!0}),H(re)!=="svelte-1lfzi34"&&(re.innerHTML=Wt),rt.forEach(c),bt=x(X),K=u(X,"DIV",{class:!0});var st=m(K);ve=u(st,"DIV",{class:!0});var tr=m(ve);Ke=$(tr,Me),tr.forEach(c),wt=x(st),se=u(st,"DIV",{class:!0,"data-svelte-h":!0}),H(se)!=="svelte-1egz3pd"&&(se.innerHTML=Ot),st.forEach(c),yt=x(X),q=u(X,"DIV",{class:!0});var lt=m(q);he=u(lt,"DIV",{class:!0});var rr=m(he);qe=$(rr,ze),rr.forEach(c),kt=x(lt),le=u(lt,"DIV",{class:!0,"data-svelte-h":!0}),H(le)!=="svelte-1b065vn"&&(le.innerHTML=At),lt.forEach(c),$t=x(X),F=u(X,"DIV",{class:!0});var at=m(F);me=u(at,"DIV",{class:!0});var sr=m(me);Fe=$(sr,Te),sr.forEach(c),Vt=x(at),ae=u(at,"DIV",{class:!0,"data-svelte-h":!0}),H(ae)!=="svelte-714lzr"&&(ae.innerHTML=Kt),at.forEach(c),X.forEach(c),Je.forEach(c),Pt.forEach(c),Dt=x(g),pe=u(g,"DIV",{class:!0});var lr=m(pe);xe=u(lr,"DIV",{class:!0});var ar=m(xe);Ue=$(ar,Le),ar.forEach(c),lr.forEach(c),Ht=x(g),ge=u(g,"DIV",{class:!0});var ir=m(ge);_e=u(ir,"DIV",{class:!0});var nr=m(_e);N=u(nr,"DIV",{class:!0});var ke=m(N);U=u(ke,"DIV",{class:!0});var it=m(U);be=u(it,"DIV",{class:!0});var or=m(be);Qe=$(or,Se),or.forEach(c),It=x(it),ie=u(it,"DIV",{class:!0,"data-svelte-h":!0}),H(ie)!=="svelte-11t0lmd"&&(ie.innerHTML=qt),it.forEach(c),jt=x(ke),Q=u(ke,"DIV",{class:!0});var nt=m(Q);we=u(nt,"DIV",{class:!0});var dr=m(we);Ge=$(dr,Ze),dr.forEach(c),Et=x(nt),ne=u(nt,"DIV",{class:!0,"data-svelte-h":!0}),H(ne)!=="svelte-1s9pky1"&&(ne.innerHTML=Ft),nt.forEach(c),Ct=x(ke),G=u(ke,"DIV",{class:!0});var ot=m(G);ye=u(ot,"DIV",{class:!0});var cr=m(ye);Pe=$(cr,Ne),cr.forEach(c),Mt=x(ot),oe=u(ot,"DIV",{class:!0,"data-svelte-h":!0}),H(oe)!=="svelte-oivy56"&&(oe.innerHTML=Ut),ot.forEach(c),ke.forEach(c),nr.forEach(c),ir.forEach(c),g.forEach(c),this.h()},h(){i(t,"class","text-lg font-medium self-center"),i(d,"class","self-center"),i(l,"class","flex justify-between dark:text-gray-300 px-5 pt-4"),i(_,"class","text-sm"),i(R,"class","flex space-x-1 text-xs"),i(h,"class","w-full flex justify-between items-center"),i(de,"class","text-sm"),i(Y,"class","flex space-x-1 text-xs"),i(B,"class","w-full flex justify-between items-center"),i(ce,"class","text-sm"),i(ee,"class","flex space-x-1 text-xs"),i(W,"class","w-full flex justify-between items-center"),i(fe,"class","text-sm"),i(te,"class","flex space-x-1 text-xs"),i(O,"class","w-full flex justify-between items-center"),i(w,"class","flex flex-col space-y-3 w-full self-start"),i(ue,"class","text-sm"),i(re,"class","flex space-x-1 text-xs"),i(A,"class","w-full flex justify-between items-center"),i(ve,"class","text-sm"),i(se,"class","flex space-x-1 text-xs"),i(K,"class","w-full flex justify-between items-center"),i(he,"class","text-sm"),i(le,"class","flex space-x-1 text-xs"),i(q,"class","w-full flex justify-between items-center"),i(me,"class","text-sm"),i(ae,"class","flex space-x-1 text-xs"),i(F,"class","w-full flex justify-between items-center"),i(M,"class","flex flex-col space-y-3 w-full self-start"),i(C,"class","flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6"),i(y,"class","flex flex-col md:flex-row w-full p-5 md:space-x-4 dark:text-gray-200"),i(xe,"class","text-lg font-medium self-center"),i(pe,"class","flex justify-between dark:text-gray-300 px-5"),i(be,"class","text-sm"),i(ie,"class","flex space-x-1 text-xs"),i(U,"class","w-full flex justify-between items-center"),i(we,"class","text-sm"),i(ne,"class","flex space-x-1 text-xs"),i(Q,"class","w-full flex justify-between items-center"),i(ye,"class","text-sm"),i(oe,"class","flex space-x-1 text-xs"),i(G,"class","w-full flex justify-between items-center"),i(N,"class","flex flex-col space-y-3 w-full self-start"),i(_e,"class","flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6"),i(ge,"class","flex flex-col md:flex-row w-full p-5 md:space-x-4 dark:text-gray-200"),i(e,"class","text-gray-700 dark:text-gray-100")},m(b,g){I(b,e,g),a(e,l),a(l,t),a(t,r),a(l,o),a(l,d),a(e,D),a(e,y),a(y,C),a(C,w),a(w,h),a(h,_),a(_,J),a(h,ft),a(h,R),a(w,ut),a(w,B),a(B,de),a(de,Be),a(B,vt),a(B,Y),a(w,ht),a(w,W),a(W,ce),a(ce,We),a(W,mt),a(W,ee),a(w,pt),a(w,O),a(O,fe),a(fe,Oe),a(O,xt),a(O,te),a(C,gt),a(C,M),a(M,A),a(A,ue),a(ue,Ae),a(A,_t),a(A,re),a(M,bt),a(M,K),a(K,ve),a(ve,Ke),a(K,wt),a(K,se),a(M,yt),a(M,q),a(q,he),a(he,qe),a(q,kt),a(q,le),a(M,$t),a(M,F),a(F,me),a(me,Fe),a(F,Vt),a(F,ae),a(e,Dt),a(e,pe),a(pe,xe),a(xe,Ue),a(e,Ht),a(e,ge),a(ge,_e),a(_e,N),a(N,U),a(U,be),a(be,Qe),a(U,It),a(U,ie),a(N,jt),a(N,Q),a(Q,we),a(we,Ge),a(Q,Et),a(Q,ne),a(N,Ct),a(N,G),a(G,ye),a(ye,Pe),a(G,Mt),a(G,oe),zt||(Qt=hr(d,"click",n[3]),zt=!0)},p(b,g){g&2&&s!==(s=b[1].t("Keyboard shortcuts")+"")&&V(r,s),g&2&&Z!==(Z=b[1].t("Open new chat")+"")&&V(J,Z),g&2&&Ie!==(Ie=b[1].t("Focus chat input")+"")&&V(Be,Ie),g&2&&je!==(je=b[1].t("Copy last code block")+"")&&V(We,je),g&2&&Ee!==(Ee=b[1].t("Copy last response")+"")&&V(Oe,Ee),g&2&&Ce!==(Ce=b[1].t("Toggle settings")+"")&&V(Ae,Ce),g&2&&Me!==(Me=b[1].t("Toggle sidebar")+"")&&V(Ke,Me),g&2&&ze!==(ze=b[1].t("Delete chat")+"")&&V(qe,ze),g&2&&Te!==(Te=b[1].t("Show shortcuts")+"")&&V(Fe,Te),g&2&&Le!==(Le=b[1].t("Input commands")+"")&&V(Ue,Le),g&2&&Se!==(Se=b[1].t("Attach file")+"")&&V(Qe,Se),g&2&&Ze!==(Ze=b[1].t("Add custom prompt")+"")&&V(Ge,Ze),g&2&&Ne!==(Ne=b[1].t("Select model")+"")&&V(Pe,Ne)},d(b){b&&c(e),zt=!1,Qt()}}}function Hr(n){let e,l,t;function s(o){n[4](o)}let r={$$slots:{default:[Dr]},$$scope:{ctx:n}};return n[0]!==void 0&&(r.show=n[0]),e=new wr({props:r}),ur.push(()=>mr(e,"show",s)),{c(){z(e.$$.fragment)},l(o){T(e.$$.fragment,o)},m(o,d){L(e,o,d),t=!0},p(o,[d]){const v={};d&35&&(v.$$scope={dirty:d,ctx:o}),!l&&d&1&&(l=!0,v.show=o[0],vr(()=>l=!1)),e.$set(v)},i(o){t||(j(e.$$.fragment,o),t=!0)},o(o){E(e.$$.fragment,o),t=!1},d(o){S(e,o)}}}function Ir(n,e,l){let t;const s=Tt("i18n");Lt(n,s,v=>l(1,t=v));let{show:r=!1}=e;const o=()=>{l(0,r=!1)};function d(v){r=v,l(0,r)}return n.$$set=v=>{"show"in v&&l(0,r=v.show)},[r,t,s,o,d]}class jr extends De{constructor(e){super(),He(this,e,Ir,Hr,Ve,{show:0})}}function Er(n){let e,l;return{c(){e=dt("svg"),l=dt("path"),this.h()},l(t){e=ct(t,"svg",{xmlns:!0,fill:!0,viewBox:!0,"stroke-width":!0,stroke:!0,class:!0});var s=m(e);l=ct(s,"path",{"stroke-linecap":!0,"stroke-linejoin":!0,d:!0}),m(l).forEach(c),s.forEach(c),this.h()},h(){i(l,"stroke-linecap","round"),i(l,"stroke-linejoin","round"),i(l,"d","M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 5.25h.008v.008H12v-.008Z"),i(e,"xmlns","http://www.w3.org/2000/svg"),i(e,"fill","none"),i(e,"viewBox","0 0 24 24"),i(e,"stroke-width",n[1]),i(e,"stroke","currentColor"),i(e,"class",n[0])},m(t,s){I(t,e,s),a(e,l)},p(t,[s]){s&2&&i(e,"stroke-width",t[1]),s&1&&i(e,"class",t[0])},i:$e,o:$e,d(t){t&&c(e)}}}function Cr(n,e,l){let{className:t="w-4 h-4"}=e,{strokeWidth:s="2"}=e;return n.$$set=r=>{"className"in r&&l(0,t=r.className),"strokeWidth"in r&&l(1,s=r.strokeWidth)},[t,s]}class Mr extends De{constructor(e){super(),He(this,e,Cr,Er,Ve,{className:0,strokeWidth:1})}}function zr(n){let e,l;return{c(){e=dt("svg"),l=dt("path"),this.h()},l(t){e=ct(t,"svg",{"aria-hidden":!0,xmlns:!0,fill:!0,viewBox:!0,"stroke-width":!0,class:!0});var s=m(e);l=ct(s,"path",{"fill-rule":!0,d:!0,"clip-rule":!0}),m(l).forEach(c),s.forEach(c),this.h()},h(){i(l,"fill-rule","evenodd"),i(l,"d","M2 7a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7Zm5.01 1H5v2.01h2.01V8Zm3 0H8v2.01h2.01V8Zm3 0H11v2.01h2.01V8Zm3 0H14v2.01h2.01V8Zm3 0H17v2.01h2.01V8Zm-12 3H5v2.01h2.01V11Zm3 0H8v2.01h2.01V11Zm3 0H11v2.01h2.01V11Zm3 0H14v2.01h2.01V11Zm3 0H17v2.01h2.01V11Zm-12 3H5v2.01h2.01V14ZM8 14l-.001 2 8.011.01V14H8Zm11.01 0H17v2.01h2.01V14Z"),i(l,"clip-rule","evenodd"),i(e,"aria-hidden","true"),i(e,"xmlns","http://www.w3.org/2000/svg"),i(e,"fill","currentColor"),i(e,"viewBox","0 0 24 24"),i(e,"stroke-width",n[1]),i(e,"class",n[0])},m(t,s){I(t,e,s),a(e,l)},p(t,[s]){s&2&&i(e,"stroke-width",t[1]),s&1&&i(e,"class",t[0])},i:$e,o:$e,d(t){t&&c(e)}}}function Tr(n,e,l){let{className:t="size-4"}=e,{strokeWidth:s="2"}=e;return n.$$set=r=>{"className"in r&&l(0,t=r.className),"strokeWidth"in r&&l(1,s=r.strokeWidth)},[t,s]}class Lr extends De{constructor(e){super(),He(this,e,Tr,zr,Ve,{className:0,strokeWidth:1})}}function Sr(n){let e;const l=n[5].default,t=pr(l,n,n[9],null);return{c(){t&&t.c()},l(s){t&&t.l(s)},m(s,r){t&&t.m(s,r),e=!0},p(s,r){t&&t.p&&(!e||r&512)&&xr(t,l,s,s[9],e?_r(l,s[9],r,null):gr(s[9]),null)},i(s){e||(j(t,s),e=!0)},o(s){E(t,s),e=!1},d(s){t&&t.d(s)}}}function Zr(n){let e,l,t,s=n[2].t("Documentation")+"",r,o;return e=new Mr({props:{className:"size-5"}}),{c(){z(e.$$.fragment),l=p(),t=f("div"),r=k(s),this.h()},l(d){T(e.$$.fragment,d),l=x(d),t=u(d,"DIV",{class:!0});var v=m(t);r=$(v,s),v.forEach(c),this.h()},h(){i(t,"class","flex items-center")},m(d,v){L(e,d,v),I(d,l,v),I(d,t,v),a(t,r),o=!0},p(d,v){(!o||v&4)&&s!==(s=d[2].t("Documentation")+"")&&V(r,s)},i(d){o||(j(e.$$.fragment,d),o=!0)},o(d){E(e.$$.fragment,d),o=!1},d(d){d&&(c(l),c(t)),S(e,d)}}}function Nr(n){let e,l,t,s=n[2].t("Keyboard shortcuts")+"",r,o;return e=new Lr({props:{className:"size-5"}}),{c(){z(e.$$.fragment),l=p(),t=f("div"),r=k(s),this.h()},l(d){T(e.$$.fragment,d),l=x(d),t=u(d,"DIV",{class:!0});var v=m(t);r=$(v,s),v.forEach(c),this.h()},h(){i(t,"class","flex items-center")},m(d,v){L(e,d,v),I(d,l,v),I(d,t,v),a(t,r),o=!0},p(d,v){(!o||v&4)&&s!==(s=d[2].t("Keyboard shortcuts")+"")&&V(r,s)},i(d){o||(j(e.$$.fragment,d),o=!0)},o(d){E(e.$$.fragment,d),o=!1},d(d){d&&(c(l),c(t)),S(e,d)}}}function Br(n){let e,l,t,s;return e=new fr({props:{class:"flex gap-2 items-center px-3 py-2 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md",id:"chat-share-button",$$slots:{default:[Zr]},$$scope:{ctx:n}}}),e.$on("click",n[6]),t=new fr({props:{class:"flex gap-2 items-center px-3 py-2 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md",id:"chat-share-button",$$slots:{default:[Nr]},$$scope:{ctx:n}}}),t.$on("click",n[7]),{c(){z(e.$$.fragment),l=p(),z(t.$$.fragment)},l(r){T(e.$$.fragment,r),l=x(r),T(t.$$.fragment,r)},m(r,o){L(e,r,o),I(r,l,o),L(t,r,o),s=!0},p(r,o){const d={};o&516&&(d.$$scope={dirty:o,ctx:r}),e.$set(d);const v={};o&516&&(v.$$scope={dirty:o,ctx:r}),t.$set(v)},i(r){s||(j(e.$$.fragment,r),j(t.$$.fragment,r),s=!0)},o(r){E(e.$$.fragment,r),E(t.$$.fragment,r),s=!1},d(r){r&&c(l),S(e,r),S(t,r)}}}function Wr(n){let e,l,t;return l=new $r({props:{class:"w-full max-w-[200px] rounded-xl px-1 py-1.5 border border-gray-300/30 dark:border-gray-700/50 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-lg",sideOffset:4,side:"top",align:"end",transition:Vr,$$slots:{default:[Br]},$$scope:{ctx:n}}}),{c(){e=f("div"),z(l.$$.fragment),this.h()},l(s){e=u(s,"DIV",{slot:!0});var r=m(e);T(l.$$.fragment,r),r.forEach(c),this.h()},h(){i(e,"slot","content")},m(s,r){I(s,e,r),L(l,e,null),t=!0},p(s,r){const o={};r&517&&(o.$$scope={dirty:r,ctx:s}),l.$set(o)},i(s){t||(j(l.$$.fragment,s),t=!0)},o(s){E(l.$$.fragment,s),t=!1},d(s){s&&c(e),S(l)}}}function Or(n){let e,l;return e=new kr({props:{$$slots:{content:[Wr],default:[Sr]},$$scope:{ctx:n}}}),e.$on("change",n[8]),{c(){z(e.$$.fragment)},l(t){T(e.$$.fragment,t)},m(t,s){L(e,t,s),l=!0},p(t,[s]){const r={};s&517&&(r.$$scope={dirty:s,ctx:t}),e.$set(r)},i(t){l||(j(e.$$.fragment,t),l=!0)},o(t){E(e.$$.fragment,t),l=!1},d(t){S(e,t)}}}function Ar(n,e,l){let t,{$$slots:s={},$$scope:r}=e;const o=Tt("i18n");Lt(n,o,h=>l(2,t=h));let{showDocsHandler:d}=e,{showShortcutsHandler:v}=e,{onClose:D=()=>{}}=e;const y=()=>{window.open("https://docs.openwebui.com","_blank")},C=()=>{v()},w=h=>{h.detail===!1&&D()};return n.$$set=h=>{"showDocsHandler"in h&&l(4,d=h.showDocsHandler),"showShortcutsHandler"in h&&l(0,v=h.showShortcutsHandler),"onClose"in h&&l(1,D=h.onClose),"$$scope"in h&&l(9,r=h.$$scope)},[v,D,t,o,d,s,y,C,w,r]}class Kr extends De{constructor(e){super(),He(this,e,Ar,Or,Ve,{showDocsHandler:4,showShortcutsHandler:0,onClose:1})}}function qr(n){let e,l="?";return{c(){e=f("button"),e.textContent=l,this.h()},l(t){e=u(t,"BUTTON",{class:!0,"data-svelte-h":!0}),H(e)!=="svelte-oq3opr"&&(e.textContent=l),this.h()},h(){i(e,"class","text-gray-600 dark:text-gray-300 bg-gray-300/20 size-5 flex items-center justify-center text-[0.7rem] rounded-full")},m(t,s){I(t,e,s)},p:$e,d(t){t&&c(e)}}}function Fr(n){let e,l;return e=new yr({props:{content:n[1].t("Help"),placement:"left",$$slots:{default:[qr]},$$scope:{ctx:n}}}),{c(){z(e.$$.fragment)},l(t){T(e.$$.fragment,t)},m(t,s){L(e,t,s),l=!0},p(t,s){const r={};s&2&&(r.content=t[1].t("Help")),s&128&&(r.$$scope={dirty:s,ctx:t}),e.$set(r)},i(t){l||(j(e.$$.fragment,t),l=!0)},o(t){E(e.$$.fragment,t),l=!1},d(t){S(e,t)}}}function Ur(n){let e,l,t,s,r,o,d,v,D,y;s=new Kr({props:{showDocsHandler:n[4],showShortcutsHandler:n[5],$$slots:{default:[Fr]},$$scope:{ctx:n}}});function C(h){n[6](h)}let w={};return n[0]!==void 0&&(w.show=n[0]),o=new jr({props:w}),ur.push(()=>mr(o,"show",C)),{c(){e=f("div"),l=f("button"),t=p(),z(s.$$.fragment),r=p(),z(o.$$.fragment),this.h()},l(h){e=u(h,"DIV",{class:!0});var _=m(e);l=u(_,"BUTTON",{id:!0,class:!0}),m(l).forEach(c),t=x(_),T(s.$$.fragment,_),_.forEach(c),r=x(h),T(o.$$.fragment,h),this.h()},h(){i(l,"id","show-shortcuts-button"),i(l,"class","hidden"),i(e,"class","hidden lg:flex fixed bottom-0 right-0 px-2 py-2 z-10")},m(h,_){I(h,e,_),a(e,l),a(e,t),L(s,e,null),I(h,r,_),L(o,h,_),v=!0,D||(y=hr(l,"click",n[3]),D=!0)},p(h,[_]){const Z={};_&1&&(Z.showDocsHandler=h[4]),_&1&&(Z.showShortcutsHandler=h[5]),_&130&&(Z.$$scope={dirty:_,ctx:h}),s.$set(Z);const J={};!d&&_&1&&(d=!0,J.show=h[0],vr(()=>d=!1)),o.$set(J)},i(h){v||(j(s.$$.fragment,h),j(o.$$.fragment,h),v=!0)},o(h){E(s.$$.fragment,h),E(o.$$.fragment,h),v=!1},d(h){h&&(c(e),c(r)),S(s),S(o,h),D=!1,y()}}}function Qr(n,e,l){let t;const s=Tt("i18n");Lt(n,s,y=>l(1,t=y));let r=!1;const o=()=>{l(0,r=!r)},d=()=>{l(0,r=!r)},v=()=>{l(0,r=!r)};function D(y){r=y,l(0,r)}return[r,t,s,o,d,v,D]}class Gr extends De{constructor(e){super(),He(this,e,Qr,Ur,Ve,{})}}function Pr(n){let e,l,t,s;return e=new Gr({}),t=new br({}),{c(){z(e.$$.fragment),l=p(),z(t.$$.fragment)},l(r){T(e.$$.fragment,r),l=x(r),T(t.$$.fragment,r)},m(r,o){L(e,r,o),I(r,l,o),L(t,r,o),s=!0},p:$e,i(r){s||(j(e.$$.fragment,r),j(t.$$.fragment,r),s=!0)},o(r){E(e.$$.fragment,r),E(t.$$.fragment,r),s=!1},d(r){r&&c(l),S(e,r),S(t,r)}}}class as extends De{constructor(e){super(),He(this,e,null,Pr,Ve,{})}}export{as as component};
//# sourceMappingURL=5.e6571a03.js.map