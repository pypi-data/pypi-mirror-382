export const __webpack_id__="9352";export const __webpack_ids__=["9352"];export const __webpack_modules__={85759:function(e,t,i){i.d(t,{M:()=>s,l:()=>a});const a=new Set(["primary","accent","disabled","red","pink","purple","deep-purple","indigo","blue","light-blue","cyan","teal","green","light-green","lime","yellow","amber","orange","deep-orange","brown","light-grey","grey","dark-grey","blue-grey","black","white"]);function s(e){return a.has(e)?`var(--${e}-color)`:e}},85032:function(e,t,i){var a=i(69868),s=i(84922),o=i(11991),l=i(65940),r=i(73120),c=i(92830),n=i(6041),d=i(79317),h=i(47420),p=i(4331),_=i(24878);i(94966),i(95635);const u="M17.63,5.84C17.27,5.33 16.67,5 16,5H5A2,2 0 0,0 3,7V17A2,2 0 0,0 5,19H16C16.67,19 17.27,18.66 17.63,18.15L22,12L17.63,5.84Z",b="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",y="___ADD_NEW___",v="___NO_LABELS___";class m extends((0,p.E)(s.WF)){async open(){await this.updateComplete,await(this._picker?.open())}hassSubscribe(){return[(0,d.o5)(this.hass.connection,(e=>{this._labels=e}))]}render(){const e=this.placeholder??this.hass.localize("ui.components.label-picker.label"),t=this._computeValueRenderer(this._labels);return s.qy`
      <ha-generic-picker
        .hass=${this.hass}
        .autofocus=${this.autofocus}
        .label=${this.label}
        .notFoundLabel=${this.hass.localize("ui.components.label-picker.no_match")}
        .placeholder=${e}
        .value=${this.value}
        .getItems=${this._getItems}
        .getAdditionalItems=${this._getAdditionalItems}
        .valueRenderer=${t}
        @value-changed=${this._valueChanged}
      >
      </ha-generic-picker>
    `}_valueChanged(e){e.stopPropagation();const t=e.detail.value;if(t!==v)if(t)if(t.startsWith(y)){this.hass.loadFragmentTranslation("config");const e=t.substring(13);(0,_.f)(this,{suggestedName:e,createEntry:async e=>{try{const t=await(0,d._9)(this.hass,e);this._setValue(t.label_id)}catch(t){(0,h.K$)(this,{title:this.hass.localize("ui.components.label-picker.failed_create_label"),text:t.message})}}})}else this._setValue(t);else this._setValue(void 0)}_setValue(e){this.value=e,setTimeout((()=>{(0,r.r)(this,"value-changed",{value:e}),(0,r.r)(this,"change")}),0)}constructor(...e){super(...e),this.noAdd=!1,this.disabled=!1,this.required=!1,this._labelMap=(0,l.A)((e=>e?new Map(e.map((e=>[e.label_id,e]))):new Map)),this._computeValueRenderer=(0,l.A)((e=>t=>{const i=this._labelMap(e).get(t);return i?s.qy`
          ${i.icon?s.qy`<ha-icon slot="start" .icon=${i.icon}></ha-icon>`:s.qy`<ha-svg-icon slot="start" .path=${u}></ha-svg-icon>`}
          <span slot="headline">${i.name}</span>
        `:s.qy`
            <ha-svg-icon slot="start" .path=${u}></ha-svg-icon>
            <span slot="headline">${t}</span>
          `})),this._getLabels=(0,l.A)(((e,t,i,a,s,o,l,r,d,h)=>{if(!e||0===e.length)return[{id:v,primary:this.hass.localize("ui.components.label-picker.no_labels"),icon_path:u}];const p=Object.values(i),_=Object.values(a);let b,y,m={};(s||o||l||r||d)&&(m=(0,n.g2)(_),b=p,y=_.filter((e=>e.labels.length>0)),s&&(b=b.filter((e=>{const t=m[e.id];return!(!t||!t.length)&&m[e.id].some((e=>s.includes((0,c.m)(e.entity_id))))})),y=y.filter((e=>s.includes((0,c.m)(e.entity_id))))),o&&(b=b.filter((e=>{const t=m[e.id];return!t||!t.length||_.every((e=>!o.includes((0,c.m)(e.entity_id))))})),y=y.filter((e=>!o.includes((0,c.m)(e.entity_id))))),l&&(b=b.filter((e=>{const t=m[e.id];return!(!t||!t.length)&&m[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&l.includes(t.attributes.device_class))}))})),y=y.filter((e=>{const t=this.hass.states[e.entity_id];return t.attributes.device_class&&l.includes(t.attributes.device_class)}))),r&&(b=b.filter((e=>r(e)))),d&&(b=b.filter((e=>{const t=m[e.id];return!(!t||!t.length)&&m[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&d(t)}))})),y=y.filter((e=>{const t=this.hass.states[e.entity_id];return!!t&&d(t)}))));let g=e;const f=new Set;let M;b&&(M=b.filter((e=>e.area_id)).map((e=>e.area_id)),b.forEach((e=>{e.labels.forEach((e=>f.add(e)))}))),y&&(M=(M??[]).concat(y.filter((e=>e.area_id)).map((e=>e.area_id))),y.forEach((e=>{e.labels.forEach((e=>f.add(e)))}))),M&&M.forEach((e=>{t[e].labels.forEach((e=>f.add(e)))})),h&&(g=g.filter((e=>!h.includes(e.label_id)))),(b||y)&&(g=g.filter((e=>f.has(e.label_id))));return g.map((e=>({id:e.label_id,primary:e.name,icon:e.icon||void 0,icon_path:e.icon?void 0:u,sorting_label:e.name,search_labels:[e.name,e.label_id,e.description].filter((e=>Boolean(e)))})))})),this._getItems=()=>this._getLabels(this._labels,this.hass.areas,this.hass.devices,this.hass.entities,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeLabels),this._allLabelNames=(0,l.A)((e=>e?[...new Set(e.map((e=>e.name.toLowerCase())).filter(Boolean))]:[])),this._getAdditionalItems=e=>{if(this.noAdd)return[];const t=this._allLabelNames(this._labels);return e&&!t.includes(e.toLowerCase())?[{id:y+e,primary:this.hass.localize("ui.components.label-picker.add_new_sugestion",{name:e}),icon_path:b}]:[{id:y,primary:this.hass.localize("ui.components.label-picker.add_new"),icon_path:b}]}}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)()],m.prototype,"label",void 0),(0,a.__decorate)([(0,o.MZ)()],m.prototype,"value",void 0),(0,a.__decorate)([(0,o.MZ)()],m.prototype,"helper",void 0),(0,a.__decorate)([(0,o.MZ)()],m.prototype,"placeholder",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean,attribute:"no-add"})],m.prototype,"noAdd",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-domains"})],m.prototype,"includeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-domains"})],m.prototype,"excludeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-device-classes"})],m.prototype,"includeDeviceClasses",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-label"})],m.prototype,"excludeLabels",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],m.prototype,"deviceFilter",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],m.prototype,"entityFilter",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],m.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],m.prototype,"required",void 0),(0,a.__decorate)([(0,o.wk)()],m.prototype,"_labels",void 0),(0,a.__decorate)([(0,o.P)("ha-generic-picker")],m.prototype,"_picker",void 0),m=(0,a.__decorate)([(0,o.EM)("ha-label-picker")],m)},95403:function(e,t,i){var a=i(69868),s=i(84922),o=i(11991),l=i(33055),r=i(65940),c=i(85759),n=i(73120),d=i(90963),h=i(79317),p=i(4331),_=i(24878);i(54820),i(54538),i(85032);class u extends((0,p.E)(s.WF)){async open(){await this.updateComplete,await(this.labelPicker?.open())}async focus(){await this.updateComplete,await(this.labelPicker?.focus())}hassSubscribe(){return[(0,h.o5)(this.hass.connection,(e=>{const t={};e.forEach((e=>{t[e.label_id]=e})),this._labels=t}))]}render(){const e=this._sortedLabels(this.value,this._labels,this.hass.locale.language);return s.qy`
      ${this.label?s.qy`<label>${this.label}</label>`:s.s6}
      ${e?.length?s.qy`<ha-chip-set>
            ${(0,l.u)(e,(e=>e?.label_id),(e=>{const t=e?.color?(0,c.M)(e.color):void 0;return s.qy`
                  <ha-input-chip
                    .item=${e}
                    @remove=${this._removeItem}
                    @click=${this._openDetail}
                    .label=${e?.name}
                    selected
                    style=${t?`--color: ${t}`:""}
                  >
                    ${e?.icon?s.qy`<ha-icon
                          slot="icon"
                          .icon=${e.icon}
                        ></ha-icon>`:s.s6}
                  </ha-input-chip>
                `}))}
          </ha-chip-set>`:s.s6}
      <ha-label-picker
        .hass=${this.hass}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
        .placeholder=${this.placeholder}
        .excludeLabels=${this.value}
        @value-changed=${this._labelChanged}
      >
      </ha-label-picker>
    `}get _value(){return this.value||[]}_removeItem(e){const t=e.currentTarget.item;this._setValue(this._value.filter((e=>e!==t.label_id)))}_openDetail(e){const t=e.currentTarget.item;(0,_.f)(this,{entry:t,updateEntry:async e=>{await(0,h.Rp)(this.hass,t.label_id,e)}})}_labelChanged(e){e.stopPropagation();const t=e.detail.value;t&&!this._value.includes(t)&&(this._setValue([...this._value,t]),this.labelPicker.value="")}_setValue(e){this.value=e,setTimeout((()=>{(0,n.r)(this,"value-changed",{value:e}),(0,n.r)(this,"change")}),0)}constructor(...e){super(...e),this.noAdd=!1,this.disabled=!1,this.required=!1,this._sortedLabels=(0,r.A)(((e,t,i)=>e?.map((e=>t?.[e])).sort(((e,t)=>(0,d.xL)(e?.name||"",t?.name||"",i)))))}}u.styles=s.AH`
    ha-chip-set {
      margin-bottom: 8px;
    }
    ha-input-chip {
      --md-input-chip-selected-container-color: var(--color, var(--grey-color));
      --ha-input-chip-selected-container-opacity: 0.5;
      --md-input-chip-selected-outline-width: 1px;
    }
    label {
      display: block;
      margin: 0 0 8px;
    }
  `,(0,a.__decorate)([(0,o.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)()],u.prototype,"label",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],u.prototype,"value",void 0),(0,a.__decorate)([(0,o.MZ)()],u.prototype,"helper",void 0),(0,a.__decorate)([(0,o.MZ)()],u.prototype,"placeholder",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean,attribute:"no-add"})],u.prototype,"noAdd",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-domains"})],u.prototype,"includeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-domains"})],u.prototype,"excludeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-device-classes"})],u.prototype,"includeDeviceClasses",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-label"})],u.prototype,"excludeLabels",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],u.prototype,"deviceFilter",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],u.prototype,"entityFilter",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],u.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],u.prototype,"required",void 0),(0,a.__decorate)([(0,o.wk)()],u.prototype,"_labels",void 0),(0,a.__decorate)([(0,o.P)("ha-label-picker",!0)],u.prototype,"labelPicker",void 0),u=(0,a.__decorate)([(0,o.EM)("ha-labels-picker")],u)},79317:function(e,t,i){i.d(t,{Rp:()=>d,_9:()=>n,o5:()=>c});var a=i(47308),s=i(90963),o=i(24802);const l=e=>e.sendMessagePromise({type:"config/label_registry/list"}).then((e=>e.sort(((e,t)=>(0,s.xL)(e.name,t.name))))),r=(e,t)=>e.subscribeEvents((0,o.s)((()=>l(e).then((e=>t.setState(e,!0)))),500,!0),"label_registry_updated"),c=(e,t)=>(0,a.N)("_labelRegistry",l,r,e,t),n=(e,t)=>e.callWS({type:"config/label_registry/create",...t}),d=(e,t,i)=>e.callWS({type:"config/label_registry/update",label_id:t,...i})},4331:function(e,t,i){i.d(t,{E:()=>o});var a=i(69868),s=i(11991);const o=e=>{class t extends e{connectedCallback(){super.connectedCallback(),this._checkSubscribed()}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const e=this.__unsubs.pop();e instanceof Promise?e.then((e=>e())):e()}this.__unsubs=void 0}}updated(e){if(super.updated(e),e.has("hass"))this._checkSubscribed();else if(this.hassSubscribeRequiredHostProps)for(const t of e.keys())if(this.hassSubscribeRequiredHostProps.includes(t))return void this._checkSubscribed()}hassSubscribe(){return[]}_checkSubscribed(){void 0===this.__unsubs&&this.isConnected&&void 0!==this.hass&&!this.hassSubscribeRequiredHostProps?.some((e=>void 0===this[e]))&&(this.__unsubs=this.hassSubscribe())}}return(0,a.__decorate)([(0,s.MZ)({attribute:!1})],t.prototype,"hass",void 0),t}},24878:function(e,t,i){i.d(t,{f:()=>o});var a=i(73120);const s=()=>i.e("3327").then(i.bind(i,76882)),o=(e,t)=>{(0,a.r)(e,"show-dialog",{dialogTag:"dialog-label-detail",dialogImport:s,dialogParams:t})}}};
//# sourceMappingURL=9352.aed9d328d414f0f1.js.map