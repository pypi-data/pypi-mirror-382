"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["1262"],{28052:function(e,t,o){o.a(e,(async function(e,t){try{o(35748),o(35058),o(65315),o(837),o(5934),o(95013);var a=o(69868),s=o(84922),r=o(11991),i=o(10763),n=o(73120),d=o(90963),l=o(20606),c=(o(23749),o(5177)),h=(o(36137),e([c]));c=(h.then?(await h)():h)[0];let p,u,_,v,y=e=>e;const b=e=>(0,s.qy)(p||(p=y`
  <ha-combo-box-item type="button">
    <span slot="headline">${0}</span>
    <span slot="supporting-text">${0}</span>
    ${0}
  </ha-combo-box-item>
`),e.name,e.slug,e.icon?(0,s.qy)(u||(u=y`
          <img
            alt=""
            slot="start"
            .src="/api/hassio/addons/${0}/icon"
          />
        `),e.slug):s.s6);class m extends s.WF{open(){var e;null===(e=this._comboBox)||void 0===e||e.open()}focus(){var e;null===(e=this._comboBox)||void 0===e||e.focus()}firstUpdated(){this._getAddons()}render(){return this._error?(0,s.qy)(_||(_=y`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):this._addons?(0,s.qy)(v||(v=y`
      <ha-combo-box
        .hass=${0}
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        .helper=${0}
        .renderer=${0}
        .items=${0}
        item-value-path="slug"
        item-id-path="slug"
        item-label-path="name"
        @value-changed=${0}
      ></ha-combo-box>
    `),this.hass,void 0===this.label&&this.hass?this.hass.localize("ui.components.addon-picker.addon"):this.label,this._value,this.required,this.disabled,this.helper,b,this._addons,this._addonChanged):s.s6}async _getAddons(){try{if((0,i.x)(this.hass,"hassio")){const e=await(0,l.b3)(this.hass);this._addons=e.addons.filter((e=>e.version)).sort(((e,t)=>(0,d.xL)(e.name,t.name,this.hass.locale.language)))}else this._error=this.hass.localize("ui.components.addon-picker.error.no_supervisor")}catch(e){this._error=this.hass.localize("ui.components.addon-picker.error.fetch_addons")}}get _value(){return this.value||""}_addonChanged(e){e.stopPropagation();const t=e.detail.value;t!==this._value&&this._setValue(t)}_setValue(e){this.value=e,setTimeout((()=>{(0,n.r)(this,"value-changed",{value:e}),(0,n.r)(this,"change")}),0)}constructor(...e){super(...e),this.value="",this.disabled=!1,this.required=!1}}(0,a.__decorate)([(0,r.MZ)()],m.prototype,"label",void 0),(0,a.__decorate)([(0,r.MZ)()],m.prototype,"value",void 0),(0,a.__decorate)([(0,r.MZ)()],m.prototype,"helper",void 0),(0,a.__decorate)([(0,r.wk)()],m.prototype,"_addons",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],m.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],m.prototype,"required",void 0),(0,a.__decorate)([(0,r.P)("ha-combo-box")],m.prototype,"_comboBox",void 0),(0,a.__decorate)([(0,r.wk)()],m.prototype,"_error",void 0),m=(0,a.__decorate)([(0,r.EM)("ha-addon-picker")],m),t()}catch(p){t(p)}}))},11629:function(e,t,o){o.a(e,(async function(e,a){try{o.r(t),o.d(t,{HaAddonSelector:function(){return p}});o(35748),o(95013);var s=o(69868),r=o(84922),i=o(11991),n=o(28052),d=e([n]);n=(d.then?(await d)():d)[0];let l,c,h=e=>e;class p extends r.WF{render(){return(0,r.qy)(l||(l=h`<ha-addon-picker
      .hass=${0}
      .value=${0}
      .label=${0}
      .helper=${0}
      .disabled=${0}
      .required=${0}
      allow-custom-entity
    ></ha-addon-picker>`),this.hass,this.value,this.label,this.helper,this.disabled,this.required)}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}p.styles=(0,r.AH)(c||(c=h`
    ha-addon-picker {
      width: 100%;
    }
  `)),(0,s.__decorate)([(0,i.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,s.__decorate)([(0,i.MZ)({attribute:!1})],p.prototype,"selector",void 0),(0,s.__decorate)([(0,i.MZ)()],p.prototype,"value",void 0),(0,s.__decorate)([(0,i.MZ)()],p.prototype,"label",void 0),(0,s.__decorate)([(0,i.MZ)()],p.prototype,"helper",void 0),(0,s.__decorate)([(0,i.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,s.__decorate)([(0,i.MZ)({type:Boolean})],p.prototype,"required",void 0),p=(0,s.__decorate)([(0,i.EM)("ha-selector-addon")],p),a()}catch(l){a(l)}}))},20606:function(e,t,o){o.d(t,{xG:function(){return n},b3:function(){return r},eK:function(){return i}});o(46852),o(65315),o(84136),o(5934);var a=o(86543),s=o(38);const r=async e=>(0,a.v)(e.config.version,2021,2,4)?e.callWS({type:"supervisor/api",endpoint:"/addons",method:"get"}):(0,s.PS)(await e.callApi("GET","hassio/addons")),i=async(e,t)=>(0,a.v)(e.config.version,2021,2,4)?e.callWS({type:"supervisor/api",endpoint:`/addons/${t}/start`,method:"post",timeout:null}):e.callApi("POST",`hassio/addons/${t}/start`),n=async(e,t)=>{(0,a.v)(e.config.version,2021,2,4)?await e.callWS({type:"supervisor/api",endpoint:`/addons/${t}/install`,method:"post",timeout:null}):await e.callApi("POST",`hassio/addons/${t}/install`)}},38:function(e,t,o){o.d(t,{PS:function(){return a},VR:function(){return s}});o(79827),o(35748),o(5934),o(88238),o(34536),o(16257),o(20152),o(44711),o(72108),o(77030),o(18223),o(95013),o(86543);const a=e=>e.data,s=e=>"object"==typeof e?"object"==typeof e.body?e.body.message||"Unknown error, see supervisor logs":e.body||e.message||"Unknown error, see supervisor logs":e;new Set([502,503,504])}}]);
//# sourceMappingURL=1262.673de608a14c0a69.js.map