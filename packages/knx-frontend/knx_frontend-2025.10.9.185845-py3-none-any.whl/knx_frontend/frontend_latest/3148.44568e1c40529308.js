export const __webpack_id__="3148";export const __webpack_ids__=["3148"];export const __webpack_modules__={26846:function(e,t,o){function i(e){return null==e||Array.isArray(e)?e:[e]}o.d(t,{e:()=>i})},87383:function(e,t,o){o.d(t,{g:()=>i});const i=e=>(t,o)=>e.includes(t,o)},10763:function(e,t,o){o.d(t,{x:()=>i});const i=(e,t)=>e&&e.config.components.includes(t)},81411:function(e,t,o){o.d(t,{a:()=>a});const i=(0,o(42109).n)((e=>{history.replaceState({scrollPosition:e},"")}),300);function a(e){return(t,o)=>{if("object"==typeof o)throw new Error("This decorator does not support this compilation type.");const a=t.connectedCallback;t.connectedCallback=function(){a.call(this);const t=this[o];t&&this.updateComplete.then((()=>{const o=this.renderRoot.querySelector(e);o&&setTimeout((()=>{o.scrollTop=t}),0)}))};const r=Object.getOwnPropertyDescriptor(t,o);let s;if(void 0===r)s={get(){return this[`__${String(o)}`]||history.state?.scrollPosition},set(e){i(e),this[`__${String(o)}`]=e},configurable:!0,enumerable:!0};else{const e=r.set;s={...r,set(t){i(t),this[`__${String(o)}`]=t,e?.call(this,t)}}}Object.defineProperty(t,o,s)}}},21431:function(e,t,o){o.d(t,{_:()=>r});var i=o(84922),a=o(64363);const r=(0,a.u$)(class extends a.WL{update(e,[t,o]){return this._element&&this._element.localName===t?(o&&Object.entries(o).forEach((([e,t])=>{this._element[e]=t})),i.c0):this.render(t,o)}render(e,t){return this._element=document.createElement(e),t&&Object.entries(t).forEach((([e,t])=>{this._element[e]=t})),this._element}constructor(e){if(super(e),e.type!==a.OA.CHILD)throw new Error("dynamicElementDirective can only be used in content bindings")}})},20674:function(e,t,o){o.d(t,{d:()=>i});const i=e=>e.stopPropagation()},22441:function(e,t,o){o.d(t,{A:()=>i});const i=e=>e.name?.trim()},41482:function(e,t,o){o.d(t,{X:()=>i});const i=e=>e.name?.trim()},88340:function(e,t,o){o.d(t,{L:()=>i});const i=(e,t)=>{const o=e.floor_id;return{area:e,floor:(o?t.floors[o]:void 0)||null}}},90963:function(e,t,o){o.d(t,{SH:()=>l,u1:()=>d,xL:()=>n});var i=o(65940);const a=(0,i.A)((e=>new Intl.Collator(e,{numeric:!0}))),r=(0,i.A)((e=>new Intl.Collator(e,{sensitivity:"accent",numeric:!0}))),s=(e,t)=>e<t?-1:e>t?1:0,n=(e,t,o=void 0)=>Intl?.Collator?a(o).compare(e,t):s(e,t),l=(e,t,o=void 0)=>Intl?.Collator?r(o).compare(e,t):s(e.toLowerCase(),t.toLowerCase()),d=e=>(t,o)=>{const i=e.indexOf(t),a=e.indexOf(o);return i===a?0:-1===i?1:-1===a?-1:i-a}},86098:function(e,t,o){o.d(t,{H:()=>b});const i=e=>e.normalize("NFD").replace(/[\u0300-\u036F]/g,"");var a=function(e){return e[e.Null=0]="Null",e[e.Backspace=8]="Backspace",e[e.Tab=9]="Tab",e[e.LineFeed=10]="LineFeed",e[e.CarriageReturn=13]="CarriageReturn",e[e.Space=32]="Space",e[e.ExclamationMark=33]="ExclamationMark",e[e.DoubleQuote=34]="DoubleQuote",e[e.Hash=35]="Hash",e[e.DollarSign=36]="DollarSign",e[e.PercentSign=37]="PercentSign",e[e.Ampersand=38]="Ampersand",e[e.SingleQuote=39]="SingleQuote",e[e.OpenParen=40]="OpenParen",e[e.CloseParen=41]="CloseParen",e[e.Asterisk=42]="Asterisk",e[e.Plus=43]="Plus",e[e.Comma=44]="Comma",e[e.Dash=45]="Dash",e[e.Period=46]="Period",e[e.Slash=47]="Slash",e[e.Digit0=48]="Digit0",e[e.Digit1=49]="Digit1",e[e.Digit2=50]="Digit2",e[e.Digit3=51]="Digit3",e[e.Digit4=52]="Digit4",e[e.Digit5=53]="Digit5",e[e.Digit6=54]="Digit6",e[e.Digit7=55]="Digit7",e[e.Digit8=56]="Digit8",e[e.Digit9=57]="Digit9",e[e.Colon=58]="Colon",e[e.Semicolon=59]="Semicolon",e[e.LessThan=60]="LessThan",e[e.Equals=61]="Equals",e[e.GreaterThan=62]="GreaterThan",e[e.QuestionMark=63]="QuestionMark",e[e.AtSign=64]="AtSign",e[e.A=65]="A",e[e.B=66]="B",e[e.C=67]="C",e[e.D=68]="D",e[e.E=69]="E",e[e.F=70]="F",e[e.G=71]="G",e[e.H=72]="H",e[e.I=73]="I",e[e.J=74]="J",e[e.K=75]="K",e[e.L=76]="L",e[e.M=77]="M",e[e.N=78]="N",e[e.O=79]="O",e[e.P=80]="P",e[e.Q=81]="Q",e[e.R=82]="R",e[e.S=83]="S",e[e.T=84]="T",e[e.U=85]="U",e[e.V=86]="V",e[e.W=87]="W",e[e.X=88]="X",e[e.Y=89]="Y",e[e.Z=90]="Z",e[e.OpenSquareBracket=91]="OpenSquareBracket",e[e.Backslash=92]="Backslash",e[e.CloseSquareBracket=93]="CloseSquareBracket",e[e.Caret=94]="Caret",e[e.Underline=95]="Underline",e[e.BackTick=96]="BackTick",e[e.a=97]="a",e[e.b=98]="b",e[e.c=99]="c",e[e.d=100]="d",e[e.e=101]="e",e[e.f=102]="f",e[e.g=103]="g",e[e.h=104]="h",e[e.i=105]="i",e[e.j=106]="j",e[e.k=107]="k",e[e.l=108]="l",e[e.m=109]="m",e[e.n=110]="n",e[e.o=111]="o",e[e.p=112]="p",e[e.q=113]="q",e[e.r=114]="r",e[e.s=115]="s",e[e.t=116]="t",e[e.u=117]="u",e[e.v=118]="v",e[e.w=119]="w",e[e.x=120]="x",e[e.y=121]="y",e[e.z=122]="z",e[e.OpenCurlyBrace=123]="OpenCurlyBrace",e[e.Pipe=124]="Pipe",e[e.CloseCurlyBrace=125]="CloseCurlyBrace",e[e.Tilde=126]="Tilde",e}({});const r=128;function s(){const e=[],t=[];for(let o=0;o<=r;o++)t[o]=0;for(let o=0;o<=r;o++)e.push(t.slice(0));return e}function n(e,t){if(t<0||t>=e.length)return!1;const o=e.codePointAt(t);switch(o){case a.Underline:case a.Dash:case a.Period:case a.Space:case a.Slash:case a.Backslash:case a.SingleQuote:case a.DoubleQuote:case a.Colon:case a.DollarSign:case a.LessThan:case a.OpenParen:case a.OpenSquareBracket:return!0;case void 0:return!1;default:return(i=o)>=127462&&i<=127487||8986===i||8987===i||9200===i||9203===i||i>=9728&&i<=10175||11088===i||11093===i||i>=127744&&i<=128591||i>=128640&&i<=128764||i>=128992&&i<=129003||i>=129280&&i<=129535||i>=129648&&i<=129750?!0:!1}var i}function l(e,t){if(t<0||t>=e.length)return!1;switch(e.charCodeAt(t)){case a.Space:case a.Tab:return!0;default:return!1}}function d(e,t,o){return t[e]!==o[e]}function c(e,t,o,i,a,s,n){const l=e.length>r?r:e.length,c=i.length>r?r:i.length;if(o>=l||s>=c||l-o>c-s)return;if(!function(e,t,o,i,a,r,s=!1){for(;t<o&&a<r;)e[t]===i[a]&&(s&&(p[t]=a),t+=1),a+=1;return t===o}(t,o,l,a,s,c,!0))return;let m;!function(e,t,o,i,a,r){let s=e-1,n=t-1;for(;s>=o&&n>=i;)a[s]===r[n]&&(u[s]=n,s--),n--}(l,c,o,s,t,a);let b,y,f=1;const x=[!1];for(m=1,b=o;b<l;m++,b++){const r=p[b],n=u[b],d=b+1<l?u[b+1]:c;for(f=r-s+1,y=r;y<d;f++,y++){let l=Number.MIN_SAFE_INTEGER,d=!1;y<=n&&(l=h(e,t,b,o,i,a,y,c,s,0===v[m-1][f-1],x));let p=0;l!==Number.MAX_SAFE_INTEGER&&(d=!0,p=l+_[m-1][f-1]);const u=y>r,$=u?_[m][f-1]+(v[m][f-1]>0?-5:0):0,w=y>r+1&&v[m][f-1]>0,k=w?_[m][f-2]+(v[m][f-2]>0?-5:0):0;if(w&&(!u||k>=$)&&(!d||k>=p))_[m][f]=k,g[m][f]=3,v[m][f]=0;else if(u&&(!d||$>=p))_[m][f]=$,g[m][f]=2,v[m][f]=0;else{if(!d)throw new Error("not possible");_[m][f]=p,g[m][f]=1,v[m][f]=v[m-1][f-1]+1}}}if(!x[0]&&!n)return;m--,f--;const $=[_[m][f],s];let w=0,k=0;for(;m>=1;){let e=f;do{const t=g[m][e];if(3===t)e-=2;else{if(2!==t)break;e-=1}}while(e>=1);w>1&&t[o+m-1]===a[s+f-1]&&!d(e+s-1,i,a)&&w+1>v[m][e]&&(e=f),e===f?w++:w=1,k||(k=e),m--,f=e-1,$.push(f)}c===l&&($[0]+=2);const M=k-l;return $[0]-=M,$}function h(e,t,o,i,a,r,s,c,h,p,u){if(t[o]!==r[s])return Number.MIN_SAFE_INTEGER;let v=1,_=!1;return s===o-i?v=e[o]===a[s]?7:5:!d(s,a,r)||0!==s&&d(s-1,a,r)?!n(r,s)||0!==s&&n(r,s-1)?(n(r,s-1)||l(r,s-1))&&(v=5,_=!0):v=5:(v=e[o]===a[s]?7:5,_=!0),v>1&&o===i&&(u[0]=!0),_||(_=d(s,a,r)||n(r,s-1)||l(r,s-1)),o===i?s>h&&(v-=_?3:5):v+=p?_?2:0:_?0:1,s+1===c&&(v-=_?3:5),v}const p=m(256),u=m(256),v=s(),_=s(),g=s();function m(e){const t=[];for(let o=0;o<=e;o++)t[o]=0;return t}const b=(e,t)=>t.map((t=>(t.score=((e,t)=>{let o=Number.NEGATIVE_INFINITY;for(const a of t.strings){const t=c(e,i(e.toLowerCase()),0,a,i(a.toLowerCase()),0,!0);if(!t)continue;const r=0===t[0]?1:t[0];r>o&&(o=r)}if(o!==Number.NEGATIVE_INFINITY)return o})(e,t),t))).filter((e=>void 0!==e.score)).sort((({score:e=0},{score:t=0})=>e>t?-1:e<t?1:0))},24802:function(e,t,o){o.d(t,{s:()=>i});const i=(e,t,o=!1)=>{let i;const a=(...a)=>{const r=o&&!i;clearTimeout(i),i=window.setTimeout((()=>{i=void 0,e(...a)}),t),r&&e(...a)};return a.cancel=()=>{clearTimeout(i)},a}},42109:function(e,t,o){o.d(t,{n:()=>i});const i=(e,t,o=!0,i=!0)=>{let a,r=0;const s=(...s)=>{const n=()=>{r=!1===o?0:Date.now(),a=void 0,e(...s)},l=Date.now();r||!1!==o||(r=l);const d=t-(l-r);d<=0||d>t?(a&&(clearTimeout(a),a=void 0),r=l,e(...s)):a||!1===i||(a=window.setTimeout(n,d))};return s.cancel=()=>{clearTimeout(a),a=void 0,r=0},s}},54820:function(e,t,o){var i=o(69868),a=o(71906),r=o(11991);class s extends a.Y{}s=(0,i.__decorate)([(0,r.EM)("ha-chip-set")],s)},54538:function(e,t,o){var i=o(69868),a=o(73142),r=o(65082),s=o(8998),n=o(49377),l=o(68336),d=o(84922),c=o(11991);class h extends a.R{}h.styles=[n.R,l.R,s.R,r.R,d.AH`
      :host {
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-sys-color-on-surface-variant: var(--primary-text-color);
        --md-sys-color-on-secondary-container: var(--primary-text-color);
        --md-input-chip-container-shape: 16px;
        --md-input-chip-outline-color: var(--outline-color);
        --md-input-chip-selected-container-color: rgba(
          var(--rgb-primary-text-color),
          0.15
        );
        --ha-input-chip-selected-container-opacity: 1;
        --md-input-chip-label-text-font: Roboto, sans-serif;
      }
      /** Set the size of mdc icons **/
      ::slotted([slot="icon"]) {
        display: flex;
        --mdc-icon-size: var(--md-input-chip-icon-size, 18px);
      }
      .selected::before {
        opacity: var(--ha-input-chip-selected-container-opacity);
      }
    `],h=(0,i.__decorate)([(0,c.EM)("ha-input-chip")],h)},44249:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991),s=o(65940),n=o(73120),l=o(22441),d=o(92830),c=o(41482),h=o(88340),p=o(18944),u=o(6041),v=o(47420),_=o(59526);o(36137),o(94966),o(93672),o(95635);const g="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",m="M20 2H4C2.9 2 2 2.9 2 4V20C2 21.11 2.9 22 4 22H20C21.11 22 22 21.11 22 20V4C22 2.9 21.11 2 20 2M4 6L6 4H10.9L4 10.9V6M4 13.7L13.7 4H18.6L4 18.6V13.7M20 18L18 20H13.1L20 13.1V18M20 10.3L10.3 20H5.4L20 5.4V10.3Z",b="___ADD_NEW___";class y extends a.WF{async open(){await this.updateComplete,await(this._picker?.open())}render(){const e=this.placeholder??this.hass.localize("ui.components.area-picker.area"),t=this._computeValueRenderer(this.hass.areas);return a.qy`
      <ha-generic-picker
        .hass=${this.hass}
        .autofocus=${this.autofocus}
        .label=${this.label}
        .helper=${this.helper}
        .notFoundLabel=${this.hass.localize("ui.components.area-picker.no_match")}
        .placeholder=${e}
        .value=${this.value}
        .getItems=${this._getItems}
        .getAdditionalItems=${this._getAdditionalItems}
        .valueRenderer=${t}
        @value-changed=${this._valueChanged}
      >
      </ha-generic-picker>
    `}_valueChanged(e){e.stopPropagation();const t=e.detail.value;if(t)if(t.startsWith(b)){this.hass.loadFragmentTranslation("config");const e=t.substring(13);(0,_.J)(this,{suggestedName:e,createEntry:async e=>{try{const t=await(0,p.L3)(this.hass,e);this._setValue(t.area_id)}catch(t){(0,v.K$)(this,{title:this.hass.localize("ui.components.area-picker.failed_create_area"),text:t.message})}}})}else this._setValue(t);else this._setValue(void 0)}_setValue(e){this.value=e,(0,n.r)(this,"value-changed",{value:e}),(0,n.r)(this,"change")}constructor(...e){super(...e),this.noAdd=!1,this.disabled=!1,this.required=!1,this._computeValueRenderer=(0,s.A)((e=>e=>{const t=this.hass.areas[e];if(!t)return a.qy`
            <ha-svg-icon slot="start" .path=${m}></ha-svg-icon>
            <span slot="headline">${t}</span>
          `;const{floor:o}=(0,h.L)(t,this.hass),i=t?(0,l.A)(t):void 0,r=o?(0,c.X)(o):void 0,s=t.icon;return a.qy`
          ${s?a.qy`<ha-icon slot="start" .icon=${s}></ha-icon>`:a.qy`<ha-svg-icon
                slot="start"
                .path=${m}
              ></ha-svg-icon>`}
          <span slot="headline">${i}</span>
          ${r?a.qy`<span slot="supporting-text">${r}</span>`:a.s6}
        `})),this._getAreas=(0,s.A)(((e,t,o,i,a,r,s,n,p)=>{let v,_,g={};const b=Object.values(e),y=Object.values(t),f=Object.values(o);(i||a||r||s||n)&&(g=(0,u.g2)(f),v=y,_=f.filter((e=>e.area_id)),i&&(v=v.filter((e=>{const t=g[e.id];return!(!t||!t.length)&&g[e.id].some((e=>i.includes((0,d.m)(e.entity_id))))})),_=_.filter((e=>i.includes((0,d.m)(e.entity_id))))),a&&(v=v.filter((e=>{const t=g[e.id];return!t||!t.length||f.every((e=>!a.includes((0,d.m)(e.entity_id))))})),_=_.filter((e=>!a.includes((0,d.m)(e.entity_id))))),r&&(v=v.filter((e=>{const t=g[e.id];return!(!t||!t.length)&&g[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&r.includes(t.attributes.device_class))}))})),_=_.filter((e=>{const t=this.hass.states[e.entity_id];return t.attributes.device_class&&r.includes(t.attributes.device_class)}))),s&&(v=v.filter((e=>s(e)))),n&&(v=v.filter((e=>{const t=g[e.id];return!(!t||!t.length)&&g[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&n(t)}))})),_=_.filter((e=>{const t=this.hass.states[e.entity_id];return!!t&&n(t)}))));let x,$=b;v&&(x=v.filter((e=>e.area_id)).map((e=>e.area_id))),_&&(x=(x??[]).concat(_.filter((e=>e.area_id)).map((e=>e.area_id)))),x&&($=$.filter((e=>x.includes(e.area_id)))),p&&($=$.filter((e=>!p.includes(e.area_id))));return $.map((e=>{const{floor:t}=(0,h.L)(e,this.hass),o=t?(0,c.X)(t):void 0,i=(0,l.A)(e);return{id:e.area_id,primary:i||e.area_id,secondary:o,icon:e.icon||void 0,icon_path:e.icon?void 0:m,sorting_label:i,search_labels:[i,o,e.area_id,...e.aliases].filter((e=>Boolean(e)))}}))})),this._getItems=()=>this._getAreas(this.hass.areas,this.hass.devices,this.hass.entities,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeAreas),this._allAreaNames=(0,s.A)((e=>Object.values(e).map((e=>(0,l.A)(e)?.toLowerCase())).filter(Boolean))),this._getAdditionalItems=e=>{if(this.noAdd)return[];const t=this._allAreaNames(this.hass.areas);return e&&!t.includes(e.toLowerCase())?[{id:b+e,primary:this.hass.localize("ui.components.area-picker.add_new_sugestion",{name:e}),icon_path:g}]:[{id:b,primary:this.hass.localize("ui.components.area-picker.add_new"),icon_path:g}]}}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)()],y.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],y.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],y.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)()],y.prototype,"placeholder",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"no-add"})],y.prototype,"noAdd",void 0),(0,i.__decorate)([(0,r.MZ)({type:Array,attribute:"include-domains"})],y.prototype,"includeDomains",void 0),(0,i.__decorate)([(0,r.MZ)({type:Array,attribute:"exclude-domains"})],y.prototype,"excludeDomains",void 0),(0,i.__decorate)([(0,r.MZ)({type:Array,attribute:"include-device-classes"})],y.prototype,"includeDeviceClasses",void 0),(0,i.__decorate)([(0,r.MZ)({type:Array,attribute:"exclude-areas"})],y.prototype,"excludeAreas",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],y.prototype,"deviceFilter",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],y.prototype,"entityFilter",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],y.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],y.prototype,"required",void 0),(0,i.__decorate)([(0,r.P)("ha-generic-picker")],y.prototype,"_picker",void 0),y=(0,i.__decorate)([(0,r.EM)("ha-area-picker")],y)},71978:function(e,t,o){var i=o(69868),a=o(29332),r=o(77485),s=o(84922),n=o(11991);class l extends a.L{}l.styles=[r.R,s.AH`
      :host {
        --mdc-theme-secondary: var(--primary-color);
      }
    `],l=(0,i.__decorate)([(0,n.EM)("ha-checkbox")],l)},36137:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991),s=o(98343);class n extends s.G{constructor(...e){super(...e),this.borderTop=!1}}n.styles=[...s.J,a.AH`
      :host {
        --md-list-item-one-line-container-height: 48px;
        --md-list-item-two-line-container-height: 64px;
      }
      :host([border-top]) md-item {
        border-top: 1px solid var(--divider-color);
      }
      [slot="start"] {
        --state-icon-color: var(--secondary-text-color);
      }
      [slot="headline"] {
        line-height: var(--ha-line-height-normal);
        font-size: var(--ha-font-size-m);
        white-space: nowrap;
      }
      [slot="supporting-text"] {
        line-height: var(--ha-line-height-normal);
        font-size: var(--ha-font-size-s);
        white-space: nowrap;
      }
      ::slotted(state-badge),
      ::slotted(img) {
        width: 32px;
        height: 32px;
      }
      ::slotted(.code) {
        font-family: var(--ha-font-family-code);
        font-size: var(--ha-font-size-xs);
      }
      ::slotted(.domain) {
        font-size: var(--ha-font-size-s);
        font-weight: var(--ha-font-weight-normal);
        line-height: var(--ha-line-height-normal);
        align-self: flex-end;
        max-width: 30%;
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
      }
    `],(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"border-top"})],n.prototype,"borderTop",void 0),n=(0,i.__decorate)([(0,r.EM)("ha-combo-box-item")],n)},26731:function(e,t,o){var i=o(69868),a=o(28786),r=(o(20551),o(67212)),s=o(84922),n=o(11991),l=o(13802),d=o(73120),c=(o(36137),o(11934));class h extends c.h{willUpdate(e){super.willUpdate(e),(e.has("value")||e.has("forceBlankValue"))&&this.forceBlankValue&&this.value&&(this.value="")}constructor(...e){super(...e),this.forceBlankValue=!1}}(0,i.__decorate)([(0,n.MZ)({type:Boolean,attribute:"force-blank-value"})],h.prototype,"forceBlankValue",void 0),h=(0,i.__decorate)([(0,n.EM)("ha-combo-box-textfield")],h);o(93672),o(20014);(0,r.SF)("vaadin-combo-box-item",s.AH`
    :host {
      padding: 0 !important;
    }
    :host([focused]:not([disabled])) {
      background-color: rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.12);
    }
    :host([selected]:not([disabled])) {
      background-color: transparent;
      color: var(--mdc-theme-primary);
      --mdc-ripple-color: var(--mdc-theme-primary);
      --mdc-theme-text-primary-on-background: var(--mdc-theme-primary);
    }
    :host([selected]:not([disabled])):before {
      background-color: var(--mdc-theme-primary);
      opacity: 0.12;
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    :host([selected][focused]:not([disabled])):before {
      opacity: 0.24;
    }
    :host(:hover:not([disabled])) {
      background-color: transparent;
    }
    [part="content"] {
      width: 100%;
    }
    [part="checkmark"] {
      display: none;
    }
  `);class p extends s.WF{async open(){await this.updateComplete,this._comboBox?.open()}async focus(){await this.updateComplete,await(this._inputElement?.updateComplete),this._inputElement?.focus()}disconnectedCallback(){super.disconnectedCallback(),this._overlayMutationObserver&&(this._overlayMutationObserver.disconnect(),this._overlayMutationObserver=void 0),this._bodyMutationObserver&&(this._bodyMutationObserver.disconnect(),this._bodyMutationObserver=void 0)}get selectedItem(){return this._comboBox.selectedItem}setInputValue(e){this._comboBox.value=e}setTextFieldValue(e){this._inputElement.value=e}render(){return s.qy`
      <!-- @ts-ignore Tag definition is not included in theme folder -->
      <vaadin-combo-box-light
        .itemValuePath=${this.itemValuePath}
        .itemIdPath=${this.itemIdPath}
        .itemLabelPath=${this.itemLabelPath}
        .items=${this.items}
        .value=${this.value||""}
        .filteredItems=${this.filteredItems}
        .dataProvider=${this.dataProvider}
        .allowCustomValue=${this.allowCustomValue}
        .disabled=${this.disabled}
        .required=${this.required}
        ${(0,a.d)(this.renderer||this._defaultRowRenderer)}
        @opened-changed=${this._openedChanged}
        @filter-changed=${this._filterChanged}
        @value-changed=${this._valueChanged}
        attr-for-value="value"
      >
        <ha-combo-box-textfield
          label=${(0,l.J)(this.label)}
          placeholder=${(0,l.J)(this.placeholder)}
          ?disabled=${this.disabled}
          ?required=${this.required}
          validationMessage=${(0,l.J)(this.validationMessage)}
          .errorMessage=${this.errorMessage}
          class="input"
          autocapitalize="none"
          autocomplete="off"
          .autocorrect=${!1}
          input-spellcheck="false"
          .suffix=${s.qy`<div
            style="width: 28px;"
            role="none presentation"
          ></div>`}
          .icon=${this.icon}
          .invalid=${this.invalid}
          .forceBlankValue=${this._forceBlankValue}
        >
          <slot name="icon" slot="leadingIcon"></slot>
        </ha-combo-box-textfield>
        ${this.value&&!this.hideClearIcon?s.qy`<ha-svg-icon
              role="button"
              tabindex="-1"
              aria-label=${(0,l.J)(this.hass?.localize("ui.common.clear"))}
              class=${"clear-button "+(this.label?"":"no-label")}
              .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
              ?disabled=${this.disabled}
              @click=${this._clearValue}
            ></ha-svg-icon>`:""}
        <ha-svg-icon
          role="button"
          tabindex="-1"
          aria-label=${(0,l.J)(this.label)}
          aria-expanded=${this.opened?"true":"false"}
          class=${"toggle-button "+(this.label?"":"no-label")}
          .path=${this.opened?"M7,15L12,10L17,15H7Z":"M7,10L12,15L17,10H7Z"}
          ?disabled=${this.disabled}
          @click=${this._toggleOpen}
        ></ha-svg-icon>
      </vaadin-combo-box-light>
      ${this._renderHelper()}
    `}_renderHelper(){return this.helper?s.qy`<ha-input-helper-text .disabled=${this.disabled}
          >${this.helper}</ha-input-helper-text
        >`:""}_clearValue(e){e.stopPropagation(),(0,d.r)(this,"value-changed",{value:void 0})}_toggleOpen(e){this.opened?(this._comboBox?.close(),e.stopPropagation()):this._comboBox?.inputElement.focus()}_openedChanged(e){e.stopPropagation();const t=e.detail.value;if(setTimeout((()=>{this.opened=t,(0,d.r)(this,"opened-changed",{value:e.detail.value})}),0),this.clearInitialValue&&(this.setTextFieldValue(""),t?setTimeout((()=>{this._forceBlankValue=!1}),100):this._forceBlankValue=!0),t){const e=document.querySelector("vaadin-combo-box-overlay");e&&this._removeInert(e),this._observeBody()}else this._bodyMutationObserver?.disconnect(),this._bodyMutationObserver=void 0}_observeBody(){"MutationObserver"in window&&!this._bodyMutationObserver&&(this._bodyMutationObserver=new MutationObserver((e=>{e.forEach((e=>{e.addedNodes.forEach((e=>{"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&this._removeInert(e)})),e.removedNodes.forEach((e=>{"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&(this._overlayMutationObserver?.disconnect(),this._overlayMutationObserver=void 0)}))}))})),this._bodyMutationObserver.observe(document.body,{childList:!0}))}_removeInert(e){if(e.inert)return e.inert=!1,this._overlayMutationObserver?.disconnect(),void(this._overlayMutationObserver=void 0);"MutationObserver"in window&&!this._overlayMutationObserver&&(this._overlayMutationObserver=new MutationObserver((e=>{e.forEach((e=>{if("inert"===e.attributeName){const t=e.target;t.inert&&(this._overlayMutationObserver?.disconnect(),this._overlayMutationObserver=void 0,t.inert=!1)}}))})),this._overlayMutationObserver.observe(e,{attributes:!0}))}_filterChanged(e){e.stopPropagation(),(0,d.r)(this,"filter-changed",{value:e.detail.value})}_valueChanged(e){if(e.stopPropagation(),this.allowCustomValue||(this._comboBox._closeOnBlurIsPrevented=!0),!this.opened)return;const t=e.detail.value;t!==this.value&&(0,d.r)(this,"value-changed",{value:t||void 0})}constructor(...e){super(...e),this.invalid=!1,this.icon=!1,this.allowCustomValue=!1,this.itemValuePath="value",this.itemLabelPath="label",this.disabled=!1,this.required=!1,this.opened=!1,this.hideClearIcon=!1,this.clearInitialValue=!1,this._forceBlankValue=!1,this._defaultRowRenderer=e=>s.qy`
    <ha-combo-box-item type="button">
      ${this.itemLabelPath?e[this.itemLabelPath]:e}
    </ha-combo-box-item>
  `}}p.styles=s.AH`
    :host {
      display: block;
      width: 100%;
    }
    vaadin-combo-box-light {
      position: relative;
    }
    ha-combo-box-textfield {
      width: 100%;
    }
    ha-combo-box-textfield > ha-icon-button {
      --mdc-icon-button-size: 24px;
      padding: 2px;
      color: var(--secondary-text-color);
    }
    ha-svg-icon {
      color: var(--input-dropdown-icon-color);
      position: absolute;
      cursor: pointer;
    }
    .toggle-button {
      right: 12px;
      top: -10px;
      inset-inline-start: initial;
      inset-inline-end: 12px;
      direction: var(--direction);
    }
    :host([opened]) .toggle-button {
      color: var(--primary-color);
    }
    .toggle-button[disabled],
    .clear-button[disabled] {
      color: var(--disabled-text-color);
      pointer-events: none;
    }
    .toggle-button.no-label {
      top: -3px;
    }
    .clear-button {
      --mdc-icon-size: 20px;
      top: -7px;
      right: 36px;
      inset-inline-start: initial;
      inset-inline-end: 36px;
      direction: var(--direction);
    }
    .clear-button.no-label {
      top: 0;
    }
    ha-input-helper-text {
      margin-top: 4px;
    }
  `,(0,i.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,i.__decorate)([(0,n.MZ)()],p.prototype,"label",void 0),(0,i.__decorate)([(0,n.MZ)()],p.prototype,"value",void 0),(0,i.__decorate)([(0,n.MZ)()],p.prototype,"placeholder",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"validationMessage",void 0),(0,i.__decorate)([(0,n.MZ)()],p.prototype,"helper",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"error-message"})],p.prototype,"errorMessage",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],p.prototype,"invalid",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],p.prototype,"icon",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"items",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"filteredItems",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"dataProvider",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"allow-custom-value",type:Boolean})],p.prototype,"allowCustomValue",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"item-value-path"})],p.prototype,"itemValuePath",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"item-label-path"})],p.prototype,"itemLabelPath",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"item-id-path"})],p.prototype,"itemIdPath",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"renderer",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],p.prototype,"opened",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean,attribute:"hide-clear-icon"})],p.prototype,"hideClearIcon",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean,attribute:"clear-initial-value"})],p.prototype,"clearInitialValue",void 0),(0,i.__decorate)([(0,n.P)("vaadin-combo-box-light",!0)],p.prototype,"_comboBox",void 0),(0,i.__decorate)([(0,n.P)("ha-combo-box-textfield",!0)],p.prototype,"_inputElement",void 0),(0,i.__decorate)([(0,n.wk)({type:Boolean})],p.prototype,"_forceBlankValue",void 0),p=(0,i.__decorate)([(0,n.EM)("ha-combo-box")],p)},72659:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991),s=o(75907),n=o(13802),l=o(33055),d=o(73120);o(81164),o(95635);class c extends a.WF{_handleFocus(e){if(!this.disabled&&this.options&&e.target===e.currentTarget){const e=null!=this.value?this.options.findIndex((e=>e.value===this.value)):-1,t=-1!==e?e:0;this._focusOption(t)}}_focusOption(e){this._activeIndex=e,this.requestUpdate(),this.updateComplete.then((()=>{const t=this.shadowRoot?.querySelector(`#option-${this.options[e].value}`);t?.focus()}))}_handleBlur(e){this.contains(e.relatedTarget)||(this._activeIndex=void 0)}_handleKeydown(e){if(!this.options||this.disabled)return;let t=this._activeIndex??0;switch(e.key){case" ":case"Enter":if(null!=this._activeIndex){const e=this.options[this._activeIndex].value;this.value=e,(0,d.r)(this,"value-changed",{value:e})}break;case"ArrowUp":case"ArrowLeft":t=t<=0?this.options.length-1:t-1,this._focusOption(t);break;case"ArrowDown":case"ArrowRight":t=(t+1)%this.options.length,this._focusOption(t);break;default:return}e.preventDefault()}_handleOptionClick(e){if(this.disabled)return;const t=e.target.value;this.value=t,(0,d.r)(this,"value-changed",{value:t})}_handleOptionMouseDown(e){if(this.disabled)return;e.preventDefault();const t=e.target.value;this._activeIndex=this.options?.findIndex((e=>e.value===t))}_handleOptionMouseUp(e){e.preventDefault()}_handleOptionFocus(e){if(this.disabled)return;const t=e.target.value;this._activeIndex=this.options?.findIndex((e=>e.value===t))}render(){return a.qy`
      <div
        class="container"
        role="radiogroup"
        aria-label=${(0,n.J)(this.label)}
        @focus=${this._handleFocus}
        @blur=${this._handleBlur}
        @keydown=${this._handleKeydown}
        ?disabled=${this.disabled}
      >
        ${this.options?(0,l.u)(this.options,(e=>e.value),(e=>this._renderOption(e))):a.s6}
      </div>
    `}_renderOption(e){const t=this.value===e.value;return a.qy`
      <div
        id=${`option-${e.value}`}
        class=${(0,s.H)({option:!0,selected:t})}
        role="radio"
        tabindex=${t?"0":"-1"}
        .value=${e.value}
        aria-checked=${t?"true":"false"}
        aria-label=${(0,n.J)(e.label)}
        title=${(0,n.J)(e.label)}
        @click=${this._handleOptionClick}
        @focus=${this._handleOptionFocus}
        @mousedown=${this._handleOptionMouseDown}
        @mouseup=${this._handleOptionMouseUp}
      >
        <div class="content">
          ${e.path?a.qy`<ha-svg-icon .path=${e.path}></ha-svg-icon>`:e.icon||a.s6}
          ${e.label&&!this.hideOptionLabel?a.qy`<span>${e.label}</span>`:a.s6}
        </div>
      </div>
    `}constructor(...e){super(...e),this.disabled=!1,this.vertical=!1,this.hideOptionLabel=!1}}c.styles=a.AH`
    :host {
      display: block;
      --control-select-color: var(--primary-color);
      --control-select-focused-opacity: 0.2;
      --control-select-selected-opacity: 1;
      --control-select-background: var(--disabled-color);
      --control-select-background-opacity: 0.2;
      --control-select-thickness: 40px;
      --control-select-border-radius: 10px;
      --control-select-padding: 4px;
      --control-select-button-border-radius: calc(
        var(--control-select-border-radius) - var(--control-select-padding)
      );
      --mdc-icon-size: 20px;
      height: var(--control-select-thickness);
      width: 100%;
      font-style: normal;
      font-weight: var(--ha-font-weight-medium);
      color: var(--primary-text-color);
      user-select: none;
      -webkit-tap-highlight-color: transparent;
    }
    :host([vertical]) {
      width: var(--control-select-thickness);
      height: 100%;
    }
    .container {
      position: relative;
      height: 100%;
      width: 100%;
      border-radius: var(--control-select-border-radius);
      transform: translateZ(0);
      display: flex;
      flex-direction: row;
      padding: var(--control-select-padding);
      box-sizing: border-box;
      outline: none;
      transition: box-shadow 180ms ease-in-out;
    }
    .container::before {
      position: absolute;
      content: "";
      top: 0;
      left: 0;
      height: 100%;
      width: 100%;
      background: var(--control-select-background);
      opacity: var(--control-select-background-opacity);
      border-radius: var(--control-select-border-radius);
    }

    .container > *:not(:last-child) {
      margin-right: var(--control-select-padding);
      margin-inline-end: var(--control-select-padding);
      margin-inline-start: initial;
      direction: var(--direction);
    }
    .container[disabled] {
      --control-select-color: var(--disabled-color);
      --control-select-focused-opacity: 0;
      color: var(--disabled-color);
    }

    .container[disabled] .option {
      cursor: not-allowed;
    }

    .option {
      cursor: pointer;
      position: relative;
      flex: 1;
      height: 100%;
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: var(--control-select-button-border-radius);
      /* For safari border-radius overflow */
      z-index: 0;
      outline: none;
      transition: box-shadow 180ms ease-in-out;
    }
    .option:focus-visible {
      box-shadow: 0 0 0 2px var(--control-select-color);
    }
    .content > *:not(:last-child) {
      margin-bottom: 4px;
    }
    .option::before {
      position: absolute;
      content: "";
      top: 0;
      left: 0;
      height: 100%;
      width: 100%;
      background-color: var(--control-select-color);
      opacity: 0;
      border-radius: var(--control-select-button-border-radius);
      transition:
        background-color ease-in-out 180ms,
        opacity ease-in-out 80ms;
    }
    .option:hover::before {
      opacity: var(--control-select-focused-opacity);
    }
    .option.selected {
      color: white;
    }
    .option.selected::before {
      opacity: var(--control-select-selected-opacity);
    }
    .option .content {
      position: relative;
      pointer-events: none;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      text-align: center;
      padding: 2px;
      width: 100%;
      box-sizing: border-box;
    }
    .option .content span {
      display: block;
      width: 100%;
      -webkit-hyphens: auto;
      -moz-hyphens: auto;
      hyphens: auto;
    }
    :host([vertical]) {
      width: var(--control-select-thickness);
      height: auto;
    }
    :host([vertical]) .container {
      flex-direction: column;
    }
    :host([vertical]) .container > *:not(:last-child) {
      margin-right: initial;
      margin-inline-end: initial;
      margin-bottom: var(--control-select-padding);
    }
  `,(0,i.__decorate)([(0,r.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],c.prototype,"options",void 0),(0,i.__decorate)([(0,r.MZ)()],c.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],c.prototype,"vertical",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"hide-option-label"})],c.prototype,"hideOptionLabel",void 0),(0,i.__decorate)([(0,r.MZ)({type:String})],c.prototype,"label",void 0),(0,i.__decorate)([(0,r.wk)()],c.prototype,"_activeIndex",void 0),c=(0,i.__decorate)([(0,r.EM)("ha-control-select")],c)},52893:function(e,t,o){var i=o(69868),a=o(90191),r=o(80065),s=o(84922),n=o(11991),l=o(75907),d=o(73120);class c extends a.M{render(){const e={"mdc-form-field--align-end":this.alignEnd,"mdc-form-field--space-between":this.spaceBetween,"mdc-form-field--nowrap":this.nowrap};return s.qy` <div class="mdc-form-field ${(0,l.H)(e)}">
      <slot></slot>
      <label class="mdc-label" @click=${this._labelClick}>
        <slot name="label">${this.label}</slot>
      </label>
    </div>`}_labelClick(){const e=this.input;if(e&&(e.focus(),!e.disabled))switch(e.tagName){case"HA-CHECKBOX":e.checked=!e.checked,(0,d.r)(e,"change");break;case"HA-RADIO":e.checked=!0,(0,d.r)(e,"change");break;default:e.click()}}constructor(...e){super(...e),this.disabled=!1}}c.styles=[r.R,s.AH`
      :host(:not([alignEnd])) ::slotted(ha-switch) {
        margin-right: 10px;
        margin-inline-end: 10px;
        margin-inline-start: inline;
      }
      .mdc-form-field {
        align-items: var(--ha-formfield-align-items, center);
        gap: 4px;
      }
      .mdc-form-field > label {
        direction: var(--direction);
        margin-inline-start: 0;
        margin-inline-end: auto;
        padding: 0;
      }
      :host([disabled]) label {
        color: var(--disabled-text-color);
      }
    `],(0,i.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],c.prototype,"disabled",void 0),c=(0,i.__decorate)([(0,n.EM)("ha-formfield")],c)},94966:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991),s=o(13802),n=o(73120),l=(o(36137),o(93672),o(20014),o(88970)),d=o(65940),c=o(90963),h=o(65209);o(26731),o(81164);const p="___no_matching_items_found___",u=e=>a.qy`
  <ha-combo-box-item type="button" compact>
    ${e.icon?a.qy`<ha-icon slot="start" .icon=${e.icon}></ha-icon>`:e.icon_path?a.qy`<ha-svg-icon slot="start" .path=${e.icon_path}></ha-svg-icon>`:a.s6}
    <span slot="headline">${e.primary}</span>
    ${e.secondary?a.qy`<span slot="supporting-text">${e.secondary}</span>`:a.s6}
  </ha-combo-box-item>
`;class v extends a.WF{async open(){await this.updateComplete,await(this.comboBox?.open())}async focus(){await this.updateComplete,await(this.comboBox?.focus())}shouldUpdate(e){return!!(e.has("value")||e.has("label")||e.has("disabled"))||!(!e.has("_opened")&&this._opened)}willUpdate(e){e.has("_opened")&&this._opened&&(this._items=this._getItems(),this._initialItems&&(this.comboBox.filteredItems=this._items),this._initialItems=!0)}render(){return a.qy`
      <ha-combo-box
        item-id-path="id"
        item-value-path="id"
        item-label-path="a11y_label"
        clear-initial-value
        .hass=${this.hass}
        .value=${this._value}
        .label=${this.label}
        .helper=${this.helper}
        .allowCustomValue=${this.allowCustomValue}
        .filteredItems=${this._items}
        .renderer=${this.rowRenderer||u}
        .required=${this.required}
        .disabled=${this.disabled}
        .hideClearIcon=${this.hideClearIcon}
        @opened-changed=${this._openedChanged}
        @value-changed=${this._valueChanged}
        @filter-changed=${this._filterChanged}
      >
      </ha-combo-box>
    `}get _value(){return this.value||""}_openedChanged(e){e.stopPropagation(),e.detail.value!==this._opened&&(this._opened=e.detail.value,(0,n.r)(this,"opened-changed",{value:this._opened}))}_valueChanged(e){e.stopPropagation(),this.comboBox.setTextFieldValue("");const t=e.detail.value?.trim();t!==p&&t!==this._value&&this._setValue(t)}_filterChanged(e){if(!this._opened)return;const t=e.target,o=e.detail.value.trim(),i=this._fuseIndex(this._items),a=new h.b(this._items,{shouldSort:!1},i).multiTermsSearch(o);let r=this._items;if(a){const e=a.map((e=>e.item));0===e.length&&e.push(this._defaultNotFoundItem(this.notFoundLabel,this.hass.localize));const t=this._getAdditionalItems(o);e.push(...t),r=e}this.searchFn&&(r=this.searchFn(o,r,this._items)),t.filteredItems=r}_setValue(e){setTimeout((()=>{(0,n.r)(this,"value-changed",{value:e})}),0)}constructor(...e){super(...e),this.autofocus=!1,this.disabled=!1,this.required=!1,this.hideClearIcon=!1,this._opened=!1,this._initialItems=!1,this._items=[],this._defaultNotFoundItem=(0,d.A)(((e,t)=>({id:p,primary:e||t("ui.components.combo-box.no_match"),icon_path:"M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z",a11y_label:e||t("ui.components.combo-box.no_match")}))),this._getAdditionalItems=e=>(this.getAdditionalItems?.(e)||[]).map((e=>({...e,a11y_label:e.a11y_label||e.primary}))),this._getItems=()=>{const e=(this.getItems?this.getItems():[]).map((e=>({...e,a11y_label:e.a11y_label||e.primary}))).sort(((e,t)=>(0,c.SH)(e.sorting_label,t.sorting_label,this.hass.locale.language)));e.length||e.push(this._defaultNotFoundItem(this.notFoundLabel,this.hass.localize));const t=this._getAdditionalItems();return e.push(...t),e},this._fuseIndex=(0,d.A)((e=>l.A.createIndex(["search_labels"],e)))}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],v.prototype,"autofocus",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],v.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],v.prototype,"required",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"allow-custom-value"})],v.prototype,"allowCustomValue",void 0),(0,i.__decorate)([(0,r.MZ)()],v.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],v.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],v.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1,type:Array})],v.prototype,"getItems",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1,type:Array})],v.prototype,"getAdditionalItems",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],v.prototype,"rowRenderer",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"hide-clear-icon",type:Boolean})],v.prototype,"hideClearIcon",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"not-found-label",type:String})],v.prototype,"notFoundLabel",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],v.prototype,"searchFn",void 0),(0,i.__decorate)([(0,r.wk)()],v.prototype,"_opened",void 0),(0,i.__decorate)([(0,r.P)("ha-combo-box",!0)],v.prototype,"comboBox",void 0),v=(0,i.__decorate)([(0,r.EM)("ha-picker-combo-box")],v);class _ extends a.WF{async focus(){await this.updateComplete,await(this.item?.focus())}render(){const e=!(!this.value||this.required||this.disabled||this.hideClearIcon);return a.qy`
      <ha-combo-box-item .disabled=${this.disabled} type="button" compact>
        ${this.value?this.valueRenderer?this.valueRenderer(this.value):a.qy`<slot name="headline">${this.value}</slot>`:a.qy`
              <span slot="headline" class="placeholder">
                ${this.placeholder}
              </span>
            `}
        ${e?a.qy`
              <ha-icon-button
                class="clear"
                slot="end"
                @click=${this._clear}
                .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
              ></ha-icon-button>
            `:a.s6}
        <ha-svg-icon
          class="arrow"
          slot="end"
          .path=${"M7,10L12,15L17,10H7Z"}
        ></ha-svg-icon>
      </ha-combo-box-item>
    `}_clear(e){e.stopPropagation(),(0,n.r)(this,"clear")}static get styles(){return[a.AH`
        ha-combo-box-item[disabled] {
          background-color: var(
            --mdc-text-field-disabled-fill-color,
            whitesmoke
          );
        }
        ha-combo-box-item {
          background-color: var(--mdc-text-field-fill-color, whitesmoke);
          border-radius: 4px;
          border-end-end-radius: 0;
          border-end-start-radius: 0;
          --md-list-item-one-line-container-height: 56px;
          --md-list-item-two-line-container-height: 56px;
          --md-list-item-top-space: 0px;
          --md-list-item-bottom-space: 0px;
          --md-list-item-leading-space: 8px;
          --md-list-item-trailing-space: 8px;
          --ha-md-list-item-gap: 8px;
          /* Remove the default focus ring */
          --md-focus-ring-width: 0px;
          --md-focus-ring-duration: 0s;
        }

        /* Add Similar focus style as the text field */
        ha-combo-box-item[disabled]:after {
          background-color: var(
            --mdc-text-field-disabled-line-color,
            rgba(0, 0, 0, 0.42)
          );
        }
        ha-combo-box-item:after {
          display: block;
          content: "";
          position: absolute;
          pointer-events: none;
          bottom: 0;
          left: 0;
          right: 0;
          height: 1px;
          width: 100%;
          background-color: var(
            --mdc-text-field-idle-line-color,
            rgba(0, 0, 0, 0.42)
          );
          transform:
            height 180ms ease-in-out,
            background-color 180ms ease-in-out;
        }

        ha-combo-box-item:focus:after {
          height: 2px;
          background-color: var(--mdc-theme-primary);
        }

        .clear {
          margin: 0 -8px;
          --mdc-icon-button-size: 32px;
          --mdc-icon-size: 20px;
        }
        .arrow {
          --mdc-icon-size: 20px;
          width: 32px;
        }

        .placeholder {
          color: var(--secondary-text-color);
          padding: 0 8px;
        }
      `]}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.hideClearIcon=!1}}(0,i.__decorate)([(0,r.MZ)({type:Boolean})],_.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],_.prototype,"required",void 0),(0,i.__decorate)([(0,r.MZ)()],_.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],_.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)()],_.prototype,"placeholder",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"hide-clear-icon",type:Boolean})],_.prototype,"hideClearIcon",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],_.prototype,"valueRenderer",void 0),(0,i.__decorate)([(0,r.P)("ha-combo-box-item",!0)],_.prototype,"item",void 0),_=(0,i.__decorate)([(0,r.EM)("ha-picker-field")],_);o(95635);class g extends a.WF{render(){return a.qy`
      ${this.label?a.qy`<label ?disabled=${this.disabled}>${this.label}</label>`:a.s6}
      <div class="container">
        ${this._opened?a.qy`
              <ha-picker-combo-box
                .hass=${this.hass}
                .autofocus=${this.autofocus}
                .allowCustomValue=${this.allowCustomValue}
                .label=${this.searchLabel??this.hass.localize("ui.common.search")}
                .value=${this.value}
                hide-clear-icon
                @opened-changed=${this._openedChanged}
                @value-changed=${this._valueChanged}
                .rowRenderer=${this.rowRenderer}
                .notFoundLabel=${this.notFoundLabel}
                .getItems=${this.getItems}
                .getAdditionalItems=${this.getAdditionalItems}
                .searchFn=${this.searchFn}
              ></ha-picker-combo-box>
            `:a.qy`
              <ha-picker-field
                type="button"
                compact
                aria-label=${(0,s.J)(this.label)}
                @click=${this.open}
                @clear=${this._clear}
                .placeholder=${this.placeholder}
                .value=${this.value}
                .required=${this.required}
                .disabled=${this.disabled}
                .hideClearIcon=${this.hideClearIcon}
                .valueRenderer=${this.valueRenderer}
              >
              </ha-picker-field>
            `}
      </div>
      ${this._renderHelper()}
    `}_renderHelper(){return this.helper?a.qy`<ha-input-helper-text .disabled=${this.disabled}
          >${this.helper}</ha-input-helper-text
        >`:a.s6}_valueChanged(e){e.stopPropagation();const t=e.detail.value;t&&(0,n.r)(this,"value-changed",{value:t})}_clear(e){e.stopPropagation(),this._setValue(void 0)}_setValue(e){this.value=e,(0,n.r)(this,"value-changed",{value:e})}async open(){this.disabled||(this._opened=!0,await this.updateComplete,this._comboBox?.focus(),this._comboBox?.open())}async _openedChanged(e){const t=e.detail.value;this._opened&&!t&&(this._opened=!1,await this.updateComplete,this._field?.focus())}static get styles(){return[a.AH`
        .container {
          position: relative;
          display: block;
        }
        label[disabled] {
          color: var(--mdc-text-field-disabled-ink-color, rgba(0, 0, 0, 0.6));
        }
        label {
          display: block;
          margin: 0 0 8px;
        }
        ha-input-helper-text {
          display: block;
          margin: 8px 0 0;
        }
      `]}constructor(...e){super(...e),this.autofocus=!1,this.disabled=!1,this.required=!1,this.hideClearIcon=!1,this._opened=!1}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],g.prototype,"autofocus",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],g.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],g.prototype,"required",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"allow-custom-value"})],g.prototype,"allowCustomValue",void 0),(0,i.__decorate)([(0,r.MZ)()],g.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],g.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],g.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)()],g.prototype,"placeholder",void 0),(0,i.__decorate)([(0,r.MZ)({type:String,attribute:"search-label"})],g.prototype,"searchLabel",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"hide-clear-icon",type:Boolean})],g.prototype,"hideClearIcon",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1,type:Array})],g.prototype,"getItems",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1,type:Array})],g.prototype,"getAdditionalItems",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"rowRenderer",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"valueRenderer",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"searchFn",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"not-found-label",type:String})],g.prototype,"notFoundLabel",void 0),(0,i.__decorate)([(0,r.P)("ha-picker-field")],g.prototype,"_field",void 0),(0,i.__decorate)([(0,r.P)("ha-picker-combo-box")],g.prototype,"_comboBox",void 0),(0,i.__decorate)([(0,r.wk)()],g.prototype,"_opened",void 0),g=(0,i.__decorate)([(0,r.EM)("ha-generic-picker")],g)},8101:function(e,t,o){o.r(t),o.d(t,{HaIconButtonArrowPrev:()=>n});var i=o(69868),a=o(84922),r=o(11991),s=o(90933);o(93672);class n extends a.WF{render(){return a.qy`
      <ha-icon-button
        .disabled=${this.disabled}
        .label=${this.label||this.hass?.localize("ui.common.back")||"Back"}
        .path=${this._icon}
      ></ha-icon-button>
    `}constructor(...e){super(...e),this.disabled=!1,this._icon="rtl"===s.G.document.dir?"M4,11V13H16L10.5,18.5L11.92,19.92L19.84,12L11.92,4.08L10.5,5.5L16,11H4Z":"M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z"}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],n.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],n.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)()],n.prototype,"label",void 0),(0,i.__decorate)([(0,r.wk)()],n.prototype,"_icon",void 0),n=(0,i.__decorate)([(0,r.EM)("ha-icon-button-arrow-prev")],n)},93672:function(e,t,o){o.r(t),o.d(t,{HaIconButton:()=>n});var i=o(69868),a=(o(31807),o(84922)),r=o(11991),s=o(13802);o(95635);class n extends a.WF{focus(){this._button?.focus()}render(){return a.qy`
      <mwc-icon-button
        aria-label=${(0,s.J)(this.label)}
        title=${(0,s.J)(this.hideTitle?void 0:this.label)}
        aria-haspopup=${(0,s.J)(this.ariaHasPopup)}
        .disabled=${this.disabled}
      >
        ${this.path?a.qy`<ha-svg-icon .path=${this.path}></ha-svg-icon>`:a.qy`<slot></slot>`}
      </mwc-icon-button>
    `}constructor(...e){super(...e),this.disabled=!1,this.hideTitle=!1}}n.shadowRootOptions={mode:"open",delegatesFocus:!0},n.styles=a.AH`
    :host {
      display: inline-block;
      outline: none;
    }
    :host([disabled]) {
      pointer-events: none;
    }
    mwc-icon-button {
      --mdc-theme-on-primary: currentColor;
      --mdc-theme-text-disabled-on-light: var(--disabled-text-color);
    }
  `,(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],n.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:String})],n.prototype,"path",void 0),(0,i.__decorate)([(0,r.MZ)({type:String})],n.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)({type:String,attribute:"aria-haspopup"})],n.prototype,"ariaHasPopup",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"hide-title",type:Boolean})],n.prototype,"hideTitle",void 0),(0,i.__decorate)([(0,r.P)("mwc-icon-button",!0)],n.prototype,"_button",void 0),n=(0,i.__decorate)([(0,r.EM)("ha-icon-button")],n)},72062:function(e,t,o){o.r(t),o.d(t,{HaIconNext:()=>n});var i=o(69868),a=o(11991),r=o(90933),s=o(95635);class n extends s.HaSvgIcon{constructor(...e){super(...e),this.path="rtl"===r.G.document.dir?"M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z":"M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"}}(0,i.__decorate)([(0,a.MZ)()],n.prototype,"path",void 0),n=(0,i.__decorate)([(0,a.EM)("ha-icon-next")],n)},98343:function(e,t,o){o.d(t,{G:()=>d,J:()=>l});var i=o(69868),a=o(64980),r=o(23719),s=o(84922),n=o(11991);const l=[r.R,s.AH`
    :host {
      --ha-icon-display: block;
      --md-sys-color-primary: var(--primary-text-color);
      --md-sys-color-secondary: var(--secondary-text-color);
      --md-sys-color-surface: var(--card-background-color);
      --md-sys-color-on-surface: var(--primary-text-color);
      --md-sys-color-on-surface-variant: var(--secondary-text-color);
    }
    md-item {
      overflow: var(--md-item-overflow, hidden);
      align-items: var(--md-item-align-items, center);
      gap: var(--ha-md-list-item-gap, 16px);
    }
  `];class d extends a.n{}d.styles=l,d=(0,i.__decorate)([(0,n.EM)("ha-md-list-item")],d)},5803:function(e,t,o){var i=o(69868),a=o(88752),r=o(43739),s=o(84922),n=o(11991);class l extends a.B{}l.styles=[r.R,s.AH`
      :host {
        --md-sys-color-surface: var(--card-background-color);
      }
    `],l=(0,i.__decorate)([(0,n.EM)("ha-md-list")],l)},3433:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991),s=o(73120);class n{processMessage(e){if("removed"===e.type)for(const t of Object.keys(e.notifications))delete this.notifications[t];else this.notifications={...this.notifications,...e.notifications};return Object.values(this.notifications)}constructor(){this.notifications={}}}o(93672);class l extends a.WF{connectedCallback(){super.connectedCallback(),this._attachNotifOnConnect&&(this._attachNotifOnConnect=!1,this._subscribeNotifications())}disconnectedCallback(){super.disconnectedCallback(),this._unsubNotifications&&(this._attachNotifOnConnect=!0,this._unsubNotifications(),this._unsubNotifications=void 0)}render(){if(!this._show)return a.s6;const e=this._hasNotifications&&(this.narrow||"always_hidden"===this.hass.dockedSidebar);return a.qy`
      <ha-icon-button
        .label=${this.hass.localize("ui.sidebar.sidebar_toggle")}
        .path=${"M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"}
        @click=${this._toggleMenu}
      ></ha-icon-button>
      ${e?a.qy`<div class="dot"></div>`:""}
    `}firstUpdated(e){super.firstUpdated(e),this.hassio&&(this._alwaysVisible=(Number(window.parent.frontendVersion)||0)<20190710)}willUpdate(e){if(super.willUpdate(e),!e.has("narrow")&&!e.has("hass"))return;const t=e.has("hass")?e.get("hass"):this.hass,o=(e.has("narrow")?e.get("narrow"):this.narrow)||"always_hidden"===t?.dockedSidebar,i=this.narrow||"always_hidden"===this.hass.dockedSidebar;this.hasUpdated&&o===i||(this._show=i||this._alwaysVisible,i?this._subscribeNotifications():this._unsubNotifications&&(this._unsubNotifications(),this._unsubNotifications=void 0))}_subscribeNotifications(){if(this._unsubNotifications)throw new Error("Already subscribed");this._unsubNotifications=((e,t)=>{const o=new n,i=e.subscribeMessage((e=>t(o.processMessage(e))),{type:"persistent_notification/subscribe"});return()=>{i.then((e=>e?.()))}})(this.hass.connection,(e=>{this._hasNotifications=e.length>0}))}_toggleMenu(){(0,s.r)(this,"hass-toggle-menu")}constructor(...e){super(...e),this.hassio=!1,this.narrow=!1,this._hasNotifications=!1,this._show=!1,this._alwaysVisible=!1,this._attachNotifOnConnect=!1}}l.styles=a.AH`
    :host {
      position: relative;
    }
    .dot {
      pointer-events: none;
      position: absolute;
      background-color: var(--accent-color);
      width: 12px;
      height: 12px;
      top: 9px;
      right: 7px;
      inset-inline-end: 7px;
      inset-inline-start: initial;
      border-radius: 50%;
      border: 2px solid var(--app-header-background-color);
    }
  `,(0,i.__decorate)([(0,r.MZ)({type:Boolean})],l.prototype,"hassio",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],l.prototype,"narrow",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],l.prototype,"hass",void 0),(0,i.__decorate)([(0,r.wk)()],l.prototype,"_hasNotifications",void 0),(0,i.__decorate)([(0,r.wk)()],l.prototype,"_show",void 0),l=(0,i.__decorate)([(0,r.EM)("ha-menu-button")],l)},88002:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991),s=o(13802);o(72062),o(95635),o(5803),o(98343);class n extends a.WF{render(){return a.qy`
      <ha-md-list
        innerRole="menu"
        itemRoles="menuitem"
        innerAriaLabel=${(0,s.J)(this.label)}
      >
        ${this.pages.map((e=>{const t=e.path.endsWith("#external-app-configuration");return a.qy`
            <ha-md-list-item
              .type=${t?"button":"link"}
              .href=${t?void 0:e.path}
              @click=${t?this._handleExternalApp:void 0}
            >
              <div
                slot="start"
                class=${e.iconColor?"icon-background":""}
                .style="background-color: ${e.iconColor||"undefined"}"
              >
                <ha-svg-icon .path=${e.iconPath}></ha-svg-icon>
              </div>
              <span slot="headline">${e.name}</span>
              ${this.hasSecondary?a.qy`<span slot="supporting-text">${e.description}</span>`:""}
              ${this.narrow?"":a.qy`<ha-icon-next slot="end"></ha-icon-next>`}
            </ha-md-list-item>
          `}))}
      </ha-md-list>
    `}_handleExternalApp(){this.hass.auth.external.fireMessage({type:"config_screen/show"})}constructor(...e){super(...e),this.narrow=!1,this.hasSecondary=!1}}n.styles=a.AH`
    ha-svg-icon,
    ha-icon-next {
      color: var(--secondary-text-color);
      height: 24px;
      width: 24px;
      display: block;
    }
    ha-svg-icon {
      padding: 8px;
    }
    .icon-background {
      border-radius: 50%;
    }
    .icon-background ha-svg-icon {
      color: #fff;
    }
    ha-md-list-item {
      font-size: var(--navigation-list-item-title-font-size);
    }
  `,(0,i.__decorate)([(0,r.MZ)({attribute:!1})],n.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],n.prototype,"narrow",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],n.prototype,"pages",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"has-secondary",type:Boolean})],n.prototype,"hasSecondary",void 0),(0,i.__decorate)([(0,r.MZ)()],n.prototype,"label",void 0),n=(0,i.__decorate)([(0,r.EM)("ha-navigation-list")],n)},56292:function(e,t,o){var i=o(69868),a=o(63442),r=o(45141),s=o(84922),n=o(11991);class l extends a.F{}l.styles=[r.R,s.AH`
      :host {
        --mdc-theme-secondary: var(--primary-color);
      }
    `],l=(0,i.__decorate)([(0,n.EM)("ha-radio")],l)},58895:function(e,t,o){var i=o(69868),a=o(11991),r=o(84922),s=(o(56292),o(75907)),n=o(7577),l=o(73120),d=o(98137),c=o(20674);class h extends r.WF{render(){const e=this.maxColumns??3,t=Math.min(e,this.options.length);return r.qy`
      <div class="list" style=${(0,n.W)({"--columns":t})}>
        ${this.options.map((e=>this._renderOption(e)))}
      </div>
    `}_renderOption(e){const t=1===this.maxColumns,o=e.disabled||this.disabled||!1,i=e.value===this.value,a=this.hass?.themes.darkMode||!1,n=!!this.hass&&(0,d.qC)(this.hass),l="object"==typeof e.image?a&&e.image.src_dark||e.image.src:e.image,h="object"==typeof e.image&&(n&&e.image.flip_rtl);return r.qy`
      <label
        class="option ${(0,s.H)({horizontal:t,selected:i})}"
        ?disabled=${o}
        @click=${this._labelClick}
      >
        <div class="content">
          <ha-radio
            .checked=${e.value===this.value}
            .value=${e.value}
            .disabled=${o}
            @change=${this._radioChanged}
            @click=${c.d}
          ></ha-radio>
          <div class="text">
            <span class="label">${e.label}</span>
            ${e.description?r.qy`<span class="description">${e.description}</span>`:r.s6}
          </div>
        </div>
        ${l?r.qy`
              <img class=${h?"flipped":""} alt="" src=${l} />
            `:r.s6}
      </label>
    `}_labelClick(e){e.stopPropagation(),e.currentTarget.querySelector("ha-radio")?.click()}_radioChanged(e){e.stopPropagation();const t=e.currentTarget.value;this.disabled||void 0===t||t===(this.value??"")||(0,l.r)(this,"value-changed",{value:t})}constructor(...e){super(...e),this.options=[]}}h.styles=r.AH`
    .list {
      display: grid;
      grid-template-columns: repeat(var(--columns, 1), minmax(0, 1fr));
      gap: 12px;
    }
    .option {
      position: relative;
      display: block;
      border: 1px solid var(--divider-color);
      border-radius: var(--ha-card-border-radius, 12px);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 12px;
      gap: 8px;
      overflow: hidden;
      cursor: pointer;
    }

    .option .content {
      position: relative;
      display: flex;
      flex-direction: row;
      gap: 8px;
      min-width: 0;
      width: 100%;
    }
    .option .content ha-radio {
      margin: -12px;
      flex: none;
    }
    .option .content .text {
      display: flex;
      flex-direction: column;
      gap: 4px;
      min-width: 0;
      flex: 1;
    }
    .option .content .text .label {
      color: var(--primary-text-color);
      font-size: var(--ha-font-size-m);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
    .option .content .text .description {
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
    }
    img {
      position: relative;
      max-width: var(--ha-select-box-image-size, 96px);
      max-height: var(--ha-select-box-image-size, 96px);
      margin: auto;
    }

    .flipped {
      transform: scaleX(-1);
    }

    .option.horizontal {
      flex-direction: row;
      align-items: flex-start;
    }

    .option.horizontal img {
      margin: 0;
    }

    .option:before {
      content: "";
      display: block;
      inset: 0;
      position: absolute;
      background-color: transparent;
      pointer-events: none;
      opacity: 0.2;
      transition:
        background-color 180ms ease-in-out,
        opacity 180ms ease-in-out;
    }
    .option:hover:before {
      background-color: var(--divider-color);
    }
    .option.selected:before {
      background-color: var(--primary-color);
    }
    .option[disabled] {
      cursor: not-allowed;
    }
    .option[disabled] .content,
    .option[disabled] img {
      opacity: 0.5;
    }
    .option[disabled]:before {
      background-color: var(--disabled-color);
      opacity: 0.05;
    }
  `,(0,i.__decorate)([(0,a.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],h.prototype,"options",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],h.prototype,"value",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean})],h.prototype,"disabled",void 0),(0,i.__decorate)([(0,a.MZ)({type:Number,attribute:"max_columns"})],h.prototype,"maxColumns",void 0),h=(0,i.__decorate)([(0,a.EM)("ha-select-box")],h)},37207:function(e,t,o){var i=o(69868),a=o(96542),r=o(5187),s=o(84922),n=o(11991),l=o(75907),d=o(24802),c=o(93360);o(93672),o(95968);class h extends a.o{render(){return s.qy`
      ${super.render()}
      ${this.clearable&&!this.required&&!this.disabled&&this.value?s.qy`<ha-icon-button
            label="clear"
            @click=${this._clearValue}
            .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
          ></ha-icon-button>`:s.s6}
    `}renderMenu(){const e=this.getMenuClasses();return s.qy`<ha-menu
      innerRole="listbox"
      wrapFocus
      class=${(0,l.H)(e)}
      activatable
      .fullwidth=${!this.fixedMenuPosition&&!this.naturalMenuWidth}
      .open=${this.menuOpen}
      .anchor=${this.anchorElement}
      .fixed=${this.fixedMenuPosition}
      @selected=${this.onSelected}
      @opened=${this.onOpened}
      @closed=${this.onClosed}
      @items-updated=${this.onItemsUpdated}
      @keydown=${this.handleTypeahead}
    >
      ${this.renderMenuContent()}
    </ha-menu>`}renderLeadingIcon(){return this.icon?s.qy`<span class="mdc-select__icon"
      ><slot name="icon"></slot
    ></span>`:s.s6}connectedCallback(){super.connectedCallback(),window.addEventListener("translations-updated",this._translationsUpdated)}async firstUpdated(){super.firstUpdated(),this.inlineArrow&&this.shadowRoot?.querySelector(".mdc-select__selected-text-container")?.classList.add("inline-arrow")}updated(e){if(super.updated(e),e.has("inlineArrow")){const e=this.shadowRoot?.querySelector(".mdc-select__selected-text-container");this.inlineArrow?e?.classList.add("inline-arrow"):e?.classList.remove("inline-arrow")}e.get("options")&&(this.layoutOptions(),this.selectByValue(this.value))}disconnectedCallback(){super.disconnectedCallback(),window.removeEventListener("translations-updated",this._translationsUpdated)}_clearValue(){!this.disabled&&this.value&&(this.valueSetDirectly=!0,this.select(-1),this.mdcFoundation.handleChange())}constructor(...e){super(...e),this.icon=!1,this.clearable=!1,this.inlineArrow=!1,this._translationsUpdated=(0,d.s)((async()=>{await(0,c.E)(),this.layoutOptions()}),500)}}h.styles=[r.R,s.AH`
      :host([clearable]) {
        position: relative;
      }
      .mdc-select:not(.mdc-select--disabled) .mdc-select__icon {
        color: var(--secondary-text-color);
      }
      .mdc-select__anchor {
        width: var(--ha-select-min-width, 200px);
      }
      .mdc-select--filled .mdc-select__anchor {
        height: var(--ha-select-height, 56px);
      }
      .mdc-select--filled .mdc-floating-label {
        inset-inline-start: 12px;
        inset-inline-end: initial;
        direction: var(--direction);
      }
      .mdc-select--filled.mdc-select--with-leading-icon .mdc-floating-label {
        inset-inline-start: 48px;
        inset-inline-end: initial;
        direction: var(--direction);
      }
      .mdc-select .mdc-select__anchor {
        padding-inline-start: 12px;
        padding-inline-end: 0px;
        direction: var(--direction);
      }
      .mdc-select__anchor .mdc-floating-label--float-above {
        transform-origin: var(--float-start);
      }
      .mdc-select__selected-text-container {
        padding-inline-end: var(--select-selected-text-padding-end, 0px);
      }
      :host([clearable]) .mdc-select__selected-text-container {
        padding-inline-end: var(--select-selected-text-padding-end, 12px);
      }
      ha-icon-button {
        position: absolute;
        top: 10px;
        right: 28px;
        --mdc-icon-button-size: 36px;
        --mdc-icon-size: 20px;
        color: var(--secondary-text-color);
        inset-inline-start: initial;
        inset-inline-end: 28px;
        direction: var(--direction);
      }
      .inline-arrow {
        flex-grow: 0;
      }
    `],(0,i.__decorate)([(0,n.MZ)({type:Boolean})],h.prototype,"icon",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],h.prototype,"clearable",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"inline-arrow",type:Boolean})],h.prototype,"inlineArrow",void 0),(0,i.__decorate)([(0,n.MZ)()],h.prototype,"options",void 0),h=(0,i.__decorate)([(0,n.EM)("ha-select")],h)},87150:function(e,t,o){o.a(e,(async function(e,i){try{o.r(t),o.d(t,{HaNumberSelector:()=>h});var a=o(69868),r=o(84922),s=o(11991),n=o(75907),l=o(73120),d=(o(20014),o(45810)),c=(o(11934),e([d]));d=(c.then?(await c)():c)[0];class h extends r.WF{willUpdate(e){e.has("value")&&(""!==this._valueStr&&this.value===Number(this._valueStr)||(this._valueStr=null==this.value||isNaN(this.value)?"":this.value.toString()))}render(){const e="box"===this.selector.number?.mode||void 0===this.selector.number?.min||void 0===this.selector.number?.max;let t;if(!e&&(t=this.selector.number.step??1,"any"===t)){t=1;const e=(this.selector.number.max-this.selector.number.min)/100;for(;t>e;)t/=10}const o=this.selector.number?.translation_key;let i=this.selector.number?.unit_of_measurement;return e&&i&&this.localizeValue&&o&&(i=this.localizeValue(`${o}.unit_of_measurement.${i}`)||i),r.qy`
      ${this.label&&!e?r.qy`${this.label}${this.required?"*":""}`:r.s6}
      <div class="input">
        ${e?r.s6:r.qy`
              <ha-slider
                labeled
                .min=${this.selector.number.min}
                .max=${this.selector.number.max}
                .value=${this.value}
                .step=${t}
                .disabled=${this.disabled}
                .required=${this.required}
                @change=${this._handleSliderChange}
                .withMarkers=${this.selector.number?.slider_ticks||!1}
              >
              </ha-slider>
            `}
        <ha-textfield
          .inputMode=${"any"===this.selector.number?.step||(this.selector.number?.step??1)%1!=0?"decimal":"numeric"}
          .label=${e?this.label:void 0}
          .placeholder=${this.placeholder}
          class=${(0,n.H)({single:e})}
          .min=${this.selector.number?.min}
          .max=${this.selector.number?.max}
          .value=${this._valueStr??""}
          .step=${this.selector.number?.step??1}
          helperPersistent
          .helper=${e?this.helper:void 0}
          .disabled=${this.disabled}
          .required=${this.required}
          .suffix=${i}
          type="number"
          autoValidate
          ?no-spinner=${!e}
          @input=${this._handleInputChange}
        >
        </ha-textfield>
      </div>
      ${!e&&this.helper?r.qy`<ha-input-helper-text .disabled=${this.disabled}
            >${this.helper}</ha-input-helper-text
          >`:r.s6}
    `}_handleInputChange(e){e.stopPropagation(),this._valueStr=e.target.value;const t=""===e.target.value||isNaN(e.target.value)?void 0:Number(e.target.value);this.value!==t&&(0,l.r)(this,"value-changed",{value:t})}_handleSliderChange(e){e.stopPropagation();const t=Number(e.target.value);this.value!==t&&(0,l.r)(this,"value-changed",{value:t})}constructor(...e){super(...e),this.required=!0,this.disabled=!1,this._valueStr=""}}h.styles=r.AH`
    .input {
      display: flex;
      justify-content: space-between;
      align-items: center;
      direction: ltr;
    }
    ha-slider {
      flex: 1;
      margin-right: 16px;
      margin-inline-end: 16px;
      margin-inline-start: 0;
    }
    ha-textfield {
      --ha-textfield-input-width: 40px;
    }
    .single {
      --ha-textfield-input-width: unset;
      flex: 1;
    }
  `,(0,a.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"selector",void 0),(0,a.__decorate)([(0,s.MZ)({type:Number})],h.prototype,"value",void 0),(0,a.__decorate)([(0,s.MZ)({type:Number})],h.prototype,"placeholder",void 0),(0,a.__decorate)([(0,s.MZ)()],h.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)()],h.prototype,"helper",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"localizeValue",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],h.prototype,"required",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],h.prototype,"disabled",void 0),h=(0,a.__decorate)([(0,s.EM)("ha-selector-number")],h),i()}catch(h){i(h)}}))},40027:function(e,t,o){o.r(t),o.d(t,{HaSelectSelector:()=>h});var i=o(69868),a=o(84922),r=o(11991),s=o(33055),n=o(26846),l=o(73120),d=o(20674),c=o(90963);o(54820),o(54538),o(71978),o(26731),o(52893),o(20014),o(25223),o(56292),o(37207),o(58895),o(8115);class h extends a.WF{_itemMoved(e){e.stopPropagation();const{oldIndex:t,newIndex:o}=e.detail;this._move(t,o)}_move(e,t){const o=this.value.concat(),i=o.splice(e,1)[0];o.splice(t,0,i),this.value=o,(0,l.r)(this,"value-changed",{value:o})}render(){const e=this.selector.select?.options?.map((e=>"object"==typeof e?e:{value:e,label:e}))||[],t=this.selector.select?.translation_key;if(this.localizeValue&&t&&e.forEach((e=>{const o=this.localizeValue(`${t}.options.${e.value}`);o&&(e.label=o)})),this.selector.select?.sort&&e.sort(((e,t)=>(0,c.SH)(e.label,t.label,this.hass.locale.language))),!this.selector.select?.multiple&&!this.selector.select?.reorder&&!this.selector.select?.custom_value&&"box"===this._mode)return a.qy`
        ${this.label?a.qy`<span class="label">${this.label}</span>`:a.s6}
        <ha-select-box
          .options=${e}
          .value=${this.value}
          @value-changed=${this._valueChanged}
          .maxColumns=${this.selector.select?.box_max_columns}
          .hass=${this.hass}
        ></ha-select-box>
        ${this._renderHelper()}
      `;if(!this.selector.select?.custom_value&&!this.selector.select?.reorder&&"list"===this._mode){if(!this.selector.select?.multiple)return a.qy`
          <div>
            ${this.label}
            ${e.map((e=>a.qy`
                <ha-formfield
                  .label=${e.label}
                  .disabled=${e.disabled||this.disabled}
                >
                  <ha-radio
                    .checked=${e.value===this.value}
                    .value=${e.value}
                    .disabled=${e.disabled||this.disabled}
                    @change=${this._valueChanged}
                  ></ha-radio>
                </ha-formfield>
              `))}
          </div>
          ${this._renderHelper()}
        `;const t=this.value&&""!==this.value?(0,n.e)(this.value):[];return a.qy`
        <div>
          ${this.label}
          ${e.map((e=>a.qy`
              <ha-formfield .label=${e.label}>
                <ha-checkbox
                  .checked=${t.includes(e.value)}
                  .value=${e.value}
                  .disabled=${e.disabled||this.disabled}
                  @change=${this._checkboxChanged}
                ></ha-checkbox>
              </ha-formfield>
            `))}
        </div>
        ${this._renderHelper()}
      `}if(this.selector.select?.multiple){const t=this.value&&""!==this.value?(0,n.e)(this.value):[],o=e.filter((e=>!e.disabled&&!t?.includes(e.value)));return a.qy`
        ${t?.length?a.qy`
              <ha-sortable
                no-style
                .disabled=${!this.selector.select.reorder}
                @item-moved=${this._itemMoved}
                handle-selector="button.primary.action"
              >
                <ha-chip-set>
                  ${(0,s.u)(t,(e=>e),((t,o)=>{const i=e.find((e=>e.value===t))?.label||t;return a.qy`
                        <ha-input-chip
                          .idx=${o}
                          @remove=${this._removeItem}
                          .label=${i}
                          selected
                        >
                          ${this.selector.select?.reorder?a.qy`
                                <ha-svg-icon
                                  slot="icon"
                                  .path=${"M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z"}
                                ></ha-svg-icon>
                              `:a.s6}
                          ${e.find((e=>e.value===t))?.label||t}
                        </ha-input-chip>
                      `}))}
                </ha-chip-set>
              </ha-sortable>
            `:a.s6}

        <ha-combo-box
          item-value-path="value"
          item-label-path="label"
          .hass=${this.hass}
          .label=${this.label}
          .helper=${this.helper}
          .disabled=${this.disabled}
          .required=${this.required&&!t.length}
          .value=${""}
          .items=${o}
          .allowCustomValue=${this.selector.select.custom_value??!1}
          @filter-changed=${this._filterChanged}
          @value-changed=${this._comboBoxValueChanged}
          @opened-changed=${this._openedChanged}
        ></ha-combo-box>
      `}if(this.selector.select?.custom_value){void 0===this.value||Array.isArray(this.value)||e.find((e=>e.value===this.value))||e.unshift({value:this.value,label:this.value});const t=e.filter((e=>!e.disabled));return a.qy`
        <ha-combo-box
          item-value-path="value"
          item-label-path="label"
          .hass=${this.hass}
          .label=${this.label}
          .helper=${this.helper}
          .disabled=${this.disabled}
          .required=${this.required}
          .items=${t}
          .value=${this.value}
          @filter-changed=${this._filterChanged}
          @value-changed=${this._comboBoxValueChanged}
          @opened-changed=${this._openedChanged}
        ></ha-combo-box>
      `}return a.qy`
      <ha-select
        fixedMenuPosition
        naturalMenuWidth
        .label=${this.label??""}
        .value=${this.value??""}
        .helper=${this.helper??""}
        .disabled=${this.disabled}
        .required=${this.required}
        clearable
        @closed=${d.d}
        @selected=${this._valueChanged}
      >
        ${e.map((e=>a.qy`
            <ha-list-item .value=${e.value} .disabled=${e.disabled}
              >${e.label}</ha-list-item
            >
          `))}
      </ha-select>
    `}_renderHelper(){return this.helper?a.qy`<ha-input-helper-text .disabled=${this.disabled}
          >${this.helper}</ha-input-helper-text
        >`:""}get _mode(){return this.selector.select?.mode||((this.selector.select?.options?.length||0)<6?"list":"dropdown")}_valueChanged(e){if(e.stopPropagation(),-1===e.detail?.index&&void 0!==this.value)return void(0,l.r)(this,"value-changed",{value:void 0});const t=e.detail?.value||e.target.value;this.disabled||void 0===t||t===(this.value??"")||(0,l.r)(this,"value-changed",{value:t})}_checkboxChanged(e){if(e.stopPropagation(),this.disabled)return;let t;const o=e.target.value,i=e.target.checked,a=this.value&&""!==this.value?(0,n.e)(this.value):[];if(i){if(a.includes(o))return;t=[...a,o]}else{if(!a?.includes(o))return;t=a.filter((e=>e!==o))}(0,l.r)(this,"value-changed",{value:t})}async _removeItem(e){e.stopPropagation();const t=[...(0,n.e)(this.value)];t.splice(e.target.idx,1),(0,l.r)(this,"value-changed",{value:t}),await this.updateComplete,this._filterChanged()}_comboBoxValueChanged(e){e.stopPropagation();const t=e.detail.value;if(this.disabled||""===t)return;if(!this.selector.select?.multiple)return void(0,l.r)(this,"value-changed",{value:t});const o=this.value&&""!==this.value?(0,n.e)(this.value):[];void 0!==t&&o.includes(t)||(setTimeout((()=>{this._filterChanged(),this.comboBox.setInputValue("")}),0),(0,l.r)(this,"value-changed",{value:[...o,t]}))}_openedChanged(e){e?.detail.value&&this._filterChanged()}_filterChanged(e){this._filter=e?.detail.value||"";const t=this.comboBox.items?.filter((e=>(e.label||e.value).toLowerCase().includes(this._filter?.toLowerCase())));this._filter&&this.selector.select?.custom_value&&t&&!t.some((e=>(e.label||e.value)===this._filter))&&t.unshift({label:this._filter,value:this._filter}),this.comboBox.filteredItems=t}constructor(...e){super(...e),this.disabled=!1,this.required=!0,this._filter=""}}h.styles=a.AH`
    :host {
      position: relative;
    }
    ha-select,
    ha-formfield {
      display: block;
    }
    ha-list-item[disabled] {
      --mdc-theme-text-primary-on-background: var(--disabled-text-color);
    }
    ha-chip-set {
      padding: 8px 0;
    }

    .label {
      display: block;
      margin: 0 0 8px;
    }

    ha-select-box + ha-input-helper-text {
      margin-top: 4px;
    }

    .sortable-fallback {
      display: none;
      opacity: 0;
    }

    .sortable-ghost {
      opacity: 0.4;
    }

    .sortable-drag {
      cursor: grabbing;
    }
  `,(0,i.__decorate)([(0,r.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],h.prototype,"selector",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],h.prototype,"localizeValue",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"required",void 0),(0,i.__decorate)([(0,r.P)("ha-combo-box",!0)],h.prototype,"comboBox",void 0),h=(0,i.__decorate)([(0,r.EM)("ha-selector-select")],h)},57674:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991),s=o(65940),n=o(21431),l=o(32556);const d={action:()=>Promise.all([o.e("6216"),o.e("1544"),o.e("8099"),o.e("5963"),o.e("615"),o.e("5831"),o.e("4443"),o.e("9236"),o.e("4580"),o.e("6013"),o.e("4258")]).then(o.bind(o,31257)),addon:()=>o.e("6253").then(o.bind(o,79084)),area:()=>o.e("3400").then(o.bind(o,87768)),areas_display:()=>o.e("3386").then(o.bind(o,75633)),attribute:()=>o.e("2532").then(o.bind(o,85263)),assist_pipeline:()=>o.e("1412").then(o.bind(o,22543)),boolean:()=>o.e("8808").then(o.bind(o,87835)),color_rgb:()=>o.e("7111").then(o.bind(o,10154)),condition:()=>Promise.all([o.e("6216"),o.e("1544"),o.e("8099"),o.e("5963"),o.e("615"),o.e("5831"),o.e("4443"),o.e("4580"),o.e("555")]).then(o.bind(o,5990)),config_entry:()=>o.e("2940").then(o.bind(o,58327)),conversation_agent:()=>o.e("7875").then(o.bind(o,65566)),constant:()=>o.e("9456").then(o.bind(o,30931)),country:()=>o.e("3866").then(o.bind(o,11441)),date:()=>o.e("4636").then(o.bind(o,25495)),datetime:()=>o.e("9603").then(o.bind(o,96318)),device:()=>o.e("4329").then(o.bind(o,26672)),duration:()=>o.e("1972").then(o.bind(o,3631)),entity:()=>Promise.all([o.e("615"),o.e("4797")]).then(o.bind(o,99888)),statistic:()=>Promise.all([o.e("615"),o.e("9460")]).then(o.bind(o,67261)),file:()=>o.e("3950").then(o.bind(o,57917)),floor:()=>o.e("183").then(o.bind(o,5034)),label:()=>Promise.all([o.e("9352"),o.e("9677")]).then(o.bind(o,89969)),image:()=>Promise.all([o.e("1092"),o.e("8311")]).then(o.bind(o,19654)),background:()=>Promise.all([o.e("1092"),o.e("8672")]).then(o.bind(o,86467)),language:()=>o.e("7682").then(o.bind(o,19785)),navigation:()=>o.e("1914").then(o.bind(o,31649)),number:()=>Promise.resolve().then(o.bind(o,87150)),object:()=>Promise.all([o.e("1544"),o.e("5831"),o.e("5857")]).then(o.bind(o,41480)),qr_code:()=>Promise.all([o.e("3033"),o.e("3513")]).then(o.bind(o,63136)),select:()=>Promise.resolve().then(o.bind(o,40027)),selector:()=>o.e("1563").then(o.bind(o,95414)),state:()=>o.e("6114").then(o.bind(o,62857)),backup_location:()=>o.e("4560").then(o.bind(o,50275)),stt:()=>o.e("6999").then(o.bind(o,30874)),target:()=>Promise.all([o.e("6735"),o.e("615"),o.e("6906")]).then(o.bind(o,66210)),template:()=>Promise.all([o.e("1544"),o.e("5831"),o.e("9715")]).then(o.bind(o,96957)),text:()=>Promise.resolve().then(o.bind(o,18664)),time:()=>o.e("7391").then(o.bind(o,39906)),icon:()=>o.e("4851").then(o.bind(o,80798)),media:()=>Promise.all([o.e("7951"),o.e("4641")]).then(o.bind(o,21971)),theme:()=>o.e("7757").then(o.bind(o,91004)),button_toggle:()=>o.e("1541").then(o.bind(o,50548)),trigger:()=>Promise.all([o.e("6216"),o.e("1544"),o.e("8099"),o.e("5963"),o.e("615"),o.e("5831"),o.e("4443"),o.e("9236"),o.e("4016")]).then(o.bind(o,24515)),tts:()=>o.e("5293").then(o.bind(o,4108)),tts_voice:()=>o.e("2566").then(o.bind(o,69205)),location:()=>Promise.all([o.e("1480"),o.e("6057")]).then(o.bind(o,96560)),color_temp:()=>Promise.all([o.e("3282"),o.e("6116")]).then(o.bind(o,27935)),ui_action:()=>Promise.all([o.e("1544"),o.e("5831"),o.e("6013"),o.e("4083")]).then(o.bind(o,96520)),ui_color:()=>o.e("6952").then(o.bind(o,12699)),ui_state_content:()=>Promise.all([o.e("9358"),o.e("4094")]).then(o.bind(o,91901))},c=new Set(["ui-action","ui-color"]);class h extends a.WF{async focus(){await this.updateComplete,this.renderRoot.querySelector("#selector")?.focus()}get _type(){const e=Object.keys(this.selector)[0];return c.has(e)?e.replace("-","_"):e}willUpdate(e){e.has("selector")&&this.selector&&d[this._type]?.()}render(){return a.qy`
      ${(0,n._)(`ha-selector-${this._type}`,{hass:this.hass,narrow:this.narrow,name:this.name,selector:this._handleLegacySelector(this.selector),value:this.value,label:this.label,placeholder:this.placeholder,disabled:this.disabled,required:this.required,helper:this.helper,context:this.context,localizeValue:this.localizeValue,id:"selector"})}
    `}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1,this.required=!0,this._handleLegacySelector=(0,s.A)((e=>{if("entity"in e)return(0,l.UU)(e);if("device"in e)return(0,l.tD)(e);const t=Object.keys(this.selector)[0];return c.has(t)?{[t.replace("-","_")]:e[t]}:e}))}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"narrow",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"name",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],h.prototype,"selector",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],h.prototype,"localizeValue",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"placeholder",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"required",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],h.prototype,"context",void 0),h=(0,i.__decorate)([(0,r.EM)("ha-selector")],h)},62351:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991);class s extends a.WF{render(){return a.qy`
      <div class="prefix-wrap">
        <slot name="prefix"></slot>
        <div
          class="body"
          ?two-line=${!this.threeLine}
          ?three-line=${this.threeLine}
        >
          <slot name="heading"></slot>
          <div class="secondary"><slot name="description"></slot></div>
        </div>
      </div>
      <div class="content"><slot></slot></div>
    `}constructor(...e){super(...e),this.narrow=!1,this.slim=!1,this.threeLine=!1,this.wrapHeading=!1}}s.styles=a.AH`
    :host {
      display: flex;
      padding: 0 16px;
      align-content: normal;
      align-self: auto;
      align-items: center;
    }
    .body {
      padding-top: 8px;
      padding-bottom: 8px;
      padding-left: 0;
      padding-inline-start: 0;
      padding-right: 16px;
      padding-inline-end: 16px;
      overflow: hidden;
      display: var(--layout-vertical_-_display, flex);
      flex-direction: var(--layout-vertical_-_flex-direction, column);
      justify-content: var(--layout-center-justified_-_justify-content, center);
      flex: var(--layout-flex_-_flex, 1);
      flex-basis: var(--layout-flex_-_flex-basis, 0.000000001px);
    }
    .body[three-line] {
      min-height: 88px;
    }
    :host(:not([wrap-heading])) body > * {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .body > .secondary {
      display: block;
      padding-top: 4px;
      font-family: var(
        --mdc-typography-body2-font-family,
        var(--mdc-typography-font-family, var(--ha-font-family-body))
      );
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      -webkit-font-smoothing: var(--ha-font-smoothing);
      -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
      font-weight: var(
        --mdc-typography-body2-font-weight,
        var(--ha-font-weight-normal)
      );
      line-height: normal;
      color: var(--secondary-text-color);
    }
    .body[two-line] {
      min-height: calc(72px - 16px);
      flex: 1;
    }
    .content {
      display: contents;
    }
    :host(:not([narrow])) .content {
      display: var(--settings-row-content-display, flex);
      justify-content: flex-end;
      flex: 1;
      min-width: 0;
      padding: 16px 0;
    }
    .content ::slotted(*) {
      width: var(--settings-row-content-width);
    }
    :host([narrow]) {
      align-items: normal;
      flex-direction: column;
      border-top: 1px solid var(--divider-color);
      padding-bottom: 8px;
    }
    ::slotted(ha-switch) {
      padding: 16px 0;
    }
    .secondary {
      white-space: normal;
    }
    .prefix-wrap {
      display: var(--settings-row-prefix-display);
    }
    :host([narrow]) .prefix-wrap {
      display: flex;
      align-items: center;
    }
    :host([slim]),
    :host([slim]) .content,
    :host([slim]) ::slotted(ha-switch) {
      padding: 0;
    }
    :host([slim]) .body {
      min-height: 0;
    }
  `,(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],s.prototype,"narrow",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],s.prototype,"slim",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"three-line"})],s.prototype,"threeLine",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"wrap-heading",reflect:!0})],s.prototype,"wrapHeading",void 0),s=(0,i.__decorate)([(0,r.EM)("ha-settings-row")],s)},45810:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),a=o(55188),r=o(84922),s=o(11991),n=o(90933),l=e([a]);a=(l.then?(await l)():l)[0];class d extends a.A{connectedCallback(){super.connectedCallback(),this.dir=n.G.document.dir}static get styles(){return[a.A.styles,r.AH`
        :host {
          --wa-form-control-activated-color: var(--ha-control-color);
          --track-size: var(--ha-slider-track-size, 4px);
          --marker-height: calc(var(--ha-slider-track-size, 4px) / 2);
          --marker-width: calc(var(--ha-slider-track-size, 4px) / 2);
          --wa-color-surface-default: var(--card-background-color);
          --wa-color-neutral-fill-normal: var(--disabled-color);
          --wa-tooltip-background-color: var(--secondary-background-color);
          --wa-tooltip-color: var(--primary-text-color);
          --wa-tooltip-font-family: var(
            --ha-tooltip-font-family,
            var(--ha-font-family-body)
          );
          --wa-tooltip-font-size: var(
            --ha-tooltip-font-size,
            var(--ha-font-size-s)
          );
          --wa-tooltip-font-weight: var(
            --ha-tooltip-font-weight,
            var(--ha-font-weight-normal)
          );
          --wa-tooltip-line-height: var(
            --ha-tooltip-line-height,
            var(--ha-line-height-condensed)
          );
          --wa-tooltip-padding: 8px;
          --wa-tooltip-border-radius: var(--ha-tooltip-border-radius, 4px);
          --wa-tooltip-arrow-size: var(--ha-tooltip-arrow-size, 8px);
          --wa-z-index-tooltip: var(--ha-tooltip-z-index, 1000);
          min-width: 100px;
          min-inline-size: 100px;
          width: 200px;
        }

        #thumb {
          border: none;
        }

        #slider:focus-visible:not(.disabled) #thumb,
        #slider:focus-visible:not(.disabled) #thumb-min,
        #slider:focus-visible:not(.disabled) #thumb-max {
          outline: var(--wa-focus-ring);
        }

        :host([size="medium"]) {
          --thumb-width: var(--ha-font-size-l, 1.25em);
          --thumb-height: var(--ha-font-size-l, 1.25em);
        }

        :host([size="small"]) {
          --thumb-width: var(--ha-font-size-m, 1em);
          --thumb-height: var(--ha-font-size-m, 1em);
        }
      `]}constructor(...e){super(...e),this.size="small",this.withTooltip=!0}}(0,i.__decorate)([(0,s.MZ)({reflect:!0})],d.prototype,"size",void 0),(0,i.__decorate)([(0,s.MZ)({type:Boolean,attribute:"with-tooltip"})],d.prototype,"withTooltip",void 0),d=(0,i.__decorate)([(0,s.EM)("ha-slider")],d),t()}catch(d){t(d)}}))},8115:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991),s=o(73120);class n extends a.WF{updated(e){e.has("disabled")&&(this.disabled?this._destroySortable():this._createSortable())}disconnectedCallback(){super.disconnectedCallback(),this._shouldBeDestroy=!0,setTimeout((()=>{this._shouldBeDestroy&&(this._destroySortable(),this._shouldBeDestroy=!1)}),1)}connectedCallback(){super.connectedCallback(),this._shouldBeDestroy=!1,this.hasUpdated&&!this.disabled&&this._createSortable()}createRenderRoot(){return this}render(){return this.noStyle?a.s6:a.qy`
      <style>
        .sortable-fallback {
          display: none !important;
        }

        .sortable-ghost {
          box-shadow: 0 0 0 2px var(--primary-color);
          background: rgba(var(--rgb-primary-color), 0.25);
          border-radius: 4px;
          opacity: 0.4;
        }

        .sortable-drag {
          border-radius: 4px;
          opacity: 1;
          background: var(--card-background-color);
          box-shadow: 0px 4px 8px 3px #00000026;
          cursor: grabbing;
        }
      </style>
    `}async _createSortable(){if(this._sortable)return;const e=this.children[0];if(!e)return;const t=(await Promise.all([o.e("9453"),o.e("4761")]).then(o.bind(o,89472))).default,i={scroll:!0,forceAutoScrollFallback:!0,scrollSpeed:20,animation:150,...this.options,onChoose:this._handleChoose,onStart:this._handleStart,onEnd:this._handleEnd,onUpdate:this._handleUpdate,onAdd:this._handleAdd,onRemove:this._handleRemove};this.draggableSelector&&(i.draggable=this.draggableSelector),this.handleSelector&&(i.handle=this.handleSelector),void 0!==this.invertSwap&&(i.invertSwap=this.invertSwap),this.group&&(i.group=this.group),this.filter&&(i.filter=this.filter),this._sortable=new t(e,i)}_destroySortable(){this._sortable&&(this._sortable.destroy(),this._sortable=void 0)}constructor(...e){super(...e),this.disabled=!1,this.noStyle=!1,this.invertSwap=!1,this.rollback=!0,this._shouldBeDestroy=!1,this._handleUpdate=e=>{(0,s.r)(this,"item-moved",{newIndex:e.newIndex,oldIndex:e.oldIndex})},this._handleAdd=e=>{(0,s.r)(this,"item-added",{index:e.newIndex,data:e.item.sortableData,item:e.item})},this._handleRemove=e=>{(0,s.r)(this,"item-removed",{index:e.oldIndex})},this._handleEnd=async e=>{(0,s.r)(this,"drag-end"),this.rollback&&e.item.placeholder&&(e.item.placeholder.replaceWith(e.item),delete e.item.placeholder)},this._handleStart=()=>{(0,s.r)(this,"drag-start")},this._handleChoose=e=>{this.rollback&&(e.item.placeholder=document.createComment("sort-placeholder"),e.item.after(e.item.placeholder))}}}(0,i.__decorate)([(0,r.MZ)({type:Boolean})],n.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"no-style"})],n.prototype,"noStyle",void 0),(0,i.__decorate)([(0,r.MZ)({type:String,attribute:"draggable-selector"})],n.prototype,"draggableSelector",void 0),(0,i.__decorate)([(0,r.MZ)({type:String,attribute:"handle-selector"})],n.prototype,"handleSelector",void 0),(0,i.__decorate)([(0,r.MZ)({type:String,attribute:"filter"})],n.prototype,"filter",void 0),(0,i.__decorate)([(0,r.MZ)({type:String})],n.prototype,"group",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"invert-swap"})],n.prototype,"invertSwap",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],n.prototype,"options",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],n.prototype,"rollback",void 0),n=(0,i.__decorate)([(0,r.EM)("ha-sortable")],n)},71622:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),a=o(68640),r=o(84922),s=o(11991),n=e([a]);a=(n.then?(await n)():n)[0];class l extends a.A{updated(e){if(super.updated(e),e.has("size"))switch(this.size){case"tiny":this.style.setProperty("--ha-spinner-size","16px");break;case"small":this.style.setProperty("--ha-spinner-size","28px");break;case"medium":this.style.setProperty("--ha-spinner-size","48px");break;case"large":this.style.setProperty("--ha-spinner-size","68px");break;case void 0:this.style.removeProperty("--ha-progress-ring-size")}}static get styles(){return[a.A.styles,r.AH`
        :host {
          --indicator-color: var(
            --ha-spinner-indicator-color,
            var(--primary-color)
          );
          --track-color: var(--ha-spinner-divider-color, var(--divider-color));
          --track-width: 4px;
          --speed: 3.5s;
          font-size: var(--ha-spinner-size, 48px);
        }
      `]}}(0,i.__decorate)([(0,s.MZ)()],l.prototype,"size",void 0),l=(0,i.__decorate)([(0,s.EM)("ha-spinner")],l),t()}catch(l){t(l)}}))},95635:function(e,t,o){o.r(t),o.d(t,{HaSvgIcon:()=>s});var i=o(69868),a=o(84922),r=o(11991);class s extends a.WF{render(){return a.JW`
    <svg
      viewBox=${this.viewBox||"0 0 24 24"}
      preserveAspectRatio="xMidYMid meet"
      focusable="false"
      role="img"
      aria-hidden="true"
    >
      <g>
        ${this.path?a.JW`<path class="primary-path" d=${this.path}></path>`:a.s6}
        ${this.secondaryPath?a.JW`<path class="secondary-path" d=${this.secondaryPath}></path>`:a.s6}
      </g>
    </svg>`}}s.styles=a.AH`
    :host {
      display: var(--ha-icon-display, inline-flex);
      align-items: center;
      justify-content: center;
      position: relative;
      vertical-align: middle;
      fill: var(--icon-primary-color, currentcolor);
      width: var(--mdc-icon-size, 24px);
      height: var(--mdc-icon-size, 24px);
    }
    svg {
      width: 100%;
      height: 100%;
      pointer-events: none;
      display: block;
    }
    path.primary-path {
      opacity: var(--icon-primary-opactity, 1);
    }
    path.secondary-path {
      fill: var(--icon-secondary-color, currentcolor);
      opacity: var(--icon-secondary-opactity, 0.5);
    }
  `,(0,i.__decorate)([(0,r.MZ)()],s.prototype,"path",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],s.prototype,"secondaryPath",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],s.prototype,"viewBox",void 0),s=(0,i.__decorate)([(0,r.EM)("ha-svg-icon")],s)},18944:function(e,t,o){o.d(t,{L3:()=>a,dj:()=>n,gs:()=>r,uG:()=>s});var i=o(90963);o(52435);const a=(e,t)=>e.callWS({type:"config/area_registry/create",...t}),r=(e,t,o)=>e.callWS({type:"config/area_registry/update",area_id:t,...o}),s=(e,t)=>e.callWS({type:"config/area_registry/delete",area_id:t}),n=(e,t)=>(o,a)=>{const r=t?t.indexOf(o):-1,s=t?t.indexOf(a):-1;if(-1===r&&-1===s){const t=e?.[o]?.name??o,r=e?.[a]?.name??a;return(0,i.xL)(t,r)}return-1===r?1:-1===s?-1:r-s}},6041:function(e,t,o){o.d(t,{FB:()=>i,fk:()=>r,g2:()=>a});o(90963);const i=(e,t,o)=>e.callWS({type:"config/device_registry/update",device_id:t,...o}),a=e=>{const t={};for(const o of e)o.device_id&&(o.device_id in t||(t[o.device_id]=[]),t[o.device_id].push(o));return t},r=(e,t,o,i)=>{const a={};for(const r of t){const t=e[r.entity_id];t?.domain&&null!==r.device_id&&(a[r.device_id]=a[r.device_id]||new Set,a[r.device_id].add(t.domain))}if(o&&i)for(const r of o)for(const e of r.config_entries){const t=i.find((t=>t.entry_id===e));t?.domain&&(a[r.id]=a[r.id]||new Set,a[r.id].add(t.domain))}return a}},32556:function(e,t,o){o.d(t,{DF:()=>u,Lo:()=>y,MH:()=>d,MM:()=>v,Qz:()=>p,Ru:()=>g,UU:()=>m,_7:()=>h,bZ:()=>c,m0:()=>l,tD:()=>b,vX:()=>_});var i=o(26846),a=o(7556),r=o(68775),s=o(5940),n=o(6041);const l=(e,t,o,i,a,r,s)=>{const n=[],l=[],d=[];return Object.values(o).forEach((o=>{o.labels.includes(t)&&p(e,a,i,o.area_id,r,s)&&d.push(o.area_id)})),Object.values(i).forEach((o=>{o.labels.includes(t)&&u(e,Object.values(a),o,r,s)&&l.push(o.id)})),Object.values(a).forEach((o=>{o.labels.includes(t)&&v(e.states[o.entity_id],r,s)&&n.push(o.entity_id)})),{areas:d,devices:l,entities:n}},d=(e,t,o,i,a)=>{const r=[];return Object.values(o).forEach((o=>{o.floor_id===t&&p(e,e.entities,e.devices,o.area_id,i,a)&&r.push(o.area_id)})),{areas:r}},c=(e,t,o,i,a,r)=>{const s=[],n=[];return Object.values(o).forEach((o=>{o.area_id===t&&u(e,Object.values(i),o,a,r)&&n.push(o.id)})),Object.values(i).forEach((o=>{o.area_id===t&&v(e.states[o.entity_id],a,r)&&s.push(o.entity_id)})),{devices:n,entities:s}},h=(e,t,o,i,a)=>{const r=[];return Object.values(o).forEach((o=>{o.device_id===t&&v(e.states[o.entity_id],i,a)&&r.push(o.entity_id)})),{entities:r}},p=(e,t,o,i,a,r)=>!!Object.values(o).some((o=>!(o.area_id!==i||!u(e,Object.values(t),o,a,r))))||Object.values(t).some((t=>!(t.area_id!==i||!v(e.states[t.entity_id],a,r)))),u=(e,t,o,a,r)=>{const s=r?(0,n.fk)(r,t):void 0;if(a.target?.device&&!(0,i.e)(a.target.device).some((e=>_(e,o,s))))return!1;if(a.target?.entity){return t.filter((e=>e.device_id===o.id)).some((t=>{const o=e.states[t.entity_id];return v(o,a,r)}))}return!0},v=(e,t,o)=>!!e&&(!t.target?.entity||(0,i.e)(t.target.entity).some((t=>g(t,e,o)))),_=(e,t,o)=>{const{manufacturer:i,model:a,model_id:r,integration:s}=e;return(!i||t.manufacturer===i)&&((!a||t.model===a)&&((!r||t.model_id===r)&&!(s&&o&&!o?.[t.id]?.has(s))))},g=(e,t,o)=>{const{domain:s,device_class:n,supported_features:l,integration:d}=e;if(s){const e=(0,a.t)(t);if(Array.isArray(s)?!s.includes(e):e!==s)return!1}if(n){const e=t.attributes.device_class;if(e&&Array.isArray(n)?!n.includes(e):e!==n)return!1}return!(l&&!(0,i.e)(l).some((e=>(0,r.$)(t,e))))&&(!d||o?.[t.entity_id]?.domain===d)},m=e=>{if(!e.entity)return{entity:null};if("filter"in e.entity)return e;const{domain:t,integration:o,device_class:i,...a}=e.entity;return t||o||i?{entity:{...a,filter:{domain:t,integration:o,device_class:i}}}:{entity:a}},b=e=>{if(!e.device)return{device:null};if("filter"in e.device)return e;const{integration:t,manufacturer:o,model:i,...a}=e.device;return t||o||i?{device:{...a,filter:{integration:t,manufacturer:o,model:i}}}:{device:a}},y=e=>{let t;if("target"in e)t=(0,i.e)(e.target?.entity);else if("entity"in e){if(e.entity?.include_entities)return;t=(0,i.e)(e.entity?.filter)}if(!t)return;const o=t.flatMap((e=>e.integration||e.device_class||e.supported_features||!e.domain?[]:(0,i.e)(e.domain).filter((e=>(0,s.z)(e)))));return[...new Set(o)]}},95226:function(e,t,o){o.d(t,{Hg:()=>a,Wj:()=>r,jG:()=>i,ow:()=>s,zt:()=>n});var i=function(e){return e.language="language",e.system="system",e.comma_decimal="comma_decimal",e.decimal_comma="decimal_comma",e.space_comma="space_comma",e.none="none",e}({}),a=function(e){return e.language="language",e.system="system",e.am_pm="12",e.twenty_four="24",e}({}),r=function(e){return e.local="local",e.server="server",e}({}),s=function(e){return e.language="language",e.system="system",e.DMY="DMY",e.MDY="MDY",e.YMD="YMD",e}({}),n=function(e){return e.language="language",e.monday="monday",e.tuesday="tuesday",e.wednesday="wednesday",e.thursday="thursday",e.friday="friday",e.saturday="saturday",e.sunday="sunday",e}({})},52435:function(e,t,o){o(90963)},92491:function(e,t,o){o.a(e,(async function(e,i){try{o.r(t);var a=o(69868),r=o(84922),s=o(11991),n=o(68985),l=o(71622),d=(o(8101),o(3433),o(83566)),c=e([l]);l=(c.then?(await c)():c)[0];class h extends r.WF{render(){return r.qy`
      ${this.noToolbar?"":r.qy`<div class="toolbar">
            ${this.rootnav||history.state?.root?r.qy`
                  <ha-menu-button
                    .hass=${this.hass}
                    .narrow=${this.narrow}
                  ></ha-menu-button>
                `:r.qy`
                  <ha-icon-button-arrow-prev
                    .hass=${this.hass}
                    @click=${this._handleBack}
                  ></ha-icon-button-arrow-prev>
                `}
          </div>`}
      <div class="content">
        <ha-spinner></ha-spinner>
        ${this.message?r.qy`<div id="loading-text">${this.message}</div>`:r.s6}
      </div>
    `}_handleBack(){(0,n.O)()}static get styles(){return[d.RF,r.AH`
        :host {
          display: block;
          height: 100%;
          background-color: var(--primary-background-color);
        }
        .toolbar {
          display: flex;
          align-items: center;
          font-size: var(--ha-font-size-xl);
          height: var(--header-height);
          padding: 8px 12px;
          pointer-events: none;
          background-color: var(--app-header-background-color);
          font-weight: var(--ha-font-weight-normal);
          color: var(--app-header-text-color, white);
          border-bottom: var(--app-header-border-bottom, none);
          box-sizing: border-box;
        }
        @media (max-width: 599px) {
          .toolbar {
            padding: 4px;
          }
        }
        ha-menu-button,
        ha-icon-button-arrow-prev {
          pointer-events: auto;
        }
        .content {
          height: calc(100% - var(--header-height));
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }
        #loading-text {
          max-width: 350px;
          margin-top: 16px;
        }
      `]}constructor(...e){super(...e),this.noToolbar=!1,this.rootnav=!1,this.narrow=!1}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean,attribute:"no-toolbar"})],h.prototype,"noToolbar",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],h.prototype,"rootnav",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],h.prototype,"narrow",void 0),(0,a.__decorate)([(0,s.MZ)()],h.prototype,"message",void 0),h=(0,a.__decorate)([(0,s.EM)("hass-loading-screen")],h),i()}catch(h){i(h)}}))},13343:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991),s=o(81411),n=o(68985),l=(o(8101),o(3433),o(83566));class d extends a.WF{render(){return a.qy`
      <div class="toolbar">
        <div class="toolbar-content">
          ${this.mainPage||history.state?.root?a.qy`
                <ha-menu-button
                  .hassio=${this.supervisor}
                  .hass=${this.hass}
                  .narrow=${this.narrow}
                ></ha-menu-button>
              `:this.backPath?a.qy`
                  <a href=${this.backPath}>
                    <ha-icon-button-arrow-prev
                      .hass=${this.hass}
                    ></ha-icon-button-arrow-prev>
                  </a>
                `:a.qy`
                  <ha-icon-button-arrow-prev
                    .hass=${this.hass}
                    @click=${this._backTapped}
                  ></ha-icon-button-arrow-prev>
                `}

          <div class="main-title">
            <slot name="header">${this.header}</slot>
          </div>
          <slot name="toolbar-icon"></slot>
        </div>
      </div>
      <div class="content ha-scrollbar" @scroll=${this._saveScrollPos}>
        <slot></slot>
      </div>
      <div id="fab">
        <slot name="fab"></slot>
      </div>
    `}_saveScrollPos(e){this._savedScrollPos=e.target.scrollTop}_backTapped(){this.backCallback?this.backCallback():(0,n.O)()}static get styles(){return[l.dp,a.AH`
        :host {
          display: block;
          height: 100%;
          background-color: var(--primary-background-color);
          overflow: hidden;
          position: relative;
        }

        :host([narrow]) {
          width: 100%;
          position: fixed;
        }

        .toolbar {
          background-color: var(--app-header-background-color);
          padding-top: var(--safe-area-inset-top);
          padding-right: var(--safe-area-inset-right);
        }
        :host([narrow]) .toolbar {
          padding-left: var(--safe-area-inset-left);
        }

        .toolbar-content {
          display: flex;
          align-items: center;
          font-size: var(--ha-font-size-xl);
          height: var(--header-height);
          font-weight: var(--ha-font-weight-normal);
          color: var(--app-header-text-color, white);
          border-bottom: var(--app-header-border-bottom, none);
          box-sizing: border-box;
          padding: 8px 12px;
        }

        .toolbar a {
          color: var(--sidebar-text-color);
          text-decoration: none;
        }

        ha-menu-button,
        ha-icon-button-arrow-prev,
        ::slotted([slot="toolbar-icon"]) {
          pointer-events: auto;
          color: var(--sidebar-icon-color);
        }

        .main-title {
          margin: var(--margin-title);
          line-height: var(--ha-line-height-normal);
          min-width: 0;
          flex-grow: 1;
          overflow-wrap: break-word;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
          text-overflow: ellipsis;
          padding-bottom: 1px;
        }

        .content {
          position: relative;
          width: calc(100% - var(--safe-area-inset-right, 0px));
          height: calc(
            100% -
              1px - var(--header-height, 0px) - var(
                --safe-area-inset-top,
                0px
              ) - var(--safe-area-inset-bottom, 0px)
          );
          margin-bottom: var(--safe-area-inset-bottom);
          margin-right: var(--safe-area-inset-right);
          overflow-y: auto;
          overflow: auto;
          -webkit-overflow-scrolling: touch;
        }
        :host([narrow]) .content {
          width: calc(
            100% - var(--safe-area-inset-left, 0px) - var(
                --safe-area-inset-right,
                0px
              )
          );
          margin-left: var(--safe-area-inset-left);
        }

        #fab {
          position: absolute;
          right: calc(16px + var(--safe-area-inset-right, 0px));
          inset-inline-end: calc(16px + var(--safe-area-inset-right, 0px));
          inset-inline-start: initial;
          bottom: calc(16px + var(--safe-area-inset-bottom, 0px));
          z-index: 1;
          display: flex;
          flex-wrap: wrap;
          justify-content: flex-end;
          gap: 8px;
        }
        :host([narrow]) #fab.tabs {
          bottom: calc(84px + var(--safe-area-inset-bottom, 0px));
        }
        #fab[is-wide] {
          bottom: calc(24px + var(--safe-area-inset-bottom, 0px));
          right: calc(24px + var(--safe-area-inset-right, 0px));
          inset-inline-end: calc(24px + var(--safe-area-inset-right, 0px));
          inset-inline-start: initial;
        }
      `]}constructor(...e){super(...e),this.mainPage=!1,this.narrow=!1,this.supervisor=!1}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)()],d.prototype,"header",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"main-page"})],d.prototype,"mainPage",void 0),(0,i.__decorate)([(0,r.MZ)({type:String,attribute:"back-path"})],d.prototype,"backPath",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"backCallback",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],d.prototype,"narrow",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],d.prototype,"supervisor",void 0),(0,i.__decorate)([(0,s.a)(".content")],d.prototype,"_savedScrollPos",void 0),(0,i.__decorate)([(0,r.Ls)({passive:!0})],d.prototype,"_saveScrollPos",null),d=(0,i.__decorate)([(0,r.EM)("hass-subpage")],d)},59526:function(e,t,o){o.d(t,{J:()=>r});var i=o(73120);const a=()=>Promise.all([o.e("3062"),o.e("615"),o.e("1092"),o.e("9352"),o.e("3872")]).then(o.bind(o,384)),r=(e,t)=>{(0,i.r)(e,"show-dialog",{dialogTag:"dialog-area-registry-detail",dialogImport:a,dialogParams:t})}},5940:function(e,t,o){o.d(t,{z:()=>i});const i=(0,o(87383).g)(["input_boolean","input_button","input_text","input_number","input_datetime","input_select","counter","timer","schedule"])},65209:function(e,t,o){o.d(t,{b:()=>r});var i=o(88970);const a={ignoreDiacritics:!0,isCaseSensitive:!1,threshold:.3,minMatchCharLength:2};class r extends i.A{multiTermsSearch(e,t){const o=e.toLowerCase().split(" "),{minMatchCharLength:i}=this.options,a=i?o.filter((e=>e.length>=i)):o;if(0===a.length)return null;const r=this.getIndex().toJSON().keys,s={$and:a.map((e=>({$or:r.map((t=>({$path:t.path,$val:e})))})))};return this.search(s,t)}constructor(e,t,o){super(e,{...a,...t},o)}}},83566:function(e,t,o){o.d(t,{RF:()=>r,dp:()=>n,nA:()=>s,og:()=>a});var i=o(84922);const a=i.AH`
  button.link {
    background: none;
    color: inherit;
    border: none;
    padding: 0;
    font: inherit;
    text-align: left;
    text-decoration: underline;
    cursor: pointer;
    outline: none;
  }
`,r=i.AH`
  :host {
    font-family: var(--ha-font-family-body);
    -webkit-font-smoothing: var(--ha-font-smoothing);
    -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
    font-size: var(--ha-font-size-m);
    font-weight: var(--ha-font-weight-normal);
    line-height: var(--ha-line-height-normal);
  }

  app-header div[sticky] {
    height: 48px;
  }

  app-toolbar [main-title] {
    margin-left: 20px;
    margin-inline-start: 20px;
    margin-inline-end: initial;
  }

  h1 {
    font-family: var(--ha-font-family-heading);
    -webkit-font-smoothing: var(--ha-font-smoothing);
    -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
    font-size: var(--ha-font-size-2xl);
    font-weight: var(--ha-font-weight-normal);
    line-height: var(--ha-line-height-condensed);
  }

  h2 {
    font-family: var(--ha-font-family-body);
    -webkit-font-smoothing: var(--ha-font-smoothing);
    -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: var(--ha-font-size-xl);
    font-weight: var(--ha-font-weight-medium);
    line-height: var(--ha-line-height-normal);
  }

  h3 {
    font-family: var(--ha-font-family-body);
    -webkit-font-smoothing: var(--ha-font-smoothing);
    -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
    font-size: var(--ha-font-size-l);
    font-weight: var(--ha-font-weight-normal);
    line-height: var(--ha-line-height-normal);
  }

  a {
    color: var(--primary-color);
  }

  .secondary {
    color: var(--secondary-text-color);
  }

  .error {
    color: var(--error-color);
  }

  .warning {
    color: var(--error-color);
  }

  ${a}

  .card-actions a {
    text-decoration: none;
  }

  .card-actions .warning {
    --mdc-theme-primary: var(--error-color);
  }

  .layout.horizontal,
  .layout.vertical {
    display: flex;
  }
  .layout.inline {
    display: inline-flex;
  }
  .layout.horizontal {
    flex-direction: row;
  }
  .layout.vertical {
    flex-direction: column;
  }
  .layout.wrap {
    flex-wrap: wrap;
  }
  .layout.no-wrap {
    flex-wrap: nowrap;
  }
  .layout.center,
  .layout.center-center {
    align-items: center;
  }
  .layout.bottom {
    align-items: flex-end;
  }
  .layout.center-justified,
  .layout.center-center {
    justify-content: center;
  }
  .flex {
    flex: 1;
    flex-basis: 0.000000001px;
  }
  .flex-auto {
    flex: 1 1 auto;
  }
  .flex-none {
    flex: none;
  }
  .layout.justified {
    justify-content: space-between;
  }
`,s=i.AH`
  /* mwc-dialog (ha-dialog) styles */
  ha-dialog {
    --mdc-dialog-min-width: 400px;
    --mdc-dialog-max-width: 600px;
    --mdc-dialog-max-width: min(600px, 95vw);
    --justify-action-buttons: space-between;
  }

  ha-dialog .form {
    color: var(--primary-text-color);
  }

  a {
    color: var(--primary-color);
  }

  /* make dialog fullscreen on small screens */
  @media all and (max-width: 450px), all and (max-height: 500px) {
    ha-dialog {
      --mdc-dialog-min-width: 100vw;
      --mdc-dialog-max-width: 100vw;
      --mdc-dialog-min-height: 100%;
      --mdc-dialog-max-height: 100%;
      --vertical-align-dialog: flex-end;
      --ha-dialog-border-radius: 0;
    }
  }
  .error {
    color: var(--error-color);
  }
`,n=i.AH`
  .ha-scrollbar::-webkit-scrollbar {
    width: 0.4rem;
    height: 0.4rem;
  }

  .ha-scrollbar::-webkit-scrollbar-thumb {
    -webkit-border-radius: 4px;
    border-radius: 4px;
    background: var(--scrollbar-thumb-color);
  }

  .ha-scrollbar {
    overflow-y: auto;
    scrollbar-color: var(--scrollbar-thumb-color) transparent;
    scrollbar-width: thin;
  }
`;i.AH`
  body {
    background-color: var(--primary-background-color);
    color: var(--primary-text-color);
    height: calc(100vh - 32px);
    width: 100vw;
  }
`},43537:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{Y:()=>c});var a=o(84922),r=(o(23749),o(86853),o(99741),o(40027),o(18664)),s=o(71739),n=o(44817),l=o(58228),d=e([r,s]);[r,s]=d.then?(await d)():d;const c=(e,t,o,i,r=e=>e)=>{const s=t.device_info?(0,n.OM)(e,t.device_info):void 0,d=s?s.name_by_user??s.name:"",c=(0,l.W)(i);return a.qy`
    <ha-card outlined>
      <h1 class="card-header">${r("entity.title")}</h1>
      <p class="card-content">${r("entity.description")}</p>
      ${i&&c?a.qy`<ha-alert
              .alertType=${"error"}
              .title=${c.error_message}
            ></ha-alert>`:a.s6}
      <ha-expansion-panel
        header=${r("entity.name_title")}
        secondary=${r("entity.name_description")}
        expanded
        .noCollapse=${!0}
      >
        <knx-device-picker
          .hass=${e}
          .key=${"entity.device_info"}
          .helper=${r("entity.device_description")}
          .value=${t.device_info??void 0}
          @value-changed=${o}
        ></knx-device-picker>
        <ha-selector-text
          .hass=${e}
          label=${r("entity.entity_label")}
          helper=${r("entity.entity_description")}
          .required=${!s}
          .selector=${{text:{type:"text",prefix:d}}}
          .key=${"entity.name"}
          .value=${t.name}
          @value-changed=${o}
        ></ha-selector-text>
      </ha-expansion-panel>
      <ha-expansion-panel .header=${r("entity.entity_category_title")} outlined>
        <ha-selector-select
          .hass=${e}
          .label=${r("entity.entity_category_title")}
          .helper=${r("entity.entity_category_description")}
          .required=${!1}
          .selector=${{select:{multiple:!1,custom_value:!1,mode:"dropdown",options:[{value:"config",label:e.localize("ui.panel.config.devices.entities.config")},{value:"diagnostic",label:e.localize("ui.panel.config.devices.entities.diagnostic")}]}}}
          .key=${"entity.entity_category"}
          .value=${t.entity_category}
          @value-changed=${o}
        ></ha-selector-select>
      </ha-expansion-panel>
    </ha-card>
  `};i()}catch(c){i(c)}}))},52190:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),a=o(84922),r=o(11991),s=o(7622),n=o(7577),l=(o(23749),o(86853),o(72659),o(95635),o(99741),o(57674),o(62351),o(90933)),d=o(73120),c=(o(86552),o(22014),o(17782)),h=o(43537),p=o(92095),u=o(21762),v=o(58228),_=o(33110),g=e([c,_,h]);[c,_,h]=g.then?(await g)():g;const m=new p.Q("knx-configure-entity");class b extends a.WF{connectedCallback(){if(super.connectedCallback(),this.platformStyle=(0,_.N)(this.platform),!this.config){this.config={entity:{},knx:{}};const e=new URLSearchParams(l.G.location.search),t=Object.fromEntries(e.entries());for(const[o,i]of Object.entries(t))(0,u.F)(this.config,o,i,m),(0,d.r)(this,"knx-entity-configuration-changed",this.config)}}render(){const e=(0,v.a)(this.validationErrors,"data"),t=(0,v.a)(e,"knx"),o=(0,v.W)(t);return a.qy`
      <div class="header">
        <h1>
          <ha-svg-icon
            .path=${this.platformStyle.iconPath}
            style=${(0,n.W)({"background-color":this.platformStyle.color})}
          ></ha-svg-icon>
          ${this.hass.localize(`component.${this.platform}.title`)||this.platform}
        </h1>
        <p>${this._backendLocalize("description")}</p>
      </div>
      <slot name="knx-validation-error"></slot>
      <ha-card outlined>
        <h1 class="card-header">${this._backendLocalize("knx.title")}</h1>
        ${o?a.qy`<ha-alert .alertType=${"error"} .title=${o.error_message}></ha-alert>`:a.s6}
        ${this.generateRootGroups(this.schema,t)}
      </ha-card>
      ${(0,h.Y)(this.hass,this.config.entity??{},this._updateConfig,(0,v.a)(e,"entity"),this._backendLocalize)}
    `}generateRootGroups(e,t){return this._generateItems(e,"knx",t)}_generateSection(e,t,o){const i=(0,v.W)(o);return a.qy` <ha-expansion-panel
      .header=${this._backendLocalize(`${t}.title`)}
      .secondary=${this._backendLocalize(`${t}.description`)}
      .expanded=${!e.collapsible||this._groupHasGroupAddressInConfig(e,t)}
      .noCollapse=${!e.collapsible}
      .outlined=${!!e.collapsible}
    >
      ${i?a.qy` <ha-alert .alertType=${"error"} .title=${"Validation error"}>
            ${i.error_message}
          </ha-alert>`:a.s6}
      ${this._generateItems(e.schema,t,o)}
    </ha-expansion-panel>`}_generateGroupSelect(e,t,o){const i=(0,v.W)(o);t in this._selectedGroupSelectOptions||(this._selectedGroupSelectOptions[t]=this._getOptionIndex(e,t));const r=this._selectedGroupSelectOptions[t],n=e.schema[r];void 0===n&&m.error("No option for index",r,e.schema);const l=e.schema.map(((e,o)=>({value:o.toString(),label:this._backendLocalize(`${t}.options.${e.translation_key}.label`)})));return a.qy` <ha-expansion-panel
      .header=${this._backendLocalize(`${t}.title`)}
      .secondary=${this._backendLocalize(`${t}.description`)}
      .expanded=${!e.collapsible||this._groupHasGroupAddressInConfig(e,t)}
      .noCollapse=${!e.collapsible}
      outlined
    >
      ${i?a.qy` <ha-alert .alertType=${"error"} .title=${"Validation error"}>
            ${i.error_message}
          </ha-alert>`:a.s6}
      <ha-control-select
        .options=${l}
        .value=${r.toString()}
        .key=${t}
        @value-changed=${this._updateGroupSelectOption}
      ></ha-control-select>
      ${n?a.qy` <p class="group-description">
              ${this._backendLocalize(`${t}.options.${n.translation_key}.description`)}
            </p>
            <div class="group-selection">
              ${(0,s.D)(r,this._generateItems(n.schema,t,o))}
            </div>`:a.s6}
    </ha-expansion-panel>`}_generateItems(e,t,o){const i=[];let r,s=[];const n=()=>{if(0===s.length||void 0===r)return;const e=t+"."+r.name,n=!r.collapsible||s.some((e=>"knx_group_address"===e.type&&this._hasGroupAddressInConfig(e,t)));i.push(a.qy`<ha-expansion-panel
          .header=${this._backendLocalize(`${e}.title`)}
          .secondary=${this._backendLocalize(`${e}.description`)}
          .expanded=${n}
          .noCollapse=${!r.collapsible}
          .outlined=${!!r.collapsible}
        >
          ${s.map((e=>this._generateItem(e,t,o)))}
        </ha-expansion-panel> `),s=[]};for(const a of e)"knx_section_flat"!==a.type?(["knx_section","knx_group_select","knx_sync_state"].includes(a.type)&&(n(),r=void 0),void 0===r?i.push(this._generateItem(a,t,o)):s.push(a)):(n(),r=a);return n(),i}_generateItem(e,t,o){const i=t+"."+e.name,r=(0,v.a)(o,e.name);switch(e.type){case"knx_section":return this._generateSection(e,i,r);case"knx_group_select":return this._generateGroupSelect(e,i,r);case"knx_group_address":return a.qy`
          <knx-group-address-selector
            .hass=${this.hass}
            .knx=${this.knx}
            .key=${i}
            .label=${this._backendLocalize(`${i}.label`)}
            .config=${(0,u.L)(this.config,i)??{}}
            .options=${e.options}
            .validationErrors=${r}
            .localizeFunction=${this._backendLocalize}
            @value-changed=${this._updateConfig}
          ></knx-group-address-selector>
        `;case"knx_sync_state":return a.qy`
          <ha-expansion-panel
            .header=${this._backendLocalize(`${i}.title`)}
            .secondary=${this._backendLocalize(`${i}.description`)}
            .outlined=${!0}
          >
            <knx-sync-state-selector-row
              .hass=${this.hass}
              .key=${i}
              .value=${(0,u.L)(this.config,i)??!0}
              .allowFalse=${e.allow_false}
              .localizeFunction=${this._backendLocalize}
              @value-changed=${this._updateConfig}
            ></knx-sync-state-selector-row>
          </ha-expansion-panel>
        `;case"ha_selector":return a.qy`
          <knx-selector-row
            .hass=${this.hass}
            .key=${i}
            .selector=${e}
            .value=${(0,u.L)(this.config,i)}
            .validationErrors=${r}
            .localizeFunction=${this._backendLocalize}
            @value-changed=${this._updateConfig}
          ></knx-selector-row>
        `;default:return m.error("Unknown selector type",e),a.s6}}_groupHasGroupAddressInConfig(e,t){return void 0!==this.config&&("knx_group_select"===e.type?!!(0,u.L)(this.config,t):e.schema.some((e=>{if("knx_group_address"===e.type)return this._hasGroupAddressInConfig(e,t);if("knx_section"===e.type||"knx_group_select"===e.type){const o=t+"."+e.name;return this._groupHasGroupAddressInConfig(e,o)}return!1})))}_hasGroupAddressInConfig(e,t){const o=(0,u.L)(this.config,t+"."+e.name);return!!o&&(void 0!==o.write||(void 0!==o.state||!!o.passive?.length))}_getRequiredKeys(e){const t=[];return e.forEach((e=>{"knx_section"!==e.type?("knx_group_address"===e.type&&e.required||"ha_selector"===e.type&&e.required)&&t.push(e.name):t.push(...this._getRequiredKeys(e.schema))})),t}_getOptionIndex(e,t){const o=(0,u.L)(this.config,t);if(void 0===o)return m.debug("No config found for group select",t),0;const i=e.schema.findIndex((e=>{const i=this._getRequiredKeys(e.schema);return 0===i.length?(m.warn("No required keys for GroupSelect option",t,e),!1):i.every((e=>e in o))}));return-1===i?(m.debug("No valid option found for group select",t,o),0):i}_updateGroupSelectOption(e){e.stopPropagation();const t=e.target.key,o=parseInt(e.detail.value,10);(0,u.F)(this.config,t,void 0,m),this._selectedGroupSelectOptions[t]=o,(0,d.r)(this,"knx-entity-configuration-changed",this.config),this.requestUpdate()}_updateConfig(e){e.stopPropagation();const t=e.target.key,o=e.detail.value;(0,u.F)(this.config,t,o,m),(0,d.r)(this,"knx-entity-configuration-changed",this.config),this.requestUpdate()}constructor(...e){super(...e),this._selectedGroupSelectOptions={},this._backendLocalize=e=>this.hass.localize(`component.knx.config_panel.entities.create.${this.platform}.${e}`)||this.hass.localize(`component.knx.config_panel.entities.create._.${e}`)}}b.styles=a.AH`
    p {
      color: var(--secondary-text-color);
    }

    .header {
      color: var(--ha-card-header-color, --primary-text-color);
      font-family: var(--ha-card-header-font-family, inherit);
      padding: 0 16px 16px;

      & h1 {
        display: inline-flex;
        align-items: center;
        font-size: 26px;
        letter-spacing: -0.012em;
        line-height: 48px;
        font-weight: normal;
        margin-bottom: 14px;

        & ha-svg-icon {
          color: var(--text-primary-color);
          padding: 8px;
          background-color: var(--blue-color);
          border-radius: 50%;
          margin-right: 8px;
        }
      }

      & p {
        margin-top: -8px;
        line-height: 24px;
      }
    }

    ::slotted(ha-alert) {
      margin-top: 0 !important;
    }

    ha-card {
      margin-bottom: 24px;
      padding: 16px;

      & .card-header {
        display: inline-flex;
        align-items: center;
      }
    }

    ha-expansion-panel {
      margin-bottom: 16px;
    }
    ha-expansion-panel > :first-child:not(ha-settings-row) {
      margin-top: 16px; /* ha-settings-row has this margin internally */
    }
    ha-expansion-panel > ha-settings-row:first-child,
    ha-expansion-panel > knx-selector-row:first-child {
      border: 0;
    }
    ha-expansion-panel > * {
      margin-left: 8px;
      margin-right: 8px;
    }

    ha-settings-row {
      margin-bottom: 8px;
      padding: 0;
    }
    ha-control-select {
      padding: 0;
      margin-left: 0;
      margin-right: 0;
      margin-bottom: 16px;
    }

    .group-description {
      align-items: center;
      margin-top: -8px;
      padding-left: 8px;
      padding-bottom: 8px;
    }

    .group-selection {
      padding-left: 8px;
      padding-right: 8px;
      & ha-settings-row:first-child {
        border-top: 0;
      }
    }

    knx-group-address-selector,
    ha-selector,
    ha-selector-text,
    ha-selector-select,
    knx-sync-state-selector-row,
    knx-device-picker {
      display: block;
      margin-bottom: 16px;
    }

    ha-alert {
      display: block;
      margin: 20px auto;
      max-width: 720px;

      & summary {
        padding: 10px;
      }
    }
  `,(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"knx",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"platform",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"config",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"schema",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"validationErrors",void 0),(0,i.__decorate)([(0,r.wk)()],b.prototype,"_selectedGroupSelectOptions",void 0),b=(0,i.__decorate)([(0,r.EM)("knx-configure-entity")],b),t()}catch(m){t(m)}}))},71739:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),a=o(84922),r=o(11991),s=o(75907),n=o(65940),l=(o(26731),o(25223),o(34977)),d=o(73120),c=o(86098),h=o(90963),p=o(44817),u=e([l]);l=(u.then?(await u)():u)[0];const v=e=>a.qy`<ha-list-item
    class=${(0,s.H)({"add-new":"add_new"===e.id})}
    .twoline=${!!e.area}
  >
    <span>${e.name}</span>
    <span slot="secondary">${e.area}</span>
  </ha-list-item>`;class _ extends a.WF{async _addDevice(e){const t=[...(0,p.L0)(this.hass),e],o=this._getDevices(t,this.hass.areas);this.comboBox.items=o,this.comboBox.filteredItems=o,await this.updateComplete,await this.comboBox.updateComplete}async open(){await this.updateComplete,await(this.comboBox?.open())}async focus(){await this.updateComplete,await(this.comboBox?.focus())}updated(e){if(!this._init&&this.hass||this._init&&e.has("_opened")&&this._opened){this._init=!0;const e=this._getDevices((0,p.L0)(this.hass),this.hass.areas),t=this.value?e.find((e=>e.identifier===this.value))?.id:void 0;this.comboBox.value=t,this._deviceId=t,this.comboBox.items=e,this.comboBox.filteredItems=e}}render(){return a.qy`
      <ha-combo-box
        .hass=${this.hass}
        .label=${void 0===this.label&&this.hass?this.hass.localize("ui.components.device-picker.device"):this.label}
        .helper=${this.helper}
        .value=${this._deviceId}
        .renderer=${v}
        item-id-path="id"
        item-value-path="id"
        item-label-path="name"
        @filter-changed=${this._filterChanged}
        @opened-changed=${this._openedChanged}
        @value-changed=${this._deviceChanged}
      ></ha-combo-box>
      ${this._showCreateDeviceDialog?this._renderCreateDeviceDialog():a.s6}
    `}_filterChanged(e){const t=e.target,o=e.detail.value;if(!o)return void(this.comboBox.filteredItems=this.comboBox.items);const i=(0,c.H)(o,t.items||[]);this._suggestion=o,this.comboBox.filteredItems=[...i,{id:"add_new_suggestion",name:`Add new device '${this._suggestion}'`}]}_openedChanged(e){this._opened=e.detail.value}_deviceChanged(e){e.stopPropagation();let t=e.detail.value;"no_devices"===t&&(t=""),["add_new_suggestion","add_new"].includes(t)?(e.target.value=this._deviceId,this._openCreateDeviceDialog()):t!==this._deviceId&&this._setValue(t)}_setValue(e){const t=this.comboBox.items.find((t=>t.id===e)),o=t?.identifier;this.value=o,this._deviceId=t?.id,setTimeout((()=>{(0,d.r)(this,"value-changed",{value:o}),(0,d.r)(this,"change")}),0)}_renderCreateDeviceDialog(){return a.qy`
      <knx-device-create-dialog
        .hass=${this.hass}
        @create-device-dialog-closed=${this._closeCreateDeviceDialog}
        .deviceName=${this._suggestion}
      ></knx-device-create-dialog>
    `}_openCreateDeviceDialog(){this._showCreateDeviceDialog=!0}async _closeCreateDeviceDialog(e){const t=e.detail.newDevice;t?await this._addDevice(t):this.comboBox.setInputValue(""),this._setValue(t?.id),this._suggestion=void 0,this._showCreateDeviceDialog=!1}constructor(...e){super(...e),this._showCreateDeviceDialog=!1,this._init=!1,this._getDevices=(0,n.A)(((e,t)=>[{id:"add_new",name:"Add new device…",area:"",strings:[]},...e.map((e=>{const o=e.name_by_user??e.name??"";return{id:e.id,identifier:(0,p.dd)(e),name:o,area:e.area_id&&t[e.area_id]?t[e.area_id].name:this.hass.localize("ui.components.device-picker.no_area"),strings:[o||""]}})).sort(((e,t)=>(0,h.xL)(e.name||"",t.name||"",this.hass.locale.language)))]))}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)()],_.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],_.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)()],_.prototype,"value",void 0),(0,i.__decorate)([(0,r.wk)()],_.prototype,"_opened",void 0),(0,i.__decorate)([(0,r.P)("ha-combo-box",!0)],_.prototype,"comboBox",void 0),(0,i.__decorate)([(0,r.wk)()],_.prototype,"_showCreateDeviceDialog",void 0),_=(0,i.__decorate)([(0,r.EM)("knx-device-picker")],_),t()}catch(v){t(v)}}))},86552:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991),s=o(75907),n=o(97809),l=o(65940),d=(o(25223),o(40027),o(93672),o(73120));o(52893),o(56292);class c extends a.WF{render(){return a.qy`
      <div>
        ${this.label??a.s6}
        ${this.options.map((e=>a.qy`
            <div class="formfield">
              <ha-radio
                .checked=${e.value===this.value}
                .value=${e.value}
                .disabled=${this.disabled}
                @change=${this._valueChanged}
              ></ha-radio>
              <label .value=${e.value} @click=${this._valueChanged}>
                <p>
                  ${this.localizeValue(this.translation_key+".options."+e.translation_key)}
                </p>
                <p class="secondary">DPT ${e.value}</p>
              </label>
            </div>
          `))}
        ${this.invalidMessage?a.qy`<p class="invalid-message">${this.invalidMessage}</p>`:a.s6}
      </div>
    `}_valueChanged(e){e.stopPropagation();const t=e.target.value;this.disabled||void 0===t||t===(this.value??"")||(0,d.r)(this,"value-changed",{value:t})}constructor(...e){super(...e),this.disabled=!1,this.invalid=!1,this.localizeValue=e=>e}}c.styles=[a.AH`
      :host([invalid]) div {
        color: var(--error-color);
      }

      .formfield {
        display: flex;
        align-items: center;
      }

      label {
        min-width: 200px; /* to make it easier to click */
      }

      p {
        pointer-events: none;
        color: var(--primary-text-color);
        margin: 0px;
      }

      .secondary {
        padding-top: 4px;
        font-family: var(
          --mdc-typography-body2-font-family,
          var(--mdc-typography-font-family, Roboto, sans-serif)
        );
        -webkit-font-smoothing: antialiased;
        font-size: var(--mdc-typography-body2-font-size, 0.875rem);
        font-weight: var(--mdc-typography-body2-font-weight, 400);
        line-height: normal;
        color: var(--secondary-text-color);
      }

      .invalid-message {
        font-size: 0.75rem;
        color: var(--error-color);
        padding-left: 16px;
      }
    `],(0,i.__decorate)([(0,r.MZ)({type:Array})],c.prototype,"options",void 0),(0,i.__decorate)([(0,r.MZ)()],c.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],c.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],c.prototype,"invalid",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],c.prototype,"invalidMessage",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],c.prototype,"localizeValue",void 0),(0,i.__decorate)([(0,r.MZ)({type:String})],c.prototype,"translation_key",void 0),c=(0,i.__decorate)([(0,r.EM)("knx-dpt-selector")],c);var h=o(39913),p=o(39635),u=o(58228),v=o(93060);const _=e=>e.map((e=>({value:e.address,label:`${e.address} - ${e.name}`})));class g extends a.WF{getValidGroupAddresses(e){return this.knx.projectData?Object.values(this.knx.projectData.group_addresses).filter((t=>!!t.dpt&&(0,p.HG)(t.dpt,e))):[]}getDptOptionByValue(e){return e?this.options.dptSelect?.find((t=>t.value===e)):void 0}shouldUpdate(e){return!(1===e.size&&e.has("hass"))}willUpdate(e){if(e.has("options")&&(this.validGroupAddresses=this.getValidGroupAddresses(this.options.validDPTs??this.options.dptSelect?.map((e=>e.dpt))??[]),this.filteredGroupAddresses=this.validGroupAddresses,this.addressOptions=_(this.filteredGroupAddresses)),e.has("config")){this._selectedDPTValue=this.config.dpt??this._selectedDPTValue;const e=this.getDptOptionByValue(this._selectedDPTValue)?.dpt;if(this.setFilteredGroupAddresses(e),e&&this.knx.projectData){const t=[this.config.write,this.config.state,...this.config.passive??[]].filter((e=>null!=e));this.dptSelectorDisabled=t.length>0&&t.every((t=>{const o=this.knx.projectData.group_addresses[t]?.dpt;return!!o&&(0,p.HG)(o,[e])}))}else this.dptSelectorDisabled=!1}this._validGADropTarget=this._dragDropContext?.groupAddress?this.filteredGroupAddresses.includes(this._dragDropContext.groupAddress):void 0}updated(e){e.has("validationErrors")&&this._gaSelectors.forEach((async e=>{await e.updateComplete;const t=(0,u.W)(this.validationErrors,e.key);e.comboBox.errorMessage=t?.error_message,e.comboBox.invalid=!!t}))}render(){const e=this.config.passive&&this.config.passive.length>0,t=!0===this._validGADropTarget,o=!1===this._validGADropTarget,i=(0,u.W)(this.validationErrors),r=this.localizeFunction(this.key+".description");return a.qy`
      ${i?a.qy`<p class="error">
            <ha-svg-icon .path=${"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z"}></ha-svg-icon>
            <b>Validation error:</b>
            ${i.error_message}
          </p>`:a.s6}
      <div class="main">
        <div class="selectors">
          ${this.options.write?a.qy`<ha-selector-select
                class=${(0,s.H)({"valid-drop-zone":t,"invalid-drop-zone":o})}
                .hass=${this.hass}
                .label=${this._baseTranslation("send_address")+(this.label?` - ${this.label}`:"")}
                .required=${this.options.write.required}
                .selector=${{select:{multiple:!1,custom_value:!0,options:this.addressOptions}}}
                .key=${"write"}
                .value=${this.config.write}
                @value-changed=${this._updateConfig}
                @dragover=${this._dragOverHandler}
                @drop=${this._dropHandler}
              ></ha-selector-select>`:a.s6}
          ${this.options.state?a.qy`<ha-selector-select
                class=${(0,s.H)({"valid-drop-zone":t,"invalid-drop-zone":o})}
                .hass=${this.hass}
                .label=${this._baseTranslation("state_address")+(this.label?` - ${this.label}`:"")}
                .required=${this.options.state.required}
                .selector=${{select:{multiple:!1,custom_value:!0,options:this.addressOptions}}}
                .key=${"state"}
                .value=${this.config.state}
                @value-changed=${this._updateConfig}
                @dragover=${this._dragOverHandler}
                @drop=${this._dropHandler}
              ></ha-selector-select>`:a.s6}
        </div>
        <div class="options">
          <ha-icon-button
            .disabled=${!!e}
            .path=${this._showPassive?"M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z":"M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z"}
            .label=${"Toggle passive address visibility"}
            @click=${this._togglePassiveVisibility}
          ></ha-icon-button>
        </div>
      </div>
      <div
        class="passive ${(0,s.H)({expanded:e||this._showPassive})}"
        @transitionend=${this._handleTransitionEnd}
      >
        <ha-selector-select
          class=${(0,s.H)({"valid-drop-zone":t,"invalid-drop-zone":o})}
          .hass=${this.hass}
          .label=${this._baseTranslation("passive_addresses")+(this.label?` - ${this.label}`:"")}
          .required=${!1}
          .selector=${{select:{multiple:!0,custom_value:!0,options:this.addressOptions}}}
          .key=${"passive"}
          .value=${this.config.passive}
          @value-changed=${this._updateConfig}
          @dragover=${this._dragOverHandler}
          @drop=${this._dropHandler}
        ></ha-selector-select>
      </div>
      ${r?a.qy`<p class="description">${r}</p>`:a.s6}
      ${this.options.validDPTs?a.qy`<p class="valid-dpts">
            ${this._baseTranslation("valid_dpts")}:
            ${this.options.validDPTs.map((e=>(0,v.Vt)(e))).join(", ")}
          </p>`:a.s6}
      ${this.options.dptSelect?this._renderDptSelector():a.s6}
    `}_renderDptSelector(){const e=(0,u.W)(this.validationErrors,"dpt");return a.qy`<knx-dpt-selector
      .key=${"dpt"}
      .label=${this._baseTranslation("dpt")}
      .options=${this.options.dptSelect}
      .value=${this._selectedDPTValue}
      .disabled=${this.dptSelectorDisabled}
      .invalid=${!!e}
      .invalidMessage=${e?.error_message}
      .localizeValue=${this.localizeFunction}
      .translation_key=${this.key}
      @value-changed=${this._updateConfig}
    >
    </knx-dpt-selector>`}_updateConfig(e){e.stopPropagation();const t=e.target,o=e.detail.value,i={...this.config,[t.key]:o},a=!!(i.write||i.state||i.passive?.length);this._updateDptSelector(t.key,i,a),this.config=i;const r=a?i:void 0;(0,d.r)(this,"value-changed",{value:r}),this.requestUpdate()}_updateDptSelector(e,t,o){if(!this.options.dptSelect)return;if("dpt"===e)this._selectedDPTValue=t.dpt;else{if(!o)return t.dpt=void 0,void(this._selectedDPTValue=void 0);t.dpt=this._selectedDPTValue}if(!this.knx.projectData)return;const i=this._getAddedGroupAddress(e,t);if(!i||void 0!==this._selectedDPTValue)return;const a=this.validGroupAddresses.find((e=>e.address===i))?.dpt;if(!a)return;const r=this.options.dptSelect.find((e=>e.dpt.main===a.main&&e.dpt.sub===a.sub));t.dpt=r?r.value:this.options.dptSelect.find((e=>(0,p.HG)(a,[e.dpt])))?.value}_getAddedGroupAddress(e,t){return"write"===e||"state"===e?t[e]:"passive"===e?t.passive?.find((e=>!this.config.passive?.includes(e))):void 0}_togglePassiveVisibility(e){e.stopPropagation(),e.preventDefault();const t=!this._showPassive;this._passiveContainer.style.overflow="hidden";const o=this._passiveContainer.scrollHeight;this._passiveContainer.style.height=`${o}px`,t||setTimeout((()=>{this._passiveContainer.style.height="0px"}),0),this._showPassive=t}_handleTransitionEnd(){this._passiveContainer.style.removeProperty("height"),this._passiveContainer.style.overflow=this._showPassive?"initial":"hidden"}_dragOverHandler(e){if(![...e.dataTransfer.types].includes("text/group-address"))return;e.preventDefault(),e.dataTransfer.dropEffect="move";const t=e.target;this._dragOverTimeout[t.key]?clearTimeout(this._dragOverTimeout[t.key]):t.classList.add("active-drop-zone"),this._dragOverTimeout[t.key]=setTimeout((()=>{delete this._dragOverTimeout[t.key],t.classList.remove("active-drop-zone")}),100)}_dropHandler(e){const t=e.dataTransfer.getData("text/group-address");if(!t)return;e.stopPropagation(),e.preventDefault();const o=e.target,i={...this.config};if(o.selector.select.multiple){const e=[...this.config[o.key]??[],t];i[o.key]=e}else i[o.key]=t;this._updateDptSelector(o.key,i),(0,d.r)(this,"value-changed",{value:i}),setTimeout((()=>o.comboBox._inputElement.blur()))}constructor(...e){super(...e),this.config={},this.localizeFunction=e=>e,this._showPassive=!1,this.validGroupAddresses=[],this.filteredGroupAddresses=[],this.addressOptions=[],this.dptSelectorDisabled=!1,this._dragOverTimeout={},this._baseTranslation=e=>this.hass.localize(`component.knx.config_panel.entities.create._.knx.knx_group_address.${e}`),this.setFilteredGroupAddresses=(0,l.A)((e=>{this.filteredGroupAddresses=e?this.getValidGroupAddresses([e]):this.validGroupAddresses,this.addressOptions=_(this.filteredGroupAddresses)}))}}g.styles=a.AH`
    .main {
      display: flex;
      flex-direction: row;
    }

    .selectors {
      flex: 1;
      padding-right: 16px;
    }

    .options {
      width: 48px;
      display: flex;
      flex-direction: column-reverse;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }

    .passive {
      overflow: hidden;
      transition: height 150ms cubic-bezier(0.4, 0, 0.2, 1);
      height: 0px;
      margin-right: 64px; /* compensate for .options */
    }

    .passive.expanded {
      height: auto;
    }

    .description,
    .valid-dpts {
      margin-top: -8px;
      margin-bottom: 12px;
      margin-left: 16px;
      margin-right: 64px;
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
    }

    ha-selector-select {
      display: block;
      margin-bottom: 16px;
      transition:
        box-shadow 250ms,
        opacity 250ms;
    }

    .valid-drop-zone {
      box-shadow: 0px 0px 5px 2px rgba(var(--rgb-primary-color), 0.5);
    }

    .valid-drop-zone.active-drop-zone {
      box-shadow: 0px 0px 5px 2px var(--primary-color);
    }

    .invalid-drop-zone {
      opacity: 0.5;
    }

    .invalid-drop-zone.active-drop-zone {
      box-shadow: 0px 0px 5px 2px var(--error-color);
    }

    .error {
      color: var(--error-color);
    }
  `,(0,i.__decorate)([(0,n.Fg)({context:h.B,subscribe:!0})],g.prototype,"_dragDropContext",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"knx",void 0),(0,i.__decorate)([(0,r.MZ)()],g.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"config",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"options",void 0),(0,i.__decorate)([(0,r.MZ)({reflect:!0})],g.prototype,"key",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"validationErrors",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"localizeFunction",void 0),(0,i.__decorate)([(0,r.wk)()],g.prototype,"_showPassive",void 0),(0,i.__decorate)([(0,r.P)(".passive")],g.prototype,"_passiveContainer",void 0),(0,i.__decorate)([(0,r.YG)("ha-selector-select")],g.prototype,"_gaSelectors",void 0),g=(0,i.__decorate)([(0,r.EM)("knx-group-address-selector")],g)},29349:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991),s=o(33055),n=o(97809),l=(o(23749),o(95635),o(92095)),d=o(39913),c=o(39635),h=o(93060);const p=new l.Q("knx-project-device-tree");class u extends a.WF{connectedCallback(){super.connectedCallback();const e=this.validDPTs?.length?(0,c.Ah)(this.data,this.validDPTs):this.data.communication_objects,t=Object.values(this.data.devices).map((t=>{const o=[],i=Object.fromEntries(Object.entries(t.channels).map((([e,t])=>[e,{name:t.name,comObjects:[]}])));for(const r of t.communication_object_ids){if(!(r in e))continue;const t=e[r];t.channel&&t.channel in i?i[t.channel].comObjects.push(t):o.push(t)}const a=Object.entries(i).reduce(((e,[t,o])=>(o.comObjects.length&&(e[t]=o),e)),{});return{ia:t.individual_address,name:t.name,manufacturer:t.manufacturer_name,description:t.description.split(/[\r\n]/,1)[0],noChannelComObjects:o,channels:a}}));this.deviceTree=t.filter((e=>!!e.noChannelComObjects.length||!!Object.keys(e.channels).length))}render(){return a.qy`<div class="device-tree-view">
      ${this._selectedDevice?this._renderSelectedDevice(this._selectedDevice):this._renderDevices()}
    </div>`}_renderDevices(){return this.deviceTree.length?a.qy`<ul class="devices">
      ${(0,s.u)(this.deviceTree,(e=>e.ia),(e=>a.qy`<li class="clickable" @click=${this._selectDevice} .device=${e}>
            ${this._renderDevice(e)}
          </li>`))}
    </ul>`:a.qy`<ha-alert alert-type="info">No suitable device found in project data.</ha-alert>`}_renderDevice(e){return a.qy`<div class="item">
      <span class="icon ia">
        <ha-svg-icon .path=${"M15,20A1,1 0 0,0 14,19H13V17H17A2,2 0 0,0 19,15V5A2,2 0 0,0 17,3H7A2,2 0 0,0 5,5V15A2,2 0 0,0 7,17H11V19H10A1,1 0 0,0 9,20H2V22H9A1,1 0 0,0 10,23H14A1,1 0 0,0 15,22H22V20H15M7,15V5H17V15H7Z"}></ha-svg-icon>
        <span>${e.ia}</span>
      </span>
      <div class="description">
        <p>${e.manufacturer}</p>
        <p>${e.name}</p>
        ${e.description?a.qy`<p>${e.description}</p>`:a.s6}
      </div>
    </div>`}_renderSelectedDevice(e){return a.qy`<ul class="selected-device">
      <li class="back-item clickable" @click=${this._selectDevice}>
        <div class="item">
          <ha-svg-icon class="back-icon" .path=${"M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z"}></ha-svg-icon>
          ${this._renderDevice(e)}
        </div>
      </li>
      ${this._renderChannels(e)}
    </ul>`}_renderChannels(e){return a.qy`${this._renderComObjects(e.noChannelComObjects)}
    ${(0,s.u)(Object.entries(e.channels),(([t,o])=>`${e.ia}_ch_${t}`),(([e,t])=>t.comObjects.length?a.qy`<li class="channel">${t.name}</li>
              ${this._renderComObjects(t.comObjects)}`:a.s6))} `}_renderComObjects(e){return a.qy`${(0,s.u)(e,(e=>`${e.device_address}_co_${e.number}`),(e=>{return a.qy`<li class="com-object">
          <div class="item">
            <span class="icon co"
              ><ha-svg-icon .path=${"M22 12C22 6.5 17.5 2 12 2S2 6.5 2 12 6.5 22 12 22 22 17.5 22 12M15 6.5L18.5 10L15 13.5V11H11V9H15V6.5M9 17.5L5.5 14L9 10.5V13H13V15H9V17.5Z"}></ha-svg-icon
              ><span>${e.number}</span></span
            >
            <div class="description">
              <p>
                ${e.text}${e.function_text?" - "+e.function_text:""}
              </p>
              <p class="co-info">${t=e.flags,`${t.read?"R":"–"} ${t.write?"W":"–"} ${t.transmit?"T":"–"} ${t.update?"U":"–"}`}</p>
            </div>
          </div>
          <ul class="group-addresses">
            ${this._renderGroupAddresses(e.group_address_links)}
          </ul>
        </li>`;var t}))} `}_renderGroupAddresses(e){const t=e.map((e=>this.data.group_addresses[e]));return a.qy`${(0,s.u)(t,(e=>e.identifier),(e=>a.qy`<li
          draggable="true"
          @dragstart=${this._dragDropContext?.gaDragStartHandler}
          @dragend=${this._dragDropContext?.gaDragEndHandler}
          @mouseover=${this._dragDropContext?.gaDragIndicatorStartHandler}
          @focus=${this._dragDropContext?.gaDragIndicatorStartHandler}
          @mouseout=${this._dragDropContext?.gaDragIndicatorEndHandler}
          @blur=${this._dragDropContext?.gaDragIndicatorEndHandler}
          .ga=${e}
        >
          <div class="item">
            <ha-svg-icon
              class="drag-icon"
              .path=${"M9,3H11V5H9V3M13,3H15V5H13V3M9,7H11V9H9V7M13,7H15V9H13V7M9,11H11V13H9V11M13,11H15V13H13V11M9,15H11V17H9V15M13,15H15V17H13V15M9,19H11V21H9V19M13,19H15V21H13V19Z"}
              .viewBox=${"4 0 16 24"}
            ></ha-svg-icon>
            <span class="icon ga">
              <span>${e.address}</span>
            </span>
            <div class="description">
              <p>${e.name}</p>
              <p class="ga-info">${(e=>{const t=(0,h.Vt)(e.dpt);return t?`DPT ${t}`:""})(e)}</p>
            </div>
          </div>
        </li>`))} `}_selectDevice(e){const t=e.target.device;p.debug("select device",t),this._selectedDevice=t,this.scrollTop=0}constructor(...e){super(...e),this.deviceTree=[]}}u.styles=a.AH`
    :host {
      display: block;
      box-sizing: border-box;
      margin: 0;
      height: 100%;
      overflow-y: scroll;
      overflow-x: hidden;
      background-color: var(--sidebar-background-color);
      color: var(--sidebar-menu-button-text-color, --primary-text-color);
      margin-right: env(safe-area-inset-right);
      border-left: 1px solid var(--divider-color);
      padding-left: 8px;
    }

    ha-alert {
      display: block;
      margin-right: 8px;
      margin-top: 8px;
    }

    ul {
      list-style-type: none;
      padding: 0;
      margin-block-start: 8px;
    }

    li {
      display: block;
      margin-bottom: 4px;
      & div.item {
        /* icon and text */
        display: flex;
        align-items: center;
        pointer-events: none;
        & > div {
          /* optional container for multiple paragraphs */
          min-width: 0;
          width: 100%;
        }
      }
    }

    li p {
      margin: 0;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }

    span.icon {
      flex: 0 0 auto;
      display: inline-flex;
      /* align-self: stretch; */
      align-items: center;

      color: var(--text-primary-color);
      font-size: 1rem;
      font-weight: 700;
      border-radius: 12px;
      padding: 3px 6px;
      margin-right: 4px;

      & > ha-svg-icon {
        float: left;
        width: 16px;
        height: 16px;
        margin-right: 4px;
      }

      & > span {
        /* icon text */
        flex: 1;
        text-align: center;
      }
    }

    span.ia {
      flex-basis: 70px;
      background-color: var(--label-badge-grey);
      & > ha-svg-icon {
        transform: rotate(90deg);
      }
    }

    span.co {
      flex-basis: 44px;
      background-color: var(--amber-color);
    }

    span.ga {
      flex-basis: 54px;
      background-color: var(--knx-green);
    }

    .description {
      margin-top: 4px;
      margin-bottom: 4px;
    }

    p.co-info,
    p.ga-info {
      font-size: 0.85rem;
      font-weight: 300;
    }

    .back-item {
      margin-left: -8px; /* revert host padding to have gapless border */
      padding-left: 8px;
      margin-top: -8px; /* revert ul margin-block-start to have gapless hover effect */
      padding-top: 8px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--divider-color);
      margin-bottom: 8px;
    }

    .back-icon {
      margin-right: 8px;
      color: var(--label-badge-grey);
    }

    li.channel {
      border-top: 1px solid var(--divider-color);
      border-bottom: 1px solid var(--divider-color);
      padding: 4px 16px;
      font-weight: 500;
    }

    li.clickable {
      cursor: pointer;
    }
    li.clickable:hover {
      background-color: rgba(var(--rgb-primary-text-color), 0.04);
    }

    li[draggable="true"] {
      cursor: grab;
    }
    li[draggable="true"]:hover {
      border-radius: 12px;
      background-color: rgba(var(--rgb-primary-color), 0.2);
    }

    ul.group-addresses {
      margin-top: 0;
      margin-bottom: 8px;

      & > li:not(:first-child) {
        /* passive addresses for this com-object */
        opacity: 0.8;
      }
    }
  `,(0,i.__decorate)([(0,n.Fg)({context:d.B})],u.prototype,"_dragDropContext",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],u.prototype,"data",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],u.prototype,"validDPTs",void 0),(0,i.__decorate)([(0,r.wk)()],u.prototype,"_selectedDevice",void 0),u=(0,i.__decorate)([(0,r.EM)("knx-project-device-tree")],u)},22014:function(e,t,o){var i=o(69868),a=o(84922),r=o(11991),s=o(75907),n=o(73120),l=(o(71978),o(57674),o(43143),o(58228));class d extends a.WF{willUpdate(e){if(e.has("selector")||e.has("key")){this._disabled=!this.selector.required&&void 0===this.value,this._haSelectorValue=this.value??this.selector.default??null;const e="boolean"in this.selector.selector,t=e||"number"in this.selector.selector;this._inlineSelector=!!this.selector.required&&t,this._optionalBooleanSelector=!this.selector.required&&e,this._optionalBooleanSelector&&(this._haSelectorValue=!0)}}render(){const e=(0,l.W)(this.validationErrors),t=this._optionalBooleanSelector?a.s6:a.qy`<ha-selector
          class=${(0,s.H)({"newline-selector":!this._inlineSelector})}
          .hass=${this.hass}
          .selector=${this.selector.selector}
          .disabled=${this._disabled}
          .value=${this._haSelectorValue}
          .localizeValue=${this.hass.localize}
          @value-changed=${this._valueChange}
        ></ha-selector>`;return a.qy`
      <div class="body">
        <div class="text">
          <p class="heading ${(0,s.H)({invalid:!!e})}">
            ${this.localizeFunction(`${this.key}.label`)}
          </p>
          <p class="description">${this.localizeFunction(`${this.key}.description`)}</p>
        </div>
        ${this.selector.required?a.s6:a.qy`<ha-selector
              class="optional-switch"
              .selector=${{boolean:{}}}
              .value=${!this._disabled}
              @value-changed=${this._toggleDisabled}
            ></ha-selector>`}
        ${this._inlineSelector?t:a.s6}
      </div>
      ${this._inlineSelector?a.s6:t}
      ${e?a.qy`<p class="invalid-message">${e.error_message}</p>`:a.s6}
    `}_toggleDisabled(e){e.stopPropagation(),this._disabled=!this._disabled,this._propagateValue()}_valueChange(e){e.stopPropagation(),this._haSelectorValue=e.detail.value,this._propagateValue()}_propagateValue(){(0,n.r)(this,"value-changed",{value:this._disabled?void 0:this._haSelectorValue})}constructor(...e){super(...e),this.localizeFunction=e=>e,this._disabled=!1,this._haSelectorValue=null,this._inlineSelector=!1,this._optionalBooleanSelector=!1}}d.styles=a.AH`
    :host {
      display: block;
      padding: 8px 16px 8px 0;
      border-top: 1px solid var(--divider-color);
    }
    .newline-selector {
      display: block;
      padding-top: 8px;
    }
    .body {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      row-gap: 8px;
    }
    .body > * {
      flex-grow: 1;
    }
    .text {
      flex-basis: 260px; /* min size of text - if inline selector is too big it will be pushed to next row */
    }
    .heading {
      margin: 0;
    }
    .description {
      margin: 0;
      display: block;
      padding-top: 4px;
      font-family: var(
        --mdc-typography-body2-font-family,
        var(--mdc-typography-font-family, Roboto, sans-serif)
      );
      -webkit-font-smoothing: antialiased;
      font-size: var(--mdc-typography-body2-font-size, 0.875rem);
      font-weight: var(--mdc-typography-body2-font-weight, 400);
      line-height: normal;
      color: var(--secondary-text-color);
    }

    .invalid {
      color: var(--error-color);
    }
    .invalid-message {
      font-size: 0.75rem;
      color: var(--error-color);
      padding-left: 16px;
    }
  `,(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)()],d.prototype,"key",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"selector",void 0),(0,i.__decorate)([(0,r.MZ)()],d.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"validationErrors",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"localizeFunction",void 0),(0,i.__decorate)([(0,r.wk)()],d.prototype,"_disabled",void 0),d=(0,i.__decorate)([(0,r.EM)("knx-selector-row")],d)},17782:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),a=o(84922),r=o(11991),s=o(73120),n=o(87150),l=(o(40027),e([n]));n=(l.then?(await l)():l)[0];class d extends a.WF{get _options(){return this.allowFalse?[!0,"init","expire","every",!1]:[!0,"init","expire","every"]}_hasMinutes(e){return"expire"===e||"every"===e}willUpdate(){if("boolean"==typeof this.value)return void(this._strategy=this.value);const[e,t]=this.value.split(" ");this._strategy=e,+t&&(this._minutes=+t)}render(){return a.qy` <div class="inline">
      <ha-selector-select
        .hass=${this.hass}
        .label=${this.localizeFunction(`${this.key}.title`)}
        .localizeValue=${this.localizeFunction}
        .selector=${{select:{translation_key:this.key,multiple:!1,custom_value:!1,mode:"dropdown",options:this._options}}}
        .key=${"strategy"}
        .value=${this._strategy}
        @value-changed=${this._handleChange}
      >
      </ha-selector-select>
      <ha-selector-number
        .hass=${this.hass}
        .disabled=${!this._hasMinutes(this._strategy)}
        .selector=${{number:{min:2,max:1440,step:1,unit_of_measurement:"minutes"}}}
        .key=${"minutes"}
        .value=${this._minutes}
        @value-changed=${this._handleChange}
      >
      </ha-selector-number>
    </div>`}_handleChange(e){let t,o;e.stopPropagation(),"strategy"===e.target.key?(t=e.detail.value,o=this._minutes):(t=this._strategy,o=e.detail.value);const i=this._hasMinutes(t)?`${t} ${o}`:t;(0,s.r)(this,"value-changed",{value:i})}constructor(...e){super(...e),this.value=!0,this.key="sync_state",this.allowFalse=!1,this.localizeFunction=e=>e,this._strategy=!0,this._minutes=60}}d.styles=a.AH`
    .description {
      margin: 0;
      display: block;
      padding-top: 4px;
      padding-bottom: 8px;
      font-family: var(
        --mdc-typography-body2-font-family,
        var(--mdc-typography-font-family, Roboto, sans-serif)
      );
      -webkit-font-smoothing: antialiased;
      font-size: var(--mdc-typography-body2-font-size, 0.875rem);
      font-weight: var(--mdc-typography-body2-font-weight, 400);
      line-height: normal;
      color: var(--secondary-text-color);
    }
    .inline {
      width: 100%;
      display: inline-flex;
      flex-flow: row wrap;
      gap: 16px;
      justify-content: space-between;
    }
    .inline > * {
      flex: 1;
      width: 100%; /* to not overflow when wrapped */
    }
  `,(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)()],d.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],d.prototype,"key",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"allowFalse",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"localizeFunction",void 0),d=(0,i.__decorate)([(0,r.EM)("knx-sync-state-selector-row")],d),t()}catch(d){t(d)}}))},34977:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),a=o(84922),r=o(11991),s=o(68985),n=(o(44249),o(72847),o(76943)),l=o(18664),d=o(73120),c=o(83566),h=o(49432),p=o(92095),u=e([n,l]);[n,l]=u.then?(await u)():u;const v=new p.Q("create_device_dialog");class _ extends a.WF{closeDialog(e){(0,d.r)(this,"create-device-dialog-closed",{newDevice:this._deviceEntry},{bubbles:!1})}_createDevice(){(0,h.Jv)(this.hass,{name:this.deviceName,area_id:this.area}).then((e=>{this._deviceEntry=e})).catch((e=>{v.error("getGroupMonitorInfo",e),(0,s.o)("/knx/error",{replace:!0,data:e})})).finally((()=>{this.closeDialog(void 0)}))}render(){return a.qy`<ha-dialog
      open
      .heading=${"Create new device"}
      scrimClickAction
      escapeKeyAction
      defaultAction="ignore"
    >
      <ha-selector-text
        .hass=${this.hass}
        .label=${"Name"}
        .required=${!0}
        .selector=${{text:{}}}
        .key=${"deviceName"}
        .value=${this.deviceName}
        @value-changed=${this._valueChanged}
      ></ha-selector-text>
      <ha-area-picker
        .hass=${this.hass}
        .label=${"Area"}
        .key=${"area"}
        .value=${this.area}
        @value-changed=${this._valueChanged}
      >
      </ha-area-picker>
      <ha-button slot="secondaryAction" @click=${this.closeDialog}>
        ${this.hass.localize("ui.common.cancel")}
      </ha-button>
      <ha-button slot="primaryAction" @click=${this._createDevice}>
        ${this.hass.localize("ui.common.add")}
      </ha-button>
    </ha-dialog>`}_valueChanged(e){e.stopPropagation();const t=e.target;t?.key&&(this[t.key]=e.detail.value)}static get styles(){return[c.nA,a.AH`
        @media all and (min-width: 600px) {
          ha-dialog {
            --mdc-dialog-min-width: 480px;
          }
        }
      `]}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],_.prototype,"deviceName",void 0),(0,i.__decorate)([(0,r.wk)()],_.prototype,"area",void 0),_=(0,i.__decorate)([(0,r.EM)("knx-device-create-dialog")],_),t()}catch(v){t(v)}}))},33110:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{N:()=>l});var a=o(93327),r=e([a]);a=(r.then?(await r)():r)[0];const n={binary_sensor:{iconPath:"M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2M10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z",color:"var(--green-color)"},button:{iconPath:"M20 20.5C20 21.3 19.3 22 18.5 22H13C12.6 22 12.3 21.9 12 21.6L8 17.4L8.7 16.6C8.9 16.4 9.2 16.3 9.5 16.3H9.7L12 18V9C12 8.4 12.4 8 13 8S14 8.4 14 9V13.5L15.2 13.6L19.1 15.8C19.6 16 20 16.6 20 17.1V20.5M20 2H4C2.9 2 2 2.9 2 4V12C2 13.1 2.9 14 4 14H8V12H4V4H20V12H18V14H20C21.1 14 22 13.1 22 12V4C22 2.9 21.1 2 20 2Z",color:"var(--purple-color)"},climate:{color:"var(--red-color)"},cover:{iconPath:"M3 4H21V8H19V20H17V8H7V20H5V8H3V4M8 9H16V11H8V9M8 12H16V14H8V12M8 15H16V17H8V15M8 18H16V20H8V18Z",color:"var(--cyan-color)"},date:{color:"var(--lime-color)"},event:{iconPath:"M13 11H11V5H13M13 15H11V13H13M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z",color:"var(--deep-orange-color)"},fan:{iconPath:"M12,11A1,1 0 0,0 11,12A1,1 0 0,0 12,13A1,1 0 0,0 13,12A1,1 0 0,0 12,11M12.5,2C17,2 17.11,5.57 14.75,6.75C13.76,7.24 13.32,8.29 13.13,9.22C13.61,9.42 14.03,9.73 14.35,10.13C18.05,8.13 22.03,8.92 22.03,12.5C22.03,17 18.46,17.1 17.28,14.73C16.78,13.74 15.72,13.3 14.79,13.11C14.59,13.59 14.28,14 13.88,14.34C15.87,18.03 15.08,22 11.5,22C7,22 6.91,18.42 9.27,17.24C10.25,16.75 10.69,15.71 10.89,14.79C10.4,14.59 9.97,14.27 9.65,13.87C5.96,15.85 2,15.07 2,11.5C2,7 5.56,6.89 6.74,9.26C7.24,10.25 8.29,10.68 9.22,10.87C9.41,10.39 9.73,9.97 10.14,9.65C8.15,5.96 8.94,2 12.5,2Z",color:"var(--light-grey-color)"},light:{color:"var(--amber-color)"},notify:{color:"var(--pink-color)"},number:{color:"var(--teal-color)"},scene:{color:"var(--deep-purple-color)"},select:{color:"var(--indigo-color)"},sensor:{color:"var(--orange-color)"},switch:{iconPath:"M18.4 1.6C18 1.2 17.5 1 17 1H7C6.5 1 6 1.2 5.6 1.6C5.2 2 5 2.5 5 3V21C5 21.5 5.2 22 5.6 22.4C6 22.8 6.5 23 7 23H17C17.5 23 18 22.8 18.4 22.4C18.8 22 19 21.5 19 21V3C19 2.5 18.8 2 18.4 1.6M16 7C16 7.6 15.6 8 15 8H9C8.4 8 8 7.6 8 7V5C8 4.4 8.4 4 9 4H15C15.6 4 16 4.4 16 5V7Z",color:"var(--blue-color)"},text:{color:"var(--brown-color)"},time:{color:"var(--light-green-color)"},valve:{iconPath:"M4 22H2V2H4M22 2H20V22H22M17.24 5.34L13.24 9.34A3 3 0 0 0 9.24 13.34L5.24 17.34L6.66 18.76L10.66 14.76A3 3 0 0 0 14.66 10.76L18.66 6.76Z",color:"var(--light-blue-color)"},weather:{color:"var(--yellow-color)"}};function l(e){return{iconPath:a.l[e],color:"var(--dark-grey-color)",...n[e]}}i()}catch(s){i(s)}}))},21762:function(e,t,o){function i(e,t,o,a){const r=t.split("."),s=r.pop();if(!s)return;let n=e;for(const i of r){if(!(i in n)){if(void 0===o)return;n[i]={}}n=n[i]}void 0===o?(a&&a.debug(`remove ${s} at ${t}`),delete n[s],!Object.keys(n).length&&r.length>0&&i(e,r.join("."),void 0)):(a&&a.debug(`update ${s} at ${t} with value`,o),n[s]=o)}function a(e,t){const o=t.split(".");let i=e;for(const a of o){if(!(a in i))return;i=i[a]}return i}o.d(t,{F:()=>i,L:()=>a})},44817:function(e,t,o){o.d(t,{L0:()=>r,OM:()=>s,dd:()=>n});const i=e=>"knx"===e[0],a=e=>e.identifiers.some(i),r=e=>Object.values(e.devices).filter(a),s=(e,t)=>Object.values(e.devices).find((e=>e.identifiers.find((e=>i(e)&&e[1]===t)))),n=e=>{const t=e.identifiers.find(i);return t?t[1]:void 0}},39635:function(e,t,o){o.d(t,{Ah:()=>r,HG:()=>a,Yb:()=>n});var i=o(65940);const a=(e,t)=>t.some((t=>e.main===t.main&&(!t.sub||e.sub===t.sub))),r=(e,t)=>{const o=((e,t)=>Object.entries(e.group_addresses).reduce(((e,[o,i])=>(i.dpt&&a(i.dpt,t)&&(e[o]=i),e)),{}))(e,t);return Object.entries(e.communication_objects).reduce(((e,[t,i])=>(i.group_address_links.some((e=>e in o))&&(e[t]=i),e)),{})};function s(e){const t=[];return e.forEach((e=>{"knx_group_address"!==e.type?"schema"in e&&t.push(...s(e.schema)):e.options.validDPTs?t.push(...e.options.validDPTs):e.options.dptSelect&&t.push(...e.options.dptSelect.map((e=>e.dpt)))})),t}const n=(0,i.A)((e=>s(e).reduce(((e,t)=>e.some((e=>{return i=t,(o=e).main===i.main&&o.sub===i.sub;var o,i}))?e:e.concat([t])),[])))},39913:function(e,t,o){o.d(t,{B:()=>n,J:()=>s});var i=o(97809);const a=new(o(92095).Q)("knx-drag-drop-context"),r=Symbol("drag-drop-context");class s{get groupAddress(){return this._groupAddress}constructor(e){this.gaDragStartHandler=e=>{const t=e.target,o=t.ga;o?(this._groupAddress=o,a.debug("dragstart",o.address,this),e.dataTransfer?.setData("text/group-address",o.address),this._updateObservers()):a.warn("dragstart: no 'ga' property found",t)},this.gaDragEndHandler=e=>{a.debug("dragend",this),this._groupAddress=void 0,this._updateObservers()},this.gaDragIndicatorStartHandler=e=>{const t=e.target.ga;t&&(this._groupAddress=t,a.debug("drag indicator start",t.address,this),this._updateObservers())},this.gaDragIndicatorEndHandler=e=>{a.debug("drag indicator end",this),this._groupAddress=void 0,this._updateObservers()},this._updateObservers=e}}const n=(0,i.q6)(r)},58228:function(e,t,o){o.d(t,{W:()=>a,a:()=>i});const i=(e,t)=>{if(!e)return;const o=[];for(const i of e)if(i.path){const[e,...a]=i.path;e===t&&o.push({...i,path:a})}return o.length?o:void 0},a=(e,t=void 0)=>(t&&(e=i(e,t)),e?.find((e=>0===e.path?.length)))},93380:function(e,t,o){o.a(e,(async function(e,i){try{o.r(t),o.d(t,{KNXCreateEntity:()=>k});var a=o(69868),r=o(84922),s=o(11991),n=o(97809),l=o(68476),d=o(92491),c=(o(13343),o(23749),o(86853),o(56730),o(95635),o(88002),o(68985)),h=o(90933),p=o(73120),u=o(42109),v=o(52190),_=(o(29349),o(49432)),g=o(33110),m=o(39635),b=o(39913),y=o(92095),f=e([d,v,g]);[d,v,g]=f.then?(await f)():f;const x="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",$="M5,3A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5.5L18.5,3H17V9A1,1 0 0,1 16,10H8A1,1 0 0,1 7,9V3H5M12,4V9H15V4H12M7,12H17A1,1 0 0,1 18,13V19H6V13A1,1 0 0,1 7,12Z",w=new y.Q("knx-create-entity");class k extends r.WF{willUpdate(e){if(e.has("route")){const e=this.route.prefix.split("/").at(-1);if("create"!==e&&"edit"!==e)return w.error("Unknown intent",e),void(this._intent=void 0);this._intent=e,this._config=void 0,this._validationErrors=void 0,this._validationBaseError=void 0,"create"===e?(this.entityId=void 0,this.entityPlatform=this.route.path.split("/")[1]):"edit"===e&&(this.entityId=this.route.path.split("/")[1])}}render(){return this.hass&&this._intent?this._projectLoadTask.render({initial:()=>r.qy`
        <hass-loading-screen .message=${"Waiting to fetch project data."}></hass-loading-screen>
      `,pending:()=>r.qy`
        <hass-loading-screen .message=${"Loading KNX project data."}></hass-loading-screen>
      `,error:e=>this._renderError("Error loading KNX project",e),complete:()=>"edit"===this._intent?this._renderEdit():this._renderCreate()}):r.qy` <hass-loading-screen></hass-loading-screen> `}_renderCreate(){return this.entityPlatform?this.knx.supportedPlatforms.includes(this.entityPlatform)?this._renderLoadSchema():(w.error("Unknown platform",this.entityPlatform),this._renderTypeSelection()):this._renderTypeSelection()}_renderEdit(){return this._entityConfigLoadTask.render({initial:()=>r.qy`
        <hass-loading-screen .message=${"Waiting to fetch entity data."}></hass-loading-screen>
      `,pending:()=>r.qy`
        <hass-loading-screen .message=${"Loading entity data."}></hass-loading-screen>
      `,error:e=>this._renderError(r.qy`${this.hass.localize("ui.card.common.entity_not_found")}:
            <code>${this.entityId}</code>`,e),complete:()=>this.entityPlatform?this.knx.supportedPlatforms.includes(this.entityPlatform)?this._renderLoadSchema():this._renderError("Unsupported platform","Unsupported platform: "+this.entityPlatform):this._renderError(r.qy`${this.hass.localize("ui.card.common.entity_not_found")}:
              <code>${this.entityId}</code>`,new Error("Entity platform unknown"))})}_renderLoadSchema(){return this._schemaLoadTask.render({initial:()=>r.qy`
        <hass-loading-screen .message=${"Waiting to fetch schema."}></hass-loading-screen>
      `,pending:()=>r.qy`
        <hass-loading-screen .message=${"Loading entity platform schema."}></hass-loading-screen>
      `,error:e=>this._renderError("Error loading schema",e),complete:()=>this._renderEntityConfig(this.entityPlatform)})}_renderError(e,t){return w.error("Error in create/edit entity",t),r.qy`
      <hass-subpage
        .hass=${this.hass}
        .narrow=${this.narrow}
        .back-path=${this.backPath}
        .header=${this.hass.localize("ui.panel.config.integrations.config_flow.error")}
      >
        <div class="content">
          <ha-alert alert-type="error"> ${e} </ha-alert>
        </div>
      </hass-subpage>
    `}_renderTypeSelection(){return r.qy`
      <hass-subpage
        .hass=${this.hass}
        .narrow=${this.narrow}
        .back-path=${this.backPath}
        .header=${this.hass.localize("component.knx.config_panel.entities.create.type_selection.title")}
      >
        <div class="type-selection">
          <ha-card
            outlined
            .header=${this.hass.localize("component.knx.config_panel.entities.create.type_selection.header")}
          >
            <!-- <p>Some help text</p> -->
            <ha-navigation-list
              .hass=${this.hass}
              .narrow=${this.narrow}
              .pages=${this.knx.supportedPlatforms.map((e=>{const t=(0,g.N)(e);return{name:`${this.hass.localize(`component.${e}.title`)}`,description:`${this.hass.localize(`component.knx.config_panel.entities.create.${e}.description`)}`,iconPath:t.iconPath,iconColor:t.color,path:`/knx/entities/create/${e}`}}))}
              has-secondary
              .label=${this.hass.localize("component.knx.config_panel.entities.create.type_selection.title")}
            ></ha-navigation-list>
          </ha-card>
        </div>
      </hass-subpage>
    `}_renderEntityConfig(e){const t="create"===this._intent,o=this.knx.schema[e];return r.qy`<hass-subpage
      .hass=${this.hass}
      .narrow=${this.narrow}
      .back-path=${this.backPath}
      .header=${t?this.hass.localize("component.knx.config_panel.entities.create.header"):`${this.hass.localize("ui.common.edit")}: ${this.entityId}`}
    >
      <div class="content">
        <div class="entity-config">
          <knx-configure-entity
            .hass=${this.hass}
            .knx=${this.knx}
            .platform=${e}
            .config=${this._config}
            .schema=${o}
            .validationErrors=${this._validationErrors}
            @knx-entity-configuration-changed=${this._configChanged}
          >
            ${this._validationBaseError?r.qy`<ha-alert slot="knx-validation-error" alert-type="error">
                  <details>
                    <summary><b>Validation error</b></summary>
                    <p>Base error: ${this._validationBaseError}</p>
                    ${this._validationErrors?.map((e=>r.qy`<p>
                          ${e.error_class}: ${e.error_message} in ${e.path?.join(" / ")}
                        </p>`))??r.s6}
                  </details>
                </ha-alert>`:r.s6}
          </knx-configure-entity>
          <ha-fab
            .label=${t?this.hass.localize("ui.common.create"):this.hass.localize("ui.common.save")}
            extended
            @click=${t?this._entityCreate:this._entityUpdate}
            ?disabled=${void 0===this._config}
          >
            <ha-svg-icon slot="icon" .path=${t?x:$}></ha-svg-icon>
          </ha-fab>
        </div>
        ${this.knx.projectData?r.qy` <div class="panel">
              <knx-project-device-tree
                .data=${this.knx.projectData}
                .validDPTs=${(0,m.Yb)(o)}
              ></knx-project-device-tree>
            </div>`:r.s6}
      </div>
    </hass-subpage>`}_configChanged(e){e.stopPropagation(),w.debug("configChanged",e.detail),this._config=e.detail,this._validationErrors&&this._entityValidate()}_entityCreate(e){e.stopPropagation(),void 0!==this._config&&void 0!==this.entityPlatform?(0,_.S$)(this.hass,{platform:this.entityPlatform,data:this._config}).then((e=>{this._handleValidationError(e,!0)||(w.debug("Successfully created entity",e.entity_id),(0,c.o)("/knx/entities",{replace:!0}),e.entity_id?this._entityMoreInfoSettings(e.entity_id):w.error("entity_id not found after creation."))})).catch((e=>{w.error("Error creating entity",e),(0,c.o)("/knx/error",{replace:!0,data:e})})):w.error("No config found.")}_entityUpdate(e){e.stopPropagation(),void 0!==this._config&&void 0!==this.entityId&&void 0!==this.entityPlatform?(0,_.zU)(this.hass,{platform:this.entityPlatform,entity_id:this.entityId,data:this._config}).then((e=>{this._handleValidationError(e,!0)||(w.debug("Successfully updated entity",this.entityId),(0,c.o)("/knx/entities",{replace:!0}))})).catch((e=>{w.error("Error updating entity",e),(0,c.o)("/knx/error",{replace:!0,data:e})})):w.error("No config found.")}_handleValidationError(e,t){return!1===e.success?(w.warn("Validation error",e),this._validationErrors=e.errors,this._validationBaseError=e.error_base,t&&setTimeout((()=>this._alertElement.scrollIntoView({behavior:"smooth"}))),!0):(this._validationErrors=void 0,this._validationBaseError=void 0,w.debug("Validation passed",e.entity_id),!1)}_entityMoreInfoSettings(e){(0,p.r)(h.G.document.querySelector("home-assistant"),"hass-more-info",{entityId:e,view:"settings"})}constructor(...e){super(...e),this._projectLoadTask=new l.YZ(this,{args:()=>[],task:async()=>{this.knx.projectInfo&&(this.knx.projectData||await this.knx.loadProject())}}),this._schemaLoadTask=new l.YZ(this,{args:()=>[this.entityPlatform],task:async([e])=>{e&&await this.knx.loadSchema(e)}}),this._entityConfigLoadTask=new l.YZ(this,{args:()=>[this.entityId],task:async([e])=>{if(!e)return;const{platform:t,data:o}=await(0,_.wE)(this.hass,e);this.entityPlatform=t,this._config=o}}),this._dragDropContextProvider=new n.DT(this,{context:b.B,initialValue:new b.J((()=>{this._dragDropContextProvider.updateObservers()}))}),this._entityValidate=(0,u.n)((()=>{w.debug("validate",this._config),void 0!==this._config&&void 0!==this.entityPlatform&&(0,_.UD)(this.hass,{platform:this.entityPlatform,data:this._config}).then((e=>{this._handleValidationError(e,!1)})).catch((e=>{w.error("validateEntity",e),(0,c.o)("/knx/error",{replace:!0,data:e})}))}),250)}}k.styles=r.AH`
    hass-loading-screen {
      --app-header-background-color: var(--sidebar-background-color);
      --app-header-text-color: var(--sidebar-text-color);
    }

    .type-selection {
      margin: 20px auto 80px;
      max-width: 720px;
    }

    @media screen and (max-width: 600px) {
      .panel {
        display: none;
      }
    }

    .content {
      display: flex;
      flex-direction: row;
      height: 100%;
      width: 100%;

      & > .entity-config {
        flex-grow: 1;
        flex-shrink: 1;
        height: 100%;
        overflow-y: scroll;
      }

      & > .panel {
        flex-grow: 0;
        flex-shrink: 3;
        width: 480px;
        min-width: 280px;
      }
    }

    knx-configure-entity {
      display: block;
      margin: 20px auto 40px; /* leave 80px space for fab */
      max-width: 720px;
    }

    ha-alert {
      display: block;
      margin: 20px auto;
      max-width: 720px;

      & summary {
        padding: 10px;
      }
    }

    ha-fab {
      /* not slot="fab" to move out of panel */
      float: right;
      margin-right: calc(16px + env(safe-area-inset-right));
      margin-bottom: 40px;
      z-index: 1;
    }
  `,(0,a.__decorate)([(0,s.MZ)({type:Object})],k.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],k.prototype,"knx",void 0),(0,a.__decorate)([(0,s.MZ)({type:Object})],k.prototype,"route",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],k.prototype,"narrow",void 0),(0,a.__decorate)([(0,s.MZ)({type:String,attribute:"back-path"})],k.prototype,"backPath",void 0),(0,a.__decorate)([(0,s.wk)()],k.prototype,"_config",void 0),(0,a.__decorate)([(0,s.wk)()],k.prototype,"_validationErrors",void 0),(0,a.__decorate)([(0,s.wk)()],k.prototype,"_validationBaseError",void 0),(0,a.__decorate)([(0,s.P)("ha-alert")],k.prototype,"_alertElement",void 0),k=(0,a.__decorate)([(0,s.EM)("knx-create-entity")],k),i()}catch(x){i(x)}}))}};
//# sourceMappingURL=3148.44568e1c40529308.js.map