"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["7026"],{15785:function(e,t,o){o.a(e,(async function(e,a){try{o.r(t),o.d(t,{HaIconPicker:function(){return w}});o(79827),o(35748),o(99342),o(35058),o(65315),o(837),o(22416),o(37089),o(59023),o(5934),o(88238),o(34536),o(16257),o(20152),o(44711),o(72108),o(77030),o(18223),o(95013);var i=o(69868),r=o(84922),n=o(11991),s=o(65940),l=o(73120),c=o(73314),d=o(5177),h=(o(81164),o(36137),e([d]));d=(h.then?(await h)():h)[0];let p,u,v,_,y,b=e=>e,m=[],g=!1;const f=async()=>{g=!0;const e=await o.e("4765").then(o.t.bind(o,43692,19));m=e.default.map((e=>({icon:`mdi:${e.name}`,parts:new Set(e.name.split("-")),keywords:e.keywords})));const t=[];Object.keys(c.y).forEach((e=>{t.push($(e))})),(await Promise.all(t)).forEach((e=>{m.push(...e)}))},$=async e=>{try{const t=c.y[e].getIconList;if("function"!=typeof t)return[];const o=await t();return o.map((t=>{var o;return{icon:`${e}:${t.name}`,parts:new Set(t.name.split("-")),keywords:null!==(o=t.keywords)&&void 0!==o?o:[]}}))}catch(t){return console.warn(`Unable to load icon list for ${e} iconset`),[]}},k=e=>(0,r.qy)(p||(p=b`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${0} slot="start"></ha-icon>
    ${0}
  </ha-combo-box-item>
`),e.icon,e.icon);class w extends r.WF{render(){return(0,r.qy)(u||(u=b`
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
    `),this.hass,this._value,g?this._iconProvider:void 0,this.label,this.helper,this.disabled,this.required,this.placeholder,this.errorMessage,this.invalid,k,this._openedChanged,this._valueChanged,this._value||this.placeholder?(0,r.qy)(v||(v=b`
              <ha-icon .icon=${0} slot="icon">
              </ha-icon>
            `),this._value||this.placeholder):(0,r.qy)(_||(_=b`<slot slot="icon" name="fallback"></slot>`)))}async _openedChanged(e){e.detail.value&&!g&&(await f(),this.requestUpdate())}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,l.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.invalid=!1,this._filterIcons=(0,s.A)(((e,t=m)=>{if(!e)return t;const o=[],a=(e,t)=>o.push({icon:e,rank:t});for(const i of t)i.parts.has(e)?a(i.icon,1):i.keywords.includes(e)?a(i.icon,2):i.icon.includes(e)?a(i.icon,3):i.keywords.some((t=>t.includes(e)))&&a(i.icon,4);return 0===o.length&&a(e,0),o.sort(((e,t)=>e.rank-t.rank))})),this._iconProvider=(e,t)=>{const o=this._filterIcons(e.filter.toLowerCase(),m),a=e.page*e.pageSize,i=a+e.pageSize;t(o.slice(a,i),o.length)}}}w.styles=(0,r.AH)(y||(y=b`
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
  `)),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],w.prototype,"hass",void 0),(0,i.__decorate)([(0,n.MZ)()],w.prototype,"value",void 0),(0,i.__decorate)([(0,n.MZ)()],w.prototype,"label",void 0),(0,i.__decorate)([(0,n.MZ)()],w.prototype,"helper",void 0),(0,i.__decorate)([(0,n.MZ)()],w.prototype,"placeholder",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"error-message"})],w.prototype,"errorMessage",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],w.prototype,"disabled",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],w.prototype,"required",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],w.prototype,"invalid",void 0),w=(0,i.__decorate)([(0,n.EM)("ha-icon-picker")],w),a()}catch(p){a(p)}}))}}]);
//# sourceMappingURL=7026.8bf663599626c0fb.js.map