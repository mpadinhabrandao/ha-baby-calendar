/*! Baby Calendar cards. MIT licence. https://github.com/mpadinhabrandao/ha-baby-calendar
 * Bundles Lit (https://lit.dev), BSD-3-Clause:
 * BSD 3-Clause License
 *
 * Copyright (c) 2017 Google LLC. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
var U=globalThis,K=U.ShadowRoot&&(U.ShadyCSS===void 0||U.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,rt=Symbol(),_t=new WeakMap,B=class{constructor(s,t,e){if(this._$cssResult$=!0,e!==rt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=s,this.t=t}get styleSheet(){let s=this.o,t=this.t;if(K&&s===void 0){let e=t!==void 0&&t.length===1;e&&(s=_t.get(t)),s===void 0&&((this.o=s=new CSSStyleSheet).replaceSync(this.cssText),e&&_t.set(t,s))}return s}toString(){return this.cssText}},yt=n=>new B(typeof n=="string"?n:n+"",void 0,rt),M=(n,...s)=>{let t=n.length===1?n[0]:s.reduce((e,i,r)=>e+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+n[r+1],n[0]);return new B(t,n,rt)},vt=(n,s)=>{if(K)n.adoptedStyleSheets=s.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of s){let e=document.createElement("style"),i=U.litNonce;i!==void 0&&e.setAttribute("nonce",i),e.textContent=t.cssText,n.appendChild(e)}},nt=K?n=>n:n=>n instanceof CSSStyleSheet?(s=>{let t="";for(let e of s.cssRules)t+=e.cssText;return yt(t)})(n):n;var{is:It,defineProperty:Ft,getOwnPropertyDescriptor:jt,getOwnPropertyNames:Wt,getOwnPropertySymbols:Vt,getPrototypeOf:qt}=Object,z=globalThis,xt=z.trustedTypes,Gt=xt?xt.emptyScript:"",Jt=z.reactiveElementPolyfillSupport,R=(n,s)=>n,ot={toAttribute(n,s){switch(s){case Boolean:n=n?Gt:null;break;case Object:case Array:n=n==null?n:JSON.stringify(n)}return n},fromAttribute(n,s){let t=n;switch(s){case Boolean:t=n!==null;break;case Number:t=n===null?null:Number(n);break;case Object:case Array:try{t=JSON.parse(n)}catch{t=null}}return t}},wt=(n,s)=>!It(n,s),$t={attribute:!0,type:String,converter:ot,reflect:!1,useDefault:!1,hasChanged:wt};Symbol.metadata??=Symbol("metadata"),z.litPropertyMetadata??=new WeakMap;var v=class extends HTMLElement{static addInitializer(s){this._$Ei(),(this.l??=[]).push(s)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(s,t=$t){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(s)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(s,t),!t.noAccessor){let e=Symbol(),i=this.getPropertyDescriptor(s,e,t);i!==void 0&&Ft(this.prototype,s,i)}}static getPropertyDescriptor(s,t,e){let{get:i,set:r}=jt(this.prototype,s)??{get(){return this[t]},set(o){this[t]=o}};return{get:i,set(o){let c=i?.call(this);r?.call(this,o),this.requestUpdate(s,c,e)},configurable:!0,enumerable:!0}}static getPropertyOptions(s){return this.elementProperties.get(s)??$t}static _$Ei(){if(this.hasOwnProperty(R("elementProperties")))return;let s=qt(this);s.finalize(),s.l!==void 0&&(this.l=[...s.l]),this.elementProperties=new Map(s.elementProperties)}static finalize(){if(this.hasOwnProperty(R("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(R("properties"))){let t=this.properties,e=[...Wt(t),...Vt(t)];for(let i of e)this.createProperty(i,t[i])}let s=this[Symbol.metadata];if(s!==null){let t=litPropertyMetadata.get(s);if(t!==void 0)for(let[e,i]of t)this.elementProperties.set(e,i)}this._$Eh=new Map;for(let[t,e]of this.elementProperties){let i=this._$Eu(t,e);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(s){let t=[];if(Array.isArray(s)){let e=new Set(s.flat(1/0).reverse());for(let i of e)t.unshift(nt(i))}else s!==void 0&&t.push(nt(s));return t}static _$Eu(s,t){let e=t.attribute;return e===!1?void 0:typeof e=="string"?e:typeof s=="string"?s.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(s=>this.enableUpdating=s),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(s=>s(this))}addController(s){(this._$EO??=new Set).add(s),this.renderRoot!==void 0&&this.isConnected&&s.hostConnected?.()}removeController(s){this._$EO?.delete(s)}_$E_(){let s=new Map,t=this.constructor.elementProperties;for(let e of t.keys())this.hasOwnProperty(e)&&(s.set(e,this[e]),delete this[e]);s.size>0&&(this._$Ep=s)}createRenderRoot(){let s=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return vt(s,this.constructor.elementStyles),s}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(s=>s.hostConnected?.())}enableUpdating(s){}disconnectedCallback(){this._$EO?.forEach(s=>s.hostDisconnected?.())}attributeChangedCallback(s,t,e){this._$AK(s,e)}_$ET(s,t){let e=this.constructor.elementProperties.get(s),i=this.constructor._$Eu(s,e);if(i!==void 0&&e.reflect===!0){let r=(e.converter?.toAttribute!==void 0?e.converter:ot).toAttribute(t,e.type);this._$Em=s,r==null?this.removeAttribute(i):this.setAttribute(i,r),this._$Em=null}}_$AK(s,t){let e=this.constructor,i=e._$Eh.get(s);if(i!==void 0&&this._$Em!==i){let r=e.getPropertyOptions(i),o=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:ot;this._$Em=i;let c=o.fromAttribute(t,r.type);this[i]=c??this._$Ej?.get(i)??c,this._$Em=null}}requestUpdate(s,t,e,i=!1,r){if(s!==void 0){let o=this.constructor;if(i===!1&&(r=this[s]),e??=o.getPropertyOptions(s),!((e.hasChanged??wt)(r,t)||e.useDefault&&e.reflect&&r===this._$Ej?.get(s)&&!this.hasAttribute(o._$Eu(s,e))))return;this.C(s,t,e)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(s,t,{useDefault:e,reflect:i,wrapped:r},o){e&&!(this._$Ej??=new Map).has(s)&&(this._$Ej.set(s,o??t??this[s]),r!==!0||o!==void 0)||(this._$AL.has(s)||(this.hasUpdated||e||(t=void 0),this._$AL.set(s,t)),i===!0&&this._$Em!==s&&(this._$Eq??=new Set).add(s))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let s=this.scheduleUpdate();return s!=null&&await s,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,r]of this._$Ep)this[i]=r;this._$Ep=void 0}let e=this.constructor.elementProperties;if(e.size>0)for(let[i,r]of e){let{wrapped:o}=r,c=this[i];o!==!0||this._$AL.has(i)||c===void 0||this.C(i,void 0,r,c)}}let s=!1,t=this._$AL;try{s=this.shouldUpdate(t),s?(this.willUpdate(t),this._$EO?.forEach(e=>e.hostUpdate?.()),this.update(t)):this._$EM()}catch(e){throw s=!1,this._$EM(),e}s&&this._$AE(t)}willUpdate(s){}_$AE(s){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(s)),this.updated(s)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(s){return!0}update(s){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(s){}firstUpdated(s){}};v.elementStyles=[],v.shadowRootOptions={mode:"open"},v[R("elementProperties")]=new Map,v[R("finalized")]=new Map,Jt?.({ReactiveElement:v}),(z.reactiveElementVersions??=[]).push("2.1.2");var ht=globalThis,At=n=>n,I=ht.trustedTypes,St=I?I.createPolicy("lit-html",{createHTML:n=>n}):void 0,Mt="$lit$",x=`lit$${Math.random().toFixed(9).slice(2)}$`,Rt="?"+x,Qt=`<${Rt}>`,S=document,D=()=>S.createComment(""),N=n=>n===null||typeof n!="object"&&typeof n!="function",mt=Array.isArray,Xt=n=>mt(n)||typeof n?.[Symbol.iterator]=="function",at=`[ 	
\f\r]`,P=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Et=/-->/g,Tt=/>/g,w=RegExp(`>|${at}(?:([^\\s"'>=/]+)(${at}*=${at}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),Ct=/'/g,kt=/"/g,Pt=/^(?:script|style|textarea|title)$/i,gt=n=>(s,...t)=>({_$litType$:n,strings:s,values:t}),a=gt(1),fe=gt(2),be=gt(3),E=Symbol.for("lit-noChange"),u=Symbol.for("lit-nothing"),Bt=new WeakMap,A=S.createTreeWalker(S,129);function Dt(n,s){if(!mt(n)||!n.hasOwnProperty("raw"))throw Error("invalid template strings array");return St!==void 0?St.createHTML(s):s}var Yt=(n,s)=>{let t=n.length-1,e=[],i,r=s===2?"<svg>":s===3?"<math>":"",o=P;for(let c=0;c<t;c++){let l=n[c],d,m,p=-1,b=0;for(;b<l.length&&(o.lastIndex=b,m=o.exec(l),m!==null);)b=o.lastIndex,o===P?m[1]==="!--"?o=Et:m[1]!==void 0?o=Tt:m[2]!==void 0?(Pt.test(m[2])&&(i=RegExp("</"+m[2],"g")),o=w):m[3]!==void 0&&(o=w):o===w?m[0]===">"?(o=i??P,p=-1):m[1]===void 0?p=-2:(p=o.lastIndex-m[2].length,d=m[1],o=m[3]===void 0?w:m[3]==='"'?kt:Ct):o===kt||o===Ct?o=w:o===Et||o===Tt?o=P:(o=w,i=void 0);let _=o===w&&n[c+1].startsWith("/>")?" ":"";r+=o===P?l+Qt:p>=0?(e.push(d),l.slice(0,p)+Mt+l.slice(p)+x+_):l+x+(p===-2?c:_)}return[Dt(n,r+(n[t]||"<?>")+(s===2?"</svg>":s===3?"</math>":"")),e]},L=class n{constructor({strings:s,_$litType$:t},e){let i;this.parts=[];let r=0,o=0,c=s.length-1,l=this.parts,[d,m]=Yt(s,t);if(this.el=n.createElement(d,e),A.currentNode=this.el.content,t===2||t===3){let p=this.el.content.firstChild;p.replaceWith(...p.childNodes)}for(;(i=A.nextNode())!==null&&l.length<c;){if(i.nodeType===1){if(i.hasAttributes())for(let p of i.getAttributeNames())if(p.endsWith(Mt)){let b=m[o++],_=i.getAttribute(p).split(x),$=/([.?@])?(.*)/.exec(b);l.push({type:1,index:r,name:$[2],strings:_,ctor:$[1]==="."?ct:$[1]==="?"?dt:$[1]==="@"?pt:k}),i.removeAttribute(p)}else p.startsWith(x)&&(l.push({type:6,index:r}),i.removeAttribute(p));if(Pt.test(i.tagName)){let p=i.textContent.split(x),b=p.length-1;if(b>0){i.textContent=I?I.emptyScript:"";for(let _=0;_<b;_++)i.append(p[_],D()),A.nextNode(),l.push({type:2,index:++r});i.append(p[b],D())}}}else if(i.nodeType===8)if(i.data===Rt)l.push({type:2,index:r});else{let p=-1;for(;(p=i.data.indexOf(x,p+1))!==-1;)l.push({type:7,index:r}),p+=x.length-1}r++}}static createElement(s,t){let e=S.createElement("template");return e.innerHTML=s,e}};function C(n,s,t=n,e){if(s===E)return s;let i=e!==void 0?t._$Co?.[e]:t._$Cl,r=N(s)?void 0:s._$litDirective$;return i?.constructor!==r&&(i?._$AO?.(!1),r===void 0?i=void 0:(i=new r(n),i._$AT(n,t,e)),e!==void 0?(t._$Co??=[])[e]=i:t._$Cl=i),i!==void 0&&(s=C(n,i._$AS(n,s.values),i,e)),s}var lt=class{constructor(s,t){this._$AV=[],this._$AN=void 0,this._$AD=s,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(s){let{el:{content:t},parts:e}=this._$AD,i=(s?.creationScope??S).importNode(t,!0);A.currentNode=i;let r=A.nextNode(),o=0,c=0,l=e[0];for(;l!==void 0;){if(o===l.index){let d;l.type===2?d=new O(r,r.nextSibling,this,s):l.type===1?d=new l.ctor(r,l.name,l.strings,this,s):l.type===6&&(d=new ut(r,this,s)),this._$AV.push(d),l=e[++c]}o!==l?.index&&(r=A.nextNode(),o++)}return A.currentNode=S,i}p(s){let t=0;for(let e of this._$AV)e!==void 0&&(e.strings!==void 0?(e._$AI(s,e,t),t+=e.strings.length-2):e._$AI(s[t])),t++}},O=class n{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(s,t,e,i){this.type=2,this._$AH=u,this._$AN=void 0,this._$AA=s,this._$AB=t,this._$AM=e,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let s=this._$AA.parentNode,t=this._$AM;return t!==void 0&&s?.nodeType===11&&(s=t.parentNode),s}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(s,t=this){s=C(this,s,t),N(s)?s===u||s==null||s===""?(this._$AH!==u&&this._$AR(),this._$AH=u):s!==this._$AH&&s!==E&&this._(s):s._$litType$!==void 0?this.$(s):s.nodeType!==void 0?this.T(s):Xt(s)?this.k(s):this._(s)}O(s){return this._$AA.parentNode.insertBefore(s,this._$AB)}T(s){this._$AH!==s&&(this._$AR(),this._$AH=this.O(s))}_(s){this._$AH!==u&&N(this._$AH)?this._$AA.nextSibling.data=s:this.T(S.createTextNode(s)),this._$AH=s}$(s){let{values:t,_$litType$:e}=s,i=typeof e=="number"?this._$AC(s):(e.el===void 0&&(e.el=L.createElement(Dt(e.h,e.h[0]),this.options)),e);if(this._$AH?._$AD===i)this._$AH.p(t);else{let r=new lt(i,this),o=r.u(this.options);r.p(t),this.T(o),this._$AH=r}}_$AC(s){let t=Bt.get(s.strings);return t===void 0&&Bt.set(s.strings,t=new L(s)),t}k(s){mt(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,e,i=0;for(let r of s)i===t.length?t.push(e=new n(this.O(D()),this.O(D()),this,this.options)):e=t[i],e._$AI(r),i++;i<t.length&&(this._$AR(e&&e._$AB.nextSibling,i),t.length=i)}_$AR(s=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);s!==this._$AB;){let e=At(s).nextSibling;At(s).remove(),s=e}}setConnected(s){this._$AM===void 0&&(this._$Cv=s,this._$AP?.(s))}},k=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(s,t,e,i,r){this.type=1,this._$AH=u,this._$AN=void 0,this.element=s,this.name=t,this._$AM=i,this.options=r,e.length>2||e[0]!==""||e[1]!==""?(this._$AH=Array(e.length-1).fill(new String),this.strings=e):this._$AH=u}_$AI(s,t=this,e,i){let r=this.strings,o=!1;if(r===void 0)s=C(this,s,t,0),o=!N(s)||s!==this._$AH&&s!==E,o&&(this._$AH=s);else{let c=s,l,d;for(s=r[0],l=0;l<r.length-1;l++)d=C(this,c[e+l],t,l),d===E&&(d=this._$AH[l]),o||=!N(d)||d!==this._$AH[l],d===u?s=u:s!==u&&(s+=(d??"")+r[l+1]),this._$AH[l]=d}o&&!i&&this.j(s)}j(s){s===u?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,s??"")}},ct=class extends k{constructor(){super(...arguments),this.type=3}j(s){this.element[this.name]=s===u?void 0:s}},dt=class extends k{constructor(){super(...arguments),this.type=4}j(s){this.element.toggleAttribute(this.name,!!s&&s!==u)}},pt=class extends k{constructor(s,t,e,i,r){super(s,t,e,i,r),this.type=5}_$AI(s,t=this){if((s=C(this,s,t,0)??u)===E)return;let e=this._$AH,i=s===u&&e!==u||s.capture!==e.capture||s.once!==e.once||s.passive!==e.passive,r=s!==u&&(e===u||i);i&&this.element.removeEventListener(this.name,this,e),r&&this.element.addEventListener(this.name,this,s),this._$AH=s}handleEvent(s){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,s):this._$AH.handleEvent(s)}},ut=class{constructor(s,t,e){this.element=s,this.type=6,this._$AN=void 0,this._$AM=t,this.options=e}get _$AU(){return this._$AM._$AU}_$AI(s){C(this,s)}};var Zt=ht.litHtmlPolyfillSupport;Zt?.(L,O),(ht.litHtmlVersions??=[]).push("3.3.3");var Nt=(n,s,t)=>{let e=t?.renderBefore??s,i=e._$litPart$;if(i===void 0){let r=t?.renderBefore??null;e._$litPart$=i=new O(s.insertBefore(D(),r),r,void 0,t??{})}return i._$AI(n),i};var ft=globalThis,y=class extends v{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let s=super.createRenderRoot();return this.renderOptions.renderBefore??=s.firstChild,s}update(s){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(s),this._$Do=Nt(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return E}};y._$litElement$=!0,y.finalized=!0,ft.litElementHydrateSupport?.({LitElement:y});var te=ft.litElementPolyfillSupport;te?.({LitElement:y});(ft.litElementVersions??=[]).push("4.2.2");var ee={diapers:"Diapers",wet:"Wet",dirty:"Dirty",both:"Both",stool_question:"Dirty diaper logged. What was it like?",stool_optional:`Optional: if you don't choose, it stays just "dirty".`,stool_normal:"Normal",stool_soft:"Soft",stool_hard:"Hard",stool_diarrhea:"Diarrhoea",bottle:"Bottle",log_bottle:"Log bottle",less:"Less 10 ml",more:"More 10 ml",formula:"Formula",breast_milk:"Breast milk",breastfeeding:"Breastfeeding",left:"Left",right:"Right",stop:"Stop",last_feed:"Last feed \xB7 {time} ({ago})",feeding_since:"Feeding since {time}",pause:"pause {duration}",total:"{duration} in total",running:"running",no_feed:"No feed yet",sleep:"Sleep",fell_asleep:"Fell asleep",woke_up:"Woke up",asleep_since:"Asleep since {time}",medications:"Medications",nothing_due:"No dose due",due_now:"Due",given:"Given",summary:"Summary",ate:"Ate",diaper:"Diaper",awake:"Awake",asleep:"Asleep",ago:"{duration} ago",never:"\u2014",today:"Today",diaper_changes:"Diapers",wet_dirty:"{wet} wet \xB7 {dirty} dirty",bottles:"Bottles",feeds:"Breastfeeding",sleeps:"Sleep",solids:"Solids",pumping:"Pumping",other:"Other entries",weight:"Weight",length:"Length",temperature:"Temperature",medication:"Medication",amount:"Amount",side:"Side",side_none:"Not specified",side_both:"Both",notes:"Notes",value:"Value",save:"Save",cancel:"Cancel",recent:"Recent entries",no_entries:"No entries in the last 24 hours",now:"Now",when:"When",minutes_ago:"{minutes} min ago",logged:"Logged: {what} at {time}",undo:"Undo",undone:"Undone",not_recorded:"Not recorded: {error}",baby_not_found:"Baby not found. Choose a baby in the card's settings.",no_baby:"Choose a baby in the card's settings.",tracker_off:"{tracker} is not enabled for {baby}.",baby:"Baby",show_all:"Show every active medication",dose_of:"Dose of {name}",diaper_wet:"wet diaper",diaper_dirty:"dirty diaper",diaper_both:"wet and dirty diaper",bottle_of:"bottle {amount} ml",feed_side:"breastfeeding {side}",sleep_entry:"sleep",weight_of:"weight {value} g",length_of:"length {value} cm",temperature_of:"temperature {value} \xB0C",pumping_of:"pumping {amount} ml",solids_entry:"solids",medication_of:"{name}"},se={diapers:"Fraldas",wet:"Xixi",dirty:"Coc\xF3",both:"Os dois",stool_question:"Coc\xF3 registado. Como era?",stool_optional:'Opcional: se n\xE3o escolheres, fica s\xF3 "coc\xF3".',stool_normal:"Normal",stool_soft:"Mole",stool_hard:"Duro",stool_diarrhea:"Diarreia",bottle:"Biber\xE3o",log_bottle:"Registar biber\xE3o",less:"Menos 10 ml",more:"Mais 10 ml",formula:"F\xF3rmula",breast_milk:"Leite materno",breastfeeding:"Mama",left:"Esquerda",right:"Direita",stop:"Parar",last_feed:"\xDAltima mamada \xB7 {time} ({ago})",feeding_since:"Mamada desde as {time}",pause:"pausa {duration}",total:"{duration} no total",running:"a decorrer",no_feed:"Ainda sem mamadas",sleep:"Sono",fell_asleep:"Adormeceu",woke_up:"Acordou",asleep_since:"A dormir desde as {time}",medications:"Medicamentos",nothing_due:"Nenhuma dose por dar",due_now:"Por dar",given:"Dado",summary:"Resumo",ate:"Comeu",diaper:"Fralda",awake:"Acordado",asleep:"A dormir",ago:"h\xE1 {duration}",never:"\u2014",today:"Hoje",diaper_changes:"Fraldas",wet_dirty:"{wet} xixi \xB7 {dirty} coc\xF3",bottles:"Biber\xF5es",feeds:"Mama",sleeps:"Sono",solids:"S\xF3lidos",pumping:"Extra\xE7\xE3o",other:"Outros registos",weight:"Peso",length:"Comprimento",temperature:"Temperatura",medication:"Medicamento",amount:"Quantidade",side:"Lado",side_none:"N\xE3o indicado",side_both:"Ambos",notes:"Notas",value:"Valor",save:"Guardar",cancel:"Cancelar",recent:"\xDAltimos registos",no_entries:"Sem registos nas \xFAltimas 24 horas",now:"Agora",when:"Quando",minutes_ago:"H\xE1 {minutes} min",logged:"Registado: {what} \xE0s {time}",undo:"Desfazer",undone:"Desfeito",not_recorded:"N\xE3o ficou registado: {error}",baby_not_found:"Beb\xE9 n\xE3o encontrado. Escolhe um beb\xE9 nas defini\xE7\xF5es do card.",no_baby:"Escolhe um beb\xE9 nas defini\xE7\xF5es do card.",tracker_off:"{tracker} n\xE3o est\xE1 ligado para {baby}.",baby:"Beb\xE9",show_all:"Mostrar todos os medicamentos ativos",dose_of:"Dose de {name}",diaper_wet:"fralda com xixi",diaper_dirty:"fralda com coc\xF3",diaper_both:"fralda com xixi e coc\xF3",bottle_of:"biber\xE3o {amount} ml",feed_side:"mama {side}",sleep_entry:"sono",weight_of:"peso {value} g",length_of:"comprimento {value} cm",temperature_of:"temperatura {value} \xB0C",pumping_of:"extra\xE7\xE3o {amount} ml",solids_entry:"s\xF3lidos",medication_of:"{name}"};function F(n){return n?.toLowerCase().startsWith("pt")?"pt":"en"}function g(n,s,t={}){return(n==="pt"?se:ee)[s].replace(/\{(\w+)\}/g,(i,r)=>r in t?String(t[r]):`{${r}}`)}var H=60,Lt=3600;function f(n){let s=Math.max(0,Math.round(n/H));if(s<60)return`${s} min`;let t=Math.floor(s/60),e=s%60;return e?`${t} h ${e} min`:`${t} h`}function j(n){let s=Math.max(0,Math.floor(n)),t=Math.floor(s/Lt),e=Math.floor(s%Lt/H),i=s%H,r=o=>String(o).padStart(2,"0");return t?`${t}:${r(e)}:${r(i)}`:`${r(e)}:${r(i)}`}function T(n,s){return n.toLocaleTimeString(s==="pt"?"pt-PT":"en-GB",{hour:"2-digit",minute:"2-digit"})}function ie(n,s,t){return g(t,"ago",{duration:f((s.getTime()-n.getTime())/1e3)})}function re(n,s){return n==="left"?g(s,"left"):n==="right"?g(s,"right"):g(s,"side_none")}function Ot(n,s,t){if(!n.length)return null;let e=new Date(n[0].start),i=n[n.length-1].end===null,r=[],o=0;n.forEach((d,m)=>{if(m>0){let _=new Date(n[m-1].end??n[m-1].start),$=(new Date(d.start).getTime()-_.getTime())/1e3;$>=H&&r.push(g(t,"pause",{duration:f($)}))}let p=re(d.side,t);if(d.end===null){r.push(`${p} ${g(t,"running")}`);return}let b=(new Date(d.end).getTime()-new Date(d.start).getTime())/1e3;o+=b,r.push(`${p} ${f(b)}`)}),n.length>1&&!i&&r.push(g(t,"total",{duration:f(o)}));let c=T(e,t);return{heading:i?g(t,"feeding_since",{time:c}):g(t,"last_feed",{time:c,ago:ie(e,s,t)}),line:r.join(" \xB7 ")}}function Ht(n,s){if(n)return new Date(s.getTime()-n*H*1e3).toISOString()}var Ut=[0,5,10,15,20,30,45,60,90,120];var W=class{constructor(){this.last=new Map}allow(s,t=Date.now()){let e=this.last.get(s);return e!==void 0&&t-e<3e3?!1:(this.last.set(s,t),!0)}};var bt=new WeakMap;function V(n,s){let t=bt.get(n);if(!t){let i={babies:null,listeners:new Set,unsubscribe:null};i.unsubscribe=n.subscribeMessage(r=>{i.babies=r.babies,i.listeners.forEach(o=>o(r.babies))},{type:"baby_calendar/subscribe_babies"}),bt.set(n,i),t=i}let e=t;return e.listeners.add(s),e.babies&&s(e.babies),()=>{e.listeners.delete(s),e.listeners.size||(bt.delete(n),e.unsubscribe?.then(i=>i()).catch(()=>{}))}}var ne=6e4,h=class extends y{constructor(){super(...arguments);this._babies=null;this._minutesAgo=0;this._undo=null;this._error=null;this._now=Date.now();this._guard=new W;this.tracker=null;this.logs=!0;this.accent="var(--primary-color)";this._timerMs=null}static{this.properties={hass:{attribute:!1},_config:{state:!0},_babies:{state:!0},_minutesAgo:{state:!0},_undo:{state:!0},_error:{state:!0},_now:{state:!0}}}setConfig(t){this._config=t}getCardSize(){return 3}getGridOptions(){return{columns:12,min_columns:6}}static getConfigElement(){return document.createElement("baby-calendar-card-editor")}static getStubConfig(){return{baby:""}}get language(){return F(this.hass?.locale?.language??this.hass?.language)}text(t,e){return g(this.language,t,e)}get baby(){return this._babies?.find(t=>t.device_id===this._config?.baby)}entity(t,e){let i=t.entities[e];return i?this.hass?.states[i]:void 0}connectedCallback(){super.connectedCallback(),this._watch()}disconnectedCallback(){super.disconnectedCallback(),this._stopWatching?.(),this._stopWatching=void 0,this._setTimer(null)}updated(t){t.has("hass")&&this._watch(),this._setTimer(this.tickMs())}tickMs(){return this._undo?1e3:null}_setTimer(t){this._timer!==void 0&&t===this._timerMs||(this._timer!==void 0&&window.clearInterval(this._timer),this._timer=void 0,this._timerMs=t,!(t===null||!this.isConnected)&&(this._timer=window.setInterval(()=>{this._now=Date.now(),this._undo&&this._undo.expires<=this._now&&(this._undo=null)},t)))}_watch(){this._stopWatching||!this.hass||!this.isConnected||(this._stopWatching=V(this.hass.connection,t=>{this._babies=t}))}async call(t,e,i,r=!1){return(await this.hass.connection.sendMessagePromise({type:"call_service",domain:t,service:e,service_data:i,return_response:r}))?.response??null}async log(t,e,i,r){let o=this.baby;if(!o||!this._guard.allow(t))return!1;let c=Ht(this._minutesAgo,new Date);try{let l=await this.call("baby_calendar",e,{device_id:o.device_id,...i,...c?{time:c}:{}},!0);this._minutesAgo=0,this._error=null;let d=l?.event_id;return d&&this.showUndo(d,r,c?new Date(c):new Date),!0}catch(l){return this.showError(l),!1}}async act(t,e){if(!this._guard.allow(t))return!1;try{return await e(),this._error=null,!0}catch(i){return this.showError(i),!1}}showUndo(t,e,i){this._undo={eventId:t,text:this.text("logged",{what:e,time:T(i,this.language)}),expires:Date.now()+ne}}showError(t){let e=t?.message??(typeof t=="string"?t:String(t));this._error=this.text("not_recorded",{error:e})}async _undoLast(){let t=this._undo;if(t)try{await this.call("baby_calendar","delete_event",{event_id:t.eventId}),this._undo=null,this._error=null}catch(e){this.showError(e)}}render(){let t=this._message();return a`<ha-card style="--bc-accent: ${this.accent}">
      <div class="header">
        <h2>${this.text(this.titleKey)}</h2>
        ${this.logs&&!t?this._renderChip():u}
      </div>
      ${t?a`<p class="message">${t}</p>`:a`<div class="body">${this.renderBody(this.baby)}</div>`}
      ${this._undo&&!t?a`<div class="undo" role="status">
            <span>${this._undo.text}</span>
            <button class="undo-button" @click=${this._undoLast}>${this.text("undo")}</button>
          </div>`:u}
      ${this._error?a`<p class="error" role="alert">${this._error}</p>`:u}
    </ha-card>`}_message(){if(!this._config?.baby)return this.text("no_baby");if(this._babies===null)return" ";let t=this.baby;return t?this.tracker&&!t.trackers.includes(this.tracker)?this.text("tracker_off",{tracker:this.text(this.titleKey),baby:t.name}):null:this.text("baby_not_found")}_renderChip(){return a`<label class="chip">
      <span class="visually-hidden">${this.text("when")}</span>
      <select
        .value=${String(this._minutesAgo)}
        @change=${t=>{this._minutesAgo=Number(t.target.value)}}
      >
        ${Ut.map(t=>a`<option value=${t} ?selected=${t===this._minutesAgo}>
              ${t?this.text("minutes_ago",{minutes:t}):this.text("now")}
            </option>`)}
      </select>
    </label>`}static{this.styles=M`
    :host {
      display: block;
    }
    ha-card {
      padding: 12px 16px 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      height: 100%;
      box-sizing: border-box;
      color: var(--primary-text-color);
    }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      min-height: 40px;
    }
    h2 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--primary-text-color);
    }
    .body {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .message {
      margin: 0;
      color: var(--secondary-text-color);
    }
    .row {
      display: grid;
      grid-template-columns: repeat(var(--columns, 3), minmax(0, 1fr));
      gap: 8px;
    }
    .big {
      min-height: 56px;
      border: none;
      border-radius: var(--ha-card-border-radius, 12px);
      background: color-mix(in srgb, var(--bc-accent) 22%, transparent);
      color: var(--primary-text-color);
      font: inherit;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      padding: 8px;
    }
    .big:hover {
      background: color-mix(in srgb, var(--bc-accent) 32%, transparent);
    }
    .big.active {
      outline: 2px solid var(--bc-accent);
      background: color-mix(in srgb, var(--bc-accent) 38%, transparent);
    }
    .big:focus-visible,
    .small:focus-visible,
    select:focus-visible {
      outline: 2px solid var(--primary-color);
      outline-offset: 2px;
    }
    .small {
      min-height: 44px;
      border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
      border-radius: 22px;
      background: transparent;
      color: var(--primary-text-color);
      font: inherit;
      font-size: 14px;
      padding: 0 14px;
      cursor: pointer;
    }
    .small.selected {
      background: color-mix(in srgb, var(--bc-accent) 22%, transparent);
      border-color: var(--bc-accent);
      font-weight: 600;
    }
    .amount {
      display: grid;
      grid-template-columns: 56px minmax(0, 1fr) 56px;
      gap: 8px;
    }
    .step {
      font-size: 24px;
    }
    .value {
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }
    .big.primary {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: var(--bc-accent);
      color: var(--text-primary-color, #fff);
      font-size: 17px;
    }
    .big.primary:hover {
      background: color-mix(in srgb, var(--bc-accent) 85%, black);
    }
    .choices {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .stack {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
    }
    .time {
      font-size: 22px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }
    .line {
      font-size: 15px;
      font-weight: 500;
    }
    .medication {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 8px 8px 12px;
      border-radius: 12px;
      background: color-mix(in srgb, var(--primary-text-color) 6%, transparent);
    }
    .medication.due {
      background: color-mix(in srgb, var(--bc-accent) 14%, transparent);
      border: 1px solid var(--bc-accent);
    }
    .medication .what {
      flex-grow: 1;
    }
    .medication .label {
      font-size: 13px;
      color: var(--secondary-text-color);
    }
    .medication .name {
      font-size: 16px;
      font-weight: 600;
    }
    .given {
      min-width: 96px;
    }
    .form {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .field {
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 14px;
      color: var(--secondary-text-color);
    }
    .field input,
    .field select {
      min-height: 44px;
      font: inherit;
      font-size: 16px;
      color: var(--primary-text-color);
      background: var(--card-background-color, transparent);
      border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
      border-radius: 10px;
      padding: 0 10px;
    }
    .list {
      list-style: none;
      margin: 0;
      padding: 0;
    }
    .list li {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.2));
    }
    .list li:last-child {
      border-bottom: none;
    }
    .when {
      color: var(--secondary-text-color);
      white-space: nowrap;
    }
    .question {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 12px;
      border-radius: 12px;
      border: 1px solid var(--bc-accent);
      background: color-mix(in srgb, var(--bc-accent) 10%, transparent);
    }
    .ask {
      margin: 0;
      font-weight: 600;
    }
    .hint {
      margin: 0;
      font-size: 13px;
      color: var(--secondary-text-color);
    }
    .chip select {
      min-height: 40px;
      border-radius: 20px;
      border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
      background: var(--card-background-color, transparent);
      color: var(--primary-text-color);
      font: inherit;
      font-size: 14px;
      padding: 0 12px;
    }
    .undo {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 6px 6px 6px 12px;
      border-radius: 12px;
      background: color-mix(in srgb, var(--primary-text-color) 10%, transparent);
      font-size: 14px;
    }
    .undo-button {
      min-height: 40px;
      border: none;
      border-radius: 10px;
      background: color-mix(in srgb, var(--primary-text-color) 16%, transparent);
      color: var(--primary-text-color);
      font: inherit;
      font-weight: 600;
      padding: 0 14px;
      cursor: pointer;
    }
    .error {
      margin: 0;
      color: var(--error-color, #db4437);
      font-size: 14px;
    }
    .visually-hidden {
      position: absolute;
      width: 1px;
      height: 1px;
      overflow: hidden;
      clip: rect(0 0 0 0);
    }
    .facts {
      display: grid;
      grid-template-columns: repeat(var(--columns, 3), minmax(0, 1fr));
      gap: 8px;
    }
    .fact {
      border-radius: 12px;
      padding: 10px 12px;
      background: color-mix(in srgb, var(--primary-text-color) 6%, transparent);
    }
    .fact .label {
      font-size: 13px;
      color: var(--secondary-text-color);
    }
    .fact .value {
      font-size: 18px;
      font-weight: 600;
    }
    .fact .detail {
      font-size: 13px;
      color: var(--secondary-text-color);
    }
  `}};var Kt=10,zt=["formula","breast_milk"],q=class extends h{constructor(){super(...arguments);this.tracker="bottle";this.titleKey="bottle";this.accent="var(--blue-color, #2196f3)";this._pending=null}static{this.properties={...h.properties,_pending:{state:!0}}}amount(t){let e=Number(this.entity(t,"bottle_amount")?.state),i=Number.isFinite(e)?e:0;return this._pending!==null&&this._pending===i&&(this._pending=null),this._pending??i}async setAmount(t,e){let i=this.entity(t,"bottle_amount"),r=Number(i?.attributes.max??500),o=Math.min(r,Math.max(0,e));this._pending=o;try{await this.call("number","set_value",{entity_id:t.entities.bottle_amount,value:o}),this._error=null}catch(c){this._pending=null,this.showError(c)}}renderBody(t){let e=this.amount(t),i=this.entity(t,"bottle_content")?.state;return a`
      <div class="amount">
        <button
          class="big step"
          aria-label=${this.text("less")}
          @click=${()=>this.setAmount(t,e-Kt)}
        >
          −
        </button>
        <div class="value" aria-live="polite">${e} ml</div>
        <button
          class="big step"
          aria-label=${this.text("more")}
          @click=${()=>this.setAmount(t,e+Kt)}
        >
          +
        </button>
      </div>
      <div class="choices">
        ${zt.map(r=>a`<button
            class="small ${i===r?"selected":""}"
            aria-pressed=${i===r?"true":"false"}
            @click=${()=>this.act(`bottle_content_${r}`,()=>this.call("select","select_option",{entity_id:t.entities.bottle_content,option:r}))}
          >
            ${this.text(r)}
          </button>`)}
      </div>
      <button
        class="big primary"
        @click=${()=>this.log("bottle","log_bottle",{amount:e,...i&&zt.includes(i)?{content:i}:{}},this.text("bottle_of",{amount:e}))}
      >
        <ha-icon icon="mdi:baby-bottle-outline"></ha-icon>
        <span>${this.text("log_bottle")}</span>
      </button>
    `}};var oe=["left","right"],G=class extends h{constructor(){super(...arguments);this.tracker="breastfeeding";this.titleKey="breastfeeding";this.accent="var(--pink-color, #e91e63)"}running(t){let e=this.entity(t,"breastfeeding_timer");if(e?.state!=="on"||!e.attributes.started_at)return null;let i=this.entity(t,"breastfeeding_last");return{side:i?.attributes.in_progress?i.attributes.side??null:null,start:new Date(e.attributes.started_at)}}tickMs(){let t=this.baby;return t&&this.running(t)?1e3:super.tickMs()??3e4}async tap(t,e){let i=this.running(t),r=this.text("feed_side",{side:this.text(e).toLowerCase()});if(i&&i.side===e){await this.log(`stop_${e}`,"stop_breastfeeding",{},r);return}i&&!await this.act(`stop_${i.side}`,()=>this.call("baby_calendar","stop_breastfeeding",{device_id:t.device_id}))||await this.log(`start_${e}`,"start_breastfeeding",{side:e},r)}renderBody(t){let e=this.running(t),i=new Date(this._now),r=this.entity(t,"breastfeeding_last")?.attributes.feed??[],o=Ot(r,i,this.language);return a`
      <div class="row" style="--columns: 2">
        ${oe.map(c=>{let l=e?.side===c;return a`<button
            class="big ${l?"active":""}"
            @click=${()=>this.tap(t,c)}
          >
            ${l?a`<span class="stack">
                  <span>${this.text("stop")} · ${this.text(c).toLowerCase()}</span>
                  <span class="time"
                    >${j((i.getTime()-e.start.getTime())/1e3)}</span
                  >
                </span>`:this.text(c)}
          </button>`})}
      </div>
      <div class="fact">
        ${o?a`<div class="label">${o.heading}</div>
              <div class="line">${o.line}</div>`:a`<div class="label">${this.text("no_feed")}</div>`}
      </div>
    `}};var ae=["wet","dirty","both"],le=["normal","soft","hard","diarrhea"],J=class extends h{constructor(){super(...arguments);this.tracker="diaper";this.titleKey="diapers";this.accent="var(--amber-color, #ffc107)"}renderBody(t){let e=this.entity(t,"stool_prompt")?.state==="on";return a`
      <div class="row">
        ${ae.map(i=>a`<button
            class="big"
            @click=${()=>this.log(`diaper_${i}`,"log_diaper",{content:i},this.text(`diaper_${i}`))}
          >
            ${this.text(i)}
          </button>`)}
      </div>
      ${e?a`<div class="question" role="group" aria-label=${this.text("stool_question")}>
            <p class="ask">${this.text("stool_question")}</p>
            <div class="row" style="--columns: 2">
              ${le.map(i=>a`<button
                  class="big"
                  @click=${()=>this.act(`stool_${i}`,()=>this.call("button","press",{entity_id:t.entities[`stool_${i}`]}))}
                >
                  ${this.text(`stool_${i}`)}
                </button>`)}
            </div>
            <p class="hint">${this.text("stool_optional")}</p>
          </div>`:""}
    `}};var Q={weight:{unit:"g",step:"1",what:"weight_of"},length:{unit:"cm",step:"0.5",what:"length_of"},temperature:{unit:"\xB0C",step:"0.1",what:"temperature_of"}},X=class extends h{constructor(){super(...arguments);this.titleKey="other";this.accent="var(--teal-color, #009688)";this._open=null;this._values={}}static{this.properties={...h.properties,_open:{state:!0},_values:{state:!0}}}forms(t){let e=["weight","length","temperature","solids","pumping"].filter(i=>t.trackers.includes(i));return t.medications.length&&e.push("medication"),e}value(t){return this._values[t]??""}setValue(t,e){this._values={...this._values,[t]:e}}async save(t,e){let i=!1;if(e in Q){let r=Number(this.value("value").replace(",","."));i=await this.log(e,`log_${e}`,{value:r},this.text(Q[e].what,{value:this.value("value")}))}else if(e==="solids"){let r=this.value("notes").trim();i=await this.log(e,"log_solids",r?{notes:r}:{},r||this.text("solids_entry"))}else if(e==="pumping"){let r=Number(this.value("amount")),o=this.value("side");i=await this.log(e,"log_pumping",{amount:r,...o?{side:o}:{}},this.text("pumping_of",{amount:r}))}else{let r=this.value("medication")||t.medications[0]?.name;i=await this.log(e,"log_medication",{medication:r},r)}i&&(this._open=null,this._values={})}renderBody(t){let e=this.forms(t);return a`
      <div class="row" style="--columns: 2">
        ${e.map(i=>a`<button
            class="big ${this._open===i?"active":""}"
            aria-expanded=${this._open===i?"true":"false"}
            @click=${()=>{this._open=this._open===i?null:i,this._values={}}}
          >
            ${this.text(i)}
          </button>`)}
      </div>
      ${this._open?this.renderForm(t,this._open):u}
    `}renderForm(t,e){let i=(o,c,l={})=>a`<label class="field">
        <span>${this.text(c)}${l.unit?` (${l.unit})`:""}</span>
        <input
          name=${o}
          type=${l.type??"text"}
          inputmode=${l.inputmode??"text"}
          step=${l.step??"any"}
          .value=${this.value(o)}
          @input=${d=>this.setValue(o,d.target.value)}
        />
      </label>`,r;if(e in Q){let{unit:o,step:c}=Q[e];r=i("value","value",{type:"number",inputmode:"decimal",step:c,unit:o})}else e==="solids"?r=i("notes","notes"):e==="pumping"?r=a`${i("amount","amount",{type:"number",inputmode:"numeric",step:"1",unit:"ml"})}
        <label class="field">
          <span>${this.text("side")}</span>
          <select
            name="side"
            @change=${o=>this.setValue("side",o.target.value)}
          >
            <option value="">${this.text("side_none")}</option>
            <option value="left">${this.text("left")}</option>
            <option value="right">${this.text("right")}</option>
            <option value="both">${this.text("side_both")}</option>
          </select>
        </label>`:r=a`<label class="field">
        <span>${this.text("medication")}</span>
        <select
          name="medication"
          @change=${o=>this.setValue("medication",o.target.value)}
        >
          ${t.medications.map(o=>a`<option value=${o.name}>${o.name}</option>`)}
        </select>
      </label>`;return a`<form
      class="form"
      @submit=${o=>{o.preventDefault(),this.save(t,e)}}
    >
      ${r}
      <div class="choices">
        <button class="small selected" type="submit">${this.text("save")}</button>
        <button
          class="small"
          type="button"
          @click=${()=>{this._open=null,this._values={}}}
        >
          ${this.text("cancel")}
        </button>
      </div>
    </form>`}};var Y=class extends h{constructor(){super(...arguments);this.titleKey="medications";this.accent="var(--red-color, #f44336)"}due(t){let e=t.entities.due;return!!(e&&this.hass?.states[e]?.state==="on")}renderBody(t){let e=this._config?.show_all?t.medications:t.medications.filter(i=>this.due(i));return e.length?a`${e.map(i=>a`<div class="medication ${this.due(i)?"due":""}">
        <div class="what">
          ${this.due(i)?a`<div class="label">${this.text("due_now")}</div>`:""}
          <div class="name">
            ${i.name}${i.dose?a` · ${i.dose}`:""}
          </div>
        </div>
        <button
          class="big given"
          @click=${()=>this.log(`med_${i.id}`,"log_medication",{medication:i.name},i.name)}
        >
          ${this.text("given")}
        </button>
      </div>`)}`:a`<p class="hint">${this.text("nothing_due")}</p>`}};var ce=24*3600*1e3,de=15,Z=class extends h{constructor(){super(...arguments);this.titleKey="recent";this.logs=!1;this._events=null;this._signature=""}static{this.properties={...h.properties,_events:{state:!0}}}signature(t){return Object.entries(t.entities).filter(([e])=>e.endsWith("_last")||e==="last_feed").map(([,e])=>this.hass?.states[e]?.last_changed??"").concat(t.medications.map(e=>this.hass?.states[e.entities.last_dose]?.last_changed??"")).join("|")}updated(t){super.updated(t);let e=this.baby;if(!e)return;let i=`${e.device_id}|${this.signature(e)}`;i!==this._signature&&(this._signature=i,this.refresh(e))}async refresh(t){let e=new Date(Date.now()+6e4),i=new Date(e.getTime()-ce-6e4);try{let o=(await this.call("baby_calendar","list_events",{device_id:t.device_id,start:i.toISOString(),end:e.toISOString()},!0))?.events??[];this._events=[...o].sort((c,l)=>c.time<l.time?1:-1).slice(0,de)}catch(r){this.showError(r)}}describe(t){let e=i=>String(Math.round(Number(i)*10)/10);switch(t.tracker){case"diaper":{let i=String(t.content),r=this.text(`diaper_${i}`);return t.stool?`${r} (${this.text(`stool_${t.stool}`).toLowerCase()})`:r}case"bottle":return this.text("bottle_of",{amount:e(t.amount)});case"breastfeeding":{let i=t.side?this.text(t.side).toLowerCase():"",r=this.text("feed_side",{side:i}).trim();return t.in_progress?`${r} \xB7 ${this.text("running")}`:`${r} \xB7 ${f(Number(t.duration??0))}`}case"sleep":return t.in_progress?`${this.text("sleep_entry")} \xB7 ${this.text("running")}`:`${this.text("sleep_entry")} \xB7 ${f(Number(t.duration??0))}`;case"weight":case"length":case"temperature":return this.text(`${t.tracker}_of`,{value:e(t.value)});case"pumping":return this.text("pumping_of",{amount:e(t.amount)});case"solids":return t.notes?`${this.text("solids_entry")} \xB7 ${t.notes}`:this.text("solids_entry");case"medication":return String(t.medication??"");default:return t.tracker}}renderBody(){return this._events===null?a``:this._events.length?a`<ul class="list">
      ${this._events.map(t=>a`<li>
          <span>${this.describe(t)}</span>
          <span class="when">${T(new Date(t.time),this.language)}</span>
        </li>`)}
    </ul>`:a`<p class="hint">${this.text("no_entries")}</p>`}};var tt=class extends h{constructor(){super(...arguments);this.tracker="sleep";this.titleKey="sleep";this.accent="var(--deep-purple-color, #673ab7)"}asleepSince(t){let e=this.entity(t,"sleep_timer");return e?.state==="on"&&e.attributes.started_at?new Date(e.attributes.started_at):null}tickMs(){let t=this.baby;return t&&this.asleepSince(t)?1e3:super.tickMs()}renderBody(t){let e=this.asleepSince(t);if(!e)return a`<button
        class="big"
        @click=${()=>this.log("sleep_start","start_sleep",{},this.text("sleep_entry"))}
      >
        ${this.text("fell_asleep")}
      </button>`;let i=(this._now-e.getTime())/1e3;return a`
      <button
        class="big active"
        @click=${()=>this.log("sleep_stop","stop_sleep",{},this.text("sleep_entry"))}
      >
        <span class="stack">
          <span>${this.text("woke_up")}</span>
          <span class="time">${j(i)}</span>
        </span>
      </button>
      <p class="hint">
        ${this.text("asleep_since",{time:T(e,this.language)})}
      </p>
    `}};var et=class extends h{constructor(){super(...arguments);this.titleKey="summary";this.logs=!1}tickMs(){return 3e4}since(t){if(!t||t==="unknown"||t==="unavailable")return this.text("never");let e=(this._now-new Date(t).getTime())/1e3;return this.text("ago",{duration:f(e)})}renderBody(t){let e=[],i=this.entity(t,"last_feed");i&&e.push(this.fact("ate",this.since(i.state)));let r=this.entity(t,"diaper_last");r&&e.push(this.fact("diaper",this.since(r.state)));let o=this.entity(t,"sleep_timer");if(o?.state==="on"&&o.attributes.started_at){let c=(this._now-new Date(o.attributes.started_at).getTime())/1e3;e.push(this.fact("asleep",f(c)))}else{let c=this.entity(t,"awake_since");c&&e.push(this.fact("awake",this.since(c.state)))}return a`<div class="facts" style="--columns: ${e.length||1}">${e}</div>`}fact(t,e){return a`<div class="fact">
      <div class="label">${this.text(t)}</div>
      <div class="value">${e}</div>
    </div>`}};var st=class extends h{constructor(){super(...arguments);this.titleKey="today";this.logs=!1}number(t,e){let i=this.entity(t,e)?.state,r=Number(i);return i===void 0||!Number.isFinite(r)?null:r}totals(t){let e=o=>this.number(t,o),i=o=>String(Math.round(o??0)),r=[];return e("diaper_changes_today")!==null&&r.push({label:"diaper_changes",value:i(e("diaper_changes_today")),detail:this.text("wet_dirty",{wet:i(e("diaper_wet_today")),dirty:i(e("diaper_dirty_today"))})}),e("bottle_count_today")!==null&&r.push({label:"bottles",value:i(e("bottle_count_today")),detail:`${i(e("bottle_ml_today"))} ml`}),e("breastfeeding_feeds_today")!==null&&r.push({label:"feeds",value:i(e("breastfeeding_feeds_today")),detail:f((e("breastfeeding_duration_today")??0)*60)}),e("sleep_duration_today")!==null&&r.push({label:"sleeps",value:f((e("sleep_duration_today")??0)*60),detail:`${i(e("sleep_count_today"))}\xD7`}),e("solids_count_today")!==null&&r.push({label:"solids",value:i(e("solids_count_today"))}),e("pumping_count_today")!==null&&r.push({label:"pumping",value:i(e("pumping_count_today")),detail:`${i(e("pumping_ml_today"))} ml`}),r}renderBody(t){return a`<div class="facts" style="--columns: 2">
      ${this.totals(t).map(e=>a`<div class="fact">
          <div class="label">${this.text(e.label)}</div>
          <div class="value">${e.value}</div>
          ${e.detail?a`<div class="detail">${e.detail}</div>`:""}
        </div>`)}
    </div>`}};var it=class extends y{constructor(){super(...arguments);this._babies=[]}static{this.properties={hass:{attribute:!1},_config:{state:!0},_babies:{state:!0}}}setConfig(t){this._config=t}connectedCallback(){super.connectedCallback(),this._watch()}disconnectedCallback(){super.disconnectedCallback(),this._stop?.(),this._stop=void 0}updated(){this._watch()}_watch(){this._stop||!this.hass||!this.isConnected||(this._stop=V(this.hass.connection,t=>{this._babies=t}))}_change(t){let e={...this._config,...t};this._config=e,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:e},bubbles:!0,composed:!0}))}render(){let t=F(this.hass?.locale?.language??this.hass?.language),e=this._config?.type==="custom:baby-calendar-medication-card";return a`
      <label>
        <span>${g(t,"baby")}</span>
        <select
          @change=${i=>this._change({baby:i.target.value})}
        >
          <option value="" ?selected=${!this._config?.baby}>—</option>
          ${this._babies.map(i=>a`<option value=${i.device_id} ?selected=${i.device_id===this._config?.baby}>
                ${i.name}
              </option>`)}
        </select>
      </label>
      ${e?a`<label class="check">
            <input
              type="checkbox"
              .checked=${!!this._config?.show_all}
              @change=${i=>this._change({show_all:i.target.checked})}
            />
            <span>${g(t,"show_all")}</span>
          </label>`:""}
    `}static{this.styles=M`
    :host {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    label {
      display: flex;
      flex-direction: column;
      gap: 4px;
      color: var(--primary-text-color);
    }
    label.check {
      flex-direction: row;
      align-items: center;
    }
    select {
      min-height: 44px;
      font: inherit;
      color: var(--primary-text-color);
      background: var(--card-background-color, transparent);
      border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
      border-radius: 8px;
      padding: 0 8px;
    }
  `}};var pe=[["baby-calendar-diaper-card",J,"Baby Calendar: diapers","Wet, dirty or both, and the stool type."],["baby-calendar-bottle-card",q,"Baby Calendar: bottle","A bottle with its amount and content."],["baby-calendar-breastfeeding-card",G,"Baby Calendar: breastfeeding","Left and right, and the last feed."],["baby-calendar-sleep-card",tt,"Baby Calendar: sleep","Fell asleep and woke up."],["baby-calendar-medication-card",Y,"Baby Calendar: medications","Doses due, with Given."],["baby-calendar-summary-card",et,"Baby Calendar: summary","Since the last feed, diaper and sleep."],["baby-calendar-today-card",st,"Baby Calendar: today","The day's totals."],["baby-calendar-entry-card",X,"Baby Calendar: other entries","Weight, length, temperature, solids, pumping, a dose."],["baby-calendar-recent-card",Z,"Baby Calendar: recent entries","The latest entries."]];customElements.get("baby-calendar-card-editor")||customElements.define("baby-calendar-card-editor",it);window.customCards=window.customCards??[];for(let[n,s,t,e]of pe)customElements.get(n)||(customElements.define(n,s),window.customCards.push({type:n,name:t,description:e,preview:!1}));export{pe as CARDS};
