/*! For license information please see 9460.10b68b1b2a4c07c4.js.LICENSE.txt */
export const __webpack_id__="9460";export const __webpack_ids__=["9460"];export const __webpack_modules__={47379:function(t,e,i){i.d(e,{u:()=>a});var s=i(90321);const a=t=>{return e=t.entity_id,void 0===(i=t.attributes).friendly_name?(0,s.Y)(e).replace(/_/g," "):(i.friendly_name??"").toString();var e,i}},92448:function(t,e,i){i.a(t,(async function(t,e){try{var s=i(69868),a=i(84922),o=i(11991),n=i(65940),r=i(26846),c=i(73120),l=i(47379),d=i(98137),h=i(28027),p=i(12527),u=i(86435),_=(i(36137),i(94966),i(93672),i(20014),i(95635),i(23114)),y=t([_]);_=(y.then?(await y)():y)[0];const v="M16,11.78L20.24,4.45L21.97,5.45L16.74,14.5L10.23,10.75L5.46,19H22V21H2V3H4V17.54L9.5,8L16,11.78Z",$="M15.07,11.25L14.17,12.17C13.45,12.89 13,13.5 13,15H11V14.5C11,13.39 11.45,12.39 12.17,11.67L13.41,10.41C13.78,10.05 14,9.55 14,9C14,7.89 13.1,7 12,7A2,2 0 0,0 10,9H8A4,4 0 0,1 12,5A4,4 0 0,1 16,9C16,9.88 15.64,10.67 15.07,11.25M13,19H11V17H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12C22,6.47 17.5,2 12,2Z",b="M11,13.5V21.5H3V13.5H11M12,2L17.5,11H6.5L12,2M17.5,13C20,13 22,15 22,17.5C22,20 20,22 17.5,22C15,22 13,20 13,17.5C13,15 15,13 17.5,13Z",m=["entity","external","no_state"],f="___missing-entity___";class g extends a.WF{willUpdate(t){(!this.hasUpdated&&!this.statisticIds||t.has("statisticTypes"))&&this._getStatisticIds()}async _getStatisticIds(){this.statisticIds=await(0,p.p3)(this.hass,this.statisticTypes)}_getAdditionalItems(){return[{id:f,primary:this.hass.localize("ui.components.statistic-picker.missing_entity"),icon_path:$}]}_computeItem(t){const e=this.hass.states[t];if(e){const i=this.hass.formatEntityName(e,"entity"),s=this.hass.formatEntityName(e,"device"),a=this.hass.formatEntityName(e,"area"),o=(0,d.qC)(this.hass),n=i||s||t,r=[a,i?s:void 0].filter(Boolean).join(o?" ◂ ":" ▸ "),c=(0,l.u)(e);return{id:t,statistic_id:t,primary:n,secondary:r,stateObj:e,type:"entity",sorting_label:[`${m.indexOf("entity")}`,s,i].join("_"),search_labels:[i,s,a,c,t].filter(Boolean)}}const i=this.statisticIds?this._statisticMetaData(t,this.statisticIds):void 0;if(i){if("external"===(t.includes(":")&&!t.includes(".")?"external":"no_state")){const e=`${m.indexOf("external")}`,s=(0,p.$O)(this.hass,t,i),a=t.split(":")[0],o=(0,h.p$)(this.hass.localize,a);return{id:t,statistic_id:t,primary:s,secondary:o,type:"external",sorting_label:[e,s].join("_"),search_labels:[s,o,t],icon_path:v}}}const s=`${m.indexOf("external")}`,a=(0,p.$O)(this.hass,t,i);return{id:t,primary:a,secondary:this.hass.localize("ui.components.statistic-picker.no_state"),type:"no_state",sorting_label:[s,a].join("_"),search_labels:[a,t],icon_path:b}}render(){const t=this.placeholder??this.hass.localize("ui.components.statistic-picker.placeholder"),e=this.hass.localize("ui.components.statistic-picker.no_match");return a.qy`
      <ha-generic-picker
        .hass=${this.hass}
        .autofocus=${this.autofocus}
        .allowCustomValue=${this.allowCustomEntity}
        .label=${this.label}
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
    `}_valueChanged(t){t.stopPropagation();const e=t.detail.value;e!==f?(this.value=e,(0,c.r)(this,"value-changed",{value:e})):window.open((0,u.o)(this.hass,this.helpMissingEntityUrl),"_blank")}async open(){await this.updateComplete,await(this._picker?.open())}constructor(...t){super(...t),this.autofocus=!1,this.disabled=!1,this.required=!1,this.helpMissingEntityUrl="/more-info/statistics/",this.entitiesOnly=!1,this.hideClearIcon=!1,this._getItems=()=>this._getStatisticsItems(this.hass,this.statisticIds,this.includeStatisticsUnitOfMeasurement,this.includeUnitClass,this.includeDeviceClass,this.entitiesOnly,this.excludeStatistics,this.value),this._getStatisticsItems=(0,n.A)(((t,e,i,s,a,o,n,c)=>{if(!e)return[];if(i){const t=(0,r.e)(i);e=e.filter((e=>t.includes(e.statistics_unit_of_measurement)))}if(s){const t=(0,r.e)(s);e=e.filter((e=>t.includes(e.unit_class)))}if(a){const t=(0,r.e)(a);e=e.filter((e=>{const i=this.hass.states[e.statistic_id];return!i||t.includes(i.attributes.device_class||"")}))}const u=(0,d.qC)(this.hass),_=[];return e.forEach((e=>{if(n&&e.statistic_id!==c&&n.includes(e.statistic_id))return;const i=this.hass.states[e.statistic_id];if(!i){if(!o){const t=e.statistic_id,i=(0,p.$O)(this.hass,e.statistic_id,e),s=e.statistic_id.includes(":")&&!e.statistic_id.includes(".")?"external":"no_state",a=`${m.indexOf(s)}`;if("no_state"===s)_.push({id:t,primary:i,secondary:this.hass.localize("ui.components.statistic-picker.no_state"),type:s,sorting_label:[a,i].join("_"),search_labels:[i,t],icon_path:b});else if("external"===s){const e=t.split(":")[0],o=(0,h.p$)(this.hass.localize,e);_.push({id:t,statistic_id:t,primary:i,secondary:o,type:s,sorting_label:[a,i].join("_"),search_labels:[i,o,t],icon_path:v})}}return}const s=e.statistic_id,a=(0,l.u)(i),r=t.formatEntityName(i,"entity"),d=t.formatEntityName(i,"device"),y=t.formatEntityName(i,"area"),$=r||d||s,f=[y,r?d:void 0].filter(Boolean).join(u?" ◂ ":" ▸ "),g=[d,r].filter(Boolean).join(" - "),C=`${m.indexOf("entity")}`;_.push({id:s,statistic_id:s,primary:$,secondary:f,a11y_label:g,stateObj:i,type:"entity",sorting_label:[C,d,r].join("_"),search_labels:[r,d,y,a,s].filter(Boolean)})})),_})),this._statisticMetaData=(0,n.A)(((t,e)=>{if(e)return e.find((e=>e.statistic_id===t))})),this._valueRenderer=t=>{const e=t,i=this._computeItem(e);return a.qy`
      ${i.stateObj?a.qy`
            <state-badge
              .hass=${this.hass}
              .stateObj=${i.stateObj}
              slot="start"
            ></state-badge>
          `:i.icon_path?a.qy`
              <ha-svg-icon slot="start" .path=${i.icon_path}></ha-svg-icon>
            `:a.s6}
      <span slot="headline">${i.primary}</span>
      ${i.secondary?a.qy`<span slot="supporting-text">${i.secondary}</span>`:a.s6}
    `},this._rowRenderer=(t,{index:e})=>{const i=this.hass.userData?.showEntityIdPicker;return a.qy`
      <ha-combo-box-item type="button" compact .borderTop=${0!==e}>
        ${t.icon_path?a.qy`
              <ha-svg-icon
                style="margin: 0 4px"
                slot="start"
                .path=${t.icon_path}
              ></ha-svg-icon>
            `:t.stateObj?a.qy`
                <state-badge
                  slot="start"
                  .stateObj=${t.stateObj}
                  .hass=${this.hass}
                ></state-badge>
              `:a.s6}
        <span slot="headline">${t.primary} </span>
        ${t.secondary?a.qy`<span slot="supporting-text">${t.secondary}</span>`:a.s6}
        ${t.statistic_id&&i?a.qy`<span slot="supporting-text" class="code">
              ${t.statistic_id}
            </span>`:a.s6}
      </ha-combo-box-item>
    `},this._searchFn=(t,e)=>{const i=e.findIndex((e=>e.stateObj?.entity_id===t||e.statistic_id===t));if(-1===i)return e;const[s]=e.splice(i,1);return e.unshift(s),e}}}(0,s.__decorate)([(0,o.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],g.prototype,"autofocus",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],g.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],g.prototype,"required",void 0),(0,s.__decorate)([(0,o.MZ)()],g.prototype,"label",void 0),(0,s.__decorate)([(0,o.MZ)()],g.prototype,"value",void 0),(0,s.__decorate)([(0,o.MZ)()],g.prototype,"helper",void 0),(0,s.__decorate)([(0,o.MZ)()],g.prototype,"placeholder",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"statistic-types"})],g.prototype,"statisticTypes",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean,attribute:"allow-custom-entity"})],g.prototype,"allowCustomEntity",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1,type:Array})],g.prototype,"statisticIds",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],g.prototype,"helpMissingEntityUrl",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-statistics-unit-of-measurement"})],g.prototype,"includeStatisticsUnitOfMeasurement",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"include-unit-class"})],g.prototype,"includeUnitClass",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"include-device-class"})],g.prototype,"includeDeviceClass",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean,attribute:"entities-only"})],g.prototype,"entitiesOnly",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-statistics"})],g.prototype,"excludeStatistics",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"hide-clear-icon",type:Boolean})],g.prototype,"hideClearIcon",void 0),(0,s.__decorate)([(0,o.P)("ha-generic-picker")],g.prototype,"_picker",void 0),g=(0,s.__decorate)([(0,o.EM)("ha-statistic-picker")],g),e()}catch(v){e(v)}}))},54803:function(t,e,i){i.a(t,(async function(t,e){try{var s=i(69868),a=i(84922),o=i(11991),n=i(33055),r=i(73120),c=i(92448),l=t([c]);c=(l.then?(await l)():l)[0];class d extends a.WF{render(){if(!this.hass)return a.s6;const t=this.ignoreRestrictionsOnFirstStatistic&&this._currentStatistics.length<=1,e=t?void 0:this.includeStatisticsUnitOfMeasurement,i=t?void 0:this.includeUnitClass,s=t?void 0:this.includeDeviceClass,o=t?void 0:this.statisticTypes;return a.qy`
      ${this.label?a.qy`<label>${this.label}</label>`:a.s6}
      ${(0,n.u)(this._currentStatistics,(t=>t),(t=>a.qy`
          <div>
            <ha-statistic-picker
              .curValue=${t}
              .hass=${this.hass}
              .includeStatisticsUnitOfMeasurement=${e}
              .includeUnitClass=${i}
              .includeDeviceClass=${s}
              .value=${t}
              .statisticTypes=${o}
              .statisticIds=${this.statisticIds}
              .excludeStatistics=${this.value}
              .allowCustomEntity=${this.allowCustomEntity}
              @value-changed=${this._statisticChanged}
            ></ha-statistic-picker>
          </div>
        `))}
      <div>
        <ha-statistic-picker
          .hass=${this.hass}
          .includeStatisticsUnitOfMeasurement=${this.includeStatisticsUnitOfMeasurement}
          .includeUnitClass=${this.includeUnitClass}
          .includeDeviceClass=${this.includeDeviceClass}
          .statisticTypes=${this.statisticTypes}
          .statisticIds=${this.statisticIds}
          .placeholder=${this.placeholder}
          .excludeStatistics=${this.value}
          .allowCustomEntity=${this.allowCustomEntity}
          @value-changed=${this._addStatistic}
        ></ha-statistic-picker>
      </div>
    `}get _currentStatistics(){return this.value||[]}async _updateStatistics(t){this.value=t,(0,r.r)(this,"value-changed",{value:t})}_statisticChanged(t){t.stopPropagation();const e=t.currentTarget.curValue,i=t.detail.value;if(i===e)return;const s=this._currentStatistics;i&&!s.includes(i)?this._updateStatistics(s.map((t=>t===e?i:t))):this._updateStatistics(s.filter((t=>t!==e)))}async _addStatistic(t){t.stopPropagation();const e=t.detail.value;if(!e)return;if(t.currentTarget.value="",!e)return;const i=this._currentStatistics;i.includes(e)||this._updateStatistics([...i,e])}constructor(...t){super(...t),this.ignoreRestrictionsOnFirstStatistic=!1}}d.styles=a.AH`
    :host {
      display: block;
    }
    ha-statistic-picker {
      display: block;
      width: 100%;
      margin-top: 8px;
    }
    label {
      display: block;
      margin-bottom: 0 0 8px;
    }
  `,(0,s.__decorate)([(0,o.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array})],d.prototype,"value",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1,type:Array})],d.prototype,"statisticIds",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"statistic-types"})],d.prototype,"statisticTypes",void 0),(0,s.__decorate)([(0,o.MZ)({type:String})],d.prototype,"label",void 0),(0,s.__decorate)([(0,o.MZ)({type:String})],d.prototype,"placeholder",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean,attribute:"allow-custom-entity"})],d.prototype,"allowCustomEntity",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"include-statistics-unit-of-measurement"})],d.prototype,"includeStatisticsUnitOfMeasurement",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"include-unit-class"})],d.prototype,"includeUnitClass",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:"include-device-class"})],d.prototype,"includeDeviceClass",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean,attribute:"ignore-restrictions-on-first-statistic"})],d.prototype,"ignoreRestrictionsOnFirstStatistic",void 0),d=(0,s.__decorate)([(0,o.EM)("ha-statistics-picker")],d),e()}catch(d){e(d)}}))},67261:function(t,e,i){i.a(t,(async function(t,s){try{i.r(e),i.d(e,{HaStatisticSelector:()=>l});var a=i(69868),o=i(84922),n=i(11991),r=i(54803),c=t([r]);r=(c.then?(await c)():c)[0];class l extends o.WF{render(){return this.selector.statistic.multiple?o.qy`
      ${this.label?o.qy`<label>${this.label}</label>`:""}
      <ha-statistics-picker
        .hass=${this.hass}
        .value=${this.value}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
      ></ha-statistics-picker>
    `:o.qy`<ha-statistic-picker
        .hass=${this.hass}
        .value=${this.value}
        .label=${this.label}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
        allow-custom-entity
      ></ha-statistic-picker>`}constructor(...t){super(...t),this.disabled=!1,this.required=!0}}(0,a.__decorate)([(0,n.MZ)({attribute:!1})],l.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],l.prototype,"selector",void 0),(0,a.__decorate)([(0,n.MZ)()],l.prototype,"value",void 0),(0,a.__decorate)([(0,n.MZ)()],l.prototype,"label",void 0),(0,a.__decorate)([(0,n.MZ)()],l.prototype,"helper",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],l.prototype,"disabled",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],l.prototype,"required",void 0),l=(0,a.__decorate)([(0,n.EM)("ha-selector-statistic")],l),s()}catch(l){s(l)}}))},6098:function(t,e,i){i.d(e,{HV:()=>o,Hh:()=>a,KF:()=>r,ON:()=>n,g0:()=>d,s7:()=>c});var s=i(87383);const a="unavailable",o="unknown",n="on",r="off",c=[a,o],l=[a,o,r],d=(0,s.g)(c);(0,s.g)(l)},28027:function(t,e,i){i.d(e,{QC:()=>o,fK:()=>a,p$:()=>s});const s=(t,e,i)=>t(`component.${e}.title`)||i?.name||e,a=(t,e)=>{const i={type:"manifest/list"};return e&&(i.integrations=e),t.callWS(i)},o=(t,e)=>t.callWS({type:"manifest/get",integration:e})},12527:function(t,e,i){i.d(e,{$O:()=>o,p3:()=>a});var s=i(47379);const a=(t,e)=>t.callWS({type:"recorder/list_statistic_ids",statistic_type:e}),o=(t,e,i)=>{const a=t.states[e];return a?(0,s.u)(a):i?.name||e}},86435:function(t,e,i){i.d(e,{o:()=>s});const s=(t,e)=>`https://${t.config.version.includes("b")?"rc":t.config.version.includes("dev")?"next":"www"}.home-assistant.io${e}`},60434:function(t,e,i){i.d(e,{T:()=>p});var s=i(11681),a=i(67851),o=i(40594);class n{disconnect(){this.G=void 0}reconnect(t){this.G=t}deref(){return this.G}constructor(t){this.G=t}}class r{get(){return this.Y}pause(){this.Y??=new Promise((t=>this.Z=t))}resume(){this.Z?.(),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var c=i(64363);const l=t=>!(0,a.sO)(t)&&"function"==typeof t.then,d=1073741823;class h extends o.Kq{render(...t){return t.find((t=>!l(t)))??s.c0}update(t,e){const i=this._$Cbt;let a=i.length;this._$Cbt=e;const o=this._$CK,n=this._$CX;this.isConnected||this.disconnected();for(let s=0;s<e.length&&!(s>this._$Cwt);s++){const t=e[s];if(!l(t))return this._$Cwt=s,t;s<a&&t===i[s]||(this._$Cwt=d,a=0,Promise.resolve(t).then((async e=>{for(;n.get();)await n.get();const i=o.deref();if(void 0!==i){const s=i._$Cbt.indexOf(t);s>-1&&s<i._$Cwt&&(i._$Cwt=s,i.setValue(e))}})))}return s.c0}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=d,this._$Cbt=[],this._$CK=new n(this),this._$CX=new r}}const p=(0,c.u$)(h)}};
//# sourceMappingURL=9460.10b68b1b2a4c07c4.js.map