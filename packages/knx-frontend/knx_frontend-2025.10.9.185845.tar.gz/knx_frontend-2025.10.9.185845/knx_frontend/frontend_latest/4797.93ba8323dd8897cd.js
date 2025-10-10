/*! For license information please see 4797.93ba8323dd8897cd.js.LICENSE.txt */
export const __webpack_id__="4797";export const __webpack_ids__=["4797"];export const __webpack_modules__={47379:function(t,e,i){i.d(e,{u:()=>a});var s=i(90321);const a=t=>{return e=t.entity_id,void 0===(i=t.attributes).friendly_name?(0,s.Y)(e).replace(/_/g," "):(i.friendly_name??"").toString();var e,i}},41602:function(t,e,i){i.d(e,{n:()=>a});const s=/^(\w+)\.(\w+)$/,a=t=>s.test(t)},31675:function(t,e,i){i.a(t,(async function(t,e){try{var s=i(69868),a=i(84922),r=i(11991),n=i(65940),o=i(73120),l=i(41602),d=(i(8115),i(57447)),c=t([d]);d=(c.then?(await c)():c)[0];const h="M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z";class u extends a.WF{render(){if(!this.hass)return a.s6;const t=this._currentEntities;return a.qy`
      ${this.label?a.qy`<label>${this.label}</label>`:a.s6}
      <ha-sortable
        .disabled=${!this.reorder||this.disabled}
        handle-selector=".entity-handle"
        @item-moved=${this._entityMoved}
      >
        <div class="list">
          ${t.map((t=>a.qy`
              <div class="entity">
                <ha-entity-picker
                  allow-custom-entity
                  .curValue=${t}
                  .hass=${this.hass}
                  .includeDomains=${this.includeDomains}
                  .excludeDomains=${this.excludeDomains}
                  .includeEntities=${this.includeEntities}
                  .excludeEntities=${this.excludeEntities}
                  .includeDeviceClasses=${this.includeDeviceClasses}
                  .includeUnitOfMeasurement=${this.includeUnitOfMeasurement}
                  .entityFilter=${this.entityFilter}
                  .value=${t}
                  .disabled=${this.disabled}
                  .createDomains=${this.createDomains}
                  @value-changed=${this._entityChanged}
                ></ha-entity-picker>
                ${this.reorder?a.qy`
                      <ha-svg-icon
                        class="entity-handle"
                        .path=${h}
                      ></ha-svg-icon>
                    `:a.s6}
              </div>
            `))}
        </div>
      </ha-sortable>
      <div>
        <ha-entity-picker
          allow-custom-entity
          .hass=${this.hass}
          .includeDomains=${this.includeDomains}
          .excludeDomains=${this.excludeDomains}
          .includeEntities=${this.includeEntities}
          .excludeEntities=${this._excludeEntities(this.value,this.excludeEntities)}
          .includeDeviceClasses=${this.includeDeviceClasses}
          .includeUnitOfMeasurement=${this.includeUnitOfMeasurement}
          .entityFilter=${this.entityFilter}
          .placeholder=${this.placeholder}
          .helper=${this.helper}
          .disabled=${this.disabled}
          .createDomains=${this.createDomains}
          .required=${this.required&&!t.length}
          @value-changed=${this._addEntity}
        ></ha-entity-picker>
      </div>
    `}_entityMoved(t){t.stopPropagation();const{oldIndex:e,newIndex:i}=t.detail,s=this._currentEntities,a=s[e],r=[...s];r.splice(e,1),r.splice(i,0,a),this._updateEntities(r)}get _currentEntities(){return this.value||[]}async _updateEntities(t){this.value=t,(0,o.r)(this,"value-changed",{value:t})}_entityChanged(t){t.stopPropagation();const e=t.currentTarget.curValue,i=t.detail.value;if(i===e||void 0!==i&&!(0,l.n)(i))return;const s=this._currentEntities;i&&!s.includes(i)?this._updateEntities(s.map((t=>t===e?i:t))):this._updateEntities(s.filter((t=>t!==e)))}async _addEntity(t){t.stopPropagation();const e=t.detail.value;if(!e)return;if(t.currentTarget.value="",!e)return;const i=this._currentEntities;i.includes(e)||this._updateEntities([...i,e])}constructor(...t){super(...t),this.disabled=!1,this.required=!1,this.reorder=!1,this._excludeEntities=(0,n.A)(((t,e)=>void 0===t?e:[...e||[],...t]))}}u.styles=a.AH`
    div {
      margin-top: 8px;
    }
    label {
      display: block;
      margin: 0 0 8px;
    }
    .entity {
      display: flex;
      flex-direction: row;
      align-items: center;
    }
    .entity ha-entity-picker {
      flex: 1;
    }
    .entity-handle {
      padding: 8px;
      cursor: move; /* fallback if grab cursor is unsupported */
      cursor: grab;
    }
  `,(0,s.__decorate)([(0,r.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array})],u.prototype,"value",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],u.prototype,"disabled",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],u.prototype,"required",void 0),(0,s.__decorate)([(0,r.MZ)()],u.prototype,"label",void 0),(0,s.__decorate)([(0,r.MZ)()],u.prototype,"placeholder",void 0),(0,s.__decorate)([(0,r.MZ)()],u.prototype,"helper",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array,attribute:"include-domains"})],u.prototype,"includeDomains",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array,attribute:"exclude-domains"})],u.prototype,"excludeDomains",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array,attribute:"include-device-classes"})],u.prototype,"includeDeviceClasses",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array,attribute:"include-unit-of-measurement"})],u.prototype,"includeUnitOfMeasurement",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array,attribute:"include-entities"})],u.prototype,"includeEntities",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array,attribute:"exclude-entities"})],u.prototype,"excludeEntities",void 0),(0,s.__decorate)([(0,r.MZ)({attribute:!1})],u.prototype,"entityFilter",void 0),(0,s.__decorate)([(0,r.MZ)({attribute:!1,type:Array})],u.prototype,"createDomains",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],u.prototype,"reorder",void 0),u=(0,s.__decorate)([(0,r.EM)("ha-entities-picker")],u),e()}catch(h){e(h)}}))},57447:function(t,e,i){i.a(t,(async function(t,e){try{var s=i(69868),a=i(84922),r=i(11991),n=i(65940),o=i(73120),l=i(92830),d=i(47379),c=i(41602),h=i(98137),u=i(28027),p=i(5940),y=i(80608),_=(i(36137),i(94966),i(95635),i(23114)),v=t([_]);_=(v.then?(await v)():v)[0];const m="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",$="M11,13.5V21.5H3V13.5H11M12,2L17.5,11H6.5L12,2M17.5,13C20,13 22,15 22,17.5C22,20 20,22 17.5,22C15,22 13,20 13,17.5C13,15 15,13 17.5,13Z",b="___create-new-entity___";class f extends a.WF{firstUpdated(t){super.firstUpdated(t),this.hass.loadBackendTranslation("title")}get _showEntityId(){return this.showEntityId||this.hass.userData?.showEntityIdPicker}render(){const t=this.placeholder??this.hass.localize("ui.components.entity.entity-picker.placeholder"),e=this.hass.localize("ui.components.entity.entity-picker.no_match");return a.qy`
      <ha-generic-picker
        .hass=${this.hass}
        .disabled=${this.disabled}
        .autofocus=${this.autofocus}
        .allowCustomValue=${this.allowCustomEntity}
        .label=${this.label}
        .helper=${this.helper}
        .searchLabel=${this.searchLabel}
        .notFoundLabel=${e}
        .placeholder=${t}
        .value=${this.value}
        .rowRenderer=${this._rowRenderer}
        .getItems=${this._getItems}
        .getAdditionalItems=${this._getAdditionalItems}
        .hideClearIcon=${this.hideClearIcon}
        .searchFn=${this._searchFn}
        .valueRenderer=${this._valueRenderer}
        @value-changed=${this._valueChanged}
      >
      </ha-generic-picker>
    `}async open(){await this.updateComplete,await(this._picker?.open())}_valueChanged(t){t.stopPropagation();const e=t.detail.value;if(e)if(e.startsWith(b)){const t=e.substring(b.length);(0,y.$)(this,{domain:t,dialogClosedCallback:t=>{t.entityId&&this._setValue(t.entityId)}})}else(0,c.n)(e)&&this._setValue(e);else this._setValue(void 0)}_setValue(t){this.value=t,(0,o.r)(this,"value-changed",{value:t}),(0,o.r)(this,"change")}constructor(...t){super(...t),this.autofocus=!1,this.disabled=!1,this.required=!1,this.showEntityId=!1,this.hideClearIcon=!1,this._valueRenderer=t=>{const e=t||"",i=this.hass.states[e];if(!i)return a.qy`
        <ha-svg-icon
          slot="start"
          .path=${$}
          style="margin: 0 4px"
        ></ha-svg-icon>
        <span slot="headline">${e}</span>
      `;const s=this.hass.formatEntityName(i,"entity"),r=this.hass.formatEntityName(i,"device"),n=this.hass.formatEntityName(i,"area"),o=(0,h.qC)(this.hass),l=s||r||e,d=[n,s?r:void 0].filter(Boolean).join(o?" ◂ ":" ▸ ");return a.qy`
      <state-badge
        .hass=${this.hass}
        .stateObj=${i}
        slot="start"
      ></state-badge>
      <span slot="headline">${l}</span>
      <span slot="supporting-text">${d}</span>
    `},this._rowRenderer=(t,{index:e})=>{const i=this._showEntityId;return a.qy`
      <ha-combo-box-item type="button" compact .borderTop=${0!==e}>
        ${t.icon_path?a.qy`
              <ha-svg-icon
                slot="start"
                style="margin: 0 4px"
                .path=${t.icon_path}
              ></ha-svg-icon>
            `:a.qy`
              <state-badge
                slot="start"
                .stateObj=${t.stateObj}
                .hass=${this.hass}
              ></state-badge>
            `}
        <span slot="headline">${t.primary}</span>
        ${t.secondary?a.qy`<span slot="supporting-text">${t.secondary}</span>`:a.s6}
        ${t.stateObj&&i?a.qy`
              <span slot="supporting-text" class="code">
                ${t.stateObj.entity_id}
              </span>
            `:a.s6}
        ${t.domain_name&&!i?a.qy`
              <div slot="trailing-supporting-text" class="domain">
                ${t.domain_name}
              </div>
            `:a.s6}
      </ha-combo-box-item>
    `},this._getAdditionalItems=()=>this._getCreateItems(this.hass.localize,this.createDomains),this._getCreateItems=(0,n.A)(((t,e)=>e?.length?e.map((e=>{const i=t("ui.components.entity.entity-picker.create_helper",{domain:(0,p.z)(e)?t(`ui.panel.config.helpers.types.${e}`):(0,u.p$)(t,e)});return{id:b+e,primary:i,secondary:t("ui.components.entity.entity-picker.new_entity"),icon_path:m}})):[])),this._getItems=()=>this._getEntities(this.hass,this.includeDomains,this.excludeDomains,this.entityFilter,this.includeDeviceClasses,this.includeUnitOfMeasurement,this.includeEntities,this.excludeEntities),this._getEntities=(0,n.A)(((t,e,i,s,a,r,n,o)=>{let c=[],p=Object.keys(t.states);n&&(p=p.filter((t=>n.includes(t)))),o&&(p=p.filter((t=>!o.includes(t)))),e&&(p=p.filter((t=>e.includes((0,l.m)(t))))),i&&(p=p.filter((t=>!i.includes((0,l.m)(t)))));const y=(0,h.qC)(this.hass);return c=p.map((e=>{const i=t.states[e],s=(0,d.u)(i),a=this.hass.formatEntityName(i,"entity"),r=this.hass.formatEntityName(i,"device"),n=this.hass.formatEntityName(i,"area"),o=(0,u.p$)(this.hass.localize,(0,l.m)(e)),c=a||r||e,h=[n,a?r:void 0].filter(Boolean).join(y?" ◂ ":" ▸ "),p=[r,a].filter(Boolean).join(" - ");return{id:e,primary:c,secondary:h,domain_name:o,sorting_label:[r,a].filter(Boolean).join("_"),search_labels:[a,r,n,o,s,e].filter(Boolean),a11y_label:p,stateObj:i}})),a&&(c=c.filter((t=>t.id===this.value||t.stateObj?.attributes.device_class&&a.includes(t.stateObj.attributes.device_class)))),r&&(c=c.filter((t=>t.id===this.value||t.stateObj?.attributes.unit_of_measurement&&r.includes(t.stateObj.attributes.unit_of_measurement)))),s&&(c=c.filter((t=>t.id===this.value||t.stateObj&&s(t.stateObj)))),c})),this._searchFn=(t,e)=>{const i=e.findIndex((e=>e.stateObj?.entity_id===t));if(-1===i)return e;const[s]=e.splice(i,1);return e.unshift(s),e}}}(0,s.__decorate)([(0,r.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],f.prototype,"autofocus",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],f.prototype,"disabled",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],f.prototype,"required",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean,attribute:"allow-custom-entity"})],f.prototype,"allowCustomEntity",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean,attribute:"show-entity-id"})],f.prototype,"showEntityId",void 0),(0,s.__decorate)([(0,r.MZ)()],f.prototype,"label",void 0),(0,s.__decorate)([(0,r.MZ)()],f.prototype,"value",void 0),(0,s.__decorate)([(0,r.MZ)()],f.prototype,"helper",void 0),(0,s.__decorate)([(0,r.MZ)()],f.prototype,"placeholder",void 0),(0,s.__decorate)([(0,r.MZ)({type:String,attribute:"search-label"})],f.prototype,"searchLabel",void 0),(0,s.__decorate)([(0,r.MZ)({attribute:!1,type:Array})],f.prototype,"createDomains",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array,attribute:"include-domains"})],f.prototype,"includeDomains",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array,attribute:"exclude-domains"})],f.prototype,"excludeDomains",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array,attribute:"include-device-classes"})],f.prototype,"includeDeviceClasses",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array,attribute:"include-unit-of-measurement"})],f.prototype,"includeUnitOfMeasurement",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array,attribute:"include-entities"})],f.prototype,"includeEntities",void 0),(0,s.__decorate)([(0,r.MZ)({type:Array,attribute:"exclude-entities"})],f.prototype,"excludeEntities",void 0),(0,s.__decorate)([(0,r.MZ)({attribute:!1})],f.prototype,"entityFilter",void 0),(0,s.__decorate)([(0,r.MZ)({attribute:"hide-clear-icon",type:Boolean})],f.prototype,"hideClearIcon",void 0),(0,s.__decorate)([(0,r.P)("ha-generic-picker")],f.prototype,"_picker",void 0),f=(0,s.__decorate)([(0,r.EM)("ha-entity-picker")],f),e()}catch(m){e(m)}}))},99888:function(t,e,i){i.a(t,(async function(t,s){try{i.r(e),i.d(e,{HaEntitySelector:()=>y});var a=i(69868),r=i(84922),n=i(11991),o=i(26846),l=i(73120),d=i(71773),c=i(32556),h=i(31675),u=i(57447),p=t([h,u]);[h,u]=p.then?(await p)():p;class y extends r.WF{_hasIntegration(t){return t.entity?.filter&&(0,o.e)(t.entity.filter).some((t=>t.integration))}willUpdate(t){t.get("selector")&&void 0!==this.value&&(this.selector.entity?.multiple&&!Array.isArray(this.value)?(this.value=[this.value],(0,l.r)(this,"value-changed",{value:this.value})):!this.selector.entity?.multiple&&Array.isArray(this.value)&&(this.value=this.value[0],(0,l.r)(this,"value-changed",{value:this.value})))}render(){return this._hasIntegration(this.selector)&&!this._entitySources?r.s6:this.selector.entity?.multiple?r.qy`
      <ha-entities-picker
        .hass=${this.hass}
        .value=${this.value}
        .label=${this.label}
        .helper=${this.helper}
        .includeEntities=${this.selector.entity.include_entities}
        .excludeEntities=${this.selector.entity.exclude_entities}
        .reorder=${this.selector.entity.reorder??!1}
        .entityFilter=${this._filterEntities}
        .createDomains=${this._createDomains}
        .disabled=${this.disabled}
        .required=${this.required}
      ></ha-entities-picker>
    `:r.qy`<ha-entity-picker
        .hass=${this.hass}
        .value=${this.value}
        .label=${this.label}
        .helper=${this.helper}
        .includeEntities=${this.selector.entity?.include_entities}
        .excludeEntities=${this.selector.entity?.exclude_entities}
        .entityFilter=${this._filterEntities}
        .createDomains=${this._createDomains}
        .disabled=${this.disabled}
        .required=${this.required}
        allow-custom-entity
      ></ha-entity-picker>`}updated(t){super.updated(t),t.has("selector")&&this._hasIntegration(this.selector)&&!this._entitySources&&(0,d.c)(this.hass).then((t=>{this._entitySources=t})),t.has("selector")&&(this._createDomains=(0,c.Lo)(this.selector))}constructor(...t){super(...t),this.disabled=!1,this.required=!0,this._filterEntities=t=>!this.selector?.entity?.filter||(0,o.e)(this.selector.entity.filter).some((e=>(0,c.Ru)(e,t,this._entitySources)))}}(0,a.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"selector",void 0),(0,a.__decorate)([(0,n.wk)()],y.prototype,"_entitySources",void 0),(0,a.__decorate)([(0,n.MZ)()],y.prototype,"value",void 0),(0,a.__decorate)([(0,n.MZ)()],y.prototype,"label",void 0),(0,a.__decorate)([(0,n.MZ)()],y.prototype,"helper",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],y.prototype,"disabled",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],y.prototype,"required",void 0),(0,a.__decorate)([(0,n.wk)()],y.prototype,"_createDomains",void 0),y=(0,a.__decorate)([(0,n.EM)("ha-selector-entity")],y),s()}catch(y){s(y)}}))},6098:function(t,e,i){i.d(e,{HV:()=>r,Hh:()=>a,KF:()=>o,ON:()=>n,g0:()=>c,s7:()=>l});var s=i(87383);const a="unavailable",r="unknown",n="on",o="off",l=[a,r],d=[a,r,o],c=(0,s.g)(l);(0,s.g)(d)},71773:function(t,e,i){i.d(e,{c:()=>r});const s=async(t,e,i,a,r,...n)=>{const o=r,l=o[t],d=l=>a&&a(r,l.result)!==l.cacheKey?(o[t]=void 0,s(t,e,i,a,r,...n)):l.result;if(l)return l instanceof Promise?l.then(d):d(l);const c=i(r,...n);return o[t]=c,c.then((i=>{o[t]={result:i,cacheKey:a?.(r,i)},setTimeout((()=>{o[t]=void 0}),e)}),(()=>{o[t]=void 0})),c},a=t=>t.callWS({type:"entity/source"}),r=t=>s("_entitySources",3e4,a,(t=>Object.keys(t.states).length),t)},28027:function(t,e,i){i.d(e,{QC:()=>r,fK:()=>a,p$:()=>s});const s=(t,e,i)=>t(`component.${e}.title`)||i?.name||e,a=(t,e)=>{const i={type:"manifest/list"};return e&&(i.integrations=e),t.callWS(i)},r=(t,e)=>t.callWS({type:"manifest/get",integration:e})},80608:function(t,e,i){i.d(e,{$:()=>r});var s=i(73120);const a=()=>i.e("8221").then(i.bind(i,27084)),r=(t,e)=>{(0,s.r)(t,"show-dialog",{dialogTag:"dialog-helper-detail",dialogImport:a,dialogParams:e})}},60434:function(t,e,i){i.d(e,{T:()=>u});var s=i(11681),a=i(67851),r=i(40594);class n{disconnect(){this.G=void 0}reconnect(t){this.G=t}deref(){return this.G}constructor(t){this.G=t}}class o{get(){return this.Y}pause(){this.Y??=new Promise((t=>this.Z=t))}resume(){this.Z?.(),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var l=i(64363);const d=t=>!(0,a.sO)(t)&&"function"==typeof t.then,c=1073741823;class h extends r.Kq{render(...t){return t.find((t=>!d(t)))??s.c0}update(t,e){const i=this._$Cbt;let a=i.length;this._$Cbt=e;const r=this._$CK,n=this._$CX;this.isConnected||this.disconnected();for(let s=0;s<e.length&&!(s>this._$Cwt);s++){const t=e[s];if(!d(t))return this._$Cwt=s,t;s<a&&t===i[s]||(this._$Cwt=c,a=0,Promise.resolve(t).then((async e=>{for(;n.get();)await n.get();const i=r.deref();if(void 0!==i){const s=i._$Cbt.indexOf(t);s>-1&&s<i._$Cwt&&(i._$Cwt=s,i.setValue(e))}})))}return s.c0}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=c,this._$Cbt=[],this._$CK=new n(this),this._$CX=new o}}const u=(0,l.u$)(h)}};
//# sourceMappingURL=4797.93ba8323dd8897cd.js.map