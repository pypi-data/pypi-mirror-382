export const __webpack_id__="5393";export const __webpack_ids__=["5393"];export const __webpack_modules__={83490:function(e,t,i){i.d(t,{I:()=>o});class a{addFromStorage(e){if(!this._storage[e]){const t=this.storage.getItem(e);t&&(this._storage[e]=JSON.parse(t))}}subscribeChanges(e,t){return this._listeners[e]?this._listeners[e].push(t):this._listeners[e]=[t],()=>{this.unsubscribeChanges(e,t)}}unsubscribeChanges(e,t){if(!(e in this._listeners))return;const i=this._listeners[e].indexOf(t);-1!==i&&this._listeners[e].splice(i,1)}hasKey(e){return e in this._storage}getValue(e){return this._storage[e]}setValue(e,t){const i=this._storage[e];this._storage[e]=t;try{void 0===t?this.storage.removeItem(e):this.storage.setItem(e,JSON.stringify(t))}catch(a){}finally{this._listeners[e]&&this._listeners[e].forEach((e=>e(i,t)))}}constructor(e=window.localStorage){this._storage={},this._listeners={},this.storage=e,this.storage===window.localStorage&&window.addEventListener("storage",(e=>{e.key&&this.hasKey(e.key)&&(this._storage[e.key]=e.newValue?JSON.parse(e.newValue):e.newValue,this._listeners[e.key]&&this._listeners[e.key].forEach((t=>t(e.oldValue?JSON.parse(e.oldValue):e.oldValue,this._storage[e.key]))))}))}}const s={};function o(e){return(t,i)=>{if("object"==typeof i)throw new Error("This decorator does not support this compilation type.");const o=e.storage||"localStorage";let r;o&&o in s?r=s[o]:(r=new a(window[o]),s[o]=r);const n=e.key||String(i);r.addFromStorage(n);const d=!1!==e.subscribe?e=>r.subscribeChanges(n,((t,a)=>{e.requestUpdate(i,t)})):void 0,l=()=>r.hasKey(n)?e.deserializer?e.deserializer(r.getValue(n)):r.getValue(n):void 0,c=(t,a)=>{let s;e.state&&(s=l()),r.setValue(n,e.serializer?e.serializer(a):a),e.state&&t.requestUpdate(i,s)},h=t.performUpdate;if(t.performUpdate=function(){this.__initialized=!0,h.call(this)},e.subscribe){const e=t.connectedCallback,i=t.disconnectedCallback;t.connectedCallback=function(){e.call(this);const t=this;t.__unbsubLocalStorage||(t.__unbsubLocalStorage=d?.(this))},t.disconnectedCallback=function(){i.call(this);this.__unbsubLocalStorage?.(),this.__unbsubLocalStorage=void 0}}const p=Object.getOwnPropertyDescriptor(t,i);let u;if(void 0===p)u={get(){return l()},set(e){(this.__initialized||void 0===l())&&c(this,e)},configurable:!0,enumerable:!0};else{const e=p.set;u={...p,get(){return l()},set(t){(this.__initialized||void 0===l())&&c(this,t),e?.call(this,t)}}}Object.defineProperty(t,i,u)}}},47379:function(e,t,i){i.d(t,{u:()=>s});var a=i(90321);const s=e=>{return t=e.entity_id,void 0===(i=e.attributes).friendly_name?(0,a.Y)(t).replace(/_/g," "):(i.friendly_name??"").toString();var t,i}},41602:function(e,t,i){i.d(t,{n:()=>s});const a=/^(\w+)\.(\w+)$/,s=e=>a.test(e)},13125:function(e,t,i){i.a(e,(async function(e,a){try{i.d(t,{T:()=>n});var s=i(96904),o=i(65940),r=e([s]);s=(r.then?(await r)():r)[0];const n=(e,t)=>{try{return d(t)?.of(e)??e}catch{return e}},d=(0,o.A)((e=>new Intl.DisplayNames(e.language,{type:"language",fallback:"code"})));a()}catch(n){a(n)}}))},5503:function(e,t,i){i.d(t,{l:()=>a});const a=async(e,t)=>{if(navigator.clipboard)try{return void(await navigator.clipboard.writeText(e))}catch{}const i=t??document.body,a=document.createElement("textarea");a.value=e,i.appendChild(a),a.select(),document.execCommand("copy"),i.removeChild(a)}},57447:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(69868),s=i(84922),o=i(11991),r=i(65940),n=i(73120),d=i(92830),l=i(47379),c=i(41602),h=i(98137),p=i(28027),u=i(5940),_=i(80608),m=(i(36137),i(94966),i(95635),i(23114)),g=e([m]);m=(g.then?(await g)():g)[0];const v="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",y="M11,13.5V21.5H3V13.5H11M12,2L17.5,11H6.5L12,2M17.5,13C20,13 22,15 22,17.5C22,20 20,22 17.5,22C15,22 13,20 13,17.5C13,15 15,13 17.5,13Z",b="___create-new-entity___";class f extends s.WF{firstUpdated(e){super.firstUpdated(e),this.hass.loadBackendTranslation("title")}get _showEntityId(){return this.showEntityId||this.hass.userData?.showEntityIdPicker}render(){const e=this.placeholder??this.hass.localize("ui.components.entity.entity-picker.placeholder"),t=this.hass.localize("ui.components.entity.entity-picker.no_match");return s.qy`
      <ha-generic-picker
        .hass=${this.hass}
        .disabled=${this.disabled}
        .autofocus=${this.autofocus}
        .allowCustomValue=${this.allowCustomEntity}
        .label=${this.label}
        .helper=${this.helper}
        .searchLabel=${this.searchLabel}
        .notFoundLabel=${t}
        .placeholder=${e}
        .value=${this.value}
        .rowRenderer=${this._rowRenderer}
        .getItems=${this._getItems}
        .getAdditionalItems=${this._getAdditionalItems}
        .hideClearIcon=${this.hideClearIcon}
        .searchFn=${this._searchFn}
        .valueRenderer=${this._valueRenderer}
        @value-changed=${this._valueChanged}
      >
      </ha-generic-picker>
    `}async open(){await this.updateComplete,await(this._picker?.open())}_valueChanged(e){e.stopPropagation();const t=e.detail.value;if(t)if(t.startsWith(b)){const e=t.substring(b.length);(0,_.$)(this,{domain:e,dialogClosedCallback:e=>{e.entityId&&this._setValue(e.entityId)}})}else(0,c.n)(t)&&this._setValue(t);else this._setValue(void 0)}_setValue(e){this.value=e,(0,n.r)(this,"value-changed",{value:e}),(0,n.r)(this,"change")}constructor(...e){super(...e),this.autofocus=!1,this.disabled=!1,this.required=!1,this.showEntityId=!1,this.hideClearIcon=!1,this._valueRenderer=e=>{const t=e||"",i=this.hass.states[t];if(!i)return s.qy`
        <ha-svg-icon
          slot="start"
          .path=${y}
          style="margin: 0 4px"
        ></ha-svg-icon>
        <span slot="headline">${t}</span>
      `;const a=this.hass.formatEntityName(i,"entity"),o=this.hass.formatEntityName(i,"device"),r=this.hass.formatEntityName(i,"area"),n=(0,h.qC)(this.hass),d=a||o||t,l=[r,a?o:void 0].filter(Boolean).join(n?" ◂ ":" ▸ ");return s.qy`
      <state-badge
        .hass=${this.hass}
        .stateObj=${i}
        slot="start"
      ></state-badge>
      <span slot="headline">${d}</span>
      <span slot="supporting-text">${l}</span>
    `},this._rowRenderer=(e,{index:t})=>{const i=this._showEntityId;return s.qy`
      <ha-combo-box-item type="button" compact .borderTop=${0!==t}>
        ${e.icon_path?s.qy`
              <ha-svg-icon
                slot="start"
                style="margin: 0 4px"
                .path=${e.icon_path}
              ></ha-svg-icon>
            `:s.qy`
              <state-badge
                slot="start"
                .stateObj=${e.stateObj}
                .hass=${this.hass}
              ></state-badge>
            `}
        <span slot="headline">${e.primary}</span>
        ${e.secondary?s.qy`<span slot="supporting-text">${e.secondary}</span>`:s.s6}
        ${e.stateObj&&i?s.qy`
              <span slot="supporting-text" class="code">
                ${e.stateObj.entity_id}
              </span>
            `:s.s6}
        ${e.domain_name&&!i?s.qy`
              <div slot="trailing-supporting-text" class="domain">
                ${e.domain_name}
              </div>
            `:s.s6}
      </ha-combo-box-item>
    `},this._getAdditionalItems=()=>this._getCreateItems(this.hass.localize,this.createDomains),this._getCreateItems=(0,r.A)(((e,t)=>t?.length?t.map((t=>{const i=e("ui.components.entity.entity-picker.create_helper",{domain:(0,u.z)(t)?e(`ui.panel.config.helpers.types.${t}`):(0,p.p$)(e,t)});return{id:b+t,primary:i,secondary:e("ui.components.entity.entity-picker.new_entity"),icon_path:v}})):[])),this._getItems=()=>this._getEntities(this.hass,this.includeDomains,this.excludeDomains,this.entityFilter,this.includeDeviceClasses,this.includeUnitOfMeasurement,this.includeEntities,this.excludeEntities),this._getEntities=(0,r.A)(((e,t,i,a,s,o,r,n)=>{let c=[],u=Object.keys(e.states);r&&(u=u.filter((e=>r.includes(e)))),n&&(u=u.filter((e=>!n.includes(e)))),t&&(u=u.filter((e=>t.includes((0,d.m)(e))))),i&&(u=u.filter((e=>!i.includes((0,d.m)(e)))));const _=(0,h.qC)(this.hass);return c=u.map((t=>{const i=e.states[t],a=(0,l.u)(i),s=this.hass.formatEntityName(i,"entity"),o=this.hass.formatEntityName(i,"device"),r=this.hass.formatEntityName(i,"area"),n=(0,p.p$)(this.hass.localize,(0,d.m)(t)),c=s||o||t,h=[r,s?o:void 0].filter(Boolean).join(_?" ◂ ":" ▸ "),u=[o,s].filter(Boolean).join(" - ");return{id:t,primary:c,secondary:h,domain_name:n,sorting_label:[o,s].filter(Boolean).join("_"),search_labels:[s,o,r,n,a,t].filter(Boolean),a11y_label:u,stateObj:i}})),s&&(c=c.filter((e=>e.id===this.value||e.stateObj?.attributes.device_class&&s.includes(e.stateObj.attributes.device_class)))),o&&(c=c.filter((e=>e.id===this.value||e.stateObj?.attributes.unit_of_measurement&&o.includes(e.stateObj.attributes.unit_of_measurement)))),a&&(c=c.filter((e=>e.id===this.value||e.stateObj&&a(e.stateObj)))),c})),this._searchFn=(e,t)=>{const i=t.findIndex((t=>t.stateObj?.entity_id===e));if(-1===i)return t;const[a]=t.splice(i,1);return t.unshift(a),t}}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],f.prototype,"autofocus",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],f.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],f.prototype,"required",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean,attribute:"allow-custom-entity"})],f.prototype,"allowCustomEntity",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean,attribute:"show-entity-id"})],f.prototype,"showEntityId",void 0),(0,a.__decorate)([(0,o.MZ)()],f.prototype,"label",void 0),(0,a.__decorate)([(0,o.MZ)()],f.prototype,"value",void 0),(0,a.__decorate)([(0,o.MZ)()],f.prototype,"helper",void 0),(0,a.__decorate)([(0,o.MZ)()],f.prototype,"placeholder",void 0),(0,a.__decorate)([(0,o.MZ)({type:String,attribute:"search-label"})],f.prototype,"searchLabel",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1,type:Array})],f.prototype,"createDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-domains"})],f.prototype,"includeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-domains"})],f.prototype,"excludeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-device-classes"})],f.prototype,"includeDeviceClasses",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-unit-of-measurement"})],f.prototype,"includeUnitOfMeasurement",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-entities"})],f.prototype,"includeEntities",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-entities"})],f.prototype,"excludeEntities",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],f.prototype,"entityFilter",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"hide-clear-icon",type:Boolean})],f.prototype,"hideClearIcon",void 0),(0,a.__decorate)([(0,o.P)("ha-generic-picker")],f.prototype,"_picker",void 0),f=(0,a.__decorate)([(0,o.EM)("ha-entity-picker")],f),t()}catch(v){t(v)}}))},17711:function(e,t,i){var a=i(69868),s=i(84922),o=i(11991),r=i(90933);i(9974),i(95968);class n extends s.WF{get items(){return this._menu?.items}get selected(){return this._menu?.selected}focus(){this._menu?.open?this._menu.focusItemAtIndex(0):this._triggerButton?.focus()}render(){return s.qy`
      <div @click=${this._handleClick}>
        <slot name="trigger" @slotchange=${this._setTriggerAria}></slot>
      </div>
      <ha-menu
        .corner=${this.corner}
        .menuCorner=${this.menuCorner}
        .fixed=${this.fixed}
        .multi=${this.multi}
        .activatable=${this.activatable}
        .y=${this.y}
        .x=${this.x}
      >
        <slot></slot>
      </ha-menu>
    `}firstUpdated(e){super.firstUpdated(e),"rtl"===r.G.document.dir&&this.updateComplete.then((()=>{this.querySelectorAll("ha-list-item").forEach((e=>{const t=document.createElement("style");t.innerHTML="span.material-icons:first-of-type { margin-left: var(--mdc-list-item-graphic-margin, 32px) !important; margin-right: 0px !important;}",e.shadowRoot.appendChild(t)}))}))}_handleClick(){this.disabled||(this._menu.anchor=this.noAnchor?null:this,this._menu.show())}get _triggerButton(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"]')}_setTriggerAria(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}constructor(...e){super(...e),this.corner="BOTTOM_START",this.menuCorner="START",this.x=null,this.y=null,this.multi=!1,this.activatable=!1,this.disabled=!1,this.fixed=!1,this.noAnchor=!1}}n.styles=s.AH`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `,(0,a.__decorate)([(0,o.MZ)()],n.prototype,"corner",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"menu-corner"})],n.prototype,"menuCorner",void 0),(0,a.__decorate)([(0,o.MZ)({type:Number})],n.prototype,"x",void 0),(0,a.__decorate)([(0,o.MZ)({type:Number})],n.prototype,"y",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],n.prototype,"multi",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],n.prototype,"activatable",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],n.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],n.prototype,"fixed",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean,attribute:"no-anchor"})],n.prototype,"noAnchor",void 0),(0,a.__decorate)([(0,o.P)("ha-menu",!0)],n.prototype,"_menu",void 0),n=(0,a.__decorate)([(0,o.EM)("ha-button-menu")],n)},96997:function(e,t,i){var a=i(69868),s=i(84922),o=i(11991);class r extends s.WF{render(){return s.qy`
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
    `}static get styles(){return[s.AH`
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
      `]}}r=(0,a.__decorate)([(0,o.EM)("ha-dialog-header")],r)},86480:function(e,t,i){i.a(e,(async function(e,a){try{i.d(t,{t:()=>m});var s=i(96904),o=i(69868),r=i(84922),n=i(11991),d=i(65940),l=i(73120),c=i(20674),h=i(13125),p=i(90963),u=i(42983),_=(i(25223),i(37207),e([s,h]));[s,h]=_.then?(await _)():_;const m=(e,t,i,a)=>{let s=[];if(t){const t=u.P.translations;s=e.map((e=>{let i=t[e]?.nativeName;if(!i)try{i=new Intl.DisplayNames(e,{type:"language",fallback:"code"}).of(e)}catch(a){i=e}return{value:e,label:i}}))}else a&&(s=e.map((e=>({value:e,label:(0,h.T)(e,a)}))));return!i&&a&&s.sort(((e,t)=>(0,p.SH)(e.label,t.label,a.language))),s};class g extends r.WF{firstUpdated(e){super.firstUpdated(e),this._computeDefaultLanguageOptions()}updated(e){super.updated(e);const t=e.has("hass")&&this.hass&&e.get("hass")&&e.get("hass").locale.language!==this.hass.locale.language;if(e.has("languages")||e.has("value")||t){if(this._select.layoutOptions(),this.disabled||this._select.value===this.value||(0,l.r)(this,"value-changed",{value:this._select.value}),!this.value)return;const e=this._getLanguagesOptions(this.languages??this._defaultLanguages,this.nativeName,this.noSort,this.hass?.locale).findIndex((e=>e.value===this.value));-1===e&&(this.value=void 0),t&&this._select.select(e)}}_computeDefaultLanguageOptions(){this._defaultLanguages=Object.keys(u.P.translations)}render(){const e=this._getLanguagesOptions(this.languages??this._defaultLanguages,this.nativeName,this.noSort,this.hass?.locale),t=this.value??(this.required&&!this.disabled?e[0]?.value:this.value);return r.qy`
      <ha-select
        .label=${this.label??(this.hass?.localize("ui.components.language-picker.language")||"Language")}
        .value=${t||""}
        .required=${this.required}
        .disabled=${this.disabled}
        @selected=${this._changed}
        @closed=${c.d}
        fixedMenuPosition
        naturalMenuWidth
        .inlineArrow=${this.inlineArrow}
      >
        ${0===e.length?r.qy`<ha-list-item value=""
              >${this.hass?.localize("ui.components.language-picker.no_languages")||"No languages"}</ha-list-item
            >`:e.map((e=>r.qy`
                <ha-list-item .value=${e.value}
                  >${e.label}</ha-list-item
                >
              `))}
      </ha-select>
    `}_changed(e){const t=e.target;this.disabled||""===t.value||t.value===this.value||(this.value=t.value,(0,l.r)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.nativeName=!1,this.noSort=!1,this.inlineArrow=!1,this._defaultLanguages=[],this._getLanguagesOptions=(0,d.A)(m)}}g.styles=r.AH`
    ha-select {
      width: 100%;
    }
  `,(0,o.__decorate)([(0,n.MZ)()],g.prototype,"value",void 0),(0,o.__decorate)([(0,n.MZ)()],g.prototype,"label",void 0),(0,o.__decorate)([(0,n.MZ)({type:Array})],g.prototype,"languages",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],g.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],g.prototype,"required",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"native-name",type:Boolean})],g.prototype,"nativeName",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"no-sort",type:Boolean})],g.prototype,"noSort",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"inline-arrow",type:Boolean})],g.prototype,"inlineArrow",void 0),(0,o.__decorate)([(0,n.wk)()],g.prototype,"_defaultLanguages",void 0),(0,o.__decorate)([(0,n.P)("ha-select")],g.prototype,"_select",void 0),g=(0,o.__decorate)([(0,n.EM)("ha-language-picker")],g),a()}catch(m){a(m)}}))},89652:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(69868),s=i(28784),o=i(84922),r=i(11991),n=e([s]);s=(n.then?(await n)():n)[0];class d extends s.A{static get styles(){return[s.A.styles,o.AH`
        :host {
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
        }
      `]}constructor(...e){super(...e),this.showDelay=150,this.hideDelay=400}}(0,a.__decorate)([(0,r.MZ)({attribute:"show-delay",type:Number})],d.prototype,"showDelay",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:"hide-delay",type:Number})],d.prototype,"hideDelay",void 0),d=(0,a.__decorate)([(0,r.EM)("ha-tooltip")],d),t()}catch(d){t(d)}}))},52428:function(e,t,i){var a=i(69868),s=i(84922),o=i(11991),r=i(73120),n=i(20674),d=i(24802),l=i(87608);i(25223),i(37207);const c="__NONE_OPTION__";class h extends s.WF{render(){if(!this._voices)return s.s6;const e=this.value??(this.required?this._voices[0]?.voice_id:c);return s.qy`
      <ha-select
        .label=${this.label||this.hass.localize("ui.components.tts-voice-picker.voice")}
        .value=${e}
        .required=${this.required}
        .disabled=${this.disabled}
        @selected=${this._changed}
        @closed=${n.d}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${this.required?s.s6:s.qy`<ha-list-item .value=${c}>
              ${this.hass.localize("ui.components.tts-voice-picker.none")}
            </ha-list-item>`}
        ${this._voices.map((e=>s.qy`<ha-list-item .value=${e.voice_id}>
              ${e.name}
            </ha-list-item>`))}
      </ha-select>
    `}willUpdate(e){super.willUpdate(e),this.hasUpdated?(e.has("language")||e.has("engineId"))&&this._debouncedUpdateVoices():this._updateVoices()}async _updateVoices(){this.engineId&&this.language?(this._voices=(await(0,l.z3)(this.hass,this.engineId,this.language)).voices,this.value&&(this._voices&&this._voices.find((e=>e.voice_id===this.value))||(this.value=void 0,(0,r.r)(this,"value-changed",{value:this.value})))):this._voices=void 0}updated(e){super.updated(e),e.has("_voices")&&this._select?.value!==this.value&&(this._select?.layoutOptions(),(0,r.r)(this,"value-changed",{value:this._select?.value}))}_changed(e){const t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===c||(this.value=t.value===c?void 0:t.value,(0,r.r)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._debouncedUpdateVoices=(0,d.s)((()=>this._updateVoices()),500)}}h.styles=s.AH`
    ha-select {
      width: 100%;
    }
  `,(0,a.__decorate)([(0,o.MZ)()],h.prototype,"value",void 0),(0,a.__decorate)([(0,o.MZ)()],h.prototype,"label",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],h.prototype,"engineId",void 0),(0,a.__decorate)([(0,o.MZ)()],h.prototype,"language",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean,reflect:!0})],h.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],h.prototype,"required",void 0),(0,a.__decorate)([(0,o.wk)()],h.prototype,"_voices",void 0),(0,a.__decorate)([(0,o.P)("ha-select")],h.prototype,"_select",void 0),h=(0,a.__decorate)([(0,o.EM)("ha-tts-voice-picker")],h)},83e3:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t);var s=i(69868),o=i(84922),r=i(11991),n=i(73120),d=i(20674),l=i(83566),c=(i(72847),i(96997),i(25223),i(79739)),h=i(93215),p=e([c,h]);[c,h]=p.then?(await p)():p;const u="M3,5A2,2 0 0,1 5,3H19A2,2 0 0,1 21,5V19A2,2 0 0,1 19,21H5C3.89,21 3,20.1 3,19V5M5,5V19H19V5H5M11,7H13A2,2 0 0,1 15,9V17H13V13H11V17H9V9A2,2 0 0,1 11,7M11,9V11H13V9H11Z",_="M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z",m="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",g="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z",v="M10,4V8H14V4H10M16,4V8H20V4H16M16,10V14H20V10H16M16,16V20H20V16H16M14,20V16H10V20H14M8,20V16H4V20H8M8,14V10H4V14H8M8,8V4H4V8H8M10,14H14V10H10V14M4,2H20A2,2 0 0,1 22,4V20A2,2 0 0,1 20,22H4C2.92,22 2,21.1 2,20V4A2,2 0 0,1 4,2Z",y="M11 15H17V17H11V15M9 7H7V9H9V7M11 13H17V11H11V13M11 9H17V7H11V9M9 11H7V13H9V11M21 5V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V5C3 3.9 3.9 3 5 3H19C20.1 3 21 3.9 21 5M19 5H5V19H19V5M9 15H7V17H9V15Z";class b extends o.WF{showDialog(e){this._params=e,this._navigateIds=e.navigateIds||[{media_content_id:void 0,media_content_type:void 0}]}closeDialog(){this._params=void 0,this._navigateIds=void 0,this._currentItem=void 0,this._preferredLayout="auto",this.classList.remove("opened"),(0,n.r)(this,"dialog-closed",{dialog:this.localName})}render(){return this._params&&this._navigateIds?o.qy`
      <ha-dialog
        open
        scrimClickAction
        escapeKeyAction
        hideActions
        flexContent
        .heading=${this._currentItem?this._currentItem.title:this.hass.localize("ui.components.media-browser.media-player-browser")}
        @closed=${this.closeDialog}
        @opened=${this._dialogOpened}
      >
        <ha-dialog-header show-border slot="heading">
          ${this._navigateIds.length>(this._params.minimumNavigateLevel??1)?o.qy`
                <ha-icon-button
                  slot="navigationIcon"
                  .path=${_}
                  @click=${this._goBack}
                ></ha-icon-button>
              `:o.s6}
          <span slot="title">
            ${this._currentItem?this._currentItem.title:this.hass.localize("ui.components.media-browser.media-player-browser")}
          </span>
          <ha-media-manage-button
            slot="actionItems"
            .hass=${this.hass}
            .currentItem=${this._currentItem}
            @media-refresh=${this._refreshMedia}
          ></ha-media-manage-button>
          <ha-button-menu
            slot="actionItems"
            @action=${this._handleMenuAction}
            @closed=${d.d}
            fixed
          >
            <ha-icon-button
              slot="trigger"
              .label=${this.hass.localize("ui.common.menu")}
              .path=${g}
            ></ha-icon-button>
            <ha-list-item graphic="icon">
              ${this.hass.localize("ui.components.media-browser.auto")}
              <ha-svg-icon
                class=${"auto"===this._preferredLayout?"selected_menu_item":""}
                slot="graphic"
                .path=${u}
              ></ha-svg-icon>
            </ha-list-item>
            <ha-list-item graphic="icon">
              ${this.hass.localize("ui.components.media-browser.grid")}
              <ha-svg-icon
                class=${"grid"===this._preferredLayout?"selected_menu_item":""}
                slot="graphic"
                .path=${v}
              ></ha-svg-icon>
            </ha-list-item>
            <ha-list-item graphic="icon">
              ${this.hass.localize("ui.components.media-browser.list")}
              <ha-svg-icon
                slot="graphic"
                class=${"list"===this._preferredLayout?"selected_menu_item":""}
                .path=${y}
              ></ha-svg-icon>
            </ha-list-item>
          </ha-button-menu>
          <ha-icon-button
            .label=${this.hass.localize("ui.common.close")}
            .path=${m}
            dialogAction="close"
            slot="actionItems"
          ></ha-icon-button>
        </ha-dialog-header>
        <ha-media-player-browse
          dialog
          .hass=${this.hass}
          .entityId=${this._params.entityId}
          .navigateIds=${this._navigateIds}
          .action=${this._action}
          .preferredLayout=${this._preferredLayout}
          .accept=${this._params.accept}
          .defaultId=${this._params.defaultId}
          .defaultType=${this._params.defaultType}
          @close-dialog=${this.closeDialog}
          @media-picked=${this._mediaPicked}
          @media-browsed=${this._mediaBrowsed}
        ></ha-media-player-browse>
      </ha-dialog>
    `:o.s6}_dialogOpened(){this.classList.add("opened")}async _handleMenuAction(e){switch(e.detail.index){case 0:this._preferredLayout="auto";break;case 1:this._preferredLayout="grid";break;case 2:this._preferredLayout="list"}}_goBack(){this._navigateIds=this._navigateIds?.slice(0,-1),this._currentItem=void 0}_mediaBrowsed(e){this._navigateIds=e.detail.ids,this._currentItem=e.detail.current}_mediaPicked(e){this._params.mediaPickedCallback(e.detail),"play"!==this._action&&this.closeDialog()}get _action(){return this._params.action||"play"}_refreshMedia(){this._browser.refresh()}static get styles(){return[l.nA,o.AH`
        ha-dialog {
          --dialog-z-index: 9;
          --dialog-content-padding: 0;
        }

        ha-media-player-browse {
          --media-browser-max-height: calc(100vh - 65px);
        }

        :host(.opened) ha-media-player-browse {
          height: calc(100vh - 65px);
        }

        @media (min-width: 800px) {
          ha-dialog {
            --mdc-dialog-max-width: 800px;
            --dialog-surface-position: fixed;
            --dialog-surface-top: 40px;
            --mdc-dialog-max-height: calc(100vh - 72px);
          }
          ha-media-player-browse {
            position: initial;
            --media-browser-max-height: calc(100vh - 145px);
            width: 700px;
          }
        }

        ha-dialog-header ha-media-manage-button {
          --mdc-theme-primary: var(--primary-text-color);
          margin: 6px;
          display: block;
        }
      `]}constructor(...e){super(...e),this._preferredLayout="auto"}}(0,s.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,s.__decorate)([(0,r.wk)()],b.prototype,"_currentItem",void 0),(0,s.__decorate)([(0,r.wk)()],b.prototype,"_navigateIds",void 0),(0,s.__decorate)([(0,r.wk)()],b.prototype,"_params",void 0),(0,s.__decorate)([(0,r.wk)()],b.prototype,"_preferredLayout",void 0),(0,s.__decorate)([(0,r.P)("ha-media-player-browse")],b.prototype,"_browser",void 0),b=(0,s.__decorate)([(0,r.EM)("dialog-media-player-browse")],b),a()}catch(u){a(u)}}))},26596:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(69868),s=i(84922),o=i(11991),r=i(65940),n=i(73120),d=i(76943),l=(i(86853),i(75518),e([d]));d=(l.then?(await l)():l)[0];class c extends s.WF{render(){return s.qy`
      <ha-card>
        <div class="card-content">
          <ha-form
            .hass=${this.hass}
            .schema=${this._schema()}
            .data=${this.item}
            .computeLabel=${this._computeLabel}
            .computeHelper=${this._computeHelper}
            @value-changed=${this._valueChanged}
          ></ha-form>
        </div>
        <div class="card-actions">
          <ha-button @click=${this._mediaPicked}>
            ${this.hass.localize("ui.common.submit")}
          </ha-button>
        </div>
      </ha-card>
    `}_valueChanged(e){const t={...e.detail.value};this.item=t}_mediaPicked(){(0,n.r)(this,"manual-media-picked",{item:{media_content_id:this.item.media_content_id||"",media_content_type:this.item.media_content_type||""}})}constructor(...e){super(...e),this._schema=(0,r.A)((()=>[{name:"media_content_id",required:!0,selector:{text:{}}},{name:"media_content_type",required:!1,selector:{text:{}}}])),this._computeLabel=e=>this.hass.localize(`ui.components.selectors.media.${e.name}`),this._computeHelper=e=>this.hass.localize(`ui.components.selectors.media.${e.name}_detail`)}}c.styles=s.AH`
    :host {
      margin: 16px auto;
      padding: 0 8px;
      display: flex;
      flex-direction: column;
      max-width: 448px;
    }
    .card-actions {
      display: flex;
      justify-content: flex-end;
    }
  `,(0,a.__decorate)([(0,o.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],c.prototype,"item",void 0),c=(0,a.__decorate)([(0,o.EM)("ha-browse-media-manual")],c),t()}catch(c){t(c)}}))},10825:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(69868),s=i(84922),o=i(11991),r=i(83490),n=i(73120),d=i(5503),l=i(70040),c=i(87608),h=i(83566),p=i(72698),u=i(76943),_=(i(86853),i(86480)),m=(i(79973),i(52428),e([u,_]));[u,_]=m.then?(await m)():m;const g="M19,21H8V7H19M19,5H8A2,2 0 0,0 6,7V21A2,2 0 0,0 8,23H19A2,2 0 0,0 21,21V7A2,2 0 0,0 19,5M16,1H4A2,2 0 0,0 2,3V17H4V3H16V1Z";class v extends s.WF{render(){return s.qy`
      <ha-card>
        <div class="card-content">
          <ha-textarea
            autogrow
            .label=${this.hass.localize("ui.components.media-browser.tts.message")}
            .value=${this._message||this.hass.localize("ui.components.media-browser.tts.example_message",{name:this.hass.user?.name||"Alice"})}
          >
          </ha-textarea>
          ${this._provider?.supported_languages?.length?s.qy` <div class="options">
                <ha-language-picker
                  .hass=${this.hass}
                  .languages=${this._provider.supported_languages}
                  .value=${this._language}
                  required
                  @value-changed=${this._languageChanged}
                ></ha-language-picker>
                <ha-tts-voice-picker
                  .hass=${this.hass}
                  .value=${this._voice}
                  .engineId=${this._provider.engine_id}
                  .language=${this._language}
                  required
                  @value-changed=${this._voiceChanged}
                ></ha-tts-voice-picker>
              </div>`:s.s6}
        </div>
        <div class="card-actions">
          <ha-button appearance="plain" @click=${this._ttsClicked}>
            ${this.hass.localize(`ui.components.media-browser.tts.action_${this.action}`)}
          </ha-button>
        </div>
      </ha-card>
      ${this._voice?s.qy`
            <div class="footer">
              ${this.hass.localize("ui.components.media-browser.tts.selected_voice_id")}
              <code>${this._voice||"-"}</code>
              <ha-icon-button
                .path=${g}
                @click=${this._copyVoiceId}
                title=${this.hass.localize("ui.components.media-browser.tts.copy_voice_id")}
              ></ha-icon-button>
            </div>
          `:s.s6}
    `}willUpdate(e){if(super.willUpdate(e),e.has("item")&&this.item.media_content_id){const e=new URLSearchParams(this.item.media_content_id.split("?")[1]),t=e.get("message"),i=e.get("language"),a=e.get("voice");t&&(this._message=t),i&&(this._language=i),a&&(this._voice=a);const s=(0,c.EF)(this.item.media_content_id);s!==this._provider?.engine_id&&(this._provider=void 0,(0,c.u1)(this.hass,s).then((e=>{if(this._provider=e.provider,!this._language&&e.provider.supported_languages?.length){const t=`${this.hass.config.language}-${this.hass.config.country}`.toLowerCase(),i=e.provider.supported_languages.find((e=>e.toLowerCase()===t));if(i)return void(this._language=i);this._language=e.provider.supported_languages?.find((e=>e.substring(0,2)===this.hass.config.language.substring(0,2)))}})),"cloud"===s&&(0,l.eN)(this.hass).then((e=>{e.logged_in&&(this._language=e.prefs.tts_default_voice[0])})))}if(e.has("_message"))return;const t=this.shadowRoot.querySelector("ha-textarea")?.value;void 0!==t&&t!==this._message&&(this._message=t)}_languageChanged(e){this._language=e.detail.value}_voiceChanged(e){this._voice=e.detail.value}async _ttsClicked(){const e=this.shadowRoot.querySelector("ha-textarea").value;this._message=e;const t={...this.item},i=new URLSearchParams;i.append("message",e),this._language&&i.append("language",this._language),this._voice&&i.append("voice",this._voice),t.media_content_id=`${t.media_content_id.split("?")[0]}?${i.toString()}`,t.media_content_type="audio/mp3",t.can_play=!0,t.title=e,(0,n.r)(this,"tts-picked",{item:t})}async _copyVoiceId(e){e.preventDefault(),await(0,d.l)(this._voice),(0,p.P)(this,{message:this.hass.localize("ui.common.copied_clipboard")})}}v.styles=[h.og,s.AH`
      :host {
        margin: 16px auto;
        padding: 0 8px;
        display: flex;
        flex-direction: column;
        max-width: 448px;
      }
      .options {
        margin-top: 16px;
        display: flex;
        justify-content: space-between;
      }
      ha-textarea {
        width: 100%;
      }
      button.link {
        color: var(--primary-color);
      }
      .footer {
        font-size: var(--ha-font-size-s);
        color: var(--secondary-text-color);
        margin: 16px 0;
        text-align: center;
      }
      .footer code {
        font-weight: var(--ha-font-weight-bold);
      }
      .footer {
        --mdc-icon-size: 14px;
        --mdc-icon-button-size: 24px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 6px;
      }
    `],(0,a.__decorate)([(0,o.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],v.prototype,"item",void 0),(0,a.__decorate)([(0,o.MZ)()],v.prototype,"action",void 0),(0,a.__decorate)([(0,o.wk)()],v.prototype,"_language",void 0),(0,a.__decorate)([(0,o.wk)()],v.prototype,"_voice",void 0),(0,a.__decorate)([(0,o.wk)()],v.prototype,"_provider",void 0),(0,a.__decorate)([(0,o.wk)(),(0,r.I)({key:"TtsMessage",state:!0,subscribe:!1})],v.prototype,"_message",void 0),v=(0,a.__decorate)([(0,o.EM)("ha-browse-media-tts")],v),t()}catch(g){t(g)}}))},79739:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(69868),s=i(84922),o=i(11991),r=i(73120),n=i(84397),d=(i(95635),i(76943)),l=i(77625),c=e([d]);d=(c.then?(await c)():c)[0];const h="M19.39 10.74L11 19.13V20H4C2.9 20 2 19.11 2 18V6C2 4.89 2.89 4 4 4H10L12 6H20C21.1 6 22 6.89 22 8V10.15C21.74 10.06 21.46 10 21.17 10C20.5 10 19.87 10.26 19.39 10.74M13 19.96V22H15.04L21.17 15.88L19.13 13.83L13 19.96M22.85 13.47L21.53 12.15C21.33 11.95 21 11.95 20.81 12.15L19.83 13.13L21.87 15.17L22.85 14.19C23.05 14 23.05 13.67 22.85 13.47Z";class p extends s.WF{render(){return this.currentItem&&((0,n.Jz)(this.currentItem.media_content_id||"")||this.hass.user?.is_admin&&(0,n.iY)(this.currentItem.media_content_id))?s.qy`
      <ha-button appearance="filled" size="small" @click=${this._manage}>
        <ha-svg-icon .path=${h} slot="start"></ha-svg-icon>
        ${this.hass.localize("ui.components.media-browser.file_management.manage")}
      </ha-button>
    `:s.s6}_manage(){(0,l.l)(this,{currentItem:this.currentItem,onClose:()=>(0,r.r)(this,"media-refresh")})}constructor(...e){super(...e),this._uploading=0}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],p.prototype,"currentItem",void 0),(0,a.__decorate)([(0,o.wk)()],p.prototype,"_uploading",void 0),p=(0,a.__decorate)([(0,o.EM)("ha-media-manage-button")],p),t()}catch(h){t(h)}}))},93215:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(69868),s=i(88588),o=i(84922),r=i(11991),n=i(75907),d=i(7577),l=i(60434),c=i(73120),h=i(24802),p=i(6098),u=i(96627),_=i(84397),m=i(87608),g=i(47420),v=i(83566),y=i(35645),b=i(45363),f=i(86435),w=i(57447),x=(i(23749),i(76943)),$=(i(17711),i(86853),i(56730),i(93672),i(19307),i(25223),i(71622)),k=(i(95635),i(89652)),M=i(10825),H=i(26596),I=e([w,x,$,k,M,H]);[w,x,$,k,M,H]=I.then?(await I)():I;const z="M21.5 9.5L20.09 10.92L17 7.83V13.5C17 17.09 14.09 20 10.5 20H4V18H10.5C13 18 15 16 15 13.5V7.83L11.91 10.91L10.5 9.5L16 4L21.5 9.5Z",V="M8,5.14V19.14L19,12.14L8,5.14Z",C="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",A="M19,10H17V8H19M19,13H17V11H19M16,10H14V8H16M16,13H14V11H16M16,17H8V15H16M7,10H5V8H7M7,13H5V11H7M8,11H10V13H8M8,8H10V10H8M11,11H13V13H11M11,8H13V10H11M20,5H4C2.89,5 2,5.89 2,7V17A2,2 0 0,0 4,19H20A2,2 0 0,0 22,17V7C22,5.89 21.1,5 20,5Z",L={can_expand:!0,can_play:!1,can_search:!1,children_media_class:"",media_class:"app",media_content_id:_.xw,media_content_type:"",iconPath:A,title:"Manual entry"};class q extends o.WF{connectedCallback(){super.connectedCallback(),this.updateComplete.then((()=>this._attachResizeObserver()))}disconnectedCallback(){super.disconnectedCallback(),this._resizeObserver&&this._resizeObserver.disconnect()}async refresh(){const e=this.navigateIds[this.navigateIds.length-1];try{this._currentItem=await this._fetchData(this.entityId,e.media_content_id,e.media_content_type),(0,c.r)(this,"media-browsed",{ids:this.navigateIds,current:this._currentItem})}catch(t){this._setError(t)}}play(){this._currentItem?.can_play&&this._runAction(this._currentItem)}willUpdate(e){if(super.willUpdate(e),this.hasUpdated||(0,y.i)(),e.has("entityId"))this._setError(void 0);else if(!e.has("navigateIds"))return;this._setError(void 0);const t=e.get("navigateIds"),i=this.navigateIds;this._content?.scrollTo(0,0),this.scrolled=!1;const a=this._currentItem,s=this._parentItem;this._currentItem=void 0,this._parentItem=void 0;const o=i[i.length-1],r=i.length>1?i[i.length-2]:void 0;let n,d;e.has("entityId")||(t&&i.length===t.length+1&&t.every(((e,t)=>{const a=i[t];return a.media_content_id===e.media_content_id&&a.media_content_type===e.media_content_type}))?d=Promise.resolve(a):t&&i.length===t.length-1&&i.every(((e,i)=>{const a=t[i];return e.media_content_id===a.media_content_id&&e.media_content_type===a.media_content_type}))&&(n=Promise.resolve(s))),o.media_content_id&&(0,_.CY)(o.media_content_id)?(this._currentItem=L,(0,c.r)(this,"media-browsed",{ids:i,current:this._currentItem})):(n||(n=this._fetchData(this.entityId,o.media_content_id,o.media_content_type)),n.then((e=>{this._currentItem=e,(0,c.r)(this,"media-browsed",{ids:i,current:e})}),(a=>{t&&e.has("entityId")&&i.length===t.length&&t.every(((e,t)=>i[t].media_content_id===e.media_content_id&&i[t].media_content_type===e.media_content_type))?(0,c.r)(this,"media-browsed",{ids:[{media_content_id:void 0,media_content_type:void 0}],replace:!0}):"entity_not_found"===a.code&&this.entityId&&(0,p.g0)(this.hass.states[this.entityId]?.state)?this._setError({message:this.hass.localize("ui.components.media-browser.media_player_unavailable"),code:"entity_not_found"}):this._setError(a)}))),d||void 0===r||(d=this._fetchData(this.entityId,r.media_content_id,r.media_content_type)),d&&d.then((e=>{this._parentItem=e}))}shouldUpdate(e){if(e.size>1||!e.has("hass"))return!0;const t=e.get("hass");return void 0===t||t.localize!==this.hass.localize}firstUpdated(){this._measureCard(),this._attachResizeObserver()}updated(e){if(super.updated(e),e.has("_scrolled"))this._animateHeaderHeight();else if(e.has("_currentItem")){if(this._setHeaderHeight(),this._observed)return;const e=this._virtualizer?._virtualizer;e&&(this._observed=!0,setTimeout((()=>e._observeMutations()),0))}}render(){if(this._error)return o.qy`
        <div class="container">
          <ha-alert alert-type="error">
            ${this._renderError(this._error)}
          </ha-alert>
        </div>
      `;if(!this._currentItem)return o.qy`<ha-spinner></ha-spinner>`;const e=this._currentItem,t=this.hass.localize(`ui.components.media-browser.class.${e.media_class}`);let i=e.children||[];const a=new Set;if(this.accept&&i.length>0){let e=[];for(const t of this.accept)if(t.endsWith("/*")){const i=t.slice(0,-1);e.push((e=>e.startsWith(i)))}else{if("*"===t){e=[()=>!0];break}e.push((e=>e===t))}i=i.filter((t=>{const i=t.media_content_type.toLowerCase(),s=t.media_content_type&&e.some((e=>e(i)));return s&&a.add(t.media_content_id),!t.media_content_type||t.can_expand||s}))}const r=u.EC[e.media_class],c=e.children_media_class?u.EC[e.children_media_class]:u.EC.directory,h=e.thumbnail?this._getThumbnailURLorBase64(e.thumbnail).then((e=>`url(${e})`)):"none";return o.qy`
              ${e.can_play?o.qy`
                      <div
                        class="header ${(0,n.H)({"no-img":!e.thumbnail,"no-dialog":!this.dialog})}"
                        @transitionend=${this._setHeaderHeight}
                      >
                        <div class="header-content">
                          ${e.thumbnail?o.qy`
                                <div
                                  class="img"
                                  style="background-image: ${(0,l.T)(h,"")}"
                                >
                                  ${this.narrow&&e?.can_play&&(!this.accept||a.has(e.media_content_id))?o.qy`
                                        <ha-fab
                                          mini
                                          .item=${e}
                                          @click=${this._actionClicked}
                                        >
                                          <ha-svg-icon
                                            slot="icon"
                                            .label=${this.hass.localize(`ui.components.media-browser.${this.action}-media`)}
                                            .path=${"play"===this.action?V:C}
                                          ></ha-svg-icon>
                                          ${this.hass.localize(`ui.components.media-browser.${this.action}`)}
                                        </ha-fab>
                                      `:""}
                                </div>
                              `:o.s6}
                          <div class="header-info">
                            <div class="breadcrumb">
                              <h1 class="title">${e.title}</h1>
                              ${t?o.qy` <h2 class="subtitle">${t}</h2> `:""}
                            </div>
                            ${!e.can_play||e.thumbnail&&this.narrow?"":o.qy`
                                  <ha-button
                                    .item=${e}
                                    @click=${this._actionClicked}
                                  >
                                    <ha-svg-icon
                                      .label=${this.hass.localize(`ui.components.media-browser.${this.action}-media`)}
                                      .path=${"play"===this.action?V:C}
                                      slot="start"
                                    ></ha-svg-icon>
                                    ${this.hass.localize(`ui.components.media-browser.${this.action}`)}
                                  </ha-button>
                                `}
                          </div>
                        </div>
                      </div>
                    `:""}
          <div
            class="content"
            @scroll=${this._scroll}
            @touchmove=${this._scroll}
          >
            ${this._error?o.qy`
                    <div class="container">
                      <ha-alert alert-type="error">
                        ${this._renderError(this._error)}
                      </ha-alert>
                    </div>
                  `:(0,_.CY)(e.media_content_id)?o.qy`<ha-browse-media-manual
                      .item=${{media_content_id:this.defaultId||"",media_content_type:this.defaultType||""}}
                      .hass=${this.hass}
                      @manual-media-picked=${this._manualPicked}
                    ></ha-browse-media-manual>`:(0,m.ni)(e.media_content_id)?o.qy`
                        <ha-browse-media-tts
                          .item=${e}
                          .hass=${this.hass}
                          .action=${this.action}
                          @tts-picked=${this._ttsPicked}
                        ></ha-browse-media-tts>
                      `:i.length||e.not_shown?"grid"===this.preferredLayout||"auto"===this.preferredLayout&&"grid"===c.layout?o.qy`
                            <lit-virtualizer
                              scroller
                              .layout=${(0,s.V)({itemSize:{width:"175px",height:"portrait"===c.thumbnail_ratio?"312px":"225px"},gap:"16px",flex:{preserve:"aspect-ratio"},justify:"space-evenly",direction:"vertical"})}
                              .items=${i}
                              .renderItem=${this._renderGridItem}
                              class="children ${(0,n.H)({portrait:"portrait"===c.thumbnail_ratio,not_shown:!!e.not_shown})}"
                            ></lit-virtualizer>
                            ${e.not_shown?o.qy`
                                  <div class="grid not-shown">
                                    <div class="title">
                                      ${this.hass.localize("ui.components.media-browser.not_shown",{count:e.not_shown})}
                                    </div>
                                  </div>
                                `:""}
                          `:o.qy`
                            <ha-list>
                              <lit-virtualizer
                                scroller
                                .items=${i}
                                style=${(0,d.W)({height:72*i.length+26+"px"})}
                                .renderItem=${this._renderListItem}
                              ></lit-virtualizer>
                              ${e.not_shown?o.qy`
                                    <ha-list-item
                                      noninteractive
                                      class="not-shown"
                                      .graphic=${r.show_list_images?"medium":"avatar"}
                                    >
                                      <span class="title">
                                        ${this.hass.localize("ui.components.media-browser.not_shown",{count:e.not_shown})}
                                      </span>
                                    </ha-list-item>
                                  `:""}
                            </ha-list>
                          `:o.qy`
                          <div class="container no-items">
                            ${"media-source://media_source/local/."===e.media_content_id?o.qy`
                                  <div class="highlight-add-button">
                                    <span>
                                      <ha-svg-icon
                                        .path=${z}
                                      ></ha-svg-icon>
                                    </span>
                                    <span>
                                      ${this.hass.localize("ui.components.media-browser.file_management.highlight_button")}
                                    </span>
                                  </div>
                                `:this.hass.localize("ui.components.media-browser.no_items")}
                          </div>
                        `}
          </div>
        </div>
      </div>
    `}async _getThumbnailURLorBase64(e){return e?e.startsWith("/")?new Promise(((t,i)=>{this.hass.fetchWithAuth(e).then((e=>e.blob())).then((e=>{const a=new FileReader;a.onload=()=>{const e=a.result;t("string"==typeof e?e:"")},a.onerror=e=>i(e),a.readAsDataURL(e)}))})):((0,b.bg)(e)&&(e=(0,b.MR)({domain:(0,b.a_)(e),type:"icon",useFallback:!0,darkOptimized:this.hass.themes?.darkMode})),e):""}_runAction(e){(0,c.r)(this,"media-picked",{item:e,navigateIds:this.navigateIds})}_ttsPicked(e){e.stopPropagation();const t=this.navigateIds.slice(0,-1);t.push(e.detail.item),(0,c.r)(this,"media-picked",{...e.detail,navigateIds:t})}_manualPicked(e){e.stopPropagation(),(0,c.r)(this,"media-picked",{item:e.detail.item,navigateIds:this.navigateIds})}async _fetchData(e,t,i){return(e&&e!==u.H1?(0,u.ET)(this.hass,e,t,i):(0,_.Fn)(this.hass,t)).then((e=>(t||"pick"!==this.action||(e.children=e.children||[],e.children.push(L)),e)))}_measureCard(){this.narrow=(this.dialog?window.innerWidth:this.offsetWidth)<450}async _attachResizeObserver(){this._resizeObserver||(this._resizeObserver=new ResizeObserver((0,h.s)((()=>this._measureCard()),250,!1))),this._resizeObserver.observe(this)}_closeDialogAction(){(0,c.r)(this,"close-dialog")}_setError(e){this.dialog?e&&(this._closeDialogAction(),(0,g.K$)(this,{title:this.hass.localize("ui.components.media-browser.media_browsing_error"),text:this._renderError(e)})):this._error=e}_renderError(e){return"Media directory does not exist."===e.message?o.qy`
        <h2>
          ${this.hass.localize("ui.components.media-browser.no_local_media_found")}
        </h2>
        <p>
          ${this.hass.localize("ui.components.media-browser.no_media_folder")}
          <br />
          ${this.hass.localize("ui.components.media-browser.setup_local_help",{documentation:o.qy`<a
              href=${(0,f.o)(this.hass,"/more-info/local-media/setup-media")}
              target="_blank"
              rel="noreferrer"
              >${this.hass.localize("ui.components.media-browser.documentation")}</a
            >`})}
          <br />
          ${this.hass.localize("ui.components.media-browser.local_media_files")}
        </p>
      `:o.qy`<span class="error">${e.message}</span>`}async _setHeaderHeight(){await this.updateComplete;const e=this._header,t=this._content;e&&t&&(this._headerOffsetHeight=e.offsetHeight,t.style.marginTop=`${this._headerOffsetHeight}px`,t.style.maxHeight=`calc(var(--media-browser-max-height, 100%) - ${this._headerOffsetHeight}px)`)}_animateHeaderHeight(){let e;const t=i=>{void 0===e&&(e=i);const a=i-e;this._setHeaderHeight(),a<400&&requestAnimationFrame(t)};requestAnimationFrame(t)}_scroll(e){const t=e.currentTarget;!this.scrolled&&t.scrollTop>this._headerOffsetHeight?this.scrolled=!0:this.scrolled&&t.scrollTop<this._headerOffsetHeight&&(this.scrolled=!1)}static get styles(){return[v.RF,o.AH`
        :host {
          display: flex;
          flex-direction: column;
          position: relative;
          direction: ltr;
        }

        ha-spinner {
          margin: 40px auto;
        }

        .container {
          padding: 16px;
        }

        .no-items {
          padding-left: 32px;
        }

        .highlight-add-button {
          display: flex;
          flex-direction: row-reverse;
          margin-right: 48px;
          margin-inline-end: 48px;
          margin-inline-start: initial;
          direction: var(--direction);
        }

        .highlight-add-button ha-svg-icon {
          position: relative;
          top: -0.5em;
          margin-left: 8px;
          margin-inline-start: 8px;
          margin-inline-end: initial;
          transform: scaleX(var(--scale-direction));
        }

        .content {
          overflow-y: auto;
          box-sizing: border-box;
          height: 100%;
        }

        /* HEADER */

        .header {
          display: flex;
          justify-content: space-between;
          border-bottom: 1px solid var(--divider-color);
          background-color: var(--card-background-color);
          position: absolute;
          top: 0;
          right: 0;
          left: 0;
          z-index: 3;
          padding: 16px;
        }
        .header_button {
          position: relative;
          right: -8px;
        }
        .header-content {
          display: flex;
          flex-wrap: wrap;
          flex-grow: 1;
          align-items: flex-start;
        }
        .header-content .img {
          height: 175px;
          width: 175px;
          margin-right: 16px;
          background-size: cover;
          border-radius: 2px;
          transition:
            width 0.4s,
            height 0.4s;
        }
        .header-info {
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          align-self: stretch;
          min-width: 0;
          flex: 1;
        }
        .header-info ha-button {
          display: block;
          padding-bottom: 16px;
        }
        .breadcrumb {
          display: flex;
          flex-direction: column;
          overflow: hidden;
          flex-grow: 1;
          padding-top: 16px;
        }
        .breadcrumb .title {
          font-size: var(--ha-font-size-4xl);
          line-height: var(--ha-line-height-condensed);
          font-weight: var(--ha-font-weight-bold);
          margin: 0;
          overflow: hidden;
          display: -webkit-box;
          -webkit-box-orient: vertical;
          -webkit-line-clamp: 2;
          padding-right: 8px;
        }
        .breadcrumb .previous-title {
          font-size: var(--ha-font-size-m);
          padding-bottom: 8px;
          color: var(--secondary-text-color);
          overflow: hidden;
          text-overflow: ellipsis;
          cursor: pointer;
          --mdc-icon-size: 14px;
        }
        .breadcrumb .subtitle {
          font-size: var(--ha-font-size-l);
          overflow: hidden;
          text-overflow: ellipsis;
          margin-bottom: 0;
          transition:
            height 0.5s,
            margin 0.5s;
        }

        .not-shown {
          font-style: italic;
          color: var(--secondary-text-color);
          padding: 8px 16px 8px;
        }

        .grid.not-shown {
          display: flex;
          align-items: center;
          text-align: center;
        }

        /* ============= CHILDREN ============= */

        ha-list {
          --mdc-list-vertical-padding: 0;
          --mdc-list-item-graphic-margin: 0;
          --mdc-theme-text-icon-on-background: var(--secondary-text-color);
          margin-top: 10px;
        }

        ha-list li:last-child {
          display: none;
        }

        ha-list li[divider] {
          border-bottom-color: var(--divider-color);
        }

        ha-list-item {
          width: 100%;
        }

        div.children {
          display: grid;
          grid-template-columns: repeat(
            auto-fit,
            minmax(var(--media-browse-item-size, 175px), 0.1fr)
          );
          grid-gap: 16px;
          padding: 16px;
        }

        :host([dialog]) .children {
          grid-template-columns: repeat(
            auto-fit,
            minmax(var(--media-browse-item-size, 175px), 0.33fr)
          );
        }

        .child {
          display: flex;
          flex-direction: column;
          cursor: pointer;
        }

        ha-card {
          position: relative;
          width: 100%;
          box-sizing: border-box;
        }

        .children ha-card .thumbnail {
          width: 100%;
          position: relative;
          box-sizing: border-box;
          transition: padding-bottom 0.1s ease-out;
          padding-bottom: 100%;
        }

        .portrait ha-card .thumbnail {
          padding-bottom: 150%;
        }

        ha-card .image {
          border-radius: 3px 3px 0 0;
        }

        .image {
          position: absolute;
          top: 0;
          right: 0;
          left: 0;
          bottom: 0;
          background-size: cover;
          background-repeat: no-repeat;
          background-position: center;
        }

        .centered-image {
          margin: 0 8px;
          background-size: contain;
        }

        .brand-image {
          background-size: 40%;
        }

        .children ha-card .icon-holder {
          display: flex;
          justify-content: center;
          align-items: center;
        }

        .child .folder {
          color: var(--secondary-text-color);
          --mdc-icon-size: calc(var(--media-browse-item-size, 175px) * 0.4);
        }

        .child .icon {
          color: #00a9f7; /* Match the png color from brands repo */
          --mdc-icon-size: calc(var(--media-browse-item-size, 175px) * 0.4);
        }

        .child .play {
          position: absolute;
          transition: color 0.5s;
          border-radius: 50%;
          top: calc(50% - 40px);
          right: calc(50% - 35px);
          opacity: 0;
          transition: opacity 0.1s ease-out;
        }

        .child .play:not(.can_expand) {
          --mdc-icon-button-size: 70px;
          --mdc-icon-size: 48px;
          background-color: var(--primary-color);
          color: var(--text-primary-color);
        }

        ha-card:hover .image {
          filter: brightness(70%);
          transition: filter 0.5s;
        }

        ha-card:hover .play {
          opacity: 1;
        }

        ha-card:hover .play.can_expand {
          bottom: 8px;
        }

        .child .play.can_expand {
          background-color: rgba(var(--rgb-card-background-color), 0.5);
          top: auto;
          bottom: 0px;
          right: 8px;
          transition:
            bottom 0.1s ease-out,
            opacity 0.1s ease-out;
        }

        .child .title {
          font-size: var(--ha-font-size-l);
          padding-top: 16px;
          padding-left: 2px;
          overflow: hidden;
          display: -webkit-box;
          -webkit-box-orient: vertical;
          -webkit-line-clamp: 1;
          text-overflow: ellipsis;
        }

        .child ha-card .title {
          margin-bottom: 16px;
          padding-left: 16px;
        }

        ha-list-item .graphic {
          background-size: contain;
          background-repeat: no-repeat;
          background-position: center;
          border-radius: 2px;
          display: flex;
          align-content: center;
          align-items: center;
          line-height: initial;
        }

        ha-list-item .graphic .play {
          opacity: 0;
          transition: all 0.5s;
          background-color: rgba(var(--rgb-card-background-color), 0.5);
          border-radius: 50%;
          --mdc-icon-button-size: 40px;
        }

        ha-list-item:hover .graphic .play {
          opacity: 1;
          color: var(--primary-text-color);
        }

        ha-list-item .graphic .play.show {
          opacity: 1;
          background-color: transparent;
        }

        ha-list-item .title {
          margin-left: 16px;
          margin-inline-start: 16px;
          margin-inline-end: initial;
        }

        /* ============= Narrow ============= */

        :host([narrow]) {
          padding: 0;
        }

        :host([narrow]) .media-source {
          padding: 0 24px;
        }

        :host([narrow]) div.children {
          grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
        }

        :host([narrow]) .breadcrumb .title {
          font-size: var(--ha-font-size-2xl);
        }
        :host([narrow]) .header {
          padding: 0;
        }
        :host([narrow]) .header.no-dialog {
          display: block;
        }
        :host([narrow]) .header_button {
          position: absolute;
          top: 14px;
          right: 8px;
        }
        :host([narrow]) .header-content {
          flex-direction: column;
          flex-wrap: nowrap;
        }
        :host([narrow]) .header-content .img {
          height: auto;
          width: 100%;
          margin-right: 0;
          padding-bottom: 50%;
          margin-bottom: 8px;
          position: relative;
          background-position: center;
          border-radius: 0;
          transition:
            width 0.4s,
            height 0.4s,
            padding-bottom 0.4s;
        }
        ha-fab {
          position: absolute;
          --mdc-theme-secondary: var(--primary-color);
          bottom: -20px;
          right: 20px;
        }
        :host([narrow]) .header-info ha-button {
          margin-top: 16px;
          margin-bottom: 8px;
        }
        :host([narrow]) .header-info {
          padding: 0 16px 8px;
        }

        /* ============= Scroll ============= */
        :host([scrolled]) .breadcrumb .subtitle {
          height: 0;
          margin: 0;
        }
        :host([scrolled]) .breadcrumb .title {
          -webkit-line-clamp: 1;
        }
        :host(:not([narrow])[scrolled]) .header:not(.no-img) ha-icon-button {
          align-self: center;
        }
        :host([scrolled]) .header-info ha-button,
        .no-img .header-info ha-button {
          padding-right: 4px;
        }
        :host([scrolled][narrow]) .no-img .header-info ha-button {
          padding-right: 16px;
        }
        :host([scrolled]) .header-info {
          flex-direction: row;
        }
        :host([scrolled]) .header-info ha-button {
          align-self: center;
          margin-top: 0;
          margin-bottom: 0;
          padding-bottom: 0;
        }
        :host([scrolled][narrow]) .no-img .header-info {
          flex-direction: row-reverse;
        }
        :host([scrolled][narrow]) .header-info {
          padding: 20px 24px 10px 24px;
          align-items: center;
        }
        :host([scrolled]) .header-content {
          align-items: flex-end;
          flex-direction: row;
        }
        :host([scrolled]) .header-content .img {
          height: 75px;
          width: 75px;
        }
        :host([scrolled]) .breadcrumb {
          padding-top: 0;
          align-self: center;
        }
        :host([scrolled][narrow]) .header-content .img {
          height: 100px;
          width: 100px;
          padding-bottom: initial;
          margin-bottom: 0;
        }
        :host([scrolled]) ha-fab {
          bottom: 0px;
          right: -24px;
          --mdc-fab-box-shadow: none;
          --mdc-theme-secondary: rgba(var(--rgb-primary-color), 0.5);
        }

        lit-virtualizer {
          height: 100%;
          overflow: overlay !important;
          contain: size layout !important;
        }

        lit-virtualizer.not_shown {
          height: calc(100% - 36px);
        }

        ha-browse-media-tts {
          direction: var(--direction);
        }
      `]}constructor(...e){super(...e),this.action="play",this.preferredLayout="auto",this.dialog=!1,this.navigateIds=[],this.narrow=!1,this.scrolled=!1,this._observed=!1,this._headerOffsetHeight=0,this._renderGridItem=e=>{const t=e.thumbnail?this._getThumbnailURLorBase64(e.thumbnail).then((e=>`url(${e})`)):"none";return o.qy`
      <div class="child" .item=${e} @click=${this._childClicked}>
        <ha-card outlined>
          <div class="thumbnail">
            ${e.thumbnail?o.qy`
                  <div
                    class="${(0,n.H)({"centered-image":["app","directory"].includes(e.media_class),"brand-image":(0,b.bg)(e.thumbnail)})} image"
                    style="background-image: ${(0,l.T)(t,"")}"
                  ></div>
                `:o.qy`
                  <div class="icon-holder image">
                    <ha-svg-icon
                      class=${e.iconPath?"icon":"folder"}
                      .path=${e.iconPath||u.EC["directory"===e.media_class&&e.children_media_class||e.media_class].icon}
                    ></ha-svg-icon>
                  </div>
                `}
            ${e.can_play?o.qy`
                  <ha-icon-button
                    class="play ${(0,n.H)({can_expand:e.can_expand})}"
                    .item=${e}
                    .label=${this.hass.localize(`ui.components.media-browser.${this.action}-media`)}
                    .path=${"play"===this.action?V:C}
                    @click=${this._actionClicked}
                  ></ha-icon-button>
                `:""}
          </div>
          <ha-tooltip .for="grid-${e.title}" distance="-4">
            ${e.title}
          </ha-tooltip>
          <div .id="grid-${e.title}" class="title">${e.title}</div>
        </ha-card>
      </div>
    `},this._renderListItem=e=>{const t=this._currentItem,i=u.EC[t.media_class],a=i.show_list_images&&e.thumbnail?this._getThumbnailURLorBase64(e.thumbnail).then((e=>`url(${e})`)):"none";return o.qy`
      <ha-list-item
        @click=${this._childClicked}
        .item=${e}
        .graphic=${i.show_list_images?"medium":"avatar"}
      >
        ${"none"!==a||e.can_play?o.qy`<div
              class=${(0,n.H)({graphic:!0,thumbnail:!0===i.show_list_images})}
              style="background-image: ${(0,l.T)(a,"")}"
              slot="graphic"
            >
              ${e.can_play?o.qy`<ha-icon-button
                    class="play ${(0,n.H)({show:!i.show_list_images||!e.thumbnail})}"
                    .item=${e}
                    .label=${this.hass.localize(`ui.components.media-browser.${this.action}-media`)}
                    .path=${"play"===this.action?V:C}
                    @click=${this._actionClicked}
                  ></ha-icon-button>`:o.s6}
            </div>`:o.qy`<ha-svg-icon
              .path=${u.EC["directory"===e.media_class&&e.children_media_class||e.media_class].icon}
              slot="graphic"
            ></ha-svg-icon>`}
        <span class="title">${e.title}</span>
      </ha-list-item>
    `},this._actionClicked=e=>{e.stopPropagation();const t=e.currentTarget.item;this._runAction(t)},this._childClicked=async e=>{const t=e.currentTarget.item;t&&(t.can_expand?(0,c.r)(this,"media-browsed",{ids:[...this.navigateIds,t]}):this._runAction(t))}}}(0,a.__decorate)([(0,r.MZ)({attribute:!1})],q.prototype,"hass",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],q.prototype,"entityId",void 0),(0,a.__decorate)([(0,r.MZ)()],q.prototype,"action",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],q.prototype,"preferredLayout",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],q.prototype,"dialog",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],q.prototype,"navigateIds",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],q.prototype,"accept",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],q.prototype,"defaultId",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],q.prototype,"defaultType",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],q.prototype,"narrow",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],q.prototype,"scrolled",void 0),(0,a.__decorate)([(0,r.wk)()],q.prototype,"_error",void 0),(0,a.__decorate)([(0,r.wk)()],q.prototype,"_parentItem",void 0),(0,a.__decorate)([(0,r.wk)()],q.prototype,"_currentItem",void 0),(0,a.__decorate)([(0,r.P)(".header")],q.prototype,"_header",void 0),(0,a.__decorate)([(0,r.P)(".content")],q.prototype,"_content",void 0),(0,a.__decorate)([(0,r.P)("lit-virtualizer")],q.prototype,"_virtualizer",void 0),(0,a.__decorate)([(0,r.Ls)({passive:!0})],q.prototype,"_scroll",null),q=(0,a.__decorate)([(0,r.EM)("ha-media-player-browse")],q),t()}catch(z){t(z)}}))},77625:function(e,t,i){i.d(t,{l:()=>s});var a=i(73120);const s=(e,t)=>{(0,a.r)(e,"show-dialog",{dialogTag:"dialog-media-manage",dialogImport:()=>i.e("7752").then(i.bind(i,10731)),dialogParams:t})}},70040:function(e,t,i){i.d(t,{eN:()=>r,p7:()=>a,q3:()=>o,vO:()=>s});const a=({hass:e,...t})=>e.callApi("POST","cloud/login",t),s=(e,t,i)=>e.callApi("POST","cloud/register",{email:t,password:i}),o=(e,t)=>e.callApi("POST","cloud/resend_confirm",{email:t}),r=e=>e.callWS({type:"cloud/status"})},28027:function(e,t,i){i.d(t,{QC:()=>o,fK:()=>s,p$:()=>a});const a=(e,t,i)=>e(`component.${t}.title`)||i?.name||t,s=(e,t)=>{const i={type:"manifest/list"};return t&&(i.integrations=t),e.callWS(i)},o=(e,t)=>e.callWS({type:"manifest/get",integration:t})},84397:function(e,t,i){i.d(t,{CY:()=>o,Fn:()=>a,Jz:()=>r,VA:()=>d,WI:()=>l,iY:()=>n,xw:()=>s});const a=(e,t)=>e.callWS({type:"media_source/browse_media",media_content_id:t}),s="__MANUAL_ENTRY__",o=e=>e.startsWith(s),r=e=>e.startsWith("media-source://media_source"),n=e=>e.startsWith("media-source://image_upload"),d=async(e,t,i)=>{const a=new FormData;a.append("media_content_id",t),a.append("file",i);const s=await e.fetchWithAuth("/api/media_source/local_source/upload",{method:"POST",body:a});if(413===s.status)throw new Error(`Uploaded file is too large (${i.name})`);if(200!==s.status)throw new Error("Unknown error");return s.json()},l=async(e,t)=>e.callWS({type:"media_source/local_source/remove",media_content_id:t})},87608:function(e,t,i){i.d(t,{EF:()=>r,S_:()=>a,Xv:()=>n,ni:()=>o,u1:()=>d,z3:()=>l});const a=(e,t)=>e.callApi("POST","tts_get_url",t),s="media-source://tts/",o=e=>e.startsWith(s),r=e=>e.substring(19),n=(e,t,i)=>e.callWS({type:"tts/engine/list",language:t,country:i}),d=(e,t)=>e.callWS({type:"tts/engine/get",engine_id:t}),l=(e,t,i)=>e.callWS({type:"tts/engine/voices",engine_id:t,language:i})},80608:function(e,t,i){i.d(t,{$:()=>o});var a=i(73120);const s=()=>i.e("8221").then(i.bind(i,27084)),o=(e,t)=>{(0,a.r)(e,"show-dialog",{dialogTag:"dialog-helper-detail",dialogImport:s,dialogParams:t})}},35645:function(e,t,i){i.d(t,{i:()=>a});const a=async()=>{await i.e("3330").then(i.bind(i,27737))}},86435:function(e,t,i){i.d(t,{o:()=>a});const a=(e,t)=>`https://${e.config.version.includes("b")?"rc":e.config.version.includes("dev")?"next":"www"}.home-assistant.io${t}`},72698:function(e,t,i){i.d(t,{P:()=>s});var a=i(73120);const s=(e,t)=>(0,a.r)(e,"hass-notification",t)}};
//# sourceMappingURL=5393.aa98e2ad3ab8e8e3.js.map