"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["1914"],{50087:function(e,t,a){a.d(t,{n:function(){return o}});a(67579),a(30500);const o=e=>e.replace(/^_*(.)|_+(.)/g,((e,t,a)=>t?t.toUpperCase():" "+a.toUpperCase()))},47304:function(e,t,a){a.a(e,(async function(e,t){try{a(79827),a(35748),a(99342),a(65315),a(837),a(22416),a(37089),a(12977),a(5934),a(18223),a(95013);var o=a(69868),i=a(84922),n=a(11991),s=a(73120),r=a(50087),l=a(48725),h=a(5177),d=(a(36137),a(81164),e([h]));h=(d.then?(await d)():d)[0];let p,c,u,v,_=e=>e;const m=[],g=e=>(0,i.qy)(p||(p=_`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${0} slot="start"></ha-icon>
    <span slot="headline">${0}</span>
    ${0}
  </ha-combo-box-item>
`),e.icon,e.title||e.path,e.title?(0,i.qy)(c||(c=_`<span slot="supporting-text">${0}</span>`),e.path):i.s6),b=(e,t,a)=>{var o,i,n;return{path:`/${e}/${null!==(o=t.path)&&void 0!==o?o:a}`,icon:null!==(i=t.icon)&&void 0!==i?i:"mdi:view-compact",title:null!==(n=t.title)&&void 0!==n?n:t.path?(0,r.n)(t.path):`${a}`}},y=(e,t)=>{var a;return{path:`/${t.url_path}`,icon:null!==(a=t.icon)&&void 0!==a?a:"mdi:view-dashboard",title:t.url_path===e.defaultPanel?e.localize("panel.states"):e.localize(`panel.${t.title}`)||t.title||(t.url_path?(0,r.n)(t.url_path):"")}};class f extends i.WF{render(){return(0,i.qy)(u||(u=_`
      <ha-combo-box
        .hass=${0}
        item-value-path="path"
        item-label-path="path"
        .value=${0}
        allow-custom-value
        .filteredItems=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
        .renderer=${0}
        @opened-changed=${0}
        @value-changed=${0}
        @filter-changed=${0}
      >
      </ha-combo-box>
    `),this.hass,this._value,this.navigationItems,this.label,this.helper,this.disabled,this.required,g,this._openedChanged,this._valueChanged,this._filterChanged)}async _openedChanged(e){this._opened=e.detail.value,this._opened&&!this.navigationItemsLoaded&&this._loadNavigationItems()}async _loadNavigationItems(){this.navigationItemsLoaded=!0;const e=Object.entries(this.hass.panels).map((([e,t])=>Object.assign({id:e},t))),t=e.filter((e=>"lovelace"===e.component_name)),a=await Promise.all(t.map((e=>(0,l.Dz)(this.hass.connection,"lovelace"===e.url_path?null:e.url_path,!0).then((t=>[e.id,t])).catch((t=>[e.id,void 0]))))),o=new Map(a);this.navigationItems=[];for(const i of e){this.navigationItems.push(y(this.hass,i));const e=o.get(i.id);e&&"views"in e&&e.views.forEach(((e,t)=>this.navigationItems.push(b(i.url_path,e,t))))}this.comboBox.filteredItems=this.navigationItems}shouldUpdate(e){return!this._opened||e.has("_opened")}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,s.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}_filterChanged(e){const t=e.detail.value.toLowerCase();if(t.length>=2){const e=[];this.navigationItems.forEach((a=>{(a.path.toLowerCase().includes(t)||a.title.toLowerCase().includes(t))&&e.push(a)})),e.length>0?this.comboBox.filteredItems=e:this.comboBox.filteredItems=[]}else this.comboBox.filteredItems=this.navigationItems}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._opened=!1,this.navigationItemsLoaded=!1,this.navigationItems=m}}f.styles=(0,i.AH)(v||(v=_`
    ha-icon,
    ha-svg-icon {
      color: var(--primary-text-color);
      position: relative;
      bottom: 0px;
    }
    *[slot="prefix"] {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
  `)),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)()],f.prototype,"label",void 0),(0,o.__decorate)([(0,n.MZ)()],f.prototype,"value",void 0),(0,o.__decorate)([(0,n.MZ)()],f.prototype,"helper",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],f.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],f.prototype,"required",void 0),(0,o.__decorate)([(0,n.wk)()],f.prototype,"_opened",void 0),(0,o.__decorate)([(0,n.P)("ha-combo-box",!0)],f.prototype,"comboBox",void 0),f=(0,o.__decorate)([(0,n.EM)("ha-navigation-picker")],f),t()}catch(p){t(p)}}))},31649:function(e,t,a){a.a(e,(async function(e,o){try{a.r(t),a.d(t,{HaNavigationSelector:function(){return c}});a(35748),a(95013);var i=a(69868),n=a(84922),s=a(11991),r=a(73120),l=a(47304),h=e([l]);l=(h.then?(await h)():h)[0];let d,p=e=>e;class c extends n.WF{render(){return(0,n.qy)(d||(d=p`
      <ha-navigation-picker
        .hass=${0}
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        .helper=${0}
        @value-changed=${0}
      ></ha-navigation-picker>
    `),this.hass,this.label,this.value,this.required,this.disabled,this.helper,this._valueChanged)}_valueChanged(e){(0,r.r)(this,"value-changed",{value:e.detail.value})}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}(0,i.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"selector",void 0),(0,i.__decorate)([(0,s.MZ)()],c.prototype,"value",void 0),(0,i.__decorate)([(0,s.MZ)()],c.prototype,"label",void 0),(0,i.__decorate)([(0,s.MZ)()],c.prototype,"helper",void 0),(0,i.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],c.prototype,"disabled",void 0),(0,i.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"required",void 0),c=(0,i.__decorate)([(0,s.EM)("ha-selector-navigation")],c),o()}catch(d){o(d)}}))},48725:function(e,t,a){a.d(t,{Dz:function(){return o}});const o=(e,t,a)=>e.sendMessagePromise({type:"lovelace/config",url_path:t,force:a})}}]);
//# sourceMappingURL=1914.68ae120af9ea4ef3.js.map