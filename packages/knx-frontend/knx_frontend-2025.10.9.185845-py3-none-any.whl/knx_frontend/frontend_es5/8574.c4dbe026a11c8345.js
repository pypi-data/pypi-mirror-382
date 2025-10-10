"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["8574"],{44537:function(e,t,i){i.d(t,{xn:function(){return o},T:function(){return a}});i(35748),i(65315),i(837),i(37089),i(39118),i(95013);var s=i(65940),r=i(47379);i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030);const o=e=>{var t;return null===(t=e.name_by_user||e.name)||void 0===t?void 0:t.trim()},a=(e,t,i)=>o(e)||i&&n(t,i)||t.localize("ui.panel.config.devices.unnamed_device",{type:t.localize(`ui.panel.config.devices.type.${e.entry_type||"device"}`)}),n=(e,t)=>{for(const i of t||[]){const t="string"==typeof i?i:i.entity_id,s=e.states[t];if(s)return(0,r.u)(s)}};(0,s.A)((e=>function(e){const t=new Set,i=new Set;for(const s of e)i.has(s)?t.add(s):i.add(s);return t}(Object.values(e).map((e=>o(e))).filter((e=>void 0!==e)))))},24383:function(e,t,i){i.d(t,{w:function(){return s}});const s=(e,t)=>{const i=e.area_id,s=i?t.areas[i]:void 0,r=null==s?void 0:s.floor_id;return{device:e,area:s||null,floor:(r?t.floors[r]:void 0)||null}}},71755:function(e,t,i){i.a(e,(async function(e,t){try{i(79827),i(35748),i(65315),i(12840),i(837),i(37089),i(59023),i(52885),i(5934),i(18223),i(95013);var s=i(69868),r=i(84922),o=i(11991),a=i(65940),n=i(73120),c=i(22441),d=i(44537),l=i(92830),u=i(24383),h=i(88120),v=i(56083),p=i(28027),_=i(45363),y=i(58453),m=e([y]);y=(m.then?(await m)():m)[0];let f,b,g,$,k,D,M,Z,x=e=>e;class q extends r.WF{firstUpdated(e){super.firstUpdated(e),this._loadConfigEntries()}async _loadConfigEntries(){const e=await(0,h.VN)(this.hass);this._configEntryLookup=Object.fromEntries(e.map((e=>[e.entry_id,e])))}render(){var e;const t=null!==(e=this.placeholder)&&void 0!==e?e:this.hass.localize("ui.components.device-picker.placeholder"),i=this.hass.localize("ui.components.device-picker.no_match"),s=this._valueRenderer(this._configEntryLookup);return(0,r.qy)(f||(f=x`
      <ha-generic-picker
        .hass=${0}
        .autofocus=${0}
        .label=${0}
        .searchLabel=${0}
        .notFoundLabel=${0}
        .placeholder=${0}
        .value=${0}
        .rowRenderer=${0}
        .getItems=${0}
        .hideClearIcon=${0}
        .valueRenderer=${0}
        @value-changed=${0}
      >
      </ha-generic-picker>
    `),this.hass,this.autofocus,this.label,this.searchLabel,i,t,this.value,this._rowRenderer,this._getItems,this.hideClearIcon,s,this._valueChanged)}async open(){var e;await this.updateComplete,await(null===(e=this._picker)||void 0===e?void 0:e.open())}_valueChanged(e){e.stopPropagation();const t=e.detail.value;this.value=t,(0,n.r)(this,"value-changed",{value:t})}constructor(...e){super(...e),this.autofocus=!1,this.disabled=!1,this.required=!1,this.hideClearIcon=!1,this._configEntryLookup={},this._getItems=()=>this._getDevices(this.hass.devices,this.hass.entities,this._configEntryLookup,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeDevices),this._getDevices=(0,a.A)(((e,t,i,s,r,o,a,n,h)=>{const _=Object.values(e),y=Object.values(t);let m={};(s||r||o||n)&&(m=(0,v.g2)(y));let f=_.filter((e=>e.id===this.value||!e.disabled_by));s&&(f=f.filter((e=>{const t=m[e.id];return!(!t||!t.length)&&m[e.id].some((e=>s.includes((0,l.m)(e.entity_id))))}))),r&&(f=f.filter((e=>{const t=m[e.id];return!t||!t.length||y.every((e=>!r.includes((0,l.m)(e.entity_id))))}))),h&&(f=f.filter((e=>!h.includes(e.id)))),o&&(f=f.filter((e=>{const t=m[e.id];return!(!t||!t.length)&&m[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&o.includes(t.attributes.device_class))}))}))),n&&(f=f.filter((e=>{const t=m[e.id];return!(!t||!t.length)&&t.some((e=>{const t=this.hass.states[e.entity_id];return!!t&&n(t)}))}))),a&&(f=f.filter((e=>e.id===this.value||a(e))));return f.map((e=>{const t=(0,d.T)(e,this.hass,m[e.id]),{area:s}=(0,u.w)(e,this.hass),r=s?(0,c.A)(s):void 0,o=e.primary_config_entry?null==i?void 0:i[e.primary_config_entry]:void 0,a=null==o?void 0:o.domain,n=a?(0,p.p$)(this.hass.localize,a):void 0;return{id:e.id,label:"",primary:t||this.hass.localize("ui.components.device-picker.unnamed_device"),secondary:r,domain:null==o?void 0:o.domain,domain_name:n,search_labels:[t,r,a,n].filter(Boolean),sorting_label:t||"zzz"}}))})),this._valueRenderer=(0,a.A)((e=>t=>{var i;const s=t,o=this.hass.devices[s];if(!o)return(0,r.qy)(b||(b=x`<span slot="headline">${0}</span>`),s);const{area:a}=(0,u.w)(o,this.hass),n=o?(0,d.xn)(o):void 0,l=a?(0,c.A)(a):void 0,h=o.primary_config_entry?e[o.primary_config_entry]:void 0;return(0,r.qy)(g||(g=x`
        ${0}
        <span slot="headline">${0}</span>
        <span slot="supporting-text">${0}</span>
      `),h?(0,r.qy)($||($=x`<img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${0}
            />`),(0,_.MR)({domain:h.domain,type:"icon",darkOptimized:null===(i=this.hass.themes)||void 0===i?void 0:i.darkMode})):r.s6,n,l)})),this._rowRenderer=e=>(0,r.qy)(k||(k=x`
    <ha-combo-box-item type="button">
      ${0}

      <span slot="headline">${0}</span>
      ${0}
      ${0}
    </ha-combo-box-item>
  `),e.domain?(0,r.qy)(D||(D=x`
            <img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${0}
            />
          `),(0,_.MR)({domain:e.domain,type:"icon",darkOptimized:this.hass.themes.darkMode})):r.s6,e.primary,e.secondary?(0,r.qy)(M||(M=x`<span slot="supporting-text">${0}</span>`),e.secondary):r.s6,e.domain_name?(0,r.qy)(Z||(Z=x`
            <div slot="trailing-supporting-text" class="domain">
              ${0}
            </div>
          `),e.domain_name):r.s6)}}(0,s.__decorate)([(0,o.MZ)({attribute:!1})],q.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],q.prototype,"autofocus",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],q.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],q.prototype,"required",void 0),(0,s.__decorate)([(0,o.MZ)()],q.prototype,"label",void 0),(0,s.__decorate)([(0,o.MZ)()],q.prototype,"value",void 0),(0,s.__decorate)([(0,o.MZ)()],q.prototype,"helper",void 0),(0,s.__decorate)([(0,o.MZ)()],q.prototype,"placeholder",void 0),(0,s.__decorate)([(0,o.MZ)({type:String,attribute:"search-label"})],q.prototype,"searchLabel",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1,type:Array})],q.prototype,"createDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-domains"})],q.prototype,"includeDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-domains"})],q.prototype,"excludeDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-device-classes"})],q.prototype,"includeDeviceClasses",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-devices"})],q.prototype,"excludeDevices",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],q.prototype,"deviceFilter",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],q.prototype,"entityFilter",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"hide-clear-icon",type:Boolean})],q.prototype,"hideClearIcon",void 0),(0,s.__decorate)([(0,o.P)("ha-generic-picker")],q.prototype,"_picker",void 0),(0,s.__decorate)([(0,o.wk)()],q.prototype,"_configEntryLookup",void 0),q=(0,s.__decorate)([(0,o.EM)("ha-device-picker")],q),t()}catch(f){t(f)}}))},65654:function(e,t,i){i.a(e,(async function(e,t){try{i(79827),i(35748),i(65315),i(837),i(37089),i(5934),i(18223),i(95013);var s=i(69868),r=i(84922),o=i(11991),a=i(73120),n=i(71755),c=e([n]);n=(c.then?(await c)():c)[0];let d,l,u,h=e=>e;class v extends r.WF{render(){if(!this.hass)return r.s6;const e=this._currentDevices;return(0,r.qy)(d||(d=h`
      ${0}
      <div>
        <ha-device-picker
          allow-custom-entity
          .hass=${0}
          .helper=${0}
          .deviceFilter=${0}
          .entityFilter=${0}
          .includeDomains=${0}
          .excludeDomains=${0}
          .excludeDevices=${0}
          .includeDeviceClasses=${0}
          .label=${0}
          .disabled=${0}
          .required=${0}
          @value-changed=${0}
        ></ha-device-picker>
      </div>
    `),e.map((e=>(0,r.qy)(l||(l=h`
          <div>
            <ha-device-picker
              allow-custom-entity
              .curValue=${0}
              .hass=${0}
              .deviceFilter=${0}
              .entityFilter=${0}
              .includeDomains=${0}
              .excludeDomains=${0}
              .includeDeviceClasses=${0}
              .value=${0}
              .label=${0}
              .disabled=${0}
              @value-changed=${0}
            ></ha-device-picker>
          </div>
        `),e,this.hass,this.deviceFilter,this.entityFilter,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,e,this.pickedDeviceLabel,this.disabled,this._deviceChanged))),this.hass,this.helper,this.deviceFilter,this.entityFilter,this.includeDomains,this.excludeDomains,e,this.includeDeviceClasses,this.pickDeviceLabel,this.disabled,this.required&&!e.length,this._addDevice)}get _currentDevices(){return this.value||[]}async _updateDevices(e){(0,a.r)(this,"value-changed",{value:e}),this.value=e}_deviceChanged(e){e.stopPropagation();const t=e.currentTarget.curValue,i=e.detail.value;i!==t&&(void 0===i?this._updateDevices(this._currentDevices.filter((e=>e!==t))):this._updateDevices(this._currentDevices.map((e=>e===t?i:e))))}async _addDevice(e){e.stopPropagation();const t=e.detail.value;if(e.currentTarget.value="",!t)return;const i=this._currentDevices;i.includes(t)||this._updateDevices([...i,t])}constructor(...e){super(...e),this.disabled=!1,this.required=!1}}v.styles=(0,r.AH)(u||(u=h`
    div {
      margin-top: 8px;
    }
  `)),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array})],v.prototype,"value",void 0),(0,s.__decorate)([(0,o.MZ)()],v.prototype,"helper",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],v.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],v.prototype,"required",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-domains"})],v.prototype,"includeDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-domains"})],v.prototype,"excludeDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-device-classes"})],v.prototype,"includeDeviceClasses",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"picked-device-label"})],v.prototype,"pickedDeviceLabel",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"pick-device-label"})],v.prototype,"pickDeviceLabel",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],v.prototype,"deviceFilter",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],v.prototype,"entityFilter",void 0),v=(0,s.__decorate)([(0,o.EM)("ha-devices-picker")],v),t()}catch(d){t(d)}}))},67373:function(e,t,i){i.a(e,(async function(e,s){try{i.r(t),i.d(t,{HaDeviceSelector:function(){return $}});i(35748),i(65315),i(837),i(59023),i(95013);var r=i(69868),o=i(84922),a=i(11991),n=i(65940),c=i(26846),d=i(73120),l=i(56083),u=i(71773),h=i(88120),v=i(32556),p=i(71755),_=i(65654),y=e([p,_]);[p,_]=y.then?(await y)():y;let m,f,b,g=e=>e;class $ extends o.WF{_hasIntegration(e){var t,i;return(null===(t=e.device)||void 0===t?void 0:t.filter)&&(0,c.e)(e.device.filter).some((e=>e.integration))||(null===(i=e.device)||void 0===i?void 0:i.entity)&&(0,c.e)(e.device.entity).some((e=>e.integration))}willUpdate(e){var t,i;e.get("selector")&&void 0!==this.value&&(null!==(t=this.selector.device)&&void 0!==t&&t.multiple&&!Array.isArray(this.value)?(this.value=[this.value],(0,d.r)(this,"value-changed",{value:this.value})):null!==(i=this.selector.device)&&void 0!==i&&i.multiple||!Array.isArray(this.value)||(this.value=this.value[0],(0,d.r)(this,"value-changed",{value:this.value})))}updated(e){super.updated(e),e.has("selector")&&this._hasIntegration(this.selector)&&!this._entitySources&&(0,u.c)(this.hass).then((e=>{this._entitySources=e})),!this._configEntries&&this._hasIntegration(this.selector)&&(this._configEntries=[],(0,h.VN)(this.hass).then((e=>{this._configEntries=e})))}render(){var e,t,i;return this._hasIntegration(this.selector)&&!this._entitySources?o.s6:null!==(e=this.selector.device)&&void 0!==e&&e.multiple?(0,o.qy)(f||(f=g`
      ${0}
      <ha-devices-picker
        .hass=${0}
        .value=${0}
        .helper=${0}
        .deviceFilter=${0}
        .entityFilter=${0}
        .disabled=${0}
        .required=${0}
      ></ha-devices-picker>
    `),this.label?(0,o.qy)(b||(b=g`<label>${0}</label>`),this.label):"",this.hass,this.value,this.helper,this._filterDevices,null!==(t=this.selector.device)&&void 0!==t&&t.entity?this._filterEntities:void 0,this.disabled,this.required):(0,o.qy)(m||(m=g`
        <ha-device-picker
          .hass=${0}
          .value=${0}
          .label=${0}
          .helper=${0}
          .deviceFilter=${0}
          .entityFilter=${0}
          .disabled=${0}
          .required=${0}
          allow-custom-entity
        ></ha-device-picker>
      `),this.hass,this.value,this.label,this.helper,this._filterDevices,null!==(i=this.selector.device)&&void 0!==i&&i.entity?this._filterEntities:void 0,this.disabled,this.required)}constructor(...e){super(...e),this.disabled=!1,this.required=!0,this._deviceIntegrationLookup=(0,n.A)(l.fk),this._filterDevices=e=>{var t;if(null===(t=this.selector.device)||void 0===t||!t.filter)return!0;const i=this._entitySources?this._deviceIntegrationLookup(this._entitySources,Object.values(this.hass.entities),Object.values(this.hass.devices),this._configEntries):void 0;return(0,c.e)(this.selector.device.filter).some((t=>(0,v.vX)(t,e,i)))},this._filterEntities=e=>(0,c.e)(this.selector.device.entity).some((t=>(0,v.Ru)(t,e,this._entitySources)))}}(0,r.__decorate)([(0,a.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,r.__decorate)([(0,a.MZ)({attribute:!1})],$.prototype,"selector",void 0),(0,r.__decorate)([(0,a.wk)()],$.prototype,"_entitySources",void 0),(0,r.__decorate)([(0,a.wk)()],$.prototype,"_configEntries",void 0),(0,r.__decorate)([(0,a.MZ)()],$.prototype,"value",void 0),(0,r.__decorate)([(0,a.MZ)()],$.prototype,"label",void 0),(0,r.__decorate)([(0,a.MZ)()],$.prototype,"helper",void 0),(0,r.__decorate)([(0,a.MZ)({type:Boolean})],$.prototype,"disabled",void 0),(0,r.__decorate)([(0,a.MZ)({type:Boolean})],$.prototype,"required",void 0),$=(0,r.__decorate)([(0,a.EM)("ha-selector-device")],$),s()}catch(m){s(m)}}))},71773:function(e,t,i){i.d(t,{c:function(){return o}});i(35748),i(5934),i(95013);const s=async(e,t,i,r,o,...a)=>{const n=o,c=n[e],d=c=>r&&r(o,c.result)!==c.cacheKey?(n[e]=void 0,s(e,t,i,r,o,...a)):c.result;if(c)return c instanceof Promise?c.then(d):d(c);const l=i(o,...a);return n[e]=l,l.then((i=>{n[e]={result:i,cacheKey:null==r?void 0:r(o,i)},setTimeout((()=>{n[e]=void 0}),t)}),(()=>{n[e]=void 0})),l},r=e=>e.callWS({type:"entity/source"}),o=e=>s("_entitySources",3e4,r,(e=>Object.keys(e.states).length),e)},28027:function(e,t,i){i.d(t,{QC:function(){return o},fK:function(){return r},p$:function(){return s}});i(24802);const s=(e,t,i)=>e(`component.${t}.title`)||(null==i?void 0:i.name)||t,r=(e,t)=>{const i={type:"manifest/list"};return t&&(i.integrations=t),e.callWS(i)},o=(e,t)=>e.callWS({type:"manifest/get",integration:t})},45363:function(e,t,i){i.d(t,{MR:function(){return s},a_:function(){return r},bg:function(){return o}});i(56660);const s=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,r=e=>e.split("/")[4],o=e=>e.startsWith("https://brands.home-assistant.io/")}}]);
//# sourceMappingURL=8574.c4dbe026a11c8345.js.map