"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2087"],{41602:function(t,e,i){i.d(e,{n:function(){return s}});i(67579),i(41190);const a=/^(\w+)\.(\w+)$/,s=t=>a.test(t)},57447:function(t,e,i){i.a(t,(async function(t,e){try{i(79827),i(35748),i(86149),i(65315),i(837),i(37089),i(5934),i(18223),i(56660),i(95013);var a=i(69868),s=i(84922),n=i(11991),o=i(65940),r=i(73120),l=i(92830),c=i(47379),d=i(41602),u=i(98137),h=i(28027),p=i(5940),y=i(80608),_=(i(36137),i(58453)),m=(i(95635),i(23114)),v=t([_,m]);[_,m]=v.then?(await v)():v;let f,b,g,$,w,M,C,j,O,I=t=>t;const Z="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",k="M11,13.5V21.5H3V13.5H11M12,2L17.5,11H6.5L12,2M17.5,13C20,13 22,15 22,17.5C22,20 20,22 17.5,22C15,22 13,20 13,17.5C13,15 15,13 17.5,13Z",E="___create-new-entity___";class x extends s.WF{firstUpdated(t){super.firstUpdated(t),this.hass.loadBackendTranslation("title")}get _showEntityId(){var t;return this.showEntityId||(null===(t=this.hass.userData)||void 0===t?void 0:t.showEntityIdPicker)}render(){var t;const e=null!==(t=this.placeholder)&&void 0!==t?t:this.hass.localize("ui.components.entity.entity-picker.placeholder"),i=this.hass.localize("ui.components.entity.entity-picker.no_match");return(0,s.qy)(f||(f=I`
      <ha-generic-picker
        .hass=${0}
        .disabled=${0}
        .autofocus=${0}
        .allowCustomValue=${0}
        .label=${0}
        .helper=${0}
        .searchLabel=${0}
        .notFoundLabel=${0}
        .placeholder=${0}
        .value=${0}
        .rowRenderer=${0}
        .getItems=${0}
        .getAdditionalItems=${0}
        .hideClearIcon=${0}
        .searchFn=${0}
        .valueRenderer=${0}
        @value-changed=${0}
      >
      </ha-generic-picker>
    `),this.hass,this.disabled,this.autofocus,this.allowCustomEntity,this.label,this.helper,this.searchLabel,i,e,this.value,this._rowRenderer,this._getItems,this._getAdditionalItems,this.hideClearIcon,this._searchFn,this._valueRenderer,this._valueChanged)}async open(){var t;await this.updateComplete,await(null===(t=this._picker)||void 0===t?void 0:t.open())}_valueChanged(t){t.stopPropagation();const e=t.detail.value;if(e)if(e.startsWith(E)){const t=e.substring(E.length);(0,y.$)(this,{domain:t,dialogClosedCallback:t=>{t.entityId&&this._setValue(t.entityId)}})}else(0,d.n)(e)&&this._setValue(e);else this._setValue(void 0)}_setValue(t){this.value=t,(0,r.r)(this,"value-changed",{value:t}),(0,r.r)(this,"change")}constructor(...t){super(...t),this.autofocus=!1,this.disabled=!1,this.required=!1,this.showEntityId=!1,this.hideClearIcon=!1,this._valueRenderer=t=>{const e=t||"",i=this.hass.states[e];if(!i)return(0,s.qy)(b||(b=I`
        <ha-svg-icon
          slot="start"
          .path=${0}
          style="margin: 0 4px"
        ></ha-svg-icon>
        <span slot="headline">${0}</span>
      `),k,e);const a=this.hass.formatEntityName(i,"entity"),n=this.hass.formatEntityName(i,"device"),o=this.hass.formatEntityName(i,"area"),r=(0,u.qC)(this.hass),l=a||n||e,c=[o,a?n:void 0].filter(Boolean).join(r?" ◂ ":" ▸ ");return(0,s.qy)(g||(g=I`
      <state-badge
        .hass=${0}
        .stateObj=${0}
        slot="start"
      ></state-badge>
      <span slot="headline">${0}</span>
      <span slot="supporting-text">${0}</span>
    `),this.hass,i,l,c)},this._rowRenderer=(t,{index:e})=>{const i=this._showEntityId;return(0,s.qy)($||($=I`
      <ha-combo-box-item type="button" compact .borderTop=${0}>
        ${0}
        <span slot="headline">${0}</span>
        ${0}
        ${0}
        ${0}
      </ha-combo-box-item>
    `),0!==e,t.icon_path?(0,s.qy)(w||(w=I`
              <ha-svg-icon
                slot="start"
                style="margin: 0 4px"
                .path=${0}
              ></ha-svg-icon>
            `),t.icon_path):(0,s.qy)(M||(M=I`
              <state-badge
                slot="start"
                .stateObj=${0}
                .hass=${0}
              ></state-badge>
            `),t.stateObj,this.hass),t.primary,t.secondary?(0,s.qy)(C||(C=I`<span slot="supporting-text">${0}</span>`),t.secondary):s.s6,t.stateObj&&i?(0,s.qy)(j||(j=I`
              <span slot="supporting-text" class="code">
                ${0}
              </span>
            `),t.stateObj.entity_id):s.s6,t.domain_name&&!i?(0,s.qy)(O||(O=I`
              <div slot="trailing-supporting-text" class="domain">
                ${0}
              </div>
            `),t.domain_name):s.s6)},this._getAdditionalItems=()=>this._getCreateItems(this.hass.localize,this.createDomains),this._getCreateItems=(0,o.A)(((t,e)=>null!=e&&e.length?e.map((e=>{const i=t("ui.components.entity.entity-picker.create_helper",{domain:(0,p.z)(e)?t(`ui.panel.config.helpers.types.${e}`):(0,h.p$)(t,e)});return{id:E+e,primary:i,secondary:t("ui.components.entity.entity-picker.new_entity"),icon_path:Z}})):[])),this._getItems=()=>this._getEntities(this.hass,this.includeDomains,this.excludeDomains,this.entityFilter,this.includeDeviceClasses,this.includeUnitOfMeasurement,this.includeEntities,this.excludeEntities),this._getEntities=(0,o.A)(((t,e,i,a,s,n,o,r)=>{let d=[],p=Object.keys(t.states);o&&(p=p.filter((t=>o.includes(t)))),r&&(p=p.filter((t=>!r.includes(t)))),e&&(p=p.filter((t=>e.includes((0,l.m)(t))))),i&&(p=p.filter((t=>!i.includes((0,l.m)(t)))));const y=(0,u.qC)(this.hass);return d=p.map((e=>{const i=t.states[e],a=(0,c.u)(i),s=this.hass.formatEntityName(i,"entity"),n=this.hass.formatEntityName(i,"device"),o=this.hass.formatEntityName(i,"area"),r=(0,h.p$)(this.hass.localize,(0,l.m)(e)),d=s||n||e,u=[o,s?n:void 0].filter(Boolean).join(y?" ◂ ":" ▸ "),p=[n,s].filter(Boolean).join(" - ");return{id:e,primary:d,secondary:u,domain_name:r,sorting_label:[n,s].filter(Boolean).join("_"),search_labels:[s,n,o,r,a,e].filter(Boolean),a11y_label:p,stateObj:i}})),s&&(d=d.filter((t=>{var e;return t.id===this.value||(null===(e=t.stateObj)||void 0===e?void 0:e.attributes.device_class)&&s.includes(t.stateObj.attributes.device_class)}))),n&&(d=d.filter((t=>{var e;return t.id===this.value||(null===(e=t.stateObj)||void 0===e?void 0:e.attributes.unit_of_measurement)&&n.includes(t.stateObj.attributes.unit_of_measurement)}))),a&&(d=d.filter((t=>t.id===this.value||t.stateObj&&a(t.stateObj)))),d})),this._searchFn=(t,e)=>{const i=e.findIndex((e=>{var i;return(null===(i=e.stateObj)||void 0===i?void 0:i.entity_id)===t}));if(-1===i)return e;const[a]=e.splice(i,1);return e.unshift(a),e}}}(0,a.__decorate)([(0,n.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],x.prototype,"autofocus",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],x.prototype,"disabled",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],x.prototype,"required",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,attribute:"allow-custom-entity"})],x.prototype,"allowCustomEntity",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,attribute:"show-entity-id"})],x.prototype,"showEntityId",void 0),(0,a.__decorate)([(0,n.MZ)()],x.prototype,"label",void 0),(0,a.__decorate)([(0,n.MZ)()],x.prototype,"value",void 0),(0,a.__decorate)([(0,n.MZ)()],x.prototype,"helper",void 0),(0,a.__decorate)([(0,n.MZ)()],x.prototype,"placeholder",void 0),(0,a.__decorate)([(0,n.MZ)({type:String,attribute:"search-label"})],x.prototype,"searchLabel",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1,type:Array})],x.prototype,"createDomains",void 0),(0,a.__decorate)([(0,n.MZ)({type:Array,attribute:"include-domains"})],x.prototype,"includeDomains",void 0),(0,a.__decorate)([(0,n.MZ)({type:Array,attribute:"exclude-domains"})],x.prototype,"excludeDomains",void 0),(0,a.__decorate)([(0,n.MZ)({type:Array,attribute:"include-device-classes"})],x.prototype,"includeDeviceClasses",void 0),(0,a.__decorate)([(0,n.MZ)({type:Array,attribute:"include-unit-of-measurement"})],x.prototype,"includeUnitOfMeasurement",void 0),(0,a.__decorate)([(0,n.MZ)({type:Array,attribute:"include-entities"})],x.prototype,"includeEntities",void 0),(0,a.__decorate)([(0,n.MZ)({type:Array,attribute:"exclude-entities"})],x.prototype,"excludeEntities",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],x.prototype,"entityFilter",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:"hide-clear-icon",type:Boolean})],x.prototype,"hideClearIcon",void 0),(0,a.__decorate)([(0,n.P)("ha-generic-picker")],x.prototype,"_picker",void 0),x=(0,a.__decorate)([(0,n.EM)("ha-entity-picker")],x),e()}catch(f){e(f)}}))},4311:function(t,e,i){i.d(e,{Hg:function(){return a},e0:function(){return s}});i(79827),i(65315),i(37089),i(36874),i(12977),i(5934),i(90917),i(18223);const a=t=>t.map((t=>{if("string"!==t.type)return t;switch(t.name){case"username":return Object.assign(Object.assign({},t),{},{autocomplete:"username",autofocus:!0});case"password":return Object.assign(Object.assign({},t),{},{autocomplete:"current-password"});case"code":return Object.assign(Object.assign({},t),{},{autocomplete:"one-time-code",autofocus:!0});default:return t}})),s=(t,e)=>t.callWS({type:"auth/sign_path",path:e})},6098:function(t,e,i){i.d(e,{HV:function(){return n},Hh:function(){return s},KF:function(){return r},ON:function(){return o},g0:function(){return d},s7:function(){return l}});var a=i(87383);const s="unavailable",n="unknown",o="on",r="off",l=[s,n],c=[s,n,r],d=(0,a.g)(l);(0,a.g)(c)},28027:function(t,e,i){i.d(e,{QC:function(){return n},fK:function(){return s},p$:function(){return a}});i(24802);const a=(t,e,i)=>t(`component.${e}.title`)||(null==i?void 0:i.name)||e,s=(t,e)=>{const i={type:"manifest/list"};return e&&(i.integrations=e),t.callWS(i)},n=(t,e)=>t.callWS({type:"manifest/get",integration:e})},80608:function(t,e,i){i.d(e,{$:function(){return n}});i(35748),i(5934),i(95013);var a=i(73120);const s=()=>i.e("8221").then(i.bind(i,27084)),n=(t,e)=>{(0,a.r)(t,"show-dialog",{dialogTag:"dialog-helper-detail",dialogImport:s,dialogParams:e})}}}]);
//# sourceMappingURL=2087.b7089bcedc609563.js.map