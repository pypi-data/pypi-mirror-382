/*! For license information please see 4851.2cf5cb2514b60eb1.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["4851"],{15785:function(t,e,o){o.a(t,(async function(t,i){try{o.r(e),o.d(e,{HaIconPicker:function(){return C}});o(79827),o(35748),o(99342),o(35058),o(65315),o(837),o(22416),o(37089),o(59023),o(5934),o(88238),o(34536),o(16257),o(20152),o(44711),o(72108),o(77030),o(18223),o(95013);var s=o(69868),a=o(84922),r=o(11991),n=o(65940),c=o(73120),l=o(73314),h=o(5177),d=(o(81164),o(36137),t([h]));h=(d.then?(await d)():d)[0];let u,p,v,_,y,b=t=>t,$=[],f=!1;const g=async()=>{f=!0;const t=await o.e("4765").then(o.t.bind(o,43692,19));$=t.default.map((t=>({icon:`mdi:${t.name}`,parts:new Set(t.name.split("-")),keywords:t.keywords})));const e=[];Object.keys(l.y).forEach((t=>{e.push(m(t))})),(await Promise.all(e)).forEach((t=>{$.push(...t)}))},m=async t=>{try{const e=l.y[t].getIconList;if("function"!=typeof e)return[];const o=await e();return o.map((e=>{var o;return{icon:`${t}:${e.name}`,parts:new Set(e.name.split("-")),keywords:null!==(o=e.keywords)&&void 0!==o?o:[]}}))}catch(e){return console.warn(`Unable to load icon list for ${t} iconset`),[]}},w=t=>(0,a.qy)(u||(u=b`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${0} slot="start"></ha-icon>
    ${0}
  </ha-combo-box-item>
`),t.icon,t.icon);class C extends a.WF{render(){return(0,a.qy)(p||(p=b`
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
    `),this.hass,this._value,f?this._iconProvider:void 0,this.label,this.helper,this.disabled,this.required,this.placeholder,this.errorMessage,this.invalid,w,this._openedChanged,this._valueChanged,this._value||this.placeholder?(0,a.qy)(v||(v=b`
              <ha-icon .icon=${0} slot="icon">
              </ha-icon>
            `),this._value||this.placeholder):(0,a.qy)(_||(_=b`<slot slot="icon" name="fallback"></slot>`)))}async _openedChanged(t){t.detail.value&&!f&&(await g(),this.requestUpdate())}_valueChanged(t){t.stopPropagation(),this._setValue(t.detail.value)}_setValue(t){this.value=t,(0,c.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}get _value(){return this.value||""}constructor(...t){super(...t),this.disabled=!1,this.required=!1,this.invalid=!1,this._filterIcons=(0,n.A)(((t,e=$)=>{if(!t)return e;const o=[],i=(t,e)=>o.push({icon:t,rank:e});for(const s of e)s.parts.has(t)?i(s.icon,1):s.keywords.includes(t)?i(s.icon,2):s.icon.includes(t)?i(s.icon,3):s.keywords.some((e=>e.includes(t)))&&i(s.icon,4);return 0===o.length&&i(t,0),o.sort(((t,e)=>t.rank-e.rank))})),this._iconProvider=(t,e)=>{const o=this._filterIcons(t.filter.toLowerCase(),$),i=t.page*t.pageSize,s=i+t.pageSize;e(o.slice(i,s),o.length)}}}C.styles=(0,a.AH)(y||(y=b`
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
  `)),(0,s.__decorate)([(0,r.MZ)({attribute:!1})],C.prototype,"hass",void 0),(0,s.__decorate)([(0,r.MZ)()],C.prototype,"value",void 0),(0,s.__decorate)([(0,r.MZ)()],C.prototype,"label",void 0),(0,s.__decorate)([(0,r.MZ)()],C.prototype,"helper",void 0),(0,s.__decorate)([(0,r.MZ)()],C.prototype,"placeholder",void 0),(0,s.__decorate)([(0,r.MZ)({attribute:"error-message"})],C.prototype,"errorMessage",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],C.prototype,"disabled",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],C.prototype,"required",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],C.prototype,"invalid",void 0),C=(0,s.__decorate)([(0,r.EM)("ha-icon-picker")],C),i()}catch(u){i(u)}}))},80798:function(t,e,o){o.a(t,(async function(t,i){try{o.r(e),o.d(e,{HaIconSelector:function(){return y}});o(35748),o(95013);var s=o(69868),a=o(84922),r=o(11991),n=o(55),c=o(73120),l=o(93327),h=o(15785),d=o(72582),u=t([h,d,l]);[h,d,l]=u.then?(await u)():u;let p,v,_=t=>t;class y extends a.WF{render(){var t,e,o,i;const s=null===(t=this.context)||void 0===t?void 0:t.icon_entity,r=s?this.hass.states[s]:void 0,c=(null===(e=this.selector.icon)||void 0===e?void 0:e.placeholder)||(null==r?void 0:r.attributes.icon)||r&&(0,n.T)((0,l.fq)(this.hass,r));return(0,a.qy)(p||(p=_`
      <ha-icon-picker
        .hass=${0}
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        .helper=${0}
        .placeholder=${0}
        @value-changed=${0}
      >
        ${0}
      </ha-icon-picker>
    `),this.hass,this.label,this.value,this.required,this.disabled,this.helper,null!==(o=null===(i=this.selector.icon)||void 0===i?void 0:i.placeholder)&&void 0!==o?o:c,this._valueChanged,!c&&r?(0,a.qy)(v||(v=_`
              <ha-state-icon
                slot="fallback"
                .hass=${0}
                .stateObj=${0}
              ></ha-state-icon>
            `),this.hass,r):a.s6)}_valueChanged(t){(0,c.r)(this,"value-changed",{value:t.detail.value})}constructor(...t){super(...t),this.disabled=!1,this.required=!0}}(0,s.__decorate)([(0,r.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,s.__decorate)([(0,r.MZ)({attribute:!1})],y.prototype,"selector",void 0),(0,s.__decorate)([(0,r.MZ)()],y.prototype,"value",void 0),(0,s.__decorate)([(0,r.MZ)()],y.prototype,"label",void 0),(0,s.__decorate)([(0,r.MZ)()],y.prototype,"helper",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],y.prototype,"disabled",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],y.prototype,"required",void 0),(0,s.__decorate)([(0,r.MZ)({attribute:!1})],y.prototype,"context",void 0),y=(0,s.__decorate)([(0,r.EM)("ha-selector-icon")],y),i()}catch(p){i(p)}}))},72582:function(t,e,o){o.a(t,(async function(t,e){try{var i=o(69868),s=o(84922),a=o(11991),r=o(55),n=o(7556),c=o(93327),l=(o(81164),o(95635),t([c]));c=(l.then?(await l)():l)[0];let h,d,u,p,v=t=>t;class _ extends s.WF{render(){var t,e;const o=this.icon||this.stateObj&&(null===(t=this.hass)||void 0===t||null===(t=t.entities[this.stateObj.entity_id])||void 0===t?void 0:t.icon)||(null===(e=this.stateObj)||void 0===e?void 0:e.attributes.icon);if(o)return(0,s.qy)(h||(h=v`<ha-icon .icon=${0}></ha-icon>`),o);if(!this.stateObj)return s.s6;if(!this.hass)return this._renderFallback();const i=(0,c.fq)(this.hass,this.stateObj,this.stateValue).then((t=>t?(0,s.qy)(d||(d=v`<ha-icon .icon=${0}></ha-icon>`),t):this._renderFallback()));return(0,s.qy)(u||(u=v`${0}`),(0,r.T)(i))}_renderFallback(){const t=(0,n.t)(this.stateObj);return(0,s.qy)(p||(p=v`
      <ha-svg-icon
        .path=${0}
      ></ha-svg-icon>
    `),c.l[t]||c.lW)}}(0,i.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"stateObj",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"stateValue",void 0),(0,i.__decorate)([(0,a.MZ)()],_.prototype,"icon",void 0),_=(0,i.__decorate)([(0,a.EM)("ha-state-icon")],_),e()}catch(h){e(h)}}))},55:function(t,e,o){o.d(e,{T:function(){return u}});o(35748),o(65315),o(84136),o(5934),o(95013);var i=o(11681),s=o(67851),a=o(40594);o(32203),o(79392),o(46852);class r{disconnect(){this.G=void 0}reconnect(t){this.G=t}deref(){return this.G}constructor(t){this.G=t}}class n{get(){return this.Y}pause(){var t;null!==(t=this.Y)&&void 0!==t||(this.Y=new Promise((t=>this.Z=t)))}resume(){var t;null!==(t=this.Z)&&void 0!==t&&t.call(this),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var c=o(64363);const l=t=>!(0,s.sO)(t)&&"function"==typeof t.then,h=1073741823;class d extends a.Kq{render(...t){var e;return null!==(e=t.find((t=>!l(t))))&&void 0!==e?e:i.c0}update(t,e){const o=this._$Cbt;let s=o.length;this._$Cbt=e;const a=this._$CK,r=this._$CX;this.isConnected||this.disconnected();for(let i=0;i<e.length&&!(i>this._$Cwt);i++){const t=e[i];if(!l(t))return this._$Cwt=i,t;i<s&&t===o[i]||(this._$Cwt=h,s=0,Promise.resolve(t).then((async e=>{for(;r.get();)await r.get();const o=a.deref();if(void 0!==o){const i=o._$Cbt.indexOf(t);i>-1&&i<o._$Cwt&&(o._$Cwt=i,o.setValue(e))}})))}return i.c0}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=h,this._$Cbt=[],this._$CK=new r(this),this._$CX=new n}}const u=(0,c.u$)(d)}}]);
//# sourceMappingURL=4851.2cf5cb2514b60eb1.js.map