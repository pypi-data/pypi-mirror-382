export const __webpack_id__="6107";export const __webpack_ids__=["6107"];export const __webpack_modules__={75518:function(e,t,a){var r=a(69868),o=a(84922),s=a(11991),i=a(21431),n=a(73120);a(23749),a(57674);const l={boolean:()=>a.e("2436").then(a.bind(a,33999)),constant:()=>a.e("3668").then(a.bind(a,33855)),float:()=>a.e("742").then(a.bind(a,84053)),grid:()=>a.e("7828").then(a.bind(a,57311)),expandable:()=>a.e("364").then(a.bind(a,51079)),integer:()=>a.e("7346").then(a.bind(a,40681)),multi_select:()=>Promise.all([a.e("6216"),a.e("3706")]).then(a.bind(a,99681)),positive_time_period_dict:()=>a.e("3540").then(a.bind(a,87551)),select:()=>a.e("2500").then(a.bind(a,10079)),string:()=>a.e("3627").then(a.bind(a,10070)),optional_actions:()=>a.e("3044").then(a.bind(a,96943))},c=(e,t)=>e?!t.name||t.flatten?e:e[t.name]:null;class h extends o.WF{getFormProperties(){return{}}async focus(){await this.updateComplete;const e=this.renderRoot.querySelector(".root");if(e)for(const t of e.children)if("HA-ALERT"!==t.tagName){t instanceof o.mN&&await t.updateComplete,t.focus();break}}willUpdate(e){e.has("schema")&&this.schema&&this.schema.forEach((e=>{"selector"in e||l[e.type]?.()}))}render(){return o.qy`
      <div class="root" part="root">
        ${this.error&&this.error.base?o.qy`
              <ha-alert alert-type="error">
                ${this._computeError(this.error.base,this.schema)}
              </ha-alert>
            `:""}
        ${this.schema.map((e=>{const t=((e,t)=>e&&t.name?e[t.name]:null)(this.error,e),a=((e,t)=>e&&t.name?e[t.name]:null)(this.warning,e);return o.qy`
            ${t?o.qy`
                  <ha-alert own-margin alert-type="error">
                    ${this._computeError(t,e)}
                  </ha-alert>
                `:a?o.qy`
                    <ha-alert own-margin alert-type="warning">
                      ${this._computeWarning(a,e)}
                    </ha-alert>
                  `:""}
            ${"selector"in e?o.qy`<ha-selector
                  .schema=${e}
                  .hass=${this.hass}
                  .narrow=${this.narrow}
                  .name=${e.name}
                  .selector=${e.selector}
                  .value=${c(this.data,e)}
                  .label=${this._computeLabel(e,this.data)}
                  .disabled=${e.disabled||this.disabled||!1}
                  .placeholder=${e.required?"":e.default}
                  .helper=${this._computeHelper(e)}
                  .localizeValue=${this.localizeValue}
                  .required=${e.required||!1}
                  .context=${this._generateContext(e)}
                ></ha-selector>`:(0,i._)(this.fieldElementName(e.type),{schema:e,data:c(this.data,e),label:this._computeLabel(e,this.data),helper:this._computeHelper(e),disabled:this.disabled||e.disabled||!1,hass:this.hass,localize:this.hass?.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(e),...this.getFormProperties()})}
          `}))}
      </div>
    `}fieldElementName(e){return`ha-form-${e}`}_generateContext(e){if(!e.context)return;const t={};for(const[a,r]of Object.entries(e.context))t[a]=this.data[r];return t}createRenderRoot(){const e=super.createRenderRoot();return this.addValueChangedListener(e),e}addValueChangedListener(e){e.addEventListener("value-changed",(e=>{e.stopPropagation();const t=e.target.schema;if(e.target===this)return;const a=!t.name||"flatten"in t&&t.flatten?e.detail.value:{[t.name]:e.detail.value};this.data={...this.data,...a},(0,n.r)(this,"value-changed",{value:this.data})}))}_computeLabel(e,t){return this.computeLabel?this.computeLabel(e,t):e?e.name:""}_computeHelper(e){return this.computeHelper?this.computeHelper(e):""}_computeError(e,t){return Array.isArray(e)?o.qy`<ul>
        ${e.map((e=>o.qy`<li>
              ${this.computeError?this.computeError(e,t):e}
            </li>`))}
      </ul>`:this.computeError?this.computeError(e,t):e}_computeWarning(e,t){return this.computeWarning?this.computeWarning(e,t):e}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1}}h.styles=o.AH`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `,(0,r.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,r.__decorate)([(0,s.MZ)({type:Boolean})],h.prototype,"narrow",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"data",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"schema",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"error",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"warning",void 0),(0,r.__decorate)([(0,s.MZ)({type:Boolean})],h.prototype,"disabled",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"computeError",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"computeWarning",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"computeLabel",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"computeHelper",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"localizeValue",void 0),h=(0,r.__decorate)([(0,s.EM)("ha-form")],h)},90806:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t);var o=a(69868),s=a(84922),i=a(65940),n=a(11991),l=a(73120),c=a(72847),h=(a(75518),a(76943)),d=a(83566),p=e([h]);h=(p.then?(await p)():p)[0];class u extends s.WF{showDialog(e){this._params=e,this._error=void 0,this._data=e.block,this._expand=!!e.block?.data}closeDialog(){this._params=void 0,this._data=void 0,(0,l.r)(this,"dialog-closed",{dialog:this.localName})}render(){return this._params&&this._data?s.qy`
      <ha-dialog
        open
        @closed=${this.closeDialog}
        .heading=${(0,c.l)(this.hass,this.hass.localize("ui.dialogs.helper_settings.schedule.edit_schedule_block"))}
      >
        <div>
          <ha-form
            .hass=${this.hass}
            .schema=${this._schema(this._expand)}
            .data=${this._data}
            .error=${this._error}
            .computeLabel=${this._computeLabelCallback}
            @value-changed=${this._valueChanged}
          ></ha-form>
        </div>
        <ha-button
          slot="secondaryAction"
          @click=${this._deleteBlock}
          appearance="plain"
          variant="danger"
        >
          ${this.hass.localize("ui.common.delete")}
        </ha-button>
        <ha-button slot="primaryAction" @click=${this._updateBlock}>
          ${this.hass.localize("ui.common.save")}
        </ha-button>
      </ha-dialog>
    `:s.s6}_valueChanged(e){this._error=void 0,this._data=e.detail.value}_updateBlock(){try{this._params.updateBlock(this._data),this.closeDialog()}catch(e){this._error={base:e?e.message:"Unknown error"}}}_deleteBlock(){try{this._params.deleteBlock(),this.closeDialog()}catch(e){this._error={base:e?e.message:"Unknown error"}}}static get styles(){return[d.nA]}constructor(...e){super(...e),this._expand=!1,this._schema=(0,i.A)((e=>[{name:"from",required:!0,selector:{time:{no_second:!0}}},{name:"to",required:!0,selector:{time:{no_second:!0}}},{name:"advanced_settings",type:"expandable",flatten:!0,expanded:e,schema:[{name:"data",required:!1,selector:{object:{}}}]}])),this._computeLabelCallback=e=>{switch(e.name){case"from":return this.hass.localize("ui.dialogs.helper_settings.schedule.start");case"to":return this.hass.localize("ui.dialogs.helper_settings.schedule.end");case"data":return this.hass.localize("ui.dialogs.helper_settings.schedule.data");case"advanced_settings":return this.hass.localize("ui.dialogs.helper_settings.generic.advanced_settings")}return""}}}(0,o.__decorate)([(0,n.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,o.__decorate)([(0,n.wk)()],u.prototype,"_error",void 0),(0,o.__decorate)([(0,n.wk)()],u.prototype,"_data",void 0),(0,o.__decorate)([(0,n.wk)()],u.prototype,"_params",void 0),customElements.define("dialog-schedule-block-info",u),r()}catch(u){r(u)}}))}};
//# sourceMappingURL=6107.f396e8c816a9437b.js.map