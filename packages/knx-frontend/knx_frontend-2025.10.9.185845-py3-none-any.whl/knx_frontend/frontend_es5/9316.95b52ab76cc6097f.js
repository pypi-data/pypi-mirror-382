(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["9316"],{94732:function(e,t,i){var o={"./ha-icon-prev":["93302","7707"],"./ha-icon-button-toolbar":["1889","1994"],"./ha-alert":["23749"],"./ha-icon-button-toggle":["51892","725"],"./ha-svg-icon.ts":["95635"],"./ha-alert.ts":["23749"],"./ha-icon":["81164"],"./ha-icon-next.ts":["72062"],"./ha-qr-code.ts":["34772","3033","8613"],"./ha-icon-overflow-menu.ts":["35881","6216","7730"],"./ha-icon-button-toggle.ts":["51892","725"],"./ha-icon-button-group":["76469","2374"],"./ha-svg-icon":["95635"],"./ha-icon-button-prev":["36745","7778"],"./ha-icon-button.ts":["93672"],"./ha-icon-overflow-menu":["35881","6216","7730"],"./ha-icon-button-arrow-next":["71013","9430"],"./ha-icon-button-prev.ts":["36745","7778"],"./ha-icon-picker":["15785","7026"],"./ha-icon-button-toolbar.ts":["1889","1994"],"./ha-icon-button-arrow-prev.ts":["8101"],"./ha-icon-button-next":["75057","1962"],"./ha-icon-next":["72062"],"./ha-icon-picker.ts":["15785","7026"],"./ha-icon-prev.ts":["93302","7707"],"./ha-icon-button-arrow-prev":["8101"],"./ha-icon-button-next.ts":["75057","1962"],"./ha-icon.ts":["81164"],"./ha-qr-code":["34772","3033","8613"],"./ha-icon-button":["93672"],"./ha-icon-button-group.ts":["76469","2374"],"./ha-icon-button-arrow-next.ts":["71013","9430"]};function s(e){if(!i.o(o,e))return Promise.resolve().then((function(){var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}));var t=o[e],s=t[0];return Promise.all(t.slice(1).map(i.e)).then((function(){return i(s)}))}s.keys=function(){return Object.keys(o)},s.id=94732,e.exports=s},71289:function(e,t,i){var o={"./flow-preview-generic.ts":["83531","9358","1466","615","1096","7024","1227"],"./flow-preview-template":["30282","9358","1466","615","1096","7024","2311"],"./flow-preview-generic_camera":["43801","9358","1466","615","1096","7024","386"],"./flow-preview-generic_camera.ts":["43801","9358","1466","615","1096","7024","386"],"./flow-preview-generic":["83531","9358","1466","615","1096","7024","1227"],"./flow-preview-template.ts":["30282","9358","1466","615","1096","7024","2311"]};function s(e){if(!i.o(o,e))return Promise.resolve().then((function(){var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}));var t=o[e],s=t[0];return Promise.all(t.slice(1).map(i.e)).then((function(){return i(s)}))}s.keys=function(){return Object.keys(o)},s.id=71289,e.exports=s},57183:function(e,t,i){"use strict";i.d(t,{d:function(){return o}});i(65315),i(84136);const o=(e,t=!0)=>{if(e.defaultPrevented||0!==e.button||e.metaKey||e.ctrlKey||e.shiftKey)return;const i=e.composedPath().find((e=>"A"===e.tagName));if(!i||i.target||i.hasAttribute("download")||"external"===i.getAttribute("rel"))return;let o=i.href;if(!o||-1!==o.indexOf("mailto:"))return;const s=window.location,a=s.origin||s.protocol+"//"+s.host;return 0===o.indexOf(a)&&(o=o.substr(a.length),"#"!==o)?(t&&e.preventDefault(),o):void 0}},44537:function(e,t,i){"use strict";i.d(t,{xn:function(){return a},T:function(){return n}});i(35748),i(65315),i(837),i(37089),i(39118),i(95013);var o=i(65940),s=i(47379);i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030);const a=e=>{var t;return null===(t=e.name_by_user||e.name)||void 0===t?void 0:t.trim()},n=(e,t,i)=>a(e)||i&&r(t,i)||t.localize("ui.panel.config.devices.unnamed_device",{type:t.localize(`ui.panel.config.devices.type.${e.entry_type||"device"}`)}),r=(e,t)=>{for(const i of t||[]){const t="string"==typeof i?i:i.entity_id,o=e.states[t];if(o)return(0,s.u)(o)}};(0,o.A)((e=>function(e){const t=new Set,i=new Set;for(const o of e)i.has(o)?t.add(o):i.add(o);return t}(Object.values(e).map((e=>a(e))).filter((e=>void 0!==e)))))},3371:function(e,t,i){"use strict";i.d(t,{d:function(){return o}});const o=e=>{switch(e.language){case"cs":case"de":case"fi":case"fr":case"sk":case"sv":return" ";default:return""}}},96997:function(e,t,i){"use strict";var o=i(69868),s=i(84922),a=i(11991);let n,r,l=e=>e;class d extends s.WF{render(){return(0,s.qy)(n||(n=l`
      <header class="header">
        <div class="header-bar">
          <section class="header-navigation-icon">
            <slot name="navigationIcon"></slot>
          </section>
          <section class="header-content">
            <div class="header-title">
              <slot name="title"></slot>
            </div>
            <div class="header-subtitle">
              <slot name="subtitle"></slot>
            </div>
          </section>
          <section class="header-action-items">
            <slot name="actionItems"></slot>
          </section>
        </div>
        <slot></slot>
      </header>
    `))}static get styles(){return[(0,s.AH)(r||(r=l`
        :host {
          display: block;
        }
        :host([show-border]) {
          border-bottom: 1px solid
            var(--mdc-dialog-scroll-divider-color, rgba(0, 0, 0, 0.12));
        }
        .header-bar {
          display: flex;
          flex-direction: row;
          align-items: flex-start;
          padding: 4px;
          box-sizing: border-box;
        }
        .header-content {
          flex: 1;
          padding: 10px 4px;
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .header-title {
          font-size: var(--ha-font-size-xl);
          line-height: var(--ha-line-height-condensed);
          font-weight: var(--ha-font-weight-normal);
        }
        .header-subtitle {
          font-size: var(--ha-font-size-m);
          line-height: 20px;
          color: var(--secondary-text-color);
        }
        @media all and (min-width: 450px) and (min-height: 500px) {
          .header-bar {
            padding: 16px;
          }
        }
        .header-navigation-icon {
          flex: none;
          min-width: 8px;
          height: 100%;
          display: flex;
          flex-direction: row;
        }
        .header-action-items {
          flex: none;
          min-width: 8px;
          height: 100%;
          display: flex;
          flex-direction: row;
        }
      `))]}}d=(0,o.__decorate)([(0,a.EM)("ha-dialog-header")],d)},44840:function(e,t,i){"use strict";i.d(t,{$:function(){return o}});i(32203),i(46852),i(65315),i(22416);const o=e=>{const t={};return e.forEach((e=>{var i,s;if(void 0!==(null===(i=e.description)||void 0===i?void 0:i.suggested_value)&&null!==(null===(s=e.description)||void 0===s?void 0:s.suggested_value))t[e.name]=e.description.suggested_value;else if("default"in e)t[e.name]=e.default;else if("expandable"===e.type){const i=o(e.schema);(e.required||Object.keys(i).length)&&(t[e.name]=i)}else if(e.required){if("boolean"===e.type)t[e.name]=!1;else if("string"===e.type)t[e.name]="";else if("integer"===e.type)t[e.name]="valueMin"in e?e.valueMin:0;else if("constant"===e.type)t[e.name]=e.value;else if("float"===e.type)t[e.name]=0;else if("select"===e.type){if(e.options.length){const i=e.options[0];t[e.name]=Array.isArray(i)?i[0]:i}}else if("positive_time_period_dict"===e.type)t[e.name]={hours:0,minutes:0,seconds:0};else if("selector"in e){const i=e.selector;var a;if("device"in i)t[e.name]=null!==(a=i.device)&&void 0!==a&&a.multiple?[]:"";else if("entity"in i){var n;t[e.name]=null!==(n=i.entity)&&void 0!==n&&n.multiple?[]:""}else if("area"in i){var r;t[e.name]=null!==(r=i.area)&&void 0!==r&&r.multiple?[]:""}else if("label"in i){var l;t[e.name]=null!==(l=i.label)&&void 0!==l&&l.multiple?[]:""}else if("boolean"in i)t[e.name]=!1;else if("addon"in i||"attribute"in i||"file"in i||"icon"in i||"template"in i||"text"in i||"theme"in i||"object"in i)t[e.name]="";else if("number"in i){var d,c;t[e.name]=null!==(d=null===(c=i.number)||void 0===c?void 0:c.min)&&void 0!==d?d:0}else if("select"in i){var h;if(null!==(h=i.select)&&void 0!==h&&h.options.length){const o=i.select.options[0],s="string"==typeof o?o:o.value;t[e.name]=i.select.multiple?[s]:s}}else if("country"in i){var p;null!==(p=i.country)&&void 0!==p&&null!==(p=p.countries)&&void 0!==p&&p.length&&(t[e.name]=i.country.countries[0])}else if("language"in i){var u;null!==(u=i.language)&&void 0!==u&&null!==(u=u.languages)&&void 0!==u&&u.length&&(t[e.name]=i.language.languages[0])}else if("duration"in i)t[e.name]={hours:0,minutes:0,seconds:0};else if("time"in i)t[e.name]="00:00:00";else if("date"in i||"datetime"in i){const i=(new Date).toISOString().slice(0,10);t[e.name]=`${i}T00:00:00`}else if("color_rgb"in i)t[e.name]=[0,0,0];else if("color_temp"in i){var _,f;t[e.name]=null!==(_=null===(f=i.color_temp)||void 0===f?void 0:f.min_mireds)&&void 0!==_?_:153}else if("action"in i||"trigger"in i||"condition"in i)t[e.name]=[];else if("media"in i||"target"in i)t[e.name]={};else{if(!("state"in i))throw new Error(`Selector ${Object.keys(i)[0]} not supported in initial form data`);var g;t[e.name]=null!==(g=i.state)&&void 0!==g&&g.multiple?[]:""}}}else;})),t}},75518:function(e,t,i){"use strict";i(35748),i(65315),i(22416),i(37089),i(12977),i(5934),i(95013);var o=i(69868),s=i(84922),a=i(11991),n=i(21431),r=i(73120);i(23749),i(57674);let l,d,c,h,p,u,_,f,g,m=e=>e;const v={boolean:()=>i.e("2436").then(i.bind(i,33999)),constant:()=>i.e("3668").then(i.bind(i,33855)),float:()=>i.e("742").then(i.bind(i,84053)),grid:()=>i.e("7828").then(i.bind(i,57311)),expandable:()=>i.e("364").then(i.bind(i,51079)),integer:()=>i.e("7346").then(i.bind(i,40681)),multi_select:()=>Promise.all([i.e("6216"),i.e("3706")]).then(i.bind(i,99681)),positive_time_period_dict:()=>i.e("3540").then(i.bind(i,87551)),select:()=>i.e("2500").then(i.bind(i,10079)),string:()=>i.e("3627").then(i.bind(i,10070)),optional_actions:()=>i.e("3044").then(i.bind(i,96943))},w=(e,t)=>e?!t.name||t.flatten?e:e[t.name]:null;class y extends s.WF{getFormProperties(){return{}}async focus(){await this.updateComplete;const e=this.renderRoot.querySelector(".root");if(e)for(const t of e.children)if("HA-ALERT"!==t.tagName){t instanceof s.mN&&await t.updateComplete,t.focus();break}}willUpdate(e){e.has("schema")&&this.schema&&this.schema.forEach((e=>{var t;"selector"in e||null===(t=v[e.type])||void 0===t||t.call(v)}))}render(){return(0,s.qy)(l||(l=m`
      <div class="root" part="root">
        ${0}
        ${0}
      </div>
    `),this.error&&this.error.base?(0,s.qy)(d||(d=m`
              <ha-alert alert-type="error">
                ${0}
              </ha-alert>
            `),this._computeError(this.error.base,this.schema)):"",this.schema.map((e=>{var t;const i=((e,t)=>e&&t.name?e[t.name]:null)(this.error,e),o=((e,t)=>e&&t.name?e[t.name]:null)(this.warning,e);return(0,s.qy)(c||(c=m`
            ${0}
            ${0}
          `),i?(0,s.qy)(h||(h=m`
                  <ha-alert own-margin alert-type="error">
                    ${0}
                  </ha-alert>
                `),this._computeError(i,e)):o?(0,s.qy)(p||(p=m`
                    <ha-alert own-margin alert-type="warning">
                      ${0}
                    </ha-alert>
                  `),this._computeWarning(o,e)):"","selector"in e?(0,s.qy)(u||(u=m`<ha-selector
                  .schema=${0}
                  .hass=${0}
                  .narrow=${0}
                  .name=${0}
                  .selector=${0}
                  .value=${0}
                  .label=${0}
                  .disabled=${0}
                  .placeholder=${0}
                  .helper=${0}
                  .localizeValue=${0}
                  .required=${0}
                  .context=${0}
                ></ha-selector>`),e,this.hass,this.narrow,e.name,e.selector,w(this.data,e),this._computeLabel(e,this.data),e.disabled||this.disabled||!1,e.required?"":e.default,this._computeHelper(e),this.localizeValue,e.required||!1,this._generateContext(e)):(0,n._)(this.fieldElementName(e.type),Object.assign({schema:e,data:w(this.data,e),label:this._computeLabel(e,this.data),helper:this._computeHelper(e),disabled:this.disabled||e.disabled||!1,hass:this.hass,localize:null===(t=this.hass)||void 0===t?void 0:t.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(e)},this.getFormProperties())))})))}fieldElementName(e){return`ha-form-${e}`}_generateContext(e){if(!e.context)return;const t={};for(const[i,o]of Object.entries(e.context))t[i]=this.data[o];return t}createRenderRoot(){const e=super.createRenderRoot();return this.addValueChangedListener(e),e}addValueChangedListener(e){e.addEventListener("value-changed",(e=>{e.stopPropagation();const t=e.target.schema;if(e.target===this)return;const i=!t.name||"flatten"in t&&t.flatten?e.detail.value:{[t.name]:e.detail.value};this.data=Object.assign(Object.assign({},this.data),i),(0,r.r)(this,"value-changed",{value:this.data})}))}_computeLabel(e,t){return this.computeLabel?this.computeLabel(e,t):e?e.name:""}_computeHelper(e){return this.computeHelper?this.computeHelper(e):""}_computeError(e,t){return Array.isArray(e)?(0,s.qy)(_||(_=m`<ul>
        ${0}
      </ul>`),e.map((e=>(0,s.qy)(f||(f=m`<li>
              ${0}
            </li>`),this.computeError?this.computeError(e,t):e)))):this.computeError?this.computeError(e,t):e}_computeWarning(e,t){return this.computeWarning?this.computeWarning(e,t):e}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1}}y.styles=(0,s.AH)(g||(g=m`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `)),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],y.prototype,"narrow",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],y.prototype,"data",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],y.prototype,"schema",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],y.prototype,"error",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],y.prototype,"warning",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],y.prototype,"disabled",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],y.prototype,"computeError",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],y.prototype,"computeWarning",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],y.prototype,"computeLabel",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],y.prototype,"computeHelper",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],y.prototype,"localizeValue",void 0),y=(0,o.__decorate)([(0,a.EM)("ha-form")],y)},53199:function(e,t,i){"use strict";i(35748),i(95013);var o=i(69868),s=i(84922),a=i(11991),n=i(3756),r=(i(79827),i(9724),i(65315),i(837),i(37089),i(48169),i(5934),i(67579),i(18223),i(34789)),l=i.n(r),d=i(73120),c=(i(45460),i(18332),i(13484),i(81071),i(92714),i(55885),i(57971));let h;const p=new class{get(e){return this._cache.get(e)}set(e,t){this._cache.set(e,t),this._expiration&&window.setTimeout((()=>this._cache.delete(e)),this._expiration)}has(e){return this._cache.has(e)}constructor(e){this._cache=new Map,this._expiration=e}}(1e3),u={reType:(0,n.A)(/((\[!(caution|important|note|tip|warning)\])(?:\s|\\n)?)/i,{input:1,type:3}),typeToHaAlert:{caution:"error",important:"info",note:"info",tip:"success",warning:"warning"}};class _ extends s.mN{disconnectedCallback(){if(super.disconnectedCallback(),this.cache){const e=this._computeCacheKey();p.set(e,this.innerHTML)}}createRenderRoot(){return this}update(e){super.update(e),void 0!==this.content&&this._render()}willUpdate(e){if(!this.innerHTML&&this.cache){const e=this._computeCacheKey();p.has(e)&&(this.innerHTML=p.get(e),this._resize())}}_computeCacheKey(){return l()({content:this.content,allowSvg:this.allowSvg,allowDataUrl:this.allowDataUrl,breaks:this.breaks})}async _render(){this.innerHTML=await(async(e,t,o)=>(h||(h=(0,c.LV)(new Worker(new URL(i.p+i.u("5640"),i.b)))),h.renderMarkdown(e,t,o)))(String(this.content),{breaks:this.breaks,gfm:!0},{allowSvg:this.allowSvg,allowDataUrl:this.allowDataUrl}),this._resize();const e=document.createTreeWalker(this,NodeFilter.SHOW_ELEMENT,null);for(;e.nextNode();){const o=e.currentNode;if(o instanceof HTMLAnchorElement&&o.host!==document.location.host)o.target="_blank",o.rel="noreferrer noopener";else if(o instanceof HTMLImageElement)this.lazyImages&&(o.loading="lazy"),o.addEventListener("load",this._resize);else if(o instanceof HTMLQuoteElement){var t;const i=(null===(t=o.firstElementChild)||void 0===t||null===(t=t.firstChild)||void 0===t?void 0:t.textContent)&&u.reType.exec(o.firstElementChild.firstChild.textContent);if(i){const{type:t}=i.groups,s=document.createElement("ha-alert");s.alertType=u.typeToHaAlert[t.toLowerCase()],s.append(...Array.from(o.childNodes).map((e=>{const t=Array.from(e.childNodes);if(!this.breaks&&t.length){var o;const e=t[0];e.nodeType===Node.TEXT_NODE&&e.textContent===i.input&&null!==(o=e.textContent)&&void 0!==o&&o.includes("\n")&&(e.textContent=e.textContent.split("\n").slice(1).join("\n"))}return t})).reduce(((e,t)=>e.concat(t)),[]).filter((e=>e.textContent&&e.textContent!==i.input))),e.parentNode().replaceChild(s,o)}}else o instanceof HTMLElement&&["ha-alert","ha-qr-code","ha-icon","ha-svg-icon"].includes(o.localName)&&i(94732)(`./${o.localName}`)}}constructor(...e){super(...e),this.allowSvg=!1,this.allowDataUrl=!1,this.breaks=!1,this.lazyImages=!1,this.cache=!1,this._resize=()=>(0,d.r)(this,"content-resize")}}(0,o.__decorate)([(0,a.MZ)()],_.prototype,"content",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:"allow-svg",type:Boolean})],_.prototype,"allowSvg",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:"allow-data-url",type:Boolean})],_.prototype,"allowDataUrl",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],_.prototype,"breaks",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,attribute:"lazy-images"})],_.prototype,"lazyImages",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],_.prototype,"cache",void 0),_=(0,o.__decorate)([(0,a.EM)("ha-markdown-element")],_);let f,g,m=e=>e;class v extends s.WF{render(){return this.content?(0,s.qy)(f||(f=m`<ha-markdown-element
      .content=${0}
      .allowSvg=${0}
      .allowDataUrl=${0}
      .breaks=${0}
      .lazyImages=${0}
      .cache=${0}
    ></ha-markdown-element>`),this.content,this.allowSvg,this.allowDataUrl,this.breaks,this.lazyImages,this.cache):s.s6}constructor(...e){super(...e),this.allowSvg=!1,this.allowDataUrl=!1,this.breaks=!1,this.lazyImages=!1,this.cache=!1}}v.styles=(0,s.AH)(g||(g=m`
    :host {
      display: block;
    }
    ha-markdown-element {
      -ms-user-select: text;
      -webkit-user-select: text;
      -moz-user-select: text;
    }
    ha-markdown-element > *:first-child {
      margin-top: 0;
    }
    ha-markdown-element > *:last-child {
      margin-bottom: 0;
    }
    ha-alert {
      display: block;
      margin: 4px 0;
    }
    a {
      color: var(--primary-color);
    }
    img {
      max-width: 100%;
    }
    code,
    pre {
      background-color: var(--markdown-code-background-color, none);
      border-radius: 3px;
    }
    svg {
      background-color: var(--markdown-svg-background-color, none);
      color: var(--markdown-svg-color, none);
    }
    code {
      font-size: var(--ha-font-size-s);
      padding: 0.2em 0.4em;
    }
    pre code {
      padding: 0;
    }
    pre {
      padding: 16px;
      overflow: auto;
      line-height: var(--ha-line-height-condensed);
      font-family: var(--ha-font-family-code);
    }
    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
      line-height: initial;
    }
    h2 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-bold);
    }
    hr {
      border-color: var(--divider-color);
      border-bottom: none;
      margin: 16px 0;
    }
  `)),(0,o.__decorate)([(0,a.MZ)()],v.prototype,"content",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:"allow-svg",type:Boolean})],v.prototype,"allowSvg",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:"allow-data-url",type:Boolean})],v.prototype,"allowDataUrl",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],v.prototype,"breaks",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,attribute:"lazy-images"})],v.prototype,"lazyImages",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],v.prototype,"cache",void 0),v=(0,o.__decorate)([(0,a.EM)("ha-markdown")],v)},80527:function(e,t,i){"use strict";i.a(e,(async function(e,t){try{var o=i(69868),s=i(35240),a=i(84922),n=i(11991),r=e([s]);s=(r.then?(await r)():r)[0];let l,d=e=>e;class c extends s.A{updated(e){if(super.updated(e),e.has("size"))switch(this.size){case"tiny":this.style.setProperty("--ha-progress-ring-size","16px");break;case"small":this.style.setProperty("--ha-progress-ring-size","28px");break;case"medium":this.style.setProperty("--ha-progress-ring-size","48px");break;case"large":this.style.setProperty("--ha-progress-ring-size","68px");break;case void 0:this.style.removeProperty("--ha-progress-ring-size")}}static get styles(){return[s.A.styles,(0,a.AH)(l||(l=d`
        :host {
          --indicator-color: var(
            --ha-progress-ring-indicator-color,
            var(--primary-color)
          );
          --track-color: var(
            --ha-progress-ring-divider-color,
            var(--divider-color)
          );
          --track-width: 4px;
          --speed: 3.5s;
          --size: var(--ha-progress-ring-size, 48px);
        }
      `))]}}(0,o.__decorate)([(0,n.MZ)()],c.prototype,"size",void 0),c=(0,o.__decorate)([(0,n.EM)("ha-progress-ring")],c),t()}catch(l){t(l)}}))},39856:function(e,t,i){"use strict";i.d(t,{KC:function(){return c},Vy:function(){return l},ds:function(){return a},ew:function(){return r},g5:function(){return d},tl:function(){return n}});var o=i(68775),s=i(6098);const a=(e,t,i)=>e.connection.subscribeMessage(i,{type:"assist_satellite/intercept_wake_word",entity_id:t}),n=(e,t)=>e.callWS({type:"assist_satellite/test_connection",entity_id:t}),r=(e,t,i)=>e.callService("assist_satellite","announce",i,{entity_id:t}),l=(e,t)=>e.callWS({type:"assist_satellite/get_configuration",entity_id:t}),d=(e,t,i)=>e.callWS({type:"assist_satellite/set_wake_words",entity_id:t,wake_word_ids:i}),c=e=>e&&e.state!==s.Hh&&(0,o.$)(e,1)},4311:function(e,t,i){"use strict";i.d(t,{Hg:function(){return o},e0:function(){return s}});i(79827),i(65315),i(37089),i(36874),i(12977),i(5934),i(90917),i(18223);const o=e=>e.map((e=>{if("string"!==e.type)return e;switch(e.name){case"username":return Object.assign(Object.assign({},e),{},{autocomplete:"username",autofocus:!0});case"password":return Object.assign(Object.assign({},e),{},{autocomplete:"current-password"});case"code":return Object.assign(Object.assign({},e),{},{autocomplete:"one-time-code",autofocus:!0});default:return e}})),s=(e,t)=>e.callWS({type:"auth/sign_path",path:t})},582:function(e,t,i){"use strict";i.d(t,{PN:function(){return a},jm:function(){return n},sR:function(){return r},t1:function(){return s},t2:function(){return d},yu:function(){return l}});i(28027);const o={"HA-Frontend-Base":`${location.protocol}//${location.host}`},s=(e,t,i)=>{var s;return e.callApi("POST","config/config_entries/flow",{handler:t,show_advanced_options:Boolean(null===(s=e.userData)||void 0===s?void 0:s.showAdvanced),entry_id:i},o)},a=(e,t)=>e.callApi("GET",`config/config_entries/flow/${t}`,void 0,o),n=(e,t,i)=>e.callApi("POST",`config/config_entries/flow/${t}`,i,o),r=(e,t)=>e.callApi("DELETE",`config/config_entries/flow/${t}`),l=(e,t)=>e.callApi("GET","config/config_entries/flow_handlers"+(t?`?type=${t}`:"")),d=e=>e.sendMessagePromise({type:"config_entries/flow/progress"})},62013:function(e,t,i){"use strict";i.d(t,{K:function(){return s},P:function(){return o}});const o=(e,t)=>e.subscribeEvents(t,"data_entry_flow_progressed"),s=(e,t)=>e.subscribeEvents(t,"data_entry_flow_progress_update")},6098:function(e,t,i){"use strict";i.d(t,{HV:function(){return a},Hh:function(){return s},KF:function(){return r},ON:function(){return n},g0:function(){return c},s7:function(){return l}});var o=i(87383);const s="unavailable",a="unknown",n="on",r="off",l=[s,a],d=[s,a,r],c=(0,o.g)(l);(0,o.g)(d)},95237:function(e,t,i){"use strict";i.d(t,{F:function(){return a},Q:function(){return s}});i(79827);const o=["generic_camera","template"],s=(e,t,i,o,s,a)=>e.connection.subscribeMessage(a,{type:`${t}/start_preview`,flow_id:i,flow_type:o,user_input:s}),a=e=>o.includes(e)?e:"generic"},93167:function(e,t,i){"use strict";i.a(e,(async function(e,o){try{i.r(t);i(79827),i(35748),i(65315),i(837),i(37089),i(36874),i(5934),i(18223),i(95013);var s=i(69868),a=i(84922),n=i(11991),r=i(65940),l=i(73120),d=(i(72847),i(96997),i(93672),i(62013)),c=i(83566),h=i(86435),p=i(47420),u=i(45493),_=i(80887),f=i(58365),g=i(34436),m=i(58784),v=(i(93273),i(23225)),w=i(16206),y=i(31319),b=i(44140),$=e([u,_,f,g,m,v]);[u,_,f,g,m,v]=$.then?(await $)():$;let x,k,C,M,z,E,D,S,F,q,O,T,A=e=>e;const H="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",P="M15.07,11.25L14.17,12.17C13.45,12.89 13,13.5 13,15H11V14.5C11,13.39 11.45,12.39 12.17,11.67L13.41,10.41C13.78,10.05 14,9.55 14,9C14,7.89 13.1,7 12,7A2,2 0 0,0 10,9H8A4,4 0 0,1 12,5A4,4 0 0,1 16,9C16,9.88 15.64,10.67 15.07,11.25M13,19H11V17H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12C22,6.47 17.5,2 12,2Z";let U=0;class Z extends a.WF{async showDialog(e){this._params=e,this._instance=U++;const t=this._instance;let i;if(e.startFlowHandler){this._loading="loading_flow",this._handler=e.startFlowHandler;try{i=await this._params.flowConfig.createFlow(this.hass,e.startFlowHandler)}catch(o){this.closeDialog();let e=o.message||o.body||"Unknown error";return"string"!=typeof e&&(e=JSON.stringify(e)),void(0,p.K$)(this,{title:this.hass.localize("ui.panel.config.integrations.config_flow.error"),text:`${this.hass.localize("ui.panel.config.integrations.config_flow.could_not_load")}: ${e}`})}if(t!==this._instance)return}else{if(!e.continueFlowId)return;this._loading="loading_flow";try{i=await e.flowConfig.fetchFlow(this.hass,e.continueFlowId)}catch(o){this.closeDialog();let e=o.message||o.body||"Unknown error";return"string"!=typeof e&&(e=JSON.stringify(e)),void(0,p.K$)(this,{title:this.hass.localize("ui.panel.config.integrations.config_flow.error"),text:`${this.hass.localize("ui.panel.config.integrations.config_flow.could_not_load")}: ${e}`})}}t===this._instance&&(this._processStep(i),this._loading=void 0)}closeDialog(){if(!this._params)return;const e=Boolean(this._step&&["create_entry","abort"].includes(this._step.type));var t;(!this._step||e||this._params.continueFlowId||this._params.flowConfig.deleteFlow(this.hass,this._step.flow_id),this._step&&this._params.dialogClosedCallback)&&this._params.dialogClosedCallback({flowFinished:e,entryId:"result"in this._step?null===(t=this._step.result)||void 0===t?void 0:t.entry_id:void 0});this._loading=void 0,this._step=void 0,this._params=void 0,this._handler=void 0,this._unsubDataEntryFlowProgress&&(this._unsubDataEntryFlowProgress(),this._unsubDataEntryFlowProgress=void 0),(0,l.r)(this,"dialog-closed",{dialog:this.localName})}_getDialogTitle(){var e;if(this._loading||!this._step||!this._params)return"";switch(this._step.type){case"form":return this._params.flowConfig.renderShowFormStepHeader(this.hass,this._step);case"abort":return this._params.flowConfig.renderAbortHeader?this._params.flowConfig.renderAbortHeader(this.hass,this._step):this.hass.localize(`component.${null!==(e=this._params.domain)&&void 0!==e?e:this._step.handler}.title`);case"progress":return this._params.flowConfig.renderShowFormProgressHeader(this.hass,this._step);case"menu":return this._params.flowConfig.renderMenuHeader(this.hass,this._step);case"create_entry":{var t;const e=this._devices(this._params.flowConfig.showDevices,Object.values(this.hass.devices),null===(t=this._step.result)||void 0===t?void 0:t.entry_id,this._params.carryOverDevices).length;return this.hass.localize("ui.panel.config.integrations.config_flow."+(e?"device_created":"success"),{number:e})}default:return""}}_getDialogSubtitle(){var e,t,i,o,s,a,n,r;if(this._loading||!this._step||!this._params)return"";switch(this._step.type){case"form":return null===(e=(t=this._params.flowConfig).renderShowFormStepSubheader)||void 0===e?void 0:e.call(t,this.hass,this._step);case"abort":return null===(i=(o=this._params.flowConfig).renderAbortSubheader)||void 0===i?void 0:i.call(o,this.hass,this._step);case"progress":return null===(s=(a=this._params.flowConfig).renderShowFormProgressSubheader)||void 0===s?void 0:s.call(a,this.hass,this._step);case"menu":return null===(n=(r=this._params.flowConfig).renderMenuSubheader)||void 0===n?void 0:n.call(r,this.hass,this._step);default:return""}}render(){var e,t,i,o,s,n,r;if(!this._params)return a.s6;const l=["form","menu","external","progress","data_entry_flow_progressed"].includes(null===(e=this._step)||void 0===e?void 0:e.type)&&(null===(t=this._params.manifest)||void 0===t?void 0:t.is_built_in)||!(null===(i=this._params.manifest)||void 0===i||!i.documentation),d=this._getDialogTitle(),c=this._getDialogSubtitle();return(0,a.qy)(x||(x=A`
      <ha-dialog
        open
        @closed=${0}
        scrimClickAction
        escapeKeyAction
        hideActions
        .heading=${0}
      >
        <ha-dialog-header slot="heading">
          <ha-icon-button
            .label=${0}
            .path=${0}
            dialogAction="close"
            slot="navigationIcon"
          ></ha-icon-button>

          <div
            slot="title"
            class="dialog-title${0}"
            title=${0}
          >
            ${0}
          </div>

          ${0}
          ${0}
        </ha-dialog-header>
        <div>
          ${0}
        </div>
      </ha-dialog>
    `),this.closeDialog,d||!0,this.hass.localize("ui.common.close"),H,"form"===(null===(o=this._step)||void 0===o?void 0:o.type)?" form":"",d,d,c?(0,a.qy)(k||(k=A` <div slot="subtitle">${0}</div>`),c):a.s6,l&&!this._loading&&this._step?(0,a.qy)(C||(C=A`
                <a
                  slot="actionItems"
                  class="help"
                  href=${0}
                  target="_blank"
                  rel="noreferrer noopener"
                >
                  <ha-icon-button
                    .label=${0}
                    .path=${0}
                  >
                  </ha-icon-button
                ></a>
              `),this._params.manifest.is_built_in?(0,h.o)(this.hass,`/integrations/${this._params.manifest.domain}`):this._params.manifest.documentation,this.hass.localize("ui.common.help"),P):a.s6,this._loading||null===this._step?(0,a.qy)(M||(M=A`
                <step-flow-loading
                  .flowConfig=${0}
                  .hass=${0}
                  .loadingReason=${0}
                  .handler=${0}
                  .step=${0}
                ></step-flow-loading>
              `),this._params.flowConfig,this.hass,this._loading,this._handler,this._step):void 0===this._step?a.s6:(0,a.qy)(z||(z=A`
                  ${0}
                `),"form"===this._step.type?(0,a.qy)(E||(E=A`
                        <step-flow-form
                          narrow
                          .flowConfig=${0}
                          .step=${0}
                          .hass=${0}
                        ></step-flow-form>
                      `),this._params.flowConfig,this._step,this.hass):"external"===this._step.type?(0,a.qy)(D||(D=A`
                          <step-flow-external
                            .flowConfig=${0}
                            .step=${0}
                            .hass=${0}
                          ></step-flow-external>
                        `),this._params.flowConfig,this._step,this.hass):"abort"===this._step.type?(0,a.qy)(S||(S=A`
                            <step-flow-abort
                              .params=${0}
                              .step=${0}
                              .hass=${0}
                              .handler=${0}
                              .domain=${0}
                            ></step-flow-abort>
                          `),this._params,this._step,this.hass,this._step.handler,null!==(s=this._params.domain)&&void 0!==s?s:this._step.handler):"progress"===this._step.type?(0,a.qy)(F||(F=A`
                              <step-flow-progress
                                .flowConfig=${0}
                                .step=${0}
                                .hass=${0}
                                .progress=${0}
                              ></step-flow-progress>
                            `),this._params.flowConfig,this._step,this.hass,this._progress):"menu"===this._step.type?(0,a.qy)(q||(q=A`
                                <step-flow-menu
                                  .flowConfig=${0}
                                  .step=${0}
                                  .hass=${0}
                                ></step-flow-menu>
                              `),this._params.flowConfig,this._step,this.hass):(0,a.qy)(O||(O=A`
                                <step-flow-create-entry
                                  .flowConfig=${0}
                                  .step=${0}
                                  .hass=${0}
                                  .navigateToResult=${0}
                                  .devices=${0}
                                ></step-flow-create-entry>
                              `),this._params.flowConfig,this._step,this.hass,null!==(n=this._params.navigateToResult)&&void 0!==n&&n,this._devices(this._params.flowConfig.showDevices,Object.values(this.hass.devices),null===(r=this._step.result)||void 0===r?void 0:r.entry_id,this._params.carryOverDevices))))}firstUpdated(e){super.firstUpdated(e),this.addEventListener("flow-update",(e=>{const{step:t,stepPromise:i}=e.detail;this._processStep(t||i)}))}willUpdate(e){super.willUpdate(e),e.has("_step")&&this._step&&["external","progress"].includes(this._step.type)&&this._subscribeDataEntryFlowProgressed()}async _processStep(e){if(void 0===e)return void this.closeDialog();const t=setTimeout((()=>{this._loading="loading_step"}),250);let i;try{i=await e}catch(a){var o;return this.closeDialog(),void(0,p.K$)(this,{title:this.hass.localize("ui.panel.config.integrations.config_flow.error"),text:null==a||null===(o=a.body)||void 0===o?void 0:o.message})}finally{clearTimeout(t),this._loading=void 0}var s;(this._step=void 0,await this.updateComplete,this._step=i,"create_entry"===i.type&&i.next_flow)&&(this._step=void 0,this._handler=void 0,this._unsubDataEntryFlowProgress&&(this._unsubDataEntryFlowProgress(),this._unsubDataEntryFlowProgress=void 0),"config_flow"===i.next_flow[0]?(0,b.W)(this._params.dialogParentElement,{continueFlowId:i.next_flow[1],carryOverDevices:this._devices(this._params.flowConfig.showDevices,Object.values(this.hass.devices),null===(s=i.result)||void 0===s?void 0:s.entry_id,this._params.carryOverDevices).map((e=>e.id)),dialogClosedCallback:this._params.dialogClosedCallback}):"options_flow"===i.next_flow[0]?(0,w.Q)(this._params.dialogParentElement,i.result,{continueFlowId:i.next_flow[1],navigateToResult:this._params.navigateToResult,dialogClosedCallback:this._params.dialogClosedCallback}):"config_subentries_flow"===i.next_flow[0]?(0,y.a)(this._params.dialogParentElement,i.result,i.next_flow[0],{continueFlowId:i.next_flow[1],navigateToResult:this._params.navigateToResult,dialogClosedCallback:this._params.dialogClosedCallback}):(this.closeDialog(),(0,p.K$)(this._params.dialogParentElement,{text:this.hass.localize("ui.panel.config.integrations.config_flow.error",{error:`Unsupported next flow type: ${i.next_flow[0]}`})})))}async _subscribeDataEntryFlowProgressed(){if(this._unsubDataEntryFlowProgress)return;this._progress=void 0;const e=[(0,d.P)(this.hass.connection,(e=>{var t;e.data.flow_id===(null===(t=this._step)||void 0===t?void 0:t.flow_id)&&(this._processStep(this._params.flowConfig.fetchFlow(this.hass,this._step.flow_id)),this._progress=void 0)})),(0,d.K)(this.hass.connection,(e=>{this._progress=Math.ceil(100*e.data.progress)}))];this._unsubDataEntryFlowProgress=async()=>{(await Promise.all(e)).map((e=>e()))}}static get styles(){return[c.nA,(0,a.AH)(T||(T=A`
        ha-dialog {
          --dialog-content-padding: 0;
        }
        .dialog-title {
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .dialog-title.form {
          white-space: normal;
        }
        .help {
          color: var(--secondary-text-color);
        }
      `))]}constructor(...e){super(...e),this._instance=U,this._devices=(0,r.A)(((e,t,i,o)=>e&&i?t.filter((e=>e.config_entries.includes(i)||(null==o?void 0:o.includes(e.id)))):[]))}}(0,s.__decorate)([(0,n.MZ)({attribute:!1})],Z.prototype,"hass",void 0),(0,s.__decorate)([(0,n.wk)()],Z.prototype,"_params",void 0),(0,s.__decorate)([(0,n.wk)()],Z.prototype,"_loading",void 0),(0,s.__decorate)([(0,n.wk)()],Z.prototype,"_progress",void 0),(0,s.__decorate)([(0,n.wk)()],Z.prototype,"_step",void 0),(0,s.__decorate)([(0,n.wk)()],Z.prototype,"_handler",void 0),Z=(0,s.__decorate)([(0,n.EM)("dialog-data-entry-flow")],Z),o()}catch(x){o(x)}}))},44140:function(e,t,i){"use strict";i.d(t,{W:function(){return m}});i(32203),i(35748),i(5934),i(95013);var o=i(84922),s=i(582),a=i(28027),n=i(5361);let r,l,d,c,h,p,u,_,f,g=e=>e;const m=(e,t)=>(0,n.g)(e,t,{flowType:"config_flow",showDevices:!0,createFlow:async(e,i)=>{const[o]=await Promise.all([(0,s.t1)(e,i,t.entryId),e.loadFragmentTranslation("config"),e.loadBackendTranslation("config",i),e.loadBackendTranslation("selector",i),e.loadBackendTranslation("title",i)]);return o},fetchFlow:async(e,t)=>{const[i]=await Promise.all([(0,s.PN)(e,t),e.loadFragmentTranslation("config")]);return await Promise.all([e.loadBackendTranslation("config",i.handler),e.loadBackendTranslation("selector",i.handler),e.loadBackendTranslation("title",i.handler)]),i},handleFlowStep:s.jm,deleteFlow:s.sR,renderAbortDescription(e,t){const i=e.localize(`component.${t.translation_domain||t.handler}.config.abort.${t.reason}`,t.description_placeholders);return i?(0,o.qy)(r||(r=g`
            <ha-markdown allow-svg breaks .content=${0}></ha-markdown>
          `),i):t.reason},renderShowFormStepHeader(e,t){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.title`,t.description_placeholders)||e.localize(`component.${t.handler}.title`)},renderShowFormStepDescription(e,t){const i=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.description`,t.description_placeholders);return i?(0,o.qy)(l||(l=g`
            <ha-markdown
              .allowDataUrl=${0}
              allow-svg
              breaks
              .content=${0}
            ></ha-markdown>
          `),"zwave_js"===t.handler,i):""},renderShowFormStepFieldLabel(e,t,i,o){var s;if("expandable"===i.type)return e.localize(`component.${t.handler}.config.step.${t.step_id}.sections.${i.name}.name`,t.description_placeholders);const a=null!=o&&null!==(s=o.path)&&void 0!==s&&s[0]?`sections.${o.path[0]}.`:"";return e.localize(`component.${t.handler}.config.step.${t.step_id}.${a}data.${i.name}`,t.description_placeholders)||i.name},renderShowFormStepFieldHelper(e,t,i,s){var a;if("expandable"===i.type)return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.sections.${i.name}.description`,t.description_placeholders);const n=null!=s&&null!==(a=s.path)&&void 0!==a&&a[0]?`sections.${s.path[0]}.`:"",r=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.${n}data_description.${i.name}`,t.description_placeholders);return r?(0,o.qy)(d||(d=g`<ha-markdown breaks .content=${0}></ha-markdown>`),r):""},renderShowFormStepFieldError(e,t,i){return e.localize(`component.${t.translation_domain||t.translation_domain||t.handler}.config.error.${i}`,t.description_placeholders)||i},renderShowFormStepFieldLocalizeValue(e,t,i){return e.localize(`component.${t.handler}.selector.${i}`)},renderShowFormStepSubmitButton(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.submit`)||e.localize("ui.panel.config.integrations.config_flow."+(!1===t.last_step?"next":"submit"))},renderExternalStepHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize("ui.panel.config.integrations.config_flow.external_step.open_site")},renderExternalStepDescription(e,t){const i=e.localize(`component.${t.translation_domain||t.handler}.config.${t.step_id}.description`,t.description_placeholders);return(0,o.qy)(c||(c=g`
        <p>
          ${0}
        </p>
        ${0}
      `),e.localize("ui.panel.config.integrations.config_flow.external_step.description"),i?(0,o.qy)(h||(h=g`
              <ha-markdown
                allow-svg
                breaks
                .content=${0}
              ></ha-markdown>
            `),i):"")},renderCreateEntryDescription(e,t){const i=e.localize(`component.${t.translation_domain||t.handler}.config.create_entry.${t.description||"default"}`,t.description_placeholders);return(0,o.qy)(p||(p=g`
        ${0}
      `),i?(0,o.qy)(u||(u=g`
              <ha-markdown
                allow-svg
                breaks
                .content=${0}
              ></ha-markdown>
            `),i):o.s6)},renderShowFormProgressHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize(`component.${t.handler}.title`)},renderShowFormProgressDescription(e,t){const i=e.localize(`component.${t.translation_domain||t.handler}.config.progress.${t.progress_action}`,t.description_placeholders);return i?(0,o.qy)(_||(_=g`
            <ha-markdown allow-svg breaks .content=${0}></ha-markdown>
          `),i):""},renderMenuHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize(`component.${t.handler}.title`)},renderMenuDescription(e,t){const i=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.description`,t.description_placeholders);return i?(0,o.qy)(f||(f=g`
            <ha-markdown allow-svg breaks .content=${0}></ha-markdown>
          `),i):""},renderMenuOption(e,t,i){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.menu_options.${i}`,t.description_placeholders)},renderMenuOptionDescription(e,t,i){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.menu_option_descriptions.${i}`,t.description_placeholders)},renderLoadingDescription(e,t,i,o){if("loading_flow"!==t&&"loading_step"!==t)return"";const s=(null==o?void 0:o.handler)||i;return e.localize(`ui.panel.config.integrations.config_flow.loading.${t}`,{integration:s?(0,a.p$)(e.localize,s):e.localize("ui.panel.config.integrations.config_flow.loading.fallback_title")})}})},45493:function(e,t,i){"use strict";i.a(e,(async function(e,t){try{i(5934);var o=i(69868),s=i(84922),a=i(11991),n=i(73120),r=i(94100),l=i(44140),d=i(46472),c=i(76943),h=e([c]);c=(h.then?(await h)():h)[0];let p,u=e=>e;class _ extends s.WF{firstUpdated(e){super.firstUpdated(e),"missing_credentials"===this.step.reason&&this._handleMissingCreds()}render(){return"missing_credentials"===this.step.reason?s.s6:(0,s.qy)(p||(p=u`
      <div class="content">
        ${0}
      </div>
      <div class="buttons">
        <ha-button appearance="plain" @click=${0}
          >${0}</ha-button
        >
      </div>
    `),this.params.flowConfig.renderAbortDescription(this.hass,this.step),this._flowDone,this.hass.localize("ui.panel.config.integrations.config_flow.close"))}async _handleMissingCreds(){(0,r.a)(this.params.dialogParentElement,{selectedDomain:this.domain,manifest:this.params.manifest,applicationCredentialAddedCallback:()=>{var e;(0,l.W)(this.params.dialogParentElement,{dialogClosedCallback:this.params.dialogClosedCallback,startFlowHandler:this.handler,showAdvanced:null===(e=this.hass.userData)||void 0===e?void 0:e.showAdvanced,navigateToResult:this.params.navigateToResult})}}),this._flowDone()}_flowDone(){(0,n.r)(this,"flow-update",{step:void 0})}static get styles(){return d.G}}(0,o.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"params",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"step",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"domain",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"handler",void 0),_=(0,o.__decorate)([(0,a.EM)("step-flow-abort")],_),t()}catch(p){t(p)}}))},80887:function(e,t,i){"use strict";i.a(e,(async function(e,t){try{i(79827),i(35748),i(99342),i(65315),i(837),i(22416),i(37089),i(59023),i(12977),i(52885),i(5934),i(84755),i(95013);var o=i(69868),s=i(84922),a=i(11991),n=i(65940),r=i(73120),l=i(44537),d=i(92830),c=i(68985),h=i(44249),p=i(76943),u=i(39856),_=i(56083),f=i(2834),g=i(28027),m=i(45363),v=i(47420),w=i(59168),y=i(46472),b=i(88120),$=e([h,p]);[h,p]=$.then?(await $)():$;let x,k,C,M,z,E,D,S,F=e=>e;class q extends s.WF{firstUpdated(e){super.firstUpdated(e),this._loadDomains()}willUpdate(e){var t;if(!e.has("devices")&&!e.has("hass"))return;if(1!==this.devices.length||this.devices[0].primary_config_entry!==(null===(t=this.step.result)||void 0===t?void 0:t.entry_id)||"voip"===this.step.result.domain)return;const i=this._deviceEntities(this.devices[0].id,Object.values(this.hass.entities),"assist_satellite");i.length&&i.some((e=>(0,u.KC)(this.hass.states[e.entity_id])))&&(this.navigateToResult=!1,this._flowDone(),(0,w.L)(this,{deviceId:this.devices[0].id}))}render(){var e;const t=this.hass.localize,i=this.step.result?Object.assign(Object.assign({},this._domains),{},{[this.step.result.entry_id]:this.step.result.domain}):this._domains;return(0,s.qy)(x||(x=F`
      <div class="content">
        ${0}
        ${0}
        ${0}
      </div>
      <div class="buttons">
        <ha-button @click=${0}
          >${0}</ha-button
        >
      </div>
    `),this.flowConfig.renderCreateEntryDescription(this.hass,this.step),"not_loaded"===(null===(e=this.step.result)||void 0===e?void 0:e.state)?(0,s.qy)(k||(k=F`<span class="error"
              >${0}</span
            >`),t("ui.panel.config.integrations.config_flow.not_loaded")):s.s6,0===this.devices.length&&["options_flow","repair_flow"].includes(this.flowConfig.flowType)?s.s6:0===this.devices.length?(0,s.qy)(C||(C=F`<p>
                ${0}
              </p>`),t("ui.panel.config.integrations.config_flow.created_config",{name:this.step.title})):(0,s.qy)(M||(M=F`
                <div class="devices">
                  ${0}
                </div>
              `),this.devices.map((e=>{var o,a,n,r,d,c;return(0,s.qy)(z||(z=F`
                      <div class="device">
                        <div class="device-info">
                          ${0}
                          <div class="device-info-details">
                            <span>${0}</span>
                            ${0}
                          </div>
                        </div>
                        <ha-textfield
                          .label=${0}
                          .placeholder=${0}
                          .value=${0}
                          @change=${0}
                          .device=${0}
                        ></ha-textfield>
                        <ha-area-picker
                          .hass=${0}
                          .device=${0}
                          .value=${0}
                          @value-changed=${0}
                        ></ha-area-picker>
                      </div>
                    `),e.primary_config_entry&&i[e.primary_config_entry]?(0,s.qy)(E||(E=F`<img
                                slot="graphic"
                                alt=${0}
                                src=${0}
                                crossorigin="anonymous"
                                referrerpolicy="no-referrer"
                              />`),(0,g.p$)(this.hass.localize,i[e.primary_config_entry]),(0,m.MR)({domain:i[e.primary_config_entry],type:"icon",darkOptimized:null===(o=this.hass.themes)||void 0===o?void 0:o.darkMode})):s.s6,e.model||e.manufacturer,e.model?(0,s.qy)(D||(D=F`<span class="secondary">
                                  ${0}
                                </span>`),e.manufacturer):s.s6,t("ui.panel.config.integrations.config_flow.device_name"),(0,l.T)(e,this.hass),null!==(a=null===(n=this._deviceUpdate[e.id])||void 0===n?void 0:n.name)&&void 0!==a?a:(0,l.xn)(e),this._deviceNameChanged,e.id,this.hass,e.id,null!==(r=null!==(d=null===(c=this._deviceUpdate[e.id])||void 0===c?void 0:c.area)&&void 0!==d?d:e.area_id)&&void 0!==r?r:void 0,this._areaPicked)}))),this._flowDone,t("ui.panel.config.integrations.config_flow."+(!this.devices.length||Object.keys(this._deviceUpdate).length?"finish":"finish_skip")))}async _loadDomains(){const e=await(0,b.VN)(this.hass);this._domains=Object.fromEntries(e.map((e=>[e.entry_id,e.domain])))}async _flowDone(){if(Object.keys(this._deviceUpdate).length){const e=[],t=Object.entries(this._deviceUpdate).map((([t,i])=>(i.name&&e.push(t),(0,_.FB)(this.hass,t,{name_by_user:i.name,area_id:i.area}).catch((e=>{(0,v.K$)(this,{text:this.hass.localize("ui.panel.config.integrations.config_flow.error_saving_device",{error:e.message})})})))));await Promise.allSettled(t);const i=[],o=[];e.forEach((e=>{const t=this._deviceEntities(e,Object.values(this.hass.entities));o.push(...t.map((e=>e.entity_id)))}));const s=await(0,f.BM)(this.hass,o);Object.entries(s).forEach((([e,t])=>{t&&i.push((0,f.G_)(this.hass,e,{new_entity_id:t}).catch((e=>(0,v.K$)(this,{text:this.hass.localize("ui.panel.config.integrations.config_flow.error_saving_entity",{error:e.message})}))))})),await Promise.allSettled(i)}(0,r.r)(this,"flow-update",{step:void 0}),this.step.result&&this.navigateToResult&&(1===this.devices.length?(0,c.o)(`/config/devices/device/${this.devices[0].id}`):(0,c.o)(`/config/integrations/integration/${this.step.result.domain}#config_entry=${this.step.result.entry_id}`))}async _areaPicked(e){const t=e.currentTarget.device,i=e.detail.value;t in this._deviceUpdate||(this._deviceUpdate[t]={}),this._deviceUpdate[t].area=i,this.requestUpdate("_deviceUpdate")}_deviceNameChanged(e){const t=e.currentTarget,i=t.device,o=t.value;i in this._deviceUpdate||(this._deviceUpdate[i]={}),this._deviceUpdate[i].name=o,this.requestUpdate("_deviceUpdate")}static get styles(){return[y.G,(0,s.AH)(S||(S=F`
        .devices {
          display: flex;
          margin: -4px;
          max-height: 600px;
          overflow-y: auto;
          flex-direction: column;
        }
        @media all and (max-width: 450px), all and (max-height: 500px) {
          .devices {
            /* header - margin content - footer */
            max-height: calc(100vh - 52px - 20px - 52px);
          }
        }
        .device {
          border: 1px solid var(--divider-color);
          padding: 6px;
          border-radius: 4px;
          margin: 4px;
          display: inline-block;
        }
        .device-info {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .device-info img {
          width: 40px;
          height: 40px;
        }
        .device-info-details {
          display: flex;
          flex-direction: column;
          justify-content: center;
        }
        .secondary {
          color: var(--secondary-text-color);
        }
        ha-textfield,
        ha-area-picker {
          display: block;
        }
        ha-textfield {
          margin: 8px 0;
        }
        .buttons > *:last-child {
          margin-left: auto;
          margin-inline-start: auto;
          margin-inline-end: initial;
        }
        .error {
          color: var(--error-color);
        }
      `))]}constructor(...e){super(...e),this._domains={},this.navigateToResult=!1,this._deviceUpdate={},this._deviceEntities=(0,n.A)(((e,t,i)=>t.filter((t=>t.device_id===e&&(!i||(0,d.m)(t.entity_id)===i)))))}}(0,o.__decorate)([(0,a.MZ)({attribute:!1})],q.prototype,"flowConfig",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],q.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],q.prototype,"step",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],q.prototype,"devices",void 0),(0,o.__decorate)([(0,a.wk)()],q.prototype,"_deviceUpdate",void 0),q=(0,o.__decorate)([(0,a.EM)("step-flow-create-entry")],q),t()}catch(x){t(x)}}))},58365:function(e,t,i){"use strict";i.a(e,(async function(e,t){try{var o=i(69868),s=i(84922),a=i(11991),n=i(46472),r=i(76943),l=e([r]);r=(l.then?(await l)():l)[0];let d,c,h=e=>e;class p extends s.WF{render(){const e=this.hass.localize;return(0,s.qy)(d||(d=h`
      <div class="content">
        ${0}
        <div class="open-button">
          <ha-button href=${0} target="_blank" rel="noreferrer">
            ${0}
          </ha-button>
        </div>
      </div>
    `),this.flowConfig.renderExternalStepDescription(this.hass,this.step),this.step.url,e("ui.panel.config.integrations.config_flow.external_step.open_site"))}firstUpdated(e){super.firstUpdated(e),window.open(this.step.url)}static get styles(){return[n.G,(0,s.AH)(c||(c=h`
        .open-button {
          text-align: center;
          padding: 24px 0;
        }
        .open-button a {
          text-decoration: none;
        }
      `))]}}(0,o.__decorate)([(0,a.MZ)({attribute:!1})],p.prototype,"flowConfig",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],p.prototype,"step",void 0),p=(0,o.__decorate)([(0,a.EM)("step-flow-external")],p),t()}catch(d){t(d)}}))},34436:function(e,t,i){"use strict";i.a(e,(async function(e,t){try{i(79827),i(35748),i(65315),i(12840),i(84136),i(22416),i(37089),i(12977),i(5934),i(95013);var o=i(69868),s=i(84922),a=i(11991),n=i(65940),r=i(21431),l=i(73120),d=i(57183),c=i(76943),h=(i(23749),i(44840)),p=(i(75518),i(53199),i(71622)),u=i(4311),_=i(95237),f=i(83566),g=i(46472),m=e([c,p]);[c,p]=m.then?(await m)():m;let v,w,y,b,$=e=>e;class x extends s.WF{disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("keydown",this._handleKeyDown)}render(){const e=this.step,t=this._stepDataProcessed;return(0,s.qy)(v||(v=$`
      <div class="content" @click=${0}>
        ${0}
        ${0}
        <ha-form
          .hass=${0}
          .narrow=${0}
          .data=${0}
          .disabled=${0}
          @value-changed=${0}
          .schema=${0}
          .error=${0}
          .computeLabel=${0}
          .computeHelper=${0}
          .computeError=${0}
          .localizeValue=${0}
        ></ha-form>
      </div>
      ${0}
      <div class="buttons">
        <ha-button @click=${0} .loading=${0}>
          ${0}
        </ha-button>
      </div>
    `),this._clickHandler,this.flowConfig.renderShowFormStepDescription(this.hass,this.step),this._errorMsg?(0,s.qy)(w||(w=$`<ha-alert alert-type="error">${0}</ha-alert>`),this._errorMsg):"",this.hass,this.narrow,t,this._loading,this._stepDataChanged,(0,u.Hg)(this.handleReadOnlyFields(e.data_schema)),this._errors,this._labelCallback,this._helperCallback,this._errorCallback,this._localizeValueCallback,e.preview?(0,s.qy)(y||(y=$`<div class="preview" @set-flow-errors=${0}>
            <h3>
              ${0}:
            </h3>
            ${0}
          </div>`),this._setError,this.hass.localize("ui.panel.config.integrations.config_flow.preview"),(0,r._)(`flow-preview-${(0,_.F)(e.preview)}`,{hass:this.hass,domain:e.preview,flowType:this.flowConfig.flowType,handler:e.handler,stepId:e.step_id,flowId:e.flow_id,stepData:t})):s.s6,this._submitStep,this._loading,this.flowConfig.renderShowFormStepSubmitButton(this.hass,this.step))}_setError(e){this._previewErrors=e.detail}firstUpdated(e){super.firstUpdated(e),setTimeout((()=>this.shadowRoot.querySelector("ha-form").focus()),0),this.addEventListener("keydown",this._handleKeyDown)}willUpdate(e){var t;super.willUpdate(e),e.has("step")&&null!==(t=this.step)&&void 0!==t&&t.preview&&i(71289)(`./flow-preview-${(0,_.F)(this.step.preview)}`),(e.has("step")||e.has("_previewErrors")||e.has("_submitErrors"))&&(this._errors=this.step.errors||this._previewErrors||this._submitErrors?Object.assign(Object.assign(Object.assign({},this.step.errors),this._previewErrors),this._submitErrors):void 0)}_clickHandler(e){(0,d.d)(e,!1)&&(0,l.r)(this,"flow-update",{step:void 0})}get _stepDataProcessed(){return void 0!==this._stepData||(this._stepData=(0,h.$)(this.step.data_schema)),this._stepData}async _submitStep(){const e=this._stepData||{},t=(e,i)=>e.every((e=>(!e.required||!["",void 0].includes(i[e.name]))&&("expandable"!==e.type||!e.required&&void 0===i[e.name]||t(e.schema,i[e.name]))));if(!(void 0===e?void 0===this.step.data_schema.find((e=>e.required)):t(this.step.data_schema,e)))return void(this._errorMsg=this.hass.localize("ui.panel.config.integrations.config_flow.not_all_required_fields"));this._loading=!0,this._errorMsg=void 0,this._submitErrors=void 0;const i=this.step.flow_id,o={};Object.keys(e).forEach((t=>{var i,s,a;const n=e[t],r=[void 0,""].includes(n),l=null===(i=this.step.data_schema)||void 0===i?void 0:i.find((e=>e.name===t)),d=null!==(s=null==l?void 0:l.selector)&&void 0!==s?s:{},c=null===(a=Object.values(d)[0])||void 0===a?void 0:a.read_only;r||c||(o[t]=n)}));try{const e=await this.flowConfig.handleFlowStep(this.hass,this.step.flow_id,o);if(!this.step||i!==this.step.flow_id)return;this._previewErrors=void 0,(0,l.r)(this,"flow-update",{step:e})}catch(s){s&&s.body?(s.body.message&&(this._errorMsg=s.body.message),s.body.errors&&(this._submitErrors=s.body.errors),s.body.message||s.body.errors||(this._errorMsg="Unknown error occurred")):this._errorMsg="Unknown error occurred"}finally{this._loading=!1}}_stepDataChanged(e){this._stepData=e.detail.value}static get styles(){return[f.RF,g.G,(0,s.AH)(b||(b=$`
        .error {
          color: red;
        }

        ha-alert,
        ha-form {
          margin-top: 24px;
          display: block;
        }

        .buttons {
          padding: 16px;
        }
      `))]}constructor(...e){super(...e),this.narrow=!1,this._loading=!1,this.handleReadOnlyFields=(0,n.A)((e=>null==e?void 0:e.map((e=>{var t,i;return Object.assign(Object.assign({},e),null!==(t=Object.values(null!==(i=null==e?void 0:e.selector)&&void 0!==i?i:{})[0])&&void 0!==t&&t.read_only?{disabled:!0}:{})})))),this._handleKeyDown=e=>{"Enter"===e.key&&this._submitStep()},this._labelCallback=(e,t,i)=>this.flowConfig.renderShowFormStepFieldLabel(this.hass,this.step,e,i),this._helperCallback=(e,t)=>this.flowConfig.renderShowFormStepFieldHelper(this.hass,this.step,e,t),this._errorCallback=e=>this.flowConfig.renderShowFormStepFieldError(this.hass,this.step,e),this._localizeValueCallback=e=>this.flowConfig.renderShowFormStepFieldLocalizeValue(this.hass,this.step,e)}}(0,o.__decorate)([(0,a.MZ)({attribute:!1})],x.prototype,"flowConfig",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],x.prototype,"narrow",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],x.prototype,"step",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,o.__decorate)([(0,a.wk)()],x.prototype,"_loading",void 0),(0,o.__decorate)([(0,a.wk)()],x.prototype,"_stepData",void 0),(0,o.__decorate)([(0,a.wk)()],x.prototype,"_previewErrors",void 0),(0,o.__decorate)([(0,a.wk)()],x.prototype,"_submitErrors",void 0),(0,o.__decorate)([(0,a.wk)()],x.prototype,"_errorMsg",void 0),x=(0,o.__decorate)([(0,a.EM)("step-flow-form")],x),t()}catch(v){t(v)}}))},58784:function(e,t,i){"use strict";i.a(e,(async function(e,t){try{var o=i(69868),s=i(84922),a=i(11991),n=i(71622),r=e([n]);n=(r.then?(await r)():r)[0];let l,d,c,h=e=>e;class p extends s.WF{render(){const e=this.flowConfig.renderLoadingDescription(this.hass,this.loadingReason,this.handler,this.step);return(0,s.qy)(l||(l=h`
      <div class="content">
        <ha-spinner size="large"></ha-spinner>
        ${0}
      </div>
    `),e?(0,s.qy)(d||(d=h`<div>${0}</div>`),e):"")}}p.styles=(0,s.AH)(c||(c=h`
    .content {
      margin-top: 0;
      padding: 50px 100px;
      text-align: center;
    }
    ha-spinner {
      margin-bottom: 16px;
    }
  `)),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],p.prototype,"flowConfig",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],p.prototype,"loadingReason",void 0),(0,o.__decorate)([(0,a.MZ)()],p.prototype,"handler",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],p.prototype,"step",void 0),p=(0,o.__decorate)([(0,a.EM)("step-flow-loading")],p),t()}catch(l){t(l)}}))},93273:function(e,t,i){"use strict";i(35748),i(35058),i(65315),i(37089),i(52885),i(95013);var o=i(69868),s=i(84922),a=i(11991),n=i(73120),r=(i(72062),i(25223),i(46472)),l=i(90963);let d,c,h,p,u,_=e=>e;class f extends s.WF{shouldUpdate(e){var t;return e.size>1||!e.has("hass")||this.hass.localize!==(null===(t=e.get("hass"))||void 0===t?void 0:t.localize)}render(){let e,t,i={};if(Array.isArray(this.step.menu_options)){e=this.step.menu_options,t={};for(const o of e)t[o]=this.flowConfig.renderMenuOption(this.hass,this.step,o),i[o]=this.flowConfig.renderMenuOptionDescription(this.hass,this.step,o)}else e=Object.keys(this.step.menu_options),t=this.step.menu_options,i=Object.fromEntries(e.map((e=>[e,this.flowConfig.renderMenuOptionDescription(this.hass,this.step,e)])));this.step.sort&&(e=e.sort(((e,i)=>(0,l.xL)(t[e],t[i],this.hass.locale.language))));const o=this.flowConfig.renderMenuDescription(this.hass,this.step);return(0,s.qy)(d||(d=_`
      ${0}
      <div class="options">
        ${0}
      </div>
    `),o?(0,s.qy)(c||(c=_`<div class="content">${0}</div>`),o):"",e.map((e=>(0,s.qy)(h||(h=_`
            <ha-list-item
              hasMeta
              .step=${0}
              @click=${0}
              ?twoline=${0}
              ?multiline-secondary=${0}
            >
              <span>${0}</span>
              ${0}
              <ha-icon-next slot="meta"></ha-icon-next>
            </ha-list-item>
          `),e,this._handleStep,i[e],i[e],t[e],i[e]?(0,s.qy)(p||(p=_`<span slot="secondary">
                    ${0}
                  </span>`),i[e]):s.s6))))}_handleStep(e){(0,n.r)(this,"flow-update",{stepPromise:this.flowConfig.handleFlowStep(this.hass,this.step.flow_id,{next_step_id:e.currentTarget.step})})}}f.styles=[r.G,(0,s.AH)(u||(u=_`
      .options {
        margin-top: 20px;
        margin-bottom: 16px;
      }
      .content {
        padding-bottom: 16px;
      }
      .content + .options {
        margin-top: 8px;
      }
      ha-list-item {
        --mdc-list-side-padding: 24px;
      }
    `))],(0,o.__decorate)([(0,a.MZ)({attribute:!1})],f.prototype,"flowConfig",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],f.prototype,"step",void 0),f=(0,o.__decorate)([(0,a.EM)("step-flow-menu")],f)},23225:function(e,t,i){"use strict";i.a(e,(async function(e,t){try{var o=i(69868),s=i(84922),a=i(11991),n=i(3371),r=i(80527),l=i(71622),d=i(46472),c=e([r,l]);[r,l]=c.then?(await c)():c;let h,p,u,_,f=e=>e;class g extends s.WF{render(){return(0,s.qy)(h||(h=f`
      <div class="content">
        ${0}
        ${0}
      </div>
    `),this.progress?(0,s.qy)(p||(p=f`
              <ha-progress-ring .value=${0} size="large"
                >${0}${0}%</ha-progress-ring
              >
            `),this.progress,this.progress,(0,n.d)(this.hass.locale)):(0,s.qy)(u||(u=f`<ha-spinner size="large"></ha-spinner>`)),this.flowConfig.renderShowFormProgressDescription(this.hass,this.step))}static get styles(){return[d.G,(0,s.AH)(_||(_=f`
        .content {
          margin-top: 0;
          padding: 50px 100px;
          text-align: center;
        }
        ha-spinner {
          margin-bottom: 16px;
        }
      `))]}}(0,o.__decorate)([(0,a.MZ)({attribute:!1})],g.prototype,"flowConfig",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],g.prototype,"step",void 0),(0,o.__decorate)([(0,a.MZ)({type:Number})],g.prototype,"progress",void 0),g=(0,o.__decorate)([(0,a.EM)("step-flow-progress")],g),t()}catch(h){t(h)}}))},46472:function(e,t,i){"use strict";i.d(t,{G:function(){return s}});let o;const s=(0,i(84922).AH)(o||(o=(e=>e)`
  h2 {
    margin: 24px 38px 0 0;
    margin-inline-start: 0px;
    margin-inline-end: 38px;
    padding: 0 24px;
    padding-inline-start: 24px;
    padding-inline-end: 24px;
    -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
    -webkit-font-smoothing: var(--ha-font-smoothing);
    font-family: var(
      --mdc-typography-headline6-font-family,
      var(--mdc-typography-font-family, var(--ha-font-family-body))
    );
    font-size: var(--mdc-typography-headline6-font-size, var(--ha-font-size-l));
    line-height: var(--mdc-typography-headline6-line-height, 2rem);
    font-weight: var(
      --mdc-typography-headline6-font-weight,
      var(--ha-font-weight-medium)
    );
    letter-spacing: var(--mdc-typography-headline6-letter-spacing, 0.0125em);
    text-decoration: var(--mdc-typography-headline6-text-decoration, inherit);
    text-transform: var(--mdc-typography-headline6-text-transform, inherit);
    box-sizing: border-box;
  }

  .content,
  .preview {
    margin-top: 20px;
    padding: 0 24px;
  }

  .buttons {
    position: relative;
    padding: 16px;
    margin: 8px 0 0;
    color: var(--primary-color);
    display: flex;
    justify-content: flex-end;
  }

  ha-markdown {
    overflow-wrap: break-word;
  }
  ha-markdown a {
    color: var(--primary-color);
  }
  ha-markdown img:first-child:last-child {
    display: block;
    margin: 0 auto;
  }
`))},59168:function(e,t,i){"use strict";i.d(t,{L:function(){return a}});i(35748),i(5934),i(95013);var o=i(73120);const s=()=>Promise.all([i.e("6216"),i.e("9358"),i.e("9972"),i.e("615"),i.e("2719")]).then(i.bind(i,97938)),a=(e,t)=>{(0,o.r)(e,"show-dialog",{dialogTag:"ha-voice-assistant-setup-dialog",dialogImport:s,dialogParams:t})}},94100:function(e,t,i){"use strict";i.d(t,{a:function(){return a}});i(35748),i(5934),i(95013);var o=i(73120);const s=()=>Promise.all([i.e("357"),i.e("3089")]).then(i.bind(i,50184)),a=(e,t)=>{(0,o.r)(e,"show-dialog",{dialogTag:"dialog-add-application-credential",dialogImport:s,dialogParams:t})}},45363:function(e,t,i){"use strict";i.d(t,{MR:function(){return o},a_:function(){return s},bg:function(){return a}});i(56660);const o=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,s=e=>e.split("/")[4],a=e=>e.startsWith("https://brands.home-assistant.io/")},86435:function(e,t,i){"use strict";i.d(t,{o:function(){return o}});i(79827),i(18223);const o=(e,t)=>`https://${e.config.version.includes("b")?"rc":e.config.version.includes("dev")?"next":"www"}.home-assistant.io${t}`}}]);
//# sourceMappingURL=9316.95b52ab76cc6097f.js.map