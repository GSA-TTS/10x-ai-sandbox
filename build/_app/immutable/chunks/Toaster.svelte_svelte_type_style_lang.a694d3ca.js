import{a1 as b}from"./scheduler.2ec89978.js";import{w as S}from"./index.f2df4749.js";function z(...t){return t.filter(Boolean).join(" ")}const a=typeof document<"u";function h(t){const o=S(t);function p(l){a&&o.set(l)}function r(l){a&&o.update(l)}return{subscribe:o.subscribe,set:p,update:r}}let w=0;function C(){const t=h([]),o=h([]);function p(s){t.update(e=>[s,...e])}function r(s){var y;const{message:e,...n}=s,u=typeof(s==null?void 0:s.id)=="number"||s.id&&((y=s.id)==null?void 0:y.length)>0?s.id:w++,f=s.dismissable===void 0?!0:s.dismissable,i=s.type===void 0?"default":s.type;return b(t).find(m=>m.id===u)?t.update(m=>m.map(g=>g.id===u?{...g,...s,id:u,title:e,dismissable:f,type:i,updated:!0}:{...g,updated:!1})):p({...n,id:u,title:e,dismissable:f,type:i}),u}function l(s){if(s===void 0){t.update(e=>e.map(n=>({...n,dismiss:!0})));return}return t.update(e=>e.map(n=>n.id===s?{...n,dismiss:!0}:n)),s}function _(s){if(s===void 0){t.set([]);return}return t.update(e=>e.filter(n=>n.id!==s)),s}function T(s,e){return r({...e,type:"default",message:s})}function v(s,e){return r({...e,type:"error",message:s})}function x(s,e){return r({...e,type:"success",message:s})}function I(s,e){return r({...e,type:"info",message:s})}function E(s,e){return r({...e,type:"warning",message:s})}function H(s,e){return r({...e,type:"loading",message:s})}function $(s,e){if(!e)return;let n;e.loading!==void 0&&(n=r({...e,promise:s,type:"loading",message:e.loading}));const u=s instanceof Promise?s:s();let f=n!==void 0;return u.then(i=>{if(i&&typeof i.ok=="boolean"&&!i.ok){f=!1;const d=typeof e.error=="function"?e.error(`HTTP error! status: ${i.status}`):e.error;r({id:n,type:"error",message:d})}else if(e.success!==void 0){f=!1;const d=typeof e.success=="function"?e.success(i):e.success;r({id:n,type:"success",message:d})}}).catch(i=>{if(e.error!==void 0){f=!1;const d=typeof e.error=="function"?e.error(i):e.error;r({id:n,type:"error",message:d})}}).finally(()=>{var i;f&&(l(n),n=void 0),(i=e.finally)==null||i.call(e)}),n}function j(s,e){const n=(e==null?void 0:e.id)||w++;return r({component:s,id:n,...e}),n}function k(s){o.update(e=>e.filter(n=>n.toastId!==s))}function B(s){if(b(o).find(n=>n.toastId===s.toastId)===void 0){o.update(n=>[s,...n]);return}o.update(n=>n.map(u=>u.toastId===s.toastId?s:u))}function P(){t.set([]),o.set([])}return{create:r,addToast:p,dismiss:l,remove:_,message:T,error:v,success:x,info:I,warning:E,loading:H,promise:$,custom:j,removeHeight:k,setHeight:B,reset:P,toasts:t,heights:o}}const c=C();function D(t,o){return c.create({message:t,...o})}const F=D,A=Object.assign(F,{success:c.success,info:c.info,warning:c.warning,error:c.error,custom:c.custom,message:c.message,promise:c.promise,dismiss:c.dismiss,loading:c.loading}),G=t=>({subscribe:t});export{A as a,z as c,c as t,G as u};
//# sourceMappingURL=Toaster.svelte_svelte_type_style_lang.a694d3ca.js.map