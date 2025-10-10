"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["8729"],{45025:function(e,t,i){i.a(e,(async function(e,t){try{i(35748),i(95013);var a=i(69868),s=i(84922),o=i(11991),r=i(73120),n=i(39422),l=e([n]);n=(l.then?(await l)():l)[0];let h,c=e=>e;class d extends s.WF{render(){return this.aliases?(0,s.qy)(h||(h=c`
      <ha-multi-textfield
        .hass=${0}
        .value=${0}
        .disabled=${0}
        .label=${0}
        .removeLabel=${0}
        .addLabel=${0}
        item-index
        @value-changed=${0}
      >
      </ha-multi-textfield>
    `),this.hass,this.aliases,this.disabled,this.hass.localize("ui.dialogs.aliases.label"),this.hass.localize("ui.dialogs.aliases.remove"),this.hass.localize("ui.dialogs.aliases.add"),this._aliasesChanged):s.s6}_aliasesChanged(e){(0,r.r)(this,"value-changed",{value:e})}constructor(...e){super(...e),this.disabled=!1}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array})],d.prototype,"aliases",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],d.prototype,"disabled",void 0),d=(0,a.__decorate)([(0,o.EM)("ha-aliases-editor")],d),t()}catch(h){t(h)}}))},36887:function(e,t,i){i.d(t,{Si:function(){return h}});var a=i(69868),s=i(84922),o=i(11991);i(81164),i(95635);let r,n,l=e=>e;const h=e=>{switch(e.level){case 0:return"M11,10H13V16H11V10M22,12H19V20H5V12H2L12,3L22,12M15,10A2,2 0 0,0 13,8H11A2,2 0 0,0 9,10V16A2,2 0 0,0 11,18H13A2,2 0 0,0 15,16V10Z";case 1:return"M12,3L2,12H5V20H19V12H22L12,3M10,8H14V18H12V10H10V8Z";case 2:return"M12,3L2,12H5V20H19V12H22L12,3M9,8H13A2,2 0 0,1 15,10V12A2,2 0 0,1 13,14H11V16H15V18H9V14A2,2 0 0,1 11,12H13V10H9V8Z";case 3:return"M12,3L22,12H19V20H5V12H2L12,3M15,11.5V10C15,8.89 14.1,8 13,8H9V10H13V12H11V14H13V16H9V18H13A2,2 0 0,0 15,16V14.5A1.5,1.5 0 0,0 13.5,13A1.5,1.5 0 0,0 15,11.5Z";case-1:return"M12,3L2,12H5V20H19V12H22L12,3M11,15H7V13H11V15M15,18H13V10H11V8H15V18Z"}return"M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z"};class c extends s.WF{render(){if(this.floor.icon)return(0,s.qy)(r||(r=l`<ha-icon .icon=${0}></ha-icon>`),this.floor.icon);const e=h(this.floor);return(0,s.qy)(n||(n=l`<ha-svg-icon .path=${0}></ha-svg-icon>`),e)}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],c.prototype,"floor",void 0),(0,a.__decorate)([(0,o.MZ)()],c.prototype,"icon",void 0),c=(0,a.__decorate)([(0,o.EM)("ha-floor-icon")],c)},24796:function(e,t,i){i.a(e,(async function(e,t){try{i(79827),i(35748),i(65315),i(12840),i(837),i(22416),i(37089),i(59023),i(5934),i(47849),i(18223),i(56660),i(95013);var a=i(69868),s=i(84922),o=i(11991),r=i(65940),n=i(73120),l=i(92830),h=i(41482),c=i(18944),d=i(56083),u=i(88285),p=i(47420),_=i(87881),y=(i(36137),i(36887),i(58453)),v=(i(93672),i(95635),e([y]));y=(v.then?(await v)():v)[0];let m,g,f,$,b,k,V=e=>e;const H="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",M="M20 2H4C2.9 2 2 2.9 2 4V20C2 21.11 2.9 22 4 22H20C21.11 22 22 21.11 22 20V4C22 2.9 21.11 2 20 2M4 6L6 4H10.9L4 10.9V6M4 13.7L13.7 4H18.6L4 18.6V13.7M20 18L18 20H13.1L20 13.1V18M20 10.3L10.3 20H5.4L20 5.4V10.3Z",w="___ADD_NEW___";class x extends s.WF{async open(){var e;await this.updateComplete,await(null===(e=this._picker)||void 0===e?void 0:e.open())}render(){var e;const t=null!==(e=this.placeholder)&&void 0!==e?e:this.hass.localize("ui.components.floor-picker.floor"),i=this._computeValueRenderer(this.hass.floors);return(0,s.qy)(m||(m=V`
      <ha-generic-picker
        .hass=${0}
        .autofocus=${0}
        .label=${0}
        .notFoundLabel=${0}
        .placeholder=${0}
        .value=${0}
        .getItems=${0}
        .getAdditionalItems=${0}
        .valueRenderer=${0}
        .rowRenderer=${0}
        @value-changed=${0}
      >
      </ha-generic-picker>
    `),this.hass,this.autofocus,this.label,this.hass.localize("ui.components.floor-picker.no_match"),t,this.value,this._getItems,this._getAdditionalItems,i,this._rowRenderer,this._valueChanged)}_valueChanged(e){e.stopPropagation();const t=e.detail.value;if(t)if(t.startsWith(w)){this.hass.loadFragmentTranslation("config");const e=t.substring(w.length);(0,_.k)(this,{suggestedName:e,createEntry:async(e,t)=>{try{const i=await(0,u.KD)(this.hass,e);t.forEach((e=>{(0,c.gs)(this.hass,e,{floor_id:i.floor_id})})),this._setValue(i.floor_id)}catch(i){(0,p.K$)(this,{title:this.hass.localize("ui.components.floor-picker.failed_create_floor"),text:i.message})}}})}else this._setValue(t);else this._setValue(void 0)}_setValue(e){this.value=e,(0,n.r)(this,"value-changed",{value:e}),(0,n.r)(this,"change")}constructor(...e){super(...e),this.noAdd=!1,this.disabled=!1,this.required=!1,this._computeValueRenderer=(0,r.A)((e=>e=>{const t=this.hass.floors[e];if(!t)return(0,s.qy)(g||(g=V`
            <ha-svg-icon slot="start" .path=${0}></ha-svg-icon>
            <span slot="headline">${0}</span>
          `),M,t);const i=t?(0,h.X)(t):void 0;return(0,s.qy)(f||(f=V`
          <ha-floor-icon slot="start" .floor=${0}></ha-floor-icon>
          <span slot="headline">${0}</span>
        `),t,i)})),this._getFloors=(0,r.A)(((e,t,i,a,s,o,r,n,c,p)=>{const _=Object.values(e),y=Object.values(t),v=Object.values(i),m=Object.values(a);let g,f,$={};(s||o||r||n||c)&&($=(0,d.g2)(m),g=v,f=m.filter((e=>e.area_id)),s&&(g=g.filter((e=>{const t=$[e.id];return!(!t||!t.length)&&$[e.id].some((e=>s.includes((0,l.m)(e.entity_id))))})),f=f.filter((e=>s.includes((0,l.m)(e.entity_id))))),o&&(g=g.filter((e=>{const t=$[e.id];return!t||!t.length||m.every((e=>!o.includes((0,l.m)(e.entity_id))))})),f=f.filter((e=>!o.includes((0,l.m)(e.entity_id))))),r&&(g=g.filter((e=>{const t=$[e.id];return!(!t||!t.length)&&$[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&r.includes(t.attributes.device_class))}))})),f=f.filter((e=>{const t=this.hass.states[e.entity_id];return t.attributes.device_class&&r.includes(t.attributes.device_class)}))),n&&(g=g.filter((e=>n(e)))),c&&(g=g.filter((e=>{const t=$[e.id];return!(!t||!t.length)&&$[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&c(t)}))})),f=f.filter((e=>{const t=this.hass.states[e.entity_id];return!!t&&c(t)}))));let b,k=_;if(g&&(b=g.filter((e=>e.area_id)).map((e=>e.area_id))),f&&(b=(null!=b?b:[]).concat(f.filter((e=>e.area_id)).map((e=>e.area_id)))),b){const e=(0,u._o)(y);k=k.filter((t=>{var i;return null===(i=e[t.floor_id])||void 0===i?void 0:i.some((e=>b.includes(e.area_id)))}))}p&&(k=k.filter((e=>!p.includes(e.floor_id))));return k.map((e=>{var t;const i=(0,h.X)(e);return{id:e.floor_id,primary:i,floor:e,sorting_label:(null===(t=e.level)||void 0===t?void 0:t.toString())||"zzzzz",search_labels:[i,e.floor_id,...e.aliases].filter((e=>Boolean(e)))}}))})),this._rowRenderer=e=>(0,s.qy)($||($=V`
    <ha-combo-box-item type="button" compact>
      ${0}
      <span slot="headline">${0}</span>
    </ha-combo-box-item>
  `),e.icon_path?(0,s.qy)(b||(b=V`
            <ha-svg-icon
              slot="start"
              style="margin: 0 4px"
              .path=${0}
            ></ha-svg-icon>
          `),e.icon_path):(0,s.qy)(k||(k=V`
            <ha-floor-icon
              slot="start"
              .floor=${0}
              style="margin: 0 4px"
            ></ha-floor-icon>
          `),e.floor),e.primary),this._getItems=()=>this._getFloors(this.hass.floors,this.hass.areas,this.hass.devices,this.hass.entities,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeFloors),this._allFloorNames=(0,r.A)((e=>Object.values(e).map((e=>{var t;return null===(t=(0,h.X)(e))||void 0===t?void 0:t.toLowerCase()})).filter(Boolean))),this._getAdditionalItems=e=>{if(this.noAdd)return[];const t=this._allFloorNames(this.hass.floors);return e&&!t.includes(e.toLowerCase())?[{id:w+e,primary:this.hass.localize("ui.components.floor-picker.add_new_sugestion",{name:e}),icon_path:H}]:[{id:w,primary:this.hass.localize("ui.components.floor-picker.add_new"),icon_path:H}]}}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)()],x.prototype,"label",void 0),(0,a.__decorate)([(0,o.MZ)()],x.prototype,"value",void 0),(0,a.__decorate)([(0,o.MZ)()],x.prototype,"helper",void 0),(0,a.__decorate)([(0,o.MZ)()],x.prototype,"placeholder",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean,attribute:"no-add"})],x.prototype,"noAdd",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-domains"})],x.prototype,"includeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-domains"})],x.prototype,"excludeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-device-classes"})],x.prototype,"includeDeviceClasses",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-floors"})],x.prototype,"excludeFloors",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],x.prototype,"deviceFilter",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],x.prototype,"entityFilter",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],x.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],x.prototype,"required",void 0),(0,a.__decorate)([(0,o.P)("ha-generic-picker")],x.prototype,"_picker",void 0),x=(0,a.__decorate)([(0,o.EM)("ha-floor-picker")],x),t()}catch(m){t(m)}}))},15785:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t),i.d(t,{HaIconPicker:function(){return V}});i(79827),i(35748),i(99342),i(35058),i(65315),i(837),i(22416),i(37089),i(59023),i(5934),i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030),i(18223),i(95013);var s=i(69868),o=i(84922),r=i(11991),n=i(65940),l=i(73120),h=i(73314),c=i(5177),d=(i(81164),i(36137),e([c]));c=(d.then?(await d)():d)[0];let u,p,_,y,v,m=e=>e,g=[],f=!1;const $=async()=>{f=!0;const e=await i.e("4765").then(i.t.bind(i,43692,19));g=e.default.map((e=>({icon:`mdi:${e.name}`,parts:new Set(e.name.split("-")),keywords:e.keywords})));const t=[];Object.keys(h.y).forEach((e=>{t.push(b(e))})),(await Promise.all(t)).forEach((e=>{g.push(...e)}))},b=async e=>{try{const t=h.y[e].getIconList;if("function"!=typeof t)return[];const i=await t();return i.map((t=>{var i;return{icon:`${e}:${t.name}`,parts:new Set(t.name.split("-")),keywords:null!==(i=t.keywords)&&void 0!==i?i:[]}}))}catch(t){return console.warn(`Unable to load icon list for ${e} iconset`),[]}},k=e=>(0,o.qy)(u||(u=m`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${0} slot="start"></ha-icon>
    ${0}
  </ha-combo-box-item>
`),e.icon,e.icon);class V extends o.WF{render(){return(0,o.qy)(p||(p=m`
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
    `),this.hass,this._value,f?this._iconProvider:void 0,this.label,this.helper,this.disabled,this.required,this.placeholder,this.errorMessage,this.invalid,k,this._openedChanged,this._valueChanged,this._value||this.placeholder?(0,o.qy)(_||(_=m`
              <ha-icon .icon=${0} slot="icon">
              </ha-icon>
            `),this._value||this.placeholder):(0,o.qy)(y||(y=m`<slot slot="icon" name="fallback"></slot>`)))}async _openedChanged(e){e.detail.value&&!f&&(await $(),this.requestUpdate())}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,l.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.invalid=!1,this._filterIcons=(0,n.A)(((e,t=g)=>{if(!e)return t;const i=[],a=(e,t)=>i.push({icon:e,rank:t});for(const s of t)s.parts.has(e)?a(s.icon,1):s.keywords.includes(e)?a(s.icon,2):s.icon.includes(e)?a(s.icon,3):s.keywords.some((t=>t.includes(e)))&&a(s.icon,4);return 0===i.length&&a(e,0),i.sort(((e,t)=>e.rank-t.rank))})),this._iconProvider=(e,t)=>{const i=this._filterIcons(e.filter.toLowerCase(),g),a=e.page*e.pageSize,s=a+e.pageSize;t(i.slice(a,s),i.length)}}}V.styles=(0,o.AH)(v||(v=m`
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
  `)),(0,s.__decorate)([(0,r.MZ)({attribute:!1})],V.prototype,"hass",void 0),(0,s.__decorate)([(0,r.MZ)()],V.prototype,"value",void 0),(0,s.__decorate)([(0,r.MZ)()],V.prototype,"label",void 0),(0,s.__decorate)([(0,r.MZ)()],V.prototype,"helper",void 0),(0,s.__decorate)([(0,r.MZ)()],V.prototype,"placeholder",void 0),(0,s.__decorate)([(0,r.MZ)({attribute:"error-message"})],V.prototype,"errorMessage",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],V.prototype,"disabled",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],V.prototype,"required",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],V.prototype,"invalid",void 0),V=(0,s.__decorate)([(0,r.EM)("ha-icon-picker")],V),a()}catch(u){a(u)}}))},88285:function(e,t,i){i.d(t,{KD:function(){return a},_o:function(){return s}});i(35748),i(99342),i(12977),i(95013),i(90963),i(52435);const a=(e,t)=>e.callWS(Object.assign({type:"config/floor_registry/create"},t)),s=e=>{const t={};for(const i of e)i.floor_id&&(i.floor_id in t||(t[i.floor_id]=[]),t[i.floor_id].push(i));return t}},3319:function(e,t,i){i.d(t,{Sn:function(){return a},q2:function(){return s},tb:function(){return o}});i(5934);const a="timestamp",s="temperature",o="humidity"},384:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t);i(35748),i(5934),i(39118),i(95013);var s=i(69868),o=i(84922),r=i(11991),n=i(73120),l=(i(23749),i(45025)),h=i(7119),c=(i(62351),i(15785)),d=i(24796),u=i(57447),p=(i(11934),i(95403)),_=i(18944),y=i(83566),v=i(3319),m=i(47420),g=i(72847),f=e([l,h,c,d,u,p]);[l,h,c,d,u,p]=f.then?(await f)():f;let $,b,k,V,H,M,w,x,C=e=>e;const z={round:!1,type:"image/jpeg",quality:.75,aspectRatio:1.78},Z=["sensor"],A=[v.q2],E=[v.tb];class q extends o.WF{async showDialog(e){this._params=e,this._error=void 0,this._params.entry?(this._name=this._params.entry.name,this._aliases=this._params.entry.aliases,this._labels=this._params.entry.labels,this._picture=this._params.entry.picture,this._icon=this._params.entry.icon,this._floor=this._params.entry.floor_id,this._temperatureEntity=this._params.entry.temperature_entity_id,this._humidityEntity=this._params.entry.humidity_entity_id):(this._name=this._params.suggestedName||"",this._aliases=[],this._labels=[],this._picture=null,this._icon=null,this._floor=null,this._temperatureEntity=null,this._humidityEntity=null),await this.updateComplete}closeDialog(){this._error="",this._params=void 0,(0,n.r)(this,"dialog-closed",{dialog:this.localName})}_renderSettings(e){return(0,o.qy)($||($=C`
      ${0}

      <ha-textfield
        .value=${0}
        @input=${0}
        .label=${0}
        .validationMessage=${0}
        required
        dialogInitialFocus
      ></ha-textfield>

      <ha-icon-picker
        .hass=${0}
        .value=${0}
        @value-changed=${0}
        .label=${0}
      ></ha-icon-picker>

      <ha-floor-picker
        .hass=${0}
        .value=${0}
        @value-changed=${0}
        .label=${0}
      ></ha-floor-picker>

      <ha-labels-picker
        .hass=${0}
        .value=${0}
        @value-changed=${0}
        .placeholder=${0}
      ></ha-labels-picker>

      <ha-picture-upload
        .hass=${0}
        .value=${0}
        crop
        select-media
        .cropOptions=${0}
        @change=${0}
      ></ha-picture-upload>
    `),e?(0,o.qy)(b||(b=C`
            <ha-settings-row>
              <span slot="heading">
                ${0}
              </span>
              <span slot="description"> ${0} </span>
            </ha-settings-row>
          `),this.hass.localize("ui.panel.config.areas.editor.area_id"),e.area_id):o.s6,this._name,this._nameChanged,this.hass.localize("ui.panel.config.areas.editor.name"),this.hass.localize("ui.panel.config.areas.editor.name_required"),this.hass,this._icon,this._iconChanged,this.hass.localize("ui.panel.config.areas.editor.icon"),this.hass,this._floor,this._floorChanged,this.hass.localize("ui.panel.config.areas.editor.floor"),this.hass,this._labels,this._labelsChanged,this.hass.localize("ui.panel.config.areas.editor.add_labels"),this.hass,this._picture,z,this._pictureChanged)}_renderAliasExpansion(){return(0,o.qy)(k||(k=C`
      <ha-expansion-panel
        outlined
        .header=${0}
        expanded
      >
        <div class="content">
          <p class="description">
            ${0}
          </p>
          <ha-aliases-editor
            .hass=${0}
            .aliases=${0}
            @value-changed=${0}
          ></ha-aliases-editor>
        </div>
      </ha-expansion-panel>
    `),this.hass.localize("ui.panel.config.areas.editor.aliases_section"),this.hass.localize("ui.panel.config.areas.editor.aliases_description"),this.hass,this._aliases,this._aliasesChanged)}_renderRelatedEntitiesExpansion(){return(0,o.qy)(V||(V=C`
      <ha-expansion-panel
        outlined
        .header=${0}
        expanded
      >
        <div class="content">
          <ha-entity-picker
            .hass=${0}
            .label=${0}
            .helper=${0}
            .value=${0}
            .includeDomains=${0}
            .includeDeviceClasses=${0}
            .entityFilter=${0}
            @value-changed=${0}
          ></ha-entity-picker>

          <ha-entity-picker
            .hass=${0}
            .label=${0}
            .helper=${0}
            .value=${0}
            .includeDomains=${0}
            .includeDeviceClasses=${0}
            .entityFilter=${0}
            @value-changed=${0}
          ></ha-entity-picker>
        </div>
      </ha-expansion-panel>
    `),this.hass.localize("ui.panel.config.areas.editor.related_entities_section"),this.hass,this.hass.localize("ui.panel.config.areas.editor.temperature_entity"),this.hass.localize("ui.panel.config.areas.editor.temperature_entity_description"),this._temperatureEntity,Z,A,this._areaEntityFilter,this._sensorChanged,this.hass,this.hass.localize("ui.panel.config.areas.editor.humidity_entity"),this.hass.localize("ui.panel.config.areas.editor.humidity_entity_description"),this._humidityEntity,Z,E,this._areaEntityFilter,this._sensorChanged)}render(){if(!this._params)return o.s6;const e=this._params.entry,t=!this._isNameValid(),i=!e;return(0,o.qy)(H||(H=C`
      <ha-dialog
        open
        @closed=${0}
        .heading=${0}
      >
        <div>
          ${0}
          <div class="form">
            ${0} ${0}
            ${0}
          </div>
        </div>
        ${0}
        <div slot="primaryAction">
          <ha-button appearance="plain" @click=${0}>
            ${0}
          </ha-button>
          <ha-button
            @click=${0}
            .disabled=${0}
          >
            ${0}
          </ha-button>
        </div>
      </ha-dialog>
    `),this.closeDialog,(0,g.l)(this.hass,e?this.hass.localize("ui.panel.config.areas.editor.update_area"):this.hass.localize("ui.panel.config.areas.editor.create_area")),this._error?(0,o.qy)(M||(M=C`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):"",this._renderSettings(e),this._renderAliasExpansion(),i?o.s6:this._renderRelatedEntitiesExpansion(),i?o.s6:(0,o.qy)(w||(w=C`<ha-button
              slot="secondaryAction"
              variant="danger"
              appearance="plain"
              @click=${0}
            >
              ${0}
            </ha-button>`),this._deleteArea,this.hass.localize("ui.common.delete")),this.closeDialog,this.hass.localize("ui.common.cancel"),this._updateEntry,t||!!this._submitting,e?this.hass.localize("ui.common.save"):this.hass.localize("ui.common.create"))}_isNameValid(){return""!==this._name.trim()}_nameChanged(e){this._error=void 0,this._name=e.target.value}_floorChanged(e){this._error=void 0,this._floor=e.detail.value}_iconChanged(e){this._error=void 0,this._icon=e.detail.value}_labelsChanged(e){this._error=void 0,this._labels=e.detail.value}_pictureChanged(e){this._error=void 0,this._picture=e.target.value}_aliasesChanged(e){this._aliases=e.detail.value}_sensorChanged(e){this[`_${e.target.includeDeviceClasses[0]}Entity`]=e.detail.value||null}async _updateEntry(){const e=!this._params.entry;this._submitting=!0;try{const t={name:this._name.trim(),picture:this._picture||(e?void 0:null),icon:this._icon||(e?void 0:null),floor_id:this._floor||(e?void 0:null),labels:this._labels||null,aliases:this._aliases,temperature_entity_id:this._temperatureEntity,humidity_entity_id:this._humidityEntity};e?await this._params.createEntry(t):await this._params.updateEntry(t),this.closeDialog()}catch(t){this._error=t.message||this.hass.localize("ui.panel.config.areas.editor.unknown_error")}finally{this._submitting=!1}}async _deleteArea(){var e;if(null===(e=this._params)||void 0===e||!e.entry)return;await(0,m.dk)(this,{title:this.hass.localize("ui.panel.config.areas.delete.confirmation_title",{name:this._params.entry.name}),text:this.hass.localize("ui.panel.config.areas.delete.confirmation_text"),dismissText:this.hass.localize("ui.common.cancel"),confirmText:this.hass.localize("ui.common.delete"),destructive:!0})&&(await(0,_.uG)(this.hass,this._params.entry.area_id),this.closeDialog())}static get styles(){return[y.nA,(0,o.AH)(x||(x=C`
        ha-textfield {
          display: block;
        }
        ha-expansion-panel {
          --expansion-panel-content-padding: 0;
        }
        ha-aliases-editor,
        ha-entity-picker,
        ha-floor-picker,
        ha-icon-picker,
        ha-labels-picker,
        ha-picture-upload,
        ha-expansion-panel {
          display: block;
          margin-bottom: 16px;
        }
        ha-dialog {
          --mdc-dialog-min-width: min(600px, 100vw);
        }
        .content {
          padding: 12px;
        }
        .description {
          margin: 0 0 16px 0;
        }
      `))]}constructor(...e){super(...e),this._areaEntityFilter=e=>{const t=this.hass.entities[e.entity_id];if(!t)return!1;const i=this._params.entry.area_id;if(t.area_id===i)return!0;if(!t.device_id)return!1;const a=this.hass.devices[t.device_id];return a&&a.area_id===i}}}(0,s.__decorate)([(0,r.MZ)({attribute:!1})],q.prototype,"hass",void 0),(0,s.__decorate)([(0,r.wk)()],q.prototype,"_name",void 0),(0,s.__decorate)([(0,r.wk)()],q.prototype,"_aliases",void 0),(0,s.__decorate)([(0,r.wk)()],q.prototype,"_labels",void 0),(0,s.__decorate)([(0,r.wk)()],q.prototype,"_picture",void 0),(0,s.__decorate)([(0,r.wk)()],q.prototype,"_icon",void 0),(0,s.__decorate)([(0,r.wk)()],q.prototype,"_floor",void 0),(0,s.__decorate)([(0,r.wk)()],q.prototype,"_temperatureEntity",void 0),(0,s.__decorate)([(0,r.wk)()],q.prototype,"_humidityEntity",void 0),(0,s.__decorate)([(0,r.wk)()],q.prototype,"_error",void 0),(0,s.__decorate)([(0,r.wk)()],q.prototype,"_params",void 0),(0,s.__decorate)([(0,r.wk)()],q.prototype,"_submitting",void 0),customElements.define("dialog-area-registry-detail",q),a()}catch($){a($)}}))},87881:function(e,t,i){i.d(t,{k:function(){return o}});i(35748),i(5934),i(95013);var a=i(73120);const s=()=>Promise.all([i.e("1092"),i.e("7035")]).then(i.bind(i,64587)),o=(e,t)=>{(0,a.r)(e,"show-dialog",{dialogTag:"dialog-floor-registry-detail",dialogImport:s,dialogParams:t})}}}]);
//# sourceMappingURL=8729.408aa8d5e455d292.js.map