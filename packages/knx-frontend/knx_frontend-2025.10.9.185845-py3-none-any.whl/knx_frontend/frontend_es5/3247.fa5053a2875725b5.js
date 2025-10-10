"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["3247"],{85759:function(e,t,i){i.d(t,{M:function(){return s},l:function(){return a}});i(35748),i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030),i(95013);const a=new Set(["primary","accent","disabled","red","pink","purple","deep-purple","indigo","blue","light-blue","cyan","teal","green","light-green","lime","yellow","amber","orange","deep-orange","brown","light-grey","grey","dark-grey","blue-grey","black","white"]);function s(e){return a.has(e)?`var(--${e}-color)`:e}},44537:function(e,t,i){i.d(t,{xn:function(){return o},T:function(){return r}});i(35748),i(65315),i(837),i(37089),i(39118),i(95013);var a=i(65940),s=i(47379);i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030);const o=e=>{var t;return null===(t=e.name_by_user||e.name)||void 0===t?void 0:t.trim()},r=(e,t,i)=>o(e)||i&&n(t,i)||t.localize("ui.panel.config.devices.unnamed_device",{type:t.localize(`ui.panel.config.devices.type.${e.entry_type||"device"}`)}),n=(e,t)=>{for(const i of t||[]){const t="string"==typeof i?i:i.entity_id,a=e.states[t];if(a)return(0,s.u)(a)}};(0,a.A)((e=>function(e){const t=new Set,i=new Set;for(const a of e)i.has(a)?t.add(a):i.add(a);return t}(Object.values(e).map((e=>o(e))).filter((e=>void 0!==e)))))},24383:function(e,t,i){i.d(t,{w:function(){return a}});const a=(e,t)=>{const i=e.area_id,a=i?t.areas[i]:void 0,s=null==a?void 0:a.floor_id;return{device:e,area:a||null,floor:(s?t.floors[s]:void 0)||null}}},71755:function(e,t,i){i.a(e,(async function(e,t){try{i(79827),i(35748),i(65315),i(12840),i(837),i(37089),i(59023),i(52885),i(5934),i(18223),i(95013);var a=i(69868),s=i(84922),o=i(11991),r=i(65940),n=i(73120),d=i(22441),c=i(44537),l=i(92830),h=i(24383),p=i(88120),u=i(56083),_=i(28027),v=i(45363),y=i(58453),m=e([y]);y=(m.then?(await m)():m)[0];let b,g,f,$,k,M,x,V,H=e=>e;class L extends s.WF{firstUpdated(e){super.firstUpdated(e),this._loadConfigEntries()}async _loadConfigEntries(){const e=await(0,p.VN)(this.hass);this._configEntryLookup=Object.fromEntries(e.map((e=>[e.entry_id,e])))}render(){var e;const t=null!==(e=this.placeholder)&&void 0!==e?e:this.hass.localize("ui.components.device-picker.placeholder"),i=this.hass.localize("ui.components.device-picker.no_match"),a=this._valueRenderer(this._configEntryLookup);return(0,s.qy)(b||(b=H`
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
    `),this.hass,this.autofocus,this.label,this.searchLabel,i,t,this.value,this._rowRenderer,this._getItems,this.hideClearIcon,a,this._valueChanged)}async open(){var e;await this.updateComplete,await(null===(e=this._picker)||void 0===e?void 0:e.open())}_valueChanged(e){e.stopPropagation();const t=e.detail.value;this.value=t,(0,n.r)(this,"value-changed",{value:t})}constructor(...e){super(...e),this.autofocus=!1,this.disabled=!1,this.required=!1,this.hideClearIcon=!1,this._configEntryLookup={},this._getItems=()=>this._getDevices(this.hass.devices,this.hass.entities,this._configEntryLookup,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeDevices),this._getDevices=(0,r.A)(((e,t,i,a,s,o,r,n,p)=>{const v=Object.values(e),y=Object.values(t);let m={};(a||s||o||n)&&(m=(0,u.g2)(y));let b=v.filter((e=>e.id===this.value||!e.disabled_by));a&&(b=b.filter((e=>{const t=m[e.id];return!(!t||!t.length)&&m[e.id].some((e=>a.includes((0,l.m)(e.entity_id))))}))),s&&(b=b.filter((e=>{const t=m[e.id];return!t||!t.length||y.every((e=>!s.includes((0,l.m)(e.entity_id))))}))),p&&(b=b.filter((e=>!p.includes(e.id)))),o&&(b=b.filter((e=>{const t=m[e.id];return!(!t||!t.length)&&m[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&o.includes(t.attributes.device_class))}))}))),n&&(b=b.filter((e=>{const t=m[e.id];return!(!t||!t.length)&&t.some((e=>{const t=this.hass.states[e.entity_id];return!!t&&n(t)}))}))),r&&(b=b.filter((e=>e.id===this.value||r(e))));return b.map((e=>{const t=(0,c.T)(e,this.hass,m[e.id]),{area:a}=(0,h.w)(e,this.hass),s=a?(0,d.A)(a):void 0,o=e.primary_config_entry?null==i?void 0:i[e.primary_config_entry]:void 0,r=null==o?void 0:o.domain,n=r?(0,_.p$)(this.hass.localize,r):void 0;return{id:e.id,label:"",primary:t||this.hass.localize("ui.components.device-picker.unnamed_device"),secondary:s,domain:null==o?void 0:o.domain,domain_name:n,search_labels:[t,s,r,n].filter(Boolean),sorting_label:t||"zzz"}}))})),this._valueRenderer=(0,r.A)((e=>t=>{var i;const a=t,o=this.hass.devices[a];if(!o)return(0,s.qy)(g||(g=H`<span slot="headline">${0}</span>`),a);const{area:r}=(0,h.w)(o,this.hass),n=o?(0,c.xn)(o):void 0,l=r?(0,d.A)(r):void 0,p=o.primary_config_entry?e[o.primary_config_entry]:void 0;return(0,s.qy)(f||(f=H`
        ${0}
        <span slot="headline">${0}</span>
        <span slot="supporting-text">${0}</span>
      `),p?(0,s.qy)($||($=H`<img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${0}
            />`),(0,v.MR)({domain:p.domain,type:"icon",darkOptimized:null===(i=this.hass.themes)||void 0===i?void 0:i.darkMode})):s.s6,n,l)})),this._rowRenderer=e=>(0,s.qy)(k||(k=H`
    <ha-combo-box-item type="button">
      ${0}

      <span slot="headline">${0}</span>
      ${0}
      ${0}
    </ha-combo-box-item>
  `),e.domain?(0,s.qy)(M||(M=H`
            <img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${0}
            />
          `),(0,v.MR)({domain:e.domain,type:"icon",darkOptimized:this.hass.themes.darkMode})):s.s6,e.primary,e.secondary?(0,s.qy)(x||(x=H`<span slot="supporting-text">${0}</span>`),e.secondary):s.s6,e.domain_name?(0,s.qy)(V||(V=H`
            <div slot="trailing-supporting-text" class="domain">
              ${0}
            </div>
          `),e.domain_name):s.s6)}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],L.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],L.prototype,"autofocus",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],L.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],L.prototype,"required",void 0),(0,a.__decorate)([(0,o.MZ)()],L.prototype,"label",void 0),(0,a.__decorate)([(0,o.MZ)()],L.prototype,"value",void 0),(0,a.__decorate)([(0,o.MZ)()],L.prototype,"helper",void 0),(0,a.__decorate)([(0,o.MZ)()],L.prototype,"placeholder",void 0),(0,a.__decorate)([(0,o.MZ)({type:String,attribute:"search-label"})],L.prototype,"searchLabel",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1,type:Array})],L.prototype,"createDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-domains"})],L.prototype,"includeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-domains"})],L.prototype,"excludeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-device-classes"})],L.prototype,"includeDeviceClasses",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-devices"})],L.prototype,"excludeDevices",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],L.prototype,"deviceFilter",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],L.prototype,"entityFilter",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"hide-clear-icon",type:Boolean})],L.prototype,"hideClearIcon",void 0),(0,a.__decorate)([(0,o.P)("ha-generic-picker")],L.prototype,"_picker",void 0),(0,a.__decorate)([(0,o.wk)()],L.prototype,"_configEntryLookup",void 0),L=(0,a.__decorate)([(0,o.EM)("ha-device-picker")],L),t()}catch(b){t(b)}}))},83264:function(e,t,i){i.a(e,(async function(e,t){try{i(91949),i(79827),i(35748),i(99342),i(35058),i(41846),i(65315),i(12840),i(837),i(84136),i(22416),i(37089),i(59023),i(5934),i(67579),i(18223),i(91844),i(95013);var a=i(69868),s=i(84922),o=i(11991),r=i(7577),n=i(65940),d=i(73120),c=i(22441),l=i(92830),h=i(41482),p=i(90963),u=i(98137),_=i(56083),v=i(88285),y=(i(36137),i(36887),i(58453)),m=(i(93672),i(95635),i(74455),e([y]));y=(m.then?(await m)():m)[0];let b,g,f,$,k,M,x,V,H,L,w,Z=e=>e;const C="M20 2H4C2.9 2 2 2.9 2 4V20C2 21.11 2.9 22 4 22H20C21.11 22 22 21.11 22 20V4C22 2.9 21.11 2 20 2M4 6L6 4H10.9L4 10.9V6M4 13.7L13.7 4H18.6L4 18.6V13.7M20 18L18 20H13.1L20 13.1V18M20 10.3L10.3 20H5.4L20 5.4V10.3Z",A="________";class D extends s.WF{async open(){var e;await this.updateComplete,await(null===(e=this._picker)||void 0===e?void 0:e.open())}render(){var e;const t=null!==(e=this.placeholder)&&void 0!==e?e:this.hass.localize("ui.components.area-picker.area"),i=this.value?this._formatValue(this.value):void 0;return(0,s.qy)(b||(b=Z`
      <ha-generic-picker
        .hass=${0}
        .autofocus=${0}
        .label=${0}
        .searchLabel=${0}
        .notFoundLabel=${0}
        .placeholder=${0}
        .value=${0}
        .getItems=${0}
        .valueRenderer=${0}
        .rowRenderer=${0}
        @value-changed=${0}
      >
      </ha-generic-picker>
    `),this.hass,this.autofocus,this.label,this.searchLabel,this.hass.localize("ui.components.area-picker.no_match"),t,i,this._getItems,this._valueRenderer,this._rowRenderer,this._valueChanged)}_valueChanged(e){e.stopPropagation();const t=e.detail.value;if(!t)return void this._setValue(void 0);const i=this._parseValue(t);this._setValue(i)}_setValue(e){this.value=e,(0,d.r)(this,"value-changed",{value:e}),(0,d.r)(this,"change")}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._valueRenderer=e=>{const t=this._parseValue(e),i="area"===t.type&&this.hass.areas[e];if(i){const e=(0,c.A)(i);return(0,s.qy)(g||(g=Z`
        ${0}
        <slot name="headline">${0}</slot>
      `),i.icon?(0,s.qy)(f||(f=Z`<ha-icon slot="start" .icon=${0}></ha-icon>`),i.icon):(0,s.qy)($||($=Z`<ha-svg-icon
              slot="start"
              .path=${0}
            ></ha-svg-icon>`),C),e)}const a="floor"===t.type&&this.hass.floors[e];if(a){const e=(0,h.X)(a);return(0,s.qy)(k||(k=Z`
        <ha-floor-icon slot="start" .floor=${0}></ha-floor-icon>
        <span slot="headline">${0}</span>
      `),a,e)}return(0,s.qy)(M||(M=Z`
      <ha-svg-icon slot="start" .path=${0}></ha-svg-icon>
      <span slot="headline">${0}</span>
    `),C,e)},this._getAreasAndFloors=(0,n.A)(((e,t,i,a,s,o,r,n,d,u,y)=>{const m=Object.values(e),b=Object.values(t),g=Object.values(i),f=Object.values(a);let $,k,M={};(s||o||r||n||d)&&(M=(0,_.g2)(f),$=g,k=f.filter((e=>e.area_id)),s&&($=$.filter((e=>{const t=M[e.id];return!(!t||!t.length)&&M[e.id].some((e=>s.includes((0,l.m)(e.entity_id))))})),k=k.filter((e=>s.includes((0,l.m)(e.entity_id))))),o&&($=$.filter((e=>{const t=M[e.id];return!t||!t.length||f.every((e=>!o.includes((0,l.m)(e.entity_id))))})),k=k.filter((e=>!o.includes((0,l.m)(e.entity_id))))),r&&($=$.filter((e=>{const t=M[e.id];return!(!t||!t.length)&&M[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&r.includes(t.attributes.device_class))}))})),k=k.filter((e=>{const t=this.hass.states[e.entity_id];return t.attributes.device_class&&r.includes(t.attributes.device_class)}))),n&&($=$.filter((e=>n(e)))),d&&($=$.filter((e=>{const t=M[e.id];return!(!t||!t.length)&&M[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&d(t)}))})),k=k.filter((e=>{const t=this.hass.states[e.entity_id];return!!t&&d(t)}))));let x,V=b;$&&(x=$.filter((e=>e.area_id)).map((e=>e.area_id))),k&&(x=(null!=x?x:[]).concat(k.filter((e=>e.area_id)).map((e=>e.area_id)))),x&&(V=V.filter((e=>x.includes(e.area_id)))),u&&(V=V.filter((e=>!u.includes(e.area_id)))),y&&(V=V.filter((e=>!e.floor_id||!y.includes(e.floor_id))));const H=(0,v._o)(V),L=Object.values(V).filter((e=>!e.floor_id||!H[e.floor_id])),w=Object.entries(H).map((([e,t])=>[m.find((t=>t.floor_id===e)),t])).sort((([e],[t])=>{var i,a;return e.level!==t.level?(null!==(i=e.level)&&void 0!==i?i:0)-(null!==(a=t.level)&&void 0!==a?a:0):(0,p.xL)(e.name,t.name)})),Z=[];return w.forEach((([e,t])=>{if(e){const i=(0,h.X)(e),a=t.map((e=>{const t=(0,c.A)(e)||e.area_id;return[e.area_id,t,...e.aliases]})).flat();Z.push({id:this._formatValue({id:e.floor_id,type:"floor"}),type:"floor",primary:i,floor:e,search_labels:[e.floor_id,i,...e.aliases,...a]})}Z.push(...t.map((e=>{const t=(0,c.A)(e)||e.area_id;return{id:this._formatValue({id:e.area_id,type:"area"}),type:"area",primary:t,area:e,icon:e.icon||void 0,search_labels:[e.area_id,t,...e.aliases]}})))})),Z.push(...L.map((e=>{const t=(0,c.A)(e)||e.area_id;return{id:this._formatValue({id:e.area_id,type:"area"}),type:"area",primary:t,icon:e.icon||void 0,search_labels:[e.area_id,t,...e.aliases]}}))),Z})),this._rowRenderer=(e,{index:t},i)=>{var a,o,n;const d=null===(a=i.filteredItems)||void 0===a?void 0:a[t+1],c=!d||"floor"===d.type||"area"===d.type&&!(null!==(o=d.area)&&void 0!==o&&o.floor_id),l=(0,u.qC)(this.hass),h="area"===e.type&&(null===(n=e.area)||void 0===n?void 0:n.floor_id);return(0,s.qy)(x||(x=Z`
      <ha-combo-box-item
        type="button"
        style=${0}
      >
        ${0}
        ${0}
        ${0}
      </ha-combo-box-item>
    `),"area"===e.type&&h?"--md-list-item-leading-space: 48px;":"","area"===e.type&&h?(0,s.qy)(V||(V=Z`
              <ha-tree-indicator
                style=${0}
                .end=${0}
                slot="start"
              ></ha-tree-indicator>
            `),(0,r.W)({width:"48px",position:"absolute",top:"0px",left:l?void 0:"4px",right:l?"4px":void 0,transform:l?"scaleX(-1)":""}),c):s.s6,"floor"===e.type&&e.floor?(0,s.qy)(H||(H=Z`<ha-floor-icon
              slot="start"
              .floor=${0}
            ></ha-floor-icon>`),e.floor):e.icon?(0,s.qy)(L||(L=Z`<ha-icon slot="start" .icon=${0}></ha-icon>`),e.icon):(0,s.qy)(w||(w=Z`<ha-svg-icon
                slot="start"
                .path=${0}
              ></ha-svg-icon>`),e.icon_path||C),e.primary)},this._getItems=()=>this._getAreasAndFloors(this.hass.floors,this.hass.areas,this.hass.devices,this.hass.entities,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeAreas,this.excludeFloors),this._formatValue=(0,n.A)((e=>[e.type,e.id].join(A))),this._parseValue=(0,n.A)((e=>{const[t,i]=e.split(A);return{id:i,type:t}}))}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],D.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)()],D.prototype,"label",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],D.prototype,"value",void 0),(0,a.__decorate)([(0,o.MZ)()],D.prototype,"helper",void 0),(0,a.__decorate)([(0,o.MZ)()],D.prototype,"placeholder",void 0),(0,a.__decorate)([(0,o.MZ)({type:String,attribute:"search-label"})],D.prototype,"searchLabel",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-domains"})],D.prototype,"includeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-domains"})],D.prototype,"excludeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-device-classes"})],D.prototype,"includeDeviceClasses",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-areas"})],D.prototype,"excludeAreas",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-floors"})],D.prototype,"excludeFloors",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],D.prototype,"deviceFilter",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],D.prototype,"entityFilter",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],D.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],D.prototype,"required",void 0),(0,a.__decorate)([(0,o.P)("ha-generic-picker")],D.prototype,"_picker",void 0),D=(0,a.__decorate)([(0,o.EM)("ha-area-floor-picker")],D),t()}catch(b){t(b)}}))},36887:function(e,t,i){i.d(t,{Si:function(){return c}});var a=i(69868),s=i(84922),o=i(11991);i(81164),i(95635);let r,n,d=e=>e;const c=e=>{switch(e.level){case 0:return"M11,10H13V16H11V10M22,12H19V20H5V12H2L12,3L22,12M15,10A2,2 0 0,0 13,8H11A2,2 0 0,0 9,10V16A2,2 0 0,0 11,18H13A2,2 0 0,0 15,16V10Z";case 1:return"M12,3L2,12H5V20H19V12H22L12,3M10,8H14V18H12V10H10V8Z";case 2:return"M12,3L2,12H5V20H19V12H22L12,3M9,8H13A2,2 0 0,1 15,10V12A2,2 0 0,1 13,14H11V16H15V18H9V14A2,2 0 0,1 11,12H13V10H9V8Z";case 3:return"M12,3L22,12H19V20H5V12H2L12,3M15,11.5V10C15,8.89 14.1,8 13,8H9V10H13V12H11V14H13V16H9V18H13A2,2 0 0,0 15,16V14.5A1.5,1.5 0 0,0 13.5,13A1.5,1.5 0 0,0 15,11.5Z";case-1:return"M12,3L2,12H5V20H19V12H22L12,3M11,15H7V13H11V15M15,18H13V10H11V8H15V18Z"}return"M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z"};class l extends s.WF{render(){if(this.floor.icon)return(0,s.qy)(r||(r=d`<ha-icon .icon=${0}></ha-icon>`),this.floor.icon);const e=c(this.floor);return(0,s.qy)(n||(n=d`<ha-svg-icon .path=${0}></ha-svg-icon>`),e)}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],l.prototype,"floor",void 0),(0,a.__decorate)([(0,o.MZ)()],l.prototype,"icon",void 0),l=(0,a.__decorate)([(0,o.EM)("ha-floor-icon")],l)},85032:function(e,t,i){i.a(e,(async function(e,t){try{i(32203),i(79827),i(35748),i(65315),i(12840),i(837),i(22416),i(37089),i(59023),i(5934),i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030),i(18223),i(56660),i(95013);var a=i(69868),s=i(84922),o=i(11991),r=i(65940),n=i(73120),d=i(92830),c=i(56083),l=i(79317),h=i(47420),p=i(4331),u=i(24878),_=i(58453),v=(i(95635),e([_]));_=(v.then?(await v)():v)[0];let y,m,b,g,f,$=e=>e;const k="M17.63,5.84C17.27,5.33 16.67,5 16,5H5A2,2 0 0,0 3,7V17A2,2 0 0,0 5,19H16C16.67,19 17.27,18.66 17.63,18.15L22,12L17.63,5.84Z",M="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",x="___ADD_NEW___",V="___NO_LABELS___";class H extends((0,p.E)(s.WF)){async open(){var e;await this.updateComplete,await(null===(e=this._picker)||void 0===e?void 0:e.open())}hassSubscribe(){return[(0,l.o5)(this.hass.connection,(e=>{this._labels=e}))]}render(){var e;const t=null!==(e=this.placeholder)&&void 0!==e?e:this.hass.localize("ui.components.label-picker.label"),i=this._computeValueRenderer(this._labels);return(0,s.qy)(y||(y=$`
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
        @value-changed=${0}
      >
      </ha-generic-picker>
    `),this.hass,this.autofocus,this.label,this.hass.localize("ui.components.label-picker.no_match"),t,this.value,this._getItems,this._getAdditionalItems,i,this._valueChanged)}_valueChanged(e){e.stopPropagation();const t=e.detail.value;if(t!==V)if(t)if(t.startsWith(x)){this.hass.loadFragmentTranslation("config");const e=t.substring(x.length);(0,u.f)(this,{suggestedName:e,createEntry:async e=>{try{const t=await(0,l._9)(this.hass,e);this._setValue(t.label_id)}catch(t){(0,h.K$)(this,{title:this.hass.localize("ui.components.label-picker.failed_create_label"),text:t.message})}}})}else this._setValue(t);else this._setValue(void 0)}_setValue(e){this.value=e,setTimeout((()=>{(0,n.r)(this,"value-changed",{value:e}),(0,n.r)(this,"change")}),0)}constructor(...e){super(...e),this.noAdd=!1,this.disabled=!1,this.required=!1,this._labelMap=(0,r.A)((e=>e?new Map(e.map((e=>[e.label_id,e]))):new Map)),this._computeValueRenderer=(0,r.A)((e=>t=>{const i=this._labelMap(e).get(t);return i?(0,s.qy)(b||(b=$`
          ${0}
          <span slot="headline">${0}</span>
        `),i.icon?(0,s.qy)(g||(g=$`<ha-icon slot="start" .icon=${0}></ha-icon>`),i.icon):(0,s.qy)(f||(f=$`<ha-svg-icon slot="start" .path=${0}></ha-svg-icon>`),k),i.name):(0,s.qy)(m||(m=$`
            <ha-svg-icon slot="start" .path=${0}></ha-svg-icon>
            <span slot="headline">${0}</span>
          `),k,t)})),this._getLabels=(0,r.A)(((e,t,i,a,s,o,r,n,l,h)=>{if(!e||0===e.length)return[{id:V,primary:this.hass.localize("ui.components.label-picker.no_labels"),icon_path:k}];const p=Object.values(i),u=Object.values(a);let _,v,y={};(s||o||r||n||l)&&(y=(0,c.g2)(u),_=p,v=u.filter((e=>e.labels.length>0)),s&&(_=_.filter((e=>{const t=y[e.id];return!(!t||!t.length)&&y[e.id].some((e=>s.includes((0,d.m)(e.entity_id))))})),v=v.filter((e=>s.includes((0,d.m)(e.entity_id))))),o&&(_=_.filter((e=>{const t=y[e.id];return!t||!t.length||u.every((e=>!o.includes((0,d.m)(e.entity_id))))})),v=v.filter((e=>!o.includes((0,d.m)(e.entity_id))))),r&&(_=_.filter((e=>{const t=y[e.id];return!(!t||!t.length)&&y[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&r.includes(t.attributes.device_class))}))})),v=v.filter((e=>{const t=this.hass.states[e.entity_id];return t.attributes.device_class&&r.includes(t.attributes.device_class)}))),n&&(_=_.filter((e=>n(e)))),l&&(_=_.filter((e=>{const t=y[e.id];return!(!t||!t.length)&&y[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&l(t)}))})),v=v.filter((e=>{const t=this.hass.states[e.entity_id];return!!t&&l(t)}))));let m=e;const b=new Set;let g;_&&(g=_.filter((e=>e.area_id)).map((e=>e.area_id)),_.forEach((e=>{e.labels.forEach((e=>b.add(e)))}))),v&&(g=(null!=g?g:[]).concat(v.filter((e=>e.area_id)).map((e=>e.area_id))),v.forEach((e=>{e.labels.forEach((e=>b.add(e)))}))),g&&g.forEach((e=>{t[e].labels.forEach((e=>b.add(e)))})),h&&(m=m.filter((e=>!h.includes(e.label_id)))),(_||v)&&(m=m.filter((e=>b.has(e.label_id))));return m.map((e=>({id:e.label_id,primary:e.name,icon:e.icon||void 0,icon_path:e.icon?void 0:k,sorting_label:e.name,search_labels:[e.name,e.label_id,e.description].filter((e=>Boolean(e)))})))})),this._getItems=()=>this._getLabels(this._labels,this.hass.areas,this.hass.devices,this.hass.entities,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeLabels),this._allLabelNames=(0,r.A)((e=>e?[...new Set(e.map((e=>e.name.toLowerCase())).filter(Boolean))]:[])),this._getAdditionalItems=e=>{if(this.noAdd)return[];const t=this._allLabelNames(this._labels);return e&&!t.includes(e.toLowerCase())?[{id:x+e,primary:this.hass.localize("ui.components.label-picker.add_new_sugestion",{name:e}),icon_path:M}]:[{id:x,primary:this.hass.localize("ui.components.label-picker.add_new"),icon_path:M}]}}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],H.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)()],H.prototype,"label",void 0),(0,a.__decorate)([(0,o.MZ)()],H.prototype,"value",void 0),(0,a.__decorate)([(0,o.MZ)()],H.prototype,"helper",void 0),(0,a.__decorate)([(0,o.MZ)()],H.prototype,"placeholder",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean,attribute:"no-add"})],H.prototype,"noAdd",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-domains"})],H.prototype,"includeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-domains"})],H.prototype,"excludeDomains",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"include-device-classes"})],H.prototype,"includeDeviceClasses",void 0),(0,a.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-label"})],H.prototype,"excludeLabels",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],H.prototype,"deviceFilter",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],H.prototype,"entityFilter",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],H.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],H.prototype,"required",void 0),(0,a.__decorate)([(0,o.wk)()],H.prototype,"_labels",void 0),(0,a.__decorate)([(0,o.P)("ha-generic-picker")],H.prototype,"_picker",void 0),H=(0,a.__decorate)([(0,o.EM)("ha-label-picker")],H),t()}catch(y){t(y)}}))},66210:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t),i.d(t,{HaTargetSelector:function(){return b}});i(35748),i(65315),i(59023),i(95013);var s=i(69868),o=i(84922),r=i(11991),n=i(65940),d=i(26846),c=i(56083),l=i(71773),h=i(32556),p=i(27957),u=e([p]);p=(u.then?(await u)():u)[0];let _,v,y,m=e=>e;class b extends o.WF{_hasIntegration(e){var t,i;return(null===(t=e.target)||void 0===t?void 0:t.entity)&&(0,d.e)(e.target.entity).some((e=>e.integration))||(null===(i=e.target)||void 0===i?void 0:i.device)&&(0,d.e)(e.target.device).some((e=>e.integration))}updated(e){super.updated(e),e.has("selector")&&this._hasIntegration(this.selector)&&!this._entitySources&&(0,l.c)(this.hass).then((e=>{this._entitySources=e})),e.has("selector")&&(this._createDomains=(0,h.Lo)(this.selector))}render(){return this._hasIntegration(this.selector)&&!this._entitySources?o.s6:(0,o.qy)(_||(_=m` ${0}
      <ha-target-picker
        .hass=${0}
        .value=${0}
        .helper=${0}
        .deviceFilter=${0}
        .entityFilter=${0}
        .disabled=${0}
        .createDomains=${0}
      ></ha-target-picker>`),this.label?(0,o.qy)(v||(v=m`<label>${0}</label>`),this.label):o.s6,this.hass,this.value,this.helper,this._filterDevices,this._filterEntities,this.disabled,this._createDomains)}constructor(...e){super(...e),this.disabled=!1,this._deviceIntegrationLookup=(0,n.A)(c.fk),this._filterEntities=e=>{var t;return null===(t=this.selector.target)||void 0===t||!t.entity||(0,d.e)(this.selector.target.entity).some((t=>(0,h.Ru)(t,e,this._entitySources)))},this._filterDevices=e=>{var t;if(null===(t=this.selector.target)||void 0===t||!t.device)return!0;const i=this._entitySources?this._deviceIntegrationLookup(this._entitySources,Object.values(this.hass.entities)):void 0;return(0,d.e)(this.selector.target.device).some((t=>(0,h.vX)(t,e,i)))}}}b.styles=(0,o.AH)(y||(y=m`
    ha-target-picker {
      display: block;
    }
  `)),(0,s.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,s.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"selector",void 0),(0,s.__decorate)([(0,r.MZ)({type:Object})],b.prototype,"value",void 0),(0,s.__decorate)([(0,r.MZ)()],b.prototype,"label",void 0),(0,s.__decorate)([(0,r.MZ)()],b.prototype,"helper",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],b.prototype,"disabled",void 0),(0,s.__decorate)([(0,r.wk)()],b.prototype,"_entitySources",void 0),(0,s.__decorate)([(0,r.wk)()],b.prototype,"_createDomains",void 0),b=(0,s.__decorate)([(0,r.EM)("ha-selector-target")],b),a()}catch(_){a(_)}}))},27957:function(e,t,i){i.a(e,(async function(e,t){try{i(79827),i(35748),i(99342),i(65315),i(837),i(84136),i(22416),i(37089),i(59023),i(12977),i(5934),i(67579),i(18223),i(30500),i(56660),i(95013);var a=i(69868),s=i(78567),o=(i(38836),i(84922)),r=i(11991),n=i(75907),d=i(26846),c=i(85759),l=i(45361),h=i(73120),p=i(20674),u=i(44537),_=i(92830),v=i(47379),y=i(41602),m=i(79317),b=i(4331),g=i(71755),f=i(57447),$=i(83264),k=i(36887),M=(i(93672),i(20014),i(85032)),x=(i(95635),i(89652)),V=e([g,f,$,M,x]);[g,f,$,M,x]=V.then?(await V)():V;let H,L,w,Z,C,A,D,F,q,z,O,E,j,S,I,R,P=e=>e;const B="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",W="M3 6H21V4H3C1.9 4 1 4.9 1 6V18C1 19.1 1.9 20 3 20H7V18H3V6M13 12H9V13.78C8.39 14.33 8 15.11 8 16C8 16.89 8.39 17.67 9 18.22V20H13V18.22C13.61 17.67 14 16.88 14 16S13.61 14.33 13 13.78V12M11 17.5C10.17 17.5 9.5 16.83 9.5 16S10.17 14.5 11 14.5 12.5 15.17 12.5 16 11.83 17.5 11 17.5M22 8H16C15.5 8 15 8.5 15 9V19C15 19.5 15.5 20 16 20H22C22.5 20 23 19.5 23 19V9C23 8.5 22.5 8 22 8M21 18H17V10H21V18Z",T="M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z",N="M17.63,5.84C17.27,5.33 16.67,5 16,5H5A2,2 0 0,0 3,7V17A2,2 0 0,0 5,19H16C16.67,19 17.27,18.66 17.63,18.15L22,12L17.63,5.84Z",K="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",X="M20 2H4C2.9 2 2 2.9 2 4V20C2 21.11 2.9 22 4 22H20C21.11 22 22 21.11 22 20V4C22 2.9 21.11 2 20 2M4 6L6 4H10.9L4 10.9V6M4 13.7L13.7 4H18.6L4 18.6V13.7M20 18L18 20H13.1L20 13.1V18M20 10.3L10.3 20H5.4L20 5.4V10.3Z",U="M18.17,12L15,8.83L16.41,7.41L21,12L16.41,16.58L15,15.17L18.17,12M5.83,12L9,15.17L7.59,16.59L3,12L7.59,7.42L9,8.83L5.83,12Z";class G extends((0,b.E)(o.WF)){hassSubscribe(){return[(0,m.o5)(this.hass.connection,(e=>{this._labels=e}))]}render(){return this.addOnTop?(0,o.qy)(H||(H=P` ${0} ${0} `),this._renderChips(),this._renderItems()):(0,o.qy)(L||(L=P` ${0} ${0} `),this._renderItems(),this._renderChips())}_renderItems(){var e,t,i,a,s;return(0,o.qy)(w||(w=P`
      <div class="mdc-chip-set items">
        ${0}
        ${0}
        ${0}
        ${0}
        ${0}
      </div>
    `),null!==(e=this.value)&&void 0!==e&&e.floor_id?(0,d.e)(this.value.floor_id).map((e=>{const t=this.hass.floors[e];return this._renderChip("floor_id",e,(null==t?void 0:t.name)||e,void 0,null==t?void 0:t.icon,t?(0,k.Si)(t):T)})):"",null!==(t=this.value)&&void 0!==t&&t.area_id?(0,d.e)(this.value.area_id).map((e=>{const t=this.hass.areas[e];return this._renderChip("area_id",e,(null==t?void 0:t.name)||e,void 0,null==t?void 0:t.icon,X)})):o.s6,null!==(i=this.value)&&void 0!==i&&i.device_id?(0,d.e)(this.value.device_id).map((e=>{const t=this.hass.devices[e];return this._renderChip("device_id",e,t?(0,u.T)(t,this.hass):e,void 0,void 0,W)})):o.s6,null!==(a=this.value)&&void 0!==a&&a.entity_id?(0,d.e)(this.value.entity_id).map((e=>{const t=this.hass.states[e];return this._renderChip("entity_id",e,t?(0,v.u)(t):e,t)})):o.s6,null!==(s=this.value)&&void 0!==s&&s.label_id?(0,d.e)(this.value.label_id).map((e=>{var t,i,a;const s=null===(t=this._labels)||void 0===t?void 0:t.find((t=>t.label_id===e));let o=null!=s&&s.color?(0,c.M)(s.color):void 0;if(null!==(i=o)&&void 0!==i&&i.startsWith("var(")){o=getComputedStyle(this).getPropertyValue(o.substring(4,o.length-1))}return null!==(a=o)&&void 0!==a&&a.startsWith("#")&&(o=(0,l.xp)(o).join(",")),this._renderChip("label_id",e,s?s.name:e,void 0,null==s?void 0:s.icon,N,o)})):o.s6)}_renderChips(){return(0,o.qy)(Z||(Z=P`
      <div class="mdc-chip-set add-container">
        <div
          class="mdc-chip area_id add"
          .type=${0}
          @click=${0}
        >
          <div class="mdc-chip__ripple"></div>
          <ha-svg-icon
            class="mdc-chip__icon mdc-chip__icon--leading"
            .path=${0}
          ></ha-svg-icon>
          <span role="gridcell">
            <span role="button" tabindex="0" class="mdc-chip__primary-action">
              <span class="mdc-chip__text"
                >${0}</span
              >
            </span>
          </span>
        </div>
        <div
          class="mdc-chip device_id add"
          .type=${0}
          @click=${0}
        >
          <div class="mdc-chip__ripple"></div>
          <ha-svg-icon
            class="mdc-chip__icon mdc-chip__icon--leading"
            .path=${0}
          ></ha-svg-icon>
          <span role="gridcell">
            <span role="button" tabindex="0" class="mdc-chip__primary-action">
              <span class="mdc-chip__text"
                >${0}</span
              >
            </span>
          </span>
        </div>
        <div
          class="mdc-chip entity_id add"
          .type=${0}
          @click=${0}
        >
          <div class="mdc-chip__ripple"></div>
          <ha-svg-icon
            class="mdc-chip__icon mdc-chip__icon--leading"
            .path=${0}
          ></ha-svg-icon>
          <span role="gridcell">
            <span role="button" tabindex="0" class="mdc-chip__primary-action">
              <span class="mdc-chip__text"
                >${0}</span
              >
            </span>
          </span>
        </div>
        <div
          class="mdc-chip label_id add"
          .type=${0}
          @click=${0}
        >
          <div class="mdc-chip__ripple"></div>
          <ha-svg-icon
            class="mdc-chip__icon mdc-chip__icon--leading"
            .path=${0}
          ></ha-svg-icon>
          <span role="gridcell">
            <span role="button" tabindex="0" class="mdc-chip__primary-action">
              <span class="mdc-chip__text"
                >${0}</span
              >
            </span>
          </span>
        </div>
        ${0}
      </div>
      ${0}
    `),"area_id",this._showPicker,K,this.hass.localize("ui.components.target-picker.add_area_id"),"device_id",this._showPicker,K,this.hass.localize("ui.components.target-picker.add_device_id"),"entity_id",this._showPicker,K,this.hass.localize("ui.components.target-picker.add_entity_id"),"label_id",this._showPicker,K,this.hass.localize("ui.components.target-picker.add_label_id"),this._renderPicker(),this.helper?(0,o.qy)(C||(C=P`<ha-input-helper-text .disabled=${0}
            >${0}</ha-input-helper-text
          >`),this.disabled,this.helper):"")}_showPicker(e){this._addMode=e.currentTarget.type}_renderChip(e,t,i,a,s,r,d){return(0,o.qy)(A||(A=P`
      <div
        class="mdc-chip ${0}"
        style=${0}
      >
        ${0}
        ${0}
        <span role="gridcell">
          <span role="button" tabindex="0" class="mdc-chip__primary-action">
            <span class="mdc-chip__text">${0}</span>
          </span>
        </span>
        ${0}
        <span role="gridcell">
          <ha-tooltip .for="remove-${0}">
            ${0}
          </ha-tooltip>
          <ha-icon-button
            class="mdc-chip__icon mdc-chip__icon--trailing"
            .label=${0}
            .path=${0}
            hide-title
            .id="remove-${0}"
            .type=${0}
            @click=${0}
          ></ha-icon-button>
        </span>
      </div>
    `),(0,n.H)({[e]:!0}),d?`--color: rgb(${d}); --background-color: rgba(${d}, .5)`:"",s?(0,o.qy)(D||(D=P`<ha-icon
              class="mdc-chip__icon mdc-chip__icon--leading"
              .icon=${0}
            ></ha-icon>`),s):r?(0,o.qy)(F||(F=P`<ha-svg-icon
                class="mdc-chip__icon mdc-chip__icon--leading"
                .path=${0}
              ></ha-svg-icon>`),r):"",a?(0,o.qy)(q||(q=P`<ha-state-icon
              class="mdc-chip__icon mdc-chip__icon--leading"
              .hass=${0}
              .stateObj=${0}
            ></ha-state-icon>`),this.hass,a):"",i,"entity_id"===e?"":(0,o.qy)(z||(z=P`<span role="gridcell">
              <ha-tooltip .for="expand-${0}"
                >${0}
              </ha-tooltip>
              <ha-icon-button
                class="expand-btn mdc-chip__icon mdc-chip__icon--trailing"
                .label=${0}
                .path=${0}
                hide-title
                .id="expand-${0}"
                .type=${0}
                @click=${0}
              ></ha-icon-button>
            </span>`),t,this.hass.localize(`ui.components.target-picker.expand_${e}`),this.hass.localize("ui.components.target-picker.expand"),U,t,e,this._handleExpand),t,this.hass.localize(`ui.components.target-picker.remove_${e}`),this.hass.localize("ui.components.target-picker.remove"),B,t,e,this._handleRemove)}_renderPicker(){var e,t,i,a,s;return this._addMode?(0,o.qy)(O||(O=P`<mwc-menu-surface
      open
      .anchor=${0}
      @closed=${0}
      @opened=${0}
      @input=${0}
      >${0}</mwc-menu-surface
    > `),this._addContainer,this._onClosed,this._onOpened,p.d,"area_id"===this._addMode?(0,o.qy)(E||(E=P`
            <ha-area-floor-picker
              .hass=${0}
              id="input"
              .type=${0}
              .placeholder=${0}
              .searchLabel=${0}
              .deviceFilter=${0}
              .entityFilter=${0}
              .includeDeviceClasses=${0}
              .includeDomains=${0}
              .excludeAreas=${0}
              .excludeFloors=${0}
              @value-changed=${0}
              @opened-changed=${0}
              @click=${0}
            ></ha-area-floor-picker>
          `),this.hass,"area_id",this.hass.localize("ui.components.target-picker.add_area_id"),this.hass.localize("ui.components.target-picker.add_area_id"),this.deviceFilter,this.entityFilter,this.includeDeviceClasses,this.includeDomains,(0,d.e)(null===(e=this.value)||void 0===e?void 0:e.area_id),(0,d.e)(null===(t=this.value)||void 0===t?void 0:t.floor_id),this._targetPicked,this._openedChanged,this._preventDefault):"device_id"===this._addMode?(0,o.qy)(j||(j=P`
              <ha-device-picker
                .hass=${0}
                id="input"
                .type=${0}
                .placeholder=${0}
                .searchLabel=${0}
                .deviceFilter=${0}
                .entityFilter=${0}
                .includeDeviceClasses=${0}
                .includeDomains=${0}
                .excludeDevices=${0}
                @value-changed=${0}
                @opened-changed=${0}
                @click=${0}
              ></ha-device-picker>
            `),this.hass,"device_id",this.hass.localize("ui.components.target-picker.add_device_id"),this.hass.localize("ui.components.target-picker.add_device_id"),this.deviceFilter,this.entityFilter,this.includeDeviceClasses,this.includeDomains,(0,d.e)(null===(i=this.value)||void 0===i?void 0:i.device_id),this._targetPicked,this._openedChanged,this._preventDefault):"label_id"===this._addMode?(0,o.qy)(S||(S=P`
                <ha-label-picker
                  .hass=${0}
                  id="input"
                  .type=${0}
                  .placeholder=${0}
                  .searchLabel=${0}
                  no-add
                  .deviceFilter=${0}
                  .entityFilter=${0}
                  .includeDeviceClasses=${0}
                  .includeDomains=${0}
                  .excludeLabels=${0}
                  @value-changed=${0}
                  @opened-changed=${0}
                  @click=${0}
                ></ha-label-picker>
              `),this.hass,"label_id",this.hass.localize("ui.components.target-picker.add_label_id"),this.hass.localize("ui.components.target-picker.add_label_id"),this.deviceFilter,this.entityFilter,this.includeDeviceClasses,this.includeDomains,(0,d.e)(null===(a=this.value)||void 0===a?void 0:a.label_id),this._targetPicked,this._openedChanged,this._preventDefault):(0,o.qy)(I||(I=P`
                <ha-entity-picker
                  .hass=${0}
                  id="input"
                  .type=${0}
                  .placeholder=${0}
                  .searchLabel=${0}
                  .entityFilter=${0}
                  .includeDeviceClasses=${0}
                  .includeDomains=${0}
                  .excludeEntities=${0}
                  .createDomains=${0}
                  @value-changed=${0}
                  @opened-changed=${0}
                  @click=${0}
                  allow-custom-entity
                ></ha-entity-picker>
              `),this.hass,"entity_id",this.hass.localize("ui.components.target-picker.add_entity_id"),this.hass.localize("ui.components.target-picker.add_entity_id"),this.entityFilter,this.includeDeviceClasses,this.includeDomains,(0,d.e)(null===(s=this.value)||void 0===s?void 0:s.entity_id),this.createDomains,this._targetPicked,this._openedChanged,this._preventDefault)):o.s6}_targetPicked(e){if(e.stopPropagation(),!e.detail.value)return;let t=e.detail.value;const i=e.currentTarget;let a=i.type;("entity_id"!==a||(0,y.n)(t))&&("area_id"===a&&(t=e.detail.value.id,a=`${e.detail.value.type}_id`),i.value="",this.value&&this.value[a]&&(0,d.e)(this.value[a]).includes(t)||(0,h.r)(this,"value-changed",{value:this.value?Object.assign(Object.assign({},this.value),{},{[a]:this.value[a]?[...(0,d.e)(this.value[a]),t]:t}):{[a]:t}}))}_handleExpand(e){const t=e.currentTarget,i=t.id.replace(/^expand-/,""),a=[],s=[],o=[];if("floor_id"===t.type)Object.values(this.hass.areas).forEach((e=>{var t;e.floor_id!==i||null!==(t=this.value.area_id)&&void 0!==t&&t.includes(e.area_id)||!this._areaMeetsFilter(e)||a.push(e.area_id)}));else if("area_id"===t.type)Object.values(this.hass.devices).forEach((e=>{var t;e.area_id!==i||null!==(t=this.value.device_id)&&void 0!==t&&t.includes(e.id)||!this._deviceMeetsFilter(e)||s.push(e.id)})),Object.values(this.hass.entities).forEach((e=>{var t;e.area_id!==i||null!==(t=this.value.entity_id)&&void 0!==t&&t.includes(e.entity_id)||!this._entityRegMeetsFilter(e)||o.push(e.entity_id)}));else if("device_id"===t.type)Object.values(this.hass.entities).forEach((e=>{var t;e.device_id!==i||null!==(t=this.value.entity_id)&&void 0!==t&&t.includes(e.entity_id)||!this._entityRegMeetsFilter(e)||o.push(e.entity_id)}));else{if("label_id"!==t.type)return;Object.values(this.hass.areas).forEach((e=>{var t;!e.labels.includes(i)||null!==(t=this.value.area_id)&&void 0!==t&&t.includes(e.area_id)||!this._areaMeetsFilter(e)||a.push(e.area_id)})),Object.values(this.hass.devices).forEach((e=>{var t;!e.labels.includes(i)||null!==(t=this.value.device_id)&&void 0!==t&&t.includes(e.id)||!this._deviceMeetsFilter(e)||s.push(e.id)})),Object.values(this.hass.entities).forEach((e=>{var t;!e.labels.includes(i)||null!==(t=this.value.entity_id)&&void 0!==t&&t.includes(e.entity_id)||!this._entityRegMeetsFilter(e,!0)||o.push(e.entity_id)}))}let r=this.value;o.length&&(r=this._addItems(r,"entity_id",o)),s.length&&(r=this._addItems(r,"device_id",s)),a.length&&(r=this._addItems(r,"area_id",a)),r=this._removeItem(r,t.type,i),(0,h.r)(this,"value-changed",{value:r})}_handleRemove(e){const t=e.currentTarget,i=t.id.replace(/^remove-/,"");(0,h.r)(this,"value-changed",{value:this._removeItem(this.value,t.type,i)})}_addItems(e,t,i){return Object.assign(Object.assign({},e),{},{[t]:e[t]?(0,d.e)(e[t]).concat(i):i})}_removeItem(e,t,i){const a=(0,d.e)(e[t]).filter((e=>String(e)!==i));if(a.length)return Object.assign(Object.assign({},e),{},{[t]:a});const s=Object.assign({},e);return delete s[t],Object.keys(s).length?s:void 0}_onClosed(e){e.stopPropagation(),e.target.open=!0}async _onOpened(){var e,t;this._addMode&&(await(null===(e=this._inputElement)||void 0===e?void 0:e.focus()),await(null===(t=this._inputElement)||void 0===t?void 0:t.open()),this._opened=!0)}_openedChanged(e){this._opened&&!e.detail.value&&(this._opened=!1,this._addMode=void 0)}_preventDefault(e){e.preventDefault()}_areaMeetsFilter(e){if(Object.values(this.hass.devices).filter((t=>t.area_id===e.area_id)).some((e=>this._deviceMeetsFilter(e))))return!0;return!!Object.values(this.hass.entities).filter((t=>t.area_id===e.area_id)).some((e=>this._entityRegMeetsFilter(e)))}_deviceMeetsFilter(e){return!!Object.values(this.hass.entities).filter((t=>t.device_id===e.id)).some((e=>this._entityRegMeetsFilter(e)))&&!(this.deviceFilter&&!this.deviceFilter(e))}_entityRegMeetsFilter(e,t=!1){if(e.hidden||e.entity_category&&!t)return!1;if(this.includeDomains&&!this.includeDomains.includes((0,_.m)(e.entity_id)))return!1;if(this.includeDeviceClasses){const t=this.hass.states[e.entity_id];if(!t)return!1;if(!t.attributes.device_class||!this.includeDeviceClasses.includes(t.attributes.device_class))return!1}if(this.entityFilter){const t=this.hass.states[e.entity_id];if(!t)return!1;if(!this.entityFilter(t))return!1}return!0}static get styles(){return(0,o.AH)(R||(R=P`
      ${0}
      .mdc-chip {
        color: var(--primary-text-color);
      }
      .items {
        z-index: 2;
      }
      .mdc-chip-set {
        padding: 4px 0;
      }
      .mdc-chip.add {
        color: rgba(0, 0, 0, 0.87);
      }
      .add-container {
        position: relative;
        display: inline-flex;
      }
      .mdc-chip:not(.add) {
        cursor: default;
      }
      .mdc-chip ha-icon-button {
        --mdc-icon-button-size: 24px;
        display: flex;
        align-items: center;
        outline: none;
      }
      .mdc-chip ha-icon-button ha-svg-icon {
        border-radius: 50%;
        background: var(--secondary-text-color);
      }
      .mdc-chip__icon.mdc-chip__icon--trailing {
        width: 16px;
        height: 16px;
        --mdc-icon-size: 14px;
        color: var(--secondary-text-color);
        margin-inline-start: 4px !important;
        margin-inline-end: -4px !important;
        direction: var(--direction);
      }
      .mdc-chip__icon--leading {
        display: flex;
        align-items: center;
        justify-content: center;
        --mdc-icon-size: 20px;
        border-radius: 50%;
        padding: 6px;
        margin-left: -13px !important;
        margin-inline-start: -13px !important;
        margin-inline-end: 4px !important;
        direction: var(--direction);
      }
      .expand-btn {
        margin-right: 0;
        margin-inline-end: 0;
        margin-inline-start: initial;
      }
      .mdc-chip.area_id:not(.add),
      .mdc-chip.floor_id:not(.add) {
        border: 1px solid #fed6a4;
        background: var(--card-background-color);
      }
      .mdc-chip.area_id:not(.add) .mdc-chip__icon--leading,
      .mdc-chip.area_id.add,
      .mdc-chip.floor_id:not(.add) .mdc-chip__icon--leading,
      .mdc-chip.floor_id.add {
        background: #fed6a4;
      }
      .mdc-chip.device_id:not(.add) {
        border: 1px solid #a8e1fb;
        background: var(--card-background-color);
      }
      .mdc-chip.device_id:not(.add) .mdc-chip__icon--leading,
      .mdc-chip.device_id.add {
        background: #a8e1fb;
      }
      .mdc-chip.entity_id:not(.add) {
        border: 1px solid #d2e7b9;
        background: var(--card-background-color);
      }
      .mdc-chip.entity_id:not(.add) .mdc-chip__icon--leading,
      .mdc-chip.entity_id.add {
        background: #d2e7b9;
      }
      .mdc-chip.label_id:not(.add) {
        border: 1px solid var(--color, #e0e0e0);
        background: var(--card-background-color);
      }
      .mdc-chip.label_id:not(.add) .mdc-chip__icon--leading,
      .mdc-chip.label_id.add {
        background: var(--background-color, #e0e0e0);
      }
      .mdc-chip:hover {
        z-index: 5;
      }
      :host([disabled]) .mdc-chip {
        opacity: var(--light-disabled-opacity);
        pointer-events: none;
      }
      mwc-menu-surface {
        --mdc-menu-min-width: 100%;
      }
      ha-entity-picker,
      ha-device-picker,
      ha-area-floor-picker {
        display: block;
        width: 100%;
      }
      ha-tooltip {
        --ha-tooltip-arrow-size: 0;
      }
    `),(0,o.iz)(s))}constructor(...e){super(...e),this.disabled=!1,this.addOnTop=!1,this._opened=!1}}(0,a.__decorate)([(0,r.MZ)({attribute:!1})],G.prototype,"hass",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],G.prototype,"value",void 0),(0,a.__decorate)([(0,r.MZ)()],G.prototype,"label",void 0),(0,a.__decorate)([(0,r.MZ)()],G.prototype,"helper",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1,type:Array})],G.prototype,"createDomains",void 0),(0,a.__decorate)([(0,r.MZ)({type:Array,attribute:"include-domains"})],G.prototype,"includeDomains",void 0),(0,a.__decorate)([(0,r.MZ)({type:Array,attribute:"include-device-classes"})],G.prototype,"includeDeviceClasses",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],G.prototype,"deviceFilter",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],G.prototype,"entityFilter",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],G.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:"add-on-top",type:Boolean})],G.prototype,"addOnTop",void 0),(0,a.__decorate)([(0,r.wk)()],G.prototype,"_addMode",void 0),(0,a.__decorate)([(0,r.P)("#input")],G.prototype,"_inputElement",void 0),(0,a.__decorate)([(0,r.P)(".add-container",!0)],G.prototype,"_addContainer",void 0),(0,a.__decorate)([(0,r.wk)()],G.prototype,"_labels",void 0),G=(0,a.__decorate)([(0,r.EM)("ha-target-picker")],G),t()}catch(H){t(H)}}))},89652:function(e,t,i){i.a(e,(async function(e,t){try{i(35748),i(95013);var a=i(69868),s=i(28784),o=i(84922),r=i(11991),n=e([s]);s=(n.then?(await n)():n)[0];let d,c=e=>e;class l extends s.A{static get styles(){return[s.A.styles,(0,o.AH)(d||(d=c`
        :host {
          --wa-tooltip-background-color: var(--secondary-background-color);
          --wa-tooltip-color: var(--primary-text-color);
          --wa-tooltip-font-family: var(
            --ha-tooltip-font-family,
            var(--ha-font-family-body)
          );
          --wa-tooltip-font-size: var(
            --ha-tooltip-font-size,
            var(--ha-font-size-s)
          );
          --wa-tooltip-font-weight: var(
            --ha-tooltip-font-weight,
            var(--ha-font-weight-normal)
          );
          --wa-tooltip-line-height: var(
            --ha-tooltip-line-height,
            var(--ha-line-height-condensed)
          );
          --wa-tooltip-padding: 8px;
          --wa-tooltip-border-radius: var(--ha-tooltip-border-radius, 4px);
          --wa-tooltip-arrow-size: var(--ha-tooltip-arrow-size, 8px);
          --wa-z-index-tooltip: var(--ha-tooltip-z-index, 1000);
        }
      `))]}constructor(...e){super(...e),this.showDelay=150,this.hideDelay=400}}(0,a.__decorate)([(0,r.MZ)({attribute:"show-delay",type:Number})],l.prototype,"showDelay",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:"hide-delay",type:Number})],l.prototype,"hideDelay",void 0),l=(0,a.__decorate)([(0,r.EM)("ha-tooltip")],l),t()}catch(d){t(d)}}))},74455:function(e,t,i){i(35748),i(95013);var a=i(69868),s=i(84922),o=i(11991);let r,n,d=e=>e;class c extends s.WF{render(){return(0,s.qy)(r||(r=d`
      <svg width="100%" height="100%" viewBox="0 0 48 48">
        <line x1="24" y1="0" x2="24" y2=${0}></line>
        <line x1="24" y1="24" x2="36" y2="24"></line>
      </svg>
    `),this.end?"24":"48")}constructor(...e){super(...e),this.end=!1}}c.styles=(0,s.AH)(n||(n=d`
    :host {
      display: block;
      width: 48px;
      height: 48px;
    }
    line {
      stroke: var(--divider-color);
      stroke-width: 2;
      stroke-dasharray: 2;
    }
  `)),(0,a.__decorate)([(0,o.MZ)({type:Boolean,reflect:!0})],c.prototype,"end",void 0),c=(0,a.__decorate)([(0,o.EM)("ha-tree-indicator")],c)},71773:function(e,t,i){i.d(t,{c:function(){return o}});i(35748),i(5934),i(95013);const a=async(e,t,i,s,o,...r)=>{const n=o,d=n[e],c=d=>s&&s(o,d.result)!==d.cacheKey?(n[e]=void 0,a(e,t,i,s,o,...r)):d.result;if(d)return d instanceof Promise?d.then(c):c(d);const l=i(o,...r);return n[e]=l,l.then((i=>{n[e]={result:i,cacheKey:null==s?void 0:s(o,i)},setTimeout((()=>{n[e]=void 0}),t)}),(()=>{n[e]=void 0})),l},s=e=>e.callWS({type:"entity/source"}),o=e=>a("_entitySources",3e4,s,(e=>Object.keys(e.states).length),e)},88285:function(e,t,i){i.d(t,{KD:function(){return a},_o:function(){return s}});i(35748),i(99342),i(12977),i(95013),i(90963),i(52435);const a=(e,t)=>e.callWS(Object.assign({type:"config/floor_registry/create"},t)),s=e=>{const t={};for(const i of e)i.floor_id&&(i.floor_id in t||(t[i.floor_id]=[]),t[i.floor_id].push(i));return t}},79317:function(e,t,i){i.d(t,{Rp:function(){return l},_9:function(){return c},o5:function(){return d}});i(35058),i(12977);var a=i(47308),s=i(90963),o=i(24802);const r=e=>e.sendMessagePromise({type:"config/label_registry/list"}).then((e=>e.sort(((e,t)=>(0,s.xL)(e.name,t.name))))),n=(e,t)=>e.subscribeEvents((0,o.s)((()=>r(e).then((e=>t.setState(e,!0)))),500,!0),"label_registry_updated"),d=(e,t)=>(0,a.N)("_labelRegistry",r,n,e,t),c=(e,t)=>e.callWS(Object.assign({type:"config/label_registry/create"},t)),l=(e,t,i)=>e.callWS(Object.assign({type:"config/label_registry/update",label_id:t},i))},4331:function(e,t,i){i.d(t,{E:function(){return o}});i(79827),i(35748),i(65315),i(59023),i(5934),i(18223),i(95013);var a=i(69868),s=i(11991);const o=e=>{class t extends e{connectedCallback(){super.connectedCallback(),this._checkSubscribed()}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const e=this.__unsubs.pop();e instanceof Promise?e.then((e=>e())):e()}this.__unsubs=void 0}}updated(e){if(super.updated(e),e.has("hass"))this._checkSubscribed();else if(this.hassSubscribeRequiredHostProps)for(const t of e.keys())if(this.hassSubscribeRequiredHostProps.includes(t))return void this._checkSubscribed()}hassSubscribe(){return[]}_checkSubscribed(){var e;void 0!==this.__unsubs||!this.isConnected||void 0===this.hass||null!==(e=this.hassSubscribeRequiredHostProps)&&void 0!==e&&e.some((e=>void 0===this[e]))||(this.__unsubs=this.hassSubscribe())}}return(0,a.__decorate)([(0,s.MZ)({attribute:!1})],t.prototype,"hass",void 0),t}},24878:function(e,t,i){i.d(t,{f:function(){return o}});i(35748),i(5934),i(95013);var a=i(73120);const s=()=>i.e("3327").then(i.bind(i,76882)),o=(e,t)=>{(0,a.r)(e,"show-dialog",{dialogTag:"dialog-label-detail",dialogImport:s,dialogParams:t})}},45363:function(e,t,i){i.d(t,{MR:function(){return a},a_:function(){return s},bg:function(){return o}});i(56660);const a=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,s=e=>e.split("/")[4],o=e=>e.startsWith("https://brands.home-assistant.io/")}}]);
//# sourceMappingURL=3247.fa5053a2875725b5.js.map