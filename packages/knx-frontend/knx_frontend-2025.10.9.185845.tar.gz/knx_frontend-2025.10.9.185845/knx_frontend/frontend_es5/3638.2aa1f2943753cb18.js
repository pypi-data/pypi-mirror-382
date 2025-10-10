"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["3638"],{15785:function(e,t,o){o.a(e,(async function(e,i){try{o.r(t),o.d(t,{HaIconPicker:function(){return k}});o(79827),o(35748),o(99342),o(35058),o(65315),o(837),o(22416),o(37089),o(59023),o(5934),o(88238),o(34536),o(16257),o(20152),o(44711),o(72108),o(77030),o(18223),o(95013);var a=o(69868),r=o(84922),s=o(11991),n=o(65940),l=o(73120),c=o(73314),d=o(5177),h=(o(81164),o(36137),e([d]));d=(h.then?(await h)():h)[0];let u,p,_,v,g,y=e=>e,m=[],f=!1;const b=async()=>{f=!0;const e=await o.e("4765").then(o.t.bind(o,43692,19));m=e.default.map((e=>({icon:`mdi:${e.name}`,parts:new Set(e.name.split("-")),keywords:e.keywords})));const t=[];Object.keys(c.y).forEach((e=>{t.push($(e))})),(await Promise.all(t)).forEach((e=>{m.push(...e)}))},$=async e=>{try{const t=c.y[e].getIconList;if("function"!=typeof t)return[];const o=await t();return o.map((t=>{var o;return{icon:`${e}:${t.name}`,parts:new Set(t.name.split("-")),keywords:null!==(o=t.keywords)&&void 0!==o?o:[]}}))}catch(t){return console.warn(`Unable to load icon list for ${e} iconset`),[]}},w=e=>(0,r.qy)(u||(u=y`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${0} slot="start"></ha-icon>
    ${0}
  </ha-combo-box-item>
`),e.icon,e.icon);class k extends r.WF{render(){return(0,r.qy)(p||(p=y`
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
    `),this.hass,this._value,f?this._iconProvider:void 0,this.label,this.helper,this.disabled,this.required,this.placeholder,this.errorMessage,this.invalid,w,this._openedChanged,this._valueChanged,this._value||this.placeholder?(0,r.qy)(_||(_=y`
              <ha-icon .icon=${0} slot="icon">
              </ha-icon>
            `),this._value||this.placeholder):(0,r.qy)(v||(v=y`<slot slot="icon" name="fallback"></slot>`)))}async _openedChanged(e){e.detail.value&&!f&&(await b(),this.requestUpdate())}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,l.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.invalid=!1,this._filterIcons=(0,n.A)(((e,t=m)=>{if(!e)return t;const o=[],i=(e,t)=>o.push({icon:e,rank:t});for(const a of t)a.parts.has(e)?i(a.icon,1):a.keywords.includes(e)?i(a.icon,2):a.icon.includes(e)?i(a.icon,3):a.keywords.some((t=>t.includes(e)))&&i(a.icon,4);return 0===o.length&&i(e,0),o.sort(((e,t)=>e.rank-t.rank))})),this._iconProvider=(e,t)=>{const o=this._filterIcons(e.filter.toLowerCase(),m),i=e.page*e.pageSize,a=i+e.pageSize;t(o.slice(i,a),o.length)}}}k.styles=(0,r.AH)(g||(g=y`
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
  `)),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],k.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)()],k.prototype,"value",void 0),(0,a.__decorate)([(0,s.MZ)()],k.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)()],k.prototype,"helper",void 0),(0,a.__decorate)([(0,s.MZ)()],k.prototype,"placeholder",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"error-message"})],k.prototype,"errorMessage",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],k.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],k.prototype,"required",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],k.prototype,"invalid",void 0),k=(0,a.__decorate)([(0,s.EM)("ha-icon-picker")],k),i()}catch(u){i(u)}}))},95189:function(e,t,o){o.a(e,(async function(e,i){try{o.r(t);o(35748),o(12977),o(95013);var a=o(69868),r=o(84922),s=o(11991),n=o(73120),l=o(15785),c=(o(11934),o(83566)),d=e([l]);l=(d.then?(await d)():d)[0];let h,u,p=e=>e;class _ extends r.WF{set item(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||""):(this._name="",this._icon="")}focus(){this.updateComplete.then((()=>{var e;return null===(e=this.shadowRoot)||void 0===e||null===(e=e.querySelector("[dialogInitialFocus]"))||void 0===e?void 0:e.focus()}))}render(){return this.hass?(0,r.qy)(h||(h=p`
      <div class="form">
        <ha-textfield
          .value=${0}
          .configValue=${0}
          @input=${0}
          .label=${0}
          autoValidate
          required
          .validationMessage=${0}
          dialogInitialFocus
        ></ha-textfield>
        <ha-icon-picker
          .hass=${0}
          .value=${0}
          .configValue=${0}
          @value-changed=${0}
          .label=${0}
        ></ha-icon-picker>
      </div>
    `),this._name,"name",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.name"),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon")):r.s6}_valueChanged(e){var t;if(!this.new&&!this._item)return;e.stopPropagation();const o=e.target.configValue,i=(null===(t=e.detail)||void 0===t?void 0:t.value)||e.target.value;if(this[`_${o}`]===i)return;const a=Object.assign({},this._item);i?a[o]=i:delete a[o],(0,n.r)(this,"value-changed",{value:a})}static get styles(){return[c.RF,(0,r.AH)(u||(u=p`
        .form {
          color: var(--primary-text-color);
        }
        .row {
          padding: 16px 0;
        }
        ha-textfield {
          display: block;
          margin: 8px 0;
        }
      `))]}constructor(...e){super(...e),this.new=!1}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],_.prototype,"new",void 0),(0,a.__decorate)([(0,s.wk)()],_.prototype,"_name",void 0),(0,a.__decorate)([(0,s.wk)()],_.prototype,"_icon",void 0),_=(0,a.__decorate)([(0,s.EM)("ha-input_boolean-form")],_),i()}catch(h){i(h)}}))}}]);
//# sourceMappingURL=3638.2aa1f2943753cb18.js.map