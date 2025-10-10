export const __webpack_id__="2940";export const __webpack_ids__=["2940"];export const __webpack_modules__={58327:function(e,t,o){o.r(t),o.d(t,{HaConfigEntrySelector:()=>_});var i=o(69868),a=o(84922),r=o(11991),s=o(73120),n=o(90963),d=o(88120),l=o(28027),c=o(45363);o(26731),o(36137);class h extends a.WF{open(){this._comboBox?.open()}focus(){this._comboBox?.focus()}firstUpdated(){this._getConfigEntries()}render(){return this._configEntries?a.qy`
      <ha-combo-box
        .hass=${this.hass}
        .label=${void 0===this.label&&this.hass?this.hass.localize("ui.components.config-entry-picker.config_entry"):this.label}
        .value=${this._value}
        .required=${this.required}
        .disabled=${this.disabled}
        .helper=${this.helper}
        .renderer=${this._rowRenderer}
        .items=${this._configEntries}
        item-value-path="entry_id"
        item-id-path="entry_id"
        item-label-path="title"
        @value-changed=${this._valueChanged}
      ></ha-combo-box>
    `:a.s6}_onImageLoad(e){e.target.style.visibility="initial"}_onImageError(e){e.target.style.visibility="hidden"}async _getConfigEntries(){(0,d.VN)(this.hass,{type:["device","hub","service"],domain:this.integration}).then((e=>{this._configEntries=e.map((e=>({...e,localized_domain_name:(0,l.p$)(this.hass.localize,e.domain)}))).sort(((e,t)=>(0,n.SH)(e.localized_domain_name+e.title,t.localized_domain_name+t.title,this.hass.locale.language)))}))}get _value(){return this.value||""}_valueChanged(e){e.stopPropagation();const t=e.detail.value;t!==this._value&&this._setValue(t)}_setValue(e){this.value=e,setTimeout((()=>{(0,s.r)(this,"value-changed",{value:e}),(0,s.r)(this,"change")}),0)}constructor(...e){super(...e),this.value="",this.disabled=!1,this.required=!1,this._rowRenderer=e=>a.qy`
    <ha-combo-box-item type="button">
      <span slot="headline">
        ${e.title||this.hass.localize("ui.panel.config.integrations.config_entry.unnamed_entry")}
      </span>
      <span slot="supporting-text">${e.localized_domain_name}</span>
      <img
        alt=""
        slot="start"
        src=${(0,c.MR)({domain:e.domain,type:"icon",darkOptimized:this.hass.themes?.darkMode})}
        crossorigin="anonymous"
        referrerpolicy="no-referrer"
        @error=${this._onImageError}
        @load=${this._onImageLoad}
      />
    </ha-combo-box-item>
  `}}(0,i.__decorate)([(0,r.MZ)()],h.prototype,"integration",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"helper",void 0),(0,i.__decorate)([(0,r.wk)()],h.prototype,"_configEntries",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"required",void 0),(0,i.__decorate)([(0,r.P)("ha-combo-box")],h.prototype,"_comboBox",void 0),h=(0,i.__decorate)([(0,r.EM)("ha-config-entry-picker")],h);class _ extends a.WF{render(){return a.qy`<ha-config-entry-picker
      .hass=${this.hass}
      .value=${this.value}
      .label=${this.label}
      .helper=${this.helper}
      .disabled=${this.disabled}
      .required=${this.required}
      .integration=${this.selector.config_entry?.integration}
      allow-custom-entity
    ></ha-config-entry-picker>`}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}_.styles=a.AH`
    ha-config-entry-picker {
      width: 100%;
    }
  `,(0,i.__decorate)([(0,r.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],_.prototype,"selector",void 0),(0,i.__decorate)([(0,r.MZ)()],_.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],_.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],_.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],_.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],_.prototype,"required",void 0),_=(0,i.__decorate)([(0,r.EM)("ha-selector-config_entry")],_)},28027:function(e,t,o){o.d(t,{QC:()=>r,fK:()=>a,p$:()=>i});const i=(e,t,o)=>e(`component.${t}.title`)||o?.name||t,a=(e,t)=>{const o={type:"manifest/list"};return t&&(o.integrations=t),e.callWS(o)},r=(e,t)=>e.callWS({type:"manifest/get",integration:t})},45363:function(e,t,o){o.d(t,{MR:()=>i,a_:()=>a,bg:()=>r});const i=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,a=e=>e.split("/")[4],r=e=>e.startsWith("https://brands.home-assistant.io/")}};
//# sourceMappingURL=2940.f326b7fd303bcb03.js.map