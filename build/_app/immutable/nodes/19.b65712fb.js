import{s as S,e as d,i as h,d as w,o as T}from"../chunks/scheduler.2ec89978.js";import{S as b,i as v,a as f,t as u,c as N,b as q,d as C,m as E,e as H,g as I}from"../chunks/index.276f3600.js";import{g as J}from"../chunks/navigation.29f17d28.js";import{c as M,g as O}from"../chunks/index.7983e08f.js";import{T as P}from"../chunks/ToolkitEditor.0a1e1273.js";import{r as j}from"../chunks/index.3b6ce8f7.js";import{a as k}from"../chunks/Toaster.svelte_svelte_type_style_lang.a694d3ca.js";function $(l){var e,t,a,c;let o,r;return o=new P({props:{id:((e=l[2])==null?void 0:e.id)??"",name:((t=l[2])==null?void 0:t.name)??"",meta:((a=l[2])==null?void 0:a.meta)??{description:""},content:((c=l[2])==null?void 0:c.content)??"",clone:l[1]}}),o.$on("save",l[4]),{c(){q(o.$$.fragment)},l(n){C(o.$$.fragment,n)},m(n,s){E(o,n,s),r=!0},p(n,s){var m,p,_,g;const i={};s&4&&(i.id=((m=n[2])==null?void 0:m.id)??""),s&4&&(i.name=((p=n[2])==null?void 0:p.name)??""),s&4&&(i.meta=((_=n[2])==null?void 0:_.meta)??{description:""}),s&4&&(i.content=((g=n[2])==null?void 0:g.content)??""),s&2&&(i.clone=n[1]),o.$set(i)},i(n){r||(f(o.$$.fragment,n),r=!0)},o(n){u(o.$$.fragment,n),r=!1},d(n){H(o,n)}}}function y(l){let o,r,e=l[0]&&$(l);return{c(){e&&e.c(),o=d()},l(t){e&&e.l(t),o=d()},m(t,a){e&&e.m(t,a),h(t,o,a),r=!0},p(t,[a]){t[0]?e?(e.p(t,a),a&1&&f(e,1)):(e=$(t),e.c(),f(e,1),e.m(o.parentNode,o)):e&&(I(),u(e,1,1,()=>{e=null}),N())},i(t){r||(f(e),r=!0)},o(t){u(e),r=!1},d(t){t&&w(o),e&&e.d(t)}}}function z(l,o,r){let e=!1,t=!1,a=null;const c=async s=>{console.log(s),await M(localStorage.token,{id:s.id,name:s.name,meta:s.meta,content:s.content}).catch(m=>(k.error(m),null))&&(k.success("Tool created successfully"),j.set(await O(localStorage.token)),await J("/workspace/tools"))};return T(()=>{sessionStorage.tool&&(r(2,a=JSON.parse(sessionStorage.tool)),sessionStorage.removeItem("tool"),console.log(a),r(1,t=!0)),r(0,e=!0)}),[e,t,a,c,s=>{c(s.detail)}]}class Q extends b{constructor(o){super(),v(this,o,z,y,S,{})}}export{Q as component};
//# sourceMappingURL=19.b65712fb.js.map