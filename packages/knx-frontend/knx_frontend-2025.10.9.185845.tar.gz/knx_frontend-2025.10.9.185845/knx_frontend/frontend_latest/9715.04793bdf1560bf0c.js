export const __webpack_id__="9715";export const __webpack_ids__=["9715"];export const __webpack_modules__={96957:function(e,t,a){a.a(e,(async function(e,o){try{a.r(t),a.d(t,{HaTemplateSelector:()=>p});var r=a(69868),s=a(84922),i=a(11991),n=a(73120),l=a(86435),d=a(84810),c=(a(20014),a(23749),e([d]));d=(c.then?(await c)():c)[0];const h=["template:","sensor:","state:","trigger: template"];class p extends s.WF{render(){return s.qy`
      ${this.warn?s.qy`<ha-alert alert-type="warning"
            >${this.hass.localize("ui.components.selectors.template.yaml_warning",{string:this.warn})}
            <br />
            <a
              target="_blank"
              rel="noopener noreferrer"
              href=${(0,l.o)(this.hass,"/docs/configuration/templating/")}
              >${this.hass.localize("ui.components.selectors.template.learn_more")}</a
            ></ha-alert
          >`:s.s6}
      ${this.label?s.qy`<p>${this.label}${this.required?"*":""}</p>`:s.s6}
      <ha-code-editor
        mode="jinja2"
        .hass=${this.hass}
        .value=${this.value}
        .readOnly=${this.disabled}
        autofocus
        autocomplete-entities
        autocomplete-icons
        @value-changed=${this._handleChange}
        dir="ltr"
        linewrap
      ></ha-code-editor>
      ${this.helper?s.qy`<ha-input-helper-text .disabled=${this.disabled}
            >${this.helper}</ha-input-helper-text
          >`:s.s6}
    `}_handleChange(e){e.stopPropagation();let t=e.target.value;this.value!==t&&(this.warn=h.find((e=>t.includes(e))),""!==t||this.required||(t=void 0),(0,n.r)(this,"value-changed",{value:t}))}constructor(...e){super(...e),this.disabled=!1,this.required=!0,this.warn=void 0}}p.styles=s.AH`
    p {
      margin-top: 0;
    }
  `,(0,r.__decorate)([(0,i.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,r.__decorate)([(0,i.MZ)()],p.prototype,"value",void 0),(0,r.__decorate)([(0,i.MZ)()],p.prototype,"label",void 0),(0,r.__decorate)([(0,i.MZ)()],p.prototype,"helper",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,r.__decorate)([(0,i.wk)()],p.prototype,"warn",void 0),p=(0,r.__decorate)([(0,i.EM)("ha-selector-template")],p),o()}catch(h){o(h)}}))},86435:function(e,t,a){a.d(t,{o:()=>o});const o=(e,t)=>`https://${e.config.version.includes("b")?"rc":e.config.version.includes("dev")?"next":"www"}.home-assistant.io${t}`},72698:function(e,t,a){a.d(t,{P:()=>r});var o=a(73120);const r=(e,t)=>(0,o.r)(e,"hass-notification",t)}};
//# sourceMappingURL=9715.04793bdf1560bf0c.js.map