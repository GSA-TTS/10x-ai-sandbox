import{s as g,f as y,u as d,l as x,g as A,h as m,v as _,m as w,d as c,j as n,i as B,w as f,r as v}from"./scheduler.2ec89978.js";import{S as j,i as E}from"./index.276f3600.js";function N(h){let e,t,a,r,i,l;return{c(){e=y("div"),t=d("svg"),a=d("style"),r=x(`.spinner_ajPY {
				transform-origin: center;
				animation: spinner_AtaB 0.75s infinite linear;
			}
			@keyframes spinner_AtaB {
				100% {
					transform: rotate(360deg);
				}
			}
		`),i=d("path"),l=d("path"),this.h()},l(s){e=A(s,"DIV",{class:!0});var o=m(e);t=_(o,"svg",{class:!0,viewBox:!0,fill:!0,xmlns:!0});var p=m(t);a=_(p,"style",{});var u=m(a);r=w(u,`.spinner_ajPY {
				transform-origin: center;
				animation: spinner_AtaB 0.75s infinite linear;
			}
			@keyframes spinner_AtaB {
				100% {
					transform: rotate(360deg);
				}
			}
		`),u.forEach(c),i=_(p,"path",{d:!0,opacity:!0}),m(i).forEach(c),l=_(p,"path",{d:!0,class:!0}),m(l).forEach(c),p.forEach(c),o.forEach(c),this.h()},h(){n(i,"d","M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z"),n(i,"opacity",".25"),n(l,"d","M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z"),n(l,"class","spinner_ajPY"),n(t,"class",h[0]),n(t,"viewBox","0 0 24 24"),n(t,"fill","currentColor"),n(t,"xmlns","http://www.w3.org/2000/svg"),n(e,"class","flex justify-center text-center")},m(s,o){B(s,e,o),f(e,t),f(t,a),f(a,r),f(t,i),f(t,l)},p(s,[o]){o&1&&n(t,"class",s[0])},i:v,o:v,d(s){s&&c(e)}}}function S(h,e,t){let{className:a="size-5"}=e;return h.$$set=r=>{"className"in r&&t(0,a=r.className)},[a]}class Z extends j{constructor(e){super(),E(this,e,S,N,g,{className:0})}}export{Z as S};
//# sourceMappingURL=Spinner.bb437d83.js.map