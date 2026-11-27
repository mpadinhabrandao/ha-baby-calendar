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
var U=globalThis,K=U.ShadowRoot&&(U.ShadyCSS===void 0||U.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,rt=Symbol(),_t=new WeakMap,B=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==rt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(K&&e===void 0){let s=t!==void 0&&t.length===1;s&&(e=_t.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&_t.set(t,e))}return e}toString(){return this.cssText}},yt=n=>new B(typeof n=="string"?n:n+"",void 0,rt),M=(n,...e)=>{let t=n.length===1?n[0]:e.reduce((s,i,r)=>s+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+n[r+1],n[0]);return new B(t,n,rt)},vt=(n,e)=>{if(K)n.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let s=document.createElement("style"),i=U.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=t.cssText,n.appendChild(s)}},nt=K?n=>n:n=>n instanceof CSSStyleSheet?(e=>{let t="";for(let s of e.cssRules)t+=s.cssText;return yt(t)})(n):n;var{is:Ft,defineProperty:jt,getOwnPropertyDescriptor:Wt,getOwnPropertyNames:Vt,getOwnPropertySymbols:qt,getPrototypeOf:Gt}=Object,z=globalThis,xt=z.trustedTypes,Jt=xt?xt.emptyScript:"",Qt=z.reactiveElementPolyfillSupport,D=(n,e)=>n,ot={toAttribute(n,e){switch(e){case Boolean:n=n?Jt:null;break;case Object:case Array:n=n==null?n:JSON.stringify(n)}return n},fromAttribute(n,e){let t=n;switch(e){case Boolean:t=n!==null;break;case Number:t=n===null?null:Number(n);break;case Object:case Array:try{t=JSON.parse(n)}catch{t=null}}return t}},wt=(n,e)=>!Ft(n,e),$t={attribute:!0,type:String,converter:ot,reflect:!1,useDefault:!1,hasChanged:wt};Symbol.metadata??=Symbol("metadata"),z.litPropertyMetadata??=new WeakMap;var v=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=$t){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(e,s,t);i!==void 0&&jt(this.prototype,e,i)}}static getPropertyDescriptor(e,t,s){let{get:i,set:r}=Wt(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:i,set(o){let l=i?.call(this);r?.call(this,o),this.requestUpdate(e,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??$t}static _$Ei(){if(this.hasOwnProperty(D("elementProperties")))return;let e=Gt(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(D("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(D("properties"))){let t=this.properties,s=[...Vt(t),...qt(t)];for(let i of s)this.createProperty(i,t[i])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[s,i]of t)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[t,s]of this.elementProperties){let i=this._$Eu(t,s);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let s=new Set(e.flat(1/0).reverse());for(let i of s)t.unshift(nt(i))}else e!==void 0&&t.push(nt(e));return t}static _$Eu(e,t){let s=t.attribute;return s===!1?void 0:typeof s=="string"?s:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return vt(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){let s=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,s);if(i!==void 0&&s.reflect===!0){let r=(s.converter?.toAttribute!==void 0?s.converter:ot).toAttribute(t,s.type);this._$Em=e,r==null?this.removeAttribute(i):this.setAttribute(i,r),this._$Em=null}}_$AK(e,t){let s=this.constructor,i=s._$Eh.get(e);if(i!==void 0&&this._$Em!==i){let r=s.getPropertyOptions(i),o=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:ot;this._$Em=i;let l=o.fromAttribute(t,r.type);this[i]=l??this._$Ej?.get(i)??l,this._$Em=null}}requestUpdate(e,t,s,i=!1,r){if(e!==void 0){let o=this.constructor;if(i===!1&&(r=this[e]),s??=o.getPropertyOptions(e),!((s.hasChanged??wt)(r,t)||s.useDefault&&s.reflect&&r===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,s))))return;this.C(e,t,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:i,wrapped:r},o){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,o??t??this[e]),r!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),i===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,r]of this._$Ep)this[i]=r;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,r]of s){let{wrapped:o}=r,l=this[i];o!==!0||this._$AL.has(i)||l===void 0||this.C(i,void 0,r,l)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(t)):this._$EM()}catch(s){throw e=!1,this._$EM(),s}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};v.elementStyles=[],v.shadowRootOptions={mode:"open"},v[D("elementProperties")]=new Map,v[D("finalized")]=new Map,Qt?.({ReactiveElement:v}),(z.reactiveElementVersions??=[]).push("2.1.2");var ht=globalThis,At=n=>n,I=ht.trustedTypes,St=I?I.createPolicy("lit-html",{createHTML:n=>n}):void 0,Mt="$lit$",x=`lit$${Math.random().toFixed(9).slice(2)}$`,Dt="?"+x,Xt=`<${Dt}>`,E=document,P=()=>E.createComment(""),N=n=>n===null||typeof n!="object"&&typeof n!="function",mt=Array.isArray,Yt=n=>mt(n)||typeof n?.[Symbol.iterator]=="function",at=`[ 	
\f\r]`,R=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Et=/-->/g,Tt=/>/g,A=RegExp(`>|${at}(?:([^\\s"'>=/]+)(${at}*=${at}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),Ct=/'/g,kt=/"/g,Rt=/^(?:script|style|textarea|title)$/i,gt=n=>(e,...t)=>({_$litType$:n,strings:e,values:t}),a=gt(1),ge=gt(2),fe=gt(3),T=Symbol.for("lit-noChange"),u=Symbol.for("lit-nothing"),Bt=new WeakMap,S=E.createTreeWalker(E,129);function Pt(n,e){if(!mt(n)||!n.hasOwnProperty("raw"))throw Error("invalid template strings array");return St!==void 0?St.createHTML(e):e}var Zt=(n,e)=>{let t=n.length-1,s=[],i,r=e===2?"<svg>":e===3?"<math>":"",o=R;for(let l=0;l<t;l++){let c=n[l],d,m,p=-1,f=0;for(;f<c.length&&(o.lastIndex=f,m=o.exec(c),m!==null);)f=o.lastIndex,o===R?m[1]==="!--"?o=Et:m[1]!==void 0?o=Tt:m[2]!==void 0?(Rt.test(m[2])&&(i=RegExp("</"+m[2],"g")),o=A):m[3]!==void 0&&(o=A):o===A?m[0]===">"?(o=i??R,p=-1):m[1]===void 0?p=-2:(p=o.lastIndex-m[2].length,d=m[1],o=m[3]===void 0?A:m[3]==='"'?kt:Ct):o===kt||o===Ct?o=A:o===Et||o===Tt?o=R:(o=A,i=void 0);let _=o===A&&n[l+1].startsWith("/>")?" ":"";r+=o===R?c+Xt:p>=0?(s.push(d),c.slice(0,p)+Mt+c.slice(p)+x+_):c+x+(p===-2?l:_)}return[Pt(n,r+(n[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),s]},L=class n{constructor({strings:e,_$litType$:t},s){let i;this.parts=[];let r=0,o=0,l=e.length-1,c=this.parts,[d,m]=Zt(e,t);if(this.el=n.createElement(d,s),S.currentNode=this.el.content,t===2||t===3){let p=this.el.content.firstChild;p.replaceWith(...p.childNodes)}for(;(i=S.nextNode())!==null&&c.length<l;){if(i.nodeType===1){if(i.hasAttributes())for(let p of i.getAttributeNames())if(p.endsWith(Mt)){let f=m[o++],_=i.getAttribute(p).split(x),w=/([.?@])?(.*)/.exec(f);c.push({type:1,index:r,name:w[2],strings:_,ctor:w[1]==="."?ct:w[1]==="?"?dt:w[1]==="@"?pt:k}),i.removeAttribute(p)}else p.startsWith(x)&&(c.push({type:6,index:r}),i.removeAttribute(p));if(Rt.test(i.tagName)){let p=i.textContent.split(x),f=p.length-1;if(f>0){i.textContent=I?I.emptyScript:"";for(let _=0;_<f;_++)i.append(p[_],P()),S.nextNode(),c.push({type:2,index:++r});i.append(p[f],P())}}}else if(i.nodeType===8)if(i.data===Dt)c.push({type:2,index:r});else{let p=-1;for(;(p=i.data.indexOf(x,p+1))!==-1;)c.push({type:7,index:r}),p+=x.length-1}r++}}static createElement(e,t){let s=E.createElement("template");return s.innerHTML=e,s}};function C(n,e,t=n,s){if(e===T)return e;let i=s!==void 0?t._$Co?.[s]:t._$Cl,r=N(e)?void 0:e._$litDirective$;return i?.constructor!==r&&(i?._$AO?.(!1),r===void 0?i=void 0:(i=new r(n),i._$AT(n,t,s)),s!==void 0?(t._$Co??=[])[s]=i:t._$Cl=i),i!==void 0&&(e=C(n,i._$AS(n,e.values),i,s)),e}var lt=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:s}=this._$AD,i=(e?.creationScope??E).importNode(t,!0);S.currentNode=i;let r=S.nextNode(),o=0,l=0,c=s[0];for(;c!==void 0;){if(o===c.index){let d;c.type===2?d=new H(r,r.nextSibling,this,e):c.type===1?d=new c.ctor(r,c.name,c.strings,this,e):c.type===6&&(d=new ut(r,this,e)),this._$AV.push(d),c=s[++l]}o!==c?.index&&(r=S.nextNode(),o++)}return S.currentNode=E,i}p(e){let t=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}},H=class n{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,i){this.type=2,this._$AH=u,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=C(this,e,t),N(e)?e===u||e==null||e===""?(this._$AH!==u&&this._$AR(),this._$AH=u):e!==this._$AH&&e!==T&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Yt(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==u&&N(this._$AH)?this._$AA.nextSibling.data=e:this.T(E.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:s}=e,i=typeof s=="number"?this._$AC(e):(s.el===void 0&&(s.el=L.createElement(Pt(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(t);else{let r=new lt(i,this),o=r.u(this.options);r.p(t),this.T(o),this._$AH=r}}_$AC(e){let t=Bt.get(e.strings);return t===void 0&&Bt.set(e.strings,t=new L(e)),t}k(e){mt(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,s,i=0;for(let r of e)i===t.length?t.push(s=new n(this.O(P()),this.O(P()),this,this.options)):s=t[i],s._$AI(r),i++;i<t.length&&(this._$AR(s&&s._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let s=At(e).nextSibling;At(e).remove(),e=s}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},k=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,i,r){this.type=1,this._$AH=u,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=r,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=u}_$AI(e,t=this,s,i){let r=this.strings,o=!1;if(r===void 0)e=C(this,e,t,0),o=!N(e)||e!==this._$AH&&e!==T,o&&(this._$AH=e);else{let l=e,c,d;for(e=r[0],c=0;c<r.length-1;c++)d=C(this,l[s+c],t,c),d===T&&(d=this._$AH[c]),o||=!N(d)||d!==this._$AH[c],d===u?e=u:e!==u&&(e+=(d??"")+r[c+1]),this._$AH[c]=d}o&&!i&&this.j(e)}j(e){e===u?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},ct=class extends k{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===u?void 0:e}},dt=class extends k{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==u)}},pt=class extends k{constructor(e,t,s,i,r){super(e,t,s,i,r),this.type=5}_$AI(e,t=this){if((e=C(this,e,t,0)??u)===T)return;let s=this._$AH,i=e===u&&s!==u||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,r=e!==u&&(s===u||i);i&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},ut=class{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){C(this,e)}};var te=ht.litHtmlPolyfillSupport;te?.(L,H),(ht.litHtmlVersions??=[]).push("3.3.3");var Nt=(n,e,t)=>{let s=t?.renderBefore??e,i=s._$litPart$;if(i===void 0){let r=t?.renderBefore??null;s._$litPart$=i=new H(e.insertBefore(P(),r),r,void 0,t??{})}return i._$AI(n),i};var ft=globalThis,y=class extends v{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Nt(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return T}};y._$litElement$=!0,y.finalized=!0,ft.litElementHydrateSupport?.({LitElement:y});var ee=ft.litElementPolyfillSupport;ee?.({LitElement:y});(ft.litElementVersions??=[]).push("4.2.2");var se={diapers:"Diapers",wet:"Wet",dirty:"Dirty",both:"Both",stool_question:"Dirty diaper logged. What was it like?",stool_optional:`Optional: if you don't choose, it stays just "dirty".`,stool_normal:"Normal",stool_soft:"Soft",stool_hard:"Hard",stool_diarrhea:"Diarrhoea",bottle:"Bottle",log_bottle:"Log bottle",less:"Less 10 ml",more:"More 10 ml",formula:"Formula",breast_milk:"Breast milk",breastfeeding:"Breastfeeding",left:"Left",right:"Right",start_left:"Start left",start_right:"Start right",stop:"Stop",last_feed:"Last feed \xB7 {time} ({ago})",feeding_since:"Feeding since {time}",pause:"pause {duration}",total:"{duration} in total",running:"running",no_feed:"No feed yet",sleep:"Sleep",fell_asleep:"Fell asleep",woke_up:"Woke up",asleep_since:"Asleep since {time}",medications:"Medications",nothing_due:"No dose due",due_now:"Due",given:"Given",schedule_times:"At {times}",schedule_interval:"Every {duration}",schedule_none:"No schedule",and:"and",next_dose:"Next {when}",tomorrow:"tomorrow",due_since:"since {time}",summary:"Summary",ate:"Ate",diaper:"Diaper",awake:"Awake",asleep:"Asleep",ago:"{duration} ago",never:"\u2014",today:"Today",diaper_changes:"Diapers",wet_dirty:"{wet} wet \xB7 {dirty} dirty",bottles:"Bottles",feeds:"Breastfeeding",sleeps:"Sleep",solids:"Solids",pumping:"Pumping",other:"Other entries",weight:"Weight",length:"Length",temperature:"Temperature",medication:"Medication",amount:"Amount",side:"Side",side_none:"Not specified",side_both:"Both",notes:"Notes",value:"Value",save:"Save",cancel:"Cancel",now:"Now",when:"When",minutes_ago:"{minutes} min ago",logged:"Logged: {what} at {time}",undo:"Undo",undone:"Undone",not_recorded:"Not recorded: {error}",baby_not_found:"Baby not found. Choose a baby in the card's settings.",no_baby:"Choose a baby in the card's settings.",tracker_off:"{tracker} is not enabled for {baby}.",baby:"Baby",show_all:"Show every active medication",dose_of:"Dose of {name}",diaper_wet:"wet diaper",diaper_dirty:"dirty diaper",diaper_both:"wet and dirty diaper",bottle_of:"bottle {amount} ml",feed_side:"breastfeeding {side}",sleep_entry:"sleep",weight_of:"weight {value} g",length_of:"length {value} cm",temperature_of:"temperature {value} \xB0C",pumping_of:"pumping {amount} ml",solids_entry:"solids",medication_of:"{name}"},ie={diapers:"Fraldas",wet:"Xixi",dirty:"Coc\xF3",both:"Os dois",stool_question:"Coc\xF3 registado. Como era?",stool_optional:'Opcional: se n\xE3o escolheres, fica s\xF3 "coc\xF3".',stool_normal:"Normal",stool_soft:"Mole",stool_hard:"Duro",stool_diarrhea:"Diarreia",bottle:"Biber\xE3o",log_bottle:"Registar biber\xE3o",less:"Menos 10 ml",more:"Mais 10 ml",formula:"F\xF3rmula",breast_milk:"Leite materno",breastfeeding:"Mama",left:"Esquerda",right:"Direita",start_left:"Come\xE7ar esquerda",start_right:"Come\xE7ar direita",stop:"Parar",last_feed:"\xDAltima mamada \xB7 {time} ({ago})",feeding_since:"Mamada desde as {time}",pause:"pausa {duration}",total:"{duration} no total",running:"a decorrer",no_feed:"Ainda sem mamadas",sleep:"Sono",fell_asleep:"Adormeceu",woke_up:"Acordou",asleep_since:"A dormir desde as {time}",medications:"Medicamentos",nothing_due:"Nenhuma dose por dar",due_now:"Por dar",given:"Dado",schedule_times:"\xC0s {times}",schedule_interval:"A cada {duration}",schedule_none:"Sem hor\xE1rio",and:"e",next_dose:"Pr\xF3xima {when}",tomorrow:"amanh\xE3",due_since:"desde {time}",summary:"Resumo",ate:"Comeu",diaper:"Fralda",awake:"Acordado",asleep:"A dormir",ago:"h\xE1 {duration}",never:"\u2014",today:"Hoje",diaper_changes:"Fraldas",wet_dirty:"{wet} xixi \xB7 {dirty} coc\xF3",bottles:"Biber\xF5es",feeds:"Mama",sleeps:"Sono",solids:"S\xF3lidos",pumping:"Extra\xE7\xE3o",other:"Outros registos",weight:"Peso",length:"Comprimento",temperature:"Temperatura",medication:"Medicamento",amount:"Quantidade",side:"Lado",side_none:"N\xE3o indicado",side_both:"Ambos",notes:"Notas",value:"Valor",save:"Guardar",cancel:"Cancelar",now:"Agora",when:"Quando",minutes_ago:"H\xE1 {minutes} min",logged:"Registado: {what} \xE0s {time}",undo:"Desfazer",undone:"Desfeito",not_recorded:"N\xE3o ficou registado: {error}",baby_not_found:"Beb\xE9 n\xE3o encontrado. Escolhe um beb\xE9 nas defini\xE7\xF5es do card.",no_baby:"Escolhe um beb\xE9 nas defini\xE7\xF5es do card.",tracker_off:"{tracker} n\xE3o est\xE1 ligado para {baby}.",baby:"Beb\xE9",show_all:"Mostrar todos os medicamentos ativos",dose_of:"Dose de {name}",diaper_wet:"fralda com xixi",diaper_dirty:"fralda com coc\xF3",diaper_both:"fralda com xixi e coc\xF3",bottle_of:"biber\xE3o {amount} ml",feed_side:"mama {side}",sleep_entry:"sono",weight_of:"peso {value} g",length_of:"comprimento {value} cm",temperature_of:"temperatura {value} \xB0C",pumping_of:"extra\xE7\xE3o {amount} ml",solids_entry:"s\xF3lidos",medication_of:"{name}"};function F(n){return n?.toLowerCase().startsWith("pt")?"pt":"en"}function h(n,e,t={}){return(n==="pt"?ie:se)[e].replace(/\{(\w+)\}/g,(i,r)=>r in t?String(t[r]):`{${r}}`)}var O=60,j=3600;function b(n){let e=Math.max(0,Math.round(n/O));if(e<60)return`${e} min`;let t=Math.floor(e/60),s=e%60;return s?`${t} h ${s} min`:`${t} h`}function W(n){let e=Math.max(0,Math.floor(n)),t=Math.floor(e/j),s=Math.floor(e%j/O),i=e%O,r=o=>String(o).padStart(2,"0");return t?`${t}:${r(s)}:${r(i)}`:`${r(s)}:${r(i)}`}function $(n,e){return n.toLocaleTimeString(e==="pt"?"pt-PT":"en-GB",{hour:"2-digit",minute:"2-digit"})}function Lt(n,e){if(n.type==="times"&&n.times?.length){let t=n.times,s=t.length===1?t[0]:`${t.slice(0,-1).join(", ")} ${h(e,"and")} ${t[t.length-1]}`;return h(e,"schedule_times",{times:s})}return n.type==="interval"&&n.hours?h(e,"schedule_interval",{duration:b(n.hours*j)}):h(e,"schedule_none")}function Ht(n,e,t){let s=$(n,t),i=l=>new Date(l.getFullYear(),l.getMonth(),l.getDate()),r=Math.round((i(n).getTime()-i(e).getTime())/(24*j*1e3)),o=s;return r===1?o=`${h(t,"tomorrow")} ${s}`:r>1&&(o=`${n.toLocaleDateString(t==="pt"?"pt-PT":"en-GB",{weekday:"short"})} ${s}`),h(t,"next_dose",{when:o})}function re(n,e,t){return h(t,"ago",{duration:b((e.getTime()-n.getTime())/1e3)})}function ne(n,e){return n==="left"?h(e,"left"):n==="right"?h(e,"right"):h(e,"side_none")}function Ot(n,e,t){if(!n.length)return null;let s=new Date(n[0].start),i=n[n.length-1].end===null,r=[],o=0;n.forEach((d,m)=>{if(m>0){let _=new Date(n[m-1].end??n[m-1].start),w=(new Date(d.start).getTime()-_.getTime())/1e3;w>=O&&r.push(h(t,"pause",{duration:b(w)}))}let p=ne(d.side,t);if(d.end===null){r.push(`${p} ${h(t,"running")}`);return}let f=(new Date(d.end).getTime()-new Date(d.start).getTime())/1e3;o+=f,r.push(`${p} ${b(f)}`)}),n.length>1&&!i&&r.push(h(t,"total",{duration:b(o)}));let l=$(s,t);return{heading:i?h(t,"feeding_since",{time:l}):h(t,"last_feed",{time:l,ago:re(s,e,t)}),line:r.join(" \xB7 ")}}function Ut(n,e){if(n)return new Date(e.getTime()-n*O*1e3).toISOString()}var Kt=[0,5,10,15,20,30,45,60,90,120];var V=class{constructor(){this.last=new Map}allow(e,t=Date.now()){let s=this.last.get(e);return s!==void 0&&t-s<3e3?!1:(this.last.set(e,t),!0)}};var bt=new WeakMap;function q(n,e){let t=bt.get(n);if(!t){let i={babies:null,listeners:new Set,unsubscribe:null};i.unsubscribe=n.subscribeMessage(r=>{i.babies=r.babies,i.listeners.forEach(o=>o(r.babies))},{type:"baby_calendar/subscribe_babies"}),bt.set(n,i),t=i}let s=t;return s.listeners.add(e),s.babies&&e(s.babies),()=>{s.listeners.delete(e),s.listeners.size||(bt.delete(n),s.unsubscribe?.then(i=>i()).catch(()=>{}))}}var oe=6e4,g=class extends y{constructor(){super(...arguments);this._babies=null;this._minutesAgo=0;this._undo=null;this._error=null;this._now=Date.now();this._guard=new V;this.tracker=null;this.logs=!0;this.accent="var(--primary-color)";this._timerMs=null}static{this.properties={hass:{attribute:!1},_config:{state:!0},_babies:{state:!0},_minutesAgo:{state:!0},_undo:{state:!0},_error:{state:!0},_now:{state:!0}}}setConfig(t){this._config=t}getCardSize(){return 3}getGridOptions(){return{columns:12,min_columns:6}}static getConfigElement(){return document.createElement("baby-calendar-card-editor")}static getStubConfig(){return{baby:""}}get language(){return F(this.hass?.locale?.language??this.hass?.language)}text(t,s){return h(this.language,t,s)}get baby(){return this._babies?.find(t=>t.device_id===this._config?.baby)}entity(t,s){let i=t.entities[s];return i?this.hass?.states[i]:void 0}connectedCallback(){super.connectedCallback(),this._watch()}disconnectedCallback(){super.disconnectedCallback(),this._stopWatching?.(),this._stopWatching=void 0,this._setTimer(null)}updated(t){t.has("hass")&&this._watch(),this._setTimer(this.tickMs())}tickMs(){return this._undo?1e3:null}_setTimer(t){this._timer!==void 0&&t===this._timerMs||(this._timer!==void 0&&window.clearInterval(this._timer),this._timer=void 0,this._timerMs=t,!(t===null||!this.isConnected)&&(this._timer=window.setInterval(()=>{this._now=Date.now(),this._undo&&this._undo.expires<=this._now&&(this._undo=null)},t)))}_watch(){this._stopWatching||!this.hass||!this.isConnected||(this._stopWatching=q(this.hass.connection,t=>{this._babies=t}))}async call(t,s,i,r=!1){return(await this.hass.connection.sendMessagePromise({type:"call_service",domain:t,service:s,service_data:i,return_response:r}))?.response??null}async log(t,s,i,r){let o=this.baby;if(!o||!this._guard.allow(t))return!1;let l=Ut(this._minutesAgo,new Date);try{let c=await this.call("baby_calendar",s,{device_id:o.device_id,...i,...l?{time:l}:{}},!0);this._minutesAgo=0,this._error=null;let d=c?.event_id;return d&&this.showUndo(d,r,l?new Date(l):new Date),!0}catch(c){return this.showError(c),!1}}async act(t,s){if(!this._guard.allow(t))return!1;try{return await s(),this._error=null,!0}catch(i){return this.showError(i),!1}}showUndo(t,s,i){this._undo={eventId:t,text:this.text("logged",{what:s,time:$(i,this.language)}),expires:Date.now()+oe}}showError(t){let s=t?.message??(typeof t=="string"?t:String(t));this._error=this.text("not_recorded",{error:s})}async _undoLast(){let t=this._undo;if(t)try{await this.call("baby_calendar","delete_event",{event_id:t.eventId}),this._undo=null,this._error=null}catch(s){this.showError(s)}}render(){let t=this._message();return a`<ha-card style="--bc-accent: ${this.accent}">
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
        ${Kt.map(t=>a`<option value=${t} ?selected=${t===this._minutesAgo}>
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
    .medication .schedule {
      font-size: 13px;
      color: var(--secondary-text-color);
    }
    .medication .schedule span {
      white-space: nowrap;
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
  `}};var zt=10,It=["formula","breast_milk"],G=class extends g{constructor(){super(...arguments);this.tracker="bottle";this.titleKey="bottle";this.accent="var(--blue-color, #2196f3)";this._pending=null}static{this.properties={...g.properties,_pending:{state:!0}}}amount(t){let s=Number(this.entity(t,"bottle_amount")?.state),i=Number.isFinite(s)?s:0;return this._pending!==null&&this._pending===i&&(this._pending=null),this._pending??i}async setAmount(t,s){let i=this.entity(t,"bottle_amount"),r=Number(i?.attributes.max??500),o=Math.min(r,Math.max(0,s));this._pending=o;try{await this.call("number","set_value",{entity_id:t.entities.bottle_amount,value:o}),this._error=null}catch(l){this._pending=null,this.showError(l)}}renderBody(t){let s=this.amount(t),i=this.entity(t,"bottle_content")?.state;return a`
      <div class="amount">
        <button
          class="big step"
          aria-label=${this.text("less")}
          @click=${()=>this.setAmount(t,s-zt)}
        >
          −
        </button>
        <div class="value" aria-live="polite">${s} ml</div>
        <button
          class="big step"
          aria-label=${this.text("more")}
          @click=${()=>this.setAmount(t,s+zt)}
        >
          +
        </button>
      </div>
      <div class="choices">
        ${It.map(r=>a`<button
            class="small ${i===r?"selected":""}"
            aria-pressed=${i===r?"true":"false"}
            @click=${()=>this.act(`bottle_content_${r}`,()=>this.call("select","select_option",{entity_id:t.entities.bottle_content,option:r}))}
          >
            ${this.text(r)}
          </button>`)}
      </div>
      <button
        class="big primary"
        @click=${()=>this.log("bottle","log_bottle",{amount:s,...i&&It.includes(i)?{content:i}:{}},this.text("bottle_of",{amount:s}))}
      >
        <ha-icon icon="mdi:baby-bottle-outline"></ha-icon>
        <span>${this.text("log_bottle")}</span>
      </button>
    `}};var ae=["left","right"],J=class extends g{constructor(){super(...arguments);this.tracker="breastfeeding";this.titleKey="breastfeeding";this.accent="var(--pink-color, #e91e63)"}running(t){let s=this.entity(t,"breastfeeding_timer");if(s?.state!=="on"||!s.attributes.started_at)return null;let i=this.entity(t,"breastfeeding_last");return{side:i?.attributes.in_progress?i.attributes.side??null:null,start:new Date(s.attributes.started_at)}}tickMs(){let t=this.baby;return t&&this.running(t)?1e3:super.tickMs()??3e4}async tap(t,s){let i=this.running(t),r=this.text("feed_side",{side:this.text(s).toLowerCase()});if(i&&i.side===s){await this.log(`stop_${s}`,"stop_breastfeeding",{},r);return}i&&!await this.act(`stop_${i.side}`,()=>this.call("baby_calendar","stop_breastfeeding",{device_id:t.device_id}))||await this.log(`start_${s}`,"start_breastfeeding",{side:s},r)}renderBody(t){let s=this.running(t),i=new Date(this._now),r=this.entity(t,"breastfeeding_last")?.attributes.feed??[],o=Ot(r,i,this.language);return a`
      <div class="row" style="--columns: 2">
        ${ae.map(l=>{let c=s?.side===l;return a`<button
            class="big ${c?"active":""}"
            @click=${()=>this.tap(t,l)}
          >
            ${c?a`<span class="stack">
                  <span>${this.text("stop")} · ${this.text(l).toLowerCase()}</span>
                  <span class="time"
                    >${W((i.getTime()-s.start.getTime())/1e3)}</span
                  >
                </span>`:this.text(`start_${l}`)}
          </button>`})}
      </div>
      <div class="fact">
        ${o?a`<div class="label">${o.heading}</div>
              <div class="line">${o.line}</div>`:a`<div class="label">${this.text("no_feed")}</div>`}
      </div>
    `}};var le=["wet","dirty","both"],ce=["normal","soft","hard","diarrhea"],Q=class extends g{constructor(){super(...arguments);this.tracker="diaper";this.titleKey="diapers";this.accent="var(--amber-color, #ffc107)"}renderBody(t){let s=this.entity(t,"stool_prompt")?.state==="on";return a`
      <div class="row">
        ${le.map(i=>a`<button
            class="big"
            @click=${()=>this.log(`diaper_${i}`,"log_diaper",{content:i},this.text(`diaper_${i}`))}
          >
            ${this.text(i)}
          </button>`)}
      </div>
      ${s?a`<div class="question" role="group" aria-label=${this.text("stool_question")}>
            <p class="ask">${this.text("stool_question")}</p>
            <div class="row" style="--columns: 2">
              ${ce.map(i=>a`<button
                  class="big"
                  @click=${()=>this.act(`stool_${i}`,()=>this.call("button","press",{entity_id:t.entities[`stool_${i}`]}))}
                >
                  ${this.text(`stool_${i}`)}
                </button>`)}
            </div>
            <p class="hint">${this.text("stool_optional")}</p>
          </div>`:""}
    `}};var X={weight:{unit:"g",step:"1",what:"weight_of"},length:{unit:"cm",step:"0.5",what:"length_of"},temperature:{unit:"\xB0C",step:"0.1",what:"temperature_of"}},Y=class extends g{constructor(){super(...arguments);this.titleKey="other";this.accent="var(--teal-color, #009688)";this._open=null;this._values={}}static{this.properties={...g.properties,_open:{state:!0},_values:{state:!0}}}forms(t){let s=["weight","length","temperature","solids","pumping"].filter(i=>t.trackers.includes(i));return t.medications.length&&s.push("medication"),s}value(t){return this._values[t]??""}setValue(t,s){this._values={...this._values,[t]:s}}async save(t,s){let i=!1;if(s in X){let r=Number(this.value("value").replace(",","."));i=await this.log(s,`log_${s}`,{value:r},this.text(X[s].what,{value:this.value("value")}))}else if(s==="solids"){let r=this.value("notes").trim();i=await this.log(s,"log_solids",r?{notes:r}:{},r||this.text("solids_entry"))}else if(s==="pumping"){let r=Number(this.value("amount")),o=this.value("side");i=await this.log(s,"log_pumping",{amount:r,...o?{side:o}:{}},this.text("pumping_of",{amount:r}))}else{let r=this.value("medication")||t.medications[0]?.name;i=await this.log(s,"log_medication",{medication:r},r)}i&&(this._open=null,this._values={})}renderBody(t){let s=this.forms(t);return a`
      <div class="row" style="--columns: 2">
        ${s.map(i=>a`<button
            class="big ${this._open===i?"active":""}"
            aria-expanded=${this._open===i?"true":"false"}
            @click=${()=>{this._open=this._open===i?null:i,this._values={}}}
          >
            ${this.text(i)}
          </button>`)}
      </div>
      ${this._open?this.renderForm(t,this._open):u}
    `}renderForm(t,s){let i=(o,l,c={})=>a`<label class="field">
        <span>${this.text(l)}${c.unit?` (${c.unit})`:""}</span>
        <input
          name=${o}
          type=${c.type??"text"}
          inputmode=${c.inputmode??"text"}
          step=${c.step??"any"}
          .value=${this.value(o)}
          @input=${d=>this.setValue(o,d.target.value)}
        />
      </label>`,r;if(s in X){let{unit:o,step:l}=X[s];r=i("value","value",{inputmode:"decimal",step:l,unit:o})}else s==="solids"?r=i("notes","notes"):s==="pumping"?r=a`${i("amount","amount",{type:"number",inputmode:"numeric",step:"1",unit:"ml"})}
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
      @submit=${o=>{o.preventDefault(),this.save(t,s)}}
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
    </form>`}};var Z=class extends g{constructor(){super(...arguments);this.titleKey="medications";this.accent="var(--red-color, #f44336)"}due(t){let s=t.entities.due;return!!(s&&this.hass?.states[s]?.state==="on")}nextDose(t){let s=t.entities.next_dose,i=s?this.hass?.states[s]?.state:void 0,r=i?new Date(i):null;return r&&!Number.isNaN(r.getTime())?r:null}dueLabel(t){let s=this.text("due_now");return t?`${s} \xB7 ${this.text("due_since",{time:$(t,this.language)})}`:s}scheduleLine(t,s,i){let r=Lt(t.schedule??{type:"none"},this.language);return s&&!i?a`<span>${r}</span> · <span>${Ht(s,new Date,this.language)}</span>`:a`<span>${r}</span>`}renderBody(t){let s=this._config?.show_all?t.medications:t.medications.filter(i=>this.due(i));return s.length?a`${s.map(i=>{let r=this.due(i),o=this.nextDose(i);return a`<div class="medication ${r?"due":""}">
        <div class="what">
          ${r?a`<div class="label">${this.dueLabel(o)}</div>`:""}
          <div class="name">
            ${i.name}${i.dose?a` · ${i.dose}`:""}
          </div>
          <div class="schedule">${this.scheduleLine(i,o,r)}</div>
        </div>
        <button
          class="big given"
          @click=${()=>this.log(`med_${i.id}`,"log_medication",{medication:i.name},i.name)}
        >
          ${this.text("given")}
        </button>
      </div>`})}`:a`<p class="hint">${this.text("nothing_due")}</p>`}};var tt=class extends g{constructor(){super(...arguments);this.tracker="sleep";this.titleKey="sleep";this.accent="var(--deep-purple-color, #673ab7)"}asleepSince(t){let s=this.entity(t,"sleep_timer");return s?.state==="on"&&s.attributes.started_at?new Date(s.attributes.started_at):null}tickMs(){let t=this.baby;return t&&this.asleepSince(t)?1e3:super.tickMs()}renderBody(t){let s=this.asleepSince(t);if(!s)return a`<button
        class="big"
        @click=${()=>this.log("sleep_start","start_sleep",{},this.text("sleep_entry"))}
      >
        ${this.text("fell_asleep")}
      </button>`;let i=(this._now-s.getTime())/1e3;return a`
      <button
        class="big active"
        @click=${()=>this.log("sleep_stop","stop_sleep",{},this.text("sleep_entry"))}
      >
        <span class="stack">
          <span>${this.text("woke_up")}</span>
          <span class="time">${W(i)}</span>
        </span>
      </button>
      <p class="hint">
        ${this.text("asleep_since",{time:$(s,this.language)})}
      </p>
    `}};var et=class extends g{constructor(){super(...arguments);this.titleKey="summary";this.logs=!1}tickMs(){return 3e4}since(t){if(!t||t==="unknown"||t==="unavailable")return this.text("never");let s=(this._now-new Date(t).getTime())/1e3;return this.text("ago",{duration:b(s)})}renderBody(t){let s=[],i=this.entity(t,"last_feed");i&&s.push(this.fact("ate",this.since(i.state)));let r=this.entity(t,"diaper_last");r&&s.push(this.fact("diaper",this.since(r.state)));let o=this.entity(t,"sleep_timer");if(o?.state==="on"&&o.attributes.started_at){let l=(this._now-new Date(o.attributes.started_at).getTime())/1e3;s.push(this.fact("asleep",b(l)))}else{let l=this.entity(t,"awake_since");l&&s.push(this.fact("awake",this.since(l.state)))}return a`<div class="facts" style="--columns: ${s.length||1}">${s}</div>`}fact(t,s){return a`<div class="fact">
      <div class="label">${this.text(t)}</div>
      <div class="value">${s}</div>
    </div>`}};var st=class extends g{constructor(){super(...arguments);this.titleKey="today";this.logs=!1}number(t,s){let i=this.entity(t,s)?.state,r=Number(i);return i===void 0||!Number.isFinite(r)?null:r}totals(t){let s=o=>this.number(t,o),i=o=>String(Math.round(o??0)),r=[];return s("diaper_changes_today")!==null&&r.push({label:"diaper_changes",value:i(s("diaper_changes_today")),detail:this.text("wet_dirty",{wet:i(s("diaper_wet_today")),dirty:i(s("diaper_dirty_today"))})}),s("bottle_count_today")!==null&&r.push({label:"bottles",value:i(s("bottle_count_today")),detail:`${i(s("bottle_ml_today"))} ml`}),s("breastfeeding_feeds_today")!==null&&r.push({label:"feeds",value:i(s("breastfeeding_feeds_today")),detail:b((s("breastfeeding_duration_today")??0)*60)}),s("sleep_duration_today")!==null&&r.push({label:"sleeps",value:b((s("sleep_duration_today")??0)*60),detail:`${i(s("sleep_count_today"))}\xD7`}),s("solids_count_today")!==null&&r.push({label:"solids",value:i(s("solids_count_today"))}),s("pumping_count_today")!==null&&r.push({label:"pumping",value:i(s("pumping_count_today")),detail:`${i(s("pumping_ml_today"))} ml`}),r}renderBody(t){return a`<div class="facts" style="--columns: 2">
      ${this.totals(t).map(s=>a`<div class="fact">
          <div class="label">${this.text(s.label)}</div>
          <div class="value">${s.value}</div>
          ${s.detail?a`<div class="detail">${s.detail}</div>`:""}
        </div>`)}
    </div>`}};var it=class extends y{constructor(){super(...arguments);this._babies=[]}static{this.properties={hass:{attribute:!1},_config:{state:!0},_babies:{state:!0}}}setConfig(t){this._config=t}connectedCallback(){super.connectedCallback(),this._watch()}disconnectedCallback(){super.disconnectedCallback(),this._stop?.(),this._stop=void 0}updated(){this._watch()}_watch(){this._stop||!this.hass||!this.isConnected||(this._stop=q(this.hass.connection,t=>{this._babies=t}))}_change(t){let s={...this._config,...t};this._config=s,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:s},bubbles:!0,composed:!0}))}render(){let t=F(this.hass?.locale?.language??this.hass?.language),s=this._config?.type==="custom:baby-calendar-medication-card";return a`
      <label>
        <span>${h(t,"baby")}</span>
        <select
          @change=${i=>this._change({baby:i.target.value})}
        >
          <option value="" ?selected=${!this._config?.baby}>—</option>
          ${this._babies.map(i=>a`<option value=${i.device_id} ?selected=${i.device_id===this._config?.baby}>
                ${i.name}
              </option>`)}
        </select>
      </label>
      ${s?a`<label class="check">
            <input
              type="checkbox"
              .checked=${!!this._config?.show_all}
              @change=${i=>this._change({show_all:i.target.checked})}
            />
            <span>${h(t,"show_all")}</span>
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
  `}};var de=[["baby-calendar-diaper-card",Q,"Baby Calendar: diapers","Wet, dirty or both, and the stool type."],["baby-calendar-bottle-card",G,"Baby Calendar: bottle","A bottle with its amount and content."],["baby-calendar-breastfeeding-card",J,"Baby Calendar: breastfeeding","Left and right, and the last feed."],["baby-calendar-sleep-card",tt,"Baby Calendar: sleep","Fell asleep and woke up."],["baby-calendar-medication-card",Z,"Baby Calendar: medications","Doses due, with Given."],["baby-calendar-summary-card",et,"Baby Calendar: summary","Since the last feed, diaper and sleep."],["baby-calendar-today-card",st,"Baby Calendar: today","The day's totals."],["baby-calendar-entry-card",Y,"Baby Calendar: other entries","Weight, length, temperature, solids, pumping, a dose."]];customElements.get("baby-calendar-card-editor")||customElements.define("baby-calendar-card-editor",it);window.customCards=window.customCards??[];for(let[n,e,t,s]of de)customElements.get(n)||(customElements.define(n,e),window.customCards.push({type:n,name:t,description:s,preview:!1}));export{de as CARDS};
