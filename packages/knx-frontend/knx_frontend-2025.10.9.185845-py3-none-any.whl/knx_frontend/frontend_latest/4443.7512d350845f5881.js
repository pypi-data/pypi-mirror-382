export const __webpack_id__="4443";export const __webpack_ids__=["4443"];export const __webpack_modules__={35384:function(e,t,i){i.d(t,{z:()=>o});const o=e=>{if(void 0===e)return;if("object"!=typeof e){if("string"==typeof e||isNaN(e)){const t=e?.toString().split(":")||[];if(1===t.length)return{seconds:Number(t[0])};if(t.length>3)return;const i=Number(t[2])||0,o=Math.floor(i);return{hours:Number(t[0])||0,minutes:Number(t[1])||0,seconds:o,milliseconds:Math.floor(1e3*Number((i-o).toFixed(4)))}}return{seconds:e}}if(!("days"in e))return e;const{days:t,minutes:i,seconds:o,milliseconds:r}=e;let a=e.hours||0;return a=(a||0)+24*(t||0),{hours:a,minutes:i,seconds:o,milliseconds:r}}},895:function(e,t,i){i.d(t,{PE:()=>n});var o=i(6423),r=i(95226);const a=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],n=e=>e.first_weekday===r.zt.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,o.S)(e.language)%7:a.includes(e.first_weekday)?a.indexOf(e.first_weekday):1},49108:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{Yq:()=>c,zB:()=>u});var r=i(96904),a=i(65940),n=i(95226),s=i(39227),l=e([r,s]);[r,s]=l.then?(await l)():l;(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"long",month:"long",day:"numeric",timeZone:(0,s.w)(e.time_zone,t)})));const c=(e,t,i)=>d(t,i.time_zone).format(e),d=(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",timeZone:(0,s.w)(e.time_zone,t)}))),u=((0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"short",day:"numeric",timeZone:(0,s.w)(e.time_zone,t)}))),(e,t,i)=>{const o=p(t,i.time_zone);if(t.date_format===n.ow.language||t.date_format===n.ow.system)return o.format(e);const r=o.formatToParts(e),a=r.find((e=>"literal"===e.type))?.value,s=r.find((e=>"day"===e.type))?.value,l=r.find((e=>"month"===e.type))?.value,c=r.find((e=>"year"===e.type))?.value,d=r[r.length-1];let u="literal"===d?.type?d?.value:"";"bg"===t.language&&t.date_format===n.ow.YMD&&(u="");return{[n.ow.DMY]:`${s}${a}${l}${a}${c}${u}`,[n.ow.MDY]:`${l}${a}${s}${a}${c}${u}`,[n.ow.YMD]:`${c}${a}${l}${a}${s}${u}`}[t.date_format]}),p=(0,a.A)(((e,t)=>{const i=e.date_format===n.ow.system?void 0:e.language;return e.date_format===n.ow.language||(e.date_format,n.ow.system),new Intl.DateTimeFormat(i,{year:"numeric",month:"numeric",day:"numeric",timeZone:(0,s.w)(e.time_zone,t)})}));(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{day:"numeric",month:"short",timeZone:(0,s.w)(e.time_zone,t)}))),(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{month:"long",year:"numeric",timeZone:(0,s.w)(e.time_zone,t)}))),(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{month:"long",timeZone:(0,s.w)(e.time_zone,t)}))),(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",timeZone:(0,s.w)(e.time_zone,t)}))),(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"long",timeZone:(0,s.w)(e.time_zone,t)}))),(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"short",timeZone:(0,s.w)(e.time_zone,t)})));o()}catch(c){o(c)}}))},12950:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{r6:()=>u});var r=i(96904),a=i(65940),n=i(49108),s=i(48505),l=i(39227),c=i(56044),d=e([r,n,s,l]);[r,n,s,l]=d.then?(await d)():d;const u=(e,t,i)=>p(t,i.time_zone).format(e),p=(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",hour:(0,c.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.J)(e)?"h12":"h23",timeZone:(0,l.w)(e.time_zone,t)})));(0,a.A)((()=>new Intl.DateTimeFormat(void 0,{year:"numeric",month:"long",day:"numeric",hour:"2-digit",minute:"2-digit"}))),(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"short",day:"numeric",hour:(0,c.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.J)(e)?"h12":"h23",timeZone:(0,l.w)(e.time_zone,t)}))),(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{month:"short",day:"numeric",hour:(0,c.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.J)(e)?"h12":"h23",timeZone:(0,l.w)(e.time_zone,t)}))),(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",hour:(0,c.J)(e)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,c.J)(e)?"h12":"h23",timeZone:(0,l.w)(e.time_zone,t)})));o()}catch(u){o(u)}}))},52744:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{i:()=>d,nR:()=>l});var r=i(96904),a=i(65940),n=e([r]);r=(n.then?(await n)():n)[0];const s=e=>e<10?`0${e}`:e,l=(e,t)=>{const i=t.days||0,o=t.hours||0,r=t.minutes||0,a=t.seconds||0,n=t.milliseconds||0;return i>0?`${Intl.NumberFormat(e.language,{style:"unit",unit:"day",unitDisplay:"long"}).format(i)} ${o}:${s(r)}:${s(a)}`:o>0?`${o}:${s(r)}:${s(a)}`:r>0?`${r}:${s(a)}`:a>0?Intl.NumberFormat(e.language,{style:"unit",unit:"second",unitDisplay:"long"}).format(a):n>0?Intl.NumberFormat(e.language,{style:"unit",unit:"millisecond",unitDisplay:"long"}).format(n):null},c=(0,a.A)((e=>new Intl.DurationFormat(e.language,{style:"long"}))),d=(e,t)=>c(e).format(t);(0,a.A)((e=>new Intl.DurationFormat(e.language,{style:"digital",hoursDisplay:"auto"}))),(0,a.A)((e=>new Intl.DurationFormat(e.language,{style:"narrow",daysDisplay:"always"}))),(0,a.A)((e=>new Intl.DurationFormat(e.language,{style:"narrow",hoursDisplay:"always"}))),(0,a.A)((e=>new Intl.DurationFormat(e.language,{style:"narrow",minutesDisplay:"always"})));o()}catch(s){o(s)}}))},48505:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{LW:()=>y,Xs:()=>h,fU:()=>c,ie:()=>u});var r=i(96904),a=i(65940),n=i(39227),s=i(56044),l=e([r,n]);[r,n]=l.then?(await l)():l;const c=(e,t,i)=>d(t,i.time_zone).format(e),d=(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{hour:"numeric",minute:"2-digit",hourCycle:(0,s.J)(e)?"h12":"h23",timeZone:(0,n.w)(e.time_zone,t)}))),u=(e,t,i)=>p(t,i.time_zone).format(e),p=(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{hour:(0,s.J)(e)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,s.J)(e)?"h12":"h23",timeZone:(0,n.w)(e.time_zone,t)}))),h=(e,t,i)=>m(t,i.time_zone).format(e),m=(0,a.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"long",hour:(0,s.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,s.J)(e)?"h12":"h23",timeZone:(0,n.w)(e.time_zone,t)}))),y=(e,t,i)=>_(t,i.time_zone).format(e),_=(0,a.A)(((e,t)=>new Intl.DateTimeFormat("en-GB",{hour:"numeric",minute:"2-digit",hour12:!1,timeZone:(0,n.w)(e.time_zone,t)})));o()}catch(c){o(c)}}))},39227:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{w:()=>c});var r=i(96904),a=i(95226),n=e([r]);r=(n.then?(await n)():n)[0];const s=Intl.DateTimeFormat?.().resolvedOptions?.().timeZone,l=s??"UTC",c=(e,t)=>e===a.Wj.local&&s?l:t;o()}catch(s){o(s)}}))},15216:function(e,t,i){i.d(t,{A:()=>r});const o=e=>e<10?`0${e}`:e;function r(e){const t=Math.floor(e/3600),i=Math.floor(e%3600/60),r=Math.floor(e%3600%60);return t>0?`${t}:${o(i)}:${o(r)}`:i>0?`${i}:${o(r)}`:r>0?""+r:null}},56044:function(e,t,i){i.d(t,{J:()=>a});var o=i(65940),r=i(95226);const a=(0,o.A)((e=>{if(e.time_format===r.Hg.language||e.time_format===r.Hg.system){const t=e.time_format===r.Hg.language?e.language:void 0;return new Date("January 1, 2023 22:00:00").toLocaleString(t).includes("10")}return e.time_format===r.Hg.am_pm}))},83490:function(e,t,i){i.d(t,{I:()=>a});class o{addFromStorage(e){if(!this._storage[e]){const t=this.storage.getItem(e);t&&(this._storage[e]=JSON.parse(t))}}subscribeChanges(e,t){return this._listeners[e]?this._listeners[e].push(t):this._listeners[e]=[t],()=>{this.unsubscribeChanges(e,t)}}unsubscribeChanges(e,t){if(!(e in this._listeners))return;const i=this._listeners[e].indexOf(t);-1!==i&&this._listeners[e].splice(i,1)}hasKey(e){return e in this._storage}getValue(e){return this._storage[e]}setValue(e,t){const i=this._storage[e];this._storage[e]=t;try{void 0===t?this.storage.removeItem(e):this.storage.setItem(e,JSON.stringify(t))}catch(o){}finally{this._listeners[e]&&this._listeners[e].forEach((e=>e(i,t)))}}constructor(e=window.localStorage){this._storage={},this._listeners={},this.storage=e,this.storage===window.localStorage&&window.addEventListener("storage",(e=>{e.key&&this.hasKey(e.key)&&(this._storage[e.key]=e.newValue?JSON.parse(e.newValue):e.newValue,this._listeners[e.key]&&this._listeners[e.key].forEach((t=>t(e.oldValue?JSON.parse(e.oldValue):e.oldValue,this._storage[e.key]))))}))}}const r={};function a(e){return(t,i)=>{if("object"==typeof i)throw new Error("This decorator does not support this compilation type.");const a=e.storage||"localStorage";let n;a&&a in r?n=r[a]:(n=new o(window[a]),r[a]=n);const s=e.key||String(i);n.addFromStorage(s);const l=!1!==e.subscribe?e=>n.subscribeChanges(s,((t,o)=>{e.requestUpdate(i,t)})):void 0,c=()=>n.hasKey(s)?e.deserializer?e.deserializer(n.getValue(s)):n.getValue(s):void 0,d=(t,o)=>{let r;e.state&&(r=c()),n.setValue(s,e.serializer?e.serializer(o):o),e.state&&t.requestUpdate(i,r)},u=t.performUpdate;if(t.performUpdate=function(){this.__initialized=!0,u.call(this)},e.subscribe){const e=t.connectedCallback,i=t.disconnectedCallback;t.connectedCallback=function(){e.call(this);const t=this;t.__unbsubLocalStorage||(t.__unbsubLocalStorage=l?.(this))},t.disconnectedCallback=function(){i.call(this);this.__unbsubLocalStorage?.(),this.__unbsubLocalStorage=void 0}}const p=Object.getOwnPropertyDescriptor(t,i);let h;if(void 0===p)h={get(){return c()},set(e){(this.__initialized||void 0===c())&&d(this,e)},configurable:!0,enumerable:!0};else{const e=p.set;h={...p,get(){return c()},set(t){(this.__initialized||void 0===c())&&d(this,t),e?.call(this,t)}}}Object.defineProperty(t,i,h)}}},88727:function(e,t,i){i.d(t,{C:()=>o});const o=e=>{e.preventDefault(),e.stopPropagation()}},27881:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{R:()=>u});var r=i(8948),a=(i(40653),i(49108)),n=i(12950),s=i(44665),l=i(8692),c=(i(3461),i(92830)),d=e([r,a,n,s]);[r,a,n,s]=d.then?(await d)():d;const u=(e,t,i,o)=>{const r=t.entity_id,a=t.attributes.device_class,n=(0,c.m)(r),s=i[r],d=s?.translation_key;return d&&e(`component.${s.platform}.entity.${n}.${d}.state_attributes.${o}.name`)||a&&e(`component.${n}.entity_component.${a}.state_attributes.${o}.name`)||e(`component.${n}.entity_component._.state_attributes.${o}.name`)||(0,l.Z)(o.replace(/_/g," ").replace(/\bid\b/g,"ID").replace(/\bip\b/g,"IP").replace(/\bmac\b/g,"MAC").replace(/\bgps\b/g,"GPS"))};o()}catch(u){o(u)}}))},44537:function(e,t,i){i.d(t,{xn:()=>a,T:()=>n});var o=i(65940),r=i(47379);const a=e=>(e.name_by_user||e.name)?.trim(),n=(e,t,i)=>a(e)||i&&s(t,i)||t.localize("ui.panel.config.devices.unnamed_device",{type:t.localize(`ui.panel.config.devices.type.${e.entry_type||"device"}`)}),s=(e,t)=>{for(const i of t||[]){const t="string"==typeof i?i:i.entity_id,o=e.states[t];if(o)return(0,r.u)(o)}};(0,o.A)((e=>function(e){const t=new Set,i=new Set;for(const o of e)i.has(o)?t.add(o):i.add(o);return t}(Object.values(e).map((e=>a(e))).filter((e=>void 0!==e)))))},47379:function(e,t,i){i.d(t,{u:()=>r});var o=i(90321);const r=e=>{return t=e.entity_id,void 0===(i=e.attributes).friendly_name?(0,o.Y)(t).replace(/_/g," "):(i.friendly_name??"").toString();var t,i}},24382:function(e,t,i){i.d(t,{e:()=>o});const o=e=>"latitude"in e.attributes&&"longitude"in e.attributes},41602:function(e,t,i){i.d(t,{n:()=>r});const o=/^(\w+)\.(\w+)$/,r=e=>o.test(e)},8692:function(e,t,i){i.d(t,{Z:()=>o});const o=e=>e.charAt(0).toUpperCase()+e.slice(1)},72106:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{c:()=>s,q:()=>l});var r=i(96904),a=i(65940),n=e([r]);r=(n.then?(await n)():n)[0];const s=(e,t)=>c(e).format(t),l=(e,t)=>d(e).format(t),c=(0,a.A)((e=>new Intl.ListFormat(e.language,{style:"long",type:"conjunction"}))),d=(0,a.A)((e=>new Intl.ListFormat(e.language,{style:"long",type:"disjunction"})));o()}catch(s){o(s)}}))},71767:function(e,t,i){i.d(t,{F:()=>r,r:()=>a});const o=/{%|{{/,r=e=>o.test(e),a=e=>{if(!e)return!1;if("string"==typeof e)return r(e);if("object"==typeof e){return(Array.isArray(e)?e:Object.values(e)).some((e=>e&&a(e)))}return!1}},3461:function(){const e="^\\d{4}-(0[1-9]|1[0-2])-([12]\\d|0[1-9]|3[01])";new RegExp(e+"$"),new RegExp(e)},4071:function(e,t,i){i.d(t,{_:()=>r});var o=i(36207);const r=(e,t)=>{if(!(t instanceof o.C5))return{warnings:[t.message],errors:void 0};const i=[],r=[];for(const o of t.failures())if(void 0===o.value)i.push(e.localize("ui.errors.config.key_missing",{key:o.path.join(".")}));else if("never"===o.type)r.push(e.localize("ui.errors.config.key_not_expected",{key:o.path.join(".")}));else{if("union"===o.type)continue;"enums"===o.type?r.push(e.localize("ui.errors.config.key_wrong_type",{key:o.path.join("."),type_correct:o.message.replace("Expected ","").split(", ")[0],type_wrong:JSON.stringify(o.value)})):r.push(e.localize("ui.errors.config.key_wrong_type",{key:o.path.join("."),type_correct:o.refinement||o.type,type_wrong:JSON.stringify(o.value)}))}return{warnings:r,errors:i}}},51663:function(e,t,i){i(90933)},4822:function(e,t,i){i.d(t,{V:()=>b});var o=i(69868),r=i(97809),a=i(84922),n=i(11991),s=i(73120),l=i(24986),c=i(7657),d=i(7137),u=i(20808);class p extends d.${}p.styles=[u.R,a.AH`
      :host {
        --ha-icon-display: block;
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-secondary: var(--secondary-text-color);
        --md-sys-color-surface: var(--card-background-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-sys-color-on-surface-variant: var(--secondary-text-color);
      }
    `],p=(0,o.__decorate)([(0,n.EM)("ha-md-select-option")],p);var h=i(39072),m=i(29512),y=i(89152);class _ extends h.V{}_.styles=[m.R,y.R,a.AH`
      :host {
        --ha-icon-display: block;
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-secondary: var(--secondary-text-color);
        --md-sys-color-surface: var(--card-background-color);
        --md-sys-color-on-surface-variant: var(--secondary-text-color);

        --md-sys-color-surface-container-highest: var(--input-fill-color);
        --md-sys-color-on-surface: var(--input-ink-color);

        --md-sys-color-surface-container: var(--input-fill-color);
        --md-sys-color-on-secondary-container: var(--primary-text-color);
        --md-sys-color-secondary-container: var(--input-fill-color);
        --md-menu-container-color: var(--card-background-color);
      }
    `],_=(0,o.__decorate)([(0,n.EM)("ha-md-select")],_);var f=i(20674);const g="NO_AUTOMATION",v="UNKNOWN_AUTOMATION";class b extends a.WF{get NO_AUTOMATION_TEXT(){return this.hass.localize("ui.panel.config.devices.automation.actions.no_actions")}get UNKNOWN_AUTOMATION_TEXT(){return this.hass.localize("ui.panel.config.devices.automation.actions.unknown_action")}get _value(){if(!this.value)return"";if(!this._automations.length)return g;const e=this._automations.findIndex((e=>(0,c.Po)(this._entityReg,e,this.value)));return-1===e?v:`${this._automations[e].device_id}_${e}`}render(){if(this._renderEmpty)return a.s6;const e=this._value;return a.qy`
      <ha-md-select
        .label=${this.label}
        .value=${e}
        @change=${this._automationChanged}
        @closed=${f.d}
        .disabled=${0===this._automations.length}
      >
        ${e===g?a.qy`<ha-md-select-option .value=${g}>
              ${this.NO_AUTOMATION_TEXT}
            </ha-md-select-option>`:a.s6}
        ${e===v?a.qy`<ha-md-select-option .value=${v}>
              ${this.UNKNOWN_AUTOMATION_TEXT}
            </ha-md-select-option>`:a.s6}
        ${this._automations.map(((e,t)=>a.qy`
            <ha-md-select-option .value=${`${e.device_id}_${t}`}>
              ${this._localizeDeviceAutomation(this.hass,this._entityReg,e)}
            </ha-md-select-option>
          `))}
      </ha-md-select>
    `}updated(e){super.updated(e),e.has("deviceId")&&this._updateDeviceInfo()}async _updateDeviceInfo(){this._automations=this.deviceId?(await this._fetchDeviceAutomations(this.hass,this.deviceId)).sort(c.RK):[],this.value&&this.value.device_id===this.deviceId||this._setValue(this._automations.length?this._automations[0]:this._createNoAutomation(this.deviceId)),this._renderEmpty=!0,await this.updateComplete,this._renderEmpty=!1}_automationChanged(e){const t=e.target.value;if(!t||[v,g].includes(t))return;const[i,o]=t.split("_"),r=this._automations[o];r.device_id===i&&this._setValue(r)}_setValue(e){if(this.value&&(0,c.Po)(this._entityReg,e,this.value))return;const t={...e};delete t.metadata,(0,s.r)(this,"value-changed",{value:t})}constructor(e,t,i){super(),this._automations=[],this._renderEmpty=!1,this._localizeDeviceAutomation=e,this._fetchDeviceAutomations=t,this._createNoAutomation=i}}b.styles=a.AH`
    ha-select {
      display: block;
    }
  `,(0,o.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)()],b.prototype,"label",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"deviceId",void 0),(0,o.__decorate)([(0,n.MZ)({type:Object})],b.prototype,"value",void 0),(0,o.__decorate)([(0,n.wk)()],b.prototype,"_automations",void 0),(0,o.__decorate)([(0,n.wk)()],b.prototype,"_renderEmpty",void 0),(0,o.__decorate)([(0,n.wk)(),(0,r.Fg)({context:l.ih,subscribe:!0})],b.prototype,"_entityReg",void 0)},95710:function(e,t,i){var o=i(69868),r=i(84922),a=i(11991),n=i(65940),s=i(73120),l=i(22441),c=i(44537),d=i(92830);const u=(e,t)=>{const i=e.area_id,o=i?t.areas[i]:void 0,r=o?.floor_id;return{device:e,area:o||null,floor:(r?t.floors[r]:void 0)||null}};var p=i(88120),h=i(6041),m=i(28027),y=i(45363);i(94966);class _ extends r.WF{firstUpdated(e){super.firstUpdated(e),this._loadConfigEntries()}async _loadConfigEntries(){const e=await(0,p.VN)(this.hass);this._configEntryLookup=Object.fromEntries(e.map((e=>[e.entry_id,e])))}render(){const e=this.placeholder??this.hass.localize("ui.components.device-picker.placeholder"),t=this.hass.localize("ui.components.device-picker.no_match"),i=this._valueRenderer(this._configEntryLookup);return r.qy`
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
    `}async open(){await this.updateComplete,await(this._picker?.open())}_valueChanged(e){e.stopPropagation();const t=e.detail.value;this.value=t,(0,s.r)(this,"value-changed",{value:t})}constructor(...e){super(...e),this.autofocus=!1,this.disabled=!1,this.required=!1,this.hideClearIcon=!1,this._configEntryLookup={},this._getItems=()=>this._getDevices(this.hass.devices,this.hass.entities,this._configEntryLookup,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeDevices),this._getDevices=(0,n.A)(((e,t,i,o,r,a,n,s,p)=>{const y=Object.values(e),_=Object.values(t);let f={};(o||r||a||s)&&(f=(0,h.g2)(_));let g=y.filter((e=>e.id===this.value||!e.disabled_by));o&&(g=g.filter((e=>{const t=f[e.id];return!(!t||!t.length)&&f[e.id].some((e=>o.includes((0,d.m)(e.entity_id))))}))),r&&(g=g.filter((e=>{const t=f[e.id];return!t||!t.length||_.every((e=>!r.includes((0,d.m)(e.entity_id))))}))),p&&(g=g.filter((e=>!p.includes(e.id)))),a&&(g=g.filter((e=>{const t=f[e.id];return!(!t||!t.length)&&f[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&a.includes(t.attributes.device_class))}))}))),s&&(g=g.filter((e=>{const t=f[e.id];return!(!t||!t.length)&&t.some((e=>{const t=this.hass.states[e.entity_id];return!!t&&s(t)}))}))),n&&(g=g.filter((e=>e.id===this.value||n(e))));return g.map((e=>{const t=(0,c.T)(e,this.hass,f[e.id]),{area:o}=u(e,this.hass),r=o?(0,l.A)(o):void 0,a=e.primary_config_entry?i?.[e.primary_config_entry]:void 0,n=a?.domain,s=n?(0,m.p$)(this.hass.localize,n):void 0;return{id:e.id,label:"",primary:t||this.hass.localize("ui.components.device-picker.unnamed_device"),secondary:r,domain:a?.domain,domain_name:s,search_labels:[t,r,n,s].filter(Boolean),sorting_label:t||"zzz"}}))})),this._valueRenderer=(0,n.A)((e=>t=>{const i=t,o=this.hass.devices[i];if(!o)return r.qy`<span slot="headline">${i}</span>`;const{area:a}=u(o,this.hass),n=o?(0,c.xn)(o):void 0,s=a?(0,l.A)(a):void 0,d=o.primary_config_entry?e[o.primary_config_entry]:void 0;return r.qy`
        ${d?r.qy`<img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${(0,y.MR)({domain:d.domain,type:"icon",darkOptimized:this.hass.themes?.darkMode})}
            />`:r.s6}
        <span slot="headline">${n}</span>
        <span slot="supporting-text">${s}</span>
      `})),this._rowRenderer=e=>r.qy`
    <ha-combo-box-item type="button">
      ${e.domain?r.qy`
            <img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${(0,y.MR)({domain:e.domain,type:"icon",darkOptimized:this.hass.themes.darkMode})}
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
  `}}(0,o.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],_.prototype,"autofocus",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],_.prototype,"disabled",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],_.prototype,"required",void 0),(0,o.__decorate)([(0,a.MZ)()],_.prototype,"label",void 0),(0,o.__decorate)([(0,a.MZ)()],_.prototype,"value",void 0),(0,o.__decorate)([(0,a.MZ)()],_.prototype,"helper",void 0),(0,o.__decorate)([(0,a.MZ)()],_.prototype,"placeholder",void 0),(0,o.__decorate)([(0,a.MZ)({type:String,attribute:"search-label"})],_.prototype,"searchLabel",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1,type:Array})],_.prototype,"createDomains",void 0),(0,o.__decorate)([(0,a.MZ)({type:Array,attribute:"include-domains"})],_.prototype,"includeDomains",void 0),(0,o.__decorate)([(0,a.MZ)({type:Array,attribute:"exclude-domains"})],_.prototype,"excludeDomains",void 0),(0,o.__decorate)([(0,a.MZ)({type:Array,attribute:"include-device-classes"})],_.prototype,"includeDeviceClasses",void 0),(0,o.__decorate)([(0,a.MZ)({type:Array,attribute:"exclude-devices"})],_.prototype,"excludeDevices",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"deviceFilter",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"entityFilter",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:"hide-clear-icon",type:Boolean})],_.prototype,"hideClearIcon",void 0),(0,o.__decorate)([(0,a.P)("ha-generic-picker")],_.prototype,"_picker",void 0),(0,o.__decorate)([(0,a.wk)()],_.prototype,"_configEntryLookup",void 0),_=(0,o.__decorate)([(0,a.EM)("ha-device-picker")],_)},57447:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(69868),r=i(84922),a=i(11991),n=i(65940),s=i(73120),l=i(92830),c=i(47379),d=i(41602),u=i(98137),p=i(28027),h=i(5940),m=i(80608),y=(i(36137),i(94966),i(95635),i(23114)),_=e([y]);y=(_.then?(await _)():_)[0];const f="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",g="M11,13.5V21.5H3V13.5H11M12,2L17.5,11H6.5L12,2M17.5,13C20,13 22,15 22,17.5C22,20 20,22 17.5,22C15,22 13,20 13,17.5C13,15 15,13 17.5,13Z",v="___create-new-entity___";class b extends r.WF{firstUpdated(e){super.firstUpdated(e),this.hass.loadBackendTranslation("title")}get _showEntityId(){return this.showEntityId||this.hass.userData?.showEntityIdPicker}render(){const e=this.placeholder??this.hass.localize("ui.components.entity.entity-picker.placeholder"),t=this.hass.localize("ui.components.entity.entity-picker.no_match");return r.qy`
      <ha-generic-picker
        .hass=${this.hass}
        .disabled=${this.disabled}
        .autofocus=${this.autofocus}
        .allowCustomValue=${this.allowCustomEntity}
        .label=${this.label}
        .helper=${this.helper}
        .searchLabel=${this.searchLabel}
        .notFoundLabel=${t}
        .placeholder=${e}
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
    `}async open(){await this.updateComplete,await(this._picker?.open())}_valueChanged(e){e.stopPropagation();const t=e.detail.value;if(t)if(t.startsWith(v)){const e=t.substring(v.length);(0,m.$)(this,{domain:e,dialogClosedCallback:e=>{e.entityId&&this._setValue(e.entityId)}})}else(0,d.n)(t)&&this._setValue(t);else this._setValue(void 0)}_setValue(e){this.value=e,(0,s.r)(this,"value-changed",{value:e}),(0,s.r)(this,"change")}constructor(...e){super(...e),this.autofocus=!1,this.disabled=!1,this.required=!1,this.showEntityId=!1,this.hideClearIcon=!1,this._valueRenderer=e=>{const t=e||"",i=this.hass.states[t];if(!i)return r.qy`
        <ha-svg-icon
          slot="start"
          .path=${g}
          style="margin: 0 4px"
        ></ha-svg-icon>
        <span slot="headline">${t}</span>
      `;const o=this.hass.formatEntityName(i,"entity"),a=this.hass.formatEntityName(i,"device"),n=this.hass.formatEntityName(i,"area"),s=(0,u.qC)(this.hass),l=o||a||t,c=[n,o?a:void 0].filter(Boolean).join(s?" ◂ ":" ▸ ");return r.qy`
      <state-badge
        .hass=${this.hass}
        .stateObj=${i}
        slot="start"
      ></state-badge>
      <span slot="headline">${l}</span>
      <span slot="supporting-text">${c}</span>
    `},this._rowRenderer=(e,{index:t})=>{const i=this._showEntityId;return r.qy`
      <ha-combo-box-item type="button" compact .borderTop=${0!==t}>
        ${e.icon_path?r.qy`
              <ha-svg-icon
                slot="start"
                style="margin: 0 4px"
                .path=${e.icon_path}
              ></ha-svg-icon>
            `:r.qy`
              <state-badge
                slot="start"
                .stateObj=${e.stateObj}
                .hass=${this.hass}
              ></state-badge>
            `}
        <span slot="headline">${e.primary}</span>
        ${e.secondary?r.qy`<span slot="supporting-text">${e.secondary}</span>`:r.s6}
        ${e.stateObj&&i?r.qy`
              <span slot="supporting-text" class="code">
                ${e.stateObj.entity_id}
              </span>
            `:r.s6}
        ${e.domain_name&&!i?r.qy`
              <div slot="trailing-supporting-text" class="domain">
                ${e.domain_name}
              </div>
            `:r.s6}
      </ha-combo-box-item>
    `},this._getAdditionalItems=()=>this._getCreateItems(this.hass.localize,this.createDomains),this._getCreateItems=(0,n.A)(((e,t)=>t?.length?t.map((t=>{const i=e("ui.components.entity.entity-picker.create_helper",{domain:(0,h.z)(t)?e(`ui.panel.config.helpers.types.${t}`):(0,p.p$)(e,t)});return{id:v+t,primary:i,secondary:e("ui.components.entity.entity-picker.new_entity"),icon_path:f}})):[])),this._getItems=()=>this._getEntities(this.hass,this.includeDomains,this.excludeDomains,this.entityFilter,this.includeDeviceClasses,this.includeUnitOfMeasurement,this.includeEntities,this.excludeEntities),this._getEntities=(0,n.A)(((e,t,i,o,r,a,n,s)=>{let d=[],h=Object.keys(e.states);n&&(h=h.filter((e=>n.includes(e)))),s&&(h=h.filter((e=>!s.includes(e)))),t&&(h=h.filter((e=>t.includes((0,l.m)(e))))),i&&(h=h.filter((e=>!i.includes((0,l.m)(e)))));const m=(0,u.qC)(this.hass);return d=h.map((t=>{const i=e.states[t],o=(0,c.u)(i),r=this.hass.formatEntityName(i,"entity"),a=this.hass.formatEntityName(i,"device"),n=this.hass.formatEntityName(i,"area"),s=(0,p.p$)(this.hass.localize,(0,l.m)(t)),d=r||a||t,u=[n,r?a:void 0].filter(Boolean).join(m?" ◂ ":" ▸ "),h=[a,r].filter(Boolean).join(" - ");return{id:t,primary:d,secondary:u,domain_name:s,sorting_label:[a,r].filter(Boolean).join("_"),search_labels:[r,a,n,s,o,t].filter(Boolean),a11y_label:h,stateObj:i}})),r&&(d=d.filter((e=>e.id===this.value||e.stateObj?.attributes.device_class&&r.includes(e.stateObj.attributes.device_class)))),a&&(d=d.filter((e=>e.id===this.value||e.stateObj?.attributes.unit_of_measurement&&a.includes(e.stateObj.attributes.unit_of_measurement)))),o&&(d=d.filter((e=>e.id===this.value||e.stateObj&&o(e.stateObj)))),d})),this._searchFn=(e,t)=>{const i=t.findIndex((t=>t.stateObj?.entity_id===e));if(-1===i)return t;const[o]=t.splice(i,1);return t.unshift(o),t}}}(0,o.__decorate)([(0,a.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],b.prototype,"autofocus",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],b.prototype,"disabled",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],b.prototype,"required",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,attribute:"allow-custom-entity"})],b.prototype,"allowCustomEntity",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,attribute:"show-entity-id"})],b.prototype,"showEntityId",void 0),(0,o.__decorate)([(0,a.MZ)()],b.prototype,"label",void 0),(0,o.__decorate)([(0,a.MZ)()],b.prototype,"value",void 0),(0,o.__decorate)([(0,a.MZ)()],b.prototype,"helper",void 0),(0,o.__decorate)([(0,a.MZ)()],b.prototype,"placeholder",void 0),(0,o.__decorate)([(0,a.MZ)({type:String,attribute:"search-label"})],b.prototype,"searchLabel",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1,type:Array})],b.prototype,"createDomains",void 0),(0,o.__decorate)([(0,a.MZ)({type:Array,attribute:"include-domains"})],b.prototype,"includeDomains",void 0),(0,o.__decorate)([(0,a.MZ)({type:Array,attribute:"exclude-domains"})],b.prototype,"excludeDomains",void 0),(0,o.__decorate)([(0,a.MZ)({type:Array,attribute:"include-device-classes"})],b.prototype,"includeDeviceClasses",void 0),(0,o.__decorate)([(0,a.MZ)({type:Array,attribute:"include-unit-of-measurement"})],b.prototype,"includeUnitOfMeasurement",void 0),(0,o.__decorate)([(0,a.MZ)({type:Array,attribute:"include-entities"})],b.prototype,"includeEntities",void 0),(0,o.__decorate)([(0,a.MZ)({type:Array,attribute:"exclude-entities"})],b.prototype,"excludeEntities",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],b.prototype,"entityFilter",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:"hide-clear-icon",type:Boolean})],b.prototype,"hideClearIcon",void 0),(0,o.__decorate)([(0,a.P)("ha-generic-picker")],b.prototype,"_picker",void 0),b=(0,o.__decorate)([(0,a.EM)("ha-entity-picker")],b),t()}catch(f){t(f)}}))},29897:function(e,t,i){var o=i(69868),r=i(84922),a=i(11991),n=i(73120);i(93672);class s extends r.WF{render(){return r.qy`
      <div
        class="row"
        tabindex="0"
        role="button"
        @keydown=${this._handleKeydown}
      >
        ${this.leftChevron?r.qy`
              <ha-icon-button
                class="expand-button"
                .path=${"M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z"}
                @click=${this._handleExpand}
                @keydown=${this._handleExpand}
              ></ha-icon-button>
            `:r.s6}
        <div class="leading-icon-wrapper">
          <slot name="leading-icon"></slot>
        </div>
        <slot class="header" name="header"></slot>
        <slot name="icons"></slot>
      </div>
    `}async _handleExpand(e){e.defaultPrevented||"keydown"===e.type&&"Enter"!==e.key&&" "!==e.key||(e.stopPropagation(),e.preventDefault(),(0,n.r)(this,"toggle-collapsed"))}async _handleKeydown(e){if(!(e.defaultPrevented||"Enter"!==e.key&&" "!==e.key&&(!this.sortSelected&&!e.altKey||e.ctrlKey||e.metaKey||e.shiftKey||"ArrowUp"!==e.key&&"ArrowDown"!==e.key))){if(e.preventDefault(),e.stopPropagation(),"ArrowUp"===e.key||"ArrowDown"===e.key)return"ArrowUp"===e.key?void(0,n.r)(this,"move-up"):void(0,n.r)(this,"move-down");!this.sortSelected||"Enter"!==e.key&&" "!==e.key?this.click():(0,n.r)(this,"stop-sort-selection")}}focus(){requestAnimationFrame((()=>{this._rowElement?.focus()}))}constructor(...e){super(...e),this.leftChevron=!1,this.collapsed=!1,this.selected=!1,this.sortSelected=!1,this.disabled=!1,this.buildingBlock=!1}}s.styles=r.AH`
    :host {
      display: block;
    }
    .row {
      display: flex;
      padding: 0 8px;
      min-height: 48px;
      align-items: center;
      cursor: pointer;
      overflow: hidden;
      font-weight: var(--ha-font-weight-medium);
      outline: none;
      border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg));
    }
    .row:focus {
      outline: var(--wa-focus-ring);
      outline-offset: -2px;
    }
    .expand-button {
      transition: transform 150ms cubic-bezier(0.4, 0, 0.2, 1);
      color: var(--ha-color-on-neutral-quiet);
      margin-left: -8px;
    }
    :host([building-block]) .leading-icon-wrapper {
      background-color: var(--ha-color-fill-neutral-loud-resting);
      border-radius: var(--ha-border-radius-md);
      padding: 4px;
      display: flex;
      justify-content: center;
      align-items: center;
      transform: rotate(45deg);
    }
    ::slotted([slot="leading-icon"]) {
      color: var(--ha-color-on-neutral-quiet);
    }
    :host([building-block]) ::slotted([slot="leading-icon"]) {
      --mdc-icon-size: 20px;
      color: var(--white-color);
      transform: rotate(-45deg);
    }
    :host([collapsed]) .expand-button {
      transform: rotate(180deg);
    }
    :host([selected]) .row,
    :host([selected]) .row:focus {
      outline: solid;
      outline-color: var(--primary-color);
      outline-offset: -2px;
      outline-width: 2px;
    }
    :host([disabled]) .row {
      border-top-right-radius: var(--ha-border-radius-square);
      border-top-left-radius: var(--ha-border-radius-square);
    }
    ::slotted([slot="header"]) {
      flex: 1;
      overflow-wrap: anywhere;
      margin: 0 12px;
    }
    :host([sort-selected]) .row {
      outline: solid;
      outline-color: rgba(var(--rgb-accent-color), 0.6);
      outline-offset: -2px;
      outline-width: 2px;
      background-color: rgba(var(--rgb-accent-color), 0.08);
    }
    .row:hover {
      background-color: rgba(var(--rgb-primary-text-color), 0.04);
    }
    :host([highlight]) .row {
      background-color: rgba(var(--rgb-primary-color), 0.08);
    }
    :host([highlight]) .row:hover {
      background-color: rgba(var(--rgb-primary-color), 0.16);
    }
  `,(0,o.__decorate)([(0,a.MZ)({attribute:"left-chevron",type:Boolean})],s.prototype,"leftChevron",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,reflect:!0})],s.prototype,"collapsed",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,reflect:!0})],s.prototype,"selected",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,reflect:!0,attribute:"sort-selected"})],s.prototype,"sortSelected",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,reflect:!0})],s.prototype,"disabled",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,reflect:!0,attribute:"building-block"})],s.prototype,"buildingBlock",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,reflect:!0})],s.prototype,"highlight",void 0),(0,o.__decorate)([(0,a.P)(".row")],s.prototype,"_rowElement",void 0),s=(0,o.__decorate)([(0,a.EM)("ha-automation-row")],s)},17711:function(e,t,i){var o=i(69868),r=i(84922),a=i(11991),n=i(90933);i(9974),i(95968);class s extends r.WF{get items(){return this._menu?.items}get selected(){return this._menu?.selected}focus(){this._menu?.open?this._menu.focusItemAtIndex(0):this._triggerButton?.focus()}render(){return r.qy`
      <div @click=${this._handleClick}>
        <slot name="trigger" @slotchange=${this._setTriggerAria}></slot>
      </div>
      <ha-menu
        .corner=${this.corner}
        .menuCorner=${this.menuCorner}
        .fixed=${this.fixed}
        .multi=${this.multi}
        .activatable=${this.activatable}
        .y=${this.y}
        .x=${this.x}
      >
        <slot></slot>
      </ha-menu>
    `}firstUpdated(e){super.firstUpdated(e),"rtl"===n.G.document.dir&&this.updateComplete.then((()=>{this.querySelectorAll("ha-list-item").forEach((e=>{const t=document.createElement("style");t.innerHTML="span.material-icons:first-of-type { margin-left: var(--mdc-list-item-graphic-margin, 32px) !important; margin-right: 0px !important;}",e.shadowRoot.appendChild(t)}))}))}_handleClick(){this.disabled||(this._menu.anchor=this.noAnchor?null:this,this._menu.show())}get _triggerButton(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"]')}_setTriggerAria(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}constructor(...e){super(...e),this.corner="BOTTOM_START",this.menuCorner="START",this.x=null,this.y=null,this.multi=!1,this.activatable=!1,this.disabled=!1,this.fixed=!1,this.noAnchor=!1}}s.styles=r.AH`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `,(0,o.__decorate)([(0,a.MZ)()],s.prototype,"corner",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:"menu-corner"})],s.prototype,"menuCorner",void 0),(0,o.__decorate)([(0,a.MZ)({type:Number})],s.prototype,"x",void 0),(0,o.__decorate)([(0,a.MZ)({type:Number})],s.prototype,"y",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],s.prototype,"multi",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],s.prototype,"activatable",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],s.prototype,"disabled",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],s.prototype,"fixed",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,attribute:"no-anchor"})],s.prototype,"noAnchor",void 0),(0,o.__decorate)([(0,a.P)("ha-menu",!0)],s.prototype,"_menu",void 0),s=(0,o.__decorate)([(0,a.EM)("ha-button-menu")],s)},75518:function(e,t,i){var o=i(69868),r=i(84922),a=i(11991),n=i(21431),s=i(73120);i(23749),i(57674);const l={boolean:()=>i.e("2436").then(i.bind(i,33999)),constant:()=>i.e("3668").then(i.bind(i,33855)),float:()=>i.e("742").then(i.bind(i,84053)),grid:()=>i.e("7828").then(i.bind(i,57311)),expandable:()=>i.e("364").then(i.bind(i,51079)),integer:()=>i.e("7346").then(i.bind(i,40681)),multi_select:()=>Promise.all([i.e("6216"),i.e("3706")]).then(i.bind(i,99681)),positive_time_period_dict:()=>i.e("3540").then(i.bind(i,87551)),select:()=>i.e("2500").then(i.bind(i,10079)),string:()=>i.e("3627").then(i.bind(i,10070)),optional_actions:()=>i.e("3044").then(i.bind(i,96943))},c=(e,t)=>e?!t.name||t.flatten?e:e[t.name]:null;class d extends r.WF{getFormProperties(){return{}}async focus(){await this.updateComplete;const e=this.renderRoot.querySelector(".root");if(e)for(const t of e.children)if("HA-ALERT"!==t.tagName){t instanceof r.mN&&await t.updateComplete,t.focus();break}}willUpdate(e){e.has("schema")&&this.schema&&this.schema.forEach((e=>{"selector"in e||l[e.type]?.()}))}render(){return r.qy`
      <div class="root" part="root">
        ${this.error&&this.error.base?r.qy`
              <ha-alert alert-type="error">
                ${this._computeError(this.error.base,this.schema)}
              </ha-alert>
            `:""}
        ${this.schema.map((e=>{const t=((e,t)=>e&&t.name?e[t.name]:null)(this.error,e),i=((e,t)=>e&&t.name?e[t.name]:null)(this.warning,e);return r.qy`
            ${t?r.qy`
                  <ha-alert own-margin alert-type="error">
                    ${this._computeError(t,e)}
                  </ha-alert>
                `:i?r.qy`
                    <ha-alert own-margin alert-type="warning">
                      ${this._computeWarning(i,e)}
                    </ha-alert>
                  `:""}
            ${"selector"in e?r.qy`<ha-selector
                  .schema=${e}
                  .hass=${this.hass}
                  .narrow=${this.narrow}
                  .name=${e.name}
                  .selector=${e.selector}
                  .value=${c(this.data,e)}
                  .label=${this._computeLabel(e,this.data)}
                  .disabled=${e.disabled||this.disabled||!1}
                  .placeholder=${e.required?"":e.default}
                  .helper=${this._computeHelper(e)}
                  .localizeValue=${this.localizeValue}
                  .required=${e.required||!1}
                  .context=${this._generateContext(e)}
                ></ha-selector>`:(0,n._)(this.fieldElementName(e.type),{schema:e,data:c(this.data,e),label:this._computeLabel(e,this.data),helper:this._computeHelper(e),disabled:this.disabled||e.disabled||!1,hass:this.hass,localize:this.hass?.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(e),...this.getFormProperties()})}
          `}))}
      </div>
    `}fieldElementName(e){return`ha-form-${e}`}_generateContext(e){if(!e.context)return;const t={};for(const[i,o]of Object.entries(e.context))t[i]=this.data[o];return t}createRenderRoot(){const e=super.createRenderRoot();return this.addValueChangedListener(e),e}addValueChangedListener(e){e.addEventListener("value-changed",(e=>{e.stopPropagation();const t=e.target.schema;if(e.target===this)return;const i=!t.name||"flatten"in t&&t.flatten?e.detail.value:{[t.name]:e.detail.value};this.data={...this.data,...i},(0,s.r)(this,"value-changed",{value:this.data})}))}_computeLabel(e,t){return this.computeLabel?this.computeLabel(e,t):e?e.name:""}_computeHelper(e){return this.computeHelper?this.computeHelper(e):""}_computeError(e,t){return Array.isArray(e)?r.qy`<ul>
        ${e.map((e=>r.qy`<li>
              ${this.computeError?this.computeError(e,t):e}
            </li>`))}
      </ul>`:this.computeError?this.computeError(e,t):e}_computeWarning(e,t){return this.computeWarning?this.computeWarning(e,t):e}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1}}d.styles=r.AH`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `,(0,o.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],d.prototype,"narrow",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"data",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"schema",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"error",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"warning",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],d.prototype,"disabled",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"computeError",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"computeWarning",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"computeLabel",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"computeHelper",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],d.prototype,"localizeValue",void 0),d=(0,o.__decorate)([(0,a.EM)("ha-form")],d)},61647:function(e,t,i){var o=i(69868),r=i(84922),a=i(11991),n=i(73120),s=(i(9974),i(5673)),l=i(89591),c=i(18396);class d extends s.W1{connectedCallback(){super.connectedCallback(),this.addEventListener("close-menu",this._handleCloseMenu)}_handleCloseMenu(e){e.detail.reason.kind===c.fi.KEYDOWN&&e.detail.reason.key===c.NV.ESCAPE||e.detail.initiator.clickAction?.(e.detail.initiator)}}d.styles=[l.R,r.AH`
      :host {
        --md-sys-color-surface-container: var(--card-background-color);
      }
    `],d=(0,o.__decorate)([(0,a.EM)("ha-md-menu")],d);class u extends r.WF{get items(){return this._menu.items}focus(){this._menu.open?this._menu.focus():this._triggerButton?.focus()}render(){return r.qy`
      <div @click=${this._handleClick}>
        <slot name="trigger" @slotchange=${this._setTriggerAria}></slot>
      </div>
      <ha-md-menu
        .quick=${this.quick}
        .positioning=${this.positioning}
        .hasOverflow=${this.hasOverflow}
        .anchorCorner=${this.anchorCorner}
        .menuCorner=${this.menuCorner}
        @opening=${this._handleOpening}
        @closing=${this._handleClosing}
      >
        <slot></slot>
      </ha-md-menu>
    `}_handleOpening(){(0,n.r)(this,"opening",void 0,{composed:!1})}_handleClosing(){(0,n.r)(this,"closing",void 0,{composed:!1})}_handleClick(){this.disabled||(this._menu.anchorElement=this,this._menu.open?this._menu.close():this._menu.show())}get _triggerButton(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"], ha-assist-chip[slot="trigger"]')}_setTriggerAria(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}constructor(...e){super(...e),this.disabled=!1,this.anchorCorner="end-start",this.menuCorner="start-start",this.hasOverflow=!1,this.quick=!1}}u.styles=r.AH`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `,(0,o.__decorate)([(0,a.MZ)({type:Boolean})],u.prototype,"disabled",void 0),(0,o.__decorate)([(0,a.MZ)()],u.prototype,"positioning",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:"anchor-corner"})],u.prototype,"anchorCorner",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:"menu-corner"})],u.prototype,"menuCorner",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,attribute:"has-overflow"})],u.prototype,"hasOverflow",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],u.prototype,"quick",void 0),(0,o.__decorate)([(0,a.P)("ha-md-menu",!0)],u.prototype,"_menu",void 0),u=(0,o.__decorate)([(0,a.EM)("ha-md-button-menu")],u)},90666:function(e,t,i){var o=i(69868),r=i(61320),a=i(41715),n=i(84922),s=i(11991);class l extends r.c{}l.styles=[a.R,n.AH`
      :host {
        --md-divider-color: var(--divider-color);
      }
    `],l=(0,o.__decorate)([(0,s.EM)("ha-md-divider")],l)},70154:function(e,t,i){var o=i(69868),r=i(45369),a=i(20808),n=i(84922),s=i(11991);class l extends r.K{}l.styles=[a.R,n.AH`
      :host {
        --ha-icon-display: block;
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-on-primary: var(--primary-text-color);
        --md-sys-color-secondary: var(--secondary-text-color);
        --md-sys-color-surface: var(--card-background-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-sys-color-on-surface-variant: var(--secondary-text-color);
        --md-sys-color-secondary-container: rgba(
          var(--rgb-primary-color),
          0.15
        );
        --md-sys-color-on-secondary-container: var(--text-primary-color);
        --mdc-icon-size: 16px;

        --md-sys-color-on-primary-container: var(--primary-text-color);
        --md-sys-color-on-secondary-container: var(--primary-text-color);
        --md-menu-item-label-text-font: Roboto, sans-serif;
      }
      :host(.warning) {
        --md-menu-item-label-text-color: var(--error-color);
        --md-menu-item-leading-icon-color: var(--error-color);
      }
      ::slotted([slot="headline"]) {
        text-wrap: nowrap;
      }
    `],(0,o.__decorate)([(0,s.MZ)({attribute:!1})],l.prototype,"clickAction",void 0),l=(0,o.__decorate)([(0,s.EM)("ha-md-menu-item")],l)},79080:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(69868),r=i(90227),a=i(84922),n=i(11991),s=i(73120),l=i(83566),c=i(84810),d=i(72698),u=i(5503),p=i(76943),h=(i(23749),e([c,p]));[c,p]=h.then?(await h)():h;const m=e=>{if("object"!=typeof e||null===e)return!1;for(const t in e)if(Object.prototype.hasOwnProperty.call(e,t))return!1;return!0};class y extends a.WF{setValue(e){try{this._yaml=m(e)?"":(0,r.Bh)(e,{schema:this.yamlSchema,quotingType:'"',noRefs:!0})}catch(t){console.error(t,e),alert(`There was an error converting to YAML: ${t}`)}}firstUpdated(){void 0!==this.defaultValue&&this.setValue(this.defaultValue)}willUpdate(e){super.willUpdate(e),this.autoUpdate&&e.has("value")&&this.setValue(this.value)}focus(){this._codeEditor?.codemirror&&this._codeEditor?.codemirror.focus()}render(){return void 0===this._yaml?a.s6:a.qy`
      ${this.label?a.qy`<p>${this.label}${this.required?" *":""}</p>`:a.s6}
      <ha-code-editor
        .hass=${this.hass}
        .value=${this._yaml}
        .readOnly=${this.readOnly}
        .disableFullscreen=${this.disableFullscreen}
        mode="yaml"
        autocomplete-entities
        autocomplete-icons
        .error=${!1===this.isValid}
        @value-changed=${this._onChange}
        @blur=${this._onBlur}
        dir="ltr"
      ></ha-code-editor>
      ${this._showingError?a.qy`<ha-alert alert-type="error">${this._error}</ha-alert>`:a.s6}
      ${this.copyClipboard||this.hasExtraActions?a.qy`
            <div class="card-actions">
              ${this.copyClipboard?a.qy`
                    <ha-button appearance="plain" @click=${this._copyYaml}>
                      ${this.hass.localize("ui.components.yaml-editor.copy_to_clipboard")}
                    </ha-button>
                  `:a.s6}
              <slot name="extra-actions"></slot>
            </div>
          `:a.s6}
    `}_onChange(e){let t;e.stopPropagation(),this._yaml=e.detail.value;let i,o=!0;if(this._yaml)try{t=(0,r.Hh)(this._yaml,{schema:this.yamlSchema})}catch(a){o=!1,i=`${this.hass.localize("ui.components.yaml-editor.error",{reason:a.reason})}${a.mark?` (${this.hass.localize("ui.components.yaml-editor.error_location",{line:a.mark.line+1,column:a.mark.column+1})})`:""}`}else t={};this._error=i??"",o&&(this._showingError=!1),this.value=t,this.isValid=o,(0,s.r)(this,"value-changed",{value:t,isValid:o,errorMsg:i})}_onBlur(){this.showErrors&&this._error&&(this._showingError=!0)}get yaml(){return this._yaml}async _copyYaml(){this.yaml&&(await(0,u.l)(this.yaml),(0,d.P)(this,{message:this.hass.localize("ui.common.copied_clipboard")}))}static get styles(){return[l.RF,a.AH`
        .card-actions {
          border-radius: var(
            --actions-border-radius,
            0px 0px var(--ha-card-border-radius, 12px)
              var(--ha-card-border-radius, 12px)
          );
          border: 1px solid var(--divider-color);
          padding: 5px 16px;
        }
        ha-code-editor {
          flex-grow: 1;
          min-height: 0;
        }
      `]}constructor(...e){super(...e),this.yamlSchema=r.my,this.isValid=!0,this.autoUpdate=!1,this.readOnly=!1,this.disableFullscreen=!1,this.required=!1,this.copyClipboard=!1,this.hasExtraActions=!1,this.showErrors=!0,this._yaml="",this._error="",this._showingError=!1}}(0,o.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)()],y.prototype,"value",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"yamlSchema",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"defaultValue",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"is-valid",type:Boolean})],y.prototype,"isValid",void 0),(0,o.__decorate)([(0,n.MZ)()],y.prototype,"label",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"auto-update",type:Boolean})],y.prototype,"autoUpdate",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"read-only",type:Boolean})],y.prototype,"readOnly",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,attribute:"disable-fullscreen"})],y.prototype,"disableFullscreen",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],y.prototype,"required",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"copy-clipboard",type:Boolean})],y.prototype,"copyClipboard",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"has-extra-actions",type:Boolean})],y.prototype,"hasExtraActions",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"show-errors",type:Boolean})],y.prototype,"showErrors",void 0),(0,o.__decorate)([(0,n.wk)()],y.prototype,"_yaml",void 0),(0,o.__decorate)([(0,n.wk)()],y.prototype,"_error",void 0),(0,o.__decorate)([(0,n.wk)()],y.prototype,"_showingError",void 0),(0,o.__decorate)([(0,n.P)("ha-code-editor")],y.prototype,"_codeEditor",void 0),y=(0,o.__decorate)([(0,n.EM)("ha-yaml-editor")],y),t()}catch(m){t(m)}}))},70614:function(e,t,i){i.d(t,{Dp:()=>d,G3:()=>c,S9:()=>u,XF:()=>a,aI:()=>s,fo:()=>l,vO:()=>n});var o=i(26846),r=(i(68985),i(51663),i(32588));i(17866);const a=e=>{if("condition"in e&&Array.isArray(e.condition))return{condition:"and",conditions:e.condition};for(const t of r.I8)if(t in e)return{condition:t,conditions:e[t]};return e};const n=e=>e?Array.isArray(e)?e.map(n):("triggers"in e&&e.triggers&&(e.triggers=n(e.triggers)),"platform"in e&&("trigger"in e||(e.trigger=e.platform),delete e.platform),e):e,s=e=>{if(!e)return[];const t=[];return(0,o.e)(e).forEach((e=>{"triggers"in e?e.triggers&&t.push(...s(e.triggers)):t.push(e)})),t},l=e=>{if(!e||"object"!=typeof e)return!1;const t=e;return"trigger"in t&&"string"==typeof t.trigger||"platform"in t&&"string"==typeof t.platform},c=e=>{if(!e||"object"!=typeof e)return!1;return"condition"in e&&"string"==typeof e.condition},d=(e,t,i,o)=>e.connection.subscribeMessage(t,{type:"subscribe_trigger",trigger:i,variables:o}),u=(e,t,i)=>e.callWS({type:"test_condition",condition:t,variables:i})},10101:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{g:()=>b,p:()=>A});var r=i(26846),a=i(52744),n=i(48505),s=i(15216),l=i(27881),c=i(47379),d=i(41602),u=i(72106),p=i(7657),h=i(3949),m=i(71767),y=e([n,a,l,u]);[n,a,l,u]=y.then?(await y)():y;const _="ui.panel.config.automation.editor.triggers.type",f="ui.panel.config.automation.editor.conditions.type",g=(e,t)=>{let i;return i="number"==typeof t?(0,s.A)(t):"string"==typeof t?t:(0,a.nR)(e,t),i},v=(e,t,i)=>{const o=e.split(":");if(o.length<2||o.length>3)return e;try{const r=new Date("1970-01-01T"+e);return 2===o.length||0===Number(o[2])?(0,n.fU)(r,t,i):(0,n.ie)(r,t,i)}catch{return e}},b=(e,t,i,o=!1)=>{try{const r=w(e,t,i,o);if("string"!=typeof r)throw new Error(String(r));return r}catch(r){console.error(r);let e="Error in describing trigger";return r.message&&(e+=": "+r.message),e}},w=(e,t,i,o=!1)=>{if((0,h.H4)(e)){const i=(0,r.e)(e.triggers);if(!i||0===i.length)return t.localize(`${_}.list.description.no_trigger`);const o=i.length;return t.localize(`${_}.list.description.full`,{count:o})}if(e.alias&&!o)return e.alias;if("event"===e.trigger&&e.event_type){const i=[];if(Array.isArray(e.event_type))for(const t of e.event_type.values())i.push(t);else i.push(e.event_type);const o=(0,u.q)(t.locale,i);return t.localize(`${_}.event.description.full`,{eventTypes:o})}if("homeassistant"===e.trigger&&e.event)return t.localize("start"===e.event?`${_}.homeassistant.description.started`:`${_}.homeassistant.description.shutdown`);if("numeric_state"===e.trigger&&e.entity_id){const i=[],o=t.states,r=Array.isArray(e.entity_id)?t.states[e.entity_id[0]]:t.states[e.entity_id];if(Array.isArray(e.entity_id))for(const t of e.entity_id.values())o[t]&&i.push((0,c.u)(o[t])||t);else e.entity_id&&i.push(o[e.entity_id]?(0,c.u)(o[e.entity_id]):e.entity_id);const a=e.attribute?r?(0,l.R)(t.localize,r,t.entities,e.attribute):e.attribute:void 0,n=e.for?g(t.locale,e.for):void 0;if(void 0!==e.above&&void 0!==e.below)return t.localize(`${_}.numeric_state.description.above-below`,{attribute:a,entity:(0,u.q)(t.locale,i),numberOfEntities:i.length,above:e.above,below:e.below,duration:n});if(void 0!==e.above)return t.localize(`${_}.numeric_state.description.above`,{attribute:a,entity:(0,u.q)(t.locale,i),numberOfEntities:i.length,above:e.above,duration:n});if(void 0!==e.below)return t.localize(`${_}.numeric_state.description.below`,{attribute:a,entity:(0,u.q)(t.locale,i),numberOfEntities:i.length,below:e.below,duration:n})}if("state"===e.trigger){const i=[],o=t.states;let a="";if(e.attribute){const i=Array.isArray(e.entity_id)?t.states[e.entity_id[0]]:t.states[e.entity_id];a=i?(0,l.R)(t.localize,i,t.entities,e.attribute):e.attribute}const n=(0,r.e)(e.entity_id);if(n)for(const e of n)o[e]&&i.push((0,c.u)(o[e])||e);const s=t.states[n[0]];let d="other",p="";if(void 0!==e.from){let i=[];if(null===e.from)e.attribute||(d="null");else{i=(0,r.e)(e.from);const o=[];for(const r of i)o.push(s?e.attribute?t.formatEntityAttributeValue(s,e.attribute,r).toString():t.formatEntityState(s,r):r);0!==o.length&&(p=(0,u.q)(t.locale,o),d="fromUsed")}}let h="other",m="";if(void 0!==e.to){let i=[];if(null===e.to)e.attribute||(h="null");else{i=(0,r.e)(e.to);const o=[];for(const r of i)o.push(s?e.attribute?t.formatEntityAttributeValue(s,e.attribute,r).toString():t.formatEntityState(s,r).toString():r);0!==o.length&&(m=(0,u.q)(t.locale,o),h="toUsed")}}e.attribute||void 0!==e.from||void 0!==e.to||(h="special");let y="";return e.for&&(y=g(t.locale,e.for)??""),t.localize(`${_}.state.description.full`,{hasAttribute:""!==a?"true":"false",attribute:a,hasEntity:0!==i.length?"true":"false",entity:(0,u.q)(t.locale,i),fromChoice:d,fromString:p,toChoice:h,toString:m,hasDuration:""!==y?"true":"false",duration:y})}if("sun"===e.trigger&&e.event){let i="";return e.offset&&(i="number"==typeof e.offset?(0,s.A)(e.offset):"string"==typeof e.offset?e.offset:JSON.stringify(e.offset)),t.localize("sunset"===e.event?`${_}.sun.description.sets`:`${_}.sun.description.rises`,{hasDuration:""!==i?"true":"false",duration:i})}if("tag"===e.trigger){const i=Object.values(t.states).find((t=>t.entity_id.startsWith("tag.")&&t.attributes.tag_id===e.tag_id));return i?t.localize(`${_}.tag.description.known_tag`,{tag_name:(0,c.u)(i)}):t.localize(`${_}.tag.description.full`)}if("time"===e.trigger&&e.at){const i=(0,r.e)(e.at).map((e=>{if("string"==typeof e)return(0,d.n)(e)?`entity ${t.states[e]?(0,c.u)(t.states[e]):e}`:v(e,t.locale,t.config);return`${`entity ${t.states[e.entity_id]?(0,c.u)(t.states[e.entity_id]):e.entity_id}`}${e.offset?" "+t.localize(`${_}.time.offset_by`,{offset:g(t.locale,e.offset)}):""}`}));let o=[];if(e.weekday){const i=(0,r.e)(e.weekday);i.length>0&&(o=i.map((e=>t.localize(`ui.panel.config.automation.editor.triggers.type.time.weekdays.${e}`))))}return t.localize(`${_}.time.description.full`,{time:(0,u.q)(t.locale,i),hasWeekdays:o.length>0?"true":"false",weekdays:(0,u.q)(t.locale,o)})}if("time_pattern"===e.trigger){if(!e.seconds&&!e.minutes&&!e.hours)return t.localize(`${_}.time_pattern.description.initial`);const i=[];let o="other",r="other",a="other",n=0,s=0,l=0;if(void 0!==e.seconds){const t="*"===e.seconds,r="string"==typeof e.seconds&&e.seconds.startsWith("/");n=t?0:"number"==typeof e.seconds?e.seconds:r?parseInt(e.seconds.substring(1)):parseInt(e.seconds),(isNaN(n)||n>59||n<0||r&&0===n)&&i.push("seconds"),o=t||r&&1===n?"every":r?"every_interval":"on_the_xth"}if(void 0!==e.minutes){const t="*"===e.minutes,o="string"==typeof e.minutes&&e.minutes.startsWith("/");s=t?0:"number"==typeof e.minutes?e.minutes:o?parseInt(e.minutes.substring(1)):parseInt(e.minutes),(isNaN(s)||s>59||s<0||o&&0===s)&&i.push("minutes"),r=t||o&&1===s?"every":o?"every_interval":void 0!==e.seconds?"has_seconds":"on_the_xth"}else void 0!==e.seconds&&(void 0!==e.hours?(s=0,r="has_seconds"):r="every");if(void 0!==e.hours){const t="*"===e.hours,o="string"==typeof e.hours&&e.hours.startsWith("/");l=t?0:"number"==typeof e.hours?e.hours:o?parseInt(e.hours.substring(1)):parseInt(e.hours),(isNaN(l)||l>23||l<0||o&&0===l)&&i.push("hours"),a=t||o&&1===l?"every":o?"every_interval":void 0!==e.seconds||void 0!==e.minutes?"has_seconds_or_minutes":"on_the_xth"}else a="every";return 0!==i.length?t.localize(`${_}.time_pattern.description.invalid`,{parts:(0,u.c)(t.locale,i.map((e=>t.localize(`${_}.time_pattern.${e}`))))}):t.localize(`${_}.time_pattern.description.full`,{secondsChoice:o,minutesChoice:r,hoursChoice:a,seconds:n,minutes:s,hours:l,secondsWithOrdinal:t.localize(`${_}.time_pattern.description.ordinal`,{part:n}),minutesWithOrdinal:t.localize(`${_}.time_pattern.description.ordinal`,{part:s}),hoursWithOrdinal:t.localize(`${_}.time_pattern.description.ordinal`,{part:l})})}if("zone"===e.trigger&&e.entity_id&&e.zone){const i=[],o=[],r=t.states;if(Array.isArray(e.entity_id))for(const t of e.entity_id.values())r[t]&&i.push((0,c.u)(r[t])||t);else i.push(r[e.entity_id]?(0,c.u)(r[e.entity_id]):e.entity_id);if(Array.isArray(e.zone))for(const t of e.zone.values())r[t]&&o.push((0,c.u)(r[t])||t);else o.push(r[e.zone]?(0,c.u)(r[e.zone]):e.zone);return t.localize(`${_}.zone.description.full`,{entity:(0,u.q)(t.locale,i),event:e.event.toString(),zone:(0,u.q)(t.locale,o),numberOfZones:o.length})}if("geo_location"===e.trigger&&e.source&&e.zone){const i=[],o=[],r=t.states;if(Array.isArray(e.source))for(const t of e.source.values())i.push(t);else i.push(e.source);if(Array.isArray(e.zone))for(const t of e.zone.values())r[t]&&o.push((0,c.u)(r[t])||t);else o.push(r[e.zone]?(0,c.u)(r[e.zone]):e.zone);return t.localize(`${_}.geo_location.description.full`,{source:(0,u.q)(t.locale,i),event:e.event.toString(),zone:(0,u.q)(t.locale,o),numberOfZones:o.length})}if("mqtt"===e.trigger)return t.localize(`${_}.mqtt.description.full`);if("template"===e.trigger){let i="";return e.for&&(i=g(t.locale,e.for)??""),t.localize(`${_}.template.description.full`,{hasDuration:""!==i?"true":"false",duration:i})}if("webhook"===e.trigger)return t.localize(`${_}.webhook.description.full`);if("conversation"===e.trigger){if(!e.command||!e.command.length)return t.localize(`${_}.conversation.description.empty`);const i=(0,r.e)(e.command);return 1===i.length?t.localize(`${_}.conversation.description.single`,{sentence:i[0]}):t.localize(`${_}.conversation.description.multiple`,{sentence:i[0],count:i.length-1})}if("persistent_notification"===e.trigger)return t.localize(`${_}.persistent_notification.description.full`);if("device"===e.trigger&&e.device_id){const o=e,r=(0,p.nx)(t,i,o);if(r)return r;const a=t.states[o.entity_id];return`${a?(0,c.u)(a):o.entity_id} ${o.type}`}if("calendar"===e.trigger){const i=t.states[e.entity_id]?(0,c.u)(t.states[e.entity_id]):e.entity_id;let o="other",r="";if(e.offset){o=e.offset.startsWith("-")?"before":"after",r=e.offset.startsWith("-")?e.offset.substring(1).split(":"):e.offset.split(":");const i={hours:r.length>0?+r[0]:0,minutes:r.length>1?+r[1]:0,seconds:r.length>2?+r[2]:0};r=(0,a.i)(t.locale,i),""===r&&(o="other")}return t.localize(`${_}.calendar.description.full`,{eventChoice:e.event,offsetChoice:o,offset:r,hasCalendar:e.entity_id?"true":"false",calendar:i})}return t.localize(`ui.panel.config.automation.editor.triggers.type.${e.trigger}.label`)||t.localize("ui.panel.config.automation.editor.triggers.unknown_trigger")},A=(e,t,i,o=!1)=>{try{const r=C(e,t,i,o);if("string"!=typeof r)throw new Error(String(r));return r}catch(r){console.error(r);let e="Error in describing condition";return r.message&&(e+=": "+r.message),e}},C=(e,t,i,o=!1)=>{if("string"==typeof e&&(0,m.r)(e))return t.localize(`${f}.template.description.full`);if(e.alias&&!o)return e.alias;if(!e.condition){const t=["and","or","not"];for(const i of t)i in e&&(0,r.e)(e[i])&&(e={condition:i,conditions:e[i]})}if("or"===e.condition){const i=(0,r.e)(e.conditions);if(!i||0===i.length)return t.localize(`${f}.or.description.no_conditions`);const o=i.length;return t.localize(`${f}.or.description.full`,{count:o})}if("and"===e.condition){const i=(0,r.e)(e.conditions);if(!i||0===i.length)return t.localize(`${f}.and.description.no_conditions`);const o=i.length;return t.localize(`${f}.and.description.full`,{count:o})}if("not"===e.condition){const i=(0,r.e)(e.conditions);return i&&0!==i.length?1===i.length?t.localize(`${f}.not.description.one_condition`):t.localize(`${f}.not.description.full`,{count:i.length}):t.localize(`${f}.not.description.no_conditions`)}if("state"===e.condition){if(!e.entity_id)return t.localize(`${f}.state.description.no_entity`);let i="";if(e.attribute){const o=Array.isArray(e.entity_id)?t.states[e.entity_id[0]]:t.states[e.entity_id];i=o?(0,l.R)(t.localize,o,t.entities,e.attribute):e.attribute}const o=[];if(Array.isArray(e.entity_id))for(const s of e.entity_id.values())t.states[s]&&o.push((0,c.u)(t.states[s])||s);else e.entity_id&&o.push(t.states[e.entity_id]?(0,c.u)(t.states[e.entity_id]):e.entity_id);const r=[],a=t.states[Array.isArray(e.entity_id)?e.entity_id[0]:e.entity_id];if(Array.isArray(e.state))for(const s of e.state.values())r.push(a?e.attribute?t.formatEntityAttributeValue(a,e.attribute,s).toString():t.formatEntityState(a,s):s);else""!==e.state&&r.push(a?e.attribute?t.formatEntityAttributeValue(a,e.attribute,e.state).toString():t.formatEntityState(a,e.state.toString()):e.state.toString());let n="";return e.for&&(n=g(t.locale,e.for)||""),t.localize(`${f}.state.description.full`,{hasAttribute:""!==i?"true":"false",attribute:i,numberOfEntities:o.length,entities:"any"===e.match?(0,u.q)(t.locale,o):(0,u.c)(t.locale,o),numberOfStates:r.length,states:(0,u.q)(t.locale,r),hasDuration:""!==n?"true":"false",duration:n})}if("numeric_state"===e.condition&&e.entity_id){const i=(0,r.e)(e.entity_id),o=t.states[i[0]],a=(0,u.c)(t.locale,i.map((e=>t.states[e]?(0,c.u)(t.states[e]):e||""))),n=e.attribute?o?(0,l.R)(t.localize,o,t.entities,e.attribute):e.attribute:void 0;if(void 0!==e.above&&void 0!==e.below)return t.localize(`${f}.numeric_state.description.above-below`,{attribute:n,entity:a,numberOfEntities:i.length,above:e.above,below:e.below});if(void 0!==e.above)return t.localize(`${f}.numeric_state.description.above`,{attribute:n,entity:a,numberOfEntities:i.length,above:e.above});if(void 0!==e.below)return t.localize(`${f}.numeric_state.description.below`,{attribute:n,entity:a,numberOfEntities:i.length,below:e.below})}if("time"===e.condition){const i=(0,r.e)(e.weekday),o=i&&i.length>0&&i.length<7;if(e.before||e.after||o){const r="string"!=typeof e.before?e.before:e.before.includes(".")?`entity ${t.states[e.before]?(0,c.u)(t.states[e.before]):e.before}`:v(e.before,t.locale,t.config),a="string"!=typeof e.after?e.after:e.after.includes(".")?`entity ${t.states[e.after]?(0,c.u)(t.states[e.after]):e.after}`:v(e.after,t.locale,t.config);let n=[];o&&(n=i.map((e=>t.localize(`ui.panel.config.automation.editor.conditions.type.time.weekdays.${e}`))));let s="";return void 0!==a&&void 0!==r?s="after_before":void 0!==a?s="after":void 0!==r&&(s="before"),t.localize(`${f}.time.description.full`,{hasTime:s,hasTimeAndDay:(a||r)&&o?"true":"false",hasDay:o?"true":"false",time_before:r,time_after:a,day:(0,u.q)(t.locale,n)})}}if("sun"===e.condition&&(e.before||e.after)){let i="";e.after&&e.after_offset&&(i="number"==typeof e.after_offset?(0,s.A)(e.after_offset):"string"==typeof e.after_offset?e.after_offset:JSON.stringify(e.after_offset));let o="";return e.before&&e.before_offset&&(o="number"==typeof e.before_offset?(0,s.A)(e.before_offset):"string"==typeof e.before_offset?e.before_offset:JSON.stringify(e.before_offset)),t.localize(`${f}.sun.description.full`,{afterChoice:e.after??"other",afterOffsetChoice:""!==i?"offset":"other",afterOffset:i,beforeChoice:e.before??"other",beforeOffsetChoice:""!==o?"offset":"other",beforeOffset:o})}if("zone"===e.condition&&e.entity_id&&e.zone){const i=[],o=[],r=t.states;if(Array.isArray(e.entity_id))for(const t of e.entity_id.values())r[t]&&i.push((0,c.u)(r[t])||t);else i.push(r[e.entity_id]?(0,c.u)(r[e.entity_id]):e.entity_id);if(Array.isArray(e.zone))for(const t of e.zone.values())r[t]&&o.push((0,c.u)(r[t])||t);else o.push(r[e.zone]?(0,c.u)(r[e.zone]):e.zone);const a=(0,u.q)(t.locale,i),n=(0,u.q)(t.locale,o);return t.localize(`${f}.zone.description.full`,{entity:a,numberOfEntities:i.length,zone:n,numberOfZones:o.length})}if("device"===e.condition&&e.device_id){const o=e,r=(0,p.I3)(t,i,o);if(r)return r;const a=t.states[o.entity_id];return`${a?(0,c.u)(a):o.entity_id} ${o.type}`}return"template"===e.condition?t.localize(`${f}.template.description.full`):"trigger"===e.condition&&null!=e.id?t.localize(`${f}.trigger.description.full`,{id:(0,u.q)(t.locale,(0,r.e)(e.id).map((e=>e.toString())))}):t.localize(`ui.panel.config.automation.editor.conditions.type.${e.condition}.label`)||t.localize("ui.panel.config.automation.editor.conditions.unknown_condition")};o()}catch(_){o(_)}}))},32588:function(e,t,i){i.d(t,{Dk:()=>o,I8:()=>a,fg:()=>n,rq:()=>r});const o={device:"M3 6H21V4H3C1.9 4 1 4.9 1 6V18C1 19.1 1.9 20 3 20H7V18H3V6M13 12H9V13.78C8.39 14.33 8 15.11 8 16C8 16.89 8.39 17.67 9 18.22V20H13V18.22C13.61 17.67 14 16.88 14 16S13.61 14.33 13 13.78V12M11 17.5C10.17 17.5 9.5 16.83 9.5 16S10.17 14.5 11 14.5 12.5 15.17 12.5 16 11.83 17.5 11 17.5M22 8H16C15.5 8 15 8.5 15 9V19C15 19.5 15.5 20 16 20H22C22.5 20 23 19.5 23 19V9C23 8.5 22.5 8 22 8M21 18H17V10H21V18Z",and:"M4.4,16.5C4.4,15.6 4.7,14.7 5.2,13.9C5.7,13.1 6.7,12.2 8.2,11.2C7.3,10.1 6.8,9.3 6.5,8.7C6.1,8 6,7.4 6,6.7C6,5.2 6.4,4.1 7.3,3.2C8.2,2.3 9.4,2 10.9,2C12.2,2 13.3,2.4 14.2,3.2C15.1,4 15.5,5 15.5,6.1C15.5,6.9 15.3,7.6 14.9,8.3C14.5,9 13.8,9.7 12.8,10.4L11.4,11.5L15.7,16.7C16.3,15.5 16.6,14.3 16.6,12.8H18.8C18.8,15.1 18.3,17 17.2,18.5L20,21.8H17L15.7,20.3C15,20.9 14.3,21.3 13.4,21.6C12.5,21.9 11.6,22.1 10.7,22.1C8.8,22.1 7.3,21.6 6.1,20.6C5,19.5 4.4,18.2 4.4,16.5M10.7,20C12,20 13.2,19.5 14.3,18.5L9.6,12.8L9.2,13.1C7.7,14.2 7,15.3 7,16.5C7,17.6 7.3,18.4 8,19C8.7,19.6 9.5,20 10.7,20M8.5,6.7C8.5,7.6 9,8.6 10.1,9.9L11.7,8.8C12.3,8.4 12.7,8 12.9,7.6C13.1,7.2 13.2,6.7 13.2,6.2C13.2,5.6 13,5.1 12.5,4.7C12.1,4.3 11.5,4.1 10.8,4.1C10.1,4.1 9.5,4.3 9.1,4.8C8.7,5.3 8.5,5.9 8.5,6.7Z",or:"M2,4C5,10 5,14 2,20H8C13,20 19,16 22,12C19,8 13,4 8,4H2M5,6H8C11.5,6 16.3,9 19.3,12C16.3,15 11.5,18 8,18H5C6.4,13.9 6.4,10.1 5,6Z",not:"M14.08,4.61L15.92,5.4L14.8,8H19V10H13.95L12.23,14H19V16H11.38L9.92,19.4L8.08,18.61L9.2,16H5V14H10.06L11.77,10H5V8H12.63L14.08,4.61Z",state:"M6.27 17.05C6.72 17.58 7 18.25 7 19C7 20.66 5.66 22 4 22S1 20.66 1 19 2.34 16 4 16C4.18 16 4.36 16 4.53 16.05L7.6 10.69L5.86 9.7L9.95 8.58L11.07 12.67L9.33 11.68L6.27 17.05M20 16C18.7 16 17.6 16.84 17.18 18H11V16L8 19L11 22V20H17.18C17.6 21.16 18.7 22 20 22C21.66 22 23 20.66 23 19S21.66 16 20 16M12 8C12.18 8 12.36 8 12.53 7.95L15.6 13.31L13.86 14.3L17.95 15.42L19.07 11.33L17.33 12.32L14.27 6.95C14.72 6.42 15 5.75 15 5C15 3.34 13.66 2 12 2S9 3.34 9 5 10.34 8 12 8Z",numeric_state:"M4,17V9H2V7H6V17H4M22,15C22,16.11 21.1,17 20,17H16V15H20V13H18V11H20V9H16V7H20A2,2 0 0,1 22,9V10.5A1.5,1.5 0 0,1 20.5,12A1.5,1.5 0 0,1 22,13.5V15M14,15V17H8V13C8,11.89 8.9,11 10,11H12V9H8V7H12A2,2 0 0,1 14,9V11C14,12.11 13.1,13 12,13H10V15H14Z",sun:"M12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,2L14.39,5.42C13.65,5.15 12.84,5 12,5C11.16,5 10.35,5.15 9.61,5.42L12,2M3.34,7L7.5,6.65C6.9,7.16 6.36,7.78 5.94,8.5C5.5,9.24 5.25,10 5.11,10.79L3.34,7M3.36,17L5.12,13.23C5.26,14 5.53,14.78 5.95,15.5C6.37,16.24 6.91,16.86 7.5,17.37L3.36,17M20.65,7L18.88,10.79C18.74,10 18.47,9.23 18.05,8.5C17.63,7.78 17.1,7.15 16.5,6.64L20.65,7M20.64,17L16.5,17.36C17.09,16.85 17.62,16.22 18.04,15.5C18.46,14.77 18.73,14 18.87,13.21L20.64,17M12,22L9.59,18.56C10.33,18.83 11.14,19 12,19C12.82,19 13.63,18.83 14.37,18.56L12,22Z",template:"M8,3A2,2 0 0,0 6,5V9A2,2 0 0,1 4,11H3V13H4A2,2 0 0,1 6,15V19A2,2 0 0,0 8,21H10V19H8V14A2,2 0 0,0 6,12A2,2 0 0,0 8,10V5H10V3M16,3A2,2 0 0,1 18,5V9A2,2 0 0,0 20,11H21V13H20A2,2 0 0,0 18,15V19A2,2 0 0,1 16,21H14V19H16V14A2,2 0 0,1 18,12A2,2 0 0,1 16,10V5H14V3H16Z",time:"M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z",trigger:"M10 7V9H9V15H10V17H6V15H7V9H6V7H10M16 7C17.11 7 18 7.9 18 9V15C18 16.11 17.11 17 16 17H12V7M16 9H14V15H16V9Z",zone:"M12,2C15.31,2 18,4.66 18,7.95C18,12.41 12,19 12,19C12,19 6,12.41 6,7.95C6,4.66 8.69,2 12,2M12,6A2,2 0 0,0 10,8A2,2 0 0,0 12,10A2,2 0 0,0 14,8A2,2 0 0,0 12,6M20,19C20,21.21 16.42,23 12,23C7.58,23 4,21.21 4,19C4,17.71 5.22,16.56 7.11,15.83L7.75,16.74C6.67,17.19 6,17.81 6,18.5C6,19.88 8.69,21 12,21C15.31,21 18,19.88 18,18.5C18,17.81 17.33,17.19 16.25,16.74L16.89,15.83C18.78,16.56 20,17.71 20,19Z"},r={device:{},entity:{icon:"M11,13.5V21.5H3V13.5H11M12,2L17.5,11H6.5L12,2M17.5,13C20,13 22,15 22,17.5C22,20 20,22 17.5,22C15,22 13,20 13,17.5C13,15 15,13 17.5,13Z",members:{state:{},numeric_state:{}}},time_location:{icon:"M15,12H16.5V16.25L19.36,17.94L18.61,19.16L15,17V12M23,16A7,7 0 0,1 16,23C13,23 10.4,21.08 9.42,18.4L8,17.9L2.66,19.97L2.5,20A0.5,0.5 0 0,1 2,19.5V4.38C2,4.15 2.15,3.97 2.36,3.9L8,2L14,4.1L19.34,2H19.5A0.5,0.5 0 0,1 20,2.5V10.25C21.81,11.5 23,13.62 23,16M9,16C9,12.83 11.11,10.15 14,9.29V6.11L8,4V15.89L9,16.24C9,16.16 9,16.08 9,16M16,11A5,5 0 0,0 11,16A5,5 0 0,0 16,21A5,5 0 0,0 21,16A5,5 0 0,0 16,11Z",members:{sun:{},time:{},zone:{}}},building_blocks:{icon:"M18.5 18.5C19.04 18.5 19.5 18.96 19.5 19.5S19.04 20.5 18.5 20.5H6.5C5.96 20.5 5.5 20.04 5.5 19.5S5.96 18.5 6.5 18.5H18.5M18.5 17H6.5C5.13 17 4 18.13 4 19.5S5.13 22 6.5 22H18.5C19.88 22 21 20.88 21 19.5S19.88 17 18.5 17M21 11H18V7H13L10 11V16H22L21 11M11.54 11L13.5 8.5H16V11H11.54M9.76 3.41L4.76 2L2 11.83C1.66 13.11 2.41 14.44 3.7 14.8L4.86 15.12L8.15 12.29L4.27 11.21L6.15 4.46L8.94 5.24C9.5 5.53 10.71 6.34 11.47 7.37L12.5 6H12.94C11.68 4.41 9.85 3.46 9.76 3.41Z",members:{and:{},or:{},not:{}}},other:{icon:"M16,12A2,2 0 0,1 18,10A2,2 0 0,1 20,12A2,2 0 0,1 18,14A2,2 0 0,1 16,12M10,12A2,2 0 0,1 12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12M4,12A2,2 0 0,1 6,10A2,2 0 0,1 8,12A2,2 0 0,1 6,14A2,2 0 0,1 4,12Z",members:{template:{},trigger:{}}}},a=["and","or","not"],n=["ha-automation-condition-and","ha-automation-condition-not","ha-automation-condition-or"]},88151:function(e,t,i){i.d(t,{$:()=>o});const o=(e,t)=>e.callWS({type:"validate_config",...t})},24986:function(e,t,i){i.d(t,{HD:()=>n,ih:()=>r,rf:()=>a});var o=i(97809);(0,o.q6)("connection"),(0,o.q6)("states"),(0,o.q6)("entities"),(0,o.q6)("devices"),(0,o.q6)("areas"),(0,o.q6)("localize"),(0,o.q6)("locale"),(0,o.q6)("config"),(0,o.q6)("themes"),(0,o.q6)("selectedTheme"),(0,o.q6)("user"),(0,o.q6)("userData"),(0,o.q6)("panels");const r=(0,o.q6)("extendedEntities"),a=(0,o.q6)("floors"),n=(0,o.q6)("labels")},7657:function(e,t,i){i.d(t,{I$:()=>d,I3:()=>f,PV:()=>_,Po:()=>h,RK:()=>w,TB:()=>u,TH:()=>b,T_:()=>v,am:()=>n,jR:()=>c,ng:()=>s,nx:()=>g,o9:()=>l});var o=i(47379),r=i(70614),a=i(2834);const n=(e,t)=>e.callWS({type:"device_automation/action/list",device_id:t}),s=(e,t)=>e.callWS({type:"device_automation/condition/list",device_id:t}),l=(e,t)=>e.callWS({type:"device_automation/trigger/list",device_id:t}).then((e=>(0,r.vO)(e))),c=(e,t)=>e.callWS({type:"device_automation/action/capabilities",action:t}),d=(e,t)=>e.callWS({type:"device_automation/condition/capabilities",condition:t}),u=(e,t)=>e.callWS({type:"device_automation/trigger/capabilities",trigger:t}),p=["device_id","domain","entity_id","type","subtype","event","condition","trigger"],h=(e,t,i)=>{if(typeof t!=typeof i)return!1;for(const o in t)if(p.includes(o))if("entity_id"!==o||t[o]?.includes(".")===i[o]?.includes(".")){if(!Object.is(t[o],i[o]))return!1}else if(!m(e,t[o],i[o]))return!1;for(const o in i)if(p.includes(o))if("entity_id"!==o||t[o]?.includes(".")===i[o]?.includes(".")){if(!Object.is(t[o],i[o]))return!1}else if(!m(e,t[o],i[o]))return!1;return!0},m=(e,t,i)=>{if(!t||!i)return!1;if(t.includes(".")){const i=(0,a.Ox)(e)[t];if(!i)return!1;t=i.id}if(i.includes(".")){const t=(0,a.Ox)(e)[i];if(!t)return!1;i=t.id}return t===i},y=(e,t,i)=>{if(!i)return"<"+e.localize("ui.panel.config.automation.editor.unknown_entity")+">";if(i.includes(".")){const t=e.states[i];return t?(0,o.u)(t):i}const r=(0,a.P9)(t)[i];return r?(0,a.jh)(e,r)||i:"<"+e.localize("ui.panel.config.automation.editor.unknown_entity")+">"},_=(e,t,i)=>e.localize(`component.${i.domain}.device_automation.action_type.${i.type}`,{entity_name:y(e,t,i.entity_id),subtype:i.subtype?e.localize(`component.${i.domain}.device_automation.action_subtype.${i.subtype}`)||i.subtype:""})||(i.subtype?`"${i.subtype}" ${i.type}`:i.type),f=(e,t,i)=>e.localize(`component.${i.domain}.device_automation.condition_type.${i.type}`,{entity_name:y(e,t,i.entity_id),subtype:i.subtype?e.localize(`component.${i.domain}.device_automation.condition_subtype.${i.subtype}`)||i.subtype:""})||(i.subtype?`"${i.subtype}" ${i.type}`:i.type),g=(e,t,i)=>e.localize(`component.${i.domain}.device_automation.trigger_type.${i.type}`,{entity_name:y(e,t,i.entity_id),subtype:i.subtype?e.localize(`component.${i.domain}.device_automation.trigger_subtype.${i.subtype}`)||i.subtype:""})||(i.subtype?`"${i.subtype}" ${i.type}`:i.type),v=(e,t)=>i=>e.localize(`component.${t.domain}.device_automation.extra_fields.${i.name}`)||i.name,b=(e,t)=>i=>e.localize(`component.${t.domain}.device_automation.extra_fields_descriptions.${i.name}`),w=(e,t)=>e.metadata?.secondary&&!t.metadata?.secondary?1:!e.metadata?.secondary&&t.metadata?.secondary?-1:0},6098:function(e,t,i){i.d(t,{HV:()=>a,Hh:()=>r,KF:()=>s,ON:()=>n,g0:()=>d,s7:()=>l});var o=i(87383);const r="unavailable",a="unknown",n="on",s="off",l=[r,a],c=[r,a,s],d=(0,o.g)(l);(0,o.g)(c)},8948:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{We:()=>s,rM:()=>n});var r=i(52744),a=e([r]);r=(a.then?(await a)():a)[0];new Set(["temperature","current_temperature","target_temperature","target_temp_temp","target_temp_high","target_temp_low","target_temp_step","min_temp","max_temp"]);const n={climate:{humidity:"%",current_humidity:"%",target_humidity_low:"%",target_humidity_high:"%",target_humidity_step:"%",min_humidity:"%",max_humidity:"%"},cover:{current_position:"%",current_tilt_position:"%"},fan:{percentage:"%"},humidifier:{humidity:"%",current_humidity:"%",min_humidity:"%",max_humidity:"%"},light:{color_temp:"mired",max_mireds:"mired",min_mireds:"mired",color_temp_kelvin:"K",min_color_temp_kelvin:"K",max_color_temp_kelvin:"K",brightness:"%"},sun:{azimuth:"°",elevation:"°"},vacuum:{battery_level:"%"},valve:{current_position:"%"},sensor:{battery_level:"%"},media_player:{volume_level:"%"}},s=["access_token","auto_update","available_modes","away_mode","changed_by","code_format","color_modes","current_activity","device_class","editable","effect_list","effect","entity_picture","event_type","event_types","fan_mode","fan_modes","fan_speed_list","forecast","friendly_name","frontend_stream_type","has_date","has_time","hs_color","hvac_mode","hvac_modes","icon","media_album_name","media_artist","media_content_type","media_position_updated_at","media_title","next_dawn","next_dusk","next_midnight","next_noon","next_rising","next_setting","operation_list","operation_mode","options","preset_mode","preset_modes","release_notes","release_summary","release_url","restored","rgb_color","rgbw_color","shuffle","sound_mode_list","sound_mode","source_list","source_type","source","state_class","supported_features","swing_mode","swing_mode","swing_modes","title","token","unit_of_measurement","xy_color"];o()}catch(n){o(n)}}))},2834:function(e,t,i){i.d(t,{BM:()=>_,Bz:()=>h,G3:()=>c,G_:()=>d,Ox:()=>m,P9:()=>y,jh:()=>s,v:()=>l});var o=i(47308),r=i(65940),a=i(47379),n=(i(90963),i(24802));const s=(e,t)=>{if(t.name)return t.name;const i=e.states[t.entity_id];return i?(0,a.u)(i):t.original_name?t.original_name:t.entity_id},l=(e,t)=>e.callWS({type:"config/entity_registry/get",entity_id:t}),c=(e,t)=>e.callWS({type:"config/entity_registry/get_entries",entity_ids:t}),d=(e,t,i)=>e.callWS({type:"config/entity_registry/update",entity_id:t,...i}),u=e=>e.sendMessagePromise({type:"config/entity_registry/list"}),p=(e,t)=>e.subscribeEvents((0,n.s)((()=>u(e).then((e=>t.setState(e,!0)))),500,!0),"entity_registry_updated"),h=(e,t)=>(0,o.N)("_entityRegistry",u,p,e,t),m=(0,r.A)((e=>{const t={};for(const i of e)t[i.entity_id]=i;return t})),y=(0,r.A)((e=>{const t={};for(const i of e)t[i.id]=i;return t})),_=(e,t)=>e.callWS({type:"config/entity_registry/get_automatic_entity_ids",entity_ids:t})},28027:function(e,t,i){i.d(t,{QC:()=>a,fK:()=>r,p$:()=>o});const o=(e,t,i)=>e(`component.${t}.title`)||i?.name||t,r=(e,t)=>{const i={type:"manifest/list"};return t&&(i.integrations=t),e.callWS(i)},a=(e,t)=>e.callWS({type:"manifest/get",integration:t})},17866:function(e,t,i){i.d(t,{BD:()=>c,Rn:()=>p,pq:()=>d,ve:()=>u});var o=i(36207),r=i(87383),a=(i(68985),i(71767)),n=(i(51663),i(70614));(0,r.g)(["queued","parallel"]);const s=(0,o.Ik)({alias:(0,o.lq)((0,o.Yj)()),continue_on_error:(0,o.lq)((0,o.zM)()),enabled:(0,o.lq)((0,o.zM)())}),l=(0,o.Ik)({entity_id:(0,o.lq)((0,o.KC)([(0,o.Yj)(),(0,o.YO)((0,o.Yj)())])),device_id:(0,o.lq)((0,o.KC)([(0,o.Yj)(),(0,o.YO)((0,o.Yj)())])),area_id:(0,o.lq)((0,o.KC)([(0,o.Yj)(),(0,o.YO)((0,o.Yj)())])),floor_id:(0,o.lq)((0,o.KC)([(0,o.Yj)(),(0,o.YO)((0,o.Yj)())])),label_id:(0,o.lq)((0,o.KC)([(0,o.Yj)(),(0,o.YO)((0,o.Yj)())]))}),c=(0,o.kp)(s,(0,o.Ik)({action:(0,o.lq)((0,o.Yj)()),service_template:(0,o.lq)((0,o.Yj)()),entity_id:(0,o.lq)((0,o.Yj)()),target:(0,o.lq)((0,o.KC)([l,(0,o.YP)((0,o.Yj)(),"has_template",(e=>(0,a.r)(e)))])),data:(0,o.lq)((0,o.Ik)()),response_variable:(0,o.lq)((0,o.Yj)()),metadata:(0,o.lq)((0,o.Ik)())}));const d=e=>"string"==typeof e&&(0,a.r)(e)?"check_condition":"delay"in e?"delay":"wait_template"in e?"wait_template":["condition","and","or","not"].some((t=>t in e))?"check_condition":"event"in e?"fire_event":!("device_id"in e)||"trigger"in e||"condition"in e?"repeat"in e?"repeat":"choose"in e?"choose":"if"in e?"if":"wait_for_trigger"in e?"wait_for_trigger":"variables"in e?"variables":"stop"in e?"stop":"sequence"in e?"sequence":"parallel"in e?"parallel":"set_conversation_response"in e?"set_conversation_response":"action"in e||"service"in e?"service":"unknown":"device_action",u=e=>"unknown"!==d(e),p=e=>{if(!e)return e;if(Array.isArray(e))return e.map(p);if("object"==typeof e&&null!==e&&"service"in e&&("action"in e||(e.action=e.service),delete e.service),"object"==typeof e&&null!==e&&"scene"in e&&(e.action="scene.turn_on",e.target={entity_id:e.scene},delete e.scene),"object"==typeof e&&null!==e&&"action"in e&&"media_player.play_media"===e.action&&"data"in e&&(e.data?.media_content_id||e.data?.media_content_type)){const t={...e.data},i={media_content_id:t.media_content_id,media_content_type:t.media_content_type,metadata:{...e.metadata||{}}};delete e.metadata,delete t.media_content_id,delete t.media_content_type,e.data={...t,media:i}}if("object"==typeof e&&null!==e&&"sequence"in e)for(const i of e.sequence)p(i);const t=d(e);if("parallel"===t){p(e.parallel)}if("choose"===t){const t=e;if(Array.isArray(t.choose))for(const e of t.choose)p(e.sequence);else t.choose&&p(t.choose.sequence);t.default&&p(t.default)}if("repeat"===t){p(e.repeat.sequence)}if("if"===t){const t=e;p(t.then),t.else&&p(t.else)}if("wait_for_trigger"===t){const t=e;(0,n.vO)(t.wait_for_trigger)}return e}},3949:function(e,t,i){i.d(t,{H4:()=>a,Sh:()=>o,_y:()=>r});const o={calendar:"M19,19H5V8H19M16,1V3H8V1H6V3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3H18V1M17,12H12V17H17V12Z",device:"M3 6H21V4H3C1.9 4 1 4.9 1 6V18C1 19.1 1.9 20 3 20H7V18H3V6M13 12H9V13.78C8.39 14.33 8 15.11 8 16C8 16.89 8.39 17.67 9 18.22V20H13V18.22C13.61 17.67 14 16.88 14 16S13.61 14.33 13 13.78V12M11 17.5C10.17 17.5 9.5 16.83 9.5 16S10.17 14.5 11 14.5 12.5 15.17 12.5 16 11.83 17.5 11 17.5M22 8H16C15.5 8 15 8.5 15 9V19C15 19.5 15.5 20 16 20H22C22.5 20 23 19.5 23 19V9C23 8.5 22.5 8 22 8M21 18H17V10H21V18Z",event:"M10,9A1,1 0 0,1 11,8A1,1 0 0,1 12,9V13.47L13.21,13.6L18.15,15.79C18.68,16.03 19,16.56 19,17.14V21.5C18.97,22.32 18.32,22.97 17.5,23H11C10.62,23 10.26,22.85 10,22.57L5.1,18.37L5.84,17.6C6.03,17.39 6.3,17.28 6.58,17.28H6.8L10,19V9M11,5A4,4 0 0,1 15,9C15,10.5 14.2,11.77 13,12.46V11.24C13.61,10.69 14,9.89 14,9A3,3 0 0,0 11,6A3,3 0 0,0 8,9C8,9.89 8.39,10.69 9,11.24V12.46C7.8,11.77 7,10.5 7,9A4,4 0 0,1 11,5M11,3A6,6 0 0,1 17,9C17,10.7 16.29,12.23 15.16,13.33L14.16,12.88C15.28,11.96 16,10.56 16,9A5,5 0 0,0 11,4A5,5 0 0,0 6,9C6,11.05 7.23,12.81 9,13.58V14.66C6.67,13.83 5,11.61 5,9A6,6 0 0,1 11,3Z",state:"M6.27 17.05C6.72 17.58 7 18.25 7 19C7 20.66 5.66 22 4 22S1 20.66 1 19 2.34 16 4 16C4.18 16 4.36 16 4.53 16.05L7.6 10.69L5.86 9.7L9.95 8.58L11.07 12.67L9.33 11.68L6.27 17.05M20 16C18.7 16 17.6 16.84 17.18 18H11V16L8 19L11 22V20H17.18C17.6 21.16 18.7 22 20 22C21.66 22 23 20.66 23 19S21.66 16 20 16M12 8C12.18 8 12.36 8 12.53 7.95L15.6 13.31L13.86 14.3L17.95 15.42L19.07 11.33L17.33 12.32L14.27 6.95C14.72 6.42 15 5.75 15 5C15 3.34 13.66 2 12 2S9 3.34 9 5 10.34 8 12 8Z",geo_location:"M12,11.5A2.5,2.5 0 0,1 9.5,9A2.5,2.5 0 0,1 12,6.5A2.5,2.5 0 0,1 14.5,9A2.5,2.5 0 0,1 12,11.5M12,2A7,7 0 0,0 5,9C5,14.25 12,22 12,22C12,22 19,14.25 19,9A7,7 0 0,0 12,2Z",homeassistant:i(90663).mdiHomeAssistant,mqtt:"M21,9L17,5V8H10V10H17V13M7,11L3,15L7,19V16H14V14H7V11Z",numeric_state:"M4,17V9H2V7H6V17H4M22,15C22,16.11 21.1,17 20,17H16V15H20V13H18V11H20V9H16V7H20A2,2 0 0,1 22,9V10.5A1.5,1.5 0 0,1 20.5,12A1.5,1.5 0 0,1 22,13.5V15M14,15V17H8V13C8,11.89 8.9,11 10,11H12V9H8V7H12A2,2 0 0,1 14,9V11C14,12.11 13.1,13 12,13H10V15H14Z",sun:"M12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,2L14.39,5.42C13.65,5.15 12.84,5 12,5C11.16,5 10.35,5.15 9.61,5.42L12,2M3.34,7L7.5,6.65C6.9,7.16 6.36,7.78 5.94,8.5C5.5,9.24 5.25,10 5.11,10.79L3.34,7M3.36,17L5.12,13.23C5.26,14 5.53,14.78 5.95,15.5C6.37,16.24 6.91,16.86 7.5,17.37L3.36,17M20.65,7L18.88,10.79C18.74,10 18.47,9.23 18.05,8.5C17.63,7.78 17.1,7.15 16.5,6.64L20.65,7M20.64,17L16.5,17.36C17.09,16.85 17.62,16.22 18.04,15.5C18.46,14.77 18.73,14 18.87,13.21L20.64,17M12,22L9.59,18.56C10.33,18.83 11.14,19 12,19C12.82,19 13.63,18.83 14.37,18.56L12,22Z",conversation:"M8,7A2,2 0 0,1 10,9V14A2,2 0 0,1 8,16A2,2 0 0,1 6,14V9A2,2 0 0,1 8,7M14,14C14,16.97 11.84,19.44 9,19.92V22H7V19.92C4.16,19.44 2,16.97 2,14H4A4,4 0 0,0 8,18A4,4 0 0,0 12,14H14M21.41,9.41L17.17,13.66L18.18,10H14A2,2 0 0,1 12,8V4A2,2 0 0,1 14,2H20A2,2 0 0,1 22,4V8C22,8.55 21.78,9.05 21.41,9.41Z",tag:"M18,6H13A2,2 0 0,0 11,8V10.28C10.41,10.62 10,11.26 10,12A2,2 0 0,0 12,14C13.11,14 14,13.1 14,12C14,11.26 13.6,10.62 13,10.28V8H16V16H8V8H10V6H8L6,6V18H18M20,20H4V4H20M20,2H4A2,2 0 0,0 2,4V20A2,2 0 0,0 4,22H20C21.11,22 22,21.1 22,20V4C22,2.89 21.11,2 20,2Z",template:"M8,3A2,2 0 0,0 6,5V9A2,2 0 0,1 4,11H3V13H4A2,2 0 0,1 6,15V19A2,2 0 0,0 8,21H10V19H8V14A2,2 0 0,0 6,12A2,2 0 0,0 8,10V5H10V3M16,3A2,2 0 0,1 18,5V9A2,2 0 0,0 20,11H21V13H20A2,2 0 0,0 18,15V19A2,2 0 0,1 16,21H14V19H16V14A2,2 0 0,1 18,12A2,2 0 0,1 16,10V5H14V3H16Z",time:"M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z",time_pattern:"M11,17A1,1 0 0,0 12,18A1,1 0 0,0 13,17A1,1 0 0,0 12,16A1,1 0 0,0 11,17M11,3V7H13V5.08C16.39,5.57 19,8.47 19,12A7,7 0 0,1 12,19A7,7 0 0,1 5,12C5,10.32 5.59,8.78 6.58,7.58L12,13L13.41,11.59L6.61,4.79V4.81C4.42,6.45 3,9.05 3,12A9,9 0 0,0 12,21A9,9 0 0,0 21,12A9,9 0 0,0 12,3M18,12A1,1 0 0,0 17,11A1,1 0 0,0 16,12A1,1 0 0,0 17,13A1,1 0 0,0 18,12M6,12A1,1 0 0,0 7,13A1,1 0 0,0 8,12A1,1 0 0,0 7,11A1,1 0 0,0 6,12Z",webhook:"M10.46,19C9,21.07 6.15,21.59 4.09,20.15C2.04,18.71 1.56,15.84 3,13.75C3.87,12.5 5.21,11.83 6.58,11.77L6.63,13.2C5.72,13.27 4.84,13.74 4.27,14.56C3.27,16 3.58,17.94 4.95,18.91C6.33,19.87 8.26,19.5 9.26,18.07C9.57,17.62 9.75,17.13 9.82,16.63V15.62L15.4,15.58L15.47,15.47C16,14.55 17.15,14.23 18.05,14.75C18.95,15.27 19.26,16.43 18.73,17.35C18.2,18.26 17.04,18.58 16.14,18.06C15.73,17.83 15.44,17.46 15.31,17.04L11.24,17.06C11.13,17.73 10.87,18.38 10.46,19M17.74,11.86C20.27,12.17 22.07,14.44 21.76,16.93C21.45,19.43 19.15,21.2 16.62,20.89C15.13,20.71 13.9,19.86 13.19,18.68L14.43,17.96C14.92,18.73 15.75,19.28 16.75,19.41C18.5,19.62 20.05,18.43 20.26,16.76C20.47,15.09 19.23,13.56 17.5,13.35C16.96,13.29 16.44,13.36 15.97,13.53L15.12,13.97L12.54,9.2H12.32C11.26,9.16 10.44,8.29 10.47,7.25C10.5,6.21 11.4,5.4 12.45,5.44C13.5,5.5 14.33,6.35 14.3,7.39C14.28,7.83 14.11,8.23 13.84,8.54L15.74,12.05C16.36,11.85 17.04,11.78 17.74,11.86M8.25,9.14C7.25,6.79 8.31,4.1 10.62,3.12C12.94,2.14 15.62,3.25 16.62,5.6C17.21,6.97 17.09,8.47 16.42,9.67L15.18,8.95C15.6,8.14 15.67,7.15 15.27,6.22C14.59,4.62 12.78,3.85 11.23,4.5C9.67,5.16 8.97,7 9.65,8.6C9.93,9.26 10.4,9.77 10.97,10.11L11.36,10.32L8.29,15.31C8.32,15.36 8.36,15.42 8.39,15.5C8.88,16.41 8.54,17.56 7.62,18.05C6.71,18.54 5.56,18.18 5.06,17.24C4.57,16.31 4.91,15.16 5.83,14.67C6.22,14.46 6.65,14.41 7.06,14.5L9.37,10.73C8.9,10.3 8.5,9.76 8.25,9.14Z",persistent_notification:"M13 11H11V5H13M13 15H11V13H13M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z",zone:"M12,2C15.31,2 18,4.66 18,7.95C18,12.41 12,19 12,19C12,19 6,12.41 6,7.95C6,4.66 8.69,2 12,2M12,6A2,2 0 0,0 10,8A2,2 0 0,0 12,10A2,2 0 0,0 14,8A2,2 0 0,0 12,6M20,19C20,21.21 16.42,23 12,23C7.58,23 4,21.21 4,19C4,17.71 5.22,16.56 7.11,15.83L7.75,16.74C6.67,17.19 6,17.81 6,18.5C6,19.88 8.69,21 12,21C15.31,21 18,19.88 18,18.5C18,17.81 17.33,17.19 16.25,16.74L16.89,15.83C18.78,16.56 20,17.71 20,19Z",list:"M7,5H21V7H7V5M7,13V11H21V13H7M4,4.5A1.5,1.5 0 0,1 5.5,6A1.5,1.5 0 0,1 4,7.5A1.5,1.5 0 0,1 2.5,6A1.5,1.5 0 0,1 4,4.5M4,10.5A1.5,1.5 0 0,1 5.5,12A1.5,1.5 0 0,1 4,13.5A1.5,1.5 0 0,1 2.5,12A1.5,1.5 0 0,1 4,10.5M7,19V17H21V19H7M4,16.5A1.5,1.5 0 0,1 5.5,18A1.5,1.5 0 0,1 4,19.5A1.5,1.5 0 0,1 2.5,18A1.5,1.5 0 0,1 4,16.5Z"},r={device:{},entity:{icon:"M11,13.5V21.5H3V13.5H11M12,2L17.5,11H6.5L12,2M17.5,13C20,13 22,15 22,17.5C22,20 20,22 17.5,22C15,22 13,20 13,17.5C13,15 15,13 17.5,13Z",members:{state:{},numeric_state:{}}},time_location:{icon:"M15,12H16.5V16.25L19.36,17.94L18.61,19.16L15,17V12M23,16A7,7 0 0,1 16,23C13,23 10.4,21.08 9.42,18.4L8,17.9L2.66,19.97L2.5,20A0.5,0.5 0 0,1 2,19.5V4.38C2,4.15 2.15,3.97 2.36,3.9L8,2L14,4.1L19.34,2H19.5A0.5,0.5 0 0,1 20,2.5V10.25C21.81,11.5 23,13.62 23,16M9,16C9,12.83 11.11,10.15 14,9.29V6.11L8,4V15.89L9,16.24C9,16.16 9,16.08 9,16M16,11A5,5 0 0,0 11,16A5,5 0 0,0 16,21A5,5 0 0,0 21,16A5,5 0 0,0 16,11Z",members:{calendar:{},sun:{},time:{},time_pattern:{},zone:{}}},other:{icon:"M16,12A2,2 0 0,1 18,10A2,2 0 0,1 20,12A2,2 0 0,1 18,14A2,2 0 0,1 16,12M10,12A2,2 0 0,1 12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12M4,12A2,2 0 0,1 6,10A2,2 0 0,1 8,12A2,2 0 0,1 6,14A2,2 0 0,1 4,12Z",members:{event:{},geo_location:{},homeassistant:{},mqtt:{},conversation:{},tag:{},template:{},webhook:{},persistent_notification:{}}}},a=e=>"triggers"in e},40653:function(e,t,i){var o=i(84922);i(7577),i(95635);new Set(["clear-night","cloudy","fog","lightning","lightning-rainy","partlycloudy","pouring","rainy","hail","snowy","snowy-rainy","sunny","windy","windy-variant"]),new Set(["partlycloudy","cloudy","fog","windy","windy-variant","hail","rainy","snowy","snowy-rainy","pouring","lightning","lightning-rainy"]),new Set(["hail","rainy","pouring","lightning-rainy"]),new Set(["windy","windy-variant"]),new Set(["snowy","snowy-rainy"]),new Set(["lightning","lightning-rainy"]),o.AH`
  .rain {
    fill: var(--weather-icon-rain-color, #30b3ff);
  }
  .sun {
    fill: var(--weather-icon-sun-color, #fdd93c);
  }
  .moon {
    fill: var(--weather-icon-moon-color, #fcf497);
  }
  .cloud-back {
    fill: var(--weather-icon-cloud-back-color, #d4d4d4);
  }
  .cloud-front {
    fill: var(--weather-icon-cloud-front-color, #f9f9f9);
  }
  .snow {
    fill: var(--weather-icon-snow-color, #f9f9f9);
    stroke: var(--weather-icon-snow-stroke-color, #d4d4d4);
    stroke-width: 1;
    paint-order: stroke;
  }
`},7245:function(e,t,i){var o=i(69868),r=i(84922),a=i(11991);i(23749);class n extends r.WF{render(){return r.qy`
      <ha-alert
        alert-type="warning"
        .title=${this.alertTitle||this.localize("ui.errors.config.editor_not_supported")}
      >
        ${this.warnings.length&&void 0!==this.warnings[0]?r.qy`<ul>
              ${this.warnings.map((e=>r.qy`<li>${e}</li>`))}
            </ul>`:r.s6}
        ${this.localize("ui.errors.config.edit_in_yaml_supported")}
      </ha-alert>
    `}constructor(...e){super(...e),this.warnings=[]}}(0,o.__decorate)([(0,a.MZ)({attribute:!1})],n.prototype,"localize",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:"alert-title"})],n.prototype,"alertTitle",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],n.prototype,"warnings",void 0),n=(0,o.__decorate)([(0,a.EM)("ha-automation-editor-warning")],n)},20850:function(e,t,i){i.d(t,{EN:()=>a,gZ:()=>s,uV:()=>r});var o=i(73120);const r="__paste__",a={repeat_count:{repeat:{count:2,sequence:[]}},repeat_while:{repeat:{while:[],sequence:[]}},repeat_until:{repeat:{until:[],sequence:[]}},repeat_for_each:{repeat:{for_each:{},sequence:[]}}},n=()=>i.e("1771").then(i.bind(i,41254)),s=(e,t)=>{(0,o.r)(e,"show-dialog",{dialogTag:"add-automation-element-dialog",dialogImport:n,dialogParams:t})}},67107:function(e,t,i){i.d(t,{V:()=>r,b:()=>a});var o=i(36207);const r=(0,o.Ik)({trigger:(0,o.Yj)(),id:(0,o.lq)((0,o.Yj)()),enabled:(0,o.lq)((0,o.zM)())}),a=(0,o.Ik)({days:(0,o.lq)((0,o.ai)()),hours:(0,o.lq)((0,o.ai)()),minutes:(0,o.lq)((0,o.ai)()),seconds:(0,o.lq)((0,o.ai)())})},68975:function(e,t,i){i.d(t,{Ju:()=>s,Lt:()=>l,aM:()=>n,bH:()=>r,yj:()=>a});var o=i(84922);const r=o.AH`
  ha-icon-button {
    --mdc-theme-text-primary-on-background: var(--primary-text-color);
  }
  ha-expansion-panel {
    --expansion-panel-summary-padding: 0 0 0 8px;
    --expansion-panel-content-padding: 0;
  }
  h3 {
    font-size: inherit;
    font-weight: inherit;
  }

  ha-card {
    transition: outline 0.2s;
  }
  .disabled-bar {
    background: var(--divider-color, #e0e0e0);
    text-align: center;
    border-top-right-radius: var(
      --ha-card-border-radius,
      var(--ha-border-radius-lg)
    );
    border-top-left-radius: var(
      --ha-card-border-radius,
      var(--ha-border-radius-lg)
    );
  }
  .warning ul {
    margin: 4px 0;
  }
  ha-md-menu-item > ha-svg-icon {
    --mdc-icon-size: 24px;
  }
  ha-tooltip {
    cursor: default;
  }
  .hidden {
    display: none;
  }
`,a=o.AH`
  .disabled {
    pointer-events: none;
  }

  .card-content.card {
    padding: 16px;
  }
  .card-content.yaml {
    padding: 0 1px;
    border-top: 1px solid var(--divider-color);
    border-bottom: 1px solid var(--divider-color);
  }
`,n=o.AH`
  .card-content.indent,
  .selector-row,
  :host([indent]) ha-form {
    margin-inline-start: 12px;
    padding-top: 12px;
    padding-bottom: 16px;
    padding-inline-start: 16px;
    padding-inline-end: 0px;
    border-inline-start: 2px solid var(--ha-color-border-neutral-quiet);
    border-bottom: 2px solid var(--ha-color-border-neutral-quiet);
    border-radius: 0;
    border-end-start-radius: var(--ha-border-radius-lg);
  }
  .card-content.indent.selected,
  :host([selected]) .card-content.indent,
  .selector-row.parent-selected,
  :host([selected]) ha-form {
    border-color: var(--primary-color);
    background: var(--ha-color-fill-primary-quiet-resting);
    background: linear-gradient(
      to right,
      var(--ha-color-fill-primary-quiet-resting) 0%,
      var(--ha-color-fill-primary-quiet-resting) 80%,
      rgba(var(--rgb-primary-color), 0) 100%
    );
  }
`,s=(o.AH`
  :host {
    overflow: hidden;
  }
  ha-fab {
    position: absolute;
    right: calc(16px + var(--safe-area-inset-right, 0px));
    bottom: calc(-80px - var(--safe-area-inset-bottom));
    transition: bottom 0.3s;
  }
  ha-fab.dirty {
    bottom: calc(16px + var(--safe-area-inset-bottom, 0px));
  }
`,o.AH`
  :host {
    display: block;
    --sidebar-width: 0;
    --sidebar-gap: 0;
  }

  .has-sidebar {
    --sidebar-width: min(
      max(var(--sidebar-dynamic-width), ${375}px),
      100vw - ${350}px - var(--mdc-drawer-width, 0px),
      var(--ha-automation-editor-max-width) -
        ${350}px - var(--mdc-drawer-width, 0px)
    );
    --sidebar-gap: 16px;
  }

  .fab-positioner {
    display: flex;
    justify-content: flex-end;
  }

  .fab-positioner ha-fab {
    position: fixed;
    right: unset;
    left: unset;
    bottom: calc(-80px - var(--safe-area-inset-bottom));
    transition: bottom 0.3s;
  }
  .fab-positioner ha-fab.dirty {
    bottom: calc(16px + var(--safe-area-inset-bottom, 0px));
  }

  .content-wrapper {
    padding-right: calc(var(--sidebar-width) + var(--sidebar-gap));
    padding-inline-end: calc(var(--sidebar-width) + var(--sidebar-gap));
    padding-inline-start: 0;
  }

  .content {
    padding-top: 24px;
    padding-bottom: 72px;
    transition: padding-bottom 180ms ease-in-out;
  }

  .content.has-bottom-sheet {
    padding-bottom: calc(90vh - 72px);
  }

  ha-automation-sidebar {
    position: fixed;
    top: calc(var(--header-height) + 16px);
    height: calc(
      -81px +
        100dvh - var(--safe-area-inset-top, 0px) - var(
          --safe-area-inset-bottom,
          0px
        )
    );
    width: var(--sidebar-width);
    display: block;
  }

  ha-automation-sidebar.hidden {
    display: none;
  }

  .sidebar-positioner {
    display: flex;
    justify-content: flex-end;
  }

  .description {
    margin: 0;
  }
  .header a {
    color: var(--secondary-text-color);
  }
`,o.AH`
  .rows {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .rows.no-sidebar {
    margin-inline-end: 0;
  }
  .sortable-ghost {
    background: none;
    border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg));
  }
  .sortable-drag {
    background: none;
  }
  ha-automation-action-row {
    display: block;
    scroll-margin-top: 48px;
  }
  .handle {
    padding: 4px;
    cursor: move; /* fallback if grab cursor is unsupported */
    cursor: grab;
    border-radius: var(--ha-border-radius-pill);
  }
  .handle:focus {
    outline: var(--wa-focus-ring);
    background: var(--ha-color-fill-neutral-quiet-resting);
  }
  .handle.active {
    outline: var(--wa-focus-ring);
    background: var(--ha-color-fill-neutral-normal-active);
  }
  .handle ha-svg-icon {
    pointer-events: none;
    height: 24px;
  }
  .buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    order: 1;
  }
`),l=(o.AH`
  .sidebar-editor {
    display: block;
    padding-top: 8px;
  }
  .description {
    padding-top: 16px;
  }
`,o.AH`
  .overflow-label {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    white-space: nowrap;
  }
  .overflow-label .shortcut {
    --mdc-icon-size: 12px;
    display: inline-flex;
    flex-direction: row;
    align-items: center;
    gap: 2px;
  }
  .overflow-label .shortcut span {
    font-size: var(--ha-font-size-s);
    font-family: var(--ha-font-family-code);
    color: var(--ha-color-text-secondary);
  }
  .shortcut-placeholder {
    display: inline-block;
    width: 60px;
  }
  .shortcut-placeholder.mac {
    width: 46px;
  }
  @media all and (max-width: 870px) {
    .shortcut-placeholder {
      display: none;
    }
  }
  ha-md-menu-item {
    --mdc-icon-size: 24px;
  }
`)},80608:function(e,t,i){i.d(t,{$:()=>a});var o=i(73120);const r=()=>i.e("8221").then(i.bind(i,27084)),a=(e,t)=>{(0,o.r)(e,"show-dialog",{dialogTag:"dialog-helper-detail",dialogImport:r,dialogParams:t})}},45363:function(e,t,i){i.d(t,{MR:()=>o,a_:()=>r,bg:()=>a});const o=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,r=e=>e.split("/")[4],a=e=>e.startsWith("https://brands.home-assistant.io/")},52493:function(e,t,i){i.d(t,{c:()=>o});const o=/Mac/i.test(navigator.userAgent)},72698:function(e,t,i){i.d(t,{P:()=>r});var o=i(73120);const r=(e,t)=>(0,o.r)(e,"hass-notification",t)}};
//# sourceMappingURL=4443.7512d350845f5881.js.map