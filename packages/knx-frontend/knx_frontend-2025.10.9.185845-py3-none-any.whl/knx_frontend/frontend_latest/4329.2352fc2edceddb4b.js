export const __webpack_id__="4329";export const __webpack_ids__=["4329"];export const __webpack_modules__={44537:function(e,t,i){i.d(t,{xn:()=>o,T:()=>a});var s=i(65940),r=i(47379);const o=e=>(e.name_by_user||e.name)?.trim(),a=(e,t,i)=>o(e)||i&&c(t,i)||t.localize("ui.panel.config.devices.unnamed_device",{type:t.localize(`ui.panel.config.devices.type.${e.entry_type||"device"}`)}),c=(e,t)=>{for(const i of t||[]){const t="string"==typeof i?i:i.entity_id,s=e.states[t];if(s)return(0,r.u)(s)}};(0,s.A)((e=>function(e){const t=new Set,i=new Set;for(const s of e)i.has(s)?t.add(s):i.add(s);return t}(Object.values(e).map((e=>o(e))).filter((e=>void 0!==e)))))},47379:function(e,t,i){i.d(t,{u:()=>r});var s=i(90321);const r=e=>{return t=e.entity_id,void 0===(i=e.attributes).friendly_name?(0,s.Y)(t).replace(/_/g," "):(i.friendly_name??"").toString();var t,i}},95710:function(e,t,i){var s=i(69868),r=i(84922),o=i(11991),a=i(65940),c=i(73120),d=i(22441),n=i(44537),l=i(92830);const h=(e,t)=>{const i=e.area_id,s=i?t.areas[i]:void 0,r=s?.floor_id;return{device:e,area:s||null,floor:(r?t.floors[r]:void 0)||null}};var u=i(88120),p=i(6041),v=i(28027),_=i(45363);i(94966);class y extends r.WF{firstUpdated(e){super.firstUpdated(e),this._loadConfigEntries()}async _loadConfigEntries(){const e=await(0,u.VN)(this.hass);this._configEntryLookup=Object.fromEntries(e.map((e=>[e.entry_id,e])))}render(){const e=this.placeholder??this.hass.localize("ui.components.device-picker.placeholder"),t=this.hass.localize("ui.components.device-picker.no_match"),i=this._valueRenderer(this._configEntryLookup);return r.qy`
      <ha-generic-picker
        .hass=${this.hass}
        .autofocus=${this.autofocus}
        .label=${this.label}
        .searchLabel=${this.searchLabel}
        .notFoundLabel=${t}
        .placeholder=${e}
        .value=${this.value}
        .rowRenderer=${this._rowRenderer}
        .getItems=${this._getItems}
        .hideClearIcon=${this.hideClearIcon}
        .valueRenderer=${i}
        @value-changed=${this._valueChanged}
      >
      </ha-generic-picker>
    `}async open(){await this.updateComplete,await(this._picker?.open())}_valueChanged(e){e.stopPropagation();const t=e.detail.value;this.value=t,(0,c.r)(this,"value-changed",{value:t})}constructor(...e){super(...e),this.autofocus=!1,this.disabled=!1,this.required=!1,this.hideClearIcon=!1,this._configEntryLookup={},this._getItems=()=>this._getDevices(this.hass.devices,this.hass.entities,this._configEntryLookup,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeDevices),this._getDevices=(0,a.A)(((e,t,i,s,r,o,a,c,u)=>{const _=Object.values(e),y=Object.values(t);let m={};(s||r||o||c)&&(m=(0,p.g2)(y));let b=_.filter((e=>e.id===this.value||!e.disabled_by));s&&(b=b.filter((e=>{const t=m[e.id];return!(!t||!t.length)&&m[e.id].some((e=>s.includes((0,l.m)(e.entity_id))))}))),r&&(b=b.filter((e=>{const t=m[e.id];return!t||!t.length||y.every((e=>!r.includes((0,l.m)(e.entity_id))))}))),u&&(b=b.filter((e=>!u.includes(e.id)))),o&&(b=b.filter((e=>{const t=m[e.id];return!(!t||!t.length)&&m[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&o.includes(t.attributes.device_class))}))}))),c&&(b=b.filter((e=>{const t=m[e.id];return!(!t||!t.length)&&t.some((e=>{const t=this.hass.states[e.entity_id];return!!t&&c(t)}))}))),a&&(b=b.filter((e=>e.id===this.value||a(e))));return b.map((e=>{const t=(0,n.T)(e,this.hass,m[e.id]),{area:s}=h(e,this.hass),r=s?(0,d.A)(s):void 0,o=e.primary_config_entry?i?.[e.primary_config_entry]:void 0,a=o?.domain,c=a?(0,v.p$)(this.hass.localize,a):void 0;return{id:e.id,label:"",primary:t||this.hass.localize("ui.components.device-picker.unnamed_device"),secondary:r,domain:o?.domain,domain_name:c,search_labels:[t,r,a,c].filter(Boolean),sorting_label:t||"zzz"}}))})),this._valueRenderer=(0,a.A)((e=>t=>{const i=t,s=this.hass.devices[i];if(!s)return r.qy`<span slot="headline">${i}</span>`;const{area:o}=h(s,this.hass),a=s?(0,n.xn)(s):void 0,c=o?(0,d.A)(o):void 0,l=s.primary_config_entry?e[s.primary_config_entry]:void 0;return r.qy`
        ${l?r.qy`<img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${(0,_.MR)({domain:l.domain,type:"icon",darkOptimized:this.hass.themes?.darkMode})}
            />`:r.s6}
        <span slot="headline">${a}</span>
        <span slot="supporting-text">${c}</span>
      `})),this._rowRenderer=e=>r.qy`
    <ha-combo-box-item type="button">
      ${e.domain?r.qy`
            <img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${(0,_.MR)({domain:e.domain,type:"icon",darkOptimized:this.hass.themes.darkMode})}
            />
          `:r.s6}

      <span slot="headline">${e.primary}</span>
      ${e.secondary?r.qy`<span slot="supporting-text">${e.secondary}</span>`:r.s6}
      ${e.domain_name?r.qy`
            <div slot="trailing-supporting-text" class="domain">
              ${e.domain_name}
            </div>
          `:r.s6}
    </ha-combo-box-item>
  `}}(0,s.__decorate)([(0,o.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],y.prototype,"autofocus",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],y.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],y.prototype,"required",void 0),(0,s.__decorate)([(0,o.MZ)()],y.prototype,"label",void 0),(0,s.__decorate)([(0,o.MZ)()],y.prototype,"value",void 0),(0,s.__decorate)([(0,o.MZ)()],y.prototype,"helper",void 0),(0,s.__decorate)([(0,o.MZ)()],y.prototype,"placeholder",void 0),(0,s.__decorate)([(0,o.MZ)({type:String,attribute:"search-label"})],y.prototype,"searchLabel",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1,type:Array})],y.prototype,"createDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-domains"})],y.prototype,"includeDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-domains"})],y.prototype,"excludeDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-device-classes"})],y.prototype,"includeDeviceClasses",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-devices"})],y.prototype,"excludeDevices",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],y.prototype,"deviceFilter",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],y.prototype,"entityFilter",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"hide-clear-icon",type:Boolean})],y.prototype,"hideClearIcon",void 0),(0,s.__decorate)([(0,o.P)("ha-generic-picker")],y.prototype,"_picker",void 0),(0,s.__decorate)([(0,o.wk)()],y.prototype,"_configEntryLookup",void 0),y=(0,s.__decorate)([(0,o.EM)("ha-device-picker")],y)},26672:function(e,t,i){i.r(t),i.d(t,{HaDeviceSelector:()=>v});var s=i(69868),r=i(84922),o=i(11991),a=i(65940),c=i(26846),d=i(73120),n=i(6041),l=i(71773),h=i(88120),u=i(32556);i(95710);class p extends r.WF{render(){if(!this.hass)return r.s6;const e=this._currentDevices;return r.qy`
      ${e.map((e=>r.qy`
          <div>
            <ha-device-picker
              allow-custom-entity
              .curValue=${e}
              .hass=${this.hass}
              .deviceFilter=${this.deviceFilter}
              .entityFilter=${this.entityFilter}
              .includeDomains=${this.includeDomains}
              .excludeDomains=${this.excludeDomains}
              .includeDeviceClasses=${this.includeDeviceClasses}
              .value=${e}
              .label=${this.pickedDeviceLabel}
              .disabled=${this.disabled}
              @value-changed=${this._deviceChanged}
            ></ha-device-picker>
          </div>
        `))}
      <div>
        <ha-device-picker
          allow-custom-entity
          .hass=${this.hass}
          .helper=${this.helper}
          .deviceFilter=${this.deviceFilter}
          .entityFilter=${this.entityFilter}
          .includeDomains=${this.includeDomains}
          .excludeDomains=${this.excludeDomains}
          .excludeDevices=${e}
          .includeDeviceClasses=${this.includeDeviceClasses}
          .label=${this.pickDeviceLabel}
          .disabled=${this.disabled}
          .required=${this.required&&!e.length}
          @value-changed=${this._addDevice}
        ></ha-device-picker>
      </div>
    `}get _currentDevices(){return this.value||[]}async _updateDevices(e){(0,d.r)(this,"value-changed",{value:e}),this.value=e}_deviceChanged(e){e.stopPropagation();const t=e.currentTarget.curValue,i=e.detail.value;i!==t&&(void 0===i?this._updateDevices(this._currentDevices.filter((e=>e!==t))):this._updateDevices(this._currentDevices.map((e=>e===t?i:e))))}async _addDevice(e){e.stopPropagation();const t=e.detail.value;if(e.currentTarget.value="",!t)return;const i=this._currentDevices;i.includes(t)||this._updateDevices([...i,t])}constructor(...e){super(...e),this.disabled=!1,this.required=!1}}p.styles=r.AH`
    div {
      margin-top: 8px;
    }
  `,(0,s.__decorate)([(0,o.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array})],p.prototype,"value",void 0),(0,s.__decorate)([(0,o.MZ)()],p.prototype,"helper",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-domains"})],p.prototype,"includeDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-domains"})],p.prototype,"excludeDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-device-classes"})],p.prototype,"includeDeviceClasses",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"picked-device-label"})],p.prototype,"pickedDeviceLabel",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"pick-device-label"})],p.prototype,"pickDeviceLabel",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],p.prototype,"deviceFilter",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],p.prototype,"entityFilter",void 0),p=(0,s.__decorate)([(0,o.EM)("ha-devices-picker")],p);class v extends r.WF{_hasIntegration(e){return e.device?.filter&&(0,c.e)(e.device.filter).some((e=>e.integration))||e.device?.entity&&(0,c.e)(e.device.entity).some((e=>e.integration))}willUpdate(e){e.get("selector")&&void 0!==this.value&&(this.selector.device?.multiple&&!Array.isArray(this.value)?(this.value=[this.value],(0,d.r)(this,"value-changed",{value:this.value})):!this.selector.device?.multiple&&Array.isArray(this.value)&&(this.value=this.value[0],(0,d.r)(this,"value-changed",{value:this.value})))}updated(e){super.updated(e),e.has("selector")&&this._hasIntegration(this.selector)&&!this._entitySources&&(0,l.c)(this.hass).then((e=>{this._entitySources=e})),!this._configEntries&&this._hasIntegration(this.selector)&&(this._configEntries=[],(0,h.VN)(this.hass).then((e=>{this._configEntries=e})))}render(){return this._hasIntegration(this.selector)&&!this._entitySources?r.s6:this.selector.device?.multiple?r.qy`
      ${this.label?r.qy`<label>${this.label}</label>`:""}
      <ha-devices-picker
        .hass=${this.hass}
        .value=${this.value}
        .helper=${this.helper}
        .deviceFilter=${this._filterDevices}
        .entityFilter=${this.selector.device?.entity?this._filterEntities:void 0}
        .disabled=${this.disabled}
        .required=${this.required}
      ></ha-devices-picker>
    `:r.qy`
        <ha-device-picker
          .hass=${this.hass}
          .value=${this.value}
          .label=${this.label}
          .helper=${this.helper}
          .deviceFilter=${this._filterDevices}
          .entityFilter=${this.selector.device?.entity?this._filterEntities:void 0}
          .disabled=${this.disabled}
          .required=${this.required}
          allow-custom-entity
        ></ha-device-picker>
      `}constructor(...e){super(...e),this.disabled=!1,this.required=!0,this._deviceIntegrationLookup=(0,a.A)(n.fk),this._filterDevices=e=>{if(!this.selector.device?.filter)return!0;const t=this._entitySources?this._deviceIntegrationLookup(this._entitySources,Object.values(this.hass.entities),Object.values(this.hass.devices),this._configEntries):void 0;return(0,c.e)(this.selector.device.filter).some((i=>(0,u.vX)(i,e,t)))},this._filterEntities=e=>(0,c.e)(this.selector.device.entity).some((t=>(0,u.Ru)(t,e,this._entitySources)))}}(0,s.__decorate)([(0,o.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],v.prototype,"selector",void 0),(0,s.__decorate)([(0,o.wk)()],v.prototype,"_entitySources",void 0),(0,s.__decorate)([(0,o.wk)()],v.prototype,"_configEntries",void 0),(0,s.__decorate)([(0,o.MZ)()],v.prototype,"value",void 0),(0,s.__decorate)([(0,o.MZ)()],v.prototype,"label",void 0),(0,s.__decorate)([(0,o.MZ)()],v.prototype,"helper",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],v.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],v.prototype,"required",void 0),v=(0,s.__decorate)([(0,o.EM)("ha-selector-device")],v)},71773:function(e,t,i){i.d(t,{c:()=>o});const s=async(e,t,i,r,o,...a)=>{const c=o,d=c[e],n=d=>r&&r(o,d.result)!==d.cacheKey?(c[e]=void 0,s(e,t,i,r,o,...a)):d.result;if(d)return d instanceof Promise?d.then(n):n(d);const l=i(o,...a);return c[e]=l,l.then((i=>{c[e]={result:i,cacheKey:r?.(o,i)},setTimeout((()=>{c[e]=void 0}),t)}),(()=>{c[e]=void 0})),l},r=e=>e.callWS({type:"entity/source"}),o=e=>s("_entitySources",3e4,r,(e=>Object.keys(e.states).length),e)},28027:function(e,t,i){i.d(t,{QC:()=>o,fK:()=>r,p$:()=>s});const s=(e,t,i)=>e(`component.${t}.title`)||i?.name||t,r=(e,t)=>{const i={type:"manifest/list"};return t&&(i.integrations=t),e.callWS(i)},o=(e,t)=>e.callWS({type:"manifest/get",integration:t})},45363:function(e,t,i){i.d(t,{MR:()=>s,a_:()=>r,bg:()=>o});const s=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,r=e=>e.split("/")[4],o=e=>e.startsWith("https://brands.home-assistant.io/")}};
//# sourceMappingURL=4329.2352fc2edceddb4b.js.map