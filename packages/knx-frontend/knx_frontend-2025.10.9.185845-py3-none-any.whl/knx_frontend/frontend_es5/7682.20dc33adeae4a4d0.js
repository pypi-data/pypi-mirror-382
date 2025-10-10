"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["7682"],{13125:function(e,t,a){a.a(e,(async function(e,l){try{a.d(t,{T:function(){return n}});var i=a(96904),o=a(65940),s=e([i]);i=(s.then?(await s)():s)[0];const n=(e,t)=>{try{var a,l;return null!==(a=null===(l=r(t))||void 0===l?void 0:l.of(e))&&void 0!==a?a:e}catch(i){return e}},r=(0,o.A)((e=>new Intl.DisplayNames(e.language,{type:"language",fallback:"code"})));l()}catch(n){l(n)}}))},86480:function(e,t,a){a.a(e,(async function(e,l){try{a.d(t,{t:function(){return m}});var i=a(96904),o=(a(35748),a(35058),a(65315),a(37089),a(95013),a(69868)),s=a(84922),n=a(11991),r=a(65940),u=a(73120),d=a(20674),h=a(13125),c=a(90963),v=a(42983),g=(a(25223),a(37207),e([i,h]));[i,h]=g.then?(await g)():g;let p,_,y,b,f=e=>e;const m=(e,t,a,l)=>{let i=[];if(t){const t=v.P.translations;i=e.map((e=>{var a;let l=null===(a=t[e])||void 0===a?void 0:a.nativeName;if(!l)try{l=new Intl.DisplayNames(e,{type:"language",fallback:"code"}).of(e)}catch(i){l=e}return{value:e,label:l}}))}else l&&(i=e.map((e=>({value:e,label:(0,h.T)(e,l)}))));return!a&&l&&i.sort(((e,t)=>(0,c.SH)(e.label,t.label,l.language))),i};class M extends s.WF{firstUpdated(e){super.firstUpdated(e),this._computeDefaultLanguageOptions()}updated(e){super.updated(e);const t=e.has("hass")&&this.hass&&e.get("hass")&&e.get("hass").locale.language!==this.hass.locale.language;if(e.has("languages")||e.has("value")||t){var a,l;if(this._select.layoutOptions(),this.disabled||this._select.value===this.value||(0,u.r)(this,"value-changed",{value:this._select.value}),!this.value)return;const e=this._getLanguagesOptions(null!==(a=this.languages)&&void 0!==a?a:this._defaultLanguages,this.nativeName,this.noSort,null===(l=this.hass)||void 0===l?void 0:l.locale).findIndex((e=>e.value===this.value));-1===e&&(this.value=void 0),t&&this._select.select(e)}}_computeDefaultLanguageOptions(){this._defaultLanguages=Object.keys(v.P.translations)}render(){var e,t,a,l,i,o,n;const r=this._getLanguagesOptions(null!==(e=this.languages)&&void 0!==e?e:this._defaultLanguages,this.nativeName,this.noSort,null===(t=this.hass)||void 0===t?void 0:t.locale),u=null!==(a=this.value)&&void 0!==a?a:this.required&&!this.disabled?null===(l=r[0])||void 0===l?void 0:l.value:this.value;return(0,s.qy)(p||(p=f`
      <ha-select
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        @selected=${0}
        @closed=${0}
        fixedMenuPosition
        naturalMenuWidth
        .inlineArrow=${0}
      >
        ${0}
      </ha-select>
    `),null!==(i=this.label)&&void 0!==i?i:(null===(o=this.hass)||void 0===o?void 0:o.localize("ui.components.language-picker.language"))||"Language",u||"",this.required,this.disabled,this._changed,d.d,this.inlineArrow,0===r.length?(0,s.qy)(_||(_=f`<ha-list-item value=""
              >${0}</ha-list-item
            >`),(null===(n=this.hass)||void 0===n?void 0:n.localize("ui.components.language-picker.no_languages"))||"No languages"):r.map((e=>(0,s.qy)(y||(y=f`
                <ha-list-item .value=${0}
                  >${0}</ha-list-item
                >
              `),e.value,e.label))))}_changed(e){const t=e.target;this.disabled||""===t.value||t.value===this.value||(this.value=t.value,(0,u.r)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.nativeName=!1,this.noSort=!1,this.inlineArrow=!1,this._defaultLanguages=[],this._getLanguagesOptions=(0,r.A)(m)}}M.styles=(0,s.AH)(b||(b=f`
    ha-select {
      width: 100%;
    }
  `)),(0,o.__decorate)([(0,n.MZ)()],M.prototype,"value",void 0),(0,o.__decorate)([(0,n.MZ)()],M.prototype,"label",void 0),(0,o.__decorate)([(0,n.MZ)({type:Array})],M.prototype,"languages",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],M.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],M.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],M.prototype,"required",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"native-name",type:Boolean})],M.prototype,"nativeName",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"no-sort",type:Boolean})],M.prototype,"noSort",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"inline-arrow",type:Boolean})],M.prototype,"inlineArrow",void 0),(0,o.__decorate)([(0,n.wk)()],M.prototype,"_defaultLanguages",void 0),(0,o.__decorate)([(0,n.P)("ha-select")],M.prototype,"_select",void 0),M=(0,o.__decorate)([(0,n.EM)("ha-language-picker")],M),l()}catch(p){l(p)}}))},19785:function(e,t,a){a.a(e,(async function(e,l){try{a.r(t),a.d(t,{HaLanguageSelector:function(){return c}});a(35748),a(95013);var i=a(69868),o=a(84922),s=a(11991),n=a(86480),r=e([n]);n=(r.then?(await r)():r)[0];let u,d,h=e=>e;class c extends o.WF{render(){var e,t,a;return(0,o.qy)(u||(u=h`
      <ha-language-picker
        .hass=${0}
        .value=${0}
        .label=${0}
        .helper=${0}
        .languages=${0}
        .nativeName=${0}
        .noSort=${0}
        .disabled=${0}
        .required=${0}
      ></ha-language-picker>
    `),this.hass,this.value,this.label,this.helper,null===(e=this.selector.language)||void 0===e?void 0:e.languages,Boolean(null===(t=this.selector)||void 0===t||null===(t=t.language)||void 0===t?void 0:t.native_name),Boolean(null===(a=this.selector)||void 0===a||null===(a=a.language)||void 0===a?void 0:a.no_sort),this.disabled,this.required)}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}c.styles=(0,o.AH)(d||(d=h`
    ha-language-picker {
      width: 100%;
    }
  `)),(0,i.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"selector",void 0),(0,i.__decorate)([(0,s.MZ)()],c.prototype,"value",void 0),(0,i.__decorate)([(0,s.MZ)()],c.prototype,"label",void 0),(0,i.__decorate)([(0,s.MZ)()],c.prototype,"helper",void 0),(0,i.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,i.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"required",void 0),c=(0,i.__decorate)([(0,s.EM)("ha-selector-language")],c),l()}catch(u){l(u)}}))}}]);
//# sourceMappingURL=7682.20dc33adeae4a4d0.js.map