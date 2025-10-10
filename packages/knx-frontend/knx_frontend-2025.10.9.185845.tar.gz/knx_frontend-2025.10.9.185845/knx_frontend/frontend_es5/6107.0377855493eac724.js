"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["6107"],{75518:function(e,t,a){a(35748),a(65315),a(22416),a(37089),a(12977),a(5934),a(95013);var r=a(69868),o=a(84922),s=a(11991),i=a(21431),n=a(73120);a(23749),a(57674);let l,c,h,d,u,p,m,_,b,g=e=>e;const v={boolean:()=>a.e("2436").then(a.bind(a,33999)),constant:()=>a.e("3668").then(a.bind(a,33855)),float:()=>a.e("742").then(a.bind(a,84053)),grid:()=>a.e("7828").then(a.bind(a,57311)),expandable:()=>a.e("364").then(a.bind(a,51079)),integer:()=>a.e("7346").then(a.bind(a,40681)),multi_select:()=>Promise.all([a.e("6216"),a.e("3706")]).then(a.bind(a,99681)),positive_time_period_dict:()=>a.e("3540").then(a.bind(a,87551)),select:()=>a.e("2500").then(a.bind(a,10079)),string:()=>a.e("3627").then(a.bind(a,10070)),optional_actions:()=>a.e("3044").then(a.bind(a,96943))},y=(e,t)=>e?!t.name||t.flatten?e:e[t.name]:null;class f extends o.WF{getFormProperties(){return{}}async focus(){await this.updateComplete;const e=this.renderRoot.querySelector(".root");if(e)for(const t of e.children)if("HA-ALERT"!==t.tagName){t instanceof o.mN&&await t.updateComplete,t.focus();break}}willUpdate(e){e.has("schema")&&this.schema&&this.schema.forEach((e=>{var t;"selector"in e||null===(t=v[e.type])||void 0===t||t.call(v)}))}render(){return(0,o.qy)(l||(l=g`
      <div class="root" part="root">
        ${0}
        ${0}
      </div>
    `),this.error&&this.error.base?(0,o.qy)(c||(c=g`
              <ha-alert alert-type="error">
                ${0}
              </ha-alert>
            `),this._computeError(this.error.base,this.schema)):"",this.schema.map((e=>{var t;const a=((e,t)=>e&&t.name?e[t.name]:null)(this.error,e),r=((e,t)=>e&&t.name?e[t.name]:null)(this.warning,e);return(0,o.qy)(h||(h=g`
            ${0}
            ${0}
          `),a?(0,o.qy)(d||(d=g`
                  <ha-alert own-margin alert-type="error">
                    ${0}
                  </ha-alert>
                `),this._computeError(a,e)):r?(0,o.qy)(u||(u=g`
                    <ha-alert own-margin alert-type="warning">
                      ${0}
                    </ha-alert>
                  `),this._computeWarning(r,e)):"","selector"in e?(0,o.qy)(p||(p=g`<ha-selector
                  .schema=${0}
                  .hass=${0}
                  .narrow=${0}
                  .name=${0}
                  .selector=${0}
                  .value=${0}
                  .label=${0}
                  .disabled=${0}
                  .placeholder=${0}
                  .helper=${0}
                  .localizeValue=${0}
                  .required=${0}
                  .context=${0}
                ></ha-selector>`),e,this.hass,this.narrow,e.name,e.selector,y(this.data,e),this._computeLabel(e,this.data),e.disabled||this.disabled||!1,e.required?"":e.default,this._computeHelper(e),this.localizeValue,e.required||!1,this._generateContext(e)):(0,i._)(this.fieldElementName(e.type),Object.assign({schema:e,data:y(this.data,e),label:this._computeLabel(e,this.data),helper:this._computeHelper(e),disabled:this.disabled||e.disabled||!1,hass:this.hass,localize:null===(t=this.hass)||void 0===t?void 0:t.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(e)},this.getFormProperties())))})))}fieldElementName(e){return`ha-form-${e}`}_generateContext(e){if(!e.context)return;const t={};for(const[a,r]of Object.entries(e.context))t[a]=this.data[r];return t}createRenderRoot(){const e=super.createRenderRoot();return this.addValueChangedListener(e),e}addValueChangedListener(e){e.addEventListener("value-changed",(e=>{e.stopPropagation();const t=e.target.schema;if(e.target===this)return;const a=!t.name||"flatten"in t&&t.flatten?e.detail.value:{[t.name]:e.detail.value};this.data=Object.assign(Object.assign({},this.data),a),(0,n.r)(this,"value-changed",{value:this.data})}))}_computeLabel(e,t){return this.computeLabel?this.computeLabel(e,t):e?e.name:""}_computeHelper(e){return this.computeHelper?this.computeHelper(e):""}_computeError(e,t){return Array.isArray(e)?(0,o.qy)(m||(m=g`<ul>
        ${0}
      </ul>`),e.map((e=>(0,o.qy)(_||(_=g`<li>
              ${0}
            </li>`),this.computeError?this.computeError(e,t):e)))):this.computeError?this.computeError(e,t):e}_computeWarning(e,t){return this.computeWarning?this.computeWarning(e,t):e}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1}}f.styles=(0,o.AH)(b||(b=g`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `)),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,r.__decorate)([(0,s.MZ)({type:Boolean})],f.prototype,"narrow",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"data",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"schema",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"error",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"warning",void 0),(0,r.__decorate)([(0,s.MZ)({type:Boolean})],f.prototype,"disabled",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"computeError",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"computeWarning",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"computeLabel",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"computeHelper",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"localizeValue",void 0),f=(0,r.__decorate)([(0,s.EM)("ha-form")],f)},90806:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t);a(35748),a(95013);var o=a(69868),s=a(84922),i=a(65940),n=a(11991),l=a(73120),c=a(72847),h=(a(75518),a(76943)),d=a(83566),u=e([h]);h=(u.then?(await u)():u)[0];let p,m=e=>e;class _ extends s.WF{showDialog(e){var t;this._params=e,this._error=void 0,this._data=e.block,this._expand=!(null===(t=e.block)||void 0===t||!t.data)}closeDialog(){this._params=void 0,this._data=void 0,(0,l.r)(this,"dialog-closed",{dialog:this.localName})}render(){return this._params&&this._data?(0,s.qy)(p||(p=m`
      <ha-dialog
        open
        @closed=${0}
        .heading=${0}
      >
        <div>
          <ha-form
            .hass=${0}
            .schema=${0}
            .data=${0}
            .error=${0}
            .computeLabel=${0}
            @value-changed=${0}
          ></ha-form>
        </div>
        <ha-button
          slot="secondaryAction"
          @click=${0}
          appearance="plain"
          variant="danger"
        >
          ${0}
        </ha-button>
        <ha-button slot="primaryAction" @click=${0}>
          ${0}
        </ha-button>
      </ha-dialog>
    `),this.closeDialog,(0,c.l)(this.hass,this.hass.localize("ui.dialogs.helper_settings.schedule.edit_schedule_block")),this.hass,this._schema(this._expand),this._data,this._error,this._computeLabelCallback,this._valueChanged,this._deleteBlock,this.hass.localize("ui.common.delete"),this._updateBlock,this.hass.localize("ui.common.save")):s.s6}_valueChanged(e){this._error=void 0,this._data=e.detail.value}_updateBlock(){try{this._params.updateBlock(this._data),this.closeDialog()}catch(e){this._error={base:e?e.message:"Unknown error"}}}_deleteBlock(){try{this._params.deleteBlock(),this.closeDialog()}catch(e){this._error={base:e?e.message:"Unknown error"}}}static get styles(){return[d.nA]}constructor(...e){super(...e),this._expand=!1,this._schema=(0,i.A)((e=>[{name:"from",required:!0,selector:{time:{no_second:!0}}},{name:"to",required:!0,selector:{time:{no_second:!0}}},{name:"advanced_settings",type:"expandable",flatten:!0,expanded:e,schema:[{name:"data",required:!1,selector:{object:{}}}]}])),this._computeLabelCallback=e=>{switch(e.name){case"from":return this.hass.localize("ui.dialogs.helper_settings.schedule.start");case"to":return this.hass.localize("ui.dialogs.helper_settings.schedule.end");case"data":return this.hass.localize("ui.dialogs.helper_settings.schedule.data");case"advanced_settings":return this.hass.localize("ui.dialogs.helper_settings.generic.advanced_settings")}return""}}}(0,o.__decorate)([(0,n.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,o.__decorate)([(0,n.wk)()],_.prototype,"_error",void 0),(0,o.__decorate)([(0,n.wk)()],_.prototype,"_data",void 0),(0,o.__decorate)([(0,n.wk)()],_.prototype,"_params",void 0),customElements.define("dialog-schedule-block-info",_),r()}catch(p){r(p)}}))}}]);
//# sourceMappingURL=6107.0377855493eac724.js.map