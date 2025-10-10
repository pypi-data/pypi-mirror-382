/*! For license information please see 4094.4d20a3c3bd12bced.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["4094"],{10815:function(t,e,i){i.a(t,(async function(t,e){try{i(79827),i(35748),i(86149),i(65315),i(837),i(84136),i(37089),i(5934),i(18223),i(95013);var a=i(69868),n=i(84922),s=i(11991),o=i(33055),r=i(65940),l=i(26846),u=i(73120),d=i(92830),c=i(10151),h=i(5177),_=(i(8115),i(54538),i(54820),t([h,c]));[h,c]=_.then?(await _)():_;let p,m,v,f,b=t=>t;const y="M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z",g=["access_token","available_modes","battery_icon","battery_level","code_arm_required","code_format","color_modes","device_class","editable","effect_list","entity_id","entity_picture","event_types","fan_modes","fan_speed_list","friendly_name","frontend_stream_type","has_date","has_time","hvac_modes","icon","id","max_color_temp_kelvin","max_mireds","max_temp","max","min_color_temp_kelvin","min_mireds","min_temp","min","mode","operation_list","options","percentage_step","precipitation_unit","preset_modes","pressure_unit","remaining","sound_mode_list","source_list","state_class","step","supported_color_modes","supported_features","swing_modes","target_temp_step","temperature_unit","token","unit_of_measurement","visibility_unit","wind_speed_unit"];class M extends n.WF{shouldUpdate(t){return!(!t.has("_opened")&&this._opened)}render(){if(!this.hass)return n.s6;const t=this._value,e=this.entityId?this.hass.states[this.entityId]:void 0,i=this.options(this.entityId,e,this.allowName),a=i.filter((t=>!this._value.includes(t.value)));return(0,n.qy)(p||(p=b`
      ${0}

      <ha-combo-box
        item-value-path="value"
        item-label-path="label"
        .hass=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
        .value=${0}
        .items=${0}
        allow-custom-value
        @filter-changed=${0}
        @value-changed=${0}
        @opened-changed=${0}
      ></ha-combo-box>
    `),null!=t&&t.length?(0,n.qy)(m||(m=b`
            <ha-sortable
              no-style
              @item-moved=${0}
              .disabled=${0}
              handle-selector="button.primary.action"
            >
              <ha-chip-set>
                ${0}
              </ha-chip-set>
            </ha-sortable>
          `),this._moveItem,this.disabled,(0,o.u)(this._value,(t=>t),((t,e)=>{var a;const s=(null===(a=i.find((e=>e.value===t)))||void 0===a?void 0:a.label)||t;return(0,n.qy)(v||(v=b`
                      <ha-input-chip
                        .idx=${0}
                        @remove=${0}
                        .label=${0}
                        selected
                      >
                        <ha-svg-icon slot="icon" .path=${0}></ha-svg-icon>
                        ${0}
                      </ha-input-chip>
                    `),e,this._removeItem,s,y,s)}))):n.s6,this.hass,this.label,this.helper,this.disabled,this.required&&!t.length,"",a,this._filterChanged,this._comboBoxValueChanged,this._openedChanged)}get _value(){return this.value?(0,l.e)(this.value):[]}_openedChanged(t){this._opened=t.detail.value,this._comboBox.filteredItems=this._comboBox.items}_filterChanged(t){var e;this._filter=(null==t?void 0:t.detail.value)||"";const i=null===(e=this._comboBox.items)||void 0===e?void 0:e.filter((t=>{var e;return(t.label||t.value).toLowerCase().includes(null===(e=this._filter)||void 0===e?void 0:e.toLowerCase())}));this._filter&&(null==i||i.unshift({label:this._filter,value:this._filter})),this._comboBox.filteredItems=i}async _moveItem(t){t.stopPropagation();const{oldIndex:e,newIndex:i}=t.detail,a=this._value.concat(),n=a.splice(e,1)[0];a.splice(i,0,n),this._setValue(a),await this.updateComplete,this._filterChanged()}async _removeItem(t){t.stopPropagation();const e=[...this._value];e.splice(t.target.idx,1),this._setValue(e),await this.updateComplete,this._filterChanged()}_comboBoxValueChanged(t){t.stopPropagation();const e=t.detail.value;if(this.disabled||""===e)return;const i=this._value;i.includes(e)||(setTimeout((()=>{this._filterChanged(),this._comboBox.setInputValue("")}),0),this._setValue([...i,e]))}_setValue(t){const e=0===t.length?void 0:1===t.length?t[0]:t;this.value=e,(0,u.r)(this,"value-changed",{value:e})}constructor(...t){super(...t),this.autofocus=!1,this.disabled=!1,this.required=!1,this.allowName=!1,this._opened=!1,this.options=(0,r.A)(((t,e,i)=>{var a;const n=t?(0,d.m)(t):void 0;return[{label:this.hass.localize("ui.components.state-content-picker.state"),value:"state"},...i?[{label:this.hass.localize("ui.components.state-content-picker.name"),value:"name"}]:[],{label:this.hass.localize("ui.components.state-content-picker.last_changed"),value:"last_changed"},{label:this.hass.localize("ui.components.state-content-picker.last_updated"),value:"last_updated"},...n?c.p4.filter((t=>{var e;return null===(e=c.HS[n])||void 0===e?void 0:e.includes(t)})).map((t=>({label:this.hass.localize(`ui.components.state-content-picker.${t}`),value:t}))):[],...Object.keys(null!==(a=null==e?void 0:e.attributes)&&void 0!==a?a:{}).filter((t=>!g.includes(t))).map((t=>({value:t,label:this.hass.formatEntityAttributeName(e,t)})))]})),this._filter=""}}M.styles=(0,n.AH)(f||(f=b`
    :host {
      position: relative;
    }

    ha-chip-set {
      padding: 8px 0;
    }

    .sortable-fallback {
      display: none;
      opacity: 0;
    }

    .sortable-ghost {
      opacity: 0.4;
    }

    .sortable-drag {
      cursor: grabbing;
    }
  `)),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],M.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],M.prototype,"entityId",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],M.prototype,"autofocus",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],M.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],M.prototype,"required",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean,attribute:"allow-name"})],M.prototype,"allowName",void 0),(0,a.__decorate)([(0,s.MZ)()],M.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)()],M.prototype,"value",void 0),(0,a.__decorate)([(0,s.MZ)()],M.prototype,"helper",void 0),(0,a.__decorate)([(0,s.wk)()],M.prototype,"_opened",void 0),(0,a.__decorate)([(0,s.P)("ha-combo-box",!0)],M.prototype,"_comboBox",void 0),M=(0,a.__decorate)([(0,s.EM)("ha-entity-state-content-picker")],M),e()}catch(p){e(p)}}))},21873:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(95013);var a=i(69868),n=i(22103),s=i(84922),o=i(11991),r=i(45980),l=i(8692),u=t([r]);r=(u.then?(await u)():u)[0];class d extends s.mN{disconnectedCallback(){super.disconnectedCallback(),this._clearInterval()}connectedCallback(){super.connectedCallback(),this.datetime&&this._startInterval()}createRenderRoot(){return this}firstUpdated(t){super.firstUpdated(t),this._updateRelative()}update(t){super.update(t),this._updateRelative()}_clearInterval(){this._interval&&(window.clearInterval(this._interval),this._interval=void 0)}_startInterval(){this._clearInterval(),this._interval=window.setInterval((()=>this._updateRelative()),6e4)}_updateRelative(){if(this.datetime){const t="string"==typeof this.datetime?(0,n.H)(this.datetime):this.datetime,e=(0,r.K)(t,this.hass.locale);this.innerHTML=this.capitalize?(0,l.Z)(e):e}else this.innerHTML=this.hass.localize("ui.components.relative_time.never")}constructor(...t){super(...t),this.capitalize=!1}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],d.prototype,"datetime",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],d.prototype,"capitalize",void 0),d=(0,a.__decorate)([(0,o.EM)("ha-relative-time")],d),e()}catch(d){e(d)}}))},91901:function(t,e,i){i.a(t,(async function(t,a){try{i.r(e),i.d(e,{HaSelectorUiStateContent:function(){return h}});i(35748),i(95013);var n=i(69868),s=i(84922),o=i(11991),r=i(4331),l=i(10815),u=t([l]);l=(u.then?(await u)():u)[0];let d,c=t=>t;class h extends((0,r.E)(s.WF)){render(){var t,e,i;return(0,s.qy)(d||(d=c`
      <ha-entity-state-content-picker
        .hass=${0}
        .entityId=${0}
        .value=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
        .allowName=${0}
      ></ha-entity-state-content-picker>
    `),this.hass,(null===(t=this.selector.ui_state_content)||void 0===t?void 0:t.entity_id)||(null===(e=this.context)||void 0===e?void 0:e.filter_entity),this.value,this.label,this.helper,this.disabled,this.required,null===(i=this.selector.ui_state_content)||void 0===i?void 0:i.allow_name)}constructor(...t){super(...t),this.disabled=!1,this.required=!0}}(0,n.__decorate)([(0,o.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,n.__decorate)([(0,o.MZ)({attribute:!1})],h.prototype,"selector",void 0),(0,n.__decorate)([(0,o.MZ)()],h.prototype,"value",void 0),(0,n.__decorate)([(0,o.MZ)()],h.prototype,"label",void 0),(0,n.__decorate)([(0,o.MZ)()],h.prototype,"helper",void 0),(0,n.__decorate)([(0,o.MZ)({type:Boolean})],h.prototype,"disabled",void 0),(0,n.__decorate)([(0,o.MZ)({type:Boolean})],h.prototype,"required",void 0),(0,n.__decorate)([(0,o.MZ)({attribute:!1})],h.prototype,"context",void 0),h=(0,n.__decorate)([(0,o.EM)("ha-selector-ui_state_content")],h),a()}catch(d){a(d)}}))},6098:function(t,e,i){i.d(e,{HV:function(){return s},Hh:function(){return n},KF:function(){return r},ON:function(){return o},g0:function(){return d},s7:function(){return l}});var a=i(87383);const n="unavailable",s="unknown",o="on",r="off",l=[n,s],u=[n,s,r],d=(0,a.g)(l);(0,a.g)(u)},4331:function(t,e,i){i.d(e,{E:function(){return s}});i(79827),i(35748),i(65315),i(59023),i(5934),i(18223),i(95013);var a=i(69868),n=i(11991);const s=t=>{class e extends t{connectedCallback(){super.connectedCallback(),this._checkSubscribed()}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const t=this.__unsubs.pop();t instanceof Promise?t.then((t=>t())):t()}this.__unsubs=void 0}}updated(t){if(super.updated(t),t.has("hass"))this._checkSubscribed();else if(this.hassSubscribeRequiredHostProps)for(const e of t.keys())if(this.hassSubscribeRequiredHostProps.includes(e))return void this._checkSubscribed()}hassSubscribe(){return[]}_checkSubscribed(){var t;void 0!==this.__unsubs||!this.isConnected||void 0===this.hass||null!==(t=this.hassSubscribeRequiredHostProps)&&void 0!==t&&t.some((t=>void 0===this[t]))||(this.__unsubs=this.hassSubscribe())}}return(0,a.__decorate)([(0,n.MZ)({attribute:!1})],e.prototype,"hass",void 0),e}},10151:function(t,e,i){i.a(t,(async function(t,a){try{i.d(e,{HS:function(){return x},p4:function(){return w}});i(79827),i(35748),i(65315),i(837),i(37089),i(5934),i(18223),i(95013);var n=i(69868),s=i(84922),o=i(11991),r=i(37507),l=i(26846),u=i(7556),d=i(47379),c=i(21873),h=i(6098),_=i(3319),p=i(25256),m=i(44473),v=t([c,m,p]);[c,m,p]=v.then?(await v)():v;let f,b,y,g,M,$,C=t=>t;const H=["button","input_button","scene"],w=["remaining_time","install_status"],x={timer:["remaining_time"],update:["install_status"]},k={valve:["current_position"],cover:["current_position"],fan:["percentage"],light:["brightness"]},Z={climate:["state","current_temperature"],cover:["state","current_position"],fan:"percentage",humidifier:["state","current_humidity"],light:"brightness",timer:"remaining_time",update:"install_status",valve:["state","current_position"]};class V extends s.WF{createRenderRoot(){return this}get _content(){var t,e;const i=(0,u.t)(this.stateObj);return null!==(t=null!==(e=this.content)&&void 0!==e?e:Z[i])&&void 0!==t?t:"state"}_computeContent(t){var e,a;const n=this.stateObj,o=(0,u.t)(n);if("state"===t)return this.dashUnavailable&&(0,h.g0)(n.state)?"—":n.attributes.device_class!==_.Sn&&!H.includes(o)||(0,h.g0)(n.state)?this.hass.formatEntityState(n):(0,s.qy)(f||(f=C`
          <hui-timestamp-display
            .hass=${0}
            .ts=${0}
            format="relative"
            capitalize
          ></hui-timestamp-display>
        `),this.hass,new Date(n.state));if("name"===t)return(0,s.qy)(b||(b=C`${0}`),this.name||(0,d.u)(n));let r;if("last_changed"!==t&&"last-changed"!==t||(r=n.last_changed),"last_updated"!==t&&"last-updated"!==t||(r=n.last_updated),"input_datetime"===o&&"timestamp"===t&&(r=new Date(1e3*n.attributes.timestamp)),"last_triggered"!==t&&("calendar"!==o||"start_time"!==t&&"end_time"!==t)&&("sun"!==o||"next_dawn"!==t&&"next_dusk"!==t&&"next_midnight"!==t&&"next_noon"!==t&&"next_rising"!==t&&"next_setting"!==t)||(r=n.attributes[t]),r)return(0,s.qy)(y||(y=C`
        <ha-relative-time
          .hass=${0}
          .datetime=${0}
          capitalize
        ></ha-relative-time>
      `),this.hass,r);if((null!==(e=x[o])&&void 0!==e?e:[]).includes(t)){if("install_status"===t)return(0,s.qy)(g||(g=C`
          ${0}
        `),(0,p.A_)(n,this.hass));if("remaining_time"===t)return i.e("830").then(i.bind(i,92125)),(0,s.qy)(M||(M=C`
          <ha-timer-remaining-time
            .hass=${0}
            .stateObj=${0}
          ></ha-timer-remaining-time>
        `),this.hass,n)}const l=n.attributes[t];return null==l||null!==(a=k[o])&&void 0!==a&&a.includes(t)&&!l?void 0:this.hass.formatEntityAttributeValue(n,t)}render(){const t=this.stateObj,e=(0,l.e)(this._content).map((t=>this._computeContent(t))).filter(Boolean);return e.length?(0,r.f)(e," · "):(0,s.qy)($||($=C`${0}`),this.hass.formatEntityState(t))}}(0,n.__decorate)([(0,o.MZ)({attribute:!1})],V.prototype,"hass",void 0),(0,n.__decorate)([(0,o.MZ)({attribute:!1})],V.prototype,"stateObj",void 0),(0,n.__decorate)([(0,o.MZ)({attribute:!1})],V.prototype,"content",void 0),(0,n.__decorate)([(0,o.MZ)({attribute:!1})],V.prototype,"name",void 0),(0,n.__decorate)([(0,o.MZ)({type:Boolean,attribute:"dash-unavailable"})],V.prototype,"dashUnavailable",void 0),V=(0,n.__decorate)([(0,o.EM)("state-display")],V),a()}catch(f){a(f)}}))},22103:function(t,e,i){i.d(e,{H:function(){return o}});i(91455),i(62928),i(42124),i(86581),i(67579),i(41190),i(47849),i(1485),i(30500),i(91844);var a=i(27554),n=i(67874),s=i(19490);function o(t,e){var i;const o=()=>(0,n.w)(null==e?void 0:e.in,NaN),m=null!==(i=null==e?void 0:e.additionalDigits)&&void 0!==i?i:2,v=function(t){const e={},i=t.split(r.dateTimeDelimiter);let a;if(i.length>2)return e;/:/.test(i[0])?a=i[0]:(e.date=i[0],a=i[1],r.timeZoneDelimiter.test(e.date)&&(e.date=t.split(r.timeZoneDelimiter)[0],a=t.substr(e.date.length,t.length)));if(a){const t=r.timezone.exec(a);t?(e.time=a.replace(t[1],""),e.timezone=t[1]):e.time=a}return e}(t);let f;if(v.date){const t=function(t,e){const i=new RegExp("^(?:(\\d{4}|[+-]\\d{"+(4+e)+"})|(\\d{2}|[+-]\\d{"+(2+e)+"})$)"),a=t.match(i);if(!a)return{year:NaN,restDateString:""};const n=a[1]?parseInt(a[1]):null,s=a[2]?parseInt(a[2]):null;return{year:null===s?n:100*s,restDateString:t.slice((a[1]||a[2]).length)}}(v.date,m);f=function(t,e){if(null===e)return new Date(NaN);const i=t.match(l);if(!i)return new Date(NaN);const a=!!i[4],n=c(i[1]),s=c(i[2])-1,o=c(i[3]),r=c(i[4]),u=c(i[5])-1;if(a)return function(t,e,i){return e>=1&&e<=53&&i>=0&&i<=6}(0,r,u)?function(t,e,i){const a=new Date(0);a.setUTCFullYear(t,0,4);const n=a.getUTCDay()||7,s=7*(e-1)+i+1-n;return a.setUTCDate(a.getUTCDate()+s),a}(e,r,u):new Date(NaN);{const t=new Date(0);return function(t,e,i){return e>=0&&e<=11&&i>=1&&i<=(_[e]||(p(t)?29:28))}(e,s,o)&&function(t,e){return e>=1&&e<=(p(t)?366:365)}(e,n)?(t.setUTCFullYear(e,s,Math.max(n,o)),t):new Date(NaN)}}(t.restDateString,t.year)}if(!f||isNaN(+f))return o();const b=+f;let y,g=0;if(v.time&&(g=function(t){const e=t.match(u);if(!e)return NaN;const i=h(e[1]),n=h(e[2]),s=h(e[3]);if(!function(t,e,i){if(24===t)return 0===e&&0===i;return i>=0&&i<60&&e>=0&&e<60&&t>=0&&t<25}(i,n,s))return NaN;return i*a.s0+n*a.Cg+1e3*s}(v.time),isNaN(g)))return o();if(!v.timezone){const t=new Date(b+g),i=(0,s.a)(0,null==e?void 0:e.in);return i.setFullYear(t.getUTCFullYear(),t.getUTCMonth(),t.getUTCDate()),i.setHours(t.getUTCHours(),t.getUTCMinutes(),t.getUTCSeconds(),t.getUTCMilliseconds()),i}return y=function(t){if("Z"===t)return 0;const e=t.match(d);if(!e)return 0;const i="+"===e[1]?-1:1,n=parseInt(e[2]),s=e[3]&&parseInt(e[3])||0;if(!function(t,e){return e>=0&&e<=59}(0,s))return NaN;return i*(n*a.s0+s*a.Cg)}(v.timezone),isNaN(y)?o():(0,s.a)(b+g+y,null==e?void 0:e.in)}const r={dateTimeDelimiter:/[T ]/,timeZoneDelimiter:/[Z ]/i,timezone:/([Z+-].*)$/},l=/^-?(?:(\d{3})|(\d{2})(?:-?(\d{2}))?|W(\d{2})(?:-?(\d{1}))?|)$/,u=/^(\d{2}(?:[.,]\d*)?)(?::?(\d{2}(?:[.,]\d*)?))?(?::?(\d{2}(?:[.,]\d*)?))?$/,d=/^([+-])(\d{2})(?::?(\d{2}))?$/;function c(t){return t?parseInt(t):1}function h(t){return t&&parseFloat(t.replace(",","."))||0}const _=[31,null,31,30,31,30,31,31,30,31,30,31];function p(t){return t%400==0||t%4==0&&t%100!=0}},37507:function(t,e,i){i.d(e,{f:function(){return a}});i(35748),i(95013);function*a(t,e){const i="function"==typeof e;if(void 0!==t){let a=-1;for(const n of t)a>-1&&(yield i?e(a):e),a++,yield n}}}}]);
//# sourceMappingURL=4094.4d20a3c3bd12bced.js.map