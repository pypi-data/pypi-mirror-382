export const __webpack_id__="9316";export const __webpack_ids__=["9316"];export const __webpack_modules__={94732:function(e,t,o){var i={"./ha-icon-prev":["93302","7707"],"./ha-icon-button-toolbar":["1889","1994"],"./ha-alert":["23749"],"./ha-icon-button-toggle":["51892","725"],"./ha-svg-icon.ts":["95635"],"./ha-alert.ts":["23749"],"./ha-icon":["81164"],"./ha-icon-next.ts":["72062"],"./ha-qr-code.ts":["34772","3033","8613"],"./ha-icon-overflow-menu.ts":["35881","6216","7730"],"./ha-icon-button-toggle.ts":["51892","725"],"./ha-icon-button-group":["76469","2374"],"./ha-svg-icon":["95635"],"./ha-icon-button-prev":["36745","7778"],"./ha-icon-button.ts":["93672"],"./ha-icon-overflow-menu":["35881","6216","7730"],"./ha-icon-button-arrow-next":["71013","9430"],"./ha-icon-button-prev.ts":["36745","7778"],"./ha-icon-picker":["15785","7026"],"./ha-icon-button-toolbar.ts":["1889","1994"],"./ha-icon-button-arrow-prev.ts":["8101"],"./ha-icon-button-next":["75057","1962"],"./ha-icon-next":["72062"],"./ha-icon-picker.ts":["15785","7026"],"./ha-icon-prev.ts":["93302","7707"],"./ha-icon-button-arrow-prev":["8101"],"./ha-icon-button-next.ts":["75057","1962"],"./ha-icon.ts":["81164"],"./ha-qr-code":["34772","3033","8613"],"./ha-icon-button":["93672"],"./ha-icon-button-group.ts":["76469","2374"],"./ha-icon-button-arrow-next.ts":["71013","9430"]};function n(e){if(!o.o(i,e))return Promise.resolve().then((function(){var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}));var t=i[e],n=t[0];return Promise.all(t.slice(1).map(o.e)).then((function(){return o(n)}))}n.keys=()=>Object.keys(i),n.id=94732,e.exports=n},71289:function(e,t,o){var i={"./flow-preview-generic.ts":["83531","9358","1466","615","9531","1227"],"./flow-preview-template":["30282","9358","1466","615","9531","2311"],"./flow-preview-generic_camera":["43801","9358","1466","615","9531","386"],"./flow-preview-generic_camera.ts":["43801","9358","1466","615","9531","386"],"./flow-preview-generic":["83531","9358","1466","615","9531","1227"],"./flow-preview-template.ts":["30282","9358","1466","615","9531","2311"]};function n(e){if(!o.o(i,e))return Promise.resolve().then((function(){var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}));var t=i[e],n=t[0];return Promise.all(t.slice(1).map(o.e)).then((function(){return o(n)}))}n.keys=()=>Object.keys(i),n.id=71289,e.exports=n},57183:function(e,t,o){o.d(t,{d:()=>i});const i=(e,t=!0)=>{if(e.defaultPrevented||0!==e.button||e.metaKey||e.ctrlKey||e.shiftKey)return;const o=e.composedPath().find((e=>"A"===e.tagName));if(!o||o.target||o.hasAttribute("download")||"external"===o.getAttribute("rel"))return;let i=o.href;if(!i||-1!==i.indexOf("mailto:"))return;const n=window.location,a=n.origin||n.protocol+"//"+n.host;return 0===i.indexOf(a)&&(i=i.substr(a.length),"#"!==i)?(t&&e.preventDefault(),i):void 0}},44537:function(e,t,o){o.d(t,{xn:()=>a,T:()=>s});var i=o(65940),n=o(47379);const a=e=>(e.name_by_user||e.name)?.trim(),s=(e,t,o)=>a(e)||o&&r(t,o)||t.localize("ui.panel.config.devices.unnamed_device",{type:t.localize(`ui.panel.config.devices.type.${e.entry_type||"device"}`)}),r=(e,t)=>{for(const o of t||[]){const t="string"==typeof o?o:o.entity_id,i=e.states[t];if(i)return(0,n.u)(i)}};(0,i.A)((e=>function(e){const t=new Set,o=new Set;for(const i of e)o.has(i)?t.add(i):o.add(i);return t}(Object.values(e).map((e=>a(e))).filter((e=>void 0!==e)))))},3371:function(e,t,o){o.d(t,{d:()=>i});const i=e=>{switch(e.language){case"cs":case"de":case"fi":case"fr":case"sk":case"sv":return" ";default:return""}}},96997:function(e,t,o){var i=o(69868),n=o(84922),a=o(11991);class s extends n.WF{render(){return n.qy`
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
    `}static get styles(){return[n.AH`
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
      `]}}s=(0,i.__decorate)([(0,a.EM)("ha-dialog-header")],s)},44840:function(e,t,o){o.d(t,{$:()=>i});const i=e=>{const t={};return e.forEach((e=>{if(void 0!==e.description?.suggested_value&&null!==e.description?.suggested_value)t[e.name]=e.description.suggested_value;else if("default"in e)t[e.name]=e.default;else if("expandable"===e.type){const o=i(e.schema);(e.required||Object.keys(o).length)&&(t[e.name]=o)}else if(e.required){if("boolean"===e.type)t[e.name]=!1;else if("string"===e.type)t[e.name]="";else if("integer"===e.type)t[e.name]="valueMin"in e?e.valueMin:0;else if("constant"===e.type)t[e.name]=e.value;else if("float"===e.type)t[e.name]=0;else if("select"===e.type){if(e.options.length){const o=e.options[0];t[e.name]=Array.isArray(o)?o[0]:o}}else if("positive_time_period_dict"===e.type)t[e.name]={hours:0,minutes:0,seconds:0};else if("selector"in e){const o=e.selector;if("device"in o)t[e.name]=o.device?.multiple?[]:"";else if("entity"in o)t[e.name]=o.entity?.multiple?[]:"";else if("area"in o)t[e.name]=o.area?.multiple?[]:"";else if("label"in o)t[e.name]=o.label?.multiple?[]:"";else if("boolean"in o)t[e.name]=!1;else if("addon"in o||"attribute"in o||"file"in o||"icon"in o||"template"in o||"text"in o||"theme"in o||"object"in o)t[e.name]="";else if("number"in o)t[e.name]=o.number?.min??0;else if("select"in o){if(o.select?.options.length){const i=o.select.options[0],n="string"==typeof i?i:i.value;t[e.name]=o.select.multiple?[n]:n}}else if("country"in o)o.country?.countries?.length&&(t[e.name]=o.country.countries[0]);else if("language"in o)o.language?.languages?.length&&(t[e.name]=o.language.languages[0]);else if("duration"in o)t[e.name]={hours:0,minutes:0,seconds:0};else if("time"in o)t[e.name]="00:00:00";else if("date"in o||"datetime"in o){const o=(new Date).toISOString().slice(0,10);t[e.name]=`${o}T00:00:00`}else if("color_rgb"in o)t[e.name]=[0,0,0];else if("color_temp"in o)t[e.name]=o.color_temp?.min_mireds??153;else if("action"in o||"trigger"in o||"condition"in o)t[e.name]=[];else if("media"in o||"target"in o)t[e.name]={};else{if(!("state"in o))throw new Error(`Selector ${Object.keys(o)[0]} not supported in initial form data`);t[e.name]=o.state?.multiple?[]:""}}}else;})),t}},75518:function(e,t,o){var i=o(69868),n=o(84922),a=o(11991),s=o(21431),r=o(73120);o(23749),o(57674);const l={boolean:()=>o.e("2436").then(o.bind(o,33999)),constant:()=>o.e("3668").then(o.bind(o,33855)),float:()=>o.e("742").then(o.bind(o,84053)),grid:()=>o.e("7828").then(o.bind(o,57311)),expandable:()=>o.e("364").then(o.bind(o,51079)),integer:()=>o.e("7346").then(o.bind(o,40681)),multi_select:()=>Promise.all([o.e("6216"),o.e("3706")]).then(o.bind(o,99681)),positive_time_period_dict:()=>o.e("3540").then(o.bind(o,87551)),select:()=>o.e("2500").then(o.bind(o,10079)),string:()=>o.e("3627").then(o.bind(o,10070)),optional_actions:()=>o.e("3044").then(o.bind(o,96943))},d=(e,t)=>e?!t.name||t.flatten?e:e[t.name]:null;class c extends n.WF{getFormProperties(){return{}}async focus(){await this.updateComplete;const e=this.renderRoot.querySelector(".root");if(e)for(const t of e.children)if("HA-ALERT"!==t.tagName){t instanceof n.mN&&await t.updateComplete,t.focus();break}}willUpdate(e){e.has("schema")&&this.schema&&this.schema.forEach((e=>{"selector"in e||l[e.type]?.()}))}render(){return n.qy`
      <div class="root" part="root">
        ${this.error&&this.error.base?n.qy`
              <ha-alert alert-type="error">
                ${this._computeError(this.error.base,this.schema)}
              </ha-alert>
            `:""}
        ${this.schema.map((e=>{const t=((e,t)=>e&&t.name?e[t.name]:null)(this.error,e),o=((e,t)=>e&&t.name?e[t.name]:null)(this.warning,e);return n.qy`
            ${t?n.qy`
                  <ha-alert own-margin alert-type="error">
                    ${this._computeError(t,e)}
                  </ha-alert>
                `:o?n.qy`
                    <ha-alert own-margin alert-type="warning">
                      ${this._computeWarning(o,e)}
                    </ha-alert>
                  `:""}
            ${"selector"in e?n.qy`<ha-selector
                  .schema=${e}
                  .hass=${this.hass}
                  .narrow=${this.narrow}
                  .name=${e.name}
                  .selector=${e.selector}
                  .value=${d(this.data,e)}
                  .label=${this._computeLabel(e,this.data)}
                  .disabled=${e.disabled||this.disabled||!1}
                  .placeholder=${e.required?"":e.default}
                  .helper=${this._computeHelper(e)}
                  .localizeValue=${this.localizeValue}
                  .required=${e.required||!1}
                  .context=${this._generateContext(e)}
                ></ha-selector>`:(0,s._)(this.fieldElementName(e.type),{schema:e,data:d(this.data,e),label:this._computeLabel(e,this.data),helper:this._computeHelper(e),disabled:this.disabled||e.disabled||!1,hass:this.hass,localize:this.hass?.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(e),...this.getFormProperties()})}
          `}))}
      </div>
    `}fieldElementName(e){return`ha-form-${e}`}_generateContext(e){if(!e.context)return;const t={};for(const[o,i]of Object.entries(e.context))t[o]=this.data[i];return t}createRenderRoot(){const e=super.createRenderRoot();return this.addValueChangedListener(e),e}addValueChangedListener(e){e.addEventListener("value-changed",(e=>{e.stopPropagation();const t=e.target.schema;if(e.target===this)return;const o=!t.name||"flatten"in t&&t.flatten?e.detail.value:{[t.name]:e.detail.value};this.data={...this.data,...o},(0,r.r)(this,"value-changed",{value:this.data})}))}_computeLabel(e,t){return this.computeLabel?this.computeLabel(e,t):e?e.name:""}_computeHelper(e){return this.computeHelper?this.computeHelper(e):""}_computeError(e,t){return Array.isArray(e)?n.qy`<ul>
        ${e.map((e=>n.qy`<li>
              ${this.computeError?this.computeError(e,t):e}
            </li>`))}
      </ul>`:this.computeError?this.computeError(e,t):e}_computeWarning(e,t){return this.computeWarning?this.computeWarning(e,t):e}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1}}c.styles=n.AH`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `,(0,i.__decorate)([(0,a.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean})],c.prototype,"narrow",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],c.prototype,"data",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],c.prototype,"schema",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],c.prototype,"error",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],c.prototype,"warning",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],c.prototype,"computeError",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],c.prototype,"computeWarning",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],c.prototype,"computeLabel",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],c.prototype,"computeHelper",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],c.prototype,"localizeValue",void 0),c=(0,i.__decorate)([(0,a.EM)("ha-form")],c)},53199:function(e,t,o){var i=o(69868),n=o(84922),a=o(11991),s=o(34789),r=o.n(s),l=o(73120),d=o(57971);let c;const p=new class{get(e){return this._cache.get(e)}set(e,t){this._cache.set(e,t),this._expiration&&window.setTimeout((()=>this._cache.delete(e)),this._expiration)}has(e){return this._cache.has(e)}constructor(e){this._cache=new Map,this._expiration=e}}(1e3),h={reType:/(?<input>(\[!(?<type>caution|important|note|tip|warning)\])(?:\s|\\n)?)/i,typeToHaAlert:{caution:"error",important:"info",note:"info",tip:"success",warning:"warning"}};class _ extends n.mN{disconnectedCallback(){if(super.disconnectedCallback(),this.cache){const e=this._computeCacheKey();p.set(e,this.innerHTML)}}createRenderRoot(){return this}update(e){super.update(e),void 0!==this.content&&this._render()}willUpdate(e){if(!this.innerHTML&&this.cache){const e=this._computeCacheKey();p.has(e)&&(this.innerHTML=p.get(e),this._resize())}}_computeCacheKey(){return r()({content:this.content,allowSvg:this.allowSvg,allowDataUrl:this.allowDataUrl,breaks:this.breaks})}async _render(){this.innerHTML=await(async(e,t,i)=>(c||(c=(0,d.LV)(new Worker(new URL(o.p+o.u("5640"),o.b)))),c.renderMarkdown(e,t,i)))(String(this.content),{breaks:this.breaks,gfm:!0},{allowSvg:this.allowSvg,allowDataUrl:this.allowDataUrl}),this._resize();const e=document.createTreeWalker(this,NodeFilter.SHOW_ELEMENT,null);for(;e.nextNode();){const t=e.currentNode;if(t instanceof HTMLAnchorElement&&t.host!==document.location.host)t.target="_blank",t.rel="noreferrer noopener";else if(t instanceof HTMLImageElement)this.lazyImages&&(t.loading="lazy"),t.addEventListener("load",this._resize);else if(t instanceof HTMLQuoteElement){const o=t.firstElementChild?.firstChild?.textContent&&h.reType.exec(t.firstElementChild.firstChild.textContent);if(o){const{type:i}=o.groups,n=document.createElement("ha-alert");n.alertType=h.typeToHaAlert[i.toLowerCase()],n.append(...Array.from(t.childNodes).map((e=>{const t=Array.from(e.childNodes);if(!this.breaks&&t.length){const e=t[0];e.nodeType===Node.TEXT_NODE&&e.textContent===o.input&&e.textContent?.includes("\n")&&(e.textContent=e.textContent.split("\n").slice(1).join("\n"))}return t})).reduce(((e,t)=>e.concat(t)),[]).filter((e=>e.textContent&&e.textContent!==o.input))),e.parentNode().replaceChild(n,t)}}else t instanceof HTMLElement&&["ha-alert","ha-qr-code","ha-icon","ha-svg-icon"].includes(t.localName)&&o(94732)(`./${t.localName}`)}}constructor(...e){super(...e),this.allowSvg=!1,this.allowDataUrl=!1,this.breaks=!1,this.lazyImages=!1,this.cache=!1,this._resize=()=>(0,l.r)(this,"content-resize")}}(0,i.__decorate)([(0,a.MZ)()],_.prototype,"content",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:"allow-svg",type:Boolean})],_.prototype,"allowSvg",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:"allow-data-url",type:Boolean})],_.prototype,"allowDataUrl",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean})],_.prototype,"breaks",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean,attribute:"lazy-images"})],_.prototype,"lazyImages",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean})],_.prototype,"cache",void 0),_=(0,i.__decorate)([(0,a.EM)("ha-markdown-element")],_);class m extends n.WF{render(){return this.content?n.qy`<ha-markdown-element
      .content=${this.content}
      .allowSvg=${this.allowSvg}
      .allowDataUrl=${this.allowDataUrl}
      .breaks=${this.breaks}
      .lazyImages=${this.lazyImages}
      .cache=${this.cache}
    ></ha-markdown-element>`:n.s6}constructor(...e){super(...e),this.allowSvg=!1,this.allowDataUrl=!1,this.breaks=!1,this.lazyImages=!1,this.cache=!1}}m.styles=n.AH`
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
  `,(0,i.__decorate)([(0,a.MZ)()],m.prototype,"content",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:"allow-svg",type:Boolean})],m.prototype,"allowSvg",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:"allow-data-url",type:Boolean})],m.prototype,"allowDataUrl",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean})],m.prototype,"breaks",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean,attribute:"lazy-images"})],m.prototype,"lazyImages",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean})],m.prototype,"cache",void 0),m=(0,i.__decorate)([(0,a.EM)("ha-markdown")],m)},80527:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),n=o(35240),a=o(84922),s=o(11991),r=e([n]);n=(r.then?(await r)():r)[0];class l extends n.A{updated(e){if(super.updated(e),e.has("size"))switch(this.size){case"tiny":this.style.setProperty("--ha-progress-ring-size","16px");break;case"small":this.style.setProperty("--ha-progress-ring-size","28px");break;case"medium":this.style.setProperty("--ha-progress-ring-size","48px");break;case"large":this.style.setProperty("--ha-progress-ring-size","68px");break;case void 0:this.style.removeProperty("--ha-progress-ring-size")}}static get styles(){return[n.A.styles,a.AH`
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
      `]}}(0,i.__decorate)([(0,s.MZ)()],l.prototype,"size",void 0),l=(0,i.__decorate)([(0,s.EM)("ha-progress-ring")],l),t()}catch(l){t(l)}}))},39856:function(e,t,o){o.d(t,{KC:()=>c,Vy:()=>l,ds:()=>a,ew:()=>r,g5:()=>d,tl:()=>s});var i=o(68775),n=o(6098);const a=(e,t,o)=>e.connection.subscribeMessage(o,{type:"assist_satellite/intercept_wake_word",entity_id:t}),s=(e,t)=>e.callWS({type:"assist_satellite/test_connection",entity_id:t}),r=(e,t,o)=>e.callService("assist_satellite","announce",o,{entity_id:t}),l=(e,t)=>e.callWS({type:"assist_satellite/get_configuration",entity_id:t}),d=(e,t,o)=>e.callWS({type:"assist_satellite/set_wake_words",entity_id:t,wake_word_ids:o}),c=e=>e&&e.state!==n.Hh&&(0,i.$)(e,1)},4311:function(e,t,o){o.d(t,{Hg:()=>i,e0:()=>n});const i=e=>e.map((e=>{if("string"!==e.type)return e;switch(e.name){case"username":return{...e,autocomplete:"username",autofocus:!0};case"password":return{...e,autocomplete:"current-password"};case"code":return{...e,autocomplete:"one-time-code",autofocus:!0};default:return e}})),n=(e,t)=>e.callWS({type:"auth/sign_path",path:t})},582:function(e,t,o){o.d(t,{PN:()=>a,jm:()=>s,sR:()=>r,t1:()=>n,t2:()=>d,yu:()=>l});const i={"HA-Frontend-Base":`${location.protocol}//${location.host}`},n=(e,t,o)=>e.callApi("POST","config/config_entries/flow",{handler:t,show_advanced_options:Boolean(e.userData?.showAdvanced),entry_id:o},i),a=(e,t)=>e.callApi("GET",`config/config_entries/flow/${t}`,void 0,i),s=(e,t,o)=>e.callApi("POST",`config/config_entries/flow/${t}`,o,i),r=(e,t)=>e.callApi("DELETE",`config/config_entries/flow/${t}`),l=(e,t)=>e.callApi("GET","config/config_entries/flow_handlers"+(t?`?type=${t}`:"")),d=e=>e.sendMessagePromise({type:"config_entries/flow/progress"})},62013:function(e,t,o){o.d(t,{K:()=>n,P:()=>i});const i=(e,t)=>e.subscribeEvents(t,"data_entry_flow_progressed"),n=(e,t)=>e.subscribeEvents(t,"data_entry_flow_progress_update")},6098:function(e,t,o){o.d(t,{HV:()=>a,Hh:()=>n,KF:()=>r,ON:()=>s,g0:()=>c,s7:()=>l});var i=o(87383);const n="unavailable",a="unknown",s="on",r="off",l=[n,a],d=[n,a,r],c=(0,i.g)(l);(0,i.g)(d)},2834:function(e,t,o){o.d(t,{BM:()=>g,Bz:()=>_,G3:()=>d,G_:()=>c,Ox:()=>m,P9:()=>u,jh:()=>r,v:()=>l});var i=o(47308),n=o(65940),a=o(47379),s=(o(90963),o(24802));const r=(e,t)=>{if(t.name)return t.name;const o=e.states[t.entity_id];return o?(0,a.u)(o):t.original_name?t.original_name:t.entity_id},l=(e,t)=>e.callWS({type:"config/entity_registry/get",entity_id:t}),d=(e,t)=>e.callWS({type:"config/entity_registry/get_entries",entity_ids:t}),c=(e,t,o)=>e.callWS({type:"config/entity_registry/update",entity_id:t,...o}),p=e=>e.sendMessagePromise({type:"config/entity_registry/list"}),h=(e,t)=>e.subscribeEvents((0,s.s)((()=>p(e).then((e=>t.setState(e,!0)))),500,!0),"entity_registry_updated"),_=(e,t)=>(0,i.N)("_entityRegistry",p,h,e,t),m=(0,n.A)((e=>{const t={};for(const o of e)t[o.entity_id]=o;return t})),u=(0,n.A)((e=>{const t={};for(const o of e)t[o.id]=o;return t})),g=(e,t)=>e.callWS({type:"config/entity_registry/get_automatic_entity_ids",entity_ids:t})},95237:function(e,t,o){o.d(t,{F:()=>a,Q:()=>n});const i=["generic_camera","template"],n=(e,t,o,i,n,a)=>e.connection.subscribeMessage(a,{type:`${t}/start_preview`,flow_id:o,flow_type:i,user_input:n}),a=e=>i.includes(e)?e:"generic"},93167:function(e,t,o){o.a(e,(async function(e,i){try{o.r(t);var n=o(69868),a=o(84922),s=o(11991),r=o(65940),l=o(73120),d=(o(72847),o(96997),o(93672),o(62013)),c=o(83566),p=o(86435),h=o(47420),_=o(45493),m=o(80887),u=o(58365),g=o(34436),f=o(58784),w=(o(15654),o(23225)),y=o(16206),v=o(53700),b=o(44140),$=e([_,m,u,g,f,w]);[_,m,u,g,f,w]=$.then?(await $)():$;const x="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",k="M15.07,11.25L14.17,12.17C13.45,12.89 13,13.5 13,15H11V14.5C11,13.39 11.45,12.39 12.17,11.67L13.41,10.41C13.78,10.05 14,9.55 14,9C14,7.89 13.1,7 12,7A2,2 0 0,0 10,9H8A4,4 0 0,1 12,5A4,4 0 0,1 16,9C16,9.88 15.64,10.67 15.07,11.25M13,19H11V17H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12C22,6.47 17.5,2 12,2Z";let z=0;class S extends a.WF{async showDialog(e){this._params=e,this._instance=z++;const t=this._instance;let o;if(e.startFlowHandler){this._loading="loading_flow",this._handler=e.startFlowHandler;try{o=await this._params.flowConfig.createFlow(this.hass,e.startFlowHandler)}catch(i){this.closeDialog();let e=i.message||i.body||"Unknown error";return"string"!=typeof e&&(e=JSON.stringify(e)),void(0,h.K$)(this,{title:this.hass.localize("ui.panel.config.integrations.config_flow.error"),text:`${this.hass.localize("ui.panel.config.integrations.config_flow.could_not_load")}: ${e}`})}if(t!==this._instance)return}else{if(!e.continueFlowId)return;this._loading="loading_flow";try{o=await e.flowConfig.fetchFlow(this.hass,e.continueFlowId)}catch(i){this.closeDialog();let e=i.message||i.body||"Unknown error";return"string"!=typeof e&&(e=JSON.stringify(e)),void(0,h.K$)(this,{title:this.hass.localize("ui.panel.config.integrations.config_flow.error"),text:`${this.hass.localize("ui.panel.config.integrations.config_flow.could_not_load")}: ${e}`})}}t===this._instance&&(this._processStep(o),this._loading=void 0)}closeDialog(){if(!this._params)return;const e=Boolean(this._step&&["create_entry","abort"].includes(this._step.type));!this._step||e||this._params.continueFlowId||this._params.flowConfig.deleteFlow(this.hass,this._step.flow_id),this._step&&this._params.dialogClosedCallback&&this._params.dialogClosedCallback({flowFinished:e,entryId:"result"in this._step?this._step.result?.entry_id:void 0}),this._loading=void 0,this._step=void 0,this._params=void 0,this._handler=void 0,this._unsubDataEntryFlowProgress&&(this._unsubDataEntryFlowProgress(),this._unsubDataEntryFlowProgress=void 0),(0,l.r)(this,"dialog-closed",{dialog:this.localName})}_getDialogTitle(){if(this._loading||!this._step||!this._params)return"";switch(this._step.type){case"form":return this._params.flowConfig.renderShowFormStepHeader(this.hass,this._step);case"abort":return this._params.flowConfig.renderAbortHeader?this._params.flowConfig.renderAbortHeader(this.hass,this._step):this.hass.localize(`component.${this._params.domain??this._step.handler}.title`);case"progress":return this._params.flowConfig.renderShowFormProgressHeader(this.hass,this._step);case"menu":return this._params.flowConfig.renderMenuHeader(this.hass,this._step);case"create_entry":{const e=this._devices(this._params.flowConfig.showDevices,Object.values(this.hass.devices),this._step.result?.entry_id,this._params.carryOverDevices).length;return this.hass.localize("ui.panel.config.integrations.config_flow."+(e?"device_created":"success"),{number:e})}default:return""}}_getDialogSubtitle(){if(this._loading||!this._step||!this._params)return"";switch(this._step.type){case"form":return this._params.flowConfig.renderShowFormStepSubheader?.(this.hass,this._step);case"abort":return this._params.flowConfig.renderAbortSubheader?.(this.hass,this._step);case"progress":return this._params.flowConfig.renderShowFormProgressSubheader?.(this.hass,this._step);case"menu":return this._params.flowConfig.renderMenuSubheader?.(this.hass,this._step);default:return""}}render(){if(!this._params)return a.s6;const e=["form","menu","external","progress","data_entry_flow_progressed"].includes(this._step?.type)&&this._params.manifest?.is_built_in||!!this._params.manifest?.documentation,t=this._getDialogTitle(),o=this._getDialogSubtitle();return a.qy`
      <ha-dialog
        open
        @closed=${this.closeDialog}
        scrimClickAction
        escapeKeyAction
        hideActions
        .heading=${t||!0}
      >
        <ha-dialog-header slot="heading">
          <ha-icon-button
            .label=${this.hass.localize("ui.common.close")}
            .path=${x}
            dialogAction="close"
            slot="navigationIcon"
          ></ha-icon-button>

          <div
            slot="title"
            class="dialog-title${"form"===this._step?.type?" form":""}"
            title=${t}
          >
            ${t}
          </div>

          ${o?a.qy` <div slot="subtitle">${o}</div>`:a.s6}
          ${e&&!this._loading&&this._step?a.qy`
                <a
                  slot="actionItems"
                  class="help"
                  href=${this._params.manifest.is_built_in?(0,p.o)(this.hass,`/integrations/${this._params.manifest.domain}`):this._params.manifest.documentation}
                  target="_blank"
                  rel="noreferrer noopener"
                >
                  <ha-icon-button
                    .label=${this.hass.localize("ui.common.help")}
                    .path=${k}
                  >
                  </ha-icon-button
                ></a>
              `:a.s6}
        </ha-dialog-header>
        <div>
          ${this._loading||null===this._step?a.qy`
                <step-flow-loading
                  .flowConfig=${this._params.flowConfig}
                  .hass=${this.hass}
                  .loadingReason=${this._loading}
                  .handler=${this._handler}
                  .step=${this._step}
                ></step-flow-loading>
              `:void 0===this._step?a.s6:a.qy`
                  ${"form"===this._step.type?a.qy`
                        <step-flow-form
                          narrow
                          .flowConfig=${this._params.flowConfig}
                          .step=${this._step}
                          .hass=${this.hass}
                        ></step-flow-form>
                      `:"external"===this._step.type?a.qy`
                          <step-flow-external
                            .flowConfig=${this._params.flowConfig}
                            .step=${this._step}
                            .hass=${this.hass}
                          ></step-flow-external>
                        `:"abort"===this._step.type?a.qy`
                            <step-flow-abort
                              .params=${this._params}
                              .step=${this._step}
                              .hass=${this.hass}
                              .handler=${this._step.handler}
                              .domain=${this._params.domain??this._step.handler}
                            ></step-flow-abort>
                          `:"progress"===this._step.type?a.qy`
                              <step-flow-progress
                                .flowConfig=${this._params.flowConfig}
                                .step=${this._step}
                                .hass=${this.hass}
                                .progress=${this._progress}
                              ></step-flow-progress>
                            `:"menu"===this._step.type?a.qy`
                                <step-flow-menu
                                  .flowConfig=${this._params.flowConfig}
                                  .step=${this._step}
                                  .hass=${this.hass}
                                ></step-flow-menu>
                              `:a.qy`
                                <step-flow-create-entry
                                  .flowConfig=${this._params.flowConfig}
                                  .step=${this._step}
                                  .hass=${this.hass}
                                  .navigateToResult=${this._params.navigateToResult??!1}
                                  .devices=${this._devices(this._params.flowConfig.showDevices,Object.values(this.hass.devices),this._step.result?.entry_id,this._params.carryOverDevices)}
                                ></step-flow-create-entry>
                              `}
                `}
        </div>
      </ha-dialog>
    `}firstUpdated(e){super.firstUpdated(e),this.addEventListener("flow-update",(e=>{const{step:t,stepPromise:o}=e.detail;this._processStep(t||o)}))}willUpdate(e){super.willUpdate(e),e.has("_step")&&this._step&&["external","progress"].includes(this._step.type)&&this._subscribeDataEntryFlowProgressed()}async _processStep(e){if(void 0===e)return void this.closeDialog();const t=setTimeout((()=>{this._loading="loading_step"}),250);let o;try{o=await e}catch(i){return this.closeDialog(),void(0,h.K$)(this,{title:this.hass.localize("ui.panel.config.integrations.config_flow.error"),text:i?.body?.message})}finally{clearTimeout(t),this._loading=void 0}this._step=void 0,await this.updateComplete,this._step=o,"create_entry"===o.type&&o.next_flow&&(this._step=void 0,this._handler=void 0,this._unsubDataEntryFlowProgress&&(this._unsubDataEntryFlowProgress(),this._unsubDataEntryFlowProgress=void 0),"config_flow"===o.next_flow[0]?(0,b.W)(this._params.dialogParentElement,{continueFlowId:o.next_flow[1],carryOverDevices:this._devices(this._params.flowConfig.showDevices,Object.values(this.hass.devices),o.result?.entry_id,this._params.carryOverDevices).map((e=>e.id)),dialogClosedCallback:this._params.dialogClosedCallback}):"options_flow"===o.next_flow[0]?(0,y.Q)(this._params.dialogParentElement,o.result,{continueFlowId:o.next_flow[1],navigateToResult:this._params.navigateToResult,dialogClosedCallback:this._params.dialogClosedCallback}):"config_subentries_flow"===o.next_flow[0]?(0,v.a)(this._params.dialogParentElement,o.result,o.next_flow[0],{continueFlowId:o.next_flow[1],navigateToResult:this._params.navigateToResult,dialogClosedCallback:this._params.dialogClosedCallback}):(this.closeDialog(),(0,h.K$)(this._params.dialogParentElement,{text:this.hass.localize("ui.panel.config.integrations.config_flow.error",{error:`Unsupported next flow type: ${o.next_flow[0]}`})})))}async _subscribeDataEntryFlowProgressed(){if(this._unsubDataEntryFlowProgress)return;this._progress=void 0;const e=[(0,d.P)(this.hass.connection,(e=>{e.data.flow_id===this._step?.flow_id&&(this._processStep(this._params.flowConfig.fetchFlow(this.hass,this._step.flow_id)),this._progress=void 0)})),(0,d.K)(this.hass.connection,(e=>{this._progress=Math.ceil(100*e.data.progress)}))];this._unsubDataEntryFlowProgress=async()=>{(await Promise.all(e)).map((e=>e()))}}static get styles(){return[c.nA,a.AH`
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
      `]}constructor(...e){super(...e),this._instance=z,this._devices=(0,r.A)(((e,t,o,i)=>e&&o?t.filter((e=>e.config_entries.includes(o)||i?.includes(e.id))):[]))}}(0,n.__decorate)([(0,s.MZ)({attribute:!1})],S.prototype,"hass",void 0),(0,n.__decorate)([(0,s.wk)()],S.prototype,"_params",void 0),(0,n.__decorate)([(0,s.wk)()],S.prototype,"_loading",void 0),(0,n.__decorate)([(0,s.wk)()],S.prototype,"_progress",void 0),(0,n.__decorate)([(0,s.wk)()],S.prototype,"_step",void 0),(0,n.__decorate)([(0,s.wk)()],S.prototype,"_handler",void 0),S=(0,n.__decorate)([(0,s.EM)("dialog-data-entry-flow")],S),i()}catch(x){i(x)}}))},44140:function(e,t,o){o.d(t,{W:()=>r});var i=o(84922),n=o(582),a=o(28027),s=o(5361);const r=(e,t)=>(0,s.g)(e,t,{flowType:"config_flow",showDevices:!0,createFlow:async(e,o)=>{const[i]=await Promise.all([(0,n.t1)(e,o,t.entryId),e.loadFragmentTranslation("config"),e.loadBackendTranslation("config",o),e.loadBackendTranslation("selector",o),e.loadBackendTranslation("title",o)]);return i},fetchFlow:async(e,t)=>{const[o]=await Promise.all([(0,n.PN)(e,t),e.loadFragmentTranslation("config")]);return await Promise.all([e.loadBackendTranslation("config",o.handler),e.loadBackendTranslation("selector",o.handler),e.loadBackendTranslation("title",o.handler)]),o},handleFlowStep:n.jm,deleteFlow:n.sR,renderAbortDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.abort.${t.reason}`,t.description_placeholders);return o?i.qy`
            <ha-markdown allow-svg breaks .content=${o}></ha-markdown>
          `:t.reason},renderShowFormStepHeader(e,t){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.title`,t.description_placeholders)||e.localize(`component.${t.handler}.title`)},renderShowFormStepDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.description`,t.description_placeholders);return o?i.qy`
            <ha-markdown
              .allowDataUrl=${"zwave_js"===t.handler}
              allow-svg
              breaks
              .content=${o}
            ></ha-markdown>
          `:""},renderShowFormStepFieldLabel(e,t,o,i){if("expandable"===o.type)return e.localize(`component.${t.handler}.config.step.${t.step_id}.sections.${o.name}.name`,t.description_placeholders);const n=i?.path?.[0]?`sections.${i.path[0]}.`:"";return e.localize(`component.${t.handler}.config.step.${t.step_id}.${n}data.${o.name}`,t.description_placeholders)||o.name},renderShowFormStepFieldHelper(e,t,o,n){if("expandable"===o.type)return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.sections.${o.name}.description`,t.description_placeholders);const a=n?.path?.[0]?`sections.${n.path[0]}.`:"",s=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.${a}data_description.${o.name}`,t.description_placeholders);return s?i.qy`<ha-markdown breaks .content=${s}></ha-markdown>`:""},renderShowFormStepFieldError(e,t,o){return e.localize(`component.${t.translation_domain||t.translation_domain||t.handler}.config.error.${o}`,t.description_placeholders)||o},renderShowFormStepFieldLocalizeValue(e,t,o){return e.localize(`component.${t.handler}.selector.${o}`)},renderShowFormStepSubmitButton(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.submit`)||e.localize("ui.panel.config.integrations.config_flow."+(!1===t.last_step?"next":"submit"))},renderExternalStepHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize("ui.panel.config.integrations.config_flow.external_step.open_site")},renderExternalStepDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.${t.step_id}.description`,t.description_placeholders);return i.qy`
        <p>
          ${e.localize("ui.panel.config.integrations.config_flow.external_step.description")}
        </p>
        ${o?i.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${o}
              ></ha-markdown>
            `:""}
      `},renderCreateEntryDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.create_entry.${t.description||"default"}`,t.description_placeholders);return i.qy`
        ${o?i.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${o}
              ></ha-markdown>
            `:i.s6}
      `},renderShowFormProgressHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize(`component.${t.handler}.title`)},renderShowFormProgressDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.progress.${t.progress_action}`,t.description_placeholders);return o?i.qy`
            <ha-markdown allow-svg breaks .content=${o}></ha-markdown>
          `:""},renderMenuHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize(`component.${t.handler}.title`)},renderMenuDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.description`,t.description_placeholders);return o?i.qy`
            <ha-markdown allow-svg breaks .content=${o}></ha-markdown>
          `:""},renderMenuOption(e,t,o){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.menu_options.${o}`,t.description_placeholders)},renderMenuOptionDescription(e,t,o){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.menu_option_descriptions.${o}`,t.description_placeholders)},renderLoadingDescription(e,t,o,i){if("loading_flow"!==t&&"loading_step"!==t)return"";const n=i?.handler||o;return e.localize(`ui.panel.config.integrations.config_flow.loading.${t}`,{integration:n?(0,a.p$)(e.localize,n):e.localize("ui.panel.config.integrations.config_flow.loading.fallback_title")})}})},16206:function(e,t,o){o.d(t,{Q:()=>c});var i=o(84922),n=o(28027);const a=(e,t)=>e.callApi("POST","config/config_entries/options/flow",{handler:t,show_advanced_options:Boolean(e.userData?.showAdvanced)}),s=(e,t)=>e.callApi("GET",`config/config_entries/options/flow/${t}`),r=(e,t,o)=>e.callApi("POST",`config/config_entries/options/flow/${t}`,o),l=(e,t)=>e.callApi("DELETE",`config/config_entries/options/flow/${t}`);var d=o(5361);const c=(e,t,o)=>(0,d.g)(e,{startFlowHandler:t.entry_id,domain:t.domain,...o},{flowType:"options_flow",showDevices:!1,createFlow:async(e,o)=>{const[i]=await Promise.all([a(e,o),e.loadFragmentTranslation("config"),e.loadBackendTranslation("options",t.domain),e.loadBackendTranslation("selector",t.domain)]);return i},fetchFlow:async(e,o)=>{const[i]=await Promise.all([s(e,o),e.loadFragmentTranslation("config"),e.loadBackendTranslation("options",t.domain),e.loadBackendTranslation("selector",t.domain)]);return i},handleFlowStep:r,deleteFlow:l,renderAbortDescription(e,o){const n=e.localize(`component.${o.translation_domain||t.domain}.options.abort.${o.reason}`,o.description_placeholders);return n?i.qy`
              <ha-markdown
                breaks
                allow-svg
                .content=${n}
              ></ha-markdown>
            `:o.reason},renderShowFormStepHeader(e,o){return e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.title`,o.description_placeholders)||e.localize("ui.dialogs.options_flow.form.header")},renderShowFormStepDescription(e,o){const n=e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.description`,o.description_placeholders);return n?i.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${n}
              ></ha-markdown>
            `:""},renderShowFormStepFieldLabel(e,o,i,n){if("expandable"===i.type)return e.localize(`component.${t.domain}.options.step.${o.step_id}.sections.${i.name}.name`,o.description_placeholders);const a=n?.path?.[0]?`sections.${n.path[0]}.`:"";return e.localize(`component.${t.domain}.options.step.${o.step_id}.${a}data.${i.name}`,o.description_placeholders)||i.name},renderShowFormStepFieldHelper(e,o,n,a){if("expandable"===n.type)return e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.sections.${n.name}.description`,o.description_placeholders);const s=a?.path?.[0]?`sections.${a.path[0]}.`:"",r=e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.${s}data_description.${n.name}`,o.description_placeholders);return r?i.qy`<ha-markdown breaks .content=${r}></ha-markdown>`:""},renderShowFormStepFieldError(e,o,i){return e.localize(`component.${o.translation_domain||t.domain}.options.error.${i}`,o.description_placeholders)||i},renderShowFormStepFieldLocalizeValue(e,o,i){return e.localize(`component.${t.domain}.selector.${i}`)},renderShowFormStepSubmitButton(e,o){return e.localize(`component.${t.domain}.options.step.${o.step_id}.submit`)||e.localize("ui.panel.config.integrations.config_flow."+(!1===o.last_step?"next":"submit"))},renderExternalStepHeader(e,t){return""},renderExternalStepDescription(e,t){return""},renderCreateEntryDescription(e,t){return i.qy`
          <p>${e.localize("ui.dialogs.options_flow.success.description")}</p>
        `},renderShowFormProgressHeader(e,o){return e.localize(`component.${t.domain}.options.step.${o.step_id}.title`)||e.localize(`component.${t.domain}.title`)},renderShowFormProgressDescription(e,o){const n=e.localize(`component.${o.translation_domain||t.domain}.options.progress.${o.progress_action}`,o.description_placeholders);return n?i.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${n}
              ></ha-markdown>
            `:""},renderMenuHeader(e,o){return e.localize(`component.${t.domain}.options.step.${o.step_id}.title`)||e.localize(`component.${t.domain}.title`)},renderMenuDescription(e,o){const n=e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.description`,o.description_placeholders);return n?i.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${n}
              ></ha-markdown>
            `:""},renderMenuOption(e,o,i){return e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.menu_options.${i}`,o.description_placeholders)},renderMenuOptionDescription(e,o,i){return e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.menu_option_descriptions.${i}`,o.description_placeholders)},renderLoadingDescription(e,o){return e.localize(`component.${t.domain}.options.loading`)||("loading_flow"===o||"loading_step"===o?e.localize(`ui.dialogs.options_flow.loading.${o}`,{integration:(0,n.p$)(e.localize,t.domain)}):"")}})},53700:function(e,t,o){o.d(t,{a:()=>c});var i=o(84922),n=o(28027);const a={"HA-Frontend-Base":`${location.protocol}//${location.host}`},s=(e,t,o,i)=>e.callApi("POST","config/config_entries/subentries/flow",{handler:[t,o],show_advanced_options:Boolean(e.userData?.showAdvanced),subentry_id:i},a),r=(e,t,o)=>e.callApi("POST",`config/config_entries/subentries/flow/${t}`,o,a),l=(e,t)=>e.callApi("DELETE",`config/config_entries/subentries/flow/${t}`);var d=o(5361);const c=(e,t,o,c)=>(0,d.g)(e,c,{flowType:"config_subentries_flow",showDevices:!0,createFlow:async(e,i)=>{const[n]=await Promise.all([s(e,i,o,c.subEntryId),e.loadFragmentTranslation("config"),e.loadBackendTranslation("config_subentries",t.domain),e.loadBackendTranslation("selector",t.domain),e.loadBackendTranslation("title",t.domain)]);return n},fetchFlow:async(e,o)=>{const i=await((e,t)=>e.callApi("GET",`config/config_entries/subentries/flow/${t}`,void 0,a))(e,o);return await e.loadFragmentTranslation("config"),await e.loadBackendTranslation("config_subentries",t.domain),await e.loadBackendTranslation("selector",t.domain),i},handleFlowStep:r,deleteFlow:l,renderAbortDescription(e,n){const a=e.localize(`component.${n.translation_domain||t.domain}.config_subentries.${o}.abort.${n.reason}`,n.description_placeholders);return a?i.qy`
            <ha-markdown allowsvg breaks .content=${a}></ha-markdown>
          `:n.reason},renderShowFormStepHeader(e,i){return e.localize(`component.${i.translation_domain||t.domain}.config_subentries.${o}.step.${i.step_id}.title`,i.description_placeholders)||e.localize(`component.${t.domain}.title`)},renderShowFormStepDescription(e,n){const a=e.localize(`component.${n.translation_domain||t.domain}.config_subentries.${o}.step.${n.step_id}.description`,n.description_placeholders);return a?i.qy`
            <ha-markdown allowsvg breaks .content=${a}></ha-markdown>
          `:""},renderShowFormStepFieldLabel(e,i,n,a){if("expandable"===n.type)return e.localize(`component.${t.domain}.config_subentries.${o}.step.${i.step_id}.sections.${n.name}.name`,i.description_placeholders);const s=a?.path?.[0]?`sections.${a.path[0]}.`:"";return e.localize(`component.${t.domain}.config_subentries.${o}.step.${i.step_id}.${s}data.${n.name}`,i.description_placeholders)||n.name},renderShowFormStepFieldHelper(e,n,a,s){if("expandable"===a.type)return e.localize(`component.${n.translation_domain||t.domain}.config_subentries.${o}.step.${n.step_id}.sections.${a.name}.description`,n.description_placeholders);const r=s?.path?.[0]?`sections.${s.path[0]}.`:"",l=e.localize(`component.${n.translation_domain||t.domain}.config_subentries.${o}.step.${n.step_id}.${r}data_description.${a.name}`,n.description_placeholders);return l?i.qy`<ha-markdown breaks .content=${l}></ha-markdown>`:""},renderShowFormStepFieldError(e,i,n){return e.localize(`component.${i.translation_domain||i.translation_domain||t.domain}.config_subentries.${o}.error.${n}`,i.description_placeholders)||n},renderShowFormStepFieldLocalizeValue(e,o,i){return e.localize(`component.${t.domain}.selector.${i}`)},renderShowFormStepSubmitButton(e,i){return e.localize(`component.${t.domain}.config_subentries.${o}.step.${i.step_id}.submit`)||e.localize("ui.panel.config.integrations.config_flow."+(!1===i.last_step?"next":"submit"))},renderExternalStepHeader(e,i){return e.localize(`component.${t.domain}.config_subentries.${o}.step.${i.step_id}.title`)||e.localize("ui.panel.config.integrations.config_flow.external_step.open_site")},renderExternalStepDescription(e,n){const a=e.localize(`component.${n.translation_domain||t.domain}.config_subentries.${o}.step.${n.step_id}.description`,n.description_placeholders);return i.qy`
        <p>
          ${e.localize("ui.panel.config.integrations.config_flow.external_step.description")}
        </p>
        ${a?i.qy`
              <ha-markdown
                allowsvg
                breaks
                .content=${a}
              ></ha-markdown>
            `:""}
      `},renderCreateEntryDescription(e,n){const a=e.localize(`component.${n.translation_domain||t.domain}.config_subentries.${o}.create_entry.${n.description||"default"}`,n.description_placeholders);return i.qy`
        ${a?i.qy`
              <ha-markdown
                allowsvg
                breaks
                .content=${a}
              ></ha-markdown>
            `:i.s6}
      `},renderShowFormProgressHeader(e,i){return e.localize(`component.${t.domain}.config_subentries.${o}.step.${i.step_id}.title`)||e.localize(`component.${t.domain}.title`)},renderShowFormProgressDescription(e,n){const a=e.localize(`component.${n.translation_domain||t.domain}.config_subentries.${o}.progress.${n.progress_action}`,n.description_placeholders);return a?i.qy`
            <ha-markdown allowsvg breaks .content=${a}></ha-markdown>
          `:""},renderMenuHeader(e,i){return e.localize(`component.${t.domain}.config_subentries.${o}.step.${i.step_id}.title`,i.description_placeholders)||e.localize(`component.${t.domain}.title`)},renderMenuDescription(e,n){const a=e.localize(`component.${n.translation_domain||t.domain}.config_subentries.${o}.step.${n.step_id}.description`,n.description_placeholders);return a?i.qy`
            <ha-markdown allowsvg breaks .content=${a}></ha-markdown>
          `:""},renderMenuOption(e,i,n){return e.localize(`component.${i.translation_domain||t.domain}.config_subentries.${o}.step.${i.step_id}.menu_options.${n}`,i.description_placeholders)},renderMenuOptionDescription(e,i,n){return e.localize(`component.${i.translation_domain||t.domain}.config_subentries.${o}.step.${i.step_id}.menu_option_descriptions.${n}`,i.description_placeholders)},renderLoadingDescription(e,t,o,i){if("loading_flow"!==t&&"loading_step"!==t)return"";const a=i?.handler||o;return e.localize(`ui.panel.config.integrations.config_flow.loading.${t}`,{integration:a?(0,n.p$)(e.localize,a):e.localize("ui.panel.config.integrations.config_flow.loading.fallback_title")})}})},45493:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),n=o(84922),a=o(11991),s=o(73120),r=o(94100),l=o(44140),d=o(46472),c=o(76943),p=e([c]);c=(p.then?(await p)():p)[0];class h extends n.WF{firstUpdated(e){super.firstUpdated(e),"missing_credentials"===this.step.reason&&this._handleMissingCreds()}render(){return"missing_credentials"===this.step.reason?n.s6:n.qy`
      <div class="content">
        ${this.params.flowConfig.renderAbortDescription(this.hass,this.step)}
      </div>
      <div class="buttons">
        <ha-button appearance="plain" @click=${this._flowDone}
          >${this.hass.localize("ui.panel.config.integrations.config_flow.close")}</ha-button
        >
      </div>
    `}async _handleMissingCreds(){(0,r.a)(this.params.dialogParentElement,{selectedDomain:this.domain,manifest:this.params.manifest,applicationCredentialAddedCallback:()=>{(0,l.W)(this.params.dialogParentElement,{dialogClosedCallback:this.params.dialogClosedCallback,startFlowHandler:this.handler,showAdvanced:this.hass.userData?.showAdvanced,navigateToResult:this.params.navigateToResult})}}),this._flowDone()}_flowDone(){(0,s.r)(this,"flow-update",{step:void 0})}static get styles(){return d.G}}(0,i.__decorate)([(0,a.MZ)({attribute:!1})],h.prototype,"params",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],h.prototype,"step",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],h.prototype,"domain",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],h.prototype,"handler",void 0),h=(0,i.__decorate)([(0,a.EM)("step-flow-abort")],h),t()}catch(h){t(h)}}))},80887:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),n=o(84922),a=o(11991),s=o(65940),r=o(73120),l=o(44537),d=o(92830),c=o(68985),p=(o(44249),o(76943)),h=o(39856),_=o(6041),m=o(2834),u=o(28027),g=o(45363),f=o(47420),w=o(59168),y=o(46472),v=o(88120),b=e([p]);p=(b.then?(await b)():b)[0];class $ extends n.WF{firstUpdated(e){super.firstUpdated(e),this._loadDomains()}willUpdate(e){if(!e.has("devices")&&!e.has("hass"))return;if(1!==this.devices.length||this.devices[0].primary_config_entry!==this.step.result?.entry_id||"voip"===this.step.result.domain)return;const t=this._deviceEntities(this.devices[0].id,Object.values(this.hass.entities),"assist_satellite");t.length&&t.some((e=>(0,h.KC)(this.hass.states[e.entity_id])))&&(this.navigateToResult=!1,this._flowDone(),(0,w.L)(this,{deviceId:this.devices[0].id}))}render(){const e=this.hass.localize,t=this.step.result?{...this._domains,[this.step.result.entry_id]:this.step.result.domain}:this._domains;return n.qy`
      <div class="content">
        ${this.flowConfig.renderCreateEntryDescription(this.hass,this.step)}
        ${"not_loaded"===this.step.result?.state?n.qy`<span class="error"
              >${e("ui.panel.config.integrations.config_flow.not_loaded")}</span
            >`:n.s6}
        ${0===this.devices.length&&["options_flow","repair_flow"].includes(this.flowConfig.flowType)?n.s6:0===this.devices.length?n.qy`<p>
                ${e("ui.panel.config.integrations.config_flow.created_config",{name:this.step.title})}
              </p>`:n.qy`
                <div class="devices">
                  ${this.devices.map((o=>n.qy`
                      <div class="device">
                        <div class="device-info">
                          ${o.primary_config_entry&&t[o.primary_config_entry]?n.qy`<img
                                slot="graphic"
                                alt=${(0,u.p$)(this.hass.localize,t[o.primary_config_entry])}
                                src=${(0,g.MR)({domain:t[o.primary_config_entry],type:"icon",darkOptimized:this.hass.themes?.darkMode})}
                                crossorigin="anonymous"
                                referrerpolicy="no-referrer"
                              />`:n.s6}
                          <div class="device-info-details">
                            <span>${o.model||o.manufacturer}</span>
                            ${o.model?n.qy`<span class="secondary">
                                  ${o.manufacturer}
                                </span>`:n.s6}
                          </div>
                        </div>
                        <ha-textfield
                          .label=${e("ui.panel.config.integrations.config_flow.device_name")}
                          .placeholder=${(0,l.T)(o,this.hass)}
                          .value=${this._deviceUpdate[o.id]?.name??(0,l.xn)(o)}
                          @change=${this._deviceNameChanged}
                          .device=${o.id}
                        ></ha-textfield>
                        <ha-area-picker
                          .hass=${this.hass}
                          .device=${o.id}
                          .value=${this._deviceUpdate[o.id]?.area??o.area_id??void 0}
                          @value-changed=${this._areaPicked}
                        ></ha-area-picker>
                      </div>
                    `))}
                </div>
              `}
      </div>
      <div class="buttons">
        <ha-button @click=${this._flowDone}
          >${e("ui.panel.config.integrations.config_flow."+(!this.devices.length||Object.keys(this._deviceUpdate).length?"finish":"finish_skip"))}</ha-button
        >
      </div>
    `}async _loadDomains(){const e=await(0,v.VN)(this.hass);this._domains=Object.fromEntries(e.map((e=>[e.entry_id,e.domain])))}async _flowDone(){if(Object.keys(this._deviceUpdate).length){const e=[],t=Object.entries(this._deviceUpdate).map((([t,o])=>(o.name&&e.push(t),(0,_.FB)(this.hass,t,{name_by_user:o.name,area_id:o.area}).catch((e=>{(0,f.K$)(this,{text:this.hass.localize("ui.panel.config.integrations.config_flow.error_saving_device",{error:e.message})})})))));await Promise.allSettled(t);const o=[],i=[];e.forEach((e=>{const t=this._deviceEntities(e,Object.values(this.hass.entities));i.push(...t.map((e=>e.entity_id)))}));const n=await(0,m.BM)(this.hass,i);Object.entries(n).forEach((([e,t])=>{t&&o.push((0,m.G_)(this.hass,e,{new_entity_id:t}).catch((e=>(0,f.K$)(this,{text:this.hass.localize("ui.panel.config.integrations.config_flow.error_saving_entity",{error:e.message})}))))})),await Promise.allSettled(o)}(0,r.r)(this,"flow-update",{step:void 0}),this.step.result&&this.navigateToResult&&(1===this.devices.length?(0,c.o)(`/config/devices/device/${this.devices[0].id}`):(0,c.o)(`/config/integrations/integration/${this.step.result.domain}#config_entry=${this.step.result.entry_id}`))}async _areaPicked(e){const t=e.currentTarget.device,o=e.detail.value;t in this._deviceUpdate||(this._deviceUpdate[t]={}),this._deviceUpdate[t].area=o,this.requestUpdate("_deviceUpdate")}_deviceNameChanged(e){const t=e.currentTarget,o=t.device,i=t.value;o in this._deviceUpdate||(this._deviceUpdate[o]={}),this._deviceUpdate[o].name=i,this.requestUpdate("_deviceUpdate")}static get styles(){return[y.G,n.AH`
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
      `]}constructor(...e){super(...e),this._domains={},this.navigateToResult=!1,this._deviceUpdate={},this._deviceEntities=(0,s.A)(((e,t,o)=>t.filter((t=>t.device_id===e&&(!o||(0,d.m)(t.entity_id)===o)))))}}(0,i.__decorate)([(0,a.MZ)({attribute:!1})],$.prototype,"flowConfig",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],$.prototype,"step",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],$.prototype,"devices",void 0),(0,i.__decorate)([(0,a.wk)()],$.prototype,"_deviceUpdate",void 0),$=(0,i.__decorate)([(0,a.EM)("step-flow-create-entry")],$),t()}catch($){t($)}}))},58365:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),n=o(84922),a=o(11991),s=o(46472),r=o(76943),l=e([r]);r=(l.then?(await l)():l)[0];class d extends n.WF{render(){const e=this.hass.localize;return n.qy`
      <div class="content">
        ${this.flowConfig.renderExternalStepDescription(this.hass,this.step)}
        <div class="open-button">
          <ha-button href=${this.step.url} target="_blank" rel="noreferrer">
            ${e("ui.panel.config.integrations.config_flow.external_step.open_site")}
          </ha-button>
        </div>
      </div>
    `}firstUpdated(e){super.firstUpdated(e),window.open(this.step.url)}static get styles(){return[s.G,n.AH`
        .open-button {
          text-align: center;
          padding: 24px 0;
        }
        .open-button a {
          text-decoration: none;
        }
      `]}}(0,i.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"flowConfig",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"step",void 0),d=(0,i.__decorate)([(0,a.EM)("step-flow-external")],d),t()}catch(d){t(d)}}))},34436:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),n=o(84922),a=o(11991),s=o(65940),r=o(21431),l=o(73120),d=o(57183),c=o(76943),p=(o(23749),o(44840)),h=(o(75518),o(53199),o(71622)),_=o(4311),m=o(95237),u=o(83566),g=o(46472),f=e([c,h]);[c,h]=f.then?(await f)():f;class w extends n.WF{disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("keydown",this._handleKeyDown)}render(){const e=this.step,t=this._stepDataProcessed;return n.qy`
      <div class="content" @click=${this._clickHandler}>
        ${this.flowConfig.renderShowFormStepDescription(this.hass,this.step)}
        ${this._errorMsg?n.qy`<ha-alert alert-type="error">${this._errorMsg}</ha-alert>`:""}
        <ha-form
          .hass=${this.hass}
          .narrow=${this.narrow}
          .data=${t}
          .disabled=${this._loading}
          @value-changed=${this._stepDataChanged}
          .schema=${(0,_.Hg)(this.handleReadOnlyFields(e.data_schema))}
          .error=${this._errors}
          .computeLabel=${this._labelCallback}
          .computeHelper=${this._helperCallback}
          .computeError=${this._errorCallback}
          .localizeValue=${this._localizeValueCallback}
        ></ha-form>
      </div>
      ${e.preview?n.qy`<div class="preview" @set-flow-errors=${this._setError}>
            <h3>
              ${this.hass.localize("ui.panel.config.integrations.config_flow.preview")}:
            </h3>
            ${(0,r._)(`flow-preview-${(0,m.F)(e.preview)}`,{hass:this.hass,domain:e.preview,flowType:this.flowConfig.flowType,handler:e.handler,stepId:e.step_id,flowId:e.flow_id,stepData:t})}
          </div>`:n.s6}
      <div class="buttons">
        <ha-button @click=${this._submitStep} .loading=${this._loading}>
          ${this.flowConfig.renderShowFormStepSubmitButton(this.hass,this.step)}
        </ha-button>
      </div>
    `}_setError(e){this._previewErrors=e.detail}firstUpdated(e){super.firstUpdated(e),setTimeout((()=>this.shadowRoot.querySelector("ha-form").focus()),0),this.addEventListener("keydown",this._handleKeyDown)}willUpdate(e){super.willUpdate(e),e.has("step")&&this.step?.preview&&o(71289)(`./flow-preview-${(0,m.F)(this.step.preview)}`),(e.has("step")||e.has("_previewErrors")||e.has("_submitErrors"))&&(this._errors=this.step.errors||this._previewErrors||this._submitErrors?{...this.step.errors,...this._previewErrors,...this._submitErrors}:void 0)}_clickHandler(e){(0,d.d)(e,!1)&&(0,l.r)(this,"flow-update",{step:void 0})}get _stepDataProcessed(){return void 0!==this._stepData||(this._stepData=(0,p.$)(this.step.data_schema)),this._stepData}async _submitStep(){const e=this._stepData||{},t=(e,o)=>e.every((e=>(!e.required||!["",void 0].includes(o[e.name]))&&("expandable"!==e.type||!e.required&&void 0===o[e.name]||t(e.schema,o[e.name]))));if(!(void 0===e?void 0===this.step.data_schema.find((e=>e.required)):t(this.step.data_schema,e)))return void(this._errorMsg=this.hass.localize("ui.panel.config.integrations.config_flow.not_all_required_fields"));this._loading=!0,this._errorMsg=void 0,this._submitErrors=void 0;const o=this.step.flow_id,i={};Object.keys(e).forEach((t=>{const o=e[t],n=[void 0,""].includes(o),a=this.step.data_schema?.find((e=>e.name===t)),s=a?.selector??{},r=Object.values(s)[0]?.read_only;n||r||(i[t]=o)}));try{const e=await this.flowConfig.handleFlowStep(this.hass,this.step.flow_id,i);if(!this.step||o!==this.step.flow_id)return;this._previewErrors=void 0,(0,l.r)(this,"flow-update",{step:e})}catch(n){n&&n.body?(n.body.message&&(this._errorMsg=n.body.message),n.body.errors&&(this._submitErrors=n.body.errors),n.body.message||n.body.errors||(this._errorMsg="Unknown error occurred")):this._errorMsg="Unknown error occurred"}finally{this._loading=!1}}_stepDataChanged(e){this._stepData=e.detail.value}static get styles(){return[u.RF,g.G,n.AH`
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
      `]}constructor(...e){super(...e),this.narrow=!1,this._loading=!1,this.handleReadOnlyFields=(0,s.A)((e=>e?.map((e=>({...e,...Object.values(e?.selector??{})[0]?.read_only?{disabled:!0}:{}}))))),this._handleKeyDown=e=>{"Enter"===e.key&&this._submitStep()},this._labelCallback=(e,t,o)=>this.flowConfig.renderShowFormStepFieldLabel(this.hass,this.step,e,o),this._helperCallback=(e,t)=>this.flowConfig.renderShowFormStepFieldHelper(this.hass,this.step,e,t),this._errorCallback=e=>this.flowConfig.renderShowFormStepFieldError(this.hass,this.step,e),this._localizeValueCallback=e=>this.flowConfig.renderShowFormStepFieldLocalizeValue(this.hass,this.step,e)}}(0,i.__decorate)([(0,a.MZ)({attribute:!1})],w.prototype,"flowConfig",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean})],w.prototype,"narrow",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],w.prototype,"step",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],w.prototype,"hass",void 0),(0,i.__decorate)([(0,a.wk)()],w.prototype,"_loading",void 0),(0,i.__decorate)([(0,a.wk)()],w.prototype,"_stepData",void 0),(0,i.__decorate)([(0,a.wk)()],w.prototype,"_previewErrors",void 0),(0,i.__decorate)([(0,a.wk)()],w.prototype,"_submitErrors",void 0),(0,i.__decorate)([(0,a.wk)()],w.prototype,"_errorMsg",void 0),w=(0,i.__decorate)([(0,a.EM)("step-flow-form")],w),t()}catch(w){t(w)}}))},58784:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),n=o(84922),a=o(11991),s=o(71622),r=e([s]);s=(r.then?(await r)():r)[0];class l extends n.WF{render(){const e=this.flowConfig.renderLoadingDescription(this.hass,this.loadingReason,this.handler,this.step);return n.qy`
      <div class="content">
        <ha-spinner size="large"></ha-spinner>
        ${e?n.qy`<div>${e}</div>`:""}
      </div>
    `}}l.styles=n.AH`
    .content {
      margin-top: 0;
      padding: 50px 100px;
      text-align: center;
    }
    ha-spinner {
      margin-bottom: 16px;
    }
  `,(0,i.__decorate)([(0,a.MZ)({attribute:!1})],l.prototype,"flowConfig",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],l.prototype,"hass",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],l.prototype,"loadingReason",void 0),(0,i.__decorate)([(0,a.MZ)()],l.prototype,"handler",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],l.prototype,"step",void 0),l=(0,i.__decorate)([(0,a.EM)("step-flow-loading")],l),t()}catch(l){t(l)}}))},15654:function(e,t,o){var i=o(69868),n=o(84922),a=o(11991),s=o(73120),r=(o(72062),o(25223),o(46472)),l=o(90963);class d extends n.WF{shouldUpdate(e){return e.size>1||!e.has("hass")||this.hass.localize!==e.get("hass")?.localize}render(){let e,t,o={};if(Array.isArray(this.step.menu_options)){e=this.step.menu_options,t={};for(const i of e)t[i]=this.flowConfig.renderMenuOption(this.hass,this.step,i),o[i]=this.flowConfig.renderMenuOptionDescription(this.hass,this.step,i)}else e=Object.keys(this.step.menu_options),t=this.step.menu_options,o=Object.fromEntries(e.map((e=>[e,this.flowConfig.renderMenuOptionDescription(this.hass,this.step,e)])));this.step.sort&&(e=e.sort(((e,o)=>(0,l.xL)(t[e],t[o],this.hass.locale.language))));const i=this.flowConfig.renderMenuDescription(this.hass,this.step);return n.qy`
      ${i?n.qy`<div class="content">${i}</div>`:""}
      <div class="options">
        ${e.map((e=>n.qy`
            <ha-list-item
              hasMeta
              .step=${e}
              @click=${this._handleStep}
              ?twoline=${o[e]}
              ?multiline-secondary=${o[e]}
            >
              <span>${t[e]}</span>
              ${o[e]?n.qy`<span slot="secondary">
                    ${o[e]}
                  </span>`:n.s6}
              <ha-icon-next slot="meta"></ha-icon-next>
            </ha-list-item>
          `))}
      </div>
    `}_handleStep(e){(0,s.r)(this,"flow-update",{stepPromise:this.flowConfig.handleFlowStep(this.hass,this.step.flow_id,{next_step_id:e.currentTarget.step})})}}d.styles=[r.G,n.AH`
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
    `],(0,i.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"flowConfig",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"step",void 0),d=(0,i.__decorate)([(0,a.EM)("step-flow-menu")],d)},23225:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(69868),n=o(84922),a=o(11991),s=o(3371),r=o(80527),l=o(71622),d=o(46472),c=e([r,l]);[r,l]=c.then?(await c)():c;class p extends n.WF{render(){return n.qy`
      <div class="content">
        ${this.progress?n.qy`
              <ha-progress-ring .value=${this.progress} size="large"
                >${this.progress}${(0,s.d)(this.hass.locale)}%</ha-progress-ring
              >
            `:n.qy`<ha-spinner size="large"></ha-spinner>`}
        ${this.flowConfig.renderShowFormProgressDescription(this.hass,this.step)}
      </div>
    `}static get styles(){return[d.G,n.AH`
        .content {
          margin-top: 0;
          padding: 50px 100px;
          text-align: center;
        }
        ha-spinner {
          margin-bottom: 16px;
        }
      `]}}(0,i.__decorate)([(0,a.MZ)({attribute:!1})],p.prototype,"flowConfig",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],p.prototype,"step",void 0),(0,i.__decorate)([(0,a.MZ)({type:Number})],p.prototype,"progress",void 0),p=(0,i.__decorate)([(0,a.EM)("step-flow-progress")],p),t()}catch(p){t(p)}}))},46472:function(e,t,o){o.d(t,{G:()=>i});const i=o(84922).AH`
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
`},59168:function(e,t,o){o.d(t,{L:()=>a});var i=o(73120);const n=()=>Promise.all([o.e("6216"),o.e("9358"),o.e("615"),o.e("9696")]).then(o.bind(o,97938)),a=(e,t)=>{(0,i.r)(e,"show-dialog",{dialogTag:"ha-voice-assistant-setup-dialog",dialogImport:n,dialogParams:t})}},94100:function(e,t,o){o.d(t,{a:()=>a});var i=o(73120);const n=()=>Promise.all([o.e("4321"),o.e("3089")]).then(o.bind(o,50184)),a=(e,t)=>{(0,i.r)(e,"show-dialog",{dialogTag:"dialog-add-application-credential",dialogImport:n,dialogParams:t})}},45363:function(e,t,o){o.d(t,{MR:()=>i,a_:()=>n,bg:()=>a});const i=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,n=e=>e.split("/")[4],a=e=>e.startsWith("https://brands.home-assistant.io/")},86435:function(e,t,o){o.d(t,{o:()=>i});const i=(e,t)=>`https://${e.config.version.includes("b")?"rc":e.config.version.includes("dev")?"next":"www"}.home-assistant.io${t}`}};
//# sourceMappingURL=9316.ad08320712a5711c.js.map