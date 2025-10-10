"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["5393"],{83490:function(e,t,i){i.d(t,{I:function(){return s}});i(46852),i(99342),i(65315),i(22416),i(36874),i(12977),i(54323);class a{addFromStorage(e){if(!this._storage[e]){const t=this.storage.getItem(e);t&&(this._storage[e]=JSON.parse(t))}}subscribeChanges(e,t){return this._listeners[e]?this._listeners[e].push(t):this._listeners[e]=[t],()=>{this.unsubscribeChanges(e,t)}}unsubscribeChanges(e,t){if(!(e in this._listeners))return;const i=this._listeners[e].indexOf(t);-1!==i&&this._listeners[e].splice(i,1)}hasKey(e){return e in this._storage}getValue(e){return this._storage[e]}setValue(e,t){const i=this._storage[e];this._storage[e]=t;try{void 0===t?this.storage.removeItem(e):this.storage.setItem(e,JSON.stringify(t))}catch(a){}finally{this._listeners[e]&&this._listeners[e].forEach((e=>e(i,t)))}}constructor(e=window.localStorage){this._storage={},this._listeners={},this.storage=e,this.storage===window.localStorage&&window.addEventListener("storage",(e=>{e.key&&this.hasKey(e.key)&&(this._storage[e.key]=e.newValue?JSON.parse(e.newValue):e.newValue,this._listeners[e.key]&&this._listeners[e.key].forEach((t=>t(e.oldValue?JSON.parse(e.oldValue):e.oldValue,this._storage[e.key]))))}))}}const o={};function s(e){return(t,i)=>{if("object"==typeof i)throw new Error("This decorator does not support this compilation type.");const s=e.storage||"localStorage";let r;s&&s in o?r=o[s]:(r=new a(window[s]),o[s]=r);const n=e.key||String(i);r.addFromStorage(n);const d=!1!==e.subscribe?e=>r.subscribeChanges(n,((t,a)=>{e.requestUpdate(i,t)})):void 0,l=()=>r.hasKey(n)?e.deserializer?e.deserializer(r.getValue(n)):r.getValue(n):void 0,c=(t,a)=>{let o;e.state&&(o=l()),r.setValue(n,e.serializer?e.serializer(a):a),e.state&&t.requestUpdate(i,o)},h=t.performUpdate;if(t.performUpdate=function(){this.__initialized=!0,h.call(this)},e.subscribe){const e=t.connectedCallback,i=t.disconnectedCallback;t.connectedCallback=function(){e.call(this);const t=this;t.__unbsubLocalStorage||(t.__unbsubLocalStorage=null==d?void 0:d(this))},t.disconnectedCallback=function(){var e;i.call(this);const t=this;null===(e=t.__unbsubLocalStorage)||void 0===e||e.call(t),t.__unbsubLocalStorage=void 0}}const p=Object.getOwnPropertyDescriptor(t,i);let u;if(void 0===p)u={get(){return l()},set(e){(this.__initialized||void 0===l())&&c(this,e)},configurable:!0,enumerable:!0};else{const e=p.set;u=Object.assign(Object.assign({},p),{},{get(){return l()},set(t){(this.__initialized||void 0===l())&&c(this,t),null==e||e.call(this,t)}})}Object.defineProperty(t,i,u)}}},13125:function(e,t,i){i.a(e,(async function(e,a){try{i.d(t,{T:function(){return n}});var o=i(96904),s=i(65940),r=e([o]);o=(r.then?(await r)():r)[0];const n=(e,t)=>{try{var i,a;return null!==(i=null===(a=d(t))||void 0===a?void 0:a.of(e))&&void 0!==i?i:e}catch(o){return e}},d=(0,s.A)((e=>new Intl.DisplayNames(e.language,{type:"language",fallback:"code"})));a()}catch(n){a(n)}}))},5503:function(e,t,i){i.d(t,{l:function(){return a}});i(5934);const a=async(e,t)=>{if(navigator.clipboard)try{return void(await navigator.clipboard.writeText(e))}catch(o){}const i=null!=t?t:document.body,a=document.createElement("textarea");a.value=e,i.appendChild(a),a.select(),document.execCommand("copy"),i.removeChild(a)}},17711:function(e,t,i){i(35748),i(65315),i(22416),i(95013);var a=i(69868),o=i(84922),s=i(11991),r=i(90933);i(9974),i(95968);let n,d,l=e=>e;class c extends o.WF{get items(){var e;return null===(e=this._menu)||void 0===e?void 0:e.items}get selected(){var e;return null===(e=this._menu)||void 0===e?void 0:e.selected}focus(){var e,t;null!==(e=this._menu)&&void 0!==e&&e.open?this._menu.focusItemAtIndex(0):null===(t=this._triggerButton)||void 0===t||t.focus()}render(){return(0,o.qy)(n||(n=l`
      <div @click=${0}>
        <slot name="trigger" @slotchange=${0}></slot>
      </div>
      <ha-menu
        .corner=${0}
        .menuCorner=${0}
        .fixed=${0}
        .multi=${0}
        .activatable=${0}
        .y=${0}
        .x=${0}
      >
        <slot></slot>
      </ha-menu>
    `),this._handleClick,this._setTriggerAria,this.corner,this.menuCorner,this.fixed,this.multi,this.activatable,this.y,this.x)}firstUpdated(e){super.firstUpdated(e),"rtl"===r.G.document.dir&&this.updateComplete.then((()=>{this.querySelectorAll("ha-list-item").forEach((e=>{const t=document.createElement("style");t.innerHTML="span.material-icons:first-of-type { margin-left: var(--mdc-list-item-graphic-margin, 32px) !important; margin-right: 0px !important;}",e.shadowRoot.appendChild(t)}))}))}_handleClick(){this.disabled||(this._menu.anchor=this.noAnchor?null:this,this._menu.show())}get _triggerButton(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"]')}_setTriggerAria(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}constructor(...e){super(...e),this.corner="BOTTOM_START",this.menuCorner="START",this.x=null,this.y=null,this.multi=!1,this.activatable=!1,this.disabled=!1,this.fixed=!1,this.noAnchor=!1}}c.styles=(0,o.AH)(d||(d=l`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `)),(0,a.__decorate)([(0,s.MZ)()],c.prototype,"corner",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"menu-corner"})],c.prototype,"menuCorner",void 0),(0,a.__decorate)([(0,s.MZ)({type:Number})],c.prototype,"x",void 0),(0,a.__decorate)([(0,s.MZ)({type:Number})],c.prototype,"y",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"multi",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"activatable",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"fixed",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean,attribute:"no-anchor"})],c.prototype,"noAnchor",void 0),(0,a.__decorate)([(0,s.P)("ha-menu",!0)],c.prototype,"_menu",void 0),c=(0,a.__decorate)([(0,s.EM)("ha-button-menu")],c)},96997:function(e,t,i){var a=i(69868),o=i(84922),s=i(11991);let r,n,d=e=>e;class l extends o.WF{render(){return(0,o.qy)(r||(r=d`
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
    `))}static get styles(){return[(0,o.AH)(n||(n=d`
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
      `))]}}l=(0,a.__decorate)([(0,s.EM)("ha-dialog-header")],l)},86480:function(e,t,i){i.a(e,(async function(e,a){try{i.d(t,{t:function(){return f}});var o=i(96904),s=(i(35748),i(35058),i(65315),i(37089),i(95013),i(69868)),r=i(84922),n=i(11991),d=i(65940),l=i(73120),c=i(20674),h=i(13125),p=i(90963),u=i(42983),m=(i(25223),i(37207),e([o,h]));[o,h]=m.then?(await m)():m;let _,g,v,b,y=e=>e;const f=(e,t,i,a)=>{let o=[];if(t){const t=u.P.translations;o=e.map((e=>{var i;let a=null===(i=t[e])||void 0===i?void 0:i.nativeName;if(!a)try{a=new Intl.DisplayNames(e,{type:"language",fallback:"code"}).of(e)}catch(o){a=e}return{value:e,label:a}}))}else a&&(o=e.map((e=>({value:e,label:(0,h.T)(e,a)}))));return!i&&a&&o.sort(((e,t)=>(0,p.SH)(e.label,t.label,a.language))),o};class w extends r.WF{firstUpdated(e){super.firstUpdated(e),this._computeDefaultLanguageOptions()}updated(e){super.updated(e);const t=e.has("hass")&&this.hass&&e.get("hass")&&e.get("hass").locale.language!==this.hass.locale.language;if(e.has("languages")||e.has("value")||t){var i,a;if(this._select.layoutOptions(),this.disabled||this._select.value===this.value||(0,l.r)(this,"value-changed",{value:this._select.value}),!this.value)return;const e=this._getLanguagesOptions(null!==(i=this.languages)&&void 0!==i?i:this._defaultLanguages,this.nativeName,this.noSort,null===(a=this.hass)||void 0===a?void 0:a.locale).findIndex((e=>e.value===this.value));-1===e&&(this.value=void 0),t&&this._select.select(e)}}_computeDefaultLanguageOptions(){this._defaultLanguages=Object.keys(u.P.translations)}render(){var e,t,i,a,o,s,n;const d=this._getLanguagesOptions(null!==(e=this.languages)&&void 0!==e?e:this._defaultLanguages,this.nativeName,this.noSort,null===(t=this.hass)||void 0===t?void 0:t.locale),l=null!==(i=this.value)&&void 0!==i?i:this.required&&!this.disabled?null===(a=d[0])||void 0===a?void 0:a.value:this.value;return(0,r.qy)(_||(_=y`
      <ha-select
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        @selected=${0}
        @closed=${0}
        fixedMenuPosition
        naturalMenuWidth
        .inlineArrow=${0}
      >
        ${0}
      </ha-select>
    `),null!==(o=this.label)&&void 0!==o?o:(null===(s=this.hass)||void 0===s?void 0:s.localize("ui.components.language-picker.language"))||"Language",l||"",this.required,this.disabled,this._changed,c.d,this.inlineArrow,0===d.length?(0,r.qy)(g||(g=y`<ha-list-item value=""
              >${0}</ha-list-item
            >`),(null===(n=this.hass)||void 0===n?void 0:n.localize("ui.components.language-picker.no_languages"))||"No languages"):d.map((e=>(0,r.qy)(v||(v=y`
                <ha-list-item .value=${0}
                  >${0}</ha-list-item
                >
              `),e.value,e.label))))}_changed(e){const t=e.target;this.disabled||""===t.value||t.value===this.value||(this.value=t.value,(0,l.r)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.nativeName=!1,this.noSort=!1,this.inlineArrow=!1,this._defaultLanguages=[],this._getLanguagesOptions=(0,d.A)(f)}}w.styles=(0,r.AH)(b||(b=y`
    ha-select {
      width: 100%;
    }
  `)),(0,s.__decorate)([(0,n.MZ)()],w.prototype,"value",void 0),(0,s.__decorate)([(0,n.MZ)()],w.prototype,"label",void 0),(0,s.__decorate)([(0,n.MZ)({type:Array})],w.prototype,"languages",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],w.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],w.prototype,"disabled",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],w.prototype,"required",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:"native-name",type:Boolean})],w.prototype,"nativeName",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:"no-sort",type:Boolean})],w.prototype,"noSort",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:"inline-arrow",type:Boolean})],w.prototype,"inlineArrow",void 0),(0,s.__decorate)([(0,n.wk)()],w.prototype,"_defaultLanguages",void 0),(0,s.__decorate)([(0,n.P)("ha-select")],w.prototype,"_select",void 0),w=(0,s.__decorate)([(0,n.EM)("ha-language-picker")],w),a()}catch(_){a(_)}}))},89652:function(e,t,i){i.a(e,(async function(e,t){try{i(35748),i(95013);var a=i(69868),o=i(28784),s=i(84922),r=i(11991),n=e([o]);o=(n.then?(await n)():n)[0];let d,l=e=>e;class c extends o.A{static get styles(){return[o.A.styles,(0,s.AH)(d||(d=l`
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
      `))]}constructor(...e){super(...e),this.showDelay=150,this.hideDelay=400}}(0,a.__decorate)([(0,r.MZ)({attribute:"show-delay",type:Number})],c.prototype,"showDelay",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:"hide-delay",type:Number})],c.prototype,"hideDelay",void 0),c=(0,a.__decorate)([(0,r.EM)("ha-tooltip")],c),t()}catch(d){t(d)}}))},52428:function(e,t,i){i(35748),i(65315),i(84136),i(37089),i(5934),i(95013);var a=i(69868),o=i(84922),s=i(11991),r=i(73120),n=i(20674),d=i(24802),l=i(87608);i(25223),i(37207);let c,h,p,u,m=e=>e;const _="__NONE_OPTION__";class g extends o.WF{render(){var e,t;if(!this._voices)return o.s6;const i=null!==(e=this.value)&&void 0!==e?e:this.required?null===(t=this._voices[0])||void 0===t?void 0:t.voice_id:_;return(0,o.qy)(c||(c=m`
      <ha-select
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        @selected=${0}
        @closed=${0}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${0}
        ${0}
      </ha-select>
    `),this.label||this.hass.localize("ui.components.tts-voice-picker.voice"),i,this.required,this.disabled,this._changed,n.d,this.required?o.s6:(0,o.qy)(h||(h=m`<ha-list-item .value=${0}>
              ${0}
            </ha-list-item>`),_,this.hass.localize("ui.components.tts-voice-picker.none")),this._voices.map((e=>(0,o.qy)(p||(p=m`<ha-list-item .value=${0}>
              ${0}
            </ha-list-item>`),e.voice_id,e.name))))}willUpdate(e){super.willUpdate(e),this.hasUpdated?(e.has("language")||e.has("engineId"))&&this._debouncedUpdateVoices():this._updateVoices()}async _updateVoices(){this.engineId&&this.language?(this._voices=(await(0,l.z3)(this.hass,this.engineId,this.language)).voices,this.value&&(this._voices&&this._voices.find((e=>e.voice_id===this.value))||(this.value=void 0,(0,r.r)(this,"value-changed",{value:this.value})))):this._voices=void 0}updated(e){var t,i,a;(super.updated(e),e.has("_voices")&&(null===(t=this._select)||void 0===t?void 0:t.value)!==this.value)&&(null===(i=this._select)||void 0===i||i.layoutOptions(),(0,r.r)(this,"value-changed",{value:null===(a=this._select)||void 0===a?void 0:a.value}))}_changed(e){const t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===_||(this.value=t.value===_?void 0:t.value,(0,r.r)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._debouncedUpdateVoices=(0,d.s)((()=>this._updateVoices()),500)}}g.styles=(0,o.AH)(u||(u=m`
    ha-select {
      width: 100%;
    }
  `)),(0,a.__decorate)([(0,s.MZ)()],g.prototype,"value",void 0),(0,a.__decorate)([(0,s.MZ)()],g.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],g.prototype,"engineId",void 0),(0,a.__decorate)([(0,s.MZ)()],g.prototype,"language",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],g.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],g.prototype,"required",void 0),(0,a.__decorate)([(0,s.wk)()],g.prototype,"_voices",void 0),(0,a.__decorate)([(0,s.P)("ha-select")],g.prototype,"_select",void 0),g=(0,a.__decorate)([(0,s.EM)("ha-tts-voice-picker")],g)},83e3:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t);i(35748),i(5934),i(95013);var o=i(69868),s=i(84922),r=i(11991),n=i(73120),d=i(20674),l=i(83566),c=(i(72847),i(96997),i(25223),i(79739)),h=i(93215),p=e([c,h]);[c,h]=p.then?(await p)():p;let u,m,_,g=e=>e;const v="M3,5A2,2 0 0,1 5,3H19A2,2 0 0,1 21,5V19A2,2 0 0,1 19,21H5C3.89,21 3,20.1 3,19V5M5,5V19H19V5H5M11,7H13A2,2 0 0,1 15,9V17H13V13H11V17H9V9A2,2 0 0,1 11,7M11,9V11H13V9H11Z",b="M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z",y="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",f="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z",w="M10,4V8H14V4H10M16,4V8H20V4H16M16,10V14H20V10H16M16,16V20H20V16H16M14,20V16H10V20H14M8,20V16H4V20H8M8,14V10H4V14H8M8,8V4H4V8H8M10,14H14V10H10V14M4,2H20A2,2 0 0,1 22,4V20A2,2 0 0,1 20,22H4C2.92,22 2,21.1 2,20V4A2,2 0 0,1 4,2Z",x="M11 15H17V17H11V15M9 7H7V9H9V7M11 13H17V11H11V13M11 9H17V7H11V9M9 11H7V13H9V11M21 5V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V5C3 3.9 3.9 3 5 3H19C20.1 3 21 3.9 21 5M19 5H5V19H19V5M9 15H7V17H9V15Z";class $ extends s.WF{showDialog(e){this._params=e,this._navigateIds=e.navigateIds||[{media_content_id:void 0,media_content_type:void 0}]}closeDialog(){this._params=void 0,this._navigateIds=void 0,this._currentItem=void 0,this._preferredLayout="auto",this.classList.remove("opened"),(0,n.r)(this,"dialog-closed",{dialog:this.localName})}render(){var e;return this._params&&this._navigateIds?(0,s.qy)(u||(u=g`
      <ha-dialog
        open
        scrimClickAction
        escapeKeyAction
        hideActions
        flexContent
        .heading=${0}
        @closed=${0}
        @opened=${0}
      >
        <ha-dialog-header show-border slot="heading">
          ${0}
          <span slot="title">
            ${0}
          </span>
          <ha-media-manage-button
            slot="actionItems"
            .hass=${0}
            .currentItem=${0}
            @media-refresh=${0}
          ></ha-media-manage-button>
          <ha-button-menu
            slot="actionItems"
            @action=${0}
            @closed=${0}
            fixed
          >
            <ha-icon-button
              slot="trigger"
              .label=${0}
              .path=${0}
            ></ha-icon-button>
            <ha-list-item graphic="icon">
              ${0}
              <ha-svg-icon
                class=${0}
                slot="graphic"
                .path=${0}
              ></ha-svg-icon>
            </ha-list-item>
            <ha-list-item graphic="icon">
              ${0}
              <ha-svg-icon
                class=${0}
                slot="graphic"
                .path=${0}
              ></ha-svg-icon>
            </ha-list-item>
            <ha-list-item graphic="icon">
              ${0}
              <ha-svg-icon
                slot="graphic"
                class=${0}
                .path=${0}
              ></ha-svg-icon>
            </ha-list-item>
          </ha-button-menu>
          <ha-icon-button
            .label=${0}
            .path=${0}
            dialogAction="close"
            slot="actionItems"
          ></ha-icon-button>
        </ha-dialog-header>
        <ha-media-player-browse
          dialog
          .hass=${0}
          .entityId=${0}
          .navigateIds=${0}
          .action=${0}
          .preferredLayout=${0}
          .accept=${0}
          .defaultId=${0}
          .defaultType=${0}
          @close-dialog=${0}
          @media-picked=${0}
          @media-browsed=${0}
        ></ha-media-player-browse>
      </ha-dialog>
    `),this._currentItem?this._currentItem.title:this.hass.localize("ui.components.media-browser.media-player-browser"),this.closeDialog,this._dialogOpened,this._navigateIds.length>(null!==(e=this._params.minimumNavigateLevel)&&void 0!==e?e:1)?(0,s.qy)(m||(m=g`
                <ha-icon-button
                  slot="navigationIcon"
                  .path=${0}
                  @click=${0}
                ></ha-icon-button>
              `),b,this._goBack):s.s6,this._currentItem?this._currentItem.title:this.hass.localize("ui.components.media-browser.media-player-browser"),this.hass,this._currentItem,this._refreshMedia,this._handleMenuAction,d.d,this.hass.localize("ui.common.menu"),f,this.hass.localize("ui.components.media-browser.auto"),"auto"===this._preferredLayout?"selected_menu_item":"",v,this.hass.localize("ui.components.media-browser.grid"),"grid"===this._preferredLayout?"selected_menu_item":"",w,this.hass.localize("ui.components.media-browser.list"),"list"===this._preferredLayout?"selected_menu_item":"",x,this.hass.localize("ui.common.close"),y,this.hass,this._params.entityId,this._navigateIds,this._action,this._preferredLayout,this._params.accept,this._params.defaultId,this._params.defaultType,this.closeDialog,this._mediaPicked,this._mediaBrowsed):s.s6}_dialogOpened(){this.classList.add("opened")}async _handleMenuAction(e){switch(e.detail.index){case 0:this._preferredLayout="auto";break;case 1:this._preferredLayout="grid";break;case 2:this._preferredLayout="list"}}_goBack(){var e;this._navigateIds=null===(e=this._navigateIds)||void 0===e?void 0:e.slice(0,-1),this._currentItem=void 0}_mediaBrowsed(e){this._navigateIds=e.detail.ids,this._currentItem=e.detail.current}_mediaPicked(e){this._params.mediaPickedCallback(e.detail),"play"!==this._action&&this.closeDialog()}get _action(){return this._params.action||"play"}_refreshMedia(){this._browser.refresh()}static get styles(){return[l.nA,(0,s.AH)(_||(_=g`
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
      `))]}constructor(...e){super(...e),this._preferredLayout="auto"}}(0,o.__decorate)([(0,r.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,o.__decorate)([(0,r.wk)()],$.prototype,"_currentItem",void 0),(0,o.__decorate)([(0,r.wk)()],$.prototype,"_navigateIds",void 0),(0,o.__decorate)([(0,r.wk)()],$.prototype,"_params",void 0),(0,o.__decorate)([(0,r.wk)()],$.prototype,"_preferredLayout",void 0),(0,o.__decorate)([(0,r.P)("ha-media-player-browse")],$.prototype,"_browser",void 0),$=(0,o.__decorate)([(0,r.EM)("dialog-media-player-browse")],$),a()}catch(u){a(u)}}))},26596:function(e,t,i){i.a(e,(async function(e,t){try{i(35748),i(12977),i(95013);var a=i(69868),o=i(84922),s=i(11991),r=i(65940),n=i(73120),d=i(76943),l=(i(86853),i(75518),e([d]));d=(l.then?(await l)():l)[0];let c,h,p=e=>e;class u extends o.WF{render(){return(0,o.qy)(c||(c=p`
      <ha-card>
        <div class="card-content">
          <ha-form
            .hass=${0}
            .schema=${0}
            .data=${0}
            .computeLabel=${0}
            .computeHelper=${0}
            @value-changed=${0}
          ></ha-form>
        </div>
        <div class="card-actions">
          <ha-button @click=${0}>
            ${0}
          </ha-button>
        </div>
      </ha-card>
    `),this.hass,this._schema(),this.item,this._computeLabel,this._computeHelper,this._valueChanged,this._mediaPicked,this.hass.localize("ui.common.submit"))}_valueChanged(e){const t=Object.assign({},e.detail.value);this.item=t}_mediaPicked(){(0,n.r)(this,"manual-media-picked",{item:{media_content_id:this.item.media_content_id||"",media_content_type:this.item.media_content_type||""}})}constructor(...e){super(...e),this._schema=(0,r.A)((()=>[{name:"media_content_id",required:!0,selector:{text:{}}},{name:"media_content_type",required:!1,selector:{text:{}}}])),this._computeLabel=e=>this.hass.localize(`ui.components.selectors.media.${e.name}`),this._computeHelper=e=>this.hass.localize(`ui.components.selectors.media.${e.name}_detail`)}}u.styles=(0,o.AH)(h||(h=p`
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
  `)),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],u.prototype,"item",void 0),u=(0,a.__decorate)([(0,s.EM)("ha-browse-media-manual")],u),t()}catch(c){t(c)}}))},10825:function(e,t,i){i.a(e,(async function(e,t){try{i(35748),i(65315),i(84136),i(12977),i(5934),i(47849),i(95013),i(13484),i(81071),i(92714),i(55885);var a=i(69868),o=i(84922),s=i(11991),r=i(83490),n=i(73120),d=i(5503),l=i(70040),c=i(87608),h=i(83566),p=i(72698),u=i(76943),m=(i(86853),i(86480)),_=(i(79973),i(52428),e([u,m]));[u,m]=_.then?(await _)():_;let g,v,b,y,f=e=>e;const w="M19,21H8V7H19M19,5H8A2,2 0 0,0 6,7V21A2,2 0 0,0 8,23H19A2,2 0 0,0 21,21V7A2,2 0 0,0 19,5M16,1H4A2,2 0 0,0 2,3V17H4V3H16V1Z";class x extends o.WF{render(){var e,t;return(0,o.qy)(g||(g=f`
      <ha-card>
        <div class="card-content">
          <ha-textarea
            autogrow
            .label=${0}
            .value=${0}
          >
          </ha-textarea>
          ${0}
        </div>
        <div class="card-actions">
          <ha-button appearance="plain" @click=${0}>
            ${0}
          </ha-button>
        </div>
      </ha-card>
      ${0}
    `),this.hass.localize("ui.components.media-browser.tts.message"),this._message||this.hass.localize("ui.components.media-browser.tts.example_message",{name:(null===(e=this.hass.user)||void 0===e?void 0:e.name)||"Alice"}),null!==(t=this._provider)&&void 0!==t&&null!==(t=t.supported_languages)&&void 0!==t&&t.length?(0,o.qy)(v||(v=f` <div class="options">
                <ha-language-picker
                  .hass=${0}
                  .languages=${0}
                  .value=${0}
                  required
                  @value-changed=${0}
                ></ha-language-picker>
                <ha-tts-voice-picker
                  .hass=${0}
                  .value=${0}
                  .engineId=${0}
                  .language=${0}
                  required
                  @value-changed=${0}
                ></ha-tts-voice-picker>
              </div>`),this.hass,this._provider.supported_languages,this._language,this._languageChanged,this.hass,this._voice,this._provider.engine_id,this._language,this._voiceChanged):o.s6,this._ttsClicked,this.hass.localize(`ui.components.media-browser.tts.action_${this.action}`),this._voice?(0,o.qy)(b||(b=f`
            <div class="footer">
              ${0}
              <code>${0}</code>
              <ha-icon-button
                .path=${0}
                @click=${0}
                title=${0}
              ></ha-icon-button>
            </div>
          `),this.hass.localize("ui.components.media-browser.tts.selected_voice_id"),this._voice||"-",w,this._copyVoiceId,this.hass.localize("ui.components.media-browser.tts.copy_voice_id")):o.s6)}willUpdate(e){var t;if(super.willUpdate(e),e.has("item")&&this.item.media_content_id){var i;const e=new URLSearchParams(this.item.media_content_id.split("?")[1]),t=e.get("message"),a=e.get("language"),o=e.get("voice");t&&(this._message=t),a&&(this._language=a),o&&(this._voice=o);const s=(0,c.EF)(this.item.media_content_id);s!==(null===(i=this._provider)||void 0===i?void 0:i.engine_id)&&(this._provider=void 0,(0,c.u1)(this.hass,s).then((e=>{var t;if(this._provider=e.provider,!this._language&&null!==(t=e.provider.supported_languages)&&void 0!==t&&t.length){var i;const t=`${this.hass.config.language}-${this.hass.config.country}`.toLowerCase(),a=e.provider.supported_languages.find((e=>e.toLowerCase()===t));if(a)return void(this._language=a);this._language=null===(i=e.provider.supported_languages)||void 0===i?void 0:i.find((e=>e.substring(0,2)===this.hass.config.language.substring(0,2)))}})),"cloud"===s&&(0,l.eN)(this.hass).then((e=>{e.logged_in&&(this._language=e.prefs.tts_default_voice[0])})))}if(e.has("_message"))return;const a=null===(t=this.shadowRoot.querySelector("ha-textarea"))||void 0===t?void 0:t.value;void 0!==a&&a!==this._message&&(this._message=a)}_languageChanged(e){this._language=e.detail.value}_voiceChanged(e){this._voice=e.detail.value}async _ttsClicked(){const e=this.shadowRoot.querySelector("ha-textarea").value;this._message=e;const t=Object.assign({},this.item),i=new URLSearchParams;i.append("message",e),this._language&&i.append("language",this._language),this._voice&&i.append("voice",this._voice),t.media_content_id=`${t.media_content_id.split("?")[0]}?${i.toString()}`,t.media_content_type="audio/mp3",t.can_play=!0,t.title=e,(0,n.r)(this,"tts-picked",{item:t})}async _copyVoiceId(e){e.preventDefault(),await(0,d.l)(this._voice),(0,p.P)(this,{message:this.hass.localize("ui.common.copied_clipboard")})}}x.styles=[h.og,(0,o.AH)(y||(y=f`
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
    `))],(0,a.__decorate)([(0,s.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],x.prototype,"item",void 0),(0,a.__decorate)([(0,s.MZ)()],x.prototype,"action",void 0),(0,a.__decorate)([(0,s.wk)()],x.prototype,"_language",void 0),(0,a.__decorate)([(0,s.wk)()],x.prototype,"_voice",void 0),(0,a.__decorate)([(0,s.wk)()],x.prototype,"_provider",void 0),(0,a.__decorate)([(0,s.wk)(),(0,r.I)({key:"TtsMessage",state:!0,subscribe:!1})],x.prototype,"_message",void 0),x=(0,a.__decorate)([(0,s.EM)("ha-browse-media-tts")],x),t()}catch(g){t(g)}}))},79739:function(e,t,i){i.a(e,(async function(e,t){try{i(35748),i(95013);var a=i(69868),o=i(84922),s=i(11991),r=i(73120),n=i(84397),d=(i(95635),i(76943)),l=i(77625),c=e([d]);d=(c.then?(await c)():c)[0];let h,p=e=>e;const u="M19.39 10.74L11 19.13V20H4C2.9 20 2 19.11 2 18V6C2 4.89 2.89 4 4 4H10L12 6H20C21.1 6 22 6.89 22 8V10.15C21.74 10.06 21.46 10 21.17 10C20.5 10 19.87 10.26 19.39 10.74M13 19.96V22H15.04L21.17 15.88L19.13 13.83L13 19.96M22.85 13.47L21.53 12.15C21.33 11.95 21 11.95 20.81 12.15L19.83 13.13L21.87 15.17L22.85 14.19C23.05 14 23.05 13.67 22.85 13.47Z";class m extends o.WF{render(){var e;return this.currentItem&&((0,n.Jz)(this.currentItem.media_content_id||"")||null!==(e=this.hass.user)&&void 0!==e&&e.is_admin&&(0,n.iY)(this.currentItem.media_content_id))?(0,o.qy)(h||(h=p`
      <ha-button appearance="filled" size="small" @click=${0}>
        <ha-svg-icon .path=${0} slot="start"></ha-svg-icon>
        ${0}
      </ha-button>
    `),this._manage,u,this.hass.localize("ui.components.media-browser.file_management.manage")):o.s6}_manage(){(0,l.l)(this,{currentItem:this.currentItem,onClose:()=>(0,r.r)(this,"media-refresh")})}constructor(...e){super(...e),this._uploading=0}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"currentItem",void 0),(0,a.__decorate)([(0,s.wk)()],m.prototype,"_uploading",void 0),m=(0,a.__decorate)([(0,s.EM)("ha-media-manage-button")],m),t()}catch(h){t(h)}}))},93215:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(30808),o=(i(79827),i(35748),i(99342),i(65315),i(12840),i(837),i(59023),i(12977),i(5934),i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030),i(90917),i(56660),i(95013),i(69868)),s=i(88588),r=i(84922),n=i(11991),d=i(75907),l=i(7577),c=i(55),h=i(73120),p=i(24802),u=i(6098),m=i(96627),_=i(84397),g=i(87608),v=i(47420),b=i(83566),y=i(35645),f=i(45363),w=i(86435),x=i(57447),$=(i(23749),i(76943)),k=(i(17711),i(86853),i(56730),i(93672),i(19307),i(25223),i(71622)),H=(i(95635),i(89652)),M=i(10825),z=i(26596),I=e([a,x,$,k,H,M,z]);[a,x,$,k,H,M,z]=I.then?(await I)():I;let V,L,A,C,q,Z,O,P,E,T,S,U,B,N,W,D,R,F,j,J,Y,K,G,X,Q,ee,te,ie,ae,oe=e=>e;const se="M21.5 9.5L20.09 10.92L17 7.83V13.5C17 17.09 14.09 20 10.5 20H4V18H10.5C13 18 15 16 15 13.5V7.83L11.91 10.91L10.5 9.5L16 4L21.5 9.5Z",re="M8,5.14V19.14L19,12.14L8,5.14Z",ne="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",de="M19,10H17V8H19M19,13H17V11H19M16,10H14V8H16M16,13H14V11H16M16,17H8V15H16M7,10H5V8H7M7,13H5V11H7M8,11H10V13H8M8,8H10V10H8M11,11H13V13H11M11,8H13V10H11M20,5H4C2.89,5 2,5.89 2,7V17A2,2 0 0,0 4,19H20A2,2 0 0,0 22,17V7C22,5.89 21.1,5 20,5Z",le={can_expand:!0,can_play:!1,can_search:!1,children_media_class:"",media_class:"app",media_content_id:_.xw,media_content_type:"",iconPath:de,title:"Manual entry"};class ce extends r.WF{connectedCallback(){super.connectedCallback(),this.updateComplete.then((()=>this._attachResizeObserver()))}disconnectedCallback(){super.disconnectedCallback(),this._resizeObserver&&this._resizeObserver.disconnect()}async refresh(){const e=this.navigateIds[this.navigateIds.length-1];try{this._currentItem=await this._fetchData(this.entityId,e.media_content_id,e.media_content_type),(0,h.r)(this,"media-browsed",{ids:this.navigateIds,current:this._currentItem})}catch(t){this._setError(t)}}play(){var e;null!==(e=this._currentItem)&&void 0!==e&&e.can_play&&this._runAction(this._currentItem)}willUpdate(e){var t;if(super.willUpdate(e),this.hasUpdated||(0,y.i)(),e.has("entityId"))this._setError(void 0);else if(!e.has("navigateIds"))return;this._setError(void 0);const i=e.get("navigateIds"),a=this.navigateIds;null===(t=this._content)||void 0===t||t.scrollTo(0,0),this.scrolled=!1;const o=this._currentItem,s=this._parentItem;this._currentItem=void 0,this._parentItem=void 0;const r=a[a.length-1],n=a.length>1?a[a.length-2]:void 0;let d,l;e.has("entityId")||(i&&a.length===i.length+1&&i.every(((e,t)=>{const i=a[t];return i.media_content_id===e.media_content_id&&i.media_content_type===e.media_content_type}))?l=Promise.resolve(o):i&&a.length===i.length-1&&a.every(((e,t)=>{const a=i[t];return e.media_content_id===a.media_content_id&&e.media_content_type===a.media_content_type}))&&(d=Promise.resolve(s))),r.media_content_id&&(0,_.CY)(r.media_content_id)?(this._currentItem=le,(0,h.r)(this,"media-browsed",{ids:a,current:this._currentItem})):(d||(d=this._fetchData(this.entityId,r.media_content_id,r.media_content_type)),d.then((e=>{this._currentItem=e,(0,h.r)(this,"media-browsed",{ids:a,current:e})}),(t=>{var o;i&&e.has("entityId")&&a.length===i.length&&i.every(((e,t)=>a[t].media_content_id===e.media_content_id&&a[t].media_content_type===e.media_content_type))?(0,h.r)(this,"media-browsed",{ids:[{media_content_id:void 0,media_content_type:void 0}],replace:!0}):"entity_not_found"===t.code&&this.entityId&&(0,u.g0)(null===(o=this.hass.states[this.entityId])||void 0===o?void 0:o.state)?this._setError({message:this.hass.localize("ui.components.media-browser.media_player_unavailable"),code:"entity_not_found"}):this._setError(t)}))),l||void 0===n||(l=this._fetchData(this.entityId,n.media_content_id,n.media_content_type)),l&&l.then((e=>{this._parentItem=e}))}shouldUpdate(e){if(e.size>1||!e.has("hass"))return!0;const t=e.get("hass");return void 0===t||t.localize!==this.hass.localize}firstUpdated(){this._measureCard(),this._attachResizeObserver()}updated(e){if(super.updated(e),e.has("_scrolled"))this._animateHeaderHeight();else if(e.has("_currentItem")){var t;if(this._setHeaderHeight(),this._observed)return;const e=null===(t=this._virtualizer)||void 0===t?void 0:t._virtualizer;e&&(this._observed=!0,setTimeout((()=>e._observeMutations()),0))}}render(){if(this._error)return(0,r.qy)(V||(V=oe`
        <div class="container">
          <ha-alert alert-type="error">
            ${0}
          </ha-alert>
        </div>
      `),this._renderError(this._error));if(!this._currentItem)return(0,r.qy)(L||(L=oe`<ha-spinner></ha-spinner>`));const e=this._currentItem,t=this.hass.localize(`ui.components.media-browser.class.${e.media_class}`);let i=e.children||[];const a=new Set;if(this.accept&&i.length>0){let e=[];for(const t of this.accept)if(t.endsWith("/*")){const i=t.slice(0,-1);e.push((e=>e.startsWith(i)))}else{if("*"===t){e=[()=>!0];break}e.push((e=>e===t))}i=i.filter((t=>{const i=t.media_content_type.toLowerCase(),o=t.media_content_type&&e.some((e=>e(i)));return o&&a.add(t.media_content_id),!t.media_content_type||t.can_expand||o}))}const o=m.EC[e.media_class],n=e.children_media_class?m.EC[e.children_media_class]:m.EC.directory,h=e.thumbnail?this._getThumbnailURLorBase64(e.thumbnail).then((e=>`url(${e})`)):"none";return(0,r.qy)(A||(A=oe`
              ${0}
          <div
            class="content"
            @scroll=${0}
            @touchmove=${0}
          >
            ${0}
          </div>
        </div>
      </div>
    `),e.can_play?(0,r.qy)(C||(C=oe`
                      <div
                        class="header ${0}"
                        @transitionend=${0}
                      >
                        <div class="header-content">
                          ${0}
                          <div class="header-info">
                            <div class="breadcrumb">
                              <h1 class="title">${0}</h1>
                              ${0}
                            </div>
                            ${0}
                          </div>
                        </div>
                      </div>
                    `),(0,d.H)({"no-img":!e.thumbnail,"no-dialog":!this.dialog}),this._setHeaderHeight,e.thumbnail?(0,r.qy)(q||(q=oe`
                                <div
                                  class="img"
                                  style="background-image: ${0}"
                                >
                                  ${0}
                                </div>
                              `),(0,c.T)(h,""),this.narrow&&null!=e&&e.can_play&&(!this.accept||a.has(e.media_content_id))?(0,r.qy)(Z||(Z=oe`
                                        <ha-fab
                                          mini
                                          .item=${0}
                                          @click=${0}
                                        >
                                          <ha-svg-icon
                                            slot="icon"
                                            .label=${0}
                                            .path=${0}
                                          ></ha-svg-icon>
                                          ${0}
                                        </ha-fab>
                                      `),e,this._actionClicked,this.hass.localize(`ui.components.media-browser.${this.action}-media`),"play"===this.action?re:ne,this.hass.localize(`ui.components.media-browser.${this.action}`)):""):r.s6,e.title,t?(0,r.qy)(O||(O=oe` <h2 class="subtitle">${0}</h2> `),t):"",!e.can_play||e.thumbnail&&this.narrow?"":(0,r.qy)(P||(P=oe`
                                  <ha-button
                                    .item=${0}
                                    @click=${0}
                                  >
                                    <ha-svg-icon
                                      .label=${0}
                                      .path=${0}
                                      slot="start"
                                    ></ha-svg-icon>
                                    ${0}
                                  </ha-button>
                                `),e,this._actionClicked,this.hass.localize(`ui.components.media-browser.${this.action}-media`),"play"===this.action?re:ne,this.hass.localize(`ui.components.media-browser.${this.action}`))):"",this._scroll,this._scroll,this._error?(0,r.qy)(E||(E=oe`
                    <div class="container">
                      <ha-alert alert-type="error">
                        ${0}
                      </ha-alert>
                    </div>
                  `),this._renderError(this._error)):(0,_.CY)(e.media_content_id)?(0,r.qy)(T||(T=oe`<ha-browse-media-manual
                      .item=${0}
                      .hass=${0}
                      @manual-media-picked=${0}
                    ></ha-browse-media-manual>`),{media_content_id:this.defaultId||"",media_content_type:this.defaultType||""},this.hass,this._manualPicked):(0,g.ni)(e.media_content_id)?(0,r.qy)(S||(S=oe`
                        <ha-browse-media-tts
                          .item=${0}
                          .hass=${0}
                          .action=${0}
                          @tts-picked=${0}
                        ></ha-browse-media-tts>
                      `),e,this.hass,this.action,this._ttsPicked):i.length||e.not_shown?"grid"===this.preferredLayout||"auto"===this.preferredLayout&&"grid"===n.layout?(0,r.qy)(N||(N=oe`
                            <lit-virtualizer
                              scroller
                              .layout=${0}
                              .items=${0}
                              .renderItem=${0}
                              class="children ${0}"
                            ></lit-virtualizer>
                            ${0}
                          `),(0,s.V)({itemSize:{width:"175px",height:"portrait"===n.thumbnail_ratio?"312px":"225px"},gap:"16px",flex:{preserve:"aspect-ratio"},justify:"space-evenly",direction:"vertical"}),i,this._renderGridItem,(0,d.H)({portrait:"portrait"===n.thumbnail_ratio,not_shown:!!e.not_shown}),e.not_shown?(0,r.qy)(W||(W=oe`
                                  <div class="grid not-shown">
                                    <div class="title">
                                      ${0}
                                    </div>
                                  </div>
                                `),this.hass.localize("ui.components.media-browser.not_shown",{count:e.not_shown})):""):(0,r.qy)(D||(D=oe`
                            <ha-list>
                              <lit-virtualizer
                                scroller
                                .items=${0}
                                style=${0}
                                .renderItem=${0}
                              ></lit-virtualizer>
                              ${0}
                            </ha-list>
                          `),i,(0,l.W)({height:72*i.length+26+"px"}),this._renderListItem,e.not_shown?(0,r.qy)(R||(R=oe`
                                    <ha-list-item
                                      noninteractive
                                      class="not-shown"
                                      .graphic=${0}
                                    >
                                      <span class="title">
                                        ${0}
                                      </span>
                                    </ha-list-item>
                                  `),o.show_list_images?"medium":"avatar",this.hass.localize("ui.components.media-browser.not_shown",{count:e.not_shown})):""):(0,r.qy)(U||(U=oe`
                          <div class="container no-items">
                            ${0}
                          </div>
                        `),"media-source://media_source/local/."===e.media_content_id?(0,r.qy)(B||(B=oe`
                                  <div class="highlight-add-button">
                                    <span>
                                      <ha-svg-icon
                                        .path=${0}
                                      ></ha-svg-icon>
                                    </span>
                                    <span>
                                      ${0}
                                    </span>
                                  </div>
                                `),se,this.hass.localize("ui.components.media-browser.file_management.highlight_button")):this.hass.localize("ui.components.media-browser.no_items")))}async _getThumbnailURLorBase64(e){if(!e)return"";if(e.startsWith("/"))return new Promise(((t,i)=>{this.hass.fetchWithAuth(e).then((e=>e.blob())).then((e=>{const a=new FileReader;a.onload=()=>{const e=a.result;t("string"==typeof e?e:"")},a.onerror=e=>i(e),a.readAsDataURL(e)}))}));var t;(0,f.bg)(e)&&(e=(0,f.MR)({domain:(0,f.a_)(e),type:"icon",useFallback:!0,darkOptimized:null===(t=this.hass.themes)||void 0===t?void 0:t.darkMode}));return e}_runAction(e){(0,h.r)(this,"media-picked",{item:e,navigateIds:this.navigateIds})}_ttsPicked(e){e.stopPropagation();const t=this.navigateIds.slice(0,-1);t.push(e.detail.item),(0,h.r)(this,"media-picked",Object.assign(Object.assign({},e.detail),{},{navigateIds:t}))}_manualPicked(e){e.stopPropagation(),(0,h.r)(this,"media-picked",{item:e.detail.item,navigateIds:this.navigateIds})}async _fetchData(e,t,i){return(e&&e!==m.H1?(0,m.ET)(this.hass,e,t,i):(0,_.Fn)(this.hass,t)).then((e=>(t||"pick"!==this.action||(e.children=e.children||[],e.children.push(le)),e)))}_measureCard(){this.narrow=(this.dialog?window.innerWidth:this.offsetWidth)<450}async _attachResizeObserver(){this._resizeObserver||(this._resizeObserver=new ResizeObserver((0,p.s)((()=>this._measureCard()),250,!1))),this._resizeObserver.observe(this)}_closeDialogAction(){(0,h.r)(this,"close-dialog")}_setError(e){this.dialog?e&&(this._closeDialogAction(),(0,v.K$)(this,{title:this.hass.localize("ui.components.media-browser.media_browsing_error"),text:this._renderError(e)})):this._error=e}_renderError(e){return"Media directory does not exist."===e.message?(0,r.qy)(F||(F=oe`
        <h2>
          ${0}
        </h2>
        <p>
          ${0}
          <br />
          ${0}
          <br />
          ${0}
        </p>
      `),this.hass.localize("ui.components.media-browser.no_local_media_found"),this.hass.localize("ui.components.media-browser.no_media_folder"),this.hass.localize("ui.components.media-browser.setup_local_help",{documentation:(0,r.qy)(j||(j=oe`<a
              href=${0}
              target="_blank"
              rel="noreferrer"
              >${0}</a
            >`),(0,w.o)(this.hass,"/more-info/local-media/setup-media"),this.hass.localize("ui.components.media-browser.documentation"))}),this.hass.localize("ui.components.media-browser.local_media_files")):(0,r.qy)(J||(J=oe`<span class="error">${0}</span>`),e.message)}async _setHeaderHeight(){await this.updateComplete;const e=this._header,t=this._content;e&&t&&(this._headerOffsetHeight=e.offsetHeight,t.style.marginTop=`${this._headerOffsetHeight}px`,t.style.maxHeight=`calc(var(--media-browser-max-height, 100%) - ${this._headerOffsetHeight}px)`)}_animateHeaderHeight(){let e;const t=i=>{void 0===e&&(e=i);const a=i-e;this._setHeaderHeight(),a<400&&requestAnimationFrame(t)};requestAnimationFrame(t)}_scroll(e){const t=e.currentTarget;!this.scrolled&&t.scrollTop>this._headerOffsetHeight?this.scrolled=!0:this.scrolled&&t.scrollTop<this._headerOffsetHeight&&(this.scrolled=!1)}static get styles(){return[b.RF,(0,r.AH)(Y||(Y=oe`
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
      `))]}constructor(...e){super(...e),this.action="play",this.preferredLayout="auto",this.dialog=!1,this.navigateIds=[],this.narrow=!1,this.scrolled=!1,this._observed=!1,this._headerOffsetHeight=0,this._renderGridItem=e=>{const t=e.thumbnail?this._getThumbnailURLorBase64(e.thumbnail).then((e=>`url(${e})`)):"none";return(0,r.qy)(K||(K=oe`
      <div class="child" .item=${0} @click=${0}>
        <ha-card outlined>
          <div class="thumbnail">
            ${0}
            ${0}
          </div>
          <ha-tooltip .for="grid-${0}" distance="-4">
            ${0}
          </ha-tooltip>
          <div .id="grid-${0}" class="title">${0}</div>
        </ha-card>
      </div>
    `),e,this._childClicked,e.thumbnail?(0,r.qy)(G||(G=oe`
                  <div
                    class="${0} image"
                    style="background-image: ${0}"
                  ></div>
                `),(0,d.H)({"centered-image":["app","directory"].includes(e.media_class),"brand-image":(0,f.bg)(e.thumbnail)}),(0,c.T)(t,"")):(0,r.qy)(X||(X=oe`
                  <div class="icon-holder image">
                    <ha-svg-icon
                      class=${0}
                      .path=${0}
                    ></ha-svg-icon>
                  </div>
                `),e.iconPath?"icon":"folder",e.iconPath||m.EC["directory"===e.media_class&&e.children_media_class||e.media_class].icon),e.can_play?(0,r.qy)(Q||(Q=oe`
                  <ha-icon-button
                    class="play ${0}"
                    .item=${0}
                    .label=${0}
                    .path=${0}
                    @click=${0}
                  ></ha-icon-button>
                `),(0,d.H)({can_expand:e.can_expand}),e,this.hass.localize(`ui.components.media-browser.${this.action}-media`),"play"===this.action?re:ne,this._actionClicked):"",e.title,e.title,e.title,e.title)},this._renderListItem=e=>{const t=this._currentItem,i=m.EC[t.media_class],a=i.show_list_images&&e.thumbnail?this._getThumbnailURLorBase64(e.thumbnail).then((e=>`url(${e})`)):"none";return(0,r.qy)(ee||(ee=oe`
      <ha-list-item
        @click=${0}
        .item=${0}
        .graphic=${0}
      >
        ${0}
        <span class="title">${0}</span>
      </ha-list-item>
    `),this._childClicked,e,i.show_list_images?"medium":"avatar","none"!==a||e.can_play?(0,r.qy)(ie||(ie=oe`<div
              class=${0}
              style="background-image: ${0}"
              slot="graphic"
            >
              ${0}
            </div>`),(0,d.H)({graphic:!0,thumbnail:!0===i.show_list_images}),(0,c.T)(a,""),e.can_play?(0,r.qy)(ae||(ae=oe`<ha-icon-button
                    class="play ${0}"
                    .item=${0}
                    .label=${0}
                    .path=${0}
                    @click=${0}
                  ></ha-icon-button>`),(0,d.H)({show:!i.show_list_images||!e.thumbnail}),e,this.hass.localize(`ui.components.media-browser.${this.action}-media`),"play"===this.action?re:ne,this._actionClicked):r.s6):(0,r.qy)(te||(te=oe`<ha-svg-icon
              .path=${0}
              slot="graphic"
            ></ha-svg-icon>`),m.EC["directory"===e.media_class&&e.children_media_class||e.media_class].icon),e.title)},this._actionClicked=e=>{e.stopPropagation();const t=e.currentTarget.item;this._runAction(t)},this._childClicked=async e=>{const t=e.currentTarget.item;t&&(t.can_expand?(0,h.r)(this,"media-browsed",{ids:[...this.navigateIds,t]}):this._runAction(t))}}}(0,o.__decorate)([(0,n.MZ)({attribute:!1})],ce.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],ce.prototype,"entityId",void 0),(0,o.__decorate)([(0,n.MZ)()],ce.prototype,"action",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],ce.prototype,"preferredLayout",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],ce.prototype,"dialog",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],ce.prototype,"navigateIds",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],ce.prototype,"accept",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],ce.prototype,"defaultId",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],ce.prototype,"defaultType",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],ce.prototype,"narrow",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],ce.prototype,"scrolled",void 0),(0,o.__decorate)([(0,n.wk)()],ce.prototype,"_error",void 0),(0,o.__decorate)([(0,n.wk)()],ce.prototype,"_parentItem",void 0),(0,o.__decorate)([(0,n.wk)()],ce.prototype,"_currentItem",void 0),(0,o.__decorate)([(0,n.P)(".header")],ce.prototype,"_header",void 0),(0,o.__decorate)([(0,n.P)(".content")],ce.prototype,"_content",void 0),(0,o.__decorate)([(0,n.P)("lit-virtualizer")],ce.prototype,"_virtualizer",void 0),(0,o.__decorate)([(0,n.Ls)({passive:!0})],ce.prototype,"_scroll",null),ce=(0,o.__decorate)([(0,n.EM)("ha-media-player-browse")],ce),t()}catch(V){t(V)}}))},77625:function(e,t,i){i.d(t,{l:function(){return o}});i(35748),i(5934),i(95013);var a=i(73120);const o=(e,t)=>{(0,a.r)(e,"show-dialog",{dialogTag:"dialog-media-manage",dialogImport:()=>Promise.all([i.e("1679"),i.e("7752")]).then(i.bind(i,10731)),dialogParams:t})}},70040:function(e,t,i){i.d(t,{eN:function(){return d},p7:function(){return s},q3:function(){return n},vO:function(){return r}});var a=i(52012);i(12977);const o=["hass"],s=e=>{let{hass:t}=e,i=(0,a.A)(e,o);return t.callApi("POST","cloud/login",i)},r=(e,t,i)=>e.callApi("POST","cloud/register",{email:t,password:i}),n=(e,t)=>e.callApi("POST","cloud/resend_confirm",{email:t}),d=e=>e.callWS({type:"cloud/status"})},84397:function(e,t,i){i.d(t,{CY:function(){return s},Fn:function(){return a},Jz:function(){return r},VA:function(){return d},WI:function(){return l},iY:function(){return n},xw:function(){return o}});i(46852),i(5934),i(56660);const a=(e,t)=>e.callWS({type:"media_source/browse_media",media_content_id:t}),o="__MANUAL_ENTRY__",s=e=>e.startsWith(o),r=e=>e.startsWith("media-source://media_source"),n=e=>e.startsWith("media-source://image_upload"),d=async(e,t,i)=>{const a=new FormData;a.append("media_content_id",t),a.append("file",i);const o=await e.fetchWithAuth("/api/media_source/local_source/upload",{method:"POST",body:a});if(413===o.status)throw new Error(`Uploaded file is too large (${i.name})`);if(200!==o.status)throw new Error("Unknown error");return o.json()},l=async(e,t)=>e.callWS({type:"media_source/local_source/remove",media_content_id:t})},35645:function(e,t,i){i.d(t,{i:function(){return a}});i(35748),i(5934),i(95013);const a=async()=>{await i.e("3767").then(i.bind(i,29338))}},86435:function(e,t,i){i.d(t,{o:function(){return a}});i(79827),i(18223);const a=(e,t)=>`https://${e.config.version.includes("b")?"rc":e.config.version.includes("dev")?"next":"www"}.home-assistant.io${t}`},72698:function(e,t,i){i.d(t,{P:function(){return o}});var a=i(73120);const o=(e,t)=>(0,a.r)(e,"hass-notification",t)}}]);
//# sourceMappingURL=5393.69c07ecba276096c.js.map