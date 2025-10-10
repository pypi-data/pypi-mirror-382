/*! For license information please see 3327.b9e71b842ca71dbf.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["3327"],{85055:function(e,t,i){i(35748),i(65315),i(37089),i(95013);var o=i(69868),a=i(84922),s=i(11991),r=i(7577),n=i(85759),l=i(73120),c=i(20674);i(25223),i(90666),i(37207);let d,h,p,u,_,v,y,m,g,b,$,f=e=>e;const k="M20.65,20.87L18.3,18.5L12,12.23L8.44,8.66L7,7.25L4.27,4.5L3,5.77L5.78,8.55C3.23,11.69 3.42,16.31 6.34,19.24C7.9,20.8 9.95,21.58 12,21.58C13.79,21.58 15.57,21 17.03,19.8L19.73,22.5L21,21.23L20.65,20.87M12,19.59C10.4,19.59 8.89,18.97 7.76,17.83C6.62,16.69 6,15.19 6,13.59C6,12.27 6.43,11 7.21,10L12,14.77V19.59M12,5.1V9.68L19.25,16.94C20.62,14 20.09,10.37 17.65,7.93L12,2.27L8.3,5.97L9.71,7.38L12,5.1Z",C="M17.5,12A1.5,1.5 0 0,1 16,10.5A1.5,1.5 0 0,1 17.5,9A1.5,1.5 0 0,1 19,10.5A1.5,1.5 0 0,1 17.5,12M14.5,8A1.5,1.5 0 0,1 13,6.5A1.5,1.5 0 0,1 14.5,5A1.5,1.5 0 0,1 16,6.5A1.5,1.5 0 0,1 14.5,8M9.5,8A1.5,1.5 0 0,1 8,6.5A1.5,1.5 0 0,1 9.5,5A1.5,1.5 0 0,1 11,6.5A1.5,1.5 0 0,1 9.5,8M6.5,12A1.5,1.5 0 0,1 5,10.5A1.5,1.5 0 0,1 6.5,9A1.5,1.5 0 0,1 8,10.5A1.5,1.5 0 0,1 6.5,12M12,3A9,9 0 0,0 3,12A9,9 0 0,0 12,21A1.5,1.5 0 0,0 13.5,19.5C13.5,19.11 13.35,18.76 13.11,18.5C12.88,18.23 12.73,17.88 12.73,17.5A1.5,1.5 0 0,1 14.23,16H16A5,5 0 0,0 21,11C21,6.58 16.97,3 12,3Z";class M extends a.WF{connectedCallback(){var e;super.connectedCallback(),null===(e=this._select)||void 0===e||e.layoutOptions()}_valueSelected(e){if(e.stopPropagation(),!this.isConnected)return;const t=e.target.value;this.value=t===this.defaultColor?void 0:t,(0,l.r)(this,"value-changed",{value:this.value})}render(){const e=this.value||this.defaultColor||"",t=!(n.l.has(e)||"none"===e||"state"===e);return(0,a.qy)(d||(d=f`
      <ha-select
        .icon=${0}
        .label=${0}
        .value=${0}
        .helper=${0}
        .disabled=${0}
        @closed=${0}
        @selected=${0}
        fixedMenuPosition
        naturalMenuWidth
        .clearable=${0}
      >
        ${0}
        ${0}
        ${0}
        ${0}
        ${0}
        ${0}
      </ha-select>
    `),Boolean(e),this.label,e,this.helper,this.disabled,c.d,this._valueSelected,!this.defaultColor,e?(0,a.qy)(h||(h=f`
              <span slot="icon">
                ${0}
              </span>
            `),"none"===e?(0,a.qy)(p||(p=f`
                      <ha-svg-icon path=${0}></ha-svg-icon>
                    `),k):"state"===e?(0,a.qy)(u||(u=f`<ha-svg-icon path=${0}></ha-svg-icon>`),C):this._renderColorCircle(e||"grey")):a.s6,this.includeNone?(0,a.qy)(_||(_=f`
              <ha-list-item value="none" graphic="icon">
                ${0}
                ${0}
                <ha-svg-icon
                  slot="graphic"
                  path=${0}
                ></ha-svg-icon>
              </ha-list-item>
            `),this.hass.localize("ui.components.color-picker.none"),"none"===this.defaultColor?` (${this.hass.localize("ui.components.color-picker.default")})`:a.s6,k):a.s6,this.includeState?(0,a.qy)(v||(v=f`
              <ha-list-item value="state" graphic="icon">
                ${0}
                ${0}
                <ha-svg-icon slot="graphic" path=${0}></ha-svg-icon>
              </ha-list-item>
            `),this.hass.localize("ui.components.color-picker.state"),"state"===this.defaultColor?` (${this.hass.localize("ui.components.color-picker.default")})`:a.s6,C):a.s6,this.includeState||this.includeNone?(0,a.qy)(y||(y=f`<ha-md-divider role="separator" tabindex="-1"></ha-md-divider>`)):a.s6,Array.from(n.l).map((e=>(0,a.qy)(m||(m=f`
            <ha-list-item .value=${0} graphic="icon">
              ${0}
              ${0}
              <span slot="graphic">${0}</span>
            </ha-list-item>
          `),e,this.hass.localize(`ui.components.color-picker.colors.${e}`)||e,this.defaultColor===e?` (${this.hass.localize("ui.components.color-picker.default")})`:a.s6,this._renderColorCircle(e)))),t?(0,a.qy)(g||(g=f`
              <ha-list-item .value=${0} graphic="icon">
                ${0}
                <span slot="graphic">${0}</span>
              </ha-list-item>
            `),e,e,this._renderColorCircle(e)):a.s6)}_renderColorCircle(e){return(0,a.qy)(b||(b=f`
      <span
        class="circle-color"
        style=${0}
      ></span>
    `),(0,r.W)({"--circle-color":(0,n.M)(e)}))}constructor(...e){super(...e),this.includeState=!1,this.includeNone=!1,this.disabled=!1}}M.styles=(0,a.AH)($||($=f`
    .circle-color {
      display: block;
      background-color: var(--circle-color, var(--divider-color));
      border: 1px solid var(--outline-color);
      border-radius: 10px;
      width: 20px;
      height: 20px;
      box-sizing: border-box;
    }
    ha-select {
      width: 100%;
    }
  `)),(0,o.__decorate)([(0,s.MZ)()],M.prototype,"label",void 0),(0,o.__decorate)([(0,s.MZ)()],M.prototype,"helper",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],M.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)()],M.prototype,"value",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"default_color"})],M.prototype,"defaultColor",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"include_state"})],M.prototype,"includeState",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"include_none"})],M.prototype,"includeNone",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],M.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.P)("ha-select")],M.prototype,"_select",void 0),M=(0,o.__decorate)([(0,s.EM)("ha-color-picker")],M)},15785:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t),i.d(t,{HaIconPicker:function(){return C}});i(79827),i(35748),i(99342),i(35058),i(65315),i(837),i(22416),i(37089),i(59023),i(5934),i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030),i(18223),i(95013);var a=i(69868),s=i(84922),r=i(11991),n=i(65940),l=i(73120),c=i(73314),d=i(5177),h=(i(81164),i(36137),e([d]));d=(h.then?(await h)():h)[0];let p,u,_,v,y,m=e=>e,g=[],b=!1;const $=async()=>{b=!0;const e=await i.e("4765").then(i.t.bind(i,43692,19));g=e.default.map((e=>({icon:`mdi:${e.name}`,parts:new Set(e.name.split("-")),keywords:e.keywords})));const t=[];Object.keys(c.y).forEach((e=>{t.push(f(e))})),(await Promise.all(t)).forEach((e=>{g.push(...e)}))},f=async e=>{try{const t=c.y[e].getIconList;if("function"!=typeof t)return[];const i=await t();return i.map((t=>{var i;return{icon:`${e}:${t.name}`,parts:new Set(t.name.split("-")),keywords:null!==(i=t.keywords)&&void 0!==i?i:[]}}))}catch(t){return console.warn(`Unable to load icon list for ${e} iconset`),[]}},k=e=>(0,s.qy)(p||(p=m`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${0} slot="start"></ha-icon>
    ${0}
  </ha-combo-box-item>
`),e.icon,e.icon);class C extends s.WF{render(){return(0,s.qy)(u||(u=m`
      <ha-combo-box
        .hass=${0}
        item-value-path="icon"
        item-label-path="icon"
        .value=${0}
        allow-custom-value
        .dataProvider=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
        .placeholder=${0}
        .errorMessage=${0}
        .invalid=${0}
        .renderer=${0}
        icon
        @opened-changed=${0}
        @value-changed=${0}
      >
        ${0}
      </ha-combo-box>
    `),this.hass,this._value,b?this._iconProvider:void 0,this.label,this.helper,this.disabled,this.required,this.placeholder,this.errorMessage,this.invalid,k,this._openedChanged,this._valueChanged,this._value||this.placeholder?(0,s.qy)(_||(_=m`
              <ha-icon .icon=${0} slot="icon">
              </ha-icon>
            `),this._value||this.placeholder):(0,s.qy)(v||(v=m`<slot slot="icon" name="fallback"></slot>`)))}async _openedChanged(e){e.detail.value&&!b&&(await $(),this.requestUpdate())}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,l.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.invalid=!1,this._filterIcons=(0,n.A)(((e,t=g)=>{if(!e)return t;const i=[],o=(e,t)=>i.push({icon:e,rank:t});for(const a of t)a.parts.has(e)?o(a.icon,1):a.keywords.includes(e)?o(a.icon,2):a.icon.includes(e)?o(a.icon,3):a.keywords.some((t=>t.includes(e)))&&o(a.icon,4);return 0===i.length&&o(e,0),i.sort(((e,t)=>e.rank-t.rank))})),this._iconProvider=(e,t)=>{const i=this._filterIcons(e.filter.toLowerCase(),g),o=e.page*e.pageSize,a=o+e.pageSize;t(i.slice(o,a),i.length)}}}C.styles=(0,s.AH)(y||(y=m`
    *[slot="icon"] {
      color: var(--primary-text-color);
      position: relative;
      bottom: 2px;
    }
    *[slot="prefix"] {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
  `)),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],C.prototype,"hass",void 0),(0,a.__decorate)([(0,r.MZ)()],C.prototype,"value",void 0),(0,a.__decorate)([(0,r.MZ)()],C.prototype,"label",void 0),(0,a.__decorate)([(0,r.MZ)()],C.prototype,"helper",void 0),(0,a.__decorate)([(0,r.MZ)()],C.prototype,"placeholder",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:"error-message"})],C.prototype,"errorMessage",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],C.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],C.prototype,"required",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],C.prototype,"invalid",void 0),C=(0,a.__decorate)([(0,r.EM)("ha-icon-picker")],C),o()}catch(p){o(p)}}))},90666:function(e,t,i){var o=i(69868),a=i(61320),s=i(41715),r=i(84922),n=i(11991);let l;class c extends a.c{}c.styles=[s.R,(0,r.AH)(l||(l=(e=>e)`
      :host {
        --md-divider-color: var(--divider-color);
      }
    `))],c=(0,o.__decorate)([(0,n.EM)("ha-md-divider")],c)},76882:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t);i(32203),i(35748),i(5934),i(39118),i(95013);var a=i(69868),s=i(84922),r=i(11991),n=i(73120),l=(i(23749),i(76943)),c=(i(85055),i(72847)),d=i(15785),h=(i(43143),i(79973),i(11934),i(83566)),p=e([l,d]);[l,d]=p.then?(await p)():p;let u,_,v,y,m=e=>e;class g extends s.WF{showDialog(e){this._params=e,this._error=void 0,this._params.entry?(this._name=this._params.entry.name||"",this._icon=this._params.entry.icon||"",this._color=this._params.entry.color||"",this._description=this._params.entry.description||""):(this._name=this._params.suggestedName||"",this._icon="",this._color="",this._description=""),document.body.addEventListener("keydown",this._handleKeyPress)}closeDialog(){return this._params=void 0,(0,n.r)(this,"dialog-closed",{dialog:this.localName}),document.body.removeEventListener("keydown",this._handleKeyPress),!0}render(){return this._params?(0,s.qy)(u||(u=m`
      <ha-dialog
        open
        @closed=${0}
        scrimClickAction
        escapeKeyAction
        .heading=${0}
      >
        <div>
          ${0}
          <div class="form">
            <ha-textfield
              dialogInitialFocus
              .value=${0}
              .configValue=${0}
              @input=${0}
              .label=${0}
              .validationMessage=${0}
              required
            ></ha-textfield>
            <ha-icon-picker
              .value=${0}
              .hass=${0}
              .configValue=${0}
              @value-changed=${0}
              .label=${0}
            ></ha-icon-picker>
            <ha-color-picker
              .value=${0}
              .configValue=${0}
              .hass=${0}
              @value-changed=${0}
              .label=${0}
            ></ha-color-picker>
            <ha-textarea
              .value=${0}
              .configValue=${0}
              @input=${0}
              .label=${0}
            ></ha-textarea>
          </div>
        </div>
        ${0}
        <ha-button
          slot="primaryAction"
          @click=${0}
          .disabled=${0}
        >
          ${0}
        </ha-button>
      </ha-dialog>
    `),this.closeDialog,(0,c.l)(this.hass,this._params.entry?this._params.entry.name||this._params.entry.label_id:this.hass.localize("ui.panel.config.labels.detail.new_label")),this._error?(0,s.qy)(_||(_=m`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):"",this._name,"name",this._input,this.hass.localize("ui.panel.config.labels.detail.name"),this.hass.localize("ui.panel.config.labels.detail.required_error_msg"),this._icon,this.hass,"icon",this._valueChanged,this.hass.localize("ui.panel.config.labels.detail.icon"),this._color,"color",this.hass,this._valueChanged,this.hass.localize("ui.panel.config.labels.detail.color"),this._description,"description",this._input,this.hass.localize("ui.panel.config.labels.detail.description"),this._params.entry&&this._params.removeEntry?(0,s.qy)(v||(v=m`
              <ha-button
                slot="secondaryAction"
                variant="danger"
                appearance="plain"
                @click=${0}
                .disabled=${0}
              >
                ${0}
              </ha-button>
            `),this._deleteEntry,this._submitting,this.hass.localize("ui.panel.config.labels.detail.delete")):s.s6,this._updateEntry,this._submitting||!this._name,this._params.entry?this.hass.localize("ui.panel.config.labels.detail.update"):this.hass.localize("ui.panel.config.labels.detail.create")):s.s6}_input(e){const t=e.target,i=t.configValue;this._error=void 0,this[`_${i}`]=t.value}_valueChanged(e){const t=e.target.configValue;this._error=void 0,this[`_${t}`]=e.detail.value||""}async _updateEntry(){this._submitting=!0;try{const e={name:this._name.trim(),icon:this._icon.trim()||null,color:this._color.trim()||null,description:this._description.trim()||null};this._params.entry?await this._params.updateEntry(e):await this._params.createEntry(e),this.closeDialog()}catch(e){this._error=e?e.message:"Unknown error"}finally{this._submitting=!1}}async _deleteEntry(){this._submitting=!0;try{await this._params.removeEntry()&&(this._params=void 0)}finally{this._submitting=!1}}static get styles(){return[h.nA,(0,s.AH)(y||(y=m`
        a {
          color: var(--primary-color);
        }
        ha-textarea,
        ha-textfield,
        ha-icon-picker,
        ha-color-picker {
          display: block;
        }
        ha-color-picker,
        ha-textarea {
          margin-top: 16px;
        }
      `))]}constructor(...e){super(...e),this._submitting=!1,this._handleKeyPress=e=>{"Escape"===e.key&&e.stopPropagation()}}}(0,a.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,a.__decorate)([(0,r.wk)()],g.prototype,"_name",void 0),(0,a.__decorate)([(0,r.wk)()],g.prototype,"_icon",void 0),(0,a.__decorate)([(0,r.wk)()],g.prototype,"_color",void 0),(0,a.__decorate)([(0,r.wk)()],g.prototype,"_description",void 0),(0,a.__decorate)([(0,r.wk)()],g.prototype,"_error",void 0),(0,a.__decorate)([(0,r.wk)()],g.prototype,"_params",void 0),(0,a.__decorate)([(0,r.wk)()],g.prototype,"_submitting",void 0),g=(0,a.__decorate)([(0,r.EM)("dialog-label-detail")],g),o()}catch(u){o(u)}}))},41715:function(e,t,i){i.d(t,{R:function(){return a}});let o;const a=(0,i(84922).AH)(o||(o=(e=>e)`:host{box-sizing:border-box;color:var(--md-divider-color, var(--md-sys-color-outline-variant, #cac4d0));display:flex;height:var(--md-divider-thickness, 1px);width:100%}:host([inset]),:host([inset-start]){padding-inline-start:16px}:host([inset]),:host([inset-end]){padding-inline-end:16px}:host::before{background:currentColor;content:"";height:100%;width:100%}@media(forced-colors: active){:host::before{background:CanvasText}}
`))},61320:function(e,t,i){i.d(t,{c:function(){return r}});i(35748),i(95013);var o=i(69868),a=i(84922),s=i(11991);class r extends a.WF{constructor(){super(...arguments),this.inset=!1,this.insetStart=!1,this.insetEnd=!1}}(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],r.prototype,"inset",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0,attribute:"inset-start"})],r.prototype,"insetStart",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0,attribute:"inset-end"})],r.prototype,"insetEnd",void 0)}}]);
//# sourceMappingURL=3327.b9e71b842ca71dbf.js.map