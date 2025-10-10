"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2719"],{895:function(t,e,i){i.a(t,(async function(t,s){try{i.d(e,{PE:function(){return c}});i(79827);var a=i(96904),n=i(6423),o=i(95075),r=t([a]);a=(r.then?(await r)():r)[0];const l=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],c=t=>t.first_weekday===o.zt.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(t.language).weekInfo.firstDay%7:(0,n.S)(t.language)%7:l.includes(t.first_weekday)?l.indexOf(t.first_weekday):1;s()}catch(l){s(l)}}))},45980:function(t,e,i){i.a(t,(async function(t,s){try{i.d(e,{K:function(){return c}});var a=i(96904),n=i(65940),o=i(83516),r=t([a,o]);[a,o]=r.then?(await r)():r;const l=(0,n.A)((t=>new Intl.RelativeTimeFormat(t.language,{numeric:"auto"}))),c=(t,e,i,s=!0)=>{const a=(0,o.x)(t,i,e);return s?l(e).format(a.value,a.unit):Intl.NumberFormat(e.language,{style:"unit",unit:a.unit,unitDisplay:"long"}).format(Math.abs(a.value))};s()}catch(l){s(l)}}))},8540:function(t,e,i){i.d(e,{j:function(){return s}});const s=(t,e,i)=>(void 0!==i&&(i=!!i),t.hasAttribute(e)?!!i||(t.removeAttribute(e),!1):!1!==i&&(t.setAttribute(e,""),!0))},41602:function(t,e,i){i.d(e,{n:function(){return a}});i(67579),i(41190);const s=/^(\w+)\.(\w+)$/,a=t=>s.test(t)},13125:function(t,e,i){i.a(t,(async function(t,s){try{i.d(e,{T:function(){return r}});var a=i(96904),n=i(65940),o=t([a]);a=(o.then?(await o)():o)[0];const r=(t,e)=>{try{var i,s;return null!==(i=null===(s=l(e))||void 0===s?void 0:s.of(t))&&void 0!==i?i:t}catch(a){return t}},l=(0,n.A)((t=>new Intl.DisplayNames(t.language,{type:"language",fallback:"code"})));s()}catch(r){s(r)}}))},8692:function(t,e,i){i.d(e,{Z:function(){return s}});const s=t=>t.charAt(0).toUpperCase()+t.slice(1)},55266:function(t,e,i){i.d(e,{b:function(){return s}});i(35748),i(42124),i(86581),i(67579),i(39227),i(47849),i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030),i(95013);const s=(t,e)=>{if(t===e)return!0;if(t&&e&&"object"==typeof t&&"object"==typeof e){if(t.constructor!==e.constructor)return!1;let i,a;if(Array.isArray(t)){if(a=t.length,a!==e.length)return!1;for(i=a;0!=i--;)if(!s(t[i],e[i]))return!1;return!0}if(t instanceof Map&&e instanceof Map){if(t.size!==e.size)return!1;for(i of t.entries())if(!e.has(i[0]))return!1;for(i of t.entries())if(!s(i[1],e.get(i[0])))return!1;return!0}if(t instanceof Set&&e instanceof Set){if(t.size!==e.size)return!1;for(i of t.entries())if(!e.has(i[0]))return!1;return!0}if(ArrayBuffer.isView(t)&&ArrayBuffer.isView(e)){if(a=t.length,a!==e.length)return!1;for(i=a;0!=i--;)if(t[i]!==e[i])return!1;return!0}if(t.constructor===RegExp)return t.source===e.source&&t.flags===e.flags;if(t.valueOf!==Object.prototype.valueOf)return t.valueOf()===e.valueOf();if(t.toString!==Object.prototype.toString)return t.toString()===e.toString();const n=Object.keys(t);if(a=n.length,a!==Object.keys(e).length)return!1;for(i=a;0!=i--;)if(!Object.prototype.hasOwnProperty.call(e,n[i]))return!1;for(i=a;0!=i--;){const a=n[i];if(!s(t[a],e[a]))return!1}return!0}return t!=t&&e!=e}},83516:function(t,e,i){i.a(t,(async function(t,s){try{i.d(e,{x:function(){return p}});i(12977);var a=i(41484),n=i(88258),o=i(39826),r=i(895),l=t([r]);r=(l.then?(await l)():l)[0];const d=1e3,h=60,u=60*h;function p(t,e=Date.now(),i,s={}){const l=Object.assign(Object.assign({},_),s||{}),c=(+t-+e)/d;if(Math.abs(c)<l.second)return{value:Math.round(c),unit:"second"};const p=c/h;if(Math.abs(p)<l.minute)return{value:Math.round(p),unit:"minute"};const g=c/u;if(Math.abs(g)<l.hour)return{value:Math.round(g),unit:"hour"};const v=new Date(t),f=new Date(e);v.setHours(0,0,0,0),f.setHours(0,0,0,0);const y=(0,a.c)(v,f);if(0===y)return{value:Math.round(g),unit:"hour"};if(Math.abs(y)<l.day)return{value:y,unit:"day"};const m=(0,r.PE)(i),w=(0,n.k)(v,{weekStartsOn:m}),b=(0,n.k)(f,{weekStartsOn:m}),$=(0,o.I)(w,b);if(0===$)return{value:y,unit:"day"};if(Math.abs($)<l.week)return{value:$,unit:"week"};const k=v.getFullYear()-f.getFullYear(),x=12*k+v.getMonth()-f.getMonth();return 0===x?{value:$,unit:"week"}:Math.abs(x)<l.month||0===k?{value:x,unit:"month"}:{value:Math.round(k),unit:"year"}}const _={second:45,minute:45,hour:22,day:5,week:4,month:11};s()}catch(c){s(c)}}))},44443:function(t,e,i){i(35748),i(12977),i(95013);var s=i(69868),a=i(30103),n=i(86811),o=i(49377),r=i(34800),l=i(84922),c=i(11991);let d,h,u,p,_=t=>t;class g extends a.k{renderOutline(){return this.filled?(0,l.qy)(d||(d=_`<span class="filled"></span>`)):super.renderOutline()}getContainerClasses(){return Object.assign(Object.assign({},super.getContainerClasses()),{},{active:this.active})}renderPrimaryContent(){return(0,l.qy)(h||(h=_`
      <span class="leading icon" aria-hidden="true">
        ${0}
      </span>
      <span class="label">${0}</span>
      <span class="touch"></span>
      <span class="trailing leading icon" aria-hidden="true">
        ${0}
      </span>
    `),this.renderLeadingIcon(),this.label,this.renderTrailingIcon())}renderTrailingIcon(){return(0,l.qy)(u||(u=_`<slot name="trailing-icon"></slot>`))}constructor(...t){super(...t),this.filled=!1,this.active=!1}}g.styles=[o.R,r.R,n.R,(0,l.AH)(p||(p=_`
      :host {
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-assist-chip-container-shape: var(
          --ha-assist-chip-container-shape,
          16px
        );
        --md-assist-chip-outline-color: var(--outline-color);
        --md-assist-chip-label-text-weight: 400;
      }
      /** Material 3 doesn't have a filled chip, so we have to make our own **/
      .filled {
        display: flex;
        pointer-events: none;
        border-radius: inherit;
        inset: 0;
        position: absolute;
        background-color: var(--ha-assist-chip-filled-container-color);
      }
      /** Set the size of mdc icons **/
      ::slotted([slot="icon"]),
      ::slotted([slot="trailing-icon"]) {
        display: flex;
        --mdc-icon-size: var(--md-input-chip-icon-size, 18px);
        font-size: var(--_label-text-size) !important;
      }

      .trailing.icon ::slotted(*),
      .trailing.icon svg {
        margin-inline-end: unset;
        margin-inline-start: var(--_icon-label-space);
      }
      ::before {
        background: var(--ha-assist-chip-container-color, transparent);
        opacity: var(--ha-assist-chip-container-opacity, 1);
      }
      :where(.active)::before {
        background: var(--ha-assist-chip-active-container-color);
        opacity: var(--ha-assist-chip-active-container-opacity);
      }
      .label {
        font-family: var(--ha-font-family-body);
      }
    `))],(0,s.__decorate)([(0,c.MZ)({type:Boolean,reflect:!0})],g.prototype,"filled",void 0),(0,s.__decorate)([(0,c.MZ)({type:Boolean})],g.prototype,"active",void 0),g=(0,s.__decorate)([(0,c.EM)("ha-assist-chip")],g)},86480:function(t,e,i){i.a(t,(async function(t,s){try{i.d(e,{t:function(){return w}});var a=i(96904),n=(i(35748),i(35058),i(65315),i(37089),i(95013),i(69868)),o=i(84922),r=i(11991),l=i(65940),c=i(73120),d=i(20674),h=i(13125),u=i(90963),p=i(42983),_=(i(25223),i(37207),t([a,h]));[a,h]=_.then?(await _)():_;let g,v,f,y,m=t=>t;const w=(t,e,i,s)=>{let a=[];if(e){const e=p.P.translations;a=t.map((t=>{var i;let s=null===(i=e[t])||void 0===i?void 0:i.nativeName;if(!s)try{s=new Intl.DisplayNames(t,{type:"language",fallback:"code"}).of(t)}catch(a){s=t}return{value:t,label:s}}))}else s&&(a=t.map((t=>({value:t,label:(0,h.T)(t,s)}))));return!i&&s&&a.sort(((t,e)=>(0,u.SH)(t.label,e.label,s.language))),a};class b extends o.WF{firstUpdated(t){super.firstUpdated(t),this._computeDefaultLanguageOptions()}updated(t){super.updated(t);const e=t.has("hass")&&this.hass&&t.get("hass")&&t.get("hass").locale.language!==this.hass.locale.language;if(t.has("languages")||t.has("value")||e){var i,s;if(this._select.layoutOptions(),this.disabled||this._select.value===this.value||(0,c.r)(this,"value-changed",{value:this._select.value}),!this.value)return;const t=this._getLanguagesOptions(null!==(i=this.languages)&&void 0!==i?i:this._defaultLanguages,this.nativeName,this.noSort,null===(s=this.hass)||void 0===s?void 0:s.locale).findIndex((t=>t.value===this.value));-1===t&&(this.value=void 0),e&&this._select.select(t)}}_computeDefaultLanguageOptions(){this._defaultLanguages=Object.keys(p.P.translations)}render(){var t,e,i,s,a,n,r;const l=this._getLanguagesOptions(null!==(t=this.languages)&&void 0!==t?t:this._defaultLanguages,this.nativeName,this.noSort,null===(e=this.hass)||void 0===e?void 0:e.locale),c=null!==(i=this.value)&&void 0!==i?i:this.required&&!this.disabled?null===(s=l[0])||void 0===s?void 0:s.value:this.value;return(0,o.qy)(g||(g=m`
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
    `),null!==(a=this.label)&&void 0!==a?a:(null===(n=this.hass)||void 0===n?void 0:n.localize("ui.components.language-picker.language"))||"Language",c||"",this.required,this.disabled,this._changed,d.d,this.inlineArrow,0===l.length?(0,o.qy)(v||(v=m`<ha-list-item value=""
              >${0}</ha-list-item
            >`),(null===(r=this.hass)||void 0===r?void 0:r.localize("ui.components.language-picker.no_languages"))||"No languages"):l.map((t=>(0,o.qy)(f||(f=m`
                <ha-list-item .value=${0}
                  >${0}</ha-list-item
                >
              `),t.value,t.label))))}_changed(t){const e=t.target;this.disabled||""===e.value||e.value===this.value||(this.value=e.value,(0,c.r)(this,"value-changed",{value:this.value}))}constructor(...t){super(...t),this.disabled=!1,this.required=!1,this.nativeName=!1,this.noSort=!1,this.inlineArrow=!1,this._defaultLanguages=[],this._getLanguagesOptions=(0,l.A)(w)}}b.styles=(0,o.AH)(y||(y=m`
    ha-select {
      width: 100%;
    }
  `)),(0,n.__decorate)([(0,r.MZ)()],b.prototype,"value",void 0),(0,n.__decorate)([(0,r.MZ)()],b.prototype,"label",void 0),(0,n.__decorate)([(0,r.MZ)({type:Array})],b.prototype,"languages",void 0),(0,n.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,n.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],b.prototype,"disabled",void 0),(0,n.__decorate)([(0,r.MZ)({type:Boolean})],b.prototype,"required",void 0),(0,n.__decorate)([(0,r.MZ)({attribute:"native-name",type:Boolean})],b.prototype,"nativeName",void 0),(0,n.__decorate)([(0,r.MZ)({attribute:"no-sort",type:Boolean})],b.prototype,"noSort",void 0),(0,n.__decorate)([(0,r.MZ)({attribute:"inline-arrow",type:Boolean})],b.prototype,"inlineArrow",void 0),(0,n.__decorate)([(0,r.wk)()],b.prototype,"_defaultLanguages",void 0),(0,n.__decorate)([(0,r.P)("ha-select")],b.prototype,"_select",void 0),b=(0,n.__decorate)([(0,r.EM)("ha-language-picker")],b),s()}catch(g){s(g)}}))},61647:function(t,e,i){i(35748),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=i(73120),r=(i(9974),i(5673)),l=i(89591),c=i(18396);let d;class h extends r.W1{connectedCallback(){super.connectedCallback(),this.addEventListener("close-menu",this._handleCloseMenu)}_handleCloseMenu(t){var e,i;t.detail.reason.kind===c.fi.KEYDOWN&&t.detail.reason.key===c.NV.ESCAPE||null===(e=(i=t.detail.initiator).clickAction)||void 0===e||e.call(i,t.detail.initiator)}}h.styles=[l.R,(0,a.AH)(d||(d=(t=>t)`
      :host {
        --md-sys-color-surface-container: var(--card-background-color);
      }
    `))],h=(0,s.__decorate)([(0,n.EM)("ha-md-menu")],h);let u,p,_=t=>t;class g extends a.WF{get items(){return this._menu.items}focus(){var t;this._menu.open?this._menu.focus():null===(t=this._triggerButton)||void 0===t||t.focus()}render(){return(0,a.qy)(u||(u=_`
      <div @click=${0}>
        <slot name="trigger" @slotchange=${0}></slot>
      </div>
      <ha-md-menu
        .quick=${0}
        .positioning=${0}
        .hasOverflow=${0}
        .anchorCorner=${0}
        .menuCorner=${0}
        @opening=${0}
        @closing=${0}
      >
        <slot></slot>
      </ha-md-menu>
    `),this._handleClick,this._setTriggerAria,this.quick,this.positioning,this.hasOverflow,this.anchorCorner,this.menuCorner,this._handleOpening,this._handleClosing)}_handleOpening(){(0,o.r)(this,"opening",void 0,{composed:!1})}_handleClosing(){(0,o.r)(this,"closing",void 0,{composed:!1})}_handleClick(){this.disabled||(this._menu.anchorElement=this,this._menu.open?this._menu.close():this._menu.show())}get _triggerButton(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"], ha-assist-chip[slot="trigger"]')}_setTriggerAria(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}constructor(...t){super(...t),this.disabled=!1,this.anchorCorner="end-start",this.menuCorner="start-start",this.hasOverflow=!1,this.quick=!1}}g.styles=(0,a.AH)(p||(p=_`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `)),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],g.prototype,"disabled",void 0),(0,s.__decorate)([(0,n.MZ)()],g.prototype,"positioning",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:"anchor-corner"})],g.prototype,"anchorCorner",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:"menu-corner"})],g.prototype,"menuCorner",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean,attribute:"has-overflow"})],g.prototype,"hasOverflow",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],g.prototype,"quick",void 0),(0,s.__decorate)([(0,n.P)("ha-md-menu",!0)],g.prototype,"_menu",void 0),g=(0,s.__decorate)([(0,n.EM)("ha-md-button-menu")],g)},44335:function(t,e,i){i(35748),i(95013);var s=i(69868),a=i(84922),n=i(11991);i(93672),i(11934);let o,r,l,c=t=>t;class d extends a.WF{render(){var t;return(0,a.qy)(o||(o=c`<ha-textfield
        .invalid=${0}
        .errorMessage=${0}
        .icon=${0}
        .iconTrailing=${0}
        .autocomplete=${0}
        .autocorrect=${0}
        .inputSpellcheck=${0}
        .value=${0}
        .placeholder=${0}
        .label=${0}
        .disabled=${0}
        .required=${0}
        .minLength=${0}
        .maxLength=${0}
        .outlined=${0}
        .helper=${0}
        .validateOnInitialRender=${0}
        .validationMessage=${0}
        .autoValidate=${0}
        .pattern=${0}
        .size=${0}
        .helperPersistent=${0}
        .charCounter=${0}
        .endAligned=${0}
        .prefix=${0}
        .name=${0}
        .inputMode=${0}
        .readOnly=${0}
        .autocapitalize=${0}
        .type=${0}
        .suffix=${0}
        @input=${0}
        @change=${0}
      ></ha-textfield>
      <ha-icon-button
        .label=${0}
        @click=${0}
        .path=${0}
      ></ha-icon-button>`),this.invalid,this.errorMessage,this.icon,this.iconTrailing,this.autocomplete,this.autocorrect,this.inputSpellcheck,this.value,this.placeholder,this.label,this.disabled,this.required,this.minLength,this.maxLength,this.outlined,this.helper,this.validateOnInitialRender,this.validationMessage,this.autoValidate,this.pattern,this.size,this.helperPersistent,this.charCounter,this.endAligned,this.prefix,this.name,this.inputMode,this.readOnly,this.autocapitalize,this._unmaskedPassword?"text":"password",(0,a.qy)(r||(r=c`<div style="width: 24px"></div>`)),this._handleInputEvent,this._handleChangeEvent,(null===(t=this.hass)||void 0===t?void 0:t.localize(this._unmaskedPassword?"ui.components.selectors.text.hide_password":"ui.components.selectors.text.show_password"))||(this._unmaskedPassword?"Hide password":"Show password"),this._toggleUnmaskedPassword,this._unmaskedPassword?"M11.83,9L15,12.16C15,12.11 15,12.05 15,12A3,3 0 0,0 12,9C11.94,9 11.89,9 11.83,9M7.53,9.8L9.08,11.35C9.03,11.56 9,11.77 9,12A3,3 0 0,0 12,15C12.22,15 12.44,14.97 12.65,14.92L14.2,16.47C13.53,16.8 12.79,17 12,17A5,5 0 0,1 7,12C7,11.21 7.2,10.47 7.53,9.8M2,4.27L4.28,6.55L4.73,7C3.08,8.3 1.78,10 1,12C2.73,16.39 7,19.5 12,19.5C13.55,19.5 15.03,19.2 16.38,18.66L16.81,19.08L19.73,22L21,20.73L3.27,3M12,7A5,5 0 0,1 17,12C17,12.64 16.87,13.26 16.64,13.82L19.57,16.75C21.07,15.5 22.27,13.86 23,12C21.27,7.61 17,4.5 12,4.5C10.6,4.5 9.26,4.75 8,5.2L10.17,7.35C10.74,7.13 11.35,7 12,7Z":"M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z")}focus(){this._textField.focus()}checkValidity(){return this._textField.checkValidity()}reportValidity(){return this._textField.reportValidity()}setCustomValidity(t){return this._textField.setCustomValidity(t)}layout(){return this._textField.layout()}_toggleUnmaskedPassword(){this._unmaskedPassword=!this._unmaskedPassword}_handleInputEvent(t){this.value=t.target.value}_handleChangeEvent(t){this.value=t.target.value,this._reDispatchEvent(t)}_reDispatchEvent(t){const e=new Event(t.type,t);this.dispatchEvent(e)}constructor(...t){super(...t),this.icon=!1,this.iconTrailing=!1,this.autocorrect=!0,this.value="",this.placeholder="",this.label="",this.disabled=!1,this.required=!1,this.minLength=-1,this.maxLength=-1,this.outlined=!1,this.helper="",this.validateOnInitialRender=!1,this.validationMessage="",this.autoValidate=!1,this.pattern="",this.size=null,this.helperPersistent=!1,this.charCounter=!1,this.endAligned=!1,this.prefix="",this.suffix="",this.name="",this.readOnly=!1,this.autocapitalize="",this._unmaskedPassword=!1}}d.styles=(0,a.AH)(l||(l=c`
    :host {
      display: block;
      position: relative;
    }
    ha-textfield {
      width: 100%;
    }
    ha-icon-button {
      position: absolute;
      top: 8px;
      right: 8px;
      inset-inline-start: initial;
      inset-inline-end: 8px;
      --mdc-icon-button-size: 40px;
      --mdc-icon-size: 20px;
      color: var(--secondary-text-color);
      direction: var(--direction);
    }
  `)),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"invalid",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:"error-message"})],d.prototype,"errorMessage",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"icon",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"iconTrailing",void 0),(0,s.__decorate)([(0,n.MZ)()],d.prototype,"autocomplete",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"autocorrect",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:"input-spellcheck"})],d.prototype,"inputSpellcheck",void 0),(0,s.__decorate)([(0,n.MZ)({type:String})],d.prototype,"value",void 0),(0,s.__decorate)([(0,n.MZ)({type:String})],d.prototype,"placeholder",void 0),(0,s.__decorate)([(0,n.MZ)({type:String})],d.prototype,"label",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],d.prototype,"disabled",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"required",void 0),(0,s.__decorate)([(0,n.MZ)({type:Number})],d.prototype,"minLength",void 0),(0,s.__decorate)([(0,n.MZ)({type:Number})],d.prototype,"maxLength",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],d.prototype,"outlined",void 0),(0,s.__decorate)([(0,n.MZ)({type:String})],d.prototype,"helper",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"validateOnInitialRender",void 0),(0,s.__decorate)([(0,n.MZ)({type:String})],d.prototype,"validationMessage",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"autoValidate",void 0),(0,s.__decorate)([(0,n.MZ)({type:String})],d.prototype,"pattern",void 0),(0,s.__decorate)([(0,n.MZ)({type:Number})],d.prototype,"size",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"helperPersistent",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"charCounter",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"endAligned",void 0),(0,s.__decorate)([(0,n.MZ)({type:String})],d.prototype,"prefix",void 0),(0,s.__decorate)([(0,n.MZ)({type:String})],d.prototype,"suffix",void 0),(0,s.__decorate)([(0,n.MZ)({type:String})],d.prototype,"name",void 0),(0,s.__decorate)([(0,n.MZ)({type:String,attribute:"input-mode"})],d.prototype,"inputMode",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"readOnly",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1,type:String})],d.prototype,"autocapitalize",void 0),(0,s.__decorate)([(0,n.wk)()],d.prototype,"_unmaskedPassword",void 0),(0,s.__decorate)([(0,n.P)("ha-textfield")],d.prototype,"_textField",void 0),(0,s.__decorate)([(0,n.Ls)({passive:!0})],d.prototype,"_handleInputEvent",null),(0,s.__decorate)([(0,n.Ls)({passive:!0})],d.prototype,"_handleChangeEvent",null),d=(0,s.__decorate)([(0,n.EM)("ha-password-field")],d)},21873:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(95013);var s=i(69868),a=i(22103),n=i(84922),o=i(11991),r=i(45980),l=i(8692),c=t([r]);r=(c.then?(await c)():c)[0];class d extends n.mN{disconnectedCallback(){super.disconnectedCallback(),this._clearInterval()}connectedCallback(){super.connectedCallback(),this.datetime&&this._startInterval()}createRenderRoot(){return this}firstUpdated(t){super.firstUpdated(t),this._updateRelative()}update(t){super.update(t),this._updateRelative()}_clearInterval(){this._interval&&(window.clearInterval(this._interval),this._interval=void 0)}_startInterval(){this._clearInterval(),this._interval=window.setInterval((()=>this._updateRelative()),6e4)}_updateRelative(){if(this.datetime){const t="string"==typeof this.datetime?(0,a.H)(this.datetime):this.datetime,e=(0,r.K)(t,this.hass.locale);this.innerHTML=this.capitalize?(0,l.Z)(e):e}else this.innerHTML=this.hass.localize("ui.components.relative_time.never")}constructor(...t){super(...t),this.capitalize=!1}}(0,s.__decorate)([(0,o.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],d.prototype,"datetime",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],d.prototype,"capitalize",void 0),d=(0,s.__decorate)([(0,o.EM)("ha-relative-time")],d),e()}catch(d){e(d)}}))},52428:function(t,e,i){i(35748),i(65315),i(84136),i(37089),i(5934),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=i(73120),r=i(20674),l=i(24802),c=i(87608);i(25223),i(37207);let d,h,u,p,_=t=>t;const g="__NONE_OPTION__";class v extends a.WF{render(){var t,e;if(!this._voices)return a.s6;const i=null!==(t=this.value)&&void 0!==t?t:this.required?null===(e=this._voices[0])||void 0===e?void 0:e.voice_id:g;return(0,a.qy)(d||(d=_`
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
    `),this.label||this.hass.localize("ui.components.tts-voice-picker.voice"),i,this.required,this.disabled,this._changed,r.d,this.required?a.s6:(0,a.qy)(h||(h=_`<ha-list-item .value=${0}>
              ${0}
            </ha-list-item>`),g,this.hass.localize("ui.components.tts-voice-picker.none")),this._voices.map((t=>(0,a.qy)(u||(u=_`<ha-list-item .value=${0}>
              ${0}
            </ha-list-item>`),t.voice_id,t.name))))}willUpdate(t){super.willUpdate(t),this.hasUpdated?(t.has("language")||t.has("engineId"))&&this._debouncedUpdateVoices():this._updateVoices()}async _updateVoices(){this.engineId&&this.language?(this._voices=(await(0,c.z3)(this.hass,this.engineId,this.language)).voices,this.value&&(this._voices&&this._voices.find((t=>t.voice_id===this.value))||(this.value=void 0,(0,o.r)(this,"value-changed",{value:this.value})))):this._voices=void 0}updated(t){var e,i,s;(super.updated(t),t.has("_voices")&&(null===(e=this._select)||void 0===e?void 0:e.value)!==this.value)&&(null===(i=this._select)||void 0===i||i.layoutOptions(),(0,o.r)(this,"value-changed",{value:null===(s=this._select)||void 0===s?void 0:s.value}))}_changed(t){const e=t.target;!this.hass||""===e.value||e.value===this.value||void 0===this.value&&e.value===g||(this.value=e.value===g?void 0:e.value,(0,o.r)(this,"value-changed",{value:this.value}))}constructor(...t){super(...t),this.disabled=!1,this.required=!1,this._debouncedUpdateVoices=(0,l.s)((()=>this._updateVoices()),500)}}v.styles=(0,a.AH)(p||(p=_`
    ha-select {
      width: 100%;
    }
  `)),(0,s.__decorate)([(0,n.MZ)()],v.prototype,"value",void 0),(0,s.__decorate)([(0,n.MZ)()],v.prototype,"label",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],v.prototype,"engineId",void 0),(0,s.__decorate)([(0,n.MZ)()],v.prototype,"language",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],v.prototype,"disabled",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],v.prototype,"required",void 0),(0,s.__decorate)([(0,n.wk)()],v.prototype,"_voices",void 0),(0,s.__decorate)([(0,n.P)("ha-select")],v.prototype,"_select",void 0),v=(0,s.__decorate)([(0,n.EM)("ha-tts-voice-picker")],v)},85023:function(t,e,i){i.d(e,{QC:function(){return s},ds:function(){return c},mp:function(){return o},nx:function(){return n},u6:function(){return r},vU:function(){return a},zn:function(){return l}});i(35748),i(12977),i(95013);const s=(t,e,i)=>"run-start"===e.type?t={init_options:i,stage:"ready",run:e.data,events:[e]}:t?((t="wake_word-start"===e.type?Object.assign(Object.assign({},t),{},{stage:"wake_word",wake_word:Object.assign(Object.assign({},e.data),{},{done:!1})}):"wake_word-end"===e.type?Object.assign(Object.assign({},t),{},{wake_word:Object.assign(Object.assign(Object.assign({},t.wake_word),e.data),{},{done:!0})}):"stt-start"===e.type?Object.assign(Object.assign({},t),{},{stage:"stt",stt:Object.assign(Object.assign({},e.data),{},{done:!1})}):"stt-end"===e.type?Object.assign(Object.assign({},t),{},{stt:Object.assign(Object.assign(Object.assign({},t.stt),e.data),{},{done:!0})}):"intent-start"===e.type?Object.assign(Object.assign({},t),{},{stage:"intent",intent:Object.assign(Object.assign({},e.data),{},{done:!1})}):"intent-end"===e.type?Object.assign(Object.assign({},t),{},{intent:Object.assign(Object.assign(Object.assign({},t.intent),e.data),{},{done:!0})}):"tts-start"===e.type?Object.assign(Object.assign({},t),{},{stage:"tts",tts:Object.assign(Object.assign({},e.data),{},{done:!1})}):"tts-end"===e.type?Object.assign(Object.assign({},t),{},{tts:Object.assign(Object.assign(Object.assign({},t.tts),e.data),{},{done:!0})}):"run-end"===e.type?Object.assign(Object.assign({},t),{},{stage:"done"}):"error"===e.type?Object.assign(Object.assign({},t),{},{stage:"error",error:e.data}):Object.assign({},t)).events=[...t.events,e],t):void console.warn("Received unexpected event before receiving session",e),a=(t,e,i)=>t.connection.subscribeMessage(e,Object.assign(Object.assign({},i),{},{type:"assist_pipeline/run"})),n=t=>t.callWS({type:"assist_pipeline/pipeline/list"}),o=(t,e)=>t.callWS({type:"assist_pipeline/pipeline/get",pipeline_id:e}),r=(t,e)=>t.callWS(Object.assign({type:"assist_pipeline/pipeline/create"},e)),l=(t,e,i)=>t.callWS(Object.assign({type:"assist_pipeline/pipeline/update",pipeline_id:e},i)),c=t=>t.callWS({type:"assist_pipeline/language/list"})},70040:function(t,e,i){i.d(e,{eN:function(){return l},p7:function(){return n},q3:function(){return r},vO:function(){return o}});var s=i(52012);i(12977);const a=["hass"],n=t=>{let{hass:e}=t,i=(0,s.A)(t,a);return e.callApi("POST","cloud/login",i)},o=(t,e,i)=>t.callApi("POST","cloud/register",{email:e,password:i}),r=(t,e)=>t.callApi("POST","cloud/resend_confirm",{email:e}),l=t=>t.callWS({type:"cloud/status"})},88702:function(t,e,i){i.d(e,{ZE:function(){return s},e1:function(){return n},vc:function(){return a}});var s=function(t){return t[t.CONTROL=1]="CONTROL",t}({});const a=(t,e,i)=>t.callWS({type:"conversation/agent/list",language:e,country:i}),n=(t,e,i)=>t.callWS({type:"conversation/agent/homeassistant/language_scores",language:e,country:i})},20606:function(t,e,i){i.d(e,{xG:function(){return r},b3:function(){return n},eK:function(){return o}});i(46852),i(65315),i(84136),i(5934);var s=i(86543),a=i(38);const n=async t=>(0,s.v)(t.config.version,2021,2,4)?t.callWS({type:"supervisor/api",endpoint:"/addons",method:"get"}):(0,a.PS)(await t.callApi("GET","hassio/addons")),o=async(t,e)=>(0,s.v)(t.config.version,2021,2,4)?t.callWS({type:"supervisor/api",endpoint:`/addons/${e}/start`,method:"post",timeout:null}):t.callApi("POST",`hassio/addons/${e}/start`),r=async(t,e)=>{(0,s.v)(t.config.version,2021,2,4)?await t.callWS({type:"supervisor/api",endpoint:`/addons/${e}/install`,method:"post",timeout:null}):await t.callApi("POST",`hassio/addons/${e}/install`)}},38:function(t,e,i){i.d(e,{PS:function(){return s},VR:function(){return a}});i(79827),i(35748),i(5934),i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030),i(18223),i(95013),i(86543);const s=t=>t.data,a=t=>"object"==typeof t?"object"==typeof t.body?t.body.message||"Unknown error, see supervisor logs":t.body||t.message||"Unknown error, see supervisor logs":t;new Set([502,503,504])},16537:function(t,e,i){i.d(e,{w:function(){return s}});const s=(t,e,i)=>t.callService("select","select_option",{option:i},{entity_id:e})},32512:function(t,e,i){i.d(e,{T:function(){return s}});const s=(t,e,i)=>t.callWS({type:"stt/engine/list",language:e,country:i})},87608:function(t,e,i){i.d(e,{EF:function(){return o},S_:function(){return s},Xv:function(){return r},ni:function(){return n},u1:function(){return l},z3:function(){return c}});i(56660);const s=(t,e)=>t.callApi("POST","tts_get_url",e),a="media-source://tts/",n=t=>t.startsWith(a),o=t=>t.substring(19),r=(t,e,i)=>t.callWS({type:"tts/engine/list",language:e,country:i}),l=(t,e)=>t.callWS({type:"tts/engine/get",engine_id:e}),c=(t,e,i)=>t.callWS({type:"tts/engine/voices",engine_id:e,language:i})},45829:function(t,e,i){i.d(e,{d:function(){return s}});const s=t=>t.callWS({type:"wyoming/info"})},50719:function(t,e,i){i.a(t,(async function(t,e){try{var s=i(69868),a=i(84922),n=i(11991),o=i(73120),r=i(76943),l=(i(95635),i(45363)),c=i(7762),d=t([r]);r=(d.then?(await d)():d)[0];let h,u,p=t=>t;const _="M17.9,17.39C17.64,16.59 16.89,16 16,16H15V13A1,1 0 0,0 14,12H8V10H10A1,1 0 0,0 11,9V7H13A2,2 0 0,0 15,5V4.59C17.93,5.77 20,8.64 20,12C20,14.08 19.2,15.97 17.9,17.39M11,19.93C7.05,19.44 4,16.08 4,12C4,11.38 4.08,10.78 4.21,10.21L9,15V16A2,2 0 0,0 11,18M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z",g="M8,7A2,2 0 0,1 10,9V14A2,2 0 0,1 8,16A2,2 0 0,1 6,14V9A2,2 0 0,1 8,7M14,14C14,16.97 11.84,19.44 9,19.92V22H7V19.92C4.16,19.44 2,16.97 2,14H4A4,4 0 0,0 8,18A4,4 0 0,0 12,14H14M21.41,9.41L17.17,13.66L18.18,10H14A2,2 0 0,1 12,8V4A2,2 0 0,1 14,2H20A2,2 0 0,1 22,4V8C22,8.55 21.78,9.05 21.41,9.41Z",v="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z";class f extends a.WF{render(){var t,e,i;return(0,a.qy)(h||(h=p`<div class="content">
        <img
          src=${0}
          alt="Nabu Casa logo"
        />
        <h1>
          ${0}
        </h1>
        <div class="features">
          <div class="feature speech">
            <div class="logos">
              <div class="round-icon">
                <ha-svg-icon .path=${0}></ha-svg-icon>
              </div>
            </div>
            <h2>
              ${0}
              <span class="no-wrap"></span>
            </h2>
            <p>
              ${0}
            </p>
          </div>
          <div class="feature access">
            <div class="logos">
              <div class="round-icon">
                <ha-svg-icon .path=${0}></ha-svg-icon>
              </div>
            </div>
            <h2>
              ${0}
              <span class="no-wrap"></span>
            </h2>
            <p>
              ${0}
            </p>
          </div>
          <div class="feature">
            <div class="logos">
              <img
                alt="Google Assistant"
                src=${0}
                crossorigin="anonymous"
                referrerpolicy="no-referrer"
              />
              <img
                alt="Amazon Alexa"
                src=${0}
                crossorigin="anonymous"
                referrerpolicy="no-referrer"
              />
            </div>
            <h2>
              ${0}
            </h2>
            <p>
              ${0}
            </p>
          </div>
        </div>
      </div>
      <div class="footer side-by-side">
        <ha-button
          href="https://www.nabucasa.com"
          target="_blank"
          rel="noreferrer noopener"
          appearance="plain"
        >
          <ha-svg-icon .path=${0} slot="start"></ha-svg-icon>
          nabucasa.com
        </ha-button>
        <ha-button @click=${0}
          >${0}</ha-button
        >
      </div>`),`/static/images/logo_nabu_casa${null!==(t=this.hass.themes)&&void 0!==t&&t.darkMode?"_dark":""}.png`,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.cloud.title"),g,this.hass.localize("ui.panel.config.voice_assistants.assistants.cloud.features.speech.title"),this.hass.localize("ui.panel.config.voice_assistants.assistants.cloud.features.speech.text"),_,this.hass.localize("ui.panel.config.voice_assistants.assistants.cloud.features.remote_access.title"),this.hass.localize("ui.panel.config.voice_assistants.assistants.cloud.features.remote_access.text"),(0,l.MR)({domain:"google_assistant",type:"icon",darkOptimized:null===(e=this.hass.themes)||void 0===e?void 0:e.darkMode}),(0,l.MR)({domain:"alexa",type:"icon",darkOptimized:null===(i=this.hass.themes)||void 0===i?void 0:i.darkMode}),this.hass.localize("ui.panel.config.voice_assistants.assistants.cloud.features.assistants.title"),this.hass.localize("ui.panel.config.voice_assistants.assistants.cloud.features.assistants.text"),v,this._signUp,this.hass.localize("ui.panel.config.cloud.register.headline"))}_signUp(){(0,o.r)(this,"cloud-step",{step:"SIGNUP"})}}f.styles=[c.s,(0,a.AH)(u||(u=p`
      :host {
        display: flex;
      }
      .features {
        display: flex;
        flex-direction: column;
        grid-gap: 16px;
        padding: 16px;
      }
      .feature {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin-bottom: 16px;
      }
      .feature .logos {
        margin-bottom: 16px;
      }
      .feature .logos > * {
        width: 40px;
        height: 40px;
        margin: 0 4px;
      }
      .round-icon {
        border-radius: 50%;
        color: #6e41ab;
        background-color: #e8dcf7;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: var(--ha-font-size-2xl);
      }
      .access .round-icon {
        color: #00aef8;
        background-color: #cceffe;
      }
      .feature h2 {
        font-size: var(--ha-font-size-l);
        font-weight: var(--ha-font-weight-medium);
        line-height: var(--ha-line-height-normal);
        margin-top: 0;
        margin-bottom: 8px;
      }
      .feature p {
        font-size: var(--ha-font-size-m);
        font-weight: var(--ha-font-weight-normal);
        line-height: var(--ha-line-height-condensed);
        margin: 0;
      }
    `))],(0,s.__decorate)([(0,n.MZ)({attribute:!1})],f.prototype,"hass",void 0),f=(0,s.__decorate)([(0,n.EM)("cloud-step-intro")],f),e()}catch(h){e(h)}}))},66999:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(12977),i(5934),i(54323),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=i(73120),r=i(68985),l=(i(23749),i(76943)),c=(i(44335),i(95635),i(11934),i(70040)),d=i(78440),h=i(47420),u=i(7762),p=t([l]);l=(p.then?(await p)():p)[0];let _,g,v,f=t=>t;class y extends a.WF{render(){var t;return(0,a.qy)(_||(_=f`<div class="content">
        <img
          src=${0}
          alt="Nabu Casa logo"
        />
        <h1>${0}</h1>
        ${0}
        <ha-textfield
          autofocus
          id="email"
          name="email"
          .label=${0}
          .disabled=${0}
          type="email"
          autocomplete="email"
          required
          @keydown=${0}
          validationMessage=${0}
        ></ha-textfield>
        <ha-password-field
          id="password"
          name="password"
          .label=${0}
          .disabled=${0}
          autocomplete="new-password"
          minlength="8"
          required
          @keydown=${0}
          validationMessage=${0}
        ></ha-password-field>
      </div>
      <div class="footer">
        <ha-button
          @click=${0}
          .disabled=${0}
          >${0}</ha-button
        >
      </div>`),`/static/images/logo_nabu_casa${null!==(t=this.hass.themes)&&void 0!==t&&t.darkMode?"_dark":""}.png`,this.hass.localize("ui.panel.config.cloud.login.sign_in"),this._error?(0,a.qy)(g||(g=f`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):"",this.hass.localize("ui.panel.config.cloud.register.email_address"),this._requestInProgress,this._keyDown,this.hass.localize("ui.panel.config.cloud.register.email_error_msg"),this.hass.localize("ui.panel.config.cloud.register.password"),this._requestInProgress,this._keyDown,this.hass.localize("ui.panel.config.cloud.register.password_error_msg"),this._handleLogin,this._requestInProgress,this.hass.localize("ui.panel.config.cloud.login.sign_in"))}_keyDown(t){"Enter"===t.key&&this._handleLogin()}async _handleLogin(){const t=this._emailField,e=this._passwordField,i=t.value,s=e.value;if(!t.reportValidity())return e.reportValidity(),void t.focus();if(!e.reportValidity())return void e.focus();this._requestInProgress=!0;const a=async(e,i)=>{try{await(0,c.p7)(Object.assign(Object.assign({hass:this.hass,email:e},i?{code:i}:{password:s}),{},{check_connection:this._checkConnection}))}catch(n){const i=n&&n.body&&n.body.code;if("mfarequired"===i){const t=await(0,h.an)(this,{title:this.hass.localize("ui.panel.config.cloud.login.totp_code_prompt_title"),inputLabel:this.hass.localize("ui.panel.config.cloud.login.totp_code"),inputType:"text",defaultValue:"",confirmText:this.hass.localize("ui.panel.config.cloud.login.submit")});if(null!==t&&""!==t)return void(await a(e,t))}if("alreadyconnectederror"===i)return void(0,d.o)(this,{details:JSON.parse(n.body.message),logInHereAction:()=>{this._checkConnection=!1,a(e)},closeDialog:()=>{this._requestInProgress=!1}});if("usernotfound"===i&&e!==e.toLowerCase())return void(await a(e.toLowerCase()));if("PasswordChangeRequired"===i)return(0,h.K$)(this,{title:this.hass.localize("ui.panel.config.cloud.login.alert_password_change_required")}),(0,r.o)("/config/cloud/forgot-password"),void(0,o.r)(this,"closed");switch(this._requestInProgress=!1,i){case"UserNotConfirmed":this._error=this.hass.localize("ui.panel.config.cloud.login.alert_email_confirm_necessary");break;case"mfarequired":this._error=this.hass.localize("ui.panel.config.cloud.login.alert_mfa_code_required");break;case"mfaexpiredornotstarted":this._error=this.hass.localize("ui.panel.config.cloud.login.alert_mfa_expired_or_not_started");break;case"invalidtotpcode":this._error=this.hass.localize("ui.panel.config.cloud.login.alert_totp_code_invalid");break;default:this._error=n&&n.body&&n.body.message?n.body.message:"Unknown error"}t.focus()}};await a(i)}constructor(...t){super(...t),this._requestInProgress=!1,this._checkConnection=!0}}y.styles=[u.s,(0,a.AH)(v||(v=f`
      :host {
        display: block;
      }
      ha-textfield,
      ha-password-field {
        display: block;
      }
    `))],(0,s.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,s.__decorate)([(0,n.wk)()],y.prototype,"_requestInProgress",void 0),(0,s.__decorate)([(0,n.wk)()],y.prototype,"_error",void 0),(0,s.__decorate)([(0,n.wk)()],y.prototype,"_checkConnection",void 0),(0,s.__decorate)([(0,n.P)("#email",!0)],y.prototype,"_emailField",void 0),(0,s.__decorate)([(0,n.P)("#password",!0)],y.prototype,"_passwordField",void 0),y=(0,s.__decorate)([(0,n.EM)("cloud-step-signin")],y),e()}catch(_){e(_)}}))},98769:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(5934),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=i(73120),r=(i(23749),i(76943)),l=(i(44335),i(95635),i(11934),i(70040)),c=i(7762),d=t([r]);r=(d.then?(await d)():d)[0];let h,u,p,_,g,v,f,y=t=>t;class m extends a.WF{render(){var t;return(0,a.qy)(h||(h=y`<div class="content">
        <img
          src=${0}
          alt="Nabu Casa logo"
        />
        <h1>
          ${0}
        </h1>
        ${0}
        ${0}
      </div>
      <div class="footer side-by-side">
        ${0}
      </div>`),`/static/images/logo_nabu_casa${null!==(t=this.hass.themes)&&void 0!==t&&t.darkMode?"_dark":""}.png`,this.hass.localize("ui.panel.config.cloud.register.create_account"),this._error?(0,a.qy)(u||(u=y`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):"","VERIFY"===this._state?(0,a.qy)(p||(p=y`<p>
              ${0}
            </p>`),this.hass.localize("ui.panel.config.cloud.register.confirm_email",{email:this._email})):(0,a.qy)(_||(_=y`<ha-textfield
                autofocus
                id="email"
                name="email"
                .label=${0}
                .disabled=${0}
                type="email"
                autocomplete="email"
                required
                @keydown=${0}
                validationMessage=${0}
              ></ha-textfield>
              <ha-password-field
                id="password"
                name="password"
                .label=${0}
                .disabled=${0}
                autocomplete="new-password"
                minlength="8"
                required
                @keydown=${0}
                validationMessage=${0}
              ></ha-password-field>`),this.hass.localize("ui.panel.config.cloud.register.email_address"),this._requestInProgress,this._keyDown,this.hass.localize("ui.panel.config.cloud.register.email_error_msg"),this.hass.localize("ui.panel.config.cloud.register.password"),this._requestInProgress,this._keyDown,this.hass.localize("ui.panel.config.cloud.register.password_error_msg")),"VERIFY"===this._state?(0,a.qy)(g||(g=y`<ha-button
                @click=${0}
                .disabled=${0}
                appearance="plain"
                >${0}</ha-button
              ><ha-button
                @click=${0}
                .disabled=${0}
                >${0}</ha-button
              >`),this._handleResendVerifyEmail,this._requestInProgress,this.hass.localize("ui.panel.config.cloud.register.resend_confirm_email"),this._login,this._requestInProgress,this.hass.localize("ui.panel.config.cloud.register.clicked_confirm")):(0,a.qy)(v||(v=y`<ha-button
                @click=${0}
                .disabled=${0}
                appearance="plain"
                >${0}</ha-button
              >
              <ha-button
                @click=${0}
                .disabled=${0}
                >${0}</ha-button
              >`),this._signIn,this._requestInProgress,this.hass.localize("ui.panel.config.cloud.login.sign_in"),this._handleRegister,this._requestInProgress,this.hass.localize("ui.common.next")))}_signIn(){(0,o.r)(this,"cloud-step",{step:"SIGNIN"})}_keyDown(t){"Enter"===t.key&&this._handleRegister()}async _handleRegister(){const t=this._emailField,e=this._passwordField;if(!t.reportValidity())return e.reportValidity(),void t.focus();if(!e.reportValidity())return void e.focus();const i=t.value.toLowerCase(),s=e.value;this._requestInProgress=!0;try{await(0,l.vO)(this.hass,i,s),this._email=i,this._password=s,this._verificationEmailSent()}catch(a){this._password="",this._error=a&&a.body&&a.body.message?a.body.message:"Unknown error"}finally{this._requestInProgress=!1}}async _handleResendVerifyEmail(){if(this._email)try{await(0,l.q3)(this.hass,this._email),this._verificationEmailSent()}catch(t){this._error=t&&t.body&&t.body.message?t.body.message:"Unknown error"}}_verificationEmailSent(){this._state="VERIFY",setTimeout((()=>this._login()),5e3)}async _login(){if(this._email&&this._password)try{await(0,l.p7)({hass:this.hass,email:this._email,password:this._password}),(0,o.r)(this,"cloud-step",{step:"DONE"})}catch(e){var t;"usernotconfirmed"===(null==e||null===(t=e.body)||void 0===t?void 0:t.code)?this._verificationEmailSent():this._error="Something went wrong. Please try again."}}constructor(...t){super(...t),this._requestInProgress=!1}}m.styles=[c.s,(0,a.AH)(f||(f=y`
      .content {
        width: 100%;
      }
      ha-textfield,
      ha-password-field {
        display: block;
      }
    `))],(0,s.__decorate)([(0,n.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,s.__decorate)([(0,n.wk)()],m.prototype,"_requestInProgress",void 0),(0,s.__decorate)([(0,n.wk)()],m.prototype,"_email",void 0),(0,s.__decorate)([(0,n.wk)()],m.prototype,"_password",void 0),(0,s.__decorate)([(0,n.wk)()],m.prototype,"_error",void 0),(0,s.__decorate)([(0,n.wk)()],m.prototype,"_state",void 0),(0,s.__decorate)([(0,n.P)("#email",!0)],m.prototype,"_emailField",void 0),(0,s.__decorate)([(0,n.P)("#password",!0)],m.prototype,"_passwordField",void 0),m=(0,s.__decorate)([(0,n.EM)("cloud-step-signup")],m),e()}catch(h){e(h)}}))},7762:function(t,e,i){i.d(e,{s:function(){return n}});var s=i(84922);let a;const n=[i(83566).RF,(0,s.AH)(a||(a=(t=>t)`
    :host {
      align-items: center;
      text-align: center;
      min-height: 400px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      height: 100%;
      padding: 24px;
      box-sizing: border-box;
    }
    .content {
      flex: 1;
    }
    .content img {
      width: 120px;
    }
    @media all and (max-width: 450px), all and (max-height: 500px) {
      :host {
        min-height: 100%;
        height: auto;
      }
      .content img {
        margin-top: 68px;
        margin-bottom: 68px;
      }
    }
    .footer {
      display: flex;
      width: 100%;
      flex-direction: row;
      justify-content: flex-end;
    }
    .footer.full-width {
      flex-direction: column;
    }
    .footer.full-width ha-button {
      width: 100%;
    }
    .footer.centered {
      justify-content: center;
    }
    .footer.side-by-side {
      justify-content: space-between;
    }
  `))]},97938:function(t,e,i){i.a(t,(async function(t,s){try{i.r(e),i.d(e,{HaVoiceAssistantSetupDialog:function(){return G},STEP:function(){return z}});i(79827),i(35748),i(99342),i(65315),i(837),i(84136),i(37089),i(5934),i(18223),i(95013);var a=i(69868),n=i(84922),o=i(11991),r=i(65940),l=i(73120),c=i(92830),d=i(13125),h=(i(44443),i(72847),i(86480)),u=(i(61647),i(39856)),p=i(88702),_=i(6098),g=i(83566),v=i(69216),f=i(36731),y=i(68409),m=i(86088),w=i(23362),b=i(70647),$=i(23866),k=i(8088),x=i(65938),C=t([v,f,y,m,w,b,$,k,x,d,h]);[v,f,y,m,w,b,$,k,x,d,h]=C.then?(await C)():C;let M,S,E,A,O,P,L,I,q,H,T,Z,j,N,W,V,R,D,U=t=>t;const F="M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z",B="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",K="M7,10L12,15L17,10H7Z";var z=function(t){return t[t.INIT=0]="INIT",t[t.UPDATE=1]="UPDATE",t[t.CHECK=2]="CHECK",t[t.WAKEWORD=3]="WAKEWORD",t[t.AREA=4]="AREA",t[t.PIPELINE=5]="PIPELINE",t[t.SUCCESS=6]="SUCCESS",t[t.CLOUD=7]="CLOUD",t[t.LOCAL=8]="LOCAL",t[t.CHANGE_WAKEWORD=9]="CHANGE_WAKEWORD",t}({});class G extends n.WF{async showDialog(t){this._params=t,await this._fetchAssistConfiguration(),this._step=1}async closeDialog(){var t;null===(t=this.renderRoot.querySelector("ha-dialog"))||void 0===t||t.close()}willUpdate(t){t.has("_step")&&5===this._step&&this._getLanguages()}_dialogClosed(){this._params=void 0,this._assistConfiguration=void 0,this._previousSteps=[],this._nextStep=void 0,this._step=0,this._language=void 0,this._languages=[],this._localOption=void 0,(0,l.r)(this,"dialog-closed",{dialog:this.localName})}render(){var t,e;if(!this._params)return n.s6;const i=this._findDomainEntityId(this._params.deviceId,this.hass.entities,"assist_satellite"),s=i?this.hass.states[i]:void 0;return(0,n.qy)(M||(M=U`
      <ha-dialog
        open
        @closed=${0}
        .heading=${0}
        hideActions
        escapeKeyAction
        scrimClickAction
      >
        <ha-dialog-header slot="heading">
          ${0}
          ${0}
        </ha-dialog-header>
        <div
          class="content"
          @next-step=${0}
          @prev-step=${0}
        >
          ${0}
        </div>
      </ha-dialog>
    `),this._dialogClosed,"Voice Satellite setup",8===this._step?n.s6:this._previousSteps.length?(0,n.qy)(S||(S=U`<ha-icon-button
                  slot="navigationIcon"
                  .label=${0}
                  .path=${0}
                  @click=${0}
                ></ha-icon-button>`),null!==(t=this.hass.localize("ui.common.back"))&&void 0!==t?t:"Back",F,this._goToPreviousStep):1!==this._step?(0,n.qy)(E||(E=U`<ha-icon-button
                    slot="navigationIcon"
                    .label=${0}
                    .path=${0}
                    @click=${0}
                  ></ha-icon-button>`),null!==(e=this.hass.localize("ui.common.close"))&&void 0!==e?e:"Close",B,this.closeDialog):n.s6,3===this._step||4===this._step?(0,n.qy)(A||(A=U`<ha-button
                @click=${0}
                class="skip-btn"
                slot="actionItems"
                >${0}</ha-button
              >`),this._goToNextStep,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.skip")):5===this._step&&this._language?(0,n.qy)(O||(O=U`<ha-md-button-menu
                    slot="actionItems"
                    positioning="fixed"
                  >
                    <ha-assist-chip
                      .label=${0}
                      slot="trigger"
                    >
                      <ha-svg-icon
                        slot="trailing-icon"
                        .path=${0}
                      ></ha-svg-icon
                    ></ha-assist-chip>
                    ${0}
                  </ha-md-button-menu>`),(0,d.T)(this._language,this.hass.locale),K,(0,h.t)(this._languages,!1,!1,this.hass.locale).map((t=>(0,n.qy)(P||(P=U`<ha-md-menu-item
                          .value=${0}
                          @click=${0}
                          @keydown=${0}
                          .selected=${0}
                        >
                          ${0}
                        </ha-md-menu-item>`),t.value,this._handlePickLanguage,this._handlePickLanguage,this._language===t.value,t.label)))):n.s6,this._goToNextStep,this._goToPreviousStep,1===this._step?(0,n.qy)(L||(L=U`<ha-voice-assistant-setup-step-update
                .hass=${0}
                .updateEntityId=${0}
              ></ha-voice-assistant-setup-step-update>`),this.hass,this._findDomainEntityId(this._params.deviceId,this.hass.entities,"update")):this._error?(0,n.qy)(I||(I=U`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):(null==s?void 0:s.state)===_.Hh?(0,n.qy)(q||(q=U`<ha-alert alert-type="error"
                    >${0}</ha-alert
                  >`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.not_available")):2===this._step?(0,n.qy)(H||(H=U`<ha-voice-assistant-setup-step-check
                      .hass=${0}
                      .assistEntityId=${0}
                    ></ha-voice-assistant-setup-step-check>`),this.hass,i):3===this._step?(0,n.qy)(T||(T=U`<ha-voice-assistant-setup-step-wake-word
                        .hass=${0}
                        .assistConfiguration=${0}
                        .assistEntityId=${0}
                        .deviceEntities=${0}
                      ></ha-voice-assistant-setup-step-wake-word>`),this.hass,this._assistConfiguration,i,this._deviceEntities(this._params.deviceId,this.hass.entities)):9===this._step?(0,n.qy)(Z||(Z=U`
                          <ha-voice-assistant-setup-step-change-wake-word
                            .hass=${0}
                            .assistConfiguration=${0}
                            .assistEntityId=${0}
                          ></ha-voice-assistant-setup-step-change-wake-word>
                        `),this.hass,this._assistConfiguration,i):4===this._step?(0,n.qy)(j||(j=U`
                            <ha-voice-assistant-setup-step-area
                              .hass=${0}
                              .deviceId=${0}
                            ></ha-voice-assistant-setup-step-area>
                          `),this.hass,this._params.deviceId):5===this._step?(0,n.qy)(N||(N=U`<ha-voice-assistant-setup-step-pipeline
                              .hass=${0}
                              .languages=${0}
                              .language=${0}
                              .assistConfiguration=${0}
                              .assistEntityId=${0}
                              @language-changed=${0}
                            ></ha-voice-assistant-setup-step-pipeline>`),this.hass,this._languages,this._language,this._assistConfiguration,i,this._languageChanged):7===this._step?(0,n.qy)(W||(W=U`<ha-voice-assistant-setup-step-cloud
                                .hass=${0}
                              ></ha-voice-assistant-setup-step-cloud>`),this.hass):8===this._step?(0,n.qy)(V||(V=U`<ha-voice-assistant-setup-step-local
                                  .hass=${0}
                                  .language=${0}
                                  .localOption=${0}
                                  .assistConfiguration=${0}
                                ></ha-voice-assistant-setup-step-local>`),this.hass,this._language,this._localOption,this._assistConfiguration):6===this._step?(0,n.qy)(R||(R=U`<ha-voice-assistant-setup-step-success
                                    .hass=${0}
                                    .assistConfiguration=${0}
                                    .assistEntityId=${0}
                                    .deviceId=${0}
                                  ></ha-voice-assistant-setup-step-success>`),this.hass,this._assistConfiguration,i,this._params.deviceId):n.s6)}async _getLanguages(){if(this._languages.length)return;const t=await(0,p.e1)(this.hass);this._languages=Object.entries(t.languages).filter((([t,e])=>e.cloud>0||e.full_local>0||e.focused_local>0)).map((([t,e])=>t)),this._language=t.preferred_language&&this._languages.includes(t.preferred_language)?t.preferred_language:void 0}async _fetchAssistConfiguration(){try{this._assistConfiguration=await(0,u.Vy)(this.hass,this._findDomainEntityId(this._params.deviceId,this.hass.entities,"assist_satellite"))}catch(t){this._error=t.message}}_handlePickLanguage(t){"keydown"===t.type&&"Enter"!==t.key&&" "!==t.key||(this._language=t.target.value)}_languageChanged(t){t.detail.value&&(this._language=t.detail.value)}_goToPreviousStep(){this._previousSteps.length&&(this._step=this._previousSteps.pop())}_goToNextStep(t){var e,i,s,a;null!=t&&null!==(e=t.detail)&&void 0!==e&&e.updateConfig&&this._fetchAssistConfiguration(),null!=t&&null!==(i=t.detail)&&void 0!==i&&i.nextStep&&(this._nextStep=t.detail.nextStep),null!=t&&null!==(s=t.detail)&&void 0!==s&&s.noPrevious||this._previousSteps.push(this._step),null!=t&&null!==(a=t.detail)&&void 0!==a&&a.step?(this._step=t.detail.step,8===t.detail.step&&(this._localOption=t.detail.option)):this._nextStep?(this._step=this._nextStep,this._nextStep=void 0):this._step+=1}static get styles(){return[g.nA,(0,n.AH)(D||(D=U`
        ha-dialog {
          --dialog-content-padding: 0;
        }
        @media all and (min-width: 450px) and (min-height: 500px) {
          ha-dialog {
            --mdc-dialog-min-width: 560px;
            --mdc-dialog-max-width: 560px;
            --mdc-dialog-min-width: min(560px, 95vw);
            --mdc-dialog-max-width: min(560px, 95vw);
          }
        }
        ha-dialog-header {
          height: 56px;
        }
        @media all and (max-width: 450px), all and (max-height: 500px) {
          .content {
            height: calc(100vh - 56px);
          }
        }
        .skip-btn {
          margin-top: 6px;
        }
        ha-alert {
          margin: 24px;
          display: block;
        }
        ha-md-button-menu {
          height: 48px;
          display: flex;
          align-items: center;
          margin-right: 12px;
          margin-inline-end: 12px;
          margin-inline-start: initial;
        }
      `))]}constructor(...t){super(...t),this._step=0,this._languages=[],this._previousSteps=[],this._deviceEntities=(0,r.A)(((t,e)=>Object.values(e).filter((e=>e.device_id===t)))),this._findDomainEntityId=(0,r.A)(((t,e,i)=>{var s;return null===(s=this._deviceEntities(t,e).find((t=>(0,c.m)(t.entity_id)===i)))||void 0===s?void 0:s.entity_id}))}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],G.prototype,"hass",void 0),(0,a.__decorate)([(0,o.wk)()],G.prototype,"_params",void 0),(0,a.__decorate)([(0,o.wk)()],G.prototype,"_step",void 0),(0,a.__decorate)([(0,o.wk)()],G.prototype,"_assistConfiguration",void 0),(0,a.__decorate)([(0,o.wk)()],G.prototype,"_error",void 0),(0,a.__decorate)([(0,o.wk)()],G.prototype,"_language",void 0),(0,a.__decorate)([(0,o.wk)()],G.prototype,"_languages",void 0),(0,a.__decorate)([(0,o.wk)()],G.prototype,"_localOption",void 0),G=(0,a.__decorate)([(0,o.EM)("ha-voice-assistant-setup-dialog")],G),s()}catch(M){s(M)}}))},69216:function(t,e,i){i.a(t,(async function(t,e){try{i(5934);var s=i(69868),a=i(84922),n=i(11991),o=i(73120),r=i(44249),l=i(56083),c=i(47420),d=i(7762),h=t([r]);r=(h.then?(await h)():h)[0];let u,p,_=t=>t;class g extends a.WF{render(){const t=this.hass.devices[this.deviceId];return(0,a.qy)(u||(u=_`<div class="content">
        <img
          src="/static/images/voice-assistant/area.png"
          alt="Casita Home Assistant logo"
        />
        <h1>
          ${0}
        </h1>
        <p class="secondary">
          ${0}
        </p>
        <ha-area-picker
          .hass=${0}
          .value=${0}
        ></ha-area-picker>
      </div>
      <div class="footer">
        <ha-button @click=${0}
          >${0}</ha-button
        >
      </div>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.area.title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.area.secondary"),this.hass,t.area_id,this._setArea,this.hass.localize("ui.common.next"))}async _setArea(){const t=this.shadowRoot.querySelector("ha-area-picker").value;t?(await(0,l.FB)(this.hass,this.deviceId,{area_id:t}),this._nextStep()):(0,c.K$)(this,{text:this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.area.no_selection")})}_nextStep(){(0,o.r)(this,"next-step")}}g.styles=[d.s,(0,a.AH)(p||(p=_`
      ha-area-picker {
        display: block;
        width: 100%;
        margin-bottom: 24px;
        text-align: initial;
      }
    `))],(0,s.__decorate)([(0,n.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],g.prototype,"deviceId",void 0),g=(0,s.__decorate)([(0,n.EM)("ha-voice-assistant-setup-step-area")],g),e()}catch(u){e(u)}}))},36731:function(t,e,i){i.a(t,(async function(t,e){try{i(65315),i(37089),i(5934);var s=i(69868),a=i(84922),n=i(11991),o=i(73120),r=(i(5803),i(98343),i(39856)),l=i(7762),c=i(97938),d=t([c]);c=(d.then?(await d)():d)[0];let h,u,p,_=t=>t;class g extends a.WF{render(){return(0,a.qy)(h||(h=_`<div class="padding content">
        <img
          src="/static/images/voice-assistant/change-wake-word.png"
          alt="Casita Home Assistant logo"
        />
        <h1>
          ${0}
        </h1>
        <p class="secondary">
          ${0}
        </p>
      </div>
      <ha-md-list>
        ${0}
      </ha-md-list>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.change_wake_word.title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.change_wake_word.secondary"),this.assistConfiguration.available_wake_words.map((t=>(0,a.qy)(u||(u=_`<ha-md-list-item
              interactive
              type="button"
              @click=${0}
              .value=${0}
            >
              ${0}
              <ha-icon-next slot="end"></ha-icon-next>
            </ha-md-list-item>`),this._wakeWordPicked,t.id,t.wake_word))))}async _wakeWordPicked(t){if(!this.assistEntityId)return;const e=t.currentTarget.value;await(0,r.g5)(this.hass,this.assistEntityId,[e]),this._nextStep()}_nextStep(){(0,o.r)(this,"next-step",{step:c.STEP.WAKEWORD,updateConfig:!0})}}g.styles=[l.s,(0,a.AH)(p||(p=_`
      :host {
        padding: 0;
      }
      .padding {
        padding: 24px;
      }
      ha-md-list {
        width: 100%;
        text-align: initial;
        margin-bottom: 24px;
      }
    `))],(0,s.__decorate)([(0,n.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],g.prototype,"assistConfiguration",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],g.prototype,"assistEntityId",void 0),g=(0,s.__decorate)([(0,n.EM)("ha-voice-assistant-setup-step-change-wake-word")],g),e()}catch(h){e(h)}}))},68409:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(5934),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=i(73120),r=i(76943),l=i(71622),c=i(39856),d=i(7762),h=i(86435),u=t([r,l]);[r,l]=u.then?(await u)():u;let p,_,g,v,f=t=>t;class y extends a.WF{willUpdate(t){var e;super.willUpdate(t),this.hasUpdated?"success"===this._status&&t.has("hass")&&"idle"===(null===(e=this.hass.states[this.assistEntityId])||void 0===e?void 0:e.state)&&this._nextStep():this._testConnection()}render(){return(0,a.qy)(p||(p=f`<div class="content">
      ${0}
    </div>`),"timeout"===this._status?(0,a.qy)(_||(_=f`<img
              src="/static/images/voice-assistant/error.png"
              alt="Casita Home Assistant error logo"
            />
            <h1>
              ${0}
            </h1>
            <p class="secondary">
              ${0}
            </p>
            <div class="footer">
              <ha-button
                appearance="plain"
                href=${0}
              >
                >${0}</ha-button
              >
              <ha-button @click=${0}
                >${0}</ha-button
              >
            </div>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.check.failed_title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.check.failed_secondary"),(0,h.o)(this.hass,"/voice_control/troubleshooting/#i-dont-get-a-voice-response"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.check.help"),this._testConnection,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.check.retry")):(0,a.qy)(g||(g=f`<img
              src="/static/images/voice-assistant/hi.png"
              alt="Casita Home Assistant hi logo"
            />
            <h1>
              ${0}
            </h1>
            <p class="secondary">
              ${0}
            </p>

            ${0}`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.check.title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.check.secondary"),this._showLoader?(0,a.qy)(v||(v=f`<ha-spinner></ha-spinner>`)):a.s6))}async _testConnection(){this._status=void 0,this._showLoader=!1;const t=setTimeout((()=>{this._showLoader=!0}),3e3),e=await(0,c.tl)(this.hass,this.assistEntityId);clearTimeout(t),this._showLoader=!1,this._status=e.status}_nextStep(){(0,o.r)(this,"next-step",{noPrevious:!0})}constructor(...t){super(...t),this._showLoader=!1}}y.styles=d.s,(0,s.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"assistEntityId",void 0),(0,s.__decorate)([(0,n.wk)()],y.prototype,"_status",void 0),(0,s.__decorate)([(0,n.wk)()],y.prototype,"_showLoader",void 0),y=(0,s.__decorate)([(0,n.EM)("ha-voice-assistant-setup-step-check")],y),e()}catch(p){e(p)}}))},86088:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=i(50719),r=i(66999),l=i(98769),c=i(73120),d=i(97938),h=t([o,r,l,d]);[o,r,l,d]=h.then?(await h)():h;let u,p,_,g=t=>t;class v extends a.WF{render(){return"SIGNUP"===this._state?(0,a.qy)(u||(u=g`<cloud-step-signup
        .hass=${0}
        @cloud-step=${0}
      ></cloud-step-signup>`),this.hass,this._cloudStep):"SIGNIN"===this._state?(0,a.qy)(p||(p=g`<cloud-step-signin
        .hass=${0}
        @cloud-step=${0}
      ></cloud-step-signin>`),this.hass,this._cloudStep):(0,a.qy)(_||(_=g`<cloud-step-intro
      .hass=${0}
      @cloud-step=${0}
    ></cloud-step-intro>`),this.hass,this._cloudStep)}_cloudStep(t){"DONE"!==t.detail.step?this._state=t.detail.step:(0,c.r)(this,"next-step",{step:d.STEP.PIPELINE,noPrevious:!0})}constructor(...t){super(...t),this._state="INTRO"}}(0,s.__decorate)([(0,n.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,s.__decorate)([(0,n.wk)()],v.prototype,"_state",void 0),v=(0,s.__decorate)([(0,n.EM)("ha-voice-assistant-setup-step-cloud")],v),e()}catch(u){e(u)}}))},23362:function(t,e,i){i.a(t,(async function(t,e){try{i(46852),i(79827),i(35748),i(35058),i(65315),i(837),i(84136),i(37089),i(59023),i(5934),i(18223),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=i(10763),r=i(73120),l=i(92830),c=i(71622),d=i(85023),h=i(582),u=i(2834),p=i(20606),_=i(32512),g=i(87608),v=i(45829),f=i(86435),y=i(7762),m=i(97938),w=i(88702),b=t([c,m]);[c,m]=b.then?(await b)():b;let $,k,x,C,z,M=t=>t;const S="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z";class E extends a.WF{render(){return(0,a.qy)($||($=M`<div class="content">
      ${0}
    </div>`),"INSTALLING"===this._state?(0,a.qy)(k||(k=M`<img
              src="/static/images/voice-assistant/update.png"
              alt="Casita Home Assistant loading logo"
            />
            <h1>
              ${0}
            </h1>
            <p>
              ${0}
            </p>
            <ha-spinner></ha-spinner>
            <p>
              ${0}
            </p>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.secondary"),this._detailState||"Installation can take several minutes"):"ERROR"===this._state?(0,a.qy)(x||(x=M`<img
                src="/static/images/voice-assistant/error.png"
                alt="Casita Home Assistant error logo"
              />
              <h1>
                ${0}
              </h1>
              <p>${0}</p>
              <p>
                ${0}
              </p>
              <ha-button
                appearance="plain"
                size="small"
                @click=${0}
                >${0}</ha-button
              >
              <ha-button
                href=${0}
                target="_blank"
                rel="noreferrer noopener"
                size="small"
                appearance="plain"
              >
                <ha-svg-icon .path=${0} slot="start"></ha-svg-icon>
                ${0}</ha-button
              >`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.failed_title"),this._error,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.failed_secondary"),this._prevStep,this.hass.localize("ui.common.back"),(0,f.o)(this.hass,"/voice_control/voice_remote_local_assistant/"),S,this.hass.localize("ui.panel.config.common.learn_more")):"NOT_SUPPORTED"===this._state?(0,a.qy)(C||(C=M`<img
                  src="/static/images/voice-assistant/error.png"
                  alt="Casita Home Assistant error logo"
                />
                <h1>
                  ${0}
                </h1>
                <p>
                  ${0}
                </p>
                <ha-button
                  appearance="plain"
                  size="small"
                  @click=${0}
                  >${0}</ha-button
                >
                <ha-button
                  href=${0}
                  target="_blank"
                  rel="noreferrer noopener"
                  appearance="plain"
                  size="small"
                >
                  <ha-svg-icon .path=${0} slot="start"></ha-svg-icon>
                  ${0}</ha-button
                >`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.not_supported_title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.not_supported_secondary"),this._prevStep,this.hass.localize("ui.common.back"),(0,f.o)(this.hass,"/voice_control/voice_remote_local_assistant/"),S,this.hass.localize("ui.panel.config.common.learn_more")):a.s6)}willUpdate(t){super.willUpdate(t),this.hasUpdated||this._checkLocal()}_prevStep(){(0,r.r)(this,"prev-step")}_nextStep(){(0,r.r)(this,"next-step",{step:m.STEP.SUCCESS,noPrevious:!0})}async _checkLocal(){if(await this._findLocalEntities(),this._localTts&&this._localStt)try{if(this._localTts.length&&this._localStt.length)return void(await this._pickOrCreatePipelineExists());if(!(0,o.x)(this.hass,"hassio"))return void(this._state="NOT_SUPPORTED");this._state="INSTALLING";const{addons:t}=await(0,p.b3)(this.hass),e=t.find((t=>t.slug===this._ttsAddonName)),i=t.find((t=>t.slug===this._sttAddonName));this._localTts.length||(e||(this._detailState=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.state.installing_${this._ttsProviderName}`),await(0,p.xG)(this.hass,this._ttsAddonName)),e&&"started"===e.state||(this._detailState=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.state.starting_${this._ttsProviderName}`),await(0,p.eK)(this.hass,this._ttsAddonName)),this._detailState=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.state.setup_${this._ttsProviderName}`),await this._setupConfigEntry("tts")),this._localStt.length||(i||(this._detailState=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.state.installing_${this._sttProviderName}`),await(0,p.xG)(this.hass,this._sttAddonName)),i&&"started"===i.state||(this._detailState=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.state.starting_${this._sttProviderName}`),await(0,p.eK)(this.hass,this._sttAddonName)),this._detailState=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.state.setup_${this._sttProviderName}`),await this._setupConfigEntry("stt")),this._detailState=this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.state.creating_pipeline"),await this._findEntitiesAndCreatePipeline()}catch(t){this._state="ERROR",this._error=t.message}}get _sttProviderName(){return"focused_local"===this.localOption?"speech-to-phrase":"faster-whisper"}get _sttAddonName(){return"focused_local"===this.localOption?"core_speech-to-phrase":"core_whisper"}get _sttHostName(){return"focused_local"===this.localOption?"core-speech-to-phrase":"core-whisper"}async _findLocalEntities(){const t=Object.values(this.hass.entities).filter((t=>"wyoming"===t.platform));if(!t.length)return this._localStt=[],void(this._localTts=[]);const e=await(0,v.d)(this.hass),i=Object.values(await(0,u.G3)(this.hass,t.map((t=>t.entity_id))));this._localTts=i.filter((t=>{var i;return"tts"===(0,l.m)(t.entity_id)&&t.config_entry_id&&(null===(i=e.info[t.config_entry_id])||void 0===i?void 0:i.tts.some((t=>t.name===this._ttsProviderName)))})),this._localStt=i.filter((t=>{var i;return"stt"===(0,l.m)(t.entity_id)&&t.config_entry_id&&(null===(i=e.info[t.config_entry_id])||void 0===i?void 0:i.asr.some((t=>t.name===this._sttProviderName)))}))}async _setupConfigEntry(t){const e=await this._findConfigFlowInProgress(t);if(e){if("create_entry"===(await(0,h.jm)(this.hass,e.flow_id,{})).type)return}return this._createConfigEntry(t)}async _findConfigFlowInProgress(t){return(await(0,h.t2)(this.hass.connection)).find((e=>"wyoming"===e.handler&&"hassio"===e.context.source&&(e.context.configuration_url&&e.context.configuration_url.includes("tts"===t?this._ttsAddonName:this._sttAddonName)||e.context.title_placeholders.name&&e.context.title_placeholders.name.toLowerCase().includes("tts"===t?this._ttsProviderName:this._sttProviderName))))}async _createConfigEntry(t){const e=await(0,h.t1)(this.hass,"wyoming"),i=await(0,h.jm)(this.hass,e.flow_id,{host:"tts"===t?this._ttsHostName:this._sttHostName,port:"tts"===t?this._ttsPort:this._sttPort});if("create_entry"!==i.type)throw new Error(`${this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.errors.failed_create_entry",{addon:"tts"===t?this._ttsProviderName:this._sttProviderName})}${"errors"in i?`: ${i.errors.base}`:""}`)}async _pickOrCreatePipelineExists(){var t,e,i;if(null===(t=this._localStt)||void 0===t||!t.length||null===(e=this._localTts)||void 0===e||!e.length)return;const s=await(0,d.nx)(this.hass);s.preferred_pipeline&&s.pipelines.sort((t=>t.id===s.preferred_pipeline?-1:0));const a=this._localTts.map((t=>t.entity_id)),n=this._localStt.map((t=>t.entity_id));let o=s.pipelines.find((t=>"conversation.home_assistant"===t.conversation_engine&&t.tts_engine&&a.includes(t.tts_engine)&&t.stt_engine&&n.includes(t.stt_engine)&&t.language.split("-")[0]===this.language.split("-")[0]));o||(o=await this._createPipeline(this._localTts[0].entity_id,this._localStt[0].entity_id)),await this.hass.callService("select","select_option",{option:o.name},{entity_id:null===(i=this.assistConfiguration)||void 0===i?void 0:i.pipeline_entity_id}),this._nextStep()}async _createPipeline(t,e){var i,s,a;const n=await(0,d.nx)(this.hass),o=(await(0,w.vc)(this.hass,this.language||this.hass.config.language,this.hass.config.country||void 0)).agents.find((t=>"conversation.home_assistant"===t.id));if(null==o||!o.supported_languages.length)throw new Error("Conversation agent does not support requested language.");const r=(await(0,g.Xv)(this.hass,this.language,this.hass.config.country||void 0)).providers.find((e=>e.engine_id===t));if(null==r||null===(i=r.supported_languages)||void 0===i||!i.length)throw new Error("TTS engine does not support requested language.");const l=await(0,g.z3)(this.hass,t,r.supported_languages[0]);if(null===(s=l.voices)||void 0===s||!s.length)throw new Error("No voice available for requested language.");const c=(await(0,_.T)(this.hass,this.language,this.hass.config.country||void 0)).providers.find((t=>t.engine_id===e));if(null==c||null===(a=c.supported_languages)||void 0===a||!a.length)throw new Error("STT engine does not support requested language.");let h=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.${this.localOption}_pipeline`),u=1;for(;n.pipelines.find((t=>t.name===h));)h=`${this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.${this.localOption}_pipeline`)} ${u}`,u++;return(0,d.u6)(this.hass,{name:h,language:this.language.split("-")[0],conversation_engine:"conversation.home_assistant",conversation_language:o.supported_languages[0],stt_engine:e,stt_language:c.supported_languages[0],tts_engine:t,tts_language:r.supported_languages[0],tts_voice:l.voices[0].voice_id,wake_word_entity:null,wake_word_id:null})}async _findEntitiesAndCreatePipeline(t=0){var e,i,s;if(await this._findLocalEntities(),null===(e=this._localTts)||void 0===e||!e.length||null===(i=this._localStt)||void 0===i||!i.length){if(t>3)throw new Error(this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.errors.could_not_find_entities"));return await new Promise((t=>{setTimeout(t,2e3)})),this._findEntitiesAndCreatePipeline(t+1)}const a=await this._createPipeline(this._localTts[0].entity_id,this._localStt[0].entity_id);await this.hass.callService("select","select_option",{option:a.name},{entity_id:null===(s=this.assistConfiguration)||void 0===s?void 0:s.pipeline_entity_id}),this._nextStep()}constructor(...t){super(...t),this._state="INTRO",this._ttsProviderName="piper",this._ttsAddonName="core_piper",this._ttsHostName="core-piper",this._ttsPort=10200,this._sttPort=10300}}E.styles=[y.s,(0,a.AH)(z||(z=M`
      ha-spinner {
        margin-top: 24px;
        margin-bottom: 24px;
      }
    `))],(0,s.__decorate)([(0,n.MZ)({attribute:!1})],E.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],E.prototype,"assistConfiguration",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],E.prototype,"localOption",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],E.prototype,"language",void 0),(0,s.__decorate)([(0,n.wk)()],E.prototype,"_state",void 0),(0,s.__decorate)([(0,n.wk)()],E.prototype,"_detailState",void 0),(0,s.__decorate)([(0,n.wk)()],E.prototype,"_error",void 0),(0,s.__decorate)([(0,n.wk)()],E.prototype,"_localTts",void 0),(0,s.__decorate)([(0,n.wk)()],E.prototype,"_localStt",void 0),E=(0,s.__decorate)([(0,n.EM)("ha-voice-assistant-setup-step-local")],E),e()}catch($){e($)}}))},70647:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(99342),i(35058),i(65315),i(84136),i(5934),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=i(65940),r=i(10763),l=i(73120),c=i(92830),d=i(13125),h=(i(58895),i(85023)),u=i(70040),p=i(88702),_=i(32512),g=i(87608),v=i(7762),f=i(97938),y=i(86435),m=t([d,f]);[d,f]=m.then?(await m)():m;let w,b,$,k,x=t=>t;const C=["cloud","focused_local","full_local"],z={cloud:0,focused_local:0,full_local:0};class M extends a.WF{willUpdate(t){if(super.willUpdate(t),this.hasUpdated||this._fetchData(),(t.has("language")||t.has("_languageScores"))&&this.language&&this._languageScores){var e;const t=this.language;var i;if(this._value&&0===(null===(e=this._languageScores[t])||void 0===e?void 0:e[this._value])&&(this._value=void 0),!this._value)this._value=null===(i=this._getOptions(this._languageScores[t]||z,this.hass.localize).supportedOptions[0])||void 0===i?void 0:i.value}}render(){if(!this._cloudChecked||!this._languageScores)return a.s6;if(!this.language){const t=(0,d.T)(this.hass.config.language,this.hass.locale);return(0,a.qy)(w||(w=x`<div class="content">
        <h1>
          ${0}
        </h1>
        ${0}
        <ha-language-picker
          .hass=${0}
          .label=${0}
          .languages=${0}
          @value-changed=${0}
        ></ha-language-picker>

        <a
          href=${0}
          >${0}</a
        >
      </div>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.unsupported_language.header"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.unsupported_language.secondary",{language:t}),this.hass,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.unsupported_language.language_picker"),this.languages,this._languageChanged,(0,y.o)(this.hass,"/voice_control/contribute-voice/"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.unsupported_language.contribute",{language:t}))}const t=this._languageScores[this.language]||z,e=this._getOptions(t,this.hass.localize),i=this._value?"full_local"===this._value?"low":"high":"",s=this._value?t[this._value]>2?"high":t[this._value]>1?"ready":t[this._value]>0?"low":"":"";return(0,a.qy)(b||(b=x`<div class="content">
        <h1>
          ${0}
        </h1>
        <div class="bar-header">
          <span
            >${0}</span
          ><span
            >${0}</span
          >
        </div>
        <div class="perf-bar ${0}">
          <div class="segment"></div>
          <div class="segment"></div>
          <div class="segment"></div>
        </div>
        <div class="bar-header">
          <span
            >${0}</span
          ><span
            >${0}</span
          >
        </div>
        <div class="perf-bar ${0}">
          <div class="segment"></div>
          <div class="segment"></div>
          <div class="segment"></div>
        </div>
        <ha-select-box
          max_columns="1"
          .options=${0}
          .value=${0}
          @value-changed=${0}
        ></ha-select-box>
        ${0}
      </div>
      <div class="footer">
        <ha-button @click=${0} .disabled=${0}
          >${0}</ha-button
        >
      </div>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.performance.header"),i?this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.pipeline.performance.${i}`):"",i,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.commands.header"),s?this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.pipeline.commands.${s}`):"",s,e.supportedOptions,this._value,this._valueChanged,e.unsupportedOptions.length?(0,a.qy)($||($=x`<h3>
                ${0}
              </h3>
              <ha-select-box
                max_columns="1"
                .options=${0}
                disabled
              ></ha-select-box>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.unsupported"),e.unsupportedOptions):a.s6,this._createPipeline,!this._value,this.hass.localize("ui.common.next"))}async _fetchData(){await this._hasCloud()&&await this._createCloudPipeline(!1)||(this._cloudChecked=!0,this._languageScores=(await(0,p.e1)(this.hass)).languages)}async _hasCloud(){if(!(0,r.x)(this.hass,"cloud"))return!1;const t=await(0,u.eN)(this.hass);return!(!t.logged_in||!t.active_subscription)}async _createCloudPipeline(t){let e,i;for(const r of Object.values(this.hass.entities))if("cloud"===r.platform){const t=(0,c.m)(r.entity_id);if("tts"===t)e=r.entity_id;else{if("stt"!==t)continue;i=r.entity_id}if(e&&i)break}try{var s;const o=await(0,h.nx)(this.hass);o.preferred_pipeline&&o.pipelines.sort((t=>t.id===o.preferred_pipeline?-1:0));let r=o.pipelines.find((s=>"conversation.home_assistant"===s.conversation_engine&&s.tts_engine===e&&s.stt_engine===i&&(!t||s.language.split("-")[0]===this.language.split("-")[0])));if(!r){var a,n;const t=(await(0,p.vc)(this.hass,this.language||this.hass.config.language,this.hass.config.country||void 0)).agents.find((t=>"conversation.home_assistant"===t.id));if(null==t||!t.supported_languages.length)return!1;const s=(await(0,g.Xv)(this.hass,this.language||this.hass.config.language,this.hass.config.country||void 0)).providers.find((t=>t.engine_id===e));if(null==s||null===(a=s.supported_languages)||void 0===a||!a.length)return!1;const l=await(0,g.z3)(this.hass,e,s.supported_languages[0]),c=(await(0,_.T)(this.hass,this.language||this.hass.config.language,this.hass.config.country||void 0)).providers.find((t=>t.engine_id===i));if(null==c||null===(n=c.supported_languages)||void 0===n||!n.length)return!1;let d="Home Assistant Cloud",u=1;for(;o.pipelines.find((t=>t.name===d));)d=`Home Assistant Cloud ${u}`,u++;r=await(0,h.u6)(this.hass,{name:d,language:(this.language||this.hass.config.language).split("-")[0],conversation_engine:"conversation.home_assistant",conversation_language:t.supported_languages[0],stt_engine:i,stt_language:c.supported_languages[0],tts_engine:e,tts_language:s.supported_languages[0],tts_voice:l.voices[0].voice_id,wake_word_entity:null,wake_word_id:null})}return await this.hass.callService("select","select_option",{option:r.name},{entity_id:null===(s=this.assistConfiguration)||void 0===s?void 0:s.pipeline_entity_id}),(0,l.r)(this,"next-step",{step:f.STEP.SUCCESS,noPrevious:!0}),!0}catch(o){return!1}}_valueChanged(t){this._value=t.detail.value}async _setupCloud(){await this._hasCloud()?this._createCloudPipeline(!0):(0,l.r)(this,"next-step",{step:f.STEP.CLOUD})}_createPipeline(){"cloud"===this._value?this._setupCloud():"focused_local"===this._value?this._setupLocalFocused():this._setupLocalFull()}_setupLocalFocused(){(0,l.r)(this,"next-step",{step:f.STEP.LOCAL,option:this._value})}_setupLocalFull(){(0,l.r)(this,"next-step",{step:f.STEP.LOCAL,option:this._value})}_languageChanged(t){t.detail.value&&(0,l.r)(this,"language-changed",{value:t.detail.value})}constructor(...t){super(...t),this.languages=[],this._cloudChecked=!1,this._getOptions=(0,o.A)(((t,e)=>{const i=[],s=[];return C.forEach((a=>{t[a]>0?i.push({label:e(`ui.panel.config.voice_assistants.satellite_wizard.pipeline.options.${a}.label`),description:e(`ui.panel.config.voice_assistants.satellite_wizard.pipeline.options.${a}.description`),value:a}):s.push({label:e(`ui.panel.config.voice_assistants.satellite_wizard.pipeline.options.${a}.label`),value:a})})),{supportedOptions:i,unsupportedOptions:s}}))}}M.styles=[v.s,(0,a.AH)(k||(k=x`
      :host {
        text-align: left;
      }
      .perf-bar {
        width: 100%;
        height: 10px;
        display: flex;
        gap: 4px;
        margin: 8px 0;
      }
      .segment {
        flex-grow: 1;
        background-color: var(--disabled-color);
        transition: background-color 0.3s;
      }
      .segment:first-child {
        border-radius: 4px 0 0 4px;
      }
      .segment:last-child {
        border-radius: 0 4px 4px 0;
      }
      .perf-bar.high .segment {
        background-color: var(--success-color);
      }
      .perf-bar.ready .segment:nth-child(-n + 2) {
        background-color: var(--warning-color);
      }
      .perf-bar.low .segment:nth-child(1) {
        background-color: var(--error-color);
      }
      .bar-header {
        display: flex;
        justify-content: space-between;
        margin: 8px 0;
        margin-top: 16px;
      }
      ha-select-box {
        display: block;
      }
      ha-select-box:first-of-type {
        margin-top: 32px;
      }
      .footer {
        margin-top: 16px;
      }
      ha-language-picker {
        display: block;
        margin-top: 16px;
        margin-bottom: 16px;
      }
    `))],(0,s.__decorate)([(0,n.MZ)({attribute:!1})],M.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],M.prototype,"assistConfiguration",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],M.prototype,"deviceId",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],M.prototype,"assistEntityId",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],M.prototype,"language",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],M.prototype,"languages",void 0),(0,s.__decorate)([(0,n.wk)()],M.prototype,"_cloudChecked",void 0),(0,s.__decorate)([(0,n.wk)()],M.prototype,"_value",void 0),(0,s.__decorate)([(0,n.wk)()],M.prototype,"_languageScores",void 0),M=(0,s.__decorate)([(0,n.EM)("ha-voice-assistant-setup-step-pipeline")],M),e()}catch(w){e(w)}}))},23866:function(t,e,i){i.a(t,(async function(t,e){try{i(79827),i(35748),i(65315),i(84136),i(37089),i(12977),i(5934),i(18223),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=i(73120),r=i(20674),l=i(44537),c=(i(25223),i(37207),i(52428),i(85023)),d=i(39856),h=i(70040),u=i(56083),p=i(16537),_=i(68121),g=i(37774),v=i(59826),f=i(7762),y=i(97938),m=t([g,y]);[g,y]=m.then?(await m)():m;let w,b,$,k,x,C,z,M,S=t=>t;const E="M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z",A="M12,2A3,3 0 0,1 15,5V11A3,3 0 0,1 12,14A3,3 0 0,1 9,11V5A3,3 0 0,1 12,2M19,11C19,14.53 16.39,17.44 13,17.93V21H11V17.93C7.61,17.44 5,14.53 5,11H7A5,5 0 0,0 12,16A5,5 0 0,0 17,11H19Z",O="M8,5.14V19.14L19,12.14L8,5.14Z";class P extends a.WF{willUpdate(t){if(super.willUpdate(t),t.has("assistConfiguration"))this._setTtsSettings();else if(t.has("hass")&&this.assistConfiguration){const e=t.get("hass");if(e){const t=e.states[this.assistConfiguration.pipeline_entity_id],i=this.hass.states[this.assistConfiguration.pipeline_entity_id];t.state!==i.state&&this._setTtsSettings()}}}render(){var t;const e=this.assistConfiguration?this.hass.states[this.assistConfiguration.pipeline_entity_id]:void 0,i=this.hass.devices[this.deviceId];return(0,a.qy)(w||(w=S`<div class="content">
        <img
          src="/static/images/voice-assistant/heart.png"
          alt="Casita Home Assistant logo"
        />
        <h1>
          ${0}
        </h1>
        <p class="secondary">
          ${0}
        </p>
        ${0}
        <div class="rows">
          <div class="row">
            <ha-textfield
              .label=${0}
              .placeholder=${0}
              .value=${0}
              @change=${0}
            ></ha-textfield>
          </div>
          ${0}
          ${0}
          ${0}
        </div>
      </div>
      <div class="footer">
        <ha-button @click=${0}
          >${0}</ha-button
        >
      </div>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.secondary"),this._error?(0,a.qy)(b||(b=S`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):a.s6,this.hass.localize("ui.panel.config.integrations.config_flow.device_name"),(0,l.T)(i,this.hass),null!==(t=this._deviceName)&&void 0!==t?t:(0,l.xn)(i),this._deviceNameChanged,this.assistConfiguration&&this.assistConfiguration.available_wake_words.length>1?(0,a.qy)($||($=S`<div class="row">
                <ha-select
                  .label=${0}
                  @closed=${0}
                  fixedMenuPosition
                  naturalMenuWidth
                  .value=${0}
                  @selected=${0}
                >
                  ${0}
                </ha-select>
                <ha-button
                  appearance="plain"
                  size="small"
                  @click=${0}
                >
                  <ha-svg-icon
                    slot="start"
                    .path=${0}
                  ></ha-svg-icon>
                  ${0}
                </ha-button>
              </div>`),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.form.wake_word_id"),r.d,this.assistConfiguration.active_wake_words[0],this._wakeWordPicked,this.assistConfiguration.available_wake_words.map((t=>(0,a.qy)(k||(k=S`<ha-list-item .value=${0}>
                        ${0}
                      </ha-list-item>`),t.id,t.wake_word))),this._testWakeWord,A,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.test_wakeword")):a.s6,e?(0,a.qy)(x||(x=S`<div class="row">
                <ha-select
                  .label=${0}
                  @closed=${0}
                  .value=${0}
                  fixedMenuPosition
                  naturalMenuWidth
                  @selected=${0}
                >
                  ${0}
                </ha-select>
                <ha-button
                  appearance="plain"
                  size="small"
                  @click=${0}
                >
                  <ha-svg-icon slot="start" .path=${0}></ha-svg-icon>
                  ${0}
                </ha-button>
              </div>`),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.devices.pipeline"),r.d,null==e?void 0:e.state,this._pipelinePicked,null==e?void 0:e.attributes.options.map((t=>(0,a.qy)(C||(C=S`<ha-list-item .value=${0}>
                        ${0}
                      </ha-list-item>`),t,this.hass.formatEntityState(e,t)))),this._openPipeline,E,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.edit_pipeline")):a.s6,this._ttsSettings?(0,a.qy)(z||(z=S`<div class="row">
                <ha-tts-voice-picker
                  .hass=${0}
                  .engineId=${0}
                  .language=${0}
                  .value=${0}
                  @value-changed=${0}
                  @closed=${0}
                ></ha-tts-voice-picker>
                <ha-button
                  appearance="plain"
                  size="small"
                  @click=${0}
                >
                  <ha-svg-icon slot="start" .path=${0}></ha-svg-icon>
                  ${0}
                </ha-button>
              </div>`),this.hass,this._ttsSettings.engine,this._ttsSettings.language,this._ttsSettings.voice,this._voicePicked,r.d,this._testTts,O,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.try_tts")):a.s6,this._done,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.done"))}async _getPipeline(){var t,e;if(null===(t=this.assistConfiguration)||void 0===t||!t.pipeline_entity_id)return[void 0,void 0];const i=this.hass.states[null===(e=this.assistConfiguration)||void 0===e?void 0:e.pipeline_entity_id].state,s=await(0,c.nx)(this.hass);let a;return a="preferred"===i?s.pipelines.find((t=>t.id===s.preferred_pipeline)):s.pipelines.find((t=>t.name===i)),[a,s.preferred_pipeline]}_deviceNameChanged(t){this._deviceName=t.target.value}async _wakeWordPicked(t){const e=t.target.value;await(0,d.g5)(this.hass,this.assistEntityId,[e])}_pipelinePicked(t){const e=this.hass.states[this.assistConfiguration.pipeline_entity_id],i=t.target.value;i!==e.state&&e.attributes.options.includes(i)&&(0,p.w)(this.hass,e.entity_id,i)}async _setTtsSettings(){const[t]=await this._getPipeline();this._ttsSettings=t?{engine:t.tts_engine,voice:t.tts_voice,language:t.tts_language}:void 0}async _voicePicked(t){const[e]=await this._getPipeline();e&&await(0,c.zn)(this.hass,e.id,Object.assign(Object.assign({},e),{},{tts_voice:t.detail.value}))}async _testTts(){const[t]=await this._getPipeline();if(t){if(t.language!==this.hass.locale.language)try{const e=await(0,v.sC)(null,t.language,!1);return void this._announce(e.data["ui.dialogs.tts-try.message_example"])}catch(e){}this._announce(this.hass.localize("ui.dialogs.tts-try.message_example"))}}async _announce(t){this.assistEntityId&&await(0,d.ew)(this.hass,this.assistEntityId,{message:t,preannounce:!1})}_testWakeWord(){(0,o.r)(this,"next-step",{step:y.STEP.WAKEWORD,nextStep:y.STEP.SUCCESS,updateConfig:!0})}async _openPipeline(){const[t]=await this._getPipeline();if(!t)return;const e=await(0,h.eN)(this.hass);(0,_.L)(this,{cloudActiveSubscription:e.logged_in&&e.active_subscription,pipeline:t,updatePipeline:async e=>{await(0,c.zn)(this.hass,t.id,e)},hideWakeWord:!0})}async _done(){if(this._deviceName)try{(0,u.FB)(this.hass,this.deviceId,{name_by_user:this._deviceName})}catch(t){return void(this._error=this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.failed_rename",{error:t.message||t}))}(0,o.r)(this,"closed")}}P.styles=[f.s,(0,a.AH)(M||(M=S`
      ha-md-list-item {
        text-align: initial;
      }
      ha-tts-voice-picker {
        display: block;
      }
      .footer {
        margin-top: 24px;
      }
      .rows {
        gap: 16px;
        display: flex;
        flex-direction: column;
      }
      .row {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .row > *:first-child {
        flex: 1;
        margin-right: 4px;
      }
      .row ha-button {
        width: 82px;
      }
    `))],(0,s.__decorate)([(0,n.MZ)({attribute:!1})],P.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],P.prototype,"assistConfiguration",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],P.prototype,"deviceId",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],P.prototype,"assistEntityId",void 0),(0,s.__decorate)([(0,n.wk)()],P.prototype,"_ttsSettings",void 0),(0,s.__decorate)([(0,n.wk)()],P.prototype,"_error",void 0),P=(0,s.__decorate)([(0,n.EM)("ha-voice-assistant-setup-step-success")],P),e()}catch(w){e(w)}}))},8088:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(5934),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=i(73120),r=i(80527),l=i(71622),c=i(6098),d=i(25256),h=i(7762),u=t([r,l,d]);[r,l,d]=u.then?(await u)():u;let p,_,g,v,f=t=>t;class y extends a.WF{willUpdate(t){if(super.willUpdate(t),this.updateEntityId){if(t.has("hass")&&this.updateEntityId){const e=t.get("hass");if(e){const t=e.states[this.updateEntityId],i=this.hass.states[this.updateEntityId];if((null==t?void 0:t.state)===c.Hh&&(null==i?void 0:i.state)!==c.Hh||(null==t?void 0:t.state)!==c.ON&&(null==i?void 0:i.state)===c.ON)return void this._tryUpdate(!1)}}t.has("updateEntityId")&&this._tryUpdate(!0)}else this._nextStep()}render(){if(!this.updateEntityId||!(this.updateEntityId in this.hass.states))return a.s6;const t=this.hass.states[this.updateEntityId],e=t&&(0,d.RJ)(t);return(0,a.qy)(p||(p=f`<div class="content">
      <img
        src="/static/images/voice-assistant/update.png"
        alt="Casita Home Assistant loading logo"
      />
      <h1>
        ${0}
      </h1>
      <p class="secondary">
        ${0}
      </p>
      ${0}
      <p>
        ${0}
      </p>
    </div>`),t&&("unavailable"===t.state||(0,d.Jy)(t))?this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.update.title"):this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.update.checking"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.update.secondary"),e?(0,a.qy)(_||(_=f`
            <ha-progress-ring
              .value=${0}
            ></ha-progress-ring>
          `),t.attributes.update_percentage):(0,a.qy)(g||(g=f`<ha-spinner></ha-spinner>`)),(null==t?void 0:t.state)===c.Hh?"Restarting voice assistant":e?`Installing ${t.attributes.update_percentage}%`:"")}async _tryUpdate(t){if(clearTimeout(this._refreshTimeout),!this.updateEntityId)return;const e=this.hass.states[this.updateEntityId];e&&this.hass.states[e.entity_id].state===c.ON&&(0,d.VK)(e)?(this._updated=!0,await this.hass.callService("update","install",{},{entity_id:e.entity_id})):t?(await this.hass.callService("homeassistant","update_entity",{},{entity_id:this.updateEntityId}),this._refreshTimeout=window.setTimeout((()=>{this._nextStep()}),1e4)):this._nextStep()}_nextStep(){(0,o.r)(this,"next-step",{noPrevious:!0,updateConfig:this._updated})}constructor(...t){super(...t),this._updated=!1}}y.styles=[h.s,(0,a.AH)(v||(v=f`
      ha-progress-ring,
      ha-spinner {
        margin-top: 24px;
        margin-bottom: 24px;
      }
    `))],(0,s.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"updateEntityId",void 0),y=(0,s.__decorate)([(0,n.EM)("ha-voice-assistant-setup-step-update")],y),e()}catch(p){e(p)}}))},65938:function(t,e,i){i.a(t,(async function(t,e){try{i(79827),i(35748),i(65315),i(84136),i(5934),i(18223),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=i(65940),r=i(73120),l=i(76943),c=i(71622),d=(i(96997),i(39856)),h=i(7762),u=i(97938),p=i(92830),_=t([l,c,u]);[l,c,u]=_.then?(await _)():_;let g,v,f,y,m,w,b,$=t=>t;class k extends a.WF{disconnectedCallback(){super.disconnectedCallback(),this._stopListeningWakeWord()}willUpdate(t){var e;(super.willUpdate(t),t.has("assistConfiguration")&&this.assistConfiguration&&!this.assistConfiguration.available_wake_words.length&&this._nextStep(),t.has("assistEntityId"))&&(this._detected=!1,this._muteSwitchEntity=null===(e=this.deviceEntities)||void 0===e||null===(e=e.find((t=>"switch"===(0,p.m)(t.entity_id)&&t.entity_id.includes("mute"))))||void 0===e?void 0:e.entity_id,this._muteSwitchEntity||this._startTimeOut(),this._listenWakeWord())}_startTimeOut(){this._timeout=window.setTimeout((()=>{this._timeout=void 0,this._timedout=!0}),15e3)}render(){if(!this.assistEntityId)return a.s6;return"idle"!==this.hass.states[this.assistEntityId].state?(0,a.qy)(g||(g=$`<ha-spinner></ha-spinner>`)):(0,a.qy)(v||(v=$`<div class="content">
        ${0}
        ${0}
      </div>
      ${0}`),this._detected?(0,a.qy)(y||(y=$`<img
                src="/static/images/voice-assistant/ok-nabu.png"
                alt="Casita Home Assistant logo"
              />
              <h1>
                ${0}
              </h1>
              <p class="secondary">
                ${0}
              </p>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.title_2",{wakeword:this._activeWakeWord(this.assistConfiguration)}),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.secondary_2")):(0,a.qy)(f||(f=$`
          <img src="/static/images/voice-assistant/sleep.png" alt="Casita Home Assistant logo"/>
          <h1>
          ${0}  
          </h1>
          <p class="secondary">${0}</p>
        </div>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.title",{wakeword:this._activeWakeWord(this.assistConfiguration)}),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.secondary")),this._timedout?(0,a.qy)(m||(m=$`<ha-alert alert-type="warning"
              >${0}</ha-alert
            >`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.time_out")):this._muteSwitchEntity&&"on"===this.hass.states[this._muteSwitchEntity].state?(0,a.qy)(w||(w=$`<ha-alert
                alert-type="warning"
                .title=${0}
                >${0}</ha-alert
              >`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.muted"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.muted_description")):a.s6,this.assistConfiguration&&this.assistConfiguration.available_wake_words.length>1?(0,a.qy)(b||(b=$`<div class="footer centered">
            <ha-button
              appearance="plain"
              size="small"
              @click=${0}
              >${0}</ha-button
            >
          </div>`),this._changeWakeWord,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.change_wake_word")):a.s6)}async _listenWakeWord(){const t=this.assistEntityId;t&&(await this._stopListeningWakeWord(),this._sub=(0,d.ds)(this.hass,t,(()=>{this._timedout=!1,clearTimeout(this._timeout),this._stopListeningWakeWord(),this._detected?this._nextStep():(this._detected=!0,this._listenWakeWord())})))}async _stopListeningWakeWord(){try{var t;null===(t=await this._sub)||void 0===t||t()}catch(e){}this._sub=void 0}_nextStep(){(0,r.r)(this,"next-step")}_changeWakeWord(){(0,r.r)(this,"next-step",{step:u.STEP.CHANGE_WAKEWORD})}constructor(...t){super(...t),this._detected=!1,this._timedout=!1,this._activeWakeWord=(0,o.A)((t=>{var e;if(!t)return"";const i=t.active_wake_words[0];return null===(e=t.available_wake_words.find((t=>t.id===i)))||void 0===e?void 0:e.wake_word}))}}k.styles=h.s,(0,s.__decorate)([(0,n.MZ)({attribute:!1})],k.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],k.prototype,"assistConfiguration",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],k.prototype,"assistEntityId",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],k.prototype,"deviceEntities",void 0),(0,s.__decorate)([(0,n.wk)()],k.prototype,"_muteSwitchEntity",void 0),(0,s.__decorate)([(0,n.wk)()],k.prototype,"_detected",void 0),(0,s.__decorate)([(0,n.wk)()],k.prototype,"_timedout",void 0),k=(0,s.__decorate)([(0,n.EM)("ha-voice-assistant-setup-step-wake-word")],k),e()}catch(g){e(g)}}))},78440:function(t,e,i){i.d(e,{o:function(){return a}});i(35748),i(12977),i(5934),i(95013);var s=i(73120);const a=(t,e)=>new Promise((a=>{const n=e.closeDialog,o=e.logInHereAction;(0,s.r)(t,"show-dialog",{dialogTag:"dialog-cloud-already-connected",dialogImport:()=>i.e("1285").then(i.bind(i,55332)),dialogParams:Object.assign(Object.assign({},e),{},{closeDialog:()=>{null==n||n(),a(!1)},logInHereAction:()=>{null==o||o(),a(!0)}})})}))},68121:function(t,e,i){i.d(e,{L:function(){return n}});i(35748),i(5934),i(95013);var s=i(73120);const a=()=>Promise.all([i.e("1544"),i.e("5831"),i.e("4848")]).then(i.bind(i,16403)),n=(t,e)=>{(0,s.r)(t,"show-dialog",{dialogTag:"dialog-voice-assistant-pipeline-detail",dialogImport:a,dialogParams:e})}},15092:function(t,e,i){i.d(e,{T:function(){return d}});i(79827),i(35748),i(12977),i(95013);var s=i(84922),a=i(78517),n=i(73120),o=i(55266),r=i(17229);class l extends HTMLElement{connectedCallback(){Object.assign(this.style,{position:"fixed",width:r.C?"100px":"50px",height:r.C?"100px":"50px",transform:"translate(-50%, -50%) scale(0)",pointerEvents:"none",zIndex:"999",background:"var(--primary-color)",display:null,opacity:"0.2",borderRadius:"50%",transition:"transform 180ms ease-in-out"}),["touchcancel","mouseout","mouseup","touchmove","mousewheel","wheel","scroll"].forEach((t=>{document.addEventListener(t,(()=>{this.cancelled=!0,this.timer&&(this._stopAnimation(),clearTimeout(this.timer),this.timer=void 0)}),{passive:!0})}))}bind(t,e={}){t.actionHandler&&(0,o.b)(e,t.actionHandler.options)||(t.actionHandler?(t.removeEventListener("touchstart",t.actionHandler.start),t.removeEventListener("touchend",t.actionHandler.end),t.removeEventListener("touchcancel",t.actionHandler.end),t.removeEventListener("mousedown",t.actionHandler.start),t.removeEventListener("click",t.actionHandler.end),t.removeEventListener("keydown",t.actionHandler.handleKeyDown)):t.addEventListener("contextmenu",(t=>{const e=t||window.event;return e.preventDefault&&e.preventDefault(),e.stopPropagation&&e.stopPropagation(),e.cancelBubble=!0,e.returnValue=!1,!1})),t.actionHandler={options:e},e.disabled||(t.actionHandler.start=t=>{let i,s;this.cancelled=!1,t.touches?(i=t.touches[0].clientX,s=t.touches[0].clientY):(i=t.clientX,s=t.clientY),e.hasHold&&(this.held=!1,this.timer=window.setTimeout((()=>{this._startAnimation(i,s),this.held=!0}),this.holdTime))},t.actionHandler.end=t=>{if("touchcancel"===t.type||"touchend"===t.type&&this.cancelled)return;const i=t.target;t.cancelable&&t.preventDefault(),e.hasHold&&(clearTimeout(this.timer),this._stopAnimation(),this.timer=void 0),e.hasHold&&this.held?(0,n.r)(i,"action",{action:"hold"}):e.hasDoubleClick?"click"===t.type&&t.detail<2||!this.dblClickTimeout?this.dblClickTimeout=window.setTimeout((()=>{this.dblClickTimeout=void 0,!1!==e.hasTap&&(0,n.r)(i,"action",{action:"tap"})}),250):(clearTimeout(this.dblClickTimeout),this.dblClickTimeout=void 0,(0,n.r)(i,"action",{action:"double_tap"})):!1!==e.hasTap&&(0,n.r)(i,"action",{action:"tap"})},t.actionHandler.handleKeyDown=t=>{["Enter"," "].includes(t.key)&&t.currentTarget.actionHandler.end(t)},t.addEventListener("touchstart",t.actionHandler.start,{passive:!0}),t.addEventListener("touchend",t.actionHandler.end),t.addEventListener("touchcancel",t.actionHandler.end),t.addEventListener("mousedown",t.actionHandler.start,{passive:!0}),t.addEventListener("click",t.actionHandler.end),t.addEventListener("keydown",t.actionHandler.handleKeyDown)))}_startAnimation(t,e){Object.assign(this.style,{left:`${t}px`,top:`${e}px`,transform:"translate(-50%, -50%) scale(1)"})}_stopAnimation(){Object.assign(this.style,{left:null,top:null,transform:"translate(-50%, -50%) scale(0)"})}constructor(...t){super(...t),this.holdTime=500,this.held=!1,this.cancelled=!1}}customElements.define("action-handler",l);const c=(t,e)=>{const i=(()=>{const t=document.body;if(t.querySelector("action-handler"))return t.querySelector("action-handler");const e=document.createElement("action-handler");return t.appendChild(e),e})();i&&i.bind(t,e)},d=(0,a.u$)(class extends a.WL{update(t,[e]){return c(t.element,e),s.c0}render(t){}})},69186:function(t,e,i){i.d(e,{$:function(){return p}});i(35748),i(65315),i(59023),i(5934),i(95013);var s=i(73120),a=i(68985),n=i(30209),o=i(28027),r=i(47420);const l=()=>i.e("5554").then(i.bind(i,17145));var c=i(72698),d=(i(79827),i(18223),i(29623)),h=i(92830);const u=(t,e)=>((t,e,i=!0)=>{const s=(0,h.m)(e),a="group"===s?"homeassistant":s;let n;switch(s){case"lock":n=i?"unlock":"lock";break;case"cover":n=i?"open_cover":"close_cover";break;case"button":case"input_button":n="press";break;case"scene":n="turn_on";break;case"valve":n=i?"open_valve":"close_valve";break;default:n=i?"turn_on":"turn_off"}return t.callService(a,n,{entity_id:e})})(t,e,d.jj.includes(t.states[e].state)),p=async(t,e,i,d)=>{let h;if("double_tap"===d&&i.double_tap_action?h=i.double_tap_action:"hold"===d&&i.hold_action?h=i.hold_action:"tap"===d&&i.tap_action&&(h=i.tap_action),h||(h={action:"more-info"}),h.confirmation&&(!h.confirmation.exemptions||!h.confirmation.exemptions.some((t=>{var i;return t.user===(null===(i=e.user)||void 0===i?void 0:i.id)})))){let i;if((0,n.j)("warning"),"call-service"===h.action||"perform-action"===h.action){const[t,s]=(h.perform_action||h.service).split(".",2),a=e.services;if(t in a&&s in a[t]){await e.loadBackendTranslation("title");const n=await e.loadBackendTranslation("services");i=`${(0,o.p$)(n,t)}: ${n(`component.${t}.services.${i}.name`)||a[t][s].name||s}`}}if(!(await(0,r.dk)(t,{text:h.confirmation.text||e.localize("ui.panel.lovelace.cards.actions.action_confirmation",{action:i||e.localize(`ui.panel.lovelace.editor.action-editor.actions.${h.action}`)||h.action})})))return}switch(h.action){case"more-info":{const a=h.entity||i.entity||i.camera_image||i.image_entity;a?(0,s.r)(t,"hass-more-info",{entityId:a}):((0,c.P)(t,{message:e.localize("ui.panel.lovelace.cards.actions.no_entity_more_info")}),(0,n.j)("failure"));break}case"navigate":h.navigation_path?(0,a.o)(h.navigation_path,{replace:h.navigation_replace}):((0,c.P)(t,{message:e.localize("ui.panel.lovelace.cards.actions.no_navigation_path")}),(0,n.j)("failure"));break;case"url":h.url_path?window.open(h.url_path):((0,c.P)(t,{message:e.localize("ui.panel.lovelace.cards.actions.no_url")}),(0,n.j)("failure"));break;case"toggle":i.entity?(u(e,i.entity),(0,n.j)("light")):((0,c.P)(t,{message:e.localize("ui.panel.lovelace.cards.actions.no_entity_toggle")}),(0,n.j)("failure"));break;case"perform-action":case"call-service":{var p;if(!h.perform_action&&!h.service)return(0,c.P)(t,{message:e.localize("ui.panel.lovelace.cards.actions.no_action")}),void(0,n.j)("failure");const[i,s]=(h.perform_action||h.service).split(".",2);e.callService(i,s,null!==(p=h.data)&&void 0!==p?p:h.service_data,h.target),(0,n.j)("light");break}case"assist":var _,g;((t,e,i)=>{var a,n,o;null!==(a=e.auth.external)&&void 0!==a&&a.config.hasAssist?e.auth.external.fireMessage({type:"assist/show",payload:{pipeline_id:i.pipeline_id,start_listening:null===(o=i.start_listening)||void 0===o||o}}):(0,s.r)(t,"show-dialog",{dialogTag:"ha-voice-command-dialog",dialogImport:l,dialogParams:{pipeline_id:i.pipeline_id,start_listening:null!==(n=i.start_listening)&&void 0!==n&&n}})})(t,e,{start_listening:null!==(_=h.start_listening)&&void 0!==_&&_,pipeline_id:null!==(g=h.pipeline_id)&&void 0!==g?g:"last_used"});break;case"fire-dom-event":(0,s.r)(t,"ll-custom",h)}}},67659:function(t,e,i){function s(t){return void 0!==t&&"none"!==t.action}function a(t){return!t.tap_action||s(t.tap_action)||s(t.hold_action)||s(t.double_tap_action)}i.d(e,{A:function(){return a},h:function(){return s}})},57543:function(t,e,i){i.d(e,{LX:function(){return o}});i(65315),i(59023),i(46852),i(37089),i(41602);function s(t,e){if(e.has("_config"))return!0;if(!e.has("hass"))return!1;const i=e.get("hass");return!i||(i.connected!==t.hass.connected||i.themes!==t.hass.themes||i.locale!==t.hass.locale||i.localize!==t.hass.localize||i.formatEntityState!==t.hass.formatEntityState||i.formatEntityAttributeName!==t.hass.formatEntityAttributeName||i.formatEntityAttributeValue!==t.hass.formatEntityAttributeValue||i.config.state!==t.hass.config.state)}function a(t,e,i){return t.states[i]!==e.states[i]}function n(t,e,i){const s=t.entities[i],a=e.entities[i];return(null==s?void 0:s.display_precision)!==(null==a?void 0:a.display_precision)}function o(t,e){if(s(t,e))return!0;if(!e.has("hass"))return!1;const i=e.get("hass"),o=t.hass;return a(i,o,t._config.entity)||n(i,o,t._config.entity)}},44954:function(t,e,i){i.a(t,(async function(t,e){try{i(79827),i(35748),i(18223),i(95013);var s=i(69868),a=i(84922),n=i(11991),o=i(75907),r=i(13802),l=i(29623),c=i(8540),d=i(92830),h=i(47379),u=i(23114),p=i(21873),_=i(15092),g=i(69186),v=i(67659),f=i(9303),y=i(20674),m=t([u,p]);[u,p]=m.then?(await m)():m;let w,b,$,k,x,C,z,M,S,E,A,O,P=t=>t;class L extends a.WF{render(){var t,e;if(!this.hass||!this.config)return a.s6;const i=this.config.entity?this.hass.states[this.config.entity]:void 0;if(!i)return(0,a.qy)(w||(w=P`
        <hui-warning .hass=${0}>
          ${0}
        </hui-warning>
      `),this.hass,(0,f.j)(this.hass,this.config.entity));const s=(0,d.m)(this.config.entity),n=(0,v.A)(this.config),c=this.secondaryText||this.config.secondary_info,u=null!==(t=this.config.name)&&void 0!==t?t:(0,h.u)(i);return(0,a.qy)(b||(b=P`
      <div
        class="row ${0}"
        @action=${0}
        .actionHandler=${0}
        tabindex=${0}
      >
        <state-badge
          .hass=${0}
          .stateObj=${0}
          .overrideIcon=${0}
          .overrideImage=${0}
          .stateColor=${0}
        ></state-badge>
        ${0}
        ${0}
      </div>
    `),(0,o.H)({pointer:n}),this._handleAction,(0,_.T)({hasHold:(0,v.h)(this.config.hold_action),hasDoubleClick:(0,v.h)(this.config.double_tap_action)}),(0,r.J)(!this.config.tap_action||(0,v.h)(this.config.tap_action)?"0":void 0),this.hass,i,this.config.icon,this.config.image,this.config.state_color,this.hideName?a.s6:(0,a.qy)($||($=P`<div
              class="info ${0}"
              .title=${0}
            >
              ${0}
              ${0}
            </div>`),(0,o.H)({"text-content":!c}),u,this.config.name||(0,h.u)(i),c?(0,a.qy)(k||(k=P`
                    <div class="secondary">
                      ${0}
                    </div>
                  `),this.secondaryText||("entity-id"===this.config.secondary_info?i.entity_id:"last-changed"===this.config.secondary_info?(0,a.qy)(x||(x=P`
                              <ha-relative-time
                                .hass=${0}
                                .datetime=${0}
                                capitalize
                              ></ha-relative-time>
                            `),this.hass,i.last_changed):"last-updated"===this.config.secondary_info?(0,a.qy)(C||(C=P`
                                <ha-relative-time
                                  .hass=${0}
                                  .datetime=${0}
                                  capitalize
                                ></ha-relative-time>
                              `),this.hass,i.last_updated):"last-triggered"===this.config.secondary_info?i.attributes.last_triggered?(0,a.qy)(z||(z=P`
                                    <ha-relative-time
                                      .hass=${0}
                                      .datetime=${0}
                                      capitalize
                                    ></ha-relative-time>
                                  `),this.hass,i.attributes.last_triggered):this.hass.localize("ui.panel.lovelace.cards.entities.never_triggered"):"position"===this.config.secondary_info&&void 0!==i.attributes.current_position?`${this.hass.localize("ui.card.cover.position")}: ${i.attributes.current_position}`:"tilt-position"===this.config.secondary_info&&void 0!==i.attributes.current_tilt_position?`${this.hass.localize("ui.card.cover.tilt_position")}: ${i.attributes.current_tilt_position}`:"brightness"===this.config.secondary_info&&i.attributes.brightness?(0,a.qy)(M||(M=P`${0}
                                      %`),Math.round(i.attributes.brightness/255*100)):"state"===this.config.secondary_info?(0,a.qy)(S||(S=P`${0}`),this.hass.formatEntityState(i)):a.s6)):a.s6),(null!==(e=this.catchInteraction)&&void 0!==e?e:!l.yd.includes(s))?(0,a.qy)(E||(E=P`
              <div class="text-content value">
                <div class="state"><slot></slot></div>
              </div>
            `)):(0,a.qy)(A||(A=P`<slot
              @touchcancel=${0}
              @touchend=${0}
              @keydown=${0}
              @click=${0}
              @action=${0}
            ></slot>`),y.d,y.d,y.d,y.d,y.d))}updated(t){var e;super.updated(t),(0,c.j)(this,"no-secondary",!(this.secondaryText||null!==(e=this.config)&&void 0!==e&&e.secondary_info))}_handleAction(t){(0,g.$)(this,this.hass,this.config,t.detail.action)}constructor(...t){super(...t),this.hideName=!1}}L.styles=(0,a.AH)(O||(O=P`
    :host {
      display: flex;
      align-items: center;
      flex-direction: row;
    }
    .row {
      display: flex;
      align-items: center;
      flex-direction: row;
      width: 100%;
      outline: none;
      transition: background-color 180ms ease-in-out;
    }
    .row:focus-visible {
      background-color: var(--primary-background-color);
    }
    .info {
      padding-left: 16px;
      padding-right: 8px;
      padding-inline-start: 16px;
      padding-inline-end: 8px;
      flex: 1 1 30%;
    }
    .info,
    .info > * {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .flex ::slotted(*) {
      margin-left: 8px;
      margin-inline-start: 8px;
      margin-inline-end: initial;
      min-width: 0;
    }
    .flex ::slotted([slot="secondary"]) {
      margin-left: 0;
      margin-inline-start: 0;
      margin-inline-end: initial;
    }
    .secondary,
    ha-relative-time {
      color: var(--secondary-text-color);
    }
    state-badge {
      flex: 0 0 40px;
    }
    .pointer {
      cursor: pointer;
    }
    .state {
      text-align: var(--float-end);
    }
    .value {
      direction: ltr;
    }
  `)),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],L.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],L.prototype,"config",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:"secondary-text"})],L.prototype,"secondaryText",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:"hide-name",type:Boolean})],L.prototype,"hideName",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:"catch-interaction",type:Boolean})],L.prototype,"catchInteraction",void 0),L=(0,s.__decorate)([(0,n.EM)("hui-generic-entity-row")],L),e()}catch(w){e(w)}}))},9303:function(t,e,i){i.d(e,{j:function(){return v}});var s=i(69868),a=i(17658),n=i(84922),o=i(11991);i(23749),i(35748),i(95013),i(86853),i(95635);let r,l,c,d,h=t=>t;const u={warning:"M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",error:"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z"};class p extends n.WF{getCardSize(){return 1}getGridOptions(){return{columns:6,rows:this.preview?"auto":1,min_rows:1,min_columns:6,fixed_rows:this.preview}}setConfig(t){this._config=t,this.severity=t.severity||"error"}render(){var t,e,i,s;const a=(null===(t=this._config)||void 0===t?void 0:t.error)||(null===(e=this.hass)||void 0===e?void 0:e.localize("ui.errors.config.configuration_error")),o=void 0===this.hass||(null===(i=this.hass)||void 0===i||null===(i=i.user)||void 0===i?void 0:i.is_admin)||this.preview,d=this.preview;return(0,n.qy)(r||(r=h`
      <ha-card class="${0} ${0}">
        <div class="header">
          <div class="icon">
            <slot name="icon">
              <ha-svg-icon .path=${0}></ha-svg-icon>
            </slot>
          </div>
          ${0}
        </div>
        ${0}
      </ha-card>
    `),this.severity,o?"":"no-title",u[this.severity],o?(0,n.qy)(l||(l=h`<div class="title"><slot>${0}</slot></div>`),a):n.s6,d&&null!==(s=this._config)&&void 0!==s&&s.message?(0,n.qy)(c||(c=h`<div class="message">${0}</div>`),this._config.message):n.s6)}constructor(...t){super(...t),this.preview=!1,this.severity="error"}}p.styles=(0,n.AH)(d||(d=h`
    ha-card {
      height: 100%;
      border-width: 0;
    }
    ha-card::after {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      opacity: 0.12;
      pointer-events: none;
      content: "";
      border-radius: var(--ha-card-border-radius, 12px);
    }
    .header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 16px;
    }
    .message {
      padding: 0 16px 16px 16px;
    }
    .no-title {
      justify-content: center;
    }
    .title {
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      font-weight: var(--ha-font-weight-bold);
    }
    ha-card.warning .icon {
      color: var(--warning-color);
    }
    ha-card.warning::after {
      background-color: var(--warning-color);
    }
    ha-card.error .icon {
      color: var(--error-color);
    }
    ha-card.error::after {
      background-color: var(--error-color);
    }
  `)),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],p.prototype,"preview",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"severity"})],p.prototype,"severity",void 0),(0,s.__decorate)([(0,o.wk)()],p.prototype,"_config",void 0),p=(0,s.__decorate)([(0,o.EM)("hui-error-card")],p);let _,g=t=>t;const v=(t,e)=>t.config.state!==a.m2?t.localize("ui.card.common.entity_not_found"):t.localize("ui.panel.lovelace.warning.starting");class f extends n.WF{render(){return(0,n.qy)(_||(_=g`<hui-error-card .hass=${0} severity="warning"
      ><slot></slot
    ></hui-error-card>`),this.hass)}}(0,s.__decorate)([(0,o.MZ)({attribute:!1})],f.prototype,"hass",void 0),f=(0,s.__decorate)([(0,o.EM)("hui-warning")],f)},37774:function(t,e,i){i.a(t,(async function(t,e){try{i(46852),i(79827),i(65315),i(37089),i(18223);var s=i(69868),a=i(84922),n=i(11991),o=i(20674),r=i(47379),l=(i(25223),i(37207),i(6098)),c=i(30209),d=i(16537),h=i(57543),u=i(44954),p=i(9303),_=t([u]);u=(_.then?(await _)():_)[0];let g,v,f,y,m=t=>t;class w extends a.WF{setConfig(t){if(!t||!t.entity)throw new Error("Entity must be specified");this._config=t}shouldUpdate(t){return(0,h.LX)(this,t)}render(){if(!this.hass||!this._config)return a.s6;const t=this.hass.states[this._config.entity];return t?(0,a.qy)(v||(v=m`
      <hui-generic-entity-row
        .hass=${0}
        .config=${0}
        hide-name
      >
        <ha-select
          .label=${0}
          .value=${0}
          .options=${0}
          .disabled=${0}
          naturalMenuWidth
          @action=${0}
          @click=${0}
          @closed=${0}
        >
          ${0}
        </ha-select>
      </hui-generic-entity-row>
    `),this.hass,this._config,this._config.name||(0,r.u)(t),t.state,t.attributes.options,t.state===l.Hh,this._handleAction,o.d,o.d,t.attributes.options?t.attributes.options.map((e=>(0,a.qy)(f||(f=m`
                  <ha-list-item .value=${0}>
                    ${0}
                  </ha-list-item>
                `),e,this.hass.formatEntityState(t,e)))):""):(0,a.qy)(g||(g=m`
        <hui-warning .hass=${0}>
          ${0}
        </hui-warning>
      `),this.hass,(0,p.j)(this.hass,this._config.entity))}_handleAction(t){const e=this.hass.states[this._config.entity],i=t.target.value;i!==e.state&&e.attributes.options.includes(i)&&((0,c.j)("light"),(0,d.w)(this.hass,e.entity_id,i))}}w.styles=(0,a.AH)(y||(y=m`
    hui-generic-entity-row {
      display: flex;
      align-items: center;
    }
    ha-select {
      width: 100%;
      --ha-select-min-width: 0;
    }
  `)),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],w.prototype,"hass",void 0),(0,s.__decorate)([(0,n.wk)()],w.prototype,"_config",void 0),w=(0,s.__decorate)([(0,n.EM)("hui-select-entity-row")],w),e()}catch(g){e(g)}}))},17229:function(t,e,i){i.d(e,{C:function(){return s}});const s="ontouchstart"in window||navigator.maxTouchPoints>0||navigator.msMaxTouchPoints>0},72698:function(t,e,i){i.d(e,{P:function(){return a}});var s=i(73120);const a=(t,e)=>(0,s.r)(t,"hass-notification",e)}}]);
//# sourceMappingURL=2719.a54eedc28c141af1.js.map