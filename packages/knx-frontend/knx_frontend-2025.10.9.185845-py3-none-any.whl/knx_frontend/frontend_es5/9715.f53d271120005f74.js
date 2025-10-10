"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["9715"],{96957:function(e,t,a){a.a(e,(async function(e,o){try{a.r(t),a.d(t,{HaTemplateSelector:function(){return g}});a(79827),a(35748),a(18223),a(95013);var r=a(69868),i=a(84922),n=a(11991),s=a(73120),l=a(86435),d=a(84810),h=(a(20014),a(23749),e([d]));d=(h.then?(await h)():h)[0];let c,p,u,_,v,f=e=>e;const y=["template:","sensor:","state:","trigger: template"];class g extends i.WF{render(){return(0,i.qy)(c||(c=f`
      ${0}
      ${0}
      <ha-code-editor
        mode="jinja2"
        .hass=${0}
        .value=${0}
        .readOnly=${0}
        autofocus
        autocomplete-entities
        autocomplete-icons
        @value-changed=${0}
        dir="ltr"
        linewrap
      ></ha-code-editor>
      ${0}
    `),this.warn?(0,i.qy)(p||(p=f`<ha-alert alert-type="warning"
            >${0}
            <br />
            <a
              target="_blank"
              rel="noopener noreferrer"
              href=${0}
              >${0}</a
            ></ha-alert
          >`),this.hass.localize("ui.components.selectors.template.yaml_warning",{string:this.warn}),(0,l.o)(this.hass,"/docs/configuration/templating/"),this.hass.localize("ui.components.selectors.template.learn_more")):i.s6,this.label?(0,i.qy)(u||(u=f`<p>${0}${0}</p>`),this.label,this.required?"*":""):i.s6,this.hass,this.value,this.disabled,this._handleChange,this.helper?(0,i.qy)(_||(_=f`<ha-input-helper-text .disabled=${0}
            >${0}</ha-input-helper-text
          >`),this.disabled,this.helper):i.s6)}_handleChange(e){e.stopPropagation();let t=e.target.value;this.value!==t&&(this.warn=y.find((e=>t.includes(e))),""!==t||this.required||(t=void 0),(0,s.r)(this,"value-changed",{value:t}))}constructor(...e){super(...e),this.disabled=!1,this.required=!0,this.warn=void 0}}g.styles=(0,i.AH)(v||(v=f`
    p {
      margin-top: 0;
    }
  `)),(0,r.__decorate)([(0,n.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,r.__decorate)([(0,n.MZ)()],g.prototype,"value",void 0),(0,r.__decorate)([(0,n.MZ)()],g.prototype,"label",void 0),(0,r.__decorate)([(0,n.MZ)()],g.prototype,"helper",void 0),(0,r.__decorate)([(0,n.MZ)({type:Boolean})],g.prototype,"disabled",void 0),(0,r.__decorate)([(0,n.MZ)({type:Boolean})],g.prototype,"required",void 0),(0,r.__decorate)([(0,n.wk)()],g.prototype,"warn",void 0),g=(0,r.__decorate)([(0,n.EM)("ha-selector-template")],g),o()}catch(c){o(c)}}))},86435:function(e,t,a){a.d(t,{o:function(){return o}});a(79827),a(18223);const o=(e,t)=>`https://${e.config.version.includes("b")?"rc":e.config.version.includes("dev")?"next":"www"}.home-assistant.io${t}`},72698:function(e,t,a){a.d(t,{P:function(){return r}});var o=a(73120);const r=(e,t)=>(0,o.r)(e,"hass-notification",t)}}]);
//# sourceMappingURL=9715.f53d271120005f74.js.map