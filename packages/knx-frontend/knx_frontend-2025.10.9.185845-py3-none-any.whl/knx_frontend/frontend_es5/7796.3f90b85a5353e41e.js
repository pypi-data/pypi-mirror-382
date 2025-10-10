"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["7796"],{58448:function(t,e,o){o.a(t,(async function(t,e){try{o(79827),o(35748),o(99342),o(65315),o(837),o(37089),o(88238),o(34536),o(16257),o(20152),o(44711),o(72108),o(77030),o(18223),o(95013);var i=o(69868),a=o(84922),r=o(11991),s=o(26846),d=o(73120),l=o(5177),u=t([l]);l=(u.then?(await u)():u)[0];let h,n=t=>t;class c extends a.WF{shouldUpdate(t){return!(!t.has("_opened")&&this._opened)}updated(t){if(t.has("_opened")&&this._opened||t.has("entityId")||t.has("attribute")){const t=(this.entityId?(0,s.e)(this.entityId):[]).map((t=>{const e=this.hass.states[t];if(!e)return[];return Object.keys(e.attributes).filter((t=>{var e;return!(null!==(e=this.hideAttributes)&&void 0!==e&&e.includes(t))})).map((t=>({value:t,label:this.hass.formatEntityAttributeName(e,t)})))})),e=[],o=new Set;for(const i of t)for(const t of i)o.has(t.value)||(o.add(t.value),e.push(t));this._comboBox.filteredItems=e}}render(){var t;return this.hass?(0,a.qy)(h||(h=n`
      <ha-combo-box
        .hass=${0}
        .value=${0}
        .autofocus=${0}
        .label=${0}
        .disabled=${0}
        .required=${0}
        .helper=${0}
        .allowCustomValue=${0}
        item-id-path="value"
        item-value-path="value"
        item-label-path="label"
        @opened-changed=${0}
        @value-changed=${0}
      >
      </ha-combo-box>
    `),this.hass,this.value,this.autofocus,null!==(t=this.label)&&void 0!==t?t:this.hass.localize("ui.components.entity.entity-attribute-picker.attribute"),this.disabled||!this.entityId,this.required,this.helper,this.allowCustomValue,this._openedChanged,this._valueChanged):a.s6}get _value(){return this.value||""}_openedChanged(t){this._opened=t.detail.value}_valueChanged(t){t.stopPropagation();const e=t.detail.value;e!==this._value&&this._setValue(e)}_setValue(t){this.value=t,setTimeout((()=>{(0,d.r)(this,"value-changed",{value:t}),(0,d.r)(this,"change")}),0)}constructor(...t){super(...t),this.autofocus=!1,this.disabled=!1,this.required=!1,this._opened=!1}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],c.prototype,"entityId",void 0),(0,i.__decorate)([(0,r.MZ)({type:Array,attribute:"hide-attributes"})],c.prototype,"hideAttributes",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],c.prototype,"autofocus",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],c.prototype,"required",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"allow-custom-value"})],c.prototype,"allowCustomValue",void 0),(0,i.__decorate)([(0,r.MZ)()],c.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],c.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],c.prototype,"helper",void 0),(0,i.__decorate)([(0,r.wk)()],c.prototype,"_opened",void 0),(0,i.__decorate)([(0,r.P)("ha-combo-box",!0)],c.prototype,"_comboBox",void 0),c=(0,i.__decorate)([(0,r.EM)("ha-entity-attribute-picker")],c),e()}catch(h){e(h)}}))},61839:function(t,e,o){o.a(t,(async function(t,i){try{o.r(e),o.d(e,{HaSelectorAttribute:function(){return p}});o(35748),o(65315),o(59023),o(95013);var a=o(69868),r=o(84922),s=o(11991),d=o(73120),l=o(58448),u=o(26846),h=t([l]);l=(h.then?(await h)():h)[0];let n,c=t=>t;class p extends r.WF{render(){var t,e,o;return(0,r.qy)(n||(n=c`
      <ha-entity-attribute-picker
        .hass=${0}
        .entityId=${0}
        .hideAttributes=${0}
        .value=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
        allow-custom-value
      ></ha-entity-attribute-picker>
    `),this.hass,(null===(t=this.selector.attribute)||void 0===t?void 0:t.entity_id)||(null===(e=this.context)||void 0===e?void 0:e.filter_entity),null===(o=this.selector.attribute)||void 0===o?void 0:o.hide_attributes,this.value,this.label,this.helper,this.disabled,this.required)}updated(t){var e;if(super.updated(t),!this.value||null!==(e=this.selector.attribute)&&void 0!==e&&e.entity_id||!t.has("context"))return;const o=t.get("context");if(!this.context||!o||o.filter_entity===this.context.filter_entity)return;let i=!1;if(this.context.filter_entity){i=!(0,u.e)(this.context.filter_entity).some((t=>{const e=this.hass.states[t];return e&&this.value in e.attributes&&void 0!==e.attributes[this.value]}))}else i=void 0!==this.value;i&&(0,d.r)(this,"value-changed",{value:void 0})}constructor(...t){super(...t),this.disabled=!1,this.required=!0}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"selector",void 0),(0,a.__decorate)([(0,s.MZ)()],p.prototype,"value",void 0),(0,a.__decorate)([(0,s.MZ)()],p.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)()],p.prototype,"helper",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"context",void 0),p=(0,a.__decorate)([(0,s.EM)("ha-selector-attribute")],p),i()}catch(n){i(n)}}))}}]);
//# sourceMappingURL=7796.3f90b85a5353e41e.js.map