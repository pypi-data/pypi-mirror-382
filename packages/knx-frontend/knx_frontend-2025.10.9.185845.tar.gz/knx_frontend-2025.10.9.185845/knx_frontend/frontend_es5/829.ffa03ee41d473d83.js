"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["829"],{4855:function(e,t,i){i.a(e,(async function(e,t){try{i(35748),i(35058),i(65315),i(37089),i(12977),i(5934),i(95013);var o=i(69868),a=i(84922),r=i(11991),n=i(73120),s=i(90963),l=i(88120),d=i(28027),c=i(45363),h=i(5177),p=(i(36137),e([h]));h=(p.then?(await p)():p)[0];let u,_,y=e=>e;class v extends a.WF{open(){var e;null===(e=this._comboBox)||void 0===e||e.open()}focus(){var e;null===(e=this._comboBox)||void 0===e||e.focus()}firstUpdated(){this._getConfigEntries()}render(){return this._configEntries?(0,a.qy)(u||(u=y`
      <ha-combo-box
        .hass=${0}
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        .helper=${0}
        .renderer=${0}
        .items=${0}
        item-value-path="entry_id"
        item-id-path="entry_id"
        item-label-path="title"
        @value-changed=${0}
      ></ha-combo-box>
    `),this.hass,void 0===this.label&&this.hass?this.hass.localize("ui.components.config-entry-picker.config_entry"):this.label,this._value,this.required,this.disabled,this.helper,this._rowRenderer,this._configEntries,this._valueChanged):a.s6}_onImageLoad(e){e.target.style.visibility="initial"}_onImageError(e){e.target.style.visibility="hidden"}async _getConfigEntries(){(0,l.VN)(this.hass,{type:["device","hub","service"],domain:this.integration}).then((e=>{this._configEntries=e.map((e=>Object.assign(Object.assign({},e),{},{localized_domain_name:(0,d.p$)(this.hass.localize,e.domain)}))).sort(((e,t)=>(0,s.SH)(e.localized_domain_name+e.title,t.localized_domain_name+t.title,this.hass.locale.language)))}))}get _value(){return this.value||""}_valueChanged(e){e.stopPropagation();const t=e.detail.value;t!==this._value&&this._setValue(t)}_setValue(e){this.value=e,setTimeout((()=>{(0,n.r)(this,"value-changed",{value:e}),(0,n.r)(this,"change")}),0)}constructor(...e){super(...e),this.value="",this.disabled=!1,this.required=!1,this._rowRenderer=e=>{var t;return(0,a.qy)(_||(_=y`
    <ha-combo-box-item type="button">
      <span slot="headline">
        ${0}
      </span>
      <span slot="supporting-text">${0}</span>
      <img
        alt=""
        slot="start"
        src=${0}
        crossorigin="anonymous"
        referrerpolicy="no-referrer"
        @error=${0}
        @load=${0}
      />
    </ha-combo-box-item>
  `),e.title||this.hass.localize("ui.panel.config.integrations.config_entry.unnamed_entry"),e.localized_domain_name,(0,c.MR)({domain:e.domain,type:"icon",darkOptimized:null===(t=this.hass.themes)||void 0===t?void 0:t.darkMode}),this._onImageError,this._onImageLoad)}}}(0,o.__decorate)([(0,r.MZ)()],v.prototype,"integration",void 0),(0,o.__decorate)([(0,r.MZ)()],v.prototype,"label",void 0),(0,o.__decorate)([(0,r.MZ)()],v.prototype,"value",void 0),(0,o.__decorate)([(0,r.MZ)()],v.prototype,"helper",void 0),(0,o.__decorate)([(0,r.wk)()],v.prototype,"_configEntries",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],v.prototype,"disabled",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],v.prototype,"required",void 0),(0,o.__decorate)([(0,r.P)("ha-combo-box")],v.prototype,"_comboBox",void 0),v=(0,o.__decorate)([(0,r.EM)("ha-config-entry-picker")],v),t()}catch(u){t(u)}}))},47340:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t),i.d(t,{HaConfigEntrySelector:function(){return p}});i(35748),i(95013);var a=i(69868),r=i(84922),n=i(11991),s=i(4855),l=e([s]);s=(l.then?(await l)():l)[0];let d,c,h=e=>e;class p extends r.WF{render(){var e;return(0,r.qy)(d||(d=h`<ha-config-entry-picker
      .hass=${0}
      .value=${0}
      .label=${0}
      .helper=${0}
      .disabled=${0}
      .required=${0}
      .integration=${0}
      allow-custom-entity
    ></ha-config-entry-picker>`),this.hass,this.value,this.label,this.helper,this.disabled,this.required,null===(e=this.selector.config_entry)||void 0===e?void 0:e.integration)}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}p.styles=(0,r.AH)(c||(c=h`
    ha-config-entry-picker {
      width: 100%;
    }
  `)),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"selector",void 0),(0,a.__decorate)([(0,n.MZ)()],p.prototype,"value",void 0),(0,a.__decorate)([(0,n.MZ)()],p.prototype,"label",void 0),(0,a.__decorate)([(0,n.MZ)()],p.prototype,"helper",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],p.prototype,"required",void 0),p=(0,a.__decorate)([(0,n.EM)("ha-selector-config_entry")],p),o()}catch(d){o(d)}}))},28027:function(e,t,i){i.d(t,{QC:function(){return r},fK:function(){return a},p$:function(){return o}});i(24802);const o=(e,t,i)=>e(`component.${t}.title`)||(null==i?void 0:i.name)||t,a=(e,t)=>{const i={type:"manifest/list"};return t&&(i.integrations=t),e.callWS(i)},r=(e,t)=>e.callWS({type:"manifest/get",integration:t})},45363:function(e,t,i){i.d(t,{MR:function(){return o},a_:function(){return a},bg:function(){return r}});i(56660);const o=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,a=e=>e.split("/")[4],r=e=>e.startsWith("https://brands.home-assistant.io/")}}]);
//# sourceMappingURL=829.ffa03ee41d473d83.js.map