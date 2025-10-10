"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["3901"],{35384:function(e,t,o){o.d(t,{z:function(){return i}});o(92344),o(47849);const i=e=>{if(void 0===e)return;if("object"!=typeof e){if("string"==typeof e||isNaN(e)){const t=(null==e?void 0:e.toString().split(":"))||[];if(1===t.length)return{seconds:Number(t[0])};if(t.length>3)return;const o=Number(t[2])||0,i=Math.floor(o);return{hours:Number(t[0])||0,minutes:Number(t[1])||0,seconds:i,milliseconds:Math.floor(1e3*Number((o-i).toFixed(4)))}}return{seconds:e}}if(!("days"in e))return e;const{days:t,minutes:o,seconds:i,milliseconds:n}=e;let r=e.hours||0;return r=(r||0)+24*(t||0),{hours:r,minutes:o,seconds:i,milliseconds:n}}},895:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{PE:function(){return c}});o(79827);var n=o(96904),r=o(6423),a=o(95075),s=e([n]);n=(s.then?(await s)():s)[0];const l=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],c=e=>e.first_weekday===a.zt.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,r.S)(e.language)%7:l.includes(e.first_weekday)?l.indexOf(e.first_weekday):1;i()}catch(l){i(l)}}))},49108:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{Yq:function(){return c},zB:function(){return u}});o(65315),o(84136);var n=o(96904),r=o(65940),a=o(95075),s=o(61608),l=e([n,s]);[n,s]=l.then?(await l)():l;(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"long",month:"long",day:"numeric",timeZone:(0,s.w)(e.time_zone,t)})));const c=(e,t,o)=>d(t,o.time_zone).format(e),d=(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",timeZone:(0,s.w)(e.time_zone,t)}))),u=((0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"short",day:"numeric",timeZone:(0,s.w)(e.time_zone,t)}))),(e,t,o)=>{var i,n,r,s;const l=p(t,o.time_zone);if(t.date_format===a.ow.language||t.date_format===a.ow.system)return l.format(e);const c=l.formatToParts(e),d=null===(i=c.find((e=>"literal"===e.type)))||void 0===i?void 0:i.value,u=null===(n=c.find((e=>"day"===e.type)))||void 0===n?void 0:n.value,h=null===(r=c.find((e=>"month"===e.type)))||void 0===r?void 0:r.value,m=null===(s=c.find((e=>"year"===e.type)))||void 0===s?void 0:s.value,f=c[c.length-1];let y="literal"===(null==f?void 0:f.type)?null==f?void 0:f.value:"";"bg"===t.language&&t.date_format===a.ow.YMD&&(y="");return{[a.ow.DMY]:`${u}${d}${h}${d}${m}${y}`,[a.ow.MDY]:`${h}${d}${u}${d}${m}${y}`,[a.ow.YMD]:`${m}${d}${h}${d}${u}${y}`}[t.date_format]}),p=(0,r.A)(((e,t)=>{const o=e.date_format===a.ow.system?void 0:e.language;return e.date_format===a.ow.language||(e.date_format,a.ow.system),new Intl.DateTimeFormat(o,{year:"numeric",month:"numeric",day:"numeric",timeZone:(0,s.w)(e.time_zone,t)})}));(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{day:"numeric",month:"short",timeZone:(0,s.w)(e.time_zone,t)}))),(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{month:"long",year:"numeric",timeZone:(0,s.w)(e.time_zone,t)}))),(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{month:"long",timeZone:(0,s.w)(e.time_zone,t)}))),(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",timeZone:(0,s.w)(e.time_zone,t)}))),(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"long",timeZone:(0,s.w)(e.time_zone,t)}))),(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"short",timeZone:(0,s.w)(e.time_zone,t)})));i()}catch(c){i(c)}}))},12950:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{r6:function(){return u}});var n=o(96904),r=o(65940),a=o(49108),s=o(48505),l=o(61608),c=o(56044),d=e([n,a,s,l]);[n,a,s,l]=d.then?(await d)():d;const u=(e,t,o)=>p(t,o.time_zone).format(e),p=(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",hour:(0,c.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.J)(e)?"h12":"h23",timeZone:(0,l.w)(e.time_zone,t)})));(0,r.A)((()=>new Intl.DateTimeFormat(void 0,{year:"numeric",month:"long",day:"numeric",hour:"2-digit",minute:"2-digit"}))),(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"short",day:"numeric",hour:(0,c.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.J)(e)?"h12":"h23",timeZone:(0,l.w)(e.time_zone,t)}))),(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{month:"short",day:"numeric",hour:(0,c.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.J)(e)?"h12":"h23",timeZone:(0,l.w)(e.time_zone,t)}))),(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",hour:(0,c.J)(e)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,c.J)(e)?"h12":"h23",timeZone:(0,l.w)(e.time_zone,t)})));i()}catch(u){i(u)}}))},52744:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{i:function(){return d},nR:function(){return l}});o(46852),o(91455);var n=o(96904),r=o(65940),a=e([n]);n=(a.then?(await a)():a)[0];const s=e=>e<10?`0${e}`:e,l=(e,t)=>{const o=t.days||0,i=t.hours||0,n=t.minutes||0,r=t.seconds||0,a=t.milliseconds||0;return o>0?`${Intl.NumberFormat(e.language,{style:"unit",unit:"day",unitDisplay:"long"}).format(o)} ${i}:${s(n)}:${s(r)}`:i>0?`${i}:${s(n)}:${s(r)}`:n>0?`${n}:${s(r)}`:r>0?Intl.NumberFormat(e.language,{style:"unit",unit:"second",unitDisplay:"long"}).format(r):a>0?Intl.NumberFormat(e.language,{style:"unit",unit:"millisecond",unitDisplay:"long"}).format(a):null},c=(0,r.A)((e=>new Intl.DurationFormat(e.language,{style:"long"}))),d=(e,t)=>c(e).format(t);(0,r.A)((e=>new Intl.DurationFormat(e.language,{style:"digital",hoursDisplay:"auto"}))),(0,r.A)((e=>new Intl.DurationFormat(e.language,{style:"narrow",daysDisplay:"always"}))),(0,r.A)((e=>new Intl.DurationFormat(e.language,{style:"narrow",hoursDisplay:"always"}))),(0,r.A)((e=>new Intl.DurationFormat(e.language,{style:"narrow",minutesDisplay:"always"})));i()}catch(s){i(s)}}))},48505:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{LW:function(){return f},Xs:function(){return h},fU:function(){return c},ie:function(){return u}});var n=o(96904),r=o(65940),a=o(61608),s=o(56044),l=e([n,a]);[n,a]=l.then?(await l)():l;const c=(e,t,o)=>d(t,o.time_zone).format(e),d=(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{hour:"numeric",minute:"2-digit",hourCycle:(0,s.J)(e)?"h12":"h23",timeZone:(0,a.w)(e.time_zone,t)}))),u=(e,t,o)=>p(t,o.time_zone).format(e),p=(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{hour:(0,s.J)(e)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,s.J)(e)?"h12":"h23",timeZone:(0,a.w)(e.time_zone,t)}))),h=(e,t,o)=>m(t,o.time_zone).format(e),m=(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"long",hour:(0,s.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,s.J)(e)?"h12":"h23",timeZone:(0,a.w)(e.time_zone,t)}))),f=(e,t,o)=>y(t,o.time_zone).format(e),y=(0,r.A)(((e,t)=>new Intl.DateTimeFormat("en-GB",{hour:"numeric",minute:"2-digit",hour12:!1,timeZone:(0,a.w)(e.time_zone,t)})));i()}catch(c){i(c)}}))},61608:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{w:function(){return p}});var n,r,a,s=o(96904),l=o(95075),c=e([s]);s=(c.then?(await c)():c)[0];const d=null===(n=Intl.DateTimeFormat)||void 0===n||null===(r=(a=n.call(Intl)).resolvedOptions)||void 0===r?void 0:r.call(a).timeZone,u=null!=d?d:"UTC",p=(e,t)=>e===l.Wj.local&&d?u:t;i()}catch(d){i(d)}}))},15216:function(e,t,o){o.d(t,{A:function(){return n}});const i=e=>e<10?`0${e}`:e;function n(e){const t=Math.floor(e/3600),o=Math.floor(e%3600/60),n=Math.floor(e%3600%60);return t>0?`${t}:${i(o)}:${i(n)}`:o>0?`${o}:${i(n)}`:n>0?""+n:null}},56044:function(e,t,o){o.d(t,{J:function(){return r}});o(79827),o(18223);var i=o(65940),n=o(95075);const r=(0,i.A)((e=>{if(e.time_format===n.Hg.language||e.time_format===n.Hg.system){const t=e.time_format===n.Hg.language?e.language:void 0;return new Date("January 1, 2023 22:00:00").toLocaleString(t).includes("10")}return e.time_format===n.Hg.am_pm}))},83490:function(e,t,o){o.d(t,{I:function(){return r}});o(46852),o(99342),o(65315),o(22416),o(36874),o(12977),o(54323);class i{addFromStorage(e){if(!this._storage[e]){const t=this.storage.getItem(e);t&&(this._storage[e]=JSON.parse(t))}}subscribeChanges(e,t){return this._listeners[e]?this._listeners[e].push(t):this._listeners[e]=[t],()=>{this.unsubscribeChanges(e,t)}}unsubscribeChanges(e,t){if(!(e in this._listeners))return;const o=this._listeners[e].indexOf(t);-1!==o&&this._listeners[e].splice(o,1)}hasKey(e){return e in this._storage}getValue(e){return this._storage[e]}setValue(e,t){const o=this._storage[e];this._storage[e]=t;try{void 0===t?this.storage.removeItem(e):this.storage.setItem(e,JSON.stringify(t))}catch(i){}finally{this._listeners[e]&&this._listeners[e].forEach((e=>e(o,t)))}}constructor(e=window.localStorage){this._storage={},this._listeners={},this.storage=e,this.storage===window.localStorage&&window.addEventListener("storage",(e=>{e.key&&this.hasKey(e.key)&&(this._storage[e.key]=e.newValue?JSON.parse(e.newValue):e.newValue,this._listeners[e.key]&&this._listeners[e.key].forEach((t=>t(e.oldValue?JSON.parse(e.oldValue):e.oldValue,this._storage[e.key]))))}))}}const n={};function r(e){return(t,o)=>{if("object"==typeof o)throw new Error("This decorator does not support this compilation type.");const r=e.storage||"localStorage";let a;r&&r in n?a=n[r]:(a=new i(window[r]),n[r]=a);const s=e.key||String(o);a.addFromStorage(s);const l=!1!==e.subscribe?e=>a.subscribeChanges(s,((t,i)=>{e.requestUpdate(o,t)})):void 0,c=()=>a.hasKey(s)?e.deserializer?e.deserializer(a.getValue(s)):a.getValue(s):void 0,d=(t,i)=>{let n;e.state&&(n=c()),a.setValue(s,e.serializer?e.serializer(i):i),e.state&&t.requestUpdate(o,n)},u=t.performUpdate;if(t.performUpdate=function(){this.__initialized=!0,u.call(this)},e.subscribe){const e=t.connectedCallback,o=t.disconnectedCallback;t.connectedCallback=function(){e.call(this);const t=this;t.__unbsubLocalStorage||(t.__unbsubLocalStorage=null==l?void 0:l(this))},t.disconnectedCallback=function(){var e;o.call(this);const t=this;null===(e=t.__unbsubLocalStorage)||void 0===e||e.call(t),t.__unbsubLocalStorage=void 0}}const p=Object.getOwnPropertyDescriptor(t,o);let h;if(void 0===p)h={get(){return c()},set(e){(this.__initialized||void 0===c())&&d(this,e)},configurable:!0,enumerable:!0};else{const e=p.set;h=Object.assign(Object.assign({},p),{},{get(){return c()},set(t){(this.__initialized||void 0===c())&&d(this,t),null==e||e.call(this,t)}})}Object.defineProperty(t,o,h)}}},88727:function(e,t,o){o.d(t,{C:function(){return i}});const i=e=>{e.preventDefault(),e.stopPropagation()}},27881:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{R:function(){return u}});o(65315),o(37089),o(59023),o(36874),o(67579),o(30500);var n=o(8948),r=(o(40653),o(49108)),a=o(12950),s=o(44665),l=o(8692),c=(o(3461),o(22017),o(92830)),d=e([n,r,a,s]);[n,r,a,s]=d.then?(await d)():d;const u=(e,t,o,i)=>{const n=t.entity_id,r=t.attributes.device_class,a=(0,c.m)(n),s=o[n],d=null==s?void 0:s.translation_key;return d&&e(`component.${s.platform}.entity.${a}.${d}.state_attributes.${i}.name`)||r&&e(`component.${a}.entity_component.${r}.state_attributes.${i}.name`)||e(`component.${a}.entity_component._.state_attributes.${i}.name`)||(0,l.Z)(i.replace(/_/g," ").replace(/\bid\b/g,"ID").replace(/\bip\b/g,"IP").replace(/\bmac\b/g,"MAC").replace(/\bgps\b/g,"GPS"))};i()}catch(u){i(u)}}))},44537:function(e,t,o){o.d(t,{xn:function(){return r},T:function(){return a}});o(35748),o(65315),o(837),o(37089),o(39118),o(95013);var i=o(65940),n=o(47379);o(88238),o(34536),o(16257),o(20152),o(44711),o(72108),o(77030);const r=e=>{var t;return null===(t=e.name_by_user||e.name)||void 0===t?void 0:t.trim()},a=(e,t,o)=>r(e)||o&&s(t,o)||t.localize("ui.panel.config.devices.unnamed_device",{type:t.localize(`ui.panel.config.devices.type.${e.entry_type||"device"}`)}),s=(e,t)=>{for(const o of t||[]){const t="string"==typeof o?o:o.entity_id,i=e.states[t];if(i)return(0,n.u)(i)}};(0,i.A)((e=>function(e){const t=new Set,o=new Set;for(const i of e)o.has(i)?t.add(i):o.add(i);return t}(Object.values(e).map((e=>r(e))).filter((e=>void 0!==e)))))},24383:function(e,t,o){o.d(t,{w:function(){return i}});const i=(e,t)=>{const o=e.area_id,i=o?t.areas[o]:void 0,n=null==i?void 0:i.floor_id;return{device:e,area:i||null,floor:(n?t.floors[n]:void 0)||null}}},24382:function(e,t,o){o.d(t,{e:function(){return i}});const i=e=>"latitude"in e.attributes&&"longitude"in e.attributes},8692:function(e,t,o){o.d(t,{Z:function(){return i}});const i=e=>e.charAt(0).toUpperCase()+e.slice(1)},72106:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{c:function(){return s},q:function(){return l}});var n=o(96904),r=o(65940),a=e([n]);n=(a.then?(await a)():a)[0];const s=(e,t)=>c(e).format(t),l=(e,t)=>d(e).format(t),c=(0,r.A)((e=>new Intl.ListFormat(e.language,{style:"long",type:"conjunction"}))),d=(0,r.A)((e=>new Intl.ListFormat(e.language,{style:"long",type:"disjunction"})));i()}catch(s){i(s)}}))},71767:function(e,t,o){o.d(t,{F:function(){return n},r:function(){return r}});o(65315),o(59023),o(67579),o(41190);const i=/{%|{{/,n=e=>i.test(e),r=e=>{if(!e)return!1;if("string"==typeof e)return n(e);if("object"==typeof e){return(Array.isArray(e)?e:Object.values(e)).some((e=>e&&r(e)))}return!1}},3461:function(e,t,o){o(42124),o(86581),o(67579),o(41190),o(47849);const i="^\\d{4}-(0[1-9]|1[0-2])-([12]\\d|0[1-9]|3[01])";new RegExp(i+"$"),new RegExp(i)},22017:function(e,t,o){o(67579),o(41190)},4071:function(e,t,o){o.d(t,{_:function(){return n}});o(35748),o(99342),o(36874),o(67579),o(30500),o(95013);var i=o(36207);const n=(e,t)=>{if(!(t instanceof i.C5))return{warnings:[t.message],errors:void 0};const o=[],n=[];for(const i of t.failures())if(void 0===i.value)o.push(e.localize("ui.errors.config.key_missing",{key:i.path.join(".")}));else if("never"===i.type)n.push(e.localize("ui.errors.config.key_not_expected",{key:i.path.join(".")}));else{if("union"===i.type)continue;"enums"===i.type?n.push(e.localize("ui.errors.config.key_wrong_type",{key:i.path.join("."),type_correct:i.message.replace("Expected ","").split(", ")[0],type_wrong:JSON.stringify(i.value)})):n.push(e.localize("ui.errors.config.key_wrong_type",{key:i.path.join("."),type_correct:i.refinement||i.type,type_wrong:JSON.stringify(i.value)}))}return{warnings:n,errors:o}}},51663:function(e,t,o){o(35748),o(65315),o(22416),o(67579),o(47849),o(79566),o(95013),o(13484),o(81071),o(92714),o(55885),o(90933)},4822:function(e,t,o){o.d(t,{V:function(){return H}});o(79827),o(35748),o(35058),o(65315),o(37089),o(12977),o(5934),o(95013);var i=o(69868),n=o(97809),r=o(84922),a=o(11991),s=o(73120),l=o(24986),c=o(7657),d=o(7137),u=o(20808);let p;class h extends d.${}h.styles=[u.R,(0,r.AH)(p||(p=(e=>e)`
      :host {
        --ha-icon-display: block;
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-secondary: var(--secondary-text-color);
        --md-sys-color-surface: var(--card-background-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-sys-color-on-surface-variant: var(--secondary-text-color);
      }
    `))],h=(0,i.__decorate)([(0,a.EM)("ha-md-select-option")],h);var m=o(39072),f=o(29512),y=o(89152);let _;class g extends m.V{}g.styles=[f.R,y.R,(0,r.AH)(_||(_=(e=>e)`
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
    `))],g=(0,i.__decorate)([(0,a.EM)("ha-md-select")],g);var v=o(20674);let b,w,A,C,$,M=e=>e;const V="NO_AUTOMATION",x="UNKNOWN_AUTOMATION";class H extends r.WF{get NO_AUTOMATION_TEXT(){return this.hass.localize("ui.panel.config.devices.automation.actions.no_actions")}get UNKNOWN_AUTOMATION_TEXT(){return this.hass.localize("ui.panel.config.devices.automation.actions.unknown_action")}get _value(){if(!this.value)return"";if(!this._automations.length)return V;const e=this._automations.findIndex((e=>(0,c.Po)(this._entityReg,e,this.value)));return-1===e?x:`${this._automations[e].device_id}_${e}`}render(){if(this._renderEmpty)return r.s6;const e=this._value;return(0,r.qy)(b||(b=M`
      <ha-md-select
        .label=${0}
        .value=${0}
        @change=${0}
        @closed=${0}
        .disabled=${0}
      >
        ${0}
        ${0}
        ${0}
      </ha-md-select>
    `),this.label,e,this._automationChanged,v.d,0===this._automations.length,e===V?(0,r.qy)(w||(w=M`<ha-md-select-option .value=${0}>
              ${0}
            </ha-md-select-option>`),V,this.NO_AUTOMATION_TEXT):r.s6,e===x?(0,r.qy)(A||(A=M`<ha-md-select-option .value=${0}>
              ${0}
            </ha-md-select-option>`),x,this.UNKNOWN_AUTOMATION_TEXT):r.s6,this._automations.map(((e,t)=>(0,r.qy)(C||(C=M`
            <ha-md-select-option .value=${0}>
              ${0}
            </ha-md-select-option>
          `),`${e.device_id}_${t}`,this._localizeDeviceAutomation(this.hass,this._entityReg,e)))))}updated(e){super.updated(e),e.has("deviceId")&&this._updateDeviceInfo()}async _updateDeviceInfo(){this._automations=this.deviceId?(await this._fetchDeviceAutomations(this.hass,this.deviceId)).sort(c.RK):[],this.value&&this.value.device_id===this.deviceId||this._setValue(this._automations.length?this._automations[0]:this._createNoAutomation(this.deviceId)),this._renderEmpty=!0,await this.updateComplete,this._renderEmpty=!1}_automationChanged(e){const t=e.target.value;if(!t||[x,V].includes(t))return;const[o,i]=t.split("_"),n=this._automations[i];n.device_id===o&&this._setValue(n)}_setValue(e){if(this.value&&(0,c.Po)(this._entityReg,e,this.value))return;const t=Object.assign({},e);delete t.metadata,(0,s.r)(this,"value-changed",{value:t})}constructor(e,t,o){super(),this._automations=[],this._renderEmpty=!1,this._localizeDeviceAutomation=e,this._fetchDeviceAutomations=t,this._createNoAutomation=o}}H.styles=(0,r.AH)($||($=M`
    ha-select {
      display: block;
    }
  `)),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],H.prototype,"hass",void 0),(0,i.__decorate)([(0,a.MZ)()],H.prototype,"label",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],H.prototype,"deviceId",void 0),(0,i.__decorate)([(0,a.MZ)({type:Object})],H.prototype,"value",void 0),(0,i.__decorate)([(0,a.wk)()],H.prototype,"_automations",void 0),(0,i.__decorate)([(0,a.wk)()],H.prototype,"_renderEmpty",void 0),(0,i.__decorate)([(0,a.wk)(),(0,n.Fg)({context:l.ih,subscribe:!0})],H.prototype,"_entityReg",void 0)},71755:function(e,t,o){o.a(e,(async function(e,t){try{o(79827),o(35748),o(65315),o(12840),o(837),o(37089),o(59023),o(52885),o(5934),o(18223),o(95013);var i=o(69868),n=o(84922),r=o(11991),a=o(65940),s=o(73120),l=o(22441),c=o(44537),d=o(92830),u=o(24383),p=o(88120),h=o(56083),m=o(28027),f=o(45363),y=o(58453),_=e([y]);y=(_.then?(await _)():_)[0];let g,v,b,w,A,C,$,M,V=e=>e;class x extends n.WF{firstUpdated(e){super.firstUpdated(e),this._loadConfigEntries()}async _loadConfigEntries(){const e=await(0,p.VN)(this.hass);this._configEntryLookup=Object.fromEntries(e.map((e=>[e.entry_id,e])))}render(){var e;const t=null!==(e=this.placeholder)&&void 0!==e?e:this.hass.localize("ui.components.device-picker.placeholder"),o=this.hass.localize("ui.components.device-picker.no_match"),i=this._valueRenderer(this._configEntryLookup);return(0,n.qy)(g||(g=V`
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
    `),this.hass,this.autofocus,this.label,this.searchLabel,o,t,this.value,this._rowRenderer,this._getItems,this.hideClearIcon,i,this._valueChanged)}async open(){var e;await this.updateComplete,await(null===(e=this._picker)||void 0===e?void 0:e.open())}_valueChanged(e){e.stopPropagation();const t=e.detail.value;this.value=t,(0,s.r)(this,"value-changed",{value:t})}constructor(...e){super(...e),this.autofocus=!1,this.disabled=!1,this.required=!1,this.hideClearIcon=!1,this._configEntryLookup={},this._getItems=()=>this._getDevices(this.hass.devices,this.hass.entities,this._configEntryLookup,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeDevices),this._getDevices=(0,a.A)(((e,t,o,i,n,r,a,s,p)=>{const f=Object.values(e),y=Object.values(t);let _={};(i||n||r||s)&&(_=(0,h.g2)(y));let g=f.filter((e=>e.id===this.value||!e.disabled_by));i&&(g=g.filter((e=>{const t=_[e.id];return!(!t||!t.length)&&_[e.id].some((e=>i.includes((0,d.m)(e.entity_id))))}))),n&&(g=g.filter((e=>{const t=_[e.id];return!t||!t.length||y.every((e=>!n.includes((0,d.m)(e.entity_id))))}))),p&&(g=g.filter((e=>!p.includes(e.id)))),r&&(g=g.filter((e=>{const t=_[e.id];return!(!t||!t.length)&&_[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&r.includes(t.attributes.device_class))}))}))),s&&(g=g.filter((e=>{const t=_[e.id];return!(!t||!t.length)&&t.some((e=>{const t=this.hass.states[e.entity_id];return!!t&&s(t)}))}))),a&&(g=g.filter((e=>e.id===this.value||a(e))));return g.map((e=>{const t=(0,c.T)(e,this.hass,_[e.id]),{area:i}=(0,u.w)(e,this.hass),n=i?(0,l.A)(i):void 0,r=e.primary_config_entry?null==o?void 0:o[e.primary_config_entry]:void 0,a=null==r?void 0:r.domain,s=a?(0,m.p$)(this.hass.localize,a):void 0;return{id:e.id,label:"",primary:t||this.hass.localize("ui.components.device-picker.unnamed_device"),secondary:n,domain:null==r?void 0:r.domain,domain_name:s,search_labels:[t,n,a,s].filter(Boolean),sorting_label:t||"zzz"}}))})),this._valueRenderer=(0,a.A)((e=>t=>{var o;const i=t,r=this.hass.devices[i];if(!r)return(0,n.qy)(v||(v=V`<span slot="headline">${0}</span>`),i);const{area:a}=(0,u.w)(r,this.hass),s=r?(0,c.xn)(r):void 0,d=a?(0,l.A)(a):void 0,p=r.primary_config_entry?e[r.primary_config_entry]:void 0;return(0,n.qy)(b||(b=V`
        ${0}
        <span slot="headline">${0}</span>
        <span slot="supporting-text">${0}</span>
      `),p?(0,n.qy)(w||(w=V`<img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${0}
            />`),(0,f.MR)({domain:p.domain,type:"icon",darkOptimized:null===(o=this.hass.themes)||void 0===o?void 0:o.darkMode})):n.s6,s,d)})),this._rowRenderer=e=>(0,n.qy)(A||(A=V`
    <ha-combo-box-item type="button">
      ${0}

      <span slot="headline">${0}</span>
      ${0}
      ${0}
    </ha-combo-box-item>
  `),e.domain?(0,n.qy)(C||(C=V`
            <img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${0}
            />
          `),(0,f.MR)({domain:e.domain,type:"icon",darkOptimized:this.hass.themes.darkMode})):n.s6,e.primary,e.secondary?(0,n.qy)($||($=V`<span slot="supporting-text">${0}</span>`),e.secondary):n.s6,e.domain_name?(0,n.qy)(M||(M=V`
            <div slot="trailing-supporting-text" class="domain">
              ${0}
            </div>
          `),e.domain_name):n.s6)}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],x.prototype,"autofocus",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],x.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],x.prototype,"required",void 0),(0,i.__decorate)([(0,r.MZ)()],x.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],x.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],x.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)()],x.prototype,"placeholder",void 0),(0,i.__decorate)([(0,r.MZ)({type:String,attribute:"search-label"})],x.prototype,"searchLabel",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1,type:Array})],x.prototype,"createDomains",void 0),(0,i.__decorate)([(0,r.MZ)({type:Array,attribute:"include-domains"})],x.prototype,"includeDomains",void 0),(0,i.__decorate)([(0,r.MZ)({type:Array,attribute:"exclude-domains"})],x.prototype,"excludeDomains",void 0),(0,i.__decorate)([(0,r.MZ)({type:Array,attribute:"include-device-classes"})],x.prototype,"includeDeviceClasses",void 0),(0,i.__decorate)([(0,r.MZ)({type:Array,attribute:"exclude-devices"})],x.prototype,"excludeDevices",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],x.prototype,"deviceFilter",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],x.prototype,"entityFilter",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"hide-clear-icon",type:Boolean})],x.prototype,"hideClearIcon",void 0),(0,i.__decorate)([(0,r.P)("ha-generic-picker")],x.prototype,"_picker",void 0),(0,i.__decorate)([(0,r.wk)()],x.prototype,"_configEntryLookup",void 0),x=(0,i.__decorate)([(0,r.EM)("ha-device-picker")],x),t()}catch(g){t(g)}}))},29897:function(e,t,o){o(35748),o(5934),o(95013);var i=o(69868),n=o(84922),r=o(11991),a=o(73120);o(93672);let s,l,c,d=e=>e;class u extends n.WF{render(){return(0,n.qy)(s||(s=d`
      <div
        class="row"
        tabindex="0"
        role="button"
        @keydown=${0}
      >
        ${0}
        <div class="leading-icon-wrapper">
          <slot name="leading-icon"></slot>
        </div>
        <slot class="header" name="header"></slot>
        <slot name="icons"></slot>
      </div>
    `),this._handleKeydown,this.leftChevron?(0,n.qy)(l||(l=d`
              <ha-icon-button
                class="expand-button"
                .path=${0}
                @click=${0}
                @keydown=${0}
              ></ha-icon-button>
            `),"M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z",this._handleExpand,this._handleExpand):n.s6)}async _handleExpand(e){e.defaultPrevented||"keydown"===e.type&&"Enter"!==e.key&&" "!==e.key||(e.stopPropagation(),e.preventDefault(),(0,a.r)(this,"toggle-collapsed"))}async _handleKeydown(e){if(!(e.defaultPrevented||"Enter"!==e.key&&" "!==e.key&&(!this.sortSelected&&!e.altKey||e.ctrlKey||e.metaKey||e.shiftKey||"ArrowUp"!==e.key&&"ArrowDown"!==e.key))){if(e.preventDefault(),e.stopPropagation(),"ArrowUp"===e.key||"ArrowDown"===e.key)return"ArrowUp"===e.key?void(0,a.r)(this,"move-up"):void(0,a.r)(this,"move-down");!this.sortSelected||"Enter"!==e.key&&" "!==e.key?this.click():(0,a.r)(this,"stop-sort-selection")}}focus(){requestAnimationFrame((()=>{var e;null===(e=this._rowElement)||void 0===e||e.focus()}))}constructor(...e){super(...e),this.leftChevron=!1,this.collapsed=!1,this.selected=!1,this.sortSelected=!1,this.disabled=!1,this.buildingBlock=!1}}u.styles=(0,n.AH)(c||(c=d`
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
  `)),(0,i.__decorate)([(0,r.MZ)({attribute:"left-chevron",type:Boolean})],u.prototype,"leftChevron",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],u.prototype,"collapsed",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],u.prototype,"selected",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"sort-selected"})],u.prototype,"sortSelected",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],u.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"building-block"})],u.prototype,"buildingBlock",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],u.prototype,"highlight",void 0),(0,i.__decorate)([(0,r.P)(".row")],u.prototype,"_rowElement",void 0),u=(0,i.__decorate)([(0,r.EM)("ha-automation-row")],u)},17711:function(e,t,o){o(35748),o(65315),o(22416),o(95013);var i=o(69868),n=o(84922),r=o(11991),a=o(90933);o(9974),o(95968);let s,l,c=e=>e;class d extends n.WF{get items(){var e;return null===(e=this._menu)||void 0===e?void 0:e.items}get selected(){var e;return null===(e=this._menu)||void 0===e?void 0:e.selected}focus(){var e,t;null!==(e=this._menu)&&void 0!==e&&e.open?this._menu.focusItemAtIndex(0):null===(t=this._triggerButton)||void 0===t||t.focus()}render(){return(0,n.qy)(s||(s=c`
      <div @click=${0}>
        <slot name="trigger" @slotchange=${0}></slot>
      </div>
      <ha-menu
        .corner=${0}
        .menuCorner=${0}
        .fixed=${0}
        .multi=${0}
        .activatable=${0}
        .y=${0}
        .x=${0}
      >
        <slot></slot>
      </ha-menu>
    `),this._handleClick,this._setTriggerAria,this.corner,this.menuCorner,this.fixed,this.multi,this.activatable,this.y,this.x)}firstUpdated(e){super.firstUpdated(e),"rtl"===a.G.document.dir&&this.updateComplete.then((()=>{this.querySelectorAll("ha-list-item").forEach((e=>{const t=document.createElement("style");t.innerHTML="span.material-icons:first-of-type { margin-left: var(--mdc-list-item-graphic-margin, 32px) !important; margin-right: 0px !important;}",e.shadowRoot.appendChild(t)}))}))}_handleClick(){this.disabled||(this._menu.anchor=this.noAnchor?null:this,this._menu.show())}get _triggerButton(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"]')}_setTriggerAria(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}constructor(...e){super(...e),this.corner="BOTTOM_START",this.menuCorner="START",this.x=null,this.y=null,this.multi=!1,this.activatable=!1,this.disabled=!1,this.fixed=!1,this.noAnchor=!1}}d.styles=(0,n.AH)(l||(l=c`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `)),(0,i.__decorate)([(0,r.MZ)()],d.prototype,"corner",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"menu-corner"})],d.prototype,"menuCorner",void 0),(0,i.__decorate)([(0,r.MZ)({type:Number})],d.prototype,"x",void 0),(0,i.__decorate)([(0,r.MZ)({type:Number})],d.prototype,"y",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],d.prototype,"multi",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],d.prototype,"activatable",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],d.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],d.prototype,"fixed",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"no-anchor"})],d.prototype,"noAnchor",void 0),(0,i.__decorate)([(0,r.P)("ha-menu",!0)],d.prototype,"_menu",void 0),d=(0,i.__decorate)([(0,r.EM)("ha-button-menu")],d)},75518:function(e,t,o){o(35748),o(65315),o(22416),o(37089),o(12977),o(5934),o(95013);var i=o(69868),n=o(84922),r=o(11991),a=o(21431),s=o(73120);o(23749),o(57674);let l,c,d,u,p,h,m,f,y,_=e=>e;const g={boolean:()=>o.e("2436").then(o.bind(o,33999)),constant:()=>o.e("3668").then(o.bind(o,33855)),float:()=>o.e("742").then(o.bind(o,84053)),grid:()=>o.e("7828").then(o.bind(o,57311)),expandable:()=>o.e("364").then(o.bind(o,51079)),integer:()=>o.e("7346").then(o.bind(o,40681)),multi_select:()=>Promise.all([o.e("6216"),o.e("3706")]).then(o.bind(o,99681)),positive_time_period_dict:()=>o.e("3540").then(o.bind(o,87551)),select:()=>o.e("2500").then(o.bind(o,10079)),string:()=>o.e("3627").then(o.bind(o,10070)),optional_actions:()=>o.e("3044").then(o.bind(o,96943))},v=(e,t)=>e?!t.name||t.flatten?e:e[t.name]:null;class b extends n.WF{getFormProperties(){return{}}async focus(){await this.updateComplete;const e=this.renderRoot.querySelector(".root");if(e)for(const t of e.children)if("HA-ALERT"!==t.tagName){t instanceof n.mN&&await t.updateComplete,t.focus();break}}willUpdate(e){e.has("schema")&&this.schema&&this.schema.forEach((e=>{var t;"selector"in e||null===(t=g[e.type])||void 0===t||t.call(g)}))}render(){return(0,n.qy)(l||(l=_`
      <div class="root" part="root">
        ${0}
        ${0}
      </div>
    `),this.error&&this.error.base?(0,n.qy)(c||(c=_`
              <ha-alert alert-type="error">
                ${0}
              </ha-alert>
            `),this._computeError(this.error.base,this.schema)):"",this.schema.map((e=>{var t;const o=((e,t)=>e&&t.name?e[t.name]:null)(this.error,e),i=((e,t)=>e&&t.name?e[t.name]:null)(this.warning,e);return(0,n.qy)(d||(d=_`
            ${0}
            ${0}
          `),o?(0,n.qy)(u||(u=_`
                  <ha-alert own-margin alert-type="error">
                    ${0}
                  </ha-alert>
                `),this._computeError(o,e)):i?(0,n.qy)(p||(p=_`
                    <ha-alert own-margin alert-type="warning">
                      ${0}
                    </ha-alert>
                  `),this._computeWarning(i,e)):"","selector"in e?(0,n.qy)(h||(h=_`<ha-selector
                  .schema=${0}
                  .hass=${0}
                  .narrow=${0}
                  .name=${0}
                  .selector=${0}
                  .value=${0}
                  .label=${0}
                  .disabled=${0}
                  .placeholder=${0}
                  .helper=${0}
                  .localizeValue=${0}
                  .required=${0}
                  .context=${0}
                ></ha-selector>`),e,this.hass,this.narrow,e.name,e.selector,v(this.data,e),this._computeLabel(e,this.data),e.disabled||this.disabled||!1,e.required?"":e.default,this._computeHelper(e),this.localizeValue,e.required||!1,this._generateContext(e)):(0,a._)(this.fieldElementName(e.type),Object.assign({schema:e,data:v(this.data,e),label:this._computeLabel(e,this.data),helper:this._computeHelper(e),disabled:this.disabled||e.disabled||!1,hass:this.hass,localize:null===(t=this.hass)||void 0===t?void 0:t.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(e)},this.getFormProperties())))})))}fieldElementName(e){return`ha-form-${e}`}_generateContext(e){if(!e.context)return;const t={};for(const[o,i]of Object.entries(e.context))t[o]=this.data[i];return t}createRenderRoot(){const e=super.createRenderRoot();return this.addValueChangedListener(e),e}addValueChangedListener(e){e.addEventListener("value-changed",(e=>{e.stopPropagation();const t=e.target.schema;if(e.target===this)return;const o=!t.name||"flatten"in t&&t.flatten?e.detail.value:{[t.name]:e.detail.value};this.data=Object.assign(Object.assign({},this.data),o),(0,s.r)(this,"value-changed",{value:this.data})}))}_computeLabel(e,t){return this.computeLabel?this.computeLabel(e,t):e?e.name:""}_computeHelper(e){return this.computeHelper?this.computeHelper(e):""}_computeError(e,t){return Array.isArray(e)?(0,n.qy)(m||(m=_`<ul>
        ${0}
      </ul>`),e.map((e=>(0,n.qy)(f||(f=_`<li>
              ${0}
            </li>`),this.computeError?this.computeError(e,t):e)))):this.computeError?this.computeError(e,t):e}_computeWarning(e,t){return this.computeWarning?this.computeWarning(e,t):e}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1}}b.styles=(0,n.AH)(y||(y=_`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `)),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],b.prototype,"narrow",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"data",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"schema",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"error",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"warning",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],b.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"computeError",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"computeWarning",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"computeLabel",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"computeHelper",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],b.prototype,"localizeValue",void 0),b=(0,i.__decorate)([(0,r.EM)("ha-form")],b)},61647:function(e,t,o){o(35748),o(95013);var i=o(69868),n=o(84922),r=o(11991),a=o(73120),s=(o(9974),o(5673)),l=o(89591),c=o(18396);let d;class u extends s.W1{connectedCallback(){super.connectedCallback(),this.addEventListener("close-menu",this._handleCloseMenu)}_handleCloseMenu(e){var t,o;e.detail.reason.kind===c.fi.KEYDOWN&&e.detail.reason.key===c.NV.ESCAPE||null===(t=(o=e.detail.initiator).clickAction)||void 0===t||t.call(o,e.detail.initiator)}}u.styles=[l.R,(0,n.AH)(d||(d=(e=>e)`
      :host {
        --md-sys-color-surface-container: var(--card-background-color);
      }
    `))],u=(0,i.__decorate)([(0,r.EM)("ha-md-menu")],u);let p,h,m=e=>e;class f extends n.WF{get items(){return this._menu.items}focus(){var e;this._menu.open?this._menu.focus():null===(e=this._triggerButton)||void 0===e||e.focus()}render(){return(0,n.qy)(p||(p=m`
      <div @click=${0}>
        <slot name="trigger" @slotchange=${0}></slot>
      </div>
      <ha-md-menu
        .quick=${0}
        .positioning=${0}
        .hasOverflow=${0}
        .anchorCorner=${0}
        .menuCorner=${0}
        @opening=${0}
        @closing=${0}
      >
        <slot></slot>
      </ha-md-menu>
    `),this._handleClick,this._setTriggerAria,this.quick,this.positioning,this.hasOverflow,this.anchorCorner,this.menuCorner,this._handleOpening,this._handleClosing)}_handleOpening(){(0,a.r)(this,"opening",void 0,{composed:!1})}_handleClosing(){(0,a.r)(this,"closing",void 0,{composed:!1})}_handleClick(){this.disabled||(this._menu.anchorElement=this,this._menu.open?this._menu.close():this._menu.show())}get _triggerButton(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"], ha-assist-chip[slot="trigger"]')}_setTriggerAria(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}constructor(...e){super(...e),this.disabled=!1,this.anchorCorner="end-start",this.menuCorner="start-start",this.hasOverflow=!1,this.quick=!1}}f.styles=(0,n.AH)(h||(h=m`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `)),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],f.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)()],f.prototype,"positioning",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"anchor-corner"})],f.prototype,"anchorCorner",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"menu-corner"})],f.prototype,"menuCorner",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"has-overflow"})],f.prototype,"hasOverflow",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],f.prototype,"quick",void 0),(0,i.__decorate)([(0,r.P)("ha-md-menu",!0)],f.prototype,"_menu",void 0),f=(0,i.__decorate)([(0,r.EM)("ha-md-button-menu")],f)},90666:function(e,t,o){var i=o(69868),n=o(61320),r=o(41715),a=o(84922),s=o(11991);let l;class c extends n.c{}c.styles=[r.R,(0,a.AH)(l||(l=(e=>e)`
      :host {
        --md-divider-color: var(--divider-color);
      }
    `))],c=(0,i.__decorate)([(0,s.EM)("ha-md-divider")],c)},70154:function(e,t,o){var i=o(69868),n=o(45369),r=o(20808),a=o(84922),s=o(11991);let l;class c extends n.K{}c.styles=[r.R,(0,a.AH)(l||(l=(e=>e)`
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
    `))],(0,i.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"clickAction",void 0),c=(0,i.__decorate)([(0,s.EM)("ha-md-menu-item")],c)},79080:function(e,t,o){o.a(e,(async function(e,t){try{o(35748),o(5934),o(95013);var i=o(69868),n=o(90227),r=o(84922),a=o(11991),s=o(73120),l=o(83566),c=o(84810),d=o(72698),u=o(5503),p=o(76943),h=(o(23749),e([c,p]));[c,p]=h.then?(await h)():h;let m,f,y,_,g,v,b=e=>e;const w=e=>{if("object"!=typeof e||null===e)return!1;for(const t in e)if(Object.prototype.hasOwnProperty.call(e,t))return!1;return!0};class A extends r.WF{setValue(e){try{this._yaml=w(e)?"":(0,n.Bh)(e,{schema:this.yamlSchema,quotingType:'"',noRefs:!0})}catch(t){console.error(t,e),alert(`There was an error converting to YAML: ${t}`)}}firstUpdated(){void 0!==this.defaultValue&&this.setValue(this.defaultValue)}willUpdate(e){super.willUpdate(e),this.autoUpdate&&e.has("value")&&this.setValue(this.value)}focus(){var e,t;null!==(e=this._codeEditor)&&void 0!==e&&e.codemirror&&(null===(t=this._codeEditor)||void 0===t||t.codemirror.focus())}render(){return void 0===this._yaml?r.s6:(0,r.qy)(m||(m=b`
      ${0}
      <ha-code-editor
        .hass=${0}
        .value=${0}
        .readOnly=${0}
        .disableFullscreen=${0}
        mode="yaml"
        autocomplete-entities
        autocomplete-icons
        .error=${0}
        @value-changed=${0}
        @blur=${0}
        dir="ltr"
      ></ha-code-editor>
      ${0}
      ${0}
    `),this.label?(0,r.qy)(f||(f=b`<p>${0}${0}</p>`),this.label,this.required?" *":""):r.s6,this.hass,this._yaml,this.readOnly,this.disableFullscreen,!1===this.isValid,this._onChange,this._onBlur,this._showingError?(0,r.qy)(y||(y=b`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):r.s6,this.copyClipboard||this.hasExtraActions?(0,r.qy)(_||(_=b`
            <div class="card-actions">
              ${0}
              <slot name="extra-actions"></slot>
            </div>
          `),this.copyClipboard?(0,r.qy)(g||(g=b`
                    <ha-button appearance="plain" @click=${0}>
                      ${0}
                    </ha-button>
                  `),this._copyYaml,this.hass.localize("ui.components.yaml-editor.copy_to_clipboard")):r.s6):r.s6)}_onChange(e){let t;e.stopPropagation(),this._yaml=e.detail.value;let o,i=!0;if(this._yaml)try{t=(0,n.Hh)(this._yaml,{schema:this.yamlSchema})}catch(r){i=!1,o=`${this.hass.localize("ui.components.yaml-editor.error",{reason:r.reason})}${r.mark?` (${this.hass.localize("ui.components.yaml-editor.error_location",{line:r.mark.line+1,column:r.mark.column+1})})`:""}`}else t={};this._error=null!=o?o:"",i&&(this._showingError=!1),this.value=t,this.isValid=i,(0,s.r)(this,"value-changed",{value:t,isValid:i,errorMsg:o})}_onBlur(){this.showErrors&&this._error&&(this._showingError=!0)}get yaml(){return this._yaml}async _copyYaml(){this.yaml&&(await(0,u.l)(this.yaml),(0,d.P)(this,{message:this.hass.localize("ui.common.copied_clipboard")}))}static get styles(){return[l.RF,(0,r.AH)(v||(v=b`
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
      `))]}constructor(...e){super(...e),this.yamlSchema=n.my,this.isValid=!0,this.autoUpdate=!1,this.readOnly=!1,this.disableFullscreen=!1,this.required=!1,this.copyClipboard=!1,this.hasExtraActions=!1,this.showErrors=!0,this._yaml="",this._error="",this._showingError=!1}}(0,i.__decorate)([(0,a.MZ)({attribute:!1})],A.prototype,"hass",void 0),(0,i.__decorate)([(0,a.MZ)()],A.prototype,"value",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],A.prototype,"yamlSchema",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],A.prototype,"defaultValue",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:"is-valid",type:Boolean})],A.prototype,"isValid",void 0),(0,i.__decorate)([(0,a.MZ)()],A.prototype,"label",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:"auto-update",type:Boolean})],A.prototype,"autoUpdate",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:"read-only",type:Boolean})],A.prototype,"readOnly",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean,attribute:"disable-fullscreen"})],A.prototype,"disableFullscreen",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean})],A.prototype,"required",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:"copy-clipboard",type:Boolean})],A.prototype,"copyClipboard",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:"has-extra-actions",type:Boolean})],A.prototype,"hasExtraActions",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:"show-errors",type:Boolean})],A.prototype,"showErrors",void 0),(0,i.__decorate)([(0,a.wk)()],A.prototype,"_yaml",void 0),(0,i.__decorate)([(0,a.wk)()],A.prototype,"_error",void 0),(0,i.__decorate)([(0,a.wk)()],A.prototype,"_showingError",void 0),(0,i.__decorate)([(0,a.P)("ha-code-editor")],A.prototype,"_codeEditor",void 0),A=(0,i.__decorate)([(0,a.EM)("ha-yaml-editor")],A),t()}catch(m){t(m)}}))},70614:function(e,t,o){o.d(t,{Dp:function(){return d},G3:function(){return c},S9:function(){return u},XF:function(){return r},aI:function(){return s},fo:function(){return l},vO:function(){return a}});o(35748),o(99342),o(65315),o(22416),o(37089),o(12977),o(95013);var i=o(26846),n=(o(68985),o(51663),o(32588));o(17866);const r=e=>{if("condition"in e&&Array.isArray(e.condition))return{condition:"and",conditions:e.condition};for(const t of n.I8)if(t in e)return{condition:t,conditions:e[t]};return e};const a=e=>e?Array.isArray(e)?e.map(a):("triggers"in e&&e.triggers&&(e.triggers=a(e.triggers)),"platform"in e&&("trigger"in e||(e.trigger=e.platform),delete e.platform),e):e,s=e=>{if(!e)return[];const t=[];return(0,i.e)(e).forEach((e=>{"triggers"in e?e.triggers&&t.push(...s(e.triggers)):t.push(e)})),t},l=e=>{if(!e||"object"!=typeof e)return!1;const t=e;return"trigger"in t&&"string"==typeof t.trigger||"platform"in t&&"string"==typeof t.platform},c=e=>{if(!e||"object"!=typeof e)return!1;return"condition"in e&&"string"==typeof e.condition},d=(e,t,o,i)=>e.connection.subscribeMessage(t,{type:"subscribe_trigger",trigger:o,variables:i}),u=(e,t,o)=>e.callWS({type:"test_condition",condition:t,variables:o})},10101:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{g:function(){return b},p:function(){return A}});o(46852),o(14423),o(79827),o(35748),o(99342),o(65315),o(84136),o(37089),o(36874),o(62928),o(67579),o(47849),o(51721),o(18223),o(1485),o(56660),o(95013);var n=o(26846),r=o(52744),a=o(48505),s=o(15216),l=o(27881),c=o(47379),d=o(41602),u=o(72106),p=o(7657),h=o(3949),m=o(71767),f=e([a,r,l,u]);[a,r,l,u]=f.then?(await f)():f;const y="ui.panel.config.automation.editor.triggers.type",_="ui.panel.config.automation.editor.conditions.type",g=(e,t)=>{let o;return o="number"==typeof t?(0,s.A)(t):"string"==typeof t?t:(0,r.nR)(e,t),o},v=(e,t,o)=>{const i=e.split(":");if(i.length<2||i.length>3)return e;try{const n=new Date("1970-01-01T"+e);return 2===i.length||0===Number(i[2])?(0,a.fU)(n,t,o):(0,a.ie)(n,t,o)}catch(n){return e}},b=(e,t,o,i=!1)=>{try{const n=w(e,t,o,i);if("string"!=typeof n)throw new Error(String(n));return n}catch(n){console.error(n);let e="Error in describing trigger";return n.message&&(e+=": "+n.message),e}},w=(e,t,o,i=!1)=>{if((0,h.H4)(e)){const o=(0,n.e)(e.triggers);if(!o||0===o.length)return t.localize(`${y}.list.description.no_trigger`);const i=o.length;return t.localize(`${y}.list.description.full`,{count:i})}if(e.alias&&!i)return e.alias;if("event"===e.trigger&&e.event_type){const o=[];if(Array.isArray(e.event_type))for(const t of e.event_type.values())o.push(t);else o.push(e.event_type);const i=(0,u.q)(t.locale,o);return t.localize(`${y}.event.description.full`,{eventTypes:i})}if("homeassistant"===e.trigger&&e.event)return t.localize("start"===e.event?`${y}.homeassistant.description.started`:`${y}.homeassistant.description.shutdown`);if("numeric_state"===e.trigger&&e.entity_id){const o=[],i=t.states,n=Array.isArray(e.entity_id)?t.states[e.entity_id[0]]:t.states[e.entity_id];if(Array.isArray(e.entity_id))for(const t of e.entity_id.values())i[t]&&o.push((0,c.u)(i[t])||t);else e.entity_id&&o.push(i[e.entity_id]?(0,c.u)(i[e.entity_id]):e.entity_id);const r=e.attribute?n?(0,l.R)(t.localize,n,t.entities,e.attribute):e.attribute:void 0,a=e.for?g(t.locale,e.for):void 0;if(void 0!==e.above&&void 0!==e.below)return t.localize(`${y}.numeric_state.description.above-below`,{attribute:r,entity:(0,u.q)(t.locale,o),numberOfEntities:o.length,above:e.above,below:e.below,duration:a});if(void 0!==e.above)return t.localize(`${y}.numeric_state.description.above`,{attribute:r,entity:(0,u.q)(t.locale,o),numberOfEntities:o.length,above:e.above,duration:a});if(void 0!==e.below)return t.localize(`${y}.numeric_state.description.below`,{attribute:r,entity:(0,u.q)(t.locale,o),numberOfEntities:o.length,below:e.below,duration:a})}if("state"===e.trigger){const o=[],i=t.states;let r="";if(e.attribute){const o=Array.isArray(e.entity_id)?t.states[e.entity_id[0]]:t.states[e.entity_id];r=o?(0,l.R)(t.localize,o,t.entities,e.attribute):e.attribute}const s=(0,n.e)(e.entity_id);if(s)for(const e of s)i[e]&&o.push((0,c.u)(i[e])||e);const d=t.states[s[0]];let p="other",h="";if(void 0!==e.from){let o=[];if(null===e.from)e.attribute||(p="null");else{o=(0,n.e)(e.from);const i=[];for(const n of o)i.push(d?e.attribute?t.formatEntityAttributeValue(d,e.attribute,n).toString():t.formatEntityState(d,n):n);0!==i.length&&(h=(0,u.q)(t.locale,i),p="fromUsed")}}let m="other",f="";if(void 0!==e.to){let o=[];if(null===e.to)e.attribute||(m="null");else{o=(0,n.e)(e.to);const i=[];for(const n of o)i.push(d?e.attribute?t.formatEntityAttributeValue(d,e.attribute,n).toString():t.formatEntityState(d,n).toString():n);0!==i.length&&(f=(0,u.q)(t.locale,i),m="toUsed")}}e.attribute||void 0!==e.from||void 0!==e.to||(m="special");let _="";var a;if(e.for)_=null!==(a=g(t.locale,e.for))&&void 0!==a?a:"";return t.localize(`${y}.state.description.full`,{hasAttribute:""!==r?"true":"false",attribute:r,hasEntity:0!==o.length?"true":"false",entity:(0,u.q)(t.locale,o),fromChoice:p,fromString:h,toChoice:m,toString:f,hasDuration:""!==_?"true":"false",duration:_})}if("sun"===e.trigger&&e.event){let o="";return e.offset&&(o="number"==typeof e.offset?(0,s.A)(e.offset):"string"==typeof e.offset?e.offset:JSON.stringify(e.offset)),t.localize("sunset"===e.event?`${y}.sun.description.sets`:`${y}.sun.description.rises`,{hasDuration:""!==o?"true":"false",duration:o})}if("tag"===e.trigger){const o=Object.values(t.states).find((t=>t.entity_id.startsWith("tag.")&&t.attributes.tag_id===e.tag_id));return o?t.localize(`${y}.tag.description.known_tag`,{tag_name:(0,c.u)(o)}):t.localize(`${y}.tag.description.full`)}if("time"===e.trigger&&e.at){const o=(0,n.e)(e.at).map((e=>{if("string"==typeof e)return(0,d.n)(e)?`entity ${t.states[e]?(0,c.u)(t.states[e]):e}`:v(e,t.locale,t.config);return`${`entity ${t.states[e.entity_id]?(0,c.u)(t.states[e.entity_id]):e.entity_id}`}${e.offset?" "+t.localize(`${y}.time.offset_by`,{offset:g(t.locale,e.offset)}):""}`}));let i=[];if(e.weekday){const o=(0,n.e)(e.weekday);o.length>0&&(i=o.map((e=>t.localize(`ui.panel.config.automation.editor.triggers.type.time.weekdays.${e}`))))}return t.localize(`${y}.time.description.full`,{time:(0,u.q)(t.locale,o),hasWeekdays:i.length>0?"true":"false",weekdays:(0,u.q)(t.locale,i)})}if("time_pattern"===e.trigger){if(!e.seconds&&!e.minutes&&!e.hours)return t.localize(`${y}.time_pattern.description.initial`);const o=[];let i="other",n="other",r="other",a=0,s=0,l=0;if(void 0!==e.seconds){const t="*"===e.seconds,n="string"==typeof e.seconds&&e.seconds.startsWith("/");a=t?0:"number"==typeof e.seconds?e.seconds:n?parseInt(e.seconds.substring(1)):parseInt(e.seconds),(isNaN(a)||a>59||a<0||n&&0===a)&&o.push("seconds"),i=t||n&&1===a?"every":n?"every_interval":"on_the_xth"}if(void 0!==e.minutes){const t="*"===e.minutes,i="string"==typeof e.minutes&&e.minutes.startsWith("/");s=t?0:"number"==typeof e.minutes?e.minutes:i?parseInt(e.minutes.substring(1)):parseInt(e.minutes),(isNaN(s)||s>59||s<0||i&&0===s)&&o.push("minutes"),n=t||i&&1===s?"every":i?"every_interval":void 0!==e.seconds?"has_seconds":"on_the_xth"}else void 0!==e.seconds&&(void 0!==e.hours?(s=0,n="has_seconds"):n="every");if(void 0!==e.hours){const t="*"===e.hours,i="string"==typeof e.hours&&e.hours.startsWith("/");l=t?0:"number"==typeof e.hours?e.hours:i?parseInt(e.hours.substring(1)):parseInt(e.hours),(isNaN(l)||l>23||l<0||i&&0===l)&&o.push("hours"),r=t||i&&1===l?"every":i?"every_interval":void 0!==e.seconds||void 0!==e.minutes?"has_seconds_or_minutes":"on_the_xth"}else r="every";return 0!==o.length?t.localize(`${y}.time_pattern.description.invalid`,{parts:(0,u.c)(t.locale,o.map((e=>t.localize(`${y}.time_pattern.${e}`))))}):t.localize(`${y}.time_pattern.description.full`,{secondsChoice:i,minutesChoice:n,hoursChoice:r,seconds:a,minutes:s,hours:l,secondsWithOrdinal:t.localize(`${y}.time_pattern.description.ordinal`,{part:a}),minutesWithOrdinal:t.localize(`${y}.time_pattern.description.ordinal`,{part:s}),hoursWithOrdinal:t.localize(`${y}.time_pattern.description.ordinal`,{part:l})})}if("zone"===e.trigger&&e.entity_id&&e.zone){const o=[],i=[],n=t.states;if(Array.isArray(e.entity_id))for(const t of e.entity_id.values())n[t]&&o.push((0,c.u)(n[t])||t);else o.push(n[e.entity_id]?(0,c.u)(n[e.entity_id]):e.entity_id);if(Array.isArray(e.zone))for(const t of e.zone.values())n[t]&&i.push((0,c.u)(n[t])||t);else i.push(n[e.zone]?(0,c.u)(n[e.zone]):e.zone);return t.localize(`${y}.zone.description.full`,{entity:(0,u.q)(t.locale,o),event:e.event.toString(),zone:(0,u.q)(t.locale,i),numberOfZones:i.length})}if("geo_location"===e.trigger&&e.source&&e.zone){const o=[],i=[],n=t.states;if(Array.isArray(e.source))for(const t of e.source.values())o.push(t);else o.push(e.source);if(Array.isArray(e.zone))for(const t of e.zone.values())n[t]&&i.push((0,c.u)(n[t])||t);else i.push(n[e.zone]?(0,c.u)(n[e.zone]):e.zone);return t.localize(`${y}.geo_location.description.full`,{source:(0,u.q)(t.locale,o),event:e.event.toString(),zone:(0,u.q)(t.locale,i),numberOfZones:i.length})}if("mqtt"===e.trigger)return t.localize(`${y}.mqtt.description.full`);if("template"===e.trigger){let o="";var m;if(e.for)o=null!==(m=g(t.locale,e.for))&&void 0!==m?m:"";return t.localize(`${y}.template.description.full`,{hasDuration:""!==o?"true":"false",duration:o})}if("webhook"===e.trigger)return t.localize(`${y}.webhook.description.full`);if("conversation"===e.trigger){if(!e.command||!e.command.length)return t.localize(`${y}.conversation.description.empty`);const o=(0,n.e)(e.command);return 1===o.length?t.localize(`${y}.conversation.description.single`,{sentence:o[0]}):t.localize(`${y}.conversation.description.multiple`,{sentence:o[0],count:o.length-1})}if("persistent_notification"===e.trigger)return t.localize(`${y}.persistent_notification.description.full`);if("device"===e.trigger&&e.device_id){const i=e,n=(0,p.nx)(t,o,i);if(n)return n;const r=t.states[i.entity_id];return`${r?(0,c.u)(r):i.entity_id} ${i.type}`}if("calendar"===e.trigger){const o=t.states[e.entity_id]?(0,c.u)(t.states[e.entity_id]):e.entity_id;let i="other",n="";if(e.offset){i=e.offset.startsWith("-")?"before":"after",n=e.offset.startsWith("-")?e.offset.substring(1).split(":"):e.offset.split(":");const o={hours:n.length>0?+n[0]:0,minutes:n.length>1?+n[1]:0,seconds:n.length>2?+n[2]:0};n=(0,r.i)(t.locale,o),""===n&&(i="other")}return t.localize(`${y}.calendar.description.full`,{eventChoice:e.event,offsetChoice:i,offset:n,hasCalendar:e.entity_id?"true":"false",calendar:o})}return t.localize(`ui.panel.config.automation.editor.triggers.type.${e.trigger}.label`)||t.localize("ui.panel.config.automation.editor.triggers.unknown_trigger")},A=(e,t,o,i=!1)=>{try{const n=C(e,t,o,i);if("string"!=typeof n)throw new Error(String(n));return n}catch(n){console.error(n);let e="Error in describing condition";return n.message&&(e+=": "+n.message),e}},C=(e,t,o,i=!1)=>{if("string"==typeof e&&(0,m.r)(e))return t.localize(`${_}.template.description.full`);if(e.alias&&!i)return e.alias;if(!e.condition){const t=["and","or","not"];for(const o of t)o in e&&(0,n.e)(e[o])&&(e={condition:o,conditions:e[o]})}if("or"===e.condition){const o=(0,n.e)(e.conditions);if(!o||0===o.length)return t.localize(`${_}.or.description.no_conditions`);const i=o.length;return t.localize(`${_}.or.description.full`,{count:i})}if("and"===e.condition){const o=(0,n.e)(e.conditions);if(!o||0===o.length)return t.localize(`${_}.and.description.no_conditions`);const i=o.length;return t.localize(`${_}.and.description.full`,{count:i})}if("not"===e.condition){const o=(0,n.e)(e.conditions);return o&&0!==o.length?1===o.length?t.localize(`${_}.not.description.one_condition`):t.localize(`${_}.not.description.full`,{count:o.length}):t.localize(`${_}.not.description.no_conditions`)}if("state"===e.condition){if(!e.entity_id)return t.localize(`${_}.state.description.no_entity`);let o="";if(e.attribute){const i=Array.isArray(e.entity_id)?t.states[e.entity_id[0]]:t.states[e.entity_id];o=i?(0,l.R)(t.localize,i,t.entities,e.attribute):e.attribute}const i=[];if(Array.isArray(e.entity_id))for(const s of e.entity_id.values())t.states[s]&&i.push((0,c.u)(t.states[s])||s);else e.entity_id&&i.push(t.states[e.entity_id]?(0,c.u)(t.states[e.entity_id]):e.entity_id);const n=[],r=t.states[Array.isArray(e.entity_id)?e.entity_id[0]:e.entity_id];if(Array.isArray(e.state))for(const s of e.state.values())n.push(r?e.attribute?t.formatEntityAttributeValue(r,e.attribute,s).toString():t.formatEntityState(r,s):s);else""!==e.state&&n.push(r?e.attribute?t.formatEntityAttributeValue(r,e.attribute,e.state).toString():t.formatEntityState(r,e.state.toString()):e.state.toString());let a="";return e.for&&(a=g(t.locale,e.for)||""),t.localize(`${_}.state.description.full`,{hasAttribute:""!==o?"true":"false",attribute:o,numberOfEntities:i.length,entities:"any"===e.match?(0,u.q)(t.locale,i):(0,u.c)(t.locale,i),numberOfStates:n.length,states:(0,u.q)(t.locale,n),hasDuration:""!==a?"true":"false",duration:a})}if("numeric_state"===e.condition&&e.entity_id){const o=(0,n.e)(e.entity_id),i=t.states[o[0]],r=(0,u.c)(t.locale,o.map((e=>t.states[e]?(0,c.u)(t.states[e]):e||""))),a=e.attribute?i?(0,l.R)(t.localize,i,t.entities,e.attribute):e.attribute:void 0;if(void 0!==e.above&&void 0!==e.below)return t.localize(`${_}.numeric_state.description.above-below`,{attribute:a,entity:r,numberOfEntities:o.length,above:e.above,below:e.below});if(void 0!==e.above)return t.localize(`${_}.numeric_state.description.above`,{attribute:a,entity:r,numberOfEntities:o.length,above:e.above});if(void 0!==e.below)return t.localize(`${_}.numeric_state.description.below`,{attribute:a,entity:r,numberOfEntities:o.length,below:e.below})}if("time"===e.condition){const o=(0,n.e)(e.weekday),i=o&&o.length>0&&o.length<7;if(e.before||e.after||i){const n="string"!=typeof e.before?e.before:e.before.includes(".")?`entity ${t.states[e.before]?(0,c.u)(t.states[e.before]):e.before}`:v(e.before,t.locale,t.config),r="string"!=typeof e.after?e.after:e.after.includes(".")?`entity ${t.states[e.after]?(0,c.u)(t.states[e.after]):e.after}`:v(e.after,t.locale,t.config);let a=[];i&&(a=o.map((e=>t.localize(`ui.panel.config.automation.editor.conditions.type.time.weekdays.${e}`))));let s="";return void 0!==r&&void 0!==n?s="after_before":void 0!==r?s="after":void 0!==n&&(s="before"),t.localize(`${_}.time.description.full`,{hasTime:s,hasTimeAndDay:(r||n)&&i?"true":"false",hasDay:i?"true":"false",time_before:n,time_after:r,day:(0,u.q)(t.locale,a)})}}if("sun"===e.condition&&(e.before||e.after)){var r,a;let o="";e.after&&e.after_offset&&(o="number"==typeof e.after_offset?(0,s.A)(e.after_offset):"string"==typeof e.after_offset?e.after_offset:JSON.stringify(e.after_offset));let i="";return e.before&&e.before_offset&&(i="number"==typeof e.before_offset?(0,s.A)(e.before_offset):"string"==typeof e.before_offset?e.before_offset:JSON.stringify(e.before_offset)),t.localize(`${_}.sun.description.full`,{afterChoice:null!==(r=e.after)&&void 0!==r?r:"other",afterOffsetChoice:""!==o?"offset":"other",afterOffset:o,beforeChoice:null!==(a=e.before)&&void 0!==a?a:"other",beforeOffsetChoice:""!==i?"offset":"other",beforeOffset:i})}if("zone"===e.condition&&e.entity_id&&e.zone){const o=[],i=[],n=t.states;if(Array.isArray(e.entity_id))for(const t of e.entity_id.values())n[t]&&o.push((0,c.u)(n[t])||t);else o.push(n[e.entity_id]?(0,c.u)(n[e.entity_id]):e.entity_id);if(Array.isArray(e.zone))for(const t of e.zone.values())n[t]&&i.push((0,c.u)(n[t])||t);else i.push(n[e.zone]?(0,c.u)(n[e.zone]):e.zone);const r=(0,u.q)(t.locale,o),a=(0,u.q)(t.locale,i);return t.localize(`${_}.zone.description.full`,{entity:r,numberOfEntities:o.length,zone:a,numberOfZones:i.length})}if("device"===e.condition&&e.device_id){const i=e,n=(0,p.I3)(t,o,i);if(n)return n;const r=t.states[i.entity_id];return`${r?(0,c.u)(r):i.entity_id} ${i.type}`}return"template"===e.condition?t.localize(`${_}.template.description.full`):"trigger"===e.condition&&null!=e.id?t.localize(`${_}.trigger.description.full`,{id:(0,u.q)(t.locale,(0,n.e)(e.id).map((e=>e.toString())))}):t.localize(`ui.panel.config.automation.editor.conditions.type.${e.condition}.label`)||t.localize("ui.panel.config.automation.editor.conditions.unknown_condition")};i()}catch(y){i(y)}}))},32588:function(e,t,o){o.d(t,{Dk:function(){return i},I8:function(){return r},fg:function(){return a},rq:function(){return n}});const i={device:"M3 6H21V4H3C1.9 4 1 4.9 1 6V18C1 19.1 1.9 20 3 20H7V18H3V6M13 12H9V13.78C8.39 14.33 8 15.11 8 16C8 16.89 8.39 17.67 9 18.22V20H13V18.22C13.61 17.67 14 16.88 14 16S13.61 14.33 13 13.78V12M11 17.5C10.17 17.5 9.5 16.83 9.5 16S10.17 14.5 11 14.5 12.5 15.17 12.5 16 11.83 17.5 11 17.5M22 8H16C15.5 8 15 8.5 15 9V19C15 19.5 15.5 20 16 20H22C22.5 20 23 19.5 23 19V9C23 8.5 22.5 8 22 8M21 18H17V10H21V18Z",and:"M4.4,16.5C4.4,15.6 4.7,14.7 5.2,13.9C5.7,13.1 6.7,12.2 8.2,11.2C7.3,10.1 6.8,9.3 6.5,8.7C6.1,8 6,7.4 6,6.7C6,5.2 6.4,4.1 7.3,3.2C8.2,2.3 9.4,2 10.9,2C12.2,2 13.3,2.4 14.2,3.2C15.1,4 15.5,5 15.5,6.1C15.5,6.9 15.3,7.6 14.9,8.3C14.5,9 13.8,9.7 12.8,10.4L11.4,11.5L15.7,16.7C16.3,15.5 16.6,14.3 16.6,12.8H18.8C18.8,15.1 18.3,17 17.2,18.5L20,21.8H17L15.7,20.3C15,20.9 14.3,21.3 13.4,21.6C12.5,21.9 11.6,22.1 10.7,22.1C8.8,22.1 7.3,21.6 6.1,20.6C5,19.5 4.4,18.2 4.4,16.5M10.7,20C12,20 13.2,19.5 14.3,18.5L9.6,12.8L9.2,13.1C7.7,14.2 7,15.3 7,16.5C7,17.6 7.3,18.4 8,19C8.7,19.6 9.5,20 10.7,20M8.5,6.7C8.5,7.6 9,8.6 10.1,9.9L11.7,8.8C12.3,8.4 12.7,8 12.9,7.6C13.1,7.2 13.2,6.7 13.2,6.2C13.2,5.6 13,5.1 12.5,4.7C12.1,4.3 11.5,4.1 10.8,4.1C10.1,4.1 9.5,4.3 9.1,4.8C8.7,5.3 8.5,5.9 8.5,6.7Z",or:"M2,4C5,10 5,14 2,20H8C13,20 19,16 22,12C19,8 13,4 8,4H2M5,6H8C11.5,6 16.3,9 19.3,12C16.3,15 11.5,18 8,18H5C6.4,13.9 6.4,10.1 5,6Z",not:"M14.08,4.61L15.92,5.4L14.8,8H19V10H13.95L12.23,14H19V16H11.38L9.92,19.4L8.08,18.61L9.2,16H5V14H10.06L11.77,10H5V8H12.63L14.08,4.61Z",state:"M6.27 17.05C6.72 17.58 7 18.25 7 19C7 20.66 5.66 22 4 22S1 20.66 1 19 2.34 16 4 16C4.18 16 4.36 16 4.53 16.05L7.6 10.69L5.86 9.7L9.95 8.58L11.07 12.67L9.33 11.68L6.27 17.05M20 16C18.7 16 17.6 16.84 17.18 18H11V16L8 19L11 22V20H17.18C17.6 21.16 18.7 22 20 22C21.66 22 23 20.66 23 19S21.66 16 20 16M12 8C12.18 8 12.36 8 12.53 7.95L15.6 13.31L13.86 14.3L17.95 15.42L19.07 11.33L17.33 12.32L14.27 6.95C14.72 6.42 15 5.75 15 5C15 3.34 13.66 2 12 2S9 3.34 9 5 10.34 8 12 8Z",numeric_state:"M4,17V9H2V7H6V17H4M22,15C22,16.11 21.1,17 20,17H16V15H20V13H18V11H20V9H16V7H20A2,2 0 0,1 22,9V10.5A1.5,1.5 0 0,1 20.5,12A1.5,1.5 0 0,1 22,13.5V15M14,15V17H8V13C8,11.89 8.9,11 10,11H12V9H8V7H12A2,2 0 0,1 14,9V11C14,12.11 13.1,13 12,13H10V15H14Z",sun:"M12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,2L14.39,5.42C13.65,5.15 12.84,5 12,5C11.16,5 10.35,5.15 9.61,5.42L12,2M3.34,7L7.5,6.65C6.9,7.16 6.36,7.78 5.94,8.5C5.5,9.24 5.25,10 5.11,10.79L3.34,7M3.36,17L5.12,13.23C5.26,14 5.53,14.78 5.95,15.5C6.37,16.24 6.91,16.86 7.5,17.37L3.36,17M20.65,7L18.88,10.79C18.74,10 18.47,9.23 18.05,8.5C17.63,7.78 17.1,7.15 16.5,6.64L20.65,7M20.64,17L16.5,17.36C17.09,16.85 17.62,16.22 18.04,15.5C18.46,14.77 18.73,14 18.87,13.21L20.64,17M12,22L9.59,18.56C10.33,18.83 11.14,19 12,19C12.82,19 13.63,18.83 14.37,18.56L12,22Z",template:"M8,3A2,2 0 0,0 6,5V9A2,2 0 0,1 4,11H3V13H4A2,2 0 0,1 6,15V19A2,2 0 0,0 8,21H10V19H8V14A2,2 0 0,0 6,12A2,2 0 0,0 8,10V5H10V3M16,3A2,2 0 0,1 18,5V9A2,2 0 0,0 20,11H21V13H20A2,2 0 0,0 18,15V19A2,2 0 0,1 16,21H14V19H16V14A2,2 0 0,1 18,12A2,2 0 0,1 16,10V5H14V3H16Z",time:"M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z",trigger:"M10 7V9H9V15H10V17H6V15H7V9H6V7H10M16 7C17.11 7 18 7.9 18 9V15C18 16.11 17.11 17 16 17H12V7M16 9H14V15H16V9Z",zone:"M12,2C15.31,2 18,4.66 18,7.95C18,12.41 12,19 12,19C12,19 6,12.41 6,7.95C6,4.66 8.69,2 12,2M12,6A2,2 0 0,0 10,8A2,2 0 0,0 12,10A2,2 0 0,0 14,8A2,2 0 0,0 12,6M20,19C20,21.21 16.42,23 12,23C7.58,23 4,21.21 4,19C4,17.71 5.22,16.56 7.11,15.83L7.75,16.74C6.67,17.19 6,17.81 6,18.5C6,19.88 8.69,21 12,21C15.31,21 18,19.88 18,18.5C18,17.81 17.33,17.19 16.25,16.74L16.89,15.83C18.78,16.56 20,17.71 20,19Z"},n={device:{},entity:{icon:"M11,13.5V21.5H3V13.5H11M12,2L17.5,11H6.5L12,2M17.5,13C20,13 22,15 22,17.5C22,20 20,22 17.5,22C15,22 13,20 13,17.5C13,15 15,13 17.5,13Z",members:{state:{},numeric_state:{}}},time_location:{icon:"M15,12H16.5V16.25L19.36,17.94L18.61,19.16L15,17V12M23,16A7,7 0 0,1 16,23C13,23 10.4,21.08 9.42,18.4L8,17.9L2.66,19.97L2.5,20A0.5,0.5 0 0,1 2,19.5V4.38C2,4.15 2.15,3.97 2.36,3.9L8,2L14,4.1L19.34,2H19.5A0.5,0.5 0 0,1 20,2.5V10.25C21.81,11.5 23,13.62 23,16M9,16C9,12.83 11.11,10.15 14,9.29V6.11L8,4V15.89L9,16.24C9,16.16 9,16.08 9,16M16,11A5,5 0 0,0 11,16A5,5 0 0,0 16,21A5,5 0 0,0 21,16A5,5 0 0,0 16,11Z",members:{sun:{},time:{},zone:{}}},building_blocks:{icon:"M18.5 18.5C19.04 18.5 19.5 18.96 19.5 19.5S19.04 20.5 18.5 20.5H6.5C5.96 20.5 5.5 20.04 5.5 19.5S5.96 18.5 6.5 18.5H18.5M18.5 17H6.5C5.13 17 4 18.13 4 19.5S5.13 22 6.5 22H18.5C19.88 22 21 20.88 21 19.5S19.88 17 18.5 17M21 11H18V7H13L10 11V16H22L21 11M11.54 11L13.5 8.5H16V11H11.54M9.76 3.41L4.76 2L2 11.83C1.66 13.11 2.41 14.44 3.7 14.8L4.86 15.12L8.15 12.29L4.27 11.21L6.15 4.46L8.94 5.24C9.5 5.53 10.71 6.34 11.47 7.37L12.5 6H12.94C11.68 4.41 9.85 3.46 9.76 3.41Z",members:{and:{},or:{},not:{}}},other:{icon:"M16,12A2,2 0 0,1 18,10A2,2 0 0,1 20,12A2,2 0 0,1 18,14A2,2 0 0,1 16,12M10,12A2,2 0 0,1 12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12M4,12A2,2 0 0,1 6,10A2,2 0 0,1 8,12A2,2 0 0,1 6,14A2,2 0 0,1 4,12Z",members:{template:{},trigger:{}}}},r=["and","or","not"],a=["ha-automation-condition-and","ha-automation-condition-not","ha-automation-condition-or"]},88151:function(e,t,o){o.d(t,{$:function(){return i}});o(12977);const i=(e,t)=>e.callWS(Object.assign({type:"validate_config"},t))},24986:function(e,t,o){o.d(t,{HD:function(){return a},ih:function(){return n},rf:function(){return r}});var i=o(97809);(0,i.q6)("connection"),(0,i.q6)("states"),(0,i.q6)("entities"),(0,i.q6)("devices"),(0,i.q6)("areas"),(0,i.q6)("localize"),(0,i.q6)("locale"),(0,i.q6)("config"),(0,i.q6)("themes"),(0,i.q6)("selectedTheme"),(0,i.q6)("user"),(0,i.q6)("userData"),(0,i.q6)("panels");const n=(0,i.q6)("extendedEntities"),r=(0,i.q6)("floors"),a=(0,i.q6)("labels")},7657:function(e,t,o){o.d(t,{I$:function(){return d},I3:function(){return _},PV:function(){return y},Po:function(){return h},RK:function(){return w},TB:function(){return u},TH:function(){return b},T_:function(){return v},am:function(){return a},jR:function(){return c},ng:function(){return s},nx:function(){return g},o9:function(){return l}});o(79827),o(18223);var i=o(47379),n=o(70614),r=o(2834);const a=(e,t)=>e.callWS({type:"device_automation/action/list",device_id:t}),s=(e,t)=>e.callWS({type:"device_automation/condition/list",device_id:t}),l=(e,t)=>e.callWS({type:"device_automation/trigger/list",device_id:t}).then((e=>(0,n.vO)(e))),c=(e,t)=>e.callWS({type:"device_automation/action/capabilities",action:t}),d=(e,t)=>e.callWS({type:"device_automation/condition/capabilities",condition:t}),u=(e,t)=>e.callWS({type:"device_automation/trigger/capabilities",trigger:t}),p=["device_id","domain","entity_id","type","subtype","event","condition","trigger"],h=(e,t,o)=>{if(typeof t!=typeof o)return!1;for(const s in t){var i,n;if(p.includes(s))if("entity_id"!==s||(null===(i=t[s])||void 0===i?void 0:i.includes("."))===(null===(n=o[s])||void 0===n?void 0:n.includes("."))){if(!Object.is(t[s],o[s]))return!1}else if(!m(e,t[s],o[s]))return!1}for(const s in o){var r,a;if(p.includes(s))if("entity_id"!==s||(null===(r=t[s])||void 0===r?void 0:r.includes("."))===(null===(a=o[s])||void 0===a?void 0:a.includes("."))){if(!Object.is(t[s],o[s]))return!1}else if(!m(e,t[s],o[s]))return!1}return!0},m=(e,t,o)=>{if(!t||!o)return!1;if(t.includes(".")){const o=(0,r.Ox)(e)[t];if(!o)return!1;t=o.id}if(o.includes(".")){const t=(0,r.Ox)(e)[o];if(!t)return!1;o=t.id}return t===o},f=(e,t,o)=>{if(!o)return"<"+e.localize("ui.panel.config.automation.editor.unknown_entity")+">";if(o.includes(".")){const t=e.states[o];return t?(0,i.u)(t):o}const n=(0,r.P9)(t)[o];return n?(0,r.jh)(e,n)||o:"<"+e.localize("ui.panel.config.automation.editor.unknown_entity")+">"},y=(e,t,o)=>e.localize(`component.${o.domain}.device_automation.action_type.${o.type}`,{entity_name:f(e,t,o.entity_id),subtype:o.subtype?e.localize(`component.${o.domain}.device_automation.action_subtype.${o.subtype}`)||o.subtype:""})||(o.subtype?`"${o.subtype}" ${o.type}`:o.type),_=(e,t,o)=>e.localize(`component.${o.domain}.device_automation.condition_type.${o.type}`,{entity_name:f(e,t,o.entity_id),subtype:o.subtype?e.localize(`component.${o.domain}.device_automation.condition_subtype.${o.subtype}`)||o.subtype:""})||(o.subtype?`"${o.subtype}" ${o.type}`:o.type),g=(e,t,o)=>e.localize(`component.${o.domain}.device_automation.trigger_type.${o.type}`,{entity_name:f(e,t,o.entity_id),subtype:o.subtype?e.localize(`component.${o.domain}.device_automation.trigger_subtype.${o.subtype}`)||o.subtype:""})||(o.subtype?`"${o.subtype}" ${o.type}`:o.type),v=(e,t)=>o=>e.localize(`component.${t.domain}.device_automation.extra_fields.${o.name}`)||o.name,b=(e,t)=>o=>e.localize(`component.${t.domain}.device_automation.extra_fields_descriptions.${o.name}`),w=(e,t)=>{var o,i,n,r;return null===(o=e.metadata)||void 0===o||!o.secondary||null!==(i=t.metadata)&&void 0!==i&&i.secondary?null!==(n=e.metadata)&&void 0!==n&&n.secondary||null===(r=t.metadata)||void 0===r||!r.secondary?0:-1:1}},8948:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{We:function(){return s},rM:function(){return a}});o(35748),o(47849),o(88238),o(34536),o(16257),o(20152),o(44711),o(72108),o(77030),o(95013);var n=o(52744),r=e([n]);n=(r.then?(await r)():r)[0];new Set(["temperature","current_temperature","target_temperature","target_temp_temp","target_temp_high","target_temp_low","target_temp_step","min_temp","max_temp"]);const a={climate:{humidity:"%",current_humidity:"%",target_humidity_low:"%",target_humidity_high:"%",target_humidity_step:"%",min_humidity:"%",max_humidity:"%"},cover:{current_position:"%",current_tilt_position:"%"},fan:{percentage:"%"},humidifier:{humidity:"%",current_humidity:"%",min_humidity:"%",max_humidity:"%"},light:{color_temp:"mired",max_mireds:"mired",min_mireds:"mired",color_temp_kelvin:"K",min_color_temp_kelvin:"K",max_color_temp_kelvin:"K",brightness:"%"},sun:{azimuth:"°",elevation:"°"},vacuum:{battery_level:"%"},valve:{current_position:"%"},sensor:{battery_level:"%"},media_player:{volume_level:"%"}},s=["access_token","auto_update","available_modes","away_mode","changed_by","code_format","color_modes","current_activity","device_class","editable","effect_list","effect","entity_picture","event_type","event_types","fan_mode","fan_modes","fan_speed_list","forecast","friendly_name","frontend_stream_type","has_date","has_time","hs_color","hvac_mode","hvac_modes","icon","media_album_name","media_artist","media_content_type","media_position_updated_at","media_title","next_dawn","next_dusk","next_midnight","next_noon","next_rising","next_setting","operation_list","operation_mode","options","preset_mode","preset_modes","release_notes","release_summary","release_url","restored","rgb_color","rgbw_color","shuffle","sound_mode_list","sound_mode","source_list","source_type","source","state_class","supported_features","swing_mode","swing_mode","swing_modes","title","token","unit_of_measurement","xy_color"];i()}catch(a){i(a)}}))},2834:function(e,t,o){o.d(t,{BM:function(){return y},Bz:function(){return h},G3:function(){return c},G_:function(){return d},Ox:function(){return m},P9:function(){return f},jh:function(){return s},v:function(){return l}});o(79827),o(35748),o(35058),o(65315),o(837),o(84136),o(12977),o(95013);var i=o(47308),n=o(65940),r=o(47379),a=(o(90963),o(24802));const s=(e,t)=>{if(t.name)return t.name;const o=e.states[t.entity_id];return o?(0,r.u)(o):t.original_name?t.original_name:t.entity_id},l=(e,t)=>e.callWS({type:"config/entity_registry/get",entity_id:t}),c=(e,t)=>e.callWS({type:"config/entity_registry/get_entries",entity_ids:t}),d=(e,t,o)=>e.callWS(Object.assign({type:"config/entity_registry/update",entity_id:t},o)),u=e=>e.sendMessagePromise({type:"config/entity_registry/list"}),p=(e,t)=>e.subscribeEvents((0,a.s)((()=>u(e).then((e=>t.setState(e,!0)))),500,!0),"entity_registry_updated"),h=(e,t)=>(0,i.N)("_entityRegistry",u,p,e,t),m=(0,n.A)((e=>{const t={};for(const o of e)t[o.entity_id]=o;return t})),f=(0,n.A)((e=>{const t={};for(const o of e)t[o.id]=o;return t})),y=(e,t)=>e.callWS({type:"config/entity_registry/get_automatic_entity_ids",entity_ids:t})},17866:function(e,t,o){o.d(t,{BD:function(){return c},Rn:function(){return p},pq:function(){return d},ve:function(){return u}});o(35748),o(65315),o(12840),o(37089),o(59023),o(12977),o(95013);var i=o(36207),n=o(87383),r=(o(68985),o(71767)),a=(o(51663),o(70614));(0,n.g)(["queued","parallel"]);const s=(0,i.Ik)({alias:(0,i.lq)((0,i.Yj)()),continue_on_error:(0,i.lq)((0,i.zM)()),enabled:(0,i.lq)((0,i.zM)())}),l=(0,i.Ik)({entity_id:(0,i.lq)((0,i.KC)([(0,i.Yj)(),(0,i.YO)((0,i.Yj)())])),device_id:(0,i.lq)((0,i.KC)([(0,i.Yj)(),(0,i.YO)((0,i.Yj)())])),area_id:(0,i.lq)((0,i.KC)([(0,i.Yj)(),(0,i.YO)((0,i.Yj)())])),floor_id:(0,i.lq)((0,i.KC)([(0,i.Yj)(),(0,i.YO)((0,i.Yj)())])),label_id:(0,i.lq)((0,i.KC)([(0,i.Yj)(),(0,i.YO)((0,i.Yj)())]))}),c=(0,i.kp)(s,(0,i.Ik)({action:(0,i.lq)((0,i.Yj)()),service_template:(0,i.lq)((0,i.Yj)()),entity_id:(0,i.lq)((0,i.Yj)()),target:(0,i.lq)((0,i.KC)([l,(0,i.YP)((0,i.Yj)(),"has_template",(e=>(0,r.r)(e)))])),data:(0,i.lq)((0,i.Ik)()),response_variable:(0,i.lq)((0,i.Yj)()),metadata:(0,i.lq)((0,i.Ik)())}));const d=e=>"string"==typeof e&&(0,r.r)(e)?"check_condition":"delay"in e?"delay":"wait_template"in e?"wait_template":["condition","and","or","not"].some((t=>t in e))?"check_condition":"event"in e?"fire_event":!("device_id"in e)||"trigger"in e||"condition"in e?"repeat"in e?"repeat":"choose"in e?"choose":"if"in e?"if":"wait_for_trigger"in e?"wait_for_trigger":"variables"in e?"variables":"stop"in e?"stop":"sequence"in e?"sequence":"parallel"in e?"parallel":"set_conversation_response"in e?"set_conversation_response":"action"in e||"service"in e?"service":"unknown":"device_action",u=e=>"unknown"!==d(e),p=e=>{var t,o;if(!e)return e;if(Array.isArray(e))return e.map(p);if("object"==typeof e&&null!==e&&"service"in e&&("action"in e||(e.action=e.service),delete e.service),"object"==typeof e&&null!==e&&"scene"in e&&(e.action="scene.turn_on",e.target={entity_id:e.scene},delete e.scene),"object"==typeof e&&null!==e&&"action"in e&&"media_player.play_media"===e.action&&"data"in e&&(null!==(t=e.data)&&void 0!==t&&t.media_content_id||null!==(o=e.data)&&void 0!==o&&o.media_content_type)){const t=Object.assign({},e.data),o={media_content_id:t.media_content_id,media_content_type:t.media_content_type,metadata:Object.assign({},e.metadata||{})};delete e.metadata,delete t.media_content_id,delete t.media_content_type,e.data=Object.assign(Object.assign({},t),{},{media:o})}if("object"==typeof e&&null!==e&&"sequence"in e)for(const n of e.sequence)p(n);const i=d(e);if("parallel"===i){p(e.parallel)}if("choose"===i){const t=e;if(Array.isArray(t.choose))for(const e of t.choose)p(e.sequence);else t.choose&&p(t.choose.sequence);t.default&&p(t.default)}if("repeat"===i){p(e.repeat.sequence)}if("if"===i){const t=e;p(t.then),t.else&&p(t.else)}if("wait_for_trigger"===i){const t=e;(0,a.vO)(t.wait_for_trigger)}return e}},3949:function(e,t,o){o.d(t,{H4:function(){return r},Sh:function(){return i},_y:function(){return n}});const i={calendar:"M19,19H5V8H19M16,1V3H8V1H6V3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3H18V1M17,12H12V17H17V12Z",device:"M3 6H21V4H3C1.9 4 1 4.9 1 6V18C1 19.1 1.9 20 3 20H7V18H3V6M13 12H9V13.78C8.39 14.33 8 15.11 8 16C8 16.89 8.39 17.67 9 18.22V20H13V18.22C13.61 17.67 14 16.88 14 16S13.61 14.33 13 13.78V12M11 17.5C10.17 17.5 9.5 16.83 9.5 16S10.17 14.5 11 14.5 12.5 15.17 12.5 16 11.83 17.5 11 17.5M22 8H16C15.5 8 15 8.5 15 9V19C15 19.5 15.5 20 16 20H22C22.5 20 23 19.5 23 19V9C23 8.5 22.5 8 22 8M21 18H17V10H21V18Z",event:"M10,9A1,1 0 0,1 11,8A1,1 0 0,1 12,9V13.47L13.21,13.6L18.15,15.79C18.68,16.03 19,16.56 19,17.14V21.5C18.97,22.32 18.32,22.97 17.5,23H11C10.62,23 10.26,22.85 10,22.57L5.1,18.37L5.84,17.6C6.03,17.39 6.3,17.28 6.58,17.28H6.8L10,19V9M11,5A4,4 0 0,1 15,9C15,10.5 14.2,11.77 13,12.46V11.24C13.61,10.69 14,9.89 14,9A3,3 0 0,0 11,6A3,3 0 0,0 8,9C8,9.89 8.39,10.69 9,11.24V12.46C7.8,11.77 7,10.5 7,9A4,4 0 0,1 11,5M11,3A6,6 0 0,1 17,9C17,10.7 16.29,12.23 15.16,13.33L14.16,12.88C15.28,11.96 16,10.56 16,9A5,5 0 0,0 11,4A5,5 0 0,0 6,9C6,11.05 7.23,12.81 9,13.58V14.66C6.67,13.83 5,11.61 5,9A6,6 0 0,1 11,3Z",state:"M6.27 17.05C6.72 17.58 7 18.25 7 19C7 20.66 5.66 22 4 22S1 20.66 1 19 2.34 16 4 16C4.18 16 4.36 16 4.53 16.05L7.6 10.69L5.86 9.7L9.95 8.58L11.07 12.67L9.33 11.68L6.27 17.05M20 16C18.7 16 17.6 16.84 17.18 18H11V16L8 19L11 22V20H17.18C17.6 21.16 18.7 22 20 22C21.66 22 23 20.66 23 19S21.66 16 20 16M12 8C12.18 8 12.36 8 12.53 7.95L15.6 13.31L13.86 14.3L17.95 15.42L19.07 11.33L17.33 12.32L14.27 6.95C14.72 6.42 15 5.75 15 5C15 3.34 13.66 2 12 2S9 3.34 9 5 10.34 8 12 8Z",geo_location:"M12,11.5A2.5,2.5 0 0,1 9.5,9A2.5,2.5 0 0,1 12,6.5A2.5,2.5 0 0,1 14.5,9A2.5,2.5 0 0,1 12,11.5M12,2A7,7 0 0,0 5,9C5,14.25 12,22 12,22C12,22 19,14.25 19,9A7,7 0 0,0 12,2Z",homeassistant:o(90663).mdiHomeAssistant,mqtt:"M21,9L17,5V8H10V10H17V13M7,11L3,15L7,19V16H14V14H7V11Z",numeric_state:"M4,17V9H2V7H6V17H4M22,15C22,16.11 21.1,17 20,17H16V15H20V13H18V11H20V9H16V7H20A2,2 0 0,1 22,9V10.5A1.5,1.5 0 0,1 20.5,12A1.5,1.5 0 0,1 22,13.5V15M14,15V17H8V13C8,11.89 8.9,11 10,11H12V9H8V7H12A2,2 0 0,1 14,9V11C14,12.11 13.1,13 12,13H10V15H14Z",sun:"M12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,2L14.39,5.42C13.65,5.15 12.84,5 12,5C11.16,5 10.35,5.15 9.61,5.42L12,2M3.34,7L7.5,6.65C6.9,7.16 6.36,7.78 5.94,8.5C5.5,9.24 5.25,10 5.11,10.79L3.34,7M3.36,17L5.12,13.23C5.26,14 5.53,14.78 5.95,15.5C6.37,16.24 6.91,16.86 7.5,17.37L3.36,17M20.65,7L18.88,10.79C18.74,10 18.47,9.23 18.05,8.5C17.63,7.78 17.1,7.15 16.5,6.64L20.65,7M20.64,17L16.5,17.36C17.09,16.85 17.62,16.22 18.04,15.5C18.46,14.77 18.73,14 18.87,13.21L20.64,17M12,22L9.59,18.56C10.33,18.83 11.14,19 12,19C12.82,19 13.63,18.83 14.37,18.56L12,22Z",conversation:"M8,7A2,2 0 0,1 10,9V14A2,2 0 0,1 8,16A2,2 0 0,1 6,14V9A2,2 0 0,1 8,7M14,14C14,16.97 11.84,19.44 9,19.92V22H7V19.92C4.16,19.44 2,16.97 2,14H4A4,4 0 0,0 8,18A4,4 0 0,0 12,14H14M21.41,9.41L17.17,13.66L18.18,10H14A2,2 0 0,1 12,8V4A2,2 0 0,1 14,2H20A2,2 0 0,1 22,4V8C22,8.55 21.78,9.05 21.41,9.41Z",tag:"M18,6H13A2,2 0 0,0 11,8V10.28C10.41,10.62 10,11.26 10,12A2,2 0 0,0 12,14C13.11,14 14,13.1 14,12C14,11.26 13.6,10.62 13,10.28V8H16V16H8V8H10V6H8L6,6V18H18M20,20H4V4H20M20,2H4A2,2 0 0,0 2,4V20A2,2 0 0,0 4,22H20C21.11,22 22,21.1 22,20V4C22,2.89 21.11,2 20,2Z",template:"M8,3A2,2 0 0,0 6,5V9A2,2 0 0,1 4,11H3V13H4A2,2 0 0,1 6,15V19A2,2 0 0,0 8,21H10V19H8V14A2,2 0 0,0 6,12A2,2 0 0,0 8,10V5H10V3M16,3A2,2 0 0,1 18,5V9A2,2 0 0,0 20,11H21V13H20A2,2 0 0,0 18,15V19A2,2 0 0,1 16,21H14V19H16V14A2,2 0 0,1 18,12A2,2 0 0,1 16,10V5H14V3H16Z",time:"M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z",time_pattern:"M11,17A1,1 0 0,0 12,18A1,1 0 0,0 13,17A1,1 0 0,0 12,16A1,1 0 0,0 11,17M11,3V7H13V5.08C16.39,5.57 19,8.47 19,12A7,7 0 0,1 12,19A7,7 0 0,1 5,12C5,10.32 5.59,8.78 6.58,7.58L12,13L13.41,11.59L6.61,4.79V4.81C4.42,6.45 3,9.05 3,12A9,9 0 0,0 12,21A9,9 0 0,0 21,12A9,9 0 0,0 12,3M18,12A1,1 0 0,0 17,11A1,1 0 0,0 16,12A1,1 0 0,0 17,13A1,1 0 0,0 18,12M6,12A1,1 0 0,0 7,13A1,1 0 0,0 8,12A1,1 0 0,0 7,11A1,1 0 0,0 6,12Z",webhook:"M10.46,19C9,21.07 6.15,21.59 4.09,20.15C2.04,18.71 1.56,15.84 3,13.75C3.87,12.5 5.21,11.83 6.58,11.77L6.63,13.2C5.72,13.27 4.84,13.74 4.27,14.56C3.27,16 3.58,17.94 4.95,18.91C6.33,19.87 8.26,19.5 9.26,18.07C9.57,17.62 9.75,17.13 9.82,16.63V15.62L15.4,15.58L15.47,15.47C16,14.55 17.15,14.23 18.05,14.75C18.95,15.27 19.26,16.43 18.73,17.35C18.2,18.26 17.04,18.58 16.14,18.06C15.73,17.83 15.44,17.46 15.31,17.04L11.24,17.06C11.13,17.73 10.87,18.38 10.46,19M17.74,11.86C20.27,12.17 22.07,14.44 21.76,16.93C21.45,19.43 19.15,21.2 16.62,20.89C15.13,20.71 13.9,19.86 13.19,18.68L14.43,17.96C14.92,18.73 15.75,19.28 16.75,19.41C18.5,19.62 20.05,18.43 20.26,16.76C20.47,15.09 19.23,13.56 17.5,13.35C16.96,13.29 16.44,13.36 15.97,13.53L15.12,13.97L12.54,9.2H12.32C11.26,9.16 10.44,8.29 10.47,7.25C10.5,6.21 11.4,5.4 12.45,5.44C13.5,5.5 14.33,6.35 14.3,7.39C14.28,7.83 14.11,8.23 13.84,8.54L15.74,12.05C16.36,11.85 17.04,11.78 17.74,11.86M8.25,9.14C7.25,6.79 8.31,4.1 10.62,3.12C12.94,2.14 15.62,3.25 16.62,5.6C17.21,6.97 17.09,8.47 16.42,9.67L15.18,8.95C15.6,8.14 15.67,7.15 15.27,6.22C14.59,4.62 12.78,3.85 11.23,4.5C9.67,5.16 8.97,7 9.65,8.6C9.93,9.26 10.4,9.77 10.97,10.11L11.36,10.32L8.29,15.31C8.32,15.36 8.36,15.42 8.39,15.5C8.88,16.41 8.54,17.56 7.62,18.05C6.71,18.54 5.56,18.18 5.06,17.24C4.57,16.31 4.91,15.16 5.83,14.67C6.22,14.46 6.65,14.41 7.06,14.5L9.37,10.73C8.9,10.3 8.5,9.76 8.25,9.14Z",persistent_notification:"M13 11H11V5H13M13 15H11V13H13M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z",zone:"M12,2C15.31,2 18,4.66 18,7.95C18,12.41 12,19 12,19C12,19 6,12.41 6,7.95C6,4.66 8.69,2 12,2M12,6A2,2 0 0,0 10,8A2,2 0 0,0 12,10A2,2 0 0,0 14,8A2,2 0 0,0 12,6M20,19C20,21.21 16.42,23 12,23C7.58,23 4,21.21 4,19C4,17.71 5.22,16.56 7.11,15.83L7.75,16.74C6.67,17.19 6,17.81 6,18.5C6,19.88 8.69,21 12,21C15.31,21 18,19.88 18,18.5C18,17.81 17.33,17.19 16.25,16.74L16.89,15.83C18.78,16.56 20,17.71 20,19Z",list:"M7,5H21V7H7V5M7,13V11H21V13H7M4,4.5A1.5,1.5 0 0,1 5.5,6A1.5,1.5 0 0,1 4,7.5A1.5,1.5 0 0,1 2.5,6A1.5,1.5 0 0,1 4,4.5M4,10.5A1.5,1.5 0 0,1 5.5,12A1.5,1.5 0 0,1 4,13.5A1.5,1.5 0 0,1 2.5,12A1.5,1.5 0 0,1 4,10.5M7,19V17H21V19H7M4,16.5A1.5,1.5 0 0,1 5.5,18A1.5,1.5 0 0,1 4,19.5A1.5,1.5 0 0,1 2.5,18A1.5,1.5 0 0,1 4,16.5Z"},n={device:{},entity:{icon:"M11,13.5V21.5H3V13.5H11M12,2L17.5,11H6.5L12,2M17.5,13C20,13 22,15 22,17.5C22,20 20,22 17.5,22C15,22 13,20 13,17.5C13,15 15,13 17.5,13Z",members:{state:{},numeric_state:{}}},time_location:{icon:"M15,12H16.5V16.25L19.36,17.94L18.61,19.16L15,17V12M23,16A7,7 0 0,1 16,23C13,23 10.4,21.08 9.42,18.4L8,17.9L2.66,19.97L2.5,20A0.5,0.5 0 0,1 2,19.5V4.38C2,4.15 2.15,3.97 2.36,3.9L8,2L14,4.1L19.34,2H19.5A0.5,0.5 0 0,1 20,2.5V10.25C21.81,11.5 23,13.62 23,16M9,16C9,12.83 11.11,10.15 14,9.29V6.11L8,4V15.89L9,16.24C9,16.16 9,16.08 9,16M16,11A5,5 0 0,0 11,16A5,5 0 0,0 16,21A5,5 0 0,0 21,16A5,5 0 0,0 16,11Z",members:{calendar:{},sun:{},time:{},time_pattern:{},zone:{}}},other:{icon:"M16,12A2,2 0 0,1 18,10A2,2 0 0,1 20,12A2,2 0 0,1 18,14A2,2 0 0,1 16,12M10,12A2,2 0 0,1 12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12M4,12A2,2 0 0,1 6,10A2,2 0 0,1 8,12A2,2 0 0,1 6,14A2,2 0 0,1 4,12Z",members:{event:{},geo_location:{},homeassistant:{},mqtt:{},conversation:{},tag:{},template:{},webhook:{},persistent_notification:{}}}},r=e=>"triggers"in e},40653:function(e,t,o){o(35748),o(99342),o(62928),o(47849),o(88238),o(34536),o(16257),o(20152),o(44711),o(72108),o(77030),o(95013);var i=o(84922);o(7577),o(95635);let n,r=e=>e;new Set(["clear-night","cloudy","fog","lightning","lightning-rainy","partlycloudy","pouring","rainy","hail","snowy","snowy-rainy","sunny","windy","windy-variant"]),new Set(["partlycloudy","cloudy","fog","windy","windy-variant","hail","rainy","snowy","snowy-rainy","pouring","lightning","lightning-rainy"]),new Set(["hail","rainy","pouring","lightning-rainy"]),new Set(["windy","windy-variant"]),new Set(["snowy","snowy-rainy"]),new Set(["lightning","lightning-rainy"]),(0,i.AH)(n||(n=r`
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
`))},7245:function(e,t,o){o(35748),o(65315),o(37089),o(95013);var i=o(69868),n=o(84922),r=o(11991);o(23749);let a,s,l,c=e=>e;class d extends n.WF{render(){return(0,n.qy)(a||(a=c`
      <ha-alert
        alert-type="warning"
        .title=${0}
      >
        ${0}
        ${0}
      </ha-alert>
    `),this.alertTitle||this.localize("ui.errors.config.editor_not_supported"),this.warnings.length&&void 0!==this.warnings[0]?(0,n.qy)(s||(s=c`<ul>
              ${0}
            </ul>`),this.warnings.map((e=>(0,n.qy)(l||(l=c`<li>${0}</li>`),e)))):n.s6,this.localize("ui.errors.config.edit_in_yaml_supported"))}constructor(...e){super(...e),this.warnings=[]}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"localize",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"alert-title"})],d.prototype,"alertTitle",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"warnings",void 0),d=(0,i.__decorate)([(0,r.EM)("ha-automation-editor-warning")],d)},20850:function(e,t,o){o.d(t,{EN:function(){return r},gZ:function(){return s},uV:function(){return n}});o(35748),o(5934),o(95013);var i=o(73120);const n="__paste__",r={repeat_count:{repeat:{count:2,sequence:[]}},repeat_while:{repeat:{while:[],sequence:[]}},repeat_until:{repeat:{until:[],sequence:[]}},repeat_for_each:{repeat:{for_each:{},sequence:[]}}},a=()=>o.e("1771").then(o.bind(o,41254)),s=(e,t)=>{(0,i.r)(e,"show-dialog",{dialogTag:"add-automation-element-dialog",dialogImport:a,dialogParams:t})}},67107:function(e,t,o){o.d(t,{V:function(){return n},b:function(){return r}});var i=o(36207);const n=(0,i.Ik)({trigger:(0,i.Yj)(),id:(0,i.lq)((0,i.Yj)()),enabled:(0,i.lq)((0,i.zM)())}),r=(0,i.Ik)({days:(0,i.lq)((0,i.ai)()),hours:(0,i.lq)((0,i.ai)()),minutes:(0,i.lq)((0,i.ai)()),seconds:(0,i.lq)((0,i.ai)())})},68975:function(e,t,o){o.d(t,{Ju:function(){return y},Lt:function(){return _},aM:function(){return f},bH:function(){return h},yj:function(){return m}});var i=o(84922);let n,r,a,s,l,c,d,u,p=e=>e;const h=(0,i.AH)(n||(n=p`
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
`)),m=(0,i.AH)(r||(r=p`
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
`)),f=(0,i.AH)(a||(a=p`
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
`)),y=((0,i.AH)(s||(s=p`
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
`)),(0,i.AH)(l||(l=p`
  :host {
    display: block;
    --sidebar-width: 0;
    --sidebar-gap: 0;
  }

  .has-sidebar {
    --sidebar-width: min(
      max(var(--sidebar-dynamic-width), ${0}px),
      100vw - ${0}px - var(--mdc-drawer-width, 0px),
      var(--ha-automation-editor-max-width) -
        ${0}px - var(--mdc-drawer-width, 0px)
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
`),375,350,350),(0,i.AH)(c||(c=p`
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
`))),_=((0,i.AH)(d||(d=p`
  .sidebar-editor {
    display: block;
    padding-top: 8px;
  }
  .description {
    padding-top: 16px;
  }
`)),(0,i.AH)(u||(u=p`
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
`)))},45363:function(e,t,o){o.d(t,{MR:function(){return i},a_:function(){return n},bg:function(){return r}});o(56660);const i=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,n=e=>e.split("/")[4],r=e=>e.startsWith("https://brands.home-assistant.io/")},52493:function(e,t,o){o.d(t,{c:function(){return i}});o(67579),o(41190);const i=/Mac/i.test(navigator.userAgent)},72698:function(e,t,o){o.d(t,{P:function(){return n}});var i=o(73120);const n=(e,t)=>(0,i.r)(e,"hass-notification",t)}}]);
//# sourceMappingURL=3901.01d9d4613b3098e9.js.map