export const __webpack_id__="2809";export const __webpack_ids__=["2809"];export const __webpack_modules__={15785:function(e,t,i){i.r(t),i.d(t,{HaIconPicker:()=>p});var a=i(69868),o=i(84922),s=i(11991),r=i(65940),n=i(73120),l=i(73314);i(26731),i(81164),i(36137);let h=[],c=!1;const d=async e=>{try{const t=l.y[e].getIconList;if("function"!=typeof t)return[];const i=await t();return i.map((t=>({icon:`${e}:${t.name}`,parts:new Set(t.name.split("-")),keywords:t.keywords??[]})))}catch(t){return console.warn(`Unable to load icon list for ${e} iconset`),[]}},u=e=>o.qy`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${e.icon} slot="start"></ha-icon>
    ${e.icon}
  </ha-combo-box-item>
`;class p extends o.WF{render(){return o.qy`
      <ha-combo-box
        .hass=${this.hass}
        item-value-path="icon"
        item-label-path="icon"
        .value=${this._value}
        allow-custom-value
        .dataProvider=${c?this._iconProvider:void 0}
        .label=${this.label}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
        .placeholder=${this.placeholder}
        .errorMessage=${this.errorMessage}
        .invalid=${this.invalid}
        .renderer=${u}
        icon
        @opened-changed=${this._openedChanged}
        @value-changed=${this._valueChanged}
      >
        ${this._value||this.placeholder?o.qy`
              <ha-icon .icon=${this._value||this.placeholder} slot="icon">
              </ha-icon>
            `:o.qy`<slot slot="icon" name="fallback"></slot>`}
      </ha-combo-box>
    `}async _openedChanged(e){e.detail.value&&!c&&(await(async()=>{c=!0;const e=await i.e("4765").then(i.t.bind(i,43692,19));h=e.default.map((e=>({icon:`mdi:${e.name}`,parts:new Set(e.name.split("-")),keywords:e.keywords})));const t=[];Object.keys(l.y).forEach((e=>{t.push(d(e))})),(await Promise.all(t)).forEach((e=>{h.push(...e)}))})(),this.requestUpdate())}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,n.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.invalid=!1,this._filterIcons=(0,r.A)(((e,t=h)=>{if(!e)return t;const i=[],a=(e,t)=>i.push({icon:e,rank:t});for(const o of t)o.parts.has(e)?a(o.icon,1):o.keywords.includes(e)?a(o.icon,2):o.icon.includes(e)?a(o.icon,3):o.keywords.some((t=>t.includes(e)))&&a(o.icon,4);return 0===i.length&&a(e,0),i.sort(((e,t)=>e.rank-t.rank))})),this._iconProvider=(e,t)=>{const i=this._filterIcons(e.filter.toLowerCase(),h),a=e.page*e.pageSize,o=a+e.pageSize;t(i.slice(a,o),i.length)}}}p.styles=o.AH`
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
  `,(0,a.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)()],p.prototype,"value",void 0),(0,a.__decorate)([(0,s.MZ)()],p.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)()],p.prototype,"helper",void 0),(0,a.__decorate)([(0,s.MZ)()],p.prototype,"placeholder",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"error-message"})],p.prototype,"errorMessage",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],p.prototype,"invalid",void 0),p=(0,a.__decorate)([(0,s.EM)("ha-icon-picker")],p)},23344:function(e,t,i){i.r(t);var a=i(69868),o=i(84922),s=i(11991),r=i(73120),n=(i(99741),i(15785),i(43143),i(11934),i(83566));class l extends o.WF{set item(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||"",this._maximum=e.maximum??void 0,this._minimum=e.minimum??void 0,this._restore=e.restore??!0,this._step=e.step??1,this._initial=e.initial??0):(this._name="",this._icon="",this._maximum=void 0,this._minimum=void 0,this._restore=!0,this._step=1,this._initial=0)}focus(){this.updateComplete.then((()=>this.shadowRoot?.querySelector("[dialogInitialFocus]")?.focus()))}render(){return this.hass?o.qy`
      <div class="form">
        <ha-textfield
          .value=${this._name}
          .configValue=${"name"}
          @input=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.generic.name")}
          autoValidate
          required
          .validationMessage=${this.hass.localize("ui.dialogs.helper_settings.required_error_msg")}
          dialogInitialFocus
        ></ha-textfield>
        <ha-icon-picker
          .hass=${this.hass}
          .value=${this._icon}
          .configValue=${"icon"}
          @value-changed=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.generic.icon")}
        ></ha-icon-picker>
        <ha-textfield
          .value=${this._minimum}
          .configValue=${"minimum"}
          type="number"
          @input=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.counter.minimum")}
        ></ha-textfield>
        <ha-textfield
          .value=${this._maximum}
          .configValue=${"maximum"}
          type="number"
          @input=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.counter.maximum")}
        ></ha-textfield>
        <ha-textfield
          .value=${this._initial}
          .configValue=${"initial"}
          type="number"
          @input=${this._valueChanged}
          .label=${this.hass.localize("ui.dialogs.helper_settings.counter.initial")}
        ></ha-textfield>
        <ha-expansion-panel
          header=${this.hass.localize("ui.dialogs.helper_settings.generic.advanced_settings")}
          outlined
        >
          <ha-textfield
            .value=${this._step}
            .configValue=${"step"}
            type="number"
            @input=${this._valueChanged}
            .label=${this.hass.localize("ui.dialogs.helper_settings.counter.step")}
          ></ha-textfield>
          <div class="row">
            <ha-switch
              .checked=${this._restore}
              .configValue=${"restore"}
              @change=${this._valueChanged}
            >
            </ha-switch>
            <div>
              ${this.hass.localize("ui.dialogs.helper_settings.counter.restore")}
            </div>
          </div>
        </ha-expansion-panel>
      </div>
    `:o.s6}_valueChanged(e){if(!this.new&&!this._item)return;e.stopPropagation();const t=e.target,i=t.configValue,a="number"===t.type?""!==t.value?Number(t.value):void 0:"ha-switch"===t.localName?e.target.checked:e.detail?.value||t.value;if(this[`_${i}`]===a)return;const o={...this._item};void 0===a||""===a?delete o[i]:o[i]=a,(0,r.r)(this,"value-changed",{value:o})}static get styles(){return[n.RF,o.AH`
        .form {
          color: var(--primary-text-color);
        }
        .row {
          margin-top: 12px;
          margin-bottom: 12px;
          color: var(--primary-text-color);
          display: flex;
          align-items: center;
        }
        .row div {
          margin-left: 16px;
          margin-inline-start: 16px;
          margin-inline-end: initial;
        }
        ha-textfield {
          display: block;
          margin: 8px 0;
        }
      `]}constructor(...e){super(...e),this.new=!1}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],l.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],l.prototype,"new",void 0),(0,a.__decorate)([(0,s.wk)()],l.prototype,"_name",void 0),(0,a.__decorate)([(0,s.wk)()],l.prototype,"_icon",void 0),(0,a.__decorate)([(0,s.wk)()],l.prototype,"_maximum",void 0),(0,a.__decorate)([(0,s.wk)()],l.prototype,"_minimum",void 0),(0,a.__decorate)([(0,s.wk)()],l.prototype,"_restore",void 0),(0,a.__decorate)([(0,s.wk)()],l.prototype,"_initial",void 0),(0,a.__decorate)([(0,s.wk)()],l.prototype,"_step",void 0),l=(0,a.__decorate)([(0,s.EM)("ha-counter-form")],l)}};
//# sourceMappingURL=2809.bbeeab3e4c582d74.js.map