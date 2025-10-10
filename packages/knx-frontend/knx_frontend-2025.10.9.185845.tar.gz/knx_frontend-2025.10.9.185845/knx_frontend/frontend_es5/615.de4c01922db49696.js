"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["615"],{47064:function(t,e,a){a.d(e,{a:function(){return o}});a(79827);var i=a(6098),r=a(92830);function o(t,e){const a=(0,r.m)(t.entity_id),o=void 0!==e?e:null==t?void 0:t.state;if(["button","event","input_button","scene"].includes(a))return o!==i.Hh;if((0,i.g0)(o))return!1;if(o===i.KF&&"alert"!==a)return!1;switch(a){case"alarm_control_panel":return"disarmed"!==o;case"alert":return"idle"!==o;case"cover":case"valve":return"closed"!==o;case"device_tracker":case"person":return"not_home"!==o;case"lawn_mower":return["mowing","error"].includes(o);case"lock":return"locked"!==o;case"media_player":return"standby"!==o;case"vacuum":return!["idle","docked","paused"].includes(o);case"plant":return"problem"===o;case"group":return["on","home","open","locked","problem"].includes(o);case"timer":return"active"===o;case"camera":return"streaming"===o}return!0}},99422:function(t,e,a){a.d(e,{Se:function(){return c},mT:function(){return h}});a(35748),a(99342),a(88238),a(34536),a(16257),a(20152),a(44711),a(72108),a(77030),a(95013);var i=a(6098),r=(a(65315),a(37089),a(92830));a(9724),a(89958),a(48169),a(90917),a(39118);var o=a(85735);var s=a(47064);const n=new Set(["alarm_control_panel","alert","automation","binary_sensor","calendar","camera","climate","cover","device_tracker","fan","group","humidifier","input_boolean","lawn_mower","light","lock","media_player","person","plant","remote","schedule","script","siren","sun","switch","timer","update","vacuum","valve","water_heater"]),c=(t,e)=>{if((void 0!==e?e:null==t?void 0:t.state)===i.Hh)return"var(--state-unavailable-color)";const a=d(t,e);return a?(r=a,Array.isArray(r)?r.reverse().reduce(((t,e)=>`var(${e}${t?`, ${t}`:""})`),void 0):`var(${r})`):void 0;var r},l=(t,e,a)=>{const i=void 0!==a?a:e.state,r=(0,s.a)(e,a);return u(t,e.attributes.device_class,i,r)},u=(t,e,a,i)=>{const r=[],s=(0,o.Y)(a,"_"),n=i?"active":"inactive";return e&&r.push(`--state-${t}-${e}-${s}-color`),r.push(`--state-${t}-${s}-color`,`--state-${t}-${n}-color`,`--state-${n}-color`),r},d=(t,e)=>{const a=void 0!==e?e:null==t?void 0:t.state,i=(0,r.m)(t.entity_id),o=t.attributes.device_class;if("sensor"===i&&"battery"===o){const t=(t=>{const e=Number(t);if(!isNaN(e))return e>=70?"--state-sensor-battery-high-color":e>=30?"--state-sensor-battery-medium-color":"--state-sensor-battery-low-color"})(a);if(t)return[t]}if("group"===i){const a=(t=>{const e=t.attributes.entity_id||[],a=[...new Set(e.map((t=>(0,r.m)(t))))];return 1===a.length?a[0]:void 0})(t);if(a&&n.has(a))return l(a,t,e)}if(n.has(i))return l(i,t,e)},h=t=>{if(t.attributes.brightness&&"plant"!==(0,r.m)(t.entity_id)){return`brightness(${(t.attributes.brightness+245)/5}%)`}return""}},85735:function(t,e,a){a.d(e,{Y:function(){return i}});a(42124),a(86581),a(67579),a(47849),a(30500);const i=(t,e="_")=>{const a="àáâäæãåāăąабçćčđďдèéêëēėęěеёэфğǵгḧхîïíīįìıİийкłлḿмñńǹňнôöòóœøōõőоṕпŕřрßśšşșсťțтûüùúūǘůűųувẃẍÿýыžźżз·",i=`aaaaaaaaaaabcccdddeeeeeeeeeeefggghhiiiiiiiiijkllmmnnnnnoooooooooopprrrsssssstttuuuuuuuuuuvwxyyyzzzz${e}`,r=new RegExp(a.split("").join("|"),"g"),o={"ж":"zh","х":"kh","ц":"ts","ч":"ch","ш":"sh","щ":"shch","ю":"iu","я":"ia"};let s;return""===t?s="":(s=t.toString().toLowerCase().replace(r,(t=>i.charAt(a.indexOf(t)))).replace(/[а-я]/g,(t=>o[t]||"")).replace(/(\d),(?=\d)/g,"$1").replace(/[^a-z0-9]+/g,e).replace(new RegExp(`(${e})\\1+`,"g"),"$1").replace(new RegExp(`^${e}+`),"").replace(new RegExp(`${e}+$`),""),""===s&&(s="unknown")),s}},45213:function(t,e,a){a.d(e,{E:function(){return r}});let i;const r=(0,a(84922).AH)(i||(i=(t=>t)`
  ha-state-icon[data-domain="alarm_control_panel"][data-state="pending"],
  ha-state-icon[data-domain="alarm_control_panel"][data-state="arming"],
  ha-state-icon[data-domain="alarm_control_panel"][data-state="triggered"],
  ha-state-icon[data-domain="lock"][data-state="jammed"] {
    animation: pulse 1s infinite;
  }

  @keyframes pulse {
    0% {
      opacity: 1;
    }
    50% {
      opacity: 0;
    }
    100% {
      opacity: 1;
    }
  }

  /* Color the icon if unavailable */
  ha-state-icon[data-state="unavailable"] {
    color: var(--state-unavailable-color);
  }
`))},23114:function(t,e,a){a.a(t,(async function(t,e){try{a(35748),a(65315),a(22416),a(95013);var i=a(69868),r=a(84922),o=a(11991),s=a(13802),n=a(7577),c=a(92830),l=a(7556),u=a(99422),d=a(45213),h=a(83733),v=a(35862),b=a(72582),p=t([b]);b=(p.then?(await p)():p)[0];let _,m,f,g=t=>t;const y="M13 14H11V9H13M13 18H11V16H13M1 21H23L12 2L1 21Z";class $ extends r.WF{connectedCallback(){var t,e;super.connectedCallback(),this.hasUpdated&&void 0===this.overrideImage&&(null!==(t=this.stateObj)&&void 0!==t&&t.attributes.entity_picture||null!==(e=this.stateObj)&&void 0!==e&&e.attributes.entity_picture_local)&&this.requestUpdate("stateObj")}disconnectedCallback(){var t,e;super.disconnectedCallback(),void 0===this.overrideImage&&(null!==(t=this.stateObj)&&void 0!==t&&t.attributes.entity_picture||null!==(e=this.stateObj)&&void 0!==e&&e.attributes.entity_picture_local)&&(this.style.backgroundImage="")}get _stateColor(){var t;const e=this.stateObj?(0,l.t)(this.stateObj):void 0;return null!==(t=this.stateColor)&&void 0!==t?t:"light"===e}render(){const t=this.stateObj;if(!t&&!this.overrideIcon&&!this.overrideImage)return(0,r.qy)(_||(_=g`<div class="missing">
        <ha-svg-icon .path=${0}></ha-svg-icon>
      </div>`),y);const e=this.getClass();if(e&&e.forEach(((t,e)=>{t?this.classList.add(e):this.classList.remove(e)})),!this.icon)return r.s6;const a=t?(0,l.t)(t):void 0;return(0,r.qy)(m||(m=g`<ha-state-icon
      .hass=${0}
      style=${0}
      data-domain=${0}
      data-state=${0}
      .icon=${0}
      .stateObj=${0}
    ></ha-state-icon>`),this.hass,(0,n.W)(this._iconStyle),(0,s.J)(a),(0,s.J)(null==t?void 0:t.state),this.overrideIcon,t)}willUpdate(t){if(super.willUpdate(t),!(t.has("stateObj")||t.has("overrideImage")||t.has("overrideIcon")||t.has("stateColor")||t.has("color")))return;const e=this.stateObj,a={};let i="";if(this.icon=!0,e){const t=(0,c.m)(e.entity_id);if(void 0===this.overrideImage)if(!e.attributes.entity_picture_local&&!e.attributes.entity_picture||this.overrideIcon){if(this.color)a.color=this.color;else if(this._stateColor){const t=(0,u.Se)(e);if(t&&(a.color=t),e.attributes.rgb_color&&(a.color=`rgb(${e.attributes.rgb_color.join(",")})`),e.attributes.brightness){const t=e.attributes.brightness;if("number"!=typeof t){const a=`Type error: state-badge expected number, but type of ${e.entity_id}.attributes.brightness is ${typeof t} (${t})`;console.warn(a)}a.filter=(0,u.mT)(e)}if(e.attributes.hvac_action){const t=e.attributes.hvac_action;t in v.sx?a.color=(0,u.Se)(e,v.sx[t]):delete a.color}}}else{let a=e.attributes.entity_picture_local||e.attributes.entity_picture;this.hass&&(a=this.hass.hassUrl(a)),"camera"===t&&(a=(0,h.su)(a,80,80)),i=`url(${a})`,this.icon=!1}else if(this.overrideImage){let t=this.overrideImage;this.hass&&(t=this.hass.hassUrl(t)),i=`url(${t})`,this.icon=!1}}this._iconStyle=a,this.style.backgroundImage=i}getClass(){const t=new Map(["has-no-radius","has-media-image","has-image"].map((t=>[t,!1])));if(this.stateObj){const e=(0,c.m)(this.stateObj.entity_id);"update"===e?t.set("has-no-radius",!0):"media_player"===e||"camera"===e?t.set("has-media-image",!0):""!==this.style.backgroundImage&&t.set("has-image",!0)}return t}static get styles(){return[d.E,(0,r.AH)(f||(f=g`
        :host {
          position: relative;
          display: inline-flex;
          width: 40px;
          color: var(--state-icon-color);
          border-radius: var(--state-badge-border-radius, 50%);
          height: 40px;
          background-size: cover;
          box-sizing: border-box;
          --state-inactive-color: initial;
          align-items: center;
          justify-content: center;
        }
        :host(.has-image) {
          border-radius: var(--state-badge-with-image-border-radius, 50%);
        }
        :host(.has-media-image) {
          border-radius: var(--state-badge-with-media-image-border-radius, 8%);
        }
        :host(.has-no-radius) {
          border-radius: 0;
        }
        :host(:focus) {
          outline: none;
        }
        :host(:not([icon]):focus) {
          border: 2px solid var(--divider-color);
        }
        :host([icon]:focus) {
          background: var(--divider-color);
        }
        ha-state-icon {
          transition:
            color 0.3s ease-in-out,
            filter 0.3s ease-in-out;
        }
        .missing {
          color: #fce588;
        }
      `))]}constructor(...t){super(...t),this.icon=!0,this._iconStyle={}}}(0,i.__decorate)([(0,o.MZ)({attribute:!1})],$.prototype,"stateObj",void 0),(0,i.__decorate)([(0,o.MZ)({attribute:!1})],$.prototype,"overrideIcon",void 0),(0,i.__decorate)([(0,o.MZ)({attribute:!1})],$.prototype,"overrideImage",void 0),(0,i.__decorate)([(0,o.MZ)({attribute:!1})],$.prototype,"stateColor",void 0),(0,i.__decorate)([(0,o.MZ)()],$.prototype,"color",void 0),(0,i.__decorate)([(0,o.MZ)({type:Boolean,reflect:!0})],$.prototype,"icon",void 0),(0,i.__decorate)([(0,o.wk)()],$.prototype,"_iconStyle",void 0),customElements.define("state-badge",$),e()}catch(_){e(_)}}))},72582:function(t,e,a){a.a(t,(async function(t,e){try{var i=a(69868),r=a(84922),o=a(11991),s=a(55),n=a(7556),c=a(93327),l=(a(81164),a(95635),t([c]));c=(l.then?(await l)():l)[0];let u,d,h,v,b=t=>t;class p extends r.WF{render(){var t,e;const a=this.icon||this.stateObj&&(null===(t=this.hass)||void 0===t||null===(t=t.entities[this.stateObj.entity_id])||void 0===t?void 0:t.icon)||(null===(e=this.stateObj)||void 0===e?void 0:e.attributes.icon);if(a)return(0,r.qy)(u||(u=b`<ha-icon .icon=${0}></ha-icon>`),a);if(!this.stateObj)return r.s6;if(!this.hass)return this._renderFallback();const i=(0,c.fq)(this.hass,this.stateObj,this.stateValue).then((t=>t?(0,r.qy)(d||(d=b`<ha-icon .icon=${0}></ha-icon>`),t):this._renderFallback()));return(0,r.qy)(h||(h=b`${0}`),(0,s.T)(i))}_renderFallback(){const t=(0,n.t)(this.stateObj);return(0,r.qy)(v||(v=b`
      <ha-svg-icon
        .path=${0}
      ></ha-svg-icon>
    `),c.l[t]||c.lW)}}(0,i.__decorate)([(0,o.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,i.__decorate)([(0,o.MZ)({attribute:!1})],p.prototype,"stateObj",void 0),(0,i.__decorate)([(0,o.MZ)({attribute:!1})],p.prototype,"stateValue",void 0),(0,i.__decorate)([(0,o.MZ)()],p.prototype,"icon",void 0),p=(0,i.__decorate)([(0,o.EM)("ha-state-icon")],p),e()}catch(u){e(u)}}))},83733:function(t,e,a){a.d(e,{su:function(){return i},wv:function(){return r}});a(12977),a(5934),a(56660),a(35748),a(95013);a(4311);const i=(t,e,a)=>`${t}&width=${e}&height=${a}`,r=async(t,e,a)=>{const i={type:"camera/stream",entity_id:e};a&&(i.format=a);const r=await t.callWS(i);return r.url=t.hassUrl(r.url),r}},35862:function(t,e,a){a.d(e,{sx:function(){return r},v5:function(){return i}});a(9724);const i="none";["auto","heat_cool","heat","cool","dry","fan_only","off"].reduce(((t,e,a)=>(t[e]=a,t)),{});const r={cooling:"cool",defrosting:"heat",drying:"dry",fan:"fan_only",heating:"heat",idle:"off",off:"off",preheating:"heat"}}}]);
//# sourceMappingURL=615.de4c01922db49696.js.map