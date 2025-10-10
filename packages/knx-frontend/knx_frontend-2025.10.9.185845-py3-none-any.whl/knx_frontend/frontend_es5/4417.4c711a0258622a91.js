"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["4417"],{15785:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t),i.d(t,{HaIconPicker:function(){return k}});i(79827),i(35748),i(99342),i(35058),i(65315),i(837),i(22416),i(37089),i(59023),i(5934),i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030),i(18223),i(95013);var o=i(69868),s=i(84922),n=i(11991),l=i(65940),r=i(73120),h=i(73314),d=i(5177),c=(i(81164),i(36137),e([d]));d=(c.then?(await c)():c)[0];let u,p,_,m,v,g=e=>e,f=[],y=!1;const b=async()=>{y=!0;const e=await i.e("4765").then(i.t.bind(i,43692,19));f=e.default.map((e=>({icon:`mdi:${e.name}`,parts:new Set(e.name.split("-")),keywords:e.keywords})));const t=[];Object.keys(h.y).forEach((e=>{t.push($(e))})),(await Promise.all(t)).forEach((e=>{f.push(...e)}))},$=async e=>{try{const t=h.y[e].getIconList;if("function"!=typeof t)return[];const i=await t();return i.map((t=>{var i;return{icon:`${e}:${t.name}`,parts:new Set(t.name.split("-")),keywords:null!==(i=t.keywords)&&void 0!==i?i:[]}}))}catch(t){return console.warn(`Unable to load icon list for ${e} iconset`),[]}},x=e=>(0,s.qy)(u||(u=g`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${0} slot="start"></ha-icon>
    ${0}
  </ha-combo-box-item>
`),e.icon,e.icon);class k extends s.WF{render(){return(0,s.qy)(p||(p=g`
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
    `),this.hass,this._value,y?this._iconProvider:void 0,this.label,this.helper,this.disabled,this.required,this.placeholder,this.errorMessage,this.invalid,x,this._openedChanged,this._valueChanged,this._value||this.placeholder?(0,s.qy)(_||(_=g`
              <ha-icon .icon=${0} slot="icon">
              </ha-icon>
            `),this._value||this.placeholder):(0,s.qy)(m||(m=g`<slot slot="icon" name="fallback"></slot>`)))}async _openedChanged(e){e.detail.value&&!y&&(await b(),this.requestUpdate())}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,r.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.invalid=!1,this._filterIcons=(0,l.A)(((e,t=f)=>{if(!e)return t;const i=[],a=(e,t)=>i.push({icon:e,rank:t});for(const o of t)o.parts.has(e)?a(o.icon,1):o.keywords.includes(e)?a(o.icon,2):o.icon.includes(e)?a(o.icon,3):o.keywords.some((t=>t.includes(e)))&&a(o.icon,4);return 0===i.length&&a(e,0),i.sort(((e,t)=>e.rank-t.rank))})),this._iconProvider=(e,t)=>{const i=this._filterIcons(e.filter.toLowerCase(),f),a=e.page*e.pageSize,o=a+e.pageSize;t(i.slice(a,o),i.length)}}}k.styles=(0,s.AH)(v||(v=g`
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
  `)),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],k.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)()],k.prototype,"value",void 0),(0,o.__decorate)([(0,n.MZ)()],k.prototype,"label",void 0),(0,o.__decorate)([(0,n.MZ)()],k.prototype,"helper",void 0),(0,o.__decorate)([(0,n.MZ)()],k.prototype,"placeholder",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"error-message"})],k.prototype,"errorMessage",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],k.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],k.prototype,"required",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],k.prototype,"invalid",void 0),k=(0,o.__decorate)([(0,n.EM)("ha-icon-picker")],k),a()}catch(u){a(u)}}))},19528:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t);i(35748),i(12977),i(95013);var o=i(69868),s=i(84922),n=i(11991),l=i(73120),r=(i(99741),i(52893),i(15785)),h=(i(56292),i(11934),i(83566)),d=e([r]);r=(d.then?(await d)():d)[0];let c,u,p=e=>e;class _ extends s.WF{set item(e){var t,i,a;(this._item=e,e)?(this._name=e.name||"",this._icon=e.icon||"",this._max=null!==(t=e.max)&&void 0!==t?t:100,this._min=null!==(i=e.min)&&void 0!==i?i:0,this._mode=e.mode||"slider",this._step=null!==(a=e.step)&&void 0!==a?a:1,this._unit_of_measurement=e.unit_of_measurement):(this._item={min:0,max:100},this._name="",this._icon="",this._max=100,this._min=0,this._mode="slider",this._step=1)}focus(){this.updateComplete.then((()=>{var e;return null===(e=this.shadowRoot)||void 0===e||null===(e=e.querySelector("[dialogInitialFocus]"))||void 0===e?void 0:e.focus()}))}render(){return this.hass?(0,s.qy)(c||(c=p`
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
        <ha-textfield
          .value=${0}
          .configValue=${0}
          type="number"
          step="any"
          @input=${0}
          .label=${0}
        ></ha-textfield>
        <ha-textfield
          .value=${0}
          .configValue=${0}
          type="number"
          step="any"
          @input=${0}
          .label=${0}
        ></ha-textfield>
        <ha-expansion-panel
          header=${0}
          outlined
        >
          <div class="layout horizontal center justified">
            ${0}
            <ha-formfield
              .label=${0}
            >
              <ha-radio
                name="mode"
                value="slider"
                .checked=${0}
                @change=${0}
              ></ha-radio>
            </ha-formfield>
            <ha-formfield
              .label=${0}
            >
              <ha-radio
                name="mode"
                value="box"
                .checked=${0}
                @change=${0}
              ></ha-radio>
            </ha-formfield>
          </div>
          <ha-textfield
            .value=${0}
            .configValue=${0}
            type="number"
            step="any"
            @input=${0}
            .label=${0}
          ></ha-textfield>

          <ha-textfield
            .value=${0}
            .configValue=${0}
            @input=${0}
            .label=${0}
          ></ha-textfield>
        </ha-expansion-panel>
      </div>
    `),this._name,"name",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.name"),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon"),this._min,"min",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.input_number.min"),this._max,"max",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.input_number.max"),this.hass.localize("ui.dialogs.helper_settings.generic.advanced_settings"),this.hass.localize("ui.dialogs.helper_settings.input_number.mode"),this.hass.localize("ui.dialogs.helper_settings.input_number.slider"),"slider"===this._mode,this._modeChanged,this.hass.localize("ui.dialogs.helper_settings.input_number.box"),"box"===this._mode,this._modeChanged,this._step,"step",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.input_number.step"),this._unit_of_measurement||"","unit_of_measurement",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.input_number.unit_of_measurement")):s.s6}_modeChanged(e){(0,l.r)(this,"value-changed",{value:Object.assign(Object.assign({},this._item),{},{mode:e.target.value})})}_valueChanged(e){var t;if(!this.new&&!this._item)return;e.stopPropagation();const i=e.target,a=i.configValue,o="number"===i.type?Number(i.value):(null===(t=e.detail)||void 0===t?void 0:t.value)||i.value;if(this[`_${a}`]===o)return;const s=Object.assign({},this._item);void 0===o||""===o?delete s[a]:s[a]=o,(0,l.r)(this,"value-changed",{value:s})}static get styles(){return[h.RF,(0,s.AH)(u||(u=p`
        .form {
          color: var(--primary-text-color);
        }

        ha-textfield {
          display: block;
          margin-bottom: 8px;
        }
      `))]}constructor(...e){super(...e),this.new=!1}}(0,o.__decorate)([(0,n.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],_.prototype,"new",void 0),(0,o.__decorate)([(0,n.wk)()],_.prototype,"_name",void 0),(0,o.__decorate)([(0,n.wk)()],_.prototype,"_icon",void 0),(0,o.__decorate)([(0,n.wk)()],_.prototype,"_max",void 0),(0,o.__decorate)([(0,n.wk)()],_.prototype,"_min",void 0),(0,o.__decorate)([(0,n.wk)()],_.prototype,"_mode",void 0),(0,o.__decorate)([(0,n.wk)()],_.prototype,"_step",void 0),(0,o.__decorate)([(0,n.wk)()],_.prototype,"_unit_of_measurement",void 0),_=(0,o.__decorate)([(0,n.EM)("ha-input_number-form")],_),a()}catch(c){a(c)}}))}}]);
//# sourceMappingURL=4417.4c711a0258622a91.js.map